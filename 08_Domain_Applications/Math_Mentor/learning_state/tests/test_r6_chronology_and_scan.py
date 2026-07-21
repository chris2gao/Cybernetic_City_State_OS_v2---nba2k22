"""Round-6: chronology, expiry semantics, CLI snapshot truth, scan hardening.

All stores are synthetic temporaries. No real learner store is touched.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest
import yaml
from conftest import (
    EPOCH,
    NEAR_TERM,
    NODE,
    STABILITY,
    expire_window,
    fail_review,
    make_event,
    open_window,
    pass_window,
    reach_classroom_passed,
    reach_two_review_passes,
)

from append_event import WriteRefused, append_event, load_store, write_snapshot
from reduce_readonly import reduce_events

PACKAGE = Path(__file__).resolve().parents[1]


def reasons(result) -> str:
    return " | ".join(reason for _, reason in result.rejected)


OPENED = "2026-05-01T00:00:00+00:00"
BEFORE = "2026-04-01T00:00:00+00:00"
AFTER = "2026-05-08T00:00:00+00:00"


def _open_at(stamp: str = OPENED) -> list[dict]:
    return reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM, timestamp=stamp)
    ]


# --- chronology: failure ---------------------------------------------------


def test_failure_before_window_opening_is_rejected():
    result = reduce_events(_open_at() + [fail_review("f", "win-A", timestamp=BEFORE)], EPOCH)
    text = reasons(result)
    assert "at or before it" in text or "backdated event" in text


def test_failure_equal_to_window_opening_is_rejected():
    result = reduce_events(_open_at() + [fail_review("f", "win-A", timestamp=OPENED)], EPOCH)
    assert "at or before it" in reasons(result)


def test_failure_after_window_opening_is_accepted():
    result = reduce_events(_open_at() + [fail_review("f", "win-A", timestamp=AFTER)], EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].status == "stale"
    assert result.snapshot[NODE].historical_failure_count == 1


# --- chronology: expiry ----------------------------------------------------


def test_expiry_before_window_opening_is_rejected():
    result = reduce_events(_open_at() + [expire_window("e", timestamp=BEFORE)], EPOCH)
    text = reasons(result)
    assert "at or before it" in text or "backdated event" in text


def test_expiry_equal_to_window_opening_is_rejected():
    result = reduce_events(_open_at() + [expire_window("e", timestamp=OPENED)], EPOCH)
    assert "at or before it" in reasons(result)


def test_expiry_after_window_opening_is_accepted():
    result = reduce_events(_open_at() + [expire_window("e", timestamp=AFTER)], EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].historical_expiry_count == 1
    assert result.snapshot[NODE].historical_failure_count == 0


def test_backdated_review_due_after_a_later_classroom_event_is_rejected():
    events = [
        make_event("a", "not_seen", "introduced", timestamp="2026-03-01T00:00:00+00:00"),
        make_event("b", "introduced", "classroom_passed", timestamp="2026-06-01T00:00:00+00:00"),
        open_window("w", "classroom_passed", "win-A", NEAR_TERM,
                    timestamp="2026-04-01T00:00:00+00:00"),
    ]
    result = reduce_events(events, EPOCH)
    assert "backdated event" in reasons(result)


# --- expiry semantics are machine-readable ---------------------------------


def test_expiry_requires_attempt_occurred_false():
    event = expire_window("e", timestamp=AFTER)
    event["stale_evidence"]["attempt_occurred"] = True
    result = reduce_events(_open_at() + [event], EPOCH)
    assert "attempt_occurred: false" in reasons(result)


def test_failure_requires_attempt_occurred_true():
    event = fail_review("f", "win-A", timestamp=AFTER)
    event["stale_evidence"]["attempt_occurred"] = False
    result = reduce_events(_open_at() + [event], EPOCH)
    assert "attempt_occurred: true" in reasons(result)


def test_expiry_semantics_are_not_inferred_from_free_text():
    """A summary saying 'nobody showed up' must not substitute for the flag."""
    event = expire_window("e", timestamp=AFTER)
    del event["stale_evidence"]["attempt_occurred"]
    event["stale_evidence"]["cause_ref_or_summary"] = "nobody showed up"
    result = reduce_events(_open_at() + [event], EPOCH)
    assert "attempt_occurred: false" in reasons(result)


# --- schema conditionals added in round 6 ----------------------------------


def test_remediation_evidence_only_on_stale_to_review_due():
    from validate_events import validate_documents

    event = make_event("a", "not_seen", "introduced", remediation_evidence="re-taught")
    assert not validate_documents([event], check_chain=False).ok


def test_human_authorization_ref_cannot_ride_another_event_type():
    from validate_events import validate_documents

    event = make_event("a", "not_seen", "introduced", human_authorization_ref="looks-official")
    assert not validate_documents([event], check_chain=False).ok


def test_review_evidence_cannot_record_a_failure():
    from validate_events import validate_documents

    event = pass_window("p", "win-A")
    event["review_evidence"]["review_result"] = "failed"
    assert not validate_documents([event], check_chain=False).ok


# --- CLI reports the snapshot it published ---------------------------------


def test_cli_reports_the_published_snapshot_not_a_later_head(synthetic_store, tmp_path, monkeypatch):
    """Another writer advances the store right after publication."""
    import append_event as writer

    append_event(synthetic_store, reach_classroom_passed()[0])
    second = reach_classroom_passed()[1]
    path = tmp_path / "ev.yml"
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(second, fh, allow_unicode=True, sort_keys=True)

    real_write_snapshot = writer.write_snapshot
    third = make_event("c3", "classroom_passed", "blocked")

    def publish_then_someone_else_appends(store):
        final, snapshot = real_write_snapshot(store)
        real_append(store, third)  # store head advances immediately afterwards
        return final, snapshot

    real_append = writer.append_event
    monkeypatch.setattr(writer, "write_snapshot", publish_then_someone_else_appends)
    code = writer.main(["append_event.py", str(synthetic_store), str(path)])
    monkeypatch.undo()

    assert code == 0
    published = yaml.safe_load(
        (synthetic_store / "snapshots" / "learning_state.yml").read_text(encoding="utf-8")
    )
    # The store now has three events, but the published snapshot describes two.
    _, events = load_store(synthetic_store)
    assert len(events) == 3
    assert published["event_count"] == 2, "the CLI must describe what it published"


def test_write_snapshot_returns_the_published_snapshot(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    path, snapshot = write_snapshot(synthetic_store)
    on_disk = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert snapshot["source_head_digest"] == on_disk["source_head_digest"]
    assert snapshot["event_count"] == on_disk["event_count"]


# --- malformed anchor / store metadata -------------------------------------


def test_malformed_anchor_json_is_refused(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    (synthetic_store / "integrity" / "head.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(WriteRefused, match="not readable JSON"):
        load_store(synthetic_store)


def test_non_object_anchor_is_refused(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    (synthetic_store / "integrity" / "head.json").write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(WriteRefused, match="not a JSON object"):
        load_store(synthetic_store)


def test_anchor_with_wrong_schema_version_is_refused(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    path = synthetic_store / "integrity" / "head.json"
    anchor = json.loads(path.read_text(encoding="utf-8"))
    anchor["schema_version"] = "something.else"
    path.write_text(json.dumps(anchor), encoding="utf-8")
    with pytest.raises(WriteRefused, match="schema_version"):
        load_store(synthetic_store)


def test_malformed_store_meta_yaml_is_refused(synthetic_store):
    (synthetic_store / "store_meta.yml").write_text("a: [unclosed\n", encoding="utf-8")
    with pytest.raises(WriteRefused, match="not readable YAML"):
        load_store(synthetic_store)


def test_non_mapping_store_meta_is_refused(synthetic_store):
    (synthetic_store / "store_meta.yml").write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(WriteRefused, match="does not contain a mapping"):
        load_store(synthetic_store)


def test_cli_reports_malformed_anchor_as_refused_before_commit(synthetic_store, tmp_path, capsys):
    import append_event as writer

    append_event(synthetic_store, reach_classroom_passed()[0])
    (synthetic_store / "integrity" / "head.json").write_text("{broken", encoding="utf-8")
    path = tmp_path / "ev.yml"
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(reach_classroom_passed()[1], fh, allow_unicode=True, sort_keys=True)

    code = writer.main(["append_event.py", str(synthetic_store), str(path)])
    captured = capsys.readouterr()
    assert code == 1
    assert "outcome: refused_before_commit" in captured.out
    assert "the store is unchanged" in captured.out


# --- privacy scan hardening ------------------------------------------------


def _absent_term() -> str:
    """A term that cannot be in the tree, because it is invented per run.

    A literal sentinel does not work here: writing it into this file commits it,
    so the tree contains the very term the test calls absent and the "clean
    tree" case can never pass.  That is not a hypothetical - it is the defect
    this helper replaces.
    """
    return f"absent-{uuid4().hex}"


def _scan(*args: str, denylist: str | None = None):
    env = dict(os.environ)
    if denylist is None:
        denylist = _absent_term()
    if denylist == "":
        env.pop("LEARNER_DENYLIST", None)
    else:
        env["LEARNER_DENYLIST"] = denylist
    return subprocess.run(
        [sys.executable, str(PACKAGE / "privacy_scan.py"), *args],
        capture_output=True, text=True, env=env,
    )


def test_scan_clean_tree_exits_zero():
    result = _scan("HEAD")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "content_matching_lines: 0" in result.stdout
    assert "filename_hits: 0" in result.stdout
    assert "scan_errors: 0" in result.stdout


def test_scan_invalid_ref_is_a_failure_not_a_clean_result():
    result = _scan("definitely-not-a-ref-xyz")
    assert result.returncode == 2, "an unverifiable scan must never look clean"
    assert "SCAN FAILED" in result.stdout
    assert "clean" in result.stdout.lower()


def test_scan_without_denylist_fails():
    result = _scan("HEAD", denylist="")
    assert result.returncode == 2
    assert "SCAN FAILED" in result.stdout


def test_scan_finds_content_matches():
    # A term that certainly appears in tracked content, but is not a learner alias.
    result = _scan("HEAD", denylist="graduation_evidence_candidate")
    assert result.returncode == 1
    assert "content_matching_lines: 0" not in result.stdout


def test_scan_finds_filename_matches():
    result = _scan("HEAD", denylist="privacy_scan")
    assert result.returncode == 1
    assert "filename_hits: 0" not in result.stdout


def test_scan_never_prints_denylist_values():
    secret = "graduation_evidence_candidate"
    result = _scan("HEAD", denylist=secret)
    assert secret not in result.stdout, "the scan must not echo denylist values"


def test_overlapping_denylist_entries_are_deduplicated():
    result = _scan("HEAD", denylist="privacy_scan,privacy_scan, privacy_scan ")
    assert "denylist_terms: 1" in result.stdout

"""Round-4 hardening: threads, fail-closed paths, evidence causes, CLI truth.

All stores are synthetic temporaries. No real learner store is touched.
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path

import pytest
import yaml
from conftest import (
    EPOCH,
    NEAR_TERM,
    NODE,
    STABILITY,
    make_event,
    open_window,
    pass_window,
    reach_classroom_passed,
    reach_two_review_passes,
    unblock,
    fail_review,
    expire_window,
)

from append_event import (
    CANONICAL_EPOCH,
    WriteRefused,
    append_event,
    derive_snapshot,
    load_store,
    read_store_meta,
    repair_anchor,
    store_meta_digest,
    write_anchor,
)
from reduce_readonly import reduce_events

PACKAGE = Path(__file__).resolve().parents[1]


def reasons(result) -> str:
    return " | ".join(reason for _, reason in result.rejected)


# --- thread safety ---------------------------------------------------------


def test_two_threads_cannot_both_append(synthetic_store):
    """The old path-keyed depth counter let a second thread walk straight in."""
    append_event(synthetic_store, reach_classroom_passed()[0])
    barrier = threading.Barrier(2)
    outcomes: list[str] = []
    lock = threading.Lock()

    def attempt(event):
        barrier.wait()
        try:
            append_event(synthetic_store, event)
            with lock:
                outcomes.append("written")
        except Exception as error:  # StoreLocked or WriteRefused are both fine
            with lock:
                outcomes.append(type(error).__name__)

    second = reach_classroom_passed()[1]
    threads = [threading.Thread(target=attempt, args=(dict(second),)) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert outcomes.count("written") <= 1, f"two threads both wrote: {outcomes}"
    # Whatever happened, the store must remain internally consistent.
    _, events = load_store(synthetic_store)
    ids = [e["event_id"] for e in events]
    assert len(ids) == len(set(ids)), "duplicate events were produced"
    assert list((synthetic_store / "events").glob(".*tmp")) == [], "temporary files leaked"


# --- fail-closed reducer ---------------------------------------------------


def test_snapshot_refuses_when_an_illegal_event_is_on_disk(synthetic_store):
    """A store must not publish a snapshot that silently ignores illegal events."""
    append_event(synthetic_store, reach_classroom_passed()[0])
    # Hand-place a structurally valid but transition-invalid event, then rebuild
    # the anchor so only the reducer objects.
    illegal = make_event("zz", "review_passed", "stale", event_type="review_result")
    _, events = load_store(synthetic_store, verify_anchor=False)
    from validate_events import event_digest

    illegal["prev_event_digest"] = event_digest(events[-1])
    with (synthetic_store / "events" / "002.yml").open("w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(illegal, fh, allow_unicode=True, sort_keys=True)
    write_anchor(synthetic_store, events + [illegal])

    with pytest.raises(WriteRefused, match="rejected events already on disk"):
        derive_snapshot(synthetic_store)
    # Diagnostic mode may still inspect it.
    assert derive_snapshot(synthetic_store, allow_rejected=True)["rejected_events"]


def test_repair_anchor_refuses_a_transition_invalid_sequence(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    illegal = make_event("zz", "review_passed", "stale", event_type="review_result")
    _, events = load_store(synthetic_store, verify_anchor=False)
    from validate_events import event_digest

    illegal["prev_event_digest"] = event_digest(events[-1])
    with (synthetic_store / "events" / "002.yml").open("w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(illegal, fh, allow_unicode=True, sort_keys=True)
    (synthetic_store / "integrity" / "head.json").unlink()

    with pytest.raises(WriteRefused, match="transition-invalid"):
        repair_anchor(synthetic_store)


def test_repair_anchor_refuses_a_mixed_learner_store(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    intruder = make_event("zz", "introduced", "classroom_passed", student_ref="other_learner")
    _, events = load_store(synthetic_store, verify_anchor=False)
    from validate_events import event_digest

    intruder["prev_event_digest"] = event_digest(events[-1])
    with (synthetic_store / "events" / "002.yml").open("w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(intruder, fh, allow_unicode=True, sort_keys=True)
    (synthetic_store / "integrity" / "head.json").unlink()

    with pytest.raises(WriteRefused, match="store binding|invalid store"):
        repair_anchor(synthetic_store)


# --- store metadata --------------------------------------------------------


def test_store_id_must_match_the_canonical_pattern(tmp_path):
    store = tmp_path / "s"
    store.mkdir()
    with (store / "store_meta.yml").open("w", encoding="utf-8") as fh:
        yaml.safe_dump(
            {
                "schema_version": "citystate.math_mentor.learning_store_meta.v1",
                "store_id": "X",
                "bound_student_ref": "fixture_alias_a",
                "bound_epoch": EPOCH,
            },
            fh,
        )
    with pytest.raises(WriteRefused, match="does not match"):
        read_store_meta(store)


def test_store_epoch_must_equal_the_package_canonical_epoch(tmp_path):
    store = tmp_path / "s"
    store.mkdir()
    with (store / "store_meta.yml").open("w", encoding="utf-8") as fh:
        yaml.safe_dump(
            {
                "schema_version": "citystate.math_mentor.learning_store_meta.v1",
                "store_id": "synthetic-store-0002",
                "bound_student_ref": "fixture_alias_a",
                "bound_epoch": "learning-state-epoch-v1",
            },
            fh,
        )
    with pytest.raises(WriteRefused, match="canonical epoch"):
        read_store_meta(store)


def test_metadata_edit_after_events_is_detected(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    meta_path = synthetic_store / "store_meta.yml"
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
    meta["store_id"] = "synthetic-store-0009"
    with meta_path.open("w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(meta, fh, sort_keys=True)
    with pytest.raises(WriteRefused, match="store binding changed"):
        load_store(synthetic_store)


def test_anchor_records_the_store_meta_digest(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    anchor = json.loads((synthetic_store / "integrity" / "head.json").read_text(encoding="utf-8"))
    assert anchor["store_meta_digest"] == store_meta_digest(read_store_meta(synthetic_store))


def test_canonical_epoch_is_loaded_from_epoch_yml():
    assert CANONICAL_EPOCH == EPOCH


# --- blocked / stale evidence ----------------------------------------------


def test_bare_block_event_is_rejected():
    events = reach_classroom_passed() + [
        make_event("b", "classroom_passed", "blocked", blocker_evidence=None),
    ]
    result = reduce_events(events, EPOCH)
    assert "requires blocker_evidence" in reasons(result)


def test_blocker_evidence_blocked_from_must_match_transition():
    events = reach_classroom_passed() + [
        make_event(
            "b", "classroom_passed", "blocked",
            blocker_evidence={
                "blocker_kind": "missing_evidence",
                "blocker_summary_or_ref": "x",
                "blocked_from": "review_passed",
            },
        ),
    ]
    result = reduce_events(events, EPOCH)
    assert "must equal transition.from" in reasons(result)


def test_classroom_result_cannot_unblock():
    events = reach_classroom_passed() + [
        make_event("b", "classroom_passed", "blocked"),
        make_event("u", "blocked", "classroom_passed",
                   blocker_resolution_evidence="resolved"),
    ]
    result = reduce_events(events, EPOCH)
    assert "unblocking is Human-only" in reasons(result)


def test_review_result_cannot_unblock():
    events = reach_classroom_passed() + [
        make_event("b", "classroom_passed", "blocked"),
        make_event("u", "blocked", "classroom_passed", event_type="review_result",
                   blocker_resolution_evidence="resolved"),
    ]
    result = reduce_events(events, EPOCH)
    assert "unblocking is Human-only" in reasons(result)


def test_human_unblock_requires_explicit_override_provenance():
    events = reach_classroom_passed() + [
        make_event("b", "classroom_passed", "blocked"),
        make_event("u", "blocked", "classroom_passed", event_type="human_acceptance",
                   source_type="registered_learned_state",
                   blocker_resolution_evidence="resolved"),
    ]
    result = reduce_events(events, EPOCH)
    assert "explicit_human_override" in reasons(result)


def test_human_unblock_returns_only_to_blocked_from():
    events = reach_classroom_passed() + [
        make_event("b", "classroom_passed", "blocked"),
        unblock("u", "introduced"),
    ]
    result = reduce_events(events, EPOCH)
    assert "must return to the recorded prior status" in reasons(result)


def test_bare_stale_event_is_rejected():
    events = reach_two_review_passes() + [
        make_event("s", "review_passed", "stale", event_type="review_result",
                   stale_evidence=None),
    ]
    result = reduce_events(events, EPOCH)
    assert "requires stale_evidence.cause" in reasons(result)


def test_expiry_is_not_counted_as_a_failed_attempt():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        expire_window("s"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    state = result.snapshot[NODE]
    assert state.historical_expiry_count == 1
    assert state.historical_failure_count == 0, "an unattempted window is not a failure"


def test_failure_is_counted_as_a_failed_attempt():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        fail_review("s", "win-A"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].historical_failure_count == 1
    assert result.snapshot[NODE].historical_expiry_count == 0


def test_decay_cause_cannot_explain_leaving_review_due():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        make_event("s", "review_due", "stale", event_type="review_result",
                   stale_evidence={"cause": "retention_decay",
                                   "cause_ref_or_summary": "x"}),
    ]
    result = reduce_events(events, EPOCH)
    assert "may only be explained by" in reasons(result)


def test_review_cause_cannot_explain_leaving_review_passed():
    events = reach_two_review_passes() + [
        make_event("s", "review_passed", "stale", event_type="review_result",
                   stale_evidence={"cause": "review_failed",
                                   "cause_ref_or_summary": "x",
                                   "attempt_occurred": True}),
    ]
    result = reduce_events(events, EPOCH)
    assert "describes a review attempt" in reasons(result)


# --- failed classroom outcomes cannot be persisted --------------------------


def test_failed_exam_result_cannot_enter_the_store(synthetic_store):
    event = make_event("a", "not_seen", "introduced")
    event["classroom_evidence"] = {
        "exam_agent_result": "failed",
        "covered_subtopics": ["s1"],
        "definition_restatement": "x",
        "trap_evidence": "y",
        "tool_and_evidence_limitations": "z",
    }
    with pytest.raises(WriteRefused):
        append_event(synthetic_store, event)
    assert list((synthetic_store / "events").glob("*.yml")) == []


def test_needs_reprep_cannot_enter_the_store(synthetic_store):
    event = make_event("a", "not_seen", "introduced")
    event["classroom_evidence"] = {
        "exam_agent_result": "needs_reprep",
        "covered_subtopics": ["s1"],
        "definition_restatement": "x",
        "trap_evidence": "y",
        "tool_and_evidence_limitations": "z",
    }
    with pytest.raises(WriteRefused):
        append_event(synthetic_store, event)
    assert list((synthetic_store / "events").glob("*.yml")) == []


# --- review timestamps -----------------------------------------------------


def test_pass_before_its_window_opened_is_rejected():
    """Backdating is caught; the message may name either guard."""
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM,
                    timestamp="2026-05-01T00:00:00+00:00"),
        pass_window("w2", "win-A", timestamp="2026-04-01T00:00:00+00:00"),
    ]
    result = reduce_events(events, EPOCH)
    text = reasons(result)
    assert "strictly later than the opening" in text or "backdated event" in text


def test_pass_equal_to_its_window_opening_is_rejected():
    same = "2026-05-01T00:00:00+00:00"
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM, timestamp=same),
        pass_window("w2", "win-A", timestamp=same),
    ]
    result = reduce_events(events, EPOCH)
    assert "strictly later than the opening" in reasons(result)


def test_pass_after_its_window_opening_is_accepted():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM,
                    timestamp="2026-05-01T00:00:00+00:00"),
        pass_window("w2", "win-A", timestamp="2026-05-08T00:00:00+00:00"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].status == "review_passed"


def test_window_opening_timestamp_is_cleared_on_pass():
    result = reduce_events(reach_two_review_passes(), EPOCH)
    assert result.snapshot[NODE].active_review_window_opened_at is None


# --- CLI outcomes, asserted through the real entry point --------------------


def _cli(store: Path, event_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PACKAGE / "append_event.py"), str(store), str(event_path)],
        capture_output=True,
        text=True,
    )


def _write(tmp_path: Path, event: dict, name: str = "ev.yml") -> Path:
    path = tmp_path / name
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(event, fh, allow_unicode=True, sort_keys=True)
    return path


def test_cli_malformed_yaml_is_refused_before_commit(synthetic_store, tmp_path):
    path = tmp_path / "broken.yml"
    path.write_text("this: [unclosed\n", encoding="utf-8")
    result = _cli(synthetic_store, path)
    assert result.returncode == 1
    assert "outcome: refused_before_commit" in result.stdout
    assert "the store is unchanged" in result.stdout
    assert list((synthetic_store / "events").glob("*.yml")) == []


def test_cli_non_mapping_yaml_is_refused(synthetic_store, tmp_path):
    path = tmp_path / "list.yml"
    path.write_text("- a\n- b\n", encoding="utf-8")
    result = _cli(synthetic_store, path)
    assert result.returncode == 1
    assert "outcome: refused_before_commit" in result.stdout


def test_cli_full_success_reports_counts(synthetic_store, tmp_path):
    path = _write(tmp_path, reach_classroom_passed()[0])
    result = _cli(synthetic_store, path)
    assert result.returncode == 0, result.stderr
    assert "outcome: full_success" in result.stdout
    assert "event_count after write: 1" in result.stdout
    assert len(list((synthetic_store / "events").glob("*.yml"))) == 1


def test_cli_snapshot_pending_is_reported_through_main(
    synthetic_store, tmp_path, monkeypatch, capsys
):
    """Exercise main() itself, not just append_event, per rereview round 4."""
    from append_event import SnapshotStale
    import append_event as writer

    append_event(synthetic_store, reach_classroom_passed()[0])
    path = _write(tmp_path, reach_classroom_passed()[1])

    def failing_snapshot(store):
        raise SnapshotStale("simulated concurrent advance during publication")

    monkeypatch.setattr(writer, "write_snapshot", failing_snapshot)
    code = writer.main(["append_event.py", str(synthetic_store), str(path)])
    captured = capsys.readouterr()
    monkeypatch.undo()

    assert code == 3, "a committed event with a failed snapshot must not look like success"
    assert "outcome: event_committed_snapshot_pending" in captured.out
    assert "the event log is intact" in captured.out
    assert "the store is unchanged" not in captured.out, "must not claim the store is unchanged"
    assert "snapshot publication failed" in captured.err
    assert len(list((synthetic_store / "events").glob("*.yml"))) == 2

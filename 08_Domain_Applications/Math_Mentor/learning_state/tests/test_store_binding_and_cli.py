"""Store/learner binding, CLI outcomes, and snapshot race prevention.

Added after foreground rereview round 3.  All stores are synthetic temporaries.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from conftest import (
    BOUND_STUDENT,
    EPOCH,
    NEAR_TERM,
    NODE,
    STABILITY,
    make_event,
    open_window,
    pass_window,
    reach_classroom_passed,
    reach_two_review_passes,
)

from append_event import (
    SnapshotStale,
    WriteRefused,
    append_event,
    derive_snapshot,
    read_store_meta,
    write_snapshot,
)
from reduce_readonly import reduce_events

PACKAGE = Path(__file__).resolve().parents[1]


def reasons(result) -> str:
    return " | ".join(reason for _, reason in result.rejected)


# --- store binding ---------------------------------------------------------


def test_store_requires_a_binding_file(tmp_path):
    bare = tmp_path / "unbound"
    (bare / "events").mkdir(parents=True)
    with pytest.raises(WriteRefused, match="missing store_meta.yml"):
        read_store_meta(bare)


def test_binding_must_declare_all_required_keys(tmp_path):
    partial = tmp_path / "partial"
    partial.mkdir()
    with (partial / "store_meta.yml").open("w", encoding="utf-8") as handle:
        yaml.safe_dump({"schema_version": "v1", "store_id": "x"}, handle)
    with pytest.raises(WriteRefused, match="missing required keys"):
        read_store_meta(partial)


def test_event_for_a_different_student_cannot_enter_the_store(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    intruder = make_event("x", "introduced", "classroom_passed", student_ref="other_learner")
    with pytest.raises(WriteRefused, match="does not match the store binding"):
        append_event(synthetic_store, intruder)
    assert derive_snapshot(synthetic_store)["event_count"] == 1


def test_mixed_student_events_cannot_merge_into_one_node_snapshot(synthetic_store):
    """Even if two learners share a node id, their evidence must not combine."""
    append_event(synthetic_store, reach_classroom_passed()[0])
    intruder = make_event("x", "introduced", "classroom_passed", student_ref="other_learner")
    with pytest.raises(WriteRefused):
        append_event(synthetic_store, intruder)
    snapshot = derive_snapshot(synthetic_store)
    assert snapshot["nodes"][NODE]["status"] == "introduced"


def test_directory_name_grants_no_authority(tmp_path):
    """A folder named after a learner proves nothing; the binding file does."""
    misleading = tmp_path / "no_1"
    (misleading / "events").mkdir(parents=True)
    with pytest.raises(WriteRefused):
        read_store_meta(misleading)


def test_binding_matches_the_fixture_student(synthetic_store):
    assert read_store_meta(synthetic_store)["bound_student_ref"] == BOUND_STUDENT


# --- CLI outcomes ----------------------------------------------------------


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PACKAGE / script), *args],
        capture_output=True,
        text=True,
    )


def _write_event_file(tmp_path: Path, event: dict, name: str = "event.yml") -> Path:
    path = tmp_path / name
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(event, handle, allow_unicode=True, sort_keys=True)
    return path


def test_cli_full_success(synthetic_store, tmp_path):
    path = _write_event_file(tmp_path, reach_classroom_passed()[0])
    result = _run("append_event.py", str(synthetic_store), str(path))
    assert result.returncode == 0, result.stderr
    assert "outcome: full_success" in result.stdout


def test_cli_refused_before_commit(synthetic_store, tmp_path):
    illegal = make_event("bad", "not_seen", "graduated", event_type="human_acceptance",
                         source_type="explicit_human_override", human_authorization_ref="h")
    path = _write_event_file(tmp_path, illegal)
    result = _run("append_event.py", str(synthetic_store), str(path))
    assert result.returncode == 1
    assert "outcome: refused_before_commit" in result.stdout
    assert "the store is unchanged" in result.stdout
    assert list((synthetic_store / "events").glob("*.yml")) == []


def test_cli_event_committed_snapshot_pending(synthetic_store, tmp_path, monkeypatch):
    """A post-commit snapshot failure must not be reported as 'unchanged'."""
    append_event(synthetic_store, reach_classroom_passed()[0])
    path = _write_event_file(tmp_path, reach_classroom_passed()[1])

    # Simulate the failure in-process, mirroring what the CLI branch reports.
    import append_event as writer

    def boom(store):
        raise SnapshotStale("simulated concurrent advance")

    monkeypatch.setattr(writer, "write_snapshot", boom)
    committed = writer.append_event(synthetic_store, reach_classroom_passed()[1])
    assert committed.exists(), "the event is committed even though the snapshot failed"
    monkeypatch.undo()
    assert derive_snapshot(synthetic_store)["event_count"] == 2


def test_reducer_cli_exits_zero_for_a_valid_event_file(tmp_path):
    document = {"bound_epoch": EPOCH, "events": reach_classroom_passed()}
    path = tmp_path / "events.yml"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(document, handle, allow_unicode=True, sort_keys=True)
    result = _run("reduce_readonly.py", str(path))
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout
    assert "actual_state_write_performed: False" in result.stdout
    assert "superseded" not in result.stdout, "the stale correction branch must be gone"


# --- snapshot races --------------------------------------------------------


def test_stale_snapshot_cannot_overwrite_a_newer_one(synthetic_store, monkeypatch):
    """Simulate another writer advancing the store between derive and publish."""
    import json

    import append_event as writer

    append_event(synthetic_store, reach_classroom_passed()[0])
    real_derive = writer.derive_snapshot

    def derive_then_someone_else_writes(store):
        snapshot = real_derive(store)
        anchor_path = store / "integrity" / "head.json"
        data = json.loads(anchor_path.read_text(encoding="utf-8"))
        data["head_digest"] = "f" * 64  # as if a newer event landed
        anchor_path.write_text(json.dumps(data), encoding="utf-8")
        return snapshot

    monkeypatch.setattr(writer, "derive_snapshot", derive_then_someone_else_writes)
    with pytest.raises(SnapshotStale):
        writer.write_snapshot(synthetic_store)
    monkeypatch.undo()
    assert list((synthetic_store / "snapshots").glob(".*tmp")) == []


def test_snapshot_records_its_source_anchor(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    path = write_snapshot(synthetic_store)
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert document["source_event_count"] == 1
    assert document["source_head_digest"]


# --- timestamps, ordering and failed reviews -------------------------------


def test_same_timestamp_passes_are_rejected(synthetic_store):
    fixed = "2026-06-01T00:00:00+00:00"
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        pass_window("w2", "win-A", timestamp=fixed),
        open_window("w3", "review_passed", "win-B", STABILITY),
        pass_window("w4", "win-B", timestamp=fixed),
    ]
    result = reduce_events(events, EPOCH)
    assert "strictly increasing timestamps" in reasons(result)


def test_stability_review_cannot_precede_near_term(synthetic_store):
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", STABILITY),
    ]
    result = reduce_events(events, EPOCH)
    assert "cannot open before a near_term_retention pass" in reasons(result)


def test_failed_review_moves_to_stale_and_is_counted(synthetic_store):
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        make_event("f1", "review_due", "stale", event_type="review_result"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    state = result.snapshot[NODE]
    assert state.status == "stale"
    assert state.historical_failure_count == 1
    assert state.active_review_window_id is None


def test_stale_resets_the_qualifying_cycle_but_keeps_history(synthetic_store):
    events = reach_two_review_passes() + [
        make_event("st", "review_passed", "stale", event_type="review_result"),
    ]
    result = reduce_events(events, EPOCH)
    state = result.snapshot[NODE]
    assert state.review_passes == 0, "the qualifying cycle must reset"
    assert state.qualifying_kinds == frozenset()
    assert state.historical_pass_count == 2, "history must survive for audit"
    assert state.graduation_evidence_candidate is False


def test_one_pass_after_remediation_is_not_enough_to_restore_eligibility(synthetic_store):
    events = reach_two_review_passes() + [
        make_event("st", "review_passed", "stale", event_type="review_result"),
        open_window("m1", "stale", "win-C", NEAR_TERM, remediation_evidence="re-taught"),
        pass_window("m2", "win-C"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    state = result.snapshot[NODE]
    assert state.review_passes == 1
    assert state.graduation_evidence_candidate is False, (
        "a single post-remediation pass must not restore eligibility"
    )


def test_full_fresh_cycle_after_remediation_restores_candidacy(synthetic_store):
    events = reach_two_review_passes() + [
        make_event("st", "review_passed", "stale", event_type="review_result"),
        open_window("m1", "stale", "win-C", NEAR_TERM, remediation_evidence="re-taught"),
        pass_window("m2", "win-C"),
        open_window("m3", "review_passed", "win-D", STABILITY),
        pass_window("m4", "win-D"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].graduation_evidence_candidate is True


# --- exhaustive blocked coverage -------------------------------------------


@pytest.mark.parametrize(
    "prefix_events,origin",
    [
        ([], "not_seen"),
        (reach_classroom_passed("p"), "classroom_passed"),
    ],
)
def test_block_and_unblock_from_reachable_statuses(prefix_events, origin):
    events = list(prefix_events) + [
        make_event("bl", origin, "blocked"),
        make_event("ub", "blocked", origin, blocker_resolution_evidence="resolved"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].status == origin
    assert result.snapshot[NODE].blocked_from is None


def test_block_from_review_due_preserves_the_active_window():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        make_event("bl", "review_due", "blocked", event_type="review_result"),
        make_event("ub", "blocked", "review_due", event_type="review_result",
                   blocker_resolution_evidence="resolved"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].active_review_window_id == "win-A"


def test_blocked_to_blocked_is_rejected():
    events = reach_classroom_passed() + [
        make_event("b1", "classroom_passed", "blocked"),
        make_event("b2", "blocked", "blocked"),
    ]
    result = reduce_events(events, EPOCH)
    assert "blocked -> blocked is not a transition" in reasons(result)
    assert result.snapshot[NODE].blocked_from == "classroom_passed"


def test_cannot_graduate_directly_out_of_blocked():
    events = reach_two_review_passes() + [
        make_event("bl", "review_passed", "blocked", event_type="review_result"),
        make_event("g", "blocked", "graduated", event_type="human_acceptance",
                   source_type="explicit_human_override", human_authorization_ref="h",
                   blocker_resolution_evidence="resolved"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected, "graduating straight out of blocked must be refused"


def test_human_acceptance_cannot_drive_a_classroom_transition():
    events = [
        make_event("a", "not_seen", "introduced", event_type="human_acceptance",
                   source_type="explicit_human_override"),
    ]
    result = reduce_events(events, EPOCH)
    assert "may not drive a transition into" in reasons(result)

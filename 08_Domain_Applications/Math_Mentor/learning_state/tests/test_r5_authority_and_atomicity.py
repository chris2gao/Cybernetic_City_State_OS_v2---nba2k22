"""Round-5: Human authority boundary, snapshot atomicity, evidence provenance.

All stores are synthetic temporaries. No real learner store is touched.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

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
    unblock,
)

from append_event import (
    SnapshotStale,
    WriteRefused,
    append_event,
    derive_snapshot,
    load_store,
    write_snapshot,
)
from reduce_readonly import reduce_events
from validate_events import validate_documents


def reasons(result) -> str:
    return " | ".join(reason for _, reason in result.rejected)


# --- Human authority boundary ----------------------------------------------


def test_reducer_can_evaluate_a_proposed_unblock():
    """Evaluation is useful and harmless; only persistence is refused."""
    events = reach_classroom_passed() + [
        make_event("b", "classroom_passed", "blocked"),
        unblock("u", "classroom_passed"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].status == "classroom_passed"
    assert result.snapshot[NODE].blocked_from is None


def test_writer_refuses_to_persist_a_valid_unblock(synthetic_store):
    for event in reach_classroom_passed():
        append_event(synthetic_store, event)
    append_event(synthetic_store, make_event("b", "classroom_passed", "blocked"))
    before = len(list((synthetic_store / "events").glob("*.yml")))
    anchor_before = (synthetic_store / "integrity" / "head.json").read_text(encoding="utf-8")

    with pytest.raises(WriteRefused, match="unsupported_pending_trusted_human_admission"):
        append_event(synthetic_store, unblock("u", "classroom_passed"))

    assert len(list((synthetic_store / "events").glob("*.yml"))) == before
    assert (synthetic_store / "integrity" / "head.json").read_text(encoding="utf-8") == anchor_before


def test_writer_refuses_to_persist_graduation(synthetic_store):
    for event in reach_classroom_passed():
        append_event(synthetic_store, event)
    before = len(list((synthetic_store / "events").glob("*.yml")))

    graduation = make_event(
        "g", "review_passed", "graduated",
        event_type="human_acceptance",
        source_type="explicit_human_override",
        human_authorization_ref="looks-official",
    )
    with pytest.raises(WriteRefused, match="unsupported_pending_trusted_human_admission"):
        append_event(synthetic_store, graduation)
    assert len(list((synthetic_store / "events").glob("*.yml"))) == before


def test_refusal_message_names_the_missing_admission_path(synthetic_store):
    for event in reach_classroom_passed():
        append_event(synthetic_store, event)
    with pytest.raises(WriteRefused) as excinfo:
        append_event(synthetic_store, make_event(
            "g", "classroom_passed", "graduated",
            event_type="human_acceptance", source_type="explicit_human_override",
            human_authorization_ref="x",
        ))
    message = str(excinfo.value)
    assert "not authority" in message, "the refusal must explain why a label is not enough"


# --- stale cause / provenance mapping --------------------------------------


@pytest.mark.parametrize(
    "cause,bad_source",
    [
        ("review_failed", "scheduler_placeholder"),
        ("review_failed", "exam_agent"),
        ("review_window_expired", "spaced_review"),
        ("review_window_expired", "exam_agent"),
        ("retention_decay", "exam_agent"),
        ("retention_decay", "scheduler_placeholder"),
        ("prerequisite_invalidated", "spaced_review"),
        ("prerequisite_invalidated", "exam_agent"),
        ("malformed_evidence", "spaced_review"),
        ("malformed_evidence", "exam_agent"),
    ],
)
def test_forbidden_stale_cause_source_combinations(cause, bad_source):
    from_status = "review_due" if cause in ("review_failed", "review_window_expired") else "review_passed"
    prefix = (
        reach_classroom_passed() + [open_window("w1", "classroom_passed", "win-A", NEAR_TERM)]
        if from_status == "review_due"
        else reach_two_review_passes()
    )
    event = make_event(
        "s", from_status, "stale", event_type="review_result", source_type=bad_source,
    )
    event["stale_evidence"] = {"cause": cause, "cause_ref_or_summary": "x"}
    event.pop("review_failure_evidence", None)
    result = reduce_events(prefix + [event], EPOCH)
    assert result.rejected, f"{cause} must not accept {bad_source}"


def test_review_failed_needs_a_structured_bundle():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
    ]
    bare = make_event("s", "review_due", "stale", event_type="review_result",
                      source_type="spaced_review")
    bare["stale_evidence"] = {"cause": "review_failed", "cause_ref_or_summary": "it went badly"}
    bare.pop("review_failure_evidence", None)
    result = reduce_events(events + [bare], EPOCH)
    assert "requires review_failure_evidence" in reasons(result)


def test_review_failure_bundle_must_cite_the_pending_window():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        fail_review("s", "win-OTHER"),
    ]
    result = reduce_events(events, EPOCH)
    assert "does not match the pending window" in reasons(result)


def test_expired_window_must_not_carry_a_failure_bundle():
    events = reach_classroom_passed() + [open_window("w1", "classroom_passed", "win-A", NEAR_TERM)]
    event = expire_window("s")
    event["review_failure_evidence"] = {
        "review_window_id": "win-A",
        "review_result": "failed",
        "failure_summary_or_ref": "x",
        "trap_or_transfer_result": "y",
    }
    result = reduce_events(events + [event], EPOCH)
    assert "must not carry review_failure_evidence" in reasons(result)


# --- transition-specific schema conditionals -------------------------------


@pytest.mark.parametrize(
    "bundle,value",
    [
        ("classroom_evidence", {"exam_agent_result": "classroom_passed", "covered_subtopics": ["s"],
                                "definition_restatement": "d", "trap_evidence": "t",
                                "tool_and_evidence_limitations": "l"}),
        ("review_evidence", {"review_window_id": "w", "review_result": "passed",
                             "definition_retention": "r", "transfer_evidence": "t"}),
        ("blocker_evidence", {"blocker_kind": "missing_evidence",
                              "blocker_summary_or_ref": "s", "blocked_from": "not_seen"}),
        ("stale_evidence", {"cause": "retention_decay", "cause_ref_or_summary": "s"}),
        ("review_failure_evidence", {"review_window_id": "w", "review_result": "failed",
                                     "failure_summary_or_ref": "s", "trap_or_transfer_result": "t"}),
    ],
)
def test_evidence_bundles_cannot_appear_on_unrelated_transitions(bundle, value):
    """An ignored bundle must never enter the append-only log."""
    event = make_event("a", "not_seen", "introduced")
    event.pop("classroom_evidence", None)
    event[bundle] = value
    report = validate_documents([event], check_chain=False)
    assert not report.ok, f"{bundle} must be rejected on not_seen -> introduced"


def test_window_fields_only_when_entering_review_due():
    event = make_event("a", "not_seen", "introduced", review_window_id="w", review_window_kind=NEAR_TERM)
    report = validate_documents([event], check_chain=False)
    assert not report.ok


def test_resolution_evidence_only_on_a_proposed_unblock():
    event = make_event("a", "not_seen", "introduced", blocker_resolution_evidence="r")
    report = validate_documents([event], check_chain=False)
    assert not report.ok


def test_the_legitimate_bundles_still_validate():
    ok_classroom = reach_classroom_passed()[1]
    assert validate_documents([ok_classroom], check_chain=False).ok
    ok_window = open_window("w", "classroom_passed", "win-A", NEAR_TERM)
    assert validate_documents([ok_window], check_chain=False).ok
    ok_fail = fail_review("s", "win-A")
    assert validate_documents([ok_fail], check_chain=False).ok


# --- snapshot atomicity ----------------------------------------------------


def test_writer_cannot_advance_while_a_snapshot_is_publishing(synthetic_store):
    """Deterministic interleave: B must not append while A holds the lock."""
    append_event(synthetic_store, reach_classroom_passed()[0])

    import append_event as writer

    inside = threading.Event()
    release = threading.Event()
    real_derive = writer.derive_snapshot

    def slow_derive(store, allow_rejected=False):
        snapshot = real_derive(store, allow_rejected=allow_rejected)
        inside.set()        # A is inside the critical section
        release.wait(5)     # hold it while B tries
        return snapshot

    writer.derive_snapshot = slow_derive
    b_result: list[str] = []

    def appender():
        inside.wait(5)
        try:
            writer.append_event(synthetic_store, reach_classroom_passed()[1])
            b_result.append("written")
        except Exception as error:
            b_result.append(type(error).__name__)
        finally:
            release.set()

    thread = threading.Thread(target=appender)
    thread.start()
    try:
        write_snapshot(synthetic_store)
    finally:
        release.set()
        thread.join(10)
        writer.derive_snapshot = real_derive

    # B either waited for the lock and then wrote, or was refused; it must never
    # have interleaved into A's critical section.
    assert b_result and b_result[0] in ("written", "StoreLocked")
    document = yaml.safe_load(
        (synthetic_store / "snapshots" / "learning_state.yml").read_text(encoding="utf-8")
    )
    anchor = json.loads((synthetic_store / "integrity" / "head.json").read_text(encoding="utf-8"))
    if b_result[0] == "written":
        # A published an H1 snapshot; the store is now at H2. The snapshot must
        # still declare which head it came from, so staleness is detectable.
        assert document["source_head_digest"] != anchor["head_digest"]
    else:
        assert document["source_head_digest"] == anchor["head_digest"]


def test_stale_snapshot_never_overwrites_a_newer_one(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    write_snapshot(synthetic_store)
    append_event(synthetic_store, reach_classroom_passed()[1])
    write_snapshot(synthetic_store)

    fresh = yaml.safe_load(
        (synthetic_store / "snapshots" / "learning_state.yml").read_text(encoding="utf-8")
    )
    assert fresh["event_count"] == 2

    import append_event as writer

    real_derive = writer.derive_snapshot

    def stale_derive(store, allow_rejected=False):
        snapshot = real_derive(store, allow_rejected=allow_rejected)
        snapshot["source_head_digest"] = "0" * 64  # pretend it came from an older head
        snapshot["event_count"] = 1
        return snapshot

    writer.derive_snapshot = stale_derive
    try:
        with pytest.raises(SnapshotStale):
            write_snapshot(synthetic_store)
    finally:
        writer.derive_snapshot = real_derive

    unchanged = yaml.safe_load(
        (synthetic_store / "snapshots" / "learning_state.yml").read_text(encoding="utf-8")
    )
    assert unchanged["event_count"] == 2, "the newer snapshot must survive"


# --- snapshot cause counters -----------------------------------------------


def test_snapshot_exposes_failure_expiry_and_decay_counts(synthetic_store):
    for event in reach_classroom_passed():
        append_event(synthetic_store, event)
    append_event(synthetic_store, open_window("w1", "classroom_passed", "win-A", NEAR_TERM))
    append_event(synthetic_store, fail_review("f", "win-A"))

    node = derive_snapshot(synthetic_store)["nodes"][NODE]
    assert node["historical_failure_count"] == 1
    assert node["historical_expiry_count"] == 0
    assert node["historical_decay_count"] == 0
    assert node["active_review_window_opened_at"] is None


def test_snapshot_exposes_expiry_separately(synthetic_store):
    for event in reach_classroom_passed():
        append_event(synthetic_store, event)
    append_event(synthetic_store, open_window("w1", "classroom_passed", "win-A", NEAR_TERM))
    append_event(synthetic_store, expire_window("e"))

    node = derive_snapshot(synthetic_store)["nodes"][NODE]
    assert node["historical_expiry_count"] == 1
    assert node["historical_failure_count"] == 0


def test_snapshot_reports_the_open_window_timestamp(synthetic_store):
    for event in reach_classroom_passed():
        append_event(synthetic_store, event)
    append_event(synthetic_store, open_window("w1", "classroom_passed", "win-A", NEAR_TERM))
    node = derive_snapshot(synthetic_store)["nodes"][NODE]
    assert node["active_review_window_id"] == "win-A"
    assert node["active_review_window_opened_at"], "an open window must expose when it opened"


# --- anchor binding --------------------------------------------------------


def test_anchor_without_store_meta_digest_fails_closed(synthetic_store):
    append_event(synthetic_store, reach_classroom_passed()[0])
    path = synthetic_store / "integrity" / "head.json"
    anchor = json.loads(path.read_text(encoding="utf-8"))
    del anchor["store_meta_digest"]
    path.write_text(json.dumps(anchor), encoding="utf-8")
    with pytest.raises(WriteRefused, match="missing store_meta_digest"):
        load_store(synthetic_store)

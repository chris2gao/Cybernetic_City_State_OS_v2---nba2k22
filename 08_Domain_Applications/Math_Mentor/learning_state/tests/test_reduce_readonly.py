"""Transition-legality tests (layer 2).

Each test pins one contract rule or one defect found by the 2026-07-19
independent review.  All fixtures are synthetic.
"""

from __future__ import annotations

from conftest import (
    EPOCH,
    NEAR_TERM,
    NODE,
    make_event,
    open_window,
    pass_window,
    reach_classroom_passed,
    reach_two_review_passes,
)

from reduce_readonly import MINIMUM_REVIEW_PASSES, reduce_events


def reasons(result) -> str:
    return " | ".join(reason for _, reason in result.rejected)


# --- legal paths -----------------------------------------------------------


def test_legal_path_reaches_classroom_passed():
    result = reduce_events(reach_classroom_passed(), EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].status == "classroom_passed"
    assert result.write_performed is False


def test_two_distinct_windows_yield_graduation_eligibility():
    result = reduce_events(reach_two_review_passes(), EPOCH)
    assert result.rejected == [], reasons(result)
    state = result.snapshot[NODE]
    assert state.review_passes == MINIMUM_REVIEW_PASSES
    assert len(state.qualifying_windows) == MINIMUM_REVIEW_PASSES
    assert state.graduation_evidence_candidate is True
    assert state.status == "review_passed"


# --- defect R4.1 / R4.2: re-entry and unblocking ---------------------------


def test_review_reentry_requires_a_new_window():
    events = reach_two_review_passes()[:4] + [
        open_window("dup", "review_passed", "win-A", NEAR_TERM),
    ]
    result = reduce_events(events, EPOCH)
    assert "already used" in reasons(result)


def test_stale_reentry_requires_remediation_evidence():
    events = reach_two_review_passes()[:4] + [
        make_event("s1", "review_passed", "stale", event_type="review_result"),
        open_window("s2", "stale", "win-C", NEAR_TERM),
    ]
    result = reduce_events(events, EPOCH)
    assert "requires remediation_evidence" in reasons(result)


def test_stale_reentry_succeeds_with_remediation_evidence():
    events = reach_two_review_passes()[:4] + [
        make_event("s1", "review_passed", "stale", event_type="review_result"),
        open_window(
            "s2", "stale", "win-C", NEAR_TERM,
            remediation_evidence="re-taught the boundary case",
        ),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].status == "review_due"


def test_unblock_returns_to_recorded_prior_status():
    events = reach_classroom_passed() + [
        make_event("b1", "classroom_passed", "blocked"),
        make_event(
            "b2", "blocked", "classroom_passed",
            blocker_resolution_evidence="prerequisite resolved",
        ),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].status == "classroom_passed"
    assert result.snapshot[NODE].blocked_from is None


def test_unblock_cannot_jump_to_a_different_status():
    events = reach_classroom_passed() + [
        make_event("b1", "classroom_passed", "blocked"),
        make_event(
            "b2", "blocked", "review_passed",
            blocker_resolution_evidence="claimed",
        ),
    ]
    result = reduce_events(events, EPOCH)
    assert "must return to the recorded prior status" in reasons(result)


def test_unblock_requires_resolution_evidence():
    events = reach_classroom_passed() + [
        make_event("b1", "classroom_passed", "blocked"),
        make_event("b2", "blocked", "classroom_passed"),
    ]
    result = reduce_events(events, EPOCH)
    assert "requires blocker_resolution_evidence" in reasons(result)


# --- defect R4.3 / R4.5: graduation is not a counter ------------------------


def test_graduation_is_never_persisted_autonomously():
    events = reach_two_review_passes() + [
        make_event(
            "g", "review_passed", "graduated",
            event_type="human_acceptance",
            source_type="explicit_human_override",
            human_authorization_ref="human:2026-07-19",
        ),
    ]
    result = reduce_events(events, EPOCH)
    assert "procedural Human gate" in reasons(result)
    assert result.snapshot[NODE].status == "review_passed"
    assert result.snapshot[NODE].graduation_evidence_candidate is True


def test_graduation_requires_distinct_windows_not_just_passes():
    """One legitimate pass is not enough, however well-evidenced it is."""
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        pass_window("w2", "win-A"),
        make_event(
            "g", "review_passed", "graduated",
            event_type="human_acceptance",
            source_type="explicit_human_override",
            human_authorization_ref="h",
        ),
    ]
    result = reduce_events(events, EPOCH)
    assert f"needs >= {MINIMUM_REVIEW_PASSES} review passes" in reasons(result)
    assert result.snapshot[NODE].graduation_evidence_candidate is False


def test_graduation_requires_human_authorization_ref():
    events = reach_two_review_passes() + [
        make_event(
            "g", "review_passed", "graduated",
            event_type="human_acceptance",
            source_type="explicit_human_override",
        ),
    ]
    result = reduce_events(events, EPOCH)
    assert "requires human_authorization_ref" in reasons(result)


# --- defect R4.4: evidence sufficiency -------------------------------------


def test_classroom_passed_requires_classroom_evidence():
    events = [
        make_event("a", "not_seen", "introduced"),
        make_event("b", "introduced", "classroom_passed", classroom_evidence=None),
    ]
    result = reduce_events(events, EPOCH)
    assert "missing required classroom_evidence" in reasons(result)


def test_classroom_passed_rejects_a_failing_exam_result():
    events = [
        make_event("a", "not_seen", "introduced"),
        make_event(
            "b", "introduced", "classroom_passed",
            classroom_evidence={
                "exam_agent_result": "failed",
                "covered_subtopics": ["s1"],
                "definition_restatement": "x",
                "trap_evidence": "y",
            },
        ),
    ]
    result = reduce_events(events, EPOCH)
    assert "must be 'classroom_passed'" in reasons(result)


def test_review_passed_requires_review_evidence():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        make_event("w2", "review_due", "review_passed", event_type="review_result",
                   review_evidence=None),
    ]
    result = reduce_events(events, EPOCH)
    assert "missing required review_evidence" in reasons(result)


def test_classroom_evidence_cannot_be_reused_as_review_pass():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        pass_window("w2", "win-A", source_type="exam_agent"),
    ]
    result = reduce_events(events, EPOCH)
    assert "classroom pass cannot be reused" in reasons(result)


def test_missing_student_ref_is_rejected():
    result = reduce_events([make_event("a", "not_seen", "introduced", student_ref=None)], EPOCH)
    assert "missing student_ref" in reasons(result)


def test_missing_provenance_keys_are_rejected():
    result = reduce_events(
        [make_event("a", "not_seen", "introduced", evidence_provenance={"source_type": "exam_agent"})],
        EPOCH,
    )
    assert "evidence_provenance missing required keys" in reasons(result)


def test_source_ref_cannot_be_counted_twice():
    events = [
        make_event("a", "not_seen", "introduced", source_ref="fixture://same"),
        make_event("b", "introduced", "classroom_passed", source_ref="fixture://same"),
    ]
    result = reduce_events(events, EPOCH)
    assert "already counted" in reasons(result)


# --- unchanged guards from v1 ----------------------------------------------


def test_epoch_mismatch_is_rejected():
    result = reduce_events(
        [make_event("a", "not_seen", "introduced", learning_state_epoch="other")], EPOCH
    )
    assert "epoch mismatch" in reasons(result)
    assert result.snapshot == {}


def test_private_identity_data_is_rejected():
    result = reduce_events([make_event("a", "not_seen", "introduced", real_name="x")], EPOCH)
    assert "private identity data" in reasons(result)


def test_duplicate_event_id_is_rejected():
    events = [make_event("a", "not_seen", "introduced"), make_event("a", "introduced", "classroom_passed")]
    result = reduce_events(events, EPOCH)
    assert "duplicate event_id" in reasons(result)


def test_stale_from_state_is_rejected():
    events = [make_event("a", "not_seen", "introduced"), make_event("b", "not_seen", "introduced")]
    result = reduce_events(events, EPOCH)
    assert "stale from-state" in reasons(result)


def test_unknown_event_type_is_rejected():
    result = reduce_events([make_event("a", "not_seen", "introduced", event_type="invented")], EPOCH)
    assert "unknown event_type" in reasons(result)

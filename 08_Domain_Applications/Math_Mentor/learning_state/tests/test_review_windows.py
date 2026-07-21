"""Review-window state model and graduation-eligibility downgrade tests.

Added after foreground rereview round 2.  The point of these tests is that
"two distinct windows" must mean two REAL, MATCHED, DIFFERENTLY-TYPED review
cycles - not two arbitrary strings.
"""

from __future__ import annotations

from conftest import (
    EPOCH,
    NEAR_TERM,
    NODE,
    STABILITY,
    make_event,
    open_window,
    pass_window,
    reach_classroom_passed,
    unblock,
    reach_two_review_passes,
)

from reduce_readonly import reduce_events


def reasons(result) -> str:
    return " | ".join(reason for _, reason in result.rejected)


# --- window matching --------------------------------------------------------


def test_pass_must_cite_the_pending_window():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        pass_window("w2", "win-DIFFERENT"),
    ]
    result = reduce_events(events, EPOCH)
    assert "does not match the pending window" in reasons(result)


def test_pass_kind_must_match_the_pending_window_kind():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        pass_window("w2", "win-A", review_window_kind=STABILITY),
    ]
    result = reduce_events(events, EPOCH)
    assert "does not match the pending window kind" in reasons(result)


def test_pass_without_an_open_window_is_rejected():
    events = reach_classroom_passed() + [
        make_event("w2", "classroom_passed", "review_passed", event_type="review_result"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected, "a pass with no pending window must be rejected"


def test_cannot_open_a_second_window_while_one_is_pending():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        open_window("w2", "review_due", "win-B", STABILITY),
    ]
    result = reduce_events(events, EPOCH)
    assert "still pending" in reasons(result) or "transition not in table" in reasons(result)


def test_matched_pass_clears_the_active_window():
    result = reduce_events(reach_two_review_passes(), EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].active_review_window_id is None
    assert result.snapshot[NODE].active_review_window_kind is None


# --- window kinds -----------------------------------------------------------


def test_two_windows_of_the_same_kind_do_not_grant_eligibility():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM),
        pass_window("w2", "win-A"),
        open_window("w3", "review_passed", "win-B", NEAR_TERM),
        pass_window("w4", "win-B"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    state = result.snapshot[NODE]
    assert state.review_passes == 2
    assert state.graduation_evidence_candidate is False, "same-kind windows must not qualify"


def test_both_required_kinds_grant_eligibility():
    result = reduce_events(reach_two_review_passes(), EPOCH)
    state = result.snapshot[NODE]
    assert state.qualifying_kinds == {NEAR_TERM, STABILITY}
    assert state.graduation_evidence_candidate is True


def test_invalid_window_kind_is_rejected():
    events = reach_classroom_passed() + [
        open_window("w1", "classroom_passed", "win-A", "made_up_kind"),
    ]
    result = reduce_events(events, EPOCH)
    assert "review_window_kind must be one of" in reasons(result)


# --- review_due authority ---------------------------------------------------


def test_review_due_requires_scheduler_provenance():
    events = reach_classroom_passed() + [
        make_event(
            "w1", "classroom_passed", "review_due",
            event_type="review_result",
            source_type="exam_agent",
            review_window_id="win-A",
            review_window_kind=NEAR_TERM,
        ),
    ]
    result = reduce_events(events, EPOCH)
    assert "scheduler-derived provenance" in reasons(result)


# --- eligibility downgrades -------------------------------------------------


def test_stale_clears_graduation_eligibility():
    events = reach_two_review_passes() + [
        make_event("st", "review_passed", "stale", event_type="review_result"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].status == "stale"
    assert result.snapshot[NODE].graduation_evidence_candidate is False


def test_blocked_clears_graduation_eligibility():
    events = reach_two_review_passes() + [
        make_event("bl", "review_passed", "blocked", event_type="review_result"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].status == "blocked"
    assert result.snapshot[NODE].graduation_evidence_candidate is False


def test_unblock_restores_eligibility_when_conditions_still_hold():
    events = reach_two_review_passes() + [
        make_event("bl", "review_passed", "blocked", event_type="review_result"),
        unblock("ub", "review_passed"),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == [], reasons(result)
    assert result.snapshot[NODE].graduation_evidence_candidate is True


def test_graduation_refused_while_a_window_is_pending():
    events = reach_two_review_passes() + [
        open_window("w7", "review_passed", "win-C", NEAR_TERM),
        make_event(
            "g", "review_due", "graduated",
            event_type="human_acceptance",
            source_type="explicit_human_override",
            human_authorization_ref="h",
        ),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected, "graduation must not be reachable from review_due"

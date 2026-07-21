"""Round-7: every accepted reducer branch advances `last_event_timestamp`.

Two acceptance branches (block, proposed unblock) used to build their own state
replacement and both omitted the timestamp, so a backdated event could be
accepted immediately after a block or an unblock.  These tests pin the invariant
on all three branches at once.

All stores are synthetic temporaries. No real learner store is touched.
"""

from __future__ import annotations

from pathlib import Path

from conftest import (
    EPOCH,
    NEAR_TERM,
    NODE,
    make_event,
    open_window,
    reach_classroom_passed,
    unblock,
)

from reduce_readonly import reduce_events

PACKAGE = Path(__file__).resolve().parents[1]

T1 = "2026-03-01T00:00:00+00:00"
T2 = "2026-03-02T00:00:00+00:00"
T3 = "2026-03-03T00:00:00+00:00"
T4 = "2026-03-04T00:00:00+00:00"


def reasons(result) -> str:
    return " | ".join(reason for _, reason in result.rejected)


def _reach_classroom_at(stamp: str) -> list[dict]:
    """classroom_passed with the second event pinned to `stamp`."""
    events = reach_classroom_passed()
    events[0]["evidence_provenance"]["evidence_timestamp"] = T1
    events[1]["evidence_provenance"]["evidence_timestamp"] = stamp
    return events


# --- the block branch ------------------------------------------------------


def test_block_advances_last_event_timestamp():
    events = _reach_classroom_at(T2) + [
        make_event("b1", "classroom_passed", "blocked", timestamp=T3)
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == []
    assert result.snapshot[NODE].status == "blocked"
    assert result.snapshot[NODE].last_event_timestamp == T3


def test_event_backdated_after_a_block_is_rejected():
    """A block at T3 followed by an event at T2 must not be accepted."""
    events = _reach_classroom_at(T2) + [
        make_event("b1", "classroom_passed", "blocked", timestamp=T3),
        unblock("u1", "classroom_passed", timestamp=T2),
    ]
    result = reduce_events(events, EPOCH)
    assert "backdated event" in reasons(result)
    # The block is still the accepted head; the backdated unblock changed nothing.
    assert result.snapshot[NODE].status == "blocked"
    assert result.snapshot[NODE].last_event_timestamp == T3


# --- the unblock branch ----------------------------------------------------


def test_proposed_unblock_advances_last_event_timestamp():
    events = _reach_classroom_at(T2) + [
        make_event("b1", "classroom_passed", "blocked", timestamp=T3),
        unblock("u1", "classroom_passed", timestamp=T4),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == []
    assert result.snapshot[NODE].status == "classroom_passed"
    assert result.snapshot[NODE].blocked_from is None
    assert result.snapshot[NODE].last_event_timestamp == T4


def test_ordinary_event_backdated_after_a_proposed_unblock_is_rejected():
    """An unblock at T4 then an ordinary event at T3 must be rejected."""
    events = _reach_classroom_at(T2) + [
        make_event("b1", "classroom_passed", "blocked", timestamp=T3),
        unblock("u1", "classroom_passed", timestamp=T4),
        open_window("w1", "classroom_passed", "win-A", NEAR_TERM, timestamp=T3),
    ]
    result = reduce_events(events, EPOCH)
    assert "backdated event" in reasons(result)
    assert result.snapshot[NODE].status == "classroom_passed"
    assert result.snapshot[NODE].last_event_timestamp == T4


# --- all accepted branches together ----------------------------------------


def test_every_accepted_branch_exposes_expected_last_event_timestamp():
    """Ordinary transition, block and unblock each publish their own stamp."""
    events = _reach_classroom_at(T2)
    ordinary = reduce_events(events, EPOCH)
    assert ordinary.rejected == []
    assert ordinary.snapshot[NODE].last_event_timestamp == T2

    blocked = reduce_events(
        events + [make_event("b1", "classroom_passed", "blocked", timestamp=T3)], EPOCH
    )
    assert blocked.rejected == []
    assert blocked.snapshot[NODE].last_event_timestamp == T3

    unblocked = reduce_events(
        events
        + [
            make_event("b1", "classroom_passed", "blocked", timestamp=T3),
            unblock("u1", "classroom_passed", timestamp=T4),
        ],
        EPOCH,
    )
    assert unblocked.rejected == []
    assert unblocked.snapshot[NODE].last_event_timestamp == T4


def test_equal_timestamp_after_block_is_still_permitted():
    """Same-session bookkeeping may repeat a stamp; only earlier is forbidden."""
    events = _reach_classroom_at(T2) + [
        make_event("b1", "classroom_passed", "blocked", timestamp=T3),
        unblock("u1", "classroom_passed", timestamp=T3),
    ]
    result = reduce_events(events, EPOCH)
    assert result.rejected == []
    assert result.snapshot[NODE].last_event_timestamp == T3

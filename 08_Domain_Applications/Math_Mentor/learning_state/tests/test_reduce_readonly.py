"""Tests for the read-only learning-state reducer.

Every test asserts a guard rail fires.  None of them writes state; the reducer
has no write path to exercise.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reduce_readonly import (  # noqa: E402
    MINIMUM_REVIEW_PASSES,
    NodeState,
    reduce_events,
)

EPOCH = "learning-state-epoch-v1"
NODE = "n_fixture_001"


def _event(event_id: str, source: str, target: str, **overrides: object) -> dict:
    event = {
        "event_id": event_id,
        "event_type": "classroom_result",
        "node_ref": {"node_id": NODE},
        "transition": {"from": source, "to": target},
        "evidence_provenance": {"source_type": "exam_agent"},
        "learning_state_epoch": EPOCH,
    }
    event.update(overrides)
    return event


def _reasons(result) -> str:
    return " | ".join(reason for _, reason in result.rejected)


def test_legal_path_reaches_classroom_passed():
    result = reduce_events(
        [_event("a", "not_seen", "introduced"), _event("b", "introduced", "classroom_passed")],
        EPOCH,
    )
    assert result.rejected == []
    assert result.snapshot[NODE] == NodeState("classroom_passed", 0, "b")
    assert result.write_performed is False


def test_reducer_never_reports_a_write():
    result = reduce_events([_event("a", "not_seen", "introduced")], EPOCH)
    assert result.write_performed is False


def test_classroom_pass_cannot_jump_to_graduated():
    events = [
        _event("a", "not_seen", "introduced"),
        _event("b", "introduced", "classroom_passed"),
        _event("c", "classroom_passed", "graduated", human_authorization_ref="h"),
    ]
    result = reduce_events(events, EPOCH)
    assert "transition not in table" in _reasons(result)
    assert result.snapshot[NODE].status == "classroom_passed"


def test_classroom_evidence_cannot_be_reused_as_review_pass():
    events = [
        _event("a", "not_seen", "introduced"),
        _event("b", "introduced", "classroom_passed"),
        _event("c", "classroom_passed", "review_due"),
        _event("d", "review_due", "review_passed"),  # source_type stays exam_agent
    ]
    result = reduce_events(events, EPOCH)
    assert "classroom pass cannot be reused" in _reasons(result)


def test_graduation_requires_minimum_review_passes():
    spaced = {"evidence_provenance": {"source_type": "spaced_review"}}
    events = [
        _event("a", "not_seen", "introduced"),
        _event("b", "introduced", "classroom_passed"),
        _event("c", "classroom_passed", "review_due"),
        _event("d", "review_due", "review_passed", **spaced),
        _event("e", "review_passed", "graduated", human_authorization_ref="h"),
    ]
    result = reduce_events(events, EPOCH)
    assert f"needs >= {MINIMUM_REVIEW_PASSES} review passes" in _reasons(result)
    assert result.snapshot[NODE].status == "review_passed"


def test_graduation_requires_human_authorization():
    spaced = {"evidence_provenance": {"source_type": "spaced_review"}}
    events = [
        _event("a", "not_seen", "introduced"),
        _event("b", "introduced", "classroom_passed"),
        _event("c", "classroom_passed", "review_due"),
        _event("d", "review_due", "review_passed", **spaced),
        _event("e", "review_passed", "review_due", **spaced),
        _event("f", "review_due", "review_passed", **spaced),
        _event("g", "review_passed", "graduated", human_authorization_ref=None),
    ]
    result = reduce_events(events, EPOCH)
    assert result.snapshot[NODE].review_passes == MINIMUM_REVIEW_PASSES
    assert "requires human_authorization_ref" in _reasons(result)
    assert result.snapshot[NODE].status == "review_passed"


def test_epoch_mismatch_is_rejected():
    result = reduce_events(
        [_event("a", "not_seen", "introduced", learning_state_epoch="other")], EPOCH
    )
    assert "epoch mismatch" in _reasons(result)
    assert result.snapshot == {}


def test_private_identity_data_is_rejected():
    result = reduce_events(
        [_event("a", "not_seen", "introduced", real_name="someone")], EPOCH
    )
    assert "private identity data" in _reasons(result)
    assert result.snapshot == {}


def test_duplicate_event_id_is_rejected():
    result = reduce_events(
        [_event("a", "not_seen", "introduced"), _event("a", "introduced", "classroom_passed")],
        EPOCH,
    )
    assert "duplicate event_id" in _reasons(result)


def test_stale_from_state_is_rejected():
    events = [
        _event("a", "not_seen", "introduced"),
        _event("b", "not_seen", "introduced"),  # snapshot already moved on
    ]
    result = reduce_events(events, EPOCH)
    assert "stale from-state" in _reasons(result)


def test_correction_supersedes_target_event():
    events = [
        _event("a", "not_seen", "introduced"),
        {
            "event_id": "fix",
            "event_type": "correction",
            "corrects_event_id": "a",
            "learning_state_epoch": EPOCH,
        },
    ]
    result = reduce_events(events, EPOCH)
    assert "superseded by a correction" in _reasons(result)
    assert result.snapshot == {}


def test_unknown_event_type_is_rejected():
    result = reduce_events(
        [_event("a", "not_seen", "introduced", event_type="invented")], EPOCH
    )
    assert "unknown event_type" in _reasons(result)


def test_fixture_file_exercises_every_guard():
    yaml = pytest.importorskip("yaml")
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "transition_guard_cases.yml"
    with fixture.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    result = reduce_events(document["events"], document["bound_epoch"])
    assert len(result.rejected) == 8
    assert result.snapshot[NODE].status == "review_passed"
    assert result.snapshot[NODE].review_passes == MINIMUM_REVIEW_PASSES

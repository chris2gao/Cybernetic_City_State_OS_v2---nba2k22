"""Tests for the structural validator and the integrity chain.

These tests deliberately overlap nothing with the transition-table tests: here
we only assert shape, privacy and chain integrity.  A structurally valid event
may still be an illegal transition, and one test pins that separation down.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reduce_readonly import reduce_events  # noqa: E402
from validate_events import (  # noqa: E402
    SCHEMA_VERSION,
    event_digest,
    validate_documents,
)

EPOCH = "learning-state-epoch-v1"


def _event(event_id: str = "ev-001", **overrides: object) -> dict:
    event = {
        "schema_version": SCHEMA_VERSION,
        "event_id": event_id,
        "event_type": "classroom_result",
        "node_ref": {"node_id": "n_fixture_001"},
        "transition": {"from": "not_seen", "to": "introduced"},
        "evidence_provenance": {"source_type": "exam_agent"},
        "learning_state_epoch": EPOCH,
    }
    event.update(overrides)
    return event


def _messages(report) -> str:
    return " | ".join(message for _, message in report.errors)


def test_wellformed_event_passes():
    report = validate_documents([_event()], check_chain=False)
    assert report.ok, _messages(report)
    assert report.checked == 1


def test_missing_required_field_is_reported():
    event = _event()
    del event["learning_state_epoch"]
    report = validate_documents([event], check_chain=False)
    assert "missing required field: learning_state_epoch" in _messages(report)


def test_wrong_schema_version_is_reported():
    report = validate_documents([_event(schema_version="something.else")], check_chain=False)
    assert "schema_version must be" in _messages(report)


def test_invalid_status_is_reported():
    report = validate_documents(
        [_event(transition={"from": "not_seen", "to": "mastered"})], check_chain=False
    )
    assert "transition.to is not a valid status" in _messages(report)


def test_invalid_source_type_is_reported():
    report = validate_documents(
        [_event(evidence_provenance={"source_type": "vibes"})], check_chain=False
    )
    assert "invalid evidence_provenance.source_type" in _messages(report)


def test_forbidden_private_field_is_reported():
    report = validate_documents([_event(real_name="someone")], check_chain=False)
    assert "forbidden private field" in _messages(report)


def test_forbidden_field_is_found_when_nested():
    report = validate_documents(
        [_event(evidence_provenance={"source_type": "exam_agent", "email": "x@y.z"})],
        check_chain=False,
    )
    assert "forbidden private field" in _messages(report)


def test_credentials_are_rejected():
    report = validate_documents([_event(api_key="secret-value")], check_chain=False)
    assert "forbidden private field" in _messages(report)


def test_correction_requires_target():
    report = validate_documents(
        [
            {
                "schema_version": SCHEMA_VERSION,
                "event_id": "fix-001",
                "event_type": "correction",
                "learning_state_epoch": EPOCH,
                "evidence_provenance": {"source_type": "explicit_human_override"},
            }
        ],
        check_chain=False,
    )
    assert "correction event requires corrects_event_id" in _messages(report)


def test_duplicate_event_id_is_reported():
    report = validate_documents([_event("dup"), _event("dup")], check_chain=False)
    assert "duplicate event_id" in _messages(report)


def test_intact_chain_validates():
    first = _event("ev-001", prev_event_digest=None)
    second = _event("ev-002", prev_event_digest=event_digest(first))
    report = validate_documents([first, second], check_chain=True)
    assert report.ok, _messages(report)


def test_tampering_with_an_earlier_event_breaks_the_chain():
    first = _event("ev-001", prev_event_digest=None)
    second = _event("ev-002", prev_event_digest=event_digest(first))
    # Someone edits the already-written first event after the fact.
    first["node_ref"] = {"node_id": "n_tampered"}
    report = validate_documents([first, second], check_chain=True)
    assert "integrity chain broken" in _messages(report)


def test_digest_ignores_the_chain_field_itself():
    base = _event("ev-001")
    with_link = dict(base, prev_event_digest="0" * 64)
    assert event_digest(base) == event_digest(with_link)


def test_digest_is_stable_across_key_order():
    a = _event("ev-001")
    b = json.loads(json.dumps(dict(reversed(list(a.items())))))
    assert event_digest(a) == event_digest(b)


def test_structural_validity_does_not_imply_legal_transition():
    """The two layers must stay independent: shape ok, semantics rejected."""
    illegal = _event("ev-001", transition={"from": "not_seen", "to": "graduated"})
    report = validate_documents([illegal], check_chain=False)
    assert report.ok, _messages(report)

    result = reduce_events([illegal], EPOCH)
    assert result.accepted == []
    assert "transition not in table" in " ".join(reason for _, reason in result.rejected)

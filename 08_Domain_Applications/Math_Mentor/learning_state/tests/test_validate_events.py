"""Structural-validity tests (layer 1) and the layer separation itself."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import EPOCH, SCHEMA_VERSION, make_event

from reduce_readonly import reduce_events
from validate_events import event_digest, validate_documents


def messages(report) -> str:
    return " | ".join(message for _, message in report.errors)


def test_wellformed_event_passes():
    report = validate_documents([make_event("a", "not_seen", "introduced")], check_chain=False)
    assert report.ok, messages(report)
    assert report.checked == 1


def test_missing_required_field_is_reported():
    event = make_event("a", "not_seen", "introduced")
    del event["learning_state_epoch"]
    report = validate_documents([event], check_chain=False)
    assert "'learning_state_epoch' is a required property" in messages(report)


def test_v1_schema_version_is_rejected():
    report = validate_documents(
        [make_event("a", "not_seen", "introduced",
                    schema_version="citystate.math_mentor.learning_event.v1")],
        check_chain=False,
    )
    assert "was expected" in messages(report)


def test_correction_is_explicitly_unsupported():
    """R4.6: the v1 correction path was half-working; v2 refuses it by name."""
    report = validate_documents(
        [make_event("a", "not_seen", "introduced", event_type="correction")],
        check_chain=False,
    )
    assert "unsupported_pending_contract" in messages(report)


def test_missing_student_ref_is_reported():
    report = validate_documents(
        [make_event("a", "not_seen", "introduced", student_ref=None)], check_chain=False
    )
    assert "student_ref" in messages(report)


def test_missing_provenance_keys_are_reported():
    report = validate_documents(
        [make_event("a", "not_seen", "introduced",
                    evidence_provenance={"source_type": "exam_agent"})],
        check_chain=False,
    )
    text = messages(report)
    assert "'source_ref' is a required property" in text
    assert "'evidence_timestamp' is a required property" in text
    assert "'evidence_limitations' is a required property" in text


def test_invalid_status_is_reported():
    report = validate_documents(
        [make_event("a", "not_seen", "mastered")], check_chain=False
    )
    assert "transition/to" in messages(report)


def test_invalid_source_type_is_reported():
    report = validate_documents(
        [make_event("a", "not_seen", "introduced", source_type="vibes")], check_chain=False
    )
    assert "source_type" in messages(report)


def test_forbidden_private_field_is_reported():
    report = validate_documents(
        [make_event("a", "not_seen", "introduced", real_name="someone")], check_chain=False
    )
    assert "forbidden private field" in messages(report)


def test_forbidden_field_is_found_when_nested():
    event = make_event("a", "not_seen", "introduced")
    event["evidence_provenance"]["email"] = "x@y.z"
    report = validate_documents([event], check_chain=False)
    assert "forbidden private field" in messages(report)


def test_credentials_are_rejected():
    report = validate_documents(
        [make_event("a", "not_seen", "introduced", api_key="secret")], check_chain=False
    )
    assert "forbidden private field" in messages(report)


def test_duplicate_event_id_is_reported():
    report = validate_documents(
        [make_event("dup", "not_seen", "introduced"), make_event("dup", "introduced", "classroom_passed")],
        check_chain=False,
    )
    assert "duplicate event_id" in messages(report)


# --- integrity chain -------------------------------------------------------


def test_intact_chain_validates():
    first = make_event("a", "not_seen", "introduced", prev_event_digest=None)
    second = make_event("b", "introduced", "classroom_passed", prev_event_digest=event_digest(first))
    report = validate_documents([first, second], check_chain=True)
    assert report.ok, messages(report)


def test_tampering_with_an_earlier_event_breaks_the_chain():
    first = make_event("a", "not_seen", "introduced", prev_event_digest=None)
    second = make_event("b", "introduced", "classroom_passed", prev_event_digest=event_digest(first))
    first["node_ref"] = {"node_id": "n_tampered"}
    report = validate_documents([first, second], check_chain=True)
    assert "integrity chain broken" in messages(report)


def test_chain_alone_cannot_detect_tail_truncation():
    """Documents the honest limit; the tail anchor is what covers this."""
    first = make_event("a", "not_seen", "introduced", prev_event_digest=None)
    second = make_event("b", "introduced", "classroom_passed", prev_event_digest=event_digest(first))
    assert validate_documents([first, second], check_chain=True).ok
    assert validate_documents([first], check_chain=True).ok


def test_digest_ignores_the_chain_field_itself():
    base = make_event("a", "not_seen", "introduced")
    assert event_digest(base) == event_digest(dict(base, prev_event_digest="0" * 64))


def test_digest_is_stable_across_key_order():
    a = make_event("a", "not_seen", "introduced")
    b = json.loads(json.dumps(dict(reversed(list(a.items())))))
    assert event_digest(a) == event_digest(b)


# --- layer separation ------------------------------------------------------


def test_structural_validity_does_not_imply_legal_transition():
    """Shape is fine; the reducer still refuses it. That separation is the point."""
    illegal = make_event("a", "not_seen", "graduated")
    assert validate_documents([illegal], check_chain=False).ok
    result = reduce_events([illegal], EPOCH)
    assert result.accepted == []
    assert result.rejected, "a structurally valid but illegal transition must be rejected"


def test_schema_file_matches_the_validator_version():
    schema_path = Path(__file__).resolve().parents[1] / "learning_event.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert "correction" not in schema["properties"]["event_type"]["enum"]

"""Schema enforcement through the real runtime path, and correction disablement.

Parity is no longer asserted by comparing hand-written constants to the schema:
the runtime validator now loads `learning_event.schema.json` itself, so there is
nothing to drift. What these tests check instead is that every constraint the
schema declares actually causes a rejection when an event goes through
`validate_documents`, i.e. the path the writer uses.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import EPOCH, make_event

from reduce_readonly import UNSUPPORTED_EVENT_TYPES, reduce_events
from validate_events import (
    SCHEMA_PATH,
    SCHEMA_VERSION,
    VALID_EVENT_TYPES,
    _build_schema_validator,
    validate_documents,
)

SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def messages(report) -> str:
    return " | ".join(message for _, message in report.errors)


def assert_rejected_by_both(event: dict, fragment: str = "") -> None:
    """Every negative case must fail the schema AND the runtime path."""
    jsonschema = pytest.importorskip("jsonschema")
    validator = jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.FormatChecker())
    schema_errors = list(validator.iter_errors(event))
    report = validate_documents([event], check_chain=False)
    assert schema_errors, "the JSON Schema accepted an event it should reject"
    assert not report.ok, "the runtime validator accepted an event the schema rejects"
    if fragment:
        assert fragment in messages(report)


# --- the validator really is the canonical schema --------------------------


def test_runtime_loads_the_canonical_schema_file():
    validator = _build_schema_validator()
    assert validator.schema["$id"] == SCHEMA["$id"]
    assert validator.schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION


def test_wellformed_event_passes_both():
    jsonschema = pytest.importorskip("jsonschema")
    event = make_event("a", "not_seen", "introduced")
    jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.FormatChecker()).validate(event)
    report = validate_documents([event], check_chain=False)
    assert report.ok, messages(report)


def test_schema_is_valid_draft_2020_12():
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


# --- negative cases, each checked against schema AND runtime ---------------


def test_malformed_event_id_is_rejected():
    assert_rejected_by_both(make_event("BAD ID", "not_seen", "introduced"))


def test_uppercase_student_ref_is_rejected():
    assert_rejected_by_both(make_event("a", "not_seen", "introduced", student_ref="Learner.One"))


def test_student_ref_with_spaces_is_rejected():
    assert_rejected_by_both(make_event("a", "not_seen", "introduced", student_ref="learner one"))


def test_integer_review_window_id_is_rejected():
    event = make_event("w", "classroom_passed", "review_due", review_window_id=7)
    assert_rejected_by_both(event)


def test_integer_evidence_limitations_is_rejected():
    event = make_event("a", "not_seen", "introduced")
    event["evidence_provenance"]["evidence_limitations"] = 5
    assert_rejected_by_both(event)


def test_actually_read_files_as_string_is_rejected():
    event = make_event("a", "not_seen", "introduced")
    event["evidence_provenance"]["actually_read_files"] = "one_file.yaml"
    assert_rejected_by_both(event)


def test_invalid_node_ref_field_type_is_rejected():
    event = make_event("a", "not_seen", "introduced")
    event["node_ref"]["node_id"] = 123
    assert_rejected_by_both(event)


def test_integer_human_authorization_ref_is_rejected():
    assert_rejected_by_both(make_event("a", "not_seen", "introduced", human_authorization_ref=7))


def test_date_only_timestamp_is_rejected():
    event = make_event("a", "not_seen", "introduced")
    event["evidence_provenance"]["evidence_timestamp"] = "2026-01-01"
    assert_rejected_by_both(event)


def test_null_source_ref_is_rejected():
    event = make_event("a", "not_seen", "introduced")
    event["evidence_provenance"]["source_ref"] = None
    assert_rejected_by_both(event)


def test_unexpected_nested_field_is_rejected():
    event = make_event("a", "not_seen", "introduced")
    event["node_ref"]["surprise"] = "value"
    assert_rejected_by_both(event)


def test_arbitrary_extra_top_level_field_is_rejected():
    assert_rejected_by_both(make_event("a", "not_seen", "introduced", surprise="value"))


def test_bad_prev_event_digest_is_rejected():
    assert_rejected_by_both(make_event("a", "not_seen", "introduced", prev_event_digest="nothex"))


def test_invalid_window_kind_is_rejected():
    event = make_event("w", "classroom_passed", "review_due", review_window_kind="made_up")
    assert_rejected_by_both(event)


def test_classroom_passed_requires_tool_and_evidence_limitations():
    event = make_event("b", "introduced", "classroom_passed")
    del event["classroom_evidence"]["tool_and_evidence_limitations"]
    report = validate_documents([event], check_chain=False)
    assert not report.ok


# --- timezone-free timestamps: a runtime-only rule -------------------------


def test_timezone_free_timestamp_is_rejected_by_runtime():
    """`format: date-time` accepts naive input, so the runtime adds this rule."""
    event = make_event("a", "not_seen", "introduced")
    event["evidence_provenance"]["evidence_timestamp"] = "2026-01-01T00:00:00"
    report = validate_documents([event], check_chain=False)
    assert "timezone offset" in messages(report)


# --- correction is disabled at every layer ---------------------------------


def test_correction_absent_from_schema_and_reducer():
    assert "correction" not in SCHEMA["properties"]["event_type"]["enum"]
    assert "corrects_event_id" not in SCHEMA["properties"]
    assert "correction" not in VALID_EVENT_TYPES
    assert "correction" in UNSUPPORTED_EVENT_TYPES


def test_validator_rejects_correction_with_a_policy_reason():
    report = validate_documents(
        [make_event("fix", "not_seen", "introduced", event_type="correction")], check_chain=False
    )
    assert "unsupported_pending_contract" in messages(report)


def test_correction_cannot_suppress_or_alter_another_event():
    good = make_event("a", "not_seen", "introduced")
    correction = make_event("fix", "not_seen", "introduced", event_type="correction")
    without = reduce_events([good], EPOCH)
    with_correction = reduce_events([good, correction], EPOCH)

    assert with_correction.snapshot["n_fixture_001"] == without.snapshot["n_fixture_001"]
    assert "a" in with_correction.accepted
    assert any(
        event_id == "fix" and "unsupported_pending_contract" in reason
        for event_id, reason in with_correction.rejected
    )

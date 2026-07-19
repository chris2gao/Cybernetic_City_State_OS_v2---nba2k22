"""Schema / runtime-validator parity and correction disablement.

A JSON Schema the writer does not enforce is worse than no schema, so these
tests assert that every constraint declared in learning_event.schema.json is
actually rejected by the runtime validator.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import EPOCH, make_event

from reduce_readonly import UNSUPPORTED_EVENT_TYPES, reduce_events
from validate_events import (
    ALLOWED_NESTED_KEYS,
    ALLOWED_TOP_LEVEL,
    SCHEMA_VERSION,
    VALID_EVENT_TYPES,
    VALID_SOURCE_TYPES,
    VALID_STATUSES,
    VALID_WINDOW_KINDS,
    validate_documents,
)

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "learning_event.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def messages(report) -> str:
    return " | ".join(message for _, message in report.errors)


# --- declared-vs-enforced parity -------------------------------------------


def test_schema_version_matches():
    assert SCHEMA["properties"]["schema_version"]["const"] == SCHEMA_VERSION


def test_event_type_enum_matches():
    assert set(SCHEMA["properties"]["event_type"]["enum"]) == VALID_EVENT_TYPES


def test_status_enum_matches():
    assert set(SCHEMA["$defs"]["learning_status"]["enum"]) == VALID_STATUSES


def test_source_type_enum_matches():
    declared = SCHEMA["properties"]["evidence_provenance"]["properties"]["source_type"]["enum"]
    assert set(declared) == VALID_SOURCE_TYPES


def test_window_kind_enum_matches():
    assert set(SCHEMA["properties"]["review_window_kind"]["enum"]) == VALID_WINDOW_KINDS


def test_top_level_property_set_matches():
    assert set(SCHEMA["properties"]) == ALLOWED_TOP_LEVEL
    assert SCHEMA["additionalProperties"] is False


def test_nested_property_sets_match():
    for parent, allowed in ALLOWED_NESTED_KEYS.items():
        declared = SCHEMA["properties"][parent]
        assert set(declared["properties"]) == allowed, parent
        assert declared["additionalProperties"] is False, parent


def test_schema_is_valid_draft_2020_12():
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


def test_representative_event_passes_both_schema_and_validator():
    jsonschema = pytest.importorskip("jsonschema")
    event = make_event("a", "not_seen", "introduced")
    jsonschema.Draft202012Validator(SCHEMA).validate(event)
    assert validate_documents([event], check_chain=False).ok


# --- negative parity cases --------------------------------------------------


def test_malformed_event_id_is_rejected():
    report = validate_documents([make_event("BAD ID", "not_seen", "introduced")], check_chain=False)
    assert "event_id must match" in messages(report)


def test_uppercase_student_ref_is_rejected():
    report = validate_documents(
        [make_event("a", "not_seen", "introduced", student_ref="No.1")], check_chain=False
    )
    assert "privacy-safe alias" in messages(report)


def test_student_ref_with_spaces_is_rejected():
    report = validate_documents(
        [make_event("a", "not_seen", "introduced", student_ref="learner one")], check_chain=False
    )
    assert "privacy-safe alias" in messages(report)


def test_invalid_timestamp_is_rejected():
    event = make_event("a", "not_seen", "introduced")
    event["evidence_provenance"]["evidence_timestamp"] = "yesterday"
    report = validate_documents([event], check_chain=False)
    assert "must be an ISO date-time" in messages(report)


def test_non_string_source_ref_is_rejected():
    event = make_event("a", "not_seen", "introduced")
    event["evidence_provenance"]["source_ref"] = 12345
    report = validate_documents([event], check_chain=False)
    assert "source_ref must be a string" in messages(report)


def test_arbitrary_extra_top_level_field_is_rejected():
    report = validate_documents(
        [make_event("a", "not_seen", "introduced", surprise="value")], check_chain=False
    )
    assert "unknown top-level fields" in messages(report)


def test_arbitrary_extra_nested_field_is_rejected():
    event = make_event("a", "not_seen", "introduced")
    event["node_ref"]["surprise"] = "value"
    report = validate_documents([event], check_chain=False)
    assert "unknown keys in node_ref" in messages(report)


def test_bad_prev_event_digest_is_rejected():
    report = validate_documents(
        [make_event("a", "not_seen", "introduced", prev_event_digest="nothex")], check_chain=False
    )
    assert "sha256 hex string" in messages(report)


def test_classroom_passed_requires_tool_and_evidence_limitations():
    event = make_event("b", "introduced", "classroom_passed")
    del event["classroom_evidence"]["tool_and_evidence_limitations"]
    report = validate_documents([event], check_chain=False)
    assert "tool_and_evidence_limitations is required" in messages(report)


# --- correction is disabled at every layer ---------------------------------


def test_correction_absent_from_schema_enum():
    assert "correction" not in SCHEMA["properties"]["event_type"]["enum"]
    assert "corrects_event_id" not in SCHEMA["properties"]


def test_correction_absent_from_reducer_valid_types():
    assert "correction" not in VALID_EVENT_TYPES
    assert "correction" in UNSUPPORTED_EVENT_TYPES


def test_validator_rejects_correction():
    report = validate_documents(
        [make_event("fix", "not_seen", "introduced", event_type="correction")], check_chain=False
    )
    assert "unsupported_pending_contract" in messages(report)


def test_correction_cannot_suppress_or_alter_another_event():
    """R2.round2: a correction must have NO effect on any other event."""
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

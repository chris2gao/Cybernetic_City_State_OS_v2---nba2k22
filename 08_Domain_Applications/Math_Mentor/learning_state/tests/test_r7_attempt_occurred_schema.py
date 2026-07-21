"""Round-7: `attempt_occurred` is enforced by the canonical schema, not described.

The field carried its rule in a `description` string only.  The reducer checked
two of the three cases, so a wrong value could pass canonical validation, and
`attempt_occurred` on a cause that describes no review attempt was accepted
everywhere despite having no contracted meaning.

Both layers are exercised: the canonical schema directly, and the real writer
path, so the contract cannot regress in one while the other still looks fine.

All stores are synthetic temporaries. No real learner store is touched.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from conftest import make_event, reach_classroom_passed

from append_event import WriteRefused, append_event
from validate_events import validate_documents

PACKAGE = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PACKAGE / "learning_event.schema.json"

NO_ATTEMPT_CAUSES = ["retention_decay", "prerequisite_invalidated", "malformed_evidence"]


def _validator():
    from jsonschema import Draft202012Validator, FormatChecker

    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _stale_event(cause: str, *, source_type: str, attempt: object = "omit") -> dict:
    """A structurally complete stale event with a controllable attempt flag."""
    event = make_event(
        "s1", "review_due", "stale", event_type="review_result", source_type=source_type
    )
    evidence = {"cause": cause, "cause_ref_or_summary": "synthetic cause"}
    if attempt != "omit":
        evidence["attempt_occurred"] = attempt
    event["stale_evidence"] = evidence
    if cause == "review_failed":
        event["review_failure_evidence"] = {
            "review_window_id": "win-A",
            "review_result": "failed",
            "failure_summary_or_ref": "synthetic failure",
            "trap_or_transfer_result": "synthetic trap result",
        }
    else:
        event.pop("review_failure_evidence", None)
    return event


def _errors(event: dict) -> str:
    return " | ".join(e.message for e in _validator().iter_errors(event))


# --- review_failed: required, must be true ---------------------------------


def test_review_failed_requires_attempt_occurred():
    event = _stale_event("review_failed", source_type="spaced_review", attempt="omit")
    assert "attempt_occurred" in _errors(event)


def test_review_failed_rejects_attempt_occurred_false():
    event = _stale_event("review_failed", source_type="spaced_review", attempt=False)
    assert _errors(event), "attempt_occurred: false contradicts a failed attempt"


def test_review_failed_accepts_attempt_occurred_true():
    event = _stale_event("review_failed", source_type="spaced_review", attempt=True)
    assert _errors(event) == ""


# --- review_window_expired: required, must be false ------------------------


def test_window_expired_requires_attempt_occurred():
    event = _stale_event(
        "review_window_expired", source_type="scheduler_placeholder", attempt="omit"
    )
    assert "attempt_occurred" in _errors(event)


def test_window_expired_rejects_attempt_occurred_true():
    event = _stale_event(
        "review_window_expired", source_type="scheduler_placeholder", attempt=True
    )
    assert _errors(event), "an expired window was never sat"


def test_window_expired_accepts_attempt_occurred_false():
    event = _stale_event(
        "review_window_expired", source_type="scheduler_placeholder", attempt=False
    )
    assert _errors(event) == ""


# --- the three causes that describe no attempt -----------------------------


@pytest.mark.parametrize("cause", NO_ATTEMPT_CAUSES)
@pytest.mark.parametrize("attempt", [True, False])
def test_unrelated_causes_forbid_attempt_occurred(cause: str, attempt: bool):
    """The field has no contracted meaning here, so it must be absent."""
    event = _stale_event(cause, source_type="explicit_human_override", attempt=attempt)
    assert _errors(event), f"{cause} must not carry attempt_occurred"


@pytest.mark.parametrize("cause", NO_ATTEMPT_CAUSES)
def test_unrelated_causes_are_valid_without_the_flag(cause: str):
    event = _stale_event(cause, source_type="explicit_human_override", attempt="omit")
    assert _errors(event) == ""


# --- the same contract on the real writer path -----------------------------


def _stale_after_classroom(cause: str, attempt: object) -> list[dict]:
    """Reach classroom_passed, then attempt an illegal-flag stale event."""
    events = reach_classroom_passed()
    bad = _stale_event(cause, source_type="explicit_human_override", attempt=attempt)
    bad["transition"] = {"from": "classroom_passed", "to": "stale"}
    bad["event_id"] = "s_writer"
    bad["evidence_provenance"]["source_ref"] = "fixture://s_writer"
    return events + [bad]


def test_writer_refuses_attempt_occurred_on_an_unrelated_cause(synthetic_store):
    for event in reach_classroom_passed():
        append_event(synthetic_store, event)
    bad = _stale_after_classroom("retention_decay", True)[-1]
    with pytest.raises(WriteRefused, match="attempt_occurred"):
        append_event(synthetic_store, bad)


def test_writer_refuses_wrong_attempt_value(synthetic_store):
    for event in reach_classroom_passed():
        append_event(synthetic_store, event)
    bad = _stale_event("review_failed", source_type="spaced_review", attempt=False)
    bad["transition"] = {"from": "classroom_passed", "to": "stale"}
    bad["event_id"] = "s_writer2"
    bad["evidence_provenance"]["source_ref"] = "fixture://s_writer2"
    with pytest.raises(WriteRefused):
        append_event(synthetic_store, bad)


def test_writer_refuses_missing_attempt_on_review_failed(synthetic_store):
    for event in reach_classroom_passed():
        append_event(synthetic_store, event)
    bad = _stale_event("review_failed", source_type="spaced_review", attempt="omit")
    bad["transition"] = {"from": "classroom_passed", "to": "stale"}
    bad["event_id"] = "s_writer3"
    bad["evidence_provenance"]["source_ref"] = "fixture://s_writer3"
    with pytest.raises(WriteRefused, match="attempt_occurred"):
        append_event(synthetic_store, bad)


# --- the documented example must itself be valid ---------------------------


def test_canonical_schema_md_example_shows_attempt_occurred():
    """The canonical example must not rely on later prose to be complete."""
    text = (PACKAGE.parent / "STUDENT_LEARNING_STATE_SCHEMA.md").read_text(
        encoding="utf-8"
    )
    start = text.index("### 5.1.6 Stale evidence")
    block = text[start : start + 1200]
    assert "attempt_occurred" in block, "the stale_evidence example omits the field"

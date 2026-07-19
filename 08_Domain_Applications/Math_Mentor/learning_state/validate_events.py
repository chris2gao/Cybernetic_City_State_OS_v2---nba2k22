"""Structural validator for Math Mentor learning events.

Two guarantees are deliberately kept apart:

  * this module answers "is this event well-formed?" (schema shape, privacy
    rules, integrity chain);
  * `reduce_readonly.py` answers "is this sequence of transitions legal?".

Passing here does NOT make a transition legal, and legality does not imply
authority.  Nothing in this module writes state; it returns findings.

Shape checking is delegated to the canonical `learning_event.schema.json` via
`jsonschema.Draft202012Validator` with a format checker, rather than being
re-implemented here.  An earlier version hand-rolled a subset of the schema and
claimed parity, which meant the writer silently accepted events the schema
rejected.  If the validator dependency is unavailable this module FAILS CLOSED:
a missing checker must never look like a passing check.

What remains hand-written here is only what JSON Schema cannot express:
forbidden private content, cross-event uniqueness, and the hash chain.

The integrity chain matters because the events live in a learner-bound local
store rather than in Git, so there is no commit history to prove that an earlier
event was not edited after the fact.  `prev_event_digest` gives tamper-evidence
for events that have a successor: altering one invalidates every later link.

Scope, stated honestly: the chain ALONE cannot detect modification of the newest
event or deletion of a suffix, because nothing downstream links to them.  The
tail anchor written by `append_event.py` covers that case.  Neither is Git
immutability nor a cryptographic signature - an actor able to rewrite both the
events and the anchor can defeat them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

SCHEMA_VERSION = "citystate.math_mentor.learning_event.v2"

# `correction` is intentionally absent in v2.  The v1 implementation left it
# half-working (a corrected event poisoned every later append), and a
# replay-safe compensation model must be specified in the contract before it is
# re-enabled.  Explicitly unsupported beats silently broken.
VALID_EVENT_TYPES = frozenset({"classroom_result", "review_result", "human_acceptance"})

UNSUPPORTED_EVENT_TYPES = frozenset({"correction"})

VALID_STATUSES = frozenset(
    {
        "not_seen",
        "introduced",
        "classroom_passed",
        "review_due",
        "review_passed",
        "graduated",
        "stale",
        "blocked",
    }
)

VALID_SOURCE_TYPES = frozenset(
    {
        "exam_agent",
        "spaced_review",
        "registered_learned_state",
        "explicit_human_override",
        "strict_sequence_fallback",
        "scheduler_placeholder",
    }
)

# STUDENT_LEARNING_STATE_SCHEMA.md section 2 forbids these outright.
FORBIDDEN_KEYS = frozenset(
    {
        "real_name",
        "contact_info",
        "email",
        "phone",
        "address",
        "private_notes",
        "token",
        "credential",
        "password",
        "api_key",
    }
)

SCHEMA_PATH = Path(__file__).resolve().parent / "learning_event.schema.json"

VALID_WINDOW_KINDS = frozenset({"near_term_retention", "stability_review"})


class ValidatorUnavailable(RuntimeError):
    """The canonical schema validator could not be loaded.  Fail closed."""


def _load_schema() -> dict:
    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_schema_validator():
    """Return a Draft 2020-12 validator bound to the canonical schema.

    Raises rather than degrading: a validator that silently checks less than the
    schema declares is exactly the defect this replaces.
    """
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError as error:  # pragma: no cover - environment failure path
        raise ValidatorUnavailable(
            "jsonschema is required to enforce learning_event.schema.json. "
            "Refusing to validate with a reduced hand-rolled subset."
        ) from error
    return Draft202012Validator(_load_schema(), format_checker=FormatChecker())


def _timestamp_has_timezone(value: object) -> bool:
    """RFC 3339 requires an offset; `date-time` format alone permits naive input."""
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


@dataclass
class ValidationReport:
    """Findings only.  Carries no write capability and no authority."""

    errors: list[tuple[str, str]] = field(default_factory=list)
    checked: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, event_id: str, message: str) -> None:
        self.errors.append((event_id, message))


def event_digest(event: dict) -> str:
    """Stable SHA-256 over the event with its own chain link excluded."""
    payload = {k: v for k, v in event.items() if k != "prev_event_digest"}
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def _scan_forbidden(node: Any, prefix: str = "") -> str | None:
    stack: list[tuple[str, Any]] = [(prefix, node)]
    while stack:
        path, current = stack.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                child = f"{path}.{key}" if path else str(key)
                if key.lower() in FORBIDDEN_KEYS and value not in (None, "", [], {}):
                    return child
                stack.append((child, value))
        elif isinstance(current, list):
            for index, value in enumerate(current):
                stack.append((f"{path}[{index}]", value))
    return None


def validate_event(event: dict, report: ValidationReport, validator=None) -> None:
    """Check one event.  Shape comes from the canonical schema, not from here."""
    event_id = str(event.get("event_id", "<missing-id>"))

    if validator is None:
        validator = _build_schema_validator()

    # --- 1. canonical shape, delegated to learning_event.schema.json --------
    for error in sorted(validator.iter_errors(event), key=lambda e: list(e.path)):
        location = "/".join(str(part) for part in error.path) or "<root>"
        report.error(event_id, f"schema: {location}: {error.message}")

    # --- 2. what JSON Schema cannot express --------------------------------
    # `correction` is not in the schema enum, so an event carrying it already
    # fails above; this adds the reason so the operator sees policy, not syntax.
    if event.get("event_type") in UNSUPPORTED_EVENT_TYPES:
        report.error(
            event_id,
            f"event_type {event.get('event_type')!r} is unsupported_pending_contract in v2; "
            "a replay-safe compensation model must be specified before re-enabling it",
        )

    forbidden = _scan_forbidden(event)
    if forbidden is not None:
        report.error(event_id, f"forbidden private field present at {forbidden}")

    # RFC 3339 requires an offset; the `date-time` format alone accepts naive
    # timestamps, and a retention claim without a timezone is not evidence.
    provenance = event.get("evidence_provenance")
    if isinstance(provenance, dict):
        timestamp = provenance.get("evidence_timestamp")
        if timestamp is not None and not _timestamp_has_timezone(timestamp):
            report.error(
                event_id,
                "evidence_provenance.evidence_timestamp must carry a timezone offset (RFC 3339)",
            )

    report.checked += 1


def validate_chain(events: list[dict], report: ValidationReport) -> None:
    """Verify the hash chain that substitutes for Git immutability locally."""
    expected: str | None = None
    for event in events:
        event_id = str(event.get("event_id", "<missing-id>"))
        actual = event.get("prev_event_digest")
        if actual != expected:
            report.error(
                event_id,
                f"integrity chain broken: prev_event_digest={actual!r}, expected {expected!r}",
            )
            return
        expected = event_digest(event)


def validate_documents(
    events: list[dict], check_chain: bool = True, bound_student_ref: str | None = None
) -> ValidationReport:
    report = ValidationReport()
    validator = _build_schema_validator()  # fail closed once, reuse per event
    seen: set[str] = set()
    for event in events:
        event_id = str(event.get("event_id", "<missing-id>"))
        if event_id in seen:
            report.error(event_id, "duplicate event_id within the same store")
        seen.add(event_id)
        validate_event(event, report, validator=validator)

        # A store belongs to exactly one learner.  Mixing subjects would let one
        # person's evidence advance another person's node state.
        if bound_student_ref is not None and event.get("student_ref") != bound_student_ref:
            report.error(
                event_id,
                f"student_ref {event.get('student_ref')!r} does not match the store binding "
                f"{bound_student_ref!r}; mixed-learner stores are refused",
            )
    if check_chain:
        validate_chain(events, report)
    return report


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_events.py <events.yml>", file=sys.stderr)
        return 2

    import yaml

    with Path(argv[1]).open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)

    events = list(document.get("events", []))
    report = validate_documents(events, check_chain=bool(document.get("chained", False)))

    print("STRUCTURAL VALIDATION - no state was written.")
    print(f"events checked: {report.checked}")
    if report.ok:
        print("result: ok")
        return 0
    print(f"errors: {len(report.errors)}")
    for event_id, message in report.errors:
        print(f"  - {event_id}: {message}")
    print("note: structural validity is not semantic legality; run reduce_readonly.py too.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

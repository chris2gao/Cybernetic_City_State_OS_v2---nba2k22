"""Structural validator for Math Mentor learning events.

Two guarantees are deliberately kept apart:

  * this module answers "is this event well-formed?" (schema shape, privacy
    rules, integrity chain);
  * `reduce_readonly.py` answers "is this sequence of transitions legal?".

Passing here does NOT make a transition legal, and legality does not imply
authority.  Nothing in this module writes state; it returns findings.

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
from hashlib import sha256
import json
from pathlib import Path
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

REQUIRED_TOP_LEVEL = ("schema_version", "event_id", "event_type", "learning_state_epoch")


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


def validate_event(event: dict, report: ValidationReport) -> None:
    event_id = str(event.get("event_id", "<missing-id>"))

    for key in REQUIRED_TOP_LEVEL:
        if key not in event:
            report.error(event_id, f"missing required field: {key}")

    if event.get("schema_version") != SCHEMA_VERSION:
        report.error(
            event_id, f"schema_version must be {SCHEMA_VERSION!r}, got {event.get('schema_version')!r}"
        )

    event_type = event.get("event_type")
    if event_type in UNSUPPORTED_EVENT_TYPES:
        report.error(
            event_id,
            f"event_type {event_type!r} is unsupported_pending_contract in v2; "
            "a replay-safe compensation model must be specified before re-enabling it",
        )
    elif event_type not in VALID_EVENT_TYPES:
        report.error(event_id, f"invalid event_type: {event_type!r}")

    forbidden = _scan_forbidden(event)
    if forbidden is not None:
        report.error(event_id, f"forbidden private field present at {forbidden}")

    node_ref = event.get("node_ref")
    if not isinstance(node_ref, dict) or not node_ref.get("node_id"):
        report.error(event_id, "learning event requires node_ref.node_id")

    if not event.get("student_ref"):
        report.error(event_id, "learning event requires a privacy-safe student_ref")

    transition = event.get("transition")
    if not isinstance(transition, dict):
        report.error(event_id, "learning event requires a transition object")
    else:
        for side in ("from", "to"):
            value = transition.get(side)
            if value not in VALID_STATUSES:
                report.error(event_id, f"transition.{side} is not a valid status: {value!r}")

    provenance = event.get("evidence_provenance")
    if not isinstance(provenance, dict):
        report.error(event_id, "evidence_provenance is required and must be an object")
    else:
        source_type = provenance.get("source_type")
        if source_type not in VALID_SOURCE_TYPES:
            report.error(event_id, f"invalid evidence_provenance.source_type: {source_type!r}")
        for key in ("source_ref", "evidence_timestamp", "evidence_limitations"):
            if not provenance.get(key):
                report.error(event_id, f"evidence_provenance.{key} is required")

    digest = event.get("prev_event_digest")
    if digest is not None and (not isinstance(digest, str) or len(digest) != 64):
        report.error(event_id, "prev_event_digest must be a 64-character sha256 hex string or null")

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


def validate_documents(events: list[dict], check_chain: bool = True) -> ValidationReport:
    report = ValidationReport()
    seen: set[str] = set()
    for event in events:
        event_id = str(event.get("event_id", "<missing-id>"))
        if event_id in seen:
            report.error(event_id, "duplicate event_id within the same store")
        seen.add(event_id)
        validate_event(event, report)
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

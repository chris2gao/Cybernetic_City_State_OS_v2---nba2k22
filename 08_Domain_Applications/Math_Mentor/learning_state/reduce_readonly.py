"""Read-only learning-state reducer for Math Mentor.

This module answers one question: *if these classroom events were persisted,
what would the learning state become, and which events would be rejected?*

It is deliberately inert.  It never writes learning state, learned history,
scheduler files, node YAML, or any repository/runtime state.  It has no side
effect other than returning values (the CLI prints them).  Persisting state
requires a separate Human-authorized writer task; this module is the read-only
first step of that program.

Storage note: the eventual writer stores events under the local CityState path,
never in this repository, because the repository is publicly readable and
learning traces are a sensitive profile.  This module reads fixtures/events from
an explicit path argument and holds no default write target.

Contracts implemented here:
  - `STUDENT_LEARNING_STATE_SCHEMA.md` section 4 (statuses) and section 5
    (transition table with its forbidden shortcuts);
  - `GRADUATION_CRITERIA.md` `graduation_minimum.minimum_review_passes`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import sys
from typing import Any

MINIMUM_REVIEW_PASSES = 2  # GRADUATION_CRITERIA.md graduation_minimum

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

VALID_EVENT_TYPES = frozenset(
    {"classroom_result", "review_result", "human_acceptance", "correction"}
)

# STUDENT_LEARNING_STATE_SCHEMA.md section 5.  `blocked` is reachable from any
# status and returns to a prior valid status only with evidence provenance, so
# it is handled separately rather than enumerated here.
ALLOWED_TRANSITIONS = frozenset(
    {
        ("not_seen", "introduced"),
        ("introduced", "classroom_passed"),
        ("classroom_passed", "review_due"),
        ("review_due", "review_passed"),
        ("review_passed", "review_due"),
        ("review_passed", "graduated"),
        ("review_passed", "stale"),
        ("graduated", "stale"),
        ("stale", "review_due"),
    }
)

PRIVATE_FIELD_NAMES = frozenset(
    {"real_name", "contact_info", "email", "phone", "address", "private_notes"}
)


@dataclass(frozen=True)
class NodeState:
    """Derived per-node state.  Immutable; the reducer rebuilds it each step."""

    status: str = "not_seen"
    review_passes: int = 0
    last_event_id: str | None = None


@dataclass
class ReductionResult:
    """Outcome of a dry reduction.  Carries no write capability."""

    snapshot: dict[str, NodeState] = field(default_factory=dict)
    accepted: list[str] = field(default_factory=list)
    rejected: list[tuple[str, str]] = field(default_factory=list)
    write_performed: bool = False  # always False by construction


def _reject(result: ReductionResult, event_id: str, reason: str) -> None:
    result.rejected.append((event_id, reason))


def _has_private_data(event: Any) -> str | None:
    """Return the offending key path if the event carries private identity data."""
    stack: list[tuple[str, Any]] = [("", event)]
    while stack:
        prefix, node = stack.pop()
        if isinstance(node, dict):
            for key, value in node.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                if key in PRIVATE_FIELD_NAMES and value not in (None, "", [], {}):
                    return path
                stack.append((path, value))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                stack.append((f"{prefix}[{index}]", value))
    return None


def reduce_events(events: list[dict], bound_epoch: str) -> ReductionResult:
    """Fold events into a derived snapshot, rejecting every illegal step.

    Pure function: no file, network, or state mutation of any kind.
    """
    result = ReductionResult()
    seen_ids: set[str] = set()
    corrected_ids: set[str] = set()

    # Corrections are resolved first so a corrected event never lands.
    for event in events:
        if event.get("event_type") == "correction":
            target = event.get("corrects_event_id")
            if target:
                corrected_ids.add(str(target))

    for event in events:
        event_id = str(event.get("event_id", "<missing-id>"))

        if event_id in seen_ids:
            _reject(result, event_id, "duplicate event_id")
            continue
        seen_ids.add(event_id)

        if event_id in corrected_ids:
            _reject(result, event_id, "superseded by a correction event")
            continue

        event_type = event.get("event_type")
        if event_type not in VALID_EVENT_TYPES:
            _reject(result, event_id, f"unknown event_type: {event_type!r}")
            continue

        if event.get("learning_state_epoch") != bound_epoch:
            _reject(
                result,
                event_id,
                f"epoch mismatch: {event.get('learning_state_epoch')!r} != {bound_epoch!r}",
            )
            continue

        private_path = _has_private_data(event)
        if private_path is not None:
            _reject(result, event_id, f"private identity data present at {private_path}")
            continue

        if event_type == "correction":
            result.accepted.append(event_id)
            continue

        node_ref = event.get("node_ref") or {}
        node_id = node_ref.get("node_id")
        if not node_id:
            _reject(result, event_id, "missing node_ref.node_id")
            continue

        transition = event.get("transition") or {}
        source = transition.get("from")
        target = transition.get("to")

        if target not in VALID_STATUSES or source not in VALID_STATUSES:
            _reject(result, event_id, f"invalid status in transition {source!r}->{target!r}")
            continue

        current = result.snapshot.get(node_id, NodeState())
        if current.status != source:
            _reject(
                result,
                event_id,
                f"stale from-state: snapshot has {current.status!r}, event claims {source!r}",
            )
            continue

        if target == "blocked":
            result.snapshot[node_id] = NodeState(
                status="blocked",
                review_passes=current.review_passes,
                last_event_id=event_id,
            )
            result.accepted.append(event_id)
            continue

        if (source, target) not in ALLOWED_TRANSITIONS:
            _reject(result, event_id, f"transition not in table: {source!r}->{target!r}")
            continue

        provenance = event.get("evidence_provenance") or {}
        source_type = provenance.get("source_type")

        if target == "classroom_passed" and source_type != "exam_agent":
            _reject(
                result,
                event_id,
                "classroom_passed requires evidence_provenance.source_type == 'exam_agent'",
            )
            continue

        if target == "review_passed":
            if source_type != "spaced_review":
                _reject(
                    result,
                    event_id,
                    "review_passed requires spaced_review evidence; classroom pass cannot be reused",
                )
                continue

        if target == "graduated":
            projected = current.review_passes
            if projected < MINIMUM_REVIEW_PASSES:
                _reject(
                    result,
                    event_id,
                    f"graduation needs >= {MINIMUM_REVIEW_PASSES} review passes, has {projected}",
                )
                continue
            if not event.get("human_authorization_ref"):
                _reject(result, event_id, "graduation requires human_authorization_ref")
                continue

        passes = current.review_passes + (1 if target == "review_passed" else 0)
        result.snapshot[node_id] = NodeState(
            status=target, review_passes=passes, last_event_id=event_id
        )
        result.accepted.append(event_id)

    return result


def _load_events(path: Path) -> tuple[str, list[dict]]:
    import yaml  # imported lazily so the module stays importable without PyYAML

    with path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    return str(document.get("bound_epoch", "")), list(document.get("events", []))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: reduce_readonly.py <events.yml>", file=sys.stderr)
        return 2

    bound_epoch, events = _load_events(Path(argv[1]))
    result = reduce_events(events, bound_epoch)

    print("DRY RUN - no learning state was written.")
    print(f"bound_epoch: {bound_epoch}")
    print(f"events read: {len(events)}")
    print()
    print("would-be snapshot:")
    if not result.snapshot:
        print("  (empty)")
    for node_id in sorted(result.snapshot):
        state = result.snapshot[node_id]
        print(
            f"  {node_id}: status={state.status} "
            f"review_passes={state.review_passes} via={state.last_event_id}"
        )
    print()
    print(f"accepted: {len(result.accepted)}")
    for event_id in result.accepted:
        print(f"  + {event_id}")
    print(f"rejected: {len(result.rejected)}")
    for event_id, reason in result.rejected:
        print(f"  - {event_id}: {reason}")
    print()
    print(f"actual_state_write_performed: {result.write_performed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

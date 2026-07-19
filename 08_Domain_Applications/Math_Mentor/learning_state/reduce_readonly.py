"""Read-only learning-state reducer for Math Mentor.

This module answers one question: *if these events were persisted, what would
the learning state become, and which events would be rejected?*

It is deliberately inert.  It never writes learning state, learned history,
scheduler files, node YAML, or any repository/runtime state.

Four layers are kept apart on purpose.  This module is layer 2 only:

  1. structural validity      -> validate_events.py
  2. transition legality      -> THIS MODULE
  3. semantic sufficiency     -> evidence requirements below, still mechanical
  4. Human authority          -> a procedural gate outside any code path here

Layer 4 matters: `graduation_eligible` can be computed, but no code in this
package may treat a string field as proof that a Human authorised anything.

Contracts implemented here:
  - `STUDENT_LEARNING_STATE_SCHEMA.md` sections 4, 5, 5.1 and 5.2;
  - `GRADUATION_CRITERIA.md` `graduation_minimum.minimum_review_passes`.

Epoch v2 note: the transition set and evidence requirements changed after the
2026-07-19 independent review, so the bound epoch was raised.  Events written
under the v1 epoch are not silently reinterpreted.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
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

# `correction` is absent by design.  The v1 implementation left it half-working
# (a corrected event poisoned every later append), so v2 rejects it at every
# layer rather than carrying dead semantics.  Re-enabling it requires a
# replay-safe compensation model specified in the contract first.
VALID_EVENT_TYPES = frozenset({"classroom_result", "review_result", "human_acceptance"})

UNSUPPORTED_EVENT_TYPES = frozenset({"correction"})

# Review windows are typed, so "two distinct windows" cannot be satisfied by two
# arbitrary strings of the same kind.  GRADUATION_CRITERIA requires retention
# over time, which means a near-term check AND a later stability check.
REQUIRED_REVIEW_WINDOW_KINDS = frozenset({"near_term_retention", "stability_review"})

# Entering review_due is a scheduling act; only scheduler-derived provenance may
# authorise it.  This module never writes or activates a scheduler.
REVIEW_DUE_SOURCE_TYPES = frozenset({"scheduler_placeholder"})

# STUDENT_LEARNING_STATE_SCHEMA.md section 5, including the 5.1 re-entry edges.
# `blocked` is reachable from any status and returns to the recorded prior
# status, so both directions are handled separately rather than enumerated.
ALLOWED_TRANSITIONS = frozenset(
    {
        ("not_seen", "introduced"),
        ("introduced", "classroom_passed"),
        ("classroom_passed", "review_due"),
        ("review_due", "review_passed"),
        ("review_passed", "review_due"),  # 5.1 re-entry, needs a new window
        ("stale", "review_due"),  # 5.1 re-entry, needs remediation evidence
        ("review_passed", "graduated"),
        ("review_passed", "stale"),
        ("graduated", "stale"),
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
    blocked_from: str | None = None
    counted_windows: frozenset[str] = frozenset()
    counted_window_kinds: frozenset[str] = frozenset()
    active_review_window_id: str | None = None
    active_review_window_kind: str | None = None
    latest_definition_retention: str | None = None
    latest_transfer_evidence: str | None = None
    graduation_eligible: bool = False


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


def _evidence_requirements(target: str, event: dict, state: NodeState) -> str | None:
    """Mechanical sufficiency checks. Returns a rejection reason, or None."""
    provenance = event.get("evidence_provenance") or {}
    source_type = provenance.get("source_type")

    if target == "classroom_passed":
        if source_type != "exam_agent":
            return "classroom_passed requires evidence_provenance.source_type == 'exam_agent'"
        classroom = event.get("classroom_evidence") or {}
        missing = [
            key
            for key in (
                "exam_agent_result",
                "covered_subtopics",
                "definition_restatement",
                "trap_evidence",
            )
            if not classroom.get(key)
        ]
        if missing:
            return f"classroom_passed missing required classroom_evidence: {sorted(missing)}"
        if classroom.get("exam_agent_result") != "classroom_passed":
            return "classroom_evidence.exam_agent_result must be 'classroom_passed'"

    if target == "review_due":
        if source_type not in REVIEW_DUE_SOURCE_TYPES:
            return (
                "entering review_due requires scheduler-derived provenance "
                f"(one of {sorted(REVIEW_DUE_SOURCE_TYPES)}), not {source_type!r}"
            )
        window = event.get("review_window_id")
        kind = event.get("review_window_kind")
        if not window:
            return "entering review_due requires a review_window_id"
        if kind not in REQUIRED_REVIEW_WINDOW_KINDS:
            return (
                f"review_window_kind must be one of {sorted(REQUIRED_REVIEW_WINDOW_KINDS)}, "
                f"got {kind!r}"
            )
        if window in state.counted_windows:
            return f"review_window_id {window!r} was already counted; windows must be distinct"
        if state.active_review_window_id is not None:
            return (
                f"review window {state.active_review_window_id!r} is still pending; "
                "close it before opening another"
            )
        if state.status == "stale" and not (event.get("remediation_evidence")):
            return "stale -> review_due requires remediation_evidence"

    if target == "review_passed":
        if source_type != "spaced_review":
            return "review_passed requires spaced_review evidence; classroom pass cannot be reused"
        review = event.get("review_evidence") or {}
        missing = [
            key
            for key in ("review_window_id", "review_result", "definition_retention", "transfer_evidence")
            if not review.get(key)
        ]
        if missing:
            return f"review_passed missing required review_evidence: {sorted(missing)}"
        if review.get("review_result") != "passed":
            return "review_evidence.review_result must be 'passed'"
        if state.active_review_window_id is None:
            return "review_passed requires a pending review window"
        if review.get("review_window_id") != state.active_review_window_id:
            return (
                f"review_evidence.review_window_id {review.get('review_window_id')!r} does not "
                f"match the pending window {state.active_review_window_id!r}"
            )
        if event.get("review_window_kind", state.active_review_window_kind) != state.active_review_window_kind:
            return (
                f"review_window_kind {event.get('review_window_kind')!r} does not match the "
                f"pending window kind {state.active_review_window_kind!r}"
            )

    if target == "graduated":
        if state.status != "review_passed":
            return f"graduation requires status 'review_passed', not {state.status!r}"
        if state.active_review_window_id is not None:
            return "graduation requires no pending review window"
        if state.review_passes < MINIMUM_REVIEW_PASSES:
            return (
                f"graduation needs >= {MINIMUM_REVIEW_PASSES} review passes, has {state.review_passes}"
            )
        missing_kinds = REQUIRED_REVIEW_WINDOW_KINDS - state.counted_window_kinds
        if missing_kinds:
            return f"graduation needs all required review-window kinds; missing {sorted(missing_kinds)}"
        if not state.latest_definition_retention:
            return "graduation requires definition-retention evidence at the latest review"
        if not state.latest_transfer_evidence:
            return "graduation requires transfer/trap evidence at the latest review"
        if not event.get("human_authorization_ref"):
            return "graduation requires human_authorization_ref"
        return (
            "graduation is a procedural Human gate; a deterministic reducer may compute "
            "graduation_eligible but must not persist 'graduated' autonomously"
        )

    return None


def _is_eligible(state: NodeState) -> bool:
    """Graduation eligibility.  False whenever the node is not currently sound."""
    return (
        state.status == "review_passed"
        and state.active_review_window_id is None
        and state.review_passes >= MINIMUM_REVIEW_PASSES
        and REQUIRED_REVIEW_WINDOW_KINDS <= state.counted_window_kinds
        and bool(state.latest_definition_retention)
        and bool(state.latest_transfer_evidence)
    )


def reduce_events(events: list[dict], bound_epoch: str) -> ReductionResult:
    """Fold events into a derived snapshot, rejecting every illegal step.

    Pure function: no file, network, or state mutation of any kind.
    """
    result = ReductionResult()
    seen_ids: set[str] = set()
    seen_source_refs: set[str] = set()

    for event in events:
        event_id = str(event.get("event_id", "<missing-id>"))

        if event_id in seen_ids:
            _reject(result, event_id, "duplicate event_id")
            continue
        seen_ids.add(event_id)

        event_type = event.get("event_type")
        if event_type in UNSUPPORTED_EVENT_TYPES:
            # Rejected, never applied: an unsupported correction must not be able
            # to suppress, alter or supersede any other event.
            _reject(
                result,
                event_id,
                f"event_type {event_type!r} is unsupported_pending_contract; it has no effect "
                "on any other event",
            )
            continue
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

        node_ref = event.get("node_ref") or {}
        node_id = node_ref.get("node_id")
        if not node_id:
            _reject(result, event_id, "missing node_ref.node_id")
            continue

        if not event.get("student_ref"):
            _reject(result, event_id, "missing student_ref on a learning event")
            continue

        provenance = event.get("evidence_provenance") or {}
        missing_provenance = [
            key
            for key in ("source_ref", "evidence_timestamp", "evidence_limitations")
            if not provenance.get(key)
        ]
        if missing_provenance:
            _reject(
                result,
                event_id,
                f"evidence_provenance missing required keys: {sorted(missing_provenance)}",
            )
            continue

        source_ref = str(provenance.get("source_ref"))
        if source_ref in seen_source_refs:
            _reject(result, event_id, f"source_ref {source_ref!r} already counted; cannot be reused")
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

        # --- blocked handling (schema section 5) ---------------------------
        if target == "blocked":
            # Eligibility is cleared while blocked; it is recomputed on unblock.
            blocked_state = NodeState(
                status="blocked",
                review_passes=current.review_passes,
                last_event_id=event_id,
                blocked_from=current.status,
                counted_windows=current.counted_windows,
                counted_window_kinds=current.counted_window_kinds,
                active_review_window_id=current.active_review_window_id,
                active_review_window_kind=current.active_review_window_kind,
                latest_definition_retention=current.latest_definition_retention,
                latest_transfer_evidence=current.latest_transfer_evidence,
                graduation_eligible=False,
            )
            result.snapshot[node_id] = blocked_state
            seen_source_refs.add(source_ref)
            result.accepted.append(event_id)
            continue

        if source == "blocked":
            if target != current.blocked_from:
                _reject(
                    result,
                    event_id,
                    f"unblock must return to the recorded prior status "
                    f"{current.blocked_from!r}, not {target!r}",
                )
                continue
            if not event.get("blocker_resolution_evidence"):
                _reject(result, event_id, "unblock requires blocker_resolution_evidence")
                continue
            restored = NodeState(
                status=target,
                review_passes=current.review_passes,
                last_event_id=event_id,
                blocked_from=None,
                counted_windows=current.counted_windows,
                counted_window_kinds=current.counted_window_kinds,
                active_review_window_id=current.active_review_window_id,
                active_review_window_kind=current.active_review_window_kind,
                latest_definition_retention=current.latest_definition_retention,
                latest_transfer_evidence=current.latest_transfer_evidence,
            )
            result.snapshot[node_id] = replace(
                restored, graduation_eligible=_is_eligible(restored)
            )
            seen_source_refs.add(source_ref)
            result.accepted.append(event_id)
            continue

        if (source, target) not in ALLOWED_TRANSITIONS:
            _reject(result, event_id, f"transition not in table: {source!r}->{target!r}")
            continue

        reason = _evidence_requirements(target, event, current)
        if reason is not None:
            _reject(result, event_id, reason)
            continue

        windows = current.counted_windows
        window_kinds = current.counted_window_kinds
        active_id = current.active_review_window_id
        active_kind = current.active_review_window_kind
        retention = current.latest_definition_retention
        transfer = current.latest_transfer_evidence
        passes = current.review_passes

        if target == "review_due":
            # Open a window; it stays pending until a matching pass or an
            # explicitly contracted failure/stale transition closes it.
            active_id = str(event.get("review_window_id"))
            active_kind = str(event.get("review_window_kind"))
            windows = windows | {active_id}
        elif target == "review_passed":
            # A pass counts only against the window it was matched to.
            review = event.get("review_evidence") or {}
            window_kinds = window_kinds | {str(active_kind)}
            retention = str(review.get("definition_retention"))
            transfer = str(review.get("transfer_evidence"))
            passes += 1
            active_id = None
            active_kind = None
        elif target == "stale":
            # A stale transition closes any pending window.
            active_id = None
            active_kind = None

        candidate = NodeState(
            status=target,
            review_passes=passes,
            last_event_id=event_id,
            blocked_from=None,
            counted_windows=windows,
            counted_window_kinds=window_kinds,
            active_review_window_id=active_id,
            active_review_window_kind=active_kind,
            latest_definition_retention=retention,
            latest_transfer_evidence=transfer,
        )
        result.snapshot[node_id] = replace(
            candidate, graduation_eligible=_is_eligible(candidate)
        )
        seen_source_refs.add(source_ref)
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
            f"  {node_id}: status={state.status} review_passes={state.review_passes} "
            f"windows={len(state.counted_windows)} graduation_eligible={state.graduation_eligible} "
            f"via={state.last_event_id}"
        )
    print()
    print(f"accepted: {len(result.accepted)}")
    for event_id in result.accepted:
        print(f"  + {event_id}")
    if result.superseded:
        print(f"superseded by corrections: {len(result.superseded)}")
        for event_id in result.superseded:
            print(f"  ~ {event_id}")
    print(f"rejected: {len(result.rejected)}")
    for event_id, reason in result.rejected:
        print(f"  - {event_id}: {reason}")
    print()
    print(f"actual_state_write_performed: {result.write_performed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

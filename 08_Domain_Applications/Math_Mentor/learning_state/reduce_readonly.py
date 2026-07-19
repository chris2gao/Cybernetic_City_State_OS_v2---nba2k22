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

Layer 4 matters: `graduation_evidence_candidate` can be computed, but no code in this
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
from datetime import datetime
from pathlib import Path
import sys
from typing import Any

# STUDENT_LEARNING_STATE_SCHEMA.md section 5.1.4.  `human_acceptance` is
# restricted so it cannot be used to drive arbitrary non-Human transitions.
EVENT_TYPE_TARGETS = {
    "classroom_result": frozenset({"introduced", "classroom_passed", "blocked"}),
    "review_result": frozenset({"review_due", "review_passed", "stale", "blocked"}),
    "human_acceptance": frozenset({"graduated"}),
}

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

# Contract 5.1.6.  Only two of these describe leaving `review_due`, and only one
# of those counts as a failed attempt: never sat is not the same as sat and failed.
STALE_CAUSES = frozenset(
    {
        "review_failed",
        "review_window_expired",
        "retention_decay",
        "prerequisite_invalidated",
        "malformed_evidence",
    }
)
REVIEW_DUE_STALE_CAUSES = frozenset({"review_failed", "review_window_expired"})

# Contract 5.1.7: each cause admits only the provenance that could actually
# witness it.  `exam_agent` is never valid for stale - a classroom result cannot
# testify about retention over time.
STALE_CAUSE_SOURCE_TYPES = {
    "review_failed": frozenset({"spaced_review"}),
    "review_window_expired": frozenset({"scheduler_placeholder"}),
    "retention_decay": frozenset(
        {"spaced_review", "registered_learned_state", "explicit_human_override"}
    ),
    "prerequisite_invalidated": frozenset(
        {"registered_learned_state", "explicit_human_override"}
    ),
    "malformed_evidence": frozenset({"explicit_human_override"}),
}

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
        ("review_due", "stale"),  # failed attempt or expired window
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
    last_event_id: str | None = None
    blocked_from: str | None = None

    # Currently qualifying cycle.  Cleared by `stale`: a node that decayed cannot
    # graduate on passes earned before the decay.
    qualifying_windows: frozenset[str] = frozenset()
    qualifying_kinds: frozenset[str] = frozenset()
    review_passes: int = 0
    latest_definition_retention: str | None = None
    latest_transfer_evidence: str | None = None
    last_qualifying_timestamp: str | None = None

    # Immutable audit history.  Never cleared, so decay is visible afterwards.
    historical_windows: frozenset[str] = frozenset()
    historical_pass_count: int = 0
    # Causes are counted separately: an expired window was never attempted, so
    # collapsing it into "failures" would misstate the learner's record.
    historical_failure_count: int = 0
    historical_expiry_count: int = 0
    historical_decay_count: int = 0

    active_review_window_id: str | None = None
    active_review_window_kind: str | None = None
    active_review_window_opened_at: str | None = None

    # Named "candidate" deliberately: no real scheduler authority exists yet, so
    # this is mechanical evidence, not a grant.
    graduation_evidence_candidate: bool = False


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
        if window in state.historical_windows:
            return f"review_window_id {window!r} was already used; windows must be distinct"
        if state.active_review_window_id is not None:
            return (
                f"review window {state.active_review_window_id!r} is still pending; "
                "close it before opening another"
            )
        # Ordering: the near-term check must precede the stability check within
        # the current qualifying cycle.
        if kind == "stability_review" and "near_term_retention" not in state.qualifying_kinds:
            return (
                "stability_review cannot open before a near_term_retention pass exists "
                "in the current qualifying cycle"
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
        # Retention is a claim about elapsed time, so timestamps must advance.
        stamp = _parse_timestamp((event.get("evidence_provenance") or {}).get("evidence_timestamp"))
        if stamp is None:
            return "review_passed requires an RFC 3339 timestamp with a timezone offset"
        previous = _parse_timestamp(state.last_qualifying_timestamp)
        if previous is not None and stamp <= previous:
            return (
                "qualifying review passes must have strictly increasing timestamps; "
                f"{stamp.isoformat()} does not follow {previous.isoformat()}"
            )
        # A pass cannot predate, or coincide with, the opening of the window it
        # claims to answer: retention is measured across an interval.
        opened = _parse_timestamp(state.active_review_window_opened_at)
        if opened is not None and stamp <= opened:
            return (
                f"review pass timestamp {stamp.isoformat()} must be strictly later than the "
                f"opening of its window ({opened.isoformat()})"
            )

    if target == "stale":
        # Contract 5.1.6: causes are not interchangeable.
        stale_evidence = event.get("stale_evidence") or {}
        cause = stale_evidence.get("cause")
        if cause not in STALE_CAUSES:
            return (
                f"transition into stale requires stale_evidence.cause in {sorted(STALE_CAUSES)}, "
                f"got {cause!r}"
            )
        if not stale_evidence.get("cause_ref_or_summary"):
            return "stale_evidence requires cause_ref_or_summary"
        if state.status == "review_due" and cause not in REVIEW_DUE_STALE_CAUSES:
            return (
                f"leaving review_due may only be explained by {sorted(REVIEW_DUE_STALE_CAUSES)}, "
                f"not {cause!r}"
            )
        if state.status != "review_due" and cause in REVIEW_DUE_STALE_CAUSES:
            return (
                f"cause {cause!r} describes a review attempt, but the node is in "
                f"{state.status!r}, not review_due"
            )

        permitted = STALE_CAUSE_SOURCE_TYPES.get(cause, frozenset())
        if source_type not in permitted:
            return (
                f"stale cause {cause!r} may only be witnessed by source_type in "
                f"{sorted(permitted)}, not {source_type!r}"
            )

        if cause == "review_failed":
            failure = event.get("review_failure_evidence") or {}
            missing_failure = [
                key
                for key in (
                    "review_window_id",
                    "review_result",
                    "failure_summary_or_ref",
                    "trap_or_transfer_result",
                )
                if not failure.get(key)
            ]
            if missing_failure:
                return (
                    "cause 'review_failed' requires review_failure_evidence; missing "
                    f"{sorted(missing_failure)}"
                )
            if failure.get("review_result") != "failed":
                return "review_failure_evidence.review_result must be 'failed'"
            if failure.get("review_window_id") != state.active_review_window_id:
                return (
                    f"review_failure_evidence.review_window_id "
                    f"{failure.get('review_window_id')!r} does not match the pending window "
                    f"{state.active_review_window_id!r}"
                )

        if cause == "review_window_expired" and event.get("review_failure_evidence"):
            return (
                "cause 'review_window_expired' means no attempt occurred; it must not "
                "carry review_failure_evidence"
            )

    if target == "graduated":
        if state.status != "review_passed":
            return f"graduation requires status 'review_passed', not {state.status!r}"
        if state.active_review_window_id is not None:
            return "graduation requires no pending review window"
        if state.review_passes < MINIMUM_REVIEW_PASSES:
            return (
                f"graduation needs >= {MINIMUM_REVIEW_PASSES} review passes in the current "
                f"qualifying cycle, has {state.review_passes}"
            )
        missing_kinds = REQUIRED_REVIEW_WINDOW_KINDS - state.qualifying_kinds
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
            "graduation_evidence_candidate but must not persist 'graduated' autonomously"
        )

    return None


def _is_eligible(state: NodeState) -> bool:
    """Mechanical graduation-evidence candidacy.

    False whenever the node is not currently sound.  This is NOT a grant: it
    reports that the evidence pattern is present, while the decision remains a
    Human gate and no scheduler authority exists yet.
    """
    return (
        state.status == "review_passed"
        and state.active_review_window_id is None
        and state.review_passes >= MINIMUM_REVIEW_PASSES
        and REQUIRED_REVIEW_WINDOW_KINDS <= state.qualifying_kinds
        and bool(state.latest_definition_retention)
        and bool(state.latest_transfer_evidence)
    )


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


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

        # --- event-type / transition constraints (contract 5.1.4) ----------
        # Unblocking is Human-only, and starting at `blocked` is NOT a licence to
        # skip the event-type check.  An earlier version exempted unblocking from
        # this rule, which let classroom_result and review_result unblock a node.
        # `blocked -> blocked` is not an unblock at all; reject it on its own
        # terms so the message names the real problem rather than the Human-only
        # rule that would otherwise fire first.
        if source == "blocked" and target == "blocked":
            recorded = result.snapshot.get(node_id, NodeState()).blocked_from
            _reject(
                result,
                event_id,
                "blocked -> blocked is not a transition; a further blocker must not "
                f"overwrite blocked_from={recorded!r}",
            )
            continue

        unblocking = source == "blocked"
        if unblocking:
            if event_type != "human_acceptance":
                _reject(
                    result,
                    event_id,
                    f"unblocking is Human-only: event_type {event_type!r} may not unblock a node",
                )
                continue
            if (event.get("evidence_provenance") or {}).get(
                "source_type"
            ) != "explicit_human_override":
                _reject(
                    result,
                    event_id,
                    "unblocking requires evidence_provenance.source_type == "
                    "'explicit_human_override'",
                )
                continue
            if target == "graduated":
                _reject(result, event_id, "cannot graduate directly out of a blocked state")
                continue
        else:
            allowed_targets = EVENT_TYPE_TARGETS.get(event_type, frozenset())
            if target not in allowed_targets:
                _reject(
                    result,
                    event_id,
                    f"event_type {event_type!r} may not drive a transition into {target!r}",
                )
                continue

        # --- blocked handling (schema section 5) ---------------------------
        if target == "blocked":
            # Contract 5.1.5: a bare `-> blocked` is not acceptable.
            blocker = event.get("blocker_evidence") or {}
            missing_blocker = [
                key
                for key in ("blocker_kind", "blocker_summary_or_ref", "blocked_from")
                if not blocker.get(key)
            ]
            if missing_blocker:
                _reject(
                    result,
                    event_id,
                    f"transition into blocked requires blocker_evidence; missing {sorted(missing_blocker)}",
                )
                continue
            if blocker.get("blocked_from") != source:
                _reject(
                    result,
                    event_id,
                    f"blocker_evidence.blocked_from {blocker.get('blocked_from')!r} must equal "
                    f"transition.from {source!r}",
                )
                continue
            if current.status == "blocked":
                # Overwriting blocked_from would lose the original status and the
                # node could never be restored correctly.
                _reject(
                    result,
                    event_id,
                    "blocked -> blocked is not a transition; a further blocker must not "
                    f"overwrite blocked_from={current.blocked_from!r}",
                )
                continue
            # Candidacy is cleared while blocked; it is recomputed on unblock.
            result.snapshot[node_id] = replace(
                current,
                status="blocked",
                last_event_id=event_id,
                blocked_from=current.status,
                graduation_evidence_candidate=False,
            )
            seen_source_refs.add(source_ref)
            result.accepted.append(event_id)
            continue

        if unblocking:
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
            restored = replace(
                current, status=target, last_event_id=event_id, blocked_from=None
            )
            result.snapshot[node_id] = replace(
                restored, graduation_evidence_candidate=_is_eligible(restored)
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

        updated = replace(current, status=target, last_event_id=event_id, blocked_from=None)

        if target == "review_due":
            # Open a window; it stays pending until a matching pass or an
            # explicitly contracted failure/expiry closes it.
            window = str(event.get("review_window_id"))
            updated = replace(
                updated,
                active_review_window_id=window,
                active_review_window_kind=str(event.get("review_window_kind")),
                active_review_window_opened_at=str(
                    (event.get("evidence_provenance") or {}).get("evidence_timestamp")
                ),
                qualifying_windows=updated.qualifying_windows | {window},
                historical_windows=updated.historical_windows | {window},
            )
        elif target == "review_passed":
            # A pass counts only against the window it was matched to.
            review = event.get("review_evidence") or {}
            stamp = (event.get("evidence_provenance") or {}).get("evidence_timestamp")
            updated = replace(
                updated,
                qualifying_kinds=updated.qualifying_kinds | {str(current.active_review_window_kind)},
                review_passes=updated.review_passes + 1,
                historical_pass_count=updated.historical_pass_count + 1,
                latest_definition_retention=str(review.get("definition_retention")),
                latest_transfer_evidence=str(review.get("transfer_evidence")),
                last_qualifying_timestamp=str(stamp),
                active_review_window_id=None,
                active_review_window_kind=None,
                active_review_window_opened_at=None,
            )
        elif target == "stale":
            # Decay closes the pending window AND resets the qualifying cycle.
            # History is preserved so the decay itself remains auditable, with
            # each cause counted separately.
            cause = (event.get("stale_evidence") or {}).get("cause")
            updated = replace(
                updated,
                qualifying_windows=frozenset(),
                qualifying_kinds=frozenset(),
                review_passes=0,
                latest_definition_retention=None,
                latest_transfer_evidence=None,
                last_qualifying_timestamp=None,
                historical_failure_count=updated.historical_failure_count
                + (1 if cause == "review_failed" else 0),
                historical_expiry_count=updated.historical_expiry_count
                + (1 if cause == "review_window_expired" else 0),
                historical_decay_count=updated.historical_decay_count
                + (1 if cause in ("retention_decay", "prerequisite_invalidated") else 0),
                active_review_window_id=None,
                active_review_window_kind=None,
                active_review_window_opened_at=None,
            )

        result.snapshot[node_id] = replace(
            updated, graduation_evidence_candidate=_is_eligible(updated)
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
            f"  {node_id}: status={state.status} "
            f"qualifying_passes={state.review_passes} "
            f"qualifying_kinds={sorted(state.qualifying_kinds)} "
            f"historical_passes={state.historical_pass_count} "
            f"graduation_evidence_candidate={state.graduation_evidence_candidate} "
            f"via={state.last_event_id}"
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

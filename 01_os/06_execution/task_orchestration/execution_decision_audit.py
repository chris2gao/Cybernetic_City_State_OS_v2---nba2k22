"""Lightweight, Host-owned gateway admission/denial events and read-only summaries.

No telemetry platform, secret capture, model scoring or new Workflow stage.
Counts describe mediated tool attempts only; bypassed Shell/GUI calls are invisible.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable
from uuid import uuid4


@dataclass(frozen=True)
class GatewayEvent:
    event_id: str
    timestamp_utc: str
    model_ref: str
    task_id: str
    session_ref: str
    mode: str
    route: str
    operation: str
    decision: str                # ADMITTED or DENIED
    reason_code: str             # APPROVED for admission, structured code otherwise
    cause: str                   # MODEL_POLICY / HUMAN_PENDING / SYSTEM_GAP / HOST_STATE / NONE

    @classmethod
    def create(cls, *, model_ref: str, task_id: str, session_ref: str,
               mode: str, route: str, operation: str, decision: str,
               reason_code: str, cause: str) -> "GatewayEvent":
        if decision not in {"ADMITTED", "DENIED"}:
            raise ValueError("Invalid admission decision")
        if cause not in {"MODEL_POLICY", "HUMAN_PENDING", "SYSTEM_GAP", "HOST_STATE", "NONE"}:
            raise ValueError("Invalid refusal category")
        return cls(str(uuid4()), datetime.now(timezone.utc).isoformat(),
                   model_ref, task_id, session_ref, mode, route, operation,
                   decision, reason_code, cause)

    def as_record(self) -> dict:
        return asdict(self)


def summarize(events: Iterable[GatewayEvent], *, model_ref: str | None = None,
              task_id: str | None = None, route: str | None = None,
              min_attempts: int = 10, conflict_rate_threshold: float = 0.3,
              same_reason_threshold: int = 3) -> dict:
    """Advisory review signal, never a model ban or automatic permission change.

    Thresholds are explicitly supplied Human review policy, not evidence that
    a model is inherently incompatible with OS. Use a bounded time/task cohort
    from durable Host audit records for longitudinal analysis.
    """
    if min_attempts < 1 or same_reason_threshold < 1 or not 0 <= conflict_rate_threshold <= 1:
        raise ValueError("Invalid aggregation thresholds")
    selected: list[GatewayEvent] = []
    seen: set[str] = set()
    for event in events:
        if ((model_ref is not None and event.model_ref != model_ref)
                or (task_id is not None and event.task_id != task_id)
                or (route is not None and event.route != route)):
            continue
        if event.event_id in seen:
            continue
        seen.add(event.event_id)
        selected.append(event)
    total = len(selected)
    denied = [e for e in selected if e.decision == "DENIED"]
    conflict = [e for e in denied if e.cause == "MODEL_POLICY"]
    by_cause: dict[str, int] = {}
    repeated: dict[str, int] = {}
    for e in denied:
        by_cause[e.cause] = by_cause.get(e.cause, 0) + 1
    for e in conflict:
        repeated[e.reason_code] = repeated.get(e.reason_code, 0) + 1
    highest_repeat = max(repeated.values(), default=0)
    rate = len(conflict) / total if total else None
    insufficient = total < min_attempts
    return {
        "attempts": total, "admitted": total - len(denied),
        "denied": len(denied), "policy_denials": len(conflict),
        "denial_rate": len(denied) / total if total else None,
        "policy_denial_rate": rate, "by_cause": by_cause,
        "policy_reasons": repeated,
        "signal": ("INSUFFICIENT_SAMPLE" if insufficient else
                   "REVIEW_MODEL_OS_FIT" if (
                       rate is not None and rate >= conflict_rate_threshold
                       or highest_repeat >= same_reason_threshold) else
                   "NO_CONFLICT_SIGNAL"),
        "interpretation": ("Advisory only; distinguish model behavior from "
                           "unapproved prototype, missing capability, and Host authorization."),
    }

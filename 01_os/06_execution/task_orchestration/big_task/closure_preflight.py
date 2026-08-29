#!/usr/bin/env python3
"""Decide whether a packet can be dispatched as one big task, and whether a
proposed pause is internal continuation or a genuine stop.

Two questions, one module, because they are the same question at two times.
Before dispatch: is everything this task will need already closed, so that it
does not have to come back and ask? During execution: is this particular reason
to pause one of the things it was supposed to handle itself?

The validator reports. It authorizes nothing. "This packet is closable" does not
mean any action is permitted; authority still comes only from the current Human
instruction and the canonical protocol.

Exit codes: 0 closable / internal continuation, 1 not closable / genuine stop,
3 input or parse error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

CONTRACT = "01_os/03_mechanisms/task_orchestration/大任务与长时执行契约_v1.yml"

INTERNAL_CONTINUATION = frozenset(
    {
        "deterministic_in_scope_construction",
        "required_validation_and_test_execution",
        "deterministic_repair_of_a_failure_this_task_caused",
        "evidence_and_receipt_update",
        "private_runtime_cleanup",
        "task_branch_commit",
        "task_branch_push",
        "completion_pointer_closure",
    }
)

GENUINE_STOP = frozenset(
    {
        "new_load_bearing_semantic_choice",
        "scope_escape_beyond_allowed_changed_paths",
        "protected_action_not_already_covered_by_current_authority",
        "safety_privacy_secret_or_credential_boundary",
        "destructive_git_or_history_rewrite",
        "runtime_or_scheduler_activation",
        "human_relay_required_to_reach_another_independent_model",
        "evidence_cannot_support_the_claim",
    }
)

INTERNAL = "internal_continuation"
STOP = "genuine_stop"
UNRECOGNIZED = "unrecognized_reason_treated_as_stop"

TERMINAL_LIFECYCLE_STATES = frozenset(
    {
        "verified_on_demand",
        "integrated_and_verified_on_demand",
        "deferred",
        "excluded",
    }
)

OPEN_LIFECYCLE_STATES = frozenset(
    {
        "research_only",
        "candidate_pending_validation",
        "candidate_ready_for_independent_review",
    }
)

# What the packet must declare is the lifecycle value this task will actually
# write when it finishes — not proof that the value is a closing one. A task
# that correctly ends as a review-ready candidate ends on an open state, and its
# group stays in the working set until review closes it. Requiring a terminal
# value here would force every implementation task to either lie or self-accept.
DECLARABLE_LIFECYCLE_STATES = TERMINAL_LIFECYCLE_STATES | OPEN_LIFECYCLE_STATES


class PreflightError(Exception):
    """Raised when the input cannot be read as a packet."""


def classify_pause(reason: str) -> str:
    """Classify one proposed pause.

    An unrecognized reason is treated as a stop. Failing closed here costs one
    Human round trip; failing open costs an unauthorized action.
    """
    value = (reason or "").strip()
    if value in INTERNAL_CONTINUATION:
        return INTERNAL
    if value in GENUINE_STOP:
        return STOP
    return UNRECOGNIZED


def _packet_body(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise PreflightError("packet_not_a_mapping")
    body = data.get("task_packet", data)
    if not isinstance(body, dict):
        raise PreflightError("task_packet_not_a_mapping")
    return body


def derive_closure(packet: dict[str, Any]) -> dict[str, Any]:
    """Map an ordinary section-7 task packet onto the eight closure fields.

    Deliberately derived rather than demanded as a new schema block: every value
    below is already fixed somewhere in the packet, so requiring authors to
    restate it would add a migration and a second place to be wrong. An explicit
    `big_task_closure` block, when present, wins.
    """
    explicit = packet.get("big_task_closure")
    explicit = explicit if isinstance(explicit, dict) else {}

    publisher = packet.get("publisher") or {}
    verification = packet.get("verification_profile") or {}

    protected: list[str] = []
    if publisher.get("master_write_authorized") is True:
        protected.append("master_write")
    if publisher.get("destructive_git_authorized") is True:
        protected.append("destructive_git")

    return {
        "objective": explicit.get("objective", packet.get("objective")),
        "allowed_changed_paths": explicit.get(
            "allowed_changed_paths", packet.get("allowed_changed_paths")
        ),
        "known_protected_actions": explicit.get(
            "known_protected_actions", protected
        ),
        "evidence_gates": explicit.get("evidence_gates", packet.get("required_tests")),
        "stop_conditions": explicit.get("stop_conditions", packet.get("prohibitions")),
        "final_reviewer_boundary": explicit.get(
            "final_reviewer_boundary", verification.get("independent_reviewer")
        ),
        "terminal_lifecycle_state": explicit.get(
            "terminal_lifecycle_state", packet.get("terminal_lifecycle_state")
        ),
        "completion_pointer_shape": explicit.get(
            "completion_pointer_shape", packet.get("required_completion_pointer")
        ),
    }


def validate_packet(packet: dict[str, Any]) -> list[str]:
    """Return findings. Empty means the packet is closable as one big task."""
    findings: list[str] = []
    closure = derive_closure(packet)

    for field, value in closure.items():
        if field == "known_protected_actions":
            # An empty list is a valid, meaningful answer: size does not create
            # an authorization requirement.
            if value is None:
                findings.append("closure_field_missing:known_protected_actions")
            elif not isinstance(value, list):
                findings.append("known_protected_actions_must_be_a_list")
            continue
        if value is None or (isinstance(value, (list, dict, str)) and not value):
            findings.append(f"closure_field_missing:{field}")

    terminal = closure.get("terminal_lifecycle_state")
    if isinstance(terminal, str) and terminal not in DECLARABLE_LIFECYCLE_STATES:
        findings.append(f"terminal_lifecycle_state_not_in_enum:{terminal}")

    verification = packet.get("verification_profile") or {}
    if verification.get("executor_self_acceptance") not in (None, "prohibited", False):
        findings.append("executor_self_acceptance_must_be_prohibited")

    protected = closure.get("known_protected_actions")
    if isinstance(protected, list) and protected:
        publisher = packet.get("publisher") or {}
        if not publisher.get("authorization_ref"):
            findings.append("protected_action_without_authorization_ref")

    return findings


def load_packet(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PreflightError(f"packet_unreadable:{exc}") from exc
    return _packet_body(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--classify")
    args = parser.parse_args()

    if args.classify is not None:
        verdict = classify_pause(args.classify)
        print(json.dumps({"reason": args.classify, "verdict": verdict}, ensure_ascii=False))
        return 0 if verdict == INTERNAL else 1

    if args.packet is None:
        parser.print_help()
        return 3

    try:
        packet = load_packet(args.packet)
    except PreflightError as exc:
        print(str(exc), file=sys.stderr)
        return 3

    findings = validate_packet(packet)
    result = {
        "packet": str(args.packet),
        "closable_as_big_task": not findings,
        "findings": findings,
        "derived_closure": derive_closure(packet),
        "authority_effect": "none",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

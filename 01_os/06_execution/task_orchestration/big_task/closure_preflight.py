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

MASTER_INTEGRATION_ACTION = "master_integration"
MASTER_INTEGRATION_CONFIRMATION_STATES = frozenset(
    {"not_requested", "current_Human_confirmed", "preconfirmed"}
)


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
    `big_task_closure` block may override derived fields, except protected-action
    detection is a safety union: a legacy explicit block may add actions but may
    not erase actions derived from the current section-7 packet.
    """
    explicit = packet.get("big_task_closure")
    explicit = explicit if isinstance(explicit, dict) else {}

    publisher = packet.get("publisher") or {}
    verification = packet.get("verification_profile") or {}
    confirmation_closure = packet.get("big_task_confirmation_closure") or {}

    protected: list[str] = []
    if isinstance(confirmation_closure, dict) and confirmation_closure.get("enabled") is True:
        known = confirmation_closure.get("known_confirmation_required_actions")
        if isinstance(known, list):
            protected.extend(
                action for action in known if isinstance(action, str) and action
            )

    if isinstance(publisher, dict) and publisher.get("master_integration_confirmation") in {
        "current_Human_confirmed",
        "preconfirmed",
    }:
        protected.append(MASTER_INTEGRATION_ACTION)

    # Preserve first-seen order while preventing duplicate action names when the
    # publisher state and confirmation-closure block describe the same action.
    protected = list(dict.fromkeys(protected))

    explicit_protected = explicit.get("known_protected_actions")
    if isinstance(explicit_protected, list):
        # Safety union: current canonical packet fields are authoritative for
        # discovering protected actions. A legacy explicit block can add an
        # action, but an empty/stale block cannot mask a current master action.
        for action in explicit_protected:
            if action not in protected:
                protected.append(action)
    elif explicit_protected is not None:
        # Preserve malformed explicit input so the normal closure validator can
        # report its type instead of silently replacing it.
        protected = explicit_protected

    return {
        "objective": explicit.get("objective", packet.get("objective")),
        "allowed_changed_paths": explicit.get(
            "allowed_changed_paths", packet.get("allowed_changed_paths")
        ),
        "known_protected_actions": protected,
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
            elif any(not isinstance(action, str) or not action for action in value):
                findings.append(
                    "known_protected_actions_items_must_be_nonempty_strings"
                )
            continue
        if value is None or (isinstance(value, (list, dict, str)) and not value):
            findings.append(f"closure_field_missing:{field}")

    terminal = closure.get("terminal_lifecycle_state")
    if isinstance(terminal, str) and terminal not in DECLARABLE_LIFECYCLE_STATES:
        findings.append(f"terminal_lifecycle_state_not_in_enum:{terminal}")

    verification = packet.get("verification_profile") or {}
    if verification.get("executor_self_acceptance") not in (None, "prohibited", False):
        findings.append("executor_self_acceptance_must_be_prohibited")

    publisher_raw = packet.get("publisher")
    if publisher_raw is not None and not isinstance(publisher_raw, dict):
        findings.append("publisher_must_be_a_mapping")
        publisher: dict[str, Any] = {}
    else:
        publisher = publisher_raw or {}

    master_state = publisher.get("master_integration_confirmation")
    if (
        master_state is not None
        and master_state not in MASTER_INTEGRATION_CONFIRMATION_STATES
    ):
        findings.append(f"master_integration_confirmation_invalid:{master_state}")

    confirmation_raw = packet.get("big_task_confirmation_closure")
    confirmation: dict[str, Any] = {}
    if confirmation_raw is not None:
        if not isinstance(confirmation_raw, dict):
            findings.append("big_task_confirmation_closure_must_be_a_mapping")
        else:
            confirmation = confirmation_raw
            enabled = confirmation.get("enabled")
            if enabled is not None and not isinstance(enabled, bool):
                findings.append("big_task_confirmation_closure_enabled_must_be_boolean")

            list_fields = (
                "known_confirmation_required_actions",
                "preconfirmed_actions",
                "uncovered_actions",
            )
            for field in list_fields:
                value = confirmation.get(field)
                if value is not None and not isinstance(value, list):
                    findings.append(f"confirmation_closure_{field}_must_be_a_list")
                elif isinstance(value, list) and any(
                    not isinstance(action, str) or not action for action in value
                ):
                    findings.append(
                        f"confirmation_closure_{field}_items_must_be_nonempty_strings"
                    )

            known = confirmation.get("known_confirmation_required_actions")
            preconfirmed = confirmation.get("preconfirmed_actions")
            uncovered = confirmation.get("uncovered_actions")
            valid_action_lists = all(
                isinstance(value, list)
                and all(isinstance(action, str) and action for action in value)
                for value in (known, preconfirmed, uncovered)
            )
            if enabled is True and valid_action_lists:
                known_set = set(known)
                preconfirmed_set = set(preconfirmed)
                uncovered_set = set(uncovered)
                for action in sorted(preconfirmed_set - known_set):
                    findings.append(
                        f"preconfirmed_action_not_declared_known:{action}"
                    )
                for action in sorted(uncovered_set - known_set):
                    findings.append(f"uncovered_action_not_declared_known:{action}")
                for action in sorted(known_set - preconfirmed_set - uncovered_set):
                    findings.append(f"confirmation_required_action_unclassified:{action}")
                for action in sorted(uncovered_set):
                    findings.append(f"confirmation_required_action_uncovered:{action}")

                if (
                    master_state in {"current_Human_confirmed", "preconfirmed"}
                    and MASTER_INTEGRATION_ACTION not in known_set
                ):
                    findings.append(
                        "master_integration_missing_from_confirmation_closure"
                    )
                if (
                    MASTER_INTEGRATION_ACTION in preconfirmed_set
                    and master_state not in {"current_Human_confirmed", "preconfirmed"}
                ):
                    findings.append(
                        "master_integration_preconfirmed_but_publisher_not_confirmed"
                    )

    protected = closure.get("known_protected_actions")
    valid_protected = (
        isinstance(protected, list)
        and all(isinstance(action, str) and action for action in protected)
    )
    if valid_protected and protected and confirmation_raw is not None:
        preconfirmed = confirmation.get("preconfirmed_actions")
        uncovered = confirmation.get("uncovered_actions")
        valid_disposition_lists = all(
            isinstance(value, list)
            and all(isinstance(action, str) and action for action in value)
            for value in (preconfirmed, uncovered)
        )
        if valid_disposition_lists:
            classified = set(preconfirmed) | set(uncovered)
            for action in protected:
                if action not in classified:
                    findings.append(f"protected_action_without_closure_disposition:{action}")

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

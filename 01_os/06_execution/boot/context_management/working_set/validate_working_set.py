#!/usr/bin/env python3
"""Static validator for the working-set and archive contract.

Its main job is a drift guard. A contract that declares one lifecycle enum while
the code that consumes it hard-codes another is worse than no contract: both
look right in isolation and disagree only at the moment something is archived.
So this validator compares the two directly and fails when they part.

Exit codes: 0 valid, 1 contract violated, 3 input or parse error.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lifecycle import OPEN, TERMINAL, UNKNOWN, OPEN_STATES, TERMINAL_STATES  # noqa: E402
from visible_set import (  # noqa: E402
    COMMUNICATION_ROOT,
    DEFAULT_HIDDEN_CLASSIFICATIONS,
    DEFAULT_VISIBLE_CLASSIFICATIONS,
    HIDDEN_SURFACES,
)

CONTRACT = "01_os/03_mechanisms/context_management/工作集与归档契约_v1.yml"

REQUIRED_TOP_LEVEL = (
    "schema_version",
    "accumulating_surfaces",
    "lifecycle_states",
    "archive_eligibility",
    "reference_safety",
    "default_visibility",
    "archive_semantics",
    "operation",
    "index",
)


def validate(repo_root: Path) -> list[str]:
    findings: list[str] = []
    path = repo_root / CONTRACT
    if not path.is_file():
        return [f"contract_missing:{CONTRACT}"]

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return ["contract_not_a_mapping"]

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            findings.append(f"contract_missing_key:{key}")
    if findings:
        return findings

    states = data["lifecycle_states"]
    declared_open = set(states.get("open") or [])
    declared_terminal = set(states.get("terminal") or [])
    if declared_open != set(OPEN_STATES):
        findings.append(
            "open_state_drift:contract="
            + ",".join(sorted(declared_open))
            + "|code="
            + ",".join(sorted(OPEN_STATES))
        )
    if declared_terminal != set(TERMINAL_STATES):
        findings.append(
            "terminal_state_drift:contract="
            + ",".join(sorted(declared_terminal))
            + "|code="
            + ",".join(sorted(TERMINAL_STATES))
        )
    if declared_open & declared_terminal:
        findings.append("state_in_both_open_and_terminal")
    if states.get("unknown_or_freeform") != "not_archivable":
        findings.append("unknown_state_must_be_not_archivable")

    visibility = data["default_visibility"]
    hidden = set(visibility.get("default_hidden_roots") or [])
    for root, _sf, _sfield in HIDDEN_SURFACES:
        if root not in hidden:
            findings.append(f"hidden_root_not_declared:{root}")
    if COMMUNICATION_ROOT not in hidden:
        findings.append(f"hidden_root_not_declared:{COMMUNICATION_ROOT}")
    # Unknown-visibility policy, bound in both directions.
    #
    # This block exists because the opposite policy shipped once and passed every
    # other check: hiding UNKNOWN alongside TERMINAL is internally consistent,
    # produces a much larger headline number, and is wrong. Independent review
    # T3-IR-001 called it blocking. So the contract must say unknown is visible,
    # the code must agree, and drifting either one back must fail here.
    expected_visibility = {
        "open_group_default_visible": True,
        "unknown_group_default_visible": True,
        "terminal_group_default_hidden": True,
        "archived_group_default_hidden": True,
        "unknown_group_archivable": False,
        "unknown_state_groups_reported_separately": True,
    }
    for key, want in expected_visibility.items():
        if visibility.get(key) is not want:
            findings.append(f"visibility_policy_drift:{key}:expected={str(want).lower()}")

    if UNKNOWN not in DEFAULT_VISIBLE_CLASSIFICATIONS:
        findings.append("code_hides_unknown_groups_contrary_to_contract")
    if OPEN not in DEFAULT_VISIBLE_CLASSIFICATIONS:
        findings.append("code_hides_open_groups_contrary_to_contract")
    if UNKNOWN in DEFAULT_HIDDEN_CLASSIFICATIONS:
        findings.append("code_lists_unknown_as_default_hidden")
    if DEFAULT_HIDDEN_CLASSIFICATIONS != {TERMINAL}:
        findings.append("default_hidden_classifications_must_be_terminal_only")
    if DEFAULT_VISIBLE_CLASSIFICATIONS & DEFAULT_HIDDEN_CLASSIFICATIONS:
        findings.append("classification_in_both_visible_and_hidden")

    if visibility.get("global_silent_exclusion") != "prohibited":
        findings.append("global_silent_exclusion_must_be_prohibited")
    if visibility.get("tool_must_report_excluded_counts") is not True:
        findings.append("excluded_counts_must_be_reported")
    if visibility.get("filtered_result_may_claim_exhaustive") is not False:
        findings.append("filtered_result_must_not_claim_exhaustive")

    semantics = data["archive_semantics"]
    if semantics.get("secure_erasure_claim") is not False:
        findings.append("secure_erasure_claim_must_be_false")
    if semantics.get("deletion") is not False:
        findings.append("archive_must_not_be_deletion")

    eligibility = data["archive_eligibility"]
    required = set(eligibility.get("all_required") or [])
    expected = {
        "state_is_terminal",
        "closure_record_physically_readable",
        "reference_safety_verified",
        "no_private_runtime_inside_group",
    }
    if required != expected:
        findings.append("eligibility_conditions_drift")
    if (eligibility.get("closure_record") or {}).get("caller_boolean_only") != "prohibited":
        findings.append("closure_record_caller_boolean_must_be_prohibited")

    if data["reference_safety"].get("unresolved_live_reference") != "blocked":
        findings.append("unresolved_live_reference_must_block")

    operation = data["operation"]
    if operation.get("idempotent") is not True:
        findings.append("operation_must_be_idempotent")
    if operation.get("already_archived_is_success_not_error") is not True:
        findings.append("already_archived_must_be_success")

    if data["index"].get("index_is_not_authority") is not True:
        findings.append("index_must_not_be_authority")

    for surface in data["accumulating_surfaces"]:
        archiver = surface.get("archiver")
        if archiver and not (repo_root / archiver).is_file():
            findings.append(f"archiver_missing:{surface.get('id')}:{archiver}")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        findings = validate(args.repository_root.resolve())
    except (OSError, yaml.YAMLError) as exc:
        print(f"working_set_contract_unreadable:{exc}", file=sys.stderr)
        return 3
    if findings:
        for item in findings:
            print(item, file=sys.stderr)
        return 1
    print("working_set_contract ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run deterministic and pointer checks against exact B2 candidate v4."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from run_bound_candidate_checks import COMMANDS, NoAliasSafeDumper, REPO, RUN, tracked_tree_matches_head
from run_bound_candidate_checks_v3 import exact_old_pointer_readback


TASK = REPO / (
    "01_os/_communication/Cybernetic_City_State_OS_v2---core/active/"
    "os-v2-mechanism-activation-and-adherence-implementation-001"
)
VALIDATOR = REPO / "01_os/06_execution/boot/communication_system/validator"
ACTIVATION = REPO / "01_os/06_execution/boot/mechanism_activation"
for module_root in (VALIDATOR, ACTIVATION):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))
from receiver_bootstrap import load_receiver_from_pointer
from reproduce_B2_counterexamples import evaluate_counterexamples_at_ref


def corrected_dispatch_pointer_readback() -> dict:
    commit = "25d5f660fd5aaaf85cd072cc539fea70f1cb0f4f"
    message_relative = "messages/foreground-implementation-dispatch-001/00004_correction.yml"
    task_prefix = TASK.relative_to(REPO).as_posix()
    constitution = yaml.safe_load(subprocess.check_output(
        ["git", "-c", "core.longpaths=true", "show", f"{commit}:{task_prefix}/constitutions/foreground-implementation-dispatch-001/00004.yml"],
        cwd=REPO,
        text=True,
    ))
    pointer = {
        "pointer_contract_version": 2,
        "task_id": "os-v2-mechanism-activation-and-adherence-implementation-001",
        "message_id": "os-v2-mechanism-activation-and-adherence-implementation-001::foreground-implementation-dispatch-001::00004",
        "carrier": "GitHub",
        "exact_path_or_GitHub_ref": f"{commit}:{task_prefix}/{message_relative}",
        "sender_endpoint_id": "foreground-implementation-dispatch-001",
        "sender_task_role": "foreground_implementation_dispatch",
        "expected_recipient_endpoint_id": "codex-implementation-executor-001",
        "expected_recipient_task_role": "implementation_executor",
        "one_line_routing_purpose": "Corrected B2 observation-provenance relay",
        "constitution_evidence_ref": "constitutions/foreground-implementation-dispatch-001/00004.yml",
        "compliance_receipt_ref": "receipts/foreground-implementation-dispatch-001/00004.yml",
        "receiver_setup": constitution["receiver_setup"],
    }
    result = load_receiver_from_pointer(
        TASK,
        "codex-implementation-executor-001",
        pointer,
        repository_root=REPO,
    )
    return {
        "target_commit": commit,
        "message_id": result["message"]["message_id"],
        "publication_claim_result": result["receiver_publication_claim"]["verification_result"],
        "sender_index_bound": bool(result["sender_index"]),
        "result": "VERIFIED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    spec_ref = "05_候选冻结/candidate_spec_v4.yml"
    spec = yaml.safe_load((RUN / spec_ref).read_text(encoding="utf-8"))
    candidate = str(spec["candidate_sha"])
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    if head != candidate or not tracked_tree_matches_head():
        raise ValueError("candidate_v4_tree_binding_failed_before_execution")

    observations = []
    total_tests = 0
    for check_id, argv in COMMANDS:
        result = subprocess.run(
            argv,
            cwd=REPO,
            text=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        combined = "\n".join(value.strip() for value in (result.stdout, result.stderr) if value.strip())
        match = re.search(r"Ran (\d+) tests?", combined)
        count = int(match.group(1)) if match else None
        total_tests += count or 0
        observations.append({
            "check_id": check_id,
            "argv": argv,
            "exit_code": result.returncode,
            "tests_run": count,
            "result": "PASS" if result.returncode == 0 else "FAIL",
            "bounded_output_tail": combined.splitlines()[-8:],
        })

    old_pointer = exact_old_pointer_readback()
    corrected_pointer = corrected_dispatch_pointer_readback()
    counterexamples = evaluate_counterexamples_at_ref(candidate)
    after_matches = tracked_tree_matches_head()
    aggregate = (
        all(item["exit_code"] == 0 for item in observations)
        and total_tests == spec["required_validation"]["deterministic"]["expected_tests"]
        and old_pointer["result"] == "VERIFIED"
        and corrected_pointer["result"] == "VERIFIED"
        and set(counterexamples.values()) == {"UNVERIFIABLE"}
        and after_matches
    )
    receipt = {
        "schema_version": "citystate.mechanism_activation.bound_candidate_checks.v4",
        "task_id": spec["task_id"],
        "candidate_spec_ref": spec_ref,
        "candidate_sha_expected": candidate,
        "candidate_sha_observed": head,
        "tracked_worktree_matches_candidate_before": True,
        "tracked_worktree_matches_candidate_after": after_matches,
        "execution_root": ".",
        "observations": observations,
        "exact_old_pointer_readback": old_pointer,
        "exact_corrected_dispatch_pointer_readback": corrected_pointer,
        "B2_counterexamples": counterexamples,
        "deterministic_tests_run": total_tests,
        "aggregate_result": "VERIFIED" if aggregate else "BLOCKED",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority_effect": "none",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.dump(receipt, Dumper=NoAliasSafeDumper, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )
    print(yaml.safe_dump({
        "aggregate_result": receipt["aggregate_result"],
        "deterministic_tests_run": total_tests,
        "old_pointer": old_pointer["result"],
        "corrected_pointer": corrected_pointer["result"],
        "B2_counterexamples": counterexamples,
        "candidate_sha": candidate,
    }, sort_keys=False), end="")
    return 0 if aggregate else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build execution-owned material claims for exact third-B2 candidate v6."""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parents[1]
ACTIVATION = REPO / "01_os/06_execution/boot/mechanism_activation"
if str(ACTIVATION) not in sys.path:
    sys.path.insert(0, str(ACTIVATION))
from activation import (
    MaterialObservationContext,
    observe_changed_path_claim,
    observe_execution_result_claim,
    observe_git_base_relation_claim,
    observe_git_commit_claim,
    observe_local_artifact_claim,
    validate_material_receipt,
)


class NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


def execution_claims(
    context,
    *,
    claim_prefix: str,
    task_id: str,
    spec_ref: str,
    expected_path: tuple[str, ...],
    result_ref: str,
    observed_projection: dict[str, tuple[str, ...]],
    artifact_expected_projection: dict[str, tuple[str, ...]],
    artifact_observed_projection: dict[str, tuple[str, ...]],
):
    source_ref = f"{spec_ref}#{'.'.join(expected_path)}"
    execution = observe_execution_result_claim(
        claim_id=f"{claim_prefix}::execution",
        action_id_or_review_id=task_id,
        expected_root=REPO,
        expected_source_ref=source_ref,
        expected_value_path=expected_path,
        result_root=REPO,
        result_ref=result_ref,
        observed_projection=observed_projection,
        observation_context=context,
    )
    artifact = observe_local_artifact_claim(
        claim_id=f"{claim_prefix}::artifact",
        action_id_or_review_id=task_id,
        expected_root=REPO,
        expected_source_ref=source_ref,
        expected_projection=artifact_expected_projection,
        artifact_root=REPO,
        artifact_ref=result_ref,
        observed_projection=artifact_observed_projection,
        observation_context=context,
    )
    return [execution, artifact]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run_prefix = f"01_os/_runs/{RUN.name}"
    spec_ref = f"{run_prefix}/05_候选冻结/candidate_spec_v6.yml"
    packet_ref = f"{run_prefix}/01_任务输入/任务包_v1.yml#allowed_changed_paths"
    spec = yaml.safe_load((REPO / spec_ref).read_text(encoding="utf-8"))
    candidate = str(spec["candidate_sha"])
    base = str(spec["base_sha"])
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    if head != candidate:
        raise ValueError("candidate_v6_is_not_current_HEAD")
    task_id = str(spec["task_id"])
    context = MaterialObservationContext()
    claims = []

    claims.append(observe_git_commit_claim(
        REPO,
        claim_id="implementation-candidate-v6::candidate",
        claim_role="candidate_SHA",
        action_id_or_review_id=task_id,
        expected_root=REPO,
        expected_source_ref=f"{spec_ref}#candidate_sha",
        expected_value_path=("candidate_sha",),
        observation_context=context,
    ))
    claims.append(observe_git_base_relation_claim(
        REPO,
        claim_id="implementation-candidate-v6::base",
        action_id_or_review_id=task_id,
        expected_root=REPO,
        expected_source_ref=f"{spec_ref}#base_expectation",
        expected_value_path=("base_expectation",),
        base_sha=base,
        candidate_sha=candidate,
        observation_context=context,
    ))
    claims.append(observe_changed_path_claim(
        REPO,
        claim_id="implementation-candidate-v6::scope",
        action_id_or_review_id=task_id,
        expected_root=REPO,
        expected_source_ref=packet_ref,
        expected_projection={"allowed_patterns": ("allowed_changed_paths",)},
        base_sha=base,
        candidate_sha=candidate,
        observation_context=context,
    ))

    deterministic_ref = f"{run_prefix}/07_测试执行/bound_candidate_checks_v6.yml"
    deterministic_path = ("required_validation", "deterministic", "expected_observation")
    deterministic_projection = {
        "schema_version": ("schema_version",),
        "candidate_sha": ("candidate_sha_observed",),
        "execution_root": ("execution_root",),
        "deterministic_tests_run": ("deterministic_tests_run",),
        "aggregate_result": ("aggregate_result",),
        "old_pointer": ("exact_old_pointer_readback", "result"),
        "first_correction_pointer": ("exact_first_B2_correction_pointer_readback", "result"),
        "second_correction_pointer": ("exact_second_B2_correction_pointer_readback", "result"),
        "third_correction_pointer": ("exact_third_B2_correction_pointer_readback", "result"),
        "corrected_attack_results": ("corrected_third_B2_attacks", "attack_results"),
        "controlled_physical_path": ("corrected_third_B2_attacks", "controlled_path_and_replay", "physical_path_result"),
        "replay_result": ("corrected_third_B2_attacks", "controlled_path_and_replay", "replay_result"),
    }
    claims.extend(execution_claims(
        context,
        claim_prefix="implementation-candidate-v6::deterministic",
        task_id=task_id,
        spec_ref=spec_ref,
        expected_path=deterministic_path,
        result_ref=deterministic_ref,
        observed_projection=deterministic_projection,
        artifact_expected_projection={
            "schema_version": deterministic_path + ("schema_version",),
            "candidate_sha": deterministic_path + ("candidate_sha",),
            "aggregate_result": deterministic_path + ("aggregate_result",),
        },
        artifact_observed_projection={
            "schema_version": ("schema_version",),
            "candidate_sha": ("candidate_sha_observed",),
            "aggregate_result": ("aggregate_result",),
        },
    ))

    for mode in ("full", "mutation-suite"):
        slug = "full" if mode == "full" else "mutation"
        result_ref = f"{run_prefix}/07_测试执行/frozen_stage04_{slug}_candidate_v6.yml"
        expected_path = ("required_validation", "frozen_stage04", "expected_outputs", mode)
        observed_projection = {
            "schema_version": ("schema_version",),
            "mode": ("mode",),
            "candidate_sha": ("tested_commit",),
            "frozen_test_package_sha256": ("frozen_test_package_sha256",),
            "total": ("total",), "passed": ("passed",), "failed": ("failed",),
        }
        claims.extend(execution_claims(
            context,
            claim_prefix=f"implementation-candidate-v6::frozen-stage04::{mode}",
            task_id=task_id,
            spec_ref=spec_ref,
            expected_path=expected_path,
            result_ref=result_ref,
            observed_projection=observed_projection,
            artifact_expected_projection={
                "schema_version": expected_path + ("schema_version",),
                "candidate_sha": expected_path + ("candidate_sha",),
            },
            artifact_observed_projection={
                "schema_version": ("schema_version",),
                "candidate_sha": ("tested_commit",),
            },
        ))

    receipt = {
        "schema_version": "citystate.mechanism_activation.candidate_material_receipt.v6",
        "task_id": task_id,
        "candidate_sha": candidate,
        "supersedes_candidate_receipt_ref": "07_测试执行/candidate_material_receipt_v5.yml",
        "execution_owned_provenance_boundary": {
            "generic_issuance_or_attachment_surface": False,
            "caller_constructible_evidence_handles": False,
            "closure_owned_binding_storage": True,
            "physical_execution_and_binding_inseparable": True,
            "claim_count": len(claims),
        },
        "material_claims": claims,
        "aggregate_result": "VERIFIED" if all(c["verification_result"] == "VERIFIED" for c in claims) else "BLOCKED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "receipt_role": "binding_index_only",
        "authority_effect": "none",
    }
    validate_material_receipt(receipt, context)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.dump(receipt, Dumper=NoAliasSafeDumper, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    print(yaml.safe_dump({"aggregate_result": receipt["aggregate_result"], "claim_count": len(claims), "candidate_sha": candidate}, sort_keys=False), end="")
    return 0 if receipt["aggregate_result"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

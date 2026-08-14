#!/usr/bin/env python3
"""Build execution-issued material claims for exact second-B2 candidate v5."""
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
    attach_material_evidence,
    consume_git_base_relation,
    consume_local_artifact,
    consume_trusted_execution_result,
    evaluate_material_claim,
    observe_changed_path_claim,
    observe_git_commit_claim,
    resolve_expected_yaml,
    validate_material_receipt,
)


class NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


def bind_record(context, expected, observed, *, role, task_id, comparator, relationship):
    record = {
        "claim_id": expected.claim_id,
        "claim_role": role,
        "action_id_or_review_id": task_id,
        "expected_claim_source_ref": expected.source_ref,
        "expected_value_or_predicate": expected.value,
        "observed_authoritative_source_class": observed.source_class,
        "observed_value": observed.value,
        "exact_observation_ref": observed.exact_ref,
        "comparator_id": comparator,
        "relationship_or_equality_check": relationship,
        "verification_result": "UNVERIFIABLE",
    }
    attach_material_evidence(context, expected, observed)
    record["verification_result"] = evaluate_material_claim(record, context)
    return record


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
    expected = resolve_expected_yaml(
        REPO, claim_id=f"{claim_prefix}::execution", source_ref=source_ref,
        value_path=expected_path,
    )
    observed = consume_trusted_execution_result(
        REPO, claim_id=expected.claim_id, result_ref=result_ref,
        projection=observed_projection,
    )
    execution = bind_record(
        context, expected, observed,
        role="execution_or_validation_result", task_id=task_id,
        comparator="execution_result_bound_to_expected_candidate_inputs_and_entrypoint",
        relationship="controlled_execution_output_equals_physical_candidate_spec",
    )
    artifact_expected = resolve_expected_yaml(
        REPO, claim_id=f"{claim_prefix}::artifact", source_ref=source_ref,
        projection=artifact_expected_projection,
    )
    artifact_observed = consume_local_artifact(
        REPO, claim_id=artifact_expected.claim_id, artifact_ref=result_ref,
        projection=artifact_observed_projection,
    )
    artifact = bind_record(
        context, artifact_expected, artifact_observed,
        role="durable_evidence_artifact", task_id=task_id,
        comparator="byte_integrity_and_semantic_role_binding",
        relationship="physical_artifact_semantics_and_sha256_consumed",
    )
    return [execution, artifact]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run_prefix = f"01_os/_runs/{RUN.name}"
    spec_ref = f"{run_prefix}/05_候选冻结/candidate_spec_v5.yml"
    packet_ref = f"{run_prefix}/01_任务输入/任务包_v1.yml#allowed_changed_paths"
    spec = yaml.safe_load((REPO / spec_ref).read_text(encoding="utf-8"))
    candidate = str(spec["candidate_sha"])
    base = str(spec["base_sha"])
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    if head != candidate:
        raise ValueError("candidate_v5_is_not_current_HEAD")
    task_id = str(spec["task_id"])
    context = MaterialObservationContext()
    claims = []

    candidate_expected = resolve_expected_yaml(
        REPO, claim_id="implementation-candidate-v5::candidate",
        source_ref=f"{spec_ref}#candidate_sha", value_path=("candidate_sha",),
    )
    claims.append(observe_git_commit_claim(
        REPO, claim_role="candidate_SHA", action_id_or_review_id=task_id,
        expected=candidate_expected, observation_context=context,
    ))

    base_expected = resolve_expected_yaml(
        REPO, claim_id="implementation-candidate-v5::base",
        source_ref=f"{spec_ref}#base_expectation", value_path=("base_expectation",),
    )
    base_observed = consume_git_base_relation(
        REPO, claim_id=base_expected.claim_id, base_sha=base, candidate_sha=candidate,
    )
    claims.append(bind_record(
        context, base_expected, base_observed,
        role="base_SHA", task_id=task_id,
        comparator="exact_base_equality_plus_required_relation",
        relationship="physical_base_commit_exists_and_is_ancestor_of_candidate",
    ))

    scope_expected = resolve_expected_yaml(
        REPO, claim_id="implementation-candidate-v5::scope", source_ref=packet_ref,
        projection={"allowed_patterns": ("allowed_changed_paths",)},
    )
    claims.append(observe_changed_path_claim(
        REPO, action_id_or_review_id=task_id, expected=scope_expected,
        base_sha=base, candidate_sha=candidate, observation_context=context,
    ))

    deterministic_ref = f"{run_prefix}/07_测试执行/bound_candidate_checks_v5.yml"
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
        "corrected_attack_results": ("corrected_second_B2_attacks", "results"),
    }
    claims.extend(execution_claims(
        context, claim_prefix="implementation-candidate-v5::deterministic",
        task_id=task_id, spec_ref=spec_ref, expected_path=deterministic_path,
        result_ref=deterministic_ref, observed_projection=deterministic_projection,
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
        result_ref = f"{run_prefix}/07_测试执行/frozen_stage04_{slug}_candidate_v5.yml"
        expected_path = ("required_validation", "frozen_stage04", "expected_outputs", mode)
        observed_projection = {
            "schema_version": ("schema_version",), "mode": ("mode",),
            "candidate_sha": ("tested_commit",),
            "frozen_test_package_sha256": ("frozen_test_package_sha256",),
            "total": ("total",), "passed": ("passed",), "failed": ("failed",),
        }
        claims.extend(execution_claims(
            context, claim_prefix=f"implementation-candidate-v5::frozen-stage04::{mode}",
            task_id=task_id, spec_ref=spec_ref, expected_path=expected_path,
            result_ref=result_ref, observed_projection=observed_projection,
            artifact_expected_projection={
                "schema_version": expected_path + ("schema_version",),
                "candidate_sha": expected_path + ("candidate_sha",),
            },
            artifact_observed_projection={
                "schema_version": ("schema_version",), "candidate_sha": ("tested_commit",),
            },
        ))

    receipt = {
        "schema_version": "citystate.mechanism_activation.candidate_material_receipt.v5",
        "task_id": task_id,
        "candidate_sha": candidate,
        "supersedes_candidate_receipt_ref": "07_测试执行/candidate_material_receipt_v4.yml",
        "controlled_execution_provenance_boundary": {
            "ordinary_caller_binding_api": False,
            "expected_handles_issued_after_physical_resolution": True,
            "observation_handles_issued_after_physical_consumption": True,
            "issued_handles_one_time_consumed": True,
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

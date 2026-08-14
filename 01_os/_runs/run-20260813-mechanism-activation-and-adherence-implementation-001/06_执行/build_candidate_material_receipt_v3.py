#!/usr/bin/env python3
"""Build two-sided material claims for final hardened candidate v3."""
from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml

from build_candidate_material_receipt import (
    NoAliasSafeDumper,
    REPO,
    RUN,
    base_claim,
    evaluate_material_claim,
    execution_claim,
    git,
    load,
    observe_changed_path_claim,
    observe_git_commit_claim,
    validate_material_receipt,
)


def bound_check_claims(spec: dict, spec_ref: str) -> list[dict]:
    relative = "07_测试执行/bound_candidate_checks_v3.yml"
    result = load(relative)
    expected = {
        "candidate_sha": spec["candidate_sha"],
        "entrypoint": spec["required_validation"]["deterministic"]["entrypoint"],
        "execution_root": ".",
        "deterministic_tests_run": spec["required_validation"]["deterministic"][
            "expected_tests"
        ],
        "aggregate_result": "VERIFIED",
        "long_path_pointer_readback": spec["required_validation"]["deterministic"][
            "exact_old_pointer_long_path_readback"
        ],
    }
    observed = {
        "candidate_sha": result.get("candidate_sha_observed"),
        "entrypoint": spec["required_validation"]["deterministic"]["entrypoint"],
        "execution_root": result.get("execution_root"),
        "deterministic_tests_run": result.get("deterministic_tests_run"),
        "aggregate_result": result.get("aggregate_result"),
        "long_path_pointer_readback": result.get(
            "exact_Git_long_path_pointer_readback", {}
        ).get("result"),
    }
    execution = {
        "claim_id": "implementation-candidate-v3::deterministic-execution",
        "claim_role": "execution_or_validation_result",
        "action_id_or_review_id": spec["task_id"],
        "expected_claim_source_ref": spec_ref,
        "expected_value_or_predicate": expected,
        "observed_authoritative_source_class": "trusted_execution_adapter",
        "observed_value": observed,
        "exact_observation_ref": relative,
        "comparator_id": "execution_result_bound_to_expected_candidate_inputs_and_entrypoint",
        "relationship_or_equality_check": "bound_deterministic_and_pointer_readback_equal_spec",
        "verification_result": "UNVERIFIABLE",
    }
    execution["verification_result"] = evaluate_material_claim(execution)
    path = RUN / relative
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    artifact = {
        "claim_id": "implementation-candidate-v3::deterministic-artifact",
        "claim_role": "durable_evidence_artifact",
        "action_id_or_review_id": spec["task_id"],
        "expected_claim_source_ref": spec_ref,
        "expected_value_or_predicate": {
            "candidate_sha": spec["candidate_sha"],
            "schema_version": "citystate.mechanism_activation.bound_candidate_checks.v3",
            "aggregate_result": "VERIFIED",
        },
        "observed_authoritative_source_class": "exact_local_filesystem_observation",
        "observed_value": {
            "candidate_sha": result.get("candidate_sha_observed"),
            "schema_version": result.get("schema_version"),
            "aggregate_result": result.get("aggregate_result"),
            "sha256": digest,
        },
        "exact_observation_ref": f"{relative}#sha256={digest}",
        "comparator_id": "byte_integrity_and_semantic_role_binding",
        "relationship_or_equality_check": "artifact_semantics_bind_final_candidate",
        "verification_result": "UNVERIFIABLE",
    }
    artifact["verification_result"] = evaluate_material_claim(artifact)
    return [execution, artifact]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    spec_relative = "05_候选冻结/candidate_spec_v3.yml"
    packet_relative = "01_任务输入/任务包_v1.yml"
    spec = load(spec_relative)
    packet = load(packet_relative)
    candidate = str(spec["candidate_sha"])
    if git("rev-parse", "HEAD").stdout.strip() != candidate:
        raise ValueError("candidate_v3_is_not_current_HEAD")

    spec_ref = f"01_os/_runs/{RUN.name}/{spec_relative}"
    packet_ref = f"01_os/_runs/{RUN.name}/{packet_relative}#allowed_changed_paths"
    candidate_claim = observe_git_commit_claim(
        REPO,
        claim_id="implementation-candidate-v3::candidate",
        claim_role="candidate_SHA",
        action_id_or_review_id=str(spec["task_id"]),
        expected_source_ref=spec_ref,
        expected_sha=candidate,
    )
    bound_base_claim = base_claim(spec, spec_ref)
    bound_base_claim["claim_id"] = "implementation-candidate-v3::base"
    claims = [
        candidate_claim,
        bound_base_claim,
        observe_changed_path_claim(
            REPO,
            claim_id="implementation-candidate-v3::scope",
            action_id_or_review_id=str(spec["task_id"]),
            expected_source_ref=packet_ref,
            base_sha=str(spec["base_sha"]),
            candidate_sha=candidate,
            allowed_patterns=list(packet["allowed_changed_paths"]),
        ),
        *bound_check_claims(spec, spec_ref),
    ]
    for relative, mode in (
        ("07_测试执行/frozen_stage04_full_candidate_v3.yml", "full"),
        ("07_测试执行/frozen_stage04_mutation_candidate_v3.yml", "mutation-suite"),
    ):
        execution, artifact = execution_claim(spec, spec_ref, relative, mode)
        execution["claim_id"] = f"implementation-candidate-v3::frozen-stage04::{mode}"
        artifact["claim_id"] = f"implementation-candidate-v3::artifact::{mode}"
        claims.extend((execution, artifact))

    receipt = {
        "schema_version": "citystate.mechanism_activation.candidate_material_receipt.v3",
        "task_id": spec["task_id"],
        "candidate_sha": candidate,
        "supersedes_candidate_receipt_ref": "07_测试执行/candidate_material_receipt_v1.yml",
        "observation_set": {
            "observation_set_id": f"{spec['task_id']}::candidate-v3::{candidate}",
            "action_id_or_review_id": spec["task_id"],
            "expected_claim_spec_refs": [spec_ref, packet_ref],
            "authoritative_observation_refs": [
                claim["exact_observation_ref"] for claim in claims
            ],
            "comparator_results": {
                claim["claim_id"]: claim["verification_result"] for claim in claims
            },
        },
        "material_claims": claims,
        "aggregate_result": (
            "VERIFIED"
            if all(claim["verification_result"] == "VERIFIED" for claim in claims)
            else "BLOCKED"
        ),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "receipt_role": "binding_index_only",
        "authority_effect": "none",
    }
    validate_material_receipt(receipt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.dump(receipt, Dumper=NoAliasSafeDumper, allow_unicode=True, sort_keys=False),
        encoding="utf-8", newline="\n",
    )
    print(yaml.safe_dump({
        "aggregate_result": receipt["aggregate_result"],
        "claim_count": len(claims),
        "candidate_sha": candidate,
    }, sort_keys=False), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

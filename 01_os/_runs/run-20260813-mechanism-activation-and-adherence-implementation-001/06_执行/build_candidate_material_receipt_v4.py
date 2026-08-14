#!/usr/bin/env python3
"""Build trusted-context material claims for exact B2 candidate v4."""
from __future__ import annotations

import argparse
import hashlib
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
    evaluate_material_claim,
    observe_changed_path_claim,
    observe_git_commit_claim,
    validate_material_receipt,
)


class NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


def load(relative: str) -> dict[str, Any]:
    value = yaml.safe_load((RUN / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"mapping_required:{relative}")
    return value


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "core.longpaths=true", *args],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def bind_and_evaluate(
    context: MaterialObservationContext,
    claim: dict[str, Any],
    *,
    expected_resolver_id: str,
    observation_adapter_id: str,
) -> dict[str, Any]:
    context.bind(
        claim_id=claim["claim_id"],
        expected_source_ref=claim["expected_claim_source_ref"],
        expected_value=claim["expected_value_or_predicate"],
        expected_resolver_id=expected_resolver_id,
        observed_source_class=claim["observed_authoritative_source_class"],
        observed_value=claim["observed_value"],
        exact_observation_ref=claim["exact_observation_ref"],
        observation_adapter_id=observation_adapter_id,
    )
    claim["verification_result"] = evaluate_material_claim(claim, context)
    return claim


def execution_and_artifact_claims(
    context: MaterialObservationContext,
    *,
    claim_prefix: str,
    task_id: str,
    expected_source_ref: str,
    relative: str,
    expected: dict[str, Any],
    observed: dict[str, Any],
) -> list[dict[str, Any]]:
    execution = {
        "claim_id": f"{claim_prefix}::execution",
        "claim_role": "execution_or_validation_result",
        "action_id_or_review_id": task_id,
        "expected_claim_source_ref": expected_source_ref,
        "expected_value_or_predicate": expected,
        "observed_authoritative_source_class": "trusted_execution_adapter",
        "observed_value": observed,
        "exact_observation_ref": relative,
        "comparator_id": "execution_result_bound_to_expected_candidate_inputs_and_entrypoint",
        "relationship_or_equality_check": "trusted_execution_result_equals_candidate_spec",
        "verification_result": "UNVERIFIABLE",
    }
    bind_and_evaluate(
        context,
        execution,
        expected_resolver_id="candidate_spec_yaml_readback",
        observation_adapter_id="trusted_execution_result_file_adapter",
    )
    digest = hashlib.sha256((RUN / relative).read_bytes()).hexdigest()
    artifact_expected = {
        key: expected[key]
        for key in ("candidate_sha", "schema_version", "aggregate_result")
        if key in expected
    }
    artifact_observed = {
        key: observed.get(key)
        for key in ("candidate_sha", "schema_version", "aggregate_result")
        if key in artifact_expected
    }
    artifact_observed["sha256"] = digest
    artifact = {
        "claim_id": f"{claim_prefix}::artifact",
        "claim_role": "durable_evidence_artifact",
        "action_id_or_review_id": task_id,
        "expected_claim_source_ref": expected_source_ref,
        "expected_value_or_predicate": artifact_expected,
        "observed_authoritative_source_class": "exact_local_filesystem_observation",
        "observed_value": artifact_observed,
        "exact_observation_ref": f"{relative}#sha256={digest}",
        "comparator_id": "byte_integrity_and_semantic_role_binding",
        "relationship_or_equality_check": "artifact_bytes_and_semantics_bind_candidate",
        "verification_result": "UNVERIFIABLE",
    }
    bind_and_evaluate(
        context,
        artifact,
        expected_resolver_id="candidate_spec_yaml_readback",
        observation_adapter_id="local_artifact_sha256_readback",
    )
    return [execution, artifact]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    spec_relative = "05_候选冻结/candidate_spec_v4.yml"
    packet_relative = "01_任务输入/任务包_v1.yml"
    deterministic_relative = "07_测试执行/bound_candidate_checks_v4.yml"
    spec = load(spec_relative)
    packet = load(packet_relative)
    deterministic = load(deterministic_relative)
    candidate = str(spec["candidate_sha"])
    base = str(spec["base_sha"])
    if git("rev-parse", "HEAD").stdout.strip() != candidate:
        raise ValueError("candidate_v4_is_not_current_HEAD")

    task_id = str(spec["task_id"])
    spec_ref = f"01_os/_runs/{RUN.name}/{spec_relative}"
    packet_ref = f"01_os/_runs/{RUN.name}/{packet_relative}#allowed_changed_paths"
    context = MaterialObservationContext()
    claims: list[dict[str, Any]] = []
    claims.append(observe_git_commit_claim(
        REPO,
        claim_id="implementation-candidate-v4::candidate",
        claim_role="candidate_SHA",
        action_id_or_review_id=task_id,
        expected_source_ref=f"{spec_ref}#candidate_sha",
        expected_sha=candidate,
        observation_context=context,
        expected_resolver_id="candidate_spec_yaml_readback",
    ))

    relation = git("merge-base", "--is-ancestor", base, candidate)
    observed_base = git("rev-parse", f"{base}^{{commit}}").stdout.strip()
    base_claim = {
        "claim_id": "implementation-candidate-v4::base",
        "claim_role": "base_SHA",
        "action_id_or_review_id": task_id,
        "expected_claim_source_ref": f"{spec_ref}#base_sha_and_required_base_relation",
        "expected_value_or_predicate": {
            "sha": base,
            "required_relation": spec["required_base_relation"],
        },
        "observed_authoritative_source_class": "actual_Git_object_database",
        "observed_value": {
            "sha": observed_base,
            "relation_satisfied": relation.returncode == 0,
        },
        "exact_observation_ref": f"git:merge-base--is-ancestor:{base}..{candidate}",
        "comparator_id": "exact_base_equality_plus_required_relation",
        "relationship_or_equality_check": "base_SHA_exists_and_is_ancestor_of_candidate",
        "verification_result": "UNVERIFIABLE",
    }
    claims.append(bind_and_evaluate(
        context,
        base_claim,
        expected_resolver_id="candidate_spec_yaml_readback",
        observation_adapter_id="git_base_relation_adapter",
    ))
    claims.append(observe_changed_path_claim(
        REPO,
        claim_id="implementation-candidate-v4::scope",
        action_id_or_review_id=task_id,
        expected_source_ref=packet_ref,
        base_sha=base,
        candidate_sha=candidate,
        allowed_patterns=list(packet["allowed_changed_paths"]),
        observation_context=context,
        expected_resolver_id="task_packet_yaml_readback",
    ))

    deterministic_expected = {
        "candidate_sha": candidate,
        "schema_version": "citystate.mechanism_activation.bound_candidate_checks.v4",
        "entrypoint": spec["required_validation"]["deterministic"]["entrypoint"],
        "execution_root": ".",
        "deterministic_tests_run": spec["required_validation"]["deterministic"]["expected_tests"],
        "aggregate_result": "VERIFIED",
        "old_pointer": "VERIFIED",
        "corrected_pointer": "VERIFIED",
        "B2_counterexamples": {
            key: "UNVERIFIABLE" for key in deterministic["B2_counterexamples"]
        },
    }
    deterministic_observed = {
        "candidate_sha": deterministic.get("candidate_sha_observed"),
        "schema_version": deterministic.get("schema_version"),
        "entrypoint": spec["required_validation"]["deterministic"]["entrypoint"],
        "execution_root": deterministic.get("execution_root"),
        "deterministic_tests_run": deterministic.get("deterministic_tests_run"),
        "aggregate_result": deterministic.get("aggregate_result"),
        "old_pointer": deterministic.get("exact_old_pointer_readback", {}).get("result"),
        "corrected_pointer": deterministic.get(
            "exact_corrected_dispatch_pointer_readback", {}
        ).get("result"),
        "B2_counterexamples": deterministic.get("B2_counterexamples"),
    }
    claims.extend(execution_and_artifact_claims(
        context,
        claim_prefix="implementation-candidate-v4::deterministic",
        task_id=task_id,
        expected_source_ref=f"{spec_ref}#required_validation.deterministic",
        relative=deterministic_relative,
        expected=deterministic_expected,
        observed=deterministic_observed,
    ))

    frozen_spec = spec["required_validation"]["frozen_stage04"]
    for mode, relative in (
        ("full", "07_测试执行/frozen_stage04_full_candidate_v4.yml"),
        ("mutation-suite", "07_测试执行/frozen_stage04_mutation_candidate_v4.yml"),
    ):
        result = load(relative)
        expected = {
            "candidate_sha": candidate,
            "schema_version": "citystate.communication.frozen_stage04_run.v1",
            "mode": mode,
            "frozen_test_package_sha256": frozen_spec["frozen_test_package_sha256"],
            "total": frozen_spec["expected_each"]["total"],
            "passed": frozen_spec["expected_each"]["passed"],
            "failed": frozen_spec["expected_each"]["failed"],
            "aggregate_result": "VERIFIED",
        }
        observed = {
            "candidate_sha": result.get("tested_commit"),
            "schema_version": result.get("schema_version"),
            "mode": result.get("mode"),
            "frozen_test_package_sha256": result.get("frozen_test_package_sha256"),
            "total": result.get("total"),
            "passed": result.get("passed"),
            "failed": result.get("failed"),
            "aggregate_result": (
                "VERIFIED" if result.get("failed") == 0 and result.get("passed") == result.get("total")
                else "BLOCKED"
            ),
        }
        claims.extend(execution_and_artifact_claims(
            context,
            claim_prefix=f"implementation-candidate-v4::frozen-stage04::{mode}",
            task_id=task_id,
            expected_source_ref=f"{spec_ref}#required_validation.frozen_stage04",
            relative=relative,
            expected=expected,
            observed=observed,
        ))

    receipt = {
        "schema_version": "citystate.mechanism_activation.candidate_material_receipt.v4",
        "task_id": task_id,
        "candidate_sha": candidate,
        "supersedes_candidate_receipt_ref": "07_测试执行/candidate_material_receipt_v3.yml",
        "trusted_observation_boundary": {
            "context_type": "MaterialObservationContext",
            "expected_sources_resolved_outside_receipt": True,
            "physical_observations_consumed_outside_receipt": True,
            "claim_count": len(claims),
        },
        "material_claims": claims,
        "aggregate_result": (
            "VERIFIED" if all(claim["verification_result"] == "VERIFIED" for claim in claims)
            else "BLOCKED"
        ),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "receipt_role": "binding_index_only",
        "authority_effect": "none",
    }
    validate_material_receipt(receipt, context)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.dump(receipt, Dumper=NoAliasSafeDumper, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )
    print(yaml.safe_dump({
        "aggregate_result": receipt["aggregate_result"],
        "claim_count": len(claims),
        "candidate_sha": candidate,
    }, sort_keys=False), end="")
    return 0 if receipt["aggregate_result"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

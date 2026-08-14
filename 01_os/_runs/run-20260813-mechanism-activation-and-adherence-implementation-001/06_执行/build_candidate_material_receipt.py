#!/usr/bin/env python3
"""Build two-sided physical claims for the immutable implementation candidate."""
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

from activation import (  # noqa: E402
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


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=REPO, text=True, check=check,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def base_claim(spec: dict[str, Any], source_ref: str) -> dict[str, Any]:
    base = str(spec["base_sha"])
    candidate = str(spec["candidate_sha"])
    observed = git("rev-parse", f"{base}^{{commit}}").stdout.strip()
    relation = git("merge-base", "--is-ancestor", base, candidate, check=False).returncode == 0
    claim = {
        "claim_id": "implementation-candidate::base",
        "claim_role": "base_SHA",
        "action_id_or_review_id": spec["task_id"],
        "expected_claim_source_ref": source_ref,
        "expected_value_or_predicate": {
            "sha": base,
            "required_relation": spec["required_base_relation"],
        },
        "observed_authoritative_source_class": "actual_Git_object_database",
        "observed_value": {"sha": observed, "relation_satisfied": relation},
        "exact_observation_ref": f"git:rev-parse-and-merge-base:{base}..{candidate}",
        "comparator_id": "exact_base_equality_plus_required_relation",
        "relationship_or_equality_check": "base_equals_spec_and_is_ancestor_of_candidate",
        "verification_result": "UNVERIFIABLE",
    }
    claim["verification_result"] = evaluate_material_claim(claim)
    return claim


def execution_claim(
    spec: dict[str, Any], source_ref: str, relative: str, expected_mode: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    result = load(relative)
    expected = {
        "candidate_sha": spec["candidate_sha"],
        "entrypoint": spec["required_validation"]["frozen_stage04"]["entrypoint"],
        "execution_root": ".",
        "test_package_sha256": spec["required_validation"]["frozen_stage04"][
            "frozen_test_package_sha256"
        ],
        "mode": expected_mode,
        **spec["required_validation"]["frozen_stage04"]["expected_each"],
    }
    observed = {
        "candidate_sha": result.get("tested_commit"),
        "entrypoint": spec["required_validation"]["frozen_stage04"]["entrypoint"],
        "execution_root": ".",
        "test_package_sha256": result.get("frozen_test_package_sha256"),
        "mode": result.get("mode"),
        "total": result.get("total"),
        "passed": result.get("passed"),
        "failed": result.get("failed"),
    }
    execution = {
        "claim_id": f"implementation-candidate::frozen-stage04::{expected_mode}",
        "claim_role": "execution_or_validation_result",
        "action_id_or_review_id": spec["task_id"],
        "expected_claim_source_ref": source_ref,
        "expected_value_or_predicate": expected,
        "observed_authoritative_source_class": "trusted_execution_adapter",
        "observed_value": observed,
        "exact_observation_ref": relative,
        "comparator_id": "execution_result_bound_to_expected_candidate_inputs_and_entrypoint",
        "relationship_or_equality_check": "frozen_execution_matches_candidate_and_package_spec",
        "verification_result": "UNVERIFIABLE",
    }
    execution["verification_result"] = evaluate_material_claim(execution)

    path = RUN / relative
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    artifact = {
        "claim_id": f"implementation-candidate::artifact::{expected_mode}",
        "claim_role": "durable_evidence_artifact",
        "action_id_or_review_id": spec["task_id"],
        "expected_claim_source_ref": source_ref,
        "expected_value_or_predicate": {
            "candidate_sha": spec["candidate_sha"],
            "mode": expected_mode,
            "test_package_sha256": expected["test_package_sha256"],
        },
        "observed_authoritative_source_class": "exact_local_filesystem_observation",
        "observed_value": {
            "candidate_sha": result.get("tested_commit"),
            "mode": result.get("mode"),
            "test_package_sha256": result.get("frozen_test_package_sha256"),
            "sha256": digest,
        },
        "exact_observation_ref": f"{relative}#sha256={digest}",
        "comparator_id": "byte_integrity_and_semantic_role_binding",
        "relationship_or_equality_check": "artifact_internal_bindings_match_candidate_spec",
        "verification_result": "UNVERIFIABLE",
    }
    artifact["verification_result"] = evaluate_material_claim(artifact)
    return execution, artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    spec_relative = "05_候选冻结/candidate_spec_v1.yml"
    packet_relative = "01_任务输入/任务包_v1.yml"
    spec = load(spec_relative)
    packet = load(packet_relative)
    candidate = str(spec["candidate_sha"])
    if git("rev-parse", "HEAD").stdout.strip() != candidate:
        raise ValueError("candidate_is_not_current_HEAD")

    spec_ref = f"01_os/_runs/{RUN.name}/{spec_relative}"
    packet_ref = f"01_os/_runs/{RUN.name}/{packet_relative}#allowed_changed_paths"
    claims: list[dict[str, Any]] = [
        observe_git_commit_claim(
            REPO,
            claim_id="implementation-candidate::candidate",
            claim_role="candidate_SHA",
            action_id_or_review_id=str(spec["task_id"]),
            expected_source_ref=spec_ref,
            expected_sha=candidate,
        ),
        base_claim(spec, spec_ref),
        observe_changed_path_claim(
            REPO,
            claim_id="implementation-candidate::scope",
            action_id_or_review_id=str(spec["task_id"]),
            expected_source_ref=packet_ref,
            base_sha=str(spec["base_sha"]),
            candidate_sha=candidate,
            allowed_patterns=list(packet["allowed_changed_paths"]),
        ),
    ]
    for relative, mode in (
        ("07_测试执行/frozen_stage04_full_candidate_v1.yml", "full"),
        ("07_测试执行/frozen_stage04_mutation_candidate_v1.yml", "mutation-suite"),
    ):
        claims.extend(execution_claim(spec, spec_ref, relative, mode))

    receipt = {
        "schema_version": "citystate.mechanism_activation.candidate_material_receipt.v1",
        "task_id": spec["task_id"],
        "candidate_sha": candidate,
        "observation_set": {
            "observation_set_id": f"{spec['task_id']}::candidate::{candidate}",
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
        yaml.dump(
            receipt, Dumper=NoAliasSafeDumper, allow_unicode=True, sort_keys=False
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(
        yaml.safe_dump(
            {
                "aggregate_result": receipt["aggregate_result"],
                "claim_count": len(claims),
                "candidate_sha": candidate,
            },
            sort_keys=False,
        ),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

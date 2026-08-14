#!/usr/bin/env python3
"""Replay the five B2 counterexamples against an exact Git implementation ref."""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml


REPO = Path(__file__).resolve().parents[4]
ACTIVATION_PATH = "01_os/06_execution/boot/mechanism_activation/activation.py"


def load_activation(implementation_ref: str) -> ModuleType:
    source = subprocess.check_output(
        ["git", "-c", "core.longpaths=true", "show", f"{implementation_ref}:{ACTIVATION_PATH}"],
        cwd=REPO,
    )
    temp = tempfile.NamedTemporaryFile(suffix="_activation.py", delete=False)
    try:
        temp.write(source)
        temp.close()
        spec = importlib.util.spec_from_file_location("b2_exact_activation", temp.name)
        if spec is None or spec.loader is None:
            raise RuntimeError("exact_activation_import_spec_missing")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(spec.name, None)
        return module
    finally:
        Path(temp.name).unlink(missing_ok=True)


def counterexamples() -> dict[str, dict[str, Any]]:
    sha = "a" * 40
    base = {
        "claim_id": "B2-counterexample",
        "claim_role": "candidate_SHA",
        "action_id_or_review_id": "B2-review",
        "expected_claim_source_ref": "missing/source.yml#candidate",
        "expected_value_or_predicate": sha,
        "observed_authoritative_source_class": "actual_Git_object_database",
        "observed_value": sha,
        "exact_observation_ref": "unconsumed:observation",
        "comparator_id": "exact_sha_role_equality",
        "relationship_or_equality_check": "equal",
        "verification_result": "UNVERIFIABLE",
    }
    return {
        "non_resolving_expected_source": dict(base),
        "asserted_complete_diff_without_git_compare": dict(
            base,
            claim_role="changed_path_and_diff_scope",
            expected_value_or_predicate={"allowed_patterns": ["allowed/**"]},
            observed_authoritative_source_class="complete_Git_compare",
            observed_value={"paths": ["allowed/a.yml"], "complete": True},
            exact_observation_ref="receipt:asserted-complete",
            comparator_id="complete_path_set_within_authorized_boundary",
        ),
        "asserted_principal_without_authenticated_observation": dict(
            base,
            claim_role="authority_and_actual_actor",
            expected_value_or_predicate={"allowed_principals": ["alice"]},
            observed_authoritative_source_class="local_authenticated_principal",
            observed_value={"authenticated_principal": "alice"},
            exact_observation_ref="receipt:asserted-principal",
            subject_principal_observation_ref="receipt:asserted-principal",
            comparator_id="authenticated_actor_satisfies_authorized_principal_binding",
        ),
        "observation_ref_source_class_mismatch": dict(
            base,
            exact_observation_ref="connector:authenticated-principal",
        ),
        "receipt_only_correct_looking_value": dict(
            base,
            claim_role="durable_evidence_artifact",
            expected_value_or_predicate={"sha256": "abc"},
            observed_authoritative_source_class="Git_blob_at_exact_commit",
            observed_value={"sha256": "abc"},
            exact_observation_ref="receipt:prose-only",
            comparator_id="byte_integrity_and_semantic_role_binding",
        ),
    }


def evaluate_counterexamples_at_ref(implementation_ref: str) -> dict[str, str]:
    activation = load_activation(implementation_ref)
    return {
        name: activation.evaluate_material_claim(claim)
        for name, claim in counterexamples().items()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation-ref", required=True)
    parser.add_argument("--expected-result", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    resolved = subprocess.check_output(
        ["git", "rev-parse", f"{args.implementation_ref}^{{commit}}"],
        cwd=REPO,
        text=True,
    ).strip()
    results = evaluate_counterexamples_at_ref(resolved)
    aggregate = all(value == args.expected_result for value in results.values())
    evidence = {
        "schema_version": "citystate.mechanism_activation.B2_counterexample_reproduction.v1",
        "implementation_ref_requested": args.implementation_ref,
        "implementation_commit_observed": resolved,
        "implementation_path": ACTIVATION_PATH,
        "counterexamples": results,
        "expected_result_each": args.expected_result,
        "aggregate_result": "VERIFIED" if aggregate else "BLOCKED",
        "authority_effect": "none",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(evidence, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )
    print(yaml.safe_dump({
        "implementation_commit": resolved,
        "counterexamples": results,
        "aggregate_result": evidence["aggregate_result"],
    }, sort_keys=False), end="")
    return 0 if aggregate else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Replay second-round B2 caller-minting attacks against exact Git refs."""
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
SHA = "a" * 40


def load_activation(implementation_ref: str) -> tuple[str, ModuleType]:
    commit = subprocess.check_output(
        ["git", "rev-parse", f"{implementation_ref}^{{commit}}"], cwd=REPO, text=True
    ).strip()
    source = subprocess.check_output(
        ["git", "-c", "core.longpaths=true", "show", f"{commit}:{ACTIVATION_PATH}"],
        cwd=REPO,
    )
    temporary = tempfile.NamedTemporaryFile(suffix="_activation.py", delete=False)
    try:
        temporary.write(source)
        temporary.close()
        name = "second_b2_" + commit[:12]
        spec = importlib.util.spec_from_file_location(name, temporary.name)
        if spec is None or spec.loader is None:
            raise RuntimeError("exact_activation_import_spec_missing")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(name, None)
        return commit, module
    finally:
        Path(temporary.name).unlink(missing_ok=True)


def base_claim(claim_id: str) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "claim_role": "candidate_SHA",
        "action_id_or_review_id": "second-B2-review",
        "expected_claim_source_ref": "nonexistent/spec.yml#candidate",
        "expected_value_or_predicate": SHA,
        "observed_authoritative_source_class": "actual_Git_object_database",
        "observed_value": SHA,
        "exact_observation_ref": "fabricated:git-observation",
        "comparator_id": "exact_sha_role_equality",
        "relationship_or_equality_check": "equal",
        "verification_result": "UNVERIFIABLE",
    }


def attacks() -> dict[str, dict[str, Any]]:
    resolver = base_claim("expected-resolver-never-executed")
    adapter = base_claim("observation-adapter-never-executed")
    diff = dict(base_claim("fabricated-complete-diff"),
        claim_role="changed_path_and_diff_scope",
        expected_value_or_predicate={"allowed_patterns": ["allowed/**"]},
        observed_authoritative_source_class="complete_Git_compare",
        observed_value={"paths": ["allowed/a.yml"], "complete": True},
        exact_observation_ref="fabricated:complete-git-diff",
        comparator_id="complete_path_set_within_authorized_boundary")
    principal = dict(base_claim("fabricated-principal"),
        claim_role="authority_and_actual_actor",
        expected_value_or_predicate={"allowed_principals": ["alice"]},
        observed_authoritative_source_class="local_authenticated_principal",
        observed_value={"authenticated_principal": "alice"},
        exact_observation_ref="fabricated:principal",
        subject_principal_observation_ref="fabricated:principal",
        comparator_id="authenticated_actor_satisfies_authorized_principal_binding")
    conditional = dict(base_claim("fabricated-conditional-ref"),
        claim_role="moving_head_or_current_ref",
        expected_value_or_predicate={"sha": SHA},
        observed_authoritative_source_class="fresh_remote_Git_ref_readback",
        observed_value={"sha": SHA, "fresh": True},
        exact_observation_ref="fabricated:remote-ref",
        freshness_requirement_when_applicable="immediately_before_action",
        freshness_observation_ref="fabricated:freshness",
        comparator_id="named_ref_fresh_state_relation")
    return {
        "expected_resolver_never_executed": resolver,
        "observation_adapter_never_executed": adapter,
        "fabricated_complete_Git_compare": diff,
        "fabricated_authenticated_principal": principal,
        "fabricated_conditional_ref_consumption": conditional,
    }


def attack_result(module: ModuleType, value: dict[str, Any]) -> str:
    context = module.MaterialObservationContext()
    if hasattr(context, "bind"):
        consumed = {value["exact_observation_ref"]}
        for field in ("subject_principal_observation_ref", "freshness_observation_ref"):
            if value.get(field):
                consumed.add(value[field])
        context.bind(
            claim_id=value["claim_id"],
            expected_source_ref=value["expected_claim_source_ref"],
            expected_value=value["expected_value_or_predicate"],
            expected_resolver_id="caller-forged-resolver",
            observed_source_class=value["observed_authoritative_source_class"],
            observed_value=value["observed_value"],
            exact_observation_ref=value["exact_observation_ref"],
            observation_adapter_id="caller-forged-adapter",
            consumed_observation_refs=consumed,
        )
        return module.evaluate_material_claim(value, context)
    try:
        expected = module._ResolvedExpectedSource(
            value["claim_id"], value["expected_claim_source_ref"],
            value["expected_value_or_predicate"], {"resolver": "caller-forged"},
        )
        observed = module._ConsumedObservation(
            value["claim_id"], value["observed_authoritative_source_class"],
            value["observed_value"], value["exact_observation_ref"],
            frozenset({value["exact_observation_ref"]}), {"adapter": "caller-forged"},
        )
        module.attach_material_evidence(context, expected, observed)
    except module.ActivationError:
        pass
    return module.evaluate_material_claim(value, context)


def evaluate_at_ref(ref: str) -> dict[str, Any]:
    commit, module = load_activation(ref)
    return {
        "commit": commit,
        "results": {name: attack_result(module, value) for name, value in attacks().items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vulnerable-ref", required=True)
    parser.add_argument("--corrected-ref", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    vulnerable = evaluate_at_ref(args.vulnerable_ref)
    corrected = evaluate_at_ref(args.corrected_ref)
    aggregate = (
        set(vulnerable["results"].values()) == {"VERIFIED"}
        and set(corrected["results"].values()) == {"UNVERIFIABLE"}
    )
    evidence = {
        "schema_version": "citystate.mechanism_activation.second_B2_provenance_replay.v1",
        "implementation_path": ACTIVATION_PATH,
        "vulnerable": vulnerable,
        "corrected": corrected,
        "expected_vulnerable_result_each": "VERIFIED",
        "expected_corrected_result_each": "UNVERIFIABLE",
        "aggregate_result": "VERIFIED" if aggregate else "BLOCKED",
        "authority_effect": "none",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(evidence, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    print(yaml.safe_dump(evidence, allow_unicode=True, sort_keys=False), end="")
    return 0 if aggregate else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Replay third-round issuance-forgeability attacks against exact Git refs."""
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


def load_activation(ref: str) -> tuple[str, ModuleType]:
    commit = subprocess.check_output(
        ["git", "rev-parse", f"{ref}^{{commit}}"], cwd=REPO, text=True
    ).strip()
    source = subprocess.check_output(
        ["git", "-c", "core.longpaths=true", "show", f"{commit}:{ACTIVATION_PATH}"],
        cwd=REPO,
    )
    temporary = tempfile.NamedTemporaryFile(suffix="_activation.py", delete=False)
    try:
        temporary.write(source)
        temporary.close()
        name = "third_b2_" + commit[:12]
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
        "action_id_or_review_id": "third-B2-review",
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
    return {
        "direct_generic_issuance_without_execution": base_claim("generic-issuance"),
        "constructed_lookalike_handles": base_claim("lookalike-handles"),
        "forged_complete_Git_compare": dict(
            base_claim("forged-diff"),
            claim_role="changed_path_and_diff_scope",
            expected_value_or_predicate={"allowed_patterns": ["allowed/**"]},
            observed_authoritative_source_class="complete_Git_compare",
            observed_value={"paths": ["allowed/a.yml"], "complete": True},
            exact_observation_ref="fabricated:complete-diff",
            comparator_id="complete_path_set_within_authorized_boundary",
        ),
        "forged_authenticated_principal": dict(
            base_claim("forged-principal"),
            claim_role="authority_and_actual_actor",
            expected_value_or_predicate={"allowed_principals": ["alice"]},
            observed_authoritative_source_class="local_authenticated_principal",
            observed_value={"authenticated_principal": "alice"},
            exact_observation_ref="fabricated:principal",
            subject_principal_observation_ref="fabricated:principal",
            comparator_id="authenticated_actor_satisfies_authorized_principal_binding",
        ),
        "forged_conditional_consumed_ref": dict(
            base_claim("forged-conditional"),
            claim_role="moving_head_or_current_ref",
            expected_value_or_predicate={"sha": SHA},
            observed_authoritative_source_class="fresh_remote_Git_ref_readback",
            observed_value={"sha": SHA, "fresh": True},
            exact_observation_ref="fabricated:remote-ref",
            freshness_requirement_when_applicable="immediately_before_action",
            freshness_observation_ref="fabricated:freshness",
            comparator_id="named_ref_fresh_state_relation",
        ),
    }


def forge(module: ModuleType, value: dict[str, Any]) -> str:
    required = (
        "_ResolvedExpectedSource", "_ConsumedObservation", "_issue_expected",
        "_issue_observed", "attach_material_evidence",
    )
    if not all(hasattr(module, name) for name in required):
        return module.evaluate_material_claim(value, module.MaterialObservationContext())
    consumed = {value["exact_observation_ref"]}
    for field in ("subject_principal_observation_ref", "freshness_observation_ref"):
        if value.get(field):
            consumed.add(value[field])
    expected = module._ResolvedExpectedSource(
        value["claim_id"], value["expected_claim_source_ref"],
        value["expected_value_or_predicate"], {"resolver": "caller-forged"},
    )
    observed = module._ConsumedObservation(
        value["claim_id"], value["observed_authoritative_source_class"],
        value["observed_value"], value["exact_observation_ref"], frozenset(consumed),
        {"adapter": "caller-forged"},
    )
    module._issue_expected(expected)
    module._issue_observed(observed)
    context = module.MaterialObservationContext()
    module.attach_material_evidence(context, expected, observed)
    return module.evaluate_material_claim(value, context)


def controlled_path_and_replay(module: ModuleType) -> dict[str, str]:
    if not hasattr(module, "observe_git_commit_claim") or hasattr(module, "_issue_expected"):
        return {"physical_path_result": "NOT_APPLICABLE", "replay_result": "NOT_APPLICABLE"}
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
        (root / "a.txt").write_text("a\n", encoding="utf-8")
        subprocess.run(["git", "add", "a.txt"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "candidate"], cwd=root, check=True)
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        (root / "task.yml").write_text("candidate: " + commit + "\n", encoding="utf-8")
        context = module.MaterialObservationContext()
        kwargs = {
            "claim_id": "controlled-candidate",
            "claim_role": "candidate_SHA",
            "action_id_or_review_id": "third-B2-review",
            "expected_root": root,
            "expected_source_ref": "task.yml#candidate",
            "expected_value_path": ("candidate",),
            "observation_context": context,
        }
        record = module.observe_git_commit_claim(root, **kwargs)
        try:
            module.observe_git_commit_claim(root, **kwargs)
            replay = "VERIFIED"
        except module.ActivationError as exc:
            replay = exc.code
        return {"physical_path_result": record["verification_result"], "replay_result": replay}


def evaluate_at_ref(ref: str) -> dict[str, Any]:
    commit, module = load_activation(ref)
    return {
        "commit": commit,
        "generic_issuance_surface_present": all(
            hasattr(module, name) for name in (
                "_ResolvedExpectedSource", "_ConsumedObservation", "_issue_expected",
                "_issue_observed", "attach_material_evidence",
            )
        ),
        "attack_results": {name: forge(module, value) for name, value in attacks().items()},
        "controlled_path_and_replay": controlled_path_and_replay(module),
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
        vulnerable["generic_issuance_surface_present"] is True
        and set(vulnerable["attack_results"].values()) == {"VERIFIED"}
        and corrected["generic_issuance_surface_present"] is False
        and set(corrected["attack_results"].values()) == {"UNVERIFIABLE"}
        and corrected["controlled_path_and_replay"]["physical_path_result"] == "VERIFIED"
        and corrected["controlled_path_and_replay"]["replay_result"] == "TRUSTED_CLAIM_BINDING_DUPLICATE"
    )
    evidence = {
        "schema_version": "citystate.mechanism_activation.third_B2_execution_only_replay.v1",
        "implementation_path": ACTIVATION_PATH,
        "vulnerable": vulnerable,
        "corrected": corrected,
        "aggregate_result": "VERIFIED" if aggregate else "BLOCKED",
        "authority_effect": "none",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(evidence, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    print(yaml.safe_dump(evidence, allow_unicode=True, sort_keys=False), end="")
    return 0 if aggregate else 1


if __name__ == "__main__":
    raise SystemExit(main())

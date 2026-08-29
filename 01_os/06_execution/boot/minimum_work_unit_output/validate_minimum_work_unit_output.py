#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

CORE_FIELDS = (
    "work_performed_or_requested",
    "implementation_or_review_method",
    "supportability_rationale",
    "feasibility_rationale",
)
ROLE_FIELDS = {
    "decision_architecture": ("task_constraints_and_boundaries", "stop_or_return_conditions"),
    "execution": ("exact_result_or_candidate_ref", "verification_evidence", "residual_risk_or_unproved_limits"),
    "independent_review": ("verdict", "primary_evidence_examined", "findings_and_residual_risk", "executor_rationale_assessment"),
}
ASSESSMENT_FIELDS = (
    "supportability_assessment",
    "feasibility_assessment",
    "primary_evidence_refs",
    "unsupported_or_inferred_claims",
)
PRIVATE_KEYS = {"chain_of_thought", "private_chain_of_thought", "private_reasoning", "scratchpad"}
VAGUE_ONLY = {"tests passed", "test passed", "best practice", "best practices", "feasible"}


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def _normalized_phrase(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def _is_vague_only(value: Any) -> bool:
    return isinstance(value, str) and _normalized_phrase(value) in VAGUE_ONLY


def validate_document(document: Any, require_mwu: bool = False) -> list[str]:
    if not isinstance(document, dict):
        return ["document_must_be_mapping"]
    unit = document.get("minimum_work_unit_output")
    if unit is None:
        return ["missing_minimum_work_unit_output"] if require_mwu else []
    if not isinstance(unit, dict):
        return ["minimum_work_unit_output_must_be_mapping"]

    errors: list[str] = []
    forbidden = PRIVATE_KEYS.intersection(unit)
    if forbidden:
        errors.append("private_reasoning_keys_prohibited:" + ",".join(sorted(forbidden)))

    role = unit.get("role")
    if role not in ROLE_FIELDS:
        errors.append("role_must_be_one_of:" + ",".join(ROLE_FIELDS))

    for field in CORE_FIELDS:
        if not _present(unit.get(field)):
            errors.append(f"missing_or_empty:{field}")
    for field in ("supportability_rationale", "feasibility_rationale"):
        if _is_vague_only(unit.get(field)):
            errors.append(f"vague_rationale_alone:{field}")

    if role in ROLE_FIELDS:
        for field in ROLE_FIELDS[role]:
            if not _present(unit.get(field)):
                errors.append(f"missing_or_empty:{field}")

    if role == "independent_review":
        assessment = unit.get("executor_rationale_assessment")
        if assessment is not None and not isinstance(assessment, dict):
            errors.append("executor_rationale_assessment_must_be_mapping")
        elif isinstance(assessment, dict):
            for field in ASSESSMENT_FIELDS:
                if field not in assessment:
                    errors.append(f"missing_executor_rationale_assessment_field:{field}")
                elif field != "unsupported_or_inferred_claims" and not _present(assessment[field]):
                    errors.append(f"empty_executor_rationale_assessment_field:{field}")
    return errors


def _valid_examples() -> list[dict[str, Any]]:
    core = {
        "work_performed_or_requested": "Bind a material work unit to the canonical contract.",
        "implementation_or_review_method": "Use the versioned contract and validator over the exact artifact.",
        "supportability_rationale": "The requirement is explicit in the canonical contract and is checked by the validator.",
        "feasibility_rationale": "The artifact is YAML in the current task boundary and can be checked without protected actions.",
    }
    return [
        {"minimum_work_unit_output": {"role": "decision_architecture", **core,
            "task_constraints_and_boundaries": ["do not change authority"],
            "stop_or_return_conditions": ["return on new semantic choice"]}},
        {"minimum_work_unit_output": {"role": "execution", **core,
            "exact_result_or_candidate_ref": "commit:example",
            "verification_evidence": ["validator exit 0"],
            "residual_risk_or_unproved_limits": ["not independently reviewed"]}},
        {"minimum_work_unit_output": {"role": "independent_review", **core,
            "verdict": "PASS", "primary_evidence_examined": ["contract", "candidate diff"],
            "findings_and_residual_risk": ["sample does not prove external integration"],
            "executor_rationale_assessment": {
                "supportability_assessment": "supported by the cited contract and diff",
                "feasibility_assessment": "supported by the observed repository surface",
                "primary_evidence_refs": ["contract", "candidate diff"],
                "unsupported_or_inferred_claims": []}}},
    ]


def run_selftests() -> tuple[int, list[str]]:
    failures: list[str] = []
    total = 0
    for idx, example in enumerate(_valid_examples(), 1):
        total += 1
        errs = validate_document(example, require_mwu=True)
        if errs:
            failures.append(f"valid_{idx}_rejected:{errs}")

    negatives = [
        ({"minimum_work_unit_output": {"role": "decision_architecture",
            "work_performed_or_requested": "x", "implementation_or_review_method": "x",
            "supportability_rationale": "tests passed", "feasibility_rationale": "specific current repo path exists",
            "task_constraints_and_boundaries": ["x"], "stop_or_return_conditions": ["x"]}},
         "vague_rationale_alone:supportability_rationale"),
        ({"minimum_work_unit_output": {"role": "independent_review",
            "work_performed_or_requested": "x", "implementation_or_review_method": "x",
            "supportability_rationale": "specific evidence x", "feasibility_rationale": "specific environment x",
            "verdict": "PASS", "primary_evidence_examined": ["x"], "findings_and_residual_risk": ["x"],
            "executor_rationale_assessment": {"supportability_assessment": "x", "feasibility_assessment": "x",
                "unsupported_or_inferred_claims": []}}},
         "missing_executor_rationale_assessment_field:primary_evidence_refs"),
        ({"minimum_work_unit_output": {"role": "execution",
            "work_performed_or_requested": "x", "implementation_or_review_method": "x",
            "supportability_rationale": "specific evidence x", "feasibility_rationale": "specific environment x",
            "exact_result_or_candidate_ref": "x", "verification_evidence": ["x"],
            "residual_risk_or_unproved_limits": ["x"], "chain_of_thought": "must never be requested"}},
         "private_reasoning_keys_prohibited:chain_of_thought"),
    ]
    for idx, (example, expected) in enumerate(negatives, 1):
        total += 1
        errs = validate_document(example, require_mwu=True)
        if expected not in errs:
            failures.append(f"negative_{idx}_not_rejected:{errs}")

    total += 1
    if validate_document({"legacy": "artifact"}, require_mwu=False):
        failures.append("legacy_artifact_rejected")
    total += 1
    if "missing_minimum_work_unit_output" not in validate_document({"new": "formal"}, require_mwu=True):
        failures.append("required_MWU_missing_not_rejected")
    return total, failures


def validate_static(root: Path) -> list[str]:
    paths = {
        "readme": root / "01_os/03_mechanisms/minimum_work_unit_output/README.md",
        "contract": root / "01_os/03_mechanisms/minimum_work_unit_output/最小工作单元输出契约_v1.yml",
        "boot": root / "01_os/02_boot/minimum_work_unit_output/启动清单_v1.yml",
        "registry": root / "01_os/05_registry/minimum_work_unit_output_v1.yml",
        "validator_readme": root / "01_os/06_execution/boot/minimum_work_unit_output/README.md",
        "os_readme": root / "01_os/README.md",
        "mechanisms_readme": root / "01_os/03_mechanisms/README.md",
    }
    errors = [f"missing_path:{p}" for p in paths.values() if not p.exists()]
    if errors:
        return errors
    contract = _load_yaml(paths["contract"])
    boot = _load_yaml(paths["boot"])
    registry = _load_yaml(paths["registry"])
    if contract.get("authority_effect") != "none":
        errors.append("contract_authority_effect_must_be_none")
    if contract.get("scope_effect") != "none":
        errors.append("contract_scope_effect_must_be_none")
    if contract.get("minimum_work_unit_required_fields") != list(CORE_FIELDS):
        errors.append("contract_core_fields_drift")
    if set(contract.get("role_specific_requirements", {})) != set(ROLE_FIELDS):
        errors.append("contract_role_set_drift")
    if boot.get("validator") != "01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py":
        errors.append("boot_validator_pointer_drift")
    if boot.get("registry") != "01_os/05_registry/minimum_work_unit_output_v1.yml":
        errors.append("boot_registry_pointer_drift")
    if boot.get("authority_effect") != "none":
        errors.append("boot_authority_effect_must_be_none")
    if registry.get("registry_id") != "minimum_work_unit_output_v1":
        errors.append("registry_id_drift")
    for path in (paths["os_readme"], paths["mechanisms_readme"]):
        if "minimum_work_unit_output" not in path.read_text(encoding="utf-8"):
            errors.append(f"navigation_marker_missing:{path}:minimum_work_unit_output")
    _, selftest_failures = run_selftests()
    errors.extend(f"selftest:{x}" for x in selftest_failures)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("static", "artifact", "selftest"))
    parser.add_argument("path", nargs="?")
    parser.add_argument("--root", default=".")
    parser.add_argument("--require-mwu", action="store_true")
    args = parser.parse_args()

    if args.mode == "selftest":
        total, failures = run_selftests()
        if failures:
            print(json.dumps({"status": "validation_failed", "mode": "selftest", "failures": failures}, ensure_ascii=False))
            return 1
        print(f"validation_passed mode=selftest cases={total}")
        return 0
    if args.mode == "artifact":
        if not args.path:
            parser.error("artifact mode requires path")
        errors = validate_document(_load_yaml(Path(args.path)), require_mwu=args.require_mwu)
        if errors:
            print(json.dumps({"status": "validation_failed", "mode": "artifact", "errors": errors}, ensure_ascii=False))
            return 1
        print("validation_passed mode=artifact")
        return 0

    errors = validate_static(Path(args.root).resolve())
    if errors:
        print(json.dumps({"status": "validation_failed", "mode": "static", "errors": errors}, ensure_ascii=False))
        return 1
    total, _ = run_selftests()
    print(f"validation_passed mode=static selftests={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

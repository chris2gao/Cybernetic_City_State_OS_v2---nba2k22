#!/usr/bin/env python3
"""Minimum Work Unit Output validator.

Machine enforcement boundary
----------------------------
This validator implements a deterministic *structural* anti-vacuity floor only:
required text type, non-emptiness, a closed set of generic-only forms, a minimum
content-token count, a closed verdict enum, and set containment between an
independent review's assessment evidence refs and the primary evidence that same
review declares it examined.

Passing these checks proves those structural properties and nothing wider. It does
not prove that a rationale is true, sufficient or task-appropriate, and it does not
prove that a reviewer actually attacked the executor rationale. Full semantic
sufficiency remains load-bearing independent-review judgement.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
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

RATIONALE_TEXT_FIELDS = ("supportability_rationale", "feasibility_rationale")
ASSESSMENT_TEXT_FIELDS = ("supportability_assessment", "feasibility_assessment")
VERDICT_VALUES = ("PASS", "FIX_REQUIRED", "REJECT")

MIN_CONTENT_TOKENS = 3
FILLER_TOKENS = frozenset({
    "a", "an", "the", "this", "that", "these", "those", "it", "its",
    "is", "are", "was", "were", "be", "been", "being",
    "and", "or", "of", "to", "in", "on", "for", "with", "by", "as", "at", "from",
    "all", "we", "i", "our", "my", "us",
    "has", "have", "had", "will", "can", "could", "should", "would", "do", "does", "did",
    "so", "very", "quite", "fully", "completely", "successfully", "just", "also", "work",
})
GENERIC_ONLY = frozenset({
    "tests passed", "test passed", "tests pass", "passed", "pass",
    "feasible", "feasibility", "supported", "supportable",
    "best practice", "best practices",
    "ok", "okay", "fine", "good", "done", "works", "correct", "verified", "valid",
    "no issues", "looks good", "lgtm", "yes", "true", "n a", "na", "nothing", "none",
})

BOOT_LOAD_ORDER = (
    "01_os/03_mechanisms/minimum_work_unit_output/README.md",
    "01_os/03_mechanisms/minimum_work_unit_output/最小工作单元输出契约_v1.yml",
)
REGISTRY_ENTRY_PATHS = (
    "01_os/03_mechanisms/minimum_work_unit_output/**",
    "01_os/02_boot/minimum_work_unit_output/**",
    "01_os/06_execution/boot/minimum_work_unit_output/**",
    "01_os/05_registry/minimum_work_unit_output_v1.yml",
)
STATIC_CONSUMED_PATHS = {
    "readme": "01_os/03_mechanisms/minimum_work_unit_output/README.md",
    "contract": "01_os/03_mechanisms/minimum_work_unit_output/最小工作单元输出契约_v1.yml",
    "boot": "01_os/02_boot/minimum_work_unit_output/启动清单_v1.yml",
    "registry": "01_os/05_registry/minimum_work_unit_output_v1.yml",
    "validator_readme": "01_os/06_execution/boot/minimum_work_unit_output/README.md",
    "os_readme": "01_os/README.md",
    "mechanisms_readme": "01_os/03_mechanisms/README.md",
}


class MWUParseError(Exception):
    """Clean, non-traceback parse failure for formal MWU artifacts."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that refuses duplicate mapping keys at any mapping level.

    Default SafeLoader applies last-key-wins silently, so two supportability_rationale
    keys can smuggle a second, contradictory value past the compliance gate.
    """


def _construct_mapping_unique(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    loader.flatten_mapping(node)
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            hash(key)
        except TypeError:
            raise MWUParseError(f"unhashable_mapping_key:{key!r}")
        if key in mapping:
            raise MWUParseError(f"duplicate_mapping_key:{key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.construct_mapping = _construct_mapping_unique  # type: ignore[assignment]
_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: _construct_mapping_unique(loader, node, deep=False),
)


def _load_yaml_text(text: str) -> Any:
    try:
        return yaml.load(text, Loader=_UniqueKeyLoader)
    except MWUParseError:
        raise
    except yaml.YAMLError as exc:
        raise MWUParseError("yaml_parse_error:" + type(exc).__name__)


def _load_yaml(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MWUParseError("unreadable_path:" + type(exc).__name__)
    return _load_yaml_text(text)


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


def _content_tokens(value: str) -> list[str]:
    return [t for t in _normalized_phrase(value).split() if t and t not in FILLER_TOKENS]


def _text_floor_errors(field: str, value: Any) -> list[str]:
    """Deterministic structural floor for a required justification text field.

    Returns at most one error code per field so the first structural defect is the
    reported one. Order: type, emptiness, generic-only form, content-token floor.
    """
    if value is None:
        return [f"missing_or_empty:{field}"]
    if not isinstance(value, str):
        return [f"rationale_must_be_text:{field}"]
    if not value.strip():
        return [f"missing_or_empty:{field}"]
    normalized = _normalized_phrase(value)
    if not normalized:
        return [f"missing_or_empty:{field}"]
    tokens = _content_tokens(value)
    if " ".join(tokens) in GENERIC_ONLY or normalized in GENERIC_ONLY:
        return [f"vague_rationale_alone:{field}"]
    if len(tokens) < MIN_CONTENT_TOKENS:
        return [f"rationale_below_content_floor:{field}"]
    return []


def _validate_independent_review(unit: dict) -> list[str]:
    """Bound the review verdict and structurally bind assessment refs to examined evidence.

    This proves only that the review declared an in-enum verdict, non-vacuous
    assessment text, and at least one evidence ref drawn from the evidence set the
    same review declares it examined. It does not prove the reviewer's reasoning is
    correct or that the assessment is semantically adequate.
    """
    errors: list[str] = []

    verdict = unit.get("verdict")
    if verdict not in VERDICT_VALUES:
        errors.append("verdict_must_be_one_of:" + ",".join(VERDICT_VALUES))

    examined = unit.get("primary_evidence_examined")
    examined_set: set[str] = set()
    if examined is not None and not isinstance(examined, (list, tuple)):
        errors.append("primary_evidence_examined_must_be_list")
    elif isinstance(examined, (list, tuple)):
        examined_set = {e.strip() for e in examined if isinstance(e, str) and e.strip()}

    assessment = unit.get("executor_rationale_assessment")
    if assessment is not None and not isinstance(assessment, dict):
        return errors + ["executor_rationale_assessment_must_be_mapping"]
    if not isinstance(assessment, dict):
        return errors

    for field in ASSESSMENT_FIELDS:
        if field not in assessment:
            errors.append(f"missing_executor_rationale_assessment_field:{field}")
        elif field != "unsupported_or_inferred_claims" and not _present(assessment[field]):
            errors.append(f"empty_executor_rationale_assessment_field:{field}")

    for field in ASSESSMENT_TEXT_FIELDS:
        if field in assessment and _present(assessment.get(field)):
            errors.extend(_text_floor_errors(field, assessment.get(field)))

    refs = assessment.get("primary_evidence_refs")
    if "primary_evidence_refs" in assessment:
        if not isinstance(refs, (list, tuple)):
            errors.append("primary_evidence_refs_must_be_list")
        else:
            cleaned = [r.strip() for r in refs if isinstance(r, str) and r.strip()]
            if len(cleaned) != len(refs):
                errors.append("primary_evidence_refs_must_be_nonempty_text_items")
            if not cleaned:
                errors.append("empty_executor_rationale_assessment_field:primary_evidence_refs")
            for ref in cleaned:
                if ref not in examined_set:
                    errors.append(f"assessment_evidence_ref_not_examined:{ref}")
    return errors


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
        if field in RATIONALE_TEXT_FIELDS:
            errors.extend(_text_floor_errors(field, unit.get(field)))
        elif not _present(unit.get(field)):
            errors.append(f"missing_or_empty:{field}")

    if role in ROLE_FIELDS:
        for field in ROLE_FIELDS[role]:
            if not _present(unit.get(field)):
                errors.append(f"missing_or_empty:{field}")

    if role == "independent_review":
        errors.extend(_validate_independent_review(unit))
    return errors


_CORE = {
    "work_performed_or_requested": "Bind a material work unit to the canonical contract.",
    "implementation_or_review_method": "Use the versioned contract and validator over the exact artifact.",
    "supportability_rationale": "The requirement is explicit in the canonical contract and is checked by the validator.",
    "feasibility_rationale": "The artifact is YAML in the current task boundary and can be checked without protected actions.",
}


def _architecture_unit(**overrides: Any) -> dict:
    unit = {"role": "decision_architecture", **_CORE,
            "task_constraints_and_boundaries": ["do not change authority"],
            "stop_or_return_conditions": ["return on new semantic choice"]}
    unit.update(overrides)
    return {"minimum_work_unit_output": unit}


def _execution_unit(**overrides: Any) -> dict:
    unit = {"role": "execution", **_CORE,
            "exact_result_or_candidate_ref": "commit:example",
            "verification_evidence": ["validator exit 0"],
            "residual_risk_or_unproved_limits": ["not independently reviewed"]}
    unit.update(overrides)
    return {"minimum_work_unit_output": unit}


def _review_unit(assessment_overrides: dict | None = None, **overrides: Any) -> dict:
    assessment = {
        "supportability_assessment": "supported by the cited contract and diff",
        "feasibility_assessment": "supported by the observed repository surface",
        "primary_evidence_refs": ["contract", "candidate diff"],
        "unsupported_or_inferred_claims": [],
    }
    if assessment_overrides is not None:
        assessment.update(assessment_overrides)
    unit = {"role": "independent_review", **_CORE,
            "verdict": "PASS", "primary_evidence_examined": ["contract", "candidate diff"],
            "findings_and_residual_risk": ["sample does not prove external integration"],
            "executor_rationale_assessment": assessment}
    unit.update(overrides)
    return {"minimum_work_unit_output": unit}


DUPLICATE_KEY_FIXTURE = """minimum_work_unit_output:
  role: execution
  work_performed_or_requested: Bind a material work unit to the canonical contract.
  implementation_or_review_method: Use the versioned contract and validator over the artifact.
  supportability_rationale: The requirement is explicit in the canonical contract text.
  feasibility_rationale: The artifact is YAML inside the current task boundary already.
  exact_result_or_candidate_ref: commit:example
  verification_evidence:
    - validator exit 0
  residual_risk_or_unproved_limits:
    - not independently reviewed
  supportability_rationale: true
"""

NESTED_DUPLICATE_KEY_FIXTURE = """minimum_work_unit_output:
  role: independent_review
  work_performed_or_requested: Review the exact candidate against primary evidence.
  implementation_or_review_method: Reconstruct from immutable commits and rerun commands.
  supportability_rationale: The verdict rests on reproduced command exit codes here.
  feasibility_rationale: Every cited artifact is readable at the exact commit given.
  verdict: PASS
  primary_evidence_examined:
    - contract
  findings_and_residual_risk:
    - none material
  executor_rationale_assessment:
    supportability_assessment: supported by the cited contract text
    feasibility_assessment: supported by the observed repository surface
    primary_evidence_refs:
      - contract
    unsupported_or_inferred_claims: []
    supportability_assessment: ok
"""


def _document_cases() -> list[tuple[str, dict, bool, str | None]]:
    """(case_id, document, expected_valid, expected_error_substring)."""
    return [
        ("positive_architecture", _architecture_unit(), True, None),
        ("positive_execution", _execution_unit(), True, None),
        ("positive_independent_review", _review_unit(), True, None),
        ("positive_concise_task_specific_rationale",
         _execution_unit(supportability_rationale="Registry entry names this loader.",
                         feasibility_rationale="Validator runs on existing PyYAML dependency."), True, None),
        ("negative_missing_core_work_performed_or_requested",
         _execution_unit(work_performed_or_requested=None), False, "missing_or_empty:work_performed_or_requested"),
        ("negative_missing_core_implementation_or_review_method",
         _execution_unit(implementation_or_review_method=None), False, "missing_or_empty:implementation_or_review_method"),
        ("negative_missing_core_supportability_rationale",
         _execution_unit(supportability_rationale=None), False, "missing_or_empty:supportability_rationale"),
        ("negative_missing_core_feasibility_rationale",
         _execution_unit(feasibility_rationale=None), False, "missing_or_empty:feasibility_rationale"),
        ("negative_bare_tests_passed",
         _architecture_unit(supportability_rationale="tests passed"), False, "vague_rationale_alone:supportability_rationale"),
        ("negative_bare_feasible",
         _architecture_unit(feasibility_rationale="feasible"), False, "vague_rationale_alone:feasibility_rationale"),
        ("negative_unknown_role", _execution_unit(role="wizard"), False, "role_must_be_one_of"),
        ("negative_container_not_mapping",
         {"minimum_work_unit_output": ["not", "a", "mapping"]}, False, "minimum_work_unit_output_must_be_mapping"),
        ("negative_private_chain_of_thought",
         _execution_unit(chain_of_thought="must never be requested"), False, "private_reasoning_keys_prohibited:chain_of_thought"),
        ("negative_reviewer_assessment_not_mapping",
         _review_unit(executor_rationale_assessment=["not", "a", "mapping"]), False,
         "executor_rationale_assessment_must_be_mapping"),
        ("negative_reviewer_missing_primary_evidence_refs",
         _review_unit(assessment_overrides={"primary_evidence_refs": None}), False,
         "empty_executor_rationale_assessment_field:primary_evidence_refs"),
        ("adversarial_generic_supportability_synonym",
         _execution_unit(supportability_rationale="All tests passed"), False, "vague_rationale_alone:supportability_rationale"),
        ("adversarial_generic_feasibility_sentence",
         _execution_unit(feasibility_rationale="This work is feasible"), False, "vague_rationale_alone:feasibility_rationale"),
        ("adversarial_non_text_rationales",
         _execution_unit(supportability_rationale=True, feasibility_rationale=1), False,
         "rationale_must_be_text:supportability_rationale"),
        ("adversarial_list_rationale",
         _execution_unit(supportability_rationale=["a", "b", "c"]), False, "rationale_must_be_text:supportability_rationale"),
        ("adversarial_mapping_rationale",
         _execution_unit(feasibility_rationale={"why": "because"}), False, "rationale_must_be_text:feasibility_rationale"),
        ("adversarial_single_content_token_rationale",
         _execution_unit(supportability_rationale="Deterministic."), False,
         "rationale_below_content_floor:supportability_rationale"),
        ("adversarial_unbounded_verdict", _review_unit(verdict="BANANA"), False, "verdict_must_be_one_of"),
        ("adversarial_lowercase_verdict", _review_unit(verdict="pass"), False, "verdict_must_be_one_of"),
        ("positive_fix_required_verdict", _review_unit(verdict="FIX_REQUIRED"), True, None),
        ("positive_reject_verdict", _review_unit(verdict="REJECT"), True, None),
        ("adversarial_disjoint_evidence_and_vague_assessment",
         _review_unit(primary_evidence_examined=["evidence:A"],
                      assessment_overrides={"primary_evidence_refs": ["evidence:B"],
                                            "supportability_assessment": "supported",
                                            "feasibility_assessment": "feasible"}), False,
         "assessment_evidence_ref_not_examined:evidence:B"),
        ("adversarial_disjoint_evidence_only",
         _review_unit(primary_evidence_examined=["evidence:A"],
                      assessment_overrides={"primary_evidence_refs": ["evidence:B"]}), False,
         "assessment_evidence_ref_not_examined:evidence:B"),
        ("adversarial_one_word_supportability_assessment",
         _review_unit(assessment_overrides={"supportability_assessment": "supported"}), False,
         "vague_rationale_alone:supportability_assessment"),
        ("adversarial_one_word_feasibility_assessment",
         _review_unit(assessment_overrides={"feasibility_assessment": "feasible"}), False,
         "vague_rationale_alone:feasibility_assessment"),
        ("adversarial_non_text_assessment",
         _review_unit(assessment_overrides={"supportability_assessment": 7}), False,
         "rationale_must_be_text:supportability_assessment"),
        ("adversarial_refs_not_list",
         _review_unit(assessment_overrides={"primary_evidence_refs": "contract"}), False,
         "primary_evidence_refs_must_be_list"),
        ("adversarial_partially_disjoint_refs",
         _review_unit(assessment_overrides={"primary_evidence_refs": ["contract", "evidence:Z"]}), False,
         "assessment_evidence_ref_not_examined:evidence:Z"),
    ]


def run_selftests() -> tuple[int, list[str]]:
    failures: list[str] = []
    total = 0

    for case_id, document, expected_valid, expected_error in _document_cases():
        total += 1
        errs = validate_document(document, require_mwu=True)
        if expected_valid and errs:
            failures.append(f"{case_id}_rejected:{errs}")
        elif not expected_valid and not errs:
            failures.append(f"{case_id}_accepted")
        elif not expected_valid and expected_error and not any(expected_error in e for e in errs):
            failures.append(f"{case_id}_wrong_error:{errs}")

    total += 1
    if validate_document({"legacy": "artifact"}, require_mwu=False):
        failures.append("legacy_without_declared_mwu_rejected")
    total += 1
    if "missing_minimum_work_unit_output" not in validate_document({"new": "formal"}, require_mwu=True):
        failures.append("negative_new_formal_output_missing_mwu_accepted")
    total += 1
    if validate_document(["not", "a", "mapping"], require_mwu=True) != ["document_must_be_mapping"]:
        failures.append("negative_document_not_mapping_accepted")

    total += 1
    try:
        _load_yaml_text(DUPLICATE_KEY_FIXTURE)
        failures.append("adversarial_duplicate_supportability_rationale_accepted")
    except MWUParseError as exc:
        if exc.code != "duplicate_mapping_key:supportability_rationale":
            failures.append(f"duplicate_key_wrong_code:{exc.code}")

    total += 1
    try:
        _load_yaml_text(NESTED_DUPLICATE_KEY_FIXTURE)
        failures.append("adversarial_nested_duplicate_assessment_key_accepted")
    except MWUParseError as exc:
        if exc.code != "duplicate_mapping_key:supportability_assessment":
            failures.append(f"nested_duplicate_key_wrong_code:{exc.code}")

    total += 1
    try:
        parsed = _load_yaml_text("minimum_work_unit_output:\n  role: execution\n")
        if not isinstance(parsed, dict):
            failures.append("unique_key_loader_broke_normal_parse")
    except MWUParseError as exc:
        failures.append(f"unique_key_loader_false_positive:{exc.code}")

    return total, failures


def validate_static(root: Path) -> list[str]:
    paths = {name: root / rel for name, rel in STATIC_CONSUMED_PATHS.items()}
    errors = [f"missing_path:{p}" for p in paths.values() if not p.exists()]
    if errors:
        return errors
    try:
        contract = _load_yaml(paths["contract"])
        boot = _load_yaml(paths["boot"])
        registry = _load_yaml(paths["registry"])
    except MWUParseError as exc:
        return ["canonical_parse_failed:" + exc.code]
    if not isinstance(contract, dict) or not isinstance(boot, dict) or not isinstance(registry, dict):
        return ["canonical_documents_must_be_mappings"]

    if contract.get("authority_effect") != "none":
        errors.append("contract_authority_effect_must_be_none")
    if contract.get("scope_effect") != "none":
        errors.append("contract_scope_effect_must_be_none")
    if contract.get("minimum_work_unit_required_fields") != list(CORE_FIELDS):
        errors.append("contract_core_fields_drift")

    roles = contract.get("role_specific_requirements")
    if not isinstance(roles, dict):
        errors.append("contract_role_specific_requirements_must_be_mapping")
    else:
        if set(roles) != set(ROLE_FIELDS):
            errors.append("contract_role_set_drift")
        for role, expected_additions in ROLE_FIELDS.items():
            block = roles.get(role)
            if not isinstance(block, dict):
                errors.append(f"contract_role_block_missing:{role}")
                continue
            if block.get("required_additions") != list(expected_additions):
                errors.append(f"contract_role_additions_drift:{role}")
        review_block = roles.get("independent_review")
        if isinstance(review_block, dict):
            if review_block.get("executor_rationale_assessment_required_fields") != list(ASSESSMENT_FIELDS):
                errors.append("contract_assessment_fields_drift")

    review_floor = contract.get("independent_review_machine_floor")
    if not isinstance(review_floor, dict):
        errors.append("contract_independent_review_machine_floor_missing")
    elif review_floor.get("verdict_allowed_values") != list(VERDICT_VALUES):
        errors.append("contract_verdict_enum_drift")

    rationale_floor = contract.get("rationale_machine_floor")
    if not isinstance(rationale_floor, dict):
        errors.append("contract_rationale_machine_floor_missing")
    else:
        if rationale_floor.get("minimum_content_tokens") != MIN_CONTENT_TOKENS:
            errors.append("contract_minimum_content_tokens_drift")
        if rationale_floor.get("generic_only_rejected_forms") != sorted(GENERIC_ONLY):
            errors.append("contract_generic_only_forms_drift")
        if rationale_floor.get("filler_tokens_removed_before_floor") != sorted(FILLER_TOKENS):
            errors.append("contract_filler_tokens_drift")

    if boot.get("validator") != "01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py":
        errors.append("boot_validator_pointer_drift")
    if boot.get("registry") != "01_os/05_registry/minimum_work_unit_output_v1.yml":
        errors.append("boot_registry_pointer_drift")
    if boot.get("authority_effect") != "none":
        errors.append("boot_authority_effect_must_be_none")
    load_order = boot.get("load_order")
    observed_load_order: list[str] = []
    if isinstance(load_order, (list, tuple)):
        for item in load_order:
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                observed_load_order.append(item["path"])
            elif isinstance(item, str):
                observed_load_order.append(item)
    if observed_load_order != list(BOOT_LOAD_ORDER):
        errors.append("boot_load_order_drift")

    if registry.get("registry_id") != "minimum_work_unit_output_v1":
        errors.append("registry_id_drift")
    entries = registry.get("entries")
    observed_entry_paths: list[str] = []
    if isinstance(entries, (list, tuple)):
        observed_entry_paths = [e["path"] for e in entries if isinstance(e, dict) and isinstance(e.get("path"), str)]
    if set(observed_entry_paths) != set(REGISTRY_ENTRY_PATHS):
        errors.append("registry_entry_path_set_drift")

    for path in (paths["os_readme"], paths["mechanisms_readme"]):
        if "minimum_work_unit_output" not in path.read_text(encoding="utf-8"):
            errors.append(f"navigation_marker_missing:{path}:minimum_work_unit_output")

    _, selftest_failures = run_selftests()
    errors.extend(f"selftest:{x}" for x in selftest_failures)
    return errors


def _mutate_execution_role_additions(contract: dict, boot: dict, registry: dict) -> None:
    contract["role_specific_requirements"]["execution"]["required_additions"] = ["exact_result_or_candidate_ref"]


def _mutate_assessment_fields(contract: dict, boot: dict, registry: dict) -> None:
    contract["role_specific_requirements"]["independent_review"]["executor_rationale_assessment_required_fields"] = []


def _mutate_boot_load_order(contract: dict, boot: dict, registry: dict) -> None:
    boot["load_order"] = []


def _mutate_registry_entries(contract: dict, boot: dict, registry: dict) -> None:
    registry["entries"] = []


def _mutate_verdict_enum(contract: dict, boot: dict, registry: dict) -> None:
    contract["independent_review_machine_floor"]["verdict_allowed_values"] = ["PASS", "FIX_REQUIRED", "REJECT", "BANANA"]


def _mutate_content_token_floor(contract: dict, boot: dict, registry: dict) -> None:
    contract["rationale_machine_floor"]["minimum_content_tokens"] = 0


def _mutate_generic_forms(contract: dict, boot: dict, registry: dict) -> None:
    contract["rationale_machine_floor"]["generic_only_rejected_forms"] = []


def _mutate_load_order_reordered(contract: dict, boot: dict, registry: dict) -> None:
    boot["load_order"] = list(reversed(boot["load_order"]))


STATIC_DRIFT_MUTATIONS = (
    ("adversarial_static_role_additions_drift", _mutate_execution_role_additions, "contract_role_additions_drift:execution"),
    ("adversarial_static_assessment_fields_drift", _mutate_assessment_fields, "contract_assessment_fields_drift"),
    ("adversarial_static_boot_load_order_erased", _mutate_boot_load_order, "boot_load_order_drift"),
    ("adversarial_static_registry_entries_erased", _mutate_registry_entries, "registry_entry_path_set_drift"),
    ("adversarial_static_verdict_enum_drift", _mutate_verdict_enum, "contract_verdict_enum_drift"),
    ("adversarial_static_content_token_floor_drift", _mutate_content_token_floor, "contract_minimum_content_tokens_drift"),
    ("adversarial_static_generic_forms_erased", _mutate_generic_forms, "contract_generic_only_forms_drift"),
    ("adversarial_static_boot_load_order_reordered", _mutate_load_order_reordered, "boot_load_order_drift"),
)


def _copy_consumed_paths(root: Path, target: Path) -> None:
    for rel in STATIC_CONSUMED_PATHS.values():
        src = root / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)


def validate_drift(root: Path) -> tuple[int, list[str]]:
    """Prove that the static bindings actually fire on shadow mutations.

    Copies only the paths validate_static consumes into an isolated temporary root,
    applies one named mutation at a time, and requires the expected static error.
    The repository under `root` is never written to.
    """
    failures: list[str] = []
    total = 0

    with tempfile.TemporaryDirectory(prefix="mwu-drift-") as tmp:
        control = Path(tmp) / "control"
        _copy_consumed_paths(root, control)
        total += 1
        control_errors = validate_static(control)
        if control_errors:
            failures.append(f"control_shadow_root_not_clean:{control_errors}")

        for case_id, mutate, expected_error in STATIC_DRIFT_MUTATIONS:
            total += 1
            target = Path(tmp) / case_id
            _copy_consumed_paths(root, target)
            contract_path = target / STATIC_CONSUMED_PATHS["contract"]
            boot_path = target / STATIC_CONSUMED_PATHS["boot"]
            registry_path = target / STATIC_CONSUMED_PATHS["registry"]
            try:
                contract = _load_yaml(contract_path)
                boot = _load_yaml(boot_path)
                registry = _load_yaml(registry_path)
                mutate(contract, boot, registry)
            except (MWUParseError, KeyError, TypeError) as exc:
                failures.append(f"{case_id}_mutation_setup_failed:{type(exc).__name__}")
                continue
            for path, doc in ((contract_path, contract), (boot_path, boot), (registry_path, registry)):
                path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
            errors = validate_static(target)
            if not errors:
                failures.append(f"{case_id}_accepted")
            elif not any(expected_error in e for e in errors):
                failures.append(f"{case_id}_wrong_error:{errors}")

    return total, failures


def _fail(mode: str, errors: list[str]) -> int:
    print(json.dumps({"status": "validation_failed", "mode": mode, "errors": errors}, ensure_ascii=False))
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("static", "artifact", "selftest", "drift"))
    parser.add_argument("path", nargs="?")
    parser.add_argument("--root", default=".")
    parser.add_argument("--require-mwu", action="store_true")
    args = parser.parse_args()

    if args.mode == "selftest":
        total, failures = run_selftests()
        if failures:
            return _fail("selftest", failures)
        print(f"validation_passed mode=selftest cases={total}")
        return 0

    if args.mode == "artifact":
        if not args.path:
            parser.error("artifact mode requires path")
        try:
            document = _load_yaml(Path(args.path))
        except MWUParseError as exc:
            return _fail("artifact", [exc.code])
        errors = validate_document(document, require_mwu=args.require_mwu)
        if errors:
            return _fail("artifact", errors)
        print("validation_passed mode=artifact")
        return 0

    if args.mode == "drift":
        root = Path(args.root).resolve()
        total, failures = validate_drift(root)
        if failures:
            return _fail("drift", failures)
        print(f"validation_passed mode=drift cases={total}")
        return 0

    errors = validate_static(Path(args.root).resolve())
    if errors:
        return _fail("static", errors)
    total, _ = run_selftests()
    print(f"validation_passed mode=static selftests={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

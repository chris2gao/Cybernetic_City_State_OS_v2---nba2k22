#!/usr/bin/env python3
"""Deterministic validator for the staged stage-collaborative-deliberation mechanism."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

PASS = 0
EXIT = {
    "missing": 10,
    "schema": 11,
    "stale": 12,
    "reference": 13,
    "invariant": 14,
    "unauthorized": 15,
    "profile": 16,
    "receipt": 17,
    "review": 18,
    "internal": 19,
}

FAILURE_TO_EXIT = {
    "missing_partial_or_stale_load_fail_open": 12,
    "unknown_dependency_fail_open": 13,
    "agreement_used_as_fact_proof": 14,
    "grounding_collapsed_into_authority": 14,
    "silence_or_response_as_agreement": 14,
    "residual_objection_erased": 14,
    "option_selection_used_as_truth": 14,
    "recommendation_used_as_authorization": 15,
    "authority_used_as_epistemic_truth": 14,
    "unbound_or_ambiguous_confirmation": 15,
    "silent_or_unscoped_invalidation": 14,
    "unverified_model_agreement_as_independent_confirmation": 18,
    "executor_self_clearance": 18,
    "execution_without_current_authority": 15,
    "premature_completion": 14,
    "collapsed_state_dimensions": 14,
    "unjustified_micro_approval_escalation": 14,
    "headcount_used_as_disposition": 14,
    "unapproved_second_order_scope_expansion": 15,
    "deferred_detail_not_durable": 14,
    "unnormalized_external_material": 14,
    "stage_profile_main_obligation_missing": 16,
    "receipt_detail_visibility_missing": 17,
    "formalistic_round_counting": 16,
    "unjustified_full_activation": 16,
    "load_bearing_gap_silently_skipped": 16,
}

REQUIRED_STATIC_PATHS = [
    "01_os/03_mechanisms/stage_collaborative_deliberation/README.md",
    "01_os/03_mechanisms/stage_collaborative_deliberation/方法论_v1.md",
    "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profile契约_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profiles_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现/结果对象契约_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现/状态转换与不变量契约_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现/路由与失败契约_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现/加载与receipt契约_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation.py",
    "01_os/02_boot/stage_collaborative_deliberation/启动清单_v1.yml",
    "01_os/05_registry/stage_collaborative_deliberation_v1.yml",
    "01_os/06_execution/boot/stage_collaborative_deliberation/README.md",
]
WORKFLOW_PROFILE_REFERENCE_GLOB = "01_os/01_workflow/*/实现/阶段协同推演profile引用_v1.yml"
REQUIRED_RECEIPT_FIELDS = [
    "receipt_schema_version","mechanism_version","active_contract_version",
    "boot_manifest_version","registry_version","loader_version",
    "profile_id_and_version","loaded_paths","missing_partial_or_stale_paths",
    "trigger_evaluation_result_ref","activation_mode_or_dormant_reason",
    "main_mechanism_ref","detail_granularity_evaluation_result",
    "open_detail_divergence_event_refs","deferred_detail_record_refs",
    "gate_results","validator_mode_and_exit_code","exact_candidate_version",
    "created_by_actor_ref","created_at",
]

def load_doc(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    if yaml is None:
        try:
            return json.loads(text)
        except Exception as exc:
            raise RuntimeError("PyYAML unavailable and file is not JSON") from exc
    return yaml.safe_load(text)

def select_case(doc: Any, case_id: str | None) -> Any:
    if isinstance(doc, dict) and "cases" in doc:
        if not case_id:
            raise ValueError("--case-id is required for suite files")
        for case in doc["cases"]:
            if case.get("case_id") == case_id:
                return case
        raise KeyError(f"case not found: {case_id}")
    return doc

def direct_error_code(data: dict[str, Any]) -> int:
    order = [
        ("internal_error", 19), ("review_execution_errors", 18),
        ("receipt_errors", 17), ("profile_gate_errors", 16),
        ("unauthorized_actions", 15), ("invariant_violations", 14),
        ("unresolved_refs", 13), ("stale_components", 12),
        ("schema_mismatch", 11), ("missing_required_paths", 10),
    ]
    for key, code in order:
        value = data.get(key)
        if value:
            return code
    failure_code = data.get("failure_code")
    if failure_code:
        return FAILURE_TO_EXIT.get(failure_code, 14)
    return 0

def validate_static_fixture(data: dict[str, Any]) -> int:
    code = direct_error_code(data)
    if code:
        return code
    snapshot = data.get("snapshot")
    if snapshot is None:
        return 0
    if snapshot.get("required_paths_resolve") is not True:
        return 10
    if snapshot.get("mechanism_version") != 1:
        return 11
    expected = {
        "profiles": 7,
        "object_types": 45,
        "result_names": 47,
        "state_dimensions": 10,
        "active_invariants": 16,
        "failure_codes": 26,
        "workflow_references": 7,
    }
    if any(snapshot.get(k) != v for k, v in expected.items()):
        return 11
    if snapshot.get("activation_state") != "staged_inert":
        return 15
    return 0

def validate_static_repo(repo_root: Path) -> int:
    missing = [p for p in REQUIRED_STATIC_PATHS if not (repo_root / p).exists()]
    if missing:
        return 10
    try:
        profile_set = load_doc(repo_root / REQUIRED_STATIC_PATHS[3])
        result_contract = load_doc(repo_root / REQUIRED_STATIC_PATHS[4])
        invariant_contract = load_doc(repo_root / REQUIRED_STATIC_PATHS[5])
        router_contract = load_doc(repo_root / REQUIRED_STATIC_PATHS[6])
        load_contract = load_doc(repo_root / REQUIRED_STATIC_PATHS[7])
        boot = load_doc(repo_root / REQUIRED_STATIC_PATHS[9])
        registry = load_doc(repo_root / REQUIRED_STATIC_PATHS[10])
    except Exception:
        return 11
    profiles = profile_set.get("profiles", [])
    active_profile_ids = {p.get("profile_id") for p in profiles}
    if len(profiles) != 7 or len(active_profile_ids) != 7 or None in active_profile_ids:
        return 16
    workflow_ref_paths = sorted(repo_root.glob(WORKFLOW_PROFILE_REFERENCE_GLOB))
    if len(workflow_ref_paths) != 7:
        return 16
    try:
        workflow_refs = [load_doc(path) for path in workflow_ref_paths]
    except Exception:
        return 11
    workflow_profile_ids = [ref.get("profile_id") if isinstance(ref, dict) else None for ref in workflow_refs]
    if len(set(workflow_profile_ids)) != 7 or set(workflow_profile_ids) != active_profile_ids:
        return 16
    if result_contract.get("measurements", {}).get("catalog_unique_object_types") != 45:
        return 11
    if invariant_contract.get("measurements", {}).get("active_invariants") != 16:
        return 11
    union = router_contract.get("complete_failure_code_union", [])
    codes = [x["code"] if isinstance(x, dict) else x for x in union]
    if len(codes) != 26 or len(set(codes)) != 26:
        return 11
    required = set(load_contract.get("stage_receipt", {}).get("required_fields", []))
    if not set(REQUIRED_RECEIPT_FIELDS).issubset(required):
        return 17
    versions = {
        boot.get("mechanism_version"), registry.get("mechanism_version"),
        result_contract.get("mechanism_version"), invariant_contract.get("mechanism_version"),
        router_contract.get("mechanism_version"), load_contract.get("mechanism_version"),
    }
    if versions != {1}:
        return 11
    if boot.get("activation_state") != "staged_inert" or registry.get("activation_state") != "staged_inert":
        return 15
    return 0

READINESS_REQUIRED_MODEL_FIELDS = (
    "problem_or_objective",
    "proposed_method",
    "feasibility_support",
    "verification_method",
)
RESOLVED_DISPOSITIONS = {"resolved", "deferred_non_blocking"}
# Nothing in this set is a Human decision, however it is labelled.
NON_DISPOSITION_BASIS_KINDS = {"silence", "no_response", "inferred", "implied", "assumed"}
# Only the current Human confirms. No model-side actor substitutes for that.
NON_HUMAN_ACTOR_CLASSES = {"executor", "reviewer", "independent_reviewer", "model", "agent"}
# The common model fields that must be complete before substantive execution.
STAGE_MODEL_COMPLETENESS_FIELDS = (
    "problem_or_objective",
    "Human_intent_understanding",
    "current_baseline_and_inputs",
    "proposed_method",
    "feasibility_support",
    "expected_output",
    "verification_method",
    "current_exact_model_version",
)


def validate_mandatory_Human_confirmation(model: dict[str, Any]) -> int:
    """Every task and every workflow stage must project the current model to the
    current Human and obtain an explicit confirmation bound to the exact current
    model version before any substantive execution.

    This is mandatory even when no load-bearing gap exists - in that case the
    required form is one concise proposal and one explicit confirmation, not a
    fixed number of rounds, a long form, or per-choice micro-approval.

    None of the following ever substitutes for the current stage's confirmation:
    Human silence or non-response, inferred consent, a previous stage's
    confirmation, a confirmation bound to an older model version, or a
    confirmation produced by an executor, reviewer or any other non-Human actor.
    """
    confirmation = model.get("Human_confirmation")
    if not isinstance(confirmation, dict):
        return 15
    if confirmation.get("explicit") is not True:
        return 14
    if confirmation.get("kind") in NON_DISPOSITION_BASIS_KINDS:
        return 14
    if confirmation.get("actor_class") in NON_HUMAN_ACTOR_CLASSES:
        return 15
    if confirmation.get("actor_class") != "current_Human":
        return 15
    if confirmation.get("scope") not in {None, "current_stage", "current_task"}:
        return 12
    if confirmation.get("stale") is True:
        return 12
    bound = confirmation.get("bound_model_version")
    if not bound or bound != model.get("current_exact_model_version"):
        return 12
    return 0


def validate_model_readiness(data: dict[str, Any]) -> int:
    """Readiness of the single Current Model, in every activation mode.

    dormant means "the model is already adequate and no new load-bearing gap
    exists", never "no model was built" - so the model is required here too.
    """
    model = data.get("current_model")
    if not isinstance(model, dict):
        return 16
    # current_stage_model_complete AND proposed_method AND feasibility_support
    # AND verification AND explicit current-Human confirmation of the exact model
    # version -> substantive execution allowed. All five are required together.
    for field in STAGE_MODEL_COMPLETENESS_FIELDS:
        if not model.get(field):
            return 16
    code = validate_mandatory_Human_confirmation(model)
    if code:
        return code

    open_items = model.get("open_load_bearing_items") or []
    for item in open_items:
        if not isinstance(item, dict):
            return 11
        disposition = item.get("disposition")
        if disposition not in RESOLVED_DISPOSITIONS:
            # an unresolved blocking load-bearing question is not readiness
            return 16
        if disposition != "resolved":
            continue
        basis = item.get("Human_basis")
        if item.get("load_bearing") and not basis:
            return 15
        if isinstance(basis, dict):
            # silence, non-response or inferred consent never becomes a decision
            if basis.get("kind") in NON_DISPOSITION_BASIS_KINDS:
                return 14
            if basis.get("stale") is True:
                return 12

    # ordinary local reversible choices stay model-owned; demanding Human sign-off
    # on them is the micro-approval escalation the mechanism forbids
    for choice in model.get("ordinary_local_choices") or []:
        if isinstance(choice, dict) and choice.get("requires_Human_confirmation") is True:
            return 14

    # never re-ask something the Human already resolved
    for inquiry in data.get("inquiry_items") or []:
        if isinstance(inquiry, dict) and inquiry.get("re_asks_resolved_input") is True:
            return 14

    # Absence of a load-bearing gap must not force *additional* inquiry rounds.
    # It never waives the mandatory projection and confirmation checked above.
    if not open_items and data.get("additional_inquiry_required") is True:
        return 16
    # round counts must not be reintroduced as a readiness basis by any caller
    if data.get("readiness_basis") == "substantive_round_count":
        return 16

    alignment = model.get("Human_alignment")
    if isinstance(alignment, dict):
        if alignment.get("stale") is True:
            return 12
        bound = alignment.get("bound_model_version")
        if bound and bound != model.get("current_exact_model_version"):
            return 12

    completion = model.get("completion")
    if isinstance(completion, dict):
        bound_output = completion.get("bound_output_version")
        if bound_output and bound_output != model.get("current_exact_output_version"):
            return 12
        if completion.get("progression_requested") is True:
            if completion.get("actual_result") is None:
                return 14
            if not completion.get("verification_result"):
                return 14
    return 0


def validate_stage_child_composition(data: dict[str, Any], receipt: dict[str, Any]) -> int:
    """CR-005: a seven-stage-loop child must compose the complete base stage
    receipt validation and then overlay alignment and stage/profile binding.
    Running only the overlay, or a receipt subset, is not acceptance."""
    if data.get("seven_stage_child") is not True:
        return 0
    if receipt.get("base_receipt_validation") != "complete":
        return 17
    if any(k not in receipt for k in REQUIRED_RECEIPT_FIELDS):
        return 17
    for binding in ("alignment_binding", "profile_binding"):
        if not receipt.get(binding):
            return 17
    return 0


def validate_completion_pointer(data: dict[str, Any]) -> int:
    """RR2-001: after a material candidate change the completion pointer must be
    append-only and bind the exact final semantic candidate, not a superseded one."""
    pointer = data.get("completion_pointer")
    if not isinstance(pointer, dict):
        return 0
    if pointer.get("append_only") is not True:
        return 14
    model = data.get("current_model") or {}
    expected = model.get("current_exact_output_version")
    if expected and pointer.get("bound_candidate_version") != expected:
        return 12
    if pointer.get("supersedes") and not pointer.get("supersedes_record_ref"):
        return 14
    return 0


def validate_instance(data: dict[str, Any]) -> int:
    code = direct_error_code(data)
    if code:
        return code
    mode = data.get("activation_mode")
    if mode not in {"dormant","full","incremental"}:
        return 11
    if mode == "dormant" and not data.get("dormant_reason"):
        return 16
    # Readiness, not round counts, decides whether the stage may progress. Fixed
    # minimum substantive rounds (full=5, incremental=2) were removed: how many
    # rounds occurred never proved that the model was adequate, and requiring
    # them manufactured discussion where no load-bearing gap existed.
    code = validate_model_readiness(data)
    if code:
        return code
    receipt = data.get("receipt")
    if not isinstance(receipt, dict):
        return 17
    if any(k not in receipt for k in REQUIRED_RECEIPT_FIELDS):
        return 17
    if receipt.get("validator_mode_and_exit_code", {}).get("exit_code") != 0:
        return 17
    code = validate_stage_child_composition(data, receipt)
    if code:
        return code
    return validate_completion_pointer(data)

def validate_material_event(data: dict[str, Any]) -> int:
    code = direct_error_code(data)
    if code:
        return code
    for key in ("event_id","exact_source_ref","dependency_graph_version","impact"):
        if key not in data:
            return 10
    impact = data["impact"]
    for key in ("affected","unaffected","unknown"):
        if key not in impact:
            return 11
    if impact["unknown"] and not data.get("unknown_scope_blocked"):
        return 13
    if not data.get("successor_or_reconfirmation_recorded"):
        return 14
    return 0

def validate_review_execution(data: dict[str, Any]) -> int:
    code = direct_error_code(data)
    if code:
        return code
    required = ("task_ref","branch","base","head","allowlist","Human_authorization_ref",
                "executor","independent_reviewer","verification")
    if any(k not in data for k in required):
        return 10
    if data["executor"] == data["independent_reviewer"]:
        return 18
    changed = set(data.get("changed_paths", []))
    allowed = set(data.get("allowlist", []))
    if changed - allowed:
        return 18
    if not data.get("Human_authorization_ref"):
        return 15
    verification = data["verification"]
    if data.get("implementation_complete") and verification.get("status") != "verified":
        return 18
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("static","instance","material_event","review_execution"))
    parser.add_argument("target")
    parser.add_argument("--case-id")
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args()
    try:
        target = Path(args.target)
        if args.mode == "static" and target.is_dir():
            code = validate_static_repo(target)
        else:
            data = select_case(load_doc(target), args.case_id)
            if not isinstance(data, dict):
                code = 11
            else:
                payload = data.get("data", data)
                if args.mode == "static":
                    code = validate_static_fixture(payload)
                elif args.mode == "instance":
                    code = validate_instance(payload)
                elif args.mode == "material_event":
                    code = validate_material_event(payload)
                else:
                    code = validate_review_execution(payload)
        if args.json_output:
            print(json.dumps({"mode": args.mode, "target": args.target, "case_id": args.case_id, "exit_code": code}))
        return code
    except Exception as exc:
        if args.json_output:
            print(json.dumps({"mode": args.mode, "target": args.target, "case_id": args.case_id, "exit_code": 19, "error": str(exc)}))
        return 19

if __name__ == "__main__":
    sys.exit(main())

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

def validate_instance(data: dict[str, Any]) -> int:
    code = direct_error_code(data)
    if code:
        return code
    mode = data.get("activation_mode")
    if mode not in {"dormant","full","incremental"}:
        return 11
    if mode == "dormant" and not data.get("dormant_reason"):
        return 16
    rounds = data.get("rounds", [])
    substantive = sum(1 for r in rounds if r.get("substantive") is True)
    if mode == "full" and substantive < 5:
        return 16
    if mode == "incremental" and substantive < 2:
        return 16
    receipt = data.get("receipt")
    if not isinstance(receipt, dict):
        return 17
    if any(k not in receipt for k in REQUIRED_RECEIPT_FIELDS):
        return 17
    if receipt.get("validator_mode_and_exit_code", {}).get("exit_code") != 0:
        return 17
    return 0

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

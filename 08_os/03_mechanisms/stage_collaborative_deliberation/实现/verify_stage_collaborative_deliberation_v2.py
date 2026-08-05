#!/usr/bin/env python3
"""Activation-aware validator for the stage collaborative deliberation mechanism."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

BASE_VALIDATOR_NAME = "verify_stage_collaborative_deliberation.py"
ACTIVATION_STATE_PATH = "08_os/03_mechanisms/stage_collaborative_deliberation/激活状态_v1.yml"
AUTHORIZATION_PATH = "08_os/_runs/run-20260804-阶段协同推演闭环激活-001/01_任务输入/Human授权_全局机制激活_v1.yml"
ACTIVE_VALIDATOR_PATH = "08_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation_v2.py"
ACTIVATION_STATE_BLOB = "8fcab2a3c92629e9c8a801a78128adb467aa5bab"
AUTHORIZATION_BLOB = "5d9d8be9e55c0c904a86907592b70d0a852d1567"
EXPECTED_ACTIVE_STATE = "active_dormant"
EXPECTED_PROFILE_IDS = {
    "workflow_stage_01_requirement_modeling",
    "workflow_stage_02_information_collection",
    "workflow_stage_03_result_modeling",
    "workflow_stage_04_test_generation",
    "workflow_stage_05_step_decomposition",
    "workflow_stage_06_execution",
    "workflow_stage_07_test_execution",
}


def load_base_validator() -> Any:
    path = Path(__file__).with_name(BASE_VALIDATOR_NAME)
    spec = importlib.util.spec_from_file_location("stage_deliberation_validator_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load base validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_base_validator()


def validate_static_fixture(data: dict[str, Any]) -> int:
    code = base.direct_error_code(data)
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
    if any(snapshot.get(key) != value for key, value in expected.items()):
        return 11
    if snapshot.get("activation_state") != EXPECTED_ACTIVE_STATE:
        return 15
    if snapshot.get("default_route") != "dormant":
        return 16
    return 0


def load_mapping(repo_root: Path, path: str) -> dict[str, Any]:
    doc = base.load_doc(repo_root / path)
    if not isinstance(doc, dict):
        raise ValueError(f"mapping required: {path}")
    return doc


def load_order_entry(boot: dict[str, Any], role: str) -> dict[str, Any] | None:
    for entry in boot.get("load_order", []):
        if isinstance(entry, dict) and entry.get("role") == role:
            return entry
    return None


def validate_static_repo(repo_root: Path) -> int:
    required_paths = list(base.REQUIRED_STATIC_PATHS) + [
        ACTIVATION_STATE_PATH,
        AUTHORIZATION_PATH,
        ACTIVE_VALIDATOR_PATH,
    ]
    if any(not (repo_root / path).exists() for path in required_paths):
        return 10
    try:
        profile_set = load_mapping(repo_root, base.REQUIRED_STATIC_PATHS[3])
        result_contract = load_mapping(repo_root, base.REQUIRED_STATIC_PATHS[4])
        invariant_contract = load_mapping(repo_root, base.REQUIRED_STATIC_PATHS[5])
        router_contract = load_mapping(repo_root, base.REQUIRED_STATIC_PATHS[6])
        load_contract = load_mapping(repo_root, base.REQUIRED_STATIC_PATHS[7])
        boot = load_mapping(repo_root, base.REQUIRED_STATIC_PATHS[9])
        registry = load_mapping(repo_root, base.REQUIRED_STATIC_PATHS[10])
        activation = load_mapping(repo_root, ACTIVATION_STATE_PATH)
        authorization_doc = load_mapping(repo_root, AUTHORIZATION_PATH)
    except Exception:
        return 11

    profiles = profile_set.get("profiles", [])
    profile_ids = {profile.get("profile_id") for profile in profiles if isinstance(profile, dict)}
    if len(profiles) != 7 or profile_ids != EXPECTED_PROFILE_IDS:
        return 16
    if any(profile.get("activation_default") != "dormant" for profile in profiles):
        return 16

    workflow_paths = sorted(repo_root.glob(base.WORKFLOW_PROFILE_REFERENCE_GLOB))
    if len(workflow_paths) != 7:
        return 16
    try:
        workflow_refs = [base.load_doc(path) for path in workflow_paths]
    except Exception:
        return 11
    if any(not isinstance(ref, dict) for ref in workflow_refs):
        return 11
    workflow_ids = [ref.get("profile_id") for ref in workflow_refs]
    if len(set(workflow_ids)) != 7 or set(workflow_ids) != EXPECTED_PROFILE_IDS:
        return 16
    for ref in workflow_refs:
        if ref.get("activation_state") != EXPECTED_ACTIVE_STATE:
            return 15
        state_ref = ref.get("activation_state_ref", {})
        if state_ref.get("path") != ACTIVATION_STATE_PATH or state_ref.get("blob_sha") != ACTIVATION_STATE_BLOB:
            return 13

    measurements = result_contract.get("measurements", {})
    if measurements.get("catalog_unique_object_types") != 45:
        return 11
    if measurements.get("main_mechanism_required_result_names") != 47:
        return 11
    if invariant_contract.get("measurements", {}).get("state_dimensions") != 10:
        return 11
    if invariant_contract.get("measurements", {}).get("active_invariants") != 16:
        return 11
    union = router_contract.get("complete_failure_code_union", [])
    codes = [item.get("code") if isinstance(item, dict) else item for item in union]
    if len(codes) != 26 or len(set(codes)) != 26:
        return 11
    required_receipt_fields = set(load_contract.get("stage_receipt", {}).get("required_fields", []))
    if not set(base.REQUIRED_RECEIPT_FIELDS).issubset(required_receipt_fields):
        return 17

    if activation.get("current_activation_state") != EXPECTED_ACTIVE_STATE:
        return 15
    if activation.get("default_route") != "dormant":
        return 16
    runtime = activation.get("runtime_effect", {})
    if runtime.get("globally_loadable") is not True or runtime.get("globally_discoverable") is not True:
        return 15
    if runtime.get("create_live_session_by_default") is not False:
        return 15
    if runtime.get("external_action_requires_separate_Human_authorization") is not True:
        return 15
    supersession = activation.get("supersession", {})
    if supersession.get("rule") != "this_append_only_record_is_authoritative_for_current_runtime_activation_state":
        return 11
    preserved = set(supersession.get("preserved_contract_semantics", []))
    expected_preserved = {
        "profile_count_7", "object_types_45", "result_names_47", "state_dimensions_10",
        "active_invariants_16", "failure_codes_26", "routers_5",
    }
    if preserved != expected_preserved:
        return 11

    authorization = authorization_doc.get("authorization", {})
    if authorization.get("decision") != "authorize_global_mechanism_activation":
        return 15
    if authorization.get("authorized_target_state") != EXPECTED_ACTIVE_STATE:
        return 15
    if authorization.get("master_publication_authorized_now") is not False:
        return 15

    if boot.get("activation_state") != EXPECTED_ACTIVE_STATE:
        return 15
    if registry.get("activation_state") != EXPECTED_ACTIVE_STATE:
        return 15
    if boot.get("default_route") != "dormant" or registry.get("default_route") != "dormant":
        return 16

    state_entry = load_order_entry(boot, "activation_state")
    auth_entry = load_order_entry(boot, "activation_authorization")
    base_validator_entry = load_order_entry(boot, "validator_base")
    active_validator_entry = load_order_entry(boot, "validator")
    if state_entry != {"role": "activation_state", "path": ACTIVATION_STATE_PATH, "blob_sha": ACTIVATION_STATE_BLOB}:
        return 13
    if auth_entry != {"role": "activation_authorization", "path": AUTHORIZATION_PATH, "blob_sha": AUTHORIZATION_BLOB}:
        return 13
    if not isinstance(base_validator_entry, dict) or base_validator_entry.get("path") != str(Path(ACTIVE_VALIDATOR_PATH).with_name(BASE_VALIDATOR_NAME)):
        return 13
    if not isinstance(active_validator_entry, dict) or active_validator_entry.get("path") != ACTIVE_VALIDATOR_PATH:
        return 13

    registry_state_ref = registry.get("activation", {}).get("state_ref", {})
    registry_auth_ref = registry.get("activation", {}).get("authorization_ref", {})
    if registry_state_ref.get("path") != ACTIVATION_STATE_PATH or registry_state_ref.get("blob_sha") != ACTIVATION_STATE_BLOB:
        return 13
    if registry_auth_ref.get("path") != AUTHORIZATION_PATH or registry_auth_ref.get("blob_sha") != AUTHORIZATION_BLOB:
        return 13
    if registry.get("runtime", {}).get("canonical_live_instance_state") != "prohibited":
        return 15
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("static", "instance", "material_event", "review_execution"))
    parser.add_argument("target")
    parser.add_argument("--case-id")
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args()
    try:
        target = Path(args.target)
        if args.mode == "static" and target.is_dir():
            code = validate_static_repo(target)
        else:
            data = base.select_case(base.load_doc(target), args.case_id)
            if not isinstance(data, dict):
                code = 11
            else:
                payload = data.get("data", data)
                if args.mode == "static":
                    code = validate_static_fixture(payload)
                elif args.mode == "instance":
                    code = base.validate_instance(payload)
                elif args.mode == "material_event":
                    code = base.validate_material_event(payload)
                else:
                    code = base.validate_review_execution(payload)
        if args.json_output:
            print(json.dumps({"mode": args.mode, "target": args.target, "case_id": args.case_id, "exit_code": code}))
        return code
    except Exception as exc:
        if args.json_output:
            print(json.dumps({"mode": args.mode, "target": args.target, "case_id": args.case_id, "exit_code": 19, "error": str(exc)}))
        return 19


if __name__ == "__main__":
    sys.exit(main())

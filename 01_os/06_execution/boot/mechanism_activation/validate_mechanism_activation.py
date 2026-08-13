#!/usr/bin/env python3
"""Validate Mechanism Activation canonical wiring; never authorize or mutate."""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Any

import yaml

try:
    from .activation import ActivationError
except ImportError:
    from activation import ActivationError


TRIGGER_FIELDS = {
    "mandatory_for_action_classes",
    "activation_predicates",
    "required_inputs",
    "enforcement_point",
    "missing_precondition_behavior",
    "receipt_requirement",
    "negative_conformance_refs",
}
INVENTORY_FIELDS = {
    "mechanism_id",
    "current_level",
    "target_level",
    "acceptance_state",
    "definition_ref",
    "boot_ref",
    "trigger_ref",
    "gate_ref",
    "receipt_ref",
    "positive_test_ref",
    "negative_test_ref",
    "known_bypass",
    "recommended_successor_action",
}
LEVELS = {
    "L0_DEFINED",
    "L1_BOOT_VISIBLE",
    "L2_TRIGGER_BOUND",
    "L3_EXECUTION_GATED",
    "L4_E2E_ADVERSARIALLY_VERIFIED",
}


def _load(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ActivationError("CANONICAL_YAML_LOAD_FAILED", path=str(path)) from exc


def _physical_ref(root: Path, value: str | None) -> bool:
    if not value:
        return False
    relative = value.split("#", 1)[0].rstrip("/")
    return (root / relative).exists()


def validate_static_repository(repo_root: Path) -> None:
    root = repo_root.resolve()
    mechanism = root / "01_os/03_mechanisms/mechanism_activation"
    boot_path = root / "01_os/02_boot/mechanism_activation/启动清单_v1.yml"
    registry_path = root / "01_os/05_registry/mechanism_activation_v1.yml"
    execution = root / "01_os/06_execution/boot/mechanism_activation"
    for required in (mechanism, boot_path, registry_path, execution):
        if not required.exists():
            raise ActivationError("ACTIVATION_SURFACE_MISSING", path=str(required))

    boot = _load(boot_path)
    if not isinstance(boot, dict) or boot.get("mechanism_version") != 1:
        raise ActivationError("BOOT_VERSION_INVALID")
    if boot.get("background_processes_started") is not False:
        raise ActivationError("BOOT_BACKGROUND_BOUNDARY_INVALID")
    if boot.get("automatic_delivery_polling_acknowledgement_scheduling_or_progression") is not False:
        raise ActivationError("BOOT_AUTONOMY_BOUNDARY_INVALID")
    for relative in boot.get("load_order") or []:
        if not (root / str(relative)).is_file():
            raise ActivationError("BOOT_REF_MISSING", path=relative)

    constitution = _load(mechanism / "正式动作宪法_v1.yml")
    if constitution.get("authority_effect") != "none" or constitution.get("resolver_or_gate_optional") is not False:
        raise ActivationError("FORMAL_CONSTITUTION_BOUNDARY_INVALID")
    if constitution.get("bypass_result") != "INVALID_FORMAL_ACTION":
        raise ActivationError("FORMAL_BYPASS_RESULT_INVALID")

    triggers = _load(mechanism / "机制触发注册表_v1.yml")
    if triggers.get("authority_effect") != "none":
        raise ActivationError("TRIGGER_REGISTRY_AUTHORITY_INVALID")
    mechanisms = triggers.get("mechanisms")
    if not isinstance(mechanisms, dict) or "communication_system" not in mechanisms:
        raise ActivationError("COMMUNICATION_TRIGGER_MISSING")
    for mechanism_id, entry in mechanisms.items():
        if not isinstance(entry, dict) or set(entry) != TRIGGER_FIELDS:
            raise ActivationError("TRIGGER_ENTRY_FIELD_SET_INVALID", mechanism_id=mechanism_id)
        for negative_ref in entry["negative_conformance_refs"]:
            if not _physical_ref(root, negative_ref):
                raise ActivationError("TRIGGER_NEGATIVE_REF_MISSING", path=negative_ref)

    claims = _load(mechanism / "物理事实双向绑定契约_v1.yml")
    if claims.get("receipt_is_physical_truth_source") is not False:
        raise ActivationError("RECEIPT_TRUTH_BOUNDARY_INVALID")
    if claims.get("aggregate_acceptance") != "every_required_material_claim_must_be_VERIFIED":
        raise ActivationError("MATERIAL_AGGREGATE_RULE_INVALID")
    trusted_boundary = claims.get("acceptance_time_trusted_observation_boundary")
    if not isinstance(trusted_boundary, dict) or not all(
        trusted_boundary.get(field) is True
        for field in (
            "context_required",
            "expected_claim_source_ref_must_be_resolved_and_consumed",
            "exact_observation_ref_must_be_resolved_and_consumed",
            "expected_facts_must_come_from_trusted_resolver_context",
            "observed_facts_must_come_from_trusted_adapter_context",
            "source_class_and_exact_ref_must_match_consumed_observation",
            "conditional_principal_and_freshness_refs_must_be_consumed",
        )
    ):
        raise ActivationError("MATERIAL_TRUSTED_OBSERVATION_BOUNDARY_INVALID")
    if not claims.get("receipt_fields_that_cannot_establish_provenance"):
        raise ActivationError("MATERIAL_RECEIPT_PROVENANCE_DENYLIST_MISSING")
    if (
        claims.get("claim_id_uniqueness_within_receipt") != "mandatory"
        or claims.get("comparator_must_be_registered_for_claim_role") is not True
    ):
        raise ActivationError("MATERIAL_CLAIM_IDENTITY_OR_ROLE_RULE_INVALID")

    inventory = _load(mechanism / "机制生效等级与盘点_v1.yml")
    entries = inventory.get("inventory")
    if not isinstance(entries, list) or not entries:
        raise ActivationError("EFFECTIVENESS_INVENTORY_MISSING")
    ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != INVENTORY_FIELDS:
            raise ActivationError("INVENTORY_FIELD_SET_INVALID")
        mechanism_id = str(entry["mechanism_id"])
        if mechanism_id in ids:
            raise ActivationError("INVENTORY_DUPLICATE_MECHANISM", mechanism_id=mechanism_id)
        ids.add(mechanism_id)
        level = str(entry["current_level"])
        if level not in LEVELS or str(entry["target_level"]) not in LEVELS:
            raise ActivationError("INVENTORY_LEVEL_INVALID", mechanism_id=mechanism_id)
        for ref_field in ("definition_ref", "boot_ref", "trigger_ref", "gate_ref", "receipt_ref",
                          "positive_test_ref", "negative_test_ref"):
            value = entry.get(ref_field)
            if value is not None and not _physical_ref(root, str(value)):
                raise ActivationError("INVENTORY_REF_MISSING", mechanism_id=mechanism_id, field=ref_field)
        if level == "L4_E2E_ADVERSARIALLY_VERIFIED" and entry.get("known_bypass"):
            raise ActivationError("L4_WITH_KNOWN_BYPASS_INVALID", mechanism_id=mechanism_id)
        if (
            level == "L4_E2E_ADVERSARIALLY_VERIFIED"
            and entry.get("acceptance_state") != "independently_accepted"
        ):
            raise ActivationError("L4_WITHOUT_INDEPENDENT_ACCEPTANCE_INVALID", mechanism_id=mechanism_id)

    registry = _load(registry_path)
    registered_paths = {entry.get("path") for entry in registry.get("entries") or []}
    expected_paths = {
        "01_os/03_mechanisms/mechanism_activation/**",
        "01_os/02_boot/mechanism_activation/**",
        "01_os/06_execution/boot/mechanism_activation/**",
        "01_os/05_registry/mechanism_activation_v1.yml",
    }
    if registered_paths != expected_paths:
        raise ActivationError("ACTIVATION_REGISTRY_COVERAGE_INVALID")

    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    if "Formal Action Constitution" not in agents or "mechanism_activation" not in agents:
        raise ActivationError("ALWAYS_ON_FORMAL_ACTION_BOOTSTRAP_MISSING")

    prohibited_imports = {"schedule", "watchdog", "apscheduler", "daemon"}
    for source in execution.rglob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = {alias.name.split(".")[0] for alias in node.names}
                if names & prohibited_imports:
                    raise ActivationError("BACKGROUND_MODULE_IMPORTED", path=str(source))
            if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
                raise ActivationError("UNBOUNDED_LOOP_PROHIBITED", path=str(source))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    static = sub.add_parser("static")
    static.add_argument("repo_root", type=Path)
    args = parser.parse_args()
    try:
        validate_static_repository(args.repo_root)
    except ActivationError as exc:
        print(f"validation_rejected:{exc.code}:{exc.evidence}", file=sys.stderr)
        return 2
    print("validation_passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

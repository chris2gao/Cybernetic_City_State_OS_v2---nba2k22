#!/usr/bin/env python3
"""Validate the model-routing mechanism without authorizing or publishing."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


class ValidationError(ValueError):
    pass


class StrictLoader(yaml.SafeLoader):
    pass


def _unique_mapping(loader: StrictLoader, node: yaml.MappingNode, deep: bool = False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValidationError(f"duplicate_key:{key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping
)


def load_yaml(path: Path) -> Any:
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError(f"yaml_invalid:{path}:{type(exc).__name__}") from exc


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"mapping_required:{label}")
    return value


def nonempty(value: Any) -> bool:
    return value is not None and not (
        isinstance(value, (str, list, dict)) and len(value) == 0
    )


def locate_by_schema(directory: Path, prefix: str) -> tuple[Path, dict[str, Any]]:
    matches = []
    for path in sorted(directory.glob("*.yml")):
        doc = require_mapping(load_yaml(path), str(path))
        if str(doc.get("schema_version", "")).startswith(prefix):
            matches.append((path, doc))
    if len(matches) != 1:
        raise ValidationError(f"schema_identity_count:{prefix}:{len(matches)}")
    return matches[0]


def validate_contract(doc: dict[str, Any]) -> None:
    if doc.get("mechanism_version") != 1:
        raise ValidationError("contract_version_invalid")
    inputs = require_mapping(doc.get("inputs"), "contract.inputs")
    outputs = require_mapping(doc.get("outputs"), "contract.outputs")
    required_inputs = {
        "task_id", "role", "risk_tier", "task_shape", "required_capabilities"
    }
    required_outputs = {
        "provider", "surface", "model", "parameter_profile", "routing_basis",
        "evidence_refs", "limitations", "availability_assumption", "authority",
    }
    if not required_inputs.issubset(set(inputs.get("required") or [])):
        raise ValidationError("required_inputs_missing")
    if not required_outputs.issubset(set(outputs.get("required") or [])):
        raise ValidationError("required_outputs_missing")
    if outputs.get("authority_constant") != "routing_only":
        raise ValidationError("routing_authority_invalid")
    rule = require_mapping(doc.get("availability_rule"), "availability_rule")
    expected = {
        "registered_default": "available",
        "unavailable_only_by": "explicit_Human_override",
        "restored_by": "explicit_Human_override",
        "automatic_quota_probe": False,
    }
    if any(rule.get(key) != value for key, value in expected.items()):
        raise ValidationError("availability_rule_invalid")
    prohibited_economic_inputs = {"token_cost", "price", "quota_balance"}
    if not prohibited_economic_inputs.issubset(
        set(doc.get("prohibited_routing_inputs") or [])
    ):
        raise ValidationError("prohibited_routing_inputs_incomplete")
    if doc.get("on_primary_unavailable") != "rerun_task_fit_among_remaining_candidates":
        raise ValidationError("unavailability_route_invalid")


def validate_catalog(doc: dict[str, Any]) -> None:
    if doc.get("mechanism_version") != 1 or doc.get("catalog_version") != 1:
        raise ValidationError("catalog_version_invalid")
    if doc.get("entitlement_is_account_availability") is not False:
        raise ValidationError("entitlement_boundary_invalid")
    entries = doc.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValidationError("catalog_entries_missing")
    identities = set()
    freshness = ("source_refs", "verified_at", "invalidation_conditions", "confidence")
    for entry in entries:
        item = require_mapping(entry, "catalog.entry")
        identity = (item.get("surface_id"), item.get("model_label"))
        if not all(nonempty(value) for value in (item.get("provider"), *identity)):
            raise ValidationError("catalog_identity_missing")
        if identity in identities:
            raise ValidationError(f"catalog_identity_duplicate:{identity}")
        identities.add(identity)
        if not isinstance(item.get("registered"), bool):
            raise ValidationError(f"registered_flag_invalid:{identity}")
        if item["registered"] is False:
            if not nonempty(item.get("status")):
                raise ValidationError(f"unregistered_status_missing:{identity}")
            continue
        for field in freshness:
            if not nonempty(item.get(field)):
                raise ValidationError(f"freshness_missing:{identity}:{field}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(item["verified_at"])):
            raise ValidationError(f"verified_at_invalid:{identity}")
        capabilities = item.get("capabilities")
        if not isinstance(capabilities, dict) or not capabilities:
            raise ValidationError(f"capabilities_missing:{identity}")
        if any(value is None or value == "" for value in capabilities.values()):
            raise ValidationError(f"capability_unknown_not_explicit:{identity}")
        profiles = item.get("parameter_profiles")
        if not isinstance(profiles, list) or not profiles:
            raise ValidationError(f"parameter_profiles_missing:{identity}")
        for profile in profiles:
            parameter = require_mapping(profile, "parameter_profile")
            if not nonempty(parameter.get("profile_id")):
                raise ValidationError(f"profile_id_missing:{identity}")
            if not nonempty(parameter.get("surface_exposure_evidence")):
                raise ValidationError(f"surface_evidence_missing:{identity}")


def validate_ledger(doc: dict[str, Any]) -> None:
    if doc.get("mechanism_version") != 1 or doc.get("ledger_version") != 1:
        raise ValidationError("ledger_version_invalid")
    observations = doc.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValidationError("observations_missing")
    hard_fields = ("qualified", "disqualified", "max_task_tier", "task_ceiling", "hard_gate")
    for observation in observations:
        item = require_mapping(observation, "observation")
        validity = item.get("validity")
        if validity not in {"formal", "diagnostic", "anecdotal"}:
            raise ValidationError("observation_validity_invalid")
        if not nonempty(item.get("confidence")) or not nonempty(item.get("source_ref")):
            raise ValidationError("observation_evidence_missing")
        if validity != "formal" and any(nonempty(item.get(key)) for key in hard_fields):
            raise ValidationError("nonformal_observation_hard_gate")
        if item.get("surface_id") == "antigravity" and validity == "formal":
            raise ValidationError("antigravity_formal_claim_prohibited")


def validate_static(root: Path) -> None:
    root = root.resolve()
    mechanism = root / "01_os/03_mechanisms/model_routing"
    boot_path = root / "01_os/02_boot/model_routing/启动清单_v1.yml"
    registry_path = root / "01_os/05_registry/model_routing_v1.yml"
    boot = require_mapping(load_yaml(boot_path), "boot")
    registry = require_mapping(load_yaml(registry_path), "registry")
    contract_path, contract = locate_by_schema(
        mechanism, "citystate.model_routing.contract.v"
    )
    _, catalog = locate_by_schema(mechanism, "citystate.model_routing.catalog.v")
    _, ledger = locate_by_schema(
        mechanism, "citystate.model_routing.project_observation.v"
    )
    versions = {
        contract.get("mechanism_version"),
        boot.get("mechanism_version"),
        registry.get("mechanism_version"),
    }
    if versions != {1}:
        raise ValidationError(f"mechanism_version_mismatch:{sorted(versions, key=str)}")
    if boot.get("background_processes_started") is not False:
        raise ValidationError("background_process_boundary_invalid")
    if boot.get("automatic_quota_probe") is not False:
        raise ValidationError("automatic_probe_boundary_invalid")
    for item in boot.get("load_order") or []:
        relative = item.get("path") if isinstance(item, dict) else item
        if not relative or not (root / relative).exists():
            raise ValidationError(f"boot_pointer_broken:{relative}")
    if boot.get("registry") != "01_os/05_registry/model_routing_v1.yml":
        raise ValidationError("boot_registry_pointer_invalid")
    declared_validator = root / str(boot.get("validator", ""))
    if not declared_validator.is_file():
        raise ValidationError("boot_validator_pointer_invalid")
    if contract_path != mechanism / "路由契约_v1.yml":
        raise ValidationError("contract_pointer_unexpected")
    validate_contract(contract)
    validate_catalog(catalog)
    validate_ledger(ledger)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    static = sub.add_parser("static")
    static.add_argument("repo_root", type=Path)
    args = parser.parse_args()
    try:
        validate_static(args.repo_root)
    except ValidationError as exc:
        print(f"validation_rejected:{exc}", file=sys.stderr)
        return 2
    print("validation_passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

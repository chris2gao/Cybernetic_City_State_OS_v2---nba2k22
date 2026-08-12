#!/usr/bin/env python3
"""Validate the model-routing mechanism without authorizing or publishing."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


MECHANISM_REL = "01_os/03_mechanisms/model_routing"
BOOT_REL = "01_os/02_boot/model_routing/启动清单_v1.yml"
REGISTRY_REL = "01_os/05_registry/model_routing_v1.yml"
LOADER_REL = "01_os/06_execution/boot/model_routing"
VALIDATOR_REL = f"{MECHANISM_REL}/实现/verify_model_routing.py"
SOURCE_INDEX_REL = f"{MECHANISM_REL}/来源索引_v1.yml"

SOURCE_LOCATORS = ("url", "ref", "path")
EXTERNAL_SOURCE_KINDS = {
    "provider_first_party",
    "independent_web_research",
    "independent_provider_first_party_research",
    "vendor_documentation",
    "product_surface_documentation",
}
ECONOMIC_ROUTING_RE = re.compile(
    r"(price|pricing|cost|quota|budget|balance|billing|cheapest|"
    r"minimize_token|minimize_cost|token_spend)",
    re.IGNORECASE,
)


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


def walk_files(directory: Path):
    if not directory.is_dir():
        return
    for path in sorted(directory.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            yield path


def expand_path_set(pattern: str) -> list[str]:
    match = re.search(r"\{([^}]*)\}", pattern)
    if not match:
        return [pattern] if pattern else []
    expanded: list[str] = []
    for part in match.group(1).split(","):
        expanded.extend(
            expand_path_set(pattern[:match.start()] + part.strip() + pattern[match.end():])
        )
    return expanded


def checked_path(root: Path, relative: str, label: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ValidationError(f"path_missing:{label}")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValidationError(f"path_outside_repository:{label}:{relative}") from exc
    return candidate


def path_pattern_exists(root: Path, pattern: str) -> bool:
    if pattern.endswith("**"):
        base = checked_path(root, pattern[:-2].rstrip("/"), "registry_pattern")
        return base.is_dir() and any(walk_files(base))
    return checked_path(root, pattern, "registry_pattern").exists()


def path_matches(pattern: str, relative: str) -> bool:
    if pattern.endswith("/**"):
        return relative.startswith(pattern[:-2])
    if pattern.endswith("**"):
        return relative.startswith(pattern[:-2])
    return relative == pattern


def validate_registry(root: Path, registry: dict[str, Any]) -> None:
    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValidationError("registry_entries_missing")
    required = {
        "path", "purpose", "loader", "loader_class", "discovery", "evidence",
        "cache_dirs", "failure_surfacing", "deletion_rule",
    }
    patterns: list[str] = []
    for entry in entries:
        item = require_mapping(entry, "registry.entry")
        missing = sorted(required - set(item))
        if missing:
            raise ValidationError(f"registry_fields_missing:{','.join(missing)}")
        for field in required - {"cache_dirs"}:
            if not nonempty(item.get(field)):
                raise ValidationError(f"registry_field_empty:{field}")
        if not isinstance(item.get("cache_dirs"), list):
            raise ValidationError("registry_cache_dirs_invalid")
        expanded = expand_path_set(str(item["path"]))
        if not expanded:
            raise ValidationError("registry_path_empty")
        for pattern in expanded:
            if not path_pattern_exists(root, pattern):
                raise ValidationError(f"registry_path_missing:{pattern}")
            patterns.append(pattern)

    coverage_roots = (
        checked_path(root, MECHANISM_REL, "mechanism_root"),
        checked_path(root, str(Path(BOOT_REL).parent).replace("\\", "/"), "boot_root"),
        checked_path(root, LOADER_REL, "loader_root"),
    )
    for coverage_root in coverage_roots:
        if not coverage_root.is_dir():
            raise ValidationError(f"registry_coverage_root_missing:{coverage_root}")
        for path in walk_files(coverage_root):
            relative = path.relative_to(root).as_posix()
            if not any(path_matches(pattern, relative) for pattern in patterns):
                raise ValidationError(f"registry_coverage_missing:{relative}")
    if not any(path_matches(pattern, REGISTRY_REL) for pattern in patterns):
        raise ValidationError(f"registry_coverage_missing:{REGISTRY_REL}")


def validate_source_index(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources = doc.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValidationError("source_index_empty")
    for source_id, value in sources.items():
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValidationError("source_id_invalid")
        record = require_mapping(value, f"source:{source_id}")
        if not nonempty(record.get("kind")):
            raise ValidationError(f"source_kind_missing:{source_id}")
        if not any(nonempty(record.get(locator)) for locator in SOURCE_LOCATORS):
            raise ValidationError(f"source_locator_missing:{source_id}")
    return sources


def source_tokens(entry: dict[str, Any]) -> set[str]:
    tokens = {str(value) for value in (entry.get("source_refs") or [])}
    for profile in entry.get("parameter_profiles") or []:
        if not isinstance(profile, dict):
            continue
        evidence = profile.get("surface_exposure_evidence")
        values = evidence if isinstance(evidence, list) else ([evidence] if evidence else [])
        tokens.update(str(value) for value in values)
    return tokens


def economic_routing_positions(node: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            key_text = str(key)
            if key_text == "prohibited_routing_inputs" or value is False:
                continue
            if ECONOMIC_ROUTING_RE.search(key_text):
                findings.append(f"{path}{key_text}")
            findings.extend(economic_routing_positions(value, f"{path}{key_text}."))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            findings.extend(economic_routing_positions(value, f"{path}[{index}]."))
    elif isinstance(node, str) and ECONOMIC_ROUTING_RE.search(node):
        findings.append(f"{path}{node}")
    return findings


def validate_contract(doc: dict[str, Any]) -> None:
    if not isinstance(doc.get("mechanism_version"), int) or doc["mechanism_version"] < 1:
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
    economic_fields = economic_routing_positions(doc)
    if economic_fields:
        raise ValidationError(f"economic_routing_semantics:{economic_fields[0]}")


def validate_catalog(doc: dict[str, Any], sources: dict[str, dict[str, Any]]) -> None:
    if not isinstance(doc.get("mechanism_version"), int) or doc["mechanism_version"] < 1:
        raise ValidationError("catalog_version_invalid")
    if not isinstance(doc.get("catalog_version"), int) or doc["catalog_version"] < 1:
        raise ValidationError("catalog_version_invalid")
    if doc.get("source_index_ref") != SOURCE_INDEX_REL:
        raise ValidationError("catalog_source_index_pointer_invalid")
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
        for field in freshness:
            if not nonempty(item.get(field)):
                raise ValidationError(f"freshness_missing:{identity}:{field}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(item["verified_at"])):
            raise ValidationError(f"verified_at_invalid:{identity}")
        refs = item.get("source_refs")
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) for ref in refs):
            raise ValidationError(f"source_refs_invalid:{identity}")
        tokens = source_tokens(item)
        unresolved = sorted(token for token in tokens if token not in sources)
        if unresolved:
            raise ValidationError(f"source_ref_unresolvable:{identity}:{unresolved[0]}")
        if item["registered"] is False:
            if not nonempty(item.get("status")):
                raise ValidationError(f"unregistered_status_missing:{identity}")
            capabilities = item.get("capabilities")
            if capabilities != "unknown" and not isinstance(capabilities, dict):
                raise ValidationError(f"unregistered_capabilities_invalid:{identity}")
            if not isinstance(item.get("parameter_profiles"), list):
                raise ValidationError(f"unregistered_profiles_invalid:{identity}")
            continue
        kinds = {str(sources[ref].get("kind", "")) for ref in refs}
        if not (kinds & EXTERNAL_SOURCE_KINDS):
            raise ValidationError(f"registered_external_source_missing:{identity}")
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
    if not isinstance(doc.get("mechanism_version"), int) or doc["mechanism_version"] < 1:
        raise ValidationError("ledger_version_invalid")
    if not isinstance(doc.get("ledger_version"), int) or doc["ledger_version"] < 1:
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
    mechanism = checked_path(root, MECHANISM_REL, "mechanism")
    boot_path = checked_path(root, BOOT_REL, "boot")
    if not mechanism.is_dir() or not boot_path.is_file():
        raise ValidationError("required_mechanism_surface_missing")
    for path in walk_files(mechanism):
        if path.suffix.lower() in {".yml", ".yaml"}:
            require_mapping(load_yaml(path), str(path))
    boot = require_mapping(load_yaml(boot_path), "boot")
    if boot.get("registry") != REGISTRY_REL:
        raise ValidationError("boot_registry_pointer_invalid")
    registry_path = checked_path(root, str(boot.get("registry")), "boot.registry")
    if not registry_path.is_file():
        raise ValidationError("boot_registry_pointer_broken")
    registry = require_mapping(load_yaml(registry_path), "registry")
    contract_path, contract = locate_by_schema(
        mechanism, "citystate.model_routing.contract.v"
    )
    catalog_path, catalog = locate_by_schema(mechanism, "citystate.model_routing.catalog.v")
    ledger_path, ledger = locate_by_schema(
        mechanism, "citystate.model_routing.project_observation.v"
    )
    source_index_path, source_index = locate_by_schema(
        mechanism, "citystate.model_routing.source_index.v"
    )
    versions = {
        "contract": contract.get("mechanism_version"),
        "catalog": catalog.get("mechanism_version"),
        "ledger": ledger.get("mechanism_version"),
        "source_index": source_index.get("mechanism_version"),
        "boot": boot.get("mechanism_version"),
        "registry": registry.get("mechanism_version"),
    }
    if len(set(versions.values())) != 1 or not isinstance(versions["contract"], int):
        raise ValidationError(f"mechanism_version_mismatch:{versions}")
    if versions["contract"] < 1:
        raise ValidationError("mechanism_version_invalid")
    catalog_versions = {
        "catalog": catalog.get("catalog_version"),
        "boot": boot.get("catalog_version"),
    }
    if len(set(catalog_versions.values())) != 1 or not isinstance(catalog_versions["catalog"], int):
        raise ValidationError(f"catalog_version_mismatch:{catalog_versions}")
    source_versions = {
        "source_index": source_index.get("source_index_version"),
        "boot": boot.get("source_index_version"),
    }
    if len(set(source_versions.values())) != 1 or not isinstance(source_versions["source_index"], int):
        raise ValidationError(f"source_index_version_mismatch:{source_versions}")
    if boot.get("background_processes_started") is not False:
        raise ValidationError("background_process_boundary_invalid")
    if boot.get("automatic_quota_probe") is not False:
        raise ValidationError("automatic_probe_boundary_invalid")
    load_paths: list[str] = []
    for item in boot.get("load_order") or []:
        relative = item.get("path") if isinstance(item, dict) else item
        target = checked_path(root, str(relative or ""), "boot.load_order")
        if not target.is_file():
            raise ValidationError(f"boot_pointer_broken:{relative}")
        load_paths.append(str(relative))
    required_load_paths = {
        contract_path.relative_to(root).as_posix(),
        catalog_path.relative_to(root).as_posix(),
        ledger_path.relative_to(root).as_posix(),
        source_index_path.relative_to(root).as_posix(),
    }
    if not required_load_paths.issubset(set(load_paths)):
        missing = sorted(required_load_paths - set(load_paths))
        raise ValidationError(f"boot_load_surface_incomplete:{missing[0]}")
    declared_validator = checked_path(root, str(boot.get("validator", "")), "boot.validator")
    if not declared_validator.is_file():
        raise ValidationError("boot_validator_pointer_invalid")
    if declared_validator.relative_to(root).as_posix() != VALIDATOR_REL:
        raise ValidationError("boot_validator_pointer_invalid")
    if contract_path != mechanism / "路由契约_v1.yml":
        raise ValidationError("contract_pointer_unexpected")
    if catalog.get("source_index_ref") != source_index_path.relative_to(root).as_posix():
        raise ValidationError("catalog_source_index_pointer_invalid")
    validate_registry(root, registry)
    sources = validate_source_index(source_index)
    validate_contract(contract)
    validate_catalog(catalog, sources)
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

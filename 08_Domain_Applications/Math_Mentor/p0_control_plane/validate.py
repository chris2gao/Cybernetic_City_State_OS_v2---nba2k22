"""Validate the deterministic Math Mentor P0 control-plane materialization.

This module is intentionally read-only.  It rebuilds the three generated
registries from the frozen source commit, validates their schemas and hashes,
and checks the fail-closed quantitative invariants reviewed for this task.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence
import uuid

from jsonschema import Draft202012Validator, FormatChecker
import yaml

try:
    from identity import canonical_json_bytes, canonical_node_uuid, sha256_bytes
    from registry_builder import OUTPUT_NAMES, build_all, load_config
    from staging_diagnostics import scan_staging
except ImportError:  # pragma: no cover - package import path
    from .identity import canonical_json_bytes, canonical_node_uuid, sha256_bytes
    from .registry_builder import OUTPUT_NAMES, build_all, load_config
    from .staging_diagnostics import scan_staging


EXPECTED_SOURCE_HEAD = "764d03d7d0a9ad553f4f3868699b06d9de5553ea"
MATH_MENTOR_REL = Path("08_Domain_Applications/Math_Mentor")
FULLWIDTH_DIAGNOSTIC_PATHS = {
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-684.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-687.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-688.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-692.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-662.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-663.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-668.yaml",
}


class ValidationError(RuntimeError):
    """A checked control-plane invariant did not hold."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"expected JSON object: {path}")
    return value


def _validate_json_schema(instance: Any, schema: Mapping[str, Any], label: str) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # jsonschema exposes several schema subclasses
        raise ValidationError(f"invalid JSON Schema {label}: {exc}") from exc
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        details = "; ".join(
            f"/{'/'.join(str(item) for item in error.path)}: {error.message}"
            for error in errors[:10]
        )
        raise ValidationError(f"schema validation failed for {label}: {details}")


def _validate_schema_definition(schema: Mapping[str, Any], label: str) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        raise ValidationError(f"invalid JSON Schema {label}: {exc}") from exc


def _validate_payload_hash(document: Mapping[str, Any], label: str) -> None:
    stored = document.get("payload_sha256")
    payload = dict(document)
    payload.pop("payload_sha256", None)
    calculated = sha256_bytes(canonical_json_bytes(payload))
    _require(stored == calculated, f"payload hash mismatch for {label}")


def _validate_uuidv5(value: str, label: str) -> None:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValidationError(f"invalid UUID for {label}: {value!r}") from exc
    _require(parsed.version == 5, f"non-v5 UUID for {label}: {value}")
    _require(str(parsed) == value, f"non-canonical UUID spelling for {label}: {value}")


def _assert_summary_subset(
    actual: Mapping[str, Any], expected: Mapping[str, Any], label: str
) -> None:
    for key, expected_value in expected.items():
        _require(key in actual, f"missing summary key {label}.{key}")
        _require(
            actual[key] == expected_value,
            f"summary mismatch {label}.{key}: expected={expected_value!r}, "
            f"actual={actual[key]!r}",
        )


def _validate_quantitative_findings(outputs: Mapping[str, Mapping[str, Any]]) -> None:
    root = outputs["ROOT_CORPUS_REGISTRY.json"]
    crosswalk = outputs["CANONICAL_NODE_CROSSWALK.json"]
    conflicts = outputs["ALIAS_CONFLICT_REGISTRY.json"]

    _assert_summary_subset(
        root["summary"],
        {
            "tracked_scope_path_count": 1014,
            "db_tracked_count": 912,
            "root_direct_count": 683,
            "nested_excluded_count": 229,
            "root_candidate_count": 667,
            "root_candidate_parse_pass_count": 667,
            "root_bridge_count": 14,
            "root_schema_count": 1,
            "root_script_count": 1,
            "excluded_asset_count": 245,
            "strict_identity_counts": {"missing": 1, "resolved": 666},
            "unique_strict_identity_count": 666,
            "duplicate_strict_identity_count": 0,
            "schema_era_counts": {
                "E1_wrapper_or_alternate_identity": 143,
                "E2_flat_migration_legacy": 496,
                "E3_stage0_canonical_body": 8,
                "E4_post_stage0_repaired": 20,
            },
            "unicode_fullwidth_roadmap_tag_unparsed_file_count": 7,
        },
        "root",
    )
    _assert_summary_subset(
        crosswalk["summary"],
        {
            "canonical_node_count": 667,
            "roadmap_entry_count": 770,
            "explicit_self_claim_file_count": 473,
            "distinct_explicit_roadmap_claim_count": 473,
            "roadmap_without_explicit_claim_count": 297,
            "alias_comparison_counts": {
                "agree": 416,
                "disagree": 53,
                "explicit_only": 4,
                "neither": 28,
                "stage0_only": 166,
            },
            "binding_status_counts": {
                "conflict_open": 53,
                "declared_consistent_unapproved": 420,
                "quarantined": 2,
                "unclaimed": 192,
            },
            "candidate_edge_count": 420,
            "human_approved_binding_count": 0,
            "consumer_allowed_count": 0,
            "unicode_fullwidth_roadmap_tag_unparsed_file_count": 7,
        },
        "crosswalk",
    )
    _assert_summary_subset(
        conflicts["summary"],
        {
            "conflict_record_count": 286,
            "counts_by_type": {
                "explicit_vs_stage0_alias_disagreement": 53,
                "filename_domain_id_difference_diagnostic": 3,
                "forbidden_filename_suffix_collision_evidence": 33,
                "missing_explicit_roadmap_alias": 194,
                "source_quarantine_disposition": 2,
                "strict_domain_id_missing": 1,
            },
            "forbidden_filename_suffix_collision_member_count": 153,
            "resolved_by_suffix_count": 0,
            "resolved_by_basename_count": 0,
            "resolved_by_fuzzy_match_count": 0,
            "resolved_from_staging_count": 0,
            "unicode_fullwidth_roadmap_tag_unparsed_file_count": 7,
        },
        "conflicts",
    )


def _validate_identity_and_exclusions(
    outputs: Mapping[str, Mapping[str, Any]], config: Mapping[str, Any]
) -> None:
    root = outputs["ROOT_CORPUS_REGISTRY.json"]
    crosswalk = outputs["CANONICAL_NODE_CROSSWALK.json"]
    conflicts = outputs["ALIAS_CONFLICT_REGISTRY.json"]
    namespace = uuid.UUID(str(config["namespace_uuid"]))

    root_ids: set[str] = set()
    fullwidth_paths: set[str] = set()
    for record in root["nodes"]:
        path = record["path"]
        canonical_uuid = record["canonical_uuid"]
        _validate_uuidv5(canonical_uuid, path)
        _require(canonical_uuid not in root_ids, f"duplicate canonical UUID: {canonical_uuid}")
        root_ids.add(canonical_uuid)
        _require(
            canonical_uuid == canonical_node_uuid(namespace, path),
            f"bootstrap UUID mismatch for {path}",
        )
        _require("/_Staging_" not in path, f"staging path admitted as root node: {path}")
        _require(record["runtime_allowed"] is False, f"runtime allowed for {path}")
        if record.get("unparsed_fullwidth_roadmap_tags"):
            fullwidth_paths.add(path)

    _require(fullwidth_paths == FULLWIDTH_DIAGNOSTIC_PATHS, "fullwidth diagnostic path set drift")

    staging_exclusions = [
        record for record in root["excluded_assets"] if "/_Staging_" in record["path"]
    ]
    _require(len(staging_exclusions) == 229, "staging exclusion count must be 229")
    _require(
        sum(Path(record["path"]).suffix.lower() in {".yaml", ".yml"} for record in staging_exclusions)
        == 228,
        "staging YAML exclusion count must be 228",
    )
    _require(
        all(
            record["parsed_as_node"] is False
            and record["identity_resolution_allowed"] is False
            for record in staging_exclusions
        ),
        "a staging exclusion became identity-resolvable",
    )

    crosswalk_ids: set[str] = set()
    for record in crosswalk["nodes"]:
        canonical_uuid = record["canonical_uuid"]
        _validate_uuidv5(canonical_uuid, "crosswalk node")
        _require(canonical_uuid not in crosswalk_ids, f"duplicate crosswalk UUID: {canonical_uuid}")
        crosswalk_ids.add(canonical_uuid)
        _require(record["consumer_allowed"] is False, "crosswalk consumer was enabled")
        _require(record["binding_status"] != "human_approved", "untrusted identity approval present")
        root_path_aliases = [
            alias for alias in record["aliases"] if alias["alias_type"] == "root_path"
        ]
        _require(len(root_path_aliases) == 1, "crosswalk node must have one root_path alias")
        _require(
            "/_Staging_" not in root_path_aliases[0]["value"],
            "staging path entered canonical crosswalk",
        )
    _require(root_ids == crosswalk_ids, "root registry and crosswalk UUID sets differ")

    roadmap_ids = [record["roadmap_id_alias"] for record in crosswalk["roadmap_entries"]]
    _require(roadmap_ids == [f"n_{number}" for number in range(1, 771)], "roadmap ID sequence drift")

    _require(
        crosswalk["identity_model"]["sole_node_primary"] == "canonical_uuid",
        "canonical UUID is no longer the sole node primary",
    )
    _require(
        crosswalk["identity_model"]["human_resolution_trust_adapter_implemented"] is False,
        "P0 unexpectedly claims a Human resolution trust adapter",
    )
    _require(
        all(record["resolution_ref"] is None for record in conflicts["conflicts"]),
        "an unauthenticated conflict resolution was applied",
    )
    _require(
        all(
            record["status"] in {"open", "diagnostic", "quarantined"}
            for record in conflicts["conflicts"]
        ),
        "unexpected conflict status",
    )

    serialized_inputs = json.dumps(
        [root.get("inputs", []), crosswalk.get("inputs", [])], ensure_ascii=False
    )
    _require("数学知识路线图_全部.yaml" not in serialized_inputs, "combined roadmap entered inputs")


def validate_control_plane(repo_root: Path, expected_source_head: str) -> dict[str, Any]:
    """Run the complete read-only P0 materialization validation."""

    repo_root = repo_root.resolve()
    _require(
        expected_source_head == EXPECTED_SOURCE_HEAD,
        f"unexpected source head: {expected_source_head}",
    )
    math_mentor = repo_root / MATH_MENTOR_REL
    first = build_all(repo_root, expected_source_head)
    second = build_all(repo_root, expected_source_head)

    _require(set(first) == set(OUTPUT_NAMES), "generated output name set drift")
    deterministic_digests: dict[str, str] = {}
    checked_in: dict[str, dict[str, Any]] = {}
    for name in OUTPUT_NAMES:
        first_bytes = canonical_json_bytes(first[name])
        second_bytes = canonical_json_bytes(second[name])
        _require(first_bytes == second_bytes, f"repeat build differs for {name}")
        materialized_path = math_mentor / name
        try:
            materialized_bytes = materialized_path.read_bytes()
        except OSError as exc:
            raise ValidationError(f"missing materialized output {materialized_path}: {exc}") from exc
        _require(materialized_bytes == first_bytes, f"materialized bytes differ for {name}")
        checked_in[name] = _read_json(materialized_path)
        deterministic_digests[name] = sha256_bytes(first_bytes)

    for name, document in checked_in.items():
        _require(document["source_head"] == expected_source_head, f"source head drift in {name}")
        _require(document["runtime_activation_performed"] is False, f"runtime activated in {name}")
        _validate_payload_hash(document, name)
        schema_path = repo_root / document["$schema"]
        schema = _read_json(schema_path)
        _validate_json_schema(document, schema, name)

    for schema_name in ("NORMALIZED_NODE_SCHEMA.json", "AUTHORIZATION_CONTEXT_SCHEMA.json"):
        schema = _read_json(math_mentor / schema_name)
        _validate_schema_definition(schema, schema_name)

    resolutions = yaml.safe_load(
        (math_mentor / "p0_control_plane/identity_resolutions.yml").read_text(encoding="utf-8")
    )
    resolutions_schema = _read_json(
        math_mentor / "p0_control_plane/schemas/identity_resolutions.schema.json"
    )
    _validate_json_schema(resolutions, resolutions_schema, "identity_resolutions.yml")
    _require(resolutions["resolutions"] == [], "identity resolution overlay must remain empty")

    _validate_quantitative_findings(checked_in)
    _validate_identity_and_exclusions(checked_in, load_config(repo_root))
    staging = scan_staging(repo_root, expected_source_head)
    _assert_summary_subset(
        staging["summary"],
        {
            "tracked_staging_assets": 229,
            "staging_yaml_files": 228,
            "staging_non_yaml_files": 1,
            "yaml_parse_pass": 213,
            "yaml_parse_fail": 15,
            "parsed_non_mapping": 0,
            "parsed_without_top_level_id": 7,
            "basename_shadows_of_root_candidates": 195,
            "strict_identity_overlap_with_root": 180,
            "raw_content_identical_to_root": 0,
            "identity_resolution_from_staging": 0,
        },
        "staging",
    )
    return {
        "status": "passed",
        "source_head": expected_source_head,
        "repeat_builds": 2,
        "byte_identical_repeatability": True,
        "materialized_outputs_match": True,
        "output_sha256": dict(sorted(deterministic_digests.items())),
        "quantitative": {
            "tracked_assets": 1014,
            "root_candidates_parsed": 667,
            "staging_assets_excluded": 229,
            "staging_yaml_parse_pass": 213,
            "staging_yaml_parse_fail": 15,
            "staging_basename_shadows": 195,
            "staging_identity_overlap": 180,
            "roadmap_entries": 770,
            "candidate_edges_unapproved": 420,
            "explicit_alias_conflicts": 53,
            "unclaimed_source_files": 194,
            "fullwidth_alias_diagnostics": 7,
            "consumer_allowed": 0,
        },
        "runtime_activation_performed": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-source-head", default=EXPECTED_SOURCE_HEAD)
    args = parser.parse_args(argv)
    try:
        result = validate_control_plane(args.repo_root, args.expected_source_head)
    except (ValidationError, OSError, ValueError, KeyError) as exc:
        print(f"P0 validation failed: {exc}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(canonical_json_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

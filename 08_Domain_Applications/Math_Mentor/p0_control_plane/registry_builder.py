"""Build deterministic, fail-closed Math Mentor P0 control-plane registries.

Only tracked YAML files directly under Pure_Math_Intuition_DB may become root
node records.  Six split roadmaps are explicit inputs.  The aggregate roadmap,
staging content, bridges, schemas, suffix matching, basename matching, and fuzzy
matching are never identity-resolution inputs.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable, Mapping, MutableMapping, Sequence
import uuid

import yaml

try:
    from identity import (
        AliasClaim,
        IdentityError,
        artifact_uuid,
        attach_payload_sha256,
        canonical_json_bytes,
        canonical_node_uuid,
        conflict_uuid,
        distinct_claim_ids,
        edge_uuid,
        namespace_uuid,
        normalize_repo_path,
        path_set_sha256,
        roadmap_id,
        roadmap_node_uuid,
        roadmap_number,
        self_alias_claims,
        sha256_bytes,
        sha256_text,
        strict_identity,
        unparsed_fullwidth_alias_claims,
    )
except ImportError:  # pragma: no cover - supports module execution from tests
    from .identity import (  # type: ignore
        AliasClaim,
        IdentityError,
        artifact_uuid,
        attach_payload_sha256,
        canonical_json_bytes,
        canonical_node_uuid,
        conflict_uuid,
        distinct_claim_ids,
        edge_uuid,
        namespace_uuid,
        normalize_repo_path,
        path_set_sha256,
        roadmap_id,
        roadmap_node_uuid,
        roadmap_number,
        self_alias_claims,
        sha256_bytes,
        sha256_text,
        strict_identity,
        unparsed_fullwidth_alias_claims,
    )


OUTPUT_NAMES = (
    "ROOT_CORPUS_REGISTRY.json",
    "CANONICAL_NODE_CROSSWALK.json",
    "ALIAS_CONFLICT_REGISTRY.json",
)
ROADMAP_KEY_RE = re.compile(r"[\(（]n_(\d+)[\)）]$")


class BuildError(RuntimeError):
    """A fail-closed control-plane build error."""


class ForbiddenInputError(BuildError):
    """A forbidden aggregate or non-allowlisted roadmap was requested."""


@dataclass
class Stage0Bundle:
    inputs: list[dict[str, Any]]
    node_records: dict[str, dict[str, Any]]
    canonical_paths: set[str]
    duplicate_filename_numbers: dict[str, list[str]]
    source_head: str
    limitations: list[str]


@dataclass
class ScannedNode:
    path: str
    document: dict[str, Any]
    raw_sha256: str
    size: int
    canonical_uuid: str
    record: dict[str, Any]


def _run_git(repo_root: Path, arguments: Sequence[str]) -> bytes:
    try:
        return subprocess.check_output(["git", *arguments], cwd=repo_root)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - environment failure
        raise BuildError(f"git {' '.join(arguments)} failed with {exc.returncode}") from exc


def current_head(repo_root: Path) -> str:
    return _run_git(repo_root, ["rev-parse", "HEAD"]).decode("ascii").strip()


def resolve_commit(repo_root: Path, revision: str) -> str:
    return _run_git(repo_root, ["rev-parse", f"{revision}^{{commit}}"]).decode("ascii").strip()


def is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=repo_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode not in {0, 1}:
        raise BuildError(
            f"cannot verify source ancestry: {ancestor} -> {descendant} "
            f"(exit {completed.returncode})"
        )
    return completed.returncode == 0


def snapshot_tree(repo_root: Path, source_head: str, scope_root: str) -> dict[str, int]:
    """Return tracked blob sizes from an immutable commit tree without reading blobs."""

    raw = _run_git(
        repo_root,
        ["ls-tree", "-r", "-l", "-z", source_head, "--", scope_root],
    )
    result: dict[str, int] = {}
    for item in raw.split(b"\0"):
        if not item:
            continue
        try:
            metadata, raw_path = item.split(b"\t", 1)
            fields = metadata.split()
            if len(fields) != 4 or fields[1] != b"blob":
                continue
            size = int(fields[3])
            path = normalize_repo_path(raw_path.decode("utf-8"))
        except (ValueError, UnicodeError) as exc:
            raise BuildError(f"cannot parse git tree entry: {item!r}") from exc
        result[path] = size
    return dict(sorted(result.items()))


def snapshot_blobs(
    repo_root: Path,
    source_head: str,
    repo_paths: Iterable[str],
) -> dict[str, bytes]:
    """Read an explicit path allowlist from one commit via one cat-file process."""

    paths = sorted({normalize_repo_path(path) for path in repo_paths})
    queries = b"".join(f"{source_head}:{path}\n".encode("utf-8") for path in paths)
    completed = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=repo_root,
        input=queries,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise BuildError(
            f"git cat-file --batch failed with {completed.returncode}: "
            f"{completed.stderr.decode('utf-8', errors='replace')}"
        )
    output = completed.stdout
    cursor = 0
    result: dict[str, bytes] = {}
    for path in paths:
        line_end = output.find(b"\n", cursor)
        if line_end < 0:
            raise BuildError(f"truncated cat-file header for {path}")
        header = output[cursor:line_end]
        cursor = line_end + 1
        if header.endswith(b" missing"):
            raise BuildError(f"snapshot blob is missing: {source_head}:{path}")
        fields = header.split()
        if len(fields) != 3 or fields[1] != b"blob":
            raise BuildError(f"unexpected cat-file header for {path}: {header!r}")
        try:
            size = int(fields[2])
        except ValueError as exc:
            raise BuildError(f"invalid cat-file size for {path}: {header!r}") from exc
        end = cursor + size
        if end >= len(output) or output[end : end + 1] != b"\n":
            raise BuildError(f"truncated cat-file body for {path}")
        result[path] = output[cursor:end]
        cursor = end + 1
    if cursor != len(output):
        raise BuildError("unexpected trailing bytes from git cat-file --batch")
    return result


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise BuildError(f"cannot parse YAML {path}: {type(exc).__name__}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"expected mapping in YAML {path}")
    return value


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot parse JSON {path}: {type(exc).__name__}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"expected object in JSON {path}")
    return value


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_config_path(repo_root: Path) -> Path:
    return repo_root / "08_Domain_Applications/Math_Mentor/p0_control_plane/identity_namespace.yml"


def default_resolutions_path(repo_root: Path) -> Path:
    return repo_root / "08_Domain_Applications/Math_Mentor/p0_control_plane/identity_resolutions.yml"


def load_config(repo_root: Path, path: Path | None = None) -> dict[str, Any]:
    config_path = path or default_config_path(repo_root)
    config = _read_yaml(config_path)
    calculated_namespace = namespace_uuid(str(config.get("namespace_name", "")))
    configured_namespace = str(config.get("namespace_uuid", ""))
    if str(calculated_namespace) != configured_namespace:
        raise BuildError(
            f"namespace UUID mismatch: configured={configured_namespace}, calculated={calculated_namespace}"
        )
    return config


def ensure_allowed_roadmap_path(path: str, config: Mapping[str, Any]) -> str:
    normalized = normalize_repo_path(path)
    forbidden = {
        normalize_repo_path(str(item)) for item in config.get("forbidden_inputs", [])
    }
    if normalized in forbidden or Path(normalized).name == "数学知识路线图_全部.yaml":
        raise ForbiddenInputError(f"aggregate roadmap is forbidden: {normalized}")
    allowlist = {
        normalize_repo_path(str(item["path"])) for item in config.get("split_roadmaps", [])
    }
    if normalized not in allowlist:
        raise ForbiddenInputError(f"roadmap is not in the six-file allowlist: {normalized}")
    return normalized


def _input_evidence(
    blobs: Mapping[str, bytes],
    repo_path: str,
    role: str,
) -> dict[str, Any]:
    normalized = normalize_repo_path(repo_path)
    try:
        raw = blobs[normalized]
    except KeyError as exc:
        raise BuildError(f"input blob was not prefetched: {normalized}") from exc
    return {
        "path": normalized,
        "role": role,
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
    }


def load_stage0(
    blobs: Mapping[str, bytes],
    config: Mapping[str, Any],
) -> Stage0Bundle:
    section = config["stage0_inventory"]
    documents: dict[str, dict[str, Any]] = {}
    inputs: list[dict[str, Any]] = []
    for raw_path in section["files"]:
        repo_path = normalize_repo_path(str(raw_path))
        inputs.append(
            _input_evidence(
                blobs,
                repo_path,
                "stage0_non_authoritative_evidence",
            )
        )
        try:
            parsed = json.loads(blobs[repo_path].decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise BuildError(f"cannot parse Stage0 JSON blob {repo_path}: {exc}") from exc
        if not isinstance(parsed, dict):
            raise BuildError(f"expected object in Stage0 JSON blob {repo_path}")
        documents[Path(repo_path).name] = parsed

    expected_names = {
        "corpus_manifest.json",
        "node_classification.json",
        "structural_exclusions.json",
        "parse_report.json",
        "identity_aliases.json",
        "duplicates_missing_conflicts.json",
    }
    if set(documents) != expected_names:
        raise BuildError(f"Stage0 inventory set mismatch: {sorted(documents)}")

    node_records_list = documents["node_classification.json"].get("records")
    if not isinstance(node_records_list, list):
        raise BuildError("Stage0 node_classification records must be a list")
    node_records = {
        normalize_repo_path(str(record["path"])): record
        for record in node_records_list
    }
    canonical_paths = {
        path
        for path, record in node_records.items()
        if record.get("classification") == "canonical_teaching_node"
    }
    duplicate_numbers_raw = documents["duplicates_missing_conflicts.json"].get(
        "duplicate_filename_numbers", {}
    )
    if not isinstance(duplicate_numbers_raw, dict):
        raise BuildError("Stage0 duplicate_filename_numbers must be an object")
    duplicate_numbers = {
        str(key): [normalize_repo_path(str(path)) for path in paths]
        for key, paths in duplicate_numbers_raw.items()
    }
    return Stage0Bundle(
        inputs=sorted(inputs, key=lambda item: item["path"]),
        node_records=node_records,
        canonical_paths=canonical_paths,
        duplicate_filename_numbers=duplicate_numbers,
        source_head=str(section["source_head"]),
        limitations=[str(item) for item in section.get("limitations", [])],
    )


def _effective_field(document: Mapping[str, Any], field: str) -> Any:
    if field in document:
        return document[field]
    concept_node = document.get("concept_node")
    if isinstance(concept_node, Mapping):
        return concept_node.get(field)
    return None


def _schema_era(path: str, document: Mapping[str, Any], stage0: Stage0Bundle) -> str:
    if "id" not in document:
        return "E1_wrapper_or_alternate_identity"
    if document.get("math_lane") in {"MathLane_A", "MathLane_B"}:
        return "E4_post_stage0_repaired"
    if path in stage0.canonical_paths:
        return "E3_stage0_canonical_body"
    return "E2_flat_migration_legacy"


def _path_identity_relation(path: str, strict_value: str | None) -> str:
    if strict_value is None:
        return "identity_missing"
    stem = Path(path).stem
    if stem == strict_value:
        return "exact_root_filename_stem"
    if stem.startswith(strict_value + "_"):
        return "strict_id_prefix_in_root_filename"
    return "exact_filename_and_domain_id_differ"


def _typed_alias(
    alias_type: str,
    value: str,
    namespace_or_version: Any,
    status: str,
    source_path: str,
    content_sha256: str,
    json_pointer: str | None,
    resolution_ref: str | None = None,
) -> dict[str, Any]:
    return {
        "alias_type": alias_type,
        "value": value,
        "namespace_or_version": namespace_or_version,
        "status": status,
        "source": {
            "path": source_path,
            "json_pointer": json_pointer,
            "content_sha256": content_sha256,
        },
        "resolution_ref": resolution_ref,
    }


def _typed_alias_sort_key(alias: Mapping[str, Any]) -> tuple[str, str, str, str]:
    source = alias.get("source")
    source_path = ""
    json_pointer = ""
    if isinstance(source, Mapping):
        source_path = str(source.get("path", ""))
        json_pointer = str(source.get("json_pointer") or "")
    return (
        str(alias.get("alias_type", "")),
        str(alias.get("value", "")),
        source_path,
        json_pointer,
    )


def _excluded_reason(db_root: str, path: str) -> str:
    relative = path[len(db_root) + 1 :]
    if "/" in relative:
        return "nested_or_staging_not_root_direct"
    name = Path(path).name
    if name.startswith("BRIDGE-") and name.endswith(('.yaml', '.yml')):
        return "root_bridge_asset"
    if name == "schema.yaml":
        return "root_structural_schema"
    if Path(name).suffix == ".py":
        return "root_script_or_test"
    return "root_non_candidate_asset"


def root_candidate_paths(
    config: Mapping[str, Any],
    tracked_tree: Mapping[str, int],
) -> list[str]:
    """Discover candidates from tracked tree metadata, without reading assets."""

    db_root = normalize_repo_path(str(config["db_root"]))
    db_prefix = db_root + "/"
    db_paths = sorted(path for path in tracked_tree if path.startswith(db_prefix))
    root_direct = [path for path in db_paths if "/" not in path[len(db_prefix) :]]
    return sorted(
        path
        for path in root_direct
        if Path(path).suffix in {".yaml", ".yml"}
        and Path(path).name != "schema.yaml"
        and not Path(path).name.startswith("BRIDGE-")
    )


def scan_root_corpus(
    blobs: Mapping[str, bytes],
    config: Mapping[str, Any],
    stage0: Stage0Bundle,
    source_head: str,
    tracked_tree: Mapping[str, int],
    namespace: uuid.UUID,
) -> tuple[dict[str, Any], list[ScannedNode]]:
    scope_root = normalize_repo_path(str(config["scope_root"]))
    db_root = normalize_repo_path(str(config["db_root"]))
    baseline = config["baseline"]
    db_prefix = db_root + "/"
    tracked_paths = sorted(tracked_tree)
    db_paths = sorted(path for path in tracked_paths if path.startswith(db_prefix))
    root_direct = [path for path in db_paths if "/" not in path[len(db_prefix) :]]
    nested = [path for path in db_paths if path not in set(root_direct)]

    root_candidates = root_candidate_paths(config, tracked_tree)

    exact_checks = {
        "db_tracked_count": len(db_paths),
        "root_direct_count": len(root_direct),
        "nested_excluded_count": len(nested),
        "root_candidate_count": len(root_candidates),
        "root_bridge_count": sum(Path(path).name.startswith("BRIDGE-") for path in root_direct),
        "root_schema_count": sum(Path(path).name == "schema.yaml" for path in root_direct),
        "root_script_count": sum(Path(path).suffix == ".py" for path in root_direct),
    }
    for key, actual in exact_checks.items():
        expected = int(baseline[key])
        if actual != expected:
            raise BuildError(f"baseline {key} mismatch: expected={expected}, actual={actual}")

    scanned: list[ScannedNode] = []
    identity_to_paths: defaultdict[str, list[str]] = defaultdict(list)
    for path in root_candidates:
        try:
            raw = blobs[path]
        except KeyError as exc:
            raise BuildError(f"root candidate blob was not prefetched: {path}") from exc
        try:
            document = yaml.safe_load(raw.decode("utf-8"))
        except (UnicodeError, yaml.YAMLError) as exc:
            raise BuildError(f"root candidate parse failed: {path}: {type(exc).__name__}: {exc}") from exc
        if not isinstance(document, dict):
            raise BuildError(f"root candidate is not a mapping: {path}")
        identity = strict_identity(document)
        fullwidth_claims = unparsed_fullwidth_alias_claims(document)
        canonical_uuid = canonical_node_uuid(namespace, path)
        aliases = [
            _typed_alias(
                "root_path",
                path,
                "repo_relative_exact_path_v1",
                "observed",
                path,
                sha256_bytes(raw),
                None,
            ),
            _typed_alias(
                "root_filename",
                Path(path).name,
                "exact_root_filename_v1",
                "observed",
                path,
                sha256_bytes(raw),
                None,
            ),
        ]
        if identity.value is not None:
            identity_to_paths[identity.value].append(path)
            aliases.append(
                _typed_alias(
                    "domain_id",
                    identity.value,
                    "math_mentor_domain_id_v1",
                    "observed",
                    path,
                    sha256_bytes(raw),
                    "/" + (identity.locator or "").replace(".", "/"),
                )
            )
        blockers = ["control_plane_identity_not_human_approved"]
        if identity.status == "missing":
            blockers.append("strict_domain_id_missing")
        elif identity.status == "conflicting":
            blockers.append("strict_domain_id_conflicting")
        if fullwidth_claims:
            blockers.append("unicode_fullwidth_roadmap_tag_unparsed")
        observed = {
            "mode": _effective_field(document, "mode"),
            "math_lane": document.get("math_lane"),
            "validation_status": _effective_field(document, "validation_status"),
            "bridge_readiness_status": _effective_field(document, "bridge_readiness_status"),
            "teaching_ready": document.get("teaching_ready"),
            "coordinator_consumable": document.get("coordinator_consumable"),
        }
        record = {
            "canonical_uuid": canonical_uuid,
            "bootstrap_uuid_seed": {
                "kind": "exact_root_path",
                "value": path,
                "immutable_after_materialization": True,
            },
            "path": path,
            "bytes": len(raw),
            "sha256": sha256_bytes(raw),
            "parsed": True,
            "schema_era": _schema_era(path, document, stage0),
            "strict_identity": identity.as_dict(),
            "typed_aliases": sorted(aliases, key=_typed_alias_sort_key),
            "path_identity_relation": _path_identity_relation(path, identity.value),
            "unparsed_fullwidth_roadmap_tags": [
                claim.as_dict() for claim in fullwidth_claims
            ],
            "observed_statuses": observed,
            "registry_status": (
                "registered"
                if identity.status.startswith("resolved")
                else f"blocked_identity_{identity.status}"
            ),
            "blockers": blockers,
            "runtime_allowed": False,
        }
        scanned.append(
            ScannedNode(path, document, sha256_bytes(raw), len(raw), canonical_uuid, record)
        )

    duplicate_ids = {
        value: paths for value, paths in identity_to_paths.items() if len(paths) > 1
    }
    if duplicate_ids:
        for node in scanned:
            value = node.record["strict_identity"]["value"]
            if value in duplicate_ids:
                node.record["registry_status"] = "blocked_identity_duplicate"
                node.record["blockers"].append("strict_domain_id_duplicate")

    excluded: list[dict[str, Any]] = []
    candidate_set = set(root_candidates)
    for path in db_paths:
        if path in candidate_set:
            continue
        excluded.append(
            {
                "asset_uuid": artifact_uuid(namespace, path),
                "path": path,
                "bytes": tracked_tree[path],
                "reason": _excluded_reason(db_root, path),
                "parsed_as_node": False,
                "identity_resolution_allowed": False,
            }
        )

    era_counts = Counter(node.record["schema_era"] for node in scanned)
    identity_counts = Counter(node.record["strict_identity"]["status"] for node in scanned)
    relation_counts = Counter(node.record["path_identity_relation"] for node in scanned)
    fullwidth_tag_file_count = sum(
        bool(node.record["unparsed_fullwidth_roadmap_tags"]) for node in scanned
    )
    registry = {
        "$schema": "08_Domain_Applications/Math_Mentor/p0_control_plane/schemas/root_corpus_registry.schema.json",
        "schema_version": "1.0.0",
        "source_head": source_head,
        "generator_version": "p0_control_plane_registry_builder_v1",
        "namespace_uuid": str(namespace),
        "source_snapshot_policy": {
            "controlled_corpus_inputs_read_from_git_commit": True,
            "development_head_may_equal_or_descend_from_source_head": True,
            "worktree_inputs": ["identity_namespace.yml", "identity_resolutions.yml"],
        },
        "scope_root": scope_root,
        "db_root": db_root,
        "inputs": stage0.inputs,
        "tracked_scope_path_set_sha256": path_set_sha256(tracked_paths),
        "discovery_policy": {
            "mode": "git_tracked_root_direct_only",
            "candidate_extensions": [".yaml", ".yml"],
            "excluded_root_classes": ["bridge", "schema", "script_or_test"],
            "nested_and_staging_identity_resolution_allowed": False,
            "suffix_basename_fuzzy_resolution_allowed": False,
        },
        "summary": {
            "tracked_scope_path_count": len(tracked_paths),
            **exact_checks,
            "root_candidate_parse_pass_count": len(scanned),
            "strict_identity_counts": dict(sorted(identity_counts.items())),
            "unique_strict_identity_count": len(identity_to_paths),
            "duplicate_strict_identity_count": len(duplicate_ids),
            "schema_era_counts": dict(sorted(era_counts.items())),
            "path_identity_relation_counts": dict(sorted(relation_counts.items())),
            "excluded_asset_count": len(excluded),
            "candidate_bytes": sum(node.size for node in scanned),
            "unicode_fullwidth_roadmap_tag_unparsed_file_count": fullwidth_tag_file_count,
        },
        "nodes": [
            node.record for node in sorted(scanned, key=lambda item: item.canonical_uuid)
        ],
        "excluded_assets": sorted(excluded, key=lambda item: item["path"]),
        "runtime_activation_performed": False,
    }
    return attach_payload_sha256(registry), scanned


def _collect_roadmap_entries(value: Any, entries: list[tuple[int, str]]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if isinstance(key, str):
                match = ROADMAP_KEY_RE.search(key)
                if match:
                    entries.append((int(match.group(1)), key))
            _collect_roadmap_entries(child, entries)
    elif isinstance(value, list):
        for child in value:
            _collect_roadmap_entries(child, entries)


def load_split_roadmaps(
    blobs: Mapping[str, bytes],
    config: Mapping[str, Any],
    namespace: uuid.UUID,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    input_records: list[dict[str, Any]] = []
    roadmap_nodes: list[dict[str, Any]] = []
    seen: set[int] = set()
    configured = config.get("split_roadmaps", [])
    if len(configured) != 6:
        raise BuildError(f"exactly six split roadmaps are required, got {len(configured)}")

    for specification in sorted(configured, key=lambda item: int(item["level"])):
        path = ensure_allowed_roadmap_path(str(specification["path"]), config)
        try:
            raw = blobs[path]
        except KeyError as exc:
            raise BuildError(f"split roadmap blob was not prefetched: {path}") from exc
        digest = sha256_bytes(raw)
        if digest != str(specification["sha256"]):
            raise BuildError(f"split roadmap hash mismatch for {path}: {digest}")
        try:
            document = yaml.safe_load(raw.decode("utf-8"))
        except (UnicodeError, yaml.YAMLError) as exc:
            raise BuildError(f"split roadmap parse failed: {path}: {exc}") from exc
        entries: list[tuple[int, str]] = []
        _collect_roadmap_entries(document, entries)
        numbers = [number for number, _ in entries]
        expected = list(
            range(int(specification["expected_first"]), int(specification["expected_last"]) + 1)
        )
        if numbers != expected or len(numbers) != int(specification["expected_count"]):
            raise BuildError(
                f"split roadmap identity sequence mismatch for {path}: "
                f"expected {expected[0]}..{expected[-1]}, got {numbers[:1]}..{numbers[-1:]}"
            )
        input_records.append(
            {
                "path": path,
                "role": "explicit_split_roadmap",
                "level": int(specification["level"]),
                "bytes": len(raw),
                "sha256": digest,
                "entry_count": len(entries),
            }
        )
        for ordinal, (number, title) in enumerate(entries, start=1):
            if number in seen:
                raise BuildError(f"duplicate roadmap identity across split files: n_{number}")
            seen.add(number)
            rid = roadmap_id(number)
            roadmap_nodes.append(
                {
                    "roadmap_entry_uuid": roadmap_node_uuid(namespace, rid),
                    "roadmap_id_alias": rid,
                    "alias_namespace_or_version": {
                        "roadmap_set": "split_roadmap_v1",
                        "level": int(specification["level"]),
                        "source_sha256": digest,
                    },
                    "level": int(specification["level"]),
                    "ordinal_in_level": ordinal,
                    "source_path": path,
                    "source_sha256": digest,
                    "title_sha256": sha256_text(title),
                }
            )

    if seen != set(range(1, 771)):
        missing = sorted(set(range(1, 771)) - seen)
        extra = sorted(seen - set(range(1, 771)))
        raise BuildError(f"split roadmap global identity mismatch: missing={missing}, extra={extra}")
    return sorted(input_records, key=lambda item: item["level"]), sorted(
        roadmap_nodes, key=lambda item: roadmap_number(item["roadmap_id_alias"])
    )


def _source_disposition(document: Mapping[str, Any]) -> dict[str, Any] | None:
    if document.get("bridge_readiness_status") != "blocked_by_disposition":
        return None
    evidence: dict[str, Any] = {
        "bridge_readiness_status": "blocked_by_disposition",
    }
    for key in ("canonical_target_id", "canonical_target", "canonical_math_target"):
        if key in document:
            evidence[key] = document[key]
    return evidence


def build_crosswalk(
    config: Mapping[str, Any],
    stage0: Stage0Bundle,
    scans: Sequence[ScannedNode],
    roadmap_inputs: Sequence[dict[str, Any]],
    roadmap_nodes: Sequence[dict[str, Any]],
    namespace: uuid.UUID,
    head: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    roadmap_by_id = {item["roadmap_id_alias"]: item for item in roadmap_nodes}
    comparisons = Counter()
    binding_statuses = Counter()
    explicit_claimed_ids: set[str] = set()
    fullwidth_diagnostic_file_count = 0
    records: list[dict[str, Any]] = []

    for scan in sorted(scans, key=lambda item: item.path):
        claims = self_alias_claims(scan.document)
        explicit_ids = distinct_claim_ids(claims)
        fullwidth_claims = unparsed_fullwidth_alias_claims(scan.document)
        fullwidth_ids = distinct_claim_ids(fullwidth_claims)
        if fullwidth_ids:
            fullwidth_diagnostic_file_count += 1
        for rid in explicit_ids:
            if rid not in roadmap_by_id:
                raise BuildError(f"explicit self claim is outside split roadmaps: {scan.path}: {rid}")
            explicit_claimed_ids.add(rid)
        stage0_record = stage0.node_records.get(scan.path, {})
        raw_stage0_claim = stage0_record.get("roadmap_identity_or_alias")
        stage0_claim = str(raw_stage0_claim) if raw_stage0_claim else None

        if len(explicit_ids) > 1:
            comparison = "explicit_multi_claim"
        elif len(explicit_ids) == 1 and stage0_claim == explicit_ids[0]:
            comparison = "agree"
        elif len(explicit_ids) == 1 and stage0_claim is None:
            comparison = "explicit_only"
        elif len(explicit_ids) == 1:
            comparison = "disagree"
        elif stage0_claim is not None:
            comparison = "stage0_only"
        else:
            comparison = "neither"
        comparisons[comparison] += 1

        disposition = _source_disposition(scan.document)
        if disposition is not None:
            binding_status = "quarantined"
        elif comparison in {"agree", "explicit_only"}:
            binding_status = "declared_consistent_unapproved"
        elif comparison in {"disagree", "explicit_multi_claim"}:
            binding_status = "conflict_open"
        else:
            binding_status = "unclaimed"
        binding_statuses[binding_status] += 1

        roadmap_aliases: list[dict[str, Any]] = []
        for claim in claims:
            roadmap_record = roadmap_by_id[claim.roadmap_id]
            roadmap_aliases.append(
                _typed_alias(
                    "roadmap_id",
                    claim.roadmap_id,
                    roadmap_record["alias_namespace_or_version"],
                    (
                        "declared_unapproved"
                        if binding_status == "declared_consistent_unapproved"
                        else "conflict"
                    ),
                    scan.path,
                    scan.raw_sha256,
                    "/" + claim.locator.replace(".", "/"),
                )
            )
        legacy_aliases: list[dict[str, Any]] = []
        if stage0_claim is not None:
            legacy_aliases.append(
                _typed_alias(
                    "legacy_alias",
                    stage0_claim,
                    {
                        "source": "stage0_inventory",
                        "source_head": stage0.source_head,
                        "authoritative": False,
                    },
                    "observed_non_authoritative",
                    next(
                        item["path"]
                        for item in stage0.inputs
                        if item["path"].endswith("node_classification.json")
                    ),
                    next(
                        item["sha256"]
                        for item in stage0.inputs
                        if item["path"].endswith("node_classification.json")
                    ),
                    None,
                )
            )

        aliases = list(scan.record["typed_aliases"]) + roadmap_aliases + legacy_aliases
        aliases.sort(key=_typed_alias_sort_key)
        linked_rid = explicit_ids[0] if binding_status == "declared_consistent_unapproved" else None
        linked_roadmap_uuid = (
            roadmap_by_id[linked_rid]["roadmap_entry_uuid"] if linked_rid is not None else None
        )
        records.append(
            {
                "canonical_uuid": scan.canonical_uuid,
                "aliases": aliases,
                "alias_comparison": {
                    "status": comparison,
                    "explicit_roadmap_claims": list(explicit_ids),
                    "stage0_non_authoritative_claim": stage0_claim,
                    "unparsed_fullwidth_roadmap_claims": list(fullwidth_ids),
                },
                "candidate_edge_uuid": (
                    edge_uuid(namespace, scan.canonical_uuid, linked_roadmap_uuid)
                    if linked_roadmap_uuid
                    else None
                ),
                "candidate_roadmap_entry_uuid": linked_roadmap_uuid,
                "binding_status": binding_status,
                "source_disposition": disposition,
                "blockers": [
                    "human_identity_approval_required",
                    *(
                        ["alias_evidence_conflict"]
                        if binding_status == "conflict_open"
                        else []
                    ),
                    *(
                        ["unicode_fullwidth_roadmap_tag_unparsed"]
                        if fullwidth_ids
                        else []
                    ),
                    *(["source_quarantine_disposition"] if disposition else []),
                ],
                "consumer_allowed": False,
                "resolution_ref": None,
            }
        )

    duplicate_explicit_claims = len(explicit_claimed_ids) != sum(
        1 for record in records if record["alias_comparison"]["explicit_roadmap_claims"]
    )
    if duplicate_explicit_claims:
        raise BuildError("explicit self claims are not one-to-one at the fixed source head")

    crosswalk = {
        "$schema": "08_Domain_Applications/Math_Mentor/p0_control_plane/schemas/canonical_node_crosswalk.schema.json",
        "schema_version": "1.0.0",
        "source_head": head,
        "generator_version": "p0_control_plane_registry_builder_v1",
        "namespace_uuid": str(namespace),
        "source_snapshot_policy": {
            "controlled_corpus_inputs_read_from_git_commit": True,
            "development_head_may_equal_or_descend_from_source_head": True,
            "worktree_inputs": ["identity_namespace.yml", "identity_resolutions.yml"],
        },
        "identity_model": {
            "sole_node_primary": "canonical_uuid",
            "human_readable_identifiers_are_typed_aliases": True,
            "bootstrap_seed": "exact_root_path",
            "bootstrap_uuid_is_immutable_after_materialization": True,
            "bootstrap_only": True,
            "prior_crosswalk_preservation_implemented": False,
            "post_bootstrap_alias_or_path_change_requires_human_reviewed_migration": True,
            "human_resolution_trust_adapter_implemented": False,
            "future_resolution_statuses": ["human_approved", "stale_resolution"],
            "automatic_semantic_identity_judgment": False,
        },
        "inputs": [*stage0.inputs, *roadmap_inputs],
        "stage0_evidence_policy": {
            "authoritative": False,
            "source_head": stage0.source_head,
            "limitations": stage0.limitations,
        },
        "resolution_policy": config["resolution_policy"],
        "extraction_limitations": [
            {
                "code": "unicode_fullwidth_roadmap_tag_unparsed",
                "status": "open",
                "effect": "diagnostic_evidence_only_no_candidate_edge",
                "requires_human": True,
            }
        ],
        "summary": {
            "canonical_node_count": len(records),
            "roadmap_entry_count": len(roadmap_nodes),
            "explicit_self_claim_file_count": sum(
                bool(record["alias_comparison"]["explicit_roadmap_claims"])
                for record in records
            ),
            "distinct_explicit_roadmap_claim_count": len(explicit_claimed_ids),
            "roadmap_without_explicit_claim_count": len(roadmap_nodes) - len(explicit_claimed_ids),
            "alias_comparison_counts": dict(sorted(comparisons.items())),
            "binding_status_counts": dict(sorted(binding_statuses.items())),
            "candidate_edge_count": sum(record["candidate_edge_uuid"] is not None for record in records),
            "human_approved_binding_count": 0,
            "consumer_allowed_count": 0,
            "unicode_fullwidth_roadmap_tag_unparsed_file_count": fullwidth_diagnostic_file_count,
        },
        "roadmap_entries": list(roadmap_nodes),
        "nodes": sorted(records, key=lambda item: item["canonical_uuid"]),
        "runtime_activation_performed": False,
    }
    return attach_payload_sha256(crosswalk), records


def _subject_for_node(scan: ScannedNode, **extra: Any) -> dict[str, Any]:
    subject = {
        "subject_uuid": scan.canonical_uuid,
        "canonical_uuid": scan.canonical_uuid,
        "path": scan.path,
    }
    subject.update(extra)
    return subject


def _make_conflict(
    namespace: uuid.UUID,
    conflict_type: str,
    subjects: Sequence[dict[str, Any]],
    evidence: Sequence[dict[str, Any]],
    prohibited_methods: Sequence[str],
    severity: str,
    status: str,
    requires_human: bool,
    allowed_decisions: Sequence[str],
    blocking_scopes: Sequence[str],
) -> dict[str, Any]:
    subject_uuids = [str(item["subject_uuid"]) for item in subjects]
    return {
        "conflict_uuid": conflict_uuid(namespace, conflict_type, subject_uuids),
        "type": conflict_type,
        "severity": severity,
        "status": status,
        "requires_human": requires_human,
        "subjects": list(subjects),
        "evidence": list(evidence),
        "prohibited_resolution_methods": list(prohibited_methods),
        "allowed_decisions": list(allowed_decisions),
        "blocking_scopes": list(blocking_scopes),
        "resolution_ref": None,
    }


def build_conflicts(
    config: Mapping[str, Any],
    stage0: Stage0Bundle,
    scans: Sequence[ScannedNode],
    crosswalk_records: Sequence[dict[str, Any]],
    namespace: uuid.UUID,
    head: str,
) -> dict[str, Any]:
    scans_by_path = {scan.path: scan for scan in scans}
    crosswalk_by_uuid = {record["canonical_uuid"]: record for record in crosswalk_records}
    prohibited = [str(item) for item in config["resolution_policy"]["prohibited_methods"]]
    blockers = [str(item) for item in config["resolution_policy"]["fail_closed_consumers"]]
    conflicts: list[dict[str, Any]] = []

    for scan in sorted(scans, key=lambda item: item.path):
        record = crosswalk_by_uuid[scan.canonical_uuid]
        comparison = record["alias_comparison"]
        if comparison["status"] in {"disagree", "explicit_multi_claim"}:
            conflicts.append(
                _make_conflict(
                    namespace,
                    "explicit_vs_stage0_alias_disagreement",
                    [
                        _subject_for_node(
                            scan,
                            explicit_claims=comparison["explicit_roadmap_claims"],
                            stage0_claim=comparison["stage0_non_authoritative_claim"],
                        )
                    ],
                    [
                        {
                            "kind": "current_self_description_vs_non_authoritative_stage0",
                            "current_path": scan.path,
                            "current_content_sha256": scan.raw_sha256,
                            "explicit_claims": comparison["explicit_roadmap_claims"],
                            "stage0_claim": comparison["stage0_non_authoritative_claim"],
                            "stage0_source_head": stage0.source_head,
                        }
                    ],
                    prohibited,
                    "error",
                    "open",
                    True,
                    ["bind_with_external_semantic_evidence", "keep_unbound", "quarantine", "defer"],
                    blockers,
                )
            )
        if not comparison["explicit_roadmap_claims"]:
            missing_alias_evidence = [
                {
                    "kind": "self_description_allowlist_has_no_ascii_roadmap_tag",
                    "current_path": scan.path,
                    "current_content_sha256": scan.raw_sha256,
                    "stage0_claim": comparison["stage0_non_authoritative_claim"],
                    "stage0_authoritative": False,
                }
            ]
            if comparison.get("unparsed_fullwidth_roadmap_claims"):
                missing_alias_evidence.append(
                    {
                        "kind": "unicode_fullwidth_roadmap_tag_unparsed",
                        "status": "open",
                        "claims": comparison["unparsed_fullwidth_roadmap_claims"],
                        "current_path": scan.path,
                        "current_content_sha256": scan.raw_sha256,
                        "candidate_edge_created": False,
                        "consumer_allowed": False,
                        "resolution_inference_allowed": False,
                    }
                )
            conflicts.append(
                _make_conflict(
                    namespace,
                    "missing_explicit_roadmap_alias",
                    [
                        _subject_for_node(
                            scan,
                            stage0_claim=comparison["stage0_non_authoritative_claim"],
                        )
                    ],
                    missing_alias_evidence,
                    prohibited,
                    "error",
                    "open",
                    True,
                    ["bind_with_external_semantic_evidence", "keep_unbound", "quarantine", "defer"],
                    blockers,
                )
            )
        if scan.record["strict_identity"]["status"] == "missing":
            conflicts.append(
                _make_conflict(
                    namespace,
                    "strict_domain_id_missing",
                    [_subject_for_node(scan)],
                    [
                        {
                            "kind": "strict_locator_scan",
                            "current_path": scan.path,
                            "current_content_sha256": scan.raw_sha256,
                            "locator_hits": [],
                        }
                    ],
                    prohibited,
                    "error",
                    "open",
                    True,
                    ["add_reviewed_domain_id_alias", "quarantine", "defer"],
                    blockers,
                )
            )
        if record["source_disposition"] is not None:
            conflicts.append(
                _make_conflict(
                    namespace,
                    "source_quarantine_disposition",
                    [_subject_for_node(scan)],
                    [
                        {
                            "kind": "current_source_disposition",
                            "current_path": scan.path,
                            "current_content_sha256": scan.raw_sha256,
                            "disposition": record["source_disposition"],
                        }
                    ],
                    prohibited,
                    "blocker",
                    "quarantined",
                    True,
                    ["keep_quarantined", "canonicalize_with_human_evidence", "defer"],
                    blockers,
                )
            )
        if scan.record["path_identity_relation"] == "exact_filename_and_domain_id_differ":
            conflicts.append(
                _make_conflict(
                    namespace,
                    "filename_domain_id_difference_diagnostic",
                    [_subject_for_node(scan)],
                    [
                        {
                            "kind": "exact_observed_alias_difference",
                            "root_filename": Path(scan.path).name,
                            "strict_domain_id": scan.record["strict_identity"]["value"],
                            "resolution_inference_allowed": False,
                        }
                    ],
                    prohibited,
                    "warning",
                    "diagnostic",
                    False,
                    ["record_only"],
                    [],
                )
            )

    for suffix, paths in sorted(
        stage0.duplicate_filename_numbers.items(), key=lambda item: int(item[0])
    ):
        subjects = [
            _subject_for_node(scans_by_path[path], observed_suffix=f"n_{int(suffix):03d}")
            for path in sorted(paths)
            if path in scans_by_path
        ]
        if len(subjects) < 2:
            raise BuildError(f"Stage0 suffix collision has fewer than two current root subjects: {suffix}")
        conflicts.append(
            _make_conflict(
                namespace,
                "forbidden_filename_suffix_collision_evidence",
                subjects,
                [
                    {
                        "kind": "non_authoritative_stage0_suffix_bucket",
                        "suffix": f"n_{int(suffix):03d}",
                        "member_count": len(subjects),
                        "stage0_source_head": stage0.source_head,
                        "resolution_inference_allowed": False,
                    }
                ],
                prohibited,
                "error",
                "open",
                True,
                ["resolve_each_subject_with_external_semantic_evidence", "keep_unbound", "defer"],
                blockers,
            )
        )

    counts = Counter(item["type"] for item in conflicts)
    membership_counts = {
        "forbidden_filename_suffix_collision_member_count": sum(
            len(item["subjects"])
            for item in conflicts
            if item["type"] == "forbidden_filename_suffix_collision_evidence"
        ),
        "unicode_fullwidth_roadmap_tag_unparsed_file_count": sum(
            any(
                evidence.get("kind") == "unicode_fullwidth_roadmap_tag_unparsed"
                for evidence in item["evidence"]
            )
            for item in conflicts
        ),
    }
    registry = {
        "$schema": "08_Domain_Applications/Math_Mentor/p0_control_plane/schemas/alias_conflict_registry.schema.json",
        "schema_version": "1.0.0",
        "source_head": head,
        "generator_version": "p0_control_plane_registry_builder_v1",
        "namespace_uuid": str(namespace),
        "source_snapshot_policy": {
            "controlled_corpus_inputs_read_from_git_commit": True,
            "development_head_may_equal_or_descend_from_source_head": True,
            "worktree_inputs": ["identity_namespace.yml", "identity_resolutions.yml"],
        },
        "stage0_evidence_policy": {
            "authoritative": False,
            "source_head": stage0.source_head,
            "limitations": stage0.limitations,
        },
        "extraction_limitations": [
            {
                "code": "unicode_fullwidth_roadmap_tag_unparsed",
                "status": "open",
                "effect": "retained_as_diagnostic_evidence_inside_missing-alias_conflicts",
                "requires_human": True,
            }
        ],
        "summary": {
            "conflict_record_count": len(conflicts),
            "counts_by_type": dict(sorted(counts.items())),
            **membership_counts,
            "resolved_by_suffix_count": 0,
            "resolved_by_basename_count": 0,
            "resolved_by_fuzzy_match_count": 0,
            "resolved_from_staging_count": 0,
        },
        "conflicts": sorted(conflicts, key=lambda item: (item["type"], item["conflict_uuid"])),
        "runtime_activation_performed": False,
    }
    return attach_payload_sha256(registry)


def validate_and_apply_resolutions(
    resolutions: Mapping[str, Any],
    head: str,
    crosswalk: MutableMapping[str, Any],
    conflict_registry: MutableMapping[str, Any],
    required_approver: str,
) -> None:
    """Fail closed until an external Human-authenticated adapter exists.

    A model-writable YAML payload cannot authenticate itself by containing the
    string ``approved_by: Human Speaker``.  The empty overlay is retained only
    as a future data contract; production P0 rejects every non-empty payload.
    """

    allowed_keys = {"schema_version", "namespace_uuid", "resolutions"}
    if set(resolutions) != allowed_keys:
        raise BuildError(
            "identity resolutions overlay must contain exactly schema_version, "
            "namespace_uuid, and resolutions"
        )
    if resolutions.get("schema_version") != "1.0.0":
        raise BuildError("identity resolutions schema_version must be 1.0.0")
    if resolutions.get("namespace_uuid") != crosswalk.get("namespace_uuid"):
        raise BuildError("identity resolutions namespace does not match the crosswalk")
    if required_approver != "Human Speaker":
        raise BuildError("identity resolution policy must require Human Speaker")

    raw_resolutions = resolutions.get("resolutions", [])
    if not isinstance(raw_resolutions, list):
        raise BuildError("identity resolutions must be a list")
    if raw_resolutions:
        raise BuildError(
            "non-empty identity_resolutions.yml is untrusted: external "
            "Human-authenticated resolution adapter is not implemented"
        )


def build_all(
    repo_root: Path,
    expected_head: str,
    config_path: Path | None = None,
    resolutions_path: Path | None = None,
) -> dict[str, dict[str, Any]]:
    repo_root = repo_root.resolve()
    if not expected_head:
        raise BuildError("expected_head is required")
    source_head = resolve_commit(repo_root, expected_head)
    development_head = current_head(repo_root)
    if not is_ancestor(repo_root, source_head, development_head):
        raise BuildError(
            f"source snapshot is not an ancestor of current HEAD: "
            f"source={source_head}, current={development_head}"
        )

    config = load_config(repo_root, config_path)
    baseline = config["baseline"]
    if source_head != str(baseline["expected_head"]):
        raise BuildError(
            f"expected_head does not match frozen baseline: {source_head} != {baseline['expected_head']}"
        )
    namespace = uuid.UUID(str(config["namespace_uuid"]))
    tracked_tree = snapshot_tree(repo_root, source_head, str(config["scope_root"]))
    tracked_paths = sorted(tracked_tree)
    actual_path_digest = path_set_sha256(tracked_paths)
    if len(tracked_paths) != int(baseline["tracked_scope_path_count"]):
        raise BuildError(
            f"tracked scope count mismatch: expected={baseline['tracked_scope_path_count']}, "
            f"actual={len(tracked_paths)}"
        )
    if actual_path_digest != str(baseline["tracked_scope_path_set_sha256"]):
        raise BuildError(
            f"tracked scope path digest mismatch: expected={baseline['tracked_scope_path_set_sha256']}, "
            f"actual={actual_path_digest}"
        )

    stage0_paths = [
        normalize_repo_path(str(path))
        for path in config["stage0_inventory"]["files"]
    ]
    roadmap_paths = [
        ensure_allowed_roadmap_path(str(item["path"]), config)
        for item in config.get("split_roadmaps", [])
    ]
    candidate_paths = root_candidate_paths(config, tracked_tree)
    controlled_input_paths = [*stage0_paths, *roadmap_paths, *candidate_paths]
    forbidden = {
        normalize_repo_path(str(path)) for path in config.get("forbidden_inputs", [])
    }
    if forbidden.intersection(controlled_input_paths):
        raise ForbiddenInputError("forbidden aggregate roadmap entered the blob allowlist")
    blobs = snapshot_blobs(repo_root, source_head, controlled_input_paths)

    stage0 = load_stage0(blobs, config)
    root_registry, scans = scan_root_corpus(
        blobs, config, stage0, source_head, tracked_tree, namespace
    )
    roadmap_inputs, roadmap_nodes = load_split_roadmaps(blobs, config, namespace)
    crosswalk, crosswalk_records = build_crosswalk(
        config, stage0, scans, roadmap_inputs, roadmap_nodes, namespace, source_head
    )
    conflicts = build_conflicts(
        config, stage0, scans, crosswalk_records, namespace, source_head
    )

    resolutions_document = _read_yaml(resolutions_path or default_resolutions_path(repo_root))
    validate_and_apply_resolutions(
        resolutions_document,
        source_head,
        crosswalk,
        conflicts,
        str(config["resolution_policy"]["required_approver"]),
    )
    # Recompute payload hashes after overlay application.
    crosswalk = attach_payload_sha256(crosswalk)
    conflicts = attach_payload_sha256(conflicts)
    return {
        "ROOT_CORPUS_REGISTRY.json": root_registry,
        "CANONICAL_NODE_CROSSWALK.json": crosswalk,
        "ALIAS_CONFLICT_REGISTRY.json": conflicts,
    }


def write_outputs(outputs: Mapping[str, Mapping[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_NAMES:
        if name not in outputs:
            raise BuildError(f"missing generated output: {name}")
        (output_dir / name).write_bytes(canonical_json_bytes(outputs[name]))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=default_repo_root())
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--resolutions", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        outputs = build_all(
            args.repo_root,
            args.expected_head,
            args.config,
            args.resolutions,
        )
        if args.write:
            write_outputs(outputs, args.output_dir or args.repo_root)
        summary = {
            name: output["summary"]
            for name, output in sorted(outputs.items())
        }
        sys.stdout.buffer.write(canonical_json_bytes(summary))
        return 0
    except (BuildError, IdentityError) as exc:
        print(f"control-plane build failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

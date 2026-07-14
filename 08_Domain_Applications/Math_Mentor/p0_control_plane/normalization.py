"""Read-only normalization for the four observed Math Mentor schema eras.

Normalization copies structural evidence into one stable shape.  It never
repairs source YAML and never turns a source status into mathematical truth,
teaching admission, bridge readiness, or mutation authority.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

import yaml


NORMALIZED_SCHEMA_VERSION = "math_mentor.normalized_node.v1"

_IDENTITY_LOCATORS: tuple[tuple[str, ...], ...] = (
    ("id",),
    ("concept_node", "id"),
    ("concept_node", "v9_1_metadata", "id"),
    ("node_meta", "id"),
    ("node_metadata", "id"),
    ("concept_node", "node", "id"),
    ("concept_node", "node_meta", "id"),
    ("metadata", "id"),
    ("node_id",),
)

_TITLE_LOCATORS: tuple[tuple[str, ...], ...] = (
    ("concept_name",),
    ("title",),
    ("node_name",),
    ("concept_node", "concept_name"),
    ("concept_node", "title"),
    ("concept_node", "node_name"),
    ("concept_node", "v9_1_metadata", "concept_name"),
    ("concept_node", "v9_1_metadata", "title"),
    ("concept_node", "node", "concept_name"),
    ("concept_node", "node", "title"),
    ("concept_node", "node_meta", "concept_name"),
    ("concept_node", "node_meta", "title"),
    ("node_meta", "concept_name"),
    ("node_meta", "title"),
    ("node_metadata", "concept_name"),
    ("node_metadata", "title"),
    ("metadata", "concept_name"),
    ("metadata", "title"),
    ("Concept",),
)

_SUBTOPIC_LOCATORS: tuple[tuple[str, ...], ...] = (
    ("sub_topics",),
    ("concept_node", "sub_topics"),
    ("concept_node", "node", "sub_topics"),
    ("concept_node", "node_meta", "sub_topics"),
    ("node_meta", "sub_topics"),
    ("node_metadata", "sub_topics"),
    ("metadata", "sub_topics"),
)


def _get_in(document: Mapping[str, Any], locator: Sequence[str]) -> Any:
    current: Any = document
    for key in locator:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current


def _first_string(
    document: Mapping[str, Any], locators: Iterable[Sequence[str]]
) -> tuple[str | None, str | None]:
    for locator in locators:
        value = _get_in(document, locator)
        if isinstance(value, str) and value.strip():
            return value.strip(), "/".join(locator)
    return None, None


def _first_list(
    document: Mapping[str, Any], locators: Iterable[Sequence[str]]
) -> tuple[list[Any], str | None]:
    for locator in locators:
        value = _get_in(document, locator)
        if isinstance(value, list):
            return list(value), "/".join(locator)
    return [], None


def _candidate_identity_hits(document: Mapping[str, Any]) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for locator in _IDENTITY_LOCATORS:
        value = _get_in(document, locator)
        if isinstance(value, str) and value.strip():
            hits.append({"locator": "/".join(locator), "value": value.strip()})
    return hits


def detect_schema_era(
    document: Mapping[str, Any],
    path: str,
    *,
    stage0_canonical_paths: Iterable[str] = (),
    changed_since_stage0_paths: Iterable[str] = (),
) -> str:
    """Classify an observed source shape without changing it.

    E3 and E4 are provenance-aware classifications.  They take precedence
    over shape-only rules so repeated runs reproduce the reviewed baseline.
    """

    normalized_path = PurePosixPath(path).as_posix()
    changed = {PurePosixPath(item).as_posix() for item in changed_since_stage0_paths}
    canonical = {PurePosixPath(item).as_posix() for item in stage0_canonical_paths}
    if normalized_path in changed:
        return "E4"
    if normalized_path in canonical:
        return "E3"
    if "concept_node" in document or "id" not in document:
        return "E1"
    return "E2"


def _observed_value(document: Mapping[str, Any], key: str) -> Any:
    if key in document:
        return document[key]
    wrapper = document.get("concept_node")
    if isinstance(wrapper, Mapping) and key in wrapper:
        return wrapper[key]
    return None


def _normalize_lane(document: Mapping[str, Any]) -> tuple[str | None, str | None]:
    raw_lane = _observed_value(document, "math_lane")
    raw_mode = _observed_value(document, "mode")
    if isinstance(raw_lane, str) and raw_lane.strip():
        lane = raw_lane.strip()
    elif isinstance(raw_mode, str):
        lane = {"A": "MathLane_A", "B": "MathLane_B", "mixed": "mixed"}.get(
            raw_mode.strip()
        )
    else:
        lane = None
    return raw_mode.strip() if isinstance(raw_mode, str) else None, lane


def normalize_node(
    document: Mapping[str, Any],
    *,
    path: str,
    source_sha256: str,
    stage0_canonical_paths: Iterable[str] = (),
    changed_since_stage0_paths: Iterable[str] = (),
) -> dict[str, Any]:
    """Return a deterministic structural view of one parsed root candidate."""

    if not isinstance(document, Mapping):
        raise TypeError("node document must be a mapping")

    hits = _candidate_identity_hits(document)
    distinct_ids = sorted({item["value"] for item in hits})
    if len(distinct_ids) == 1:
        identity_status = "resolved"
        strict_id = distinct_ids[0]
        identity_locator = next(item["locator"] for item in hits if item["value"] == strict_id)
    elif not distinct_ids:
        identity_status = "missing"
        strict_id = None
        identity_locator = None
    else:
        identity_status = "conflict"
        strict_id = None
        identity_locator = None

    title, title_locator = _first_string(document, _TITLE_LOCATORS)
    sub_topics, subtopics_locator = _first_list(document, _SUBTOPIC_LOCATORS)
    raw_mode, math_lane = _normalize_lane(document)

    lifecycle_keys = (
        "formal_definition_status",
        "prerequisites_status",
        "mapping_boundary_status",
        "validation_status",
        "teaching_ready",
        "teaching_readiness_status",
        "bridge_readiness_status",
        "coordinator_consumable",
        "independent_teaching_node",
        "disposition",
        "canonical_target_id",
    )
    lifecycle = {key: _observed_value(document, key) for key in lifecycle_keys}

    return {
        "schema_version": NORMALIZED_SCHEMA_VERSION,
        "source": {
            "path": PurePosixPath(path).as_posix(),
            "sha256": source_sha256,
        },
        "schema_era": detect_schema_era(
            document,
            path,
            stage0_canonical_paths=stage0_canonical_paths,
            changed_since_stage0_paths=changed_since_stage0_paths,
        ),
        "parse_status": "parsed",
        "identity": {
            "status": identity_status,
            "strict_id": strict_id,
            "locator": identity_locator,
            "locator_hits": hits,
        },
        "content": {
            "title": title,
            "title_locator": title_locator,
            "sub_topics": sub_topics,
            "subtopics_locator": subtopics_locator,
        },
        "routing": {
            "mode": raw_mode,
            "math_lane": math_lane,
            "mode_routing_status": _observed_value(document, "mode_routing_status"),
        },
        "lifecycle": lifecycle,
        "mathematical_truth_status": "not_evaluated",
        "consumer_allowed": False,
        "evidence_limits": [
            "structural_normalization_only",
            "not_mathematical_validation",
            "not_teaching_admission",
            "not_mutation_authority",
        ],
    }


def parse_and_normalize_node(
    raw: bytes,
    *,
    path: str,
    stage0_canonical_paths: Iterable[str] = (),
    changed_since_stage0_paths: Iterable[str] = (),
) -> dict[str, Any]:
    """Parse one YAML byte string and normalize it without side effects."""

    digest = sha256(raw).hexdigest()
    document = yaml.safe_load(raw.decode("utf-8-sig"))
    return normalize_node(
        document,
        path=path,
        source_sha256=digest,
        stage0_canonical_paths=stage0_canonical_paths,
        changed_since_stage0_paths=changed_since_stage0_paths,
    )

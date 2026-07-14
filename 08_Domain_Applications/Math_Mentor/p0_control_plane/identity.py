"""Deterministic identity primitives for the Math Mentor control plane.

This module deliberately separates artifact identity, local-node identity, and
roadmap identity.  A UUID produced here is a stable name, not proof that two
mathematical concepts are semantically identical.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import PurePosixPath
import re
import unicodedata
import uuid
from typing import Any, Iterable, Mapping, Sequence


STRICT_ID_LOCATORS: tuple[tuple[str, ...], ...] = (
    ("id",),
    ("node_id",),
    ("concept_node", "id"),
    ("node_meta", "id"),
    ("node_metadata", "id"),
    ("metadata", "id"),
    ("concept_node", "node_meta", "id"),
    ("concept_node", "v9_1_metadata", "id"),
    ("concept_node", "node", "id"),
)

SELF_CLAIM_LOCATORS: tuple[tuple[str, ...], ...] = (
    ("concept_name",),
    ("title",),
    ("concept_node", "concept_name"),
    ("concept_node", "title"),
    ("node_meta", "concept_name"),
    ("node_meta", "title"),
    ("node_metadata", "concept_name"),
    ("node_metadata", "title"),
    ("metadata", "concept_name"),
    ("metadata", "title"),
)

ROADMAP_ALIAS_RE = re.compile(r"\(n_(\d+)\)")
FULLWIDTH_ROADMAP_ALIAS_RE = re.compile(r"（n_(\d+)）")
ROADMAP_ID_RE = re.compile(r"n_([1-9]\d*|0)$")


class IdentityError(ValueError):
    """Raised when deterministic identity input is malformed."""


@dataclass(frozen=True)
class IdentityHit:
    locator: str
    value: str

    def as_dict(self) -> dict[str, str]:
        return {"locator": self.locator, "value": self.value}


@dataclass(frozen=True)
class StrictIdentity:
    status: str
    value: str | None
    locator: str | None
    hits: tuple[IdentityHit, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "value": self.value,
            "locator": self.locator,
            "locator_hits": [hit.as_dict() for hit in self.hits],
        }


@dataclass(frozen=True)
class AliasClaim:
    roadmap_id: str
    locator: str

    def as_dict(self) -> dict[str, str]:
        return {"roadmap_id": self.roadmap_id, "locator": self.locator}


def _lookup(document: Mapping[str, Any], locator: Sequence[str]) -> Any:
    current: Any = document
    for component in locator:
        if not isinstance(current, Mapping) or component not in current:
            return None
        current = current[component]
    return current


def locator_text(locator: Sequence[str]) -> str:
    return ".".join(locator)


def normalize_repo_path(path: str) -> str:
    """Return a canonical, repo-relative, NFC-normalized POSIX path."""

    normalized = unicodedata.normalize("NFC", path.replace("\\", "/"))
    if re.match(r"^[A-Za-z]:/", normalized):
        raise IdentityError(f"absolute Windows path is forbidden: {path!r}")
    candidate = PurePosixPath(normalized)
    if candidate.is_absolute():
        raise IdentityError(f"absolute path is forbidden: {path!r}")
    if not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise IdentityError(f"non-canonical repo path: {path!r}")
    rendered = candidate.as_posix()
    if rendered != normalized:
        raise IdentityError(f"path normalization changed structure: {path!r}")
    return rendered


def strict_identity(document: Mapping[str, Any]) -> StrictIdentity:
    hits: list[IdentityHit] = []
    for locator in STRICT_ID_LOCATORS:
        value = _lookup(document, locator)
        if value is None or value == "":
            continue
        if not isinstance(value, (str, int)):
            raise IdentityError(
                f"identity at {locator_text(locator)} must be a scalar, got {type(value).__name__}"
            )
        hits.append(IdentityHit(locator_text(locator), str(value)))

    if not hits:
        return StrictIdentity("missing", None, None, ())

    distinct = sorted({hit.value for hit in hits})
    if len(distinct) != 1:
        return StrictIdentity("conflicting", None, None, tuple(hits))

    status = "resolved" if len(hits) == 1 else "resolved_redundant"
    return StrictIdentity(status, distinct[0], hits[0].locator, tuple(hits))


def self_alias_claims(document: Mapping[str, Any]) -> tuple[AliasClaim, ...]:
    """Extract only explicit self-description roadmap tags.

    Filename suffixes, basenames, fuzzy title matching, prerequisite fields,
    and staging files are intentionally outside this function.
    """

    claims: set[tuple[int, str]] = set()
    for locator in SELF_CLAIM_LOCATORS:
        value = _lookup(document, locator)
        if not isinstance(value, str):
            continue
        for raw_number in ROADMAP_ALIAS_RE.findall(value):
            number = int(raw_number)
            if number < 1:
                raise IdentityError(f"roadmap identity must be positive: n_{number}")
            claims.add((number, locator_text(locator)))

    return tuple(
        AliasClaim(roadmap_id(number), locator)
        for number, locator in sorted(claims, key=lambda item: (item[0], item[1]))
    )


def unparsed_fullwidth_alias_claims(
    document: Mapping[str, Any],
) -> tuple[AliasClaim, ...]:
    """Inventory fullwidth roadmap tags without promoting them to aliases.

    The frozen independent-review extraction recognizes only ASCII ``(n_*)``.
    Fullwidth ``（n_*）`` evidence is therefore explicit diagnostic evidence,
    remains unbound, and may not create a candidate edge.
    """

    claims: set[tuple[int, str]] = set()
    for locator in SELF_CLAIM_LOCATORS:
        value = _lookup(document, locator)
        if not isinstance(value, str):
            continue
        for raw_number in FULLWIDTH_ROADMAP_ALIAS_RE.findall(value):
            number = int(raw_number)
            if number < 1:
                raise IdentityError(f"roadmap identity must be positive: n_{number}")
            claims.add((number, locator_text(locator)))
    return tuple(
        AliasClaim(roadmap_id(number), locator)
        for number, locator in sorted(claims, key=lambda item: (item[0], item[1]))
    )


def distinct_claim_ids(claims: Iterable[AliasClaim]) -> tuple[str, ...]:
    return tuple(sorted({claim.roadmap_id for claim in claims}, key=roadmap_number))


def roadmap_id(number: int) -> str:
    if number < 1:
        raise IdentityError(f"roadmap identity must be positive: {number}")
    return f"n_{number}"


def roadmap_number(value: str) -> int:
    match = ROADMAP_ID_RE.fullmatch(value)
    if not match:
        raise IdentityError(f"invalid roadmap identity: {value!r}")
    number = int(match.group(1))
    if number < 1:
        raise IdentityError(f"roadmap identity must be positive: {value!r}")
    return number


def namespace_uuid(namespace_name: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_URL, namespace_name)


def _named_uuid(namespace: uuid.UUID, kind: str, value: str) -> str:
    return str(uuid.uuid5(namespace, f"{kind}|v1|{value}"))


def artifact_uuid(namespace: uuid.UUID, repo_path: str) -> str:
    return _named_uuid(namespace, "asset", normalize_repo_path(repo_path))


def canonical_node_uuid(namespace: uuid.UUID, bootstrap_root_path: str) -> str:
    """Create a canonical node UUID during the one-time bootstrap.

    The exact root path is only the deterministic bootstrap seed.  Once the
    external crosswalk is materialized, this UUID is the sole primary identity
    and must be preserved through reviewed alias/path migrations rather than
    recomputed from a domain ID, roadmap ID, suffix, or fuzzy match.
    """

    return _named_uuid(namespace, "canonical-node", normalize_repo_path(bootstrap_root_path))


def roadmap_node_uuid(namespace: uuid.UUID, value: str) -> str:
    return _named_uuid(namespace, "roadmap-node", roadmap_id(roadmap_number(value)))


def edge_uuid(namespace: uuid.UUID, node_uuid: str, roadmap_uuid: str) -> str:
    return _named_uuid(namespace, "edge", f"{node_uuid}|{roadmap_uuid}")


def conflict_uuid(namespace: uuid.UUID, conflict_type: str, subject_uuids: Iterable[str]) -> str:
    subjects = sorted(set(subject_uuids))
    if not subjects:
        raise IdentityError("a conflict must have at least one subject")
    return _named_uuid(namespace, "conflict", f"{conflict_type}|{'|'.join(subjects)}")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(unicodedata.normalize("NFC", value).encode("utf-8"))


def path_set_sha256(paths: Iterable[str]) -> str:
    canonical = sorted(normalize_repo_path(path) for path in paths)
    return sha256_bytes(("\n".join(canonical) + "\n").encode("utf-8"))


def canonical_json_bytes(value: Any) -> bytes:
    """Canonical JSON for this integer/string/bool/null-only data model."""

    rendered = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return (rendered + "\n").encode("utf-8")


def attach_payload_sha256(value: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(value)
    payload.pop("payload_sha256", None)
    payload["payload_sha256"] = sha256_bytes(canonical_json_bytes(payload))
    return payload

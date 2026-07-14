"""Pure, fail-closed admission evaluation for Math Mentor assets.

Admission answers whether an exact asset/blob has enough evidence for one
read-only use.  It does not grant authorization, promote readiness, map legacy
review claims into current learning status, or write any repository/runtime
state.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, fields
from hashlib import sha256
import json
from pathlib import PurePosixPath
import re
from types import MappingProxyType
from typing import Any
from weakref import WeakKeyDictionary

from .admission_evidence import (
    TrustedAdmissionEvidence,
    is_verified_admission_evidence,
)
from .authorization import is_verified_authorization_decision


ADM_OK = "ADM_OK"
ADM_REQUEST_UNTRUSTED = "ADM_REQUEST_UNTRUSTED"
ADM_READ_ONLY_LIMIT = "ADM_READ_ONLY_LIMIT"
ADM_TEASER_LIMIT = "ADM_TEASER_LIMIT"
ADM_LEGACY_IMPORT_ONLY = "ADM_LEGACY_IMPORT_ONLY"
ADM_AUTH_DENIED = "ADM_AUTH_DENIED"
ADM_AUTH_HUMAN_REQUIRED = "ADM_AUTH_HUMAN_REQUIRED"
ADM_AUTH_SCOPE_MISMATCH = "ADM_AUTH_SCOPE_MISMATCH"
ADM_IDENTITY_MISSING = "ADM_IDENTITY_MISSING"
ADM_IDENTITY_AMBIGUOUS = "ADM_IDENTITY_AMBIGUOUS"
ADM_IDENTITY_CONFLICT = "ADM_IDENTITY_CONFLICT"
ADM_IDENTITY_CROSSWALK_INVALID = "ADM_IDENTITY_CROSSWALK_INVALID"
ADM_SCHEMA_MISSING = "ADM_SCHEMA_MISSING"
ADM_SCHEMA_INVALID = "ADM_SCHEMA_INVALID"
ADM_SCHEMA_UNSUPPORTED = "ADM_SCHEMA_UNSUPPORTED"
ADM_NON_CANONICAL_ASSET = "ADM_NON_CANONICAL_ASSET"
ADM_BRIDGE_ADMISSION_NOT_IMPLEMENTED = "ADM_BRIDGE_ADMISSION_NOT_IMPLEMENTED"
ADM_STAGING_ASSET = "ADM_STAGING_ASSET"
ADM_STRUCTURAL_ONLY_ASSET = "ADM_STRUCTURAL_ONLY_ASSET"
ADM_READINESS_MISSING = "ADM_READINESS_MISSING"
ADM_NOT_READY = "ADM_NOT_READY"
ADM_REVIEW_REQUIRED = "ADM_REVIEW_REQUIRED"
ADM_MANUAL_REVIEW_REQUIRED = "ADM_MANUAL_REVIEW_REQUIRED"
ADM_VALIDATOR_MISSING = "ADM_VALIDATOR_MISSING"
ADM_VALIDATOR_REJECTED = "ADM_VALIDATOR_REJECTED"
ADM_EVIDENCE_MISSING = "ADM_EVIDENCE_MISSING"
ADM_EVIDENCE_STALE = "ADM_EVIDENCE_STALE"
ADM_TRUSTED_EVIDENCE_MISSING = "ADM_TRUSTED_EVIDENCE_MISSING"
ADM_TRUSTED_EVIDENCE_UNTRUSTED = "ADM_TRUSTED_EVIDENCE_UNTRUSTED"
ADM_EVIDENCE_FIXTURE_IN_PRODUCTION = "ADM_EVIDENCE_FIXTURE_IN_PRODUCTION"
ADM_EVIDENCE_REPO_MISMATCH = "ADM_EVIDENCE_REPO_MISMATCH"
ADM_EVIDENCE_PAYLOAD_HASH_MISMATCH = "ADM_EVIDENCE_PAYLOAD_HASH_MISMATCH"
ADM_EVIDENCE_SOURCE_HEAD_MISMATCH = "ADM_EVIDENCE_SOURCE_HEAD_MISMATCH"
ADM_EVIDENCE_PATH_MISMATCH = "ADM_EVIDENCE_PATH_MISMATCH"
ADM_EVIDENCE_BLOB_MISMATCH = "ADM_EVIDENCE_BLOB_MISMATCH"
ADM_EVIDENCE_CROSSWALK_MISMATCH = "ADM_EVIDENCE_CROSSWALK_MISMATCH"
ADM_EVIDENCE_SCHEMA_VERSION_MISMATCH = "ADM_EVIDENCE_SCHEMA_VERSION_MISMATCH"
ADM_EVIDENCE_VALIDATOR_BLOB_MISMATCH = "ADM_EVIDENCE_VALIDATOR_BLOB_MISMATCH"
ADM_EVIDENCE_PREREQUISITE_MISMATCH = "ADM_EVIDENCE_PREREQUISITE_MISMATCH"
ADM_EVIDENCE_CLASS_MISMATCH = "ADM_EVIDENCE_CLASS_MISMATCH"
ADM_BLOB_MISMATCH = "ADM_BLOB_MISMATCH"
ADM_PREREQUISITE_UNRESOLVED = "ADM_PREREQUISITE_UNRESOLVED"
ADM_REQUESTED_USE_FORBIDDEN = "ADM_REQUESTED_USE_FORBIDDEN"
ADM_STATE_WRITE_FORBIDDEN = "ADM_STATE_WRITE_FORBIDDEN"
ADM_LEGACY_EXECUTION_FORBIDDEN = "ADM_LEGACY_EXECUTION_FORBIDDEN"
ADM_LEGACY_STATUS_NOT_CANONICAL = "ADM_LEGACY_STATUS_NOT_CANONICAL"
ADM_DUPLICATE_SOURCE = "ADM_DUPLICATE_SOURCE"


REQUESTED_USES = frozenset(
    {
        "manual_teaching_read_only",
        "teaser_read_only",
        "lesson_planning_read_only",
        "review_generation_read_only",
        "legacy_import_read_only",
    }
)
ASSET_ROLES = frozenset(
    {
        "canonical_node",
        "canonical_bridge",
        "staging_node",
        "structural_asset",
        "legacy_state_table",
        "legacy_prompt",
        "legacy_orchestrator",
        "legacy_template",
    }
)
IDENTITY_STATUSES = frozenset(
    {"resolved", "missing", "ambiguous", "conflict", "not_applicable"}
)
SCHEMA_STATUSES = frozenset(
    {"valid", "invalid", "unsupported", "missing", "not_applicable"}
)
READINESS_STATUSES = frozenset(
    {
        "ready",
        "review_required",
        "manual_review_required",
        "not_ready",
        "blocked",
        "missing",
        "not_applicable",
    }
)
VALIDATOR_STATUSES = frozenset(
    {"accepted", "rejected", "missing", "not_applicable"}
)
PROVENANCE_STATUSES = frozenset({"exact_blob_verified", "stale", "missing"})
PREREQUISITE_STATUSES = frozenset({"resolved", "unresolved", "not_required"})
SCHEMA_ERAS = frozenset({"E1", "E2", "E3", "E4", "legacy", "unknown"})
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_UUIDV5_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_REQUEST_SEAL = object()
_ISSUED_REQUESTS = WeakKeyDictionary()
_PURE_DB_PREFIX = (
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/"
)
_LEGACY_PROMPT_PREFIX = "08_Domain_Applications/Math_Mentor/复习巩固期prompt/"
_LEGACY_STATE_PATHS = frozenset(
    {
        "08_Domain_Applications/Math_Mentor/数学间隔重复调度表.md",
        "08_Domain_Applications/Math_Mentor/拖延知识点清单.md",
        "08_Domain_Applications/Math_Mentor/已毕业知识点.md",
    }
)
_LEGACY_ORCHESTRATOR_PATHS = frozenset(
    {
        "08_Domain_Applications/Math_Mentor/复习巩固期总调度prompt.md",
        "08_Domain_Applications/Math_Mentor/复习执行协议.md",
    }
)
_LEGACY_TEMPLATE_PATH = (
    "08_Domain_Applications/Math_Mentor/数学间隔重复调度表(通用模板).md"
)


class AdmissionInputError(ValueError):
    pass


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AdmissionInputError(f"{name} must be an object")
    return value


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdmissionInputError(f"{name} must be a non-empty string")
    return value


def _nullable_string(value: Any, name: str) -> str | None:
    if value is None:
        return None
    return _string(value, name)


def _enum(value: Any, allowed: frozenset[str], name: str) -> str:
    if value not in allowed:
        raise AdmissionInputError(f"unsupported {name}: {value!r}")
    return value


def _sha1(value: Any, name: str) -> str:
    value = _string(value, name)
    if not _SHA1_RE.fullmatch(value):
        raise AdmissionInputError(f"{name} must be a 40 character Git SHA")
    return value


def _sha256(value: Any, name: str) -> str:
    value = _string(value, name)
    if not _SHA256_RE.fullmatch(value):
        raise AdmissionInputError(f"{name} must be a 64 character SHA-256")
    return value


def _payload_sha256(value: Mapping[str, Any]) -> str:
    try:
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise AdmissionInputError("admission request must be canonical JSON data") from exc
    return sha256((rendered + "\n").encode("utf-8")).hexdigest()


def _path(value: Any, name: str) -> str:
    value = _string(value, name)
    if "\\" in value or value.startswith("/") or value.endswith("/"):
        raise AdmissionInputError(f"{name} must be a normalized repository path")
    pure = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in pure.parts) or str(pure) != value:
        raise AdmissionInputError(f"{name} must be a normalized repository path")
    return value


def _uuidv5(value: Any, name: str) -> str:
    value = _string(value, name)
    if not _UUIDV5_RE.fullmatch(value):
        raise AdmissionInputError(f"{name} must be a lowercase RFC 4122 UUIDv5")
    return value


def _is_staging_path(path: str) -> bool:
    return any(part.startswith("_Staging_") for part in PurePosixPath(path).parts)


def _derived_legacy_role(path: str) -> str | None:
    if path in _LEGACY_STATE_PATHS:
        return "legacy_state_table"
    if path in _LEGACY_ORCHESTRATOR_PATHS:
        return "legacy_orchestrator"
    if path == _LEGACY_TEMPLATE_PATH:
        return "legacy_template"
    if path.startswith(_LEGACY_PROMPT_PREFIX):
        return "legacy_prompt"
    return None


def _canonical_node_path_allowed(path: str) -> bool:
    if not path.startswith(_PURE_DB_PREFIX):
        return False
    relative = path[len(_PURE_DB_PREFIX) :]
    if "/" in relative or not relative.endswith(".yaml"):
        return False
    lowered = relative.lower()
    if lowered == "schema.yaml" or lowered.startswith("bridge-"):
        return False
    return True


@dataclass(frozen=True, eq=False)
class AdmissionRequest:
    schema_version: str
    request_payload_sha256: str
    request_id: str
    requested_use: str
    repo_id: str
    source_head: str
    path: str
    blob_oid: str
    asset_role: str
    schema_era: str
    identity_status: str
    canonical_node_id: str | None
    identity_registry_ref: str | None
    identity_registry_source_head: str | None
    identity_registry_blob_oid: str | None
    identity_crosswalk_payload_sha256: str | None
    crosswalk_canonical_path: str | None
    crosswalk_canonical_blob_oid: str | None
    schema_status: str
    normalized_schema_version: str | None
    readiness_status: str
    validator_status: str
    validator_ref: str | None
    validated_blob_oid: str | None
    provenance_status: str
    prerequisite_status: str
    prerequisite_evidence_ref: str
    prerequisite_evidence_sha256: str
    legacy_stage: str | None
    legacy_status: str | None
    requested_canonical_status: str | None
    state_write_requested: bool
    duplicate_source: bool
    evidence_refs: tuple[str, ...]
    _seal: object = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._seal is not _REQUEST_SEAL:
            raise AdmissionInputError(
                "AdmissionRequest must be created by from_mapping"
            )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AdmissionRequest":
        request_payload_sha256 = _payload_sha256(value)
        if value.get("schema_version") != "math_mentor.admission_request.v1":
            raise AdmissionInputError("unsupported admission request schema")
        asset = _mapping(value.get("asset"), "asset")
        identity = _mapping(value.get("identity_evidence"), "identity_evidence")
        schema = _mapping(value.get("schema_evidence"), "schema_evidence")
        readiness = _mapping(value.get("readiness_evidence"), "readiness_evidence")
        provenance = _mapping(
            value.get("provenance_evidence"), "provenance_evidence"
        )
        prerequisites = _mapping(
            value.get("prerequisite_evidence"), "prerequisite_evidence"
        )
        legacy = _mapping(value.get("legacy_claim", {}), "legacy_claim")

        raw_refs = value.get("evidence_refs", [])
        if not isinstance(raw_refs, Sequence) or isinstance(raw_refs, (str, bytes)):
            raise AdmissionInputError("evidence_refs must be an array")
        evidence_refs = tuple(_string(item, "evidence_refs item") for item in raw_refs)

        validated_blob_oid = readiness.get("validated_blob_oid")
        if validated_blob_oid is not None:
            validated_blob_oid = _sha1(
                validated_blob_oid, "readiness_evidence.validated_blob_oid"
            )
        schema_era = _enum(asset.get("schema_era"), SCHEMA_ERAS, "schema era")
        identity_status = _enum(
            identity.get("status"), IDENTITY_STATUSES, "identity status"
        )
        if identity_status == "resolved":
            canonical_node_id = _uuidv5(
                identity.get("canonical_node_id"), "identity canonical_node_id"
            )
            registry_source_head = _sha1(
                identity.get("registry_source_head"), "identity registry_source_head"
            )
            registry_blob_oid = _sha1(
                identity.get("registry_blob_oid"), "identity registry_blob_oid"
            )
            crosswalk_payload_sha256 = _sha256(
                identity.get("crosswalk_payload_sha256"),
                "identity crosswalk_payload_sha256",
            )
            canonical_path = _path(
                identity.get("canonical_path"), "identity canonical_path"
            )
            canonical_blob_oid = _sha1(
                identity.get("canonical_blob_oid"), "identity canonical_blob_oid"
            )
            registry_ref = _string(identity.get("registry_ref"), "identity registry_ref")
            expected_ref = (
                f"canonical-crosswalk:{registry_source_head}:{registry_blob_oid}"
            )
            if registry_ref != expected_ref:
                raise AdmissionInputError(
                    "identity registry_ref is not bound to its source head and blob"
                )
        else:
            canonical_node_id = _nullable_string(
                identity.get("canonical_node_id"), "identity canonical_node_id"
            )
            registry_ref = _nullable_string(
                identity.get("registry_ref"), "identity registry_ref"
            )
            registry_source_head = None
            registry_blob_oid = None
            crosswalk_payload_sha256 = None
            canonical_path = None
            canonical_blob_oid = None
        prerequisite_status = _enum(
            prerequisites.get("status"),
            PREREQUISITE_STATUSES,
            "prerequisite status",
        )
        prerequisite_evidence_ref = _string(
            prerequisites.get("evidence_ref"), "prerequisite evidence_ref"
        )
        prerequisite_evidence_sha256 = _sha256(
            prerequisites.get("evidence_sha256"),
            "prerequisite evidence_sha256",
        )
        request = cls(
            schema_version="math_mentor.admission_request.v1",
            request_payload_sha256=request_payload_sha256,
            request_id=_string(value.get("request_id"), "request_id"),
            requested_use=_enum(
                value.get("requested_use"), REQUESTED_USES, "requested use"
            ),
            repo_id=_string(asset.get("repo_id"), "asset.repo_id"),
            source_head=_sha1(asset.get("source_head"), "asset.source_head"),
            path=_path(asset.get("path"), "asset.path"),
            blob_oid=_sha1(asset.get("blob_oid"), "asset.blob_oid"),
            asset_role=_enum(asset.get("asset_role"), ASSET_ROLES, "asset role"),
            schema_era=schema_era,
            identity_status=identity_status,
            canonical_node_id=canonical_node_id,
            identity_registry_ref=registry_ref,
            identity_registry_source_head=registry_source_head,
            identity_registry_blob_oid=registry_blob_oid,
            identity_crosswalk_payload_sha256=crosswalk_payload_sha256,
            crosswalk_canonical_path=canonical_path,
            crosswalk_canonical_blob_oid=canonical_blob_oid,
            schema_status=_enum(
                schema.get("status"), SCHEMA_STATUSES, "schema status"
            ),
            normalized_schema_version=_nullable_string(
                schema.get("normalized_schema_version"),
                "normalized_schema_version",
            ),
            readiness_status=_enum(
                readiness.get("source_status"),
                READINESS_STATUSES,
                "readiness status",
            ),
            validator_status=_enum(
                readiness.get("validator_status"),
                VALIDATOR_STATUSES,
                "validator status",
            ),
            validator_ref=_nullable_string(
                readiness.get("validator_ref"), "validator_ref"
            ),
            validated_blob_oid=validated_blob_oid,
            provenance_status=_enum(
                provenance.get("status"),
                PROVENANCE_STATUSES,
                "provenance status",
            ),
            prerequisite_status=prerequisite_status,
            prerequisite_evidence_ref=prerequisite_evidence_ref,
            prerequisite_evidence_sha256=prerequisite_evidence_sha256,
            legacy_stage=_nullable_string(legacy.get("legacy_stage"), "legacy_stage"),
            legacy_status=_nullable_string(
                legacy.get("legacy_status"), "legacy_status"
            ),
            requested_canonical_status=_nullable_string(
                legacy.get("requested_canonical_status"),
                "requested_canonical_status",
            ),
            state_write_requested=bool(value.get("state_write_requested", False)),
            duplicate_source=bool(value.get("duplicate_source", False)),
            evidence_refs=evidence_refs,
            _seal=_REQUEST_SEAL,
        )
        _ISSUED_REQUESTS[request] = _request_fingerprint(request)
        return request


def _request_fingerprint(value: AdmissionRequest) -> tuple[Any, ...]:
    """Capture every parsed field so post-issuance mutation invalidates it."""

    return tuple(getattr(value, item.name) for item in fields(value))


def is_parsed_admission_request(value: Any) -> bool:
    return (
        type(value) is AdmissionRequest
        and value._seal is _REQUEST_SEAL
        and _ISSUED_REQUESTS.get(value) == _request_fingerprint(value)
    )


@dataclass(frozen=True)
class AdmissionDecision:
    status: str
    effective_use: str
    reason_codes: tuple[str, ...]
    dimensions: Mapping[str, str]
    evidence_refs: tuple[str, ...]
    restrictions: Mapping[str, bool]
    canonical_learning_status: None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "dimensions", MappingProxyType(dict(self.dimensions))
        )
        object.__setattr__(
            self, "restrictions", MappingProxyType(dict(self.restrictions))
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "effective_use": self.effective_use,
            "reason_codes": list(self.reason_codes),
            "dimensions": dict(self.dimensions),
            "evidence_refs": list(self.evidence_refs),
            "restrictions": dict(self.restrictions),
            "canonical_learning_status": None,
        }


def _authorization_parts(
    value: Any, request: AdmissionRequest
) -> tuple[str, Any]:
    # Serialized dictionaries and duck-typed objects are deliberately rejected.
    # Rehydrating a trusted decision is a future host-boundary concern, not a
    # capability of this P0 module.
    if not is_verified_authorization_decision(value):
        return "indeterminate", None
    if value.status != "allow":
        return value.status, value.authorization_context
    context = value.authorization_context
    if not isinstance(context, Mapping):
        return "scope_mismatch", None
    binding = context.get("binding")
    if not isinstance(binding, Mapping):
        return "scope_mismatch", None
    if (
        binding.get("source_head") != request.source_head
        or binding.get("operation") != "repository.read"
        or binding.get("effect_class") != "read_only"
    ):
        return "scope_mismatch", None
    resources = binding.get("resources")
    if not isinstance(resources, Sequence) or isinstance(resources, (str, bytes)):
        return "scope_mismatch", None
    exact_asset_bound = any(
        isinstance(resource, Mapping)
        and resource.get("repo_id") == request.repo_id
        and resource.get("path") == request.path
        and resource.get("match") == "exact"
        for resource in resources
    )
    if not exact_asset_bound:
        return "scope_mismatch", None
    return "allow", context


def _dimensions(
    request: AdmissionRequest,
    auth_status: str,
    evidence: TrustedAdmissionEvidence | None = None,
) -> dict[str, str]:
    if evidence is None:
        return {
            "authorization": auth_status,
            "identity": "untrusted",
            "schema": "untrusted",
            "readiness": "untrusted",
            "provenance": "untrusted",
            "prerequisites": "untrusted",
        }
    return {
        "authorization": auth_status,
        "identity": evidence.identity_status,
        "schema": evidence.schema_status,
        "readiness": evidence.readiness_status,
        "provenance": evidence.provenance_status,
        "prerequisites": evidence.prerequisite_status,
    }


def _decision(
    request: AdmissionRequest,
    auth_status: str,
    status: str,
    reason_codes: Sequence[str],
    *,
    effective_use: str = "none",
    evidence: TrustedAdmissionEvidence | None = None,
) -> AdmissionDecision:
    evidence_refs = (
        (f"{evidence.provider_ref}#{evidence.evidence_id}",)
        if evidence is not None
        else ()
    )
    return AdmissionDecision(
        status=status,
        effective_use=effective_use,
        reason_codes=tuple(reason_codes),
        dimensions=_dimensions(request, auth_status, evidence),
        evidence_refs=evidence_refs,
        restrictions={
            "read_only": True,
            "state_write_allowed": False,
            "scheduler_write_allowed": False,
            "runtime_activation_allowed": False,
            "coordinator_activation_allowed": False,
            "consumer_allowed": False,
        },
    )


def _evidence_binding_codes(
    request: AdmissionRequest,
    value: Any,
    *,
    environment_mode: str,
) -> tuple[TrustedAdmissionEvidence | None, list[str]]:
    if value is None:
        return None, [ADM_TRUSTED_EVIDENCE_MISSING]
    if not is_verified_admission_evidence(value):
        return None, [ADM_TRUSTED_EVIDENCE_UNTRUSTED]
    evidence = value
    if environment_mode not in {"production", "test"}:
        return evidence, [ADM_TRUSTED_EVIDENCE_UNTRUSTED]
    if evidence.trust_source == "test_fixture" and environment_mode != "test":
        return evidence, [ADM_EVIDENCE_FIXTURE_IN_PRODUCTION]

    codes: list[str] = []
    if (
        evidence.admission_request_payload_sha256
        != request.request_payload_sha256
    ):
        codes.append(ADM_EVIDENCE_PAYLOAD_HASH_MISMATCH)
    if evidence.admission_request_schema_version != request.schema_version:
        codes.append(ADM_EVIDENCE_SCHEMA_VERSION_MISMATCH)
    if evidence.repo_id != request.repo_id:
        codes.append(ADM_EVIDENCE_REPO_MISMATCH)
    if evidence.source_head != request.source_head:
        codes.append(ADM_EVIDENCE_SOURCE_HEAD_MISMATCH)
    if evidence.path != request.path:
        codes.append(ADM_EVIDENCE_PATH_MISMATCH)
    if evidence.blob_oid != request.blob_oid:
        codes.append(ADM_EVIDENCE_BLOB_MISMATCH)

    expected_class = (
        "legacy_state_table"
        if request.asset_role == "legacy_state_table"
        else "canonical_node"
    )
    if evidence.evidence_class != expected_class or evidence.asset_role != expected_class:
        codes.append(ADM_EVIDENCE_CLASS_MISMATCH)
    if evidence.schema_era != request.schema_era:
        codes.append(ADM_EVIDENCE_SCHEMA_VERSION_MISMATCH)

    if expected_class == "canonical_node":
        if (
            evidence.canonical_node_id != request.canonical_node_id
            or evidence.crosswalk_source_head
            != request.identity_registry_source_head
            or evidence.crosswalk_blob_oid != request.identity_registry_blob_oid
            or evidence.crosswalk_payload_sha256
            != request.identity_crosswalk_payload_sha256
        ):
            codes.append(ADM_EVIDENCE_CROSSWALK_MISMATCH)
        if evidence.normalized_schema_version != request.normalized_schema_version:
            codes.append(ADM_EVIDENCE_SCHEMA_VERSION_MISMATCH)
        if (
            evidence.validator_ref != request.validator_ref
            or evidence.validated_blob_oid != request.validated_blob_oid
            or evidence.validated_blob_oid != request.blob_oid
        ):
            codes.append(ADM_EVIDENCE_VALIDATOR_BLOB_MISMATCH)

    if (
        evidence.prerequisite_status != request.prerequisite_status
        or evidence.prerequisite_evidence_ref
        != request.prerequisite_evidence_ref
        or evidence.prerequisite_evidence_sha256
        != request.prerequisite_evidence_sha256
    ):
        codes.append(ADM_EVIDENCE_PREREQUISITE_MISMATCH)
    return evidence, list(dict.fromkeys(codes))


def evaluate_admission(
    request: AdmissionRequest,
    authorization_decision: Any,
    admission_evidence: Any = None,
    *,
    environment_mode: str = "production",
) -> AdmissionDecision:
    """Evaluate two independent gates without I/O or state mutation.

    Authorization grants the exact read effect.  Admission evidence establishes
    externally attested asset/readiness facts.  Neither can substitute for the
    other, and no field on ``request`` is treated as trusted evidence.

    ``environment_mode`` is a trusted host/test-composition input, not a field
    accepted from the model-generated request.  Production composition must
    retain the default and cannot use deterministic test evidence.
    """

    if not is_parsed_admission_request(request):
        return _decision(
            request,
            "indeterminate",
            "blocked",
            [ADM_REQUEST_UNTRUSTED],
        )

    auth_status, auth_context = _authorization_parts(authorization_decision, request)
    if auth_status == "deny":
        return _decision(request, auth_status, "blocked", [ADM_AUTH_DENIED])
    if auth_status == "scope_mismatch":
        return _decision(
            request, auth_status, "blocked", [ADM_AUTH_SCOPE_MISMATCH]
        )
    if auth_status != "allow" or not auth_context:
        return _decision(
            request, auth_status, "blocked", [ADM_AUTH_HUMAN_REQUIRED]
        )
    if request.state_write_requested:
        return _decision(
            request, auth_status, "blocked", [ADM_STATE_WRITE_FORBIDDEN]
        )

    # Safe path/role denials do not require trusting any caller readiness claim.
    if _is_staging_path(request.path):
        return _decision(request, auth_status, "quarantined", [ADM_STAGING_ASSET])
    derived_legacy_role = _derived_legacy_role(request.path)
    if derived_legacy_role is not None and request.asset_role != derived_legacy_role:
        codes = [ADM_NON_CANONICAL_ASSET]
        codes.append(
            ADM_LEGACY_EXECUTION_FORBIDDEN
            if derived_legacy_role != "legacy_state_table"
            else ADM_REQUESTED_USE_FORBIDDEN
        )
        return _decision(request, auth_status, "blocked", codes)
    if request.asset_role == "canonical_node" and not _canonical_node_path_allowed(
        request.path
    ):
        code = (
            ADM_STRUCTURAL_ONLY_ASSET
            if PurePosixPath(request.path).name.lower() == "schema.yaml"
            else ADM_NON_CANONICAL_ASSET
        )
        return _decision(request, auth_status, "blocked", [code])
    if request.asset_role == "canonical_bridge":
        return _decision(
            request,
            auth_status,
            "blocked",
            [ADM_BRIDGE_ADMISSION_NOT_IMPLEMENTED, ADM_NON_CANONICAL_ASSET],
        )
    if (
        request.asset_role == "legacy_state_table"
        and request.path not in _LEGACY_STATE_PATHS
    ):
        return _decision(request, auth_status, "blocked", [ADM_NON_CANONICAL_ASSET])
    if request.asset_role in {
        "legacy_prompt",
        "legacy_orchestrator",
        "legacy_template",
    }:
        codes = [ADM_LEGACY_EXECUTION_FORBIDDEN]
        if request.duplicate_source:
            codes.append(ADM_DUPLICATE_SOURCE)
        return _decision(request, auth_status, "blocked", codes)
    if request.asset_role == "staging_node":
        return _decision(request, auth_status, "quarantined", [ADM_STAGING_ASSET])
    if request.asset_role == "structural_asset":
        return _decision(
            request, auth_status, "blocked", [ADM_STRUCTURAL_ONLY_ASSET]
        )
    if request.asset_role not in {"canonical_node", "legacy_state_table"}:
        return _decision(request, auth_status, "blocked", [ADM_NON_CANONICAL_ASSET])

    evidence, evidence_codes = _evidence_binding_codes(
        request, admission_evidence, environment_mode=environment_mode
    )
    if evidence_codes:
        return _decision(
            request,
            auth_status,
            "blocked",
            evidence_codes,
            evidence=evidence,
        )
    assert evidence is not None  # established by _evidence_binding_codes

    def decide(
        status: str,
        codes: Sequence[str],
        *,
        effective_use: str = "none",
    ) -> AdmissionDecision:
        return _decision(
            request,
            auth_status,
            status,
            codes,
            effective_use=effective_use,
            evidence=evidence,
        )

    if evidence.provenance_status == "missing":
        return decide("blocked", [ADM_EVIDENCE_MISSING])
    if evidence.provenance_status == "stale":
        return decide("blocked", [ADM_EVIDENCE_STALE])

    if request.asset_role == "legacy_state_table":
        if request.requested_use != "legacy_import_read_only":
            return decide(
                "blocked", [ADM_NON_CANONICAL_ASSET, ADM_REQUESTED_USE_FORBIDDEN]
            )
        if request.requested_canonical_status is not None:
            return decide("blocked", [ADM_LEGACY_STATUS_NOT_CANONICAL])
        return decide(
            "admitted_legacy_import_read_only",
            [ADM_LEGACY_IMPORT_ONLY, ADM_READ_ONLY_LIMIT],
            effective_use="legacy_import_read_only",
        )

    if request.requested_use == "legacy_import_read_only":
        return decide("blocked", [ADM_REQUESTED_USE_FORBIDDEN])
    if evidence.identity_status == "conflict":
        return decide("quarantined", [ADM_IDENTITY_CONFLICT])
    if evidence.identity_status == "ambiguous":
        return decide("quarantined", [ADM_IDENTITY_AMBIGUOUS])
    if evidence.identity_status != "resolved" or not evidence.canonical_node_id:
        return decide("blocked", [ADM_IDENTITY_MISSING])
    if request.identity_registry_source_head != request.source_head:
        return decide("blocked", [ADM_EVIDENCE_STALE])
    if (
        request.crosswalk_canonical_path != request.path
        or request.crosswalk_canonical_blob_oid != request.blob_oid
    ):
        return decide(
            "quarantined",
            [ADM_IDENTITY_CROSSWALK_INVALID, ADM_IDENTITY_CONFLICT],
        )

    if evidence.schema_status == "missing":
        return decide("blocked", [ADM_SCHEMA_MISSING])
    if evidence.schema_status == "invalid":
        return decide("blocked", [ADM_SCHEMA_INVALID])
    if evidence.schema_status != "valid":
        return decide("blocked", [ADM_SCHEMA_UNSUPPORTED])
    if evidence.readiness_status == "review_required":
        return decide("review_required", [ADM_REVIEW_REQUIRED])
    if evidence.readiness_status == "manual_review_required":
        return decide("review_required", [ADM_MANUAL_REVIEW_REQUIRED])
    if evidence.readiness_status == "missing":
        return decide("blocked", [ADM_READINESS_MISSING])
    if evidence.readiness_status != "ready":
        return decide("blocked", [ADM_NOT_READY])
    if evidence.validator_status == "missing":
        return decide("review_required", [ADM_VALIDATOR_MISSING])
    if evidence.validator_status != "accepted":
        return decide("review_required", [ADM_VALIDATOR_REJECTED])
    if evidence.validated_blob_oid is None:
        return decide("review_required", [ADM_VALIDATOR_MISSING])

    if evidence.prerequisite_status == "unresolved":
        if request.requested_use == "teaser_read_only":
            return decide(
                "admitted_teaser_only",
                [ADM_TEASER_LIMIT, ADM_READ_ONLY_LIMIT],
                effective_use="teaser_read_only",
            )
        return decide("blocked", [ADM_PREREQUISITE_UNRESOLVED])
    if request.requested_use == "teaser_read_only":
        return decide(
            "admitted_teaser_only",
            [ADM_TEASER_LIMIT, ADM_READ_ONLY_LIMIT],
            effective_use="teaser_read_only",
        )
    return decide(
        "admitted_manual_read_only",
        [ADM_OK, ADM_READ_ONLY_LIMIT],
        effective_use=request.requested_use,
    )


__all__ = [
    "AdmissionDecision",
    "AdmissionInputError",
    "AdmissionRequest",
    "evaluate_admission",
]

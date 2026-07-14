"""Sealed evidence boundary for Math Mentor admission.

All fields on ``AdmissionRequest`` are caller claims.  This module does not
read a node, run a validator, resolve an identity conflict, or activate a
consumer.  It only seals a precomputed evidence record supplied by an external
provider boundary.  The production provider is intentionally inactive in P0;
the deterministic provider is test-only.

Serialized, copied, duck-typed, or directly constructed evidence is not
trusted.  Only the exact in-process object issued by a provider is registered
as valid evidence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from pathlib import PurePosixPath
import re
from typing import Any
from weakref import WeakKeyDictionary


EVIDENCE_PROVIDER_INACTIVE = "EVIDENCE_PROVIDER_INACTIVE"
EVIDENCE_FIXTURE_IN_PRODUCTION = "EVIDENCE_FIXTURE_IN_PRODUCTION"
EVIDENCE_HANDLE_UNTRUSTED = "EVIDENCE_HANDLE_UNTRUSTED"
EVIDENCE_RECORD_INVALID = "EVIDENCE_RECORD_INVALID"

_SCHEMA_VERSION = "math_mentor.trusted_admission_evidence.v1"
_REQUEST_SCHEMA_VERSION = "math_mentor.admission_request.v1"
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_UUIDV5_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_EVIDENCE_SEAL = object()
_ISSUED_EVIDENCE = WeakKeyDictionary()

_EVIDENCE_CLASSES = frozenset({"canonical_node", "legacy_state_table"})
_SCHEMA_ERAS = frozenset({"E1", "E2", "E3", "E4", "legacy", "unknown"})
_IDENTITY_STATUSES = frozenset(
    {"resolved", "missing", "ambiguous", "conflict", "not_applicable"}
)
_SCHEMA_STATUSES = frozenset(
    {"valid", "invalid", "unsupported", "missing", "not_applicable"}
)
_READINESS_STATUSES = frozenset(
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
_VALIDATOR_STATUSES = frozenset(
    {"accepted", "rejected", "missing", "not_applicable"}
)
_PROVENANCE_STATUSES = frozenset(
    {"exact_blob_verified", "stale", "missing"}
)
_PREREQUISITE_STATUSES = frozenset(
    {"resolved", "unresolved", "not_required"}
)


class AdmissionEvidenceError(RuntimeError):
    def __init__(self, message: str, code: str = EVIDENCE_RECORD_INVALID):
        super().__init__(message)
        self.code = code


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AdmissionEvidenceError(f"{name} must be an object")
    return value


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdmissionEvidenceError(f"{name} must be a non-empty string")
    return value


def _optional_string(value: Any, name: str) -> str | None:
    if value is None:
        return None
    return _string(value, name)


def _enum(value: Any, allowed: frozenset[str], name: str) -> str:
    if value not in allowed:
        raise AdmissionEvidenceError(f"unsupported {name}: {value!r}")
    return value


def _sha1(value: Any, name: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    value = _string(value, name)
    if not _SHA1_RE.fullmatch(value):
        raise AdmissionEvidenceError(f"{name} must be a 40 character Git SHA")
    return value


def _sha256(value: Any, name: str) -> str:
    value = _string(value, name)
    if not _SHA256_RE.fullmatch(value):
        raise AdmissionEvidenceError(f"{name} must be a 64 character SHA-256")
    return value


def _uuidv5(value: Any, name: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    value = _string(value, name)
    if not _UUIDV5_RE.fullmatch(value):
        raise AdmissionEvidenceError(f"{name} must be a lowercase UUIDv5")
    return value


def _path(value: Any, name: str) -> str:
    value = _string(value, name)
    if "\\" in value or value.startswith("/") or value.endswith("/"):
        raise AdmissionEvidenceError(f"{name} must be a normalized repo path")
    pure = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in pure.parts) or str(pure) != value:
        raise AdmissionEvidenceError(f"{name} must be a normalized repo path")
    return value


@dataclass(frozen=True, eq=False)
class TrustedAdmissionEvidence:
    evidence_id: str
    evidence_class: str
    provider_ref: str
    trust_source: str
    repo_id: str
    source_head: str
    path: str
    blob_oid: str
    canonical_node_id: str | None
    crosswalk_source_head: str | None
    crosswalk_blob_oid: str | None
    crosswalk_payload_sha256: str | None
    admission_request_payload_sha256: str
    admission_request_schema_version: str
    normalized_schema_version: str | None
    validator_ref: str | None
    validated_blob_oid: str | None
    prerequisite_status: str
    prerequisite_evidence_ref: str
    prerequisite_evidence_sha256: str
    asset_role: str
    schema_era: str
    identity_status: str
    schema_status: str
    readiness_status: str
    validator_status: str
    provenance_status: str
    consumer_allowed: bool
    conflict_status: str
    _seal: object = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._seal is not _EVIDENCE_SEAL:
            raise AdmissionEvidenceError(
                "TrustedAdmissionEvidence must be issued by an evidence provider",
                EVIDENCE_HANDLE_UNTRUSTED,
            )

    def to_dict(self) -> dict[str, Any]:
        """Return an untrusted audit snapshot that cannot re-enter admission."""

        return {
            "schema_version": _SCHEMA_VERSION,
            "evidence_id": self.evidence_id,
            "evidence_class": self.evidence_class,
            "provider_ref": self.provider_ref,
            "trust_source": self.trust_source,
            "binding": {
                "repo_id": self.repo_id,
                "source_head": self.source_head,
                "path": self.path,
                "blob_oid": self.blob_oid,
                "canonical_node_id": self.canonical_node_id,
                "crosswalk_source_head": self.crosswalk_source_head,
                "crosswalk_blob_oid": self.crosswalk_blob_oid,
                "crosswalk_payload_sha256": self.crosswalk_payload_sha256,
                "admission_request_payload_sha256": self.admission_request_payload_sha256,
                "admission_request_schema_version": self.admission_request_schema_version,
                "normalized_schema_version": self.normalized_schema_version,
                "validator_ref": self.validator_ref,
                "validated_blob_oid": self.validated_blob_oid,
                "prerequisite_status": self.prerequisite_status,
                "prerequisite_evidence_ref": self.prerequisite_evidence_ref,
                "prerequisite_evidence_sha256": self.prerequisite_evidence_sha256,
            },
            "findings": {
                "asset_role": self.asset_role,
                "schema_era": self.schema_era,
                "identity_status": self.identity_status,
                "schema_status": self.schema_status,
                "readiness_status": self.readiness_status,
                "validator_status": self.validator_status,
                "provenance_status": self.provenance_status,
                "consumer_allowed": self.consumer_allowed,
                "conflict_status": self.conflict_status,
            },
        }


def _evidence_fingerprint(value: TrustedAdmissionEvidence) -> tuple[Any, ...]:
    """Capture every issued field so object.__setattr__ cannot retain trust."""

    return tuple(getattr(value, item.name) for item in fields(value))


def _issue_evidence(record: Mapping[str, Any]) -> TrustedAdmissionEvidence:
    """Issue deterministic test evidence only.

    P0 has no production issuer.  Keeping this helper test-fixture-only means
    even direct module-private invocation remains rejected by production
    admission.
    """
    if record.get("schema_version") != _SCHEMA_VERSION:
        raise AdmissionEvidenceError("unsupported trusted admission evidence schema")
    binding = _mapping(record.get("binding"), "binding")
    findings = _mapping(record.get("findings"), "findings")
    evidence_class = _enum(
        record.get("evidence_class"), _EVIDENCE_CLASSES, "evidence class"
    )
    canonical = evidence_class == "canonical_node"

    canonical_node_id = _uuidv5(
        binding.get("canonical_node_id"),
        "binding.canonical_node_id",
        nullable=not canonical,
    )
    crosswalk_source_head = _sha1(
        binding.get("crosswalk_source_head"),
        "binding.crosswalk_source_head",
        nullable=not canonical,
    )
    crosswalk_blob_oid = _sha1(
        binding.get("crosswalk_blob_oid"),
        "binding.crosswalk_blob_oid",
        nullable=not canonical,
    )
    crosswalk_payload_sha256 = (
        _sha256(
            binding.get("crosswalk_payload_sha256"),
            "binding.crosswalk_payload_sha256",
        )
        if canonical
        else None
    )
    normalized_schema_version = _optional_string(
        binding.get("normalized_schema_version"),
        "binding.normalized_schema_version",
    )
    validator_ref = _optional_string(
        binding.get("validator_ref"), "binding.validator_ref"
    )
    validated_blob_oid = _sha1(
        binding.get("validated_blob_oid"),
        "binding.validated_blob_oid",
        nullable=not canonical,
    )
    if canonical and (
        normalized_schema_version is None
        or validator_ref is None
        or validated_blob_oid is None
    ):
        raise AdmissionEvidenceError(
            "canonical evidence requires schema and validator bindings"
        )
    if not canonical and any(
        value is not None
        for value in (
            canonical_node_id,
            crosswalk_source_head,
            crosswalk_blob_oid,
            crosswalk_payload_sha256,
            normalized_schema_version,
            validator_ref,
            validated_blob_oid,
            binding.get("crosswalk_payload_sha256"),
        )
    ):
        raise AdmissionEvidenceError(
            "legacy evidence must not claim canonical or validator bindings"
        )

    consumer_allowed = findings.get("consumer_allowed")
    if consumer_allowed is not False:
        raise AdmissionEvidenceError("consumer_allowed must remain false in P0")
    if findings.get("conflict_status") != "not_evaluated":
        raise AdmissionEvidenceError(
            "the evidence provider must not adjudicate identity conflicts"
        )

    evidence = TrustedAdmissionEvidence(
        evidence_id=_string(record.get("evidence_id"), "evidence_id"),
        evidence_class=evidence_class,
        provider_ref=_string(record.get("provider_ref"), "provider_ref"),
        trust_source="test_fixture",
        repo_id=_string(binding.get("repo_id"), "binding.repo_id"),
        source_head=_sha1(binding.get("source_head"), "binding.source_head"),
        path=_path(binding.get("path"), "binding.path"),
        blob_oid=_sha1(binding.get("blob_oid"), "binding.blob_oid"),
        canonical_node_id=canonical_node_id,
        crosswalk_source_head=crosswalk_source_head,
        crosswalk_blob_oid=crosswalk_blob_oid,
        crosswalk_payload_sha256=crosswalk_payload_sha256,
        admission_request_payload_sha256=_sha256(
            binding.get("admission_request_payload_sha256"),
            "binding.admission_request_payload_sha256",
        ),
        admission_request_schema_version=_enum(
            binding.get("admission_request_schema_version"),
            frozenset({_REQUEST_SCHEMA_VERSION}),
            "admission request schema version",
        ),
        normalized_schema_version=normalized_schema_version,
        validator_ref=validator_ref,
        validated_blob_oid=validated_blob_oid,
        prerequisite_status=_enum(
            binding.get("prerequisite_status"),
            _PREREQUISITE_STATUSES,
            "prerequisite status",
        ),
        prerequisite_evidence_ref=_string(
            binding.get("prerequisite_evidence_ref"),
            "binding.prerequisite_evidence_ref",
        ),
        prerequisite_evidence_sha256=_sha256(
            binding.get("prerequisite_evidence_sha256"),
            "binding.prerequisite_evidence_sha256",
        ),
        asset_role=_enum(
            findings.get("asset_role"), _EVIDENCE_CLASSES, "asset role"
        ),
        schema_era=_enum(findings.get("schema_era"), _SCHEMA_ERAS, "schema era"),
        identity_status=_enum(
            findings.get("identity_status"),
            _IDENTITY_STATUSES,
            "identity status",
        ),
        schema_status=_enum(
            findings.get("schema_status"), _SCHEMA_STATUSES, "schema status"
        ),
        readiness_status=_enum(
            findings.get("readiness_status"),
            _READINESS_STATUSES,
            "readiness status",
        ),
        validator_status=_enum(
            findings.get("validator_status"),
            _VALIDATOR_STATUSES,
            "validator status",
        ),
        provenance_status=_enum(
            findings.get("provenance_status"),
            _PROVENANCE_STATUSES,
            "provenance status",
        ),
        consumer_allowed=False,
        conflict_status="not_evaluated",
        _seal=_EVIDENCE_SEAL,
    )
    _ISSUED_EVIDENCE[evidence] = _evidence_fingerprint(evidence)
    return evidence


class AdmissionEvidenceProvider(ABC):
    @abstractmethod
    def authenticate(
        self, opaque_handle: object, *, mode: str = "production"
    ) -> TrustedAdmissionEvidence:
        raise NotImplementedError


class ProductionAdmissionEvidenceProvider(AdmissionEvidenceProvider):
    """Inactive P0 boundary; a future Human-gated host adapter must replace it."""

    def authenticate(
        self, opaque_handle: object, *, mode: str = "production"
    ) -> TrustedAdmissionEvidence:
        raise AdmissionEvidenceError(
            "production admission evidence provider is inactive in P0",
            EVIDENCE_PROVIDER_INACTIVE,
        )


class DeterministicTestAdmissionEvidenceProvider(AdmissionEvidenceProvider):
    """Test-composition fixture provider; never a production trust source."""

    def __init__(self, records: Mapping[str, Mapping[str, Any]]):
        self._records = dict(records)

    def authenticate(
        self, opaque_handle: object, *, mode: str = "production"
    ) -> TrustedAdmissionEvidence:
        if mode != "test":
            raise AdmissionEvidenceError(
                "deterministic evidence fixtures are forbidden in production",
                EVIDENCE_FIXTURE_IN_PRODUCTION,
            )
        record = self._records.get(str(opaque_handle))
        if record is None:
            raise AdmissionEvidenceError(
                "unknown deterministic evidence handle",
                EVIDENCE_HANDLE_UNTRUSTED,
            )
        return _issue_evidence(record)


def is_verified_admission_evidence(value: Any) -> bool:
    return (
        type(value) is TrustedAdmissionEvidence
        and value._seal is _EVIDENCE_SEAL
        and _ISSUED_EVIDENCE.get(value) == _evidence_fingerprint(value)
    )


__all__ = [
    "AdmissionEvidenceError",
    "AdmissionEvidenceProvider",
    "DeterministicTestAdmissionEvidenceProvider",
    "ProductionAdmissionEvidenceProvider",
    "TrustedAdmissionEvidence",
    "is_verified_admission_evidence",
]

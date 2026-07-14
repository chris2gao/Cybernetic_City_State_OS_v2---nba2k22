"""Fail-closed authorization primitives for the Math Mentor P0 control plane.

Business payloads are untrusted.  In particular, ``human_gate`` and
``authorized_scope`` are descriptive fields and never grant permission.  A
caller must first exchange an opaque platform handle through a
``TrustBoundaryAdapter`` and then pass the sealed ``TrustedHumanGrant`` to
``verify_authorization``.

The deterministic adapter in this module exists only for unit tests.  Both the
adapter and the verifier reject test grants in production mode.

Replay evaluation is deliberately narrow: the verifier can compare a nonce
only with a host-supplied read-only snapshot.  It does not atomically consume
nonces, persist replay state, or provide cross-process replay protection.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import hmac
import json
from pathlib import PurePosixPath
import re
from types import MappingProxyType
from typing import Any, ClassVar
from weakref import WeakKeyDictionary


AUTH_OK = "AUTH_OK"
AUTH_PAYLOAD_GATE_IGNORED = "AUTH_PAYLOAD_GATE_IGNORED"
AUTH_CONTEXT_MISSING = "AUTH_CONTEXT_MISSING"
AUTH_PROTECTED_ACTION_REQUIRES_EXPLICIT_GRANT = (
    "AUTH_PROTECTED_ACTION_REQUIRES_EXPLICIT_GRANT"
)
AUTH_OPERATION_NOT_GRANTED = "AUTH_OPERATION_NOT_GRANTED"
AUTH_RESOURCE_NOT_GRANTED = "AUTH_RESOURCE_NOT_GRANTED"
AUTH_EFFECT_CEILING_EXCEEDED = "AUTH_EFFECT_CEILING_EXCEEDED"
AUTH_POST_COMPLETION_GATE_REQUIRED = "AUTH_POST_COMPLETION_GATE_REQUIRED"
AUTH_REQUEST_SCHEMA_INVALID = "AUTH_REQUEST_SCHEMA_INVALID"
AUTH_ENVELOPE_UNTRUSTED = "AUTH_ENVELOPE_UNTRUSTED"
AUTH_PRINCIPAL_INVALID = "AUTH_PRINCIPAL_INVALID"
AUTH_TASK_MISMATCH = "AUTH_TASK_MISMATCH"
AUTH_REQUEST_MISMATCH = "AUTH_REQUEST_MISMATCH"
AUTH_OBJECTIVE_MISMATCH = "AUTH_OBJECTIVE_MISMATCH"
AUTH_SOURCE_HEAD_MISMATCH = "AUTH_SOURCE_HEAD_MISMATCH"
AUTH_NOT_YET_VALID = "AUTH_NOT_YET_VALID"
AUTH_EXPIRED = "AUTH_EXPIRED"
AUTH_REVOKED = "AUTH_REVOKED"
AUTH_NONCE_REPLAY = "AUTH_NONCE_REPLAY"
AUTH_SECRET_SCOPE_FORBIDDEN = "AUTH_SECRET_SCOPE_FORBIDDEN"
AUTH_FIXTURE_IN_PRODUCTION = "AUTH_FIXTURE_IN_PRODUCTION"
AUTH_INDETERMINATE = "AUTH_INDETERMINATE"


OPERATIONS = frozenset(
    {
        "repository.read",
        "conversation.teach",
        "control_plane.write",
        "communication.write",
        "student_state.write",
        "scheduler_state.write",
        "prompt.mutate",
        "node.mutate",
        "bridge.mutate",
        "runtime.activate",
        "coordinator.activate",
        "external_tool.execute",
        "source.publish",
        "protected_git.rewrite",
        "secret.read",
    }
)

OPERATION_EFFECT = {
    "repository.read": "read_only",
    "conversation.teach": "conversation_only",
    "control_plane.write": "business_file_write",
    "communication.write": "business_file_write",
    "student_state.write": "student_state_write",
    "scheduler_state.write": "scheduler_state_write",
    "prompt.mutate": "business_file_write",
    "node.mutate": "business_file_write",
    "bridge.mutate": "business_file_write",
    "runtime.activate": "runtime_activation",
    "coordinator.activate": "runtime_activation",
    "external_tool.execute": "runtime_activation",
    "source.publish": "publication",
    "protected_git.rewrite": "destructive_git",
    "secret.read": "secret_or_privacy",
}

EFFECT_RANK = {
    "read_only": 0,
    "conversation_only": 0,
    "business_file_write": 1,
    "student_state_write": 2,
    "scheduler_state_write": 2,
    "runtime_activation": 3,
    "publication": 4,
    "destructive_git": 5,
    "secret_or_privacy": 6,
}

AUTHORITY_CLASSES = frozenset(
    {"current_explicit_human", "authenticated_human_approved_task"}
)
AUTHENTICATED_CHANNELS = frozenset(
    {"current_human_turn", "authenticated_approval_channel"}
)
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_WILDCARD_RE = re.compile(r"[*?\[\]{}]")
_REQUEST_SEAL = object()
_TRUST_SEAL = object()
_DECISION_SEAL = object()
_ISSUED_REQUESTS = WeakKeyDictionary()
_ISSUED_GRANTS = WeakKeyDictionary()
_ISSUED_DECISIONS = WeakKeyDictionary()


class AuthorizationInputError(ValueError):
    """A request or trusted-envelope record failed structural validation."""

    def __init__(self, message: str, code: str = AUTH_REQUEST_SCHEMA_INVALID):
        super().__init__(message)
        self.code = code


class TrustBoundaryError(RuntimeError):
    """An opaque authorization handle could not cross the trust boundary."""

    def __init__(self, message: str, code: str = AUTH_ENVELOPE_UNTRUSTED):
        super().__init__(message)
        self.code = code


def _has_unicode_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _required_string(value: Any, field_name: str) -> str:
    if type(value) is not str or not value.strip():
        raise AuthorizationInputError(f"{field_name} must be a non-empty string")
    if _has_unicode_surrogate(value):
        raise AuthorizationInputError(
            f"{field_name} must not contain Unicode surrogate code points"
        )
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, field_name)


def _required_bool(value: Any, field_name: str) -> bool:
    if type(value) is not bool:
        raise AuthorizationInputError(f"{field_name} must be a boolean")
    return value


def _validate_sha1(value: Any, field_name: str) -> str:
    value = _required_string(value, field_name)
    if not _SHA1_RE.fullmatch(value):
        raise AuthorizationInputError(f"{field_name} must be a 40 character Git SHA")
    return value


def _validate_sha256(value: Any, field_name: str) -> str:
    value = _required_string(value, field_name)
    if not _SHA256_RE.fullmatch(value):
        raise AuthorizationInputError(f"{field_name} must be a sha256:<64-hex> value")
    return value


def _validate_relative_path(value: Any, field_name: str, *, prefix: bool) -> str:
    value = _required_string(value, field_name)
    if (
        "\\" in value
        or ":" in value
        or _WILDCARD_RE.search(value)
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise AuthorizationInputError(f"{field_name} must be a literal POSIX path")
    if prefix:
        if not value.endswith("/"):
            raise AuthorizationInputError(f"{field_name} prefix must end with '/'")
        path_body = value[:-1]
    else:
        if value.endswith("/"):
            raise AuthorizationInputError(f"{field_name} exact path must not end with '/'")
        path_body = value
    if any(part.endswith((".", " ")) for part in path_body.split("/")):
        raise AuthorizationInputError(
            f"{field_name} components must not end with dot or space"
        )
    pure = PurePosixPath(path_body)
    if pure.is_absolute() or not path_body or any(part in {"", ".", ".."} for part in pure.parts):
        raise AuthorizationInputError(f"{field_name} must be repository-relative")
    if str(pure) != path_body:
        raise AuthorizationInputError(f"{field_name} must already be normalized")
    return value


def _parse_time(value: Any, field_name: str, *, nullable: bool = False) -> datetime | None:
    if value is None and nullable:
        return None
    value = _required_string(value, field_name)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise AuthorizationInputError(f"{field_name} must include a timezone")
        return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise AuthorizationInputError(f"{field_name} must be valid RFC3339") from exc


def _format_time(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(item) for item in value)
    return value


def _deep_thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _deep_thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_deep_thaw(item) for item in value]
    return value


def _issuance_fingerprint(value: Any) -> str:
    try:
        canonical = json.dumps(
            _deep_thaw(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise AuthorizationInputError(
            "authorization issuance value is not canonically encodable"
        ) from exc
    return sha256(canonical).hexdigest()


def _as_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if type(value) is not dict:
        raise AuthorizationInputError(f"{field_name} must be a plain object")
    if any(type(key) is not str for key in value):
        raise AuthorizationInputError(
            f"{field_name} keys must be exact built-in strings"
        )
    return value


def _as_string_set(value: Any, field_name: str, allowed: frozenset[str]) -> frozenset[str]:
    if type(value) is not list:
        raise AuthorizationInputError(f"{field_name} must be a plain array")
    result: set[str] = set()
    for item in value:
        item = _required_string(item, field_name)
        if item not in allowed:
            raise AuthorizationInputError(f"unsupported value {item!r} in {field_name}")
        result.add(item)
    return frozenset(result)


@dataclass(frozen=True, slots=True)
class ResourceRef:
    repo_id: str
    path: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ResourceRef":
        value = _as_mapping(value, "resource")
        return cls(
            repo_id=_required_string(value.get("repo_id"), "resources.repo_id"),
            path=_validate_relative_path(
                value.get("path"), "resources.path", prefix=False
            ),
        )

    def to_dict(self) -> dict[str, str]:
        return _resource_ref_snapshot(self)


@dataclass(frozen=True, slots=True)
class ResourceSelector:
    repo_id: str
    path: str
    match: str
    operations: frozenset[str]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ResourceSelector":
        value = _as_mapping(value, "resource selector")
        match = _required_string(value.get("match"), "resource selector match")
        if match not in {"exact", "prefix"}:
            raise AuthorizationInputError("resource selector match must be exact or prefix")
        operations = _as_string_set(
            value.get("operations"), "resource_selectors.operations", OPERATIONS
        )
        if not operations:
            raise AuthorizationInputError("resource selector operations must not be empty")
        return cls(
            repo_id=_required_string(
                value.get("repo_id"), "resource_selectors.repo_id"
            ),
            path=_validate_relative_path(
                value.get("path"), "resource_selectors.path", prefix=match == "prefix"
            ),
            match=match,
            operations=operations,
        )

    def matches(self, resource: ResourceRef, operation: str) -> bool:
        return _resource_selector_matches(self, resource, operation)

    def to_dict(self) -> dict[str, Any]:
        return _resource_selector_snapshot(self)


def _resource_ref_snapshot(resource: ResourceRef) -> dict[str, str]:
    if type(resource) is not ResourceRef:
        raise AuthorizationInputError("issued resource must be an exact ResourceRef")
    repo_id = _required_string(resource.repo_id, "issued resource repo_id")
    path = _required_string(resource.path, "issued resource path")
    return {"repo_id": repo_id, "path": path, "match": "exact"}


def _resource_selector_snapshot(selector: ResourceSelector) -> dict[str, Any]:
    if type(selector) is not ResourceSelector:
        raise AuthorizationInputError(
            "issued resource selector must be an exact ResourceSelector"
        )
    repo_id = _required_string(selector.repo_id, "issued selector repo_id")
    path = _required_string(selector.path, "issued selector path")
    match = _required_string(selector.match, "issued selector match")
    if match not in {"exact", "prefix"}:
        raise AuthorizationInputError("issued selector match is invalid")
    if type(selector.operations) is not frozenset or any(
        type(operation) is not str for operation in selector.operations
    ):
        raise AuthorizationInputError(
            "issued selector operations must be an exact frozenset of strings"
        )
    return {
        "repo_id": repo_id,
        "path": path,
        "match": match,
        "operations": sorted(selector.operations),
    }


def _resource_selector_matches(
    selector: ResourceSelector,
    resource: ResourceRef,
    operation: str,
) -> bool:
    """Match immutable selector fields without instance method dispatch."""

    if type(selector) is not ResourceSelector or type(resource) is not ResourceRef:
        return False
    if type(operation) is not str:
        return False
    if resource.repo_id != selector.repo_id or operation not in selector.operations:
        return False
    if selector.match == "exact":
        return resource.path == selector.path
    return resource.path.startswith(selector.path)


@dataclass(frozen=True, eq=False)
class AuthorizationRequest:
    schema_version: str
    request_id: str
    task_id: str
    objective_sha256: str
    source_head: str
    operation: str
    effect_class: str
    resources: tuple[ResourceRef, ...]
    gate_phase: str = "pre_action"
    payload_human_gate: Any = field(default=None, repr=False, compare=False)
    _seal: object | None = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AuthorizationRequest":
        value = _as_mapping(value, "authorization request")
        schema_version = _required_string(value.get("schema_version"), "schema_version")
        if schema_version != "math_mentor.authorization_request.v1":
            raise AuthorizationInputError("unsupported authorization request schema")
        operation = _required_string(value.get("operation"), "operation")
        effect_class = _required_string(value.get("effect_class"), "effect_class")
        if operation not in OPERATIONS:
            raise AuthorizationInputError("unsupported operation")
        if effect_class not in EFFECT_RANK or OPERATION_EFFECT[operation] != effect_class:
            raise AuthorizationInputError("operation and effect_class do not agree")
        raw_resources = value.get("resources")
        if type(raw_resources) is not list:
            raise AuthorizationInputError("resources must be a plain array")
        resources = tuple(
            ResourceRef.from_mapping(_as_mapping(item, "resources item"))
            for item in raw_resources
        )
        if operation not in {"conversation.teach"} and not resources:
            raise AuthorizationInputError("this operation requires at least one resource")
        gate_phase = _required_string(
            value.get("gate_phase", "pre_action"), "gate_phase"
        )
        if gate_phase not in {"pre_action", "post_completion"}:
            raise AuthorizationInputError("gate_phase must be pre_action or post_completion")
        business_payload = value.get("business_payload", {})
        business_payload = _as_mapping(business_payload, "business_payload")
        payload_gate = value.get(
            "payload_human_gate", business_payload.get("human_gate")
        )
        instance = cls(
            schema_version="math_mentor.authorization_request.v1",
            request_id=_required_string(value.get("request_id"), "request_id"),
            task_id=_required_string(value.get("task_id"), "task_id"),
            objective_sha256=_validate_sha256(
                value.get("objective_sha256"), "objective_sha256"
            ),
            source_head=_validate_sha1(value.get("source_head"), "source_head"),
            operation=operation,
            effect_class=effect_class,
            resources=resources,
            gate_phase=gate_phase,
            payload_human_gate=payload_gate,
        )
        object.__setattr__(instance, "_seal", _REQUEST_SEAL)
        _ISSUED_REQUESTS[instance] = _request_fingerprint(instance)
        return instance

    def is_factory_issued(self) -> bool:
        """Return true only for this exact object emitted by ``from_mapping``."""

        return _verified_request_snapshot(self) is not None


@dataclass(frozen=True, slots=True)
class _RequestSnapshot:
    schema_version: str
    request_id: str
    task_id: str
    objective_sha256: str
    source_head: str
    operation: str
    effect_class: str
    resources: tuple[ResourceRef, ...]
    gate_phase: str
    payload_human_gate: str | None


def _snapshot_request(request: Any) -> _RequestSnapshot:
    if type(request) is not AuthorizationRequest:
        raise AuthorizationInputError("issued request must be an AuthorizationRequest")
    string_fields = {
        "schema_version": request.schema_version,
        "request_id": request.request_id,
        "task_id": request.task_id,
        "objective_sha256": request.objective_sha256,
        "source_head": request.source_head,
        "operation": request.operation,
        "effect_class": request.effect_class,
        "gate_phase": request.gate_phase,
    }
    for field_name, field_value in string_fields.items():
        _required_string(field_value, f"issued request {field_name}")
    if type(request.resources) is not tuple:
        raise AuthorizationInputError("issued request resources must be an exact tuple")
    resources_list: list[ResourceRef] = []
    for item in request.resources:
        item_snapshot = _resource_ref_snapshot(item)
        resources_list.append(
            ResourceRef(
                repo_id=item_snapshot["repo_id"],
                path=item_snapshot["path"],
            )
        )
    resources = tuple(resources_list)
    observed_gate = request.payload_human_gate
    if observed_gate is not None:
        if type(observed_gate) is not str:
            observed_gate = "<non-string>"
        elif _has_unicode_surrogate(observed_gate):
            raise AuthorizationInputError(
                "payload_human_gate must not contain Unicode surrogates"
            )
    return _RequestSnapshot(
        **string_fields,
        resources=resources,
        payload_human_gate=observed_gate,
    )


def _request_snapshot_fingerprint(snapshot: _RequestSnapshot) -> str:
    return _issuance_fingerprint(
        {
            "schema_version": snapshot.schema_version,
            "request_id": snapshot.request_id,
            "task_id": snapshot.task_id,
            "objective_sha256": snapshot.objective_sha256,
            "source_head": snapshot.source_head,
            "operation": snapshot.operation,
            "effect_class": snapshot.effect_class,
            "resources": [
                _resource_ref_snapshot(item) for item in snapshot.resources
            ],
            "gate_phase": snapshot.gate_phase,
            "payload_human_gate_observed": snapshot.payload_human_gate,
        }
    )


def _request_fingerprint(request: AuthorizationRequest) -> str:
    return _request_snapshot_fingerprint(_snapshot_request(request))


def _verified_request_snapshot(value: Any) -> _RequestSnapshot | None:
    if type(value) is not AuthorizationRequest or value._seal is not _REQUEST_SEAL:
        return None
    try:
        issued = _ISSUED_REQUESTS.get(value)
        snapshot = _snapshot_request(value)
        current = _request_snapshot_fingerprint(snapshot)
    except Exception:
        return None
    if type(issued) is not str or not hmac.compare_digest(issued, current):
        return None
    return snapshot


@dataclass(frozen=True, eq=False)
class TrustedHumanGrant:
    """Sealed output of a trust-boundary adapter, never a business payload."""

    envelope_id: str
    authority_class: str
    principal_ref: str
    channel: str
    evidence_ref: str
    task_id: str
    request_id: str
    objective_sha256: str
    source_head: str
    allowed_operations: frozenset[str]
    resource_selectors: tuple[ResourceSelector, ...]
    effect_ceiling: str
    explicitly_denied_operations: frozenset[str]
    issued_at: datetime
    not_before: datetime
    expires_at: datetime | None
    revoked: bool
    revocation_ref: str | None
    nonce: str
    one_time: bool
    pre_action: str
    post_completion: str
    post_completion_approval_ref: str | None
    trust_source: str
    _seal: object = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._seal is not _TRUST_SEAL:
            raise TrustBoundaryError(
                "TrustedHumanGrant must be created by a trust-boundary adapter"
            )

    def is_factory_issued(self) -> bool:
        return _verified_grant_snapshot(self) is not None


@dataclass(frozen=True, slots=True)
class _GrantSnapshot:
    envelope_id: str
    authority_class: str
    principal_ref: str
    channel: str
    evidence_ref: str
    task_id: str
    request_id: str
    objective_sha256: str
    source_head: str
    allowed_operations: frozenset[str]
    resource_selectors: tuple[ResourceSelector, ...]
    effect_ceiling: str
    explicitly_denied_operations: frozenset[str]
    issued_at: datetime
    not_before: datetime
    expires_at: datetime | None
    revoked: bool
    revocation_ref: str | None
    nonce: str
    one_time: bool
    pre_action: str
    post_completion: str
    post_completion_approval_ref: str | None
    trust_source: str


def _snapshot_grant(grant: Any) -> _GrantSnapshot:
    if type(grant) is not TrustedHumanGrant:
        raise AuthorizationInputError("issued grant must be a TrustedHumanGrant")
    string_fields = {
        "envelope_id": grant.envelope_id,
        "authority_class": grant.authority_class,
        "principal_ref": grant.principal_ref,
        "channel": grant.channel,
        "evidence_ref": grant.evidence_ref,
        "task_id": grant.task_id,
        "request_id": grant.request_id,
        "objective_sha256": grant.objective_sha256,
        "source_head": grant.source_head,
        "effect_ceiling": grant.effect_ceiling,
        "nonce": grant.nonce,
        "pre_action": grant.pre_action,
        "post_completion": grant.post_completion,
        "trust_source": grant.trust_source,
    }
    for field_name, field_value in string_fields.items():
        _required_string(field_value, f"issued grant {field_name}")
    optional_strings = {
        "revocation_ref": grant.revocation_ref,
        "post_completion_approval_ref": grant.post_completion_approval_ref,
    }
    for field_name, field_value in optional_strings.items():
        if field_value is not None:
            _required_string(field_value, f"issued grant {field_name}")
    collection_snapshots: dict[str, frozenset[str]] = {}
    for field_name, field_value in (
        ("allowed_operations", grant.allowed_operations),
        ("explicitly_denied_operations", grant.explicitly_denied_operations),
    ):
        if type(field_value) is not frozenset or any(
            type(item) is not str for item in field_value
        ):
            raise AuthorizationInputError(
                f"issued grant {field_name} must be an exact frozenset of strings"
            )
        collection_snapshots[field_name] = frozenset(field_value)
    if type(grant.resource_selectors) is not tuple:
        raise AuthorizationInputError(
            "issued grant resource_selectors must be an exact tuple"
        )
    selector_snapshots: list[ResourceSelector] = []
    for selector in grant.resource_selectors:
        selector_snapshot = _resource_selector_snapshot(selector)
        selector_snapshots.append(
            ResourceSelector(
                repo_id=selector_snapshot["repo_id"],
                path=selector_snapshot["path"],
                match=selector_snapshot["match"],
                operations=frozenset(selector_snapshot["operations"]),
            )
        )
    datetime_snapshots: dict[str, datetime] = {}
    for field_name, field_value in (
        ("issued_at", grant.issued_at),
        ("not_before", grant.not_before),
    ):
        if type(field_value) is not datetime or field_value.tzinfo is not timezone.utc:
            raise AuthorizationInputError(
                f"issued grant {field_name} must be an exact UTC datetime"
            )
        datetime_snapshots[field_name] = field_value
    expires_at = grant.expires_at
    if expires_at is not None and (
        type(expires_at) is not datetime or expires_at.tzinfo is not timezone.utc
    ):
        raise AuthorizationInputError(
            "issued grant expires_at must be an exact UTC datetime or null"
        )
    revoked = grant.revoked
    one_time = grant.one_time
    if type(revoked) is not bool or type(one_time) is not bool:
        raise AuthorizationInputError("issued grant boolean fields must be exact bools")
    return _GrantSnapshot(
        **string_fields,
        allowed_operations=collection_snapshots["allowed_operations"],
        resource_selectors=tuple(selector_snapshots),
        explicitly_denied_operations=collection_snapshots[
            "explicitly_denied_operations"
        ],
        issued_at=datetime_snapshots["issued_at"],
        not_before=datetime_snapshots["not_before"],
        expires_at=expires_at,
        revoked=revoked,
        **optional_strings,
        one_time=one_time,
    )


def _grant_snapshot_fingerprint(grant: _GrantSnapshot) -> str:
    return _issuance_fingerprint(
        {
            "envelope_id": grant.envelope_id,
            "authority_class": grant.authority_class,
            "principal_ref": grant.principal_ref,
            "channel": grant.channel,
            "evidence_ref": grant.evidence_ref,
            "task_id": grant.task_id,
            "request_id": grant.request_id,
            "objective_sha256": grant.objective_sha256,
            "source_head": grant.source_head,
            "effect_ceiling": grant.effect_ceiling,
            "nonce": grant.nonce,
            "pre_action": grant.pre_action,
            "post_completion": grant.post_completion,
            "trust_source": grant.trust_source,
            "allowed_operations": sorted(grant.allowed_operations),
            "resource_selectors": [
                _resource_selector_snapshot(selector)
                for selector in grant.resource_selectors
            ],
            "explicitly_denied_operations": sorted(
                grant.explicitly_denied_operations
            ),
            "issued_at": _format_time(grant.issued_at),
            "not_before": _format_time(grant.not_before),
            "expires_at": _format_time(grant.expires_at),
            "revoked": grant.revoked,
            "revocation_ref": grant.revocation_ref,
            "post_completion_approval_ref": grant.post_completion_approval_ref,
            "one_time": grant.one_time,
        }
    )


def _grant_fingerprint(grant: TrustedHumanGrant) -> str:
    return _grant_snapshot_fingerprint(_snapshot_grant(grant))


def _verified_grant_snapshot(value: Any) -> _GrantSnapshot | None:
    if type(value) is not TrustedHumanGrant or value._seal is not _TRUST_SEAL:
        return None
    try:
        issued = _ISSUED_GRANTS.get(value)
        snapshot = _snapshot_grant(value)
        current = _grant_snapshot_fingerprint(snapshot)
    except Exception:
        return None
    if type(issued) is not str or not hmac.compare_digest(issued, current):
        return None
    return snapshot


def _trusted_grant_from_record(
    record: Mapping[str, Any], *, trust_source: str
) -> TrustedHumanGrant:
    record = _as_mapping(record, "trusted grant")
    schema_version = _required_string(record.get("schema_version"), "schema_version")
    if schema_version != "math_mentor.trusted_human_grant.v1":
        raise TrustBoundaryError("unsupported trusted grant schema")
    authority = _as_mapping(record.get("authority"), "authority")
    binding = _as_mapping(record.get("binding"), "binding")
    grant = _as_mapping(record.get("grant"), "grant")
    validity = _as_mapping(record.get("validity"), "validity")
    gates = _as_mapping(record.get("gates"), "gates")

    authority_class = _required_string(
        authority.get("authority_class"), "authority.authority_class"
    )
    if authority_class not in AUTHORITY_CLASSES:
        raise TrustBoundaryError("authority class is not Human-authoritative")
    principal_type = _required_string(
        authority.get("principal_type"), "authority.principal_type"
    )
    if principal_type != "human_speaker":
        raise TrustBoundaryError("principal must be human_speaker", AUTH_PRINCIPAL_INVALID)
    channel = _required_string(authority.get("channel"), "authority.channel")
    if channel not in AUTHENTICATED_CHANNELS:
        raise TrustBoundaryError("untrusted authorization channel")

    allowed_operations = _as_string_set(
        grant.get("allowed_operations"), "allowed_operations", OPERATIONS
    )
    denied_operations = _as_string_set(
        grant.get("explicitly_denied_operations", []),
        "explicitly_denied_operations",
        OPERATIONS,
    )
    if allowed_operations & denied_operations:
        raise TrustBoundaryError("an operation cannot be both allowed and denied")
    effect_ceiling = _required_string(
        grant.get("effect_ceiling"), "grant.effect_ceiling"
    )
    if effect_ceiling not in EFFECT_RANK:
        raise TrustBoundaryError("unsupported effect ceiling")
    raw_selectors = grant.get("resource_selectors")
    if type(raw_selectors) is not list:
        raise TrustBoundaryError("resource_selectors must be a plain array")
    selectors = tuple(
        ResourceSelector.from_mapping(_as_mapping(item, "resource selector"))
        for item in raw_selectors
    )

    pre_action = _required_string(gates.get("pre_action"), "gates.pre_action")
    if pre_action != "satisfied":
        raise TrustBoundaryError("trusted grant pre_action gate is not satisfied")
    post_completion = _required_string(
        gates.get("post_completion"), "gates.post_completion"
    )
    if post_completion not in {"required", "not_required", "satisfied"}:
        raise TrustBoundaryError("invalid post_completion gate")
    post_ref = _optional_string(
        gates.get("post_completion_approval_ref"),
        "gates.post_completion_approval_ref",
    )
    if post_completion == "satisfied" and not isinstance(post_ref, str):
        raise TrustBoundaryError("satisfied post_completion gate needs evidence")
    if post_completion != "satisfied" and post_ref is not None:
        raise TrustBoundaryError(
            "post_completion evidence is only valid for a satisfied gate"
        )

    issued_at = _parse_time(validity.get("issued_at"), "validity.issued_at")
    not_before = _parse_time(validity.get("not_before"), "validity.not_before")
    expires_at = _parse_time(
        validity.get("expires_at"), "validity.expires_at", nullable=True
    )
    if issued_at > not_before:
        raise TrustBoundaryError("issued_at must not be after not_before")
    if expires_at is not None and expires_at <= not_before:
        raise TrustBoundaryError("expires_at must be after not_before")
    revoked = _required_bool(validity.get("revoked"), "validity.revoked")
    one_time = _required_bool(validity.get("one_time"), "validity.one_time")
    revocation_ref = _optional_string(
        validity.get("revocation_ref"), "validity.revocation_ref"
    )
    if revoked and revocation_ref is None:
        raise TrustBoundaryError("a revoked grant must identify revocation evidence")

    instance = TrustedHumanGrant(
        envelope_id=_required_string(record.get("envelope_id"), "envelope_id"),
        authority_class=authority_class,
        principal_ref=_required_string(authority.get("principal_ref"), "principal_ref"),
        channel=channel,
        evidence_ref=_required_string(authority.get("evidence_ref"), "evidence_ref"),
        task_id=_required_string(binding.get("task_id"), "binding.task_id"),
        request_id=_required_string(binding.get("request_id"), "binding.request_id"),
        objective_sha256=_validate_sha256(
            binding.get("objective_sha256"), "binding.objective_sha256"
        ),
        source_head=_validate_sha1(binding.get("source_head"), "binding.source_head"),
        allowed_operations=allowed_operations,
        resource_selectors=selectors,
        effect_ceiling=effect_ceiling,
        explicitly_denied_operations=denied_operations,
        issued_at=issued_at,
        not_before=not_before,
        expires_at=expires_at,
        revoked=revoked,
        revocation_ref=revocation_ref,
        nonce=_required_string(validity.get("nonce"), "validity.nonce"),
        one_time=one_time,
        pre_action=pre_action,
        post_completion=post_completion,
        post_completion_approval_ref=post_ref,
        trust_source=trust_source,
        _seal=_TRUST_SEAL,
    )
    _ISSUED_GRANTS[instance] = _grant_fingerprint(instance)
    return instance


class TrustBoundaryAdapter(ABC):
    """Translate an opaque, externally authenticated handle into a sealed grant."""

    @abstractmethod
    def authenticate(
        self, opaque_handle: object, *, mode: str = "production"
    ) -> TrustedHumanGrant:
        raise NotImplementedError


class ProductionTrustBoundaryAdapter(TrustBoundaryAdapter):
    """Adapter around a host-owned authenticated-envelope resolver.

    The resolver is supplied by the production composition root.  It must
    authenticate the opaque handle outside the business payload before
    returning the grant record.
    """

    def __init__(self, resolver: Callable[[object], Mapping[str, Any] | None]):
        if not callable(resolver):
            raise TypeError("resolver must be callable")
        self._resolver = resolver

    def authenticate(
        self, opaque_handle: object, *, mode: str = "production"
    ) -> TrustedHumanGrant:
        if type(mode) is not str or mode != "production":
            raise TrustBoundaryError("production adapter requires production mode")
        record = self._resolver(opaque_handle)
        if record is None:
            raise TrustBoundaryError("opaque authorization handle was not authenticated")
        if type(record) is not dict:
            raise TrustBoundaryError("external resolver returned an invalid grant record")
        try:
            return _trusted_grant_from_record(
                record, trust_source="external_platform"
            )
        except AuthorizationInputError as exc:
            raise TrustBoundaryError(str(exc)) from exc


class DeterministicTestTrustBoundaryAdapter(TrustBoundaryAdapter):
    """Deterministic adapter for fixtures; intentionally unusable in production."""

    def __init__(self, records: Mapping[str, Mapping[str, Any]]):
        if type(records) is not dict or any(
            type(handle) is not str or type(record) is not dict
            for handle, record in records.items()
        ):
            raise TrustBoundaryError(
                "deterministic trust records must be a plain string-to-object map"
            )
        self._records = dict(records)

    def authenticate(
        self, opaque_handle: object, *, mode: str = "production"
    ) -> TrustedHumanGrant:
        if type(mode) is not str or mode != "test":
            raise TrustBoundaryError(
                "deterministic trust fixtures are forbidden in production",
                AUTH_FIXTURE_IN_PRODUCTION,
            )
        if type(opaque_handle) is not str:
            raise TrustBoundaryError("unknown deterministic fixture handle")
        record = self._records.get(opaque_handle)
        if record is None:
            raise TrustBoundaryError("unknown deterministic fixture handle")
        try:
            return _trusted_grant_from_record(record, trust_source="test_fixture")
        except AuthorizationInputError as exc:
            raise TrustBoundaryError(str(exc)) from exc


_FORBIDDEN_DIRECTORY_NAMES = frozenset(
    {
        ".aws",
        ".azure",
        ".docker",
        ".git",
        ".gnupg",
        ".kube",
        ".ssh",
        "secrets",
        "credentials",
        "private_keys",
    }
)
_FORBIDDEN_EXACT_FILENAMES = frozenset(
    {
        ".git-credentials",
        ".netrc",
        ".npmrc",
        ".pypirc",
        "id_rsa",
        "id_ed25519",
        "credentials.json",
        "application_default_credentials.json",
        "service-account.json",
        "service_account.json",
        "token.json",
    }
)
_FORBIDDEN_FILE_SUFFIXES = frozenset({".pem", ".key", ".p12", ".pfx"})


@dataclass(frozen=True, slots=True)
class ReadonlyAuthorizationPolicy:
    """Non-customizable view of the fixed protected-path policy floor."""

    FORBIDDEN_DIRECTORY_NAMES: ClassVar[frozenset[str]] = (
        _FORBIDDEN_DIRECTORY_NAMES
    )
    FORBIDDEN_EXACT_FILENAMES: ClassVar[frozenset[str]] = (
        _FORBIDDEN_EXACT_FILENAMES
    )
    FORBIDDEN_FILE_SUFFIXES: ClassVar[frozenset[str]] = _FORBIDDEN_FILE_SUFFIXES

    def resource_is_secret(self, resource: ResourceRef) -> bool:
        return _resource_is_secret(resource)


def _resource_is_secret(resource: ResourceRef) -> bool:
    """Apply the fixed protected-path floor independently of policy instances."""

    parts = tuple(part.casefold() for part in PurePosixPath(resource.path).parts)
    if not parts:
        return True
    if any(part in _FORBIDDEN_DIRECTORY_NAMES for part in parts):
        return True
    if any(part == ".env" or part.startswith(".env.") for part in parts):
        return True
    filename = parts[-1]
    if filename in _FORBIDDEN_EXACT_FILENAMES:
        return True
    return any(filename.endswith(suffix) for suffix in _FORBIDDEN_FILE_SUFFIXES)


@dataclass(frozen=True, slots=True)
class ReadonlyReplaySnapshot:
    """Host-supplied point-in-time evidence, not a nonce-consumption store.

    P0 performs only membership testing against this immutable snapshot.  It
    neither consumes a successful nonce nor persists changes, so atomic and
    cross-process replay protection remain external host responsibilities.
    """

    consumed_nonces: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if type(self.consumed_nonces) is not frozenset or any(
            type(nonce) is not str or not nonce
            for nonce in self.consumed_nonces
        ):
            raise AuthorizationInputError(
                "consumed_nonces must be an immutable frozenset of non-empty strings"
            )


@dataclass(frozen=True, eq=False)
class AuthorizationDecision:
    status: str
    reason_codes: tuple[str, ...]
    authorization_context: Mapping[str, Any] | None
    requested_effect: Mapping[str, Any]
    audit: Mapping[str, Any]
    _seal: object = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._seal is not _DECISION_SEAL:
            raise TrustBoundaryError(
                "AuthorizationDecision must be created by verify_authorization"
            )

    def is_factory_issued(self) -> bool:
        if type(self) is not AuthorizationDecision or self._seal is not _DECISION_SEAL:
            return False
        try:
            issued = _ISSUED_DECISIONS.get(self)
            if type(issued) is not _DecisionIssuance:
                return False
            if (
                type(self.status) is not str
                or type(self.reason_codes) is not tuple
                or any(type(code) is not str for code in self.reason_codes)
                or self.status != issued.status
                or self.reason_codes != issued.reason_codes
                or self.authorization_context is not issued.authorization_context
                or self.requested_effect is not issued.requested_effect
                or self.audit is not issued.audit
            ):
                return False
            current = _decision_fingerprint(self)
        except Exception:
            return False
        return hmac.compare_digest(issued.fingerprint, current)

    def to_dict(self) -> dict[str, Any]:
        """Return an audit/transport snapshot, never reusable as trusted input."""
        return {
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "authorization_context": _deep_thaw(self.authorization_context),
            "requested_effect": _deep_thaw(self.requested_effect),
            "audit": _deep_thaw(self.audit),
        }


@dataclass(frozen=True, slots=True)
class _DecisionIssuance:
    fingerprint: str
    status: str
    reason_codes: tuple[str, ...]
    authorization_context: Mapping[str, Any] | None
    requested_effect: Mapping[str, Any]
    audit: Mapping[str, Any]


def _deep_frozen_snapshot(value: Any, field_name: str) -> Any:
    if type(value) is MappingProxyType:
        result: dict[str, Any] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise AuthorizationInputError(
                    f"{field_name} keys must be exact strings"
                )
            result[key] = _deep_frozen_snapshot(item, f"{field_name}.{key}")
        return result
    if type(value) is tuple:
        return [
            _deep_frozen_snapshot(item, f"{field_name}[]") for item in value
        ]
    if type(value) in {str, int, float, bool, type(None)}:
        return value
    raise AuthorizationInputError(
        f"{field_name} must contain only owned immutable built-in values"
    )


def _decision_fingerprint(decision: AuthorizationDecision) -> str:
    if type(decision) is not AuthorizationDecision:
        raise AuthorizationInputError("issued decision must be exact")
    if type(decision.status) is not str or type(decision.reason_codes) is not tuple:
        raise AuthorizationInputError("issued decision scalar fields are invalid")
    if any(type(code) is not str for code in decision.reason_codes):
        raise AuthorizationInputError("issued decision reason codes must be strings")
    context = (
        None
        if decision.authorization_context is None
        else _deep_frozen_snapshot(
            decision.authorization_context, "authorization_context"
        )
    )
    return _issuance_fingerprint(
        {
            "status": decision.status,
            "reason_codes": list(decision.reason_codes),
            "authorization_context": context,
            "requested_effect": _deep_frozen_snapshot(
                decision.requested_effect, "requested_effect"
            ),
            "audit": _deep_frozen_snapshot(decision.audit, "audit"),
        }
    )


def _issue_decision(decision: AuthorizationDecision) -> AuthorizationDecision:
    _ISSUED_DECISIONS[decision] = _DecisionIssuance(
        fingerprint=_decision_fingerprint(decision),
        status=decision.status,
        reason_codes=decision.reason_codes,
        authorization_context=decision.authorization_context,
        requested_effect=decision.requested_effect,
        audit=decision.audit,
    )
    return decision


def _observed_gate(value: Any) -> str | None:
    if value is None:
        return None
    if type(value) is str:
        return value[:64]
    return "<non-string>"


def _requested_effect(
    request: AuthorizationRequest | _RequestSnapshot,
) -> dict[str, Any]:
    return {
        "task_id": request.task_id,
        "request_id": request.request_id,
        "source_head": request.source_head,
        "operation": request.operation,
        "effect_class": request.effect_class,
        "resources": [_resource_ref_snapshot(item) for item in request.resources],
        "gate_phase": request.gate_phase,
    }


def _finish(
    status: str,
    codes: Sequence[str],
    request: AuthorizationRequest | _RequestSnapshot,
    context: Mapping[str, Any] | None = None,
) -> AuthorizationDecision:
    final_codes = list(codes)
    observed = _observed_gate(request.payload_human_gate)
    if observed is not None and AUTH_PAYLOAD_GATE_IGNORED not in final_codes:
        final_codes.append(AUTH_PAYLOAD_GATE_IGNORED)
    return _issue_decision(
        AuthorizationDecision(
            status=status,
            reason_codes=tuple(final_codes),
            authorization_context=(
                _deep_freeze(context) if context is not None else None
            ),
            requested_effect=_deep_freeze(_requested_effect(request)),
            audit=_deep_freeze(
                {
                    "payload_human_gate_observed": observed,
                    "payload_human_gate_used_for_authorization": False,
                }
            ),
            _seal=_DECISION_SEAL,
        )
    )


def _reject_untrusted_request() -> AuthorizationDecision:
    """Reject a direct, copied, or duck-typed request without inspecting it."""

    return _issue_decision(
        AuthorizationDecision(
            status="deny",
            reason_codes=(AUTH_REQUEST_SCHEMA_INVALID,),
            authorization_context=None,
            requested_effect=_deep_freeze(
                {
                    "task_id": None,
                    "request_id": None,
                    "source_head": None,
                    "operation": None,
                    "effect_class": None,
                    "resources": [],
                    "gate_phase": None,
                }
            ),
            audit=_deep_freeze(
                {
                    "payload_human_gate_observed": None,
                    "payload_human_gate_used_for_authorization": False,
                }
            ),
            _seal=_DECISION_SEAL,
        )
    )


def is_verified_authorization_decision(value: Any) -> bool:
    """Return true only for an in-process decision emitted by this verifier."""

    return (
        type(value) is AuthorizationDecision
        and AuthorizationDecision.is_factory_issued(value)
    )


def get_verified_authorization_snapshot(
    value: Any,
) -> tuple[str, Mapping[str, Any] | None, Mapping[str, Any]] | None:
    """Return issuer-owned immutable fields, never caller-replaced fields."""

    if not is_verified_authorization_decision(value):
        return None
    issued = _ISSUED_DECISIONS.get(value)
    if type(issued) is not _DecisionIssuance:
        return None
    return (
        issued.status,
        issued.authorization_context,
        issued.requested_effect,
    )


def _authorization_context(
    request: AuthorizationRequest | _RequestSnapshot,
    grant: TrustedHumanGrant | _GrantSnapshot,
    now: datetime,
    reason_codes: Sequence[str],
    replay_snapshot_supplied: bool,
) -> dict[str, Any]:
    context_id = sha256(
        (
            f"{grant.envelope_id}|{request.task_id}|{request.request_id}|"
            f"{request.operation}|{request.source_head}"
        ).encode("utf-8")
    ).hexdigest()[:24]
    observed = _observed_gate(request.payload_human_gate)
    return {
        "schema_version": "math_mentor.authorization_context.v1",
        "authorization_id": f"authz-{context_id}",
        "authority": {
            "authority_class": grant.authority_class,
            "principal_type": "human_speaker",
            "principal_ref": grant.principal_ref,
            "channel": grant.channel,
            "evidence_ref": grant.evidence_ref,
            "authenticated": True,
        },
        "binding": {
            "task_id": request.task_id,
            "request_id": request.request_id,
            "objective_sha256": request.objective_sha256,
            "source_head": request.source_head,
            "operation": request.operation,
            "effect_class": request.effect_class,
            "resources": [
                _resource_ref_snapshot(item) for item in request.resources
            ],
        },
        "grant": {
            "allowed_operations": sorted(grant.allowed_operations),
            "resource_selectors": [
                _resource_selector_snapshot(item)
                for item in grant.resource_selectors
            ],
            "effect_ceiling": grant.effect_ceiling,
            "explicitly_denied_operations": sorted(
                grant.explicitly_denied_operations
            ),
        },
        "validity": {
            "issued_at": _format_time(grant.issued_at),
            "not_before": _format_time(grant.not_before),
            "expires_at": _format_time(grant.expires_at),
            "revocation_ref": grant.revocation_ref,
            "nonce": grant.nonce,
            "one_time": grant.one_time,
            "replay_status": (
                "not_present_in_supplied_snapshot"
                if replay_snapshot_supplied
                else "snapshot_not_supplied"
            ),
            "replay_snapshot_scope": "host_supplied_readonly_snapshot_only",
            "atomic_nonce_consumption_implemented": False,
            "nonce_persistence_implemented": False,
            "cross_process_replay_protection_implemented": False,
        },
        "gates": {
            "pre_action": grant.pre_action,
            "post_completion": grant.post_completion,
            "post_completion_approval_ref": grant.post_completion_approval_ref,
        },
        "verification": {
            "decision": "allow",
            "verifier_version": "math_mentor.authorization_verifier.v1",
            "verified_at": _format_time(now),
            "reason_codes": list(reason_codes),
            "payload_human_gate_observed": observed,
            "payload_human_gate_used_for_authorization": False,
        },
    }


def verify_authorization(
    request: Any,
    trusted_grant: TrustedHumanGrant | None,
    *,
    policy: ReadonlyAuthorizationPolicy | None = None,
    replay_snapshot: ReadonlyReplaySnapshot | None = None,
    now: datetime | None = None,
    environment_mode: str = "production",
) -> AuthorizationDecision:
    """Verify an exact requested effect against externally trusted evidence.

    ``replay_snapshot`` is point-in-time evidence supplied by the host.  This
    local verifier does not update it, atomically consume the nonce, persist
    nonce state, or coordinate replay protection across processes.
    """

    request_snapshot = _verified_request_snapshot(request)
    if request_snapshot is None:
        return _reject_untrusted_request()
    request = request_snapshot
    if policy is not None and type(policy) is not ReadonlyAuthorizationPolicy:
        raise AuthorizationInputError("policy must be a ReadonlyAuthorizationPolicy")
    policy = policy or ReadonlyAuthorizationPolicy()
    if replay_snapshot is not None and type(replay_snapshot) is not ReadonlyReplaySnapshot:
        raise AuthorizationInputError(
            "replay_snapshot must be a ReadonlyReplaySnapshot"
        )
    replay_snapshot_supplied = replay_snapshot is not None
    observed_nonces = (
        frozenset() if replay_snapshot is None else replay_snapshot.consumed_nonces
    )
    if type(observed_nonces) is not frozenset or any(
        type(nonce) is not str or not nonce
        for nonce in observed_nonces
    ):
        raise AuthorizationInputError(
            "replay_snapshot must contain an exact frozenset of strings"
        )
    consumed_nonces = frozenset(observed_nonces)
    if (
        request.operation == "secret.read"
        or request.effect_class == "secret_or_privacy"
        or any(_resource_is_secret(item) for item in request.resources)
    ):
        return _finish("deny", [AUTH_SECRET_SCOPE_FORBIDDEN], request)
    if type(environment_mode) is not str or environment_mode not in {
        "production",
        "test",
    }:
        return _finish("deny", [AUTH_INDETERMINATE], request)
    if now is not None and (
        type(now) is not datetime or now.tzinfo is not timezone.utc
    ):
        raise AuthorizationInputError("now must be an exact UTC datetime")
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    if trusted_grant is None:
        return _finish("human_required", [AUTH_CONTEXT_MISSING], request)
    grant_snapshot = _verified_grant_snapshot(trusted_grant)
    if grant_snapshot is None:
        return _finish("deny", [AUTH_ENVELOPE_UNTRUSTED], request)
    trusted_grant = grant_snapshot
    if trusted_grant.trust_source == "test_fixture" and environment_mode != "test":
        return _finish("deny", [AUTH_FIXTURE_IN_PRODUCTION], request)

    checks: list[str] = []
    if trusted_grant.authority_class not in AUTHORITY_CLASSES:
        checks.append(AUTH_PRINCIPAL_INVALID)
    if trusted_grant.task_id != request.task_id:
        checks.append(AUTH_TASK_MISMATCH)
    if trusted_grant.request_id != request.request_id:
        checks.append(AUTH_REQUEST_MISMATCH)
    if trusted_grant.objective_sha256 != request.objective_sha256:
        checks.append(AUTH_OBJECTIVE_MISMATCH)
    if trusted_grant.source_head != request.source_head:
        checks.append(AUTH_SOURCE_HEAD_MISMATCH)
    if trusted_grant.revoked:
        checks.append(AUTH_REVOKED)
    if now < trusted_grant.not_before:
        checks.append(AUTH_NOT_YET_VALID)
    if trusted_grant.expires_at is not None and now >= trusted_grant.expires_at:
        checks.append(AUTH_EXPIRED)
    if trusted_grant.nonce in consumed_nonces:
        checks.append(AUTH_NONCE_REPLAY)
    if checks:
        return _finish("deny", checks, request)

    missing_scope: list[str] = []
    if (
        request.operation in trusted_grant.explicitly_denied_operations
        or request.operation not in trusted_grant.allowed_operations
    ):
        missing_scope.append(AUTH_OPERATION_NOT_GRANTED)
    if EFFECT_RANK[request.effect_class] > EFFECT_RANK[trusted_grant.effect_ceiling]:
        missing_scope.append(AUTH_EFFECT_CEILING_EXCEEDED)
    for resource in request.resources:
        if not any(
            _resource_selector_matches(selector, resource, request.operation)
            for selector in trusted_grant.resource_selectors
        ):
            missing_scope.append(AUTH_RESOURCE_NOT_GRANTED)
            break
    if missing_scope:
        return _finish("human_required", missing_scope, request)

    if (
        request.gate_phase == "post_completion"
        and trusted_grant.post_completion != "satisfied"
    ):
        return _finish(
            "human_required", [AUTH_POST_COMPLETION_GATE_REQUIRED], request
        )

    reason_codes = [AUTH_OK]
    if request.payload_human_gate is not None:
        reason_codes.append(AUTH_PAYLOAD_GATE_IGNORED)
    context = _authorization_context(
        request,
        trusted_grant,
        now,
        reason_codes,
        replay_snapshot_supplied,
    )
    return _finish("allow", reason_codes, request, context)


__all__ = [
    "AuthorizationDecision",
    "AuthorizationInputError",
    "AuthorizationRequest",
    "DeterministicTestTrustBoundaryAdapter",
    "ProductionTrustBoundaryAdapter",
    "ReadonlyAuthorizationPolicy",
    "ReadonlyReplaySnapshot",
    "ResourceRef",
    "ResourceSelector",
    "TrustBoundaryAdapter",
    "TrustBoundaryError",
    "TrustedHumanGrant",
    "get_verified_authorization_snapshot",
    "is_verified_authorization_decision",
    "verify_authorization",
]

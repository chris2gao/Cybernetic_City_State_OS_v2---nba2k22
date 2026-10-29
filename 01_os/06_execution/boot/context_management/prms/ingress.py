"""Foreground trusted-host port; disabled by default, no credential provisioning.

The host owns authentication, immutable grants and the backend transport. The
request carries an opaque authentication context, never self-declared session or
scope claims. Deploy this object outside the model's execution/credential domain.
Same-process Python encapsulation does not establish that boundary. Offline
adapter tests prove IMPLEMENTED_UNVERIFIED_PLATFORM only, never enforced ACLs.
"""
from dataclasses import dataclass
import math
import time
from typing import Protocol

from source import PRMSError
from state import WriterGate, identifier
from memory import copy_all_memory


@dataclass(frozen=True)
class CopyGrant:
    source_role: str
    target_role: str
    source_commit: str
    approval_ref: str


@dataclass(frozen=True)
class HostSession:
    session_id: str
    subject: str
    authority_ref: str
    expires_at: float
    allowed_roles: tuple[str, ...]
    allowed_tasks: tuple[str, ...]
    allowed_operations: tuple[str, ...]
    copy_grants: tuple[CopyGrant, ...] = ()


class HostAuthority(Protocol):
    def authenticate(self, authentication_context: object) -> HostSession:
        """Verify host identity, expiry and revocation against trusted records.

        Return host-held grants, not fields copied from an unverified request.
        Raise on invalid, revoked, replayed or incorrectly bound credentials.
        Concrete credential/identity-provider integration is deployment-owned.
        """


class TrustedIngress:
    implementation_status = "IMPLEMENTED_UNVERIFIED_PLATFORM"

    def __init__(self, store, authority: HostAuthority | None = None, *, enabled=False, clock=time.time):
        self._gate = WriterGate(store)
        self._authority = authority
        self._enabled = enabled
        self._clock = clock
        self._bindings = {}
        self._revoked = set()

    def revoke_session(self, session_id):
        """Host control-plane method; never expose as a model-selected route."""
        identifier(session_id)
        self._revoked.add(session_id)
        binding = self._bindings.pop(session_id, None)
        if binding:
            self._gate.revoke_isolated_session(binding[1])

    def _authenticate(self, context):
        if not self._enabled:
            raise PRMSError("INGRESS_DISABLED", "trusted ingress is dormant")
        if self._authority is None:
            raise PRMSError("AUTHORITY_UNVERIFIED", "host authenticator required")
        try:
            grant = self._authority.authenticate(context)
        except Exception:
            # Authentication errors and context values can contain secrets.
            raise PRMSError("AUTHORITY_UNVERIFIED", "host authentication refused") from None
        if not isinstance(grant, HostSession):
            raise PRMSError("AUTHORITY_UNVERIFIED", "host-authenticated session record required")
        identifier(grant.session_id)
        if (not isinstance(grant.subject, str) or not grant.subject
                or not isinstance(grant.authority_ref, str) or not grant.authority_ref
                or type(grant.expires_at) not in (int, float) or not math.isfinite(grant.expires_at)
                or grant.expires_at <= self._clock() or grant.session_id in self._revoked):
            raise PRMSError("AUTHORITY_UNVERIFIED", "expired, revoked or unbound host session")
        for field in (grant.allowed_roles, grant.allowed_tasks, grant.allowed_operations, grant.copy_grants):
            if not isinstance(field, tuple):
                raise PRMSError("AUTHORITY_UNVERIFIED", "host scopes must be immutable explicit tuples")
        for item in grant.allowed_roles + grant.allowed_tasks + grant.allowed_operations:
            identifier(item)
        if not all(isinstance(item, CopyGrant) for item in grant.copy_grants):
            raise PRMSError("AUTHORITY_UNVERIFIED", "host copy grants required")
        old = self._bindings.get(grant.session_id)
        if old and old[0] != grant:
            self.revoke_session(grant.session_id)
            raise PRMSError("AUTHORITY_UNVERIFIED", "session binding changed; issue a new session identity")
        if not old:
            scopes = [dict(source_role=x.source_role, target_role=x.target_role,
                           source_commit=x.source_commit, approval_ref=x.approval_ref) for x in grant.copy_grants]
            capability = self._gate._bind_host_session(grant.session_id, grant.allowed_roles,
                allowed_tasks=grant.allowed_tasks, allowed_operations=grant.allowed_operations,
                allowed_copy_scopes=scopes)
            self._bindings[grant.session_id] = (grant, capability)
        return self._bindings[grant.session_id]

    def mutate(self, authentication_context, role_id, *, operation_id, expected_head,
               expected_version, expected_epoch, kind, payload):
        grant, capability = self._authenticate(authentication_context)
        def revalidate(_candidate):
            if self._authenticate(authentication_context) != (grant, capability):
                raise PRMSError("AUTHORITY_UNVERIFIED", "session changed before publication")
        result = self._gate.apply(capability, role_id, operation_id=operation_id,
            expected_head=expected_head, expected_version=expected_version,
            expected_epoch=expected_epoch, kind=kind, payload=payload, before_publish=revalidate)
        return {**result, "ingress_status": self.implementation_status,
                "platform_enforcement": "NOT_VERIFIED"}

    def copy(self, authentication_context, source_role, target_role, *, source_commit,
             operation_id, expected_head, approval_ref):
        grant, capability = self._authenticate(authentication_context)
        def revalidate(_candidate):
            if self._authenticate(authentication_context) != (grant, capability):
                raise PRMSError("AUTHORITY_UNVERIFIED", "session changed before copy publication")
        result = copy_all_memory(self._gate.store, self._gate, capability, source_role, target_role,
            source_head=source_commit, operation_id=operation_id, target_expected_head=expected_head,
            scope_approval_ref=approval_ref, before_publish=revalidate)
        return {**result, "ingress_status": self.implementation_status,
                "platform_enforcement": "NOT_VERIFIED"}

    def recover(self, authentication_context, role_id):
        _, capability = self._authenticate(authentication_context)
        self._gate.authorize_operation(capability, role_id, "RECOVER")
        return self._gate.recover(role_id)

    def require_enforced(self):
        # No enabled flag or injected authenticator proves actual platform ACLs.
        self._gate.require_enforced()

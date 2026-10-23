"""Fixed-manifest policy model with MOCK fixtures only, not a live safety claim.

Executor cannot register ranges. Caller supplies an independently pinned policy
digest; editing both trust inputs or calling a different backend is outside this
model. A production adapter must still bind a real PID, image and sensitive map.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from types import MappingProxyType


class Denied(ValueError):
    pass


@dataclass(frozen=True)
class Binding:
    pid: int
    creation_token: str
    image_sha256: str
    module_base: int
    context: str


@dataclass(frozen=True)
class Permit:
    key: str
    phase: str
    address: int
    size: int
    calls: int


@dataclass(frozen=True)
class Policy:
    digest: str
    binding: Binding
    permits: tuple
    budgets: tuple
    denied_ranges: tuple

    @classmethod
    def load(cls, path, externally_pinned_sha256):
        raw = Path(path).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != externally_pinned_sha256:
            raise Denied('Policy digest differs from external trust input')
        data = json.loads(raw)
        if data['mode'] != 'OFFLINE_MOCK_ONLY_NOT_HUMAN_LIVE_AUTHORIZATION':
            raise Denied('This model has no live adapter')
        b = data['binding']
        binding = Binding(b['pid'], b['creation_token'], b['image_sha256'], int(b['module_base'], 16), b['context'])
        budgets = tuple((k, v) for k, v in data['phase_budgets'].items())
        permits = tuple(Permit(p['key'], p['phase'], int(p['address'], 16), p['size'], p['max_calls']) for p in data['permits'])
        denied = tuple((int(p['address'], 16), p['size']) for p in data['denied_ranges'])
        if len({p.key for p in permits}) != len(permits) or any(type(v) is not int or v < 0 for _, v in budgets):
            raise Denied('Invalid manifest')
        if any(p.phase not in dict(budgets) or p.size <= 0 or p.calls <= 0 or p.address < 0 or p.address+p.size > 2**64 for p in permits):
            raise Denied('Invalid permit')
        return cls(digest, binding, permits, budgets, denied)


class MockBackend:
    """Exact immutable byte fixtures. Cannot attach to Windows or dereference."""
    def __init__(self, binding, fixtures):
        self.binding = binding
        self.fixtures = MappingProxyType({k: bytes(v) for k, v in fixtures.items()})
        self.calls = []

    def read_fixture(self, address, size):
        self.calls.append((address, size))
        return self.fixtures[address][:size]


class Reader:
    def __init__(self, policy, backend):
        if type(backend) is not MockBackend:
            raise Denied('Only the offline mock backend is supported')
        self.policy, self.backend = policy, backend
        self.permits = MappingProxyType({p.key: p for p in policy.permits})
        self.used = {phase: 0 for phase, _ in policy.budgets}
        self.calls = {p.key: 0 for p in policy.permits}
        self.audit = []
        self.failed = False

    def read(self, key, phase, address, size, binding):
        """The sole mock read boundary, including reads invoked by helpers."""
        p = self.permits.get(key)
        reason = None
        if self.failed:
            reason = 'Reader stopped after failed/partial backend read'
        elif binding != self.policy.binding or self.backend.binding != self.policy.binding:
            reason = 'Process/build/module/context binding mismatch'
        elif p is None or (phase, address, size) != (p.phase, p.address, p.size):
            reason = 'Not an exact fixed permit; helper/changed-range requests denied'
        elif any(address < a+n and a < address+size for a, n in self.policy.denied_ranges):
            reason = 'Sensitive range overrides permit'
        elif self.calls[key] >= p.calls or self.used[phase]+size > dict(self.policy.budgets)[phase]:
            reason = 'Phase/call budget exhausted; no transfer'
        if reason:
            self.audit.append(dict(key=key, phase=phase, status='DENIED', reason=reason))
            raise Denied(reason)
        # Charge BEFORE backend. A failed/short read consumes this attempt.
        self.used[phase] += size
        self.calls[key] += 1
        try:
            raw = self.backend.read_fixture(address, size)
            if len(raw) != size:
                raise Denied('Partial fixture read')
        except Exception:
            self.failed = True
            self.audit.append(dict(key=key, phase=phase, status='FAILED_CHARGED', bytes=size))
            raise
        self.audit.append(dict(key=key, phase=phase, status='MOCK_SUCCESS', bytes=size,
                               sha256=hashlib.sha256(raw).hexdigest()))
        return raw

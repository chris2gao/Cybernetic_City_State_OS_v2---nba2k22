"""Opt-in Human-reviewed G/R/A/D prototypes bound to existing domain capabilities.

This module never generates a script, grants permission, starts a workflow, or
runs a side effect on compilation. It reuses the PR23 Atom/Chain/Executor.
The HOST (not the proposing model) must own review_lookup, capability_catalog,
domain fact readings and per-instance external write authorization.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from copy import deepcopy
import hashlib
import json
from typing import Callable, Mapping
from types import MappingProxyType

from atomic_tasks import Atom, Chain, Executor, Ready


@dataclass(frozen=True)
class Criterion:
    """One Human-auditable Ready/Done requirement and its rationale."""
    key: str
    fact: str
    why: str
    basis: str


@dataclass(frozen=True)
class Operation:
    """One *existing*, version-pinned callable, not steps invented at runtime."""
    capability_id: str
    version: str
    effect: str                    # READ_ONLY or WRITE
    parameters: tuple[str, ...]
    why: str
    procedure_ref: str = ""          # Reviewed immutable capability documentation, alternative to steps


@dataclass(frozen=True)
class ProcedureStep:
    """Human design review of one intended operation/check (not a tool invocation)."""
    key: str
    action: str
    why: str
    basis: str
    execution_owner: str            # CAPABILITY_INTERNAL or HOST_BINDING
    binding: str = ""                # Child key or bound capability; reviewed before use


@dataclass(frozen=True)
class Prototype:
    key: str
    goal: str
    ready: tuple[Criterion, ...]
    done: tuple[Criterion, ...]
    operation: Operation | None = None
    children: tuple["Prototype", ...] = ()
    procedure: tuple[ProcedureStep, ...] = ()  # Reviewed once, never dispatched by this metadata


@dataclass(frozen=True)
class HumanReview:
    """Receipt supplied by trusted Human-side storage; not an approval token."""
    prototype_key: str
    prototype_digest: str
    decision_ref: str
    accepted: bool


@dataclass(frozen=True)
class Capability:
    """Trusted domain-owned implementation registered outside the task document."""
    capability_id: str
    version: str
    effect: str
    invoke: Callable[..., object]
    procedure_ref: str = ""          # Domain catalog's independently registered documentation reference


class NeedsHumanReview(ValueError):
    pass


class CapabilityGap(ValueError):
    pass


def _nodes(root: Prototype) -> tuple[Prototype, ...]:
    seen: set[str] = set()
    result: list[Prototype] = []

    def visit(node: Prototype) -> None:
        if (not node.key or not node.goal or node.key in seen
                or not node.done or bool(node.operation) == bool(node.children)):
            raise ValueError("Unique nonempty task, independent Done, and exactly one action/children required")
        seen.add(node.key)
        keys = [check.key for check in node.ready + node.done]
        if len(keys) != len(set(keys)) or any(
                not all((c.key, c.fact, c.why, c.basis)) for c in node.ready + node.done):
            raise ValueError("Each minimum criterion needs a unique key, fact, reason and basis")
        step_keys = [step.key for step in node.procedure]
        if (len(step_keys) != len(set(step_keys)) or any(
                not all((step.key, step.action, step.why, step.basis))
                or step.execution_owner not in {"CAPABILITY_INTERNAL", "HOST_BINDING"}
                for step in node.procedure)):
            raise ValueError("Procedure steps require unique keys, reasons, basis and declared owner")
        if node.operation:
            op = node.operation
            if (not all((op.capability_id, op.version, op.why))
                    or op.effect not in {"READ_ONLY", "WRITE"}
                    or len(op.parameters) != len(set(op.parameters))
                    or any(not p for p in op.parameters)):
                raise ValueError("Invalid explicitly bound action")
        result.append(node)
        for child in node.children:
            visit(child)

    visit(root)
    return tuple(result)


def _validate_procedure_alignment(nodes: tuple[Prototype, ...]) -> None:
    """No procedural Host action can be promised without an actual bound Atom.

    Review may show proposed excessive/unbound operations for Human correction;
    compilation must reject them, including when a bogus review receipt exists.
    """
    for node in nodes:
        host_steps = [step for step in node.procedure if step.execution_owner == "HOST_BINDING"]
        internal_steps = [step for step in node.procedure if step.execution_owner == "CAPABILITY_INTERNAL"]
        if node.children:
            if internal_steps:
                raise CapabilityGap(f"{node.key}: composite node has no internal callable for procedure steps")
            if host_steps and [step.binding for step in host_steps] != [
                    child.key for child in node.children]:
                raise CapabilityGap(f"{node.key}: Host steps must match actual child calls and order")
        else:
            assert node.operation is not None
            if len(host_steps) > 1 or (
                    host_steps and host_steps[0].binding != node.operation.capability_id):
                raise CapabilityGap(f"{node.key}: unbound extra Host procedure; only existing callable is allowed")
            if any(step.binding and step.binding != node.operation.capability_id
                   for step in internal_steps):
                raise CapabilityGap(f"{node.key}: internal procedure belongs to a different capability")


def digest(prototype: Prototype) -> str:
    """Hash this node's reviewed contract and child identities, not descendant internals.

    An edited leaf must be re-reviewed; unrelated ancestors whose own G/R/A/D and
    child ordering remain unchanged must NOT trigger redundant Human approvals.
    """
    node = asdict(prototype)
    node["children"] = [child.key for child in prototype.children]
    data = json.dumps(node, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def review_packet(root: Prototype) -> tuple[dict, ...]:
    """Inspectable BEFORE execution. Human can challenge every criterion/action."""
    return tuple({
        "key": node.key,
        "goal": node.goal,
        "digest": digest(node),
        "ready": [asdict(c) for c in node.ready],
        "done": [asdict(c) for c in node.done],
        "action": asdict(node.operation) if node.operation else None,
        "procedure": [asdict(step) for step in node.procedure],
        "children": [child.key for child in node.children],
        "status": "PENDING_HUMAN_REVIEW",
    } for node in _nodes(root))


def compile_approved(
    root: Prototype,
    *,
    review_lookup: Callable[[str, str], HumanReview | None],
    capabilities: Mapping[str, Capability],
    bindings: Mapping[str, object],
    read_fact: Callable[[str, Mapping[str, object]], bool],
    authorize_write: Callable[[str, Mapping[str, object]], bool] | None = None,
    guard_before_invoke: Callable[[], None] | None = None,
    on_action_admitted: Callable[[str, str], None] | None = None,
) -> Executor:
    """Compile reviewed prototypes into the EXISTING PR23 Executor; no side effects.

    Human-visible procedure is design metadata, NOT extra runtime commands.
    Review is per node/type: approved reusable task prototype can be bound
    to different runtime instances without re-review. Write authority remains
    instance-specific. The returned executor is NEVER automatically advanced.
    """
    nodes = _nodes(root)
    _validate_procedure_alignment(nodes)
    # R1: an approved title and a callable ID are not an approved procedure.
    # Composite task children are their explicit operation plan; every leaf
    # must provide its concrete reviewed steps or cite fixed-version capability
    # documentation. A draft may still be previewed without either.
    for node in nodes:
        if node.operation and not node.procedure and not node.operation.procedure_ref.strip():
            raise NeedsHumanReview(
                f"{node.key}: concrete ProcedureStep or reviewed pinned capability procedure_ref required"
            )
    # A compiled instance must not change identity/target if the caller later
    # mutates its original bindings. Use a JSON-compatible immutable snapshot;
    # each callback gets a private copy so callbacks cannot modify the snapshot.
    if any(type(key) is not str for key in bindings):
        raise ValueError("Instance binding keys must be strings")
    try:
        bound_instance = MappingProxyType(json.loads(json.dumps(dict(bindings),
                                                             allow_nan=False)))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Instance bindings must be JSON-compatible: {exc}") from exc
    def current_bindings() -> dict[str, object]:
        return deepcopy(dict(bound_instance))

    resolved: dict[str, Capability] = {}
    for node in nodes:
        sha = digest(node)
        approval = review_lookup(node.key, sha)
        if (approval is None or not isinstance(approval, HumanReview)
                or not approval.accepted or approval.prototype_key != node.key
                or approval.prototype_digest != sha or not approval.decision_ref):
            raise NeedsHumanReview(f"{node.key}: Human review for exact prototype digest required")
        if node.operation:
            op = node.operation
            registered = capabilities.get(op.capability_id)
            if (registered is None or registered.capability_id != op.capability_id
                    or registered.version != op.version or registered.effect != op.effect
                    or not callable(registered.invoke)):
                raise CapabilityGap(f"{node.key}: pinned callable not available; no script generation allowed")
            # No model-only document claim: the same immutable reference must
            # also be declared by the Host-owned capability registration.
            if op.procedure_ref and registered.procedure_ref != op.procedure_ref:
                raise CapabilityGap(
                    f"{node.key}: cited capability procedure not present in trusted catalog"
                )
            for key in op.parameters:
                if key not in bound_instance:
                    raise CapabilityGap(f"{node.key}: missing bound parameter {key}")
            resolved[node.key] = registered

    def make(node: Prototype) -> Atom | Chain:
        def check(conditions: tuple[Criterion, ...]) -> bool:
            for criterion in conditions:
                actual = read_fact(criterion.fact, current_bindings())
                if type(actual) is not bool:
                    raise TypeError(f"{criterion.fact}: domain fact must be boolean")
                if not actual:
                    return False
            return True

        def ready() -> Ready:
            if not check(node.ready):
                return Ready(False, "Reviewed minimum Ready not observed")
            if node.operation and node.operation.effect == "WRITE":
                if authorize_write is None or not authorize_write(node.operation.capability_id, current_bindings()):
                    return Ready(False, "Per-instance external write authority missing")
            # If Host mode changed while acquiring Ready, stop before PR23 marks
            # any Action attempted; no real side effect has occurred at this point.
            if guard_before_invoke is not None:
                guard_before_invoke()
            return Ready(True)

        def done() -> bool:
            return check(node.done)

        if node.children:
            return Chain(node.key, node.goal, ready,
                         tuple(make(child) for child in node.children), done)
        assert node.operation is not None
        op = node.operation
        registered = resolved[node.key]
        kwargs = {key: bound_instance[key] for key in op.parameters}

        def action() -> object:
            # Recheck before the side effect; a prototype review is never write consent.
            if op.effect == "WRITE" and (
                    authorize_write is None or not authorize_write(op.capability_id, current_bindings())):
                raise PermissionError("External write authority expired or revoked")
            # Recheck Host mode immediately at the invocation boundary, even if
            # a Ready/fact/authorization callback changed it during inspect().
            if guard_before_invoke is not None:
                guard_before_invoke()
            if on_action_admitted is not None:
                on_action_admitted(node.key, op.capability_id)
            return registered.invoke(**deepcopy(kwargs))

        return Atom(node.key, node.goal, ready, action, done)

    return Executor(make(root))

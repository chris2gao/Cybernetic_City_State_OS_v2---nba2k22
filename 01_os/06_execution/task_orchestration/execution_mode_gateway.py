"""Small mode-separated Host adapter for reviewed task prototypes.

DEFAULT is EXECUTION. This is a callable gateway, not an OS sandbox.
The actual Host must expose *only* this route to an execution-mode Agent and
must independently own mode state, Human decisions, capability registrations,
development permissions and any real filesystem/Native isolation.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Mapping

from atomic_tasks import Advance, Decision, Executor
from reviewed_prototypes import Capability, HumanReview, Prototype, compile_approved


EXECUTION = "EXECUTION"
DEVELOPMENT = "DEVELOPMENT"
DEFAULT_MODE = EXECUTION


class ModeViolation(PermissionError):
    """A requested operation is outside the current Human-selected mode."""


class DevelopmentAuthorizationRequired(PermissionError):
    """The trusted Host did not authorize this development operation."""


@dataclass(frozen=True)
class ModeState:
    """Snapshot returned by trusted Host; agent-authored JSON is not authority."""
    mode: str = DEFAULT_MODE
    task_id: str = ""
    human_decision_ref: str = ""
    scope_ref: str = ""


@dataclass(frozen=True)
class DevelopmentTool:
    """Only tools specifically registered by Host can be dispatched here."""
    name: str
    invoke: Callable[..., object]


class ModeBoundExecutor:
    """PR23 Executor exposed through an immutable EXECUTION-mode session gate."""

    def __init__(self, executor: Executor, ensure_execution: Callable[[], None]):
        self._executor = executor
        self._ensure_execution = ensure_execution

    def inspect(self) -> Decision:
        self._ensure_execution()
        return self._executor.inspect()

    def advance(self) -> Advance:
        # No side-effecting Atom is attempted when Human mode/scope changed.
        self._ensure_execution()
        return self._executor.advance()

    def run_available(self) -> tuple[Advance, ...]:
        # Check before EVERY Atom rather than calling the unguarded bulk method.
        events: list[Advance] = []
        while True:
            event = self.advance()
            events.append(event)
            if event.status != "ADVANCED":
                return tuple(events)


class ExecutionModeGateway:
    """Frozen task session: no method promotes EXECUTION to DEVELOPMENT.

    read_mode and verify_development MUST be trusted Host callbacks; passing
    model-generated 'Human' strings is NOT proof of authentication. It also
    cannot restrict unrelated Shell/GUI tools the Host still exposes directly.
    """

    def __init__(
        self,
        *,
        read_mode: Callable[[], ModeState],
        verify_development: Callable[[ModeState, str, Mapping[str, object]], bool] | None = None,
        development_tools: Mapping[str, DevelopmentTool] | None = None,
    ):
        self._read_mode = read_mode
        initial = read_mode()
        if (not isinstance(initial, ModeState)
                or initial.mode not in {EXECUTION, DEVELOPMENT}
                or (initial.mode == DEVELOPMENT and not all(
                    (initial.task_id, initial.human_decision_ref, initial.scope_ref)))):
            raise ModeViolation("Invalid Host mode or missing development decision/scope")
        self._state = initial
        self._invalidated = False  # a changed Host decision cannot be silently restored
        self._verify_development = verify_development
        self._development_tools = dict(development_tools or {})

    def _require(self, expected: str) -> None:
        if self._invalidated:
            raise ModeViolation("Host mode/scope changed in this session; a new authorized session is required")
        current = self._read_mode()
        if current != self._state:
            self._invalidated = True
            raise ModeViolation("Host mode/task/scope changed; recompile or open a new authorized session")
        if current.mode != expected:
            raise ModeViolation(
                f"{expected} operation denied in {current.mode} mode; "
                "Human must authorize a new task session, not an Agent mode switch"
            )

    def compile_execution(
        self,
        root: Prototype,
        *,
        review_lookup: Callable[[str, str], HumanReview | None],
        capabilities: Mapping[str, Capability],
        bindings: Mapping[str, object],
        read_fact: Callable[[str, Mapping[str, object]], bool],
        authorize_write: Callable[[str, Mapping[str, object]], bool] | None = None,
    ) -> ModeBoundExecutor:
        """Only pre-reviewed, version-bound actions can run in EXECUTION mode."""
        self._require(EXECUTION)
        compiled = compile_approved(
            root,
            review_lookup=review_lookup,
            capabilities=capabilities,
            bindings=bindings,
            read_fact=read_fact,
            authorize_write=authorize_write,
            guard_before_invoke=lambda: self._require(EXECUTION),
        )
        return ModeBoundExecutor(compiled, lambda: self._require(EXECUTION))

    def invoke_development(self, name: str, *, args: Mapping[str, object]) -> object:
        """Use a separately Human-authorized Host tool only in DEVELOPMENT mode.

        Scope enforcement and the physical tool implementation belong to Host.
        No generic shell fallback, mode escalation or automatic action invention.
        """
        self._require(DEVELOPMENT)
        tool = self._development_tools.get(name)
        if tool is None or tool.name != name or not callable(tool.invoke):
            raise ModeViolation(f"Development tool {name!r} is not registered by Host")
        if any(type(key) is not str for key in args):
            raise ValueError("Development argument names must be strings")
        try:
            import json
            frozen_args = json.loads(json.dumps(dict(args), allow_nan=False))
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Development arguments must be JSON-compatible: {exc}") from exc
        if (self._verify_development is None
                or self._verify_development(self._state, name, deepcopy(frozen_args)) is not True):
            raise DevelopmentAuthorizationRequired(
                "Human development authorization missing/invalid for task, scope or tool"
            )
        self._require(DEVELOPMENT)  # revoke/changing scope prevents invocation
        return tool.invoke(**deepcopy(frozen_args))

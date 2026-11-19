"""Small outcome-driven task composition for *trusted, in-process* domain actions.

This is a business-loop helper, not a command runner, scheduler, permission system,
Workflow stage, or evidence store. Callers supply real readiness, action and
business-outcome functions. The helper cannot grant authority for side effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Union


@dataclass(frozen=True)
class Ready:
    ok: bool
    reason: str = ""


@dataclass(frozen=True)
class Atom:
    key: str
    goal: str
    ready: Callable[[], Ready]
    action: Callable[[], object]
    done: Callable[[], bool]


@dataclass(frozen=True)
class Chain:
    key: str
    goal: str
    ready: Callable[[], Ready]
    children: tuple["Task", ...]
    done: Callable[[], bool]


Task = Union[Atom, Chain]


@dataclass(frozen=True)
class Decision:
    status: str
    node: str
    reason: str = ""


@dataclass(frozen=True)
class Advance:
    status: str
    node: str
    next: Decision
    reason: str = ""


class Executor:
    """Advance the first ready unfinished business node, once per action.

    Safety invariant: if an action was attempted but its actual Done cannot be
    observed, this instance never silently retries the action. A restarted
    process must reconcile the real world through its domain adapter / journal;
    this small in-memory helper is NOT a durable replay-prevention mechanism.
    """

    def __init__(self, root: Task):
        self.root = root
        self._attempted: set[str] = set()
        self._validate_tree(root, set())

    @staticmethod
    def _validate_tree(task: Task, known: set[str]) -> None:
        if not task.key or not task.goal or task.key in known:
            raise ValueError("Task keys must be unique and goals nonempty")
        known.add(task.key)
        if isinstance(task, Chain):
            if not task.children:
                raise ValueError("A chain requires at least one child")
            for child in task.children:
                Executor._validate_tree(child, known)

    @staticmethod
    def _done(task: Task) -> bool:
        observed = task.done()
        if type(observed) is not bool:
            raise TypeError("Done must report an actual boolean observation")
        return observed

    @staticmethod
    def _ready(task: Task) -> Ready:
        observed = task.ready()
        if not isinstance(observed, Ready) or type(observed.ok) is not bool:
            raise TypeError("Ready must return Ready(ok=bool, reason=str)")
        return observed

    def inspect(self) -> Decision:
        """Find current work without executing an action or making a receipt."""
        return self._inspect(self.root)

    def _inspect(self, task: Task) -> Decision:
        try:
            if self._done(task):
                return Decision("DONE", task.key)
            readiness = self._ready(task)
        except Exception as exc:
            return Decision("OBSERVATION_ERROR", task.key, f"{type(exc).__name__}: {exc}")
        if not readiness.ok:
            return Decision("BLOCKED", task.key, readiness.reason)
        if isinstance(task, Chain):
            for child in task.children:
                child_state = self._inspect(child)
                if child_state.status != "DONE":
                    return child_state
            return Decision("PARENT_INCOMPLETE", task.key, "Children are done but parent Done is false")
        if task.key in self._attempted:
            return Decision("RECONCILE", task.key, "Action attempted without confirmed Done; do not replay")
        return Decision("READY", task.key)

    def _lookup(self, task: Task, key: str) -> Atom | None:
        if task.key == key:
            return task if isinstance(task, Atom) else None
        if isinstance(task, Chain):
            for child in task.children:
                result = self._lookup(child, key)
                if result is not None:
                    return result
        return None

    def advance(self) -> Advance:
        """Run at most one real action; never infer Done from a return code."""
        current = self.inspect()
        if current.status != "READY":
            return Advance(current.status, current.node, current, current.reason)
        atom = self._lookup(self.root, current.node)
        assert atom is not None  # READY is only returned for an Atom
        self._attempted.add(atom.key)  # mark before any possible side effect
        try:
            atom.action()
        except Exception as exc:
            return Advance("ACTION_UNCERTAIN", atom.key, self.inspect(),
                           f"Action raised {type(exc).__name__}; reconcile external effects before retry")
        after = self.inspect()
        if after.status == "RECONCILE" and after.node == atom.key:
            return Advance("NOT_DONE", atom.key, after, "Action returned but business Done was not observed")
        if after.status == "OBSERVATION_ERROR" and after.node == atom.key:
            return Advance("NOT_DONE", atom.key, after, "Done could not be verified; reconcile before replay")
        return Advance("ADVANCED", atom.key, after)

    def run_available(self) -> tuple[Advance, ...]:
        """Advance only the finite, existing child chain until complete/blocker.

        No scheduler, polling, backoff or automatic retry. Each Atom can run once
        in this instance; unknown side effects require domain-level reconciliation.
        """
        events: list[Advance] = []
        while True:
            step = self.advance()
            events.append(step)
            if step.status != "ADVANCED":
                return tuple(events)

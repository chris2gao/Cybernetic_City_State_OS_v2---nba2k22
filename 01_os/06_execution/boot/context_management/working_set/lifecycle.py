#!/usr/bin/env python3
"""Lifecycle state model for accumulating groups.

The enum is not invented here. It is the run-state list already declared in
`01_os/开发入口与单窗口任务规范_v1.md` section 5. This module only adds the
classification layer the archive mechanism needs — which of those states is
terminal — and refuses to guess about anything outside the enum.

Refusing to guess is the load-bearing behaviour. On d9a18b57 the 50 run groups
carried 24 mutually distinct free-text status strings, so a lenient parser would
have happily "classified" all of them and produced a confident wrong answer.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

OPEN_STATES = frozenset(
    {
        "research_only",
        "candidate_pending_validation",
        "candidate_ready_for_independent_review",
    }
)

TERMINAL_STATES = frozenset(
    {
        "verified_on_demand",
        "integrated_and_verified_on_demand",
        "deferred",
        "excluded",
    }
)

OPEN = "open"
TERMINAL = "terminal"
UNKNOWN = "unknown"

CLOSURE_RECORD_KEYS = frozenset(
    {"completion_pointer", "human_acceptance", "exclusion_or_deferral"}
)


class WorkingSetError(Exception):
    """Raised when the tree cannot support a claim the caller wants to make."""


@dataclass(frozen=True)
class GroupState:
    group_id: str
    group_path: Path
    state_file: Path | None
    state_raw: str | None
    classification: str
    closure_record_ref: str | None
    closure_record_path: Path | None

    @property
    def is_terminal(self) -> bool:
        return self.classification == TERMINAL


def classify(state: str | None) -> str:
    """Map a raw state string onto open / terminal / unknown.

    Anything not literally in the declared enum is UNKNOWN. A free-text status
    is not evidence of a state.
    """
    if state is None:
        return UNKNOWN
    value = state.strip()
    if value in TERMINAL_STATES:
        return TERMINAL
    if value in OPEN_STATES:
        return OPEN
    return UNKNOWN


def _load_mapping(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise WorkingSetError(f"state_file_unreadable:{path.name}") from exc
    if not isinstance(data, dict):
        raise WorkingSetError(f"state_file_not_a_mapping:{path.name}")
    return data


def read_group_state(
    group_path: Path,
    *,
    state_file: str | None = "run.yml",
    state_field: str = "lifecycle",
) -> GroupState:
    """Read one group's lifecycle state from the physical tree.

    A missing state file is UNKNOWN, never an error: 18 of the 50 groups on
    d9a18b57 have no run.yml at all, and that is exactly the condition the
    archive gate must refuse rather than crash on.
    """
    group_id = group_path.name
    if state_file is None:
        return GroupState(group_id, group_path, None, None, UNKNOWN, None, None)

    path = group_path / state_file
    if not path.is_file():
        return GroupState(group_id, group_path, None, None, UNKNOWN, None, None)

    data = _load_mapping(path)
    raw = data.get(state_field)
    state_raw = raw.strip() if isinstance(raw, str) else None
    closure_ref = data.get("closure_record")
    closure_ref = closure_ref if isinstance(closure_ref, str) and closure_ref else None

    closure_path: Path | None = None
    if closure_ref is not None:
        candidate = (group_path / closure_ref).resolve()
        try:
            candidate.relative_to(group_path.resolve())
        except ValueError:
            raise WorkingSetError(
                f"closure_record_outside_group:{group_id}"
            ) from None
        closure_path = candidate

    return GroupState(
        group_id=group_id,
        group_path=group_path,
        state_file=path,
        state_raw=state_raw,
        classification=classify(state_raw),
        closure_record_ref=closure_ref,
        closure_record_path=closure_path,
    )


def validate_closure_record(state: GroupState) -> str:
    """Prove a closure record physically exists and carries a closure key.

    Mirrors the already-proven shape in the communication archiver: the caller
    declares a relative ref, the ref must resolve inside the group, the target
    must be readable, and it must parse as a mapping carrying real content.
    A boolean from the caller is never accepted.
    """
    if state.closure_record_ref is None:
        raise WorkingSetError(f"closure_record_not_declared:{state.group_id}")
    if state.closure_record_path is None or not state.closure_record_path.is_file():
        raise WorkingSetError(f"closure_record_unreadable:{state.group_id}")
    data = _load_mapping(state.closure_record_path)
    present = sorted(CLOSURE_RECORD_KEYS & set(data))
    if not present:
        raise WorkingSetError(f"closure_record_has_no_closure_key:{state.group_id}")
    return state.closure_record_ref

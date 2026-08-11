"""Minimal discovery and Human/current validation and update."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

VALIDATOR_ROOT = Path(__file__).resolve().parents[1] / "validator"
import sys
if str(VALIDATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_ROOT))
from validate_communication_system import CommunicationValidationError  # noqa: E402

DISCOVERY_FIELDS = {"active_task_roots", "archived_task_roots"}
CURRENT_FIELDS = {
    "task_id", "title", "current_stage_or_checkpoint", "important_refs",
    "pending_Human_decision", "last_material_update",
}
MATERIAL_TRIGGERS = {
    "task_started", "Human_decision_required", "material_block_or_risk",
    "stage_completed", "final_result_ready", "Human_requests",
}


def validate_discovery(data: dict[str, Any]) -> None:
    if not isinstance(data, dict) or set(data) != DISCOVERY_FIELDS:
        raise CommunicationValidationError("discovery_field_set_invalid")
    for field in DISCOVERY_FIELDS:
        values = data[field]
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise CommunicationValidationError("discovery_roots_must_be_string_lists")
        if len(values) != len(set(values)):
            raise CommunicationValidationError("discovery_root_duplicate")


def update_Human_current(path: Path, payload: dict[str, Any], *, event_kind: str,
                         writer_endpoint_id: str, navigation_owner_endpoint_id: str,
                         current_task_id: str, writer_task_role: str,
                         current_task_authority: dict[str, Any],
                         explicit_Human_authorization: dict[str, Any] | None = None) -> None:
    if event_kind not in MATERIAL_TRIGGERS:
        raise CommunicationValidationError("Human_current_nonmaterial_update_prohibited")
    authority = current_task_authority if isinstance(current_task_authority, dict) else {}
    explicit = (
        explicit_Human_authorization
        if isinstance(explicit_Human_authorization, dict)
        else {}
    )
    ordinary_authorized = (
        writer_endpoint_id == navigation_owner_endpoint_id
        and writer_task_role == "architecture_and_decision"
        and authority.get("task_id") == current_task_id
        and authority.get("writer_endpoint_id") == writer_endpoint_id
        and authority.get("writer_task_role") == writer_task_role
        and authority.get("navigation_owner_endpoint_id") == navigation_owner_endpoint_id
        and authority.get("can_write_Human_current") is True
    )
    explicitly_authorized = (
        explicit.get("task_id") == current_task_id
        and explicit.get("writer_endpoint_id") == writer_endpoint_id
        and explicit.get("writer_task_role") == writer_task_role
        and explicit.get("authorized_action") == "write_Human_current"
        and explicit.get("can_write_Human_current") is True
    )
    if not (ordinary_authorized or explicitly_authorized):
        raise CommunicationValidationError("Human_current_writer_not_authorized")
    if not isinstance(payload, dict) or set(payload) != CURRENT_FIELDS:
        raise CommunicationValidationError("Human_current_field_set_invalid")
    if payload.get("task_id") != current_task_id:
        raise CommunicationValidationError("Human_current_task_binding_mismatch")
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise CommunicationValidationError("Human_current_temporary_conflict")
    temporary.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
                         encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def resolve_default_context(repository_root: Path, task_id: str, *,
                            authority: str = "default_load") -> Path:
    if authority == "default_load":
        target = repository_root / "active" / task_id
    elif authority in {"exact_archive_pointer", "Human_explicit_request"}:
        target = repository_root / "archive" / task_id
    else:
        raise CommunicationValidationError("archive_context_authority_missing")
    if not target.is_dir():
        raise CommunicationValidationError("context_task_root_missing")
    return target


def resolve_context_with_trace(repository_root: Path, task_id: str, *,
                               authority: str = "default_load") -> dict[str, Any]:
    attempted = (
        repository_root / "active" / task_id
        if authority == "default_load"
        else repository_root / "archive" / task_id
    )
    try:
        target = resolve_default_context(repository_root, task_id, authority=authority)
    except CommunicationValidationError:
        return {
            "structured_read_trace": True,
            "attempted_paths": [str(attempted)],
            "successful_read_paths": [],
            "authority_source": authority,
            "target": "archive" if authority != "default_load" else "active",
            "content": None,
            "rejected": True,
        }
    context = target / "context.txt"
    content = context.read_text(encoding="utf-8")
    return {
        "structured_read_trace": True,
        "attempted_paths": [str(context)],
        "successful_read_paths": [str(context)],
        "authority_source": authority,
        "target": "archive" if authority != "default_load" else "active",
        "content": content,
        "rejected": False,
    }

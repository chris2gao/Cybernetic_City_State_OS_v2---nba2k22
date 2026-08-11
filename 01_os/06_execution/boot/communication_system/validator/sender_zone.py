"""Sender-owned path, sequence, and append-only index validation."""
from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Any

try:
    from .validate_communication_system import CommunicationValidationError
except ImportError:
    from validate_communication_system import CommunicationValidationError

INDEX_FIELDS = {
    "sequence", "message_id", "title", "message_type",
    "expected_recipient_endpoint_id", "expected_recipient_task_role",
    "exact_message_path",
}
INDEX_PROHIBITED = {"message_body", "content", "summary", "long_summary", "delivery_state"}


def next_sequence(entries: list[dict[str, Any]]) -> str:
    if not entries:
        return "00001"
    sequences = [entry.get("sequence") for entry in entries]
    _validate_sequences(sequences)
    value = int(sequences[-1]) + 1
    if value > 10000:
        raise CommunicationValidationError("sequence_exhausted")
    return f"{value:05d}"


def _validate_sequences(sequences: list[Any]) -> None:
    if any(not isinstance(seq, str) or len(seq) != 5 or not seq.isdigit() for seq in sequences):
        raise CommunicationValidationError("sequence_format_invalid")
    values = [int(seq) for seq in sequences]
    if any(value < 1 or value > 10000 for value in values):
        raise CommunicationValidationError("sequence_out_of_range")
    if values != sorted(values) or len(values) != len(set(values)):
        raise CommunicationValidationError("sequence_not_strictly_monotonic")


def ensure_sender_owned_path(relative_path: str, sender_endpoint_id: str) -> None:
    path = PurePosixPath(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise CommunicationValidationError("sender_path_outside_task_root")
    owned = (
        path == PurePosixPath("indexes") / f"{sender_endpoint_id}.yml"
        or len(path.parts) >= 3
        and path.parts[0] in {"messages", "documents"}
        and path.parts[1] == sender_endpoint_id
    )
    if not owned:
        raise CommunicationValidationError("cross_sender_write_prohibited")


def validate_sender_index(entries: list[dict[str, Any]], *, sender_endpoint_id: str,
                          task_root: Path,
                          baseline: list[dict[str, Any]] | None = None,
                          require_targets: bool = True) -> None:
    if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
        raise CommunicationValidationError("sender_index_must_be_list_of_mappings")
    if baseline is not None and entries[:len(baseline)] != baseline:
        raise CommunicationValidationError("sender_index_not_append_only")
    if baseline is not None and len(entries) < len(baseline):
        raise CommunicationValidationError("sender_index_truncated")
    _validate_sequences([entry.get("sequence") for entry in entries])
    seen_ids = set()
    for entry in entries:
        if set(entry) & INDEX_PROHIBITED:
            raise CommunicationValidationError("sender_index_prohibited_field")
        if set(entry) != INDEX_FIELDS:
            raise CommunicationValidationError("sender_index_field_set_invalid")
        sequence = entry["sequence"]
        message_id = entry["message_id"]
        expected_prefix = f"::{sender_endpoint_id}::{sequence}"
        if not isinstance(message_id, str) or not message_id.endswith(expected_prefix):
            raise CommunicationValidationError("sender_index_message_id_mismatch")
        if message_id in seen_ids:
            raise CommunicationValidationError("sender_index_message_id_reused")
        seen_ids.add(message_id)
        relative = entry["exact_message_path"]
        ensure_sender_owned_path(relative, sender_endpoint_id)
        target = (task_root.resolve() / relative).resolve()
        try:
            target.relative_to(task_root.resolve())
        except ValueError as exc:
            raise CommunicationValidationError("sender_index_target_outside_task_root") from exc
        if require_targets and not target.is_file():
            raise CommunicationValidationError("sender_index_target_missing")


def validate_physical_pointer_index(current: Any, baseline: Any, message_dir: Path) -> None:
    targets_exist = (
        isinstance(current, list)
        and all(
            isinstance(pointer, str) and (message_dir / pointer).is_file()
            for pointer in current
        )
    )
    valid = (
        isinstance(baseline, list)
        and isinstance(current, list)
        and all(isinstance(pointer, str) for pointer in current)
        and current[:len(baseline)] == baseline
        and len(current) == len(baseline) + 1
        and len(set(current)) == len(current)
        and targets_exist
    )
    if not valid:
        raise CommunicationValidationError(
            "sender_index_integrity",
            {
                "failure_code": "SENDER_INDEX_INTEGRITY",
                "baseline_index": baseline,
                "observed_index": current,
                "physical_targets_exist": targets_exist,
            },
        )

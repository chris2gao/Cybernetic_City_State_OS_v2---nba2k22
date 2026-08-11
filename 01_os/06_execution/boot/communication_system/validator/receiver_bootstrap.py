#!/usr/bin/env python3
"""Load only the receiver's exact, direct communication context."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .validate_communication_system import (
        CommunicationValidationError,
        CommunicationValidator,
        load_yaml,
    )
except ImportError:
    from validate_communication_system import CommunicationValidationError, CommunicationValidator, load_yaml


def _resolve_file(root: Path, relative: str) -> Path:
    if "*" in relative or "?" in relative:
        raise CommunicationValidationError("bootstrap_glob_prohibited")
    target = (root / relative).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise CommunicationValidationError("bootstrap_path_outside_task_root") from exc
    if not target.is_file():
        raise CommunicationValidationError(f"bootstrap_required_file_missing:{relative}")
    return target


def load_receiver_context(task_root: Path, endpoint_id: str,
                          message_relative_path: str) -> dict[str, Any]:
    root = task_root.resolve()
    manifest_path = _resolve_file(root, "manifest.yml")
    card_path = _resolve_file(root, f"endpoints/{endpoint_id}.yml")
    manifest = load_yaml(manifest_path)
    card = load_yaml(card_path)
    validator = CommunicationValidator()
    validator.validate_endpoint_card(card)
    role_path = _resolve_file(root, card["role_context_entry_ref"])
    message_path = _resolve_file(root, message_relative_path)
    message = load_yaml(message_path)
    validator.validate_message(message, message_path=message_path, task_root=root)
    if message.get("expected_recipient_endpoint_id") != card.get("endpoint_id"):
        raise CommunicationValidationError("bootstrap_recipient_endpoint_mismatch")
    if message.get("expected_recipient_task_role") != card.get("task_role"):
        raise CommunicationValidationError("bootstrap_recipient_role_mismatch")
    paths = [manifest_path, card_path, role_path, message_path]
    for ref in message["required_refs"]:
        ref_path = _resolve_file(root, ref)
        if ref_path not in paths:
            paths.append(ref_path)
    return {
        "manifest": manifest,
        "endpoint_card": card,
        "role_context": role_path.read_text(encoding="utf-8"),
        "message": message,
        "direct_refs": [path.read_text(encoding="utf-8") for path in paths[4:]],
        "read_paths": [str(path.relative_to(root)).replace("\\", "/") for path in paths],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-root", required=True, type=Path)
    parser.add_argument("--endpoint-id", required=True)
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    try:
        result = load_receiver_context(args.task_root, args.endpoint_id, args.message)
    except CommunicationValidationError as exc:
        print(f"bootstrap_rejected:{exc}", file=sys.stderr)
        return 2
    print(json.dumps({"read_paths": result["read_paths"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

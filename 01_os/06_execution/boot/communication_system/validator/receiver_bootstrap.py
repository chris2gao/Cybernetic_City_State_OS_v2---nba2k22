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
        parse_safe_yaml,
    )
except ImportError:
    from validate_communication_system import (
        CommunicationValidationError,
        CommunicationValidator,
        load_yaml,
        parse_safe_yaml,
    )


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
                          message_relative_path: str,
                          *, allow_legacy_v1: bool = False) -> dict[str, Any]:
    """Historical v1 reader. New formal actions must use load_receiver_from_pointer."""
    if not allow_legacy_v1:
        raise CommunicationValidationError(
            "legacy_v1_pointer_read_only_explicit_mode_required"
        )
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


def load_receiver_from_pointer(
    task_root: Path,
    endpoint_id: str,
    pointer: dict[str, Any],
    *,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    """Bootstrap a formal receiver only from a physically valid v2 pointer."""
    root = task_root.resolve()
    validator = CommunicationValidator()
    validated = validator.validate_pointer(
        pointer,
        task_root=root,
        repository_root=repository_root,
    )
    assert isinstance(validated, dict)

    commit: str | None = None
    task_prefix: str | None = None
    if pointer["carrier"] == "GitHub":
        if repository_root is None:
            raise CommunicationValidationError("bootstrap_GitHub_repository_root_required")
        repository_root = repository_root.resolve()
        commit = str(pointer["exact_path_or_GitHub_ref"]).split(":", 1)[0]
        try:
            task_prefix = root.relative_to(repository_root).as_posix().rstrip("/")
        except ValueError as exc:
            raise CommunicationValidationError("bootstrap_task_root_outside_repository") from exc

    def read_text(relative: str) -> str:
        if commit is None:
            return _resolve_file(root, relative).read_text(encoding="utf-8")
        assert repository_root is not None and task_prefix is not None
        return validator._git_blob(repository_root, commit, f"{task_prefix}/{relative}")

    def read_yaml(relative: str) -> dict[str, Any]:
        if commit is None:
            value = load_yaml(_resolve_file(root, relative))
        else:
            value = parse_safe_yaml(read_text(relative))
        if not isinstance(value, dict):
            raise CommunicationValidationError(f"bootstrap_mapping_required:{relative}")
        return value

    manifest = read_yaml("manifest.yml")
    if manifest.get("task_id") != pointer.get("task_id"):
        raise CommunicationValidationError("bootstrap_manifest_task_mismatch")
    if manifest.get("communication_contract_version") != 2:
        raise CommunicationValidationError("bootstrap_v2_manifest_upgrade_required")
    receiver_card_ref = f"endpoints/{endpoint_id}.yml"
    receiver_card = read_yaml(receiver_card_ref)
    validator.validate_endpoint_card(receiver_card)
    sender_card_ref = f"endpoints/{pointer['sender_endpoint_id']}.yml"
    sender_card = read_yaml(sender_card_ref)
    validator.validate_endpoint_card(sender_card)
    cards = {
        sender_card["endpoint_id"]: sender_card,
        receiver_card["endpoint_id"]: receiver_card,
    }
    message_relative = validated["message_relative_path"]
    message = validated["message"]
    validator.validate_message(message, message_path=Path(message_relative), cards=cards)
    validator.validate_recipient_delegation_with_loader(
        message, authority_loader=read_yaml
    )
    # GitHub exact-commit evidence proves what was authorized at dispatch time.
    # Delegation liveness is mutable, so a GitHub receiver must also fail closed
    # against the current physical task-root state (revocation/supersession).
    if commit is not None:
        validator.validate_recipient_delegation(message, task_root=root)
    if message.get("expected_recipient_endpoint_id") != receiver_card.get("endpoint_id"):
        raise CommunicationValidationError("bootstrap_recipient_endpoint_mismatch")
    if message.get("expected_recipient_task_role") != receiver_card.get("task_role"):
        raise CommunicationValidationError("bootstrap_recipient_role_mismatch")

    role_ref = str(receiver_card["role_context_entry_ref"])
    role_text = read_text(role_ref)
    message_refs = [str(ref) for ref in message.get("required_refs") or []]
    activation_ref_paths = list(dict.fromkeys(
        str(ref).split("#", 1)[0] for ref in validated.get("activation_refs") or []
    ))
    extra_activation_paths = [
        ref for ref in activation_ref_paths if ref not in message_refs
    ]
    direct_refs = [
        read_text(ref) for ref in [*message_refs, *extra_activation_paths]
    ]
    read_paths = [
        "manifest.yml",
        receiver_card_ref,
        role_ref,
        sender_card_ref,
        message_relative,
        *message_refs,
        str(pointer["constitution_evidence_ref"]),
        str(pointer["compliance_receipt_ref"]),
        validated["sender_index_ref"],
        *extra_activation_paths,
    ]
    ordered_paths = list(dict.fromkeys(read_paths))
    return {
        "manifest": manifest,
        "endpoint_card": receiver_card,
        "role_context": role_text,
        "message": message,
        "direct_refs": direct_refs,
        "constitution": validated["constitution"],
        "compliance_receipt": validated["compliance_receipt"],
        "sender_index": validated["sender_index"],
        "receiver_setup": pointer["receiver_setup"],
        "activation_evidence_refs": validated.get("activation_refs") or [],
        "receiver_publication_claim": validated["receiver_publication_claim"],
        "read_paths": ordered_paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-root", required=True, type=Path)
    parser.add_argument("--endpoint-id", required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--pointer", type=Path)
    source.add_argument("--message")
    parser.add_argument("--legacy-v1", action="store_true")
    parser.add_argument("--repository-root", type=Path)
    args = parser.parse_args()
    try:
        if args.pointer:
            result = load_receiver_from_pointer(
                args.task_root,
                args.endpoint_id,
                load_yaml(args.pointer),
                repository_root=args.repository_root,
            )
        elif args.legacy_v1:
            result = load_receiver_context(
                args.task_root, args.endpoint_id, args.message, allow_legacy_v1=True
            )
        else:
            raise CommunicationValidationError(
                "legacy_v1_pointer_read_only_explicit_mode_required"
            )
    except CommunicationValidationError as exc:
        print(f"bootstrap_rejected:{exc}", file=sys.stderr)
        return 2
    print(json.dumps({"read_paths": result["read_paths"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

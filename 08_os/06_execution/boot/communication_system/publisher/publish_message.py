#!/usr/bin/env python3
"""Publish one validated immutable message and return a pointer for Human relay."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

VALID_GITHUB_TRIGGERS = {
    "web_recipient", "Human_explicit_request", "full_task_convergence",
}

BOOT_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_ROOT = BOOT_ROOT / "validator"
if str(VALIDATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_ROOT))
from sender_zone import next_sequence, validate_sender_index  # noqa: E402
from validate_communication_system import (  # noqa: E402
    CommunicationValidationError,
    CommunicationValidator,
    load_yaml,
    parse_safe_yaml,
)


def _atomic_create(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise CommunicationValidationError("published_message_is_immutable") from exc


def _atomic_replace(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise CommunicationValidationError("publication_temporary_path_conflict")
    try:
        temporary.write_text(text, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _privacy_check(value: Any, privacy_class: str, carrier: str) -> None:
    if privacy_class not in {"repository_shareable", "local_only", "forbidden"}:
        raise CommunicationValidationError("privacy_class_invalid")
    if privacy_class == "forbidden":
        raise CommunicationValidationError("forbidden_content_cannot_be_materialized")
    if carrier == "GitHub" and privacy_class != "repository_shareable":
        raise CommunicationValidationError("GitHub_requires_repository_shareable")
    prohibited_keys = {"password", "access_token", "private_key", "authentication_file"}
    if isinstance(value, dict) and prohibited_keys & {str(key).lower() for key in value}:
        raise CommunicationValidationError("forbidden_data_marker")


def _endpoint_cards(root: Path, message: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cards = {}
    for endpoint_id in (
        message.get("sender_endpoint_id"),
        message.get("expected_recipient_endpoint_id"),
    ):
        path = root / "endpoints" / f"{endpoint_id}.yml"
        if not path.is_file():
            raise CommunicationValidationError(f"endpoint_card_missing_for_message:{endpoint_id}")
        cards[str(endpoint_id)] = load_yaml(path)
    return cards


def _validate_required_documents(root: Path, message: dict[str, Any], carrier: str,
                                 trace: list[str]) -> None:
    validator = CommunicationValidator()
    for relative in message.get("required_refs", []):
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise CommunicationValidationError("required_ref_outside_task_root") from exc
        if not path.is_file():
            raise CommunicationValidationError(f"required_ref_missing:{relative}")
        if Path(relative).parts[:1] == ("documents",):
            content = path.read_text(encoding="utf-8")
            validator.validate_document(content)
            front_end = content.find("\n---\n", 4)
            front = load_yaml_front_matter(content, front_end)
            _privacy_check(front, str(front.get("privacy_class")), carrier)
            trace.append(f"document_validated:{relative}")


def load_yaml_front_matter(content: str, marker: int) -> dict[str, Any]:
    if marker < 0:
        raise CommunicationValidationError("document_front_matter_unclosed")
    value = parse_safe_yaml(content[4:marker])
    if not isinstance(value, dict):
        raise CommunicationValidationError("document_front_matter_must_be_mapping")
    return value


def publish(task_root: Path, message_source: Path, *, carrier: str = "local",
            github_trigger: str | None = None,
            privacy_class: str = "repository_shareable",
            protected_action: bool = False,
            current_task_authority: dict[str, Any] | None = None,
            Human_authorization: dict[str, Any] | None = None,
            publication_trace: list[str] | None = None) -> dict[str, Any]:
    if carrier not in {"local", "GitHub"}:
        raise CommunicationValidationError("carrier_invalid")
    if carrier == "GitHub" and github_trigger not in VALID_GITHUB_TRIGGERS:
        raise CommunicationValidationError("GitHub_publication_requires_explicit_trigger")
    root = task_root.resolve()
    message = load_yaml(message_source)
    trace = publication_trace if publication_trace is not None else []
    _privacy_check(message, privacy_class, carrier)
    cards = _endpoint_cards(root, message)
    _validate_required_documents(root, message, carrier, trace)
    manifest_path = root / "manifest.yml"
    if manifest_path.is_file():
        manifest = load_yaml(manifest_path)
        if manifest.get("task_id") != message.get("task_id"):
            raise CommunicationValidationError("publication_task_scope_mismatch")
    sender = message.get("sender_endpoint_id")
    index_path = root / "indexes" / f"{sender}.yml"
    entries = load_yaml(index_path) if index_path.exists() else []
    sequence = next_sequence(entries)
    expected_id = f"{message.get('task_id')}::{sender}::{sequence}"
    if message.get("message_id") != expected_id:
        raise CommunicationValidationError("publication_message_id_sequence_mismatch")
    relative = f"messages/{sender}/{sequence}_{message.get('message_type')}.yml"
    target = root / relative
    validator = CommunicationValidator()
    recipient = str(message.get("expected_recipient_endpoint_id"))
    validator.validate_carrier_route(
        expected_recipient_environment=str(cards[recipient].get("environment_class")),
        carrier=carrier,
        Human_requested_GitHub=github_trigger == "Human_explicit_request",
        full_convergence_requested=github_trigger == "full_task_convergence",
    )
    validator.validate_message(message, message_path=target, task_root=root, cards=cards)
    if protected_action:
        validator.validate_protected_action_authority(
            message,
            task_root=root,
            current_task_authority=current_task_authority or {},
            Human_authorization=Human_authorization,
        )
    entry = {
        "sequence": sequence,
        "message_id": message["message_id"],
        "title": message["title"],
        "message_type": message["message_type"],
        "expected_recipient_endpoint_id": message["expected_recipient_endpoint_id"],
        "expected_recipient_task_role": message["expected_recipient_task_role"],
        "exact_message_path": relative,
    }
    updated = [*entries, entry]
    validate_sender_index(
        updated,
        sender_endpoint_id=sender,
        task_root=root,
        baseline=entries,
        require_targets=False,
    )
    _atomic_create(target, yaml.safe_dump(message, allow_unicode=True, sort_keys=False))
    trace.append(f"message_published:{relative}")
    try:
        validate_sender_index(updated, sender_endpoint_id=sender, task_root=root, baseline=entries)
        _atomic_replace(index_path, yaml.safe_dump(updated, allow_unicode=True, sort_keys=False))
    except Exception:
        target.unlink(missing_ok=True)
        trace.append(f"message_rolled_back:{relative}")
        raise
    trace.append(f"index_updated:indexes/{sender}.yml")
    document_refs = [
        ref for ref in message.get("required_refs", [])
        if Path(ref).parts[:1] == ("documents",)
    ]
    validator.validate_publication_trace(trace, document_refs)
    pointer = {
        "task_id": message["task_id"],
        "message_id": message["message_id"],
        "carrier": carrier,
        "exact_path_or_GitHub_ref": relative,
        "sender_endpoint_id": sender,
        "sender_task_role": message["sender_task_role"],
        "expected_recipient_endpoint_id": message["expected_recipient_endpoint_id"],
        "expected_recipient_task_role": message["expected_recipient_task_role"],
        "one_line_routing_purpose": message["title"],
    }
    validator.validate_pointer(pointer, task_root=root)
    return pointer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-root", required=True, type=Path)
    parser.add_argument("--message", required=True, type=Path)
    parser.add_argument("--carrier", choices=["local", "GitHub"], default="local")
    parser.add_argument("--github-trigger", choices=sorted(VALID_GITHUB_TRIGGERS))
    parser.add_argument("--privacy-class", choices=["repository_shareable", "local_only", "forbidden"],
                        default="repository_shareable")
    args = parser.parse_args()
    try:
        pointer = publish(args.task_root, args.message, carrier=args.carrier,
                          github_trigger=args.github_trigger, privacy_class=args.privacy_class)
    except (CommunicationValidationError, OSError, yaml.YAMLError) as exc:
        print(f"publication_rejected:{exc}", file=sys.stderr)
        return 2
    print(yaml.safe_dump(pointer, allow_unicode=True, sort_keys=False), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

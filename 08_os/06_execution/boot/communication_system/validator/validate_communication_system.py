#!/usr/bin/env python3
"""Validate communication artifacts. This program never publishes or authorizes."""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from yaml.events import AliasEvent
from yaml.nodes import MappingNode


class CommunicationValidationError(ValueError):
    """A deterministic contract violation with optional physical evidence."""

    def __init__(self, message: str, payload: dict[str, Any] | None = None):
        super().__init__(message)
        self.payload = payload or {"failure_code": message.split(":", 1)[0]}


ENDPOINT_FIELDS = {
    "endpoint_id", "principal_class", "model_or_product", "environment_class",
    "interface_class", "task_role", "local_file_read", "local_file_write",
    "GitHub_read", "GitHub_write", "instance_label", "role_context_entry_ref",
}
CAPABILITY_FIELDS = {"local_file_read", "local_file_write", "GitHub_read", "GitHub_write"}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
MESSAGE_REQUIRED = {
    "message_id", "task_id", "title", "message_type", "sender_endpoint_id",
    "sender_task_role", "expected_recipient_endpoint_id",
    "expected_recipient_task_role", "content", "required_refs",
}
MESSAGE_OPTIONAL = {
    "requested_action", "in_reply_to", "supersedes", "references",
    "authorization_ref", "facts", "decisions", "assumptions", "unknowns",
    "constraints", "risks",
}
MESSAGE_TYPES = {"request", "response", "result", "decision_required", "correction", "blocked"}
ACTION_REQUIRED = {"request", "decision_required", "blocked"}
PROHIBITED_MESSAGE_FIELDS = {
    "summary", "delivery_state", "delivered", "read_state", "read",
    "understood_state", "accepted_state", "actual_recipient_record",
    "message_custom_digest", "protocol_version", "private_chain_of_thought",
    "self_authorization", "identity_claim_grants_authority",
}
DOCUMENT_REQUIRED = {
    "document_id", "task_id", "author_endpoint_id", "author_task_role",
    "purpose", "privacy_class",
}
DOCUMENT_OPTIONAL = {"supersedes"}
PRIVACY_CLASSES = {"repository_shareable", "local_only", "forbidden"}
POINTER_FIELDS = {
    "task_id", "message_id", "carrier", "exact_path_or_GitHub_ref",
    "sender_endpoint_id", "sender_task_role", "expected_recipient_endpoint_id",
    "expected_recipient_task_role", "one_line_routing_purpose",
}


class StrictSafeLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(loader: StrictSafeLoader, node: MappingNode, deep: bool = False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise CommunicationValidationError(f"duplicate_yaml_key:{key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def parse_safe_yaml(content: str) -> Any:
    if not isinstance(content, str):
        raise CommunicationValidationError("yaml_input_must_be_text")
    try:
        events = list(yaml.parse(content))
        if any(isinstance(event, AliasEvent) or getattr(event, "anchor", None) for event in events):
            raise CommunicationValidationError("yaml_anchor_or_alias_prohibited")
        if re.search(r"(?m)^\s*<<\s*:", content):
            raise CommunicationValidationError("yaml_merge_key_prohibited")
        documents = list(yaml.load_all(content, Loader=StrictSafeLoader))
    except CommunicationValidationError:
        raise
    except yaml.constructor.ConstructorError as exc:
        raise CommunicationValidationError("yaml_custom_tag_prohibited") from exc
    except yaml.YAMLError as exc:
        raise CommunicationValidationError(f"yaml_parse_failed:{exc}") from exc
    if len(documents) != 1:
        raise CommunicationValidationError("yaml_must_have_exactly_one_document")
    return documents[0]


def load_yaml(path: Path) -> Any:
    try:
        return parse_safe_yaml(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise CommunicationValidationError(f"yaml_load_failed:{path}:{exc}") from exc


class CommunicationValidator:
    """Pure validation methods with no authority or background execution."""

    def validate_endpoint_card(self, card: dict[str, Any]) -> None:
        if not isinstance(card, dict):
            raise CommunicationValidationError("endpoint_card_must_be_mapping")
        missing = sorted(ENDPOINT_FIELDS - set(card))
        unknown = sorted(set(card) - ENDPOINT_FIELDS)
        if missing:
            raise CommunicationValidationError("endpoint_card_missing:" + ",".join(missing))
        if unknown:
            raise CommunicationValidationError("endpoint_card_unknown:" + ",".join(unknown))
        if not SAFE_ID.fullmatch(str(card["endpoint_id"])):
            raise CommunicationValidationError("endpoint_id_invalid")
        if not card.get("task_role") or not card.get("role_context_entry_ref"):
            raise CommunicationValidationError("endpoint_role_context_missing")
        for field in CAPABILITY_FIELDS:
            if not isinstance(card[field], bool):
                raise CommunicationValidationError(f"endpoint_capability_not_boolean:{field}")

    def validate_role_binding(self, message: dict[str, Any],
                              cards: dict[str, dict[str, Any]]) -> None:
        sender_id = message.get("sender_endpoint_id")
        recipient_id = message.get("expected_recipient_endpoint_id")
        if sender_id not in cards or recipient_id not in cards:
            raise CommunicationValidationError("endpoint_card_missing_for_message")
        sender = cards[sender_id]
        recipient = cards[recipient_id]
        self.validate_endpoint_card(sender)
        self.validate_endpoint_card(recipient)
        if message.get("sender_task_role") != sender["task_role"]:
            raise CommunicationValidationError("sender_role_mismatch")
        if message.get("expected_recipient_task_role") != recipient["task_role"]:
            raise CommunicationValidationError("recipient_role_mismatch")
        if message.get("self_authorization") is True:
            raise CommunicationValidationError("self_authorization_prohibited")
        if message.get("identity_claim_grants_authority") is True:
            raise CommunicationValidationError("identity_claim_cannot_authorize")
        authorization_ref = message.get("authorization_ref")
        refs = message.get("required_refs") or []
        if authorization_ref and authorization_ref not in refs:
            raise CommunicationValidationError("authorization_ref_not_in_required_refs")

    def validate_action_origin(self, *, source_has_requested_action: bool,
                               emitted_has_requested_action: bool) -> None:
        if not source_has_requested_action and emitted_has_requested_action:
            raise CommunicationValidationError("synthesized_requested_action_prohibited")

    def validate_direct_ref_set(self, observed: list[str], expected: list[str]) -> None:
        if observed != expected:
            raise CommunicationValidationError("required_ref_set_mismatch")

    def validate_existing_resource_ref(self, task_root: Path, relative: str) -> None:
        target = (task_root.resolve() / relative).resolve()
        try:
            target.relative_to(task_root.resolve())
        except ValueError as exc:
            raise CommunicationValidationError("existing_resource_reference_invalid") from exc
        if not target.is_file():
            raise CommunicationValidationError("existing_resource_reference_invalid")

    def validate_read_trace(self, observed: list[str], allowed: list[str], *,
                            bootstrap: bool = False) -> None:
        if observed != allowed:
            code = "bootstrap_read_set_invalid" if bootstrap else "unauthorized_context_expansion"
            raise CommunicationValidationError(code, {
                "failure_code": code,
                "observed": observed,
                "allowed": allowed,
            })

    def validate_inline_content(self, content: str, *, maximum_chars: int = 4000) -> None:
        if len(content) > maximum_chars:
            raise CommunicationValidationError("long_content_requires_document")

    def validate_carrier_route(self, *, expected_recipient_environment: str,
                               carrier: str, Human_requested_GitHub: bool = False,
                               full_convergence_requested: bool = False) -> None:
        github_required = (
            expected_recipient_environment == "web_cloud_model"
            or Human_requested_GitHub
            or full_convergence_requested
        )
        if github_required and carrier != "GitHub":
            raise CommunicationValidationError("web_republication_required")
        if not github_required and carrier != "local":
            raise CommunicationValidationError("local_default_route_violation")

    def validate_Human_route(self, *, selected_recipient_endpoint_id: str,
                             actual_recipient_endpoint_id: str) -> None:
        if selected_recipient_endpoint_id != actual_recipient_endpoint_id:
            raise CommunicationValidationError("Human_route_override_failed")

    def validate_publication_trace(self, trace: list[str], required_refs: list[str]) -> None:
        document_events = [f"document_validated:{ref}" for ref in required_refs]
        try:
            message_index = next(i for i, event in enumerate(trace) if event.startswith("message_published:"))
            index_index = next(i for i, event in enumerate(trace) if event.startswith("index_updated:"))
        except StopIteration as exc:
            raise CommunicationValidationError("publication_trace_incomplete") from exc
        if any(event not in trace[:message_index] for event in document_events):
            raise CommunicationValidationError("publication_document_order_invalid")
        if index_index <= message_index:
            raise CommunicationValidationError("publication_index_order_invalid")

    def validate_protected_action_authority(
        self,
        message: dict[str, Any],
        *,
        task_root: Path,
        current_task_authority: dict[str, Any],
        Human_authorization: dict[str, Any] | None,
    ) -> None:
        task_id = message.get("task_id")
        sender = message.get("sender_endpoint_id")
        role = message.get("sender_task_role")
        action = message.get("requested_action")
        if not isinstance(current_task_authority, dict) or (
            current_task_authority.get("task_id") != task_id
            or current_task_authority.get("writer_endpoint_id") != sender
            or current_task_authority.get("writer_task_role") != role
            or current_task_authority.get("requested_action") != action
        ):
            raise CommunicationValidationError("current_task_authority_binding_invalid")
        authorization_ref = message.get("authorization_ref")
        if not authorization_ref or authorization_ref not in message.get("required_refs", []):
            raise CommunicationValidationError("protected_action_human_authorization_required")
        target = (task_root.resolve() / str(authorization_ref)).resolve()
        try:
            target.relative_to(task_root.resolve())
        except ValueError as exc:
            raise CommunicationValidationError("authorization_ref_outside_task_root") from exc
        if not target.is_file():
            raise CommunicationValidationError("authorization_ref_unreadable")
        physical = load_yaml(target)
        if Human_authorization is not None and Human_authorization != physical:
            raise CommunicationValidationError("Human_authorization_physical_state_mismatch")
        if not isinstance(physical, dict) or (
            physical.get("task_id") != task_id
            or physical.get("writer_endpoint_id") != sender
            or physical.get("authorized_action") != action
            or physical.get("granted") is not True
        ):
            raise CommunicationValidationError("protected_action_human_authorization_required")

    def validate_message(self, message: dict[str, Any], *, message_path: Path | None = None,
                         task_root: Path | None = None,
                         cards: dict[str, dict[str, Any]] | None = None) -> None:
        if not isinstance(message, dict):
            raise CommunicationValidationError("message_must_be_mapping")
        prohibited = sorted(set(message) & PROHIBITED_MESSAGE_FIELDS)
        if prohibited:
            raise CommunicationValidationError("prohibited_message_field:" + ",".join(prohibited))
        missing = sorted(MESSAGE_REQUIRED - set(message))
        if missing:
            raise CommunicationValidationError("message_required_field_missing:" + ",".join(missing))
        unknown = sorted(set(message) - MESSAGE_REQUIRED - MESSAGE_OPTIONAL)
        if unknown:
            raise CommunicationValidationError("message_unknown_field:" + ",".join(unknown))
        message_type = message["message_type"]
        if message_type not in MESSAGE_TYPES:
            raise CommunicationValidationError("message_type_invalid")
        if message_type in ACTION_REQUIRED and not message.get("requested_action"):
            raise CommunicationValidationError("requested_action_required")
        for field in ("task_id", "sender_endpoint_id", "expected_recipient_endpoint_id"):
            if not SAFE_ID.fullmatch(str(message[field])):
                raise CommunicationValidationError(f"message_identifier_invalid:{field}")
        message_id = str(message["message_id"])
        prefix = f"{message['task_id']}::{message['sender_endpoint_id']}::"
        if not message_id.startswith(prefix):
            raise CommunicationValidationError("message_id_identity_mismatch")
        sequence = message_id.removeprefix(prefix)
        if not re.fullmatch(r"\d{5}", sequence) or not 1 <= int(sequence) <= 10000:
            raise CommunicationValidationError("message_sequence_invalid")
        refs = message["required_refs"]
        if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
            raise CommunicationValidationError("required_refs_must_be_string_list")
        if len(refs) != len(set(refs)):
            raise CommunicationValidationError("required_refs_must_be_unique")
        if message.get("authorization_ref") and message["authorization_ref"] not in refs:
            raise CommunicationValidationError("authorization_ref_not_in_required_refs")
        if message_path is not None:
            expected_name = f"{sequence}_{message_type}.yml"
            if message_path.name != expected_name or message_path.parent.name != message["sender_endpoint_id"]:
                raise CommunicationValidationError("message_path_identity_mismatch")
        if task_root is not None:
            root = task_root.resolve()
            for ref in refs:
                target = (root / ref).resolve()
                try:
                    target.relative_to(root)
                except ValueError as exc:
                    raise CommunicationValidationError("required_ref_outside_task_root") from exc
                if not target.is_file():
                    raise CommunicationValidationError(f"required_ref_missing:{ref}")
        if cards is not None:
            self.validate_role_binding(message, cards)

    def validate_document(self, content: str, *, existing_repository_resource: bool = False) -> None:
        if existing_repository_resource:
            return
        if not content.startswith("---\n"):
            raise CommunicationValidationError("document_front_matter_missing")
        marker = content.find("\n---\n", 4)
        if marker < 0:
            raise CommunicationValidationError("document_front_matter_unclosed")
        front = parse_safe_yaml(content[4:marker])
        if not isinstance(front, dict):
            raise CommunicationValidationError("document_front_matter_must_be_mapping")
        missing = sorted(DOCUMENT_REQUIRED - set(front))
        unknown = sorted(set(front) - DOCUMENT_REQUIRED - DOCUMENT_OPTIONAL)
        if missing:
            raise CommunicationValidationError("document_front_matter_missing:" + ",".join(missing))
        if unknown:
            raise CommunicationValidationError("document_front_matter_unknown:" + ",".join(unknown))
        if front.get("privacy_class") not in PRIVACY_CLASSES:
            raise CommunicationValidationError("document_privacy_class_invalid")

    def validate_pointer(self, pointer: dict[str, Any], *, task_root: Path) -> None:
        if not isinstance(pointer, dict) or set(pointer) != POINTER_FIELDS:
            raise CommunicationValidationError("Human_pointer_field_set_invalid")
        if pointer.get("carrier") not in {"local", "GitHub"}:
            raise CommunicationValidationError("Human_pointer_carrier_invalid")
        exact = str(pointer.get("exact_path_or_GitHub_ref", ""))
        if pointer["carrier"] == "local":
            target = (task_root.resolve() / exact).resolve()
            try:
                target.relative_to(task_root.resolve())
            except ValueError as exc:
                raise CommunicationValidationError("Human_pointer_outside_task_root") from exc
            if not target.is_file():
                raise CommunicationValidationError("Human_pointer_target_unpublished")
        if not str(pointer.get("message_id", "")).startswith(
            f"{pointer.get('task_id')}::{pointer.get('sender_endpoint_id')}::"
        ):
            raise CommunicationValidationError("Human_pointer_identity_mismatch")


def validate_static_repository(repo_root: Path) -> None:
    root = repo_root.resolve()
    os_root = root / "08_os"
    manifest_path = os_root / "02_boot/communication_system/启动清单_v1.yml"
    manifest = load_yaml(manifest_path)
    if manifest.get("background_processes_started") is not False:
        raise CommunicationValidationError("boot_background_boundary_invalid")
    if manifest.get("canonical_live_state_created_by_boot") is not False:
        raise CommunicationValidationError("boot_live_state_boundary_invalid")
    for relative in manifest.get("load_order") or []:
        if not (root / relative).is_file():
            raise CommunicationValidationError(f"boot_ref_missing:{relative}")
    mechanism = os_root / "03_mechanisms/communication_system"
    for contract in mechanism.glob("*.yml"):
        load_yaml(contract)
    local = load_yaml(
        os_root / "06_execution/boot/communication_system/fixtures/cross_endpoint/local_message.yml"
    )
    web = load_yaml(
        os_root / "06_execution/boot/communication_system/fixtures/cross_endpoint/web_message.yml"
    )
    if local != web:
        raise CommunicationValidationError("static_endpoint_parity_mismatch")
    execution = os_root / "06_execution/boot/communication_system"
    prohibited_imports = {"schedule", "watchdog", "apscheduler", "daemon"}
    for source in execution.rglob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.name.split(".")[0] for alias in node.names]
                if set(names) & prohibited_imports:
                    raise CommunicationValidationError(f"background_module_imported:{source}")
            if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
                raise CommunicationValidationError(f"unbounded_loop_prohibited:{source}")



def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    endpoint = sub.add_parser("endpoint-card")
    endpoint.add_argument("path", type=Path)
    message = sub.add_parser("message")
    message.add_argument("path", type=Path)
    message.add_argument("--task-root", type=Path)
    static = sub.add_parser("static")
    static.add_argument("repo_root", type=Path)
    args = parser.parse_args()
    validator = CommunicationValidator()
    try:
        if args.command == "endpoint-card":
            validator.validate_endpoint_card(load_yaml(args.path))
        elif args.command == "message":
            validator.validate_message(load_yaml(args.path), message_path=args.path,
                                       task_root=args.task_root)
        elif args.command == "static":
            validate_static_repository(args.repo_root)
    except CommunicationValidationError as exc:
        print(f"validation_rejected:{exc}", file=sys.stderr)
        return 2
    print("validation_passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

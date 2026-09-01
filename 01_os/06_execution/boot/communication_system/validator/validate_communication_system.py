#!/usr/bin/env python3
"""Validate communication artifacts. This program never publishes or authorizes."""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Callable

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
    "confirmation_ref", "authorization_ref", "recipient_delegation_ref", "facts", "decisions", "assumptions", "unknowns",
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
POINTER_V1_FIELDS = {
    "task_id", "message_id", "carrier", "exact_path_or_GitHub_ref",
    "sender_endpoint_id", "sender_task_role", "expected_recipient_endpoint_id",
    "expected_recipient_task_role", "one_line_routing_purpose",
}
POINTER_V2_FIELDS = POINTER_V1_FIELDS | {
    "pointer_contract_version", "constitution_evidence_ref",
    "compliance_receipt_ref", "receiver_setup",
}
MODEL_CATALOG_REF = "01_os/03_mechanisms/model_routing/模型与产品面目录_v1.yml"
RECEIVER_ROLE_CONTRACT_REF = "01_os/03_mechanisms/model_routing/协作角色与接收者设置契约_v1.yml"
TRIGGER_REGISTRY_REF = "01_os/03_mechanisms/mechanism_activation/机制触发注册表_v1.yml"
COMMUNICATION_PUBLISHER_REF = (
    "01_os/06_execution/boot/communication_system/publisher/publish_message.py"
)


def canonical_task_relative_ref(value: Any, code: str) -> str:
    """Return a canonical POSIX task-relative file ref, rejecting traversal/aliases."""
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("./"):
        raise CommunicationValidationError(code)
    clean = value.split("#", 1)[0]
    path = PurePosixPath(clean)
    if (
        not clean
        or path.is_absolute()
        or "." in path.parts
        or ".." in path.parts
        or path.as_posix() != clean
    ):
        raise CommunicationValidationError(code)
    return clean

REPO_ROOT = Path(__file__).resolve().parents[5]
ACTIVATION_ROOT = REPO_ROOT / "01_os/06_execution/boot/mechanism_activation"
MODEL_ROUTING_ROOT = REPO_ROOT / "01_os/06_execution/boot/model_routing"
for _module_root in (ACTIVATION_ROOT, MODEL_ROUTING_ROOT):
    if str(_module_root) not in sys.path:
        sys.path.insert(0, str(_module_root))
from activation import (  # noqa: E402
    ActivationError,
    MaterialObservationContext,
    evaluate_pre_action_gate,
    observe_communication_message_git_claim,
    observe_communication_message_local_claim,
    resolve_required_mechanisms,
    validate_constitution_evidence,
    validate_material_receipt,
)
from route_receiver import (  # noqa: E402
    ReceiverSetupError,
    validate_receiver_setup,
)


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
        canonical_task_relative_ref(
            card["role_context_entry_ref"], "endpoint_role_context_ref_noncanonical"
        )
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
        refs = message.get("required_refs") or []
        confirmation_ref = message.get("confirmation_ref")
        if confirmation_ref and confirmation_ref not in refs:
            raise CommunicationValidationError("confirmation_ref_not_in_required_refs")
        authorization_ref = message.get("authorization_ref")
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

    def _load_authority_mapping(self, task_root: Path, relative: str) -> dict[str, Any]:
        ref = canonical_task_relative_ref(relative, "authorization_ref_noncanonical")
        target = (task_root.resolve() / ref).resolve()
        try:
            target.relative_to(task_root.resolve())
        except ValueError as exc:
            raise CommunicationValidationError("authorization_ref_outside_task_root") from exc
        if not target.is_file():
            raise CommunicationValidationError("authorization_ref_unreadable")
        value = load_yaml(target)
        if not isinstance(value, dict):
            raise CommunicationValidationError("authorization_ref_not_mapping")
        return value

    def _validate_Human_task_authority_v2(self, root: dict[str, Any], *, task_id: str) -> set[str]:
        commitment = root.get("task_nonce_commitment") or {}
        scope = root.get("task_authority_scope")
        holder = root.get("initial_authority_holder_endpoint_id")
        holder_role = root.get("initial_authority_holder_task_role")
        if (
            root.get("task_id") != task_id
            or not root.get("task_authority_id")
            or root.get("Human_disposition") not in {"authorized", "confirmed", "accepted"}
            or root.get("task_authority_revoked") is True
            or not isinstance(holder, str) or not SAFE_ID.fullmatch(holder)
            or not isinstance(holder_role, str) or not holder_role
            or not isinstance(scope, list) or not scope
            or any(not isinstance(item, str) or not item for item in scope)
            or len(scope) != len(set(scope))
            or not isinstance(commitment, dict)
            or commitment.get("scheme") != "citystate-human-task-authority-v2"
            or commitment.get("algorithm") != "sha256"
            or not re.fullmatch(r"[0-9a-f]{64}", str(commitment.get("digest", "")))
        ):
            raise CommunicationValidationError("Human_task_authority_v2_invalid")
        return set(scope)

    def _validate_delegation_chain(
        self, physical: dict[str, Any], *, task_id: str,
        required_refs: list[str], expected_recipient_endpoint_id: str,
        expected_recipient_task_role: str, requested_action: str,
        task_root: Path | None = None,
        authority_loader: Callable[[str], dict[str, Any]] | None = None,
    ) -> None:
        if authority_loader is None:
            if task_root is None:
                raise CommunicationValidationError("delegation_authority_loader_required")
            authority_loader = lambda relative: self._load_authority_mapping(task_root, relative)
        root_ref = physical.get("Human_task_authority_ref")
        if not isinstance(root_ref, str) or root_ref not in required_refs:
            raise CommunicationValidationError("Human_task_authority_ref_required")
        root = authority_loader(root_ref)
        root_scope = self._validate_Human_task_authority_v2(root, task_id=task_id)
        root_authority_id = root["task_authority_id"]
        root_holder = root["initial_authority_holder_endpoint_id"]
        root_holder_role = root["initial_authority_holder_task_role"]

        child: dict[str, Any] | None = None
        current = physical
        seen_parent_refs: set[str] = set()
        for _depth in range(32):
            if current.get("schema_version") != "citystate.communication.task_authority_delegation.v2":
                raise CommunicationValidationError("authorization_v2_schema_invalid")
            if current.get("task_id") != task_id or current.get("granted") is not True or current.get("revoked") is True:
                raise CommunicationValidationError("authorization_v2_not_live")
            if current.get("task_authority_id") != root_authority_id:
                raise CommunicationValidationError("delegation_task_authority_mismatch")
            if current.get("Human_task_authority_ref") != root_ref:
                raise CommunicationValidationError("delegation_root_authority_mismatch")
            delegator = current.get("delegator_endpoint_id")
            delegator_role = current.get("delegator_task_role")
            recipient = current.get("recipient_endpoint_id")
            recipient_role = current.get("recipient_task_role")
            if not all(isinstance(value, str) and value for value in (delegator, delegator_role, recipient, recipient_role)):
                raise CommunicationValidationError("delegation_identity_invalid")
            if delegator == recipient:
                raise CommunicationValidationError("self_delegation_prohibited")
            actions = current.get("authorized_actions")
            scope = current.get("delegated_scope")
            if (
                not isinstance(actions, list) or not actions
                or any(not isinstance(item, str) or not item for item in actions)
                or len(actions) != len(set(actions))
                or not isinstance(scope, list) or not scope
                or any(not isinstance(item, str) or not item for item in scope)
                or len(scope) != len(set(scope))
            ):
                raise CommunicationValidationError("delegation_action_or_scope_invalid")
            if not set(scope).issubset(root_scope):
                raise CommunicationValidationError("delegation_exceeds_Human_task_scope")
            if child is not None:
                if child.get("delegator_endpoint_id") != recipient or child.get("delegator_task_role") != recipient_role:
                    raise CommunicationValidationError("delegation_parent_recipient_mismatch")
                if current.get("allow_redelegation") is not True:
                    raise CommunicationValidationError("redelegation_not_granted")
                if not set(child["authorized_actions"]).issubset(set(actions)):
                    raise CommunicationValidationError("redelegation_action_expansion")
                if not set(child["delegated_scope"]).issubset(set(scope)):
                    raise CommunicationValidationError("redelegation_scope_expansion")

            parent_ref = current.get("parent_delegation_ref")
            if parent_ref is None:
                if delegator != root_holder or delegator_role != root_holder_role:
                    raise CommunicationValidationError("root_delegator_not_Human_bound_holder")
                break
            if not isinstance(parent_ref, str) or parent_ref not in required_refs:
                raise CommunicationValidationError("parent_delegation_ref_required")
            if parent_ref in seen_parent_refs:
                raise CommunicationValidationError("delegation_cycle_detected")
            seen_parent_refs.add(parent_ref)
            child = current
            current = authority_loader(parent_ref)
        else:
            raise CommunicationValidationError("delegation_chain_too_deep")

        if physical.get("recipient_endpoint_id") != expected_recipient_endpoint_id or physical.get("recipient_task_role") != expected_recipient_task_role:
            raise CommunicationValidationError("authorization_v2_recipient_mismatch")
        if requested_action not in physical.get("authorized_actions", []):
            raise CommunicationValidationError("authorization_v2_action_not_delegated")

    def _validate_v2_authorization_document(
        self, physical: dict[str, Any], *, task_root: Path, task_id: str,
        writer_endpoint_id: str, writer_task_role: str, requested_action: str,
        required_refs: list[str],
    ) -> None:
        schema = physical.get("schema_version")
        if schema == "citystate.communication.task_authority_delegation.v2":
            self._validate_delegation_chain(
                physical, task_root=task_root, task_id=task_id,
                required_refs=required_refs,
                expected_recipient_endpoint_id=writer_endpoint_id,
                expected_recipient_task_role=writer_task_role,
                requested_action=requested_action,
            )
            return
        if schema != "citystate.communication.direct_human_authorization.v2":
            raise CommunicationValidationError("authorization_v2_schema_invalid")
        if physical.get("task_id") != task_id or physical.get("granted") is not True or physical.get("revoked") is True:
            raise CommunicationValidationError("authorization_v2_not_live")
        actions = physical.get("authorized_actions")
        if not isinstance(actions, list) or requested_action not in actions:
            raise CommunicationValidationError("authorization_v2_action_not_delegated")
        if physical.get("writer_endpoint_id") != writer_endpoint_id or physical.get("writer_task_role") != writer_task_role:
            raise CommunicationValidationError("authorization_v2_writer_mismatch")
        root_ref = physical.get("Human_task_authority_ref")
        if not isinstance(root_ref, str) or root_ref not in required_refs:
            raise CommunicationValidationError("Human_task_authority_ref_required")
        root = self._load_authority_mapping(task_root, root_ref)
        self._validate_Human_task_authority_v2(root, task_id=task_id)

    def validate_recipient_delegation(self, message: dict[str, Any], *, task_root: Path) -> None:
        ref = message.get("recipient_delegation_ref")
        if ref is None:
            return
        refs = message.get("required_refs") or []
        if ref not in refs:
            raise CommunicationValidationError("recipient_delegation_ref_not_in_required_refs")
        physical = self._load_authority_mapping(task_root, str(ref))
        self._validate_delegation_chain(
            physical, task_root=task_root, task_id=str(message.get("task_id")),
            required_refs=refs,
            expected_recipient_endpoint_id=str(message.get("expected_recipient_endpoint_id")),
            expected_recipient_task_role=str(message.get("expected_recipient_task_role")),
            requested_action=str(message.get("requested_action") or ""),
        )

    def validate_recipient_delegation_with_loader(
        self,
        message: dict[str, Any],
        *,
        authority_loader: Callable[[str], dict[str, Any]],
    ) -> None:
        """Validate delegated-start authority from an immutable/external ref loader."""
        ref = message.get("recipient_delegation_ref")
        if ref is None:
            return
        refs = message.get("required_refs") or []
        if ref not in refs:
            raise CommunicationValidationError("recipient_delegation_ref_not_in_required_refs")
        physical = authority_loader(str(ref))
        self._validate_delegation_chain(
            physical,
            task_id=str(message.get("task_id")),
            required_refs=refs,
            expected_recipient_endpoint_id=str(message.get("expected_recipient_endpoint_id")),
            expected_recipient_task_role=str(message.get("expected_recipient_task_role")),
            requested_action=str(message.get("requested_action") or ""),
            authority_loader=authority_loader,
        )

    def _validate_Human_confirmation_v1(
        self, physical: dict[str, Any], *, task_id: str, requested_action: str,
    ) -> None:
        actions = physical.get("confirmed_actions")
        confirmation_id = physical.get("confirmation_id")
        if (
            physical.get("schema_version") != "citystate.communication.human_confirmation.v1"
            or physical.get("task_id") != task_id
            or not isinstance(confirmation_id, str) or not SAFE_ID.fullmatch(confirmation_id)
            or physical.get("confirmed_by") != "Human"
            or physical.get("disposition") != "confirmed"
            or physical.get("revoked") is True
            or not isinstance(actions, list) or not actions
            or any(not isinstance(item, str) or not item for item in actions)
            or len(actions) != len(set(actions))
        ):
            raise CommunicationValidationError("Human_confirmation_v1_invalid")
        if requested_action not in actions:
            raise CommunicationValidationError("Human_confirmation_action_not_confirmed")

    def validate_protected_action_authority(
        self,
        message: dict[str, Any],
        *,
        task_root: Path,
        current_task_authority: dict[str, Any] | None = None,
        Human_authorization: dict[str, Any] | None = None,
    ) -> None:
        task_id = str(message.get("task_id"))
        sender = str(message.get("sender_endpoint_id"))
        role = str(message.get("sender_task_role"))
        action = str(message.get("requested_action"))
        refs = message.get("required_refs", [])

        # New default: protected actions use a compact Human confirmation record.
        # No task-authority event, nonce, code or delegation chain is required.
        confirmation_ref = message.get("confirmation_ref")
        if confirmation_ref is not None:
            if message.get("authorization_ref") is not None:
                raise CommunicationValidationError("multiple_Human_confirmation_mechanisms")
            if confirmation_ref not in refs:
                raise CommunicationValidationError("confirmation_ref_not_in_required_refs")
            physical = self._load_authority_mapping(task_root, str(confirmation_ref))
            if Human_authorization is not None and Human_authorization != physical:
                raise CommunicationValidationError("Human_confirmation_physical_state_mismatch")
            self._validate_Human_confirmation_v1(
                physical, task_id=task_id, requested_action=action,
            )
            return

        # Legacy compatibility: old authorization documents remain strictly readable
        # when an existing message already references them. New ordinary work should
        # not create these artifacts.
        authorization_ref = message.get("authorization_ref")
        if not authorization_ref or authorization_ref not in refs:
            raise CommunicationValidationError("protected_action_human_confirmation_required")
        if not isinstance(current_task_authority, dict) or (
            current_task_authority.get("task_id") != task_id
            or current_task_authority.get("writer_endpoint_id") != sender
            or current_task_authority.get("writer_task_role") != role
            or current_task_authority.get("requested_action") != action
        ):
            raise CommunicationValidationError("current_task_authority_binding_invalid")
        physical = self._load_authority_mapping(task_root, str(authorization_ref))
        if Human_authorization is not None and Human_authorization != physical:
            raise CommunicationValidationError("Human_authorization_physical_state_mismatch")
        if physical.get("schema_version") in {
            "citystate.communication.direct_human_authorization.v2",
            "citystate.communication.task_authority_delegation.v2",
        }:
            self._validate_v2_authorization_document(
                physical, task_root=task_root, task_id=task_id,
                writer_endpoint_id=sender, writer_task_role=role,
                requested_action=action, required_refs=refs,
            )
            return
        # Historical v1 direct Human authorization remains readable for legacy messages.
        if (
            physical.get("task_id") != task_id
            or physical.get("writer_endpoint_id") != sender
            or physical.get("authorized_action") != action
            or physical.get("granted") is not True
        ):
            raise CommunicationValidationError("protected_action_human_confirmation_required")

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
        if message_type == "correction":
            supersedes = message.get("supersedes")
            if not isinstance(supersedes, str) or not supersedes:
                raise CommunicationValidationError("correction_requires_supersedes")
            canonical_task_relative_ref(supersedes, "correction_supersedes_noncanonical")
            if task_root is not None and not (task_root.resolve() / str(supersedes)).is_file():
                raise CommunicationValidationError("superseded_message_missing")
        elif message.get("supersedes") is not None:
            raise CommunicationValidationError("supersedes_only_valid_for_correction")
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
        for ref in refs:
            canonical_task_relative_ref(ref, "required_ref_noncanonical")
        if message.get("confirmation_ref") and message["confirmation_ref"] not in refs:
            raise CommunicationValidationError("confirmation_ref_not_in_required_refs")
        if message.get("authorization_ref") and message["authorization_ref"] not in refs:
            raise CommunicationValidationError("authorization_ref_not_in_required_refs")
        if message.get("recipient_delegation_ref") and message["recipient_delegation_ref"] not in refs:
            raise CommunicationValidationError("recipient_delegation_ref_not_in_required_refs")
        if message_path is not None:
            expected_name = f"{sequence}_{message_type}.yml"
            if message_path.name != expected_name or message_path.parent.name != message["sender_endpoint_id"]:
                raise CommunicationValidationError("message_path_identity_mismatch")
        if task_root is not None:
            self.validate_recipient_delegation(message, task_root=task_root)
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

    def validate_pointer_v1(self, pointer: dict[str, Any], *, task_root: Path) -> None:
        if not isinstance(pointer, dict) or set(pointer) != POINTER_V1_FIELDS:
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

    @staticmethod
    def _git_blob(repository_root: Path, commit: str, relative: str) -> str:
        # Read the blob as bytes and decode it as strict UTF-8 here. Never let
        # subprocess decode: with text=True it uses the process locale encoding,
        # which on a CP936/GBK Windows host fails inside subprocess's reader
        # thread. That failure does not propagate — returncode stays 0 and
        # stdout becomes None — so a valid UTF-8 blob silently reached
        # parse_safe_yaml as None and surfaced as yaml_input_must_be_text.
        # Repository blobs are UTF-8 by contract, independent of PYTHONUTF8,
        # the host locale or the console code page.
        proc = subprocess.run(
            ["git", "-c", "core.longpaths=true", "show", f"{commit}:{relative}"],
            cwd=repository_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode:
            raise CommunicationValidationError(f"Human_pointer_GitHub_blob_missing:{relative}")
        if not isinstance(proc.stdout, bytes):
            raise CommunicationValidationError(
                f"Human_pointer_GitHub_blob_not_bytes:{relative}"
            )
        try:
            return proc.stdout.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CommunicationValidationError(
                f"Human_pointer_GitHub_blob_not_utf8:{relative}:{exc}"
            ) from exc

    def validate_pointer_v2(
        self,
        pointer: dict[str, Any],
        *,
        task_root: Path,
        repository_root: Path | None = None,
    ) -> dict[str, Any]:
        if not isinstance(pointer, dict) or set(pointer) != POINTER_V2_FIELDS:
            raise CommunicationValidationError("Human_pointer_v2_field_set_invalid")
        if pointer.get("pointer_contract_version") != 2:
            raise CommunicationValidationError("Human_pointer_version_invalid")
        if pointer.get("carrier") not in {"local", "GitHub"}:
            raise CommunicationValidationError("Human_pointer_carrier_invalid")
        if not str(pointer.get("message_id", "")).startswith(
            f"{pointer.get('task_id')}::{pointer.get('sender_endpoint_id')}::"
        ):
            raise CommunicationValidationError("Human_pointer_identity_mismatch")

        catalog = load_yaml(REPO_ROOT / MODEL_CATALOG_REF)
        roles = load_yaml(REPO_ROOT / RECEIVER_ROLE_CONTRACT_REF)
        try:
            validate_receiver_setup(pointer["receiver_setup"], catalog=catalog, role_contract=roles)
        except ReceiverSetupError as exc:
            raise CommunicationValidationError(f"Human_pointer_receiver_setup_invalid:{exc}") from exc

        root = task_root.resolve()
        evidence_refs = (
            str(pointer["constitution_evidence_ref"]),
            str(pointer["compliance_receipt_ref"]),
        )
        for evidence_ref in evidence_refs:
            canonical_task_relative_ref(evidence_ref, "Human_pointer_evidence_ref_noncanonical")
        git_commit: str | None = None
        git_prefix: str | None = None
        exact_trigger_registry: dict[str, Any] | None = None
        if pointer["carrier"] == "local":
            exact = str(pointer["exact_path_or_GitHub_ref"])
            canonical_task_relative_ref(exact, "Human_pointer_path_noncanonical")
            message_path = (root / exact).resolve()
            try:
                message_path.relative_to(root)
            except ValueError as exc:
                raise CommunicationValidationError("Human_pointer_outside_task_root") from exc
            if not message_path.is_file():
                raise CommunicationValidationError("Human_pointer_target_unpublished")
            evidence_paths = []
            for relative in evidence_refs:
                target = (root / relative).resolve()
                try:
                    target.relative_to(root)
                except ValueError as exc:
                    raise CommunicationValidationError("Human_pointer_evidence_outside_task_root") from exc
                if not target.is_file():
                    raise CommunicationValidationError(f"Human_pointer_evidence_missing:{relative}")
                evidence_paths.append(target)
            message = load_yaml(message_path)
            constitution = load_yaml(evidence_paths[0])
            receipt = load_yaml(evidence_paths[1])
            message_relative = exact
        else:
            if repository_root is None:
                raise CommunicationValidationError("Human_pointer_GitHub_repository_root_required")
            repository_root = repository_root.resolve()
            try:
                task_prefix = root.relative_to(repository_root).as_posix()
            except ValueError as exc:
                raise CommunicationValidationError("Human_pointer_task_root_outside_repository") from exc
            exact = str(pointer["exact_path_or_GitHub_ref"])
            match = re.fullmatch(r"([0-9a-f]{40}):(.+)", exact)
            if not match:
                raise CommunicationValidationError("Human_pointer_GitHub_ref_invalid")
            commit, message_repository_path = match.groups()
            git_commit = commit
            prefix = task_prefix.rstrip("/") + "/"
            git_prefix = prefix
            if not message_repository_path.startswith(prefix):
                raise CommunicationValidationError("Human_pointer_GitHub_path_outside_task_root")
            message_relative = message_repository_path.removeprefix(prefix)
            canonical_task_relative_ref(message_relative, "Human_pointer_GitHub_path_noncanonical")
            message = parse_safe_yaml(self._git_blob(repository_root, commit, message_repository_path))
            constitution = parse_safe_yaml(
                self._git_blob(repository_root, commit, f"{prefix}{evidence_refs[0]}")
            )
            receipt = parse_safe_yaml(
                self._git_blob(repository_root, commit, f"{prefix}{evidence_refs[1]}")
            )
            exact_catalog = parse_safe_yaml(
                self._git_blob(repository_root, commit, MODEL_CATALOG_REF)
            )
            exact_roles = parse_safe_yaml(
                self._git_blob(repository_root, commit, RECEIVER_ROLE_CONTRACT_REF)
            )
            exact_trigger_registry = parse_safe_yaml(
                self._git_blob(repository_root, commit, TRIGGER_REGISTRY_REF)
            )
            if not all(isinstance(value, dict) for value in (
                exact_catalog, exact_roles, exact_trigger_registry
            )):
                raise CommunicationValidationError("Human_pointer_exact_contract_mapping_required")
            try:
                validate_receiver_setup(
                    pointer["receiver_setup"],
                    catalog=exact_catalog,
                    role_contract=exact_roles,
                )
            except ReceiverSetupError as exc:
                raise CommunicationValidationError(
                    f"Human_pointer_exact_receiver_setup_invalid:{exc}"
                ) from exc
        self.validate_message(
            message,
            message_path=Path(message_relative),
            task_root=root if pointer["carrier"] == "local" else None,
        )
        if not isinstance(constitution, dict) or not isinstance(receipt, dict):
            raise CommunicationValidationError("Human_pointer_evidence_mapping_required")
        sender_card_ref = f"endpoints/{message['sender_endpoint_id']}.yml"
        recipient_card_ref = f"endpoints/{message['expected_recipient_endpoint_id']}.yml"
        sender_index_ref = f"indexes/{message['sender_endpoint_id']}.yml"
        if pointer["carrier"] == "local":
            manifest = load_yaml(root / "manifest.yml")
            sender_card = load_yaml(root / sender_card_ref)
            recipient_card = load_yaml(root / recipient_card_ref)
            sender_index = load_yaml(root / sender_index_ref)
            for card in (sender_card, recipient_card):
                if isinstance(card, dict):
                    role_ref = canonical_task_relative_ref(
                        card.get("role_context_entry_ref"),
                        "Human_pointer_role_context_ref_noncanonical",
                    )
                    if not (root / role_ref).is_file():
                        raise CommunicationValidationError(
                            f"Human_pointer_role_context_missing:{role_ref}"
                        )
        else:
            assert repository_root is not None and git_commit is not None and git_prefix is not None
            manifest = parse_safe_yaml(
                self._git_blob(repository_root, git_commit, f"{git_prefix}manifest.yml")
            )
            sender_card = parse_safe_yaml(
                self._git_blob(repository_root, git_commit, f"{git_prefix}{sender_card_ref}")
            )
            recipient_card = parse_safe_yaml(
                self._git_blob(repository_root, git_commit, f"{git_prefix}{recipient_card_ref}")
            )
            sender_index = parse_safe_yaml(
                self._git_blob(repository_root, git_commit, f"{git_prefix}{sender_index_ref}")
            )
            for ref in message.get("required_refs") or []:
                self._git_blob(repository_root, git_commit, f"{git_prefix}{ref}")
            if message.get("message_type") == "correction":
                self._git_blob(
                    repository_root, git_commit, f"{git_prefix}{message['supersedes']}"
                )
            for card in (sender_card, recipient_card):
                if isinstance(card, dict):
                    role_ref = canonical_task_relative_ref(
                        card.get("role_context_entry_ref"),
                        "Human_pointer_role_context_ref_noncanonical",
                    )
                    self._git_blob(repository_root, git_commit, f"{git_prefix}{role_ref}")

        if not isinstance(manifest, dict) or (
            manifest.get("task_id") != pointer.get("task_id")
            or manifest.get("communication_contract_version") != 2
        ):
            raise CommunicationValidationError("Human_pointer_manifest_binding_invalid")
        cards = {
            str(message["sender_endpoint_id"]): sender_card,
            str(message["expected_recipient_endpoint_id"]): recipient_card,
        }
        self.validate_role_binding(message, cards)
        try:
            from .sender_zone import validate_sender_index
        except ImportError:
            from sender_zone import validate_sender_index
        validate_sender_index(
            sender_index,
            sender_endpoint_id=str(message["sender_endpoint_id"]),
            task_root=root,
            require_targets=pointer["carrier"] == "local",
        )
        sequence = str(message["message_id"]).rsplit("::", 1)[-1]
        expected_index_entry = {
            "sequence": sequence,
            "message_id": message["message_id"],
            "title": message["title"],
            "message_type": message["message_type"],
            "expected_recipient_endpoint_id": message["expected_recipient_endpoint_id"],
            "expected_recipient_task_role": message["expected_recipient_task_role"],
            "exact_message_path": message_relative,
        }
        if not isinstance(sender_index, list) or sender_index.count(expected_index_entry) != 1:
            raise CommunicationValidationError("Human_pointer_sender_index_binding_invalid")
        for field in (
            "task_id", "message_id", "sender_endpoint_id", "sender_task_role",
            "expected_recipient_endpoint_id", "expected_recipient_task_role",
        ):
            if pointer.get(field) != message.get(field):
                raise CommunicationValidationError(f"Human_pointer_message_binding_mismatch:{field}")
        if pointer.get("one_line_routing_purpose") != message.get("title"):
            raise CommunicationValidationError("Human_pointer_routing_purpose_mismatch")
        expected_constitution_ref = (
            f"constitutions/{message['sender_endpoint_id']}/{sequence}.yml"
        )
        expected_receipt_ref = f"receipts/{message['sender_endpoint_id']}/{sequence}.yml"
        if pointer["constitution_evidence_ref"] != expected_constitution_ref:
            raise CommunicationValidationError("Human_pointer_constitution_path_binding_invalid")
        if pointer["compliance_receipt_ref"] != expected_receipt_ref:
            raise CommunicationValidationError("Human_pointer_receipt_path_binding_invalid")
        if constitution.get("schema_version") != "citystate.formal_action.constitution_evidence.v1":
            raise CommunicationValidationError("Human_pointer_constitution_schema_invalid")
        if receipt.get("schema_version") != "citystate.formal_action.compliance_receipt.v1":
            raise CommunicationValidationError("Human_pointer_receipt_schema_invalid")
        if receipt.get("receipt_role") != "binding_index_only":
            raise CommunicationValidationError("Human_pointer_receipt_role_invalid")
        if receipt.get("constitution_evidence_ref") != expected_constitution_ref:
            raise CommunicationValidationError("Human_pointer_receipt_constitution_binding_invalid")
        if constitution.get("resolver_result_ref") != f"{expected_constitution_ref}#resolution":
            raise CommunicationValidationError("Human_pointer_resolver_result_ref_invalid")
        if constitution.get("gate_result_ref") != f"{expected_constitution_ref}#gate":
            raise CommunicationValidationError("Human_pointer_gate_result_ref_invalid")
        if constitution.get("mechanism_execution_ref") != COMMUNICATION_PUBLISHER_REF:
            raise CommunicationValidationError("Human_pointer_mechanism_execution_ref_invalid")
        if pointer["carrier"] == "local":
            if not (REPO_ROOT / COMMUNICATION_PUBLISHER_REF).is_file():
                raise CommunicationValidationError("Human_pointer_mechanism_execution_missing")
        else:
            assert repository_root is not None and git_commit is not None
            self._git_blob(repository_root, git_commit, COMMUNICATION_PUBLISHER_REF)
        activation_context = constitution.get("activation_context")
        mechanism_preconditions = constitution.get("mechanism_preconditions")
        if not isinstance(activation_context, dict) or not isinstance(mechanism_preconditions, dict):
            raise CommunicationValidationError("Human_pointer_constitution_replay_inputs_missing")
        context_bindings = {
            "action_id": message.get("message_id"),
            "formal_message_type": message.get("message_type"),
            "task_id": message.get("task_id"),
            "sender_endpoint_id": message.get("sender_endpoint_id"),
            "intended_recipient_endpoint_id": message.get("expected_recipient_endpoint_id"),
        }
        for field, expected in context_bindings.items():
            if activation_context.get(field) != expected:
                raise CommunicationValidationError(
                    f"Human_pointer_constitution_context_binding_mismatch:{field}"
                )
        if constitution.get("classification_basis_ref") != activation_context.get(
            "classification_basis_ref"
        ):
            raise CommunicationValidationError(
                "Human_pointer_constitution_classification_basis_mismatch"
            )
        triggers = load_yaml(REPO_ROOT / TRIGGER_REGISTRY_REF)
        try:
            replayed_resolution = resolve_required_mechanisms(activation_context, triggers)
            if set(mechanism_preconditions) != set(replayed_resolution["required_mechanisms"]):
                raise ActivationError("MECHANISM_PRECONDITION_SET_MISMATCH")
            replayed_gate = evaluate_pre_action_gate(
                replayed_resolution,
                mechanism_preconditions,
                refs_root=root if pointer["carrier"] == "local" else None,
            )
            if exact_trigger_registry is not None:
                exact_resolution = resolve_required_mechanisms(
                    activation_context, exact_trigger_registry
                )
                if exact_resolution != replayed_resolution:
                    raise ActivationError("CURRENT_AND_EXACT_TRIGGER_RESOLUTION_MISMATCH")
        except ActivationError as exc:
            raise CommunicationValidationError(
                f"Human_pointer_constitution_replay_rejected:{exc.code}"
            ) from exc
        if constitution.get("resolution") != replayed_resolution:
            raise CommunicationValidationError("Human_pointer_constitution_resolution_replay_mismatch")
        if constitution.get("gate") != replayed_gate:
            raise CommunicationValidationError("Human_pointer_constitution_gate_replay_mismatch")
        if constitution.get("receiver_setup") != pointer.get("receiver_setup"):
            raise CommunicationValidationError("Human_pointer_constitution_receiver_setup_mismatch")
        try:
            validate_constitution_evidence(
                constitution,
                resolution=replayed_resolution,
                gate=replayed_gate,
            )
        except ActivationError as exc:
            raise CommunicationValidationError(f"Human_pointer_activation_evidence_invalid:{exc.code}") from exc
        if constitution.get("action_id") != pointer.get("message_id"):
            raise CommunicationValidationError("Human_pointer_constitution_action_mismatch")
        if constitution.get("formal_artifact_ref") != message_relative:
            raise CommunicationValidationError("Human_pointer_constitution_artifact_mismatch")
        if receipt.get("action_id") != pointer.get("message_id"):
            raise CommunicationValidationError("Human_pointer_receipt_action_mismatch")
        publication_claims = [
            claim for claim in receipt.get("material_claims", [])
            if isinstance(claim, dict) and claim.get("claim_role") == "communication_publication"
        ]
        if len(publication_claims) != 1:
            raise CommunicationValidationError(
                "Human_pointer_activation_evidence_invalid:MATERIAL_PUBLICATION_CLAIM_CARDINALITY"
            )
        publication_claim = publication_claims[0]
        expected_publication = {
            "task_id": activation_context.get("task_id"),
            "message_id": constitution.get("action_id"),
            "carrier": pointer.get("carrier"),
            "sender_endpoint_id": constitution.get("sender_endpoint_id"),
            "expected_recipient_endpoint_id": constitution.get("intended_recipient_endpoint_id"),
            "materialized_path": constitution.get("formal_artifact_ref"),
        }
        observed_publication = {
            "task_id": message.get("task_id"),
            "message_id": message.get("message_id"),
            "carrier": pointer.get("carrier"),
            "sender_endpoint_id": message.get("sender_endpoint_id"),
            "expected_recipient_endpoint_id": message.get("expected_recipient_endpoint_id"),
            "materialized_path": message_relative,
        }
        if publication_claim.get("expected_claim_source_ref") != pointer["constitution_evidence_ref"]:
            raise CommunicationValidationError("Human_pointer_publication_expected_source_mismatch")
        if publication_claim.get("expected_value_or_predicate") != expected_publication:
            raise CommunicationValidationError("Human_pointer_publication_expected_binding_mismatch")
        if publication_claim.get("observed_value") != observed_publication:
            raise CommunicationValidationError(
                "Human_pointer_activation_evidence_invalid:MATERIAL_OBSERVATION_CONTEXT_MISMATCH"
            )
        allowed_receipt_observation_refs = {
            f"publisher-materialization:{pointer['carrier']}:{message_relative}",
            f"communication_publication_readback:{message_relative}",
        }
        receipt_observation_ref = str(publication_claim.get("exact_observation_ref", ""))
        if receipt_observation_ref not in allowed_receipt_observation_refs:
            raise CommunicationValidationError("Human_pointer_publication_observation_ref_mismatch")
        if publication_claim.get("observed_authoritative_source_class") != "communication_publisher_observation":
            raise CommunicationValidationError("Human_pointer_publication_source_class_mismatch")
        receipt_context = MaterialObservationContext()
        try:
            receipt_kind = (
                "publisher_materialization"
                if receipt_observation_ref.startswith("publisher-materialization:")
                else "communication_publication_readback"
            )
            if pointer["carrier"] == "local":
                observe_communication_message_local_claim(
                    root,
                    claim_id=str(publication_claim.get("claim_id")),
                    action_id_or_review_id=str(pointer["message_id"]),
                    constitution_ref=str(pointer["constitution_evidence_ref"]),
                    message_relative=message_relative,
                    carrier="local",
                    observation_kind=receipt_kind,
                    observation_context=receipt_context,
                )
            else:
                assert repository_root is not None and git_commit is not None and git_prefix is not None
                observe_communication_message_git_claim(
                    repository_root,
                    claim_id=str(publication_claim.get("claim_id")),
                    action_id_or_review_id=str(pointer["message_id"]),
                    commit=git_commit,
                    constitution_repo_path=f"{git_prefix}{pointer['constitution_evidence_ref']}",
                    constitution_ref=str(pointer["constitution_evidence_ref"]),
                    message_repo_path=f"{git_prefix}{message_relative}",
                    message_relative=message_relative,
                    observation_kind=receipt_kind,
                    observation_context=receipt_context,
                )
            validate_material_receipt(receipt, receipt_context)
        except ActivationError as exc:
            raise CommunicationValidationError(
                f"Human_pointer_activation_evidence_invalid:{exc.code}"
            ) from exc
        receiver_context = MaterialObservationContext()
        receiver_claim_id = f"{pointer['message_id']}::receiver-publication-readback"
        try:
            if pointer["carrier"] == "local":
                receiver_publication_claim = observe_communication_message_local_claim(
                    root,
                    claim_id=receiver_claim_id,
                    action_id_or_review_id=str(pointer["message_id"]),
                    constitution_ref=str(pointer["constitution_evidence_ref"]),
                    message_relative=message_relative,
                    carrier="local",
                    observation_kind="exact_local_pointer",
                    exact_pointer_ref=str(pointer["exact_path_or_GitHub_ref"]),
                    observation_context=receiver_context,
                )
            else:
                assert repository_root is not None and git_commit is not None and git_prefix is not None
                receiver_publication_claim = observe_communication_message_git_claim(
                    repository_root,
                    claim_id=receiver_claim_id,
                    action_id_or_review_id=str(pointer["message_id"]),
                    commit=git_commit,
                    constitution_repo_path=f"{git_prefix}{pointer['constitution_evidence_ref']}",
                    constitution_ref=str(pointer["constitution_evidence_ref"]),
                    message_repo_path=f"{git_prefix}{message_relative}",
                    message_relative=message_relative,
                    observation_kind="exact_git_pointer",
                    exact_pointer_ref=str(pointer["exact_path_or_GitHub_ref"]),
                    observation_context=receiver_context,
                )
        except ActivationError as exc:
            raise CommunicationValidationError(
                f"Human_pointer_publication_readback_unverified:{exc.code}"
            ) from exc
        if receiver_publication_claim["verification_result"] != "VERIFIED":
            raise CommunicationValidationError("Human_pointer_publication_readback_unverified")
        activation_refs = [
            constitution.get("classification_basis_ref"),
            pointer["receiver_setup"].get("routing_basis_ref"),
            pointer["receiver_setup"].get("availability_assumption_or_observation_ref"),
            *(constitution.get("gate", {}).get("verified_precondition_refs", {}).values()),
        ]
        for reference in activation_refs:
            if not isinstance(reference, str) or not reference:
                raise CommunicationValidationError("Human_pointer_activation_ref_invalid")
            clean = reference.split("#", 1)[0]
            canonical_task_relative_ref(reference, "Human_pointer_activation_ref_noncanonical")
            if pointer["carrier"] == "local":
                target = (root / clean).resolve()
                try:
                    target.relative_to(root)
                except ValueError as exc:
                    raise CommunicationValidationError("Human_pointer_activation_ref_outside_task") from exc
                if not target.is_file():
                    raise CommunicationValidationError(f"Human_pointer_activation_ref_missing:{clean}")
            else:
                assert repository_root is not None and git_commit is not None and git_prefix is not None
                self._git_blob(repository_root, git_commit, f"{git_prefix}{clean}")
        return {
            "message": message,
            "constitution": constitution,
            "compliance_receipt": receipt,
            "message_relative_path": message_relative,
            "sender_index": sender_index,
            "sender_index_ref": sender_index_ref,
            "activation_refs": list(dict.fromkeys(str(ref) for ref in activation_refs)),
            "receiver_publication_claim": receiver_publication_claim,
        }

    def validate_pointer(
        self,
        pointer: dict[str, Any],
        *,
        task_root: Path,
        repository_root: Path | None = None,
        allow_legacy_v1: bool = False,
    ) -> dict[str, Any] | None:
        if isinstance(pointer, dict) and pointer.get("pointer_contract_version") == 2:
            return self.validate_pointer_v2(
                pointer, task_root=task_root, repository_root=repository_root
            )
        if allow_legacy_v1:
            self.validate_pointer_v1(pointer, task_root=task_root)
            return None
        raise CommunicationValidationError("legacy_v1_pointer_read_only_explicit_mode_required")


def validate_static_repository(repo_root: Path) -> None:
    root = repo_root.resolve()
    os_root = root / "01_os"
    manifest_path = os_root / "02_boot/communication_system/启动清单_v1.yml"
    manifest = load_yaml(manifest_path)
    if manifest.get("background_processes_started") is not False:
        raise CommunicationValidationError("boot_background_boundary_invalid")
    if manifest.get("canonical_live_state_created_by_boot") is not False:
        raise CommunicationValidationError("boot_live_state_boundary_invalid")
    for relative in manifest.get("load_order") or []:
        if not (root / relative).is_file():
            raise CommunicationValidationError(f"boot_ref_missing:{relative}")
    required_activation_refs = {
        "01_os/03_mechanisms/communication_system/正式动作接入契约_v1.yml",
        "01_os/03_mechanisms/communication_system/Human中转指针契约_v2.yml",
    }
    if not required_activation_refs.issubset(set(manifest.get("load_order") or [])):
        raise CommunicationValidationError("boot_formal_activation_surface_incomplete")
    mechanism = os_root / "03_mechanisms/communication_system"
    communication_contract = load_yaml(mechanism / "通讯契约_v1.yml")
    expected_root_resolution = {
        "precedence": [
            "explicit_--root",
            "environment_CITYSTATE_COMMUNICATION_ROOT",
            "user_home_default",
        ],
        "environment_variable": "CITYSTATE_COMMUNICATION_ROOT",
        "default_expression": 'Path.home() / ".citystate" / "communication"',
        "repository_partition": "<resolved_communication_root>/<repository_id>/",
    }
    if communication_contract.get("local_root_resolution") != expected_root_resolution:
        raise CommunicationValidationError("communication_root_resolution_contract_invalid")
    formal = load_yaml(mechanism / "正式动作接入契约_v1.yml")
    if formal.get("direct_publisher_call_without_activation_bundle") != "FORMAL_ACTIVATION_REQUIRED":
        raise CommunicationValidationError("formal_publisher_gate_contract_invalid")
    required_formal_validity = {
        "sender_index_exactly_binds_message_identity_and_route",
        "receiver_replays_resolver_and_gate_from_saved_inputs",
        "recipient_delegation_revalidated_from_carrier_state_when_present",
        "GitHub_recipient_delegation_current_liveness_revalidated_when_present",
        "canonical_mechanism_execution_ref_physically_resolves",
        "correction_physically_binds_existing_superseded_message_when_applicable",
    }
    if not required_formal_validity.issubset(
        set(formal.get("formal_action_validity_requires") or [])
    ):
        raise CommunicationValidationError("formal_receiver_closure_contract_incomplete")
    pointer_v2 = load_yaml(mechanism / "Human中转指针契约_v2.yml")
    if pointer_v2.get("pointer_contract_version") != 2:
        raise CommunicationValidationError("pointer_v2_contract_invalid")
    if pointer_v2.get("migration", {}).get("v1_pointer", {}).get("new_formal_publication") != "prohibited":
        raise CommunicationValidationError("pointer_v1_migration_boundary_invalid")
    required_git_validation = {
        "sender_index_contains_exact_message_binding_at_same_commit",
        "mechanism_execution_ref_is_canonical_and_exists_at_same_commit",
        "correction_supersedes_blob_exists_at_same_commit_when_applicable",
        "recipient_delegation_chain_revalidated_from_exact_commit_when_present",
        "recipient_delegation_current_liveness_revalidated_from_physical_task_root_when_present",
    }
    if not required_git_validation.issubset(set(pointer_v2.get("GitHub_validation") or [])):
        raise CommunicationValidationError("pointer_v2_physical_closure_incomplete")
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

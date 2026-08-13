#!/usr/bin/env python3
"""Publish one validated immutable message and return a pointer for Human relay."""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

VALID_GITHUB_TRIGGERS = {
    "web_recipient", "Human_explicit_request", "full_task_convergence",
}


class NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


def _dump_yaml(value: Any) -> str:
    return yaml.dump(
        value,
        Dumper=NoAliasSafeDumper,
        allow_unicode=True,
        sort_keys=False,
    )

BOOT_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_ROOT = BOOT_ROOT / "validator"
if str(VALIDATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_ROOT))
from sender_zone import next_sequence, validate_sender_index  # noqa: E402
from validate_communication_system import (  # noqa: E402
    CommunicationValidationError,
    CommunicationValidator,
    canonical_task_relative_ref,
    load_yaml,
    parse_safe_yaml,
)

REPO_ROOT = Path(__file__).resolve().parents[5]
ACTIVATION_ROOT = REPO_ROOT / "01_os/06_execution/boot/mechanism_activation"
MODEL_ROUTING_ROOT = REPO_ROOT / "01_os/06_execution/boot/model_routing"
for module_root in (ACTIVATION_ROOT, MODEL_ROUTING_ROOT):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))
from activation import (  # noqa: E402
    ActivationError,
    evaluate_material_claim,
    evaluate_pre_action_gate,
    resolve_required_mechanisms,
    validate_constitution_evidence,
    validate_material_receipt,
)
from route_receiver import (  # noqa: E402
    ReceiverSetupError,
    validate_receiver_setup,
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
    if isinstance(value, dict):
        if prohibited_keys & {str(key).lower() for key in value}:
            raise CommunicationValidationError("forbidden_data_marker")
        for nested in value.values():
            _privacy_check(nested, privacy_class, carrier)
    elif isinstance(value, list):
        for nested in value:
            _privacy_check(nested, privacy_class, carrier)


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


def _task_ref(root: Path, relative: str, code: str) -> Path:
    clean = canonical_task_relative_ref(relative, f"{code}_noncanonical")
    target = (root.resolve() / clean).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise CommunicationValidationError(f"{code}_outside_task_root") from exc
    if not target.is_file():
        raise CommunicationValidationError(f"{code}_missing:{clean}")
    return target


def _prepare_formal_activation(
    root: Path,
    message: dict[str, Any],
    *,
    message_relative: str,
    activation_context: dict[str, Any] | None,
    mechanism_preconditions: dict[str, Any] | None,
    receiver_setup: dict[str, Any] | None,
    cards: dict[str, dict[str, Any]],
    carrier: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str]:
    if not isinstance(activation_context, dict) or not isinstance(mechanism_preconditions, dict):
        raise CommunicationValidationError("FORMAL_ACTIVATION_REQUIRED")
    if not isinstance(receiver_setup, dict):
        raise CommunicationValidationError("RECEIVER_SETUP_REQUIRED")
    if receiver_setup.get("communication_carrier") != carrier:
        raise CommunicationValidationError("RECEIVER_SETUP_CARRIER_MISMATCH")
    context = dict(activation_context)
    bindings = {
        "action_id": message["message_id"],
        "formal_message_type": message["message_type"],
        "task_id": message["task_id"],
        "sender_endpoint_id": message["sender_endpoint_id"],
        "intended_recipient_endpoint_id": message["expected_recipient_endpoint_id"],
    }
    for field, expected in bindings.items():
        if field in context and context[field] != expected:
            raise CommunicationValidationError(f"FORMAL_ACTIVATION_MESSAGE_BINDING_MISMATCH:{field}")
        context[field] = expected
    if not context.get("classification_basis_ref"):
        raise CommunicationValidationError("FORMAL_CLASSIFICATION_BASIS_REQUIRED")
    _task_ref(root, str(context["classification_basis_ref"]), "FORMAL_CLASSIFICATION_BASIS")
    for setup_ref in (
        receiver_setup.get("routing_basis_ref"),
        receiver_setup.get("availability_assumption_or_observation_ref"),
    ):
        if not isinstance(setup_ref, str):
            raise CommunicationValidationError("RECEIVER_SETUP_EVIDENCE_REF_REQUIRED")
        _task_ref(root, setup_ref, "RECEIVER_SETUP_EVIDENCE_REF")

    catalog = load_yaml(REPO_ROOT / "01_os/03_mechanisms/model_routing/模型与产品面目录_v1.yml")
    role_contract = load_yaml(
        REPO_ROOT / "01_os/03_mechanisms/model_routing/协作角色与接收者设置契约_v1.yml"
    )
    try:
        validate_receiver_setup(receiver_setup, catalog=catalog, role_contract=role_contract)
        triggers = load_yaml(
            REPO_ROOT / "01_os/03_mechanisms/mechanism_activation/机制触发注册表_v1.yml"
        )
        resolution = resolve_required_mechanisms(context, triggers, endpoint_cards=cards)
        if set(mechanism_preconditions) != set(resolution["required_mechanisms"]):
            raise ActivationError(
                "MECHANISM_PRECONDITION_SET_MISMATCH",
                expected=resolution["required_mechanisms"],
                observed=sorted(str(key) for key in mechanism_preconditions),
            )
        gate = evaluate_pre_action_gate(
            resolution, mechanism_preconditions, refs_root=root
        )
    except (ActivationError, ReceiverSetupError) as exc:
        raise CommunicationValidationError(f"FORMAL_ACTIVATION_REJECTED:{exc}") from exc
    if gate["gate_result"] != "VERIFIED":
        raise CommunicationValidationError(
            "FORMAL_PRE_ACTION_GATE_BLOCKED:" + ",".join(gate["blocking_failures"])
        )

    sequence = message["message_id"].rsplit("::", 1)[-1]
    constitution_ref = f"constitutions/{message['sender_endpoint_id']}/{sequence}.yml"
    receipt_ref = f"receipts/{message['sender_endpoint_id']}/{sequence}.yml"
    constitution = {
        "schema_version": "citystate.formal_action.constitution_evidence.v1",
        "action_id": message["message_id"],
        "action_class": resolution["action_class"],
        "sender_endpoint_id": message["sender_endpoint_id"],
        "intended_recipient_endpoint_id": resolution["normalized_recipient_endpoint_id"],
        "classification_basis_ref": context["classification_basis_ref"],
        "required_mechanisms": resolution["required_mechanisms"],
        "resolver_result_ref": f"{constitution_ref}#resolution",
        "gate_result_ref": f"{constitution_ref}#gate",
        "mechanism_execution_ref": (
            "01_os/06_execution/boot/communication_system/publisher/publish_message.py"
        ),
        "formal_artifact_ref": message_relative,
        "activation_context": context,
        "mechanism_preconditions": mechanism_preconditions,
        "authority_effect": "none",
        "resolution": resolution,
        "gate": gate,
        "receiver_setup": receiver_setup,
    }
    try:
        validate_constitution_evidence(constitution, resolution=resolution, gate=gate)
    except ActivationError as exc:
        raise CommunicationValidationError(f"FORMAL_CONSTITUTION_INVALID:{exc.code}") from exc
    return resolution, gate, constitution, constitution_ref, receipt_ref


def _compliance_receipt(
    root: Path,
    constitution: dict[str, Any],
    *,
    message_relative: str,
    constitution_ref: str,
    carrier: str,
) -> dict[str, Any]:
    materialized = load_yaml(root / message_relative)
    claim = {
        "claim_id": f"{constitution['action_id']}::local-materialization",
        "claim_role": "communication_publication",
        "action_id_or_review_id": constitution["action_id"],
        "expected_claim_source_ref": constitution_ref,
        "expected_value_or_predicate": {
            "task_id": constitution["activation_context"]["task_id"],
            "message_id": constitution["action_id"],
            "carrier": constitution["receiver_setup"]["communication_carrier"],
            "sender_endpoint_id": constitution["sender_endpoint_id"],
            "expected_recipient_endpoint_id": constitution["intended_recipient_endpoint_id"],
            "materialized_path": constitution["formal_artifact_ref"],
        },
        "observed_authoritative_source_class": "communication_publisher_observation",
        "observed_value": {
            "task_id": materialized.get("task_id"),
            "message_id": materialized.get("message_id"),
            "carrier": carrier,
            "sender_endpoint_id": materialized.get("sender_endpoint_id"),
            "expected_recipient_endpoint_id": materialized.get("expected_recipient_endpoint_id"),
            "materialized_path": message_relative,
        },
        "exact_observation_ref": f"publisher-materialization:{carrier}:{message_relative}",
        "comparator_id": "published_message_identity_and_route_equality",
        "relationship_or_equality_check": "expected_message_identity_equals_materialized_identity",
        "verification_result": "UNVERIFIABLE",
    }
    claim["verification_result"] = evaluate_material_claim(claim)
    receipt = {
        "schema_version": "citystate.formal_action.compliance_receipt.v1",
        "action_id": constitution["action_id"],
        "constitution_evidence_ref": constitution_ref,
        "receipt_role": "binding_index_only",
        "material_claims": [claim],
        "aggregate_result": "VERIFIED" if claim["verification_result"] == "VERIFIED" else "BLOCKED",
    }
    try:
        validate_material_receipt(receipt)
    except ActivationError as exc:
        raise CommunicationValidationError(f"FORMAL_COMPLIANCE_RECEIPT_INVALID:{exc.code}") from exc
    return receipt


def publish(task_root: Path, message_source: Path, *, carrier: str = "local",
            github_trigger: str | None = None,
            privacy_class: str = "repository_shareable",
            protected_action: bool = False,
            current_task_authority: dict[str, Any] | None = None,
            Human_authorization: dict[str, Any] | None = None,
            publication_trace: list[str] | None = None,
            activation_context: dict[str, Any] | None = None,
            mechanism_preconditions: dict[str, Any] | None = None,
            receiver_setup: dict[str, Any] | None = None,
            _defer_GitHub_readback: bool = False) -> dict[str, Any]:
    if carrier not in {"local", "GitHub"}:
        raise CommunicationValidationError("carrier_invalid")
    if carrier == "GitHub" and github_trigger not in VALID_GITHUB_TRIGGERS:
        raise CommunicationValidationError("GitHub_publication_requires_explicit_trigger")
    root = task_root.resolve()
    message = load_yaml(message_source)
    trace = publication_trace if publication_trace is not None else []
    _privacy_check(message, privacy_class, carrier)
    for formal_value in (activation_context, mechanism_preconditions, receiver_setup):
        _privacy_check(formal_value, privacy_class, carrier)
    CommunicationValidator().validate_inline_content(str(message.get("content", "")))
    cards = _endpoint_cards(root, message)
    _validate_required_documents(root, message, carrier, trace)
    manifest_path = root / "manifest.yml"
    if manifest_path.is_file():
        manifest = load_yaml(manifest_path)
        if manifest.get("task_id") != message.get("task_id"):
            raise CommunicationValidationError("publication_task_scope_mismatch")
        if manifest.get("communication_contract_version") != 2:
            raise CommunicationValidationError("formal_publication_requires_v2_manifest")
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
    if carrier == "GitHub" and not _defer_GitHub_readback:
        raise CommunicationValidationError("GitHub_formal_publication_requires_convergence_wrapper")
    validator.validate_message(message, message_path=target, task_root=root, cards=cards)
    _, _, constitution, constitution_ref, receipt_ref = _prepare_formal_activation(
        root,
        message,
        message_relative=relative,
        activation_context=activation_context,
        mechanism_preconditions=mechanism_preconditions,
        receiver_setup=receiver_setup,
        cards=cards,
        carrier=carrier,
    )
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
    constitution_path = root / constitution_ref
    receipt_path = root / receipt_ref
    created: list[Path] = []
    index_existed = index_path.exists()
    index_before = index_path.read_text(encoding="utf-8") if index_existed else None
    try:
        _atomic_create(
            constitution_path,
            _dump_yaml(constitution),
        )
        created.append(constitution_path)
        trace.append(f"constitution_published:{constitution_ref}")
        _atomic_create(target, _dump_yaml(message))
        created.append(target)
        trace.append(f"message_published:{relative}")
        validate_sender_index(updated, sender_endpoint_id=sender, task_root=root, baseline=entries)
        _atomic_replace(index_path, _dump_yaml(updated))
        trace.append(f"index_updated:indexes/{sender}.yml")
        receipt = _compliance_receipt(
            root,
            constitution,
            message_relative=relative,
            constitution_ref=constitution_ref,
            carrier=carrier,
        )
        _atomic_create(
            receipt_path,
            _dump_yaml(receipt),
        )
        created.append(receipt_path)
        trace.append(f"compliance_receipt_published:{receipt_ref}")
    except Exception:
        if index_existed and index_before is not None:
            _atomic_replace(index_path, index_before)
        else:
            index_path.unlink(missing_ok=True)
        for created_path in reversed(created):
            created_path.unlink(missing_ok=True)
        trace.append(f"message_rolled_back:{relative}")
        raise
    document_refs = [
        ref for ref in message.get("required_refs", [])
        if Path(ref).parts[:1] == ("documents",)
    ]
    validator.validate_publication_trace(trace, document_refs)
    pointer = {
        "pointer_contract_version": 2,
        "task_id": message["task_id"],
        "message_id": message["message_id"],
        "carrier": carrier,
        "exact_path_or_GitHub_ref": relative,
        "sender_endpoint_id": sender,
        "sender_task_role": message["sender_task_role"],
        "expected_recipient_endpoint_id": message["expected_recipient_endpoint_id"],
        "expected_recipient_task_role": message["expected_recipient_task_role"],
        "one_line_routing_purpose": message["title"],
        "constitution_evidence_ref": constitution_ref,
        "compliance_receipt_ref": receipt_ref,
        "receiver_setup": receiver_setup,
    }
    if carrier == "local":
        validator.validate_pointer(pointer, task_root=root)
    return pointer


def bind_GitHub_pointer(
    pointer: dict[str, Any],
    *,
    repository_root: Path,
    repository_task_root: Path,
    remote_commit_sha: str,
) -> dict[str, Any]:
    """Bind a provisional GitHub pointer to the exact remotely read-back commit."""
    if not re.fullmatch(r"[0-9a-f]{40}", remote_commit_sha):
        raise CommunicationValidationError("GitHub_remote_commit_sha_invalid")
    repository_root = repository_root.resolve()
    repository_task_root = repository_task_root.resolve()
    try:
        prefix = repository_task_root.relative_to(repository_root).as_posix()
    except ValueError as exc:
        raise CommunicationValidationError("GitHub_task_root_outside_repository") from exc
    bound = dict(pointer)
    relative = str(pointer["exact_path_or_GitHub_ref"])
    bound["carrier"] = "GitHub"
    bound["exact_path_or_GitHub_ref"] = f"{remote_commit_sha}:{prefix}/{relative}"
    CommunicationValidator().validate_pointer(
        bound,
        task_root=repository_task_root,
        repository_root=repository_root,
    )
    return bound


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-root", required=True, type=Path)
    parser.add_argument("--message", required=True, type=Path)
    parser.add_argument("--carrier", choices=["local", "GitHub"], default="local")
    parser.add_argument("--github-trigger", choices=sorted(VALID_GITHUB_TRIGGERS))
    parser.add_argument("--privacy-class", choices=["repository_shareable", "local_only", "forbidden"],
                        default="repository_shareable")
    parser.add_argument("--activation-context", required=True, type=Path)
    parser.add_argument("--mechanism-preconditions", required=True, type=Path)
    parser.add_argument("--receiver-setup", required=True, type=Path)
    args = parser.parse_args()
    try:
        pointer = publish(args.task_root, args.message, carrier=args.carrier,
                          github_trigger=args.github_trigger, privacy_class=args.privacy_class,
                          activation_context=load_yaml(args.activation_context),
                          mechanism_preconditions=load_yaml(args.mechanism_preconditions),
                          receiver_setup=load_yaml(args.receiver_setup))
    except (CommunicationValidationError, OSError, yaml.YAMLError) as exc:
        print(f"publication_rejected:{exc}", file=sys.stderr)
        return 2
    print(yaml.safe_dump(pointer, allow_unicode=True, sort_keys=False), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

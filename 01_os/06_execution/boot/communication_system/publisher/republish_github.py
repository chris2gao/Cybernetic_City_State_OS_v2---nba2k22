#!/usr/bin/env python3
"""Explicitly republish one local message into a Git task tree and converge once."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

BOOT_ROOT = Path(__file__).resolve().parents[1]
for module_root in (Path(__file__).resolve().parent, BOOT_ROOT / "validator", BOOT_ROOT / "convergence"):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

from converge_task import converge  # noqa: E402
from publish_message import (  # noqa: E402
    VALID_GITHUB_TRIGGERS,
    _atomic_create,
    _endpoint_cards,
    _privacy_check,
    _validate_required_documents,
    bind_GitHub_pointer,
    publish,
)
from validate_communication_system import (  # noqa: E402
    CommunicationValidationError,
    CommunicationValidator,
    canonical_task_relative_ref,
    load_yaml,
)


def _task_relative_file(root: Path, relative: str) -> Path:
    clean = canonical_task_relative_ref(relative, "GitHub_material_ref_noncanonical")
    target = (root.resolve() / clean).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise CommunicationValidationError("GitHub_material_outside_task_root") from exc
    if not target.is_file():
        raise CommunicationValidationError(f"GitHub_material_missing:{relative}")
    return target


def _material_refs(local_root: Path, message: dict[str, Any],
                   cards: dict[str, dict[str, Any]],
                   activation_context: dict[str, Any],
                   mechanism_preconditions: dict[str, Any],
                   receiver_setup: dict[str, Any]) -> list[str]:
    refs = ["manifest.yml"]
    for endpoint_id in (
        message["sender_endpoint_id"],
        message["expected_recipient_endpoint_id"],
    ):
        refs.append(f"endpoints/{endpoint_id}.yml")
        refs.append(str(cards[endpoint_id]["role_context_entry_ref"]))
    refs.extend(message.get("required_refs", []))
    refs.append(str(activation_context.get("classification_basis_ref", "")))
    for precondition in mechanism_preconditions.values():
        if isinstance(precondition, dict):
            refs.append(str(precondition.get("evidence_ref", "")))
    refs.extend([
        str(receiver_setup.get("routing_basis_ref", "")),
        str(receiver_setup.get("availability_assumption_or_observation_ref", "")),
    ])
    ordered = []
    for ref in refs:
        clean = ref.split("#", 1)[0]
        if clean and clean not in ordered:
            _task_relative_file(local_root, clean)
            ordered.append(clean)
    return ordered


def _copy_immutable(source: Path, target: Path) -> bool:
    content = source.read_bytes()
    if target.exists():
        if not target.is_file() or target.read_bytes() != content:
            raise CommunicationValidationError("GitHub_material_immutable_conflict")
        return False
    _atomic_create(target, content.decode("utf-8"))
    return True


def republish_and_converge(
    local_task_root: Path,
    repository_task_root: Path,
    message_source: Path,
    *,
    repository_root: Path,
    branch: str,
    allowed_task_root: str,
    github_trigger: str,
    privacy_class: str = "repository_shareable",
    publication_trace: list[str] | None = None,
    activation_context: dict[str, Any] | None = None,
    mechanism_preconditions: dict[str, Any] | None = None,
    receiver_setup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if github_trigger not in VALID_GITHUB_TRIGGERS:
        raise CommunicationValidationError("GitHub_publication_requires_explicit_trigger")
    local_root = local_task_root.resolve()
    repo_task = repository_task_root.resolve()
    repo_root = repository_root.resolve()
    try:
        repo_task.relative_to(repo_root)
    except ValueError as exc:
        raise CommunicationValidationError("GitHub_task_root_outside_repository") from exc
    message = load_yaml(message_source)
    if not isinstance(activation_context, dict) or not isinstance(mechanism_preconditions, dict):
        raise CommunicationValidationError("FORMAL_ACTIVATION_REQUIRED")
    if not isinstance(receiver_setup, dict):
        raise CommunicationValidationError("RECEIVER_SETUP_REQUIRED")
    trace = publication_trace if publication_trace is not None else []
    _privacy_check(message, privacy_class, "GitHub")
    cards = _endpoint_cards(local_root, message)
    validator = CommunicationValidator()
    validator.validate_message(message, task_root=local_root, cards=cards)
    validator.validate_carrier_route(
        expected_recipient_environment=str(
            cards[message["expected_recipient_endpoint_id"]].get("environment_class")
        ),
        carrier="GitHub",
        Human_requested_GitHub=github_trigger == "Human_explicit_request",
        full_convergence_requested=github_trigger == "full_task_convergence",
    )
    _validate_required_documents(local_root, message, "GitHub", trace)
    copied_refs = []
    for relative in _material_refs(
        local_root, message, cards, activation_context, mechanism_preconditions, receiver_setup
    ):
        source = _task_relative_file(local_root, relative)
        target = repo_task / relative
        if _copy_immutable(source, target):
            copied_refs.append(relative)
        trace.append(f"GitHub_material_published:{relative}")
    pointer = publish(
        repo_task,
        message_source,
        carrier="GitHub",
        github_trigger=github_trigger,
        privacy_class=privacy_class,
        publication_trace=trace,
        activation_context=activation_context,
        mechanism_preconditions=mechanism_preconditions,
        receiver_setup=receiver_setup,
        _defer_GitHub_readback=True,
    )
    repository_prefix = repo_task.relative_to(repo_root).as_posix()
    exact_paths = [f"{repository_prefix}/{relative}" for relative in copied_refs]
    exact_paths.extend([
        f"{repository_prefix}/{pointer['exact_path_or_GitHub_ref']}",
        f"{repository_prefix}/indexes/{message['sender_endpoint_id']}.yml",
        f"{repository_prefix}/{pointer['constitution_evidence_ref']}",
        f"{repository_prefix}/{pointer['compliance_receipt_ref']}",
    ])
    convergence = converge(
        repo_root,
        branch,
        exact_paths,
        allowed_task_root,
        f"publish {message['message_id']} for Human relay",
    )
    bound_pointer = bind_GitHub_pointer(
        pointer,
        repository_root=repo_root,
        repository_task_root=repo_task,
        remote_commit_sha=convergence["remote_head"],
    )
    return {
        "pointer": bound_pointer,
        "publication_trace": trace,
        "convergence": convergence,
        "exact_published_paths": exact_paths,
    }

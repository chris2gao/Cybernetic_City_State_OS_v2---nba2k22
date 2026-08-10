"""Correction immutability, endpoint parity, and frozen cross-model scoring."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from .validate_communication_system import CommunicationValidationError, CommunicationValidator, load_yaml
except ImportError:
    from validate_communication_system import CommunicationValidationError, CommunicationValidator, load_yaml


def verify_immutable_published_message(original: bytes, observed: bytes) -> None:
    if original != observed:
        raise CommunicationValidationError("published_message_mutation_prohibited")


def validate_correction(message: dict[str, Any], *, task_root: Path) -> None:
    CommunicationValidator().validate_message(message, task_root=task_root)
    if message.get("message_type") != "correction" or not message.get("supersedes"):
        raise CommunicationValidationError("correction_requires_supersedes")
    target = (task_root.resolve() / str(message["supersedes"])).resolve()
    try:
        target.relative_to(task_root.resolve())
    except ValueError as exc:
        raise CommunicationValidationError("supersedes_outside_task_root") from exc
    if not target.is_file():
        raise CommunicationValidationError("superseded_message_missing")


def assert_endpoint_parity(local: dict[str, Any], web: dict[str, Any]) -> None:
    validator = CommunicationValidator()
    validator.validate_message(local)
    validator.validate_message(web)
    if local != web:
        raise CommunicationValidationError("endpoint_canonical_parity_mismatch")


def score_cross_model(packet_path: Path, result_paths: list[Path]) -> None:
    packet = load_yaml(packet_path)
    task_id = packet.get("task_id")
    for result_path in result_paths:
        result = load_yaml(result_path)
        fixtures = result.get("fixture_results") if isinstance(result, dict) else None
        if not isinstance(fixtures, list):
            raise CommunicationValidationError("cross_model_fixture_results_missing")
        for fixture in fixtures:
            fixture_id = fixture.get("fixture_id")
            recovered = fixture.get("recovered")
            if not isinstance(recovered, dict):
                raise CommunicationValidationError(f"cross_model_recovered_missing:{fixture_id}")
            if recovered.get("task_id") != task_id:
                raise CommunicationValidationError(f"cross_model_task_id_mismatch:{fixture_id}")
            sender = recovered.get("sender_endpoint_id")
            recipient = recovered.get("expected_recipient_endpoint_id")
            purpose = str(recovered.get("message_type_and_purpose", ""))
            paths = set(recovered.get("exact_paths_to_read") or [])
            if fixture_id in {"F1-minimal-yaml-index", "F2-compact-json-index", "F3-free-text-pointer"}:
                expected = {
                    "08_os/_runs/run-x/06_执行/发布任务包.yml",
                    "08_os/_runs/run-x/durable/Human_decisions/授权发布.yml",
                }
                authority = str(recovered.get("authority_interpretation", ""))
                valid = (
                    sender == "chatgpt-web-planner-01"
                    and recipient == "claude-code-cli-executor-01"
                    and "request" in purpose.lower()
                    and "执行超出默认角色的受保护发布" in purpose
                    and ("授权发布" in authority or "authoriz" in authority.lower())
                    and paths == expected
                )
            elif fixture_id == "F4-long-content-reference":
                valid = (
                    sender == "claude-code-desktop-reviewer-01"
                    and recipient == "chatgpt-web-planner-01"
                    and "response" in purpose.lower()
                    and "审核意见" in purpose
                    and paths == {"08_os/_runs/run-x/03_结果建模/审核意见_v1.md"}
                )
            else:
                raise CommunicationValidationError(f"cross_model_fixture_unknown:{fixture_id}")
            if not valid:
                raise CommunicationValidationError(f"cross_model_exact_recovery_mismatch:{fixture_id}")


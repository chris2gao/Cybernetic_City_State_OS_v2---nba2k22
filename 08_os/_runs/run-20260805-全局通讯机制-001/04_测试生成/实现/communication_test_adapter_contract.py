import typing
from typing import Any, Dict, List, Optional

class MissingCapabilityError(Exception):
    pass

class CommunicationTestAdapter:
    """
    Abstract contract for the Stage 04 communication system tests.
    A conforming Stage 06 production adapter will implement these.
    """
    def __init__(self, mode: str):
        self.mode = mode

    def validate_message(self, message: Dict[str, Any]) -> None:
        raise MissingCapabilityError("validate_message")

    def validate_document(self, content: str) -> None:
        raise MissingCapabilityError("validate_document")

    def validate_sender_index(self, index_data: Dict[str, Any]) -> None:
        raise MissingCapabilityError("validate_sender_index")

    def publish_message(self, message: Dict[str, Any]) -> None:
        raise MissingCapabilityError("publish_message")

    def bootstrap_receiver(self, endpoint_id: str) -> None:
        raise MissingCapabilityError("bootstrap_receiver")

    def evaluate_authority(self, role: str, action: str, refs: List[str]) -> bool:
        raise MissingCapabilityError("evaluate_authority")

    def publish_to_GitHub(self, message: Dict[str, Any]) -> None:
        raise MissingCapabilityError("publish_to_GitHub")

    def converge_task_branch(self, local_path: str, remote_url: str, branch: str) -> bool:
        raise MissingCapabilityError("converge_task_branch")

    def update_Human_current(self, trigger_event: Dict[str, Any]) -> None:
        raise MissingCapabilityError("update_Human_current")

    def archive_task(self, task_id: str) -> None:
        raise MissingCapabilityError("archive_task")

    def inspect_forbidden_automation(self, message: Dict[str, Any]) -> None:
        raise MissingCapabilityError("inspect_forbidden_automation")

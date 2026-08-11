from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import yaml

try:
    from .receiver_bootstrap import load_receiver_context
    from .validate_communication_system import CommunicationValidationError, CommunicationValidator
except ImportError:
    from receiver_bootstrap import load_receiver_context
    from validate_communication_system import CommunicationValidationError, CommunicationValidator


class DocumentAndBootstrapTests(unittest.TestCase):
    def test_document_front_matter(self):
        content = """---
document_id: doc-001
task_id: task-001
author_endpoint_id: sender-01
author_task_role: execution
purpose: evidence
privacy_class: repository_shareable
---
Body.
"""
        CommunicationValidator().validate_document(content)
        with self.assertRaisesRegex(CommunicationValidationError, "front_matter_missing"):
            CommunicationValidator().validate_document("Body only")

    def test_bootstrap_reads_only_declared_direct_set(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            for directory in ("endpoints", "roles", "messages/sender-01", "documents/sender-01"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "manifest.yml").write_text("task_id: task-001\n", encoding="utf-8")
            card = {
                "endpoint_id": "receiver-01", "principal_class": "model",
                "model_or_product": "neutral", "environment_class": "local",
                "interface_class": "terminal", "task_role": "review",
                "local_file_read": True, "local_file_write": False,
                "GitHub_read": True, "GitHub_write": False,
                "instance_label": "receiver", "role_context_entry_ref": "roles/review.md",
            }
            (root / "endpoints/receiver-01.yml").write_text(yaml.safe_dump(card), encoding="utf-8")
            (root / "roles/review.md").write_text("Review role", encoding="utf-8")
            (root / "documents/sender-01/doc.md").write_text("Evidence", encoding="utf-8")
            message = {
                "message_id": "task-001::sender-01::00001", "task_id": "task-001",
                "title": "Result", "message_type": "result",
                "sender_endpoint_id": "sender-01", "sender_task_role": "execution",
                "expected_recipient_endpoint_id": "receiver-01",
                "expected_recipient_task_role": "review", "content": "See evidence",
                "required_refs": ["documents/sender-01/doc.md"],
            }
            path = root / "messages/sender-01/00001_result.yml"
            path.write_text(yaml.safe_dump(message, sort_keys=False), encoding="utf-8")
            result = load_receiver_context(root, "receiver-01", "messages/sender-01/00001_result.yml")
            self.assertEqual(result["read_paths"], [
                "manifest.yml", "endpoints/receiver-01.yml", "roles/review.md",
                "messages/sender-01/00001_result.yml", "documents/sender-01/doc.md",
            ])

    def test_missing_or_outside_ref_fails_closed(self):
        validator = CommunicationValidator()
        message = {
            "message_id": "task-001::sender-01::00001", "task_id": "task-001",
            "title": "Result", "message_type": "result",
            "sender_endpoint_id": "sender-01", "sender_task_role": "execution",
            "expected_recipient_endpoint_id": "receiver-01",
            "expected_recipient_task_role": "review", "content": "See evidence",
            "required_refs": ["../outside.md"],
        }
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(CommunicationValidationError, "outside_task_root"):
                validator.validate_message(message, task_root=Path(temp))

    def test_endpoint_card_is_bound_to_selected_receiver(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            for directory in ("endpoints", "roles", "messages/sender-01"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "manifest.yml").write_text("task_id: task-001\n", encoding="utf-8")
            card = {
                "endpoint_id": "other-receiver", "principal_class": "model",
                "model_or_product": "neutral", "environment_class": "local",
                "interface_class": "terminal", "task_role": "review",
                "local_file_read": True, "local_file_write": False,
                "GitHub_read": True, "GitHub_write": False,
                "instance_label": "receiver", "role_context_entry_ref": "roles/review.md",
            }
            (root / "endpoints/receiver-01.yml").write_text(yaml.safe_dump(card), encoding="utf-8")
            (root / "roles/review.md").write_text("Review role", encoding="utf-8")
            message = {
                "message_id": "task-001::sender-01::00001", "task_id": "task-001",
                "title": "Result", "message_type": "result",
                "sender_endpoint_id": "sender-01", "sender_task_role": "execution",
                "expected_recipient_endpoint_id": "receiver-01",
                "expected_recipient_task_role": "review", "content": "Done",
                "required_refs": [],
            }
            path = root / "messages/sender-01/00001_result.yml"
            path.write_text(yaml.safe_dump(message, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError, "bootstrap_recipient_endpoint_mismatch"):
                load_receiver_context(root, "receiver-01", "messages/sender-01/00001_result.yml")


if __name__ == "__main__":
    unittest.main()

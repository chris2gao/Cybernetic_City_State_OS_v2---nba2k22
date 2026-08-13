from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

import yaml

try:
    from .publish_message import publish
except ImportError:
    from publish_message import publish

VALIDATOR = Path(__file__).resolve().parents[1] / "validator"
if str(VALIDATOR) not in sys.path:
    sys.path.insert(0, str(VALIDATOR))
from validate_communication_system import CommunicationValidationError  # noqa: E402


def message():
    return {
        "message_id": "task-001::sender-01::00001", "task_id": "task-001",
        "title": "Result ready", "message_type": "result",
        "sender_endpoint_id": "sender-01", "sender_task_role": "execution",
        "expected_recipient_endpoint_id": "receiver-01",
        "expected_recipient_task_role": "review", "content": "Review result.",
        "required_refs": [],
    }


def card(endpoint_id, role, environment="local"):
    return {
        "endpoint_id": endpoint_id, "principal_class": "model",
        "model_or_product": "test", "environment_class": environment,
        "interface_class": "terminal", "task_role": role,
        "local_file_read": True, "local_file_write": True,
        "GitHub_read": True, "GitHub_write": False,
        "instance_label": endpoint_id, "role_context_entry_ref": f"roles/{role}.md",
    }


def receiver_setup(carrier="local"):
    return {
        "collaboration_role": "independent_review",
        "provider": "OpenAI",
        "product": "Codex Desktop",
        "surface": "codex_desktop",
        "model": "GPT-5.6 Sol",
        "reasoning_or_parameter_profile": "codex_sol_strongest_exposed",
        "session_mode": "fresh",
        "isolation_level": "fresh_session",
        "repository_access_mode": "local_worktree" if carrier == "local" else "GitHub",
        "repository_or_worktree_requirement": "task-root",
        "required_branch_or_sha": "task-001",
        "local_files_required": False,
        "github_publication_required_before_start": carrier == "GitHub",
        "communication_carrier": carrier,
        "routing_basis_ref": "routing.yml",
        "availability_assumption_or_observation_ref": "routing.yml#availability",
        "limitations": ["executor_private_context"],
    }


def formal_kwargs(root: Path, *, carrier="local"):
    return {
        "activation_context": {
            "intended_cross_endpoint_side_effect": True,
            "actionable_content": True,
            "communication_context_ref": "manifest.yml",
            "classification_basis_ref": "source.yml",
        },
        "mechanism_preconditions": {
            "communication_system": {
                "verification_result": "VERIFIED",
                "evidence_ref": "manifest.yml",
            },
        },
        "receiver_setup": receiver_setup(carrier),
    }


class PublisherTests(unittest.TestCase):
    def _fixture(self, root: Path) -> Path:
        (root / "indexes").mkdir()
        (root / "endpoints").mkdir()
        (root / "roles").mkdir()
        (root / "endpoints/sender-01.yml").write_text(
            yaml.safe_dump(card("sender-01", "execution")), encoding="utf-8"
        )
        (root / "endpoints/receiver-01.yml").write_text(
            yaml.safe_dump(card("receiver-01", "review")), encoding="utf-8"
        )
        (root / "roles/execution.md").write_text("execution\n", encoding="utf-8")
        (root / "roles/review.md").write_text("review\n", encoding="utf-8")
        (root / "manifest.yml").write_text(
            "task_id: task-001\ncommunication_contract_version: 2\n", encoding="utf-8"
        )
        (root / "routing.yml").write_text("availability: registered_default\n", encoding="utf-8")
        source = root / "source.yml"
        source.write_text(yaml.safe_dump(message(), sort_keys=False), encoding="utf-8")
        return source

    def test_local_default_publishes_message_then_index_and_pointer(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self._fixture(root)
            pointer = publish(root, source, **formal_kwargs(root))
            self.assertTrue((root / pointer["exact_path_or_GitHub_ref"]).is_file())
            self.assertTrue((root / "indexes/sender-01.yml").is_file())
            self.assertEqual(pointer["carrier"], "local")

    def test_existing_message_is_immutable(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self._fixture(root)
            publish(root, source, **formal_kwargs(root))
            with self.assertRaises(CommunicationValidationError):
                publish(root, source, **formal_kwargs(root))

    def test_GitHub_requires_trigger_and_shareable_privacy(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self._fixture(root)
            with self.assertRaisesRegex(CommunicationValidationError, "explicit_trigger"):
                publish(root, source, carrier="GitHub", **formal_kwargs(root, carrier="GitHub"))
            with self.assertRaisesRegex(CommunicationValidationError, "repository_shareable"):
                publish(root, source, carrier="GitHub", github_trigger="web_recipient",
                        privacy_class="local_only", **formal_kwargs(root, carrier="GitHub"))

    def test_web_receiver_requires_GitHub_carrier(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self._fixture(root)
            (root / "endpoints/receiver-01.yml").write_text(
                yaml.safe_dump(card("receiver-01", "review", "web_cloud_model")),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(CommunicationValidationError, "web_republication_required"):
                publish(root, source, **formal_kwargs(root))
            with self.assertRaisesRegex(
                CommunicationValidationError, "requires_convergence_wrapper"
            ):
                publish(
                    root, source, carrier="GitHub", github_trigger="web_recipient",
                    **formal_kwargs(root, carrier="GitHub")
                )

    def test_forbidden_is_never_materialized(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self._fixture(root)
            with self.assertRaisesRegex(CommunicationValidationError, "cannot_be_materialized"):
                publish(root, source, privacy_class="forbidden", **formal_kwargs(root))
            self.assertFalse((root / "messages").exists())

    def test_nested_forbidden_marker_in_formal_bundle_is_rejected(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self._fixture(root)
            kwargs = formal_kwargs(root)
            kwargs["activation_context"]["metadata"] = {"access_token": "dummy"}
            with self.assertRaisesRegex(CommunicationValidationError, "forbidden_data_marker"):
                publish(root, source, **kwargs)
            self.assertFalse((root / "messages").exists())

    def test_invalid_required_document_leaves_no_message_or_index(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self._fixture(root)
            document = root / "documents/sender-01/invalid.md"
            document.parent.mkdir(parents=True)
            document.write_text("body only", encoding="utf-8")
            value = message()
            value["required_refs"] = ["documents/sender-01/invalid.md"]
            source.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError, "front_matter"):
                publish(root, source, **formal_kwargs(root))
            self.assertFalse((root / "messages").exists())
            self.assertFalse((root / "indexes/sender-01.yml").exists())


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

import yaml

try:
    from .validate_communication_system import (
        CommunicationValidationError,
        CommunicationValidator,
        parse_safe_yaml,
    )
except ImportError:
    from validate_communication_system import (
        CommunicationValidationError,
        CommunicationValidator,
        parse_safe_yaml,
    )


def card(endpoint_id="sender-01", task_role="backend_execution_and_handoff"):
    return {
        "endpoint_id": endpoint_id,
        "principal_class": "model",
        "model_or_product": "vendor-independent",
        "environment_class": "local",
        "interface_class": "terminal",
        "task_role": task_role,
        "local_file_read": True,
        "local_file_write": True,
        "GitHub_read": True,
        "GitHub_write": False,
        "instance_label": "test",
        "role_context_entry_ref": "role.yml",
    }


class EndpointAndRoleTests(unittest.TestCase):
    def setUp(self):
        self.validator = CommunicationValidator()

    def test_missing_endpoint_field_is_rejected(self):
        value = card()
        value.pop("task_role")
        with self.assertRaisesRegex(CommunicationValidationError, "endpoint_card_missing"):
            self.validator.validate_endpoint_card(value)

    def test_role_mismatch_is_rejected(self):
        cards = {"sender-01": card(), "receiver-01": card("receiver-01", "review")}
        message = {
            "sender_endpoint_id": "sender-01",
            "expected_recipient_endpoint_id": "receiver-01",
            "sender_task_role": "wrong",
            "expected_recipient_task_role": "review",
            "required_refs": [],
        }
        with self.assertRaisesRegex(CommunicationValidationError, "sender_role_mismatch"):
            self.validator.validate_role_binding(message, cards)

    def test_role_context_ref_must_be_canonical_task_relative_path(self):
        value = card()
        value["role_context_entry_ref"] = "roles/../outside.yml"
        with self.assertRaisesRegex(CommunicationValidationError, "noncanonical"):
            self.validator.validate_endpoint_card(value)


def valid_message():
    return {
        "message_id": "task-001::sender-01::00001",
        "task_id": "task-001",
        "title": "Request",
        "message_type": "request",
        "sender_endpoint_id": "sender-01",
        "sender_task_role": "backend_execution_and_handoff",
        "expected_recipient_endpoint_id": "receiver-01",
        "expected_recipient_task_role": "review",
        "content": "Please review the referenced artifact.",
        "required_refs": [],
        "requested_action": "Review and respond through Human relay.",
    }


class SafeYamlAndMessageTests(unittest.TestCase):
    def setUp(self):
        self.validator = CommunicationValidator()

    def test_valid_message_passes(self):
        self.validator.validate_message(valid_message())

    def test_duplicate_key_is_rejected(self):
        with self.assertRaisesRegex(CommunicationValidationError, "duplicate_yaml_key"):
            parse_safe_yaml("a: 1\na: 2\n")

    def test_multiple_documents_are_rejected(self):
        with self.assertRaisesRegex(CommunicationValidationError, "exactly_one_document"):
            parse_safe_yaml("a: 1\n---\nb: 2\n")

    def test_alias_and_merge_are_rejected(self):
        with self.assertRaisesRegex(CommunicationValidationError, "anchor_or_alias"):
            parse_safe_yaml("a: &x {b: 1}\nc: *x\n")
        with self.assertRaisesRegex(CommunicationValidationError, "merge_key"):
            parse_safe_yaml("a: {b: 1}\nc:\n  <<: {b: 2}\n")

    def test_custom_tag_is_rejected(self):
        with self.assertRaisesRegex(CommunicationValidationError, "custom_tag"):
            parse_safe_yaml("a: !custom value\n")

    def test_missing_action_and_prohibited_state_are_rejected(self):
        message = valid_message()
        message.pop("requested_action")
        with self.assertRaisesRegex(CommunicationValidationError, "requested_action_required"):
            self.validator.validate_message(message)
        message = valid_message()
        message["delivered"] = True
        with self.assertRaisesRegex(CommunicationValidationError, "prohibited_message_field"):
            self.validator.validate_message(message)

    def test_message_identity_is_exact(self):
        message = valid_message()
        message["message_id"] = "task-001::other::00001"
        with self.assertRaisesRegex(CommunicationValidationError, "message_id_identity_mismatch"):
            self.validator.validate_message(message)

    def test_required_refs_are_canonical_even_without_local_task_root(self):
        message = valid_message()
        message["required_refs"] = ["documents/../outside.md"]
        with self.assertRaisesRegex(CommunicationValidationError, "required_ref_noncanonical"):
            self.validator.validate_message(message)

    def test_exact_git_blob_reader_enables_windows_longpaths(self):
        completed = subprocess.CompletedProcess([], 0, stdout=b"value", stderr=b"")
        with patch("subprocess.run", return_value=completed) as invoked:
            value = self.validator._git_blob(Path("."), "a" * 40, "deep/path.yml")
        self.assertEqual(value, "value")
        self.assertEqual(
            invoked.call_args.args[0][:4],
            ["git", "-c", "core.longpaths=true", "show"],
        )

    def test_exact_git_blob_reader_never_lets_subprocess_decode(self):
        # text=True would make subprocess decode with the host locale encoding.
        completed = subprocess.CompletedProcess([], 0, stdout=b"value", stderr=b"")
        with patch("subprocess.run", return_value=completed) as invoked:
            self.validator._git_blob(Path("."), "a" * 40, "deep/path.yml")
        kwargs = invoked.call_args.kwargs
        self.assertNotIn("encoding", kwargs)
        self.assertFalse(kwargs.get("text", False))
        self.assertFalse(kwargs.get("universal_newlines", False))

    def test_exact_git_blob_reader_decodes_non_ascii_utf8(self):
        payload = "任务: 中文 UTF-8 载荷\nvalue: 城邦\n"
        completed = subprocess.CompletedProcess(
            [], 0, stdout=payload.encode("utf-8"), stderr=b""
        )
        with patch("subprocess.run", return_value=completed):
            value = self.validator._git_blob(Path("."), "a" * 40, "任务/契约.yml")
        self.assertEqual(value, payload)
        self.assertEqual(parse_safe_yaml(value)["value"], "城邦")

    def test_exact_git_blob_reader_rejects_invalid_utf8(self):
        # 0x80 is the byte that made GBK decoding fail inside subprocess.
        completed = subprocess.CompletedProcess([], 0, stdout=b"a: \x80\xff", stderr=b"")
        with patch("subprocess.run", return_value=completed):
            with self.assertRaisesRegex(
                CommunicationValidationError, "Human_pointer_GitHub_blob_not_utf8"
            ):
                self.validator._git_blob(Path("."), "a" * 40, "deep/path.yml")

    def test_exact_git_blob_reader_reports_missing_blob_before_decoding(self):
        completed = subprocess.CompletedProcess([], 128, stdout=b"", stderr=b"fatal")
        with patch("subprocess.run", return_value=completed):
            with self.assertRaisesRegex(
                CommunicationValidationError, "Human_pointer_GitHub_blob_missing"
            ):
                self.validator._git_blob(Path("."), "a" * 40, "deep/path.yml")

    def test_exact_git_blob_reader_reads_real_non_ascii_repository_blob(self):
        # Real git, real UTF-8 blob with a non-ASCII path. This is the case that
        # returned None under text=True on a CP936 host.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for args in (
                ["git", "init", "-q"],
                ["git", "config", "user.email", "t@example.invalid"],
                ["git", "config", "user.name", "t"],
            ):
                subprocess.run(args, cwd=root, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            relative = "任务/中文契约.yml"
            blob = "task_id: 城邦-001\nnote: 非 ASCII UTF-8\n"
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(blob, encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "commit", "-qm", "utf8"], cwd=root, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                  stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
            value = self.validator._git_blob(root, head, relative)
        self.assertEqual(value, blob)
        self.assertEqual(parse_safe_yaml(value)["task_id"], "城邦-001")

    def test_self_authorization_is_rejected(self):
        cards = {"sender-01": card(), "receiver-01": card("receiver-01", "review")}
        message = {
            "sender_endpoint_id": "sender-01",
            "expected_recipient_endpoint_id": "receiver-01",
            "sender_task_role": "backend_execution_and_handoff",
            "expected_recipient_task_role": "review",
            "required_refs": [],
            "self_authorization": True,
        }
        with self.assertRaisesRegex(CommunicationValidationError, "self_authorization_prohibited"):
            self.validator.validate_role_binding(message, cards)

    def test_authorization_ref_must_be_direct_ref(self):
        cards = {"sender-01": card(), "receiver-01": card("receiver-01", "review")}
        message = {
            "sender_endpoint_id": "sender-01",
            "expected_recipient_endpoint_id": "receiver-01",
            "sender_task_role": "backend_execution_and_handoff",
            "expected_recipient_task_role": "review",
            "required_refs": [],
            "authorization_ref": "Human/decisions/authorization.yml",
        }
        with self.assertRaisesRegex(CommunicationValidationError, "authorization_ref_not_in_required_refs"):
            self.validator.validate_role_binding(message, cards)

    def test_protected_action_uses_bound_physical_authorization(self):
        message = valid_message()
        message["authorization_ref"] = "Human_decisions/authorization.yml"
        message["required_refs"] = [message["authorization_ref"]]
        current = {
            "task_id": "task-001",
            "writer_endpoint_id": "sender-01",
            "writer_task_role": "backend_execution_and_handoff",
            "requested_action": message["requested_action"],
        }
        authorization = {
            "task_id": "task-001",
            "writer_endpoint_id": "sender-01",
            "authorized_action": message["requested_action"],
            "granted": True,
        }
        with TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / message["authorization_ref"]
            target.parent.mkdir(parents=True)
            target.write_text(yaml.safe_dump(authorization), encoding="utf-8")
            self.validator.validate_protected_action_authority(
                message, task_root=root, current_task_authority=current,
                Human_authorization=authorization,
            )
            authorization["granted"] = False
            target.write_text(yaml.safe_dump(authorization), encoding="utf-8")
            with self.assertRaisesRegex(
                CommunicationValidationError, "Human_authorization_physical_state_mismatch"
            ):
                self.validator.validate_protected_action_authority(
                    message, task_root=root, current_task_authority=current,
                    Human_authorization={**authorization, "granted": True},
                )


if __name__ == "__main__":
    unittest.main()

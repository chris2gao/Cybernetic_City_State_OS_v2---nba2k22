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

    def test_ordinary_message_needs_no_authority_or_delegation(self):
        message = valid_message()
        self.assertNotIn("authorization_ref", message)
        self.assertNotIn("confirmation_ref", message)
        self.assertNotIn("recipient_delegation_ref", message)
        self.validator.validate_message(message)

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


    def test_protected_action_simple_Human_confirmation_passes_without_task_authority(self):
        message = valid_message()
        message["requested_action"] = "publish-to-master"
        message["confirmation_ref"] = "Human/confirm-master.yml"
        message["required_refs"] = [message["confirmation_ref"]]
        confirmation = {
            "schema_version": "citystate.communication.human_confirmation.v1",
            "task_id": "task-001",
            "confirmation_id": "HC-001",
            "confirmed_by": "Human",
            "disposition": "confirmed",
            "confirmed_actions": ["publish-to-master"],
            "revoked": False,
        }
        with TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / message["confirmation_ref"]
            target.parent.mkdir(parents=True)
            target.write_text(yaml.safe_dump(confirmation), encoding="utf-8")
            self.validator.validate_protected_action_authority(
                message,
                task_root=root,
                Human_authorization=confirmation,
            )

    def test_protected_action_confirmation_must_cover_exact_action(self):
        message = valid_message()
        message["requested_action"] = "publish-to-master"
        message["confirmation_ref"] = "Human/confirm-other.yml"
        message["required_refs"] = [message["confirmation_ref"]]
        confirmation = {
            "schema_version": "citystate.communication.human_confirmation.v1",
            "task_id": "task-001",
            "confirmation_id": "HC-002",
            "confirmed_by": "Human",
            "disposition": "confirmed",
            "confirmed_actions": ["delete-merged-task-branch"],
            "revoked": False,
        }
        with TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / message["confirmation_ref"]
            target.parent.mkdir(parents=True)
            target.write_text(yaml.safe_dump(confirmation), encoding="utf-8")
            with self.assertRaisesRegex(
                CommunicationValidationError, "Human_confirmation_action_not_confirmed"
            ):
                self.validator.validate_protected_action_authority(
                    message, task_root=root, Human_authorization=confirmation,
                )

    def test_protected_action_without_confirmation_requests_confirmation_not_task_authority(self):
        message = valid_message()
        message["requested_action"] = "publish-to-master"
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(
                CommunicationValidationError, "protected_action_human_confirmation_required"
            ):
                self.validator.validate_protected_action_authority(
                    message, task_root=Path(temp)
                )


    def _write_v2_authority(self, root: Path, *, writer="sender-01", role="backend_execution_and_handoff", delegated=False, revoked=False):
        human_ref = "Human/task_authority.yml"
        human = {
            "schema_version": "citystate.Human_task_authority_event.v2",
            "task_id": "task-001", "task_authority_id": "TA-001",
            "initial_authority_holder_endpoint_id": "dispatcher-01",
            "initial_authority_holder_task_role": "decision_architecture",
            "task_authority_scope": ["task", "review"],
            "Human_disposition": "authorized", "task_authority_revoked": False,
            "task_nonce_commitment": {"scheme": "citystate-human-task-authority-v2", "algorithm": "sha256", "digest": "a" * 64},
        }
        hp = root / human_ref; hp.parent.mkdir(parents=True, exist_ok=True)
        hp.write_text(yaml.safe_dump(human), encoding="utf-8")
        auth_ref = "delegations/d1.yml" if delegated else "Human/direct.yml"
        auth = {
            "schema_version": "citystate.communication.task_authority_delegation.v2" if delegated else "citystate.communication.direct_human_authorization.v2",
            "task_id": "task-001", "task_authority_id": "TA-001", "authorized_actions": ["do-work"],
            "Human_task_authority_ref": human_ref, "granted": True, "revoked": revoked,
        }
        if delegated:
            auth.update({"delegation_id": "DEL-1", "delegator_endpoint_id": "dispatcher-01", "delegator_task_role": "decision_architecture", "recipient_endpoint_id": writer, "recipient_task_role": role, "delegated_scope": ["task"], "allow_redelegation": False})
        else:
            auth.update({"writer_endpoint_id": writer, "writer_task_role": role})
        ap = root / auth_ref; ap.parent.mkdir(parents=True, exist_ok=True)
        ap.write_text(yaml.safe_dump(auth), encoding="utf-8")
        return human_ref, auth_ref, auth

    def test_v2_direct_Human_authorization_passes(self):
        message = valid_message(); message["requested_action"] = "do-work"
        current = {"task_id":"task-001","writer_endpoint_id":"sender-01","writer_task_role":"backend_execution_and_handoff","requested_action":"do-work"}
        with TemporaryDirectory() as temp:
            root=Path(temp); human_ref, auth_ref, auth=self._write_v2_authority(root)
            message["authorization_ref"]=auth_ref; message["required_refs"]=[auth_ref,human_ref]
            self.validator.validate_protected_action_authority(message, task_root=root, current_task_authority=current, Human_authorization=auth)
            auth["revoked"]=True; (root/auth_ref).write_text(yaml.safe_dump(auth),encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError,"authorization_v2_not_live"):
                self.validator.validate_protected_action_authority(message, task_root=root, current_task_authority=current, Human_authorization=auth)

    def test_v2_delegated_writer_passes_and_revocation_fails(self):
        message = valid_message(); message["requested_action"] = "do-work"
        current = {"task_id":"task-001","writer_endpoint_id":"sender-01","writer_task_role":"backend_execution_and_handoff","requested_action":"do-work"}
        with TemporaryDirectory() as temp:
            root=Path(temp); human_ref, auth_ref, auth=self._write_v2_authority(root, delegated=True)
            message["authorization_ref"]=auth_ref; message["required_refs"]=[auth_ref,human_ref]
            self.validator.validate_protected_action_authority(message, task_root=root, current_task_authority=current, Human_authorization=auth)
            auth["revoked"]=True; (root/auth_ref).write_text(yaml.safe_dump(auth),encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError,"authorization_v2_not_live"):
                self.validator.validate_protected_action_authority(message, task_root=root, current_task_authority=current, Human_authorization=auth)

    def test_v2_recipient_delegation_is_bound_to_recipient_and_action(self):
        message=valid_message(); message["requested_action"]="do-work"
        with TemporaryDirectory() as temp:
            root=Path(temp); human_ref, auth_ref, _=self._write_v2_authority(root, writer="receiver-01", role="review", delegated=True)
            message["expected_recipient_endpoint_id"]="receiver-01"; message["expected_recipient_task_role"]="review"
            message["recipient_delegation_ref"]=auth_ref; message["required_refs"]=[auth_ref,human_ref]
            self.validator.validate_recipient_delegation(message, task_root=root)
            bad=yaml.safe_load((root/auth_ref).read_text(encoding="utf-8")); bad["recipient_endpoint_id"]="other"; (root/auth_ref).write_text(yaml.safe_dump(bad),encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError,"authorization_v2_recipient_mismatch"):
                self.validator.validate_recipient_delegation(message, task_root=root)


    def test_v2_forged_root_delegator_is_rejected(self):
        message = valid_message(); message["requested_action"] = "do-work"
        current = {"task_id":"task-001","writer_endpoint_id":"sender-01","writer_task_role":"backend_execution_and_handoff","requested_action":"do-work"}
        with TemporaryDirectory() as temp:
            root=Path(temp); human_ref, auth_ref, auth=self._write_v2_authority(root, delegated=True)
            auth["delegator_endpoint_id"]="forged-dispatcher"
            (root/auth_ref).write_text(yaml.safe_dump(auth),encoding="utf-8")
            message["authorization_ref"]=auth_ref; message["required_refs"]=[auth_ref,human_ref]
            with self.assertRaisesRegex(CommunicationValidationError,"root_delegator_not_Human_bound_holder"):
                self.validator.validate_protected_action_authority(message, task_root=root, current_task_authority=current, Human_authorization=auth)

    def test_v2_redelegation_requires_live_parent_and_narrows_authority(self):
        message = valid_message(); message["requested_action"] = "do-work"
        current = {"task_id":"task-001","writer_endpoint_id":"sender-01","writer_task_role":"backend_execution_and_handoff","requested_action":"do-work"}
        with TemporaryDirectory() as temp:
            root=Path(temp); human_ref, _, _=self._write_v2_authority(root)
            parent_ref="delegations/parent.yml"; child_ref="delegations/child.yml"
            parent={"schema_version":"citystate.communication.task_authority_delegation.v2","task_id":"task-001","task_authority_id":"TA-001","delegation_id":"DEL-P","delegator_endpoint_id":"dispatcher-01","delegator_task_role":"decision_architecture","recipient_endpoint_id":"mid-01","recipient_task_role":"delegator","authorized_actions":["do-work","review-work"],"delegated_scope":["task"],"allow_redelegation":True,"Human_task_authority_ref":human_ref,"granted":True,"revoked":False}
            child={"schema_version":"citystate.communication.task_authority_delegation.v2","task_id":"task-001","task_authority_id":"TA-001","delegation_id":"DEL-C","delegator_endpoint_id":"mid-01","delegator_task_role":"delegator","recipient_endpoint_id":"sender-01","recipient_task_role":"backend_execution_and_handoff","authorized_actions":["do-work"],"delegated_scope":["task"],"allow_redelegation":False,"parent_delegation_ref":parent_ref,"Human_task_authority_ref":human_ref,"granted":True,"revoked":False}
            for ref,doc in ((parent_ref,parent),(child_ref,child)):
                p=root/ref; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(yaml.safe_dump(doc),encoding="utf-8")
            refs=[child_ref,parent_ref,human_ref]; message["authorization_ref"]=child_ref; message["required_refs"]=refs
            self.validator.validate_protected_action_authority(message, task_root=root, current_task_authority=current, Human_authorization=child)
            parent["allow_redelegation"]=False; (root/parent_ref).write_text(yaml.safe_dump(parent),encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError,"redelegation_not_granted"):
                self.validator.validate_protected_action_authority(message, task_root=root, current_task_authority=current, Human_authorization=child)
            parent["allow_redelegation"]=True; parent["authorized_actions"]=["review-work"]; (root/parent_ref).write_text(yaml.safe_dump(parent),encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError,"redelegation_action_expansion"):
                self.validator.validate_protected_action_authority(message, task_root=root, current_task_authority=current, Human_authorization=child)

    def test_v21_loader_based_delegated_start_passes_without_Human_code(self):
        message = valid_message(); message["requested_action"] = "do-work"
        with TemporaryDirectory() as temp:
            root = Path(temp)
            human_ref, auth_ref, _ = self._write_v2_authority(
                root, writer="receiver-01", role="review", delegated=True
            )
            message["expected_recipient_endpoint_id"] = "receiver-01"
            message["expected_recipient_task_role"] = "review"
            message["recipient_delegation_ref"] = auth_ref
            message["required_refs"] = [auth_ref, human_ref]
            def loader(ref):
                path = root / ref
                if not path.is_file():
                    raise CommunicationValidationError("authorization_ref_unreadable")
                return yaml.safe_load(path.read_text(encoding="utf-8"))
            self.validator.validate_recipient_delegation_with_loader(
                message, authority_loader=loader
            )
            delegation = loader(auth_ref); delegation["revoked"] = True
            (root / auth_ref).write_text(yaml.safe_dump(delegation), encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError, "authorization_v2_not_live"):
                self.validator.validate_recipient_delegation_with_loader(
                    message, authority_loader=loader
                )

    def test_v21_loader_based_delegated_start_rejects_forgery_and_widening(self):
        message = valid_message(); message["requested_action"] = "do-work"
        with TemporaryDirectory() as temp:
            root = Path(temp)
            human_ref, auth_ref, baseline = self._write_v2_authority(
                root, writer="receiver-01", role="review", delegated=True
            )
            message["expected_recipient_endpoint_id"] = "receiver-01"
            message["expected_recipient_task_role"] = "review"
            message["recipient_delegation_ref"] = auth_ref
            message["required_refs"] = [auth_ref, human_ref]
            def loader(ref):
                path = root / ref
                if not path.is_file():
                    raise CommunicationValidationError("authorization_ref_unreadable")
                return yaml.safe_load(path.read_text(encoding="utf-8"))
            cases = [
                ("wrong_task", {"task_id":"other-task"}, "authorization_v2_not_live"),
                ("wrong_authority", {"task_authority_id":"TA-OTHER"}, "delegation_task_authority_mismatch"),
                ("wrong_recipient", {"recipient_endpoint_id":"other"}, "authorization_v2_recipient_mismatch"),
                ("wrong_action", {"authorized_actions":["other"]}, "authorization_v2_action_not_delegated"),
                ("scope_widening", {"delegated_scope":["outside"]}, "delegation_exceeds_Human_task_scope"),
                ("forged_root", {"delegator_endpoint_id":"forged"}, "root_delegator_not_Human_bound_holder"),
            ]
            for name, delta, error in cases:
                with self.subTest(name=name):
                    doc = dict(baseline); doc.update(delta)
                    (root / auth_ref).write_text(yaml.safe_dump(doc), encoding="utf-8")
                    with self.assertRaisesRegex(CommunicationValidationError, error):
                        self.validator.validate_recipient_delegation_with_loader(
                            message, authority_loader=loader
                        )


if __name__ == "__main__":
    unittest.main()

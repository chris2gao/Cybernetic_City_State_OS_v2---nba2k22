from pathlib import Path
from tempfile import TemporaryDirectory
import copy
import sys
import unittest

import yaml

HERE = Path(__file__).resolve()
PUBLISHER = HERE.parents[1] / "publisher"
if str(PUBLISHER) not in sys.path:
    sys.path.insert(0, str(PUBLISHER))
from publish_message import publish  # noqa: E402

try:
    from .receiver_bootstrap import load_receiver_context, load_receiver_from_pointer
    from .validate_communication_system import CommunicationValidationError
except ImportError:
    from receiver_bootstrap import load_receiver_context, load_receiver_from_pointer
    from validate_communication_system import CommunicationValidationError


def card(endpoint_id, role):
    return {
        "endpoint_id": endpoint_id,
        "principal_class": "model",
        "model_or_product": "test",
        "environment_class": "local",
        "interface_class": "terminal",
        "task_role": role,
        "local_file_read": True,
        "local_file_write": True,
        "GitHub_read": True,
        "GitHub_write": False,
        "instance_label": endpoint_id,
        "role_context_entry_ref": f"roles/{role}.md",
    }


def setup():
    return {
        "collaboration_role": "independent_review",
        "provider": "OpenAI",
        "product": "Codex Desktop",
        "surface": "codex_desktop",
        "model": "GPT-5.6 Sol",
        "reasoning_or_parameter_profile": "codex_sol_strongest_exposed",
        "session_mode": "fresh",
        "isolation_level": "fresh_session",
        "repository_access_mode": "local_worktree",
        "repository_or_worktree_requirement": "task-root",
        "required_branch_or_sha": "task-001",
        "local_files_required": False,
        "github_publication_required_before_start": False,
        "communication_carrier": "local",
        "routing_basis_ref": "routing.yml",
        "availability_assumption_or_observation_ref": "routing.yml#availability",
        "limitations": ["executor_private_context"],
    }


class FormalCommunicationActivationTests(unittest.TestCase):
    def fixture(self, root: Path, *, content="Perform the requested review.") -> Path:
        for directory in ("indexes", "endpoints", "roles"):
            (root / directory).mkdir(parents=True, exist_ok=True)
        (root / "manifest.yml").write_text(
            "task_id: task-001\ncommunication_contract_version: 2\n", encoding="utf-8"
        )
        (root / "routing.yml").write_text("availability: registered_default\n", encoding="utf-8")
        for endpoint_id, role in (("sender-01", "execution"), ("receiver-01", "review")):
            (root / f"endpoints/{endpoint_id}.yml").write_text(
                yaml.safe_dump(card(endpoint_id, role), sort_keys=False), encoding="utf-8"
            )
            (root / f"roles/{role}.md").write_text(role, encoding="utf-8")
        message = {
            "message_id": "task-001::sender-01::00001",
            "task_id": "task-001",
            "title": "Formal review request",
            "message_type": "request",
            "sender_endpoint_id": "sender-01",
            "sender_task_role": "execution",
            "expected_recipient_endpoint_id": "receiver-01",
            "expected_recipient_task_role": "review",
            "content": content,
            "required_refs": [],
            "requested_action": "review exact candidate",
        }
        source = root / "source.yml"
        source.write_text(yaml.safe_dump(message, sort_keys=False), encoding="utf-8")
        return source

    @staticmethod
    def activation_kwargs():
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
            "receiver_setup": setup(),
        }

    def test_positive_end_to_end_requires_v2_pointer_constitution_and_receipt(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            pointer = publish(root, source, **self.activation_kwargs())
            self.assertEqual(pointer["pointer_contract_version"], 2)
            result = load_receiver_from_pointer(root, "receiver-01", pointer)
            self.assertEqual(result["message"]["message_id"], pointer["message_id"])
            self.assertEqual(result["compliance_receipt"]["aggregate_result"], "VERIFIED")
            self.assertIn(pointer["constitution_evidence_ref"], result["read_paths"])
            self.assertIn("source.yml", result["read_paths"])
            self.assertIn("routing.yml#availability", result["activation_evidence_refs"])
            self.assertEqual(
                result["receiver_publication_claim"]["verification_result"], "VERIFIED"
            )


    def test_v21_receiver_bootstrap_revalidates_recipient_delegation_without_code(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            human_ref = "Human/task_authority.yml"
            delegation_ref = "delegations/receiver.yml"
            (root / "Human").mkdir(parents=True, exist_ok=True)
            (root / "delegations").mkdir(parents=True, exist_ok=True)
            human = {
                "schema_version": "citystate.Human_task_authority_event.v2",
                "task_id": "task-001", "task_authority_id": "TA-001",
                "initial_authority_holder_endpoint_id": "sender-01",
                "initial_authority_holder_task_role": "execution",
                "task_authority_scope": ["review"], "Human_disposition": "authorized",
                "task_authority_revoked": False,
                "task_nonce_commitment": {"scheme":"citystate-human-task-authority-v2","algorithm":"sha256","digest":"a"*64},
            }
            delegation = {
                "schema_version": "citystate.communication.task_authority_delegation.v2",
                "task_id": "task-001", "task_authority_id": "TA-001", "granted": True, "revoked": False,
                "Human_task_authority_ref": human_ref,
                "delegator_endpoint_id": "sender-01", "delegator_task_role": "execution",
                "recipient_endpoint_id": "receiver-01", "recipient_task_role": "review",
                "authorized_actions": ["review exact candidate"], "delegated_scope": ["review"],
                "parent_delegation_ref": None, "allow_redelegation": False,
            }
            (root / human_ref).write_text(yaml.safe_dump(human), encoding="utf-8")
            (root / delegation_ref).write_text(yaml.safe_dump(delegation), encoding="utf-8")
            message = yaml.safe_load(source.read_text(encoding="utf-8"))
            message["recipient_delegation_ref"] = delegation_ref
            message["required_refs"] = [delegation_ref, human_ref]
            source.write_text(yaml.safe_dump(message, sort_keys=False), encoding="utf-8")
            pointer = publish(root, source, **self.activation_kwargs())
            result = load_receiver_from_pointer(root, "receiver-01", pointer)
            self.assertEqual(result["message"]["recipient_delegation_ref"], delegation_ref)
            delegation["revoked"] = True
            (root / delegation_ref).write_text(yaml.safe_dump(delegation), encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError, "authorization_v2_not_live"):
                load_receiver_from_pointer(root, "receiver-01", pointer)


    def test_direct_publisher_without_resolver_gate_bundle_creates_nothing(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            with self.assertRaisesRegex(ValueError, "FORMAL_ACTIVATION_REQUIRED"):
                publish(root, source, receiver_setup=setup())
            self.assertFalse((root / "messages").exists())
            self.assertFalse((root / "constitutions").exists())

    def test_missing_or_stale_communication_context_blocks_formal_handoff(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            kwargs = self.activation_kwargs()
            kwargs["activation_context"]["communication_context_ref"] = None
            with self.assertRaisesRegex(ValueError, "PRE_ACTION_GATE_BLOCKED"):
                publish(root, source, **kwargs)
            kwargs = self.activation_kwargs()
            kwargs["mechanism_preconditions"]["communication_system"].update({
                "freshness_required": True,
                "freshness_result": "STALE",
            })
            with self.assertRaisesRegex(ValueError, "PRE_ACTION_GATE_BLOCKED"):
                publish(root, source, **kwargs)

    def test_long_human_copy_paste_body_cannot_substitute_for_document(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root, content="x" * 4001)
            with self.assertRaisesRegex(ValueError, "long_content_requires_document"):
                publish(root, source, **self.activation_kwargs())

    def test_message_or_exact_looking_pointer_without_evidence_is_not_formal(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            pointer = publish(root, source, **self.activation_kwargs())
            with self.assertRaisesRegex(CommunicationValidationError, "explicit_mode_required"):
                load_receiver_context(root, "receiver-01", pointer["exact_path_or_GitHub_ref"])
            no_evidence = dict(pointer)
            no_evidence["constitution_evidence_ref"] = "constitutions/sender-01/missing.yml"
            with self.assertRaisesRegex(CommunicationValidationError, "evidence_missing"):
                load_receiver_from_pointer(root, "receiver-01", no_evidence)

    def test_nonverified_material_subclaim_blocks_receiver_even_if_receipt_claims_verified(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            pointer = publish(root, source, **self.activation_kwargs())
            receipt_path = root / pointer["compliance_receipt_ref"]
            receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
            receipt["material_claims"][0]["observed_value"]["message_id"] = "other"
            receipt_path.write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError, "activation_evidence_invalid"):
                load_receiver_from_pointer(root, "receiver-01", pointer)

    def test_self_consistent_receipt_cannot_redefine_constitution_or_observation(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            pointer = publish(root, source, **self.activation_kwargs())
            receipt_path = root / pointer["compliance_receipt_ref"]
            receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
            claim = receipt["material_claims"][0]
            claim["expected_value_or_predicate"]["sender_endpoint_id"] = "attacker"
            claim["observed_value"]["sender_endpoint_id"] = "attacker"
            receipt_path.write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError, "expected_binding_mismatch"):
                load_receiver_from_pointer(root, "receiver-01", pointer)

    def test_receiver_replays_resolver_instead_of_trusting_embedded_result(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            pointer = publish(root, source, **self.activation_kwargs())
            constitution_path = root / pointer["constitution_evidence_ref"]
            constitution = yaml.safe_load(constitution_path.read_text(encoding="utf-8"))
            constitution["resolution"]["action_allowed_to_enter_enforcement"] = False
            constitution_path.write_text(
                yaml.safe_dump(constitution, sort_keys=False), encoding="utf-8"
            )
            with self.assertRaisesRegex(CommunicationValidationError, "resolution_replay_mismatch"):
                load_receiver_from_pointer(root, "receiver-01", pointer)

    def test_pointer_requires_exact_sender_owned_evidence_paths_and_index_binding(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            pointer = publish(root, source, **self.activation_kwargs())
            rebound = dict(pointer)
            rebound["constitution_evidence_ref"] = pointer["compliance_receipt_ref"]
            with self.assertRaisesRegex(CommunicationValidationError, "constitution_path_binding"):
                load_receiver_from_pointer(root, "receiver-01", rebound)
            misleading = dict(pointer)
            misleading["one_line_routing_purpose"] = "Different Human-facing route"
            with self.assertRaisesRegex(CommunicationValidationError, "routing_purpose_mismatch"):
                load_receiver_from_pointer(root, "receiver-01", misleading)
            index_path = root / "indexes/sender-01.yml"
            index_path.write_text("[]\n", encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError, "sender_index_binding"):
                load_receiver_from_pointer(root, "receiver-01", pointer)

    def test_pointer_rejects_forged_execution_ref_and_duplicate_material_claim_id(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            pointer = publish(root, source, **self.activation_kwargs())
            constitution_path = root / pointer["constitution_evidence_ref"]
            constitution = yaml.safe_load(constitution_path.read_text(encoding="utf-8"))
            constitution["mechanism_execution_ref"] = "publisher-looking-but-not-canonical.py"
            constitution_path.write_text(
                yaml.safe_dump(constitution, sort_keys=False), encoding="utf-8"
            )
            with self.assertRaisesRegex(CommunicationValidationError, "execution_ref_invalid"):
                load_receiver_from_pointer(root, "receiver-01", pointer)

        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            pointer = publish(root, source, **self.activation_kwargs())
            receipt_path = root / pointer["compliance_receipt_ref"]
            receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
            receipt["material_claims"].append(copy.deepcopy(receipt["material_claims"][0]))
            receipt_path.write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(CommunicationValidationError, "activation_evidence_invalid"):
                load_receiver_from_pointer(root, "receiver-01", pointer)

    def test_legacy_nine_field_pointer_is_explicit_historical_only(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            pointer = publish(root, source, **self.activation_kwargs())
            legacy = {key: value for key, value in pointer.items() if key in {
                "task_id", "message_id", "carrier", "exact_path_or_GitHub_ref",
                "sender_endpoint_id", "sender_task_role", "expected_recipient_endpoint_id",
                "expected_recipient_task_role", "one_line_routing_purpose",
            }}
            with self.assertRaisesRegex(CommunicationValidationError, "legacy_v1_pointer"):
                load_receiver_from_pointer(root, "receiver-01", legacy)


if __name__ == "__main__":
    unittest.main()

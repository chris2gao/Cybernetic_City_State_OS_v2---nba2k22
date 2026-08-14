from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import yaml

from activation import (
    ActivationError,
    classify_planned_action,
    evaluate_pre_action_gate,
    normalize_recipient,
    resolve_required_mechanisms,
    validate_constitution_evidence,
)


REPO = Path(__file__).resolve().parents[4]
TRIGGERS = yaml.safe_load(
    (REPO / "01_os/03_mechanisms/mechanism_activation/机制触发注册表_v1.yml")
    .read_text(encoding="utf-8")
)


def formal_context(**overrides):
    value = {
        "action_id": "task-001::sender-01::00001",
        "formal_message_type": "request",
        "intended_cross_endpoint_side_effect": True,
        "actionable_content": True,
        "intended_recipient_endpoint_id": "receiver-01",
        "task_id": "task-001",
        "sender_endpoint_id": "sender-01",
        "communication_context_ref": "manifest.yml",
        "classification_basis_ref": "action_context.yml",
        "caller_self_label": "discussion_only",
    }
    value.update(overrides)
    return value


class FormalActionConstitutionTests(unittest.TestCase):
    def test_euphemistic_relay_is_formal_without_dispatch_keyword(self):
        result = classify_planned_action(formal_context(caller_self_label="casual_note"))
        self.assertTrue(result["formal"])
        self.assertEqual(result["action_class"], "formal_cross_endpoint_task_dispatch")

    def test_discussion_label_cannot_downgrade_actionable_recipient_instruction(self):
        result = classify_planned_action(formal_context(caller_self_label="ordinary_discussion"))
        self.assertTrue(result["formal"])

    def test_quoted_or_template_analysis_remains_ordinary(self):
        for kind in ("quoted_prior_message", "template_example"):
            result = classify_planned_action({
                "content_kind": kind,
                "intended_recipient_is_Human_only": True,
                "intended_cross_endpoint_side_effect": False,
                "actionable_content": False,
                "formal_state_claim": False,
            })
            self.assertFalse(result["formal"])

    def test_actionable_request_to_current_human_is_ordinary_discussion(self):
        result = classify_planned_action({
            "intended_recipient_is_Human_only": True,
            "intended_cross_endpoint_side_effect": False,
            "actionable_content": True,
            "formal_state_claim": False,
        })
        self.assertFalse(result["formal"])

    def test_mixed_action_segments_formal_part(self):
        context = formal_context(semantic_segments=[
            {
                "intended_recipient_is_Human_only": True,
                "intended_cross_endpoint_side_effect": False,
                "actionable_content": False,
                "formal_state_claim": False,
            },
            {
                "formal_message_type": "request",
                "Human_relay_requested": True,
                "actionable_content": True,
            },
        ])
        result = classify_planned_action(context)
        self.assertEqual(result["formal_segment_indexes"], [1])
        self.assertTrue(result["mixed_action_segmented"])

    def test_alias_and_role_are_exact_not_lexical_guesses(self):
        self.assertEqual(
            normalize_recipient(
                {"recipient_alias": "reviewer"},
                aliases={"reviewer": "receiver-01"},
                endpoint_cards={"receiver-01": {"task_role": "review"}},
            ),
            "receiver-01",
        )
        with self.assertRaisesRegex(ActivationError, "RECIPIENT_ALIAS_UNRESOLVED"):
            normalize_recipient({"recipient_alias": "sounds-like-reviewer"}, aliases={})
        with self.assertRaisesRegex(ActivationError, "RECIPIENT_ROLE_AMBIGUOUS"):
            normalize_recipient(
                {"intended_recipient_task_role": "review"},
                endpoint_cards={"a": {"task_role": "review"}, "b": {"task_role": "review"}},
            )

    def test_missing_context_is_resolved_then_gate_blocks(self):
        resolution = resolve_required_mechanisms(
            formal_context(communication_context_ref=None), TRIGGERS
        )
        self.assertIn("communication_system:communication_context_ref", resolution["missing_preconditions"])
        gate = evaluate_pre_action_gate(resolution, {})
        self.assertEqual(gate["gate_result"], "BLOCKED")

    def test_receiver_selection_makes_model_routing_mandatory(self):
        resolution = resolve_required_mechanisms(
            formal_context(
                requires_receiver_selection=True,
                collaboration_role="execution",
                risk_tier="T2_semantic",
                task_shape="implementation",
                required_capabilities=["local_repository"],
                routing_basis_ref="routing.yml",
                availability_assumption_or_observation_ref="availability.yml",
            ),
            TRIGGERS,
        )
        self.assertEqual(resolution["required_mechanisms"], ["communication_system", "model_routing"])
        self.assertEqual(resolution["route_requirements"], ["receiver_setup"])

    def test_unknown_registry_predicate_fails_closed(self):
        triggers = yaml.safe_load(yaml.safe_dump(TRIGGERS))
        triggers["mechanisms"]["communication_system"]["activation_predicates"] = [
            "caller_defined_untrusted_predicate"
        ]
        with self.assertRaisesRegex(ActivationError, "TRIGGER_PREDICATE_UNKNOWN"):
            resolve_required_mechanisms(formal_context(), triggers)

    def test_gate_requires_physical_precondition_refs_and_freshness(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "manifest.yml").write_text("task_id: task-001\n", encoding="utf-8")
            resolution = resolve_required_mechanisms(formal_context(), TRIGGERS)
            gate = evaluate_pre_action_gate(
                resolution,
                {"communication_system": {
                    "verification_result": "VERIFIED",
                    "evidence_ref": "manifest.yml",
                    "freshness_required": True,
                    "freshness_result": "VERIFIED",
                }},
                refs_root=root,
            )
            self.assertEqual(gate["gate_result"], "VERIFIED")
            self.assertEqual(gate["authority_effect"], "none")

    def test_constitution_rejects_resolver_or_gate_omission(self):
        resolution = resolve_required_mechanisms(formal_context(), TRIGGERS)
        gate = evaluate_pre_action_gate(
            resolution,
            {"communication_system": {"verification_result": "VERIFIED", "evidence_ref": "manifest.yml"}},
        )
        evidence = {
            "action_id": formal_context()["action_id"],
            "action_class": resolution["action_class"],
            "sender_endpoint_id": "sender-01",
            "intended_recipient_endpoint_id": "receiver-01",
            "classification_basis_ref": "action_context.yml",
            "required_mechanisms": resolution["required_mechanisms"],
            "resolver_result_ref": "resolver.yml",
            "gate_result_ref": "gate.yml",
            "mechanism_execution_ref": "publisher.py",
            "formal_artifact_ref": "messages/sender-01/00001_request.yml",
            "activation_context": formal_context(),
            "mechanism_preconditions": {
                "communication_system": {
                    "verification_result": "VERIFIED",
                    "evidence_ref": "manifest.yml",
                },
            },
            "authority_effect": "none",
        }
        validate_constitution_evidence(evidence, resolution=resolution, gate=gate)
        no_resolver = dict(evidence)
        no_resolver.pop("resolver_result_ref")
        with self.assertRaisesRegex(ActivationError, "FIELDS_MISSING"):
            validate_constitution_evidence(no_resolver, resolution=resolution, gate=gate)
        blocked_gate = dict(gate, gate_result="BLOCKED")
        with self.assertRaisesRegex(ActivationError, "GATE_NOT_VERIFIED"):
            validate_constitution_evidence(evidence, resolution=resolution, gate=blocked_gate)


if __name__ == "__main__":
    unittest.main()

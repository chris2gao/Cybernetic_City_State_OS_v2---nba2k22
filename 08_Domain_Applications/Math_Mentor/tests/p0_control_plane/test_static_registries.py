from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any, Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]
MATH_MENTOR = Path(__file__).resolve().parents[2]


def load_yaml(name: str) -> dict[str, Any]:
    value = yaml.safe_load((MATH_MENTOR / name).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} must contain a YAML mapping")
    return value


def by_id(records: Iterable[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record[key]
        if record_id in indexed:
            raise AssertionError(f"duplicate {key}: {record_id}")
        indexed[record_id] = record
    return indexed


class StaticRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authority = load_yaml("MATH_MENTOR_AUTHORITY_REGISTRY.yml")
        cls.capability = load_yaml("MATH_MENTOR_CAPABILITY_MATURITY.yml")
        cls.deprecation = load_yaml("MATH_MENTOR_DEPRECATION_MAP.yml")
        cls.identity_text = (MATH_MENTOR / "CANONICAL_NODE_IDENTITY_SCHEMA.md").read_text(
            encoding="utf-8-sig"
        )
        cls.builder_text = (MATH_MENTOR / "p0_control_plane/registry_builder.py").read_text(
            encoding="utf-8-sig"
        )
        cls.protocol_text = (REPO_ROOT / ".ai/PROTOCOL.md").read_text(
            encoding="utf-8-sig"
        )

        cls.authority_sources = by_id(cls.authority["authority_sources"], "authority_id")
        cls.action_rules = by_id(cls.authority["action_rules"], "action_id")
        cls.capabilities = by_id(cls.capability["capabilities"], "capability_id")
        cls.deprecations = by_id(cls.deprecation["entries"], "deprecation_id")

    def assert_repo_reference_exists(self, reference: str) -> None:
        self.assertIsInstance(reference, str)
        self.assertNotEqual("", reference)
        if any(token in reference for token in "*?["):
            matches = list(REPO_ROOT.glob(reference))
            self.assertTrue(matches, f"repository glob has no match: {reference}")
        else:
            self.assertTrue((REPO_ROOT / reference).exists(), f"missing repository ref: {reference}")

    def test_registries_are_derived_and_do_not_activate_runtime(self) -> None:
        self.assertEqual("derived_non_authorizing_index", self.authority["registry_role"])
        self.assertEqual(
            "derived_evidence_index_not_activation", self.capability["registry_role"]
        )
        self.assertEqual(
            "derived_routing_guard_not_deletion_authority",
            self.deprecation["registry_role"],
        )
        self.assertFalse(self.authority["operational_activation"])
        self.assertFalse(self.capability["operational_activation"])
        self.assertFalse(self.deprecation["operational_activation"])

    def test_registry_ids_are_unique_and_authority_uses_unordered_tiers(self) -> None:
        self.assertEqual(
            len(self.authority["authority_sources"]), len(self.authority_sources)
        )
        self.assertEqual(len(self.authority["action_rules"]), len(self.action_rules))
        self.assertEqual(len(self.capability["capabilities"]), len(self.capabilities))
        self.assertEqual(len(self.deprecation["entries"]), len(self.deprecations))

        self.assertEqual(
            "unordered; source list order is inventory order only",
            self.authority["canonical_authority_order"]["same_tier_ordering"],
        )
        for source in self.authority["authority_sources"]:
            self.assertNotIn("authority_rank", source)
            self.assertIn("authority_tier", source)
            self.assertIn("authority_group", source)
        source_tiers = [
            source["authority_tier"] for source in self.authority["authority_sources"]
        ]
        self.assertEqual(sorted(source_tiers), source_tiers)

    def test_authority_tiers_match_canonical_protocol_order_exactly(self) -> None:
        self.assertEqual(
            {
                "path": ".ai/PROTOCOL.md",
                "section": "Canonical Instruction Authority And State Freshness",
            },
            self.authority["canonical_authority_order"]["canonical_ref"],
        )
        expected_tiers = [
            (
                1,
                "platform_system_developer_safety",
                "platform, system, developer, and safety instructions",
            ),
            (2, "current_explicit_human_instruction", "current explicit Human instruction"),
            (
                3,
                "authenticated_human_approved_task_override",
                "authenticated current Human-approved task-specific permission or override",
            ),
            (
                4,
                "plan3_and_cybernetic_citizen_contracts",
                "Plan 3 constitution and the Cybernetic Citizen runtime contract",
            ),
            (
                5,
                "durable_repository_control_protocols",
                "durable repository control protocols",
            ),
            (
                6,
                "relevant_domain_authority_protocols",
                "relevant domain-authority protocols",
            ),
            (
                7,
                "ordinary_signal_and_task_details",
                "ordinary current signal and task operational details",
            ),
            (
                8,
                "routing_and_historical_evidence",
                "routing documents and historical evidence",
            ),
        ]
        actual_tiers = [
            (
                item["authority_tier"],
                item["authority_group"],
                item["canonical_label"],
            )
            for item in self.authority["canonical_authority_order"]["tiers"]
        ]
        self.assertEqual(expected_tiers, actual_tiers)
        self.assertTrue(
            self.authority["canonical_authority_order"][
                "lower_number_has_higher_authority"
            ]
        )

        protocol_positions = []
        for tier, _, label in expected_tiers:
            token = f"{tier}. {label}"
            self.assertEqual(1, self.protocol_text.count(token), token)
            protocol_positions.append(self.protocol_text.index(token))
        self.assertEqual(sorted(protocol_positions), protocol_positions)

        group_by_tier = {tier: group for tier, group, _ in expected_tiers}
        for source in self.authority["authority_sources"]:
            self.assertEqual(
                group_by_tier[source["authority_tier"]],
                source["authority_group"],
                source["authority_id"],
            )

        expected_source_ids_by_tier = {
            1: {"platform_system_developer_safety"},
            2: {"current_explicit_human_instruction"},
            3: {"authenticated_human_approved_task_override"},
            4: {"plan3_human_speaker", "cybernetic_citizen_contract"},
            5: {
                "repository_working_agreements",
                "ai_handoff_protocol",
                "ai_protocol_adherence",
                "codex_task_input_contract",
                "long_run_program_protocol",
            },
            6: {
                "math_mentor_universal_protocol",
                "knowledge_completion_program",
                "node_quality_audit_contract",
                "bridge_schema_contract",
                "teacher_initialization_contract",
                "teaching_flow_contract",
                "coordinator_manual_contract",
                "student_state_contract",
                "spaced_review_contract",
                "graduation_contract",
                "capability_semantics_contract",
                "tool_truthfulness_contract",
            },
            7: {"ordinary_current_signal_task_details"},
            8: {
                "city_state_bootstrap",
                "teaching_system_blueprint",
                "teaching_system_implementation_plan",
                "post_p2_historical_memory",
                "stage0_inventory_evidence",
            },
        }
        actual_source_ids_by_tier = {
            tier: {
                source["authority_id"]
                for source in self.authority["authority_sources"]
                if source["authority_tier"] == tier
            }
            for tier in range(1, 9)
        }
        self.assertEqual(expected_source_ids_by_tier, actual_source_ids_by_tier)

    def test_authenticated_override_is_not_an_ordinary_model_packet(self) -> None:
        override = self.authority_sources[
            "authenticated_human_approved_task_override"
        ]
        ordinary = self.authority_sources["ordinary_current_signal_task_details"]

        self.assertEqual(3, override["authority_tier"])
        self.assertTrue(override["can_grant"])
        self.assertIn("authenticated_approval_channel", override["verification"])
        self.assertIn("never inferred", override["scope"])

        self.assertEqual(7, ordinary["authority_tier"])
        self.assertFalse(ordinary["can_grant"])
        self.assertIn("not_human_authentication", ordinary["verification"])
        self.assertIn("never grant an override", ordinary["scope"])

    def test_all_repository_references_exist(self) -> None:
        self.assert_repo_reference_exists(
            self.authority["canonical_authority_order"]["canonical_ref"]["path"]
        )
        for source in self.authority["authority_sources"]:
            reference = source.get("ref")
            if reference is None:
                self.assertEqual("external", source["source_kind"])
                self.assertIn(source["authority_tier"], {1, 2, 3, 7})
                expected_state = (
                    "task_scoped"
                    if source["authority_tier"] == 7
                    else "external_current"
                )
                self.assertEqual(expected_state, source["state"])
            else:
                self.assert_repo_reference_exists(reference)

        self.assert_repo_reference_exists(self.capability["baseline"]["authority_registry_ref"])
        for capability in self.capability["capabilities"]:
            for reference in capability["evidence_refs"]:
                self.assert_repo_reference_exists(reference)

        for reference in self.deprecation["baseline"]["current_state_contracts"]:
            self.assert_repo_reference_exists(reference)
        for entry in self.deprecation["entries"]:
            for reference in entry["paths"]:
                self.assert_repo_reference_exists(reference)
            for reference in entry["source_refs"]:
                self.assert_repo_reference_exists(reference)
            for reference in entry["replacement_refs"]:
                self.assert_repo_reference_exists(reference)

    def test_rule_cross_references_resolve(self) -> None:
        source_ids = set(self.authority_sources)
        action_ids = set(self.action_rules)
        for rule in self.authority["action_rules"]:
            grant_sources = set(rule["grant_authority_any_of"])
            governing_sources = set(rule["governing_authority_sources"])
            operational_sources = set(rule["operational_detail_sources"])
            all_references = grant_sources | governing_sources | operational_sources
            self.assertTrue(governing_sources, rule["action_id"])
            self.assertTrue(
                all_references.issubset(source_ids),
                f"unknown authority source in {rule['action_id']}",
            )
            if rule["default_decision"] == "deny":
                self.assertEqual(set(), grant_sources, rule["action_id"])
            else:
                self.assertTrue(grant_sources, rule["action_id"])
            for source_id in grant_sources:
                self.assertTrue(self.authority_sources[source_id]["can_grant"], source_id)
                self.assertLessEqual(
                    self.authority_sources[source_id]["authority_tier"], 3, source_id
                )
            self.assertEqual(
                {"ordinary_current_signal_task_details"}, operational_sources
            )
            for source_id in operational_sources:
                self.assertFalse(self.authority_sources[source_id]["can_grant"])
                self.assertEqual(7, self.authority_sources[source_id]["authority_tier"])
        for capability in self.capability["capabilities"]:
            self.assertIn(capability["authority_action_id"], action_ids)

    def test_protected_actions_remain_governed_by_plan3_and_awakening(self) -> None:
        protected_actions = {
            "write_scoped_p0_control_plane_artifact",
            "mutate_teaching_node",
            "open_p3_or_generate_bridge",
            "formal_coordinator_bridge_admission",
            "activate_runtime_or_production_coordinator",
            "write_learning_state_or_review_schedule",
            "publish_source_or_merge_master",
            "access_secrets_or_credentials",
            "bypass_human_speaker",
        }
        constitutional_sources = {
            "plan3_human_speaker",
            "cybernetic_citizen_contract",
        }
        for action_id in protected_actions:
            self.assertTrue(
                constitutional_sources.issubset(
                    set(self.action_rules[action_id]["governing_authority_sources"])
                ),
                action_id,
            )

        ordinary_id = "ordinary_current_signal_task_details"
        for rule in self.authority["action_rules"]:
            self.assertNotIn(ordinary_id, rule["grant_authority_any_of"])
            self.assertNotIn(ordinary_id, rule["governing_authority_sources"])

    def test_capability_maturity_never_exceeds_evidence(self) -> None:
        tier_ranks = {
            tier_id: definition["rank"]
            for tier_id, definition in self.capability["evidence_tiers"].items()
        }
        maturity = self.capability["maturity_states"]

        for capability in self.capability["capabilities"]:
            state = capability["maturity_state"]
            tier = capability["evidence_tier"]
            minimum_tier = maturity[state]["minimum_evidence_tier"]
            self.assertGreaterEqual(
                tier_ranks[tier],
                tier_ranks[minimum_tier],
                f"{capability['capability_id']} overclaims {state} with {tier}",
            )
            self.assertLessEqual(
                maturity[state]["maturity_rank"],
                tier_ranks[tier],
                f"{capability['capability_id']} maturity rank exceeds evidence",
            )
            if tier == "T0":
                self.assertEqual([], capability["evidence_refs"])
            else:
                self.assertTrue(capability["evidence_refs"])
            if state == "operational":
                self.assertEqual("T4", tier)

        self.assertFalse(
            any(item["maturity_state"] == "operational" for item in self.capability["capabilities"]),
            "P0 must not claim an operational capability",
        )

    def test_legacy_entries_are_read_only_and_forbid_execution_and_write(self) -> None:
        safe_allowed_actions = {"read", "compare", "read_only_import", "cite_with_provenance"}
        for entry in self.deprecation["entries"]:
            forbidden = set(entry["forbidden_actions"])
            allowed = set(entry["allowed_actions"])
            self.assertIn("execute", forbidden, entry["deprecation_id"])
            self.assertIn("write", forbidden, entry["deprecation_id"])
            self.assertTrue(allowed.issubset(safe_allowed_actions), entry["deprecation_id"])
            self.assertTrue(allowed.isdisjoint(forbidden), entry["deprecation_id"])

    def test_stage0_is_stale_historical_evidence_only(self) -> None:
        stage0 = self.deprecations["stage0_inventory_bundle"]
        self.assertEqual("historical_frozen", stage0["state"])
        self.assertTrue(stage0["stale_at_current_baseline"])
        self.assertNotEqual(stage0["source_head"], self.deprecation["baseline"]["source_head"])
        self.assertTrue(
            {"execute", "write", "identity_promote", "status_promote"}.issubset(
                set(stage0["forbidden_actions"])
            )
        )

        capability = self.capabilities["stage0_corpus_inventory"]
        self.assertEqual("frozen", capability["lifecycle_state"])
        self.assertEqual("stale_historical", capability["activation_state"])
        self.assertTrue(capability["stale_at_current_baseline"])
        self.assertNotEqual(
            capability["evidence_source_head"], self.capability["baseline"]["source_head"]
        )

    def test_no_r5_or_classroom_pass_to_graduated_semantics(self) -> None:
        rule = self.action_rules["promote_classroom_pass_directly_to_graduated"]
        self.assertEqual("deny", rule["default_decision"])
        self.assertTrue(
            {"r5_to_graduated", "classroom_pass_to_graduated"}.issubset(
                set(rule["forbidden_side_effects"])
            )
        )

        capability = self.capabilities["classroom_pass_to_graduated_transition"]
        self.assertEqual("absent", capability["maturity_state"])
        self.assertEqual("T0", capability["evidence_tier"])
        self.assertEqual("prohibited", capability["activation_state"])

        for entry_id in (
            "legacy_review_master_scheduler_prompt",
            "legacy_graduated_knowledge_table",
        ):
            forbidden = set(self.deprecations[entry_id]["forbidden_actions"])
            self.assertIn("r5_to_graduated", forbidden)
            self.assertIn("status_promote", forbidden)

    def test_ui_runtime_coordinator_and_writers_are_not_implemented(self) -> None:
        blocked_capabilities = (
            "production_coordinator_runtime",
            "learning_state_writer",
            "spaced_review_scheduler_writer",
            "frontend_or_ui",
            "coordinator_bridge_consumption",
        )
        for capability_id in blocked_capabilities:
            capability = self.capabilities[capability_id]
            self.assertEqual("absent", capability["maturity_state"])
            self.assertEqual("T0", capability["evidence_tier"])
            self.assertEqual("blocked", capability["activation_state"])

    def test_identity_contract_uses_external_opaque_uuidv5_as_only_primary(self) -> None:
        required_phrases = (
            "sole primary key",
            "immutable opaque UUIDv5",
            "CANONICAL_NODE_CROSSWALK.json",
            '"canonical_uuid"',
            "typed aliases only",
            '"domain_id"',
            '"root_path"',
            '"root_filename"',
            '"roadmap_id"',
            '"legacy_alias"',
            "consumer_allowed",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, self.identity_text)
        self.assertIn(
            '"canonical-node|v1|" + NFC(repo_relative_exact_root_path)',
            self.identity_text,
        )

    def test_identity_document_matches_builder_fail_closed_state_model(self) -> None:
        binding_statuses = {
            "declared_consistent_unapproved",
            "human_approved",
            "conflict_open",
            "unclaimed",
            "quarantined",
            "canonicalize",
            "stale_resolution",
        }
        alias_statuses = {
            "observed",
            "declared_unapproved",
            "conflict",
            "observed_non_authoritative",
            "human_approved",
            "quarantined",
        }
        comparison_statuses = {
            "agree",
            "explicit_only",
            "disagree",
            "explicit_multi_claim",
            "stage0_only",
            "neither",
        }
        for status in binding_statuses | alias_statuses | comparison_statuses:
            self.assertIn(status, self.identity_text)
        for status in binding_statuses:
            self.assertIn(status, self.builder_text)
        for status in {
            "observed",
            "declared_unapproved",
            "conflict",
            "observed_non_authoritative",
        }:
            self.assertIn(status, self.builder_text)
        for status in comparison_statuses:
            self.assertIn(status, self.builder_text)

        self.assertIn('"alias_comparison": {', self.identity_text)
        self.assertIn('"alias_comparison": {', self.builder_text)
        self.assertIn("bootstrap_only: true", self.identity_text)
        self.assertIn("prior_crosswalk_preservation_implemented: false", self.identity_text)
        self.assertIn('"bootstrap_only": True', self.builder_text)
        self.assertIn('"prior_crosswalk_preservation_implemented": False', self.builder_text)


if __name__ == "__main__":
    unittest.main()

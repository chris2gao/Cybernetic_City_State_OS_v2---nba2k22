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

    def test_registry_ids_and_ranks_are_unique(self) -> None:
        self.assertEqual(
            len(self.authority["authority_sources"]), len(self.authority_sources)
        )
        self.assertEqual(len(self.authority["action_rules"]), len(self.action_rules))
        self.assertEqual(len(self.capability["capabilities"]), len(self.capabilities))
        self.assertEqual(len(self.deprecation["entries"]), len(self.deprecations))

        ranks = [record["authority_rank"] for record in self.authority["authority_sources"]]
        self.assertEqual(len(ranks), len(set(ranks)), "authority ranks must be unique")
        self.assertEqual(sorted(ranks), list(range(1, len(ranks) + 1)))

    def test_all_repository_references_exist(self) -> None:
        for source in self.authority["authority_sources"]:
            reference = source.get("ref")
            if reference is None:
                self.assertEqual("external", source["source_kind"])
                self.assertEqual("external_current", source["state"])
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
            self.assertTrue(rule["required_authority"])
            self.assertTrue(
                set(rule["required_authority"]).issubset(source_ids),
                f"unknown authority source in {rule['action_id']}",
            )
        for capability in self.capability["capabilities"]:
            self.assertIn(capability["authority_action_id"], action_ids)

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

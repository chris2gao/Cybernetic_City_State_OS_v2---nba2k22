import copy
import tempfile
import unittest
from fixtures import project, proposal
from gm_core.decisions import validate_proposal
from gm_core.history import StateStore


class DecisionProtocolTests(unittest.TestCase):
    def test_default_proposed_and_pending_storage_only(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            item = proposal(data)
            item.pop("status")
            verdict = validate_proposal(item, data)
            self.assertTrue(verdict["valid"])
            path = StateStore(directory).save_pending(item, verdict)
            self.assertTrue(path.exists())
            self.assertFalse(verdict["execution_authorized"])
            with self.assertRaises(FileExistsError):
                StateStore(directory).save_pending(item, verdict)

    def test_external_approval_claims_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            for claim in ({"approved": True}, {"metadata": {"approved": True}}, {"status": "EXECUTED_VERIFIED"}):
                item = proposal(data)
                item.update(claim)
                self.assertFalse(validate_proposal(item, data)["valid"])

    def test_wrong_source_and_unknown_fact_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            item = proposal(data)
            item["source_batch_id"] = "OTHER_BATCH"
            self.assertFalse(validate_proposal(item, data)["valid"])
            item = proposal(data)
            item["evidence"][0]["field"] = "state.total_wins"
            self.assertIn("UNKNOWN_FIELD_CLAIMED_AS_FACT", validate_proposal(item, data)["errors"])

    def test_malformed_and_traversal_references(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            self.assertFalse(validate_proposal({}, data)["valid"])
            item = proposal(data)
            item["evidence"][0]["file"] = "../../../../../config/gm_policy.json"
            self.assertIn("INVALID_EVIDENCE_REFERENCE", validate_proposal(item, data)["errors"])
            item = proposal(data)
            item["teams"] = [{}]
            self.assertFalse(validate_proposal(item, data)["valid"])

    def test_calculation_ids_must_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            item = proposal(data)
            item["calculation_refs"] = ["invented_calculation"]
            self.assertIn("UNKNOWN_CALCULATION_REFERENCE", validate_proposal(item, data)["errors"])

    def test_unknown_calculation_and_disguised_edit_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            item = proposal(data)
            item["calculation_refs"] = ["unknown_value"]
            values = {"unknown_value": {"availability": "UNKNOWN", "value": None}}
            self.assertIn("CALCULATION_INPUT_UNAVAILABLE", validate_proposal(item, data, values)["errors"])
            item = proposal(data)
            item["changes"] = [{"field": "overall_rating", "value": 99}]
            self.assertIn("CHANGES_NOT_ALLOWED_FOR_THIS_OPERATION", validate_proposal(item, data)["errors"])

    def test_configured_rules_are_not_observed_game_facts(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            item = proposal(data)
            item["evidence"][0].update(file="league.json", field="rules.salary_cap")
            self.assertIn("CONFIGURED_RULE_CLAIMED_AS_OBSERVED", validate_proposal(item, data)["errors"])

    def test_future_protocol_serialization_has_no_dispatch(self):
        import json
        from dataclasses import asdict
        from gm_core.models import ModelHandoff, Asset
        handoff = ModelHandoff("SYNTHETIC", "owner", ["T00"], "BATCH", "POLICY")
        self.assertIn("PROTOCOL_ONLY_NO_MODEL_DISPATCH", json.dumps(asdict(handoff)))
        self.assertIsNone(asdict(Asset("draft_pick", "UNKNOWN_PICK"))["observed_owner"])

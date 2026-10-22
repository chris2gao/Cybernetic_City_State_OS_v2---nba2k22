import tempfile
import unittest
from fixtures import project, proposal
from gm_core.worldline import reference_context, draft_candidates
from gm_core.decisions import validate_proposal


class WorldlineTests(unittest.TestCase):
    def test_reference_switch_and_no_game_result(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            modern = reference_context("2025-06-01", data.policy)
            historical = reference_context("2026-06-01", data.policy)
            self.assertEqual(modern["reference_mode"], "MODERN")
            self.assertEqual(historical["reference_year"], 1988)
            self.assertIsNone(historical["game_results"])
            self.assertFalse(historical["attribute_write_authority"])
            self.assertEqual(historical["mc_growth"], "DISABLED_DEFERRED")
            self.assertIsNone(reference_context("2027-06-01", data.policy)["reference_year"])

    def test_only_rookie_models_and_conflicts(self):
        rows = [{"full_name": "Synthetic Rookie", "draft_year": 1984, "draft_round": 1,
                 "draft_pick": 1, "model_category": "HISTORICAL_ROOKIE"}]
        result = draft_candidates(rows + rows + [dict(rows[0], model_category="OTHER_UNCLASSIFIED")], [])
        self.assertEqual(len(result["candidates"]), 1)
        conflict = draft_candidates(rows, ["SYNTHETIC ROOKIE"])
        self.assertFalse(conflict["candidates"])
        self.assertEqual(len(conflict["conflicts"]), 1)

    def test_attribute_changes_and_mc_are_not_enabled(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            for operation in ("PLAYER_EDIT", "MC_GROWTH"):
                item = proposal(data)
                item["operation"] = operation
                self.assertFalse(validate_proposal(item, data)["valid"])
            item = proposal(data)
            item["operation"] = "HISTORICAL_GRAVITY"
            self.assertFalse(validate_proposal(item, data)["valid"])
            item.update(reference_sources=["SYNTHETIC_HISTORY_NOT_GAME_FACT"],
                        changes=[{"field": "test_rating", "old_value": 70, "value": 71}], calculation_refs=["synthetic_delta"])
            verdict = validate_proposal(item, data, {"synthetic_delta": {"availability": "CALCULATED", "value": 1}})
            self.assertTrue(verdict["valid"])
            self.assertFalse(verdict["execution_authorized"])
            self.assertEqual(verdict["player_approval"], "NOT_GRANTED")

import tempfile
import unittest
from fixtures import project, proposal
from gm_core.trades import constraints, player_valuation
from gm_core.decisions import validate_proposal
from gm_core.tactics import check_field
from trade_engine import DynamicTradeEngine


class TradeConstraintTests(unittest.TestCase):
    def test_legacy_generator_cannot_initialize_or_fill_values(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                DynamicTradeEngine(directory + "/must_not_exist.sqlite")
            engine = object.__new__(DynamicTradeEngine)
            with self.assertRaises(ValueError):
                engine.calculate_player_base_value({})

    def test_no_real_valuation_without_observed_attributes(self):
        self.assertIsNone(player_valuation({"salary_current_year": 100})["value"])
        self.assertIn("overall_rating", player_valuation({})["reason"])

    def test_pick_ownership_unknown_never_legal(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            result = constraints(data, [{"kind": "draft_pick", "asset_id": "SYNTHETIC_PICK"}])
            self.assertEqual(result["legality"], "UNKNOWN")
            self.assertIn("DRAFT_PICK_OWNERSHIP_UNKNOWN", result["missing_data"])
            self.assertFalse(result["executable"])

    def test_protected_player_and_duplicate_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            asset = {"kind": "player", "asset_id": "SYNTHETIC_PLAYER", "player_name": "Tyrese Haliburton"}
            result = constraints(data, [asset, asset])
            self.assertIn("PROTECTED_PLAYER", result["errors"])
            self.assertIn("DUPLICATE_ASSET", result["errors"])

    def test_no_legal_certificate_for_motivated_trade(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory, complete=True)
            item = proposal(data)
            item.update(operation="TRADE_PROPOSAL", teams=["T00", "T01"], legality="LEGAL",
                        assets=[{"kind": "player", "asset_id": "SYNTHETIC_PLAYER"}], calculation_refs=["T00.observed_roster_salary_sum"])
            verdict = validate_proposal(item, data, {"T00.observed_roster_salary_sum": {"availability": "CALCULATED", "value": 15000000}})
            self.assertFalse(verdict["valid"])
            self.assertIn("V1_CANNOT_CERTIFY_TRADE_LEGALITY", verdict["errors"])

    def test_legacy_team_tactics_are_revoked_regardless_of_old_enum(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            self.assertFalse(check_field(data.gm_policy, "poe_pnr_def", 99)["valid"])
            self.assertFalse(check_field(data.gm_policy, "poe_pnr_def", 6)["valid"])
            self.assertTrue(check_field(data.gm_policy, "POEOffense2", 7)["valid"])
            self.assertFalse(check_field(data.gm_policy, "POEOffense2", 6)["valid"])
            self.assertFalse(check_field(data.gm_policy, "poe_on_ball", 12)["valid"])
            item = proposal(data)
            item.update(operation="TACTIC_CHANGE", changes=[{"field": "poe_on_ball", "value": 12}])
            self.assertIn("LEGACY_TACTICAL_CHANGE_CONTRACT_REVOKED", validate_proposal(item, data)["errors"])

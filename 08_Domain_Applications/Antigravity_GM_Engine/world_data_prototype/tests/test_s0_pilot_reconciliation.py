"""Tests for VAE G2 Pilot 01 S0 Baseline, Score Discrepancy Scope, and REA Preflight Contract.

Part of NBA2K22-VAE-G2-S0-BASELINE-LOOP-OBSERVABILITY-20261101-001.
"""
import json
import sqlite3
import unittest
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[4] / "01_os" / "07_content" / "_runs" / "run-20261101-nba2k22-vae-g2-s0-baseline-loop-observability-pilot-001"
EXEC_DIR = RUN_DIR / "06_执行"
DB_PATH = Path(__file__).resolve().parents[4] / "01_os" / "07_content" / "_runs" / "run-20261024-nba2k22-world-data-implementation-002" / "_runtime" / "world-saves" / "nba2k22_test_01" / "world-v24.sqlite"


class S0PilotReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope_path = EXEC_DIR / "score_discrepancy_scope.json"
        cls.baseline_path = EXEC_DIR / "s0_selected_pilot_baseline_and_sources.json"
        cls.preflight_path = EXEC_DIR / "one_pilot_g2_rea_preflight.json"

        with open(cls.scope_path, "r", encoding="utf-8") as f:
            cls.scope_data = json.load(f)
        with open(cls.baseline_path, "r", encoding="utf-8") as f:
            cls.baseline_data = json.load(f)
        with open(cls.preflight_path, "r", encoding="utf-8") as f:
            cls.preflight_data = json.load(f)

    def test_score_discrepancy_scope_structure_and_counts(self):
        """V04: Verify all 238 games are accounted for, with 222 exact and 16 categorized."""
        self.assertEqual(self.scope_data["total_audited_games"], 238)
        self.assertEqual(self.scope_data["exact_conserved_count"], 222)
        self.assertEqual(self.scope_data["total_discrepancy_count"], 16)

        # Breakdowns
        mag = self.scope_data["breakdown_by_delta_magnitude"]
        self.assertEqual(mag["within_tolerance_lte_3"], 4)
        self.assertEqual(mag["within_tolerance_lte_4"], 6)
        self.assertEqual(mag["outside_tolerance_gt_4"], 10)

        cat = self.scope_data["breakdown_by_category"]
        self.assertEqual(cat["OVERTIME_REGULATION_PERIOD_TRUNCATION"], 5)
        self.assertEqual(cat["TEAM_ROSTER_STATLINE_TRUNCATION"], 11)
        self.assertEqual(cat["CAUSE_UNKNOWN"], 0)

        # Exactly 16 cases listed
        self.assertEqual(len(self.scope_data["discrepancy_cases"]), 16)

    def test_score_discrepancy_against_sqlite(self):
        """Validate discrepancy cases against the underlying SQLite database."""
        if not DB_PATH.exists():
            self.skipTest("SQLite DB not found at runtime path")

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        # Verify all 16 discrepancy game IDs match actual DB differences
        discrepancy_ids = {case["native_game_id"] for case in self.scope_data["discrepancy_cases"]}
        self.assertEqual(len(discrepancy_ids), 16)

        for case in self.scope_data["discrepancy_cases"]:
            gid = case["game_id"]
            uid = case["unit_id"]

            hp = sum(x[0] for x in conn.execute(
                "SELECT period_points FROM game_period_scores WHERE game_id=? AND unit_id=? AND team_id=?",
                (gid, uid, case["home_team_id"])
            ).fetchall())
            ap = sum(x[0] for x in conn.execute(
                "SELECT period_points FROM game_period_scores WHERE game_id=? AND unit_id=? AND team_id=?",
                (gid, uid, case["away_team_id"])
            ).fetchall())
            hpb = sum(x[0] for x in conn.execute(
                "SELECT points FROM player_game_boxes WHERE game_id=? AND unit_id=? AND team_id=?",
                (gid, uid, case["home_team_id"])
            ).fetchall())
            apb = sum(x[0] for x in conn.execute(
                "SELECT points FROM player_game_boxes WHERE game_id=? AND unit_id=? AND team_id=?",
                (gid, uid, case["away_team_id"])
            ).fetchall())

            home_diff = hp - hpb
            away_diff = ap - apb
            max_delta = max(abs(home_diff), abs(away_diff))

            self.assertEqual(max_delta, case["max_team_delta"], f"Mismatch for game {gid}")
            self.assertTrue(max_delta > 0, f"Expected discrepancy for game {gid}")

        conn.close()

    def test_s0_pilot_selection_and_sample_adequacy(self):
        """V02 & V06: Verify single Pilot 1 selection and >= 10 game sample adequacy."""
        self.assertEqual(self.baseline_data["pilot_id"], "PILOT_01_SHOT_TOUCHES")
        justification = self.baseline_data["selection_justification"]
        self.assertEqual(justification["target_player_id"], "player:native:2459")
        self.assertEqual(justification["target_team_id"], "team:native:28")

        adequacy = self.baseline_data["s0_baseline_sample_adequacy"]
        self.assertTrue(adequacy["is_adequacy_met"])
        self.assertGreaterEqual(adequacy["target_games_count"], 10)
        self.assertEqual(adequacy["target_games_count"], 16)
        self.assertTrue(adequacy["all_games_score_conserved"])
        self.assertEqual(adequacy["readiness_verdict"], "S0_BASELINE_READY")

    def test_s0_pilot_game_isolation_and_metric_distributions(self):
        """V03 & V05: Confirm zero overlap with discrepancy games and valid distributions."""
        games = self.baseline_data["s0_consecutive_games"]
        self.assertEqual(len(games), 16)

        discrepancy_ids = {case["native_game_id"] for case in self.scope_data["discrepancy_cases"]}
        for g in games:
            self.assertTrue(g["score_conserved_exact"])
            self.assertNotIn(g["native_game_id"], discrepancy_ids)
            self.assertGreaterEqual(g["minutes_played"], 30)
            self.assertGreater(g["points"], 0)
            self.assertGreater(g["fg_attempted"], 0)

        # Check metric distributions
        dist = self.baseline_data["s0_metric_distributions"]
        self.assertAlmostEqual(dist["fg_attempted"]["mean"], 19.875, places=2)
        self.assertAlmostEqual(dist["points"]["mean"], 29.562, places=2)
        self.assertAlmostEqual(dist["minutes"]["mean"], 36.375, places=2)
        self.assertAlmostEqual(dist["true_shooting_pct"]["mean"], 0.663, places=2)

    def test_rea_g2_preflight_contract(self):
        """V06, V08, V09: Verify strict read-only boundary, exact offset 0x458, and falsification criteria."""
        pre = self.preflight_data
        setting = pre["native_setting_definition"]
        self.assertEqual(setting["setting_field_id"], "TENDENCY_NATIVE_001")
        self.assertEqual(setting["byte_offset"], "0x458")
        self.assertEqual(setting["data_type"], "uint8")
        self.assertEqual(setting["baseline_s0_value"], 95)

        # Boundary checks
        boundary = pre["rea_readback_protocol"]["setter_contract_boundary"]
        self.assertEqual(boundary["authorization_status"], "NOT_AUTHORIZED_IN_EXECUTION_RUN")
        self.assertEqual(boundary["game_mutation_policy"], "STRICT_READ_ONLY")

        # Proposed intervention
        intv = pre["proposed_s1_intervention"]
        self.assertEqual(intv["proposed_s1_value"], 80)
        self.assertEqual(intv["delta"], -15)
        self.assertEqual(intv["execution_status"], "PENDING_HUMAN_GAMEPLAY")

        # Falsification criteria
        hypo = pre["hypothesis_and_falsification"]
        self.assertIn("FALSIFICATION_1", hypo["falsification_criteria"][0])
        self.assertIn("no_causal_overreach_clause", hypo)


if __name__ == "__main__":
    unittest.main()

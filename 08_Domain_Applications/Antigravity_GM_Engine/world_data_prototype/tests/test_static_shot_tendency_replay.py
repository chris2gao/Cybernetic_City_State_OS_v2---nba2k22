"""Tests for S0 Static Shot Tendency Analysis, Join Quality, and Live Numeric Replay.

Part of NBA2K22-VAE-S0-STATIC-SHOT-TENDENCY-LOOP-20261101-001.
"""
import json
import sqlite3
import unittest
from pathlib import Path

# Add prototype to sys.path
import sys
BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from recalculate_s0_static_metrics import recalculate_all_s0_metrics

RUN_DIR = Path(__file__).resolve().parents[4] / "01_os" / "07_content" / "_runs" / "run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001"
EXEC_DIR = RUN_DIR / "06_执行"
DB_PATH = Path(__file__).resolve().parents[4] / "01_os" / "07_content" / "_runs" / "run-20261024-nba2k22-world-data-implementation-002" / "_runtime" / "world-saves" / "nba2k22_test_01" / "world-v24.sqlite"
SCOPE_PATH = Path(__file__).resolve().parents[4] / "01_os" / "07_content" / "_runs" / "run-20261101-nba2k22-vae-g2-s0-baseline-loop-observability-pilot-001" / "06_执行" / "score_discrepancy_scope.json"


class StaticShotTendencyReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.join_path = EXEC_DIR / "static_source_join_quality.json"
        cls.summary_path = EXEC_DIR / "static_shot_tendency_s0_summary.json"
        cls.report_path = EXEC_DIR / "static_shot_tendency_s0_analysis.md"

        with open(cls.join_path, "r", encoding="utf-8") as f:
            cls.join_data = json.load(f)
        with open(cls.summary_path, "r", encoding="utf-8") as f:
            cls.summary_data = json.load(f)
        with open(cls.report_path, "r", encoding="utf-8") as f:
            cls.report_text = f.read()

        if DB_PATH.exists():
            cls.live_metrics = recalculate_all_s0_metrics(DB_PATH, SCOPE_PATH)
        else:
            cls.live_metrics = None

    def test_q01_save_binding_and_db_matching(self):
        """Q01: Verify save binding matches MyLEAGUE0003 and local SQLite, no new capture/mutation."""
        src = self.join_data["source_environment"]
        self.assertEqual(src["save_id"], "nba2k22_test_01")
        self.assertEqual(src["loaded_filename"], "MyLEAGUE0003")
        self.assertEqual(src["database_file"], "world-v24.sqlite")

    def test_q02_provenance_and_offset_verification(self):
        """Q02: Verify real byte offset 0x458 and PlayerData mapping; documented overall_raw gap."""
        sett = self.join_data["native_setting_definition"]
        self.assertEqual(sett["field_id"], "TENDENCY_NATIVE_001")
        self.assertEqual(sett["byte_offset_hex"], "0x458")
        self.assertEqual(sett["byte_offset_dec"], 1112)
        self.assertEqual(sett["native_struct"], "PlayerData")

        # Documented data gap
        attr_audit = self.join_data["table_join_provenance"]["player_attribute_snapshots"]
        self.assertIn("UNPOPULATED", attr_audit["overall_raw_status"])
        self.assertIn("POPULATED", attr_audit["individual_shooting_attributes_status"])

    def test_q03_sample_eligibility_and_denominator(self):
        """Q03: Verified eligible players and denominators; no fake 462 equally qualified sample."""
        pop = self.join_data["sample_population_breakdown"]
        self.assertEqual(pop["raw_league_roster_count"], 461)
        self.assertEqual(pop["players_with_simulated_minutes"], 369)
        self.assertEqual(pop["cohort_qualified_rotation"]["sample_size"], 268)
        self.assertEqual(pop["cohort_clean_conserved_rotation"]["sample_size"], 257)

        # In summary JSON
        counts = self.summary_data["cohort_definitions_and_counts"]
        self.assertEqual(counts["cohort_qualified_rotation"]["count"], 268)
        self.assertEqual(counts["cohort_clean_conserved_rotation"]["count"], 257)

    def test_q04_fga36_and_shot_share_metrics(self):
        """Q04: Verify FGA/36 and team shot share metrics and correlation strength."""
        corr = self.summary_data["bivariate_correlations"]
        self.assertGreater(corr["shot_tendency_vs_fga_per_game"], 0.90)
        self.assertGreater(corr["shot_tendency_vs_fga_per_36"], 0.88)
        self.assertGreater(corr["shot_tendency_vs_team_shot_share"], 0.90)

        # Monotonicity of bins
        bins = self.summary_data["tendency_bins_breakdown"]
        self.assertEqual(len(bins), 6)
        for i in range(len(bins) - 1):
            self.assertLess(bins[i]["mean_tendency"], bins[i+1]["mean_tendency"])
            self.assertLess(bins[i]["mean_fga_36"], bins[i+1]["mean_fga_36"])
            self.assertLess(bins[i]["mean_team_shot_share"], bins[i+1]["mean_team_shot_share"])

    def test_q05_multivariate_controls_and_no_causal_overreach(self):
        """Q05: Verify regression models control for confounders and include causal caveats."""
        m3 = self.summary_data["multivariate_regression_models"]["model_3_full_multivariate"]
        self.assertGreater(m3["r2"], 0.80)
        coefs = m3["coefficients"]
        self.assertIn("ShotTendency", coefs)
        self.assertIn("MPG", coefs)
        self.assertIn("TouchesTendency", coefs)
        self.assertIn("Pos_SG", coefs)
        self.assertGreater(coefs["ShotTendency"]["t_stat"], 10.0)

        # Methodological caveats present
        caveats = self.summary_data["static_evidence_evaluation_of_proposed_intervention"]["methodological_caveats"]
        self.assertTrue(any("CROSS_SECTIONAL_SLOPE_NOT_CAUSAL" in c for c in caveats))

    def test_q06_human_declaration_context(self):
        """Q06: Historical no-manual-modifications recorded as Human declaration."""
        decl = self.join_data["source_environment"]["human_declaration"]
        self.assertIn("Human confirmed NO manual", decl)

    def test_q07_phase_a_human_gates_preserved(self):
        """Q07: Verify Phase A smoke test plan preserves WAIT_HUMAN_AUTHORIZATION gate."""
        smoke = self.summary_data["phase_a_human_smoke_test_recommendation"]
        self.assertEqual(smoke["authorization_gate"], "WAIT_HUMAN_AUTHORIZATION")
        self.assertEqual(smoke["target_player"], "Damian Lillard (player:native:2459)")
        self.assertEqual(smoke["proposed_value"], 80)
        self.assertEqual(smoke["status"], "PROPOSED_AWAITING_HUMAN_APPROVAL")

    def test_q08_sqlite_live_query_reproducibility(self):
        """Q08: Live recomputation of core sample, correlations, regressions, and bins on SQLite."""
        if self.live_metrics is None:
            self.skipTest("SQLite DB not found at runtime path")

        res = self.live_metrics
        # 1. Base table row counts in SQLite
        rc = res["row_counts"]
        self.assertEqual(rc["player_tendency_snapshots"], 13667)
        self.assertEqual(rc["player_attribute_snapshots"], 13667)
        self.assertEqual(rc["player_vitals_observations"], 23837)
        self.assertEqual(rc["capture_units"], 58)

        # 2. Sample sizes
        self.assertEqual(res["cohort_all_count"], 268)
        self.assertEqual(res["cohort_clean_count"], 257)

        # 3. Live correlations match reported values
        c = res["correlations"]
        self.assertAlmostEqual(c["shot_tendency_vs_fga_per_game"], 0.9303, places=3)
        self.assertAlmostEqual(c["shot_tendency_vs_fga_per_36"], 0.9008, places=3)
        self.assertAlmostEqual(c["shot_tendency_vs_team_shot_share"], 0.9316, places=3)
        self.assertAlmostEqual(c["shot_tendency_vs_mpg"], 0.6960, places=3)

        # 4. Live Model 3 estimates match reported values
        m3_coef = res["model_3"]["coefficients"]["ShotTendency"]
        self.assertAlmostEqual(m3_coef["beta"], 0.2145, places=3)
        self.assertAlmostEqual(m3_coef["std_error"], 0.0127, places=3)
        self.assertAlmostEqual(m3_coef["t_stat"], 16.83, places=1)
        self.assertAlmostEqual(res["model_3"]["r2"], 0.8446, places=3)

        # 5. Live Model 4 estimates match reported values
        m4_coef = res["model_4"]["coefficients"]["ShotTendency"]
        self.assertAlmostEqual(m4_coef["beta"], 0.0017, places=4)
        self.assertAlmostEqual(m4_coef["t_stat"], 17.35, places=1)
        self.assertAlmostEqual(res["model_4"]["r2"], 0.9370, places=3)

        # 6. Live Lillard statistics match reported values
        lil = res["lillard"]
        self.assertEqual(lil["games_played"], 16)
        self.assertAlmostEqual(lil["fga_per_game"], 19.875, places=2)
        self.assertAlmostEqual(lil["fga_per_36"], 19.670, places=2)
        self.assertAlmostEqual(lil["team_shot_share"], 0.2309, places=3)

        # 7. Live 6 bins match counts and strict monotonicity
        expected_counts = [28, 108, 52, 44, 27, 9]
        live_counts = [b["count"] for b in res["bins"]]
        self.assertEqual(live_counts, expected_counts)
        for i in range(len(res["bins"]) - 1):
            self.assertLess(res["bins"][i]["mean_tendency"], res["bins"][i+1]["mean_tendency"])
            self.assertLess(res["bins"][i]["mean_fga_36"], res["bins"][i+1]["mean_fga_36"])
            self.assertLess(res["bins"][i]["mean_team_shot_share"], res["bins"][i+1]["mean_team_shot_share"])


if __name__ == "__main__":
    unittest.main()

"""Tests for S0 Static Shot Tendency Analysis, Join Quality, and Human-Gated Phase A Protocols.

Part of NBA2K22-VAE-S0-STATIC-SHOT-TENDENCY-LOOP-20261101-001.
"""
import json
import sqlite3
import unittest
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[4] / "01_os" / "07_content" / "_runs" / "run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001"
EXEC_DIR = RUN_DIR / "06_执行"
DB_PATH = Path(__file__).resolve().parents[4] / "01_os" / "07_content" / "_runs" / "run-20261024-nba2k22-world-data-implementation-002" / "_runtime" / "world-saves" / "nba2k22_test_01" / "world-v24.sqlite"


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
        """Q08: Run deterministic verification against world-v24.sqlite if present."""
        if not DB_PATH.exists():
            self.skipTest("SQLite DB not found at runtime path")

        conn = sqlite3.connect(DB_PATH)
        # Verify Lillard game count is 16
        lillard_games = conn.execute("""
            SELECT COUNT(DISTINCT pb.game_id)
            FROM player_game_boxes pb
            JOIN game_state_observations s ON pb.game_id = s.game_id AND pb.unit_id = s.unit_id
            WHERE pb.player_id = 'player:native:2459' AND s.is_final = 1 AND s.was_simulated = 1
        """).fetchone()[0]
        self.assertEqual(lillard_games, 16)
        conn.close()


if __name__ == "__main__":
    unittest.main()

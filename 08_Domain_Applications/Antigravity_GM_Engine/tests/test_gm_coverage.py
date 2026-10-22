import tempfile
import unittest
from fixtures import project
from gm_core.coverage import assess, state_value
from gm_core.reports import prepare_run
from gm_core.models import MODULES


class CoverageTests(unittest.TestCase):
    def test_same_input_produces_same_calculations(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory, complete=True)
            first = prepare_run(data, "SYNTHETIC_FIRST")
            second = prepare_run(data, "SYNTHETIC_SECOND", mode="analysis")
            self.assertEqual(first["calculations"], second["calculations"])
            self.assertEqual(second["status"], "ANALYSIS_ONLY")
            self.assertFalse(second["decisions"])
    def test_partial_data_does_not_fail_30_teams(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            run = prepare_run(data, "SYNTHETIC_PARTIAL")
            self.assertEqual(run["teams_reviewed"], 30)
            self.assertEqual(run["status"], "SIMULATION")
            for abbreviation, team in run["team_reviews"].items():
                self.assertEqual(set(team["modules"]), set(MODULES))
                self.assertEqual(team["profile"]["lifecycle"]["state"], "UNDETERMINED")
                self.assertEqual(team["modules"]["staff"]["evaluation"], "NOT_EVALUABLE")
                self.assertIsNone(run["calculations"][f"{abbreviation}.win_percentage"]["value"])
                self.assertFalse(any(module["executable_operation_ready"] for module in team["modules"].values()))

    def test_source_not_observed_overrides_non_null_field(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            data.teams["T00"]["state"]["total_wins"] = 99
            self.assertEqual(assess(data, data.teams["T00"], "results")["readiness"], "BLOCKED")

    def test_complete_synthetic_metrics_and_staff(self):
        with tempfile.TemporaryDirectory() as directory:
            run = prepare_run(project(directory, complete=True), "SYNTHETIC_COMPLETE")
            self.assertEqual(run["calculations"]["T00.win_percentage"]["value"], 0.6)
            self.assertEqual(run["calculations"]["T00.net_rating"]["value"], 5)
            self.assertEqual(run["team_reviews"]["T00"]["modules"]["staff"]["readiness"], "READY")

    def test_all_unknown_still_serializable(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            for team in data.teams.values():
                team["state"] = {"team_id": team["identity"]["team_id"]}
                team["roster"] = []
            run = prepare_run(data, "SYNTHETIC_UNKNOWN")
            self.assertEqual(run["teams_reviewed"], 30)
            self.assertEqual(run["team_reviews"]["T00"]["modules"]["business"]["readiness"], "BLOCKED")

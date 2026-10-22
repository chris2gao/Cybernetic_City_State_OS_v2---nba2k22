import copy
import tempfile
import unittest
from pathlib import Path
from fixtures import project
from gm_core.reports import prepare_run
from gm_core.history import compare_context, StateStore


class FranchiseTests(unittest.TestCase):
    def test_salary_is_not_lifecycle_and_goals_unapproved(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            data.teams["T00"]["state"]["total_salary"] = 999_000_000
            run = prepare_run(data, "SYNTHETIC_A")
            profile = run["team_reviews"]["T00"]["profile"]
            self.assertEqual(profile["lifecycle"]["state"], "UNDETERMINED")
            self.assertEqual(profile["status"], "PROPOSED")
            self.assertIsNone(profile["last_confirmed_decision"])

    def test_independent_teams_and_snapshot_change(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory, complete=True)
            before = prepare_run(data, "SYNTHETIC_BEFORE")
            data.teams["T00"]["state"]["budget"] += 10
            after = prepare_run(data, "SYNTHETIC_AFTER", previous=before)
            self.assertEqual(after["team_reviews"]["T00"]["changes_from_previous"]["budget"]["after"], 20_000_010)
            self.assertEqual(after["team_reviews"]["T01"]["changes_from_previous"], {})
            self.assertNotEqual(before["team_reviews"]["T00"]["profile"]["team"], before["team_reviews"]["T01"]["profile"]["team"])

    def test_rollback_or_wrong_career_does_not_adopt_future_history(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            previous = prepare_run(data, "SYNTHETIC_FUTURE")
            previous["source"]["game_date"] = "2022-01-01"
            with self.assertRaises(ValueError):
                compare_context(data, previous)
            previous["source"]["game_date"] = data.source.game_date
            previous["career_id"] = "another_career"
            with self.assertRaises(ValueError):
                compare_context(data, previous)

    def test_existing_formal_profiles_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            store = StateStore(directory)
            formal = Path(directory) / "gm_state/careers/synthetic_career/teams/T00.json"
            formal.parent.mkdir(parents=True)
            formal.write_text("PLAYER_CONFIRMED_EXISTING_PROFILE", encoding="utf-8")
            run = prepare_run(data, "SYNTHETIC_ISOLATED")
            output = store.save_run(run, "simulation")
            self.assertTrue((output / "teams/T00.json").exists())
            self.assertEqual(formal.read_text(encoding="utf-8"), "PLAYER_CONFIRMED_EXISTING_PROFILE")
            with self.assertRaises(FileExistsError):
                store.save_run(run, "simulation")

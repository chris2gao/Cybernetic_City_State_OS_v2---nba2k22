import json
import unittest
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from screening_matrix import make_matrix
from sim_control import Binding, Game, Plan, Snapshot, preflight, run_fixture


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.start = date(2021, 12, 21)
        self.target = self.start + timedelta(days=2)
        self.binding = Binding("fixture-save", "fixture-world", "a" * 64, "fixture-epoch", "2021-22")
        self.game = Game("g1", self.target, "ATL", "BOS")
        self.before = Snapshot(self.binding, self.start, (self.game,), True)
        self.plan = Plan(self.binding, self.start, self.target, ("g1",), 3)
        completed = replace(self.game, final=True, simulated=True, box_complete=True, capture_unit="fixture-capture")
        self.after = replace(self.before, day=self.target, games=(completed,))
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.journal = Path(folder.name)

    def execute(self, frames):
        return run_fixture(self.plan, self.before, frames, self.journal, fixture_grant_digest=self.plan.digest)

    def test_dry_run_and_invalid_grant_do_not_consume_observation_or_journal(self):
        self.assertEqual(run_fixture(self.plan, self.before, None, self.journal), "DRY_RUN_READY")
        self.assertEqual(run_fixture(self.plan, self.before, None, self.journal, fixture_grant_digest="bad"),
                         "FIXTURE_GRANT_MISMATCH")
        self.assertEqual(list(self.journal.iterdir()), [])

    def test_async_and_saving_wait_for_complete_same_unit(self):
        pending = [replace(self.before, runtime="SIMULATING"), replace(self.after, runtime="SAVING")]
        self.assertEqual(self.execute([*pending, self.after]), "OFFLINE_COMPLETE")
        log = [json.loads(line) for line in next(self.journal.iterdir()).read_text().splitlines()]
        self.assertEqual([row["status"] for row in log[1:]], ["PENDING", "PENDING", "OFFLINE_COMPLETE", "OFFLINE_COMPLETE"])
        self.assertEqual(self.execute([]), "HELD_NO_REPLAY")

    def test_date_change_does_not_prove_game_completion(self):
        self.assertEqual(self.execute([replace(self.before, day=self.target)]), "PARTIAL_RESULT")

    def test_unknown_box(self):
        incomplete = replace(self.after.games[0], box_complete=False)
        self.assertEqual(self.execute([replace(self.after, games=(incomplete,))]), "PARTIAL_RESULT")

    def test_mismatched_capture_unit(self):
        second = replace(self.game, game_id="g2")
        self.before = replace(self.before, games=(self.game, second))
        self.plan = replace(self.plan, expected_game_ids=("g1", "g2"))
        complete = self.after.games[0]
        after = replace(self.after, games=(complete, replace(complete, game_id="g2", capture_unit="other")))
        self.assertEqual(self.execute([after]), "PARTIAL_RESULT")

    def test_timeout_never_retries_even_after_new_epoch_or_plan(self):
        self.assertEqual(self.execute([replace(self.before, runtime="SIMULATING")] * 4), "TIMEOUT_UNKNOWN")
        self.binding = replace(self.binding, epoch="restarted")
        self.plan = replace(self.plan, binding=self.binding, max_polls=2)
        self.before = replace(self.before, binding=self.binding)
        self.assertEqual(self.execute([]), "HELD_NO_REPLAY")

    def test_observation_exception_holds_journal(self):
        self.assertEqual(self.execute([None]), "UNKNOWN")
        self.assertEqual(self.execute([self.after]), "HELD_NO_REPLAY")

    def test_empty_reservation_after_crash_still_holds(self):
        self.assertEqual(self.execute([self.after]), "OFFLINE_COMPLETE")
        next(self.journal.iterdir()).write_text("", encoding="utf-8")
        self.assertEqual(self.execute([self.after]), "HELD_NO_REPLAY")

    def test_new_final_outside_window_is_unknown(self):
        outside = replace(self.after.games[0], game_id="unexpected", day=self.target + timedelta(days=1))
        self.assertEqual(self.execute([replace(self.after, games=(*self.after.games, outside))]), "UNKNOWN")

    def test_overshoot_or_dialog_or_changed_schedule_is_unknown(self):
        examples = [
            replace(self.after, day=self.target + timedelta(days=1)),
            replace(self.after, runtime="DIALOG"),
            replace(self.after, games=(replace(self.after.games[0], home="MIA"),)),
            replace(self.after, phase="PLAYOFFS"),
            replace(self.after, binding=replace(self.binding, epoch="another")),
        ]
        for frame in examples:
            with self.subTest(frame=frame), TemporaryDirectory() as temp:
                result = run_fixture(self.plan, self.before, [frame], temp, fixture_grant_digest=self.plan.digest)
                self.assertEqual(result, "UNKNOWN")

    def test_preflight_denies_wrong_mode_offday_events_incomplete_and_in_progress(self):
        for plan, state, code in [
            (self.plan, replace(self.before, schedule_complete=False), "SCHEDULE_UNKNOWN"),
            (self.plan, replace(self.before, runtime="GAME_IN_PROGRESS"), "UNSAFE_SCENE"),
            (self.plan, replace(self.before, blocking_dates=(self.target,)), "SEASON_EVENT"),
            (self.plan, replace(self.before, binding=replace(self.binding, mode="MyCAREER")), "BINDING_MISMATCH"),
            (self.plan, replace(self.before, games=()), "SCHEDULE_MISMATCH"),
            (replace(self.plan, expected_game_ids=()), replace(self.before, games=()), "OFFDAY_ONLY"),
            (replace(self.plan, target=self.start), self.before, "INVALID_WINDOW"),
        ]:
            with self.subTest(code=code):
                self.assertEqual(preflight(plan, state), code)


class MatrixTests(unittest.TestCase):
    def test_replay_and_exposure_symmetry(self):
        matrix = make_matrix()
        fixture = Path(__file__).with_name("single-worldline-matrix.json")
        self.assertEqual(matrix, json.loads(fixture.read_bytes()))
        rows = {r["team"]: r for r in matrix["teams"]}
        self.assertEqual(len(rows), 30)
        for arm, count in [("H", 6), ("L", 6), ("C", 6), ("RESERVE", 12)]:
            self.assertEqual(sum(r["arm"] == arm for r in rows.values()), count)
        self.assertEqual(len({g["game_id"] for g in matrix["games"]}), 90)
        for game in matrix["games"]:
            home, away = rows[game["home"]], rows[game["away"]]
            self.assertEqual(game["home_opponent_exposure"], away["arm"])
            self.assertEqual(game["away_opponent_exposure"], home["arm"])
            self.assertEqual(game["opposite_treatment"], {home["arm"], away["arm"]} == {"H", "L"})
            self.assertIn(game["game_id"], home["game_ids"])
            self.assertIn(game["game_id"], away["game_ids"])


if __name__ == "__main__":
    unittest.main()

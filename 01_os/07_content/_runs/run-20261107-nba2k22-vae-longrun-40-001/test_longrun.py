import json
from pathlib import Path
import tempfile
import unittest
from collections import Counter
from copy import deepcopy

from build_ledger import build
from build_observed_round import FEATURES, assign_blocks
from experiment_round import analyze, fixture, plan
from window_harness import FixturePort, Journal, execute_fixture, fixture_permit, reconcile_fixture

HERE = Path(__file__).resolve().parent


class LongrunTests(unittest.TestCase):
    def setUp(self):
        self.plan = plan(fixture(), 20261107)
        self.permit = fixture_permit(self.plan)

    def test_observed_blocking_is_repeatable_and_covers_all_teams(self):
        features = {team: {feature: team + offset for offset, feature in enumerate(FEATURES)}
                    for team in range(30)}
        candidates = {team: {"position": "CENTER"} for team in features}
        groups, _, _ = assign_blocks(features, candidates)
        self.assertEqual(groups, [list(range(start, start + 5)) for start in range(0, 30, 5)])
        self.assertEqual(groups, assign_blocks(dict(reversed(list(features.items()))), candidates)[0])

    def test_pinned_ledger_and_eligibility(self):
        ledger = build()
        self.assertEqual(json.loads((HERE / "mechanism_research_ledger.json").read_bytes()), ledger)
        self.assertEqual(ledger["coverage"]["stage02_observation_fields"], 204)
        self.assertEqual(ledger["coverage"]["tendency_subset"]["unknown_read_only"], 51)
        self.assertEqual(ledger["coverage"]["historical_bounded_live_writer_fields"], 1)
        self.assertFalse(any(row["eligible_for_live_round_now"] for row in ledger["rows"]))

    def test_preregistration_replays(self):
        self.assertEqual(json.loads((HERE / "round_fixture_plan.json").read_bytes()), self.plan)
        self.assertEqual(Counter(item["arm"] for item in self.plan["assignments"]),
                         {"H": 6, "L": 6, "C": 6, "RESERVE": 12})
        self.assertEqual(len(self.plan["write_candidates"]), 12)
        self.assertNotEqual(self.plan["assignments"], plan(fixture(), 20261108)["assignments"])
        self.assertTrue(all(row["applied_value"] is None for row in self.plan["assignments"]))

    def test_invalid_schedule_and_uid(self):
        data = fixture()
        data["games"][0]["day"] = data["stop"]
        with self.assertRaises(ValueError):
            plan(data, 1)
        data = fixture()
        data["teams"][1]["candidate"]["uid"] = data["teams"][0]["candidate"]["uid"]
        with self.assertRaises(ValueError):
            plan(data, 1)
        data = fixture()
        data["teams"][0]["candidate"]["shot_tendency"] = 97
        with self.assertRaises(ValueError):
            plan(data, 1)

    def test_full_fixture_and_duplicate_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            port = FixturePort(self.plan)
            report = execute_fixture(root, self.plan, self.permit, port)
            self.assertEqual(report["planned_game_count"], 60)
            self.assertEqual(report["classification"], "UNDERPOWERED_SCREENING_ONLY")
            self.assertEqual((port.commands, port.setters), (1, 12))
            self.assertIn("checkpoint", Journal(root, self.plan).inspect())
            with self.assertRaises(FileExistsError):
                execute_fixture(root, self.plan, self.permit, port)
            self.assertEqual((port.commands, port.setters), (1, 12))

    def test_preflight_stops(self):
        for fault in ("wrong_binding", "lost_focus", "season_boundary", "not_persistent"):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                port = FixturePort(self.plan, fault)
                with self.assertRaises(ValueError):
                    execute_fixture(Path(directory), self.plan, self.permit, port)
                self.assertEqual((port.commands, port.setters), (0, 0))

    def test_tampered_or_incomplete_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            port = FixturePort(self.plan)
            bad = dict(self.permit, setter_digests=[])
            with self.assertRaises(ValueError):
                execute_fixture(Path(directory), self.plan, bad, port)
            bad_plan = deepcopy(self.plan)
            bad_plan["write_candidates"][0]["target"] = 100
            with self.assertRaises(ValueError):
                execute_fixture(Path(directory), bad_plan, self.permit, port)
            self.assertEqual((port.commands, port.setters), (0, 0))

    def test_unqualified_factor_and_live_attempt_denied(self):
        with tempfile.TemporaryDirectory() as directory:
            for changes in ({"factor": "TOUCHES"}, {"evidence_scope": "REAL_NATIVE"}):
                candidate = dict(self.plan, **changes)
                port = FixturePort(candidate)
                with self.assertRaises(ValueError):
                    execute_fixture(Path(directory), candidate, fixture_permit(candidate), port)
                self.assertEqual((port.commands, port.setters), (0, 0))

    def test_cas_stops_before_simulation(self):
        with tempfile.TemporaryDirectory() as directory:
            port = FixturePort(self.plan, "cas")
            with self.assertRaises(RuntimeError):
                execute_fixture(Path(directory), self.plan, self.permit, port)
            self.assertEqual((port.commands, port.setters), (0, 0))

    def test_unknown_crash_and_partial_no_replay(self):
        for fault in ("unknown", "crash", "partial", "mixed_unit", "score"):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                port = FixturePort(self.plan, fault)
                with self.assertRaises((ValueError, RuntimeError)):
                    execute_fixture(root, self.plan, self.permit, port)
                self.assertIn("halt", Journal(root, self.plan).inspect())
                with self.assertRaises(FileExistsError):
                    execute_fixture(root, self.plan, self.permit, port)
                self.assertEqual(port.commands, 1)
                replay = reconcile_fixture(root, self.plan, FixturePort(self.plan).capture())
                self.assertEqual(replay["planned_game_count"], 60)
                self.assertEqual(port.commands, 1)

    def test_same_binding_and_no_dnp_imputation(self):
        capture = FixturePort(self.plan, "dnp").capture()
        report = analyze(self.plan, capture)
        dnp = next(row for row in report["observations"] if row["disposition"] == "DNP")
        self.assertIsNone(dnp["fga_per_36"])
        self.assertEqual(dnp["fga"], 0)
        missing = analyze(self.plan, FixturePort(self.plan, "unobserved").capture())
        self.assertIsNone(next(row for row in missing["observations"] if row["disposition"] == "UNOBSERVED")["fga"])
        capture["identity"] = dict(capture["identity"], worldline="other")
        with self.assertRaises(ValueError):
            analyze(self.plan, capture)


if __name__ == "__main__":
    unittest.main()

import unittest
from fixtures import ROOT
from gm_core.calculations import (difference, observed_sum, distribution, win_percentage,
                                  efficiency, field_changes, roster_changes, draft_year, salary_exchange)


class CalculationsTests(unittest.TestCase):
    def test_payroll_and_known_zero(self):
        self.assertEqual(difference(20, 30)["value"], -10)
        self.assertEqual(observed_sum([0, 4])["value"], 4)
        self.assertEqual(difference(0, 0)["availability"], "CALCULATED")

    def test_unknown_never_filled_with_zero(self):
        for value in (None, True, float("nan"), float("inf"), "10"):
            self.assertIsNone(difference(value, 10)["value"])
            self.assertIsNone(observed_sum([value])["value"])
        self.assertIsNone(observed_sum([])["value"])
        self.assertIsNone(observed_sum(None)["value"])
        self.assertIsNone(field_changes(None, {})["value"])
        self.assertIsNone(roster_changes(None, [])["value"])
        self.assertIsNone(distribution(None, "position")["value"])

    def test_numeric_overflow_is_unknown(self):
        self.assertIsNone(difference(1e308, -1e308)["value"])
        self.assertIsNone(observed_sum([1e308, 1e308])["value"])
        self.assertIsNone(efficiency(1e308, 0.1)["value"])

    def test_distribution(self):
        self.assertEqual(distribution(["PG", "PG", "C"], "position")["value"], {"C": 1, "PG": 2})
        self.assertIsNone(distribution(["PG", None], "position")["value"])
        self.assertEqual(distribution([1, 2, 2], "contract_years")["value"], {"1": 1, "2": 2})

    def test_results_and_conflict(self):
        self.assertEqual(win_percentage(12, 8, 20)["value"], 0.6)
        self.assertIsNone(win_percentage(12, 8, 21)["value"])
        self.assertIsNone(win_percentage(None, 8)["value"])
        self.assertIsNone(win_percentage(0, 0)["value"])
        self.assertEqual(efficiency(110, 100)["value"], 110)
        self.assertIsNone(efficiency(110, 0)["value"])

    def test_determinism_diff_and_salary(self):
        self.assertEqual(difference(123, 45), difference(123, 45))
        self.assertEqual(field_changes({"a": 1}, {"a": 2})["a"], {"before": 1, "after": 2})
        self.assertEqual(salary_exchange([10, 20], [50])["payroll_change"]["value"], 20)
        self.assertIsNone(salary_exchange([None], [50])["payroll_change"]["value"])

    def test_draft_cycle_and_invalid_counts(self):
        self.assertEqual([draft_year(n)["value"]["next_class_year"] for n in (0, 36, 37, 38)], [1984, 2020, 1984, 1985])
        for count in (None, -1, True, 1.5):
            self.assertIsNone(draft_year(count)["value"])

    def test_roster_changes_and_identity_conflict(self):
        before = [{"player_name": "Synthetic", "face_id": 1, "salary_current_year": 10}]
        after = [dict(before[0], salary_current_year=11)]
        self.assertEqual(roster_changes(before, after)["value"]["changed"][0]["fields"]["salary_current_year"]["after"], 11)
        self.assertIsNone(roster_changes(before + before, after)["value"])

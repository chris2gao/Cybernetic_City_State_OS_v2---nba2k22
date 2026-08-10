"""Unit tests for the quiet verification entry point.

The load-bearing properties are: a passing check must not print its output,
a failing check must still surface evidence, and a non-zero expected exit code
must be honoured rather than treated as failure.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quiet_verify as qv  # noqa: E402

PY = sys.executable


def check(name, code, noise=""):
    script = f"import sys; sys.stdout.write({noise!r}); sys.exit({code})"
    return {"name": name, "cmd": [PY, "-c", script]}


class TestRunCheck(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_passing_check_discards_output(self):
        noisy = "line\n" * 500
        r = qv.run_check(check("ok", 0, noisy), self.root, tail=20)
        self.assertTrue(r["ok"])
        self.assertEqual(r["tail"], "", "a passing check must not carry its output")

    def test_failing_check_keeps_bounded_tail(self):
        noisy = "".join(f"l{i}\n" for i in range(500))
        r = qv.run_check(check("bad", 1, noisy), self.root, tail=20)
        self.assertFalse(r["ok"])
        self.assertEqual(len(r["tail"].splitlines()), 20)
        self.assertIn("l499", r["tail"])

    def test_expected_nonzero_exit_counts_as_ok(self):
        c = check("expects_2", 2)
        c["expect_exit"] = 2
        self.assertTrue(qv.run_check(c, self.root, tail=5)["ok"])

    def test_unexpected_zero_exit_is_failure(self):
        c = check("expects_2", 0)
        c["expect_exit"] = 2
        self.assertFalse(qv.run_check(c, self.root, tail=5)["ok"])


class TestSummaryAndLoading(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_summary_counts(self):
        results = [{"ok": True}, {"ok": False}, {"ok": True}]
        self.assertEqual(qv.summarize(results), "checks 2/3 ok")

    def test_load_checks_rejects_missing_cmd(self):
        f = self.root / "checks.yml"
        f.write_text("checks:\n- name: broken\n", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            qv.load_checks(f)

    def test_load_checks_rejects_empty(self):
        f = self.root / "checks.yml"
        f.write_text("checks: []\n", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            qv.load_checks(f)

    def test_main_returns_1_when_a_check_fails(self):
        f = self.root / "checks.yml"
        f.write_text(
            "checks:\n"
            f"- name: good\n  cmd: ['{PY}', '-c', 'pass']\n"
            f"- name: bad\n  cmd: ['{PY}', '-c', 'raise SystemExit(1)']\n",
            encoding="utf-8",
        )
        rc = qv.main(["--checks", str(f), "--repo-root", str(self.root)])
        self.assertEqual(rc, 1)

    def test_default_check_set_is_declared(self):
        names = [c["name"] for c in qv.DEFAULT_CHECKS]
        self.assertEqual(
            names,
            ["workflow_static", "context_structure",
             "no_canonical_live_state", "stage_deliberation_v2_static"],
        )


if __name__ == "__main__":
    unittest.main()

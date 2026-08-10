"""Unit tests for the task preflight.

The load-bearing properties are: a closed or absent gate must never read as open,
and only genuine stop conditions may count as hard failures.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preflight_task_context as pf  # noqa: E402

CLEAN = {
    "task_id": "t", "branch_declared": "dev/x", "branch_actual": "dev/x",
    "local_head": "a" * 40, "hooks_path": ".githooks", "dirty_path_count": 0,
    "head_descends_from_base": True, "master_unchanged": True,
    "remote_master": "b" * 40, "commits_since_base": [],
}


class TestGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _gate(self, text):
        p = self.root / "gate.yml"
        p.write_text(text, encoding="utf-8")
        return pf.read_gate(p, "authorization.enter_stage_06_execution")

    def test_absent_gate_is_not_open(self):
        g = pf.read_gate(self.root / "missing.yml", "authorization.enter_stage_06_execution")
        self.assertFalse(g["present"])
        self.assertFalse(g["open"])

    def test_false_gate_is_not_open(self):
        g = self._gate("authorization:\n  enter_stage_06_execution: false\n")
        self.assertTrue(g["present"])
        self.assertFalse(g["open"])

    def test_true_gate_is_open(self):
        self.assertTrue(self._gate("authorization:\n  enter_stage_06_execution: true\n")["open"])

    def test_truthy_string_is_not_open(self):
        """'true' as a string must not pass an identity check."""
        self.assertFalse(self._gate("authorization:\n  enter_stage_06_execution: 'true'\n")["open"])

    def test_missing_key_is_not_open(self):
        self.assertFalse(self._gate("authorization: {}\n")["open"])


class TestHardFailures(unittest.TestCase):
    def test_clean_report_has_none(self):
        self.assertEqual(pf.hard_failures(dict(CLEAN), require_clean=True), [])

    def test_dirty_worktree_blocks_unless_allowed(self):
        r = dict(CLEAN, dirty_path_count=3)
        self.assertIn("worktree_dirty:3", pf.hard_failures(r, require_clean=True))
        self.assertEqual(pf.hard_failures(r, require_clean=False), [])

    def test_hook_guard_mismatch_blocks(self):
        r = dict(CLEAN, hooks_path="")
        self.assertIn("hook_guard:unset", pf.hard_failures(r, require_clean=True))

    def test_non_ancestor_base_blocks(self):
        r = dict(CLEAN, head_descends_from_base=False)
        self.assertIn("head_not_descended_from_declared_base",
                      pf.hard_failures(r, require_clean=True))

    def test_unknown_ancestry_does_not_block(self):
        """--no-remote / no declared base leaves fields None; None must not block."""
        r = dict(CLEAN, head_descends_from_base=None, master_unchanged=None)
        self.assertEqual(pf.hard_failures(r, require_clean=True), [])

    def test_branch_mismatch_blocks(self):
        r = dict(CLEAN, branch_actual="dev/other")
        self.assertIn("branch_mismatch:dev/other", pf.hard_failures(r, require_clean=True))

    def test_moved_master_blocks(self):
        r = dict(CLEAN, master_unchanged=False)
        self.assertTrue(
            any(f.startswith("remote_master_moved") for f in pf.hard_failures(r, True)))


class TestHelpers(unittest.TestCase):
    def test_parse_ls_remote(self):
        text = "abc\trefs/heads/master\ndef\trefs/heads/dev/x\n"
        self.assertEqual(pf.parse_ls_remote(text),
                         {"refs/heads/master": "abc", "refs/heads/dev/x": "def"})

    def test_dotted_get_missing_branch(self):
        self.assertIsNone(pf.dotted_get({"a": {"b": 1}}, "a.c.d"))
        self.assertEqual(pf.dotted_get({"a": {"b": 1}}, "a.b"), 1)

    def test_render_marks_blocked(self):
        out = pf.render(dict(CLEAN, base_declared="x", allowlist=[], prohibitions=[],
                             required_tests=[], remote_branch=None), None, ["hook_guard:unset"])
        self.assertIn("preflight       BLOCKED", out)


if __name__ == "__main__":
    unittest.main()

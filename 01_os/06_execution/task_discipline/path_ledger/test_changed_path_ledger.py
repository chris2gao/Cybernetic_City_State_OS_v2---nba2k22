"""Unit tests for the changed-path ledger.

Covers the two things that have actually gone wrong on this repository:
an allowlist matcher wider than intended, and status parsing that loses files
inside an untracked directory with non-ASCII names.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import changed_path_ledger as ledger  # noqa: E402

CN_RUN = "01_os/_runs/run-20260809-任务纪律工具-001"
CN_FILE = f"{CN_RUN}/01_任务输入/任务包_v1.yml"
TOOLS = "01_os/06_execution/task_discipline/**"


class TestMatches(unittest.TestCase):
    def test_double_star_covers_subtree(self):
        self.assertTrue(ledger.matches(TOOLS, "01_os/06_execution/task_discipline/preflight/a.py"))

    def test_double_star_does_not_leak_to_sibling_prefix(self):
        self.assertFalse(ledger.matches(TOOLS, "01_os/06_execution/task_discipline_other/a.py"))

    def test_exact_pattern_is_exact(self):
        pat = "01_os/05_registry/task_discipline_v1.yml"
        self.assertTrue(ledger.matches(pat, pat))
        self.assertFalse(ledger.matches(pat, "01_os/05_registry/task_discipline_v2.yml"))

    def test_no_inner_segment_globbing(self):
        self.assertFalse(ledger.matches("01_os/*/task_discipline/**",
                                        "01_os/06_execution/task_discipline/a.py"))

    def test_non_ascii_path_matches(self):
        self.assertTrue(ledger.matches(f"{CN_RUN}/**", CN_FILE))


class TestClassify(unittest.TestCase):
    def test_splits_inside_and_outside(self):
        inside, outside = ledger.classify(
            {CN_FILE, "01_os/06_execution/task_discipline/x.py", ".ai/PROTOCOL.md"},
            [f"{CN_RUN}/**", TOOLS],
        )
        self.assertEqual(len(inside), 2)
        self.assertEqual(outside, [".ai/PROTOCOL.md"])

    def test_empty_allowlist_puts_everything_outside(self):
        inside, outside = ledger.classify({CN_FILE}, [])
        self.assertEqual(inside, [])
        self.assertEqual(outside, [CN_FILE])


class TestWorktreeAgainstRealGit(unittest.TestCase):
    """The S-07 regression: an untracked directory must not collapse to one entry,
    and a non-ASCII path must not come back octal-escaped."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        for cmd in (
            ["init", "-q", "-b", "main"],
            ["config", "user.email", "t@example.invalid"],
            ["config", "user.name", "test"],
            # deliberately hostile defaults: octal escaping on, untracked collapsed
            ["config", "core.quotepath", "true"],
            ["config", "status.showUntrackedFiles", "normal"],
        ):
            subprocess.run(["git", *cmd], cwd=self.repo, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (self.repo / "seed.txt").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "seed.txt"], cwd=self.repo, check=True,
                       stdout=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.repo, check=True,
                       stdout=subprocess.DEVNULL)

    def tearDown(self):
        self._tmp.cleanup()

    def test_untracked_dir_expands_and_keeps_utf8(self):
        nested = self.repo / "01_os" / "_runs" / "运行-001" / "实现"
        nested.mkdir(parents=True)
        (nested / "工具.py").write_text("x = 1\n", encoding="utf-8")
        (nested / "plain.py").write_text("x = 1\n", encoding="utf-8")

        paths = ledger.worktree_paths(self.repo)

        self.assertIn("01_os/_runs/运行-001/实现/工具.py", paths)
        self.assertIn("01_os/_runs/运行-001/实现/plain.py", paths)
        self.assertNotIn("01_os/_runs/运行-001/实现/", paths)
        self.assertFalse([p for p in paths if "\\3" in p], "octal-escaped path leaked")

    def test_tracked_modification_is_included(self):
        (self.repo / "seed.txt").write_text("changed\n", encoding="utf-8")
        self.assertIn("seed.txt", ledger.worktree_paths(self.repo))


class TestRenameRegressionF1(unittest.TestCase):
    """Review finding F1: a rename must surface BOTH paths.

    Moving a file from a directory the allowlist does not cover into one it does
    is a change to an uncovered path. With git's default rename detection the
    ledger saw only the new name and reported the change as compliant.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self._g("init", "-q", "-b", "main")
        self._g("config", "user.email", "t@example.invalid")
        self._g("config", "user.name", "test")

    def tearDown(self):
        self._tmp.cleanup()

    def _g(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=False,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL).stdout.decode("utf-8")

    def test_rename_reports_old_and_new_path(self):
        (self.repo / "outside.txt").write_text("same content, so git sees a rename\n",
                                               encoding="utf-8")
        self._g("add", "-A")
        self._g("commit", "-qm", "base")
        base = self._g("rev-parse", "HEAD").strip()

        (self.repo / "inside").mkdir()
        self._g("mv", "outside.txt", "inside/renamed.txt")
        self._g("commit", "-qm", "rename")

        paths = ledger.committed_paths(self.repo, base, "HEAD")
        self.assertIn("inside/renamed.txt", paths)
        self.assertIn("outside.txt", paths, "F1: the vacated path must not disappear")

    def test_rename_out_of_allowlist_is_reported_as_violation(self):
        (self.repo / "outside.txt").write_text("payload\n", encoding="utf-8")
        self._g("add", "-A")
        self._g("commit", "-qm", "base")
        base = self._g("rev-parse", "HEAD").strip()
        (self.repo / "inside").mkdir()
        self._g("mv", "outside.txt", "inside/renamed.txt")
        self._g("commit", "-qm", "rename")

        paths = ledger.committed_paths(self.repo, base, "HEAD")
        _, outside = ledger.classify(paths, ["inside/**"])
        self.assertEqual(outside, ["outside.txt"])

    def test_non_ascii_rename_keeps_both_utf8_paths(self):
        (self.repo / "旧路径.txt").write_text("内容\n", encoding="utf-8")
        self._g("add", "-A")
        self._g("commit", "-qm", "base")
        base = self._g("rev-parse", "HEAD").strip()
        self._g("mv", "旧路径.txt", "新路径.txt")
        self._g("commit", "-qm", "rename")

        paths = ledger.committed_paths(self.repo, base, "HEAD")
        self.assertEqual(paths, {"旧路径.txt", "新路径.txt"})


if __name__ == "__main__":
    unittest.main()

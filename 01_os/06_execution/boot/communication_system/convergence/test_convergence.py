from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import unittest
from unittest.mock import patch

try:
    from .converge_task import (ConvergenceError, _git, converge,
                                observe_non_fast_forward, observe_same_path_conflict)
except ImportError:
    from converge_task import (ConvergenceError, _git, converge,
                               observe_non_fast_forward, observe_same_path_conflict)


ENV = {**os.environ, "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.com",
       "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com"}


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, env=ENV, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()


class ConvergenceTests(unittest.TestCase):
    def test_git_wrapper_enables_windows_longpaths(self):
        completed = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        with patch("subprocess.run", return_value=completed) as invoked:
            _git(Path("."), "status")
        self.assertEqual(
            invoked.call_args.args[0][:4],
            ["git", "-c", "core.longpaths=true", "status"],
        )

    def _repos(self, base: Path):
        remote = base / "remote.git"
        seed = base / "seed"
        actor = base / "actor"
        git(base, "init", "--bare", str(remote))
        git(base, "clone", str(remote), str(seed))
        (seed / "01_os/_communication/repo/active/task/messages/a").mkdir(parents=True)
        (seed / "README.md").write_text("init\n", encoding="utf-8")
        git(seed, "add", "README.md")
        git(seed, "branch", "-M", "task")
        git(seed, "commit", "-m", "init")
        git(seed, "push", "origin", "task")
        git(base, "clone", "--branch", "task", str(remote), str(actor))
        return remote, seed, actor

    def test_disjoint_remote_change_fast_forwards_then_single_push(self):
        with TemporaryDirectory() as temp:
            base = Path(temp)
            _, local, actor = self._repos(base)
            (actor / "remote.txt").write_text("remote\n", encoding="utf-8")
            git(actor, "add", "remote.txt")
            git(actor, "commit", "-m", "remote")
            git(actor, "push", "origin", "task")
            path = "01_os/_communication/repo/active/task/messages/a/00001_result.yml"
            (local / path).write_text("message\n", encoding="utf-8")
            result = converge(local, "task", [path],
                              "01_os/_communication/repo/active/task", "publish")
            self.assertEqual(result["push_attempt_count"], 1)
            self.assertTrue((local / "remote.txt").is_file())
            self.assertEqual(git(local, "rev-parse", "HEAD"), git(local, "rev-parse", "origin/task"))

    def test_committed_divergence_fails_closed(self):
        with TemporaryDirectory() as temp:
            base = Path(temp)
            _, local, actor = self._repos(base)
            (actor / "remote.txt").write_text("remote\n", encoding="utf-8")
            git(actor, "add", "remote.txt")
            git(actor, "commit", "-m", "remote")
            git(actor, "push", "origin", "task")
            path = "01_os/_communication/repo/active/task/messages/a/00001_result.yml"
            (local / path).write_text("message\n", encoding="utf-8")
            git(local, "add", path)
            git(local, "commit", "-m", "local")
            with self.assertRaisesRegex(ConvergenceError, "NON_FAST_FORWARD"):
                converge(local, "task", [path],
                         "01_os/_communication/repo/active/task", "publish")

    def test_path_outside_task_root_is_rejected_before_git(self):
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ConvergenceError, "PATH_OUTSIDE_TASK_ROOT"):
                converge(Path(temp), "task", ["README.md"],
                         "01_os/_communication/repo/active/task", "publish")

    def test_conflict_observation_stops_before_continuation(self):
        with TemporaryDirectory() as temp:
            _, local, actor = self._repos(Path(temp))
            (actor / "README.md").write_text("remote\n", encoding="utf-8")
            git(actor, "add", "README.md")
            git(actor, "commit", "-m", "remote conflict")
            git(actor, "push", "origin", "task")
            (local / "README.md").write_text("local\n", encoding="utf-8")
            git(local, "add", "README.md")
            git(local, "commit", "-m", "local conflict")
            observation = observe_same_path_conflict(local, "task")
            self.assertTrue(observation["operation_stopped"])
            self.assertFalse(observation["continuation_commit_created"])
            self.assertTrue(observation["Human_escalation_required"])

    def test_non_fast_forward_observation_never_force_pushes(self):
        with TemporaryDirectory() as temp:
            _, local, actor = self._repos(Path(temp))
            (actor / "remote.txt").write_text("remote\n", encoding="utf-8")
            git(actor, "add", "remote.txt")
            git(actor, "commit", "-m", "remote")
            git(actor, "push", "origin", "task")
            (local / "local.txt").write_text("local\n", encoding="utf-8")
            git(local, "add", "local.txt")
            git(local, "commit", "-m", "local")
            observation = observe_non_fast_forward(local, "task")
            self.assertEqual(len(observation["push_attempts"]), 1)
            self.assertNotIn("--force", observation["push_attempts"][0]["argv"])
            self.assertEqual(observation["remote_head_before"], observation["remote_head_after"])


if __name__ == "__main__":
    unittest.main()

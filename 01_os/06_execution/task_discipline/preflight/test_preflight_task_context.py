"""Unit tests for the task preflight.

The load-bearing properties are: a closed or absent gate must never read as open,
and only genuine stop conditions may count as hard failures.
"""
from __future__ import annotations

import sys
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preflight_task_context as pf  # noqa: E402

CLEAN = {
    "task_id": "t", "branch_declared": "dev/x", "branch_actual": "dev/x",
    "local_head": "a" * 40, "hooks_path": ".githooks", "dirty_path_count": 0,
    "head_descends_from_base": True, "master_unchanged": True,
    "master_verification": "verified_unchanged",
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

    def test_yaml11_yes_does_not_open_the_gate(self):
        """F3: YAML 1.1 resolves yes to True; the gate must still refuse it."""
        g = self._gate("authorization:\n  enter_stage_06_execution: yes\n")
        self.assertIs(g["value"], True, "PyYAML still resolves yes to True")
        self.assertFalse(g["open"], "F3: only the literal true may open the gate")
        self.assertIn("literal", g["reason"])

    def test_yaml11_on_does_not_open_the_gate(self):
        g = self._gate("authorization:\n  enter_stage_06_execution: on\n")
        self.assertFalse(g["open"])

    def test_capitalised_True_does_not_open_the_gate(self):
        g = self._gate("authorization:\n  enter_stage_06_execution: True\n")
        self.assertFalse(g["open"], "the contract says lowercase true")

    def test_literal_true_opens_and_records_raw(self):
        g = self._gate("authorization:\n  enter_stage_06_execution: true\n")
        self.assertTrue(g["open"])
        self.assertEqual(g["raw"], "true")
        self.assertEqual(g["reason"], "open")

    def test_false_records_reason_not_true(self):
        g = self._gate("authorization:\n  enter_stage_06_execution: false\n")
        self.assertEqual(g["reason"], "not_true")

    def test_absent_gate_records_reason_absent(self):
        g = pf.read_gate(self.root / "nope.yml", "authorization.enter_stage_06_execution")
        self.assertEqual(g["reason"], "absent")


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

    def test_unknown_base_ancestry_blocks(self):
        """Unknown ancestry cannot stand in for the required declared base."""
        r = dict(CLEAN, head_descends_from_base=None)
        self.assertIn("base_ancestry_unverified", pf.hard_failures(r, require_clean=True))

    def test_branch_mismatch_blocks(self):
        r = dict(CLEAN, branch_actual="dev/other")
        self.assertIn("branch_mismatch:dev/other", pf.hard_failures(r, require_clean=True))

    def test_moved_master_blocks(self):
        r = dict(CLEAN, master_unchanged=False, master_verification="moved")
        self.assertTrue(
            any(f.startswith("remote_master_moved") for f in pf.hard_failures(r, True)))

    def test_big_task_missing_confirmation_closure_blocks(self):
        r = dict(CLEAN, big_task=True, big_task_confirmation_closure=None)
        self.assertIn(
            "big_task_confirmation_closure_missing",
            pf.hard_failures(r, require_clean=True),
        )

    def test_big_task_uncovered_confirmation_blocks_before_dispatch(self):
        r = dict(CLEAN, big_task=True, big_task_confirmation_closure={
            "enabled": True,
            "known_confirmation_required_actions": ["publish-to-master"],
            "preconfirmed_actions": [],
            "uncovered_actions": ["publish-to-master"],
        })
        self.assertIn(
            "big_task_confirmation_closure_incomplete:publish-to-master",
            pf.hard_failures(r, require_clean=True),
        )

    def test_big_task_complete_confirmation_closure_passes(self):
        r = dict(CLEAN, big_task=True, big_task_confirmation_closure={
            "enabled": True,
            "known_confirmation_required_actions": ["publish-to-master"],
            "preconfirmed_actions": ["publish-to-master"],
            "uncovered_actions": [],
        })
        self.assertEqual(pf.hard_failures(r, require_clean=True), [])


class TestUnverifiedMasterF2(unittest.TestCase):
    """Review finding F2: an unread master must not pass as verified."""

    def test_not_read_blocks_by_default(self):
        r = dict(CLEAN, master_unchanged=None, master_verification="not_read",
                 remote_master=None)
        self.assertIn("master_not_verified:not_read", pf.hard_failures(r, require_clean=True))

    def test_missing_expectation_blocks_by_default(self):
        r = dict(CLEAN, master_unchanged=None,
                 master_verification="no_expectation_declared")
        self.assertIn("master_not_verified:no_expectation_declared",
                      pf.hard_failures(r, require_clean=True))

    def test_explicit_acceptance_unblocks(self):
        r = dict(CLEAN, master_unchanged=None, master_verification="not_read",
                 remote_master=None)
        self.assertEqual(
            pf.hard_failures(r, require_clean=True, accept_unverified_master=True), [])

    def test_acceptance_does_not_excuse_a_moved_master(self):
        r = dict(CLEAN, master_unchanged=False, master_verification="moved")
        self.assertTrue(
            pf.hard_failures(r, require_clean=True, accept_unverified_master=True),
            "accepting 'unverified' must not also accept 'verified and wrong'")

    def test_summary_never_says_bare_ok_when_unverified(self):
        r = dict(CLEAN, master_unchanged=None, master_verification="not_read",
                 remote_master=None, base_declared="x", allowlist=[], prohibitions=[],
                 required_tests=[], remote_branch=None)
        out = pf.render(r, None, [])
        self.assertIn("NOT VERIFIED", out)
        self.assertNotIn("preflight       ok\n", out + "\n")
        self.assertIn("UNVERIFIED MASTER", out)

    def test_summary_says_ok_only_when_verified(self):
        r = dict(CLEAN, base_declared="x", allowlist=[], prohibitions=[],
                 required_tests=[], remote_branch=None)
        out = pf.render(r, None, [])
        self.assertIn("verified unchanged", out)
        self.assertTrue(out.rstrip().endswith("preflight       ok"))


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


class TestPacketAgainstRealGit(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self._git("init", "-q", "-b", "master")
        self._git("config", "user.email", "test@example.invalid")
        self._git("config", "user.name", "test")
        self._git("config", "core.hooksPath", ".githooks")
        (self.repo / "seed").write_text("seed\n", encoding="utf-8")
        self._git("add", "seed")
        self._git("commit", "-qm", "seed")
        self.base = self._git("rev-parse", "HEAD").strip()
        self.remote = self.root / "remote.git"
        self._git("init", "--bare", "-q", str(self.remote))
        self._git("remote", "add", "origin", str(self.remote))
        self._git("push", "-q", "origin", "master")
        self._git("switch", "-q", "-c", "codex/test")
        self.body = {
            "task_id": "packet-test", "branch": "codex/test", "exact_base_sha": self.base,
            "allowed_changed_paths": ["seed"], "required_tests": ["unit"],
            "prohibitions": ["force_push"],
            "publisher": {"expected_remote_master_head": self.base},
        }
        self.packet = self.root / "packet.yml"

    def tearDown(self):
        self._tmp.cleanup()

    def _git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.repo, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode("utf-8")

    def _cli(self, data):
        self.packet.write_text(pf.yaml.safe_dump(data), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(Path(pf.__file__).resolve()), "--packet", str(self.packet),
             "--repo-root", str(self.repo), "--json"],
            cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        return result

    def test_wrapped_and_flat_packets_pass_same_real_git_facts(self):
        for data, expected in (({"task_packet": self.body}, "wrapped_v1"),
                               (self.body, "legacy_flat")):
            with self.subTest(expected=expected):
                result = self._cli(data)
                self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
                report = json.loads(result.stdout)["report"]
                self.assertEqual(report["packet_format"], expected)
                self.assertEqual(report["prohibitions"], ["force_push"])
                self.assertEqual(report["local_head"], self.base)
                self.assertEqual(report["master_verification"], "verified_unchanged")

    def test_publication_expected_head_does_not_verify_master(self):
        self.body["publisher"] = {"expected_remote_head": self.base}
        result = self._cli({"task_packet": self.body})
        self.assertEqual(result.returncode, 1)
        self.assertIn("master_not_verified:no_expectation_declared",
                      json.loads(result.stdout)["hard_failures"])

    def test_missing_fields_fail_before_git_collection(self):
        for field in ("task_id", "branch", "exact_base_sha", "allowed_changed_paths",
                      "required_tests", "prohibitions"):
            data = dict(self.body)
            del data[field]
            with self.subTest(field=field), patch.object(pf, "git") as git_mock:
                with self.assertRaises(pf.PacketInputError):
                    pf.collect(self.repo, {"task_packet": data}, use_remote=True)
                git_mock.assert_not_called()

    def test_invalid_packet_cli_returns_input_error(self):
        for field, value in (("task_id", False), ("exact_base_sha", "HEAD"),
                             ("allowed_changed_paths", []), ("prohibitions", False)):
            data = dict(self.body)
            data[field] = value
            with self.subTest(field=field):
                result = self._cli({"task_packet": data})
                self.assertEqual(result.returncode, 3)
                self.assertIn(b"preflight_error:", result.stderr)
                self.assertNotIn(b"Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()

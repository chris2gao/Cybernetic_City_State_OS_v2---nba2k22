from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "validate.py"
PATTERNS = ROOT / "patterns.json"
FIXTURE = Path(__file__).parent / "fixtures/personal_path_segments.json"
VALIDATOR_SPEC = importlib.util.spec_from_file_location("personal_paths_validate", VALIDATOR)
assert VALIDATOR_SPEC and VALIDATOR_SPEC.loader
VALIDATOR_MODULE = importlib.util.module_from_spec(VALIDATOR_SPEC)
sys.modules[VALIDATOR_SPEC.name] = VALIDATOR_MODULE
VALIDATOR_SPEC.loader.exec_module(VALIDATOR_MODULE)


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


class PersonalPathValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        git(self.repo, "init", "--quiet")
        git(self.repo, "config", "user.email", "validator@example.invalid")
        git(self.repo, "config", "user.name", "Validator Test")
        (self.repo / "clean.txt").write_text("portable evidence\n", encoding="utf-8")
        git(self.repo, "add", "clean.txt")
        git(self.repo, "commit", "--quiet", "-m", "baseline")
        self.base = git(self.repo, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--repo-root",
                str(self.repo),
                "--config",
                str(PATTERNS),
                *args,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def write_negative_fixture(self, relative: str = "evidence.txt") -> str:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        value = "".join(fixture["segments"])
        (self.repo / relative).write_text(f"artifact={value}\n", encoding="utf-8")
        return value

    def write_fixture(self, relative: str, value: str) -> None:
        (self.repo / relative).write_text(f"artifact={value}\n", encoding="utf-8")

    def windows_user_home(self) -> str:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        return "".join(fixture["segments"])

    def test_tracked_clean_returns_zero(self) -> None:
        result = self.invoke("--mode", "tracked")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["hit_count"], 0)

    def test_tracked_negative_fixture_is_reported_with_detail(self) -> None:
        value = self.write_negative_fixture()
        git(self.repo, "add", "evidence.txt")
        result = self.invoke("--mode", "tracked")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("evidence.txt:1:windows_user_home", result.stdout)
        self.assertIn(json.dumps(value)[1:-1], result.stdout)

    def test_changed_mode_detects_staged_fixture_and_summary_hides_value(self) -> None:
        value = self.write_negative_fixture("changed.txt")
        git(self.repo, "add", "changed.txt")
        result = self.invoke("--mode", "changed", "--base", self.base, "--summary-only")
        self.assertEqual(result.returncode, 1, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["hit_files"], 1)
        self.assertEqual(summary["hit_count"], 1)
        self.assertNotIn(value, result.stdout)

    def test_changed_mode_without_base_returns_two(self) -> None:
        result = self.invoke("--mode", "changed")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--base is required", result.stderr)

    def test_escaped_backslash_variant_is_detected(self) -> None:
        value = self.windows_user_home().replace("\\", "\\\\") + "\\x"
        self.write_fixture("escaped.txt", value)
        git(self.repo, "add", "escaped.txt")
        result = self.invoke("--mode", "tracked")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("escaped.txt:1:windows_user_home", result.stdout)

    def test_forward_slash_variant_is_detected(self) -> None:
        value = self.windows_user_home().replace("\\", "/") + "/y"
        self.write_fixture("forward.txt", value)
        git(self.repo, "add", "forward.txt")
        result = self.invoke("--mode", "tracked")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("forward.txt:1:windows_user_home", result.stdout)

    def test_case_insensitive_variant_is_detected(self) -> None:
        value = self.windows_user_home().lower() + "\\z"
        self.write_fixture("case.txt", value)
        git(self.repo, "add", "case.txt")
        result = self.invoke("--mode", "tracked")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("case.txt:1:windows_user_home", result.stdout)

    def test_every_default_pattern_is_detected(self) -> None:
        values = [pattern.literal for pattern in VALIDATOR_MODULE.load_patterns(PATTERNS)]
        (self.repo / "all-patterns.txt").write_text("\n".join(values) + "\n", encoding="utf-8")
        git(self.repo, "add", "all-patterns.txt")
        result = self.invoke("--mode", "tracked", "--summary-only")
        self.assertEqual(result.returncode, 1, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["hit_count"], len(values))


if __name__ == "__main__":
    unittest.main()

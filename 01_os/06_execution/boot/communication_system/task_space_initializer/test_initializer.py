import io
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

try:
    from .initialize_task_space import MANIFEST_FIELDS, initialize, main, resolve_communication_root
except ImportError:
    from initialize_task_space import MANIFEST_FIELDS, initialize, main, resolve_communication_root
import yaml


class InitializerTests(unittest.TestCase):
    def test_root_resolution_precedence(self):
        with TemporaryDirectory() as temp:
            base = Path(temp)
            explicit = base / "explicit"
            environment = base / "environment"
            home = base / "home"
            self.assertEqual(
                resolve_communication_root(
                    explicit,
                    environ={"CITYSTATE_COMMUNICATION_ROOT": str(environment)},
                    home=home,
                ),
                explicit.resolve(),
            )
            self.assertEqual(
                resolve_communication_root(
                    None,
                    environ={"CITYSTATE_COMMUNICATION_ROOT": str(environment)},
                    home=home,
                ),
                environment.resolve(),
            )
            self.assertEqual(
                resolve_communication_root(None, environ={}, home=home),
                (home / ".citystate" / "communication").resolve(),
            )

    def test_cli_root_is_optional_and_environment_is_used(self):
        with TemporaryDirectory() as temp:
            root = Path(temp) / "communication"
            argv = [
                "initialize_task_space.py",
                "--repository-id", "repo",
                "--task-id", "task-001",
                "--task-goal", "goal",
                "--navigation-owner", "owner-01",
                "--privacy-policy-ref", "privacy.yml",
            ]
            with (
                patch.dict(os.environ, {"CITYSTATE_COMMUNICATION_ROOT": str(root)}, clear=False),
                patch("sys.argv", argv),
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(main(), 0)
            self.assertTrue((root / "repo" / "active" / "task-001" / "manifest.yml").is_file())

    def test_create_and_idempotent_reentry(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            task = initialize(root, "repo", "task-001", "goal", "owner-01", "privacy.yml")
            manifest = yaml.safe_load((task / "manifest.yml").read_text(encoding="utf-8"))
            self.assertEqual(set(manifest), MANIFEST_FIELDS)
            self.assertEqual(
                initialize(root, "repo", "task-001", "goal", "owner-01", "privacy.yml"),
                task,
            )

    def test_conflicting_existing_manifest_fails_closed(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            task = initialize(root, "repo", "task-001", "goal", "owner-01", "privacy.yml")
            (task / "manifest.yml").write_text("task_id: wrong\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "existing_artifact_conflict"):
                initialize(root, "repo", "task-001", "goal", "owner-01", "privacy.yml")

    def test_unsafe_identifier_is_rejected(self):
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "invalid_task_id"):
                initialize(Path(temp), "repo", "../escape", "goal", "owner-01", "privacy.yml")


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

try:
    from .initialize_task_space import MANIFEST_FIELDS, initialize
except ImportError:
    from initialize_task_space import MANIFEST_FIELDS, initialize
import yaml


class InitializerTests(unittest.TestCase):
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

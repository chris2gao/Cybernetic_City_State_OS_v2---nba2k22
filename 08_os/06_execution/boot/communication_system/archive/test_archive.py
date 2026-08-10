from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import yaml

try:
    from .archive_task import archive
    from .navigation import resolve_default_context, update_Human_current, validate_discovery
except ImportError:
    from archive_task import archive
    from navigation import resolve_default_context, update_Human_current, validate_discovery

VALIDATOR_ROOT = Path(__file__).resolve().parents[1] / "validator"
import sys
if str(VALIDATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_ROOT))
from validate_communication_system import CommunicationValidationError  # noqa: E402


class ArchiveTests(unittest.TestCase):
    def _prerequisites(self):
        return {
            "completion_pointer_ref": "final_results/result.yml",
            "material_residuals_ref": "material_failures/residuals.yml",
            "private_runtime_policy_ref": "private_runtime_policy.yml",
            "github_copy_required": False,
        }

    def _task(self, base: Path):
        root = base / "repo"
        task = root / "active" / "task-001"
        for name in ("indexes", "messages", "documents", "Human", "final_results", "material_failures"):
            (task / name).mkdir(parents=True, exist_ok=True)
        (task / "final_results/result.yml").write_text("status: complete\n", encoding="utf-8")
        (task / "material_failures/residuals.yml").write_text(
            "material_residuals_recorded: true\n", encoding="utf-8"
        )
        (task / "private_runtime_policy.yml").write_text(
            "private_runtime_not_durable_source: true\n", encoding="utf-8"
        )
        (root / "archive").mkdir()
        (root / "discovery.yml").write_text(yaml.safe_dump({
            "active_task_roots": ["active/task-001/"], "archived_task_roots": [],
        }), encoding="utf-8")
        return root, task

    def test_whole_task_archive_then_private_runtime_delete(self):
        with TemporaryDirectory() as temp:
            base = Path(temp)
            root, _ = self._task(base)
            runtime = base / "private_runtime"
            runtime.mkdir()
            (runtime / "scratch.txt").write_text("scratch", encoding="utf-8")
            result = archive(
                root, "task-001", [runtime],
                durable_prerequisites=self._prerequisites(),
            )
            self.assertTrue((root / "archive/task-001/final_results/result.yml").is_file())
            self.assertFalse(runtime.exists())
            self.assertEqual(len(result["private_runtime_deleted"]), 1)

    def test_archive_is_not_in_default_load(self):
        with TemporaryDirectory() as temp:
            root, _ = self._task(Path(temp))
            archive(root, "task-001", durable_prerequisites=self._prerequisites())
            with self.assertRaisesRegex(CommunicationValidationError, "task_root_missing"):
                resolve_default_context(root, "task-001")
            self.assertTrue(resolve_default_context(root, "task-001", authority="exact_archive_pointer").is_dir())

    def test_discovery_and_Human_current_are_minimal_and_owned(self):
        with self.assertRaisesRegex(CommunicationValidationError, "field_set_invalid"):
            validate_discovery({"active_task_roots": [], "archived_task_roots": [], "message_body": "x"})
        with TemporaryDirectory() as temp:
            current = Path(temp) / "current.yml"
            payload = {
                "task_id": "task-001", "title": "Task", "current_stage_or_checkpoint": "done",
                "important_refs": ["final_results/result.yml"], "pending_Human_decision": None,
                "last_material_update": "stage_completed",
            }
            with self.assertRaisesRegex(CommunicationValidationError, "not_authorized"):
                update_Human_current(current, payload, event_kind="stage_completed",
                                     writer_endpoint_id="other", navigation_owner_endpoint_id="owner",
                                     current_task_id="task-001", writer_task_role="execution",
                                     current_task_authority={
                                         "task_id": "task-001",
                                         "writer_endpoint_id": "other",
                                         "writer_task_role": "execution",
                                         "navigation_owner_endpoint_id": "owner",
                                         "can_write_Human_current": True,
                                     })
            with self.assertRaisesRegex(CommunicationValidationError, "nonmaterial"):
                update_Human_current(current, payload, event_kind="ordinary_message",
                                     writer_endpoint_id="owner", navigation_owner_endpoint_id="owner",
                                     current_task_id="task-001",
                                     writer_task_role="architecture_and_decision",
                                     current_task_authority={
                                         "task_id": "task-001",
                                         "writer_endpoint_id": "owner",
                                         "writer_task_role": "architecture_and_decision",
                                         "navigation_owner_endpoint_id": "owner",
                                         "can_write_Human_current": True,
                                     })
            update_Human_current(current, payload, event_kind="stage_completed",
                                 writer_endpoint_id="owner", navigation_owner_endpoint_id="owner",
                                 current_task_id="task-001",
                                 writer_task_role="architecture_and_decision",
                                 current_task_authority={
                                     "task_id": "task-001",
                                     "writer_endpoint_id": "owner",
                                     "writer_task_role": "architecture_and_decision",
                                     "navigation_owner_endpoint_id": "owner",
                                     "can_write_Human_current": True,
                                 })
            self.assertTrue(current.is_file())
            explicitly_authorized = dict(payload, title="Explicit Human authorization")
            update_Human_current(
                current, explicitly_authorized, event_kind="Human_requests",
                writer_endpoint_id="executor", navigation_owner_endpoint_id="owner",
                current_task_id="task-001", writer_task_role="execution",
                current_task_authority={},
                explicit_Human_authorization={
                    "task_id": "task-001", "writer_endpoint_id": "executor",
                    "writer_task_role": "execution",
                    "authorized_action": "write_Human_current",
                    "can_write_Human_current": True,
                },
            )
            self.assertEqual(yaml.safe_load(current.read_text(encoding="utf-8"))["title"],
                             "Explicit Human authorization")

    def test_missing_durable_prerequisite_blocks_before_move(self):
        with TemporaryDirectory() as temp:
            root, task = self._task(Path(temp))
            prerequisites = self._prerequisites()
            (task / prerequisites["private_runtime_policy_ref"]).write_text(
                "private_runtime_not_durable_source: false\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(CommunicationValidationError, "durable_prerequisite"):
                archive(root, "task-001", durable_prerequisites=prerequisites)
            self.assertTrue(task.is_dir())
            self.assertFalse((root / "archive/task-001").exists())


if __name__ == "__main__":
    unittest.main()

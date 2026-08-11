from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

import yaml

MODULE_ROOT = Path(__file__).resolve().parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))
from republish_github import republish_and_converge  # noqa: E402


ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, env=ENV, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    ).stdout.strip()


def card(endpoint_id: str, role: str, environment: str) -> dict:
    return {
        "endpoint_id": endpoint_id, "principal_class": "model",
        "model_or_product": "test", "environment_class": environment,
        "interface_class": "terminal", "task_role": role,
        "local_file_read": True, "local_file_write": True,
        "GitHub_read": True, "GitHub_write": False,
        "instance_label": endpoint_id, "role_context_entry_ref": f"roles/{role}.md",
    }


class GitHubRepublicationTests(unittest.TestCase):
    def test_material_message_index_are_published_and_pushed_in_order(self):
        with TemporaryDirectory() as temp:
            base = Path(temp)
            remote = base / "remote.git"
            repo = base / "repo"
            readback = base / "readback"
            local = base / "local-task"
            git(base, "init", "--bare", str(remote))
            git(base, "clone", str(remote), str(repo))
            (repo / "README.md").write_text("seed\n", encoding="utf-8")
            git(repo, "add", "README.md")
            git(repo, "branch", "-M", "task")
            git(repo, "commit", "-m", "seed")
            git(repo, "push", "origin", "task")
            for directory in ("endpoints", "roles", "documents/sender-01"):
                (local / directory).mkdir(parents=True, exist_ok=True)
            (local / "manifest.yml").write_text("task_id: task-001\n", encoding="utf-8")
            (local / "endpoints/sender-01.yml").write_text(
                yaml.safe_dump(card("sender-01", "execution", "local")), encoding="utf-8"
            )
            (local / "endpoints/receiver-01.yml").write_text(
                yaml.safe_dump(card("receiver-01", "review", "web_cloud_model")), encoding="utf-8"
            )
            (local / "roles/execution.md").write_text("Execution", encoding="utf-8")
            (local / "roles/review.md").write_text("Review", encoding="utf-8")
            document_ref = "documents/sender-01/evidence.md"
            (local / document_ref).write_text(
                """---
document_id: evidence-001
task_id: task-001
author_endpoint_id: sender-01
author_task_role: execution
purpose: review_evidence
privacy_class: repository_shareable
---
Evidence.
""",
                encoding="utf-8",
            )
            message = {
                "message_id": "task-001::sender-01::00001", "task_id": "task-001",
                "title": "Review", "message_type": "result",
                "sender_endpoint_id": "sender-01", "sender_task_role": "execution",
                "expected_recipient_endpoint_id": "receiver-01",
                "expected_recipient_task_role": "review", "content": "See evidence.",
                "required_refs": [document_ref],
            }
            source = local / "source.yml"
            source.write_text(yaml.safe_dump(message, sort_keys=False), encoding="utf-8")
            task_prefix = "01_os/_communication/core/active/task-001"
            trace = []
            result = republish_and_converge(
                local,
                repo / task_prefix,
                source,
                repository_root=repo,
                branch="task",
                allowed_task_root=task_prefix,
                github_trigger="web_recipient",
                publication_trace=trace,
            )
            git(base, "clone", "--branch", "task", str(remote), str(readback))
            published = readback / task_prefix
            self.assertTrue((published / document_ref).is_file())
            self.assertTrue((published / "messages/sender-01/00001_result.yml").is_file())
            self.assertTrue((published / "indexes/sender-01.yml").is_file())
            material_position = trace.index(f"GitHub_material_published:{document_ref}")
            message_position = next(i for i, event in enumerate(trace) if event.startswith("message_published:"))
            index_position = next(i for i, event in enumerate(trace) if event.startswith("index_updated:"))
            self.assertLess(material_position, message_position)
            self.assertLess(message_position, index_position)
            self.assertEqual(result["convergence"]["push_attempt_count"], 1)
            self.assertEqual(git(repo, "rev-parse", "HEAD"), git(repo, "rev-parse", "origin/task"))


if __name__ == "__main__":
    unittest.main()

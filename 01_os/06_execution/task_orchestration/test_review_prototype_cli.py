"""Read-only universal review CLI tests."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import review_prototype_cli as cli


def example():
    return {
        "schema": cli.SCHEMA,
        "prototype": {
            "key": "build-project",
            "goal": "Real project artifact exists",
            "ready": [{"key": "source", "fact": "source_known",
                       "why": "Correct source", "basis": "Human design"}],
            "done": [{"key": "artifact", "fact": "artifact_observed",
                      "why": "Consumer outcome", "basis": "Result contract"}],
            "children": [{
                "key": "convert",
                "goal": "Converted artifact exists",
                "ready": [{"key": "input", "fact": "input_readable",
                           "why": "Necessary input", "basis": "Tool contract"}],
                "done": [{"key": "output", "fact": "output_exists",
                          "why": "Real output", "basis": "Result contract"}],
                "operation": {
                    "capability_id": "generic.convert", "version": "1.0",
                    "effect": "READ_ONLY", "parameters": ["source"],
                    "why": "Already implemented callable"
                },
                "procedure": [{
                    "key": "invoke", "action": "Call known converter once",
                    "why": "Creates output", "basis": "Existing implementation",
                    "execution_owner": "CAPABILITY_INTERNAL"
                }]
            }]
        }
    }


class UniversalPreview(unittest.TestCase):
    def test_nested_non_game_task_has_reviewable_steps(self):
        packet = cli.review_packet(cli.parse_document(example()))
        self.assertEqual([x["key"] for x in packet], ["build-project", "convert"])
        self.assertEqual(packet[1]["procedure"][0]["action"], "Call known converter once")
        self.assertEqual(packet[1]["status"], "PENDING_HUMAN_REVIEW")

    def test_extra_undeclared_operation_is_rejected(self):
        doc = example()
        doc["prototype"]["children"][0]["operation"]["arbitrary_shell"] = "echo hacked"
        with self.assertRaises(ValueError):
            cli.parse_document(doc)

    def test_cli_only_previews_never_executes_or_approves(self):
        with tempfile.TemporaryDirectory() as path:
            proposal = Path(path) / "input.json"
            proposal.write_text(json.dumps(example()), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = cli.main(["--input", str(proposal)])
            self.assertEqual(rc, 0)
            reply = json.loads(output.getvalue())
            self.assertEqual(reply["status"], "PENDING_HUMAN_REVIEW")
            self.assertEqual(len(reply["nodes"]), 2)

    def test_rejects_missing_schema_and_incomplete_task(self):
        doc = example()
        doc["schema"] = "other"
        with self.assertRaises(ValueError):
            cli.parse_document(doc)
        doc = example()
        doc["prototype"]["children"][0]["done"] = []
        with self.assertRaises(ValueError):
            cli.parse_document(doc)


if __name__ == "__main__":
    unittest.main()

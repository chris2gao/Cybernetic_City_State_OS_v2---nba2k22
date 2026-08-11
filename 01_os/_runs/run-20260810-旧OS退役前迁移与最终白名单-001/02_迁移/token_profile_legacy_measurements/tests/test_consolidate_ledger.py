from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "consolidate_ledger.py"
spec = importlib.util.spec_from_file_location("consolidate_ledger", SCRIPT)
module = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)

def record(**changes):
    value = {key: None for key in module.REQUIRED}
    value.update({"schema_version": "token_profile_run.v1", "task_id": "task", "task_type": "test",
                  "provider": "codex", "model": "test-model", "effort": "medium",
                  "session_mode": "cold", "protocol_profile": "candidate", "repair_attempts": 0,
                  "review_rounds": 0, "validation_result": "pass", "quality_incidents": 0,
                  "metric_source": "unavailable", "input_tokens": 12})
    value.update(changes); return value

class ConsolidateLedgerTests(unittest.TestCase):
    def test_aggregates_valid_records_and_skips_malformed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "one.json").write_text(json.dumps(record()), encoding="utf-8")
            (root / "bad.json").write_text("not-json", encoding="utf-8")
            result = module.aggregate(root)
            self.assertEqual(result["record_count"], 1); self.assertEqual(result["skipped_malformed_files"], 1)
            self.assertEqual(result["sums_non_null"]["input_tokens"], 12)
    def test_rejects_prompt_like_unrecognized_shape(self):
        value = record(); value.pop("task_id"); value["prompt"] = "private body"
        self.assertFalse(module.valid_record(value))
    def test_atomic_write_replaces_output(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "record.json"; module.atomic_write(path, b"{}\n")
            self.assertEqual(path.read_bytes(), b"{}\n")
if __name__ == "__main__": unittest.main()

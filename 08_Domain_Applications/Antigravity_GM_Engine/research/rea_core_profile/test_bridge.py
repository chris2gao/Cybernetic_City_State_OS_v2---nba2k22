import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge


class ProfileTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.profile = json.loads(bridge.PROFILE.read_text(encoding="utf-8"))

    def catalog(self, build=None):
        sha = self.profile["target"]["sha256"]
        data = {
            "action_registry.json": {"game_build_sha256": sha, "actions": [
                {"action_id": "test_live", "capability": "CALL_LOGIC_RECOVERED"},
                {"action_id": "test_static", "capability": "CALL_LOGIC_RECOVERED"},
                {"action_id": "test_pending", "capability": "PARTIAL_BINDING"},
            ]},
            "native_live_validation.json": {"game_build_sha256": build or sha, "actions": {
                "test_live": {"status": "REAL_NATIVE_EFFECT_VERIFIED_SUBSET", "exact_input": {"id": 1}}
            }},
            "native_bindings.json": {"game_build_sha256": sha, "bindings": []},
            "read_catalog.json": {"datasets": []},
        }
        with patch.object(bridge, "git_blob", side_effect=lambda _, __, p: json.dumps(data[p.split("/")[-1]]).encode()):
            return bridge.load_catalog(self.root, self.profile)

    def test_historical_scope_is_exact_and_static_is_distinct(self):
        actions = self.catalog()["actions"]
        self.assertEqual(actions["test_live"]["evidence_level"], "LiveEffectVerified")
        self.assertEqual(actions["test_live"]["historical_example"]["exact_input"], {"id": 1})
        self.assertEqual(actions["test_static"]["evidence_level"], "StaticRecovered")
        self.assertEqual(actions["test_pending"]["evidence_level"], "Pending")
        self.assertTrue(all(row["current_execution"] == "NOT_RUN" for row in actions.values()))

    def test_mismatched_build_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "domain build"):
            self.catalog("0" * 64)

    def receipt(self, **changes):
        raw = b'{"ok":true,"data":{"fixture":true}}'
        (self.root / "result.stdout").write_bytes(raw)
        report = {"schema_version": "citystate.rea.receipt.v1", "status": "VERIFIED_TOOL_CALL", "exit_code": 0,
                  "evidence_scope": "local_tool_only", "authority_effect": "none",
                  "command": "inspect-byte-entropy", "observed_version": "6.8.0",
                  "parameters": {"length": "4096"}, "output": "result.stdout",
                  "source": {"sha256": self.profile["target"]["sha256"]},
                  "raw_files": [{"path": "result.stdout", "size_bytes": len(raw),
                                 "sha256": hashlib.sha256(raw).hexdigest()}]}
        report.update(changes)
        encoded = json.dumps(report).encode()
        (self.root / "receipt.json").write_bytes(encoded)
        (self.root / "domain_invocation.json").write_text(json.dumps({
            "core_commit": self.profile["core"]["commit"], "operation": "invoke",
            "receipt_sha256": hashlib.sha256(encoded).hexdigest(),
        }), encoding="utf-8")

    def test_static_result_does_not_promote_game_effect(self):
        self.receipt()
        result = bridge.verify_static_receipt(self.root, self.profile)
        self.assertEqual(result["status"], "DOMAIN_STATIC_RECEIPT_VERIFIED")
        self.assertEqual(result["current_game_effect"], "NOT_RUN")

    def test_changed_bytes_and_different_operation_are_rejected(self):
        self.receipt()
        (self.root / "result.stdout").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Raw output changed"):
            bridge.verify_static_receipt(self.root, self.profile)
        self.receipt(command="capture-process")
        with self.assertRaisesRegex(ValueError, "Receipt does not bind"):
            bridge.verify_static_receipt(self.root, self.profile)

    def test_wrong_target_and_unbound_core_receipt_are_rejected(self):
        self.receipt(source={"sha256": "0" * 64})
        with self.assertRaises(ValueError):
            bridge.verify_static_receipt(self.root, self.profile)
        self.receipt()
        (self.root / "domain_invocation.json").unlink()
        with self.assertRaises(FileNotFoundError):
            bridge.verify_static_receipt(self.root, self.profile)

    def test_missing_core_reports_pinned_checkout_hint(self):
        with patch.object(bridge, "git_blob", side_effect=FileNotFoundError):
            with self.assertRaisesRegex(FileNotFoundError, "Core tool unavailable"):
                bridge.call_core(self.root, self.profile, self.root / "new", "probe")


if __name__ == "__main__":
    unittest.main()

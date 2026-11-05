"""Exercise the actual subprocess adapter with an isolated protocol fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adapter


FAKE = """import json, sys, time
mode, *args = sys.argv[1:]
def emit(doc): print(json.dumps(doc))
if args == ['--version']:
    print('6.8.0')
elif '--schema' in args:
    emit({'args': {'properties': {'path': {'type': 'string'}}},
          'options': {'properties': {'length': {'type': 'integer'}}}})
elif args[0] == 'capabilities':
    emit({'ok': True, 'data': {'analysis_provider_candidates': [
        {'provider': {'id': 'sample'}, 'availability': {'status': 'unavailable', 'code': 'not_configured'}}]}})
elif mode == 'timeout':
    time.sleep(10)
elif mode == 'large':
    print('x' * 4096)
elif mode == 'malformed':
    print('not JSON')
elif mode in ('permission_denied', 'backend_missing'):
    emit({'ok': False, 'error': {'code': mode}})
    raise SystemExit(7)
else:
    emit({'ok': True, 'data': {'evidence': 'synthetic'}})
"""


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = self.root / "fixture.py"
        self.fixture.write_text(FAKE, encoding="utf-8")
        self.target = self.root / "fixture.exe"
        self.target.write_bytes(b"MZ" + bytes(128))

    def args(self, **changes):
        values = dict(operation="invoke", evidence_dir=self.root / "evidence", launcher=None,
                      expected_version="6.8.0", command="inspect-byte-entropy", artifact=self.target,
                      expected_sha256=None, option=["length=64"], timeout=5, max_output=8192)
        values.update(changes)
        return argparse.Namespace(**values)

    def invoke(self, mode="ok", **changes):
        with patch.object(adapter, "launcher", return_value=[sys.executable, str(self.fixture), mode]):
            return adapter.execute(self.args(**changes))

    def test_result_pins_target_and_raw_output(self):
        report = self.invoke()
        self.assertEqual(report["status"], "VERIFIED_TOOL_CALL")
        self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.target.read_bytes()).hexdigest())
        output = next(row for row in report["raw_files"] if row["path"] == "result.stdout")
        self.assertEqual(output["sha256"], hashlib.sha256((self.root / "evidence/result.stdout").read_bytes()).hexdigest())
        self.assertEqual(report["evidence_scope"], "local_tool_only")

    def test_probe_distinguishes_backend_from_cli(self):
        report = self.invoke(operation="probe")
        self.assertEqual(report["status"], "AVAILABLE_UNVERIFIED")
        self.assertEqual(report["providers"][0]["status"], "unavailable")

    def test_missing_launcher(self):
        self.assertEqual(adapter.execute(self.args(launcher=self.root / "missing.mjs"))["status"], "NOT_INSTALLED")

    def test_wrong_version_never_dispatches(self):
        report = self.invoke(expected_version="1.2.3")
        self.assertEqual(report["status"], "VERSION_MISMATCH")
        self.assertFalse((self.root / "evidence/result.stdout").exists())

    def test_wrong_target_fingerprint_never_dispatches(self):
        self.assertEqual(self.invoke(expected_sha256="a" * 64)["status"], "SOURCE_MISMATCH")
        self.assertFalse((self.root / "evidence/result.stdout").exists())

    def test_live_command_and_arbitrary_option_refused(self):
        self.assertEqual(self.invoke(command="capture-process")["status"], "INVALID_REQUEST")
        self.assertEqual(self.invoke(option=["output_file=elsewhere"], evidence_dir=self.root / "other")["status"], "INVALID_REQUEST")

    def test_timeout_recorded_without_retry(self):
        report = self.invoke("timeout", timeout=2)
        self.assertEqual(report["status"], "TIMEOUT")
        self.assertFalse(report["automatic_replay"])

    def test_oversize_result_and_invalid_json_refused(self):
        self.assertEqual(self.invoke("large", max_output=1024)["status"], "OUTPUT_LIMIT")
        self.assertEqual(self.invoke("malformed", evidence_dir=self.root / "other")["status"], "INVALID_TOOL_OUTPUT")

    def test_backend_and_permission_errors_preserve_exit(self):
        for mode, status in (("permission_denied", "PERMISSION_DENIED"), ("backend_missing", "BACKEND_UNAVAILABLE")):
            with self.subTest(mode=mode):
                report = self.invoke(mode, evidence_dir=self.root / mode)
                self.assertEqual((report["status"], report["exit_code"]), (status, 7))

    def test_reusing_evidence_directory_fails(self):
        self.invoke()
        with self.assertRaises(FileExistsError):
            self.invoke()


if __name__ == "__main__":
    unittest.main()

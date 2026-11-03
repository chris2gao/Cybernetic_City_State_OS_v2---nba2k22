"""Adversarial intake boundaries; no submitted code or native image is executed."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

CONTROL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('aux_screen', CONTROL / 'tools/review_aux_submission.py')
screen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(screen)


class AuxiliaryIntake(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / 'bundle'
        self.sub = self.root / 'submission'
        self.bundle.mkdir()
        self.sub.mkdir()
        self.scope_path = CONTROL / 'auxiliary/gemini_information_20261028/SCOPE.json'
        self.scope = json.loads(self.scope_path.read_text(encoding='utf8'))
        (self.bundle / 'frozen.txt').write_bytes(b'frozen')
        self.manifest = self.root / 'manifest.json'
        self.manifest.write_text(json.dumps({'packet_id': self.scope['packet_id'],
            'target_sha256': self.scope['target_sha256'], 'owner_source_commit': 'a' * 40,
            'files': [{'path': 'frozen.txt', 'bytes': 6, 'sha256': screen.sha(b'frozen')}]}), encoding='utf8')
        (self.bundle / 'INPUT_MANIFEST.json').write_bytes(self.manifest.read_bytes())
        (self.sub / 'raw.json').write_bytes(b'{"static":"test fixture only"}')
        call = {'tool': 'fixture_static_reader', 'operation': 'read_bytes', 'arguments': {'rva': 16},
                'target_sha256': self.scope['target_sha256'], 'provenance': 'OWNER_INPUT_REVIEW',
                'outcome': 'TEST_FIXTURE', 'output_artifact': 'raw.json'}
        (self.sub / 'tool_calls.jsonl').write_text(json.dumps(call) + '\n', encoding='utf8')
        self.obj = {'schema_version': 'nba2k22.auxiliary_submission.v1', 'packet_id': self.scope['packet_id'],
                    'target_sha256': self.scope['target_sha256'], 'owner_source_commit': 'a' * 40,
                    'input_manifest_sha256': screen.sha(self.manifest.read_bytes()),
                    'producer': {'observed_model': 'TEST_FIXTURE', 'subagents_used': False},
                    'status': 'PARTIAL', 'task_results': [{'task_id': task, 'status': 'UNKNOWN', 'reason': 'Fixture'}
                                                       for task in self.scope['task_ids']],
                    'claims': [{'id': 'C1', 'task_id': self.scope['task_ids'][0], 'kind': 'ENUM_TABLE',
                                'statement': 'Test fixture candidate', 'evidence_level': 'STATIC_FACT_CANDIDATE',
                                'provenance': 'OWNER_INPUT_REVIEW', 'source_rvas': [16],
                                'evidence_refs': ['raw.json'], 'coverage_limit': 'Fixture only',
                                'uncertainty': 'No real native fact',
                                'counterexample': {'status': 'NOT_RUN', 'reason': 'Fixture'}}],
                    'tool_trace': 'tool_calls.jsonl', 'artifacts': []}
        self.refresh()

    def refresh(self):
        self.obj['artifacts'] = [{'path': name, 'kind': kind, 'bytes': len((self.sub / name).read_bytes()),
                                  'sha256': screen.sha((self.sub / name).read_bytes())}
                                 for name, kind in [('raw.json', 'raw_tool_output'), ('tool_calls.jsonl', 'call_trace')]]

    def run_review(self):
        (self.sub / 'submission.json').write_text(json.dumps(self.obj), encoding='utf8')
        return screen.review(self.scope_path, self.manifest, self.bundle, self.sub)

    def invalid(self):
        result = self.run_review()
        self.assertEqual(result['status'], 'INVALID_SUBMISSION', result)
        self.assertFalse(result['semantic_acceptance'])

    def test_ready_means_triage_only(self):
        result = self.run_review()
        self.assertEqual(result['status'], 'READY_FOR_CODEX_TRIAGE')
        self.assertFalse(result['semantic_acceptance'])
        self.assertFalse(result['submitted_code_executed'])
        self.assertIn('MISSING_NEGATIVE_CONTROL', [x['hint'] for x in result['triage_hints']])

    def test_input_tamper(self):
        (self.bundle / 'frozen.txt').write_bytes(b'changed')
        self.invalid()

    def test_artifact_tamper(self):
        (self.sub / 'raw.json').write_bytes(b'changed')
        self.invalid()

    def test_bundle_manifest_tamper(self):
        (self.bundle / 'INPUT_MANIFEST.json').write_bytes(b'{}')
        self.invalid()

    def test_path_escape(self):
        self.obj['artifacts'][0]['path'] = '../outside.json'
        self.invalid()

    def test_unlisted_file(self):
        (self.sub / 'unlisted.py').write_text('raise Exception()', encoding='utf8')
        self.invalid()

    def test_duplicate_json_keys(self):
        self.run_review()
        path = self.sub / 'submission.json'
        path.write_text('{"packet_id":1,"packet_id":2}', encoding='utf8')
        result = screen.review(self.scope_path, self.manifest, self.bundle, self.sub)
        self.assertIn('Duplicate JSON', result['errors'][0])

    def test_wrong_target(self):
        self.obj['target_sha256'] = '0' * 64
        self.invalid()

    def test_wrong_packet(self):
        self.obj['packet_id'] = 'OTHER'
        self.invalid()

    def test_unsupported_maturity(self):
        self.obj['claims'][0]['evidence_level'] = 'LIVE_ACCEPTED'
        self.invalid()

    def test_no_trace(self):
        self.obj['tool_trace'] = 'missing.jsonl'
        self.invalid()

    def test_forbidden_operation(self):
        path = self.sub / 'tool_calls.jsonl'
        value = json.loads(path.read_text(encoding='utf8'))
        value['operation'] = 'attach_target'
        path.write_text(json.dumps(value), encoding='utf8')
        self.refresh()
        self.invalid()

    def test_submitted_python_never_executes(self):
        sentinel = self.root / 'EXECUTED'
        raw = ('from pathlib import Path\nPath(' + repr(str(sentinel)) + ').write_text("bad")\n').encode()
        (self.sub / 'reproducer.py').write_bytes(raw)
        self.obj['artifacts'].append({'path': 'reproducer.py', 'kind': 'reproducer', 'bytes': len(raw), 'sha256': screen.sha(raw)})
        self.assertEqual(self.run_review()['status'], 'READY_FOR_CODEX_TRIAGE')
        self.assertFalse(sentinel.exists())

    def test_symlink_or_reparse_rejected(self):
        path = self.sub / 'link.txt'
        try:
            path.symlink_to(self.bundle / 'frozen.txt')
        except OSError:
            # Windows may forbid creating symlinks; exercise the same lstat reparse branch.
            from unittest.mock import patch
            original = Path.lstat
            def flagged(target, *args, **kwargs):
                if target == self.sub / 'raw.json':
                    class Reparse:
                        st_file_attributes = 0x400
                    return Reparse()
                return original(target, *args, **kwargs)
            with patch.object(Path, 'lstat', flagged):
                self.invalid()
        else:
            self.invalid()

    def test_nonfinite_json_rejected(self):
        (self.sub / 'tool_calls.jsonl').write_text('{"value":NaN}', encoding='utf8')
        self.refresh()
        self.invalid()


if __name__ == '__main__':
    unittest.main()

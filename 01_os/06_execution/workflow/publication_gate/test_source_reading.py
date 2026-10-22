"""Real-Git source probes, not complete workflow or independent acceptance."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_publication_gate import Chain, RUN, STAGES, commit, discard, git, write

SPEC = importlib.util.spec_from_file_location(
    "source_gate_subject", Path(__file__).with_name("workflow_publication_gate.py"))
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


class SourceReadingCases(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="gate-source-"))
        git(self.repo, "init", "-b", "fixture")
        git(self.repo, "config", "user.name", "Synthetic source fixture")
        git(self.repo, "config", "user.email", "source@example.invalid")
        write(self.repo, "record.yml", {"status": "verified"})
        self.head = commit(self.repo, "regular source")

    def tearDown(self):
        discard(self.repo)

    def test_regular_file_and_true_absence(self):
        self.assertEqual(gate._load_yaml_at(self.repo, self.head, "record.yml"), {"status": "verified"})
        self.assertIsNone(gate._blob_at(self.repo, self.head, "absent.yml"))

    def test_git_read_failure_is_not_absence(self):
        with self.assertRaises(gate.GateError) as caught:
            gate._blob_at(self.repo, "0" * 40, "record.yml")
        self.assertEqual(caught.exception.code, gate.REPO)

    def test_symlink_mode_is_not_a_regular_yaml_source(self):
        blob = git(self.repo, "rev-parse", f"{self.head}:record.yml")
        git(self.repo, "update-index", "--cacheinfo", f"120000,{blob},record.yml")
        git(self.repo, "commit", "-m", "synthetic link mode")
        candidate = git(self.repo, "rev-parse", "HEAD")
        with self.assertRaises(gate.GateError) as caught:
            gate._load_yaml_at(self.repo, candidate, "record.yml")
        self.assertEqual(caught.exception.code, gate.REF)

    def test_duplicate_explicit_yaml_key_is_not_last_value_wins(self):
        write(self.repo, "record.yml", "status: rejected\nstatus: verified\n")
        candidate = commit(self.repo, "ambiguous source")
        with self.assertRaises(gate.GateError) as caught:
            gate._load_yaml_at(self.repo, candidate, "record.yml")
        self.assertEqual(caught.exception.code, gate.REF)

    def test_legal_yaml_merge_is_preserved(self):
        write(self.repo, "record.yml", "defaults: &d {status: planned}\nrecord: {<<: *d, status: verified}\n")
        candidate = commit(self.repo, "legal merge")
        self.assertEqual(gate._load_yaml_at(self.repo, candidate, "record.yml")["record"],
                         {"status": "verified"})

    def test_yaml_cycle_is_refused(self):
        write(self.repo, "record.yml", "record: &r {self: *r}\n")
        candidate = commit(self.repo, "cyclic source")
        with self.assertRaises(gate.GateError) as caught:
            gate._load_yaml_at(self.repo, candidate, "record.yml")
        self.assertEqual(caught.exception.code, gate.REF)


class PublishedSourceCases(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gate-published-source-"))

    def tearDown(self):
        discard(self.tmp)

    def test_receipt_symlink_mode_refused_by_real_cli(self):
        chain = Chain(self.tmp)
        path = f"{RUN}/{STAGES[0]}/receipt.yml"
        blob = git(chain.repo, "rev-parse", f"{chain.head}:{path}")
        git(chain.repo, "update-index", "--cacheinfo", f"120000,{blob},{path}")
        git(chain.repo, "commit", "-m", "synthetic receipt link")
        chain.head = git(chain.repo, "rev-parse", "HEAD")
        code, findings = chain.run_gate()
        self.assertEqual(code, gate.REF, findings)
        self.assertIn("regular_git_blob_required", " | ".join(findings))

    def test_duplicate_manifest_key_refused_by_real_cli(self):
        chain = Chain(self.tmp)
        path = f"{RUN}/manifest.yml"
        raw = (chain.repo / path).read_text(encoding="utf-8")
        write(chain.repo, path, "artifacts: []\n" + raw)
        chain.head = commit(chain.repo, "ambiguous manifest")
        code, findings = chain.run_gate()
        self.assertEqual(code, gate.REF, findings)
        self.assertIn("unreadable:", " | ".join(findings))


if __name__ == "__main__":
    unittest.main()

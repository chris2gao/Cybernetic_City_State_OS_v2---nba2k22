"""Real committed-run inputs, not an owner stub or a structural-only positive."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import yaml
import test_minimum_operational_loop as structural_fixture

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SPEC = importlib.util.spec_from_file_location(
    "committed_gate_fixture", HERE.parent / "publication_gate/test_publication_gate.py")
gate_fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate_fixture)
loop = structural_fixture.loop


def full_chain(folder, completion_mutators=None):
    chain = gate_fixture.Chain(folder, completion_mutators=completion_mutators)
    # Contract and schema bytes are source inputs. No production validation helper
    # builds the expected result. Fabricated approvals remain in this temp repo.
    contract = structural_fixture.load(ROOT / loop.CONTRACT_PATH)
    paths = [loop.CONTRACT_PATH] + [stage["schema_path"] for stage in contract["stage_order"]]
    for rel in paths:
        gate_fixture.write(chain.repo, rel, (ROOT / rel).read_text(encoding="utf-8"))
    run_root = chain.repo / gate_fixture.RUN
    manifest = structural_fixture.load(structural_fixture.FIXTURE / "manifest.yml")
    for entry in manifest["artifacts"]:
        sid = entry["stage_id"]
        doc = structural_fixture.load(structural_fixture.FIXTURE / entry["path"])
        doc["stage_control"] = chain.controls[sid]
        doc["deliberation_receipt"] = chain.embedded[sid]
        structural_fixture.save(run_root / entry["path"], doc)
    structural_fixture.save(run_root / "manifest.yml", manifest)
    # The test's rebind helper recomputes only byte digests and declared input refs.
    structural_fixture.rebind(run_root)
    chain.head = gate_fixture.commit(chain.repo, "complete structural artifacts for committed run")
    return chain


class CommittedRunCases(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="codex-committed-loop-"))

    def tearDown(self):
        gate_fixture.discard(self.tmp)

    def test_complete_committed_run_passes(self):
        chain = full_chain(self.tmp)
        self.assertEqual(loop.validate_structure(chain.repo / gate_fixture.RUN, chain.repo)[0], 0)
        self.assertEqual(chain.run_gate()[0], 0)
        code, findings = loop.validate_run(chain.repo / gate_fixture.RUN, chain.repo, chain.head)
        self.assertEqual(code, 0, findings)
        self.assertFalse(any("not_validated" in line for line in findings), findings)

    def test_dirty_worktree_cannot_change_the_committed_verdict(self):
        chain = full_chain(self.tmp)
        path = chain.repo / gate_fixture.RUN / gate_fixture.FILES[0]
        path.write_text("not the committed artifact\n", encoding="utf-8")
        code, findings = loop.validate_run(chain.repo / gate_fixture.RUN, chain.repo, chain.head)
        self.assertEqual(code, 0, findings)

    def test_owner_refusal_reaches_full_runner(self):
        chain = full_chain(self.tmp, completion_mutators={
            gate_fixture.STAGES[0]: lambda record, _: record.pop("actual_result")})
        code, findings = loop.validate_run(chain.repo / gate_fixture.RUN, chain.repo, chain.head)
        self.assertEqual(code, 34, findings)
        self.assertIn("actual_result_required", " | ".join(findings))
        self.assertIn("publication_gate_exit_17", " | ".join(findings))

    def test_candidate_cannot_supply_the_judge(self):
        chain = full_chain(self.tmp)
        gate_fixture.write(chain.repo, loop.DELIBERATION_VALIDATOR,
                           "raise RuntimeError('candidate supplied judge was executed')\n")
        chain.head = gate_fixture.commit(chain.repo, "candidate supplied judge is data only")
        code, findings = loop.validate_run(chain.repo / gate_fixture.RUN, chain.repo, chain.head)
        self.assertEqual(code, 0, findings)

    def test_committed_schema_symlink_is_a_source_failure(self):
        chain = full_chain(self.tmp)
        oid = gate_fixture.git(chain.repo, "rev-parse", f"HEAD:{loop.CONTRACT_PATH}")
        gate_fixture.git(chain.repo, "update-index", "--cacheinfo", f"120000,{oid},{loop.CONTRACT_PATH}")
        gate_fixture.git(chain.repo, "commit", "-m", "schema bytes in a symlink entry")
        head = gate_fixture.git(chain.repo, "rev-parse", "HEAD")
        code, findings = loop.validate_run(chain.repo / gate_fixture.RUN, chain.repo, head)
        self.assertEqual(code, 33, findings)
        self.assertIn("source_regular_blob_required", " | ".join(findings))

    def test_committed_bad_payload_is_not_repaired_by_a_dirty_good_copy(self):
        chain = full_chain(self.tmp)
        run_root = chain.repo / gate_fixture.RUN
        path = run_root / gate_fixture.FILES[0]
        good = path.read_bytes()
        doc = yaml.safe_load(good)
        del doc["payload"]["success_criteria"]
        structural_fixture.save(path, doc)
        structural_fixture.rebind(run_root)
        bad = gate_fixture.commit(chain.repo, "committed missing required payload")
        path.write_bytes(good)
        structural_fixture.rebind(run_root)
        code, findings = loop.validate_run(run_root, chain.repo, bad)
        self.assertEqual(code, 33, findings)
        self.assertIn("payload_required", " | ".join(findings))


if __name__ == "__main__":
    unittest.main()

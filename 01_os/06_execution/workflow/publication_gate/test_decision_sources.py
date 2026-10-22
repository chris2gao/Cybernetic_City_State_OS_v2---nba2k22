"""Synthetic exact decision sources through the real gate; no Human authentication."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_publication_gate import Chain, RUN, STAGES, STAGE_FIELDS, TASK_ID, discard, write


class DecisionSourceCases(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gate-decision-"))

    def tearDown(self):
        discard(self.tmp)

    def chain(self, *, unknown=False, stale=False, label_only=False, string_flag=False):
        def model(doc, chain):
            action = chain.packet["stage_actions"][0]
            decision = {"actor_class": "current_Human", "kind": "explicit_statement",
                        "decision_id": "decision-1", "task_id": TASK_ID,
                        "exact_base_sha": chain.boundary, "stale": stale, "revoked": False}
            for field in ("action_id", "target", "expected_target_head", "stage_ids", "paths"):
                decision[field] = action[field]
            path = f"{RUN}/decision.yml"
            basis = {"kind": "explicit_statement", "decision_id": "decision-1",
                     "source_ref": {"path": path, "blob_sha": write(chain.repo, path, decision)}}
            if label_only:
                basis = {"actor_class": "current_Human", "kind": "explicit_statement"}
            if unknown:
                item = {
                    "disposition": "unknown_with_blocking_or_deferred_disposition_and_revisit_trigger",
                    "blocking": False, "deferral": "deferred_nonblocking",
                    "reason_and_scope": "Synthetic uncertainty scoped to a future optional input.",
                    "revisit_trigger": "Input becomes available.", "load_bearing": False,
                    "Human_decision_boundary": True,
                    "downstream_impact_assessment": {
                        field: False for field in ("stage_objective_blocked", "decision_blocked",
                                                   "verification_blocked", "authority_blocked",
                                                   "downstream_acceptance_blocked")},
                    "decision_id": "decision-1", "Human_basis": basis}
                doc["stage_specific_model_elements"][STAGE_FIELDS[STAGES[0]][0]] = item
            else:
                doc["open_load_bearing_items"] = [{
                    "load_bearing": "true" if string_flag else True, "disposition": "resolved",
                    "decision_id": "decision-1", "Human_basis": basis}]
        return Chain(self.tmp, model_mutators={STAGES[0]: model})

    def refused(self, chain, reason):
        code, findings = chain.run_gate()
        self.assertEqual(code, 17, findings)
        self.assertIn(reason, " | ".join(findings))
        self.assertIn("plan", " | ".join(findings))

    def test_exact_explicit_source_passes(self):
        code, findings = self.chain().run_gate()
        self.assertEqual(code, 0, findings)

    def test_stale_explicit_source_is_refused(self):
        self.refused(self.chain(stale=True), "decision_source_mismatch")

    def test_bound_unknown_deferral_passes(self):
        code, findings = self.chain(unknown=True).run_gate()
        self.assertEqual(code, 0, findings)

    def test_unknown_deferral_actor_label_is_insufficient(self):
        self.refused(self.chain(unknown=True, label_only=True), "decision_identity_mismatch")

    def test_load_bearing_flag_requires_boolean(self):
        self.refused(self.chain(string_flag=True), "boolean_required:load_bearing")


if __name__ == "__main__":
    unittest.main()

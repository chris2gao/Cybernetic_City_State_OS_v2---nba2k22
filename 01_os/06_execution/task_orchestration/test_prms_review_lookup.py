"""R4 read-only PRMS provenance boundary: no invented Human approvals."""
from pathlib import Path
import hashlib
import json
import tempfile
import unittest

from prms_review_lookup import PRMSReviewLookup, SCHEMA
from reviewed_prototypes import (
    Capability, Criterion, NeedsHumanReview, Operation, Prototype,
    compile_approved, digest,
)


class PRMSReviewLookupTests(unittest.TestCase):
    def setUp(self):
        self.scope = "OS-CORE-TEST-PRMS-REVIEW"
        self.node = Prototype(
            "readonly", "Produce one observable answer",
            (Criterion("ready", "ready", "Existing source known", "reviewed record"),),
            (Criterion("done", "done", "Consumer result observed", "reviewed record"),),
            Operation("demo.read", "v1", "READ_ONLY", ("source",),
                      "Run existing read callable once"),
            procedure=(),
        )
        # R1 documented mature capability option (the document is a test fixture).
        from dataclasses import replace
        self.node = replace(self.node, operation=replace(
            self.node.operation,
            procedure_ref="fixture://mature-tool-document@0000000000000000000000000000000000000000"))
        self.fixture_approval_text = (
            "Human explicitly approved the exact prototype \n"
            f"key: {self.node.key}\n"
            f"digest: {digest(self.node)}\n"
            f"scope: {self.scope}\n"
        )

    def _write_receipt(self, root, *, mutate=None):
        path = Path(root) / "HUMAN_PROTOTYPE_APPROVAL.md"
        path.write_text(self.fixture_approval_text, encoding="utf-8")
        review = {
            "prototype_key": self.node.key,
            "prototype_digest": digest(self.node),
            "decision": "APPROVED",
            "decision_ref": "fixture:explicit-human-review",
            "source_file": path.name,
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        if mutate:
            review.update(mutate)
        manifest = {
            "schema": SCHEMA,
            "task_scope": self.scope,
            "reviews": [review],
        }
        (Path(root) / "HUMAN_PROTOTYPE_REVIEWS.json").write_text(
            json.dumps(manifest), encoding="utf-8")
        return path

    def _lookup(self, root, *, scope=None, verify=None):
        if verify is None:
            def verify(path, key, sha):
                return (key == self.node.key and sha == digest(self.node)
                        and f"digest: {sha}" in path.read_text(encoding="utf-8")
                        and "Human explicitly approved" in path.read_text(encoding="utf-8"))
        return PRMSReviewLookup(Path(root), scope or self.scope, verify)

    def test_exact_source_and_scope_bind_to_compiler_and_business_done(self):
        # This is a FIXTURE proving that binding works. It is NOT real Human signoff.
        with tempfile.TemporaryDirectory() as root:
            self._write_receipt(root)
            lookup = self._lookup(root)
            approval = lookup(self.node.key, digest(self.node))
            self.assertIsNotNone(approval)
            facts = {"ready": True, "done": False}
            calls = []
            def action(source):
                calls.append(source)
                facts["done"] = True
            compiled = compile_approved(
                self.node, review_lookup=lookup,
                capabilities={"demo.read": Capability(
                    "demo.read", "v1", "READ_ONLY", action,
                    procedure_ref=self.node.operation.procedure_ref)},
                bindings={"source": "example"},
                read_fact=lambda fact, args: facts[fact])
            self.assertEqual(compiled.run_available()[-1].status, "DONE")
            self.assertEqual(calls, ["example"])

    def test_architecture_human_decision_is_not_specific_prototype_approval(self):
        # REAL Core PRMS Human decision, read-only. It approves mode semantics,
        # not an exact task prototype digest; it must not be promoted.
        core_os = Path(__file__).resolve().parents[2]
        run = core_os / "_runs" / "run-20261116-human-reviewed-atomic-prototypes-001"
        source = run / "HUMAN_DECISION_MODE_SEPARATION.md"
        self.assertTrue(source.is_file(), "Existing actual PRMS decision must be present")
        self.assertIn("Human", source.read_text(encoding="utf-8"))
        self.assertIsNone(self._lookup(run)(self.node.key, digest(self.node)))

    def test_no_manifest_bare_true_or_wrong_scope_does_not_approve(self):
        with tempfile.TemporaryDirectory() as root:
            self._write_receipt(root)
            self.assertIsNone(self._lookup(root, scope="different")(
                self.node.key, digest(self.node)))
            self.assertIsNone(self._lookup(root, verify=lambda *args: False)(
                self.node.key, digest(self.node)))
            path = Path(root) / "HUMAN_PROTOTYPE_APPROVAL.md"
            path.write_text("Agent wrote approved=True", encoding="utf-8")
            self.assertIsNone(self._lookup(root)(self.node.key, digest(self.node)))
            self.assertIsNone(self._lookup(root)(self.node.key, "a" * 64))

    def test_unsafe_reference_duplicate_and_rejected_review_are_ignored(self):
        with tempfile.TemporaryDirectory() as root:
            self._write_receipt(root)
            manifest = Path(root) / "HUMAN_PROTOTYPE_REVIEWS.json"
            obj = json.loads(manifest.read_text(encoding="utf-8"))
            obj["reviews"][0]["source_file"] = "../other/approval.md"
            manifest.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIsNone(self._lookup(root)(self.node.key, digest(self.node)))
            self._write_receipt(root, mutate={"decision": "REJECTED"})
            self.assertIsNone(self._lookup(root)(self.node.key, digest(self.node)))
            self._write_receipt(root)
            obj = json.loads(manifest.read_text(encoding="utf-8"))
            obj["reviews"].append(dict(obj["reviews"][0]))
            manifest.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIsNone(self._lookup(root)(self.node.key, digest(self.node)))

    def test_wrong_documentation_or_missing_human_source_does_not_execute(self):
        with tempfile.TemporaryDirectory() as root:
            self._write_receipt(root)
            lookup = self._lookup(root, verify=lambda path, key, sha: False)
            called = []
            with self.assertRaises(NeedsHumanReview):
                compile_approved(
                    self.node, review_lookup=lookup,
                    capabilities={"demo.read": Capability(
                        "demo.read", "v1", "READ_ONLY", lambda source: called.append(source),
                        procedure_ref=self.node.operation.procedure_ref)},
                    bindings={"source": "example"}, read_fact=lambda name, args: True)
            self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()

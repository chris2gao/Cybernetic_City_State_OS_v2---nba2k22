"""Offline behavioral tests. No game, shell, network or Native calls."""
import unittest

# Stable catalog documentation is a TEST FIXTURE; it is not a Human approval.
FIXTURE_PROCEDURE_REF = "fixture://known-procedure@0000000000000000000000000000000000000000"

from reviewed_prototypes import (
    Capability, CapabilityGap, Criterion, HumanReview, NeedsHumanReview,
    Operation, ProcedureStep, Prototype, compile_approved, digest, review_packet,
)



def check(key, fact):
    return Criterion(key, fact, f"Why {key} is necessary", "fixture-evidence")


def capture():
    return Prototype(
        "capture", "Read one bound source unit",
        (check("identity", "save_bound"), check("source", "readable")),
        (check("receipt", "captured"),),
        Operation("worlddata.capture", "v1", "READ_ONLY", ("save",), "Reuse existing capture", procedure_ref=FIXTURE_PROCEDURE_REF),
    )


def reviews_for(root):
    return {node["key"]: HumanReview(node["key"], node["digest"],
                                     f"human-reviewed-{node['key']}", True)
            for node in review_packet(root)}


def compile_fixture(root, review_map, catalog, facts, bindings=None, authorize=None):
    return compile_approved(
        root, review_lookup=lambda key, sha: review_map.get(key),
        capabilities=catalog,
        bindings=bindings or {"save": "MyLEAGUE-test"},
        read_fact=lambda key, params: facts[key],
        authorize_write=authorize,
    )


class ReviewedPrototypeTests(unittest.TestCase):
    def test_review_packet_exposes_every_step_and_reason_before_execution(self):
        packet = review_packet(capture())
        self.assertEqual(len(packet), 1)
        self.assertEqual([x["key"] for x in packet[0]["ready"]], ["identity", "source"])
        self.assertEqual(packet[0]["action"]["parameters"], ("save",))
        self.assertTrue(all(x["why"] and x["basis"] for x in packet[0]["done"]))
        self.assertEqual(packet[0]["status"], "PENDING_HUMAN_REVIEW")

    def test_human_can_review_and_remove_unneeded_procedure_steps(self):
        base = capture()
        needed = ProcedureStep("call", "Invoke pinned existing capability",
                               "Produces the actual source data", "existing-tool-doc",
                               "CAPABILITY_INTERNAL")
        excessive = ProcedureStep("repeat", "Run a second full source scan",
                                  "Hypothetical caution", "unsupported-assumption",
                                  "HOST_BINDING")
        before = Prototype(base.key, base.goal, base.ready, base.done,
                           base.operation, procedure=(needed, excessive))
        proposed = review_packet(before)[0]
        self.assertEqual(len(proposed["procedure"]), 2)
        self.assertEqual(proposed["procedure"][1]["execution_owner"], "HOST_BINDING")
        after = Prototype(base.key, base.goal, base.ready, base.done,
                          base.operation, procedure=(needed,))
        self.assertNotEqual(digest(before), digest(after))
        approvals = reviews_for(before)
        with self.assertRaises(NeedsHumanReview):
            compile_fixture(after, approvals, {}, {})
        # Human reviewing the revised prototype is distinct from runtime dispatch.
        self.assertEqual(len(review_packet(after)[0]["procedure"]), 1)

    def test_invalid_procedure_metadata_refused_before_execution(self):
        base = capture()
        invalid = ProcedureStep("x", "step", "reason", "basis", "FREE_SHELL")
        proposed = Prototype(base.key, base.goal, base.ready, base.done,
                             base.operation, procedure=(invalid,))
        with self.assertRaises(ValueError):
            review_packet(proposed)

    def test_missing_or_fabricated_review_cannot_run(self):
        calls = []
        root = capture()
        cap = {"worlddata.capture": Capability("worlddata.capture", "v1", "READ_ONLY",
                                                 lambda **kwargs: calls.append(kwargs), procedure_ref=FIXTURE_PROCEDURE_REF)}
        with self.assertRaises(NeedsHumanReview):
            compile_fixture(root, {}, cap, {"save_bound": True, "readable": True, "captured": False})
        forged = {"capture": HumanReview("capture", "0" * 64, "model-says-approved", True)}
        with self.assertRaises(NeedsHumanReview):
            compile_fixture(root, forged, cap, {"save_bound": True, "readable": True, "captured": False})
        self.assertEqual(calls, [])

    def test_approved_capture_reused_in_two_instances_without_replanning(self):
        calls = []
        root = capture()
        grant = reviews_for(root)
        for filename in ("MyLEAGUE0005", "MyLEAGUE0006"):
            facts = {"save_bound": True, "readable": True, "captured": False}
            def run(save, state=facts):
                calls.append(save)
                state["captured"] = True
            cat = {"worlddata.capture": Capability("worlddata.capture", "v1", "READ_ONLY", run, procedure_ref=FIXTURE_PROCEDURE_REF)}
            e = compile_fixture(root, grant, cat, facts, {"save": filename})
            self.assertEqual(e.inspect().status, "READY")
            self.assertEqual(e.advance().status, "ADVANCED")
            self.assertEqual(e.advance().status, "DONE")
        self.assertEqual(calls, ["MyLEAGUE0005", "MyLEAGUE0006"])

    def test_no_extra_ready_checks_are_added_at_runtime(self):
        root = capture()
        facts = {"save_bound": True, "readable": True, "captured": False}
        calls = []
        def run(save):
            calls.append(save)
            facts["captured"] = True
        e = compile_fixture(root, reviews_for(root),
                            {"worlddata.capture": Capability("worlddata.capture", "v1", "READ_ONLY", run, procedure_ref=FIXTURE_PROCEDURE_REF)},
                            facts)
        self.assertEqual(e.run_available()[-1].status, "DONE")
        self.assertEqual(len(calls), 1)

    def test_added_check_or_changed_action_invalidates_original_review(self):
        root = capture()
        grant = reviews_for(root)
        extra = Prototype(root.key, root.goal, root.ready + (check("invented", "extra"),),
                          root.done, root.operation)
        changed = Prototype(root.key, root.goal, root.ready, root.done,
                            Operation("worlddata.capture", "v2", "READ_ONLY", ("save",),
                                      "new callable", procedure_ref=FIXTURE_PROCEDURE_REF))
        for candidate in (extra, changed):
            self.assertNotEqual(digest(candidate), digest(root))
            with self.subTest(candidate=candidate), self.assertRaises(NeedsHumanReview):
                compile_fixture(candidate, grant, {}, {})

    def test_missing_or_changed_capability_cannot_fall_back_to_script(self):
        root = capture()
        for cap in ({}, {"worlddata.capture": Capability("worlddata.capture", "v2",
                                                          "READ_ONLY", lambda **kw: None, procedure_ref=FIXTURE_PROCEDURE_REF)},
                    {"worlddata.capture": Capability("worlddata.capture", "v1",
                                                          "WRITE", lambda **kw: None, procedure_ref=FIXTURE_PROCEDURE_REF)}):
            with self.subTest(cap=cap), self.assertRaises(CapabilityGap):
                compile_fixture(root, reviews_for(root), cap, {})

    def test_ready_block_and_done_only_from_real_fact(self):
        facts = {"save_bound": False, "readable": True, "captured": False}
        calls = []
        def run(save):
            calls.append(save)  # Does NOT set captured: return success is not Done.
        root = capture()
        e = compile_fixture(root, reviews_for(root),
                            {"worlddata.capture": Capability("worlddata.capture", "v1", "READ_ONLY", run, procedure_ref=FIXTURE_PROCEDURE_REF)},
                            facts)
        self.assertEqual(e.advance().status, "BLOCKED")
        self.assertEqual(calls, [])
        facts["save_bound"] = True
        self.assertEqual(e.advance().status, "NOT_DONE")
        self.assertEqual(e.advance().status, "RECONCILE")
        self.assertEqual(len(calls), 1)

    def test_composed_parent_requires_both_review_and_own_done(self):
        sub = capture()
        parent = Prototype("research", "Actual study observations",
                           (check("authorized-domain", "domain_ok"),),
                           (check("study-done", "study_result"),), children=(sub,))
        grant = reviews_for(parent)
        facts = {"domain_ok": True, "save_bound": True, "readable": True,
                 "captured": False, "study_result": False}
        def run(save):
            facts["captured"] = True
        cat = {"worlddata.capture": Capability("worlddata.capture", "v1", "READ_ONLY", run, procedure_ref=FIXTURE_PROCEDURE_REF)}
        no_child = {"research": grant["research"]}
        with self.assertRaises(NeedsHumanReview):
            compile_fixture(parent, no_child, cat, facts)
        e = compile_fixture(parent, grant, cat, facts)
        self.assertEqual(e.advance().status, "ADVANCED")
        self.assertEqual(e.inspect().status, "PARENT_INCOMPLETE")
        facts["study_result"] = True
        self.assertEqual(e.inspect().status, "DONE")

    def test_unbound_extra_host_action_cannot_be_executed(self):
        base = capture()
        additional = ProcedureStep(
            "probe", "Repeat external preflight", "A supposed improvement",
            "proposal-only", "HOST_BINDING", "unregistered.probe")
        candidate = Prototype(base.key, base.goal, base.ready, base.done,
                              base.operation, procedure=(additional,))
        self.assertEqual(review_packet(candidate)[0]["procedure"][0]["action"],
                         "Repeat external preflight")
        calls = []
        caps = {"worlddata.capture": Capability(
            "worlddata.capture", "v1", "READ_ONLY", lambda **kwargs: calls.append(kwargs), procedure_ref=FIXTURE_PROCEDURE_REF)}
        with self.assertRaises(CapabilityGap):
            compile_fixture(candidate, reviews_for(candidate), caps,
                            {"save_bound": True, "readable": True, "captured": False})
        self.assertEqual(calls, [])

    def test_composite_procedure_must_follow_actual_children(self):
        sub = capture()
        parent = Prototype("research", "A real final output",
                           (check("start", "start_ok"),),
                           (check("result", "study_result"),), children=(sub,),
                           procedure=(ProcedureStep(
                               "call-child", "Invoke capture", "Business dependency",
                               "reviewed design", "HOST_BINDING", "capture"),))
        facts = {"start_ok": True, "study_result": False, "save_bound": True,
                 "readable": True, "captured": False}
        calls = []
        def captured(save):
            calls.append(save)
            facts["captured"] = True
        cat = {"worlddata.capture": Capability(
            "worlddata.capture", "v1", "READ_ONLY", captured, procedure_ref=FIXTURE_PROCEDURE_REF)}
        valid = compile_fixture(parent, reviews_for(parent), cat, facts)
        self.assertEqual(valid.advance().status, "ADVANCED")
        self.assertEqual(calls, ["MyLEAGUE-test"])
        bogus = Prototype(parent.key, parent.goal, parent.ready, parent.done,
                          children=(sub,), procedure=(ProcedureStep(
                              "other", "Run an unrelated shell check", "Additional",
                              "proposal-only", "HOST_BINDING", "unrelated"),))
        with self.assertRaises(CapabilityGap):
            compile_fixture(bogus, reviews_for(bogus), cat, facts)

    def test_child_change_only_needs_local_re_review(self):
        sub = capture()
        parent = Prototype("research", "Real completed study",
                           (check("start", "start_ok"),),
                           (check("result", "study_result"),), children=(sub,))
        updated_sub = Prototype(sub.key, sub.goal,
                                sub.ready + (check("extra", "extra_check"),),
                                sub.done, sub.operation)
        updated_parent = Prototype(parent.key, parent.goal, parent.ready,
                                   parent.done, children=(updated_sub,))
        self.assertNotEqual(digest(sub), digest(updated_sub))
        self.assertEqual(digest(parent), digest(updated_parent))
        approvals = reviews_for(parent)
        facts = {"start_ok": True, "study_result": False, "save_bound": True,
                 "readable": True, "captured": False, "extra_check": True}
        catalog = {"worlddata.capture": Capability("worlddata.capture", "v1",
                                                    "READ_ONLY", lambda save: None, procedure_ref=FIXTURE_PROCEDURE_REF)}
        with self.assertRaises(NeedsHumanReview):
            compile_fixture(updated_parent, approvals, catalog, facts)
        approvals["capture"] = reviews_for(updated_parent)["capture"]
        # An unchanged parent review remains usable after the changed child is approved.
        self.assertEqual(compile_fixture(updated_parent, approvals, catalog, facts)
                         .inspect().status, "READY")

    def test_instance_binding_is_frozen_even_if_caller_or_fact_callback_mutates(self):
        base = capture()
        bindings = {"save": "first"}
        facts = {"save_bound": True, "readable": True, "captured": False}
        seen = []
        def read_fact(name, params):
            seen.append(("fact", name, params["save"]))
            params["save"] = "tamper-read"
            return facts[name]
        def invoke(save):
            seen.append(("invoke", save))
            facts["captured"] = True
        cat = {"worlddata.capture": Capability(
            "worlddata.capture", "v1", "READ_ONLY", invoke, procedure_ref=FIXTURE_PROCEDURE_REF)}
        compiled = compile_approved(
            base, review_lookup=lambda key, sha: reviews_for(base).get(key),
            capabilities=cat, bindings=bindings, read_fact=read_fact)
        bindings["save"] = "other"
        self.assertEqual(compiled.advance().status, "ADVANCED")
        self.assertIn(("invoke", "first"), seen)
        self.assertFalse(any(row[-1] in {"other", "tamper-read"} for row in seen))

    def test_write_authority_checks_same_snapshot_as_invocation(self):
        action = Prototype("setter", "Write authorized target",
                           (check("ready", "ready"),),
                           (check("verified", "verified"),),
                           Operation("native.setter", "1", "WRITE", ("uid",),
                                     "Existing versioned callable", procedure_ref=FIXTURE_PROCEDURE_REF))
        bindings = {"uid": 7}
        facts = {"ready": True, "verified": False}
        authorized = []
        invocations = []
        def permission(cap, args):
            authorized.append(args["uid"])
            args["uid"] = 500  # A misbehaving callback must not redirect the Action
            return True
        e = compile_approved(
            action, review_lookup=lambda key, sha: reviews_for(action).get(key),
            capabilities={"native.setter": Capability("native.setter", "1", "WRITE",
                                                       lambda uid: invocations.append(uid), procedure_ref=FIXTURE_PROCEDURE_REF)},
            bindings=bindings,
            read_fact=lambda name, args: facts[name],
            authorize_write=permission)
        bindings["uid"] = 999
        self.assertEqual(e.advance().status, "NOT_DONE")
        self.assertEqual(invocations, [7])
        self.assertTrue(authorized)
        self.assertEqual(set(authorized), {7})

    def test_nonserializable_instance_binding_refused(self):
        base = capture()
        with self.assertRaises(ValueError):
            compile_approved(
                base, review_lookup=lambda key, sha: reviews_for(base).get(key),
                capabilities={"worlddata.capture": Capability(
                    "worlddata.capture", "v1", "READ_ONLY", lambda save: None, procedure_ref=FIXTURE_PROCEDURE_REF)},
                bindings={"save": object()},
                read_fact=lambda name, args: True)

    def test_write_needs_separate_instance_authority_and_rechecks_on_call(self):
        calls = []
        action = Prototype("setter", "Set one approved attribute",
                           (check("identity", "identity_ok"),),
                           (check("getter", "getter_matches"),),
                           Operation("native.setter", "v1", "WRITE", ("save", "uid"),
                                     "CAS and readback via existing native capability", procedure_ref=FIXTURE_PROCEDURE_REF))
        grant = reviews_for(action)
        facts = {"identity_ok": True, "getter_matches": False}
        catalog = {"native.setter": Capability("native.setter", "v1", "WRITE",
                                                lambda **kw: calls.append(kw), procedure_ref=FIXTURE_PROCEDURE_REF)}
        permission = {"allowed": False}
        e = compile_fixture(action, grant, catalog, facts,
                            {"save": "test", "uid": 1},
                            lambda cap, args: permission["allowed"])
        self.assertEqual(e.advance().status, "BLOCKED")
        self.assertEqual(calls, [])
        permission["allowed"] = True
        self.assertEqual(e.inspect().status, "READY")
        permission["allowed"] = False
        self.assertEqual(e.advance().status, "BLOCKED")
        self.assertEqual(calls, [])
        permission["allowed"] = True
        self.assertEqual(e.advance().status, "NOT_DONE")
        self.assertEqual(len(calls), 1)
        self.assertEqual(e.advance().status, "RECONCILE")

    def test_invalid_fact_type_is_not_silent_success(self):
        root = capture()
        e = compile_fixture(root, reviews_for(root),
                            {"worlddata.capture": Capability("worlddata.capture", "v1",
                                                             "READ_ONLY", lambda **kw: None, procedure_ref=FIXTURE_PROCEDURE_REF)},
                            {"save_bound": "true", "readable": True, "captured": False})
        self.assertEqual(e.inspect().status, "OBSERVATION_ERROR")
        self.assertEqual(e.advance().status, "OBSERVATION_ERROR")


if __name__ == "__main__":
    unittest.main()

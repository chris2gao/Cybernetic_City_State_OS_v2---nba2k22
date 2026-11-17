"""No shell, game or external side effects: mode gateway positive/negative tests."""
import unittest

# Stable catalog documentation is a TEST FIXTURE; it is not a Human approval.
FIXTURE_PROCEDURE_REF = "fixture://known-procedure@0000000000000000000000000000000000000000"

from execution_mode_gateway import (
    DEFAULT_MODE, DEVELOPMENT, EXECUTION, DevelopmentAuthorizationRequired,
    DevelopmentTool, ExecutionModeGateway, ModeState, ModeViolation,
)
from reviewed_prototypes import (
    Capability, Criterion, HumanReview, NeedsHumanReview, Operation, Prototype,
    digest,
)


def fact(key):
    return Criterion(key, key, "Necessary consumer observation", "reviewed evidence")


def prototype(key="capture"):
    return Prototype(
        key, "Produce one actual outcome",
        (fact("input_ok"),), (fact("output_done"),),
        Operation("known.cap", "v1", "READ_ONLY", ("target",), "Reuse existing function", procedure_ref=FIXTURE_PROCEDURE_REF),
    )


class ModeGatewayTests(unittest.TestCase):
    def setUp(self):
        self.mode = ModeState()
        self.gate = ExecutionModeGateway(read_mode=lambda: self.mode)
        self.values = {"input_ok": True, "output_done": False}
        self.calls = []
        self.root = prototype()
        self.capabilities = {"known.cap": Capability(
            "known.cap", "v1", "READ_ONLY", self._capture, procedure_ref=FIXTURE_PROCEDURE_REF)}
        self.reviews = {
            "capture": HumanReview("capture", digest(self.root), "Human-review-1", True)
        }

    def _capture(self, target):
        self.calls.append(target)
        self.values["output_done"] = True

    def compiled(self, gate=None, root=None, **kwargs):
        return (gate or self.gate).compile_execution(
            root or self.root,
            review_lookup=kwargs.get(
                "review_lookup", lambda key, sha: self.reviews.get(key)),
            capabilities=kwargs.get("capabilities", self.capabilities),
            bindings=kwargs.get("bindings", {"target": "A"}),
            read_fact=kwargs.get(
                "read_fact", lambda name, bindings: self.values[name]),
        )

    def test_default_mode_is_execution_without_per_instance_mode_paperwork(self):
        self.assertEqual(DEFAULT_MODE, EXECUTION)
        self.assertEqual(self.mode.mode, EXECUTION)
        self.assertEqual(self.compiled().run_available()[-1].status, "DONE")
        self.assertEqual(self.calls, ["A"])

    def test_execution_mode_rejects_development_even_with_tool_registered(self):
        invoked = []
        g = ExecutionModeGateway(
            read_mode=lambda: self.mode,
            development_tools={"edit": DevelopmentTool("edit", lambda **kw: invoked.append(kw))},
            verify_development=lambda *args: True,
        )
        with self.assertRaises(ModeViolation):
            g.invoke_development("edit", args={"path": "one.py"})
        self.assertEqual(invoked, [])

    def test_execution_still_requires_real_prototype_human_review(self):
        with self.assertRaises(NeedsHumanReview):
            self.compiled(review_lookup=lambda key, sha: None)
        self.assertEqual(self.calls, [])

    def test_execution_rejects_runtime_capability_invention(self):
        unknown = Prototype("capture", self.root.goal, self.root.ready,
                            self.root.done,
                            Operation("new.shell", "v1", "READ_ONLY", ("target",),
                                      "Someone added a glue tool", procedure_ref=FIXTURE_PROCEDURE_REF))
        approval = {"capture": HumanReview("capture", digest(unknown), "reviewed", True)}
        from reviewed_prototypes import CapabilityGap
        with self.assertRaises(CapabilityGap):
            self.compiled(root=unknown, review_lookup=lambda key, sha: approval[key])
        self.assertEqual(self.calls, [])

    def test_mode_change_after_compile_blocks_action_not_goal(self):
        executor = self.compiled()
        self.assertEqual(executor.inspect().status, "READY")
        self.mode = ModeState(DEVELOPMENT, "T1", "Human-decision-2", "scope-1")
        with self.assertRaises(ModeViolation):
            executor.advance()
        self.assertEqual(self.calls, [])
        self.mode = ModeState()  # Restoring old mode cannot revive an invalidated session
        with self.assertRaises(ModeViolation):
            executor.advance()
        self.assertEqual(self.calls, [])
        # A new session may resume safely after a fresh source/approval check.
        renewed = self.compiled(gate=ExecutionModeGateway(read_mode=lambda: self.mode))
        self.assertEqual(renewed.advance().status, "ADVANCED")
        self.assertEqual(self.calls, ["A"])

    def test_mode_change_within_ready_check_prevents_invocation(self):
        def read_fact(key, binding):
            if key == "input_ok":
                self.mode = ModeState(DEVELOPMENT, "T1", "Human-1", "scope-1")
            return self.values[key]
        executor = self.compiled(read_fact=read_fact)
        # There is no second model-controlled command between readiness and action.
        # The capability boundary itself must check the Host mode again.
        with self.assertRaises(ModeViolation):
            executor.advance()
        self.assertEqual(self.calls, [])
        self.assertEqual(self.gate.audit_events[-1].decision, "DENIED")
        self.assertEqual(self.gate.audit_events[-1].cause, "HOST_STATE")

    def test_loop_blocks_remaining_children_when_mode_changes_mid_execution(self):
        first = Prototype("first", "First reviewed outcome",
                          (fact("input_ok"),), (fact("first_done"),),
                          Operation("first.cap", "v1", "READ_ONLY", ("target",),
                                    "Pre-existing first callable", procedure_ref=FIXTURE_PROCEDURE_REF))
        second = Prototype("second", "Second reviewed outcome",
                           (fact("first_done"),), (fact("second_done"),),
                           Operation("second.cap", "v1", "READ_ONLY", ("target",),
                                     "Pre-existing second callable", procedure_ref=FIXTURE_PROCEDURE_REF))
        root = Prototype("parent", "Both outcomes",
                         (fact("input_ok"),), (fact("parent_done"),),
                         children=(first, second))
        facts = {"input_ok": True, "first_done": False,
                 "second_done": False, "parent_done": False}
        calls = []
        def first_tool(target):
            calls.append("first")
            facts["first_done"] = True
            self.mode = ModeState(DEVELOPMENT, "new-task", "Human-new", "new-scope")
        def second_tool(target):
            calls.append("second")
            facts["second_done"] = True
        approvals = {
            node.key: HumanReview(node.key, digest(node), "reviewed", True)
            for node in (root, first, second)
        }
        runner = self.gate.compile_execution(
            root, review_lookup=lambda key, sha: approvals[key],
            capabilities={
                "first.cap": Capability("first.cap", "v1", "READ_ONLY", first_tool, procedure_ref=FIXTURE_PROCEDURE_REF),
                "second.cap": Capability("second.cap", "v1", "READ_ONLY", second_tool, procedure_ref=FIXTURE_PROCEDURE_REF),
            },
            bindings={"target": "sample"},
            read_fact=lambda name, bindings: facts[name],
        )
        with self.assertRaises(ModeViolation):
            runner.run_available()
        self.assertEqual(calls, ["first"])
        self.assertFalse(facts["parent_done"])
        self.assertFalse(facts["second_done"])

    def test_invalid_development_mode_without_scoped_human_decision(self):
        for state in (ModeState(DEVELOPMENT), ModeState(DEVELOPMENT, "T1", "", "scope"),
                      ModeState("ARBITRARY", "T1", "a", "scope")):
            with self.subTest(state=state), self.assertRaises(ModeViolation):
                ExecutionModeGateway(read_mode=lambda value=state: value)

    def test_development_mode_must_revalidate_human_scope(self):
        self.mode = ModeState(DEVELOPMENT, "T1", "Human-actual-decision", "scope-1")
        calls = []
        checked = []
        def verify(state, action, args):
            checked.append((state.task_id, state.scope_ref, action, args["path"]))
            return state.human_decision_ref == "Human-actual-decision" and args["path"] == "allowed.py"
        g = ExecutionModeGateway(
            read_mode=lambda: self.mode, verify_development=verify,
            development_tools={"edit": DevelopmentTool("edit", lambda **kwargs: calls.append(kwargs))})
        with self.assertRaises(DevelopmentAuthorizationRequired):
            g.invoke_development("edit", args={"path": "outside.py"})
        self.assertEqual(calls, [])
        g.invoke_development("edit", args={"path": "allowed.py"})
        self.assertEqual(calls, [{"path": "allowed.py"}])
        self.assertEqual(len(checked), 2)

    def test_human_decision_string_alone_is_not_development_authority(self):
        self.mode = ModeState(DEVELOPMENT, "T1", "someone-wrote-approved", "scope-1")
        calls = []
        g = ExecutionModeGateway(
            read_mode=lambda: self.mode,
            development_tools={"edit": DevelopmentTool("edit", lambda **kw: calls.append(kw))})
        with self.assertRaises(DevelopmentAuthorizationRequired):
            g.invoke_development("edit", args={"path": "x"})
        self.assertEqual(calls, [])

    def test_development_unregistered_tool_fails_closed(self):
        self.mode = ModeState(DEVELOPMENT, "T1", "Human", "scope")
        g = ExecutionModeGateway(
            read_mode=lambda: self.mode,
            development_tools={"edit": DevelopmentTool("edit", lambda **kw: None)},
            verify_development=lambda *args: True)
        with self.assertRaises(ModeViolation):
            g.invoke_development("shell", args={"command": "unsupported"})

    def test_development_mode_cannot_dispatch_business_execution(self):
        self.mode = ModeState(DEVELOPMENT, "T1", "Human", "scope")
        g = ExecutionModeGateway(
            read_mode=lambda: self.mode,
            verify_development=lambda *args: True)
        with self.assertRaises(ModeViolation):
            self.compiled(gate=g)

    def test_development_scope_change_after_verification_stops_tool(self):
        self.mode = ModeState(DEVELOPMENT, "T1", "Human-1", "scope-1")
        calls = []
        def verify(state, name, args):
            self.mode = ModeState(DEVELOPMENT, "T1", "Human-1", "scope-2")
            return True
        g = ExecutionModeGateway(
            read_mode=lambda: self.mode, verify_development=verify,
            development_tools={"edit": DevelopmentTool("edit", lambda **kw: calls.append(kw))})
        with self.assertRaises(ModeViolation):
            g.invoke_development("edit", args={"path": "x"})
        self.assertEqual(calls, [])

    def test_mode_switch_is_not_an_agent_callable(self):
        self.assertFalse(hasattr(self.gate, "switch_mode"))
        self.assertFalse(hasattr(self.gate, "set_mode"))


if __name__ == "__main__":
    unittest.main()

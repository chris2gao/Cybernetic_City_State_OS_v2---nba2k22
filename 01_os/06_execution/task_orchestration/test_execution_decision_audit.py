"""Audit evidence for admitted tool attempts and categorized refusals."""
import unittest

from execution_decision_audit import GatewayEvent, summarize
from execution_mode_gateway import (
    DEVELOPMENT, DevelopmentAuthorizationRequired, DevelopmentTool,
    ExecutionModeGateway, ModeState, ModeViolation,
)
from reviewed_prototypes import (
    Capability, CapabilityGap, Criterion, HumanReview, NeedsHumanReview,
    Operation, Prototype, digest,
)


def event(decision, cause="NONE", reason="APPROVED", model="codex",
          route="DEVELOPMENT", task="T1"):
    return GatewayEvent.create(
        model_ref=model, task_id=task, session_ref="session-1",
        mode=DEVELOPMENT, route=route, operation="edit",
        decision=decision, reason_code=reason, cause=cause)


class AuditTests(unittest.TestCase):
    def test_denied_mode_never_invokes_and_produces_structured_receipt(self):
        calls = []
        saved = []
        gateway = ExecutionModeGateway(
            read_mode=lambda: ModeState(), model_ref="codex",
            audit_sink=saved.append,
            development_tools={"edit": DevelopmentTool("edit", lambda **kw: calls.append(kw))},
            verify_development=lambda *args: True,
        )
        with self.assertRaises(ModeViolation):
            gateway.invoke_development("edit", args={"path": "secret-shall-not-log"})
        self.assertEqual(calls, [])
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].decision, "DENIED")
        self.assertEqual(saved[0].reason_code, "WRONG_MODE")
        self.assertEqual(saved[0].cause, "MODEL_POLICY")
        self.assertEqual(saved[0].model_ref, "codex")
        self.assertNotIn("secret-shall-not-log", str(saved[0].as_record()))
        self.assertEqual(tuple(saved), gateway.audit_events)

    def test_unapproved_prototype_is_human_pending_not_model_conflict(self):
        saved = []
        gate = ExecutionModeGateway(read_mode=lambda: ModeState(),
                                    model_ref="codex", audit_sink=saved.append)
        node = Prototype("read", "Readable artifact",
                         (Criterion("r", "r", "required", "Human"),),
                         (Criterion("d", "d", "required", "Human"),),
                         Operation("known", "1", "READ_ONLY", (), "existing"))
        with self.assertRaises(NeedsHumanReview):
            gate.compile_execution(node, review_lookup=lambda k, v: None,
                                   capabilities={}, bindings={},
                                   read_fact=lambda k, v: True)
        self.assertEqual(saved[0].cause, "HUMAN_PENDING")
        self.assertEqual(saved[0].reason_code, "HUMAN_REVIEW_MISSING")
        self.assertEqual(summarize(saved, min_attempts=1)["policy_denials"], 0)

    def test_capability_gap_is_system_gap_not_model_conflict(self):
        saved = []
        gate = ExecutionModeGateway(read_mode=lambda: ModeState(),
                                    model_ref="codex", audit_sink=saved.append)
        node = Prototype("read", "Readable artifact", (),
                         (Criterion("d", "d", "required", "Human"),),
                         Operation("missing", "1", "READ_ONLY", (), "existing"))
        record = HumanReview("read", digest(node), "human-record", True)
        with self.assertRaises(CapabilityGap):
            gate.compile_execution(node, review_lookup=lambda k, v: record,
                                   capabilities={}, bindings={},
                                   read_fact=lambda k, v: True)
        self.assertEqual(saved[0].cause, "SYSTEM_GAP")

    def test_allowed_execution_one_real_admission_and_no_internal_check_spam(self):
        saved = []
        calls = []
        facts = {"ready": True, "done": False}
        gate = ExecutionModeGateway(read_mode=lambda: ModeState(),
                                    model_ref="claude", audit_sink=saved.append)
        node = Prototype("read", "Real business output",
                         (Criterion("r", "ready", "required", "Human"),),
                         (Criterion("d", "done", "required", "Human"),),
                         Operation("known", "1", "READ_ONLY", ("target",), "existing"))
        record = HumanReview("read", digest(node), "Human-approval", True)
        def run(target):
            calls.append(target)
            facts["done"] = True
        runner = gate.compile_execution(
            node, review_lookup=lambda k, v: record,
            capabilities={"known": Capability("known", "1", "READ_ONLY", run)},
            bindings={"target": "A"}, read_fact=lambda k, v: facts[k])
        self.assertEqual(runner.inspect().status, "READY")
        self.assertEqual(runner.run_available()[-1].status, "DONE")
        self.assertEqual(calls, ["A"])
        self.assertEqual([e.route for e in saved], ["COMPILE", "EXECUTE"])
        self.assertEqual([e.decision for e in saved], ["ADMITTED", "ADMITTED"])

    def test_development_denial_then_allow_and_host_sink_failure_fails_closed(self):
        events = []
        state = ModeState(DEVELOPMENT, "T1", "Human-1", "scope-A")
        calls = []
        approved = {"allow": False}
        gate = ExecutionModeGateway(
            read_mode=lambda: state, model_ref="codex", audit_sink=events.append,
            verify_development=lambda *args: approved["allow"],
            development_tools={"edit": DevelopmentTool("edit", lambda **kw: calls.append(kw))})
        with self.assertRaises(DevelopmentAuthorizationRequired):
            gate.invoke_development("edit", args={"path": "one"})
        approved["allow"] = True
        gate.invoke_development("edit", args={"path": "one"})
        self.assertEqual(calls, [{"path": "one"}])
        self.assertEqual([e.cause for e in events], ["HUMAN_PENDING", "NONE"])
        broken = ExecutionModeGateway(
            read_mode=lambda: state, model_ref="codex",
            audit_sink=lambda event: (_ for _ in ()).throw(OSError("ledger offline")),
            verify_development=lambda *args: True,
            development_tools={"edit": DevelopmentTool("edit", lambda **kw: calls.append(kw))})
        with self.assertRaises(OSError):
            broken.invoke_development("edit", args={"path": "two"})
        self.assertEqual(calls, [{"path": "one"}])

    def test_summary_deduplicates_and_separates_causes_and_models(self):
        events = [
            event("DENIED", "MODEL_POLICY", "UNREGISTERED_TOOL"),
            event("DENIED", "MODEL_POLICY", "WRONG_MODE"),
            event("DENIED", "MODEL_POLICY", "WRONG_MODE"),
            event("DENIED", "HUMAN_PENDING", "DEVELOPMENT_AUTHORITY_MISSING"),
            event("DENIED", "SYSTEM_GAP", "CAPABILITY_GAP"),
            event("ADMITTED"),
            event("ADMITTED"),
            event("ADMITTED"),
            event("ADMITTED"),
            event("ADMITTED"),
            event("DENIED", "MODEL_POLICY", "WRONG_MODE", model="other"),
        ]
        events.append(events[0])  # same event replay from two evidence sources
        outcome = summarize(events, model_ref="other", min_attempts=2)
        self.assertEqual(outcome["signal"], "INSUFFICIENT_SAMPLE")
        outcome = summarize(events, model_ref="codex", min_attempts=5,
                            conflict_rate_threshold=0.3, same_reason_threshold=3)
        self.assertEqual(outcome["attempts"], 10)
        self.assertEqual(outcome["denied"], 5)
        self.assertEqual(outcome["policy_denials"], 3)
        self.assertEqual(outcome["policy_denial_rate"], 0.3)
        self.assertEqual(outcome["signal"], "REVIEW_MODEL_OS_FIT")
        self.assertEqual(outcome["by_cause"]["HUMAN_PENDING"], 1)
        self.assertEqual(outcome["by_cause"]["SYSTEM_GAP"], 1)
        self.assertEqual(outcome["policy_reasons"]["WRONG_MODE"], 2)

    def test_no_automatic_model_ban_even_if_threshold_exceeded(self):
        events = [event("DENIED", "MODEL_POLICY", "UNREGISTERED_TOOL")
                  for _ in range(6)]
        result = summarize(events, min_attempts=5,
                           conflict_rate_threshold=0.2,
                           same_reason_threshold=3)
        self.assertEqual(result["signal"], "REVIEW_MODEL_OS_FIT")
        self.assertNotIn("ban", result)
        self.assertEqual(len(events), 6)

    def test_empty_or_small_sample_is_not_incompatibility(self):
        self.assertEqual(summarize([])["signal"], "INSUFFICIENT_SAMPLE")
        one = [event("DENIED", "MODEL_POLICY", "WRONG_MODE")]
        self.assertEqual(summarize(one, min_attempts=10)["signal"],
                         "INSUFFICIENT_SAMPLE")


if __name__ == "__main__":
    unittest.main()

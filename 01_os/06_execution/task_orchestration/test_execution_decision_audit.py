"""Audit evidence for admitted tool attempts and categorized refusals."""
import unittest

# Stable catalog documentation is a TEST FIXTURE; it is not a Human approval.
FIXTURE_PROCEDURE_REF = "fixture://known-procedure@0000000000000000000000000000000000000000"
from pathlib import Path
import tempfile

from execution_decision_audit import GatewayEvent, append_jsonl_sink, load_jsonl, summarize
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
    def test_host_jsonl_sink_persists_events_for_later_read_only_report(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            state = ModeState(DEVELOPMENT, "T1", "Human-decision", "scope")
            gate = ExecutionModeGateway(
                read_mode=lambda: state, model_ref="codex",
                audit_sink=append_jsonl_sink(path),
                development_tools={"edit": DevelopmentTool("edit", lambda path: path)},
                verify_development=lambda *args: True)
            gate.invoke_development("edit", args={"path": "approved.py"})
            with self.assertRaises(ModeViolation):
                gate.invoke_development("unknown", args={"password": "must-not-be-logged"})
            records = load_jsonl(path)
            self.assertEqual(len(records), 2)
            self.assertEqual([e.decision for e in records], ["ADMITTED", "DENIED"])
            self.assertEqual(records[1].reason_code, "UNREGISTERED_TOOL")
            self.assertEqual(records[0].model_ref, "codex")
            self.assertNotIn("must-not-be-logged", path.read_text(encoding="utf-8"))
            self.assertEqual(summarize(records, model_ref="codex", min_attempts=2,
                                       conflict_rate_threshold=0.5)["policy_denials"], 1)

    def test_unavailable_optional_sink_reports_once_and_allows_authorized_action(self):
        with tempfile.TemporaryDirectory() as directory:
            missing_parent = Path(directory) / "nonexistent" / "events.jsonl"
            calls = []
            state = ModeState(DEVELOPMENT, "T1", "Human-decision", "scope")
            gate = ExecutionModeGateway(
                read_mode=lambda: state, model_ref="codex",
                audit_sink=append_jsonl_sink(missing_parent),
                development_tools={"edit": DevelopmentTool(
                    "edit", lambda **kw: calls.append(kw))},
                verify_development=lambda *args: True)
            gate.invoke_development("edit", args={"path": "example.py"})
            gate.invoke_development("edit", args={"path": "second.py"})
            self.assertEqual(calls, [{"path": "example.py"}, {"path": "second.py"}])
            self.assertEqual(len(gate.audit_faults), 1)
            self.assertIn("OPTIONAL_AUDIT_UNAVAILABLE", gate.audit_faults[0])
            self.assertFalse(missing_parent.exists())

    def test_r2_optional_audit_failure_surfaces_one_warning_without_hidden_repeat(self):
        state = ModeState(DEVELOPMENT, "T1", "Human-decision", "scope")
        warnings = []
        calls = []
        def bad_sink(event):
            raise OSError("private-log-path-not-to-expose")
        gate = ExecutionModeGateway(
            read_mode=lambda: state, audit_sink=bad_sink,
            on_audit_fault=warnings.append,
            verify_development=lambda *args: True,
            development_tools={"edit": DevelopmentTool(
                "edit", lambda **kwargs: calls.append(kwargs))})
        gate.invoke_development("edit", args={"path": "one"})
        gate.invoke_development("edit", args={"path": "two"})
        self.assertEqual(calls, [{"path": "one"}, {"path": "two"}])
        self.assertEqual(len(warnings), 1)
        self.assertEqual(len(gate.audit_faults), 1)
        self.assertIn("OPTIONAL_AUDIT_UNAVAILABLE", warnings[0])
        self.assertNotIn("private-log-path", warnings[0])
        self.assertEqual(len(gate.audit_events), 2)

    def test_r2_audit_failure_does_not_override_real_write_authorization(self):
        gate = ExecutionModeGateway(
            read_mode=lambda: ModeState(),
            audit_sink=lambda event: (_ for _ in ()).throw(OSError("optional ledger offline")))
        node = Prototype("write", "Authorized outcome",
                         (), (Criterion("d", "done", "real readback", "Human review"),),
                         Operation("native.write", "v1", "WRITE", ("target",),
                                   "Guarded existing capability",
                                   procedure_ref=FIXTURE_PROCEDURE_REF))
        review = HumanReview("write", digest(node), "test-only-review", True)
        calls = []
        runner = gate.compile_execution(
            node, review_lookup=lambda key, sha: review,
            capabilities={"native.write": Capability("native.write", "v1", "WRITE",
                                                      lambda target: calls.append(target),
                                                      procedure_ref=FIXTURE_PROCEDURE_REF)},
            bindings={"target": "actual"}, read_fact=lambda key, args: False,
            authorize_write=lambda cap, args: False)
        self.assertEqual(runner.advance().status, "BLOCKED")
        self.assertEqual(calls, [])
        self.assertEqual(len(gate.audit_faults), 1)

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
                         Operation("known", "1", "READ_ONLY", (), "existing", procedure_ref=FIXTURE_PROCEDURE_REF))
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
                         Operation("missing", "1", "READ_ONLY", (), "existing", procedure_ref=FIXTURE_PROCEDURE_REF))
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
                         Operation("known", "1", "READ_ONLY", ("target",), "existing", procedure_ref=FIXTURE_PROCEDURE_REF))
        record = HumanReview("read", digest(node), "Human-approval", True)
        def run(target):
            calls.append(target)
            facts["done"] = True
        runner = gate.compile_execution(
            node, review_lookup=lambda k, v: record,
            capabilities={"known": Capability("known", "1", "READ_ONLY", run, procedure_ref=FIXTURE_PROCEDURE_REF)},
            bindings={"target": "A"}, read_fact=lambda k, v: facts[k])
        self.assertEqual(runner.inspect().status, "READY")
        self.assertEqual(runner.run_available()[-1].status, "DONE")
        self.assertEqual(calls, ["A"])
        self.assertEqual([e.route for e in saved], ["COMPILE", "EXECUTE"])
        self.assertEqual([e.decision for e in saved], ["ADMITTED", "ADMITTED"])

    def test_completed_action_does_not_become_denial_after_mode_change(self):
        from execution_mode_gateway import ModeState
        state = [ModeState()]
        events = []
        facts = {"input_ok": True, "output_done": False}
        child = Prototype("child", "Get confirmed result",
                          (Criterion("r", "input_ok", "required", "Human"),),
                          (Criterion("d", "output_done", "required", "Human"),),
                          Operation("known", "1", "READ_ONLY", (), "existing", procedure_ref=FIXTURE_PROCEDURE_REF))
        record = HumanReview("child", digest(child), "Human", True)
        def action():
            facts["output_done"] = True
            state[0] = ModeState(DEVELOPMENT, "new-task", "Human", "new-scope")
        gate = ExecutionModeGateway(
            read_mode=lambda: state[0], audit_sink=events.append, model_ref="codex")
        runner = gate.compile_execution(
            child, review_lookup=lambda key, sha: record,
            capabilities={"known": Capability("known", "1", "READ_ONLY", action, procedure_ref=FIXTURE_PROCEDURE_REF)},
            bindings={}, read_fact=lambda k, args: facts[k])
        self.assertEqual(runner.advance().status, "ADVANCED")
        self.assertTrue(facts["output_done"])
        self.assertEqual([e.decision for e in events], ["ADMITTED", "ADMITTED"])
        with self.assertRaises(ModeViolation):
            runner.advance()
        self.assertEqual(events[-1].reason_code, "SESSION_REVOKED")
        self.assertEqual([e.decision for e in events], ["ADMITTED", "ADMITTED", "DENIED"])

    def test_development_denial_then_allow_despite_optional_sink_failure(self):
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
        broken.invoke_development("edit", args={"path": "two"})
        self.assertEqual(calls, [{"path": "one"}, {"path": "two"}])
        self.assertEqual(len(broken.audit_faults), 1)

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

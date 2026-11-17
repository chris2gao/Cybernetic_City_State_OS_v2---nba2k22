"""Agent self-disclosure is useful without turning the OS into surveillance."""
import tempfile
from pathlib import Path
import unittest

from agent_self_report import (
    AgentSelfReport, append_self_report_jsonl_sink, load_self_reports,
    summarize_self_reports,
)
from execution_decision_audit import GatewayEvent, summarize


def report(**changes):
    data = {
        "model_ref": "codex", "task_id": "T1", "session_ref": "S1",
        "prototype_ref": "capture-v1", "kind": "UNNECESSARY_CHECK",
        "handling": "CORRECTED_WITHIN_SCOPE",
        "description": "I repeated a source check already performed by the bound tool.",
        "consequence": "No changed business result; avoid this extra check next time.",
    }
    data.update(changes)
    return AgentSelfReport.create(**data)


class TrustFirstSelfReportTests(unittest.TestCase):
    def test_agent_can_acknowledge_unobserved_overwork(self):
        item = report()
        self.assertEqual(item.source, "AGENT_SELF_REPORT")
        self.assertEqual(item.kind, "UNNECESSARY_CHECK")
        self.assertEqual(item.handling, "CORRECTED_WITHIN_SCOPE")
        self.assertIn("already performed", item.description)

    def test_report_is_distinct_from_host_refusal(self):
        disclosed = report()
        denied = GatewayEvent.create(
            model_ref="codex", task_id="T1", session_ref="S1",
            mode="EXECUTION", route="DEVELOPMENT", operation="new-glue",
            decision="DENIED", reason_code="WRONG_MODE", cause="MODEL_POLICY",
        )
        self.assertEqual(summarize([denied], min_attempts=1)["policy_denials"], 1)
        with self.assertRaises((AttributeError, ValueError, TypeError)):
            summarize_self_reports([denied])
        self.assertEqual(summarize_self_reports([disclosed])["disclosures"], 1)
        # The self-report is NOT silently added to the Host refusal denominator.
        self.assertEqual(summarize([denied], min_attempts=1)["attempts"], 1)

    def test_voluntary_disclosure_does_not_score_as_violation(self):
        rows = [report(kind="PROTOTYPE_MISMATCH",
                       handling="REQUESTED_HUMAN_DECISION")]
        summary = summarize_self_reports(rows)
        self.assertNotIn("policy_denials", summary)
        self.assertNotIn("signal", summary)
        self.assertEqual(summary["by_handling"]["REQUESTED_HUMAN_DECISION"], 1)

    def test_local_append_and_read_are_reusable_without_new_service(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "voluntary.jsonl"
            sink = append_self_report_jsonl_sink(path)
            sink(report())
            sink(report(kind="EXTRA_STEP_PROPOSED",
                        handling="STOPPED_AND_REPORTED"))
            restored = load_self_reports(path)
            self.assertEqual(len(restored), 2)
            self.assertEqual(restored[0].source, "AGENT_SELF_REPORT")
            self.assertEqual(summarize_self_reports(restored)["disclosures"], 2)
            self.assertEqual(summarize_self_reports(restored, model_ref="claude")["disclosures"], 0)

    def test_duplicate_forwarding_does_not_double_count(self):
        item = report()
        outcome = summarize_self_reports([item, item])
        self.assertEqual(outcome["disclosures"], 1)

    def test_self_report_is_optional_when_sink_unavailable(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "not-created" / "reports.jsonl"
            item = report()
            with self.assertRaises(FileNotFoundError):
                append_self_report_jsonl_sink(path)(item)
            # The Agent still has a valid structured report for the active chat
            # or an existing checkpoint; reporting cannot grant or revoke access.
            self.assertEqual(item.kind, "UNNECESSARY_CHECK")

    def test_bad_source_or_kind_cannot_be_confused_with_gateway_event(self):
        with self.assertRaises(ValueError):
            report(kind="HOST_DENIED")
        with self.assertRaises(ValueError):
            report(description=" ")
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "reports.jsonl"
            sink = append_self_report_jsonl_sink(path)
            with self.assertRaises(TypeError):
                sink({"source": "HOST_OBSERVED"})
            sink(report())
            raw = path.read_text(encoding="utf-8").replace(
                "AGENT_SELF_REPORT", "HOST_OBSERVED")
            path.write_text(raw, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_self_reports(path)


if __name__ == "__main__":
    unittest.main()

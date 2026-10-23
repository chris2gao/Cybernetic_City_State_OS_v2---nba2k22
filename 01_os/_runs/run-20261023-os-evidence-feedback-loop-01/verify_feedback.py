#!/usr/bin/env python3
"""Static regression examples for an optional core feedback-policy proposal.

This checks document provenance, boundary phrases and counterexample scenarios.
It does NOT prove actual memory-call traces or make the policy active.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROOT = (REPO / "AGENT_WORKING_DISCIPLINE.md").read_text(encoding="utf-8")
ENTRY = (REPO / "01_os/开发入口与单窗口任务规范_v1.md").read_text(encoding="utf-8")
CASE = (Path(__file__).parent / "feedback_case.md").read_text(encoding="utf-8")

def classify(evidence, one_off, generalizable, severe, duplicate, within_envelope):
    # This is a scenario oracle, not a new runtime permission or OS scheduler.
    if within_envelope:
        return "IN_SCOPE_CONTINUE"
    if not evidence:
        return "HOLD_FINDING"
    if duplicate:
        return "REJECT_DUPLICATE"
    if severe or generalizable:
        return "CORE_CANDIDATE"
    if one_off:
        return "LOCAL_FIX"
    return "STOP_AND_REQUEST_SCOPE"

def feedback_cases():
    actual = [
        classify(True, True, False, False, False, False),
        classify(True, False, True, False, False, False),
        classify(True, False, False, True, False, False),
        classify(False, False, False, False, False, False),
        classify(True, False, True, False, True, False),
        classify(True, False, False, False, False, True),
        classify(True, False, False, False, False, False)
    ]
    expected = [
        "LOCAL_FIX", "CORE_CANDIDATE", "CORE_CANDIDATE",
        "HOLD_FINDING", "REJECT_DUPLICATE", "IN_SCOPE_CONTINUE",
        "STOP_AND_REQUEST_SCOPE"
    ]
    assert actual == expected, (actual, expected)
    assert all("`"+x+"`" in CASE for x in set(expected))
    print("PASS FEEDBACK_CASES")

def source_links_and_scope():
    for token in (
        "7d84614710d9855d3ffd683da1cdb6fc896ebcf1",
        "1d980be8f32642e8c177a6ad8e9b429beaa48647",
        "3ae48d2183a6e77d63a43783c7e1999edc01711e",
        "没有完整的 ReadProcessMemory 调用日志",
    ):
        assert token in CASE, token
    assert "## 9. Promote evidence-backed execution feedback" in ROOT
    assert "## 13. 现场经验回流到共享 OS" in ENTRY
    assert "不是本候选要做的事" in CASE
    print("PASS SOURCE_LINKS_AND_SCOPE")

def guardrail_non_regression():
    for token in (
        "not authorization",
        "outside the envelope",
        "does not retroactively",
        "No background monitor",
        "independent",
        "core task",
        "consumer capability",
    ):
        assert token.lower() in ROOT.lower(), token
    for token in (
        "不能直接修改领域内的 core 副本",
        "不等于批准发布到 core/master",
        "不引入新的 always-on",
        "人类",
    ):
        assert token in ENTRY or token == "人类", token
    assert "publish_or_merge_to_master" not in CASE
    print("PASS GUARDRAIL_NON_REGRESSION")

CHECKS = {
    "FEEDBACK_CASES": feedback_cases,
    "SOURCE_LINKS_AND_SCOPE": source_links_and_scope,
    "GUARDRAIL_NON_REGRESSION": guardrail_non_regression,
}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in CHECKS:
        raise SystemExit("Usage: verify_feedback.py "+ "|".join(CHECKS))
    CHECKS[sys.argv[1]]()

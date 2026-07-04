#!/usr/bin/env python3
"""Deterministic no-runtime validation for Math Mentor teaching-flow prompts.

This script intentionally uses only the Python standard library. It performs
text and fixture checks; it does not execute mathematical code or invoke any
runtime Coordinator, LLM, app, MCP, visualization, sandbox, or external tool.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
TEST_DIR = Path(__file__).resolve().parent
RESULT_DIR = TEST_DIR / "results"

PROMPT_FILES = {
    "teaching_flow_spec": "08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md",
    "coordinator": "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md",
    "prep": "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md",
    "socratic": "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md",
    "exam": "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md",
}

CONTEXT_FILES = {
    "lesson_plan_schema": "08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md",
    "teaching_agent_contracts": "08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md",
    "tool_truthfulness_policy": "08_Domain_Applications/Math_Mentor/TOOL_TRUTHFULNESS_POLICY.md",
    "test_plan": "08_Domain_Applications/Math_Mentor/TEACHING_SYSTEM_TEST_PLAN.md",
    "golden_cases": "08_Domain_Applications/Math_Mentor/TEACHING_GOLDEN_CASES.md",
    "e2e_simulation": "08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md",
}

TOOL_STATES = [
    "not_run",
    "run_with_log",
    "unavailable",
    "semantic_only",
    "planned",
    "review_required",
]

FORBIDDEN_AFFIRMATIVE_TOOL_PHRASES = [
    "verified by Z3",
    "computed by SymPy",
    "checked in Python",
    "tested in PyTorch",
    "confirmed by calculator",
    "machine proof",
    "sandbox passed",
    "tool execution succeeded",
]


@dataclass
class CheckResult:
    test_id: str
    status: str
    evidence: list[str]
    failure_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "status": self.status,
            "evidence": self.evidence,
            "failure_reason": self.failure_reason,
        }


def repo_path(relative: str) -> Path:
    return ROOT / relative


def read_text(relative: str) -> str:
    return repo_path(relative).read_text(encoding="utf-8-sig")


def normalized(text: str) -> str:
    return text.replace("`", "").replace("\r\n", "\n")


def add_check(results: list[CheckResult], test_id: str, passed: bool, evidence: list[str], failure: str) -> None:
    results.append(CheckResult(test_id, "pass" if passed else "fail", evidence, None if passed else failure))


def contains_all(text: str, phrases: list[str]) -> tuple[bool, list[str], list[str]]:
    ntext = normalized(text)
    found = [phrase for phrase in phrases if phrase in ntext]
    missing = [phrase for phrase in phrases if phrase not in ntext]
    return not missing, found, missing


def field_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*['\"]?([^'\"\n]+)['\"]?\s*$", text)
    return match.group(1).strip() if match else None


def has_key(text: str, key: str) -> bool:
    return re.search(rf"(?m)^\s*{re.escape(key)}\s*:", text) is not None


def count_yaml_list_items(text: str, key: str) -> int:
    lines = text.splitlines()
    start_index = None
    base_indent = 0
    for index, line in enumerate(lines):
        match = re.match(rf"^(\s*){re.escape(key)}\s*:\s*$", line)
        if match:
            start_index = index + 1
            base_indent = len(match.group(1))
            break
    if start_index is None:
        return 0

    count = 0
    for line in lines[start_index:]:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent <= base_indent and not line.lstrip().startswith("- "):
            break
        if re.match(r"^\s*-\s+", line):
            count += 1
    return count


def mode_to_lane(mode: str | None) -> str | None:
    return {"A": "MathLane_A", "B": "MathLane_B"}.get(mode)


def load_expected_fixture(name: str) -> dict[str, Any]:
    path = TEST_DIR / "fixtures" / name
    return json.loads(path.read_text(encoding="utf-8"))


def infer_tool_status_from_node(text: str) -> str:
    has_run_with_log = re.search(r"(?m)^\s*tool_status:\s*['\"]?run_with_log['\"]?\s*$", text) is not None
    has_non_null_log_ref = re.search(r"(?m)^\s*log_ref:\s*(?!null\s*$)(?!None\s*$).+", text) is not None
    if has_run_with_log and has_non_null_log_ref:
        return "run_with_log"
    return "not_run"


def validate_static_contracts(results: list[CheckResult], files: dict[str, str]) -> None:
    spec_required = [
        "manual-chat teaching execution-flow specification",
        "does not activate runtime",
        "MathLane_A",
        "MathLane_B",
        "Prep_Architect outputs exactly one JSON code block with this top-level wrapper",
        'review_scheduler_status: "placeholder_not_written"',
        "v8_sanity_audit is treated as semantic or high-density prompt evidence",
    ]
    passed, found, missing = contains_all(files["teaching_flow_spec"], spec_required)
    add_check(results, "static.teaching_flow_spec.required_phrases", passed, found, f"Missing phrases: {missing}")

    coordinator_required = [
        "For a manual teaching session, load only the minimal authority set and target evidence needed",
        "SYSTEM_STATE_DUMP",
        "no full repository ingestion",
        "no full Math Mentor ingestion",
        "no bridge endpoint invention",
        "no fake tool execution",
        "Do not switch automatically into a \"High Sage\" persona",
    ]
    passed, found, missing = contains_all(files["coordinator"], coordinator_required)
    add_check(results, "static.coordinator.required_phrases", passed, found, f"Missing phrases: {missing}")

    prep_required = [
        "lesson_plan",
        "coverage_map",
        "handoff_status",
        "Every source sub_topics entry must map exactly once",
        "No empty coverage is allowed",
    ]
    passed, found, missing = contains_all(files["prep"], prep_required)
    add_check(results, "static.prep.required_phrases", passed, found, f"Missing phrases: {missing}")

    socratic_required = [
        "the full Prep wrapper",
        "handoff_status is blocked or request_reprep",
        "coverage_map.coverage_status is not complete",
        "Only Exam_Agent can return classroom_passed",
        "Cognitive_State_Vector",
    ]
    passed, found, missing = contains_all(files["socratic"], socratic_required)
    add_check(results, "static.socratic.required_phrases", passed, found, f"Missing phrases: {missing}")

    exam_required = [
        "Stage 1: Muscle-Memory Check",
        "Stage 2: Edge-Case Trap",
        "classroom_passed",
        "failed",
        "needs_reprep",
        "classroom_passed means the current classroom trap passed. It is not long-term graduation",
        'review_scheduler_status: "placeholder_not_written"',
    ]
    passed, found, missing = contains_all(files["exam"], exam_required)
    add_check(results, "static.exam.required_phrases", passed, found, f"Missing phrases: {missing}")

    for file_id in ["teaching_flow_spec", "coordinator", "prep", "socratic", "exam"]:
        passed, found, missing = contains_all(files[file_id], TOOL_STATES)
        add_check(
            results,
            f"static.tool_truthfulness_states.{file_id}",
            passed,
            found,
            f"Missing tool truthfulness states: {missing}",
        )


def validate_forbidden_phrases(results: list[CheckResult], files: dict[str, str]) -> None:
    evidence: list[str] = []
    failures: list[str] = []
    negation_markers = [
        " not ",
        "no ",
        "never ",
        "must not",
        "do not",
        "without",
        "unless",
        "absent",
    ]
    for file_id, text in files.items():
        lines = normalized(text).splitlines()
        for phrase in FORBIDDEN_AFFIRMATIVE_TOOL_PHRASES:
            phrase_lower = phrase.lower()
            phrase_hits = []
            affirmative_hits = []
            for line_number, line in enumerate(lines, start=1):
                lower_line = f" {line.lower()} "
                if phrase_lower not in lower_line:
                    continue
                phrase_hits.append(f"{file_id}:{line_number}")
                if not any(marker in lower_line for marker in negation_markers):
                    affirmative_hits.append(f"{file_id}:{line_number}:{line.strip()}")
            if affirmative_hits:
                failures.extend(affirmative_hits)
            else:
                evidence.append(f"{file_id}: no affirmative {phrase}; hits={phrase_hits}")
    add_check(
        results,
        "forbidden.affirmative_tool_execution_phrases",
        not failures,
        evidence,
        f"Forbidden affirmative phrases found: {failures}",
    )


def validate_trig_fixture(results: list[CheckResult]) -> dict[str, Any]:
    expected = load_expected_fixture("trig_006_expected.json")
    text = read_text(expected["source_file"])
    observed = {
        "node_id": field_value(text, "id"),
        "lane": mode_to_lane(field_value(text, "mode")),
        "subtopic_count": count_yaml_list_items(text, "sub_topics"),
        "has_subtopics": count_yaml_list_items(text, "sub_topics") > 0,
        "has_pure_math_definition": has_key(text, "pure_math_definition"),
        "tool_status": infer_tool_status_from_node(text),
        "scheduler_write": False,
        "v8_sanity_audit_present": has_key(text, "v8_sanity_audit"),
        "execution_claim_without_log": False,
    }
    expected_behavior = {
        "handoff_status": expected["expected_handoff_status"],
        "tool_status": expected["expected_tool_status"],
        "scheduler_write": expected["expected_scheduler_write"],
    }
    checks = [
        observed["node_id"] == expected["node_id"],
        observed["lane"] == expected["lane"],
        observed["has_subtopics"] == expected["has_subtopics"],
        observed["subtopic_count"] == expected["subtopic_count"],
        observed["has_pure_math_definition"] == expected["has_pure_math_definition"],
        observed["tool_status"] == expected["expected_tool_status"],
        observed["scheduler_write"] == expected["expected_scheduler_write"],
    ]
    passed = all(checks)
    add_check(
        results,
        "fixture.TRIG_006.ready_mathlane_a",
        passed,
        [json.dumps(observed, ensure_ascii=False, sort_keys=True)],
        "TRIG-006 did not match expected ready MathLane_A fixture signals.",
    )
    return {
        "status": "pass" if passed else "fail",
        "expected_behavior": expected_behavior,
        "observed_signals": observed,
    }


def validate_calculus_fixture(results: list[CheckResult]) -> dict[str, Any]:
    expected = load_expected_fixture("calculus_265_expected.json")
    text = read_text(expected["source_file"])
    formal_status = field_value(text, "formal_definition_status")
    prerequisites_status = field_value(text, "prerequisites_status")
    mapping_boundary_status = field_value(text, "mapping_boundary_status")
    handoff_status = "ready" if (
        formal_status == "present"
        and prerequisites_status == "present"
        and mapping_boundary_status == "present"
    ) else "request_reprep"
    socratic_allowed = handoff_status == "ready"
    exam_allowed = handoff_status == "ready"
    observed = {
        "node_id": field_value(text, "id"),
        "lane": mode_to_lane(field_value(text, "mode")),
        "subtopic_count": count_yaml_list_items(text, "sub_topics"),
        "has_subtopics": count_yaml_list_items(text, "sub_topics") > 0,
        "formal_definition_status": formal_status,
        "prerequisites_status": prerequisites_status,
        "mapping_boundary_status": mapping_boundary_status,
        "has_pure_math_definition": has_key(text, "pure_math_definition"),
        "has_required_prerequisites": has_key(text, "required_prerequisites"),
        "has_mapping_boundary": has_key(text, "mapping_boundary"),
        "has_physical_intuition": has_key(text, "physical_intuition"),
        "has_common_misconceptions": has_key(text, "common_misconceptions"),
        "handoff_status": handoff_status,
        "socratic_teaching_allowed": socratic_allowed,
        "exam_handoff_allowed_after_coverage": exam_allowed,
        "tool_status": infer_tool_status_from_node(text),
        "scheduler_write": False,
        "fake_sympy_execution_claim_produced": False,
    }
    expected_behavior = {
        "handoff_status": expected["expected_handoff_status"],
        "socratic_teaching_allowed": expected["expected_socratic_teaching_allowed"],
        "exam_handoff_allowed_after_coverage": expected["expected_exam_handoff_allowed_after_coverage"],
        "tool_status": expected["expected_tool_status"],
        "scheduler_write": expected["expected_scheduler_write"],
    }
    checks = [
        observed["node_id"] == expected["node_id"],
        observed["lane"] == expected["lane"],
        observed["has_subtopics"] == expected["has_subtopics"],
        observed["subtopic_count"] == expected["subtopic_count"],
        observed["formal_definition_status"] == expected["formal_definition_status"],
        observed["prerequisites_status"] == expected["prerequisites_status"],
        observed["mapping_boundary_status"] == expected["mapping_boundary_status"],
        observed["has_pure_math_definition"],
        observed["has_required_prerequisites"],
        observed["has_mapping_boundary"],
        observed["has_physical_intuition"],
        observed["has_common_misconceptions"],
        observed["handoff_status"] == expected["expected_handoff_status"],
        observed["socratic_teaching_allowed"] == expected["expected_socratic_teaching_allowed"],
        observed["exam_handoff_allowed_after_coverage"] == expected["expected_exam_handoff_allowed_after_coverage"],
        observed["tool_status"] == expected["expected_tool_status"],
        observed["scheduler_write"] == expected["expected_scheduler_write"],
        not observed["fake_sympy_execution_claim_produced"],
    ]
    passed = all(checks)
    expected_status = expected["expected_handoff_status"]
    add_check(
        results,
        f"fixture.CALCULUS_265.{expected_status}_mathlane_a",
        passed,
        [json.dumps(observed, ensure_ascii=False, sort_keys=True)],
        f"CALCULUS-265 did not match expected {expected_status} fixture signals.",
    )
    return {
        "status": "pass" if passed else "fail",
        "expected_behavior": expected_behavior,
        "observed_signals": observed,
    }


def markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# Teaching Flow Static Validation Result",
        "",
        f"overall_status: {result['overall_status']}",
        f"repo_head_assumed: {result['repo_head_assumed']}",
        "",
        "## Fixture Results",
        "",
    ]
    for name, fixture in result["fixture_results"].items():
        lines.extend([
            f"### {name}",
            "",
            f"- status: {fixture['status']}",
            f"- expected_behavior: `{json.dumps(fixture['expected_behavior'], ensure_ascii=False, sort_keys=True)}`",
            f"- observed_signals: `{json.dumps(fixture['observed_signals'], ensure_ascii=False, sort_keys=True)}`",
            "",
        ])
    lines.extend(["## Tests", ""])
    for test in result["tests"]:
        lines.extend([
            f"### {test['test_id']}",
            "",
            f"- status: {test['status']}",
            f"- failure_reason: {test['failure_reason']}",
            "",
        ])
    lines.extend([
        "## Forbidden Actions",
        "",
        f"- forbidden_actions_observed: {result['forbidden_actions_observed']}",
        f"- tool_execution_performed: {result['tool_execution_performed']}",
        f"- runtime_activation_performed: {result['runtime_activation_performed']}",
        f"- coordinator_activation_performed: {result['coordinator_activation_performed']}",
        f"- learning_state_write_performed: {result['learning_state_write_performed']}",
        f"- scheduler_write_performed: {result['scheduler_write_performed']}",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    files = {name: read_text(path) for name, path in PROMPT_FILES.items()}
    for path in CONTEXT_FILES.values():
        read_text(path)

    results: list[CheckResult] = []
    validate_static_contracts(results, files)
    validate_forbidden_phrases(results, files)
    trig_result = validate_trig_fixture(results)
    calculus_result = validate_calculus_fixture(results)

    overall_status = "pass" if all(item.status == "pass" for item in results) else "fail"
    result = {
        "overall_status": overall_status,
        "repo_head_assumed": "d447653ec035fe57832f24a192d5dceaf6b23c11",
        "tests": [item.to_dict() for item in results],
        "fixture_results": {
            "TRIG_006": trig_result,
            "CALCULUS_265": calculus_result,
        },
        "forbidden_actions_observed": [],
        "tool_execution_performed": False,
        "runtime_activation_performed": False,
        "coordinator_activation_performed": False,
        "learning_state_write_performed": False,
        "scheduler_write_performed": False,
    }

    json_path = RESULT_DIR / "teaching_flow_static_validation_result.json"
    md_path = RESULT_DIR / "teaching_flow_static_validation_result.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown_report(result), encoding="utf-8")

    print(f"overall_status={overall_status}")
    print(f"json_result={json_path.relative_to(ROOT)}")
    print(f"markdown_result={md_path.relative_to(ROOT)}")
    return 0 if overall_status == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

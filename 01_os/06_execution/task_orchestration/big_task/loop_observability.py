#!/usr/bin/env python3
"""Read-only, deterministic development-loop JSONL validator and reporter.

Strict v1 records are auditable; historical adapters never supply missing evidence.
No authority, Git operation, scheduler, stage transition or acceptance is performed.
Exit: 0 strict valid; 1 evidence/validation findings; 3 malformed input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from closure_preflight import GENUINE_STOP, INTERNAL_CONTINUATION, DECLARABLE_LIFECYCLE_STATES

VERSION = "core.development_loop.iteration.v1"
SHA = re.compile(r"^[a-f0-9]{40}$")
TRIGGERS = {"planned_increment", "test_failure", "review_remediation", "research", "human_scope_update", "resumed_checkpoint"}
OUTCOMES = {"improvement_verified_in_scope", "hypothesis_refuted_and_revised", "verified_no_regression_but_goal_incomplete", "scoped_gap_with_evidence_and_next_trigger", "objective_met_ready_for_series_review", "genuine_stop_reached"}
REGRESSIONS = {"PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"}
GRADES = {"EXECUTED_VERIFIED", "DOCUMENTED_ONLY", "LEGACY_EVIDENCE_MISSING", "UNVERIFIED"}
STATES = {"PASS", "FAIL", "SKIP", "UNKNOWN"}
REQUIRED = ("schema_version", "task_id", "iteration_id", "iteration_index", "trigger_type", "objective", "source_ref", "before_sha", "after_sha", "actual_test_receipts", "expected_vs_observed", "regression_status", "evidence_grade", "remaining_gaps", "next_action_or_stop_reason", "outcome")
LEGACY_A = "legacy_g2_s0"
LEGACY_B = "legacy_season_host"


def issue(code: str, index: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"code": code}
    if index is not None:
        result["record"] = index
    return result


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ValueError("INPUT_UNREADABLE") from exc
    if not lines:
        raise ValueError("EMPTY_JSONL")
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            raise ValueError(f"BLANK_JSONL_LINE:{line_number}")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"INVALID_JSONL:{line_number}:{exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"JSONL_RECORD_NOT_OBJECT:{line_number}")
        rows.append(row)
    return rows


def detect_format(rows: list[dict[str, Any]], requested: str) -> str:
    if requested != "auto":
        return requested
    matches = set()
    for row in rows:
        if row.get("schema_version") == VERSION:
            matches.add("strict")
        elif "bounded_objective" in row and "iteration_id" in row:
            matches.add(LEGACY_A)
        elif "iteration" in row and "increment" in row:
            matches.add(LEGACY_B)
        else:
            matches.add("unknown")
    if len(matches) != 1 or "unknown" in matches:
        raise ValueError("UNKNOWN_OR_MIXED_JSONL_FORMAT")
    return matches.pop()


def _member(value: Any, options: set[str] | frozenset[str]) -> bool:
    return isinstance(value, str) and value in options


def _string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()
    task: str | None = None
    prev_sha: str | None = None
    for pos, row in enumerate(rows, 1):
        missing = [k for k in REQUIRED if k not in row]
        findings.extend(issue("REQUIRED_FIELD_MISSING:" + key, pos) for key in missing)
        ident = row.get("iteration_id")
        if not _string(ident):
            findings.append(issue("INVALID_ITERATION_ID", pos))
        elif ident in seen:
            findings.append(issue("DUPLICATE_ITERATION_ID", pos))
        else:
            seen.add(ident)
        if row.get("schema_version") != VERSION:
            findings.append(issue("INVALID_SCHEMA_VERSION", pos))
        current_task = row.get("task_id")
        if not _string(current_task):
            findings.append(issue("INVALID_TASK_ID", pos))
        elif task is not None and current_task != task:
            findings.append(issue("MIXED_TASK_IDS", pos))
        else:
            task = current_task
        idx = row.get("iteration_index")
        if type(idx) is not int or idx != pos:
            findings.append(issue("NONCONTIGUOUS_ITERATION_ORDER", pos))
        if not _member(row.get("trigger_type"), TRIGGERS):
            findings.append(issue("INVALID_TRIGGER_TYPE", pos))
        for key in ("objective", "source_ref", "next_action_or_stop_reason"):
            if not _string(row.get(key)):
                findings.append(issue("INVALID_REQUIRED_TEXT:" + key, pos))
        before, after = row.get("before_sha"), row.get("after_sha")
        if not isinstance(before, str) or not SHA.fullmatch(before):
            findings.append(issue("INVALID_BEFORE_SHA", pos))
        if not isinstance(after, str) or not SHA.fullmatch(after):
            findings.append(issue("INVALID_AFTER_SHA", pos))
        if pos > 1 and prev_sha is not None and before != prev_sha:
            findings.append(issue("CHECKPOINT_SHA_CHAIN_MISMATCH", pos))
        prev_sha = after if isinstance(after, str) and SHA.fullmatch(after) else None
        if not any(isinstance(row.get(k), list) and bool(row[k]) and all(_string(v) for v in row[k]) for k in ("changed_paths", "research_actions")):
            findings.append(issue("NO_CHANGED_PATHS_OR_RESEARCH_ACTIONS", pos))
        receipts = row.get("actual_test_receipts")
        any_pass = False
        any_failure = False
        if not isinstance(receipts, list):
            findings.append(issue("INVALID_TEST_RECEIPTS", pos))
        else:
            for i, r in enumerate(receipts, 1):
                if not isinstance(r, dict) or not _string(r.get("test_name")) or type(r.get("exit_code")) is not int or not _member(r.get("status"), STATES) or not _string(r.get("receipt_ref")):
                    findings.append(issue(f"INVALID_TEST_RECEIPT:{i}", pos))
                    continue
                if r["status"] == "PASS":
                    any_pass = True
                    if r["exit_code"] != 0:
                        findings.append(issue("PASS_CONTRADICTS_EXIT_CODE", pos))
                        any_failure = True
                if r["status"] == "FAIL" or r["exit_code"] != 0:
                    any_failure = True
        comparison = row.get("expected_vs_observed")
        if not isinstance(comparison, dict) or not all(_string(comparison.get(k)) for k in ("expected", "observed")):
            findings.append(issue("MISSING_EXPECTED_VS_OBSERVED", pos))
        regression = row.get("regression_status")
        grade = row.get("evidence_grade")
        outcome = row.get("outcome")
        if not _member(regression, REGRESSIONS):
            findings.append(issue("INVALID_REGRESSION_STATUS", pos))
        if not _member(grade, GRADES):
            findings.append(issue("INVALID_EVIDENCE_GRADE", pos))
        if not _member(outcome, OUTCOMES):
            findings.append(issue("INVALID_ITERATION_OUTCOME", pos))
        if grade == "EXECUTED_VERIFIED" and (not any_pass or any_failure or regression in ("FAIL", "UNKNOWN")):
            findings.append(issue("EVIDENCE_GRADE_EXCEEDS_TEST_PROOF", pos))
        if any_failure and outcome in ("improvement_verified_in_scope", "objective_met_ready_for_series_review"):
            findings.append(issue("SUCCESS_CLAIM_WITH_FAILED_TEST", pos))
        gaps = row.get("remaining_gaps")
        if not isinstance(gaps, list) or any(not isinstance(v, dict) or not _string(v.get("id")) or not _member(v.get("status"), {"OPEN", "CLOSED", "BLOCKED"}) for v in gaps):
            findings.append(issue("INVALID_REMAINING_GAPS", pos))
            gaps = []
        if outcome == "objective_met_ready_for_series_review" and any(v.get("status") in ("OPEN", "BLOCKED") for v in gaps):
            findings.append(issue("OPEN_GAP_CONTRADICTS_OBJECTIVE_MET", pos))
        if outcome == "objective_met_ready_for_series_review" and (grade != "EXECUTED_VERIFIED" or any_failure or not any_pass):
            findings.append(issue("COMPLETION_WITHOUT_EXECUTED_EVIDENCE", pos))
        stop_reason = row.get("stop_reason")
        if stop_reason is not None and not _member(stop_reason, GENUINE_STOP):
            findings.append(issue("INVALID_GENUINE_STOP_REASON", pos))
        if outcome == "genuine_stop_reached" and not stop_reason:
            findings.append(issue("STOP_WITHOUT_GENUINE_STOP_REASON", pos))
        pause_reason = row.get("continuation_reason")
        if pause_reason is not None and not _member(pause_reason, INTERNAL_CONTINUATION):
            findings.append(issue("UNRECOGNIZED_CONTINUATION_REASON", pos))
        lifecycle = row.get("lifecycle")
        if lifecycle is not None and not _member(lifecycle, DECLARABLE_LIFECYCLE_STATES):
            findings.append(issue("LIFECYCLE_NOT_IN_CANONICAL_ENUM", pos))
        if row.get("independent_review_status") in ("PASS", "APPROVED", "independently_accepted"):
            findings.append(issue("SELF_DECLARED_INDEPENDENT_REVIEW", pos))
        actions = row.get("protected_actions", [])
        if not isinstance(actions, list):
            findings.append(issue("INVALID_PROTECTED_ACTIONS", pos))
            actions = []
        for action in actions:
            if not isinstance(action, dict):
                findings.append(issue("INVALID_PROTECTED_ACTION", pos))
            elif action.get("status") in ("EXECUTED", "COMPLETED"):
                findings.append(issue("PROTECTED_ACTION_REQUIRES_EXTERNAL_HUMAN_PROOF", pos))
        review = row.get("review_schedule")
        if review is not None:
            if not isinstance(review, dict) or review.get("review_mode") not in ("deferred_to_series", "immediate_required"):
                findings.append(issue("INVALID_REVIEW_SCHEDULE", pos))
            elif review.get("review_mode") == "deferred_to_series":
                required = ("series_id", "review_trigger", "must_review_before", "candidate_head", "verification_receipt", "downstream_consumption", "deferral_reason", "next_owner")
                if any(not _string(review.get(k)) for k in required) or review.get("downstream_consumption") != "candidate_only":
                    findings.append(issue("DEFERRED_REVIEW_BOUNDARY_INCOMPLETE", pos))
                if review.get("candidate_head") != after:
                    findings.append(issue("REVIEW_CANDIDATE_SHA_MISMATCH", pos))
    return findings


def replay_legacy(rows: list[dict[str, Any]], fmt: str, task_id: str | None, source_ref: str | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    normalized: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()
    last_sha: str | None = None
    for pos, r in enumerate(rows, 1):
        if fmt == LEGACY_A:
            ident, index = r.get("iteration_id"), pos
            receipts = r.get("test_receipts", [])
            test_evidence = [dict(test_name=t.get("test_name"), exit_code=t.get("exit_code"), status=t.get("status")) for t in receipts if isinstance(t, dict)] if isinstance(receipts, list) else []
            sha0, sha1 = r.get("sha_before"), r.get("sha_after")
            objective, trigger = r.get("bounded_objective"), r.get("trigger_type")
            change = r.get("actions")
            result = r.get("outcome")
            next_ref = r.get("next_trigger_or_stop_ref")
            evidence_missing = [k for k in ("expected_vs_observed", "regression_status", "remaining_gaps", "task_id") if k not in r]
            if not test_evidence or any(type(t.get("exit_code")) is not int for t in test_evidence):
                evidence_missing.append("actual_test_exit_codes")
        else:
            index = r.get("iteration")
            ident = str(index) if type(index) is int else None
            sha0, sha1 = r.get("before_sha"), r.get("after_sha")
            objective, trigger = r.get("goal"), r.get("phase")
            change = [r["action"]] if _string(r.get("action")) else []
            result = r.get("status")
            next_ref = r.get("next_action_or_stop_reason")
            test_evidence = []  # tests_passed counts never substitute for exit_code
            evidence_missing = ["before_sha", "after_sha", "actual_test_exit_codes", "expected_vs_observed", "regression_status", "remaining_gaps", "task_id", "next_action_or_stop_reason"]
        if not _string(ident) or ident in seen:
            findings.append(issue("INVALID_OR_DUPLICATE_LEGACY_ID", pos))
        seen.add(ident)
        if index != pos:
            findings.append(issue("LEGACY_ORDER_MISMATCH", pos))
        if last_sha is not None and sha0 is not None and sha0 != last_sha:
            findings.append(issue("LEGACY_SHA_CHAIN_MISMATCH", pos))
        if not isinstance(sha0, str) or not SHA.fullmatch(sha0) or not isinstance(sha1, str) or not SHA.fullmatch(sha1):
            findings.append(issue("LEGACY_EVIDENCE_MISSING:SHA", pos))
        last_sha = sha1 if isinstance(sha1, str) and SHA.fullmatch(sha1) else None
        if not _string(objective) or not isinstance(change, list) or not change:
            findings.append(issue("LEGACY_MISSING_OBJECTIVE_OR_ACTION", pos))
        if not _string(next_ref):
            findings.append(issue("LEGACY_EVIDENCE_MISSING:NEXT_TRIGGER", pos))
        if fmt == LEGACY_B and result == "PASS":
            findings.append(issue("LEGACY_SELF_REPORTED_PASS_NOT_EXECUTED_PROOF", pos))
        for key in evidence_missing:
            findings.append(issue("LEGACY_EVIDENCE_MISSING:" + key, pos))
        normalized.append({"task_id": task_id, "iteration_id": ident, "iteration_index": index, "trigger_type_source": trigger, "objective": objective, "source_ref": source_ref, "before_sha": sha0, "after_sha": sha1, "research_actions": change, "actual_test_receipts": test_evidence, "source_status": result, "next_action_or_stop_reason": next_ref, "evidence_grade": "LEGACY_EVIDENCE_MISSING", "missing_fields": evidence_missing})
    return normalized, findings


def build_report(rows: list[dict[str, Any]], fmt: str, findings: list[dict[str, Any]], normalized: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    records = normalized if normalized is not None else rows
    test_counts = Counter()
    changes: set[str] = set()
    open_gaps: list[dict[str, Any]] = []
    for r in records:
        for t in r.get("actual_test_receipts", []) if isinstance(r.get("actual_test_receipts"), list) else []:
            if isinstance(t, dict):
                test_counts[str(t.get("status", "UNKNOWN"))] += 1
        changes.update(x for x in r.get("changed_paths", []) if isinstance(x, str)) if isinstance(r.get("changed_paths"), list) else None
        for g in r.get("remaining_gaps", []) if isinstance(r.get("remaining_gaps"), list) else []:
            if isinstance(g, dict) and g.get("status") != "CLOSED":
                open_gaps.append(g)
    missing = sum(1 for f in findings if "MISSING" in f["code"] or "PROOF" in f["code"])
    outcomes = Counter(str(r.get("outcome", r.get("source_status", "UNKNOWN"))) for r in records)
    triggers = Counter(str(r.get("trigger_type", r.get("trigger_type_source", "UNKNOWN"))) for r in records)
    any_failure = bool(findings)
    strict_auditable = fmt == "strict" and not any_failure
    final = rows[-1]
    return {"schema_version": "core.development_loop.report.v1", "authority_effect": "none", "source_format": fmt, "record_count": len(rows), "parsed": True, "compatible_read": True, "strict_audit_pass": strict_auditable, "evidence_status": "STRICT_VERIFIED" if strict_auditable else ("LEGACY_EVIDENCE_MISSING" if fmt != "strict" else "INVALID"), "trigger_distribution": dict(sorted(triggers.items())), "outcome_distribution": dict(sorted(outcomes.items())), "test_receipt_distribution": dict(sorted(test_counts.items())), "missing_evidence_findings": missing, "first_before_sha": records[0].get("before_sha"), "last_after_sha": records[-1].get("after_sha"), "changed_paths": sorted(changes), "open_gaps": open_gaps, "open_gap_evidence_status": "UNKNOWN_LEGACY_NOT_RECORDED" if fmt != "strict" else "RECORDED", "next_action_or_stop_reason": records[-1].get("next_action_or_stop_reason"), "review_candidate": bool(strict_auditable and final.get("outcome") == "objective_met_ready_for_series_review" and final.get("review_schedule") and final["review_schedule"].get("review_mode") == "deferred_to_series"), "review_status": "NOT_INDEPENDENTLY_ACCEPTED", "findings": findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--format", choices=("auto", "strict", LEGACY_A, LEGACY_B), default="auto")
    parser.add_argument("--task-id", help="Historical run.yml provenance only; not an original log field")
    parser.add_argument("--source-ref", help="Exact immutable historical source ref supplied by caller")
    parser.add_argument("--report", type=Path, help="Optional derived report; original JSONL never changed")
    args = parser.parse_args(argv)
    if args.report is not None and args.input.resolve() == args.report.resolve():
        print("REPORT_MUST_NOT_OVERWRITE_INPUT", file=sys.stderr)
        return 3
    try:
        rows = read_jsonl(args.input)
        fmt = detect_format(rows, args.format)
        if fmt == "strict":
            findings = validate(rows)
            report = build_report(rows, fmt, findings)
        else:
            norm, findings = replay_legacy(rows, fmt, args.task_id, args.source_ref)
            report = build_report(rows, fmt, findings, norm)
        if args.source_ref:
            report["source_ref"] = args.source_ref
        if args.task_id:
            report["task_id_from_run_metadata"] = args.task_id
    except ValueError as exc:
        report = {"schema_version": "core.development_loop.report.v1", "authority_effect": "none", "parsed": False, "compatible_read": False, "strict_audit_pass": False, "findings": [issue(str(exc))]}
        rc = 3
    else:
        rc = 1 if report["findings"] else 0
    output = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.report:
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(output, encoding="utf-8")
        except OSError as exc:
            print("REPORT_WRITE_FAILED:" + str(exc), file=sys.stderr)
            return 3
    print(output, end="")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

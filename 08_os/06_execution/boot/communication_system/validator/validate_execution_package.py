#!/usr/bin/env python3
"""Validate Stage06 schema bindings, attempts, and physical changed paths."""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve()
REPO = HERE.parents[5]
RUN = REPO / "08_os/_runs/run-20260805-全局通讯机制-001"
PACKAGE = RUN / "06_执行/06_execution.yml"
STEPS = RUN / "05_步骤拆分/05_steps.yml"
TESTS = RUN / "04_测试生成/04_tests.yml"
SCHEMA = REPO / "08_os/01_workflow/06_执行/实现/最小运行schema_v1.yml"


def allowed(pattern: str, path: str) -> bool:
    return path.startswith(pattern[:-2]) if pattern.endswith("/**") else path == pattern


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="7b63fa2110ab3e7ae2dc0def5901ef7975abc204")
    parser.add_argument("--allow-in-progress", action="store_true")
    args = parser.parse_args()
    findings = []
    try:
        package = yaml.safe_load(PACKAGE.read_text(encoding="utf-8"))
        steps_art = yaml.safe_load(STEPS.read_text(encoding="utf-8"))
        tests_art = yaml.safe_load(TESTS.read_text(encoding="utf-8"))
        schema = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"load_error:{exc}", file=sys.stderr)
        return 3
    if package.get("stage_id") != schema["stage_id"] or package.get("artifact_kind") != schema["artifact_kind"]:
        findings.append("stage_identity_mismatch")
    if not args.allow_in_progress and package.get("status") != "complete":
        findings.append("status_not_complete")
    payload = package.get("payload") or {}
    for field in schema["payload_required_fields"]:
        if field not in payload:
            findings.append(f"payload_field_missing:{field}")
    allowed_paths = payload.get("allowed_write_paths") or []
    actual = payload.get("actual_write_paths") or []
    for path in actual:
        if not any(allowed(pattern, path) for pattern in allowed_paths):
            findings.append(f"actual_path_not_allowed:{path}")
    physical = subprocess.check_output(
        ["git", "-c", "core.quotepath=false", "diff", "--name-only", args.base, "--"],
        cwd=REPO, text=True,
    ).splitlines()
    if sorted(actual) != sorted(physical):
        findings.append("actual_write_paths_do_not_match_physical_diff")
    frozen = (tests_art.get("payload") or {}).get("test_package_sha256")
    if payload.get("frozen_test_package_sha256") != frozen:
        findings.append("frozen_test_package_sha256_mismatch")
    budgets = {step["step_id"]: step["retry_budget"] for step in steps_art["payload"]["steps"]}
    by_step = {sid: [] for sid in budgets}
    for attempt in payload.get("attempts") or []:
        sid = attempt.get("step_id")
        if sid not in by_step:
            findings.append(f"attempt_unknown_step:{sid}")
        else:
            by_step[sid].append(attempt)
        for field in ("step_id", "attempt", "result", "actual_write_paths", "unauthorized_write_attempts"):
            if field not in attempt:
                findings.append(f"attempt_field_missing:{sid}:{field}")
    for sid, records in by_step.items():
        if not records or len(records) > budgets[sid]:
            findings.append(f"attempt_budget_or_coverage:{sid}")
            continue
        if [record["attempt"] for record in records] != list(range(1, len(records) + 1)):
            findings.append(f"attempt_sequence_invalid:{sid}")
        if not args.allow_in_progress and records[-1].get("result") != "pass":
            findings.append(f"step_last_result_not_pass:{sid}")
    if payload.get("unauthorized_write_attempts"):
        findings.append("unauthorized_write_attempts_not_empty")
    for finding in findings:
        print(finding, file=sys.stderr)
    print(f"findings={len(findings)} physical_changed_paths={len(physical)} attempts={len(payload.get('attempts') or [])}")
    return 2 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

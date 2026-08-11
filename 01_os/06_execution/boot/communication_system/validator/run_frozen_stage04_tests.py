#!/usr/bin/env python3
"""Execute the frozen Stage04 cases read-only and write evidence only under Stage06."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve()
REPO = HERE.parents[5]
RUN = REPO / "01_os/_runs/run-20260805-全局通讯机制-001"
STAGE04 = RUN / "04_测试生成"
ORACLE = STAGE04 / "实现/run_stage04_executable_tests.py"


def _sanitize_evidence(value):
    if isinstance(value, dict):
        return {key: _sanitize_evidence(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_evidence(item) for item in value]
    if isinstance(value, str):
        temp_root = str(Path(tempfile.gettempdir()).resolve())
        normalized = value.replace(temp_root, "<system-temp>")
        return re.sub(
            r"<system-temp>[\\/][^\\/\s]+",
            "<isolated-temp>",
            normalized,
        )
    return value


def _load_oracle():
    spec = importlib.util.spec_from_file_location("frozen_stage04_oracle", ORACLE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "mutation-suite"], default="full")
    parser.add_argument("--expected-tested-commit")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    oracle = _load_oracle()
    from stage04_production_adapter import Stage04ProductionAdapter
    adapter = Stage04ProductionAdapter(args.mode)
    freeze_data = yaml.safe_load((STAGE04 / "冻结测试候选_v1.yml").read_text(encoding="utf-8"))
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    if args.expected_tested_commit and head != args.expected_tested_commit:
        print("tested_commit_mismatch", file=sys.stderr)
        return 2
    results = []
    passed = 0
    for case in oracle.TESTS:
        adapter.begin_case(case.test_id)
        fixture = case.fixture_factory(args.mode, REPO, "", freeze_data)
        exc = None
        try:
            case.action(adapter, fixture)
        except Exception as caught:  # noqa: BLE001
            exc = caught
        try:
            case.evaluator(exc, fixture)
            ok = args.mode == "full"
            reason = None if ok else "mutation_not_rejected"
        except Exception as caught:  # noqa: BLE001
            ok = args.mode == "mutation-suite" and str(caught) == case.failure_code
            reason = None if ok else str(caught)
        passed += int(ok)
        results.append({"test_id": case.test_id, "status": "PASS" if ok else "FAIL",
                        "failure_code": case.failure_code, "reason": reason,
                        "physical_trace": _sanitize_evidence(adapter.case_trace())})
    output = {
        "schema_version": "citystate.communication.frozen_stage04_run.v1",
        "mode": args.mode,
        "tested_commit": head,
        "frozen_04_tests_git_blob_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD:01_os/_runs/run-20260805-全局通讯机制-001/04_测试生成/04_tests.yml"],
            cwd=REPO, text=True).strip(),
        "frozen_test_package_sha256": "2bd1fb7237cbb95527b9cae75542c7e81a1412be393307b8b96b7c96a7c7a70b",
        "oracle_sha256": hashlib.sha256(ORACLE.read_bytes()).hexdigest(),
        "total": len(results), "passed": passed, "failed": len(results) - passed,
        "results": results,
    }
    output_path = args.output or RUN / "06_执行" / f"frozen_stage04_production_{args.mode.replace('-', '_')}_results.yml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(output, allow_unicode=True, sort_keys=False),
                           encoding="utf-8", newline="\n")
    print(json.dumps({"total": len(results), "passed": passed,
                      "failed": len(results) - passed}, ensure_ascii=False))
    return 0 if passed == len(results) == 50 else 1


if __name__ == "__main__":
    raise SystemExit(main())

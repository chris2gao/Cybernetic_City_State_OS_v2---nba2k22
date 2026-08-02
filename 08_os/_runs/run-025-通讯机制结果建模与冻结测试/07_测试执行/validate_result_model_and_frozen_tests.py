#!/usr/bin/env python3
"""Validate T56 result model, blocker evidence, and frozen tests."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml


RUN_REL = Path("08_os/_runs/run-025-通讯机制结果建模与冻结测试")
B_REL = RUN_REL / "03_结果建模/B_通讯机制结果模型_v1.yml"
TRACE_REL = RUN_REL / "03_结果建模/B_追溯矩阵_v1.yml"
TEST_REL = RUN_REL / "04_测试生成/冻结测试集_v1.yml"
COVERAGE_REL = RUN_REL / "04_测试生成/测试覆盖报告_v1.json"
FREEZE_MANIFEST_REL = RUN_REL / "04_测试生成/冻结清单_v1.json"
RESULTS_REL = RUN_REL / "07_测试执行/results.json"
INDEPENDENT_SCRIPT_REL = RUN_REL / "07_测试执行/measure_frozen_tests_independently.ps1"
CONNECTOR_REL = RUN_REL / "02_前置阻塞清理/connector支持裁定_v1.yml"
BASELINE_REL = RUN_REL / "02_前置阻塞清理/token_baseline"
INVENTORY_1_REL = RUN_REL / "02_前置阻塞清理/core_window_inventory_run_1.json"
INVENTORY_2_REL = RUN_REL / "02_前置阻塞清理/core_window_inventory_run_2.json"
INVENTORY_COMPARE_REL = RUN_REL / "02_前置阻塞清理/core_window_inventory_consistency.json"
A_V2_REL = Path("08_os/_runs/run-023-通讯机制需求建模/01_需求建模/A_通讯机制需求建模_v2.yml")
EVIDENCE_REL = Path("08_os/_runs/run-024-通讯机制信息收集/02_信息收集与提炼/evidence/证据索引_v1.yml")
A_V2_SHA256 = "2b6f8df7c72f43876d639c6ca9cc1b4e9d5091f97918d82e7c78690cd6c363f7"

REQUIRED_TOKEN_FIELDS = {
    "schema_version", "task_id", "task_type", "provider", "model", "effort",
    "session_mode", "protocol_profile", "input_tokens", "output_tokens",
    "reasoning_tokens", "cache_read_tokens", "cache_write_tokens", "tool_output_bytes",
    "reported_cost", "wall_seconds", "repair_attempts", "review_rounds",
    "validation_result", "quality_incidents", "metric_source",
}
NUMERIC_TOKEN_FIELDS = {
    "input_tokens", "output_tokens", "reasoning_tokens", "cache_read_tokens",
    "cache_write_tokens", "tool_output_bytes", "reported_cost", "wall_seconds",
    "repair_attempts", "review_rounds", "quality_incidents",
}
UNAVAILABLE_TOKEN_FIELDS = {
    "input_tokens", "output_tokens", "reasoning_tokens", "cache_read_tokens",
    "cache_write_tokens", "tool_output_bytes", "reported_cost",
}


class ValidationFailure(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path}: root must be mapping")
    return data


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path}: root must be object")
    return data


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)


def require_evidence_refs(refs: Any, evidence_ids: set[str], context: str) -> None:
    require(isinstance(refs, list) and refs, f"{context}: evidence refs required")
    unknown = [ref for ref in refs if ref not in evidence_ids]
    require(not unknown, f"{context}: unknown evidence refs {unknown}")


def require_exact_tags(claim_names: list[str], prefix: str, numbers: list[int]) -> None:
    for number in numbers:
        tag = f"[{prefix}{number}]"
        require(sum(tag in name for name in claim_names) == 1, f"{tag}: must appear in exactly one claim")


def validate_b(repo: Path, evidence_ids: set[str]) -> tuple[dict[str, Any], set[str], dict[str, str]]:
    data = load_yaml(repo / B_REL)
    expected_top = {"承重命题", "主张", "实现方法", "候选与淘汰", "未被证据覆盖的部分"}
    require(set(data) == expected_top, "B: top-level fields must exactly follow B_schema_v1")
    require(isinstance(data["承重命题"], str) and data["承重命题"].strip(), "B: bearing proposition required")

    claims = data["主张"]
    require(isinstance(claims, list) and claims, "B: claims required")
    claim_names: list[str] = []
    for index, claim in enumerate(claims):
        require(isinstance(claim, dict), f"B claim {index}: mapping required")
        name = claim.get("主张")
        require(isinstance(name, str) and name.strip(), f"B claim {index}: name required")
        require(name not in claim_names, f"B: duplicate claim {name}")
        claim_names.append(name)
        require_evidence_refs(claim.get("依据"), evidence_ids, f"B claim {name}")
        claim_type = claim.get("类型")
        require(claim_type in {"事实", "推论", "设计选择"}, f"B claim {name}: invalid type")
        if claim_type == "推论":
            require(bool(str(claim.get("推理", "")).strip()), f"B claim {name}: inference reasoning required")
        if claim_type == "设计选择":
            require(isinstance(claim.get("备选"), list) and claim["备选"], f"B claim {name}: alternatives required")
            require(bool(str(claim.get("推理", "")).strip()), f"B claim {name}: decision reason required")

    methods = data["实现方法"]
    require(isinstance(methods, list) and methods, "B: implementation methods required")
    method_ids: set[str] = set()
    method_text: dict[str, str] = {}
    covered_claims: set[str] = set()
    for method in methods:
        require(isinstance(method, dict), "B method: mapping required")
        method_id = method.get("ID")
        require(isinstance(method_id, str) and re.fullmatch(r"M-[A-Z0-9-]+", method_id), "B method: valid ID required")
        require(method_id not in method_ids, f"B: duplicate method ID {method_id}")
        method_ids.add(method_id)
        text = method.get("方法")
        require(isinstance(text, str) and text.strip(), f"{method_id}: method text required")
        method_text[method_id] = text
        require(method.get("类型") in {"脚本", "prompt", "skill", "配置", "文档", "流程"}, f"{method_id}: invalid type")
        require_evidence_refs(method.get("依据"), evidence_ids, f"B method {method_id}")
        target = method.get("实现哪条主张")
        require(target in claim_names, f"{method_id}: dangling claim reference")
        covered_claims.add(target)
    require(set(claim_names) == covered_claims, "B: every claim must be implemented")

    candidates = data["候选与淘汰"]
    require(isinstance(candidates, list) and len(candidates) >= 2, "B: at least two candidates required")
    require(any(item.get("状态") == "采纳" for item in candidates), "B: adopted candidate required")
    require(any(item.get("状态") == "淘汰" for item in candidates), "B: rejected candidate required")
    for item in candidates:
        require(item.get("状态") in {"采纳", "淘汰"}, "B candidate: invalid status")
        if item["状态"] == "淘汰":
            require_evidence_refs(item.get("淘汰依据"), evidence_ids, f"B rejected candidate {item.get('候选')}")

    uncovered = data["未被证据覆盖的部分"]
    require(isinstance(uncovered, list), "B: uncovered section must be a list")
    for item in uncovered:
        require(item.get("风险") in {"高", "中", "低"}, "B uncovered item: risk required")
        require(bool(str(item.get("部分", "")).strip()) and bool(str(item.get("为何无依据", "")).strip()), "B uncovered item incomplete")

    require_exact_tags(claim_names, "I", list(range(1, 9)))
    require_exact_tags(claim_names, "C", list(range(17, 24)))
    for number in range(1, 9):
        matching = next(name for name in claim_names if f"[I{number}]" in name)
        require(any(word in matching for word in ("[保留]", "[改造]", "[拒绝]")), f"I{number}: disposition missing")

    joined = "\n".join(walk_strings(data))
    forbidden_numeric = re.compile(r"(观察期|真实任务|传输类型|双权威|rollback).{0,40}(至少|不少于|最多|超过|低于|高于|阈值为|时长为|次数为)\s*\d", re.I)
    require(forbidden_numeric.search(joined) is None, "B: observation-period numeric threshold is forbidden")

    required_method_tokens = {
        "M-AUTH-TARGET-01": ["ReplayStore", "available", "consumed", "原子", "local_git", "github_cli", "connector"],
        "M-ROLLBACK-LOSS-01": ["已 push commit", "未提交工作区", "在途任务", "耐久"],
        "M-TRANSPORT-01": ["local_git", "github_cli", "github_api_connector", "available=true", "重评"],
        "M-LAYOUT-01": ["03_mechanisms/communication", "02_boot/communication", "06_execution/mechanisms/communication", "05_registry/communication_v1.yml"],
        "M-TOKEN-01": ["旧入口", "阶段六", "阶段七", "null"],
        "M-LAYER-01": [".ai/TOKEN_USAGE_PROFILE.md", "01_workflow"],
    }
    for method_id, tokens in required_method_tokens.items():
        require(method_id in method_text, f"B: required method missing {method_id}")
        for token in tokens:
            require(token in method_text[method_id], f"{method_id}: required design token missing {token}")
    return data, method_ids, method_text


def validate_trace_matrix(repo: Path, method_ids: set[str]) -> dict[str, Any]:
    data = load_yaml(repo / TRACE_REL)
    invariants = data.get("invariants")
    require(isinstance(invariants, dict) and set(invariants) == {f"I{i}" for i in range(1, 9)}, "trace: I1-I8 required")
    for key, item in invariants.items():
        require(item.get("disposition") in {"保留", "改造", "拒绝"}, f"trace {key}: disposition required")
        require(set(item.get("method_ids", [])) <= method_ids and item.get("method_ids"), f"trace {key}: methods invalid")
        require(bool(str(item.get("reason_anchor", "")).strip()), f"trace {key}: reason required")

    constraints = data.get("A_v2_new_constraints")
    require(isinstance(constraints, dict) and set(constraints) == {f"C{i}" for i in range(17, 24)}, "trace: C17-C23 required")
    for key, methods in constraints.items():
        require(isinstance(methods, list) and methods and set(methods) <= method_ids, f"trace {key}: methods invalid")

    criteria = data.get("success_criteria")
    require(isinstance(criteria, dict) and set(criteria) == {f"R{i}" for i in range(1, 15)}, "trace: R1-R14 required")
    for key, methods in criteria.items():
        require(isinstance(methods, list) and methods and set(methods) <= method_ids, f"trace {key}: methods invalid")
    require(data.get("canonical_landing_design", {}).get("created_in_T56") is False, "trace: T56 must not create canonical landing")
    return data


def validate_source_list(sources: Any, evidence_ids: set[str], context: str) -> None:
    require(isinstance(sources, list) and sources, f"{context}: sources required")
    for source in sources:
        require(isinstance(source, str), f"{context}: source must be string")
        require(re.fullmatch(r"R(?:[1-9]|1[0-4])|E-\d{3}", source) is not None, f"{context}: forbidden source {source}")
        if source.startswith("E-"):
            require(source in evidence_ids, f"{context}: unknown evidence {source}")


def validate_r8_no_numeric_threshold(entry: dict[str, Any]) -> None:
    text = " ".join(str(entry.get(field, "")) for field in ("描述", "测量方法", "通过判据"))
    forbidden = re.compile(r"(阈值|至少|不少于|最多|低于|高于)\s*[:：=]?\s*\d")
    require(forbidden.search(text) is None, f"{entry.get('描述')}: R8 numeric threshold forbidden")


def validate_test_entry(entry: dict[str, Any], method_ids: set[str], evidence_ids: set[str]) -> tuple[str, str]:
    expected_fields = {"描述", "被测主体", "判据来源", "测量方法", "通过判据", "可失败", "对应成功判据", "类型"}
    require(set(entry) == expected_fields, f"test fields mismatch: {entry.get('描述')}")
    description = entry.get("描述")
    require(isinstance(description, str), "test description required")
    match = re.match(r"^\[(T\d{3})\]\s+.+", description)
    require(match is not None, f"test ID required: {description}")
    require(entry.get("被测主体") in method_ids, f"{description}: unknown B method")
    validate_source_list(entry.get("判据来源"), evidence_ids, description)
    require(bool(str(entry.get("测量方法", "")).strip()), f"{description}: measurement required")
    require(bool(str(entry.get("通过判据", "")).strip()), f"{description}: pass criterion required")
    require(entry.get("可失败") is True, f"{description}: 可失败 must be true")
    criterion = entry.get("对应成功判据")
    require(isinstance(criterion, str) and re.fullmatch(r"R(?:[1-9]|1[0-4])", criterion), f"{description}: invalid R")
    require(entry.get("类型") in {"事实核对", "行为验证", "边界检查", "一致性检查"}, f"{description}: invalid type")
    if criterion == "R8":
        validate_r8_no_numeric_threshold(entry)
    return match.group(1), criterion


def validate_tests(repo: Path, method_ids: set[str], evidence_ids: set[str]) -> tuple[dict[str, Any], dict[str, int]]:
    data = load_yaml(repo / TEST_REL)
    require(set(data) == {"凭证选择记录", "测试", "方法资格", "实现前检查"}, "tests: top-level fields mismatch")
    credential = data["凭证选择记录"]
    required_credential = {"裁定人", "时间", "依据证据", "选定属性", "为何是这些", "度量选择", "容差"}
    require(isinstance(credential, dict) and set(credential) == required_credential, "tests: credential record incomplete")
    require(isinstance(credential["时间"], (str, dt.date)), "tests: credential date required")
    require_evidence_refs(credential["依据证据"], evidence_ids, "tests credential")
    require(isinstance(credential["选定属性"], list) and credential["选定属性"], "tests: selected attributes required")
    for key in ("裁定人", "为何是这些", "度量选择", "容差"):
        require(bool(str(credential[key]).strip()), f"tests credential: {key} required")

    entries = data["测试"]
    require(isinstance(entries, list) and entries, "tests: entries required")
    seen_ids: set[str] = set()
    coverage = {f"R{i}": 0 for i in range(1, 15)}
    for entry in entries:
        require(isinstance(entry, dict), "test entry must be mapping")
        test_id, criterion = validate_test_entry(entry, method_ids, evidence_ids)
        require(test_id not in seen_ids, f"tests: duplicate {test_id}")
        seen_ids.add(test_id)
        coverage[criterion] += 1
    required_ids = {f"T{i:03d}" for i in range(1, 41)}
    require(seen_ids == required_ids, f"tests: exact T001-T040 set required, missing={sorted(required_ids-seen_ids)}")

    qualifications = data["方法资格"]
    require(isinstance(qualifications, dict), "tests: method qualification required")
    require(set(qualifications) == {"可测试性", "同行评审", "已知错误率", "操作标准", "普遍接受度"}, "tests: Daubert fields mismatch")
    require(all(bool(str(value).strip()) for value in qualifications.values()), "tests: Daubert fields must be nonempty")

    precheck = data["实现前检查"]
    require(isinstance(precheck, dict) and set(precheck) == {"约束可满足", "边界僭越"}, "tests: precheck fields mismatch")
    require(precheck["约束可满足"] in {"是", "否", "未检查"}, "tests: invalid satisfiability")
    require(isinstance(precheck["边界僭越"], list), "tests: boundary list required")
    require(all("：" in item or ":" in item for item in precheck["边界僭越"]), "tests: every boundary item needs disposition")

    gaps = [criterion for criterion, count in coverage.items() if count == 0]
    require(not gaps, f"tests: uncovered success criteria {gaps}")
    return data, coverage


def validate_connector(repo: Path) -> dict[str, Any]:
    data = load_yaml(repo / CONNECTOR_REL)
    matrix = data.get("canonical_support_matrix", {})
    connector = matrix.get("github_api_connector", {})
    require(connector.get("mode") == "excluded", "connector: unavailable transport must be excluded")
    condition = str(connector.get("invalidation_condition", ""))
    require("available=true" in condition and "正负例" in condition, "connector: automatic invalidation/retest required")
    scope = data.get("R6_scope_for_P1", {})
    require(scope.get("supported_equivalence_pair") == ["local_git", "github_cli"], "connector: R6 pair must be local_git/github_cli")
    require(scope.get("connector_claim") == "not_verified", "connector: verified claim forbidden")
    return data


def validate_token_baselines(repo: Path) -> dict[str, Any]:
    paths = sorted((repo / BASELINE_REL).glob("old_entry_baseline_*.json"))
    require(len(paths) >= 3, "token baseline: at least three old-entry records required")
    records = [load_json(path) for path in paths]
    matching = None
    for record in records:
        require(REQUIRED_TOKEN_FIELDS <= set(record), f"token baseline {record.get('task_id')}: required fields missing")
        require(record.get("schema_version") == "token_profile_run.v1", "token baseline: schema_version mismatch")
        for field in NUMERIC_TOKEN_FIELDS:
            value = record[field]
            require(value is None or isinstance(value, (int, float)) and not isinstance(value, bool), f"token baseline: invalid numeric {field}")
        require(record.get("validation_result") == "pass", "token baseline: replay must pass")
        require(all(record[field] is None for field in UNAVAILABLE_TOKEN_FIELDS), "token baseline: unavailable metrics must remain null")
        current = json.dumps(record.get("matching_dimensions"), ensure_ascii=False, sort_keys=True)
        matching = matching or current
        require(current == matching, "token baseline: task type/scale/acceptance mismatch")
    aggregate = load_json(repo / BASELINE_REL / "token_profile_aggregate.json")
    require(aggregate.get("record_count") == len(records), "token baseline: aggregate count mismatch")
    require(aggregate.get("skipped_malformed_files") == 0, "token baseline: malformed record skipped")
    return {"record_count": len(records), "matching_dimensions_equal": True, "token_metrics_status": "not_observable"}


def validate_inventory(repo: Path) -> dict[str, Any]:
    first_path = repo / INVENTORY_1_REL
    second_path = repo / INVENTORY_2_REL
    require(first_path.read_bytes() == second_path.read_bytes(), "inventory: reruns must be byte-identical")
    first = load_json(first_path)
    compare = load_json(repo / INVENTORY_COMPARE_REL)
    require(compare.get("byte_identical") is True, "inventory: comparison record must pass")
    require(first.get("coverage", {}).get("completeness") == "partial", "inventory: current completeness must stay honest")
    require(first.get("coverage", {}).get("recompute_before_T7_cutover") is True, "inventory: T7 recompute required")
    not_observable = first.get("coverage", {}).get("not_observable")
    require(isinstance(not_observable, list) and not_observable, "inventory: not_observable list required")
    require(first.get("observations", {}).get("client_session_manifest", {}).get("status") == "not_observable", "inventory: client session status required")
    require(first.get("observations", {}).get("git_worktrees", {}).get("items"), "inventory: observed worktrees required")
    for path in (first_path, second_path, repo / INVENTORY_COMPARE_REL):
        text = path.read_text(encoding="utf-8")
        require(re.search(r"[A-Za-z]:\\Users\\", text, re.I) is None, f"inventory: personal absolute path leaked in {path.name}")
    return {
        "byte_identical": True,
        "worktree_candidates": len(first["observations"]["git_worktrees"]["items"]),
        "not_observable": not_observable,
    }


def negative_self_tests(test_data: dict[str, Any], method_ids: set[str], evidence_ids: set[str], claim_names: list[str]) -> list[str]:
    results = []

    bad_source = copy.deepcopy(test_data["测试"][0])
    bad_source["判据来源"] = ["B.M-EVENT-01"]
    try:
        validate_test_entry(bad_source, method_ids, evidence_ids)
    except ValidationFailure:
        results.append("reject_B_only_traceability")
    else:
        raise ValidationFailure("negative self-test failed: B-only traceability accepted")

    bad_r8 = copy.deepcopy(next(item for item in test_data["测试"] if item["对应成功判据"] == "R8"))
    bad_r8["通过判据"] = "阈值 5"
    try:
        validate_test_entry(bad_r8, method_ids, evidence_ids)
    except ValidationFailure:
        results.append("reject_R8_numeric_threshold")
    else:
        raise ValidationFailure("negative self-test failed: R8 numeric threshold accepted")

    missing_i1 = [name for name in claim_names if "[I1]" not in name]
    try:
        require_exact_tags(missing_i1, "I", list(range(1, 9)))
    except ValidationFailure:
        results.append("reject_missing_invariant")
    else:
        raise ValidationFailure("negative self-test failed: missing invariant accepted")
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()
    repo = args.repo_root.resolve()

    require(sha256(repo / A_V2_REL) == A_V2_SHA256, "A v2 hash mismatch")
    evidence = load_yaml(repo / EVIDENCE_REL)
    entries = evidence.get("evidence_entries")
    require(isinstance(entries, list), "evidence index: entries required")
    evidence_ids = {entry.get("evidence_id") for entry in entries}
    require(evidence_ids == {f"E-{i:03d}" for i in range(1, 28)}, "evidence index: exact E-001..E-027 required")

    b_data, method_ids, _ = validate_b(repo, evidence_ids)
    validate_trace_matrix(repo, method_ids)
    test_data, coverage = validate_tests(repo, method_ids, evidence_ids)
    validate_connector(repo)
    token_result = validate_token_baselines(repo)
    inventory_result = validate_inventory(repo)
    claim_names = [claim["主张"] for claim in b_data["主张"]]
    negative_results = negative_self_tests(test_data, method_ids, evidence_ids, claim_names)

    test_sha = sha256(repo / TEST_REL)
    coverage_report = {
        "artifact_type": "frozen_test_traceability_coverage",
        "test_set": TEST_REL.as_posix(),
        "test_set_sha256": test_sha,
        "allowed_trace_sources": ["R1-R14", "E-001-E-027"],
        "forbidden_trace_sources": ["B design entries"],
        "test_count": len(test_data["测试"]),
        "traceability_violations": 0,
        "coverage_by_success_criterion": coverage,
        "zero_coverage_gaps": [criterion for criterion, count in coverage.items() if count == 0],
        "R8_numeric_thresholds": 0,
    }
    write_json(repo / COVERAGE_REL, coverage_report)

    frozen_files = [TEST_REL, Path(__file__).resolve().relative_to(repo), INDEPENDENT_SCRIPT_REL]
    freeze_manifest = {
        "artifact_type": "T56_frozen_test_manifest",
        "freeze_commit": "resolved_by_git_commit_order",
        "return_to_stage_4_records": [],
        "files": [
            {"path": path.as_posix(), "sha256": sha256(repo / path)}
            for path in frozen_files
        ],
    }
    write_json(repo / FREEZE_MANIFEST_REL, freeze_manifest)

    results = {
        "status": "pass",
        "checks": {
            "A_v2_hash": "passed",
            "B_schema_and_cross_references": "passed",
            "invariants_I1_I8": "passed",
            "A_v2_constraints_C17_C23": "passed",
            "B_numeric_observation_thresholds": 0,
            "frozen_test_schema": "passed",
            "test_traceability_violations": 0,
            "R1_R14_coverage_gaps": [],
            "R8_numeric_thresholds": 0,
            "connector_support_boundary": "passed",
            "token_old_entry_baseline": token_result,
            "core_window_inventory": inventory_result,
            "negative_self_tests": negative_results,
        },
        "counts": {
            "evidence_entries": len(evidence_ids),
            "B_claims": len(b_data["主张"]),
            "B_methods": len(method_ids),
            "frozen_tests": len(test_data["测试"]),
        },
    }
    write_json(repo / RESULTS_REL, results)
    print(json.dumps({"status": "pass", "tests": len(test_data["测试"]), "coverage_gaps": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationFailure as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1)

#!/usr/bin/env python3
"""Task-specific validator for run-024 evidence package completeness and stability."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


RUN_REL = Path("08_os/_runs/run-024-通讯机制信息收集")
EVIDENCE_REL = RUN_REL / "02_信息收集与提炼/evidence"
BASE = "a66ee671e47f3a90f3a108eb7531c7c84b0f9d37"
EXPECTED_A_SHA256 = "cfff1e32928db0c8aeb860260b8ed9c34e32994ab1b137e015dcafe5eac0f4a7"


class ValidationFailure(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path}: root must be mapping")
    return data


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def validate(repo: Path) -> dict:
    evidence = repo / EVIDENCE_REL
    required_files = [
        "00_挖掘目标与领域_v1.yml",
        "01_内部证据_v1.yml",
        "证据索引_v1.yml",
        "可行性判断_v1.yml",
        "边界记录_v1.yml",
        "信源使用记录_v1.yml",
        "core任务类型枚举_v1.json",
    ]
    missing = [name for name in required_files if not (evidence / name).is_file()]
    require(not missing, f"missing evidence files: {missing}")

    goal = load_yaml(evidence / required_files[0])
    internal = load_yaml(evidence / required_files[1])
    index = load_yaml(evidence / required_files[2])
    judgment = load_yaml(evidence / required_files[3])
    boundary = load_yaml(evidence / required_files[4])
    sources_doc = load_yaml(evidence / required_files[5])
    enumeration = json.loads((evidence / required_files[6]).read_text(encoding="utf-8"))

    questions = goal.get("研究问题")
    require(isinstance(questions, list) and questions, "research questions required")
    question_ids = set()
    for item in questions:
        for field in ("id", "问题", "类型", "用途", "捕获单位", "停止条件"):
            require(field in item, f"research question missing {field}")
        require(item["类型"] in {"开放发现", "定向核实"}, f"invalid question type: {item['类型']}")
        require(item["id"] not in question_ids, f"duplicate question id: {item['id']}")
        question_ids.add(item["id"])
        if item["类型"] == "开放发现":
            require(bool(item["捕获单位"]), f"open question {item['id']} needs capture unit")

    sources = sources_doc.get("sources")
    require(isinstance(sources, list) and sources, "sources required")
    source_ids = set()
    source_fields = {
        "source_id",
        "名称",
        "地址",
        "类型",
        "信源可靠性",
        "可靠性理由",
        "发布时间或版本",
        "访问日期",
        "检索限制",
        "可访问性",
        "基础库专用",
    }
    for source in sources:
        require(source_fields <= set(source), f"source missing fields: {source.get('source_id')}")
        require(source["source_id"] not in source_ids, f"duplicate source: {source['source_id']}")
        source_ids.add(source["source_id"])
        limits = source["检索限制"]
        require(
            {"索引偏向", "返回上限", "付费墙", "时间覆盖", "术语壁垒"} <= set(limits),
            f"source limits incomplete: {source['source_id']}",
        )

    entries = index.get("evidence_entries")
    require(isinstance(entries, list) and entries, "evidence entries required")
    entry_ids = set()
    entry_fields = {
        "evidence_id",
        "research_question_ids",
        "主张",
        "方向",
        "source_refs",
        "独立性",
        "信息可信度",
        "可信度理由",
        "时间适用性",
        "适用边界",
        "与A的关系",
        "对B的约束",
        "对测试的潜在线索",
        "事实与推断",
    }
    for entry in entries:
        require(entry_fields <= set(entry), f"evidence missing fields: {entry.get('evidence_id')}")
        eid = entry["evidence_id"]
        require(eid not in entry_ids, f"duplicate evidence id: {eid}")
        entry_ids.add(eid)
        require(set(entry["research_question_ids"]) <= question_ids, f"unknown RQ in {eid}")
        require(entry["方向"] in {"支持", "推翻", "限制", "冲突", "未决"}, f"invalid direction {eid}")
        require(entry["source_refs"], f"source refs required: {eid}")
        for ref in entry["source_refs"]:
            require(ref.get("source_id") in source_ids, f"unknown source in {eid}")
            require("location" in ref and "original_source" in ref, f"bad source ref in {eid}")
        relation = entry["与A的关系"]
        require(
            {"supports_success_criteria", "tests_assumptions", "resolves_ambiguities"} <= set(relation),
            f"A relation incomplete: {eid}",
        )
        require({"读到的事实", "合并方推断"} <= set(entry["事实与推断"]), f"fact/inference missing: {eid}")

    capability_rows = internal.get("old_capability_decisions")
    require(isinstance(capability_rows, list) and len(capability_rows) == 34, "expected 34 capability rows")
    capability_ids = set()
    for row in capability_rows:
        required = {"capability_id", "capability", "判定", "理由", "失败历史", "evidence_refs"}
        require(required <= set(row), f"capability row incomplete: {row.get('capability_id')}")
        cid = row["capability_id"]
        require(cid not in capability_ids, f"duplicate capability id: {cid}")
        capability_ids.add(cid)
        require(row["判定"] in {"保留", "改造", "拒绝", "待验证"}, f"invalid decision: {cid}")
        require(bool(str(row["理由"]).strip()), f"empty reason: {cid}")
        require(bool(str(row["失败历史"]).strip()), f"empty failure history: {cid}")
        require(row["evidence_refs"] and set(row["evidence_refs"]) <= entry_ids, f"bad evidence refs: {cid}")

    coverage = internal.get("source_coverage")
    require(isinstance(coverage, list) and len(coverage) >= 10, "source coverage incomplete")
    require(all(item.get("status") and item.get("finding") for item in coverage), "source coverage blank")

    ambiguities = internal.get("ambiguity_tracking")
    require(isinstance(ambiguities, list) and len(ambiguities) == 8, "expected all 8 A ambiguities")
    ambiguity_ids = {item.get("ambiguity_id") for item in ambiguities}
    require(len(ambiguity_ids) == 8, "ambiguity IDs must be unique")
    token_items = [item for item in ambiguities if "token" in item.get("topic", "").lower()]
    require(len(token_items) == 1 and token_items[0].get("stage2_status") == "escalated", "token ambiguity not escalated")
    require(bool(token_items[0].get("handoff")), "token escalation handoff required")

    require(judgment.get("judgment") in {"supported", "refuted", "partially_supported", "blocked"}, "bad judgment")
    for key in ("bearing_statement", "supported_parts", "refuted_or_limited_parts", "unresolved_parts", "stop_decision"):
        require(key in judgment, f"judgment missing {key}")
    require(judgment["stop_decision"].get("stop") is True, "explicit stop decision required")
    require(judgment["stop_decision"].get("basis"), "stop basis required")

    for key in ("searched", "empty_returns", "truncations", "inaccessible_sources", "search_asymmetry"):
        require(isinstance(boundary.get(key), list) and boundary[key], f"boundary missing {key}")

    require(enumeration.get("base_commit") == BASE, "enumeration base mismatch")
    counts = enumeration.get("counts", {})
    require(counts.get("core_owned_paths_total") == 44, "unexpected core-owned total")
    require(counts.get("core_owned_paths_outside_08_os") == 34, "unexpected non-08 core-owned total")
    require(counts.get("task_types_outside_08_os") == 8, "unexpected task type count")
    require(counts.get("tracked_ai_task_files") == 5, "unexpected tracked .ai/TASKS count")
    require(counts.get("indexed_ai_task_files") == 4, "unexpected indexed .ai/TASKS count")
    require(counts.get("run_id_collision_commits") == 0, "run-id collision detected")
    require(enumeration.get("unclassified_core_paths") == [], "unclassified core paths")
    require(enumeration.get("assignments_not_in_manifest") == [], "task rules outside manifest")
    carrier = enumeration["task_carrier_inventory"]
    require(
        carrier.get("tracked_but_not_indexed") == [".ai/TASKS/context-stage2-local-partition-001.md"],
        "unexpected task index delta",
    )
    known = {item["commit"][:7]: item for item in enumeration["known_instances"]}
    require(set(known) == {"d56ac9e", "ea653f1", "5739a29"}, "known commit set mismatch")
    require(all(item["is_ancestor_of_base"] for item in known.values()), "known commit not ancestor")
    require(any(path.startswith(".githooks/") for path in known["d56ac9e"]["outside_08_os"]), "d56 instance missing")
    require(
        ".ai/REPOSITORY_PUBLISHER_AUTHORITY.yml" in known["ea653f1"]["outside_08_os"],
        "ea653f1 instance missing",
    )
    require(
        {"CORE_MANIFEST.yml", "True_Fork_Protocol.md"} <= set(known["5739a29"]["outside_08_os"]),
        "5739a29 instance missing",
    )

    enumerator = repo / RUN_REL / "06_执行/enumerate_core_task_types.py"
    with tempfile.TemporaryDirectory() as temp_dir:
        first = Path(temp_dir) / "first.json"
        second = Path(temp_dir) / "second.json"
        for output in (first, second):
            completed = run_command(
                [
                    sys.executable,
                    str(enumerator),
                    "--repo-root",
                    str(repo),
                    "--base",
                    BASE,
                    "--output",
                    str(output),
                ],
                repo,
            )
            require(completed.returncode == 0, f"enumerator failed: {completed.stderr}")
        first_bytes = first.read_bytes()
        second_bytes = second.read_bytes()
        require(first_bytes == second_bytes, "enumerator output is not stable")
        require(first_bytes == (evidence / "core任务类型枚举_v1.json").read_bytes(), "canonical enumeration is stale")
        enumeration_sha256 = hashlib.sha256(first_bytes).hexdigest()

    a_path = repo / "08_os/_runs/run-023-通讯机制需求建模/01_需求建模/A_通讯机制需求建模_v1.yml"
    require(hashlib.sha256(a_path.read_bytes()).hexdigest() == EXPECTED_A_SHA256, "A hash mismatch")
    human_gate = load_yaml(
        repo / "08_os/_runs/run-023-通讯机制需求建模/01_需求建模/Human确认_v1.yml"
    )
    require(human_gate.get("status") == "human_confirmed", "A Human gate is not closed")
    require(human_gate.get("candidate", {}).get("sha256") == EXPECTED_A_SHA256, "Human gate hash mismatch")

    independent_path = repo / RUN_REL / "07_测试执行/independent_results.json"
    require(independent_path.is_file(), "independent measurement result missing")
    independent = json.loads(independent_path.read_text(encoding="utf-8-sig"))
    require(independent.get("result") == "pass", "independent measurement did not pass")
    require(
        "does not import task validator" in independent.get("measurement_tool", ""),
        "independent measurement tool boundary missing",
    )

    forbidden_dirs = [repo / RUN_REL / "03_结果建模", repo / RUN_REL / ".ai"]
    require(not any(path.exists() for path in forbidden_dirs), "forbidden result-modeling or .ai path present")

    changed_tracked = {
        line
        for line in run_command(
            ["git", "-c", "core.quotepath=false", "diff", "--name-only", BASE, "--"], repo
        ).stdout.splitlines()
        if line
    }
    changed_untracked = {
        line
        for line in run_command(
            ["git", "-c", "core.quotepath=false", "ls-files", "--others", "--exclude-standard"], repo
        ).stdout.splitlines()
        if line
    }
    changed_paths = sorted(changed_tracked | changed_untracked)
    allowed_prefix = RUN_REL.as_posix() + "/"
    out_of_scope = [path for path in changed_paths if not path.startswith(allowed_prefix)]
    require(changed_paths, "no changed paths observed")
    require(not out_of_scope, f"out-of-scope changed paths: {out_of_scope}")

    return {
        "schema_version": "run024.evidence_validation.v1",
        "result": "pass",
        "base_commit": BASE,
        "checks": {
            "required_evidence_files": len(required_files),
            "research_questions": len(question_ids),
            "sources": len(source_ids),
            "evidence_entries": len(entry_ids),
            "capability_decisions": len(capability_ids),
            "ambiguities": len(ambiguity_ids),
            "enumeration_sha256": enumeration_sha256,
            "enumeration_rerun_stable": True,
            "token_ambiguity_escalated": True,
            "a_human_gate_bound": True,
            "independent_executor_measurement_passed": True,
            "forbidden_stage_paths_absent": True,
            "changed_paths": changed_paths,
            "out_of_scope_paths": 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    try:
        result = validate(repo)
        exit_code = 0
    except (ValidationFailure, OSError, ValueError, yaml.YAMLError) as exc:
        result = {"schema_version": "run024.evidence_validation.v1", "result": "fail", "error": str(exc)}
        exit_code = 1
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = repo / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

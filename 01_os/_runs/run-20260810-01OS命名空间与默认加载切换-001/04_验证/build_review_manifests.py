"""Build the reviewed reference scope and the exact 205-item resolution layer.

Every decision surface is explicit. New paths or uncovered manual occurrences fail;
there is no default rewrite/historical classification.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import yaml


SCANNER_PATH = Path(__file__).with_name("scan_os_namespace_refs.py")
SPEC = importlib.util.spec_from_file_location("scan_os_namespace_refs", SCANNER_PATH)
assert SPEC and SPEC.loader
scanner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scanner)

BULK_RULES = {"generated_run_snapshot_or_receipt", "semantically_named_run_record"}

# Exact lines whose semantics state a frozen before-state, migration observation,
# or measured historical state. Multiple occurrences on one listed line are retained.
RETAINED_HISTORY_LINES = {
    "01_os/_runs/run-008-上下文管理结构迁移/05_步骤拆分/迁移映射_v1.yml":
        {4, 5, 15, 16, 18, 19, 46, 47, 53},
    "01_os/_runs/run-008-上下文管理结构迁移/06_执行/变更清单.md": {38, 48},
    "01_os/_runs/run-016-引用图事实盘点枚举/06_执行/枚举结果_v1.md":
        {4, 15, 76, 78, 107, 108, 109, 110, 111, 112, 114, 136},
    "01_os/_runs/run-20260810-旧OS物理删除-001/03_删除结果/删除后非08树_v1.yml": {5, 30},
    "01_os/_runs/run-20260810-旧OS物理删除-001/08_结论/执行报告_v1.yml":
        {71, 90, 110, 115, 116, 163, 224, 231, 256, 269, 270},
    "01_os/_runs/run-20260810-旧OS退役前迁移与最终白名单-001/03_最终清单/迁移闭包验证_v1.yml":
        {8, 10, 18, 24, 106, 158, 168},
    "01_os/_runs/run-20260810-旧OS退役前迁移与最终白名单-001/08_结论/执行报告_v1.yml": {15},
}

CORRECTION_KEYS = {
    ("01_os/03_mechanisms/context_management/依据材料/系统机制总结_历史输入_v1.md", 6):
        ("durable_provenance_pointer", "migrated_by is a durable pointer to a run artifact, not the historical claim itself."),
    ("01_os/05_registry/repository_guards_v1.yml", 156):
        ("registry_evidence_pointer", "The registry evidence field must continue resolving after the namespace move."),
    ("README.md", 31):
        ("current_documentation_and_namespace_state", "This is stale current-state retirement guidance, not a frozen historical statement."),
}

HISTORICAL_MANUAL_FILES = {
    "01_os/_runs/run-007-上下文管理信息收集测试/artifacts/local-partition/results/command_log.json":
        ("recorded_command_execution", "This JSON line records the command that was actually executed in the completed run."),
    "01_os/_runs/run-20260805-全局通讯机制-001/02_信息收集与提炼/antigravity_desktop_executor_01_result.yml":
        ("captured_model_output", "The literal is captured executor output describing the path vocabulary observed at that time."),
    "01_os/_runs/run-20260805-全局通讯机制-001/04_测试生成/results/mutation_suite_v3.yml":
        ("recorded_command_execution", "The literal is the frozen command observed in this historical test result."),
    "01_os/_runs/run-20260805-全局通讯机制-001/04_测试生成/results/preimplementation_baseline_v3.yml":
        ("recorded_command_execution", "The literal is the frozen command observed in this historical test result."),
    "01_os/_runs/run-20260805-全局通讯机制-001/04_测试生成/results/synthetic_conforming_full_v2.yml":
        ("recorded_command_execution", "The literal is the frozen command observed in this historical test result."),
    "01_os/_runs/run-20260805-全局通讯机制-001/04_测试生成/results/synthetic_conforming_full_v3.yml":
        ("recorded_command_execution", "The literal is the frozen command observed in this historical test result."),
}

MIXED_MANUAL_FILE = (
    "01_os/_runs/run-20260804-阶段协同推演闭环激活-001/07_测试执行/MAJOR-1_Windows路径修复与复验_v1.yml"
)

REWRITE_MANUAL_FILES = {
    "01_os/_runs/run-007-上下文管理信息收集测试/artifacts/local-partition/README.md",
    "01_os/_runs/run-007-上下文管理信息收集测试/artifacts/local-partition/run_local_partition.py",
    "01_os/_runs/run-012-check-jsonschema安装接入验证/07_测试执行/run_validation.ps1",
    "01_os/_runs/run-012-check-jsonschema安装接入验证/07_测试执行/validate_repository_state.py",
    "01_os/_runs/run-013-mutmut安装接入验证/07_测试执行/real_target_tests/prepare_target.py",
    "01_os/_runs/run-013-mutmut安装接入验证/07_测试执行/run_validation.py",
    "01_os/_runs/run-013-mutmut安装接入验证/07_测试执行/run_validation.sh",
    "01_os/_runs/run-013-mutmut安装接入验证/07_测试执行/validate_repository_state.py",
    "01_os/_runs/run-014-cosmic-ray安装对照验证/07_测试执行/compile_results.py",
    "01_os/_runs/run-014-cosmic-ray安装对照验证/07_测试执行/redact_changed_text.py",
    "01_os/_runs/run-014-cosmic-ray安装对照验证/07_测试执行/rerun_all_experiments.sh",
    "01_os/_runs/run-014-cosmic-ray安装对照验证/07_测试执行/run_validation.sh",
    "01_os/_runs/run-014-cosmic-ray安装对照验证/07_测试执行/test_summarize.py",
    "01_os/_runs/run-014-cosmic-ray安装对照验证/07_测试执行/validate_repository_state.py",
    "01_os/_runs/run-014-cosmic-ray安装对照验证/07_测试执行/validate_wrapper.py",
    "01_os/_runs/run-20260804-阶段协同推演闭环激活-001/08_结论/completion_pointer.yml",
    "01_os/_runs/run-20260805-七阶段最小运行闭环-001/08_结论/completion_pointer.yml",
    "01_os/_runs/run-20260805-全局通讯机制-001/04_测试生成/实现/run_stage04_executable_tests.py",
    "01_os/_runs/run-20260805-全局通讯机制-001/04_测试生成/实现/synthetic_adapters.py",
    "01_os/_runs/run-20260805-全局通讯机制-001/04_测试生成/实现/validate_test_candidate.py",
    "01_os/_runs/run-20260805-全局通讯机制-001/05_步骤拆分/实现/validate_05_steps.py",
    "01_os/_runs/run-20260810-旧OS物理删除-001/04_验证/verify_exact_deletion.py",
    "01_os/_runs/run-20260810-旧OS退役前迁移与最终白名单-001/04_验证/build_final_lists.py",
    "01_os/_runs/run-20260810-旧OS退役前迁移与最终白名单-001/04_验证/verify_migration_closure.py",
    "01_os/_runs/run-20260810-根级保留文件重写与依赖盘点-001/07_测试执行/classify_counts.py",
    "01_os/_runs/run-20260810-根级保留文件重写与依赖盘点-001/07_测试执行/scan_non08_references.py",
    "01_os/_runs/run-20260810-根级保留文件重写与依赖盘点-001/07_测试执行/verify_rewrite.py",
}


def manual_decision(item: dict) -> tuple[str, str, str, str]:
    path = item["path"]
    if path in HISTORICAL_MANUAL_FILES:
        group, reason = HISTORICAL_MANUAL_FILES[path]
        return "preserve_historical_literal", group, reason, "literal remains unchanged as recorded run evidence"
    if path == MIXED_MANUAL_FILE and item["line"] in {54, 55}:
        return (
            "preserve_historical_literal",
            "before_after_state",
            "The old/repaired Windows value is a measured before/after fact from the completed repair.",
            "literal remains unchanged because rewriting it would alter the recorded before/after state",
        )
    if path == MIXED_MANUAL_FILE:
        return (
            "rewrite_current_path",
            "durable_validation_pointer",
            "This field remains a reproduction or validation pointer to a repository artifact.",
            "replace repository root segment 01_os with 01_os",
        )
    if path in REWRITE_MANUAL_FILES:
        suffix = Path(path).suffix.lower()
        group = "executable_or_reproduction_pointer" if suffix in scanner.CODE_SUFFIXES else "durable_artifact_pointer"
        reason = (
            "The executable, test, wrapper, or reproduction reference must resolve against the current repository tree."
            if suffix in scanner.CODE_SUFFIXES
            else "The command or completion pointer must remain loadable after the namespace move."
        )
        return "rewrite_current_path", group, reason, "replace repository root segment 01_os with 01_os"
    raise ValueError(f"uncovered manual occurrence path: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-scan", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--scope-output", required=True)
    parser.add_argument("--resolution-output", required=True)
    args = parser.parse_args()
    raw = json.loads(Path(args.raw_scan).read_text(encoding="utf-8"))
    if raw.get("source_commit") != args.source_commit:
        raise ValueError("raw scan source does not match requested source commit")
    entries = raw["entries"]
    for item in entries:
        item["occurrence_id"] = scanner.occurrence_id(args.source_commit, item)

    retained = [
        item for item in entries
        if item["path"] in RETAINED_HISTORY_LINES and item["line"] in RETAINED_HISTORY_LINES[item["path"]]
    ]
    if len(retained) != 47 or any(item["classification_rule"] not in BULK_RULES for item in retained):
        raise ValueError(f"reviewed historical scope drifted: {len(retained)} entries")
    corrections = [item for item in entries if (item["path"], item["line"]) in CORRECTION_KEYS]
    if len(corrections) != 3:
        raise ValueError(f"classification correction scope drifted: {len(corrections)} entries")

    scope = {
        "schema_version": "citystate.os_namespace_reference_scope.v1",
        "source_commit": args.source_commit,
        "excluded_bulk_rules": sorted(BULK_RULES),
        "scope_rationale": (
            "Generated inventories and receipts are echo surfaces, not additional path obligations. "
            "The listed 47 occurrences are exact content-bound exceptions that state past facts."
        ),
        "retained_historical_occurrences": [
            {
                "occurrence_id": item["occurrence_id"],
                "path": item["path"], "line": item["line"], "column": item["column"], "match": item["match"],
                "historical_reason": "frozen_measured_or_migration_state",
                "reason": "This occurrence records a measured prior state, migration mapping, or completed-run observation.",
            }
            for item in retained
        ],
        "classification_corrections": [
            {
                "occurrence_id": item["occurrence_id"],
                "path": item["path"], "line": item["line"], "column": item["column"], "match": item["match"],
                "from_classification": "preserve_historical_literal",
                "final_classification": "rewrite_current_path",
                "semantic_class": CORRECTION_KEYS[(item["path"], item["line"])][0],
                "reason": CORRECTION_KEYS[(item["path"], item["line"])][1],
            }
            for item in corrections
        ],
    }

    scoped = [
        item for item in entries
        if item["classification_rule"] not in BULK_RULES
        or (item["path"] in RETAINED_HISTORY_LINES and item["line"] in RETAINED_HISTORY_LINES[item["path"]])
    ]
    manual = [item for item in scoped if item["proposed_classification"] == "manual_review"]
    if len(manual) != 205:
        raise ValueError(f"manual set drifted: {len(manual)} entries")
    resolutions = []
    for item in manual:
        classification, group, reason, expected = manual_decision(item)
        resolutions.append({
            "occurrence_id": item["occurrence_id"],
            "path": item["path"], "line": item["line"],
            "occurrence_on_line": item["occurrence_on_line"], "match": item["match"],
            "final_classification": classification, "semantic_group": group,
            "reason": reason, "expected_after_cutover": expected,
        })
    if len({row["occurrence_id"] for row in resolutions}) != 205:
        raise ValueError("manual resolution occurrence IDs are not unique")
    resolution = {
        "schema_version": "citystate.manual_review_resolution.v1",
        "source_commit": args.source_commit,
        "decision_policy": "explicit path-level semantic decisions with a two-line before/after override; no fallback",
        "original_manual_occurrences": len(manual),
        "resolutions": resolutions,
    }

    for path, document in ((Path(args.scope_output), scope), (Path(args.resolution_output), resolution)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=120),
            encoding="utf-8", newline="\n",
        )
    print(f"review_manifests_ok retained_history={len(retained)} corrections={len(corrections)} manual={len(manual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

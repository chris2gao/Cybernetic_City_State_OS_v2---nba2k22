#!/usr/bin/env python3
"""Deterministic validator for the context-management structure."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


REPO = Path(__file__).resolve().parents[4]
MECHANISM = REPO / "08_os/03_mechanisms/context_management"
OLD_PATH = "08_os/01_workflow/context-management-mechanism"
UNVERSIONED_D2 = "08_os/_dev/决定_谁执行.md"
D2_V01 = "08_os/_dev/决定_谁执行_v0.1.md"
D2_V02 = "08_os/_dev/决定_谁执行_v0.2.md"
FINDINGS: list[tuple[str, str]] = []


def finding(code: str, message: str) -> None:
    FINDINGS.append((code, message))


def load_yaml(relative: str, code: str) -> Any:
    path = REPO / relative
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        finding(code, f"{relative}: {type(exc).__name__}: {exc}")
        return None


def require_paths() -> None:
    required = [
        "08_os/02_boot/context_management/README.md",
        "08_os/02_boot/context_management/启动清单_v1.yml",
        "08_os/03_mechanisms/context_management/README.md",
        "08_os/03_mechanisms/context_management/方法论_v1.md",
        "08_os/03_mechanisms/context_management/文件隔离与产物生命周期_v1.md",
        "08_os/03_mechanisms/context_management/依据材料/requirement/A_需求建模_v2.yml",
        "08_os/03_mechanisms/context_management/依据材料/requirement/人类确认_v2.yml",
        "08_os/03_mechanisms/context_management/依据材料/evidence/07_证据索引与可行性判断_v1.yml",
        "08_os/03_mechanisms/context_management/实现/文件布局契约_v1.yml",
        "08_os/05_registry/context_management_v1.yml",
        "08_os/06_execution/boot/context_management/README.md",
        "08_os/_dev/开发产物与文件隔离规范_v1.md",
        D2_V01,
        D2_V02,
        "08_os/_runs/run-008-上下文管理结构迁移/run.yml",
        "08_os/_runs/run-008-上下文管理结构迁移/05_步骤拆分/迁移映射_v1.yml",
        "08_os/_runs/run-009-上下文管理结构复核修订/run.yml",
        "08_os/_runs/run-009-上下文管理结构复核修订/06_执行/变更清单.md",
        "08_os/_runs/run-009-上下文管理结构复核修订/07_测试执行/测试记录.md",
    ]
    for relative in required:
        if not (REPO / relative).is_file():
            finding("CM001_REQUIRED_PATH", relative)
    if (REPO / OLD_PATH).exists():
        finding("CM002_OLD_DIRECTORY_PRESENT", OLD_PATH)
    if (REPO / UNVERSIONED_D2).exists():
        finding("CM025_UNVERSIONED_D2_PRESENT", UNVERSIONED_D2)

    d2_v01 = REPO / D2_V01
    if d2_v01.is_file():
        text = d2_v01.read_text(encoding="utf-8")
        if "已被 `决定_谁执行_v0.2.md` 取代" not in text:
            finding("CM026_D2_V01_NOT_SUPERSEDED", D2_V01)

    d2_v02 = REPO / D2_V02
    if d2_v02.is_file():
        text = d2_v02.read_text(encoding="utf-8")
        required = {
            "workspace_partition",
            "enforced_access_boundary",
            "ACL",
            "容器",
            "tool root",
            "网关",
            "正负例",
            "DACL",
            "publish allowlist",
        }
        missing = sorted(token for token in required if token not in text)
        if missing:
            finding("CM027_D2_V02_SEMANTICS", str(missing))


def check_boot_and_contract() -> None:
    boot = load_yaml(
        "08_os/02_boot/context_management/启动清单_v1.yml",
        "CM003_BOOT_YAML",
    )
    if isinstance(boot, dict):
        for item in boot.get("load_order", []):
            relative = item.get("path", "")
            if not relative or not (REPO / relative).is_file():
                finding("CM004_BOOT_REF_MISSING", relative or "<empty>")
        for key in ("validator", "registry"):
            relative = boot.get(key, "")
            if not relative or not (REPO / relative).is_file():
                finding("CM004_BOOT_REF_MISSING", f"{key}={relative}")

    contract = load_yaml(
        "08_os/03_mechanisms/context_management/实现/文件布局契约_v1.yml",
        "CM005_CONTRACT_YAML",
    )
    if isinstance(contract, dict):
        keep = contract.get("keep_roots", [])
        for declared in contract.get("declared_roots", []):
            if not any(declared.startswith(root) for root in keep):
                finding("CM006_DECLARED_ROOT_OUTSIDE_KEEP", declared)
        classes = {
            item.get("id"): item
            for item in contract.get("classes", [])
            if isinstance(item, dict)
        }
        expected = {
            "os_development_run": ("08_os/_runs/<run-id>/", "core"),
            "domain_runtime_run": (".ai/PROGRAM_RUNS/<run-id>/", "domain"),
            "os_development_private_runtime": (
                "08_os/_runs/<run-id>/_runtime/",
                "core_runtime_untracked",
            ),
            "domain_private_runtime": (
                ".ai/PROGRAM_RUNS/<run-id>/_runtime/",
                "domain_runtime_untracked",
            ),
        }
        for class_id, (path, ownership) in expected.items():
            item = classes.get(class_id, {})
            if item.get("path") != path or item.get("ownership") != ownership:
                finding("CM028_RUN_CLASS_CONTRACT", class_id)
            if class_id.endswith("private_runtime") and item.get("tracked") is not False:
                finding("CM028_RUN_CLASS_CONTRACT", f"{class_id}:tracked")

    run009 = load_yaml(
        "08_os/_runs/run-009-上下文管理结构复核修订/run.yml",
        "CM034_RUN009_YAML",
    )
    if isinstance(run009, dict):
        for relative in run009.get("records", {}).values():
            if not (REPO / relative).is_file():
                finding("CM035_RUN009_REF_MISSING", relative)


def check_registry() -> None:
    registry = load_yaml(
        "08_os/05_registry/context_management_v1.yml",
        "CM007_REGISTRY_YAML",
    )
    if not isinstance(registry, dict):
        return
    entries = registry.get("entries", [])
    required_fields = {
        "path",
        "purpose",
        "loader",
        "loader_class",
        "discovery",
        "evidence",
        "cache_dirs",
        "failure_surfacing",
        "deletion_rule",
    }
    registered = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            finding("CM008_REGISTRY_ENTRY_INVALID", str(index))
            continue
        missing = sorted(required_fields - set(entry))
        if missing:
            finding("CM008_REGISTRY_ENTRY_INVALID", f"{index}:{missing}")
        registered.add(entry.get("path"))
    required_sets = {
        "08_os/02_boot/context_management/**",
        "08_os/03_mechanisms/context_management/依据材料/requirement/**",
        "08_os/03_mechanisms/context_management/依据材料/evidence/**",
        "08_os/06_execution/boot/context_management/README.md",
        "08_os/_dev/开发产物与文件隔离规范_v1.md",
        D2_V02,
        "08_os/claude与人类的开发对话日志.md",
        "08_os/01_workflow/02_信息收集与提炼/实现/运行验证补充_v1.md",
    }
    for path_set in sorted(required_sets - registered):
        finding("CM009_REGISTRY_COVERAGE", path_set)


def iter_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"path", "地址"} or key.endswith("_ref"):
                if isinstance(item, str) and item.startswith("08_os/"):
                    refs.append(item)
            refs.extend(iter_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.extend(iter_refs(item))
    return refs


def check_final_evidence() -> None:
    final = load_yaml(
        "08_os/03_mechanisms/context_management/依据材料/evidence/"
        "07_证据索引与可行性判断_v1.yml",
        "CM010_FINAL_EVIDENCE_YAML",
    )
    if not isinstance(final, dict):
        return
    for relative in sorted(set(iter_refs(final))):
        if not (REPO / relative).exists():
            finding("CM011_FINAL_REF_MISSING", relative)
        if OLD_PATH in relative:
            finding("CM012_FINAL_REF_OLD_PATH", relative)
    if final.get("requirement_version") != 2:
        finding("CM013_A_V2_NOT_ACTIVE", str(final.get("requirement_version")))
    completion = final.get("stage_completion_basis", {})
    if not completion.get("human_confirmation_v2_confirmed"):
        finding("CM014_CONFIRMATION_V2_MISSING", "final evidence")


def check_active_text() -> None:
    active = [
        "08_os/README.md",
        "08_os/01_workflow/README.md",
        "08_os/01_workflow/02_信息收集与提炼/README.md",
        "08_os/01_workflow/02_信息收集与提炼/实现/README.md",
        "08_os/01_workflow/02_信息收集与提炼/实现/运行验证补充_v1.md",
        "08_os/01_workflow/06_执行/README.md",
        "08_os/01_workflow/06_执行/方法论_v0.1.md",
        "08_os/02_boot/README.md",
        "08_os/02_boot/协作伙伴.md",
        "08_os/02_boot/context_management/README.md",
        "08_os/03_mechanisms/README.md",
        "08_os/03_mechanisms/context_management/README.md",
        "08_os/03_mechanisms/context_management/方法论_v1.md",
        "08_os/03_mechanisms/context_management/文件隔离与产物生命周期_v1.md",
        "08_os/05_registry/README.md",
        "08_os/06_execution/README.md",
        "08_os/06_execution/boot/context_management/README.md",
        "08_os/_dev/WORKFLOW_BACKBONE_v0.3.md",
        "08_os/_dev/WORKFLOW_MECHANISM_v0.2.md",
        "08_os/_dev/IMPLEMENTATION_PLAN_v0.2.md",
        "08_os/_dev/开发产物与文件隔离规范_v1.md",
        D2_V02,
    ]
    false_boundary = [
        re.compile(r"worktree\s*(是|构成|提供).{0,12}(访问边界|真边界|安全边界)", re.I),
        re.compile(r"每角色一个工作树.{0,20}(真边界|访问边界)", re.I),
        re.compile(r"要变成真边界.{0,30}(worktree|工作树|clone)", re.I),
        re.compile(r"每角色一个工作树的隔离方案", re.I),
    ]
    broad = ("git add --all", "git add .")
    for relative in active:
        path = REPO / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if OLD_PATH in text:
            finding("CM015_ACTIVE_OLD_PATH", relative)
        if "决定_谁执行.md" in text:
            finding("CM029_ACTIVE_UNVERSIONED_D2_REF", relative)
        for pattern in false_boundary:
            if pattern.search(text):
                finding("CM016_FALSE_BOUNDARY_CLAIM", relative)
        for line_no, line in enumerate(text.splitlines(), 1):
            lowered = line.lower()
            if any(token in lowered for token in broad):
                if not any(word in line for word in ("禁止", "不得", "forbid")):
                    finding("CM017_BROAD_STAGING", f"{relative}:{line_no}")


def check_runtime_and_evidence() -> None:
    ignored_paths = {
        "08_os/_runs/*/_runtime/": "08_os/_runs/example/_runtime/private.txt",
        ".ai/PROGRAM_RUNS/*/_runtime/": (
            ".ai/PROGRAM_RUNS/example/_runtime/private.txt"
        ),
    }
    for rule, probe in ignored_paths.items():
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", probe],
            cwd=REPO,
            check=False,
        )
        if ignored.returncode != 0:
            finding("CM018_RUNTIME_NOT_IGNORED", rule)

    tracked = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files", "-z"],
        cwd=REPO,
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8").split("\0")
    for relative in tracked:
        normalized = relative.replace("\\", "/").lower()
        if "/_runtime/" in normalized or "/private/" in normalized or "/scratch/" in normalized:
            finding("CM019_PRIVATE_TRACKED", relative)

    summary_path = (
        REPO
        / "08_os/_runs/run-007-上下文管理信息收集测试/"
        "artifacts/local-partition/results/run_summary.json"
    )
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        if summary["experiment_summary"]["PART-01"] != "failed":
            finding("CM020_PART01_NOT_FAILED", str(summary["experiment_summary"]))
    except Exception as exc:
        finding("CM020_PART01_NOT_FAILED", f"{type(exc).__name__}: {exc}")

    runs_root = REPO / "08_os/_runs"
    for index in range(1, 9):
        prefix = f"run-{index:03d}-"
        if not any(path.is_dir() for path in runs_root.glob(f"{prefix}*")):
            finding("CM030_OS_RUN_HISTORY_MISSING", prefix)


def check_ownership() -> None:
    manifest = load_yaml("CORE_MANIFEST.yml", "CM021_CORE_MANIFEST_YAML")
    if not isinstance(manifest, dict):
        return
    core = manifest.get("core_owned_paths", [])
    domain = manifest.get("domain_owned_paths", [])
    expected_core = {
        "08_os/README.md",
        "08_os/01_workflow/",
        "08_os/02_boot/",
        "08_os/03_mechanisms/",
        "08_os/04_skills_and_tools/",
        "08_os/05_registry/",
        "08_os/06_execution/",
        "08_os/_dev/",
        "08_os/_runs/",
        "08_os/claude与人类的开发对话日志.md",
    }
    expected_domain = {"08_os/07_content/", ".ai/PROGRAM_RUNS/"}
    for missing in sorted(expected_core - set(core)):
        finding("CM022_CORE_OWNERSHIP_MISSING", missing)
    for missing in sorted(expected_domain - set(domain)):
        finding("CM023_DOMAIN_OWNERSHIP_MISSING", missing)
    if "08_os/_runs/" in domain:
        finding("CM031_OS_RUN_DOMAIN_OWNED", "08_os/_runs/")
    if ".ai/PROGRAM_RUNS/" in core:
        finding("CM032_DOMAIN_RUN_CORE_OWNED", ".ai/PROGRAM_RUNS/")
    for left in core:
        for right in domain:
            if left.startswith(right) or right.startswith(left):
                finding("CM024_OWNERSHIP_OVERLAP", f"{left} <> {right}")


def check_active_ownership_text() -> None:
    required_tokens = {
        "08_os/README.md": {
            "08_os/_runs/",
            "core-owned",
            ".ai/PROGRAM_RUNS/",
            "domain-owned",
        },
        "08_os/03_mechanisms/context_management/文件隔离与产物生命周期_v1.md": {
            "08_os/_runs/",
            "core-owned",
            ".ai/PROGRAM_RUNS/",
            "domain-owned",
        },
        "08_os/_dev/开发产物与文件隔离规范_v1.md": {
            "08_os/_runs/",
            "core-owned",
            ".ai/PROGRAM_RUNS/",
            "domain-owned",
        },
    }
    for relative, tokens in required_tokens.items():
        text = (REPO / relative).read_text(encoding="utf-8")
        missing = sorted(token for token in tokens if token not in text)
        if missing:
            finding("CM033_ACTIVE_RUN_OWNERSHIP_TEXT", f"{relative}:{missing}")


def main() -> int:
    require_paths()
    check_boot_and_contract()
    check_registry()
    check_final_evidence()
    check_active_text()
    check_runtime_and_evidence()
    check_ownership()
    check_active_ownership_text()
    if FINDINGS:
        for code, message in FINDINGS:
            print(f"{code}: {message}")
        return 1
    print("context-management structure: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

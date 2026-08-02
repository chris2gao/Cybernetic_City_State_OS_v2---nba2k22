#!/usr/bin/env python3
"""Deterministically enumerate core window/task classes from one immutable Git base."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


TASK_TYPE_RULES = [
    {
        "task_type": "constitutional_and_governance",
        "purpose": "宪章、议会、碳基索引与城邦目标裁定",
        "paths": [
            "04_Parliament/",
            "05_Carbon_Index/",
            "0号方案.md",
            "1号方案.md",
            "2号方案.md",
            "3号方案.md",
            "城邦系统需要实现的目标原则.md",
        ],
    },
    {
        "task_type": "bootstrap_routing_architecture_and_fork",
        "purpose": "启动、路由、架构、实例与 fork 治理",
        "paths": [
            "00_City_State_Routing_Table.md",
            "06_Silicon_Index/",
            "AGENTS.md",
            "ARCHITECTURE.md",
            "CLAUDE.md",
            "INSTANCE_CONFIG.md",
            "True_Fork_Protocol.md",
        ],
    },
    {
        "task_type": "compiler_execution_and_legacy_backbone",
        "purpose": "编译、执行计划、私有区与旧运行骨架",
        "paths": [
            "07_Compiler/",
            "07_Execution_Plans/",
            "07_Silicon_Private_Zones/",
            "system_backbone/",
        ],
    },
    {
        "task_type": "communication_protocol_bootstrap_and_routing",
        "purpose": "旧通讯协议、初始化、load profile 与角色 routing memory",
        "paths": [
            ".ai/PROTOCOL.md",
            ".ai/PROTOCOL_ADHERENCE.md",
            ".ai/HANDOFF_INIT_PROMPT.md",
            ".ai/load_profiles/",
            ".ai/role_memory/",
        ],
    },
    {
        "task_type": "backend_task_and_long_run_contracts",
        "purpose": "后端执行、任务输入、大任务与 long-run 合同",
        "paths": [
            ".ai/CODEX_WORK_MECHANISM_PROTOCOL.md",
            ".ai/CODEX_TASK_INPUT_CONTRACT.md",
            ".ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md",
            ".ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md",
        ],
    },
    {
        "task_type": "token_and_resource_routing",
        "purpose": "Token/资源路由、操作规范与本地计量工具",
        "paths": [
            ".ai/TOKEN_USAGE_PROFILE.md",
            ".ai/TOKEN_USAGE_OPERATIONAL_NORMS.md",
            ".ai/token_profile/",
        ],
    },
    {
        "task_type": "communication_transport_state_and_validation",
        "purpose": "lane、状态归并、通讯合规与 proof chain",
        "paths": [
            ".ai/lanes/",
            ".ai/communication_compliance/",
        ],
    },
    {
        "task_type": "repository_publication_governance",
        "purpose": "发布授权与本地 Git 守卫",
        "paths": [
            ".ai/REPOSITORY_PUBLISHER_AUTHORITY.yml",
            ".githooks/",
        ],
    },
]

KNOWN_COMMITS = ["d56ac9e", "ea653f1", "5739a29"]


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def manifest_list(text: str, key: str) -> list[str]:
    lines = text.splitlines()
    start = lines.index(f"{key}:") + 1
    values: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith((" ", "#")):
            break
        match = re.match(r'^  - "(.+)"$', line)
        if match:
            values.append(match.group(1))
    return values


def path_exists(tree_paths: list[str], declared_path: str) -> bool:
    prefix = declared_path.rstrip("/")
    return prefix in tree_paths or any(path.startswith(prefix + "/") for path in tree_paths)


def full_commit(repo: Path, commitish: str) -> str:
    return git(repo, "rev-parse", f"{commitish}^{{commit}}").strip()


def classify(repo: Path, base: str) -> dict:
    resolved_base = full_commit(repo, base)
    manifest = git(repo, "show", f"{resolved_base}:CORE_MANIFEST.yml")
    core_paths = manifest_list(manifest, "core_owned_paths")
    domain_paths = manifest_list(manifest, "domain_owned_paths")
    tree_paths = sorted(
        path for path in git(repo, "ls-tree", "-r", "--name-only", resolved_base).splitlines() if path
    )

    non_os_core_paths = sorted(path for path in core_paths if not path.startswith("08_os/"))
    assigned: dict[str, str] = {}
    task_types = []
    for rule in TASK_TYPE_RULES:
        active_paths = []
        for path in rule["paths"]:
            if path in assigned:
                raise RuntimeError(f"duplicate task-type path assignment: {path}")
            assigned[path] = rule["task_type"]
            active_paths.append({"path": path, "present": path_exists(tree_paths, path)})
        task_types.append(
            {
                "task_type": rule["task_type"],
                "purpose": rule["purpose"],
                "active_paths": active_paths,
            }
        )

    unclassified = sorted(set(non_os_core_paths) - set(assigned))
    extra_assignments = sorted(set(assigned) - set(non_os_core_paths))

    task_files = sorted(
        path for path in tree_paths if path.startswith(".ai/TASKS/") and not path.endswith("/")
    )
    task_index = git(repo, "show", f"{resolved_base}:.ai/TASKS/index.md")
    indexed_task_files = sorted(path for path in task_files if f"`{path}`" in task_index)

    known_instances = []
    for short_commit in KNOWN_COMMITS:
        commit = full_commit(repo, short_commit)
        ancestor = (
            subprocess.run(
                ["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, resolved_base]
            ).returncode
            == 0
        )
        changed_paths = sorted(
            path
            for path in git(
                repo,
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                commit,
            ).splitlines()
            if path
        )
        known_instances.append(
            {
                "commit": commit,
                "is_ancestor_of_base": ancestor,
                "changed_paths": changed_paths,
                "outside_08_os": [path for path in changed_paths if not path.startswith("08_os/")],
            }
        )

    run_path = "08_os/_runs/run-024-通讯机制信息收集"
    collision_commits = [
        line
        for line in git(repo, "log", resolved_base, "--format=%H", "--", run_path).splitlines()
        if line
    ]

    return {
        "schema_version": "run024.core_task_type_enumeration.v1",
        "base_commit": resolved_base,
        "method": {
            "finite_universe": "CORE_MANIFEST.yml core_owned_paths at base commit",
            "tree_observation": "git ls-tree -r --name-only <base>",
            "classification": "static exhaustive path-to-task-type rules in this script",
            "runtime_window_inventory": "not_observable_from_git",
            "window_coverage_rule": "any core window touching an enumerated active path inherits its task type regardless of provider or UI",
        },
        "counts": {
            "core_owned_paths_total": len(core_paths),
            "core_owned_paths_outside_08_os": len(non_os_core_paths),
            "task_types_outside_08_os": len(task_types),
            "tracked_ai_task_files": len(task_files),
            "indexed_ai_task_files": len(indexed_task_files),
            "run_id_collision_commits": len(collision_commits),
        },
        "task_types": task_types,
        "unclassified_core_paths": unclassified,
        "assignments_not_in_manifest": extra_assignments,
        "task_carrier_inventory": {
            "path": ".ai/TASKS/",
            "ownership": "domain_owned_paths in CORE_MANIFEST.yml",
            "tracked_files": task_files,
            "indexed_files": indexed_task_files,
            "tracked_but_not_indexed": sorted(set(task_files) - set(indexed_task_files)),
        },
        "known_instances": known_instances,
        "run_id_collision_commits": collision_commits,
        "domain_owned_paths": domain_paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = repo / output
    data = classify(repo, args.base)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"result": "pass", "output": str(output), "counts": data["counts"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

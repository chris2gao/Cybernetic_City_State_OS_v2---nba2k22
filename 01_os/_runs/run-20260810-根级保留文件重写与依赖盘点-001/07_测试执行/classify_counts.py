#!/usr/bin/env python3
"""Assign every tracked non-08 file to exactly one retention bucket and count.

The inventory is written by hand from evidence; this script exists so its numbers
are measured rather than asserted, and so that no file falls through unassigned.
Every tracked path outside 01_os/** must land in exactly one bucket.

Usage
    python classify_counts.py [--repo-root .]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter

RETAIN = {
    "AGENTS.md",
    "AGENT_WORKING_DISCIPLINE.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "CORE_MANIFEST.yml",
    ".githooks/pre-push",
    ".githooks/install.ps1",
    ".githooks/test_pre_push_logic.ps1",
    ".githooks/.gitattributes",
    ".githooks/README.md",
    ".gitignore",
    ".gitattributes",
    ".claude/settings.json",
    "new-domain.ps1",
}

MIGRATE = {
    ".ai/REPOSITORY_PUBLISHER_AUTHORITY.yml",
    ".ai/TOKEN_USAGE_PROFILE.md",
    "系统机制总结.md",
}

HUMAN_PREFIX = ("01_Research_Reports/", ".ai/token_profile/")
HUMAN_EXACT = {
    "PROJECT_CONTEXT.md",
    "ARCHITECTURE.md",
    # Correction round 1: its only claimed edge is an external Human standing
    # instruction that cannot be verified from this task's Git evidence. Provisional
    # keep until the Human decides, not a proven repository dependency.
    ".ai/HANDOFF_COMMON_CONVENTIONS.md",
}

# Path roots that carry a classification but no tracked file in this repository.
# They are counted as declarations, never as files, so that an entry-level table and
# a file-count table can never be read as the same number.
DECLARATION_ONLY = {
    ".ai/PROGRAM_RUNS/": "migrate_then_delete_source",
}

DELETE_GROUPS = {
    "06_Silicon_Index": ("06_Silicon_Index/",),
    "ai_communication_plane": (".ai/",),
    "generated_navigation": (),
    "legacy_root_documents": (),
    "legacy_content_trees": (
        "04_Parliament/",
        "system_backbone/",
        "07_Compiler/",
        "05_Carbon_Index/",
        "07_Silicon_Private_Zones/",
        "campaigns/",
        ".claude/",
    ),
}
GENERATED_NAV = {
    "index.md",
    "abstracts.json",
    "repository_index_manifest.json",
    "search_results.json",
    "generate_repository_indexes.py",
}
LEGACY_ROOT_DOCS = {
    "00_City_State_Routing_Table.md",
    "3号方案.md",
    "True_Fork_Protocol.md",
    "INSTANCE_CONFIG.md",
    "城邦系统需要实现的目标原则.md",
    "Plan 3 External Augmentation OS 总体架构设计方案 v0.1.md",
    "开发分支与合并进度总账.md",
    "未完成任务备忘录.yml",
    "agent-run.ps1",
    "agent-status.ps1",
    "agent-stop.ps1",
}


def bucket(path: str) -> tuple[str, str]:
    if path in RETAIN:
        return "retain_non_08", ""
    if path in MIGRATE:
        return "migrate_then_delete_source", ""
    if path in HUMAN_EXACT or path.startswith(HUMAN_PREFIX):
        return "Human_decision_required", ""
    # Location decides the group, so a generated index.md inside a legacy tree is
    # counted with that tree and nothing is counted twice. The cross-cutting count
    # of generated artifacts is reported separately below.
    if path.startswith("06_Silicon_Index/"):
        return "delete_candidate", "06_Silicon_Index"
    if path.startswith(".ai/"):
        return "delete_candidate", "ai_communication_plane"
    for prefix in DELETE_GROUPS["legacy_content_trees"]:
        if path.startswith(prefix):
            return "delete_candidate", "legacy_content_trees"
    if path in GENERATED_NAV:
        return "delete_candidate", "generated_navigation_root"
    if path in LEGACY_ROOT_DOCS:
        return "delete_candidate", "legacy_root_documents"
    return "UNASSIGNED", ""


def is_generated_artifact(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return path in GENERATED_NAV or name == "index.md"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    out = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True,
        encoding="utf-8", cwd=args.repo_root,
    )
    if out.returncode != 0:
        raise SystemExit(out.stderr.strip())
    tracked = [p for p in out.stdout.splitlines() if p]
    non08 = [p for p in tracked if not p.startswith("01_os/")]

    buckets: Counter[str] = Counter()
    groups: Counter[str] = Counter()
    unassigned: list[str] = []
    for path in non08:
        name, group = bucket(path)
        buckets[name] += 1
        if group:
            groups[group] += 1
        if name == "UNASSIGNED":
            unassigned.append(path)

    print(f"tracked_files_total: {len(tracked)}")
    print(f"tracked_under_01_os: {len(tracked) - len(non08)}")
    print(f"tracked_outside_01_os: {len(non08)}")
    for name in (
        "retain_non_08",
        "migrate_then_delete_source",
        "delete_candidate",
        "Human_decision_required",
        "UNASSIGNED",
    ):
        print(f"  {name}: {buckets[name]}")
    print("delete_candidate groups:")
    for group, count in sorted(groups.items()):
        print(f"  {group}: {count}")
    generated = [p for p in non08 if is_generated_artifact(p)]
    print(f"cross_cutting_generated_navigation_artifacts: {len(generated)}")

    print("declaration_only_entries (classified, zero tracked files):")
    for path, name in sorted(DECLARATION_ONLY.items()):
        present = sum(1 for p in tracked if p.startswith(path))
        print(f"  {path} -> {name}, tracked_files={present}")
        if present:
            unassigned.append(f"{path} declared file-less but has {present} tracked files")
    for path in unassigned:
        print(f"  UNASSIGNED {path}")
    total = sum(buckets[k] for k in buckets)
    print(f"sum_of_buckets: {total} (must equal tracked_outside_01_os)")
    ok = total == len(non08) and not unassigned
    print("RESULT " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

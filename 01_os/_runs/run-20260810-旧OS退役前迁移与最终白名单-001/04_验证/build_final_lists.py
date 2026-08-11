#!/usr/bin/env python3
"""Partition every tracked non-08 path into the final pre-deletion buckets.

Three buckets, and every tracked path outside 01_os/** lands in exactly one:

  final_retain                     survives the retirement unchanged
  deferred_until_root_move_rewrite survives, but names a current 01_os/ path and
                                   must be rewritten when 01_os moves to the root
  final_delete_authorized          Human-approved for direct deletion

The 453 delete candidates from the predecessor run are not re-adjudicated here.
They are reproduced by importing that run's own classifier and taking its
delete_candidate bucket verbatim, so this list cannot quietly drift from the one
that was independently reviewed. The Human additions and the now-migrated sources
are added on top, each named explicitly.

Membership of deferred_until_root_move_rewrite is measured first and then widened
by one named exception. The measurement is: a retained file belongs there if it
literally contains "01_os/", because that string moves when 01_os moves to the
repository root. The measurement alone is not sufficient - new-domain.ps1 needs a
cutover rewrite for the opposite reason, that line 99 still directs new domains to
08_Domain_Applications/ and 03_Daily_Execution/, which are neither current nor
tracked. A file can need rewriting because it names a path that is arriving or
because it names one that is leaving, and only the first is greppable.

Usage
    python build_final_lists.py [--repo-root .] [--out-dir <dir>] [--check-only]
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

PREDECESSOR_CLASSIFIER = (
    "01_os/_runs/run-20260810-根级保留文件重写与依赖盘点-001/07_测试执行/classify_counts.py"
)

# Human decisions carried by this run's task packet, each listed as the exact
# reason it is being deleted rather than as a bare path.
HUMAN_ADDED_DELETES = {
    "01_Research_Reports/": "Human decision: delete without further semantic comparison",
    "PROJECT_CONTEXT.md": "Human decision: delete; describes the previous system",
    "ARCHITECTURE.md": "Human decision: delete; describes the previous system",
    ".ai/HANDOFF_COMMON_CONVENTIONS.md": "Human decision: delete",
}

# Sources whose active dependencies this task removed. Each may only enter the
# delete list because the migration landed, so each carries its proof.
MIGRATED_SOURCE_DELETES = {
    ".ai/REPOSITORY_PUBLISHER_AUTHORITY.yml":
        "M1: authority migrated to 01_os/05_registry/repository_publisher_authority_v1.yml; all six consumers repointed",
    ".ai/TOKEN_USAGE_PROFILE.md":
        "M2: last active pointer removed from the OS entry section 12; discipline already absorbed into AGENT_WORKING_DISCIPLINE.md",
    ".ai/token_profile/":
        "M5: six files copied byte-exact into this run's evidence subtree with blob shas",
    "系统机制总结.md":
        "M4: content migrated to 01_os/03_mechanisms/context_management/依据材料/系统机制总结_历史输入_v1.md; 17 structured refs repointed",
}


# Deferred for a reason no grep for "01_os/" can find: the file names paths that
# are going away rather than paths that are arriving.
EXPLICIT_DEFERRED = {
    "new-domain.ps1":
        "line 99 still directs a new domain to 08_Domain_Applications/ and "
        "03_Daily_Execution/, neither of which is current or tracked; the "
        "post-creation instructions must be revalidated before cutover",
}


def git(*args: str, root: str = ".") -> str:
    out = subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8", cwd=root
    )
    if out.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def load_predecessor(root: Path):
    path = root / PREDECESSOR_CLASSIFIER
    spec = importlib.util.spec_from_file_location("predecessor_classifier", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out-dir", default="")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()

    predecessor = load_predecessor(root)
    tracked = [p for p in git("ls-files", root=str(root)).splitlines() if p]
    non08 = [p for p in tracked if not p.startswith("01_os/")]

    predecessor_delete = []
    predecessor_buckets = {}
    for path in non08:
        name, _group = predecessor.bucket(path)
        predecessor_buckets.setdefault(name, []).append(path)
        if name == "delete_candidate":
            predecessor_delete.append(path)

    delete_reason: dict[str, str] = {}
    for path in predecessor_delete:
        delete_reason[path] = "predecessor run delete_candidate, independently reviewed"
    for prefix, reason in {**HUMAN_ADDED_DELETES, **MIGRATED_SOURCE_DELETES}.items():
        matched = [
            p for p in non08
            if p == prefix or (prefix.endswith("/") and p.startswith(prefix))
        ]
        if not matched:
            print(f"  WARNING no tracked path matches {prefix}")
        for path in matched:
            delete_reason[path] = reason

    final_delete = sorted(delete_reason)
    remaining = [p for p in non08 if p not in delete_reason]

    deferred, retain = [], []
    deferred_reason: dict[str, str] = {}
    for path in remaining:
        try:
            text = (root / path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        if "01_os/" in text:
            deferred.append(path)
            deferred_reason[path] = "names a current 01_os/ path; moves when 01_os moves to the root"
        elif path in EXPLICIT_DEFERRED:
            deferred.append(path)
            deferred_reason[path] = EXPLICIT_DEFERRED[path]
        else:
            retain.append(path)

    problems = []
    if len(predecessor_delete) != 453:
        problems.append(
            f"predecessor delete_candidate reproduced as {len(predecessor_delete)}, expected 453"
        )
    if len(final_delete) + len(retain) + len(deferred) != len(non08):
        problems.append("buckets do not sum to the tracked non-08 file count")
    overlap = (set(final_delete) & set(retain)) | (set(final_delete) & set(deferred))
    if overlap:
        problems.append(f"overlap between delete and keep: {sorted(overlap)[:5]}")
    if set(retain) & set(deferred):
        problems.append("overlap between retain and deferred")
    for path in final_delete:
        if path.startswith("01_os/"):
            problems.append(f"01_os path in delete list: {path}")

    print(f"tracked_outside_01_os: {len(non08)}")
    print(f"predecessor_delete_candidates_reproduced: {len(predecessor_delete)}")
    print(f"final_delete_authorized: {len(final_delete)}")
    print(f"final_retain: {len(retain)}")
    print(f"deferred_until_root_move_rewrite: {len(deferred)}")
    print(f"unassigned: {len(non08) - len(final_delete) - len(retain) - len(deferred)}")
    for item in problems:
        print(f"  PROBLEM {item}")
    print("RESULT " + ("FAIL" if problems else "PASS"))

    if args.out_dir and not problems:
        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        write_delete_list(out / "最终直接删除清单_v1.yml", final_delete, delete_reason)
        write_whitelist(out / "最终非08白名单_v1.yml", retain, deferred, len(non08),
                        len(final_delete), deferred_reason)
        print(f"wrote {out}")

    return 1 if problems else 0


def write_delete_list(path: Path, paths: list[str], reasons: dict[str, str]) -> None:
    lines = [
        "schema_version: citystate.final_delete_list.v1",
        "task_id: os-v2-pre-deletion-migration-final-whitelist-001",
        "run_id: run-20260810-旧OS退役前迁移与最终白名单-001",
        "generated_by: 04_验证/build_final_lists.py",
        "deletion_performed_by_this_task: false",
        "deletion_gate: remains closed until independent review passes",
        "",
        "# Every path below is a tracked file outside 01_os/**, approved by the Human",
        "# for direct deletion. The list is generated, never hand-edited: the",
        "# predecessor's delete candidates are reproduced by importing that run's own",
        "# classifier, so this file cannot drift from the set that was reviewed.",
        "",
        f"count: {len(paths)}",
        "reason_classes:",
        "  predecessor_reviewed: predecessor run delete_candidate, independently reviewed",
        "  human_decision: Human decision recorded in this task packet",
        "  migrated_source: active dependencies removed by this task's M1-M5",
        "",
        "paths:",
    ]
    for item in paths:
        lines.append(f"  - path: {item!r}")
        lines.append(f"    reason: {reasons[item]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_whitelist(path: Path, retain: list[str], deferred: list[str],
                    total: int, deleted: int,
                    deferred_reason: dict[str, str]) -> None:
    lines = [
        "schema_version: citystate.final_retention_whitelist.v1",
        "task_id: os-v2-pre-deletion-migration-final-whitelist-001",
        "run_id: run-20260810-旧OS退役前迁移与最终白名单-001",
        "generated_by: 04_验证/build_final_lists.py",
        "",
        "# What survives outside 01_os/** after the approved deletion runs.",
        "# Deferred membership is measured and then widened by one named exception:",
        "# containing \"01_os/\" is greppable, but new-domain.ps1 needs a cutover",
        "# rewrite because it names paths that are leaving, which no such grep finds.",
        "# Retain here means protected from deletion, never protected from change.",
        "",
        f"tracked_outside_01_os: {total}",
        f"final_delete_authorized: {deleted}",
        f"final_retain: {len(retain)}",
        f"deferred_until_root_move_rewrite: {len(deferred)}",
        "",
        "final_retain:",
    ]
    lines += [f"  - {item!r}" for item in sorted(retain)]
    lines.append("")
    lines.append("deferred_until_root_move_rewrite:")
    for item in sorted(deferred):
        lines.append(f"  - path: {item!r}")
        lines.append(f"    rewrite_reason: {deferred_reason[item]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())

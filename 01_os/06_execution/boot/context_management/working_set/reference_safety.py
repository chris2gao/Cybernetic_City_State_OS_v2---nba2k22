#!/usr/bin/env python3
"""Prove that moving a group would not break a live reference.

Archiving changes paths. Everything in this repository that points at durable
evidence points at it by repository-relative path — completion pointers,
`important_refs`, review adjudications, registry entries. So the only honest
precondition for a move is: enumerate every tracked file outside the group whose
bytes contain the group's path prefix, and report them exactly.

The scan reports paths, never a boolean. A caller that receives "3 referencing
files" can act; a caller that receives "unsafe" cannot.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lifecycle import WorkingSetError  # noqa: E402


def _git(repo_root: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode not in (0, 1):  # 1 = grep found nothing
        raise WorkingSetError("git_command_failed:" + " ".join(args))
    return proc.stdout


def tracked_paths(repo_root: Path) -> list[str]:
    raw = _git(repo_root, "ls-files", "-z")
    return [p.decode("utf-8") for p in raw.split(b"\x00") if p]


def find_live_references(repo_root: Path, group_relpath: str) -> list[str]:
    """Tracked files outside `group_relpath` that mention it.

    `group_relpath` is repository-relative and uses forward slashes, e.g.
    `01_os/_runs/run-20260809-任务纪律工具-001`.
    """
    prefix = group_relpath.rstrip("/")
    if not prefix:
        raise WorkingSetError("reference_scan_prefix_empty")

    raw = _git(repo_root, "grep", "-l", "-I", "-z", "-F", prefix, "--", ".")
    hits = [p.decode("utf-8") for p in raw.split(b"\x00") if p]
    inside = prefix + "/"
    return sorted(h for h in hits if h != prefix and not h.startswith(inside))


def scan(repo_root: Path, group_relpath: str) -> dict[str, object]:
    referencing = find_live_references(repo_root, group_relpath)
    return {
        "group": group_relpath,
        "referencing_paths": referencing,
        "referencing_count": len(referencing),
        "reference_safe": not referencing,
    }

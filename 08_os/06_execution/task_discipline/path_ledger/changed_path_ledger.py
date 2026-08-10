"""Physical changed-path ledger.

Builds the exact set of paths a task actually changed, straight from Git, and
compares it against the task packet's `allowed_changed_paths`. Replaces
hand-maintained path lists in handoff reports.

Why it exists: `git status --porcelain` collapses an untracked directory into a
single entry and, without `core.quotepath=false`, prints non-ASCII paths as octal
escapes. Both make a hand-written ledger silently wrong on this repository, whose
paths are largely Chinese. This tool always uses `-z` (NUL-separated, never quoted)
and always expands untracked directories, so neither setting can change its answer.

Usage
    python changed_path_ledger.py --base <sha> [--head HEAD] [--repo-root .]
                                  [--packet <task packet yaml>] [--json]

Exit codes
    0  ledger produced; if a packet was given, every path is inside the allowlist
    1  at least one changed path falls outside the allowlist
    3  git or input error
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - yaml ships with the repo toolchain
    yaml = None


def matches(pattern: str, path: str) -> bool:
    """Task-packet allowlist semantics.

    `dir/**` covers everything under `dir/`; anything else is an exact path.
    Deliberately narrow: no `*` globbing inside a segment, because an allowlist
    is a permission boundary and a loose matcher silently widens it.
    """
    if pattern.endswith("/**"):
        return path.startswith(pattern[:-2])
    return path == pattern


def _git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} exited {proc.returncode}: "
            f"{proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    return proc.stdout.decode("utf-8")


def committed_paths(repo_root: Path, base: str, head: str) -> set[str]:
    out = _git(repo_root, "diff", "--name-only", "-z", f"{base}..{head}")
    return {p for p in out.split("\0") if p}


def worktree_paths(repo_root: Path) -> set[str]:
    """Staged, unstaged and untracked paths, with untracked directories expanded."""
    out = _git(repo_root, "status", "--porcelain=1", "-z", "--untracked-files=all")
    paths: set[str] = set()
    fields = [f for f in out.split("\0") if f]
    i = 0
    while i < len(fields):
        entry = fields[i]
        status, path = entry[:2], entry[3:]
        if "R" in status or "C" in status:
            # rename/copy: the following NUL field is the source path
            i += 1
            if i < len(fields):
                paths.add(fields[i])
        if path:
            paths.add(path)
        i += 1
    return paths


def classify(paths: set[str], allowlist: list[str]) -> tuple[list[str], list[str]]:
    inside, outside = [], []
    for path in sorted(paths):
        (inside if any(matches(p, path) for p in allowlist) else outside).append(path)
    return inside, outside


def load_allowlist(packet: Path) -> list[str]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read a task packet")
    data = yaml.safe_load(packet.read_text(encoding="utf-8"))
    allowlist = (data or {}).get("allowed_changed_paths")
    if not allowlist:
        raise RuntimeError(f"{packet}: allowed_changed_paths missing or empty")
    return list(allowlist)


def build(repo_root: Path, base: str, head: str, packet: Path | None) -> dict:
    paths = committed_paths(repo_root, base, head) | worktree_paths(repo_root)
    result: dict = {
        "base": base,
        "head": head,
        "path_count": len(paths),
        "paths": sorted(paths),
    }
    if packet is None:
        result["allowlist_checked"] = False
        return result
    allowlist = load_allowlist(packet)
    inside, outside = classify(paths, allowlist)
    result.update(
        allowlist_checked=True,
        allowlist_source=str(packet).replace("\\", "/"),
        allowlist=allowlist,
        inside_count=len(inside),
        outside_allowlist=outside,
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="exact base SHA or ref")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--packet", help="task packet yaml carrying allowed_changed_paths")
    parser.add_argument("--json", action="store_true", help="emit the full ledger as JSON")
    parser.add_argument("--list", action="store_true", help="print every path, one per line")
    args = parser.parse_args(argv)

    try:
        ledger = build(
            Path(args.repo_root).resolve(),
            args.base,
            args.head,
            Path(args.packet) if args.packet else None,
        )
    except (RuntimeError, OSError) as exc:
        print(f"path_ledger_error: {exc}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=False))
    else:
        line = f"paths={ledger['path_count']}"
        if ledger.get("allowlist_checked"):
            outside = ledger["outside_allowlist"]
            line += f" allowlist={'ok' if not outside else f'VIOLATION({len(outside)})'}"
        print(line)
        if args.list:
            for path in ledger["paths"]:
                print(f"  {path}")

    outside = ledger.get("outside_allowlist") or []
    for path in outside:
        print(f"outside_allowlist: {path}", file=sys.stderr)
    return 1 if outside else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Measure where cumulative repository material actually costs an agent.

Run from the repository root:
    python 01_os/_runs/run-20260828-t3-archive-and-big-task-workflow-001/02_测量/measure_working_set.py

The point of this script is to separate three different quantities that are
routinely conflated:

  repository_bytes   how much content exists on disk / in the tree
  listing_bytes      what one full tracked-path enumeration returns
  probe_hits         what an unfiltered content search returns, and how much
                     of it comes from historical evidence rather than from the
                     current canonical surface

Only the last two are agent context cost. A surface can be large and cost
nothing if nothing enumerates or searches it.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SURFACES = [
    "01_os/_runs",
    "01_os/_communication",
    "01_os/_dev",
    "01_os/01_workflow",
    "01_os/02_boot",
    "01_os/03_mechanisms",
    "01_os/04_skills_and_tools",
    "01_os/05_registry",
    "01_os/06_execution",
    "01_os/07_content",
]

# Terms an agent actually searches for while routing a task in this repository.
PROBES = [
    "task_authority",
    "allowed_changed_paths",
    "completion_pointer",
    "archive",
    "registry",
    "risk_tier",
    "hook_guard",
    "lifecycle",
]

BOOTSTRAP_FILES = [
    "CLAUDE.md",
    "AGENTS.md",
    "AGENT_WORKING_DISCIPLINE.md",
    "01_os/README.md",
    "01_os/开发入口与单窗口任务规范_v1.md",
]


def git(*args: str) -> str:
    out = subprocess.run(
        ["git", *args],
        capture_output=True,
        check=True,
    )
    return out.stdout.decode("utf-8", errors="replace")


def tracked_paths() -> list[str]:
    raw = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, check=True
    ).stdout
    return [p.decode("utf-8") for p in raw.split(b"\x00") if p]


def surface_of(path: str) -> str:
    for s in SURFACES:
        if path == s or path.startswith(s + "/"):
            return s
    if "/" not in path:
        return "<repo root>"
    return "<other>"


def blob_sizes(paths: list[str]) -> dict[str, int]:
    """Exact blob byte size per tracked path, from the object database."""
    spec = "".join(f"HEAD:{p}\n" for p in paths).encode("utf-8")
    proc = subprocess.run(
        ["git", "cat-file", "--batch-check=%(objectsize)"],
        input=spec,
        capture_output=True,
        check=True,
    )
    sizes = proc.stdout.decode("utf-8").split("\n")
    result: dict[str, int] = {}
    for path, line in zip(paths, sizes):
        line = line.strip()
        result[path] = int(line) if line.isdigit() else 0
    return result


def probe(term: str, paths_by_surface: dict[str, list[str]]) -> dict[str, int]:
    """Count matching lines per surface for one unfiltered content search."""
    proc = subprocess.run(
        ["git", "grep", "-I", "-c", "-F", term, "HEAD"],
        capture_output=True,
        check=False,
    )
    counts: dict[str, int] = {}
    for line in proc.stdout.decode("utf-8", errors="replace").splitlines():
        # format: HEAD:<path>:<count>
        if not line.startswith("HEAD:"):
            continue
        rest = line[len("HEAD:") :]
        path, _, num = rest.rpartition(":")
        if not num.isdigit():
            continue
        counts[surface_of(path)] = counts.get(surface_of(path), 0) + int(num)
    return counts


def main() -> int:
    root = Path(git("rev-parse", "--show-toplevel").strip())
    head = git("rev-parse", "HEAD").strip()

    paths = tracked_paths()
    sizes = blob_sizes(paths)

    by_surface: dict[str, dict[str, int]] = {}
    paths_by_surface: dict[str, list[str]] = {}
    for p in paths:
        s = surface_of(p)
        rec = by_surface.setdefault(
            s, {"tracked_files": 0, "content_bytes": 0, "path_string_bytes": 0}
        )
        rec["tracked_files"] += 1
        rec["content_bytes"] += sizes.get(p, 0)
        rec["path_string_bytes"] += len(p.encode("utf-8")) + 1
        paths_by_surface.setdefault(s, []).append(p)

    total_files = len(paths)
    total_content = sum(sizes.values())
    total_listing = sum(len(p.encode("utf-8")) + 1 for p in paths)

    # Depth / fan-out of the accumulating surfaces.
    fanout: dict[str, dict[str, int]] = {}
    for s in ("01_os/_runs", "01_os/_communication", "01_os/_dev"):
        children = set()
        max_depth = 0
        for p in paths_by_surface.get(s, []):
            tail = p[len(s) + 1 :]
            children.add(tail.split("/")[0])
            max_depth = max(max_depth, tail.count("/") + 1)
        fanout[s] = {
            "top_level_groups": len(children),
            "max_depth_below_surface": max_depth,
        }

    probes = {t: probe(t, paths_by_surface) for t in PROBES}

    bootstrap = {}
    for f in BOOTSTRAP_FILES:
        blob = root / f
        if blob.exists():
            data = blob.read_bytes()
            bootstrap[f] = {
                "bytes": len(data),
                "lines": data.count(b"\n") + 1,
            }
        else:
            bootstrap[f] = {"bytes": 0, "lines": 0, "missing": True}

    report = {
        "head": head,
        "totals": {
            "tracked_files": total_files,
            "content_bytes": total_content,
            "full_listing_bytes": total_listing,
        },
        "by_surface": by_surface,
        "fanout": fanout,
        "probes": probes,
        "bootstrap_default_load": bootstrap,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

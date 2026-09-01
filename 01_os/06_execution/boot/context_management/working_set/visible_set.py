#!/usr/bin/env python3
"""Compute the default-visible working set, and say exactly what it hid.

Why this exists rather than a `.ignore` line: a global silent exclusion turns
90% enumeration noise into false negatives, and a caller who receives an empty
result cannot tell filtering from absence. This tool therefore always reports
the excluded counts alongside the result, and never lets a filtered listing be
presented as exhaustive.

Usage from the repository root:

    # what a task should see by default
    python 01_os/06_execution/boot/context_management/working_set/visible_set.py --list

    # the widening switch, when history is actually the subject
    python .../working_set/visible_set.py --list --include-hidden

    # before/after enumeration cost
    python .../working_set/visible_set.py --measure

    # machine-readable index of every accumulating group and its state
    python .../working_set/visible_set.py --index
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lifecycle import OPEN, TERMINAL, UNKNOWN, GroupState, read_group_state  # noqa: E402
from reference_safety import tracked_paths  # noqa: E402

# Mirrors accumulating_surfaces in
# 01_os/03_mechanisms/context_management/工作集与归档契约_v1.yml
HIDDEN_SURFACES: tuple[tuple[str, str | None, str], ...] = (
    # (root, state_file, state_field)
    ("01_os/07_content/_runs/", "run.yml", "lifecycle"),
    ("01_os/_runs/", "run.yml", "lifecycle"),
    ("01_os/_dev/", None, "lifecycle"),
)

# The communication surface keeps its own archiver and discovery file; this tool
# treats it as hidden-by-default but does not classify its task states.
COMMUNICATION_ROOT = "01_os/_communication/"

RESERVED_GROUP_NAMES = frozenset({"_archive", "_index", "_runtime"})

# Which lifecycle classifications are visible by default.
#
# UNKNOWN is visible. That is the whole point of the distinction and it was got
# wrong once: an earlier revision hid UNKNOWN alongside TERMINAL, which meant the
# 68 groups whose state the tree cannot vouch for were the ones being treated as
# history, and most of the reported visibility gain came from hiding exactly
# them. A group is hidden only after it has been positively classified as
# finished against the declared enum. Unclassifiable is not finished.
#
# Visible and archivable are different questions. UNKNOWN is visible here and
# still non-archivable in archive_group.py, which requires exact TERMINAL.
DEFAULT_VISIBLE_CLASSIFICATIONS = frozenset({OPEN, UNKNOWN})
DEFAULT_HIDDEN_CLASSIFICATIONS = frozenset({TERMINAL})

INDEX_PATH = "01_os/_runs/_index/工作集索引_v1.yml"


def _surface_of(path: str) -> tuple[str, str | None, str] | None:
    for root, state_file, state_field in HIDDEN_SURFACES:
        if path.startswith(root):
            return root, state_file, state_field
    return None


def _group_id(path: str, root: str) -> str:
    return path[len(root) :].split("/")[0]


def collect_groups(repo_root: Path, paths: list[str]) -> dict[str, GroupState]:
    """One GroupState per accumulating group present in the tracked tree."""
    seen: dict[str, tuple[str, str | None, str]] = {}
    for path in paths:
        surface = _surface_of(path)
        if surface is None:
            continue
        root, state_file, state_field = surface
        gid = _group_id(path, root)
        if not gid or gid in RESERVED_GROUP_NAMES:
            continue
        seen.setdefault(root + gid, surface)

    groups: dict[str, GroupState] = {}
    for relpath, (_root, state_file, state_field) in sorted(seen.items()):
        groups[relpath] = read_group_state(
            repo_root / relpath, state_file=state_file, state_field=state_field
        )
    return groups


def _is_archived(relpath: str) -> bool:
    return "/_archive/" in relpath or relpath.endswith("/_archive")


def partition(
    repo_root: Path, paths: list[str], groups: dict[str, GroupState]
) -> dict[str, list[str]]:
    """Split tracked paths into visible and hidden.

    Open and unknown groups stay visible; only a group positively classified as
    terminal, or already sitting under an archive root, is hidden. Hiding
    requires proof that the work is finished, not the absence of proof that it
    is live.
    """
    visible_groups = {
        rel
        for rel, st in groups.items()
        if st.classification in DEFAULT_VISIBLE_CLASSIFICATIONS
    }
    visible: list[str] = []
    hidden: list[str] = []
    for path in paths:
        if path.startswith(COMMUNICATION_ROOT):
            hidden.append(path)
            continue
        surface = _surface_of(path)
        if surface is None:
            visible.append(path)
            continue
        root, _sf, _sfield = surface
        gid = _group_id(path, root)
        relgroup = root + gid
        if gid in RESERVED_GROUP_NAMES or _is_archived(path):
            hidden.append(path)
        elif relgroup in visible_groups:
            visible.append(path)
        else:
            hidden.append(path)
    return {"visible": visible, "hidden": hidden}


def _listing_bytes(paths: list[str]) -> int:
    return sum(len(p.encode("utf-8")) + 1 for p in paths)


def build_report(repo_root: Path) -> dict[str, object]:
    paths = tracked_paths(repo_root)
    groups = collect_groups(repo_root, paths)
    split = partition(repo_root, paths, groups)

    by_class: dict[str, list[str]] = {OPEN: [], TERMINAL: [], UNKNOWN: []}
    for rel, st in groups.items():
        by_class[st.classification].append(rel)

    full_bytes = _listing_bytes(paths)
    visible_bytes = _listing_bytes(split["visible"])
    return {
        "tracked_files": len(paths),
        "visible_files": len(split["visible"]),
        "hidden_files": len(split["hidden"]),
        "full_listing_bytes": full_bytes,
        "visible_listing_bytes": visible_bytes,
        "excluded_listing_bytes": full_bytes - visible_bytes,
        "excluded_fraction": (
            round((full_bytes - visible_bytes) / full_bytes, 4) if full_bytes else 0.0
        ),
        "groups_total": len(groups),
        "groups_open": sorted(by_class[OPEN]),
        "groups_terminal": sorted(by_class[TERMINAL]),
        "groups_unknown_state": sorted(by_class[UNKNOWN]),
        "groups_default_visible": sorted(by_class[OPEN] + by_class[UNKNOWN]),
        "groups_default_hidden": sorted(by_class[TERMINAL]),
        # Visible and archivable are different questions, and the report says so
        # rather than leaving a reader to infer that a visible group is live.
        "unknown_state_groups_default_visible": True,
        "unknown_state_groups_archivable": False,
        "communication_surface_policy": "delegated_to_communication_navigation_archive_contract",
        "filtered_result_is_not_exhaustive": True,
    }


def build_index(repo_root: Path, head: str | None = None) -> dict[str, object]:
    report = build_report(repo_root)
    return {
        "schema_version": "context_management.working_set_index.v1",
        "generated_from_sha": head,
        "index_is_not_authority": True,
        "authority_is_physical_tree": True,
        # Visible carries open and unknown; hidden carries only what has been
        # positively classified as finished.
        "visible_groups": report["groups_default_visible"],
        "hidden_groups": report["groups_default_hidden"],
        "archived_groups": [],
        # Unknown groups are reported separately as well, because "visible" must
        # not be read as "classified".
        "unknown_state_groups": report["groups_unknown_state"],
        "unknown_state_groups_default_visible": True,
        "unknown_state_groups_archivable": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--include-hidden", action="store_true")
    parser.add_argument("--measure", action="store_true")
    parser.add_argument("--index", action="store_true")
    parser.add_argument("--head")
    args = parser.parse_args()

    root = args.repository_root.resolve()
    if not (root / ".git").exists() and not (root / ".git").is_file():
        print("working_set_rejected:not_a_repository_root", file=sys.stderr)
        return 3

    if args.index:
        print(json.dumps(build_index(root, args.head), ensure_ascii=False, indent=2))
        return 0

    if args.measure:
        print(json.dumps(build_report(root), ensure_ascii=False, indent=2))
        return 0

    if args.list:
        paths = tracked_paths(root)
        groups = collect_groups(root, paths)
        split = partition(root, paths, groups)
        chosen = paths if args.include_hidden else split["visible"]
        for path in chosen:
            print(path)
        # Never let a filtered listing pass as exhaustive.
        if args.include_hidden:
            print(f"# widened: all {len(paths)} tracked paths listed", file=sys.stderr)
        else:
            print(
                f"# default working set: {len(split['visible'])} listed, "
                f"{len(split['hidden'])} hidden "
                f"({_listing_bytes(split['hidden'])} bytes of path text). "
                f"Hidden means positively classified as finished, or already "
                f"archived, or the delegated communication surface; groups whose "
                f"lifecycle is unknown are listed, not hidden. "
                f"Re-run with --include-hidden when history is the subject.",
                file=sys.stderr,
            )
        return 0

    parser.print_help()
    return 3


if __name__ == "__main__":
    raise SystemExit(main())

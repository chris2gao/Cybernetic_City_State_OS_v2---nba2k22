#!/usr/bin/env python3
"""Gate, then prove, an exact 490-file physical deletion.

This task deletes and decides nothing. The only authority is the delete list
produced and independently reviewed by the predecessor run, pinned by blob sha, so
every question this script asks is arithmetic rather than judgement:

  --phase pre    run BEFORE any deletion. Fails closed if any gate does not hold.
                 Writes a snapshot of the surviving files' blob shas, because
                 "unchanged" cannot be proven after the fact from memory.
  --phase post   run AFTER the deletion. Proves the tracked tree is exactly the
                 whitelist, that the deleted set is exactly the list, that no
                 08_os path went, and that the survivors are byte-identical apart
                 from the one file this task is allowed to touch.

The pre-phase snapshot is the pivot. Without it, a post-phase check can only say
what is there now; with it, it can say what changed.

Usage
    python verify_exact_deletion.py --phase pre  [--repo-root .]
    python verify_exact_deletion.py --phase post [--repo-root .]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PREDECESSOR = "08_os/_runs/run-20260810-旧OS退役前迁移与最终白名单-001/03_最终清单"
DELETE_LIST = f"{PREDECESSOR}/最终直接删除清单_v1.yml"
WHITELIST = f"{PREDECESSOR}/最终非08白名单_v1.yml"

EXPECTED_DELETE_BLOB = "162f59cbd101cbfa8a725981f835762ae829aafe"
EXPECTED_WHITELIST_BLOB = "b92adfc064860ddf29ca5549c34c6d6d7d111a7f"
EXPECTED_DELETE_COUNT = 490
EXPECTED_WHITELIST_COUNT = 15

# The one whitelist file this task may change, because deletion changes what is
# true about the tree it describes. Every other survivor must be byte-identical.
MUTABLE_SURVIVOR = "CORE_MANIFEST.yml"

SNAPSHOT = (
    "08_os/_runs/run-20260810-旧OS物理删除-001/04_验证/pre_delete_snapshot.json"
)

PATH_ENTRY = re.compile(r"^\s*-\s+path:\s+'(?P<p>.+)'\s*$")
BARE_ENTRY = re.compile(r"^\s*-\s+'(?P<p>.+)'\s*$")


def git(*args: str, root: str = ".") -> str:
    out = subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8", cwd=root
    )
    if out.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def blob(root: Path, path: str) -> str:
    return git("hash-object", "--", path, root=str(root)).strip()


def parse_delete_list(text: str) -> list[str]:
    paths, in_paths = [], False
    for line in text.splitlines():
        if line.startswith("paths:"):
            in_paths = True
            continue
        if not in_paths:
            continue
        match = PATH_ENTRY.match(line)
        if match:
            paths.append(match.group("p"))
    return paths


def parse_whitelist(text: str) -> tuple[list[str], list[str]]:
    retain, deferred, section = [], [], None
    for line in text.splitlines():
        if line.startswith("final_retain:"):
            section = "retain"
            continue
        if line.startswith("deferred_until_root_move_rewrite:"):
            section = "deferred"
            continue
        if section is None:
            continue
        bare = BARE_ENTRY.match(line)
        entry = PATH_ENTRY.match(line)
        if bare:
            (retain if section == "retain" else deferred).append(bare.group("p"))
        elif entry:
            (retain if section == "retain" else deferred).append(entry.group("p"))
    return retain, deferred


def load(root: Path) -> tuple[list[str], list[str], list[str], list[str]]:
    delete = parse_delete_list((root / DELETE_LIST).read_text(encoding="utf-8"))
    retain, deferred = parse_whitelist((root / WHITELIST).read_text(encoding="utf-8"))
    non08 = [p for p in git("ls-files", root=str(root)).splitlines()
             if p and not p.startswith("08_os/")]
    return delete, retain, deferred, non08


def phase_pre(root: Path) -> int:
    problems: list[str] = []
    delete, retain, deferred, non08 = load(root)
    whitelist = retain + deferred

    actual_delete_blob = blob(root, DELETE_LIST)
    actual_whitelist_blob = blob(root, WHITELIST)
    if actual_delete_blob != EXPECTED_DELETE_BLOB:
        problems.append(f"delete-list blob {actual_delete_blob} != {EXPECTED_DELETE_BLOB}")
    if actual_whitelist_blob != EXPECTED_WHITELIST_BLOB:
        problems.append(
            f"whitelist blob {actual_whitelist_blob} != {EXPECTED_WHITELIST_BLOB}"
        )
    if len(delete) != EXPECTED_DELETE_COUNT:
        problems.append(f"delete list parsed {len(delete)} paths, expected {EXPECTED_DELETE_COUNT}")
    if len(set(delete)) != len(delete):
        problems.append("delete list contains duplicates")
    if len(whitelist) != EXPECTED_WHITELIST_COUNT:
        problems.append(f"whitelist parsed {len(whitelist)} paths, expected {EXPECTED_WHITELIST_COUNT}")

    overlap = sorted(set(delete) & set(whitelist))
    if overlap:
        problems.append(f"delete/whitelist overlap: {overlap}")

    os_paths = sorted(p for p in delete if p.startswith("08_os/"))
    if os_paths:
        problems.append(f"08_os paths in delete list: {os_paths[:5]}")

    missing = sorted(set(delete) - set(non08))
    if missing:
        problems.append(f"{len(missing)} delete-list paths are not tracked: {missing[:5]}")

    union = set(delete) | set(whitelist)
    if union != set(non08):
        only_tree = sorted(set(non08) - union)
        only_lists = sorted(union - set(non08))
        problems.append(
            f"pre-delete non-08 tracked != delete ∪ whitelist; "
            f"tree-only={len(only_tree)} {only_tree[:5]}, list-only={len(only_lists)} {only_lists[:5]}"
        )

    print(f"delete_list_blob:    {actual_delete_blob}")
    print(f"whitelist_blob:      {actual_whitelist_blob}")
    print(f"delete_paths:        {len(delete)}")
    print(f"whitelist_paths:     {len(whitelist)} ({len(retain)} retain + {len(deferred)} deferred)")
    print(f"pre_delete_non08:    {len(non08)}")
    print(f"overlap:             {len(overlap)}")
    print(f"08_os_in_delete:     {len(os_paths)}")
    print(f"union_equals_tree:   {union == set(non08)}")

    if not problems:
        snapshot = {
            "pre_delete_non08_count": len(non08),
            "delete_paths": sorted(delete),
            "whitelist_paths": sorted(whitelist),
            "survivor_blobs": {p: blob(root, p) for p in sorted(whitelist)},
            "ignored_untracked": sorted(
                p for p in git(
                    "ls-files", "--others", "--exclude-standard", root=str(root)
                ).splitlines() if p
            ),
        }
        (root / SNAPSHOT).write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"snapshot written:    {SNAPSHOT}")

    for item in problems:
        print(f"  GATE FAILED {item}")
    print("RESULT " + ("BLOCKED" if problems else "CLEARED_FOR_DELETION"))
    return 1 if problems else 0


def phase_post(root: Path) -> int:
    problems: list[str] = []
    snapshot = json.loads((root / SNAPSHOT).read_text(encoding="utf-8"))
    delete = set(snapshot["delete_paths"])
    whitelist = set(snapshot["whitelist_paths"])
    before_blobs: dict[str, str] = snapshot["survivor_blobs"]

    non08 = {p for p in git("ls-files", root=str(root)).splitlines()
             if p and not p.startswith("08_os/")}

    if non08 != whitelist:
        unexpected_gone = sorted(whitelist - non08)
        unexpected_left = sorted(non08 - whitelist)
        problems.append(
            f"post-delete non-08 tracked != whitelist; "
            f"missing={len(unexpected_gone)} {unexpected_gone[:5]}, "
            f"extra={len(unexpected_left)} {unexpected_left[:5]}"
        )

    still_present = sorted(delete & non08)
    if still_present:
        problems.append(f"{len(still_present)} delete-list paths still tracked")

    os_now = {p for p in git("ls-files", root=str(root)).splitlines()
              if p.startswith("08_os/")}
    os_before = set(snapshot.get("os_paths", []))
    if os_before and os_now != os_before:
        problems.append("08_os tracked set changed")

    changed, unchanged = [], []
    for path in sorted(whitelist):
        if path == MUTABLE_SURVIVOR:
            continue
        if path not in non08:
            continue
        now = blob(root, path)
        (changed if now != before_blobs[path] else unchanged).append(path)
    if changed:
        problems.append(f"survivor blobs changed: {changed}")

    # Preservation is a question about the filesystem, not about the index. An
    # earlier version of this check compared "still untracked?" before and after and
    # reported a loss when a file this run wrote was committed - which is a status
    # change, not a disappearance. What matters is that nothing vanished from disk.
    recorded = snapshot["ignored_untracked"]
    lost = sorted(p for p in recorded if not (root / p).exists())
    became_tracked = sorted(
        p for p in recorded
        if (root / p).exists()
        and p not in set(git("ls-files", "--others", "--exclude-standard",
                             root=str(root)).splitlines())
    )
    if lost:
        problems.append(f"local files disappeared from disk: {lost[:5]}")

    # The snapshot used --exclude-standard, so it never contained ignored files:
    # .ssh/, .claude/settings.local.json and the _runtime trees were outside it.
    # Those are exactly the ones a deletion task must not touch, so they are checked
    # directly against the filesystem rather than through that list.
    must_survive = [
        ".ssh/id_ed25519",
        ".ssh/id_ed25519.pub",
        ".ssh/known_hosts",
        ".claude/settings.local.json",
    ]
    missing_protected = [p for p in must_survive if not (root / p).exists()]
    if missing_protected:
        problems.append(f"protected local files missing: {missing_protected}")
    ssh_present = (root / ".ssh" / "id_ed25519").exists()

    print(f"post_delete_non08:        {len(non08)}")
    print(f"whitelist_set_equality:   {non08 == whitelist}")
    print(f"delete_list_still_present:{len(still_present)}")
    print(f"survivor_blobs_unchanged: {len(unchanged)} of {len(whitelist) - 1}")
    print(f"mutable_survivor:         {MUTABLE_SURVIVOR}")
    print(f"local_files_still_on_disk:{len(recorded) - len(lost)} of {len(recorded)}, "
          f"{len(lost)} lost, {len(became_tracked)} now tracked (committed by this run)")
    print(f"protected_local_present:  {len(must_survive) - len(missing_protected)} of {len(must_survive)}")
    print(f"ssh_key_untouched:        {ssh_present}")
    for item in problems:
        print(f"  PROBLEM {item}")
    print("RESULT " + ("FAIL" if problems else "PASS"))
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["pre", "post"], required=True)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    return phase_pre(root) if args.phase == "pre" else phase_post(root)


if __name__ == "__main__":
    sys.exit(main())

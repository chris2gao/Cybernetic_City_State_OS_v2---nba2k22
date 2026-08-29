#!/usr/bin/env python3
"""Archive one accumulating group, or refuse and say exactly why.

Archive is a move, never a deletion, and this module makes no secure-erasure
claim: the group's commits stay reachable from the branch that carried them.

Four conditions must all hold, and each is read from the physical tree rather
than accepted from the caller:

  1. the group's lifecycle state is literally one of the declared terminal values
  2. a closure record is declared, resolves inside the group, and carries a
     closure key
  3. no tracked file outside the group references the group's path
  4. the group contains no tracked private runtime

There is deliberately no force flag. The contract states that an unresolved live
reference blocks and that rebinding without proof is prohibited, so an override
here would be a way to violate the contract while appearing to satisfy it.

Usage:

    python .../archive_group.py --repository-root . \
        --group 01_os/_runs/run-20260809-example-001
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lifecycle import (  # noqa: E402
    TERMINAL,
    WorkingSetError,
    read_group_state,
    validate_closure_record,
)
from reference_safety import scan  # noqa: E402

PRIVATE_RUNTIME_NAMES = ("_runtime", "private_runtime")


def _tracked_under(repo_root: Path, relpath: str) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "-z", "--", relpath],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise WorkingSetError("git_ls_files_failed")
    return [p.decode("utf-8") for p in proc.stdout.split(b"\x00") if p]


def _assert_no_tracked_private_runtime(repo_root: Path, group_rel: str) -> None:
    for name in PRIVATE_RUNTIME_NAMES:
        hits = _tracked_under(repo_root, f"{group_rel}/**/{name}")
        hits += _tracked_under(repo_root, f"{group_rel}/{name}")
        if hits:
            raise WorkingSetError(
                "tracked_private_runtime_inside_group:" + hits[0]
            )


def _archive_target(group_rel: str, archive_root: str | None) -> str:
    parts = group_rel.rstrip("/").split("/")
    group_id = parts[-1]
    root = archive_root or "/".join(parts[:-1]) + "/_archive"
    return f"{root.rstrip('/')}/{group_id}"


def archive_group(
    repo_root: Path,
    group_rel: str,
    *,
    archive_root: str | None = None,
) -> dict[str, object]:
    root = repo_root.resolve()
    group_rel = group_rel.strip().rstrip("/").replace("\\", "/")
    if not group_rel or group_rel.startswith("/") or ".." in group_rel.split("/"):
        raise WorkingSetError("group_path_invalid")

    source = (root / group_rel).resolve()
    target_rel = _archive_target(group_rel, archive_root)
    target = (root / target_rel).resolve()
    for path in (source, target):
        try:
            path.relative_to(root)
        except ValueError:
            raise WorkingSetError("group_path_outside_repository") from None

    trace: list[str] = []

    # Idempotence: already archived is success, not an error. A cleanup that
    # cannot be re-run is a cleanup nobody runs twice, and half-finished states
    # are exactly what needs re-running.
    if not source.is_dir() and target.is_dir():
        return {
            "group": group_rel,
            "archived_path": target_rel,
            "already_archived": True,
            "moved": False,
            "operation_trace": ["already_archived"],
            "secure_erasure_claim": False,
        }
    if not source.is_dir():
        raise WorkingSetError(f"group_not_found:{group_rel}")
    if target.exists():
        raise WorkingSetError(f"archive_target_occupied:{target_rel}")

    state = read_group_state(source)
    if state.classification != TERMINAL:
        raise WorkingSetError(
            f"group_state_not_terminal:{group_rel}:"
            f"{state.state_raw or '<none>'}:{state.classification}"
        )
    trace.append("terminal_state_verified")

    closure_ref = validate_closure_record(state)
    trace.append("closure_record_verified")

    _assert_no_tracked_private_runtime(root, group_rel)
    trace.append("no_tracked_private_runtime")

    reference = scan(root, group_rel)
    if not reference["reference_safe"]:
        raise WorkingSetError(
            "live_references_block_archive:"
            + ",".join(reference["referencing_paths"][:10])
        )
    trace.append("reference_safety_verified")

    target.parent.mkdir(parents=True, exist_ok=True)
    os.replace(source, target)
    trace.append("group_moved")

    return {
        "group": group_rel,
        "archived_path": target_rel,
        "already_archived": False,
        "moved": True,
        "terminal_state": state.state_raw,
        "closure_record_ref": closure_ref,
        "referencing_count": reference["referencing_count"],
        "operation_trace": trace,
        "secure_erasure_claim": False,
        "git_history_remains_reachable": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--group", required=True)
    parser.add_argument("--archive-root")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        if args.dry_run:
            root = args.repository_root.resolve()
            group_rel = args.group.strip().rstrip("/").replace("\\", "/")
            state = read_group_state(root / group_rel)
            reference = scan(root, group_rel)
            result: dict[str, object] = {
                "group": group_rel,
                "dry_run": True,
                "state_raw": state.state_raw,
                "classification": state.classification,
                "closure_record_ref": state.closure_record_ref,
                "referencing_count": reference["referencing_count"],
                "referencing_paths": reference["referencing_paths"][:20],
                "eligible": state.classification == TERMINAL
                and bool(state.closure_record_ref)
                and bool(reference["reference_safe"]),
            }
        else:
            result = archive_group(
                args.repository_root, args.group, archive_root=args.archive_root
            )
    except (WorkingSetError, OSError) as exc:
        print(f"archive_rejected:{exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

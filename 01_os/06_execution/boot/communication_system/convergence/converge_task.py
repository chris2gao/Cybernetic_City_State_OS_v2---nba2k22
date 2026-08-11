#!/usr/bin/env python3
"""Converge explicit task paths once; divergence is surfaced, never repaired automatically."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any


class ConvergenceError(RuntimeError):
    def __init__(self, failure_code: str, **evidence: Any):
        self.report = {
            "failure_code": failure_code,
            "conflict_paths": evidence.pop("conflict_paths", []),
            "next_owner": "task_navigation_owner",
            "Human_escalation_required": True,
            **evidence,
        }
        super().__init__(failure_code)


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode:
        raise ConvergenceError(
            "GIT_COMMAND_FAILED", argv=["git", *args], return_code=result.returncode,
            stderr=result.stderr.strip(),
        )
    return result


def _head(repo: Path, ref: str) -> str:
    return _git(repo, "rev-parse", ref).stdout.strip()


def _is_ancestor(repo: Path, older: str, newer: str) -> bool:
    return _git(repo, "merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def _validate_paths(paths: list[str], allowed_task_root: str) -> None:
    root = PurePosixPath(allowed_task_root)
    if root.is_absolute() or ".." in root.parts:
        raise ConvergenceError("INVALID_TASK_ROOT")
    if not paths:
        raise ConvergenceError("NO_EXACT_PATHS")
    for value in paths:
        path = PurePosixPath(value)
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ConvergenceError("PATH_OUTSIDE_TASK_ROOT", conflict_paths=[value]) from exc
        if path.is_absolute() or ".." in path.parts or any(ch in value for ch in "*?"):
            raise ConvergenceError("NON_EXACT_PATH", conflict_paths=[value])


def converge(repo: Path, branch: str, paths: list[str], allowed_task_root: str,
             commit_message: str) -> dict[str, Any]:
    repo = repo.resolve()
    _validate_paths(paths, allowed_task_root)
    status_lines = _git(repo, "status", "--porcelain", "--untracked-files=all").stdout.splitlines()
    dirty_paths = [line[3:].replace("\\", "/") for line in status_lines if len(line) >= 4]
    unexpected = sorted(set(dirty_paths) - set(paths))
    if unexpected:
        raise ConvergenceError("UNAUTHORIZED_DIRTY_PATH", conflict_paths=unexpected)
    _git(repo, "fetch", "origin", branch)
    local_before = _head(repo, "HEAD")
    remote_fetched = _head(repo, "FETCH_HEAD")
    if _is_ancestor(repo, local_before, remote_fetched):
        if local_before != remote_fetched:
            ff = _git(repo, "merge", "--ff-only", "FETCH_HEAD", check=False)
            if ff.returncode:
                raise ConvergenceError(
                    "FAST_FORWARD_BLOCKED_BY_LOCAL_PATH", local_head=local_before,
                    remote_head=remote_fetched, conflict_paths=dirty_paths,
                )
    elif not _is_ancestor(repo, remote_fetched, local_before):
        raise ConvergenceError(
            "NON_FAST_FORWARD", local_head=local_before, remote_head=remote_fetched,
        )
    for path in paths:
        _git(repo, "add", "--", path)
    staged = _git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
    if staged:
        _git(repo, "commit", "-m", commit_message, "--", *paths)
    candidate = _head(repo, "HEAD")
    remote_line = _git(repo, "ls-remote", "origin", f"refs/heads/{branch}").stdout.strip()
    remote_now = remote_line.split()[0] if remote_line else None
    if remote_now != remote_fetched:
        raise ConvergenceError(
            "REMOTE_CHANGED_AFTER_FETCH", local_head=candidate, remote_head=remote_now,
        )
    push = _git(repo, "push", "origin", f"HEAD:refs/heads/{branch}", check=False)
    if push.returncode:
        raise ConvergenceError(
            "NON_FAST_FORWARD", local_head=candidate, remote_head=remote_now,
            push_return_code=push.returncode,
        )
    readback_line = _git(repo, "ls-remote", "origin", f"refs/heads/{branch}").stdout.strip()
    readback = readback_line.split()[0] if readback_line else None
    if readback != candidate:
        raise ConvergenceError("REMOTE_READBACK_MISMATCH", local_head=candidate, remote_head=readback)
    return {
        "status": "converged", "local_head": candidate, "remote_head": readback,
        "staged_paths": staged, "push_attempt_count": 1,
    }


def observe_same_path_conflict(repo: Path, branch: str = "master") -> dict[str, Any]:
    repo = repo.resolve()
    _git(repo, "fetch", "origin", branch)
    before = _head(repo, "HEAD")
    argv = ["git", "merge", "--no-edit", f"origin/{branch}"]
    merge = _git(repo, *argv[1:], check=False)
    unresolved = sorted(
        _git(repo, "diff", "--name-only", "--diff-filter=U", check=False).stdout.splitlines()
    )
    observation = {
        "structured_command_trace": True,
        "merge_argv": argv,
        "merge_return_code": merge.returncode,
        "observed_unresolved_paths": unresolved,
        "emitted_conflict_paths": list(unresolved),
        "continuation_commit_created": _head(repo, "HEAD") != before,
        "push_attempt_count": 0,
        "push_attempts": [],
        "operation_stopped": True,
        "next_owner": "task_navigation_owner",
        "Human_escalation_required": True,
    }
    _git(repo, "merge", "--abort", check=False)
    return observation


def observe_non_fast_forward(repo: Path, branch: str = "master") -> dict[str, Any]:
    repo = repo.resolve()
    remote_ref = f"refs/heads/{branch}"
    before_line = _git(repo, "ls-remote", "origin", remote_ref).stdout.strip()
    before = before_line.split()[0] if before_line else None
    argv = ["git", "push", "origin", branch]
    pushed = _git(repo, *argv[1:], check=False)
    after_line = _git(repo, "ls-remote", "origin", remote_ref).stdout.strip()
    after = after_line.split()[0] if after_line else None
    return {
        "structured_command_trace": True,
        "push_attempts": [{"argv": argv, "return_code": pushed.returncode}],
        "retry_count": 0,
        "remote_head_before": before,
        "remote_head_after": after,
        "route": ["task_navigation_owner", "Human"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--allowed-task-root", required=True)
    parser.add_argument("--path", action="append", required=True)
    parser.add_argument("--commit-message", required=True)
    args = parser.parse_args()
    try:
        result = converge(args.repo, args.branch, args.path, args.allowed_task_root,
                          args.commit_message)
    except ConvergenceError as exc:
        print(json.dumps(exc.report, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

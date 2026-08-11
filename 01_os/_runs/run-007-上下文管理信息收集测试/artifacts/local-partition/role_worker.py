#!/usr/bin/env python3
"""Fresh-process worker for the local context-partition experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def resolve_inside(workspace: Path, relative_path: str) -> Path:
    candidate = (workspace / relative_path).resolve()
    root = workspace.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"reference escapes workspace: {relative_path}")
    return candidate


def load_authorized(
    workspace: Path,
    entry: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    loaded: dict[str, dict[str, Any]] = {}
    read_paths: list[str] = []
    for ref in entry["authorized_refs"]:
        relative_path = ref["path"]
        path = resolve_inside(workspace, relative_path)
        actual_hash = sha256_file(path)
        if actual_hash != ref["sha256"]:
            raise ValueError(
                f"authorized ref hash mismatch: {relative_path}: "
                f"{ref['sha256']} != {actual_hash}"
            )
        loaded[relative_path] = load_json(path)
        read_paths.append(relative_path)
    return loaded, read_paths


def run_executor(entry_path: Path, entry: dict[str, Any], workspace: Path) -> int:
    loaded, read_paths = load_authorized(workspace, entry)
    planner_path = "published/planner_to_executor.json"
    input_path = "fixtures/authorized_input_v1.json"
    test_path = "fixtures/test_spec_v1.json"
    planner = loaded[planner_path]
    input_payload = loaded[input_path]
    test_spec = loaded[test_path]

    if planner["task_id"] != entry["task_id"]:
        raise ValueError("planner handoff task mismatch")
    if planner["input_version"] != entry["input_version"]:
        raise ValueError("planner handoff input version mismatch")

    result = sum(input_payload["values"])
    passed = result == test_spec["expected_result"]
    output_path = resolve_inside(workspace, entry["output_path"])
    write_json(
        output_path,
        {
            "schema_version": "local_partition.executor_restore_result.v1",
            "task_id": entry["task_id"],
            "role": "executor",
            "status": "passed" if passed else "failed",
            "current_step": entry["current_step"],
            "deterministic_operation": test_spec["operation"],
            "result": result,
            "expected_result": test_spec["expected_result"],
            "read_paths": read_paths,
            "unauthorized_paths_read": [],
            "entry_path": entry_path.relative_to(workspace).as_posix(),
        },
    )
    return 0 if passed else 2


def run_reviewer(entry_path: Path, entry: dict[str, Any], workspace: Path) -> int:
    loaded, read_paths = load_authorized(workspace, entry)
    handoff_path = "published/executor_to_reviewer.json"
    test_path = "fixtures/test_spec_v1.json"
    implementation_path = "published/implementation.json"
    handoff = loaded[handoff_path]
    test_spec = loaded[test_path]
    implementation = loaded[implementation_path]

    passed = (
        handoff["task_id"] == entry["task_id"]
        and handoff["status"] == "passed"
        and implementation["operation"] == test_spec["operation"]
        and implementation["result"] == test_spec["expected_result"]
    )
    output_path = resolve_inside(workspace, entry["output_path"])
    write_json(
        output_path,
        {
            "schema_version": "local_partition.reviewer_verdict.v1",
            "task_id": entry["task_id"],
            "role": "reviewer",
            "status": "passed" if passed else "failed",
            "verdict": "accept" if passed else "reject",
            "read_paths": read_paths,
            "unauthorized_paths_read": [],
            "entry_path": entry_path.relative_to(workspace).as_posix(),
        },
    )
    return 0 if passed else 3


def run_stale(entry_path: Path, entry: dict[str, Any], workspace: Path) -> int:
    comparisons: list[dict[str, Any]] = []
    for dependency in entry["dependencies"]:
        path = resolve_inside(workspace, dependency["path"])
        actual_hash = sha256_file(path)
        comparisons.append(
            {
                "path": dependency["path"],
                "expected_sha256": dependency["sha256"],
                "actual_sha256": actual_hash,
                "stale": actual_hash != dependency["sha256"],
            }
        )
    stale = any(item["stale"] for item in comparisons)
    output_path = resolve_inside(workspace, entry["stale_output_path"])
    write_json(
        output_path,
        {
            "schema_version": "local_partition.stale_check.v1",
            "task_id": entry["task_id"],
            "role": entry["role"],
            "status": "stale" if stale else "current",
            "stale": stale,
            "comparisons": comparisons,
            "entry_path": entry_path.relative_to(workspace).as_posix(),
        },
    )
    return 0 if stale else 4


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        required=True,
        choices=("executor", "reviewer", "stale"),
    )
    parser.add_argument("--entry", required=True)
    args = parser.parse_args()

    entry_path = Path(args.entry).resolve()
    entry = load_json(entry_path)
    workspace = entry_path.parent.parent.resolve()
    if args.mode == "executor":
        return run_executor(entry_path, entry, workspace)
    if args.mode == "reviewer":
        return run_reviewer(entry_path, entry, workspace)
    return run_stale(entry_path, entry, workspace)


if __name__ == "__main__":
    raise SystemExit(main())

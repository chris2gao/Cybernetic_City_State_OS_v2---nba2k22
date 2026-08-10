#!/usr/bin/env python3
"""Move one complete public task to archive and then remove explicit private runtime."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

try:
    from .navigation import validate_discovery
except ImportError:
    from navigation import validate_discovery

VALIDATOR_ROOT = Path(__file__).resolve().parents[1] / "validator"
if str(VALIDATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_ROOT))
from validate_communication_system import CommunicationValidationError, load_yaml  # noqa: E402


def _atomic_yaml(path: Path, data: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise CommunicationValidationError("archive_temporary_path_conflict")
    temporary.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                         encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _validate_public_task(task: Path) -> None:
    for name in ("private_runtime", "_runtime"):
        if (task / name).exists():
            raise CommunicationValidationError("private_runtime_inside_public_task")
    required = {"indexes", "messages", "documents", "Human", "final_results", "material_failures"}
    missing = sorted(name for name in required if not (task / name).is_dir())
    if missing:
        raise CommunicationValidationError("public_history_category_missing:" + ",".join(missing))
    if not any((task / "final_results").iterdir()):
        raise CommunicationValidationError("durable_completion_result_missing")
    for path in task.rglob("*"):
        if path.is_symlink():
            raise CommunicationValidationError("public_task_symlink_prohibited")


def _validate_runtime_target(path: Path, repository_root: Path) -> Path:
    target = path.resolve()
    if target.name not in {"_runtime", "private_runtime"}:
        raise CommunicationValidationError("private_runtime_target_name_invalid")
    if target == target.anchor or len(target.parts) < 3:
        raise CommunicationValidationError("private_runtime_target_too_broad")
    public = repository_root.resolve()
    try:
        public.relative_to(target)
    except ValueError:
        pass
    else:
        raise CommunicationValidationError("private_runtime_target_contains_public_root")
    return target


def _load_prerequisite(active: Path, prerequisites: dict[str, Any], ref_field: str) -> dict[str, Any]:
    relative = prerequisites.get(ref_field)
    if not isinstance(relative, str) or not relative:
        raise CommunicationValidationError(f"archive_durable_prerequisite_missing:{ref_field}")
    target = (active.resolve() / relative).resolve()
    try:
        target.relative_to(active.resolve())
    except ValueError as exc:
        raise CommunicationValidationError(
            f"archive_durable_prerequisite_outside_task:{ref_field}"
        ) from exc
    if not target.is_file():
        raise CommunicationValidationError(f"archive_durable_prerequisite_unreadable:{ref_field}")
    value = load_yaml(target)
    if not isinstance(value, dict):
        raise CommunicationValidationError(f"archive_durable_prerequisite_invalid:{ref_field}")
    return value


def _validate_durable_prerequisites(active: Path, prerequisites: dict[str, Any]) -> list[str]:
    completion = _load_prerequisite(active, prerequisites, "completion_pointer_ref")
    residuals = _load_prerequisite(active, prerequisites, "material_residuals_ref")
    runtime_policy = _load_prerequisite(active, prerequisites, "private_runtime_policy_ref")
    missing = []
    if completion.get("status") != "complete":
        missing.append("completion_pointer_status")
    if residuals.get("material_residuals_recorded") is not True:
        missing.append("material_residuals_recorded")
    if runtime_policy.get("private_runtime_not_durable_source") is not True:
        missing.append("private_runtime_not_durable_source")
    observed = [
        str(prerequisites["completion_pointer_ref"]),
        str(prerequisites["material_residuals_ref"]),
        str(prerequisites["private_runtime_policy_ref"]),
    ]
    if prerequisites.get("github_copy_required") is True:
        convergence = _load_prerequisite(active, prerequisites, "github_convergence_ref")
        observed.append(str(prerequisites["github_convergence_ref"]))
        if convergence.get("github_convergence_complete") is not True:
            missing.append("github_convergence_complete")
    if missing:
        raise CommunicationValidationError(
            "archive_durable_prerequisite_missing:" + ",".join(missing)
        )
    return observed


def _validate_runtime_git_state(targets: list[Path], git_root: Path | None) -> None:
    if not targets:
        return
    resolved_git = git_root.resolve() if git_root is not None else None
    for target in targets:
        if resolved_git is None:
            continue
        try:
            relative = target.relative_to(resolved_git)
        except ValueError:
            continue
        tracked = subprocess.run(
            ["git", "ls-files", "-z", "--", relative.as_posix()],
            cwd=resolved_git,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if tracked.returncode != 0:
            raise CommunicationValidationError("private_runtime_git_state_unreadable")
        if tracked.stdout:
            raise CommunicationValidationError("tracked_private_runtime_deletion_prohibited")
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", "--", relative.as_posix()],
            cwd=resolved_git,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=False,
        )
        if ignored.returncode != 0:
            raise CommunicationValidationError("repository_private_runtime_must_be_ignored")


def archive_physical_tree(
    active: Path,
    archived: Path,
    *,
    discovery_update: Callable[[], None],
    private_runtime_paths: list[Path],
    durable_prerequisites: dict[str, Any],
    git_root: Path | None = None,
    required_categories: set[str] | None = None,
) -> dict[str, Any]:
    if not active.is_dir() or archived.exists():
        raise CommunicationValidationError("archive_source_or_target_invalid")
    if required_categories:
        missing = sorted(name for name in required_categories if not (active / name).is_dir())
        if missing:
            raise CommunicationValidationError("public_history_category_missing:" + ",".join(missing))
    prerequisite_refs = _validate_durable_prerequisites(active, durable_prerequisites)
    runtime_targets = [path.resolve() for path in private_runtime_paths]
    _validate_runtime_git_state(runtime_targets, git_root)
    trace = ["durable_prerequisite_verified", "private_runtime_git_state_verified"]
    archived.parent.mkdir(parents=True, exist_ok=True)
    os.replace(active, archived)
    trace.append("public_archive_completed")
    try:
        discovery_update()
    except Exception:
        os.replace(archived, active)
        raise
    trace.append("discovery_updated")
    deleted = []
    for target in runtime_targets:
        if target.exists():
            shutil.rmtree(target)
            deleted.append(str(target))
    trace.append("private_runtime_deleted")
    return {
        "archived_task_root": str(archived),
        "private_runtime_deleted": deleted,
        "operation_trace": trace,
        "durable_prerequisite_observed": True,
        "durable_prerequisite_refs": prerequisite_refs,
    }


def archive(repository_root: Path, task_id: str,
            private_runtime_paths: list[Path] | None = None, *,
            durable_prerequisites: dict[str, Any]) -> dict[str, object]:
    root = repository_root.resolve()
    active = root / "active" / task_id
    archived = root / "archive" / task_id
    if not active.is_dir() or archived.exists():
        raise CommunicationValidationError("archive_source_or_target_invalid")
    _validate_public_task(active)
    discovery_path = root / "discovery.yml"
    discovery = load_yaml(discovery_path)
    validate_discovery(discovery)
    active_ref = f"active/{task_id}/"
    archive_ref = f"archive/{task_id}/"
    if active_ref not in discovery["active_task_roots"]:
        raise CommunicationValidationError("discovery_active_task_missing")
    runtime_targets = [_validate_runtime_target(path, root) for path in (private_runtime_paths or [])]

    def update_discovery() -> None:
        discovery["active_task_roots"].remove(active_ref)
        if archive_ref not in discovery["archived_task_roots"]:
            discovery["archived_task_roots"].append(archive_ref)
        _atomic_yaml(discovery_path, discovery)

    return archive_physical_tree(
        active,
        archived,
        discovery_update=update_discovery,
        private_runtime_paths=runtime_targets,
        durable_prerequisites=durable_prerequisites,
        git_root=root,
        required_categories={
            "indexes", "messages", "documents", "Human", "final_results", "material_failures",
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--private-runtime", action="append", type=Path, default=[])
    parser.add_argument("--completion-pointer-ref", required=True)
    parser.add_argument("--material-residuals-ref", required=True)
    parser.add_argument("--private-runtime-policy-ref", required=True)
    parser.add_argument("--github-copy-required", action="store_true")
    parser.add_argument("--github-convergence-ref")
    args = parser.parse_args()
    try:
        result = archive(
            args.repository_root,
            args.task_id,
            args.private_runtime,
            durable_prerequisites={
                "completion_pointer_ref": args.completion_pointer_ref,
                "material_residuals_ref": args.material_residuals_ref,
                "private_runtime_policy_ref": args.private_runtime_policy_ref,
                "github_copy_required": args.github_copy_required,
                "github_convergence_ref": args.github_convergence_ref,
            },
        )
    except (CommunicationValidationError, OSError) as exc:
        print(f"archive_rejected:{exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

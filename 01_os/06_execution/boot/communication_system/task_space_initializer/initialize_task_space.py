#!/usr/bin/env python3
"""Create one public communication task space without background behavior."""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections.abc import Mapping
from pathlib import Path

import yaml

MANIFEST_FIELDS = {
    "repository_id", "task_id", "task_goal", "task_role_context_refs",
    "communication_root", "active_task_root", "current_carrier_state",
    "work_branch_when_GitHub", "task_navigation_owner_endpoint_id",
    "endpoint_card_refs", "Human_current_ref", "privacy_policy_ref",
    "lifecycle_status", "communication_contract_version",
}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
COMMUNICATION_ROOT_ENV = "CITYSTATE_COMMUNICATION_ROOT"


def _dump(data: object) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def _safe_component(value: str, label: str) -> str:
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f"invalid_{label}")
    return value


def _write_exact_or_create(path: Path, content: str) -> None:
    if path.is_symlink():
        raise ValueError(f"symlink_not_allowed:{path}")
    if path.exists():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise ValueError(f"existing_artifact_conflict:{path}")
        return
    path.write_text(content, encoding="utf-8", newline="\n")


def resolve_communication_root(
    explicit_root: Path | None,
    *,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    """Resolve the machine-global communication root with canonical precedence."""
    if explicit_root is not None:
        return explicit_root.expanduser().resolve()
    environment = os.environ if environ is None else environ
    configured = environment.get(COMMUNICATION_ROOT_ENV, "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    resolved_home = Path.home() if home is None else home
    return (resolved_home / ".citystate" / "communication").resolve()


def initialize(root: Path, repository_id: str, task_id: str, task_goal: str,
               navigation_owner: str, privacy_policy_ref: str,
               role_context_refs: list[str] | None = None) -> Path:
    repository_id = _safe_component(repository_id, "repository_id")
    task_id = _safe_component(task_id, "task_id")
    navigation_owner = _safe_component(navigation_owner, "navigation_owner")
    root = root.resolve()
    if root.exists() and (not root.is_dir() or root.is_symlink()):
        raise ValueError("communication_root_must_be_real_directory")
    root.mkdir(parents=True, exist_ok=True)
    repository_root = root / repository_id
    active = repository_root / "active"
    archive = repository_root / "archive"
    task = active / task_id
    for directory in (
        active, archive, task / "endpoints", task / "indexes", task / "messages",
        task / "documents", task / "Human" / "decisions", task / "final_results",
        task / "material_failures",
    ):
        if directory.exists() and (not directory.is_dir() or directory.is_symlink()):
            raise ValueError(f"directory_conflict:{directory}")
        directory.mkdir(parents=True, exist_ok=True)

    manifest = {
        "repository_id": repository_id,
        "task_id": task_id,
        "task_goal": task_goal,
        "task_role_context_refs": role_context_refs or [],
        "communication_root": str(repository_root),
        "active_task_root": str(task),
        "current_carrier_state": "local_only_current",
        "work_branch_when_GitHub": None,
        "task_navigation_owner_endpoint_id": navigation_owner,
        "endpoint_card_refs": [],
        "Human_current_ref": "Human/current.yml",
        "privacy_policy_ref": privacy_policy_ref,
        "lifecycle_status": "active",
        "communication_contract_version": 1,
    }
    if set(manifest) != MANIFEST_FIELDS:
        raise ValueError("manifest_contract_internal_error")
    current = {
        "task_id": task_id,
        "title": task_goal,
        "current_stage_or_checkpoint": "task_started",
        "important_refs": ["manifest.yml"],
        "pending_Human_decision": None,
        "last_material_update": "task_started",
    }
    _write_exact_or_create(task / "manifest.yml", _dump(manifest))
    _write_exact_or_create(task / "Human" / "current.yml", _dump(current))

    discovery_path = repository_root / "discovery.yml"
    discovery = {"active_task_roots": [f"active/{task_id}/"], "archived_task_roots": []}
    if discovery_path.exists():
        loaded = yaml.safe_load(discovery_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict) or set(loaded) != set(discovery):
            raise ValueError("discovery_contract_conflict")
        active_roots = loaded.get("active_task_roots")
        archived_roots = loaded.get("archived_task_roots")
        if not isinstance(active_roots, list) or not isinstance(archived_roots, list):
            raise ValueError("discovery_contract_conflict")
        if f"archive/{task_id}/" in archived_roots:
            raise ValueError("task_already_archived")
        if f"active/{task_id}/" not in active_roots:
            active_roots.append(f"active/{task_id}/")
            discovery_path.write_text(_dump(loaded), encoding="utf-8", newline="\n")
    else:
        _write_exact_or_create(discovery_path, _dump(discovery))
    return task


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--repository-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--task-goal", required=True)
    parser.add_argument("--navigation-owner", required=True)
    parser.add_argument("--privacy-policy-ref", required=True)
    parser.add_argument("--role-context-ref", action="append", default=[])
    args = parser.parse_args()
    try:
        root = resolve_communication_root(args.root)
        task = initialize(root, args.repository_id, args.task_id, args.task_goal,
                          args.navigation_owner, args.privacy_policy_ref,
                          args.role_context_ref)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"initialization_rejected:{exc}", file=sys.stderr)
        return 2
    print(task)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

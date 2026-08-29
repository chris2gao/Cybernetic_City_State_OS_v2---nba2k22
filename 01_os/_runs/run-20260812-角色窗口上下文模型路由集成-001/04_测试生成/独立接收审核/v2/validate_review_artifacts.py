#!/usr/bin/env python3
"""Validate the durable Stage04 v2 independent-review artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[5]
VERDICT = HERE / "Stage04_v2独立接收裁决_v1.yml"
RESULT = HERE / "independent_variant_probe_results_v1.json"
ALLOWED_PREFIX = (
    "01_os/_runs/run-20260812-角色窗口上下文模型路由集成-001/"
    "04_测试生成/独立接收审核/v2/"
)


class StrictLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    out = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in out:
            raise ValueError(f"duplicate YAML key: {key!r}")
        out[key] = loader.construct_object(value_node, deep=deep)
    return out


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def main() -> int:
    verdict = yaml.load(VERDICT.read_text(encoding="utf-8"), Loader=StrictLoader)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert verdict["verdict"] == "FIX_REQUIRED"
    assert verdict["stage05_entry_authorized_by_this_review"] is False
    assert verdict["pass_completion_marker_emitted"] is False
    assert len(verdict["new_blocking_findings"]) == 6
    digest = hashlib.sha256(RESULT.read_bytes()).hexdigest()
    assert digest == verdict["independent_reproduction"]["independent_adversarial_probe"]["result_sha256"]
    assert result["base_candidate"] == {"green": 43, "total": 43, "red": []}
    assert result["variants"]["V10_disabled_suffix_prohibitions"]["red"] == ["RW-T25"]
    assert result["variants"]["V11_list_shaped_entry_modes"]["red"] == ["RW-T08", "RW-T09"]
    assert result["variants"]["V12_structured_provider_pin"]["red"] == []
    assert result["variants"]["V13_yaml_role_applicability_matrix"]["red"] == ["RW-T05", "RW-T31"]
    assert result["variants"]["V14_mixed_descriptive_declarations"]["red"] == []
    assert result["variants"]["V15_markdown_definition_list_catalog"]["red"] == []
    closure = result["dependency_closure"]
    assert closure["deterministic_two_runs"] is True
    assert closure["staged_file_count"] == 1012
    assert closure["history_path_count"] == 776
    assert closure["unresolved_file_ref_count"] == 16
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    )
    changed = []
    for record in proc.stdout.decode("utf-8").split("\0"):
        if record:
            changed.append(record[3:].replace("\\", "/"))
    scope_source = "worktree"
    if not changed:
        proc = subprocess.run(
            ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
        )
        changed = [
            path.replace("\\", "/")
            for path in proc.stdout.decode("utf-8").split("\0")
            if path
        ]
        scope_source = "HEAD"
    assert changed and all(path.startswith(ALLOWED_PREFIX) for path in changed), changed
    noun = "file" if len(changed) == 1 else "files"
    print(
        f"review_artifacts_valid: {len(changed)} {noun}, 6 blockers, "
        f"{len(changed)} {scope_source} paths inside v2 boundary"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the durable Stage04 v3 independent-review artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[5]
VERDICT = HERE / "Stage04_v3独立接收裁决_v1.yml"
RESULT = HERE / "independent_v3_probe_results_v1.json"
PROBE = HERE / "independent_v3_probes.py"
ALLOWED_PREFIX = (
    "01_os/_runs/run-20260812-角色窗口上下文模型路由集成-001/"
    "04_测试生成/独立接收审核/v3/"
)


class StrictLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader: StrictLoader, node: yaml.MappingNode, deep: bool = False):
    out = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in out:
            raise ValueError(f"duplicate YAML key: {key!r}")
        out[key] = loader.construct_object(value_node, deep=deep)
    return out


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths() -> tuple[str, list[str]]:
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    changed = []
    for record in proc.stdout.decode("utf-8").split("\0"):
        if record:
            changed.append(record[3:].replace("\\", "/"))
    if changed:
        return "worktree", changed
    proc = subprocess.run(
        ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return (
        "HEAD",
        [
            path.replace("\\", "/")
            for path in proc.stdout.decode("utf-8").split("\0")
            if path
        ],
    )


def main() -> int:
    verdict = yaml.load(VERDICT.read_text(encoding="utf-8"), Loader=StrictLoader)
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    assert verdict["verdict"] == "FIX_REQUIRED"
    assert verdict["stage05_entry_authorized_by_this_review"] is False
    assert verdict["pass_completion_marker_emitted"] is False
    assert len(verdict["blocking_findings"]) == 10
    assert verdict["correction_budget_implication"]["third_in_place_correction_permitted"] is False

    reproduction = verdict["independent_reproduction"]["independent_adversarial_probe"]
    assert sha256(RESULT) == reproduction["result_sha256"]
    assert sha256(PROBE) == reproduction["script_sha256"]
    assert result["base_candidate"]["green"] == 43
    assert result["base_candidate"]["total"] == 43
    assert result["base_candidate"]["red"] == []

    expected_red = {
        "I01_negative_prefix_handoff_prohibitions": ["RW-T25"],
        "I02_list_record_handoff_prohibitions": ["RW-T25"],
        "I03_list_pair_entry_modes": ["RW-T08", "RW-T09"],
        "I04_prohibited_provider_list": ["RW-T19"],
        "I05_resource_neighbor_provider_pin": [],
        "I06_unlisted_provider_pin": [],
        "I07_role_reference_matrix": ["RW-T05", "RW-T31"],
        "I08_generic_id_second_role_source": [],
        "I09_yaml_mapping_model_catalog": [],
        "I10_markdown_heading_model_catalog": [],
        "I11_non_boolean_autonomy_enablement": [],
        "I12_carried_delivery_state": [],
        "I13_string_authority_grant": [],
        "I14_full_tree_sentinel_dependency": [],
        "I15_no_run_id_binding": ["RW-T07"],
    }
    assert set(result["variants"]) == set(expected_red)
    for name, red in expected_red.items():
        assert result["variants"][name]["red"] == red, name
        assert result["variants"][name]["mechanism_validator_exit"] == 0, name

    conforming_rejected = 0
    nonconforming_accepted = 0
    for value in result["variants"].values():
        description = value["description"]
        if description.startswith("conforming:") and value["red"]:
            conforming_rejected += 1
        if description.startswith("nonconforming:") and not value["red"]:
            nonconforming_accepted += 1
    assert conforming_rejected == 6
    assert nonconforming_accepted == 8

    audit = result["package_audit"]
    assert audit["normalized_digest"]["matches"] is True
    assert audit["all_input_and_supporting_hashes_match"] is True
    assert audit["all_receipt_artifact_hashes_match"] is True
    assert audit["freeze_receipt_yaml_parse"]["passed"] is False
    assert audit["primary_diff_path_count"] == 6
    assert audit["receipt_changed_path_count_claim"] == 5
    assert len(audit["receipt_changed_path_list"]) == 5
    assert audit["crawler_symbols_absent"] is True
    assert audit["full_tree_probe_symbol_present"] is True

    source, paths = changed_paths()
    assert paths and all(path.startswith(ALLOWED_PREFIX) for path in paths), paths
    print(
        "review_artifacts_valid: "
        f"10 blockers, 6 conforming false positives, 8 violating false negatives, "
        f"{len(paths)} {source} paths inside v3 boundary"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

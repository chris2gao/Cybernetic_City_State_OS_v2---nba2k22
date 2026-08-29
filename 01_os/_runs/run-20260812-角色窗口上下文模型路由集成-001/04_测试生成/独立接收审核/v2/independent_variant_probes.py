#!/usr/bin/env python3
"""Independent adversarial probes for the Stage04 artifact_version 2 review.

This file is review evidence, not part of the frozen package.  It imports the
frozen harness without modifying it, builds the declared conforming candidate,
and applies additional representations that are absent from C01..C09.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

import yaml


HERE = Path(__file__).resolve()
STAGE04 = HERE.parents[2]
REPO_ROOT = HERE.parents[6]
HARNESS_PATH = STAGE04 / "实现/verify_stage04_acceptance.py"
FIXTURES = STAGE04 / "fixtures"


def load_harness():
    spec = importlib.util.spec_from_file_location("stage04_v2_harness", HARNESS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {HARNESS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


H = load_harness()


def load_yaml(path: Path) -> Any:
    return H.load_yaml_strict(path)


def write_yaml(path: Path, value: Any) -> None:
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=4096),
        encoding="utf-8",
    )


def replace_once(path: Path, old: str, new: str) -> None:
    body = path.read_text(encoding="utf-8")
    if old not in body:
        raise RuntimeError(f"patch anchor absent in {path}: {old[:80]!r}")
    path.write_text(body.replace(old, new, 1), encoding="utf-8")


def candidate_path(tree: Path, rel: str) -> Path:
    return tree / rel


WINDOWS = "01_os/03_mechanisms/window_role_binding/windows_v1.yml"
ROLES = "01_os/03_mechanisms/window_role_binding/roles_v1.yml"
HANDOFF = "01_os/03_mechanisms/window_role_binding/handoff_v1.yml"
BOOT = "01_os/02_boot/window_role_binding/boot_v1.yml"
VALIDATOR = "01_os/03_mechanisms/window_role_binding/impl/check_binding.py"


def disabled_suffix_prohibitions(tree: Path) -> None:
    """Equivalent handoff prohibitions expressed as ``*_disabled: true``."""
    handoff = candidate_path(tree, HANDOFF)
    doc = load_yaml(handoff)
    rec = doc["handoff_record"]
    fields = list(rec.pop("prohibited_fields"))
    for field in fields:
        rec[f"{field}_disabled"] = True
    write_yaml(handoff, doc)

    validator = candidate_path(tree, VALIDATOR)
    replace_once(
        validator,
        '    prohibited = {str(x) for x in (rec.get("prohibited_fields") or [])}\n'
        '    if "private_chain_of_thought" not in prohibited:\n',
        '    raw_prohibited = rec.get("prohibited_fields") or []\n'
        '    prohibited = {str(x) for x in raw_prohibited} if isinstance(raw_prohibited, list) else set()\n'
        '    prohibited.update(\n'
        '        str(k).removesuffix("_disabled")\n'
        '        for k, v in rec.items() if str(k).endswith("_disabled") and v is True\n'
        '    )\n'
        '    if "private_chain_of_thought" not in prohibited:\n',
    )


def list_shaped_entry_modes(tree: Path) -> None:
    """Equivalent fresh/reentry records represented as a list of mappings."""
    windows = candidate_path(tree, WINDOWS)
    doc = load_yaml(windows)
    modes = doc["entry_modes"]
    doc["entry_modes"] = [dict(mode_id=mode_id, **body) for mode_id, body in modes.items()]
    write_yaml(windows, doc)

    validator = candidate_path(tree, VALIDATOR)
    replace_once(
        validator,
        '    modes = win_doc.get("entry_modes")\n'
        '    if not isinstance(modes, dict):\n',
        '    modes = win_doc.get("entry_modes")\n'
        '    if isinstance(modes, list):\n'
        '        modes = {\n'
        '            str(item.get("mode_id")): {k: v for k, v in item.items() if k != "mode_id"}\n'
        '            for item in modes if isinstance(item, dict) and item.get("mode_id")\n'
        '        }\n'
        '    if not isinstance(modes, dict):\n',
    )


def structured_provider_pin(tree: Path) -> None:
    """A forbidden normative provider pin stored as a mapping key."""
    roles = candidate_path(tree, ROLES)
    doc = load_yaml(roles)
    doc["roles"]["independent_review"]["preferred_provider"] = {"openai": True}
    write_yaml(roles, doc)


def yaml_role_applicability_matrix(tree: Path) -> None:
    """A workflow applicability matrix, not a second role source of truth."""
    target = candidate_path(
        tree, "01_os/01_workflow/03_结果建模/role_stage_context_applicability.yml"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    write_yaml(
        target,
        {
            "schema_version": "workflow.role_stage_context_applicability.v1",
            "purpose": "routing applicability only; canonical role properties live in the mechanism",
            "applicability": [
                {
                    "role": "backend_execution",
                    "stage_scope": "workflow_stage_06_execution",
                    "context_hint": "implementation packet",
                },
                {
                    "role": "independent_review",
                    "stage_scope": "workflow_stage_09_review",
                    "context_hint": "primary evidence",
                },
                {
                    "role": "deep_research",
                    "stage_scope": "workflow_stage_02_information_collection",
                    "context_hint": "research scope",
                },
            ],
        },
    )


def mixed_descriptive_declarations(tree: Path) -> None:
    """Each boot description mentions all three concepts; content must win."""
    boot = candidate_path(tree, BOOT)
    doc = load_yaml(boot)
    for item in doc["load_order"]:
        path = str(item.get("path", ""))
        if path.endswith(("roles_v1.yml", "windows_v1.yml", "handoff_v1.yml")):
            item["purpose"] = (
                "role/window/handoff composition declaration; exact document kind is established "
                "by content while path, loader and evidence remain metadata"
            )
            item["description"] = "role window handoff cross-reference"
    write_yaml(boot, doc)


def markdown_definition_list_catalog(tree: Path) -> None:
    """A forbidden second mutable catalog in Markdown definition-list form."""
    catalog = load_yaml(candidate_path(tree, H.MODEL_CATALOG))
    labels = []
    for entry in catalog.get("entries") or []:
        value = entry.get("model_label")
        if isinstance(value, str) and value not in labels:
            labels.append(value)
        if len(labels) == 3:
            break
    if len(labels) < 3:
        raise RuntimeError("live model catalog exposes fewer than three model labels")
    target = candidate_path(tree, "01_os/01_workflow/03_结果建模/second_model_catalog.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "# Stage-local model catalog\n\n"
        + "\n\n".join(f"{label}\n: stage-owned mutable routing tier" for label in labels)
        + "\n",
        encoding="utf-8",
    )


def run_variant(master: Path, mutate: Callable[[Path], None], semantic_expectation: str) -> dict:
    with tempfile.TemporaryDirectory() as td:
        tree = Path(td) / "tree"
        shutil.copytree(master, tree, symlinks=True)
        mutate(tree)
        H.ensure_git(tree)
        failed, rows = H.run_acceptance(tree)
        row_map = {row["test_id"]: row for row in rows}
        return {
            "semantic_expectation": semantic_expectation,
            "green": len(rows) - failed,
            "total": len(rows),
            "red": sorted(test_id for test_id, row in row_map.items() if not row["passed"]),
            "details": {
                test_id: row_map[test_id]["detail"]
                for test_id in sorted(row_map)
                if not row_map[test_id]["passed"]
            },
            "target_results": {
                test_id: {"passed": row_map[test_id]["passed"], "detail": row_map[test_id]["detail"]}
                for test_id in ("RW-T08", "RW-T09", "RW-T19", "RW-T25", "RW-T05", "RW-T31", "RW-T43")
            },
        }


def closure_audit(master: Path) -> dict:
    tree = H.Tree(master)
    all_lists = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as td:
            all_lists.append(H.stage_dependency_closure(tree, Path(td) / "closure"))
    staged = set(all_lists[0])
    unresolved_files: set[str] = set()
    unresolved_dir_members: set[str] = set()
    for rel in sorted(staged):
        if not rel.endswith((".yml", ".yaml", ".md", ".py", ".txt")):
            continue
        body = tree.text(rel) or ""
        for cand in H.REPO_PATH_RX.findall(body):
            cand = cand.rstrip(".,;:")
            if tree.path(cand).is_file() and cand not in staged:
                unresolved_files.add(cand)
            elif tree.path(cand).is_dir():
                for child in H.walk_files(tree.path(cand)):
                    child_rel = tree.rel(child)
                    if child_rel not in staged:
                        unresolved_dir_members.add(child_rel)
    required = {
        "context_management": "01_os/03_mechanisms/context_management/实现/文件布局契约_v1.yml",
        "model_routing": H.MODEL_CONTRACT,
        "communication_system": H.COMM_MESSAGE,
    }
    return {
        "deterministic_two_runs": all_lists[0] == all_lists[1],
        "staged_file_count": len(staged),
        "staged_list_sha256": hashlib.sha256(
            "\n".join(sorted(staged)).encode("utf-8")
        ).hexdigest(),
        "required_dependency_presence": {name: path in staged for name, path in required.items()},
        "history_path_count": sum(
            rel.startswith("01_os/_runs/") or rel.startswith("01_os/07_content/_runs/")
            for rel in staged
        ),
        "unresolved_file_ref_count": len(unresolved_files),
        "unresolved_file_refs_first_20": sorted(unresolved_files)[:20],
        "unresolved_directory_member_count": len(unresolved_dir_members),
        "unresolved_directory_members_first_20": sorted(unresolved_dir_members)[:20],
    }


def independent_digest() -> str:
    package = load_yaml(STAGE04 / "04_tests.yml")
    payload = dict(package["payload"])
    payload.pop("test_package_sha256", None)
    raw = yaml.safe_dump(payload, allow_unicode=True, sort_keys=True, width=4096)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        master = Path(td) / "candidate"
        H.build_candidate_tree(FIXTURES, REPO_ROOT, master)
        base_failed, base_rows = H.run_acceptance(master)
        report = {
            "review_probe_version": 1,
            "independent_normalized_digest": independent_digest(),
            "base_candidate": {
                "green": len(base_rows) - base_failed,
                "total": len(base_rows),
                "red": sorted(row["test_id"] for row in base_rows if not row["passed"]),
            },
            "variants": {
                "V10_disabled_suffix_prohibitions": run_variant(
                    master,
                    disabled_suffix_prohibitions,
                    "conforming; all checks should remain green",
                ),
                "V11_list_shaped_entry_modes": run_variant(
                    master,
                    list_shaped_entry_modes,
                    "conforming; all checks should remain green",
                ),
                "V12_structured_provider_pin": run_variant(
                    master,
                    structured_provider_pin,
                    "nonconforming; RW-T19 must turn red",
                ),
                "V13_yaml_role_applicability_matrix": run_variant(
                    master,
                    yaml_role_applicability_matrix,
                    "conforming; RW-T05/RW-T31 must remain green",
                ),
                "V14_mixed_descriptive_declarations": run_variant(
                    master,
                    mixed_descriptive_declarations,
                    "conforming; content priority must keep all checks green",
                ),
                "V15_markdown_definition_list_catalog": run_variant(
                    master,
                    markdown_definition_list_catalog,
                    "nonconforming; RW-T43 must turn red",
                ),
            },
            "dependency_closure": closure_audit(master),
        }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    output = HERE.with_name("independent_variant_probe_results_v1.json")
    output.write_bytes(rendered.encode("utf-8"))
    print(
        json.dumps(
            {
                "result_path": str(output),
                "base_candidate": report["base_candidate"],
                "variant_red_sets": {
                    key: value["red"] for key, value in report["variants"].items()
                },
                "dependency_closure": report["dependency_closure"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

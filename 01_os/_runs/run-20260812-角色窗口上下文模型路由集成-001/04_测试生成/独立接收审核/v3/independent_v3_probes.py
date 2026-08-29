#!/usr/bin/env python3
"""Fresh independent adversarial probes for the frozen Stage04 v3 package.

This is review evidence, not part of the frozen package.  It imports the frozen
harness only as the object under test, independently builds the candidate tree,
and exercises representations that are absent from the author's mutation and
conforming-variant samples.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

import yaml


HERE = Path(__file__).resolve()
STAGE04 = HERE.parents[2]
RUN_ROOT = HERE.parents[3]
REPO_ROOT = HERE.parents[6]
HARNESS_PATH = STAGE04 / "实现/verify_stage04_acceptance.py"
FIXTURES = STAGE04 / "fixtures"

ROLES = "01_os/03_mechanisms/window_role_binding/roles_v1.yml"
WINDOWS = "01_os/03_mechanisms/window_role_binding/windows_v1.yml"
HANDOFF = "01_os/03_mechanisms/window_role_binding/handoff_v1.yml"
VALIDATOR = "01_os/03_mechanisms/window_role_binding/impl/check_binding.py"


def load_harness():
    spec = importlib.util.spec_from_file_location("stage04_v3_harness_under_review", HARNESS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {HARNESS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


H = load_harness()


class UniqueLoader(yaml.SafeLoader):
    pass


def _unique_mapping(loader: UniqueLoader, node: yaml.MappingNode, deep: bool = False):
    out = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in out:
            raise ValueError(f"duplicate YAML key: {key!r}")
        out[key] = loader.construct_object(value_node, deep=deep)
    return out


UniqueLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping
)


def load_yaml(path: Path) -> Any:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueLoader)


def write_yaml(path: Path, value: Any) -> None:
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=4096),
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(path: Path, old: str, new: str) -> None:
    body = path.read_text(encoding="utf-8")
    if old not in body:
        raise RuntimeError(f"patch anchor absent in {path}: {old[:100]!r}")
    path.write_text(body.replace(old, new, 1), encoding="utf-8")


def apply_operation(tree: Path, op: dict[str, Any]) -> None:
    path = tree / op["file"]
    kind = op["operation"]
    if kind == "delete_file":
        path.unlink()
        return
    if kind == "create_file":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(op["content"], encoding="utf-8")
        return
    if kind == "move_file":
        target = tree / op["to"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))
        return
    body = path.read_text(encoding="utf-8")
    if kind == "replace":
        if op["find"] not in body:
            raise RuntimeError(f"overlay anchor absent in {path}")
        body = body.replace(op["find"], op["replace"], 1)
    elif kind == "replace_all":
        if op["find"] not in body:
            raise RuntimeError(f"overlay anchor absent in {path}")
        body = body.replace(op["find"], op["replace"])
    elif kind == "append":
        body += op["append"]
    elif kind == "delete_line":
        lines = body.splitlines(keepends=True)
        kept = [line for line in lines if op["find"] not in line]
        if len(kept) == len(lines):
            raise RuntimeError(f"overlay line absent in {path}")
        body = "".join(kept)
    else:
        raise RuntimeError(f"unsupported overlay operation: {kind}")
    path.write_text(body, encoding="utf-8")


def build_candidate(dest: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> list[str]:
        return [
            name
            for name in names
            if name in {".git", "__pycache__", ".pytest_cache", "_runtime", "08_os"}
        ]

    shutil.copytree(REPO_ROOT, dest, ignore=ignore, symlinks=True)
    overlay = FIXTURES / "overlay"
    for source in sorted(overlay.rglob("*")):
        if source.is_file():
            target = dest / source.relative_to(overlay)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    edits = load_yaml(FIXTURES / "overlay_edits_v1.yml").get("edits", [])
    for edit in edits:
        apply_operation(dest, edit)
    subprocess.run(["git", "init", "-q"], cwd=dest, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=independent-review@local",
            "-c",
            "user.name=independent-review",
            "commit",
            "-q",
            "-m",
            "candidate",
        ],
        cwd=dest,
        check=True,
        capture_output=True,
    )


def role_doc(tree: Path) -> dict[str, Any]:
    return load_yaml(tree / ROLES)


def handoff_doc(tree: Path) -> dict[str, Any]:
    return load_yaml(tree / HANDOFF)


def window_doc(tree: Path) -> dict[str, Any]:
    return load_yaml(tree / WINDOWS)


def patch_validator_prefix_prohibitions(tree: Path) -> None:
    validator = tree / VALIDATOR
    anchor = "            prohibited.add(str(k)[: m.start()])\n"
    addition = (
        anchor
        + "    for k, v in rec.items():\n"
        + "        m = re.match(r\"(prohibited|forbidden|disallowed|disabled|banned)_(.+)$\", str(k), re.I)\n"
        + "        if m and v is True:\n"
        + "            prohibited.add(m.group(2))\n"
    )
    replace_once(validator, anchor, addition)


def patch_validator_record_prohibitions(tree: Path) -> None:
    validator = tree / VALIDATOR
    old = (
        "    if isinstance(raw, dict):\n"
        "        prohibited = {str(k) for k, v in raw.items() if v is True}\n"
        "    else:\n"
        "        prohibited = {str(x) for x in raw}\n"
    )
    new = (
        "    if isinstance(raw, dict):\n"
        "        prohibited = {str(k) for k, v in raw.items() if v is True}\n"
        "    elif isinstance(raw, list):\n"
        "        prohibited = set()\n"
        "        for item in raw:\n"
        "            if isinstance(item, dict) and item.get(\"prohibited\") is True:\n"
        "                prohibited.add(str(item.get(\"field\")))\n"
        "            elif isinstance(item, str):\n"
        "                prohibited.add(item)\n"
        "    else:\n"
        "        prohibited = set()\n"
    )
    replace_once(validator, old, new)


def negative_prefix_handoff(tree: Path) -> None:
    doc = handoff_doc(tree)
    record = doc["handoff_record"]
    fields = list(record.pop("prohibited_fields"))
    for field in fields:
        record[f"prohibited_{field}"] = True
    write_yaml(tree / HANDOFF, doc)
    patch_validator_prefix_prohibitions(tree)


def list_record_handoff(tree: Path) -> None:
    doc = handoff_doc(tree)
    record = doc["handoff_record"]
    fields = list(record["prohibited_fields"])
    record["prohibited_fields"] = [
        {"field": field, "prohibited": True} for field in fields
    ]
    write_yaml(tree / HANDOFF, doc)
    patch_validator_record_prohibitions(tree)


def list_pair_entry_modes(tree: Path) -> None:
    doc = window_doc(tree)
    modes = doc["entry_modes"]
    doc["entry_modes"] = [[mode_id, body] for mode_id, body in modes.items()]
    write_yaml(tree / WINDOWS, doc)
    validator = tree / VALIDATOR
    anchor = "        for item in modes:\n            if isinstance(item, dict):\n"
    replacement = (
        "        for item in modes:\n"
        "            if (isinstance(item, list) and len(item) == 2\n"
        "                    and isinstance(item[0], str) and isinstance(item[1], dict)):\n"
        "                norm[item[0]] = item[1]\n"
        "                continue\n"
        "            if isinstance(item, dict):\n"
    )
    replace_once(validator, anchor, replacement)


def no_run_id_binding(tree: Path) -> None:
    """A R02 binds task/role/stage/repository facts, not a mandatory run_id."""
    doc = window_doc(tree)
    ident = doc["window_identity"]
    ident["bound_facts"] = [
        value for value in ident["bound_facts"] if value != "run_id"
    ]
    fresh = doc["entry_modes"]["fresh"]
    fresh["required_fields"] = [
        value for value in fresh["required_fields"] if value != "run_id"
    ]
    write_yaml(tree / WINDOWS, doc)


def prohibited_provider_list(tree: Path) -> None:
    doc = role_doc(tree)
    doc["roles"]["independent_review"]["prohibited_provider"] = [
        "openai",
        "anthropic",
    ]
    write_yaml(tree / ROLES, doc)


def resource_neighbor_provider_pin(tree: Path) -> None:
    doc = role_doc(tree)
    doc["roles"]["independent_review"]["resource_constraints"] = {
        "preferred_provider": {"openai": True}
    }
    write_yaml(tree / ROLES, doc)


def unlisted_provider_pin(tree: Path) -> None:
    doc = role_doc(tree)
    doc["roles"]["independent_review"]["preferred_provider"] = {
        "mistral": True
    }
    write_yaml(tree / ROLES, doc)


def role_reference_matrix(tree: Path) -> None:
    target = tree / "01_os/01_workflow/03_结果建模/role_reference_matrix.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    entries = {}
    for role in ("backend_execution", "independent_review", "deep_research"):
        entries[role] = {
            "stage_scope": "task-declared",
            "model_route_ref": "01_os/03_mechanisms/model_routing/路由契约_v1.yml",
            "handoff_ref": "01_os/03_mechanisms/window_role_binding/handoff_v1.yml",
            "authority_ref": "01_os/05_registry/repository_publisher_authority_v1.yml",
        }
    write_yaml(
        target,
        {
            "schema_version": "workflow.role_reference_matrix.v1",
            "purpose": "references only; owns no role semantics",
            "role_references": entries,
        },
    )


def generic_id_second_role_source(tree: Path) -> None:
    target = tree / "01_os/01_workflow/03_结果建模/second_role_source.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    roles = {}
    for index, label in enumerate(
        ("backend_execution", "independent_review", "deep_research"), start=1
    ):
        roles[f"R{index}"] = {
            "label": label,
            "responsibility": f"normative responsibility for {label}",
            "independence_requirement": "normative separation rule",
            "authority_limit": "normative authority boundary",
        }
    write_yaml(
        target,
        {
            "schema_version": "workflow.second_role_source.v1",
            "purpose": "stage-owned mutable role definitions",
            "role_definitions": roles,
        },
    )


def yaml_mapping_model_catalog(tree: Path) -> None:
    target = tree / "01_os/01_workflow/03_结果建模/second_model_catalog.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    write_yaml(
        target,
        {
            "schema_version": "workflow.stage_model_tiers.v1",
            "stage_owned_models": {
                "GPT-5.6 Sol": {"tier": "flagship", "mutable": True},
                "GPT-5.6 Terra": {"tier": "balanced", "mutable": True},
                "GPT-5.6 Luna": {"tier": "economy", "mutable": True},
            },
        },
    )


def markdown_heading_model_catalog(tree: Path) -> None:
    target = tree / "01_os/01_workflow/03_结果建模/second_model_catalog_headings.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "# Stage-owned mutable model catalog\n\n"
        "## GPT-5.6 Sol\n\nTier: flagship\n\n"
        "## GPT-5.6 Terra\n\nTier: balanced\n\n"
        "## GPT-5.6 Luna\n\nTier: economy\n",
        encoding="utf-8",
    )


def non_boolean_autonomy_enablement(tree: Path) -> None:
    doc = handoff_doc(tree)
    doc["automatic_task_progression"] = "after_handoff_publication"
    doc["scheduler"] = "run_on_window_entry"
    write_yaml(tree / HANDOFF, doc)


def carried_delivery_state(tree: Path) -> None:
    doc = handoff_doc(tree)
    doc["handoff_record"]["delivery_state"] = "mutable_runtime_state"
    write_yaml(tree / HANDOFF, doc)


def string_authority_grant(tree: Path) -> None:
    doc = role_doc(tree)
    doc["roles"]["backend_execution"]["master_write_authorized"] = "granted"
    write_yaml(tree / ROLES, doc)


def full_tree_sentinel_dependency(tree: Path) -> None:
    sentinel_rel = "01_os/07_content/full_tree_probe_sentinel.txt"
    sentinel = tree / sentinel_rel
    sentinel.parent.mkdir(parents=True, exist_ok=True)
    sentinel.write_text("full candidate tree sentinel\n", encoding="utf-8")
    validator = tree / VALIDATOR
    anchor = "    problems: list[str] = []\n"
    replacement = (
        anchor
        + f"    if not (root / {sentinel_rel!r}).is_file():\n"
        + f"        problems.append(\"full-tree sentinel missing: {sentinel_rel}\")\n"
    )
    replace_once(validator, anchor, replacement)


VARIANTS: dict[str, tuple[str, Callable[[Path], None], tuple[str, ...]]] = {
    "I01_negative_prefix_handoff_prohibitions": (
        "conforming: negative-prefix prohibition fields must stay green",
        negative_prefix_handoff,
        ("RW-T25",),
    ),
    "I02_list_record_handoff_prohibitions": (
        "conforming: list-of-record prohibition declarations must stay green",
        list_record_handoff,
        ("RW-T25",),
    ),
    "I03_list_pair_entry_modes": (
        "conforming: list-of-pairs preserves fresh/reentry and predecessor semantics",
        list_pair_entry_modes,
        ("RW-T08", "RW-T09"),
    ),
    "I04_prohibited_provider_list": (
        "conforming: a negative provider declaration is not a provider pin",
        prohibited_provider_list,
        ("RW-T19",),
    ),
    "I05_resource_neighbor_provider_pin": (
        "nonconforming: resource_constraints contains a normative OpenAI pin",
        resource_neighbor_provider_pin,
        ("RW-T19",),
    ),
    "I06_unlisted_provider_pin": (
        "nonconforming: provider independence forbids unlisted vendors too",
        unlisted_provider_pin,
        ("RW-T19",),
    ),
    "I07_role_reference_matrix": (
        "conforming: pointer-only role matrix owns no role semantics",
        role_reference_matrix,
        ("RW-T05", "RW-T31"),
    ),
    "I08_generic_id_second_role_source": (
        "nonconforming: generic IDs with role labels still form a second role source",
        generic_id_second_role_source,
        ("RW-T05", "RW-T31"),
    ),
    "I09_yaml_mapping_model_catalog": (
        "nonconforming: YAML mapping keys restate the live model catalog",
        yaml_mapping_model_catalog,
        ("RW-T43",),
    ),
    "I10_markdown_heading_model_catalog": (
        "nonconforming: repeated Markdown headings restate the live model catalog",
        markdown_heading_model_catalog,
        ("RW-T43",),
    ),
    "I11_non_boolean_autonomy_enablement": (
        "nonconforming: descriptive enabled values still activate automation",
        non_boolean_autonomy_enablement,
        ("RW-T26", "RW-T34"),
    ),
    "I12_carried_delivery_state": (
        "nonconforming: a handoff cannot carry mutable delivery state",
        carried_delivery_state,
        ("RW-T25",),
    ),
    "I13_string_authority_grant": (
        "nonconforming: authority granted as a string is still an escalation",
        string_authority_grant,
        ("RW-T04", "RW-T18"),
    ),
    "I14_full_tree_sentinel_dependency": (
        "conforming topology probe: the declared validator must see a foreign full-tree sentinel",
        full_tree_sentinel_dependency,
        ("RW-T37", "RW-T38", "RW-T39", "RW-T40", "RW-T41", "RW-T42"),
    ),
    "I15_no_run_id_binding": (
        "conforming: A R02 requires task/role/stage/repository facts but does not mandate run_id",
        no_run_id_binding,
        ("RW-T07",),
    ),
}


def run_variant(master: Path, name: str, description: str,
                mutate: Callable[[Path], None], targets: tuple[str, ...]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as td:
        tree = Path(td) / "tree"
        shutil.copytree(master, tree, symlinks=True)
        mutate(tree)
        failed, rows = H.run_acceptance(tree)
        row_map = {row["test_id"]: row for row in rows}
        validator_rc, validator_output = H.run_validator(tree, VALIDATOR, tree)
        return {
            "description": description,
            "green": len(rows) - failed,
            "total": len(rows),
            "red": sorted(row["test_id"] for row in rows if not row["passed"]),
            "target_results": {
                target: {
                    "passed": row_map[target]["passed"],
                    "detail": row_map[target]["detail"],
                }
                for target in targets
            },
            "mechanism_validator_exit": validator_rc,
            "mechanism_validator_tail": validator_output[-300:],
        }


def package_audit() -> dict[str, Any]:
    package_path = STAGE04 / "04_tests.yml"
    package = load_yaml(package_path)
    payload = dict(package["payload"])
    claimed_digest = payload.pop("test_package_sha256")
    normalized = yaml.safe_dump(payload, allow_unicode=True, sort_keys=True, width=4096)
    computed_digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    refs = []
    for group in ("input_refs", "supporting_refs"):
        for item in package.get(group) or []:
            path = RUN_ROOT / item["path"]
            actual = sha256(path) if path.is_file() else None
            refs.append(
                {
                    "group": group,
                    "path": item["path"],
                    "claimed": item.get("sha256"),
                    "actual": actual,
                    "matches": actual == item.get("sha256"),
                }
            )

    receipt_path = STAGE04 / "freeze_receipt_v3.yml"
    receipt_text = receipt_path.read_text(encoding="utf-8")
    receipt_parse_error = None
    try:
        receipt = load_yaml(receipt_path)
    except Exception as exc:  # the frozen receipt is itself under review
        receipt = None
        receipt_parse_error = f"{type(exc).__name__}: {exc}"

    changed_match = re.search(
        r"(?ms)^changed_paths:\s*\n(?P<body>.*?)(?=^artifact_hashes:)", receipt_text
    )
    changed_body = changed_match.group("body") if changed_match else ""
    receipt_path_lines = re.findall(r"(?m)^  - (.+)$", changed_body)
    count_match = re.search(r"(?m)^  count:\s*(\d+)\s*$", changed_body)
    receipt_count_claim = int(count_match.group(1)) if count_match else None

    receipt_hashes = []
    artifact_match = re.search(
        r"(?ms)^artifact_hashes:\s*\n(?P<body>.*?)(?=^byte_unchanged_verified:)",
        receipt_text,
    )
    artifact_body = artifact_match.group("body") if artifact_match else ""
    for rel, claimed in re.findall(
        r"(?m)^  - path:\s*(.+?)\s*$\n    sha256:\s*([0-9a-f]{64})\s*$",
        artifact_body,
    ):
        path = STAGE04 / rel
        actual = sha256(path) if path.is_file() else None
        receipt_hashes.append(
            {
                "path": rel,
                "claimed": claimed,
                "actual": actual,
                "matches": actual == claimed,
            }
        )

    diff = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "236e7c52c06804d58324c1113e007cb4608088f7..afad6fdd79e51aaae89e5517b29561d763049a8d",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.splitlines()
    harness_text = HARNESS_PATH.read_text(encoding="utf-8")
    package_text = package_path.read_text(encoding="utf-8")
    return {
        "normalized_digest": {
            "claimed": claimed_digest,
            "computed": computed_digest,
            "matches": claimed_digest == computed_digest,
        },
        "input_and_supporting_refs": refs,
        "all_input_and_supporting_hashes_match": all(item["matches"] for item in refs),
        "receipt_artifact_hashes": receipt_hashes,
        "all_receipt_artifact_hashes_match": all(item["matches"] for item in receipt_hashes),
        "freeze_receipt_yaml_parse": {
            "passed": receipt_parse_error is None,
            "error": receipt_parse_error,
        },
        "primary_diff_paths": diff,
        "primary_diff_path_count": len(diff),
        "receipt_changed_path_count_claim": receipt_count_claim,
        "receipt_changed_path_list": receipt_path_lines,
        "harness_docstring_stale_v2": "artifact_version 2" in harness_text[:1600],
        "harness_docstring_stale_round1": "correction round 1" in harness_text[:1600],
        "package_still_claims_dependency_closure": "full boot-declared dependency closure" in package_text,
        "crawler_symbols_absent": all(
            symbol not in harness_text
            for symbol in ("stage_dependency_closure", "probe_mech_validator", "REPO_PATH_RX")
        ),
        "full_tree_probe_symbol_present": "def probe_full_tree" in harness_text,
    }


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        master = Path(td) / "candidate"
        build_candidate(master)
        base_failed, base_rows = H.run_acceptance(master)
        report: dict[str, Any] = {
            "review_probe_version": 1,
            "package_audit": package_audit(),
            "base_candidate": {
                "green": len(base_rows) - base_failed,
                "total": len(base_rows),
                "red": sorted(row["test_id"] for row in base_rows if not row["passed"]),
                "full_tree_file_count": sum(1 for _ in H.walk_files(master)),
            },
            "variants": {},
        }
        for name, (description, mutate, targets) in VARIANTS.items():
            report["variants"][name] = run_variant(
                master, name, description, mutate, targets
            )

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    output = HERE.with_name("independent_v3_probe_results_v1.json")
    output.write_text(rendered, encoding="utf-8")
    print(
        json.dumps(
            {
                "result_path": str(output),
                "base_candidate": report["base_candidate"],
                "variant_red_sets": {
                    name: result["red"] for name, result in report["variants"].items()
                },
                "variant_validator_exits": {
                    name: result["mechanism_validator_exit"]
                    for name, result in report["variants"].items()
                },
                "package_audit_summary": {
                    "digest_matches": report["package_audit"]["normalized_digest"]["matches"],
                    "refs_match": report["package_audit"]["all_input_and_supporting_hashes_match"],
                    "artifact_hashes_match": report["package_audit"]["all_receipt_artifact_hashes_match"],
                    "freeze_receipt_yaml_parse_passed": report["package_audit"]["freeze_receipt_yaml_parse"]["passed"],
                    "primary_diff_path_count": report["package_audit"]["primary_diff_path_count"],
                    "receipt_changed_path_count_claim": report["package_audit"]["receipt_changed_path_count_claim"],
                    "receipt_changed_path_list_count": len(report["package_audit"]["receipt_changed_path_list"]),
                    "harness_docstring_stale_v2": report["package_audit"]["harness_docstring_stale_v2"],
                    "package_still_claims_dependency_closure": report["package_audit"]["package_still_claims_dependency_closure"],
                    "crawler_symbols_absent": report["package_audit"]["crawler_symbols_absent"],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

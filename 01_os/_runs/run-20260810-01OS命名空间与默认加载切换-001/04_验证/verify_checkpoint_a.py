"""Fail-closed structural and repeatability verifier for Checkpoint A."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import yaml


ALLOWED_CLASSES = {"rewrite_current_path", "preserve_historical_literal"}
REQUIRED_STARTUP_FILES = {
    "AGENTS.md", "AGENT_WORKING_DISCIPLINE.md", "CLAUDE.md", "GEMINI.md",
    "README.md", "CORE_MANIFEST.yml", "01_os/README.md", "01_os/开发入口与单窗口任务规范_v1.md",
}


def fail(message: str) -> None:
    raise ValueError(message)


def git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if proc.returncode != 0:
        fail(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout.decode("utf-8", "replace")


def run_checked(command: list[str], cwd: Path) -> str:
    proc = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        fail(
            f"repeatability command exited {proc.returncode}: {' '.join(command)}; "
            f"{proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    return proc.stdout.decode("utf-8", "replace").strip()


def verify(repo_root: Path, run_root: Path, base: str) -> dict[str, int]:
    scanner_path = run_root / "04_验证" / "scan_os_namespace_refs.py"
    builder_path = run_root / "04_验证" / "build_review_manifests.py"
    scan_path = run_root / "04_验证" / "01_os引用扫描完整结果_v1.json"
    mapping_path = run_root / "02_路径映射" / "08_to_01引用分类_v1.yml"
    scope_path = run_root / "02_路径映射" / "reviewed_reference_scope_v1.yml"
    resolution_path = run_root / "02_路径映射" / "manual_review_resolution_v1.yml"
    startup_path = run_root / "03_启动入口盘点" / "默认启动关系盘点_v1.yml"
    amendment_path = run_root / "03_启动入口盘点" / "Checkpoint_B冻结修正计划_v1.yml"
    run_path = run_root / "run.yml"
    packet_path = run_root / "01_任务输入" / "任务包_v1.yml"

    scan = json.loads(scan_path.read_text(encoding="utf-8"))
    mapping = yaml.safe_load(mapping_path.read_text(encoding="utf-8"))
    scope = yaml.safe_load(scope_path.read_text(encoding="utf-8"))
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    startup = yaml.safe_load(startup_path.read_text(encoding="utf-8"))
    amendment = yaml.safe_load(amendment_path.read_text(encoding="utf-8"))
    run_record = yaml.safe_load(run_path.read_text(encoding="utf-8"))
    packet = yaml.safe_load(packet_path.read_text(encoding="utf-8"))

    expected_allowlist = ["01_os/_runs/run-20260810-01OS命名空间与默认加载切换-001/**"]
    if run_record.get("source_base") != base or packet.get("exact_base_sha") != base:
        fail("run/task packet base does not equal exact source base")
    if run_record.get("allowed_changed_paths") != expected_allowlist or packet.get("allowed_changed_paths") != expected_allowlist:
        fail("run/task packet allowlist is not the exact run prefix")
    if any(document.get("source_commit") != base for document in (scan, mapping, scope, resolution, startup, amendment)):
        fail("one or more Checkpoint A artifacts are not bound to the exact source base")
    if scan.get("enumeration") != "git ls-files -z with temporary index loaded from source_commit":
        fail("required git ls-files -z enumeration evidence missing")

    entries = scan.get("entries") or []
    mapping_entries = mapping.get("entries") or []
    if len(entries) != len(mapping_entries) or scan["text"]["occurrences"] != len(entries):
        fail("scan/mapping occurrence length mismatch")
    class_counts = Counter(item.get("proposed_classification") for item in entries)
    if set(class_counts) - ALLOWED_CLASSES:
        fail(f"unresolved or invalid final classes: {sorted(set(class_counts) - ALLOWED_CLASSES)}")
    measured = {
        "rewrite_current_path": class_counts["rewrite_current_path"],
        "preserve_historical_literal": class_counts["preserve_historical_literal"],
        "manual_review": 0,
    }
    if scan.get("classification") != measured or mapping.get("classification") != measured:
        fail("measured final classification totals do not match artifacts")

    seen_ids: set[str] = set()
    seen_positions: set[tuple[str, int, int]] = set()
    for scan_entry, map_entry in zip(entries, mapping_entries, strict=True):
        item_id = scan_entry.get("occurrence_id")
        position = (scan_entry["path"], scan_entry["line"], scan_entry["column"])
        if not item_id or item_id in seen_ids or position in seen_positions:
            fail(f"duplicate or missing occurrence identity: {position}")
        seen_ids.add(item_id)
        seen_positions.add(position)
        classification = scan_entry["proposed_classification"]
        semantic_group = (
            scan_entry.get("semantic_class")
            if classification == "rewrite_current_path"
            else scan_entry.get("historical_reason")
        )
        if not semantic_group or not scan_entry.get("reason") or not scan_entry.get("expected_after_cutover"):
            fail(f"incomplete final occurrence: {item_id}")
        expected_map = {
            "occurrence_id": item_id,
            "path": scan_entry["path"], "line": scan_entry["line"], "column": scan_entry["column"],
            "occurrence_on_line": scan_entry["occurrence_on_line"], "old_text": scan_entry["match"],
            "classification": classification, "classification_rule": scan_entry["classification_rule"],
            "semantic_group": semantic_group, "reason": scan_entry["reason"],
            "expected_after_cutover": scan_entry["expected_after_cutover"],
        }
        if map_entry != expected_map:
            fail(f"mapping entry diverges from scan entry: {item_id}")

    manual_rows = resolution.get("resolutions") or []
    manual_ids = [row.get("occurrence_id") for row in manual_rows]
    if resolution.get("original_manual_occurrences") != 205 or len(manual_rows) != 205:
        fail("manual resolution does not contain the complete original 205-item set")
    if len(set(manual_ids)) != 205 or not set(manual_ids).issubset(seen_ids):
        fail("manual resolution has duplicates, stale IDs, or IDs absent from the final partition")
    resolved_counts = Counter(row["final_classification"] for row in manual_rows)
    if set(resolved_counts) - ALLOWED_CLASSES:
        fail("manual resolution contains an invalid final class")
    closure = mapping.get("closure") or {}
    manual_closure = closure.get("manual_resolution") or {}
    if any(manual_closure.get(key) != value for key, value in {
        "original_manual_occurrences": 205, "covered": 205, "missing": 0, "stale": 0, "duplicates": 0,
    }.items()):
        fail("manual-resolution closure proof is incomplete")
    if closure.get("overlap") != 0 or closure.get("unassigned") != 0:
        fail("final reference partition has overlap or unassigned occurrences")

    retained = scope.get("retained_historical_occurrences") or []
    corrections = scope.get("classification_corrections") or []
    scope_ids = [row.get("occurrence_id") for row in retained + corrections]
    if (
        len(retained) != 47
        or len(corrections) != 3
        or len(set(scope_ids)) != 50
        or not set(scope_ids).issubset(seen_ids)
    ):
        fail("reviewed reference scope is not the exact 47+3 content-bound set")
    scope_closure = closure.get("reference_scope") or {}
    if scope_closure.get("raw_occurrences") != 4680 or scope_closure.get("excluded_generated_echo_occurrences") != 3586:
        fail("raw-to-reviewed scope closure measurements drifted")

    grouped = scan.get("grouped_counts") or {}
    rewrite_groups = grouped.get("rewrite_current_path_by_semantic_class") or {}
    historical_groups = grouped.get("preserve_historical_literal_by_reason") or {}
    if sum(rewrite_groups.values()) != measured["rewrite_current_path"]:
        fail("rewrite semantic groups do not sum to the measured rewrite partition")
    if sum(historical_groups.values()) != measured["preserve_historical_literal"]:
        fail("historical reason groups do not sum to the measured historical partition")
    if mapping.get("grouped_counts") != grouped:
        fail("mapping grouped counts diverge from scan")

    independent_paths = [
        value for value in git(repo_root, "ls-tree", "-r", "--name-only", base).splitlines() if value
    ]
    independent_physical = sum(path.startswith("01_os/") for path in independent_paths)
    if independent_physical != scan["physical"]["tracked_under_01_os"]:
        fail("independent git ls-tree physical count disagrees with scanner")

    if set(startup.get("inspected_files") or []) != REQUIRED_STARTUP_FILES:
        fail("startup inventory does not cover the exact required file set")
    planned = amendment.get("planned_B") or {}
    if planned.get("physical_root") != {"from": "01_os/", "to": "01_os/"}:
        fail("planned B physical root transition is not frozen")
    if planned.get("compatibility_shim") is not False or planned.get("root_lift") is not False:
        fail("planned B still permits a shim or root lift")
    if set((amendment.get("findings") or {})) != {
        "F1_retirement_wording_stale", "F2_deleted_root_docs_stale_references",
        "F3_unowned_OS_root_documents", "F4_final_namespace_decision", "F5_default_loading_architecture",
    }:
        fail("Checkpoint B amendment does not cover F1-F5 exactly")
    if amendment.get("checkpoint_A_boundary") != {
        "canonical_or_root_router_files_modified": False,
        "namespace_rename_executed": False,
        "checkpoint_B_executed": False,
    }:
        fail("Checkpoint A boundary attestation is incomplete")
    if (repo_root / "01_os").exists():
        fail("01_os exists during inventory-only checkpoint")
    for required in REQUIRED_STARTUP_FILES:
        if not (repo_root / required).is_file():
            fail(f"required startup file missing: {required}")

    with tempfile.TemporaryDirectory(prefix="checkpoint_a_repeat_") as temp_dir:
        temp = Path(temp_dir)
        raw_json, raw_map = temp / "raw.json", temp / "raw.yml"
        rebuilt_scope = temp / "reviewed_reference_scope_v1.yml"
        rebuilt_resolution = temp / "manual_review_resolution_v1.yml"
        final_json = temp / "01_os引用扫描完整结果_v1.json"
        final_map = temp / "08_to_01引用分类_v1.yml"
        run_checked([
            sys.executable, str(scanner_path), "--repo-root", str(repo_root), "--source-treeish", base,
            "--output", str(raw_json), "--mapping-output", str(raw_map),
        ], repo_root)
        run_checked([
            sys.executable, str(builder_path), "--raw-scan", str(raw_json), "--source-commit", base,
            "--scope-output", str(rebuilt_scope), "--resolution-output", str(rebuilt_resolution),
        ], repo_root)
        if rebuilt_scope.read_bytes() != scope_path.read_bytes() or rebuilt_resolution.read_bytes() != resolution_path.read_bytes():
            fail("review manifests are not byte-repeatable from the immutable source scan")
        run_checked([
            sys.executable, str(scanner_path), "--repo-root", str(repo_root), "--source-treeish", base,
            "--reference-scope", str(rebuilt_scope), "--manual-resolution", str(rebuilt_resolution),
            "--output", str(final_json), "--mapping-output", str(final_map),
        ], repo_root)
        if final_json.read_bytes() != scan_path.read_bytes() or final_map.read_bytes() != mapping_path.read_bytes():
            fail("final scan/mapping are not byte-repeatable")

        negative_json, negative_yaml = temp / "negative.json", temp / "negative.yml"
        negative = subprocess.run([
            sys.executable, str(scanner_path), "--repo-root", str(repo_root),
            "--source-treeish", "definitely-not-a-ref", "--reference-scope", str(scope_path),
            "--manual-resolution", str(resolution_path), "--output", str(negative_json),
            "--mapping-output", str(negative_yaml),
        ], cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if negative.returncode != 2 or negative_json.exists() or negative_yaml.exists():
            fail("invalid-treeish fail-closed probe failed")

    return {
        "tracked_under_01_os": independent_physical,
        "occurrences": len(entries),
        **measured,
        "overlap": 0,
        "unassigned": 0,
        "manual_resolution_covered": len(manual_rows),
        "manual_rewrite": resolved_counts["rewrite_current_path"],
        "manual_historical": resolved_counts["preserve_historical_literal"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    try:
        counts = verify(Path(args.repo_root).resolve(), Path(args.run_root).resolve(), args.base)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"checkpoint_a_verify_error: {exc}", file=sys.stderr)
        return 1
    print("checkpoint_a_verify_ok " + " ".join(f"{key}={value}" for key, value in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

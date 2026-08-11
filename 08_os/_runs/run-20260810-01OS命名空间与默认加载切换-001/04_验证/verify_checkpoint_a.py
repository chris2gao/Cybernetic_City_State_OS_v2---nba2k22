"""Fail-closed structural verifier for Checkpoint A inventory artifacts."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ALLOWED_CLASSES = {
    "rewrite_current_path",
    "preserve_historical_literal",
    "manual_review",
}
REQUIRED_STARTUP_FILES = {
    "AGENTS.md",
    "AGENT_WORKING_DISCIPLINE.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "CORE_MANIFEST.yml",
    "08_os/README.md",
    "08_os/开发入口与单窗口任务规范_v1.md",
}


def fail(message: str) -> None:
    raise ValueError(message)


def git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        fail(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout.decode("utf-8", "replace")


def verify(repo_root: Path, run_root: Path, base: str) -> dict[str, int]:
    scanner_path = run_root / "04_验证" / "scan_os_namespace_refs.py"
    scan_path = run_root / "04_验证" / "08_os引用扫描完整结果_v1.json"
    mapping_path = run_root / "02_路径映射" / "08_to_01引用分类_v1.yml"
    startup_path = run_root / "03_启动入口盘点" / "默认启动关系盘点_v1.yml"
    run_path = run_root / "run.yml"
    packet_path = run_root / "01_任务输入" / "任务包_v1.yml"
    validation_path = run_root / "04_验证" / "验证结果_v1.yml"
    scan = json.loads(scan_path.read_text(encoding="utf-8"))
    mapping = yaml.safe_load(mapping_path.read_text(encoding="utf-8"))
    startup = yaml.safe_load(startup_path.read_text(encoding="utf-8"))
    run_record = yaml.safe_load(run_path.read_text(encoding="utf-8"))
    packet = yaml.safe_load(packet_path.read_text(encoding="utf-8"))
    validation = yaml.safe_load(validation_path.read_text(encoding="utf-8"))

    expected_allowlist = ["08_os/_runs/run-20260810-01OS命名空间与默认加载切换-001/**"]
    if run_record.get("source_base") != base or packet.get("exact_base_sha") != base:
        fail("run/task packet base does not equal exact source base")
    if run_record.get("allowed_changed_paths") != expected_allowlist:
        fail("run record allowlist is not the exact run prefix")
    if packet.get("allowed_changed_paths") != expected_allowlist:
        fail("task packet allowlist is not the exact run prefix")

    if scan.get("source_commit") != base or mapping.get("source_commit") != base:
        fail("scan/mapping source_commit does not equal exact base")
    if scan.get("enumeration") != "git ls-files -z with temporary index loaded from source_commit":
        fail("required git ls-files -z enumeration evidence missing")

    entries = scan.get("entries") or []
    mapping_entries = mapping.get("entries") or []
    if len(entries) != len(mapping_entries):
        fail("scan and mapping entry counts differ")
    if scan["text"]["occurrences"] != len(entries):
        fail("scan occurrence count does not equal entries length")
    files_with_hits = len({entry["path"] for entry in entries})
    if scan["text"]["files_with_08_os_reference"] != files_with_hits:
        fail("files-with-hit count mismatch")

    class_counts = {name: 0 for name in ALLOWED_CLASSES}
    seen_keys: set[tuple[str, int, int]] = set()
    for scan_entry, map_entry in zip(entries, mapping_entries, strict=True):
        classification = scan_entry.get("proposed_classification")
        if classification not in ALLOWED_CLASSES:
            fail(f"invalid classification: {classification}")
        class_counts[classification] += 1
        key = (scan_entry["path"], scan_entry["line"], scan_entry["column"])
        if key in seen_keys:
            fail(f"duplicate occurrence key: {key}")
        seen_keys.add(key)
        if not scan_entry.get("match") or not scan_entry.get("reason") or not scan_entry.get("expected_after_cutover"):
            fail(f"incomplete scan entry: {key}")
        if len(scan_entry.get("context") or []) > 7:
            fail(f"unbounded context: {key}")
        expected_map = {
            "path": scan_entry["path"],
            "line": scan_entry["line"],
            "column": scan_entry["column"],
            "old_text": scan_entry["match"],
            "classification": classification,
            "classification_rule": scan_entry["classification_rule"],
            "reason": scan_entry["reason"],
            "expected_after_cutover": scan_entry["expected_after_cutover"],
        }
        if map_entry != expected_map:
            fail(f"mapping entry diverges from scan entry: {key}")

    if scan["classification"] != class_counts or mapping["classification"] != class_counts:
        fail("classification totals mismatch")
    if mapping["physical"]["tracked_under_08_os"] != scan["physical"]["tracked_under_08_os"]:
        fail("physical count mismatch")
    if mapping["text"]["files_with_08_os_reference"] != files_with_hits:
        fail("mapping files-with-hit mismatch")
    if mapping["text"]["occurrences"] != len(entries):
        fail("mapping occurrence count mismatch")
    if validation.get("inventory", {}).get("classification") != class_counts:
        fail("validation record classification totals mismatch")

    independent_paths = [
        item.decode("utf-8", "surrogateescape")
        for item in subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "-z", base],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout.split(b"\0")
        if item
    ]
    independent_physical = sum(path.startswith("08_os/") for path in independent_paths)
    if independent_physical != scan["physical"]["tracked_under_08_os"]:
        fail("independent git ls-tree physical count disagrees with scanner")

    scanner_source = scanner_path.read_text(encoding="utf-8")
    if '["ls-files", "-z"]' not in scanner_source or "GIT_INDEX_FILE" not in scanner_source:
        fail("scanner source does not contain required git ls-files -z temporary-index enumeration")
    with tempfile.TemporaryDirectory(prefix="checkpoint_a_negative_") as temp_dir:
        negative_json = Path(temp_dir) / "negative.json"
        negative_yaml = Path(temp_dir) / "negative.yml"
        negative = subprocess.run(
            [
                sys.executable,
                str(scanner_path),
                "--repo-root",
                str(repo_root),
                "--source-treeish",
                "definitely-not-a-ref",
                "--output",
                str(negative_json),
                "--mapping-output",
                str(negative_yaml),
            ],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if negative.returncode != 2:
            fail(f"scanner invalid-treeish probe returned {negative.returncode}, expected 2")
        if negative_json.exists() or negative_yaml.exists():
            fail("scanner wrote artifacts after invalid-treeish failure")

    if set(startup.get("inspected_files") or []) != REQUIRED_STARTUP_FILES:
        fail("startup inventory does not cover the exact required file set")
    if startup.get("target_architecture", {}).get("shared_canonical_startup_router") != "AGENTS.md":
        fail("target startup router not frozen")
    if startup.get("freeze_decisions", {}).get("permanent_os_root_after_cutover") != "01_os/":
        fail("permanent 01_os root not frozen")
    if startup.get("freeze_decisions", {}).get("checkpoint_A_modified_any_inspected_file") is not False:
        fail("startup inventory does not attest read-only inspection")

    if (repo_root / "01_os").exists():
        fail("01_os exists during inventory-only checkpoint")
    for required in REQUIRED_STARTUP_FILES:
        if not (repo_root / required).is_file():
            fail(f"required startup file missing: {required}")
    if git(repo_root, "rev-parse", f"{base}^{{commit}}").strip() != base:
        fail("base is not a resolvable 40-character commit")

    return {
        "tracked_under_08_os": scan["physical"]["tracked_under_08_os"],
        "files_with_hit": files_with_hits,
        "occurrences": len(entries),
        **class_counts,
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

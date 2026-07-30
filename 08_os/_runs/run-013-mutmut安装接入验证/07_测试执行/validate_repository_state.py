from __future__ import annotations

import json
from pathlib import Path
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[4]
BASE = "31ce5812bf34e7e4fc338543841973246a6a2467"
RUN_ROOT = ROOT / "08_os/_runs/run-013-mutmut安装接入验证"
REGISTRY_PATH = ROOT / "08_os/05_registry/skills_and_tools_v1.yml"
RUN_PATH = RUN_ROOT / "run.yml"
RESULTS_PATH = RUN_ROOT / "07_测试执行/results.json"
RECEIPT_PATH = RUN_ROOT / "01_任务输入/environment_receipt.json"
TARGET_PATH = (
    ROOT / "08_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py"
)
WRAPPER_PATH = ROOT / "08_os/06_execution/tools/mutmut/invoke.sh"


registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
run = yaml.safe_load(RUN_PATH.read_text(encoding="utf-8"))
results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

assert registry["schema_version"] == "citystate.registry.v1"
assert run["schema_version"] == "os_development_run.v1"
assert results["schema_version"] == "citystate.mutmut_validation.v1"
assert receipt["schema_version"] == "citystate.mutmut_environment_receipt.v1"

entry_fields = {
    "path",
    "purpose",
    "loader",
    "loader_class",
    "discovery",
    "evidence",
    "cache_dirs",
    "failure_surfacing",
    "deletion_rule",
}
for entry in registry["entries"]:
    assert entry_fields <= entry.keys(), (entry["path"], entry_fields - entry.keys())
    assert (ROOT / entry["path"]).exists(), entry["path"]
    evidence = entry["evidence"]
    if (
        isinstance(evidence, str)
        and "/" in evidence
        and " " not in evidence
        and not evidence.startswith(("http://", "https://"))
    ):
        assert (ROOT / evidence).exists(), evidence

tools = {item["name"]: item for item in registry["tools"]}
tool = tools["mutmut"]
assert tool["version"] == "3.6.0"
assert tool["status"] == "verified_on_demand"
assert tool["mount"] == "on_demand_wsl_cli"
assert tool["default_loaded"] is False
assert tool["mcp_exposed"] is False
assert tool["expected_version"] == "3.6.0"
assert tool["version_gate"] == "exact_runtime_probe_before_mutation"
assert tool["target_policy"] == "explicit_single_python_file_allowlist"
assert tool["validated_at"] == "2026-07-30"
assert (ROOT / tool["evidence"]).exists()
assert (ROOT / tool["canonical_wrapper"]).exists()

assert run["task_id"] == "mutmut-wsl-installation-validation-001"
assert run["implementation_base"] == BASE
assert run["work_branch"] == "codex/mutmut-wsl-installation-validation-001"
assert run["tool"]["status"] == "verified_on_demand"
assert run["tool"]["default_loaded"] is False
assert run["tool"]["mcp_exposed"] is False
assert run["measurement"]["exact_model_tokens"] == "not_observable"
assert run["measurement"]["peak_process_tree_memory"] == "not_observable_reliably"
assert run["measurement"]["resident_processes_after_run"] == 0
assert run["measurement"]["system_install_performed"] is False
assert run["measurement"]["sudo_used"] is False

assert results["summary"] == {
    "environment_passed": True,
    "calibration_passed": True,
    "real_target_passed": True,
    "wrapper_boundary_passed": True,
    "process_residue_count": 0,
    "all_passed": True,
}
weak = results["calibration"]["runs"][:2]
strong = results["calibration"]["runs"][2:]
assert all(item["status_counts"] == {"killed": 3, "survived": 5} for item in weak)
assert all(item["status_counts"] == {"killed": 6, "survived": 2} for item in strong)
assert results["real_target"]["initial"]["status_counts"] == {
    "killed": 118,
    "survived": 11,
}
for item in results["real_target"]["strengthened_wrapper_runs"]:
    assert item["status_counts"] == {"killed": 127, "survived": 2}
assert len(results["real_target"]["equivalent_survivors"]) == 2
assert results["real_target"]["canonical_source_modified"] is False
assert results["wrapper"]["apply_exposed"] is False
assert all(item["passed"] is True for item in results["wrapper"]["cases"])
assert results["resources"]["exact_model_tokens"] == "not_observable"
assert results["resources"]["resident_processes_after_run"] == 0
assert results["token_and_context"]["boot_loaded"] is False
assert results["token_and_context"]["mcp_exposed"] is False
assert results["cleanup"] == {
    "repository_mutants_absent": True,
    "repository_target_copy_absent": True,
    "dirty_sentinel_absent": True,
    "temporary_archives_cleaned": True,
}

assert receipt["virtualenv"]["mutmut_version"] == "3.6.0"
assert receipt["virtualenv"]["include_system_site_packages"] is False
assert receipt["system_install_performed"] is False
assert receipt["sudo_used"] is False
assert receipt["credentials_used_or_recorded"] is False
assert receipt["process_residue_count"] == 0
assert receipt["origin_master_at_start"] == receipt["origin_master_at_end"]

assert WRAPPER_PATH.stat().st_mode & 0o111
wrapper_text = WRAPPER_PATH.read_text(encoding="utf-8")
assert "mutmut apply" not in wrapper_text
assert " archive --format=tar HEAD " in wrapper_text
assert "status --porcelain" in wrapper_text
assert "EXPECTED_MUTMUT_VERSION=\"3.6.0\"" in wrapper_text

subprocess.run(
    ["git", "diff", "--quiet", BASE, "--", TARGET_PATH.relative_to(ROOT)],
    cwd=ROOT,
    check=True,
)
subprocess.run(
    ["git", "diff", "--quiet", BASE, "--", "08_os/02_boot"],
    cwd=ROOT,
    check=True,
)
for path in (ROOT / "08_os/02_boot").rglob("*"):
    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        assert "mutmut" not in text, path

canonical_paths = [
    ROOT / "08_os/04_skills_and_tools/README.md",
    ROOT / "08_os/04_skills_and_tools/mutmut/README.md",
    ROOT / "08_os/05_registry/skills_and_tools_v1.yml",
    ROOT / "08_os/06_execution/tools/mutmut/README.md",
    WRAPPER_PATH,
]
for path in canonical_paths:
    text = path.read_text(encoding="utf-8")
    assert "/home/gk" not in text, path
    assert r"C:\Users\gk" not in text, path

allowed_exact = {
    "08_os/04_skills_and_tools/README.md",
    "08_os/05_registry/skills_and_tools_v1.yml",
}
allowed_prefixes = (
    "08_os/04_skills_and_tools/mutmut/",
    "08_os/06_execution/tools/mutmut/",
    "08_os/_runs/run-013-mutmut安装接入验证/",
)
changed = subprocess.check_output(
    [
        "git",
        "-c",
        "core.quotepath=false",
        "diff",
        "--name-only",
        f"{BASE}..HEAD",
    ],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
).splitlines()
status = subprocess.check_output(
    ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
    cwd=ROOT,
)
status_paths = []
for record in filter(None, status.decode("utf-8").split("\0")):
    status_paths.append(record[3:].replace("\\", "/"))
for path in [*changed, *status_paths]:
    assert path in allowed_exact or path.startswith(allowed_prefixes), path

assert not (RUN_ROOT / "07_测试执行/real_target_tests/mutants").exists()
assert not (RUN_ROOT / "07_测试执行/real_target_tests/target").exists()
assert (
    subprocess.check_output(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    ).strip()
    == "codex/mutmut-wsl-installation-validation-001"
)

print("PASS yaml_safe_load")
print("PASS registry_entries_and_repository_paths")
print("PASS verified_on_demand_metadata")
print("PASS calibration_real_target_and_wrapper_receipts")
print("PASS canonical_target_unchanged")
print("PASS boot_non_reference_and_unchanged")
print("PASS canonical_absolute_user_path_scan")
print("PASS cleanup_and_changed_path_allowlist")

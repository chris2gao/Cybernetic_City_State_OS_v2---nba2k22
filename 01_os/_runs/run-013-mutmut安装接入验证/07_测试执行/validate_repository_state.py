from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[4]
BASE = "31ce5812bf34e7e4fc338543841973246a6a2467"
REVIEWED_CANDIDATE = "382750bad85231736920ab0f04a992b8a91f408c"
STALE_LOCAL_TRACKING = "987ff40fa0317053bf0484f6e3556976e560f63b"
CORRECTION_BRANCH = "codex/mutmut-evidence-consistency-fix-001"
RUN_ROOT = ROOT / "01_os/_runs/run-013-mutmut安装接入验证"
REGISTRY_PATH = ROOT / "01_os/05_registry/skills_and_tools_v1.yml"
RUN_PATH = RUN_ROOT / "run.yml"
RESULTS_PATH = RUN_ROOT / "07_测试执行/results.json"
RECEIPT_PATH = RUN_ROOT / "01_任务输入/environment_receipt.json"
ENVIRONMENT_SUMMARY_PATH = RUN_ROOT / "01_任务输入/环境与安装回执.md"
CHANGE_RECORD_PATH = RUN_ROOT / "06_执行/变更清单.md"
TEST_RECORD_PATH = RUN_ROOT / "07_测试执行/测试记录.md"
REVIEW_HANDOFF_PATH = RUN_ROOT / "08_结论/审核回传.md"
TARGET_PATH = (
    ROOT / "01_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py"
)
WRAPPER_PATH = ROOT / "01_os/06_execution/tools/mutmut/invoke.sh"


def git_show_bytes(revision: str, relative: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{relative}"],
        cwd=ROOT,
    )


def git_show_json(revision: str, relative: str) -> dict[str, object]:
    return json.loads(git_show_bytes(revision, relative).decode("utf-8"))


registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
run = yaml.safe_load(RUN_PATH.read_text(encoding="utf-8"))
results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
candidate_results = git_show_json(
    REVIEWED_CANDIDATE,
    RESULTS_PATH.relative_to(ROOT).as_posix(),
)
candidate_receipt = git_show_json(
    REVIEWED_CANDIDATE,
    RECEIPT_PATH.relative_to(ROOT).as_posix(),
)

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

revision = run["evidence_consistency_revision"]
assert revision["task_id"] == "mutmut-evidence-consistency-fix-001"
assert revision["work_branch"] == CORRECTION_BRANCH
assert revision["reviewed_candidate"] == REVIEWED_CANDIDATE
assert revision["finding"] == {"MMV-R01": "resolved"}

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
assert set(results["resources"]["lifecycle_measurement"]) == {
    "installed_idle",
    "registered_on_demand",
    "calibration_invoked",
    "real_target_invoked",
    "diagnostic_consumed_by_model",
}
assert results["resources"]["lifecycle_measurement"]["registered_on_demand"][
    "default_loaded"
] is False
assert results["resources"]["lifecycle_measurement"]["registered_on_demand"][
    "mcp_exposed"
] is False
assert results["token_and_context"]["boot_loaded"] is False
assert results["token_and_context"]["mcp_exposed"] is False
assert results["cleanup"] == {
    "repository_mutants_absent": True,
    "repository_target_copy_absent": True,
    "dirty_sentinel_absent": True,
    "temporary_archives_cleaned": True,
}

preserved_result_keys = {
    "schema_version",
    "generated_at_utc",
    "task_id",
    "source_head",
    "validation_head",
    "summary",
    "environment",
    "fork_probe",
    "calibration",
    "real_target",
    "wrapper",
    "resources",
    "token_and_context",
    "process_residue",
    "cleanup",
}
for key in preserved_result_keys:
    assert results[key] == candidate_results[key], key

assert receipt["virtualenv"]["mutmut_version"] == "3.6.0"
assert receipt["virtualenv"]["include_system_site_packages"] is False
assert receipt["system_install_performed"] is False
assert receipt["sudo_used"] is False
assert receipt["credentials_used_or_recorded"] is False
assert receipt["process_residue_count"] == 0
for command_id in (
    "pip",
    "pip_show_mutmut",
    "pip_show_libcst",
    "pytest",
    "version",
):
    assert receipt["commands"][command_id]["exit_code"] == 0, command_id

new_receipt_evidence_keys = {
    "wsl_local_remote_tracking_master_at_start",
    "wsl_local_remote_tracking_master_at_end",
    "implementation_base",
    "reviewed_candidate",
    "authoritative_remote_master_at_handoff",
    "candidate_relation",
    "local_clone_fallback_note",
}
old_ambiguous_keys = {"origin_master_at_start", "origin_master_at_end"}
assert not old_ambiguous_keys.intersection(receipt)
assert not old_ambiguous_keys.intersection(results["git"])
candidate_receipt_without_ambiguous = {
    key: value
    for key, value in candidate_receipt.items()
    if key not in old_ambiguous_keys
}
corrected_receipt_without_evidence = {
    key: value
    for key, value in receipt.items()
    if key not in new_receipt_evidence_keys
}
assert corrected_receipt_without_evidence == candidate_receipt_without_ambiguous

for evidence in (receipt, results["git"], revision):
    assert (
        evidence["wsl_local_remote_tracking_master_at_start"]
        == STALE_LOCAL_TRACKING
    )
    assert (
        evidence["wsl_local_remote_tracking_master_at_end"]
        == STALE_LOCAL_TRACKING
    )
    assert (
        evidence["wsl_local_remote_tracking_master_at_start"]
        == evidence["wsl_local_remote_tracking_master_at_end"]
    )
    assert evidence["wsl_local_remote_tracking_master_at_start"] != BASE
    assert evidence["implementation_base"] == BASE
    assert evidence["reviewed_candidate"] == REVIEWED_CANDIDATE
    authoritative = evidence["authoritative_remote_master_at_handoff"]
    assert authoritative["sha"] == BASE
    assert authoritative["source"] in {"git_ls_remote", "github_api"}
    assert authoritative["ref"] == "refs/heads/master"
    assert authoritative["observed_at_utc"]
    assert authoritative["command_exit_code"] == 0
    relation = evidence["candidate_relation"]
    assert relation == {
        "merge_base_with_implementation_base": BASE,
        "implementation_base_ahead": 0,
        "candidate_ahead": 14,
        "local_remote_tracking_ref_used_for_relation": False,
    }

assert results["git"]["work_branch"] == "codex/mutmut-wsl-installation-validation-001"
assert results["git"]["master_modified"] is False
assert results["git"]["merge_performed"] is False
assert receipt["authoritative_remote_master_at_handoff"] == results["git"][
    "authoritative_remote_master_at_handoff"
]
assert receipt["candidate_relation"] == results["git"]["candidate_relation"]
assert revision["authoritative_remote_master_at_handoff"] == {
    key: value
    for key, value in receipt["authoritative_remote_master_at_handoff"].items()
    if key != "command"
}
assert revision["candidate_relation"] == receipt["candidate_relation"]
assert revision["local_clone_fallback_tracking_ref_authoritative"] is False
assert revision["mutation_retest"] == "not_run_accepted_without_retest"
assert (
    revision["full_pytest_retest"]
    == "not_run_no_code_or_test_semantics_changed"
)

merge_base = subprocess.check_output(
    ["git", "merge-base", BASE, REVIEWED_CANDIDATE],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
).strip()
assert merge_base == BASE
relation_counts = subprocess.check_output(
    ["git", "rev-list", "--left-right", "--count", f"{BASE}...{REVIEWED_CANDIDATE}"],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
).split()
assert relation_counts == ["0", "14"], relation_counts
subprocess.run(
    ["git", "merge-base", "--is-ancestor", REVIEWED_CANDIDATE, "HEAD"],
    cwd=ROOT,
    check=True,
)

wrapper_tree_entry = subprocess.check_output(
    [
        "git",
        "ls-tree",
        REVIEWED_CANDIDATE,
        "--",
        WRAPPER_PATH.relative_to(ROOT).as_posix(),
    ],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
).split()
assert wrapper_tree_entry[0] == "100755"
wrapper_text = WRAPPER_PATH.read_text(encoding="utf-8")
assert "mutmut apply" not in wrapper_text
assert " archive --format=tar HEAD " in wrapper_text
assert "status --porcelain" in wrapper_text
assert "EXPECTED_MUTMUT_VERSION=\"3.6.0\"" in wrapper_text

subprocess.run(
    [
        "git",
        "diff",
        "--quiet",
        REVIEWED_CANDIDATE,
        "--",
        TARGET_PATH.relative_to(ROOT),
    ],
    cwd=ROOT,
    check=True,
)
subprocess.run(
    ["git", "diff", "--quiet", REVIEWED_CANDIDATE, "--", "01_os/02_boot"],
    cwd=ROOT,
    check=True,
)
for path in (ROOT / "01_os/02_boot").rglob("*"):
    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        assert "mutmut" not in text, path

canonical_paths = [
    ROOT / "01_os/04_skills_and_tools/README.md",
    ROOT / "01_os/04_skills_and_tools/mutmut/README.md",
    ROOT / "01_os/05_registry/skills_and_tools_v1.yml",
    ROOT / "01_os/06_execution/tools/mutmut/README.md",
    WRAPPER_PATH,
]
for path in canonical_paths:
    text = path.read_text(encoding="utf-8")
    assert "/home/gk" not in text, path
    assert r"C:\Users\gk" not in text, path

allowed_exact = {
    "01_os/_runs/run-013-mutmut安装接入验证/01_任务输入/environment_receipt.json",
    "01_os/_runs/run-013-mutmut安装接入验证/01_任务输入/环境与安装回执.md",
    "01_os/_runs/run-013-mutmut安装接入验证/06_执行/变更清单.md",
    "01_os/_runs/run-013-mutmut安装接入验证/07_测试执行/results.json",
    "01_os/_runs/run-013-mutmut安装接入验证/07_测试执行/validate_repository_state.py",
    "01_os/_runs/run-013-mutmut安装接入验证/07_测试执行/测试记录.md",
    "01_os/_runs/run-013-mutmut安装接入验证/08_结论/审核回传.md",
    "01_os/_runs/run-013-mutmut安装接入验证/run.yml",
}
changed = subprocess.check_output(
    [
        "git",
        "-c",
        "core.quotepath=false",
        "diff",
        "--name-only",
        f"{REVIEWED_CANDIDATE}..HEAD",
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
    assert path in allowed_exact, path

preserved_prefixes = (
    "01_os/02_boot/",
    "01_os/04_skills_and_tools/",
    "01_os/05_registry/",
    "01_os/06_execution/tools/mutmut/",
    "01_os/06_execution/tools/check_jsonschema/",
    "07_Compiler/",
)
candidate_tracked = subprocess.check_output(
    ["git", "-c", "core.quotepath=false", "ls-tree", "-r", "--name-only", REVIEWED_CANDIDATE],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
).splitlines()
for relative in candidate_tracked:
    if not relative.startswith(preserved_prefixes):
        continue
    path = ROOT / relative
    assert path.is_file(), relative
    assert git_show_bytes("HEAD", relative) == git_show_bytes(
        REVIEWED_CANDIDATE,
        relative,
    ), relative

documentation = {
    "environment_summary": ENVIRONMENT_SUMMARY_PATH.read_text(encoding="utf-8"),
    "change_record": CHANGE_RECORD_PATH.read_text(encoding="utf-8"),
    "test_record": TEST_RECORD_PATH.read_text(encoding="utf-8"),
    "review_handoff": REVIEW_HANDOFF_PATH.read_text(encoding="utf-8"),
}
for name, text in documentation.items():
    assert STALE_LOCAL_TRACKING in text, name
    assert BASE in text, name
    assert "local" in text.lower(), name
assert REVIEWED_CANDIDATE in documentation["review_handoff"]
assert "authoritative_remote_master_at_handoff" in documentation["review_handoff"]
assert "origin/master at start/end" not in documentation["review_handoff"]
assert "MMV-R01" in documentation["change_record"]
assert "MMV-R01" in documentation["test_record"]
assert "MMV-R01" in documentation["review_handoff"]

high_confidence_secret_patterns = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
]
for relative in sorted(set([*changed, *status_paths])):
    path = ROOT / relative
    if not path.is_file() or path.stat().st_size > 2_000_000:
        continue
    payload = path.read_bytes()
    if b"\0" in payload:
        continue
    text = payload.decode("utf-8", errors="ignore")
    assert not any(pattern.search(text) for pattern in high_confidence_secret_patterns), (
        relative
    )

assert not (RUN_ROOT / "07_测试执行/real_target_tests/mutants").exists()
assert not (RUN_ROOT / "07_测试执行/real_target_tests/target").exists()
assert (
    subprocess.check_output(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    ).strip()
    == CORRECTION_BRANCH
)

print("PASS yaml_safe_load")
print("PASS registry_entries_and_repository_paths")
print("PASS verified_on_demand_metadata")
print("PASS calibration_real_target_and_wrapper_receipts")
print("PASS reviewed_candidate_machine_results_preserved")
print("PASS local_tracking_implementation_base_authoritative_remote_classification")
print("PASS candidate_merge_base_and_ahead_behind_relation")
print("PASS forbidden_candidate_blobs_unchanged")
print("PASS canonical_target_unchanged")
print("PASS boot_non_reference_and_unchanged")
print("PASS canonical_absolute_user_path_scan")
print("PASS scoped_high_confidence_secret_scan")
print("PASS correction_document_consistency")
print("PASS cleanup_and_correction_changed_path_allowlist")

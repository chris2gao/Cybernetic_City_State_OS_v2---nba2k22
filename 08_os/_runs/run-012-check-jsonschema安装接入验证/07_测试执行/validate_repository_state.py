from __future__ import annotations

import json
from pathlib import Path
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[4]
REGISTRY_PATH = ROOT / "08_os/05_registry/skills_and_tools_v1.yml"
RUN_PATH = ROOT / "08_os/_runs/run-012-check-jsonschema安装接入验证/run.yml"
RESULTS_PATH = (
    ROOT
    / "08_os/_runs/run-012-check-jsonschema安装接入验证/07_测试执行/results.json"
)
INSTALL_RECEIPT_PATH = (
    ROOT
    / "08_os/_runs/run-012-check-jsonschema安装接入验证/01_任务输入"
    / "安装真实性命令回执.json"
)
BASE = "987ff40fa0317053bf0484f6e3556976e560f63b"


registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
run = yaml.safe_load(RUN_PATH.read_text(encoding="utf-8"))
results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
installation = json.loads(INSTALL_RECEIPT_PATH.read_text(encoding="utf-8"))

assert registry["schema_version"] == "citystate.registry.v1"
assert run["schema_version"] == "os_development_run.v1"

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

tools = {tool["name"]: tool for tool in registry["tools"]}
tool = tools["check-jsonschema"]
assert tool["version"] == "0.37.4"
assert tool["status"] == "verified_on_demand"
assert tool["mount"] == "on_demand_cli"
assert tool["default_loaded"] is False
assert tool["mcp_exposed"] is False
assert tool["expected_version"] == "0.37.4"
assert tool["version_gate"] == "exact_runtime_probe_before_validation"
assert tool["schema_reference_policy"] == "self_contained_json_fragment_only"
assert tool["validated_at"] == "2026-07-30"
assert (ROOT / tool["evidence"]).exists()
assert (ROOT / tool["canonical_wrapper"]).exists()
assert (ROOT / tool["schema_preflight"]).exists()

assert run["tool"]["status"] == "verified_on_demand"
assert run["tool"]["default_loaded"] is False
assert run["tool"]["mcp_exposed"] is False
assert run["tool"]["expected_version"] == "0.37.4"
assert run["tool"]["version_gate"] == "exact_runtime_probe_before_validation"
assert run["tool"]["schema_reference_policy"] == "self_contained_json_fragment_only"
assert run["revision"]["findings"] == {
    "CJV-R01": "resolved",
    "CJV-R02": "resolved",
}
assert run["validation"]["original_matrix_27"] == "passed"
assert run["validation"]["network_reference_closure_10"] == "passed"
assert run["validation"]["version_boundary_4"] == "passed"
assert run["validation"]["validation_not_started_sentinels"] == "passed"
assert run["measurement"]["exact_model_tokens"] == "not_observable"
assert run["measurement"]["network_packet_capture"] == "not_run"
assert (
    run["measurement"]["network_behavior"]
    == "not_observable_no_packet_capture"
)
assert run["measurement"]["resident_processes_after_run"] == 0
assert run["measurement"]["environment_changes_performed"] is False

assert results["summary"] == {
    "total_cases": 43,
    "passed_cases": 43,
    "failed_cases": 0,
    "original_cases": 27,
    "original_cases_passed": 27,
    "correction_cases": 14,
    "correction_cases_passed": 14,
    "measurement_cases": 2,
    "measurement_cases_passed": 2,
    "all_passed": True,
}
assert results["repeatability"]["run_count"] == 5
assert results["repeatability"]["identical_exit_and_diagnostics"] is True
assert results["process_residue"]["matching_process_count"] == 0
assert results["network_measurement"] == "not_observable_no_packet_capture"
assert "direct CLI bypass remains network-capable" in results["local_only_design"]
assert (
    results["token_and_context"]["comparison"]["proxy_label"]
    == "proxy_not_billing_tokens"
)
for measurement in results["gate_measurements"].values():
    assert measurement > 0
assert run["measurement"]["version_probe_ms"] == results["gate_measurements"][
    "version_probe_ms"
]
assert run["measurement"]["schema_preflight_ms"] == results["gate_measurements"][
    "schema_preflight_ms"
]
assert run["measurement"]["direct_cli_validation_ms"] == results[
    "gate_measurements"
]["direct_cli_validation_ms"]
assert run["measurement"]["wrapper_total_ms"] == results["gate_measurements"][
    "wrapper_total_ms"
]

cases = {item["id"]: item for item in results["cases"]}
expected_correction_exits = {
    "CJV-FRAGMENT-REF": 0,
    "CJV-HTTPS-REF": 65,
    "CJV-HTTP-DYNAMIC-REF": 65,
    "CJV-HTTPS-RECURSIVE-REF": 65,
    "CJV-RELATIVE-REF": 65,
    "CJV-HTTPS-ID": 65,
    "CJV-HTTP-LEGACY-ID": 65,
    "CJV-NONSTRING-REF": 65,
    "CJV-YAML-SCHEMA": 65,
    "CJV-DAMAGED-JSON": 65,
    "CJV-REAL-VERSION": 0,
    "CJV-FAKE-VERSION": 78,
    "CJV-CORRUPT-VERSION": 78,
    "CJV-PROBE-FAILURE": 78,
}
for case_id, expected_exit in expected_correction_exits.items():
    case = cases[case_id]
    assert case["passed"] is True, case_id
    assert case["result"]["exit_code"] == expected_exit, case_id
    assert case["forbidden_path_absent"] is True, case_id

commands = {item["id"]: item for item in installation["commands"]}
assert commands["PY-VERSION"]["exit_code"] == 0
assert "Python 3.14.6" in commands["PY-VERSION"]["stdout"]
assert commands["PIPX-VERSION-DIRECT"]["exit_code"] == 127
assert commands["PIPX-LIST-DIRECT"]["exit_code"] == 127
assert commands["PIPX-VERSION-MODULE"]["exit_code"] == 0
assert commands["PIPX-VERSION-MODULE"]["stdout"].strip() == "1.16.5"
assert commands["TOOL-VERSION"]["exit_code"] == 0
assert "version 0.37.4" in commands["TOOL-VERSION"]["stdout"]
assert commands["NEW-SUBPROCESS-PATH"]["exit_code"] == 0
assert installation["process_residue"]["matching_process_count"] == 0
assert installation["environment_changes_performed"] is False

canonical_paths = [
    ROOT / "08_os/04_skills_and_tools/README.md",
    ROOT / "08_os/04_skills_and_tools/check-jsonschema/README.md",
    ROOT / "08_os/05_registry/skills_and_tools_v1.yml",
    ROOT / "08_os/06_execution/tools/check_jsonschema/README.md",
    ROOT / "08_os/06_execution/tools/check_jsonschema/invoke.ps1",
    ROOT / "08_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py",
]
for path in canonical_paths:
    text = path.read_text(encoding="utf-8")
    assert r"C:\Users\gk" not in text, path

boot_root = ROOT / "08_os/02_boot"
for path in boot_root.rglob("*"):
    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert "check-jsonschema" not in text, path
        assert "check_jsonschema" not in text, path

subprocess.run(
    ["git", "diff", "--quiet", BASE, "--", "08_os/02_boot"],
    cwd=ROOT,
    check=True,
)

status = subprocess.check_output(
    ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
)
allowed_exact = {
    "08_os/04_skills_and_tools/README.md",
    "08_os/05_registry/skills_and_tools_v1.yml",
}
allowed_prefixes = (
    "08_os/04_skills_and_tools/check-jsonschema/",
    "08_os/06_execution/tools/check_jsonschema/",
    "08_os/_runs/run-012-check-jsonschema安装接入验证/",
)
for record in filter(None, status.split("\0")):
    changed = record[3:].replace("\\", "/")
    assert changed in allowed_exact or changed.startswith(allowed_prefixes), changed

print("PASS yaml_safe_load")
print("PASS registry_entries_and_repository_paths")
print("PASS verified_on_demand_metadata")
print("PASS installation_and_validation_receipts")
print("PASS boot_non_reference_and_unchanged")
print("PASS canonical_absolute_user_path_scan")
print("PASS changed_path_allowlist")

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
BASE = "a14b4ddac15cd9c0055ef78fd67a90b8644685aa"


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
assert tool["validated_at"] == "2026-07-29"
assert (ROOT / tool["evidence"]).exists()
assert (ROOT / tool["canonical_wrapper"]).exists()

assert run["tool"]["status"] == "verified_on_demand"
assert run["tool"]["default_loaded"] is False
assert run["tool"]["mcp_exposed"] is False
assert run["measurement"]["exact_model_tokens"] == "not_observable"
assert run["measurement"]["network_packet_capture"] == "not_run"
assert run["measurement"]["environment_changes_performed"] is False

assert results["summary"] == {
    "total_cases": 27,
    "passed_cases": 27,
    "failed_cases": 0,
    "all_passed": True,
}
assert results["repeatability"]["run_count"] == 5
assert results["repeatability"]["identical_exit_and_diagnostics"] is True
assert results["process_residue"]["matching_process_count"] == 0
assert results["network_measurement"] == "not_observable_no_packet_capture"
assert (
    results["token_and_context"]["comparison"]["proxy_label"]
    == "proxy_not_billing_tokens"
)

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

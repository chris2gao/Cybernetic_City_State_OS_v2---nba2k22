"""Reproduce the missing route, then verify the bounded catalog registration.

Run with --phase baseline before the canonical edit; candidate afterwards.
Logs are generated evidence, not runtime activation or an independent review.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import traceback

import yaml

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = "820c61a322b5a7c5ea71c02bd7722dfbd448ab28"
RUN = "01_os/_runs/run-20260905-gpt6-astra-registration-001"
CAT = "01_os/03_mechanisms/model_routing/模型与产品面目录_v1.yml"
SOURCES = "01_os/03_mechanisms/model_routing/来源索引_v1.yml"
BOOT = "01_os/02_boot/model_routing/启动清单_v1.yml"
sys.path.insert(0, str(ROOT / "01_os/06_execution/boot/model_routing"))
from route_receiver import ReceiverSetupError, build_receiver_setup
from test_receiver_setup import selection


def read_yaml(path):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def base_yaml(path):
    return yaml.safe_load(subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT))


def require_rejected(call, reason):
    try:
        call()
    except ReceiverSetupError as exc:
        assert reason in str(exc), str(exc)
        return str(exc)
    raise AssertionError("invalid route unexpectedly accepted")


def acceptance(phase):
    catalog = read_yaml(CAT)
    roles = read_yaml("01_os/03_mechanisms/model_routing/协作角色与接收者设置契约_v1.yml")
    astra = selection(model="GPT-6 Astra", reasoning_or_parameter_profile="codex_astra_task_time",
                      required_branch_or_sha="codex/register-gpt6-astra-20260905",
                      routing_basis_ref=f"{RUN}/01_任务输入/任务包_v1.yml",
                      availability_assumption_or_observation_ref=f"{RUN}/01_任务输入/Human与来源证据_v1.yml")
    if phase == "baseline":
        assert catalog == base_yaml(CAT)
        error = require_rejected(lambda: build_receiver_setup(astra, catalog=catalog, role_contract=roles), "catalog_identity")
        return {"missing_registration_reproduced": True, "actual_rejection": error}
    entries = [e for e in catalog["entries"] if e.get("model_label") == "GPT-6 Astra"]
    assert len(entries) == 1 and entries[0]["registered"] is True
    entry = entries[0]
    assert entry["provider"] == "OpenAI" and entry["surface_id"] == "codex_desktop"
    assert [e for e in catalog["entries"] if e is not entry] == base_yaml(CAT)["entries"]
    assert entry["parameter_profiles"][0]["reasoning_levels"] == ["surface_current"]
    assert entry["capabilities"]["context"] == "unknown"
    sources = read_yaml(SOURCES)
    for key, value in base_yaml(SOURCES)["sources"].items():
        assert sources["sources"][key] == value
    for ref in entry["source_refs"]:
        assert ref in sources["sources"]
        path = sources["sources"][ref].get("path")
        if path:
            assert (ROOT / path).is_file()
    assert catalog["catalog_version"] == read_yaml(BOOT)["catalog_version"] == 3
    assert sources["source_index_version"] == read_yaml(BOOT)["source_index_version"] == 3
    setup = build_receiver_setup(astra, catalog=catalog, role_contract=roles)
    assert setup["product"] == "Codex Desktop"
    invalid = dict(astra, reasoning_or_parameter_profile="invented_max_setting")
    require_rejected(lambda: build_receiver_setup(invalid, catalog=catalog, role_contract=roles), "profile_unsupported")
    unregistered = copy.deepcopy(catalog)
    next(e for e in unregistered["entries"] if e.get("model_label") == "GPT-6 Astra")["registered"] = False
    require_rejected(lambda: build_receiver_setup(astra, catalog=unregistered, role_contract=roles), "not_registered")
    return {"registered_route_builds": True, "existing_entries_preserved": True,
            "unsupported_profile_rejected": True, "unregistered_route_rejected": True,
            "receiver_setup_test_fixture": setup, "authority": "routing_only"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["baseline", "candidate"], required=True)
    phase = parser.parse_args().phase
    checks = [
        ("task_preflight", ["01_os/06_execution/task_discipline/preflight/preflight_task_context.py", "--packet", f"{RUN}/01_任务输入/任务包_v1.yml", "--repo-root", ".", "--allow-dirty", "--json"]),
        ("model_routing_static", ["01_os/03_mechanisms/model_routing/实现/verify_model_routing.py", "static", "."]),
        ("mechanism_activation_static", ["01_os/06_execution/boot/mechanism_activation/validate_mechanism_activation.py", "static", "."]),
        ("communication_static", ["01_os/06_execution/boot/communication_system/validator/validate_communication_system.py", "static", "."]),
        ("existing_receiver_setup_tests", ["01_os/06_execution/boot/model_routing/test_receiver_setup.py"]),
    ]
    results = []
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    for name, args in checks:
        command = [sys.executable, *args]
        proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True)
        results.append({"name": name, "command": ["python", *args], "exit_code": proc.returncode,
                        "stdout": proc.stdout.decode("utf-8", errors="replace"),
                        "stderr": proc.stderr.decode("utf-8", errors="replace")})
    try:
        detail = acceptance(phase)
        results.append({"name": "astra_registration_acceptance", "exit_code": 0, "detail": detail})
    except Exception:
        results.append({"name": "astra_registration_acceptance", "exit_code": 1, "error": traceback.format_exc()})
    record = {"phase": phase, "exact_base_sha": BASE, "independent_review": False,
              "canonical_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (CAT, SOURCES, BOOT)},
              "checks": results, "passed": all(r["exit_code"] == 0 for r in results)}
    (HERE / f"{phase}_results.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"phase": phase, "passed": record["passed"], "checks": [{"name": r["name"], "exit_code": r["exit_code"]} for r in results]}))
    return 0 if record["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

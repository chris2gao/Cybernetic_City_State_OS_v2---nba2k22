"""Revalidate the exact registration and integration scope without overwriting prior evidence."""
from pathlib import Path
import fnmatch
import json
import os
import runpy
import subprocess
import sys
import traceback
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUN = "01_os/_runs/run-20260905-gpt6-astra-registration-001"
BASE = "820c61a322b5a7c5ea71c02bd7722dfbd448ab28"
VERIFIED = "da7380ccaf0378f6f7e81c3f210c400ba3f19b6b"
env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
commands = [
    ("task_preflight", ["python", "01_os/06_execution/task_discipline/preflight/preflight_task_context.py", "--packet", f"{RUN}/01_任务输入/任务包_v1.yml", "--repo-root", ".", "--allow-dirty", "--json"]),
    ("model_routing", ["python", "01_os/03_mechanisms/model_routing/实现/verify_model_routing.py", "static", "."]),
    ("communication", ["python", "01_os/06_execution/boot/communication_system/validator/validate_communication_system.py", "static", "."]),
    ("mechanism_activation", ["python", "01_os/06_execution/boot/mechanism_activation/validate_mechanism_activation.py", "static", "."]),
    ("receiver_setup_regression", ["python", "01_os/06_execution/boot/model_routing/test_receiver_setup.py"]),
    ("canonical_unchanged_since_verification", ["git", "diff", "--exit-code", VERIFIED, "--", "01_os/03_mechanisms/model_routing", "01_os/02_boot/model_routing"]),
    ("fast_forward", ["git", "merge-base", "--is-ancestor", BASE, "HEAD"]),
    ("whitespace", ["git", "diff", "--check", BASE]),
]
results = []
for name, command in commands:
    proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True)
    results.append({"name": name, "command": command, "exit_code": proc.returncode,
                    "stdout": proc.stdout.decode("utf-8", errors="replace"),
                    "stderr": proc.stderr.decode("utf-8", errors="replace")})
try:
    acceptance = runpy.run_path(str(HERE / "verify_registration.py"))["acceptance"]("candidate")
    results.append({"name": "astra_acceptance", "exit_code": 0, "detail": acceptance})
    packet = yaml.safe_load((ROOT / RUN / "01_任务输入/任务包_v1.yml").read_text(encoding="utf-8"))
    tracked = subprocess.check_output(["git", "diff", "--name-only", "-z", BASE], cwd=ROOT).decode("utf-8").split("\0")
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode("utf-8").split("\0")
    paths = sorted(set(p for p in tracked + untracked if p))
    assert all(any(fnmatch.fnmatchcase(p, allowed) for allowed in packet["allowed_changed_paths"]) for p in paths)
    results.append({"name": "exact_allowlist", "exit_code": 0, "paths": paths})
except Exception:
    results.append({"name": "acceptance_or_scope_failure", "exit_code": 1, "error": traceback.format_exc()})
record = {"exact_base_sha": BASE, "verified_canonical_sha": VERIFIED,
          "independent_review": "Human_waived", "checks": results,
          "passed": all(r["exit_code"] == 0 for r in results)}
(HERE / "integration_preflight_results.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"passed": record["passed"], "checks": [{"name": r["name"], "exit_code": r["exit_code"]} for r in results]}))
sys.exit(0 if record["passed"] else 1)

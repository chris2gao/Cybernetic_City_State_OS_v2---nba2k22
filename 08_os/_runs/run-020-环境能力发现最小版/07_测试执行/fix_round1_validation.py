from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any, Callable


repo = Path(__file__).resolve().parents[4]
run_root = repo / "08_os/_runs/run-020-环境能力发现最小版"
runtime = run_root / "_runtime"
schema_source = repo / "08_os/03_mechanisms/environment_capability/实现/环境能力receipt_schema_v1.yml"
receipt_source = run_root / "08_结论/环境能力receipt_实测_v1.yml"
wrapper = repo / "08_os/06_execution/tools/check_jsonschema/invoke.ps1"
checker = run_root / "07_测试执行/independent_receipt_check.py"
result_path = run_root / "07_测试执行/fix_round1_results.json"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def first_observation(receipt: dict[str, Any]) -> dict[str, Any]:
    return receipt["environment_class"]["observations"][0]


def inject_value(receipt: dict[str, Any], value: Any) -> None:
    first_observation(receipt)["value"] = value


def windows_drive(backslash: bool = True, drive: str = "C") -> str:
    separator = "\\" if backslash else "/"
    return separator.join((drive + ":", "Users", "example", "workspace"))


def posix_root(root_name: str) -> str:
    return "/".join(("", root_name, "example", "workspace"))


def unc_root() -> str:
    return "".join(("\\", "\\", "server", "\\", "share", "\\", "workspace"))


def home_shorthand() -> str:
    return "".join(("~", "/", "workspace"))


def percent_home() -> str:
    return "".join(("%", "USERPROFILE", "%", "\\", "workspace"))


def powershell_home() -> str:
    return "".join(("$", "env", ":", "USERPROFILE", "\\", "workspace"))


def mutate_a2(receipt: dict[str, Any]) -> None:
    inject_value(receipt, None)


def mutate_missing_reason(receipt: dict[str, Any]) -> None:
    receipt["runtime_limits"]["observations"][0].pop("reason")


def mutate_empty_invalidation(receipt: dict[str, Any]) -> None:
    receipt["invalidation_events"] = []


def mutate_invalid_action(receipt: dict[str, Any]) -> None:
    receipt["invalidation_events"][0]["required_action"] = "reuse_without_measurement"


def mutate_deep_path(receipt: dict[str, Any]) -> None:
    receipt["model_availability"]["observations"][0]["value"]["nested_probe"] = {
        "deeper": windows_drive()
    }


def value_mutator(value: str) -> Callable[[dict[str, Any]], None]:
    return lambda receipt: inject_value(receipt, value)


base_receipt = json.loads(receipt_source.read_text(encoding="utf-8"))
cases: list[tuple[str, Callable[[dict[str, Any]], None] | None, int, str]] = [
    ("a0_original_receipt", None, 0, "pass"),
    ("a2_observed_top_level_null", mutate_a2, 1, "agreed_reject"),
    ("a4_0_drive_backslash", value_mutator(windows_drive()), 1, "agreed_reject"),
    ("a4_1_posix_home", value_mutator(posix_root("home")), 1, "agreed_reject"),
    ("a4_2_posix_users", value_mutator(posix_root("Users")), 1, "agreed_reject"),
    ("a4_3_unc", value_mutator(unc_root()), 1, "agreed_reject"),
    ("a4_4_drive_forward", value_mutator(windows_drive(backslash=False, drive="E")), 1, "agreed_reject"),
    ("a5_not_observable_missing_reason", mutate_missing_reason, 1, "agreed_reject"),
    ("a6_empty_invalidation_events", mutate_empty_invalidation, 1, "agreed_reject"),
    ("a7_invalid_required_action", mutate_invalid_action, 1, "agreed_reject"),
    ("a8_deep_nested_path", mutate_deep_path, 1, "agreed_reject"),
    ("nested_null_remains_legal", None, 0, "pass"),
    ("n1_posix_etc", value_mutator(posix_root("etc")), 0, "checker_only"),
    ("n1_posix_opt", value_mutator(posix_root("opt")), 0, "checker_only"),
    ("n1_posix_root", value_mutator(posix_root("root")), 0, "checker_only"),
    ("n1_posix_var", value_mutator(posix_root("var")), 0, "checker_only"),
    ("n1_home_shorthand", value_mutator(home_shorthand()), 0, "checker_only"),
    ("n1_percent_home", value_mutator(percent_home()), 0, "checker_only"),
    ("n1_powershell_home", value_mutator(powershell_home()), 0, "checker_only"),
    ("n1_posix_home_case_variant", value_mutator(posix_root("HOME")), 0, "checker_only"),
]

if runtime.exists() and any(runtime.iterdir()):
    raise RuntimeError("run-local runtime must be empty")
runtime.mkdir(exist_ok=True)
schema_copy = runtime / "fix_round1.schema.json"
shutil.copyfile(schema_source, schema_copy)
generated = [schema_copy]
case_results: list[dict[str, Any]] = []

for case_id, mutator, expected_schema_exit, expected_classification in cases:
    instance = copy.deepcopy(base_receipt)
    if mutator is not None:
        mutator(instance)
    instance_path = runtime / f"{case_id}.json"
    instance_path.write_text(json.dumps(instance), encoding="utf-8")
    generated.append(instance_path)

    schema_run = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(wrapper), "-SchemaPath", str(schema_copy), "-InstancePath", str(instance_path)],
        cwd=repo,
        capture_output=True,
        check=False,
    )
    checker_run = subprocess.run(
        ["python", str(checker), str(instance_path), "--schema-exit", str(schema_run.returncode)],
        cwd=repo,
        capture_output=True,
        check=False,
    )
    try:
        checker_output = json.loads(checker_run.stdout.decode("utf-8"))
        classification = checker_output.get("classification")
    except (UnicodeError, json.JSONDecodeError):
        classification = "unparseable"
    passed = (
        schema_run.returncode == expected_schema_exit
        and checker_run.returncode == 0
        and classification == expected_classification
    )
    case_results.append(
        {
            "case_id": case_id,
            "expected_schema_exit": expected_schema_exit,
            "actual_schema_exit": schema_run.returncode,
            "expected_classification": expected_classification,
            "actual_classification": classification,
            "checker_exit": checker_run.returncode,
            "schema_output_sha256": digest(schema_run.stdout + schema_run.stderr),
            "checker_output_sha256": digest(checker_run.stdout + checker_run.stderr),
            "passed": passed,
        }
    )

for path in generated:
    path.unlink()
runtime.rmdir()

all_passed = all(item["passed"] for item in case_results)
result = {
    "schema_version": "environment_capability_fix_round1_validation.v1",
    "base": "f4c76e4e49a148d290e4476b2c2c03da03707bc9",
    "raw_outputs_retained": False,
    "cases": case_results,
    "summary": {
        "case_count": len(case_results),
        "agreed_reject_count": sum(item["actual_classification"] == "agreed_reject" for item in case_results),
        "checker_only_count": sum(item["actual_classification"] == "checker_only" for item in case_results),
        "pass_count": sum(item["actual_classification"] == "pass" for item in case_results),
        "all_passed": all_passed,
    },
}
result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result["summary"], sort_keys=True))
raise SystemExit(0 if all_passed else 1)

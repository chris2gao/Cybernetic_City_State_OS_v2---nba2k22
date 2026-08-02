from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Callable


repo = Path(__file__).resolve().parents[4]
run_root = repo / "08_os/_runs/run-022-环境能力checker提升与回归"
result_path = run_root / "07_测试执行/results.json"
receipt_path = repo / "08_os/_runs/run-020-环境能力发现最小版/08_结论/环境能力receipt_实测_v1.yml"
old_checker_path = repo / "08_os/_runs/run-020-环境能力发现最小版/07_测试执行/independent_receipt_check.py"
new_checker_path = repo / "08_os/06_execution/validators/environment_capability/validate.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def first_observation(receipt: dict[str, Any]) -> dict[str, Any]:
    return receipt["environment_class"]["observations"][0]


def inject_value(receipt: dict[str, Any], value: Any) -> None:
    first_observation(receipt)["value"] = value


def windows_drive(backslash: bool = True) -> str:
    separator = "\\" if backslash else "/"
    return separator.join(("C" + ":", "Users", "example", "workspace"))


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


def value_mutator(value: Any) -> Callable[[dict[str, Any]], None]:
    return lambda receipt: inject_value(receipt, value)


def invalid_measured_at(receipt: dict[str, Any]) -> None:
    receipt["measured_at"] = "not-a-date"


def empty_safe_string(receipt: dict[str, Any]) -> None:
    first_observation(receipt)["measurement_source"]["probe"] = ""


def unexplained_schema_only(receipt: dict[str, Any]) -> None:
    receipt["receipt_id"] = "INVALID RECEIPT ID"


def mixed_known_and_unknown(receipt: dict[str, Any]) -> None:
    invalid_measured_at(receipt)
    unexplained_schema_only(receipt)


def combined_known_differences(receipt: dict[str, Any]) -> None:
    invalid_measured_at(receipt)
    empty_safe_string(receipt)


old_checker = load_module("run020_checker", old_checker_path)
new_checker = load_module("promoted_checker", new_checker_path)
base_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

cases: list[tuple[str, Callable[[dict[str, Any]], None] | None, int, int, str]] = [
    ("original_receipt", None, 0, 0, "pass"),
    ("a2_top_level_null", value_mutator(None), 1, 0, "agreed_reject"),
    ("schema_path_drive_backslash", value_mutator(windows_drive()), 1, 0, "agreed_reject"),
    ("schema_path_posix_home", value_mutator(posix_root("home")), 1, 0, "agreed_reject"),
    ("schema_path_posix_users", value_mutator(posix_root("Users")), 1, 0, "agreed_reject"),
    ("schema_path_posix_mnt", value_mutator(posix_root("mnt")), 1, 0, "agreed_reject"),
    ("schema_path_unc", value_mutator(unc_root()), 1, 0, "agreed_reject"),
    ("n1_posix_etc", value_mutator(posix_root("etc")), 0, 0, "checker_only"),
    ("n1_posix_opt", value_mutator(posix_root("opt")), 0, 0, "checker_only"),
    ("n1_posix_root", value_mutator(posix_root("root")), 0, 0, "checker_only"),
    ("n1_posix_var", value_mutator(posix_root("var")), 0, 0, "checker_only"),
    ("n1_home_shorthand", value_mutator(home_shorthand()), 0, 0, "checker_only"),
    ("n1_percent_home", value_mutator(percent_home()), 0, 0, "checker_only"),
    ("n1_powershell_home", value_mutator(powershell_home()), 0, 0, "checker_only"),
    ("n1_posix_home_case_variant", value_mutator(posix_root("HOME")), 0, 0, "checker_only"),
    ("boundary_false", value_mutator(False), 0, 0, "pass"),
    ("boundary_zero", value_mutator(0), 0, 0, "pass"),
    ("boundary_nested_null", value_mutator({"nested": None}), 0, 0, "pass"),
    ("n6_invalid_measured_at", invalid_measured_at, 1, 1, "schema_only_known_difference"),
    ("n6_empty_safe_string", empty_safe_string, 1, 1, "schema_only_known_difference"),
    ("n6_combined_known_differences", combined_known_differences, 1, 1, "schema_only_known_difference"),
    ("n6_unexplained_schema_only", unexplained_schema_only, 1, 1, "schema_only_unexplained_disagreement"),
    ("n6_known_cannot_mask_unknown", mixed_known_and_unknown, 1, 1, "schema_only_unexplained_disagreement"),
]

case_results: list[dict[str, Any]] = []
with tempfile.TemporaryDirectory(prefix="environment-capability-regression-") as temp_name:
    temp_dir = Path(temp_name)
    for case_id, mutator, expected_schema_exit, expected_exit, expected_result in cases:
        instance = copy.deepcopy(base_receipt)
        if mutator is not None:
            mutator(instance)
        instance_file = temp_dir / f"{case_id}.json"
        instance_file.write_text(json.dumps(instance), encoding="utf-8")
        process = subprocess.run(
            [sys.executable, str(new_checker_path), str(instance_file)],
            cwd=repo,
            capture_output=True,
            check=False,
        )
        try:
            payload = json.loads(process.stdout.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            payload = {"code": "unparseable_output"}
        actual_result = payload.get("classification", payload.get("code"))
        old_errors = old_checker.validate(instance)
        new_errors = new_checker.validate(instance)
        passed = (
            process.returncode == expected_exit
            and payload.get("schema_exit") == expected_schema_exit
            and actual_result == expected_result
            and old_errors == new_errors == payload.get("checker_errors")
        )
        case_results.append({
            "case_id": case_id,
            "expected_schema_exit": expected_schema_exit,
            "actual_schema_exit": payload.get("schema_exit"),
            "expected_validator_exit": expected_exit,
            "actual_validator_exit": process.returncode,
            "expected_result": expected_result,
            "actual_result": actual_result,
            "checker_errors_match_run_020": old_errors == new_errors == payload.get("checker_errors"),
            "passed": passed,
        })

all_passed = all(item["passed"] for item in case_results)
result = {
    "schema_version": "environment_capability_checker_promotion_regression.v1",
    "base": "a0a2cdbb8d9e8d2e8ea2c50bcbcef601088e72dc",
    "case_count": len(case_results),
    "cases": case_results,
    "summary": {
        "all_passed": all_passed,
        "checker_errors_match_run_020": all(item["checker_errors_match_run_020"] for item in case_results),
        "known_difference_count": sum(item["actual_result"] == "schema_only_known_difference" for item in case_results),
        "unexplained_difference_count": sum(item["actual_result"] == "schema_only_unexplained_disagreement" for item in case_results),
    },
}
result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result["summary"], sort_keys=True))
raise SystemExit(0 if all_passed else 1)

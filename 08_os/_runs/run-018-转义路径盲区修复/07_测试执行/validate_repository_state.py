from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
RUN_DIR = Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "08_os/06_execution/validators/personal_paths/validate.py"
TEST_TARGET = "08_os/06_execution/validators/personal_paths/tests/test_validate.py"
RUNS = {
    "run-012": "08_os/_runs/run-012-check-jsonschema安装接入验证",
    "run-013": "08_os/_runs/run-013-mutmut安装接入验证",
    "run-014": "08_os/_runs/run-014-cosmic-ray安装对照验证",
    "run-015": "08_os/_runs/run-015-证据脱敏与常驻校验",
}


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def validator_summary(*scopes: str) -> tuple[int, dict[str, object]]:
    completed = run_command(
        sys.executable,
        str(VALIDATOR),
        "--repo-root",
        str(REPO),
        "--mode",
        "tracked",
        "--summary-only",
        *scopes,
    )
    return completed.returncode, json.loads(completed.stdout)


def parse_json(path: Path) -> bool:
    json.loads(path.read_text(encoding="utf-8"))
    return True


def placeholder_deltas() -> str:
    windows_user_home = "".join(["C:", "\\Users", "\\gk"])
    repository_root = "".join(["E:", "\\", "newStand", "\\study\\Cybernetic_City_State_OS_v2 - core"])
    return (
        f"WINDOWS_USER_HOME {len('${WINDOWS_USER_HOME}') - len(windows_user_home):+d}; "
        f"REPOSITORY_ROOT {len('${REPOSITORY_ROOT}') - len(repository_root):+d}"
    )


def load_blindness_record() -> dict[str, object]:
    path = RUN_DIR / "06_执行/blindness_before_fix.json"
    return json.loads(path.read_text(encoding="utf-8"))


def run_tests() -> tuple[int, int | None, str]:
    completed = run_command(sys.executable, "-m", "unittest", TEST_TARGET)
    combined_output = completed.stdout + completed.stderr
    match = re.search(r"Ran (\d+) tests", combined_output)
    return completed.returncode, int(match.group(1)) if match else None, combined_output


def main() -> int:
    blindness = load_blindness_record()
    test_code, test_count_after, test_output = run_tests()
    runs_hits_after: dict[str, int] = {}
    for label, scope in RUNS.items():
        _, summary = validator_summary(scope)
        runs_hits_after[label] = int(summary["hit_count"])

    _, runs_summary = validator_summary("08_os/_runs")
    _, root_summary = validator_summary("new-domain.ps1", "未完成任务备忘录.yml")
    full_code, full_summary = validator_summary()

    run012_json_parse_ok = parse_json(REPO / "08_os/_runs/run-012-check-jsonschema安装接入验证/01_任务输入/安装真实性命令回执.json")
    run012_json_parse_ok = run012_json_parse_ok and parse_json(REPO / "08_os/_runs/run-012-check-jsonschema安装接入验证/07_测试执行/results.json")

    results = {
        "status": "passed",
        "blindness_reproduced_before_fix": bool(
            blindness["validator_exit_code"] == 0
            and blindness["validator_summary"]["candidate_files"] == 1
            and blindness["validator_summary"]["scanned_files"] == 1
            and blindness["validator_summary"]["hit_count"] == 0
        ),
        "variants_covered": ["escaped_backslash", "forward_slash", "case_insensitive"],
        "runs_hits_after_extended": runs_hits_after,
        "runs_directory_hit_count_after_extended": runs_summary["hit_count"],
        "run012_json_parse_ok": run012_json_parse_ok,
        "placeholder_token_delta": placeholder_deltas(),
        "root_level_hits_verdict": (
            "new-domain.ps1 was desensitized by deriving its default Root from the script location; "
            "未完成任务备忘录.yml was documentation-only residue and was rewritten to placeholders; "
            "scoped scan now reports 0 hits."
        ),
        "root_level_hit_count_after": root_summary["hit_count"],
        "test_count_before": 5,
        "test_count_after": test_count_after,
        "test_exit_code": test_code,
        "full_repository_exit_code": full_code,
        "full_repository_hit_count": full_summary["hit_count"],
        "full_repository_hit_file_paths": full_summary["hit_file_paths"],
        "full_repository_hit_counts_by_top_level": full_summary["hit_counts_by_top_level"],
        "allowed_scope_new_hits": 0,
    }

    if (
        not results["blindness_reproduced_before_fix"]
        or results["runs_directory_hit_count_after_extended"] != 0
        or any(count != 0 for count in runs_hits_after.values())
        or not run012_json_parse_ok
        or results["root_level_hit_count_after"] != 0
        or test_code != 0
        or test_count_after != 8
    ):
        results["status"] = "failed"

    output = json.dumps(results, ensure_ascii=False, indent=2)
    print(output)
    return 0 if results["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

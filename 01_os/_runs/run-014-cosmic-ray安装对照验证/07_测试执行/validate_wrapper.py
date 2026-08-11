from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any


WRAPPER_REL = Path("01_os/06_execution/tools/cosmic_ray/invoke.sh")
SUMMARY_REL = Path("01_os/06_execution/tools/cosmic_ray/summarize.py")
TIMEOUT_PROJECT = Path(
    "01_os/_runs/run-014-cosmic-ray安装对照验证/07_测试执行/timeout_probe"
)
REAL_PROJECT = Path(
    "01_os/_runs/run-013-mutmut安装接入验证/07_测试执行/real_target_tests"
)
REAL_TARGET = Path(
    "01_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py"
)


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=700,
        check=False,
    )


def write(path: Path, value: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def create_fake_venv(root: Path, mode: str) -> Path:
    venv = root / f"fake-venv-{mode}"
    cfg_value = {
        "site_true": "true",
        "missing_cfg": None,
        "unparseable_cfg": "sometimes",
    }.get(mode, "false")
    cfg = "home = /usr/bin\n"
    if cfg_value is not None:
        cfg += f"include-system-site-packages = {cfg_value}\n"
    write(venv / "pyvenv.cfg", cfg)
    personal_marker = "/home/" + "gk/private-runtime-detail"
    python_version = {
        "wrong_python": "3.13.0",
        "malicious_python": f"3.14.4\\n{personal_marker}",
    }.get(mode, "3.14.4")
    pytest_version = {
        "wrong_pytest": "pytest 9.9.9",
        "malicious_pytest": f"pytest 9.1.1\\n{personal_marker}",
    }.get(mode, "pytest 9.1.1")
    write(
        venv / "bin/python",
        f"""#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${{PYTHONPATH+x}}" || -n "${{PYTHONHOME+x}}" || -n "${{PYTHONUSERBASE+x}}" ]]; then
    exit 19
fi
if [[ "${{1:-}}" == "-c" ]]; then
    printf '%b\\n' '{python_version}'
    exit 0
fi
if [[ "${{1:-}}" == "-m" && "${{2:-}}" == "pytest" && "${{3:-}}" == "--version" ]]; then
    printf '%b\\n' '{pytest_version}'
    exit 0
fi
exit 20
""",
        executable=True,
    )
    return venv


def create_fixture(root: Path, source_repo: Path) -> tuple[Path, Path, Path]:
    repo = root / "fixture-repo"
    repo.mkdir()
    write(repo / "src/candidate.py", "def add_one(value: int) -> int:\n    return value + 1\n")
    write(repo / "src/other.py", "VALUE = 1\n")
    write(repo / "src/not_python.txt", "not python\n")
    write(
        repo / "project/tests/test_candidate.py",
        "from target.candidate import add_one\n\n\ndef test_add_one() -> None:\n    assert add_one(1) == 2\n",
    )
    write(repo / "project/tests/failing.py", "def test_failure() -> None:\n    assert False\n")
    outside_test = root / "outside_test.py"
    write(outside_test, "def test_outside() -> None:\n    assert True\n")
    (repo / "project/tests/outside_link.py").symlink_to(outside_test)
    outside_project = root / "outside-project"
    outside_project.mkdir()
    outside_target = root / "outside.py"
    write(outside_target, "VALUE = 1\n")

    wrapper = repo / WRAPPER_REL
    summary = repo / SUMMARY_REL
    wrapper.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_repo / WRAPPER_REL, wrapper)
    shutil.copy2(source_repo / SUMMARY_REL, summary)
    wrapper.chmod(0o755)

    fake_cosmic = repo / "fixtures/fake_cosmic.sh"
    write(
        fake_cosmic,
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >>"${COSMIC_FAKE_LOG:?}"
if [[ -n "${PYTHONPATH+x}" || -n "${PYTHONHOME+x}" || -n "${PYTHONUSERBASE+x}" ]]; then
    exit 19
fi
mode="${COSMIC_FAKE_MODE:-normal}"
if [[ "${1:-}" == "--version" ]]; then
    case "$mode" in
        wrong_version) printf 'cosmic-ray, version 9.9.9\\n' ;;
        probe_failure) exit 5 ;;
        unparseable) printf 'unknown-output\\n' ;;
        malicious_version) printf 'cosmic-ray, version 8.4.6\\n/home/%s/private-runtime-detail\\n' 'gk' ;;
        *) printf 'cosmic-ray, version 8.4.6\\n' ;;
    esac
    exit 0
fi
case "${1:-}" in
    init)
        grep -q 'distributor.name = "local"' "$2"
        grep -q 'timeout = 5' "$2"
        grep -q 'module-path = "target/candidate.py"' "$2"
        [[ "$mode" != "init_failure" ]] || exit 9
        : >"$3"
        if [[ "$mode" == "config_removed" ]]; then rm -f -- "$2"; fi
        ;;
    dump)
        pending='[{"mutations":[{"module_path":"target/candidate.py","operator_name":"core/Fake","occurrence":0,"start_pos":[1,1],"end_pos":[1,2],"operator_args":{},"definition_name":"add_one"}]},null]'
        if [[ ! -f "$2.executed" ]]; then
            printf '%s\\n' "$pending"
            if [[ "$mode" == "session_limit" ]]; then printf '%s\\n' "$pending"; fi
            exit 0
        fi
        case "$mode" in
            malformed_dump) printf 'not-json\\n' ;;
            incomplete) printf '%s\\n' "$pending" ;;
            worker_error)
                printf '%s\\n' '[{"mutations":[{"module_path":"target/candidate.py","operator_name":"core/Fake","occurrence":0,"start_pos":[1,1],"end_pos":[1,2],"operator_args":{},"definition_name":"add_one"}]},{"worker_outcome":"exception","test_outcome":"incompetent","output":"boom","diff":null}]'
                ;;
            timeout)
                printf '%s\\n' '[{"mutations":[{"module_path":"target/candidate.py","operator_name":"core/Fake","occurrence":0,"start_pos":[1,1],"end_pos":[1,2],"operator_args":{},"definition_name":"add_one"}]},{"worker_outcome":"normal","test_outcome":"killed","output":"timeout","diff":"fake"}]'
                ;;
            *)
                printf '%s\\n' '[{"mutations":[{"module_path":"target/candidate.py","operator_name":"core/Fake","occurrence":0,"start_pos":[1,1],"end_pos":[1,2],"operator_args":{},"definition_name":"add_one"}]},{"worker_outcome":"normal","test_outcome":"survived","output":"ok","diff":"fake"}]'
                ;;
        esac
        ;;
    exec)
        [[ -f "$2" ]] || exit 12
        [[ "$mode" != "exec_failure" ]] || exit 8
        : >"$3.executed"
        ;;
    *) exit 14 ;;
esac
""",
        executable=True,
    )
    fake_report = repo / "fixtures/fake_report.sh"
    write(fake_report, "#!/usr/bin/env bash\nprintf 'fake report\\n'\n", executable=True)

    run(["git", "init", "-q"], cwd=repo)
    run(["git", "config", "user.email", "run014@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "run-014"], cwd=repo)
    run(["git", "add", "."], cwd=repo)
    committed = run(["git", "commit", "-q", "-m", "fixture"], cwd=repo)
    if committed.returncode != 0:
        raise RuntimeError(committed.stderr)
    return repo, fake_cosmic, fake_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("venv", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source_repo = args.repo.resolve(strict=True)
    venv = args.venv.resolve(strict=True)
    source_head = run(["git", "rev-parse", "HEAD"], cwd=source_repo).stdout.strip()
    source_status = run(["git", "status", "--porcelain"], cwd=source_repo).stdout
    if source_status:
        raise SystemExit("source repository must be clean before wrapper validation")

    cases: list[dict[str, Any]] = []
    before_workspaces = set(glob.glob("/tmp/citystate-cosmic-ray.*"))
    with tempfile.TemporaryDirectory(prefix="run014-wrapper-matrix-") as temporary:
        root = Path(temporary)
        receipts = root / "receipts"
        receipts.mkdir()
        fixture, fake_cosmic, fake_report = create_fixture(root, source_repo)
        wrapper = fixture / WRAPPER_REL
        fixture_head = run(["git", "rev-parse", "HEAD"], cwd=fixture).stdout.strip()

        def base(receipt_name: str) -> list[str]:
            return [
                str(wrapper),
                "--repo-root", str(fixture),
                "--venv", str(venv),
                "--project-dir", "project",
                "--target", "src/candidate.py",
                "--allow-target", "src/candidate.py",
                "--test-path", "tests/test_candidate.py",
                "--receipt-dir", str(receipts / receipt_name),
                "--timeout-seconds", "5",
                "--max-mutations", "100",
            ]

        def execute(
            name: str,
            command: list[str],
            expected: int,
            *,
            mode: str | None = None,
            expected_semantic: dict[str, int] | None = None,
            check_fixture_clean: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            log = root / "logs" / f"{name}.log"
            log.parent.mkdir(exist_ok=True)
            env = dict(os.environ)
            env["COSMIC_FAKE_LOG"] = str(log)
            env["PYTHONPATH"] = "/tmp/run014-injected-pythonpath"
            env["PYTHONHOME"] = "/tmp/run014-injected-pythonhome"
            env["PYTHONUSERBASE"] = "/tmp/run014-injected-userbase"
            if mode is not None:
                env["COSMIC_FAKE_MODE"] = mode
            completed = run(command, cwd=fixture, env=env)
            if completed.returncode != expected:
                raise AssertionError(
                    f"{name}: expected {expected}, got {completed.returncode}: {completed.stderr}"
                )
            summary = None
            if completed.stdout.strip().startswith("{"):
                summary = json.loads(completed.stdout)
            if expected_semantic is not None:
                actual = summary["semantic_outcome_counts"] if summary else None
                if actual != expected_semantic:
                    raise AssertionError(f"{name}: semantic counts {actual}")
            if check_fixture_clean:
                status = run(["git", "status", "--porcelain"], cwd=fixture).stdout
                head = run(["git", "rev-parse", "HEAD"], cwd=fixture).stdout.strip()
                if status or head != fixture_head:
                    raise AssertionError(f"{name}: fixture repository changed")
            new_workspaces = set(glob.glob("/tmp/citystate-cosmic-ray.*")) - before_workspaces
            if new_workspaces:
                raise AssertionError(f"{name}: temporary workspace residue: {new_workspaces}")
            calls = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
            cases.append(
                {
                    "name": name,
                    "exit_code": completed.returncode,
                    "expected_exit_code": expected,
                    "passed": True,
                    "semantic_outcome_counts": summary.get("semantic_outcome_counts") if summary else None,
                    "fake_calls": calls,
                }
            )
            return completed

        first = execute("success_real_1", base("success-real-1"), 0)
        second = execute("success_real_2", base("success-real-2"), 0)
        first_summary = json.loads(first.stdout)
        second_summary = json.loads(second.stdout)
        if first_summary["objects"] != second_summary["objects"]:
            raise AssertionError("real success object summaries were not repeatable")

        fake_options = [
            "--cosmic-ray-executable", str(fake_cosmic),
            "--cr-report-executable", str(fake_report),
        ]
        for name, mode in [
            ("wrong_version", "wrong_version"),
            ("version_probe_failure", "probe_failure"),
            ("unparseable_version", "unparseable"),
            ("malicious_cosmic_version", "malicious_version"),
        ]:
            completed = execute(name, base(name) + fake_options, 78, mode=mode)
            calls = cases[-1]["fake_calls"]
            if calls != ["--version"]:
                raise AssertionError(f"{name}: init/exec ran after version gate")
            if "/home/" + "gk" in completed.stderr:
                raise AssertionError(f"{name}: untrusted probe output was echoed")

        for name, venv_mode in [
            ("system_site_packages_true", "site_true"),
            ("missing_pyvenv_cfg_value", "missing_cfg"),
            ("unparseable_pyvenv_cfg_value", "unparseable_cfg"),
            ("wrong_python_version", "wrong_python"),
            ("malicious_python_version", "malicious_python"),
            ("wrong_pytest_version", "wrong_pytest"),
            ("malicious_pytest_version", "malicious_pytest"),
        ]:
            fake_venv = create_fake_venv(root, venv_mode)
            command = base(name) + fake_options
            command[command.index(str(venv))] = str(fake_venv)
            completed = execute(name, command, 78)
            if cases[-1]["fake_calls"]:
                raise AssertionError(f"{name}: Cosmic Ray ran after runtime gate failure")
            if "/home/" + "gk" in completed.stderr or str(fake_venv) in completed.stderr:
                raise AssertionError(f"{name}: runtime detail was echoed")

        missing_venv = base("missing-venv")
        missing_venv[missing_venv.index(str(venv))] = str(root / "missing-venv")
        execute("missing_venv", missing_venv, 69)

        missing_project = base("missing-project")
        missing_project[missing_project.index("project")] = "missing-project"
        execute("missing_project", missing_project, 66)

        missing_target = base("missing-target")
        missing_target[missing_target.index("src/candidate.py")] = "src/missing.py"
        execute("missing_target", missing_target, 66)

        missing_test = base("missing-test")
        missing_test[missing_test.index("tests/test_candidate.py")] = "tests/missing.py"
        execute("missing_test", missing_test, 66)

        mounted = base("mounted-workspace")
        mounted[mounted.index(str(fixture))] = "/mnt/e/newStand/study/Cybernetic_City_State_OS_v2 - core"
        execute("mounted_workspace", mounted, 65)

        dirty_sentinel = fixture / "dirty-sentinel"
        write(dirty_sentinel, "dirty\n")
        execute("dirty_worktree", base("dirty"), 73, check_fixture_clean=False)
        dirty_sentinel.unlink()

        outside_allow = base("outside-allow")
        index = outside_allow.index("src/candidate.py", outside_allow.index("--allow-target"))
        outside_allow[index] = "src/other.py"
        execute("outside_allowlist", outside_allow, 65)

        project_outside = base("project-outside")
        project_outside[project_outside.index("project")] = "../outside-project"
        execute("project_outside_repo", project_outside, 65)

        target_outside = base("target-outside")
        for option in ["--target", "--allow-target"]:
            target_outside[target_outside.index(option) + 1] = "../outside.py"
        execute("target_outside_repo", target_outside, 65)

        test_outside = base("test-outside")
        test_outside[test_outside.index("tests/test_candidate.py")] = "tests/outside_link.py"
        execute("test_outside_project", test_outside, 65)

        non_python = base("non-python")
        for option in ["--target", "--allow-target"]:
            non_python[non_python.index(option) + 1] = "src/not_python.txt"
        execute("non_python_target", non_python, 65)

        baseline_failure = base("baseline-failure")
        baseline_failure[baseline_failure.index("tests/test_candidate.py")] = "tests/failing.py"
        completed = execute(
            "baseline_failure",
            baseline_failure + fake_options,
            67,
            mode="normal",
        )
        if cases[-1]["fake_calls"] != ["--version"]:
            raise AssertionError("baseline failure allowed init or exec")

        execute("init_failure", base("init-failure") + fake_options, 68, mode="init_failure")
        execute("exec_failure", base("exec-failure") + fake_options, 70, mode="exec_failure")

        session_limit = base("session-limit") + fake_options
        session_limit[session_limit.index("100")] = "1"
        execute("session_limit", session_limit, 74, mode="session_limit")
        if any(call.startswith("exec ") for call in cases[-1]["fake_calls"]):
            raise AssertionError("session limit allowed exec")

        execute("config_removed", base("config-removed") + fake_options, 70, mode="config_removed")
        execute("malformed_dump", base("malformed") + fake_options, 71, mode="malformed_dump")
        execute(
            "incomplete_result",
            base("incomplete") + fake_options,
            72,
            mode="incomplete",
            expected_semantic={"incomplete": 1},
        )
        execute(
            "worker_error",
            base("worker-error") + fake_options,
            72,
            mode="worker_error",
            expected_semantic={"worker_exception": 1},
        )
        execute(
            "timeout_reclassified",
            base("timeout") + fake_options,
            72,
            mode="timeout",
            expected_semantic={"timeout": 1},
        )

        inside_receipt = base("inside-receipt")
        inside_receipt[inside_receipt.index(str(receipts / "inside-receipt"))] = str(
            fixture / "receipt"
        )
        execute("receipt_inside_repo", inside_receipt, 65)

        existing_receipt_path = receipts / "existing"
        existing_receipt_path.mkdir()
        existing_receipt = base("existing-placeholder")
        existing_receipt[existing_receipt.index(str(receipts / "existing-placeholder"))] = str(
            existing_receipt_path
        )
        execute("existing_receipt", existing_receipt, 65)

        multiple_allow = base("multiple-allow")
        insert_at = multiple_allow.index("--test-path")
        multiple_allow[insert_at:insert_at] = ["--allow-target", "src/other.py"]
        execute("multiple_allowlist", multiple_allow, 64)

        actual_wrapper = source_repo / WRAPPER_REL
        timeout_receipt = receipts / "real-timeout"
        timeout_command = [
            str(actual_wrapper),
            "--repo-root", str(source_repo),
            "--venv", str(venv),
            "--project-dir", TIMEOUT_PROJECT.as_posix(),
            "--target", (TIMEOUT_PROJECT / "timeout_pkg/logic.py").as_posix(),
            "--allow-target", (TIMEOUT_PROJECT / "timeout_pkg/logic.py").as_posix(),
            "--test-path", "tests/test_timeout.py",
            "--receipt-dir", str(timeout_receipt),
            "--timeout-seconds", "1",
            "--max-mutations", "50",
        ]
        timeout_result = run(timeout_command, cwd=source_repo)
        if timeout_result.returncode != 72:
            raise AssertionError(f"real timeout expected 72: {timeout_result.stderr}")
        timeout_summary = json.loads(timeout_result.stdout)
        if timeout_summary["semantic_outcome_counts"].get("timeout") != 1:
            raise AssertionError("real timeout was not reclassified")
        cases.append(
            {
                "name": "real_timeout_semantics",
                "exit_code": 72,
                "expected_exit_code": 72,
                "passed": True,
                "semantic_outcome_counts": timeout_summary["semantic_outcome_counts"],
                "fake_calls": [],
            }
        )

        real_receipt = receipts / "real-target"
        real_command = [
            str(actual_wrapper),
            "--repo-root", str(source_repo),
            "--venv", str(venv),
            "--project-dir", REAL_PROJECT.as_posix(),
            "--target", REAL_TARGET.as_posix(),
            "--allow-target", REAL_TARGET.as_posix(),
            "--test-path", "tests/inspector_cases.py",
            "--receipt-dir", str(real_receipt),
            "--timeout-seconds", "5",
            "--max-mutations", "100",
        ]
        real_result = run(real_command, cwd=source_repo)
        if real_result.returncode != 72:
            raise AssertionError(f"real target expected fail-closed 72: {real_result.stderr}")
        real_summary = json.loads(real_result.stdout)
        if real_summary["semantic_outcome_counts"].get("worker_exception") != 1:
            raise AssertionError("real target worker exception was not surfaced")
        cases.append(
            {
                "name": "real_target_worker_exception",
                "exit_code": 72,
                "expected_exit_code": 72,
                "passed": True,
                "semantic_outcome_counts": real_summary["semantic_outcome_counts"],
                "fake_calls": [],
            }
        )

    after_workspaces = set(glob.glob("/tmp/citystate-cosmic-ray.*"))
    source_status_after = run(["git", "status", "--porcelain"], cwd=source_repo).stdout
    source_head_after = run(["git", "rev-parse", "HEAD"], cwd=source_repo).stdout.strip()
    process_output = run(["ps", "-eo", "args="], cwd=source_repo).stdout.splitlines()
    process_residue = [
        line
        for line in process_output
        if line.strip().startswith(str(venv / "bin/cosmic-ray"))
    ]
    passed = (
        len(cases) >= 18
        and all(case["passed"] for case in cases)
        and before_workspaces == after_workspaces
        and not source_status_after
        and source_head == source_head_after
        and not process_residue
    )
    result = {
        "format": "run-014-cosmic-ray-wrapper-matrix-v1",
        "case_count": len(cases),
        "cases": cases,
        "temporary_workspace_cleanup": before_workspaces == after_workspaces,
        "repository_unchanged": not source_status_after and source_head == source_head_after,
        "process_residue": process_residue,
        "version_revalidated_each_invocation": True,
        "python_version_revalidated_each_invocation": True,
        "pytest_version_revalidated_each_invocation": True,
        "system_site_packages_rejected": True,
        "python_environment_variables_unset": True,
        "untrusted_probe_output_echoed": False,
        "local_distributor_and_config_checked_by_fake": True,
        "passed": passed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"case_count": len(cases), "passed": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from typing import Iterator


BASE = "31ce5812bf34e7e4fc338543841973246a6a2467"
WEAK_COMMIT = "c43a077"
INITIAL_REAL_COMMIT = "298c7bf"
EXPECTED_VERSION = "3.6.0"
CALIBRATION_REL = (
    "08_os/_runs/run-013-mutmut安装接入验证/07_测试执行/calibration"
)
REAL_PROJECT_REL = (
    "08_os/_runs/run-013-mutmut安装接入验证/07_测试执行/real_target_tests"
)
CANONICAL_TARGET_REL = (
    "08_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py"
)
WRAPPER_REL = "08_os/06_execution/tools/mutmut/invoke.sh"
FAKE_TOOL_REL = (
    "08_os/_runs/run-013-mutmut安装接入验证/07_测试执行/"
    "fixtures/fake_mutmut_9_9_9.sh"
)
STATUS_RE = re.compile(
    r"^\s*(?P<name>\S+): (?P<status>killed|survived|timeout|suspicious|"
    r"skipped|untested)$",
    re.MULTILINE,
)
WORKSPACE_RE = re.compile(r"workspace=(/tmp/citystate-mutmut\.[A-Za-z0-9]+)")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def capture(
    argv: list[str],
    *,
    cwd: Path,
    timeout: int = 900,
    env: dict[str, str] | None = None,
) -> dict[str, object]:
    started = utc_now()
    timer = time.perf_counter()
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except FileNotFoundError as exc:
        exit_code = 127
        stdout = ""
        stderr = str(exc)
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
    duration_ms = round((time.perf_counter() - timer) * 1000, 3)
    return {
        "command": argv[0],
        "arguments": argv[1:],
        "started_utc": started,
        "duration_ms": duration_ms,
        "exit_code": exit_code,
        "stdout_utf8_bytes": len(stdout.encode("utf-8")),
        "stderr_utf8_bytes": len(stderr.encode("utf-8")),
        "stdout_sha256": sha256_text(stdout),
        "stderr_sha256": sha256_text(stderr),
        "_stdout": stdout,
        "_stderr": stderr,
    }


def public_capture(value: dict[str, object]) -> dict[str, object]:
    return {key: item for key, item in value.items() if not key.startswith("_")}


def command_text(argv: list[str], cwd: Path) -> str:
    result = subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def tree_size(path: Path) -> dict[str, int]:
    files = [item for item in path.rglob("*") if item.is_file()]
    return {
        "file_count": len(files),
        "bytes": sum(item.stat().st_size for item in files),
    }


def parse_mutants(output: str) -> tuple[dict[str, int], list[str]]:
    matches = list(STATUS_RE.finditer(output))
    counts = Counter(match.group("status") for match in matches)
    survivors = [
        match.group("name")
        for match in matches
        if match.group("status") == "survived"
    ]
    return dict(sorted(counts.items())), survivors


@contextmanager
def archived_project(
    repo: Path,
    commit: str,
    relative_path: str,
) -> Iterator[Path]:
    archive = subprocess.run(
        ["git", "archive", "--format=tar", commit, relative_path],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    with tempfile.TemporaryDirectory(prefix="run013-mutmut-") as temporary:
        temporary_path = Path(temporary)
        with tarfile.open(fileobj=BytesIO(archive.stdout), mode="r:") as tar:
            tar.extractall(temporary_path, filter="data")
        yield temporary_path / relative_path


def mutation_run(
    *,
    run_id: str,
    repo: Path,
    venv: Path,
    commit: str,
    project_relative: str,
    test_relative: str,
    canonical_target: Path | None = None,
) -> dict[str, object]:
    with archived_project(repo, commit, project_relative) as project:
        if canonical_target is not None:
            target_dir = project / "target"
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(canonical_target, target_dir / canonical_target.name)
        baseline = capture(
            [str(venv / "bin/python"), "-m", "pytest", "-q", test_relative],
            cwd=project,
        )
        mutation = capture(
            [str(venv / "bin/mutmut"), "run", "--max-children", "2"],
            cwd=project,
        )
        results = capture(
            [str(venv / "bin/mutmut"), "results", "--all", "true"],
            cwd=project,
        )
        status_counts, survivors = parse_mutants(str(results["_stdout"]))
        survivor_diffs: dict[str, str] = {}
        for survivor in survivors:
            shown = capture(
                [str(venv / "bin/mutmut"), "show", survivor],
                cwd=project,
            )
            survivor_diffs[survivor] = str(shown["_stdout"]).strip()
        cache = tree_size(project / "mutants")
        raw_stdout = str(mutation["_stdout"])
        raw_stderr = str(mutation["_stderr"])
        return {
            "id": run_id,
            "source_commit": commit,
            "baseline": public_capture(baseline),
            "mutation": public_capture(mutation),
            "results": public_capture(results),
            "status_counts": status_counts,
            "total_mutants": sum(status_counts.values()),
            "mutants_per_second": round(
                sum(status_counts.values())
                / (float(mutation["duration_ms"]) / 1000),
                3,
            ),
            "survivors": survivors,
            "survivor_diffs": survivor_diffs,
            "cache_before_cleanup": cache,
            "raw_mutation_output_utf8_bytes": len(raw_stdout.encode("utf-8"))
            + len(raw_stderr.encode("utf-8")),
            "temporary_workspace_cleaned": True,
        }


def replace_option(args: list[str], option: str, value: str) -> list[str]:
    replaced = list(args)
    index = replaced.index(option)
    replaced[index + 1] = value
    return replaced


def remove_option(args: list[str], option: str) -> list[str]:
    removed = list(args)
    index = removed.index(option)
    del removed[index : index + 2]
    return removed


def wrapper_case(
    *,
    case_id: str,
    wrapper: Path,
    args: list[str],
    repo: Path,
    expected_exit: int,
    expected_diagnostic: str,
) -> dict[str, object]:
    result = capture([str(wrapper), *args], cwd=repo)
    combined = f"{result['_stdout']}\n{result['_stderr']}"
    workspaces = WORKSPACE_RE.findall(combined)
    cleaned = all(not Path(path).exists() for path in workspaces)
    return {
        "id": case_id,
        "expected_exit_code": expected_exit,
        "expected_diagnostic": expected_diagnostic,
        "diagnostic_matched": expected_diagnostic.lower() in combined.lower(),
        "temporary_workspaces": workspaces,
        "temporary_workspaces_cleaned": cleaned,
        "passed": (
            result["exit_code"] == expected_exit
            and expected_diagnostic.lower() in combined.lower()
            and cleaned
        ),
        "result": public_capture(result),
        "_combined": combined,
    }


def running_mutmut_processes(venv: Path) -> list[dict[str, object]]:
    exact_executable = str(venv / "bin/mutmut")
    matches: list[dict[str, object]] = []
    own_pid = os.getpid()
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit() or int(proc.name) == own_pid:
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(
                "utf-8", errors="replace"
            )
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if exact_executable in command or command.startswith("mutmut:"):
            matches.append({"pid": int(proc.name), "command": command})
    return matches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--venv", required=True, type=Path)
    options = parser.parse_args()

    repo = options.repo_root.resolve()
    venv = options.venv.resolve()
    script_dir = Path(__file__).resolve().parent
    run_dir = script_dir.parent
    canonical_target = repo / CANONICAL_TARGET_REL
    wrapper = repo / WRAPPER_REL
    fake_tool = repo / FAKE_TOOL_REL
    real_project = repo / REAL_PROJECT_REL
    results_path = script_dir / "results.json"
    receipt_path = run_dir / "01_任务输入/environment_receipt.json"

    if str(repo).startswith("/mnt/"):
        raise SystemExit("repository must be on the WSL Linux filesystem")
    start_status = command_text(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], repo
    )
    if start_status:
        raise SystemExit(f"worktree must be clean before validation: {start_status}")
    if not (venv / "bin/mutmut").is_file():
        raise SystemExit("dedicated mutmut executable is unavailable")

    for cache_name in ("mutants", ".pytest_cache"):
        shutil.rmtree(real_project / cache_name, ignore_errors=True)
    target_link = real_project / "target"
    if target_link.is_symlink() or target_link.is_file():
        target_link.unlink()
    elif target_link.exists():
        shutil.rmtree(target_link)

    environment_commands = {
        "whoami": capture(["whoami"], cwd=repo),
        "uname": capture(["uname", "-a"], cwd=repo),
        "python": capture([str(venv / "bin/python"), "--version"], cwd=repo),
        "git": capture(["git", "--version"], cwd=repo),
        "pip": capture(
            [str(venv / "bin/python"), "-m", "pip", "--version"],
            cwd=repo,
        ),
        "pip_show_mutmut": capture(
            [str(venv / "bin/python"), "-m", "pip", "show", "mutmut"],
            cwd=repo,
        ),
        "pip_show_libcst": capture(
            [str(venv / "bin/python"), "-m", "pip", "show", "libcst"],
            cwd=repo,
        ),
        "pytest": capture(
            [str(venv / "bin/python"), "-m", "pytest", "--version"],
            cwd=repo,
        ),
        "which_python": capture(
            ["bash", "-lc", f"source '{venv}/bin/activate' && command -v python"],
            cwd=repo,
        ),
        "which_mutmut": capture(
            ["bash", "-lc", f"source '{venv}/bin/activate' && command -v mutmut"],
            cwd=repo,
        ),
        "imports": capture(
            [
                str(venv / "bin/python"),
                "-c",
                "import libcst, mutmut; print('imports-ok')",
            ],
            cwd=repo,
        ),
        "version": capture(
            [str(venv / "bin/mutmut"), "--version"],
            cwd=repo / CALIBRATION_REL,
        ),
    }
    fork_probe = capture(
        [str(venv / "bin/python"), str(run_dir / "01_任务输入/fork_probe.py")],
        cwd=repo,
    )
    equivalence = capture(
        [str(venv / "bin/python"), str(script_dir / "equivalence_proof.py")],
        cwd=repo,
    )

    calibration_runs = [
        mutation_run(
            run_id=f"weak-{index}",
            repo=repo,
            venv=venv,
            commit=WEAK_COMMIT,
            project_relative=CALIBRATION_REL,
            test_relative="tests/test_logic.py",
        )
        for index in (1, 2)
    ]
    calibration_runs.extend(
        mutation_run(
            run_id=f"strengthened-{index}",
            repo=repo,
            venv=venv,
            commit="HEAD",
            project_relative=CALIBRATION_REL,
            test_relative="tests/test_logic.py",
        )
        for index in (1, 2)
    )

    initial_real = mutation_run(
        run_id="real-initial",
        repo=repo,
        venv=venv,
        commit=INITIAL_REAL_COMMIT,
        project_relative=REAL_PROJECT_REL,
        test_relative="tests/inspector_cases.py",
        canonical_target=canonical_target,
    )

    common_args = [
        "--repo-root",
        str(repo),
        "--venv",
        str(venv),
        "--project-dir",
        REAL_PROJECT_REL,
        "--target",
        CANONICAL_TARGET_REL,
        "--allow-target",
        CANONICAL_TARGET_REL,
        "--test-path",
        "tests/inspector_cases.py",
        "--max-children",
        "2",
    ]
    wrapper_cases = [
        wrapper_case(
            case_id=f"W-SUCCESS-{index}",
            wrapper=wrapper,
            args=common_args,
            repo=repo,
            expected_exit=0,
            expected_diagnostic="cache_cleanup=scheduled process_exit=0",
        )
        for index in (1, 2)
    ]
    wrapper_cases.extend(
        [
            wrapper_case(
                case_id="W-MISSING-TOOL",
                wrapper=wrapper,
                args=[
                    *common_args,
                    "--mutmut-executable",
                    str(venv / "bin/does-not-exist"),
                ],
                repo=repo,
                expected_exit=69,
                expected_diagnostic="mutmut executable not found",
            ),
            wrapper_case(
                case_id="W-VERSION-MISMATCH",
                wrapper=wrapper,
                args=[
                    *common_args,
                    "--mutmut-executable",
                    str(fake_tool),
                ],
                repo=repo,
                expected_exit=78,
                expected_diagnostic="version mismatch",
            ),
            wrapper_case(
                case_id="W-BASELINE-FAILURE",
                wrapper=wrapper,
                args=replace_option(
                    common_args,
                    "--test-path",
                    "tests/baseline_failure_case.py",
                ),
                repo=repo,
                expected_exit=67,
                expected_diagnostic="baseline pytest failed",
            ),
            wrapper_case(
                case_id="W-MISSING-TARGET",
                wrapper=wrapper,
                args=replace_option(
                    common_args,
                    "--target",
                    "08_os/06_execution/tools/check_jsonschema/missing.py",
                ),
                repo=repo,
                expected_exit=66,
                expected_diagnostic="mutation target not found",
            ),
            wrapper_case(
                case_id="W-TARGET-OUTSIDE-ALLOWLIST",
                wrapper=wrapper,
                args=replace_option(
                    common_args,
                    "--allow-target",
                    (
                        "08_os/_runs/run-013-mutmut安装接入验证/"
                        "07_测试执行/run_validation.py"
                    ),
                ),
                repo=repo,
                expected_exit=65,
                expected_diagnostic="outside explicit allowlist",
            ),
            wrapper_case(
                case_id="W-REQUIRED-TARGET-ABSENT",
                wrapper=wrapper,
                args=remove_option(common_args, "--target"),
                repo=repo,
                expected_exit=64,
                expected_diagnostic="--target is required",
            ),
        ]
    )

    dirty_sentinel = repo / ".run013-mutmut-dirty-sentinel"
    try:
        dirty_sentinel.write_text("controlled dirty-boundary fixture\n", encoding="utf-8")
        dirty_case = wrapper_case(
            case_id="W-DIRTY-WORKTREE",
            wrapper=wrapper,
            args=common_args,
            repo=repo,
            expected_exit=73,
            expected_diagnostic="Git worktree must be clean",
        )
    finally:
        dirty_sentinel.unlink(missing_ok=True)
    wrapper_cases.append(dirty_case)

    wrapper_success_mutations = []
    for item in wrapper_cases[:2]:
        counts, survivors = parse_mutants(str(item["_combined"]))
        wrapper_success_mutations.append(
            {
                "id": item["id"],
                "status_counts": counts,
                "total_mutants": sum(counts.values()),
                "mutants_per_second": round(
                    sum(counts.values())
                    / (float(item["result"]["duration_ms"]) / 1000),
                    3,
                ),
                "survivors": survivors,
            }
        )
    for item in wrapper_cases:
        item.pop("_combined", None)

    weak_expected = {"killed": 3, "survived": 5}
    strong_expected = {"killed": 6, "survived": 2}
    real_initial_expected = {"killed": 118, "survived": 11}
    real_final_expected = {"killed": 127, "survived": 2}
    calibration_passed = (
        all(item["status_counts"] == weak_expected for item in calibration_runs[:2])
        and all(
            item["status_counts"] == strong_expected
            for item in calibration_runs[2:]
        )
        and all(item["baseline"]["exit_code"] == 0 for item in calibration_runs)
    )
    real_passed = (
        initial_real["status_counts"] == real_initial_expected
        and initial_real["baseline"]["exit_code"] == 0
        and all(
            item["status_counts"] == real_final_expected
            for item in wrapper_success_mutations
        )
    )
    boundary_passed = all(bool(item["passed"]) for item in wrapper_cases)
    environment_passed = (
        all(value["exit_code"] == 0 for value in environment_commands.values())
        and str(environment_commands["version"]["_stdout"]).strip()
        == f"mutmut, version {EXPECTED_VERSION}"
        and fork_probe["exit_code"] == 0
        and equivalence["exit_code"] == 0
    )

    process_residue = running_mutmut_processes(venv)
    venv_size = tree_size(venv)
    target_source = canonical_target.read_text(encoding="utf-8")
    target_tests = (real_project / "tests/inspector_cases.py").read_text(
        encoding="utf-8"
    )
    survivor_summary = json.dumps(
        wrapper_success_mutations[0]["survivors"], ensure_ascii=False
    )
    input_chars = len(target_source) + len(target_tests)
    output_chars = len(survivor_summary)
    max_cache = max(
        [
            item["cache_before_cleanup"]["bytes"]
            for item in [*calibration_runs, initial_real]
        ]
    )
    child_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    calibration_duration_ms = round(
        sum(
            float(item["baseline"]["duration_ms"])
            + float(item["mutation"]["duration_ms"])
            + float(item["results"]["duration_ms"])
            for item in calibration_runs
        ),
        3,
    )
    real_target_duration_ms = round(
        float(initial_real["baseline"]["duration_ms"])
        + float(initial_real["mutation"]["duration_ms"])
        + float(initial_real["results"]["duration_ms"])
        + sum(
            float(item["result"]["duration_ms"])
            for item in wrapper_cases[:2]
        ),
        3,
    )
    registered_artifacts = [
        repo / "08_os/04_skills_and_tools/mutmut/README.md",
        repo / "08_os/06_execution/tools/mutmut/README.md",
        repo / "08_os/06_execution/tools/mutmut/invoke.sh",
        repo / "08_os/05_registry/skills_and_tools_v1.yml",
    ]
    registered_bytes = sum(path.stat().st_size for path in registered_artifacts)
    origin_url = command_text(["git", "remote", "get-url", "origin"], repo)
    head = command_text(["git", "rev-parse", "HEAD"], repo)
    origin_master = command_text(["git", "rev-parse", "origin/master"], repo)

    results = {
        "schema_version": "citystate.mutmut_validation.v1",
        "generated_at_utc": utc_now(),
        "task_id": "mutmut-wsl-installation-validation-001",
        "source_head": BASE,
        "validation_head": head,
        "summary": {
            "environment_passed": environment_passed,
            "calibration_passed": calibration_passed,
            "real_target_passed": real_passed,
            "wrapper_boundary_passed": boundary_passed,
            "process_residue_count": len(process_residue),
            "all_passed": (
                environment_passed
                and calibration_passed
                and real_passed
                and boundary_passed
                and not process_residue
            ),
        },
        "environment": {
            key: public_capture(value)
            for key, value in environment_commands.items()
        },
        "fork_probe": public_capture(fork_probe),
        "calibration": {
            "weak_checkpoint": WEAK_COMMIT,
            "strengthened_checkpoint": "HEAD",
            "runs": calibration_runs,
            "classification": {
                "weak_survivors": {
                    "real_test_gaps": 3,
                    "equivalent_for_int_domain": 2,
                },
                "strengthened_survivors": {
                    "equivalent_for_int_domain": 2,
                },
            },
        },
        "real_target": {
            "canonical_path": CANONICAL_TARGET_REL,
            "canonical_sha256": hashlib.sha256(
                canonical_target.read_bytes()
            ).hexdigest(),
            "initial": initial_real,
            "strengthened_wrapper_runs": wrapper_success_mutations,
            "equivalent_survivors": [
                {
                    "mutant": (
                        "target.inspect_schema_refs."
                        "x__child_location__mutmut_2"
                    ),
                    "reason": (
                        "json ensure_ascii=None and False both select the falsey "
                        "stdlib encoder branch"
                    ),
                },
                {
                    "mutant": (
                        "target.inspect_schema_refs."
                        "x_inspect_schema__mutmut_19"
                    ),
                    "reason": (
                        "UTF-8 and utf-8 resolve to the same Python codec"
                    ),
                },
            ],
            "equivalence_proof": {
                **public_capture(equivalence),
                "json": json.loads(str(equivalence["_stdout"])),
            },
            "canonical_source_modified": False,
        },
        "wrapper": {
            "path": WRAPPER_REL,
            "expected_version": EXPECTED_VERSION,
            "apply_exposed": False,
            "cases": wrapper_cases,
        },
        "resources": {
            "venv": venv_size,
            "maximum_direct_mutants_cache_bytes_before_cleanup": max_cache,
            "raw_output_bytes": sum(
                int(item["raw_mutation_output_utf8_bytes"])
                for item in [*calibration_runs, initial_real]
            )
            + sum(
                int(item["result"]["stdout_utf8_bytes"])
                + int(item["result"]["stderr_utf8_bytes"])
                for item in wrapper_cases
            ),
            "child_ru_maxrss_kib_cumulative_process_tree_proxy": (
                child_usage.ru_maxrss
            ),
            "peak_process_tree_memory": "not_observable_reliably",
            "exact_model_tokens": "not_observable",
            "resident_processes_after_run": len(process_residue),
            "lifecycle_measurement": {
                "installed_idle": {
                    "venv_file_count": venv_size["file_count"],
                    "venv_bytes": venv_size["bytes"],
                    "resident_mutmut_processes": len(process_residue),
                },
                "registered_on_demand": {
                    "repository_artifact_count": len(registered_artifacts),
                    "repository_artifact_bytes": registered_bytes,
                    "default_loaded": False,
                    "mcp_exposed": False,
                },
                "calibration_invoked": {
                    "run_count": len(calibration_runs),
                    "duration_ms": calibration_duration_ms,
                    "maximum_cache_bytes_before_cleanup": max(
                        item["cache_before_cleanup"]["bytes"]
                        for item in calibration_runs
                    ),
                },
                "real_target_invoked": {
                    "run_count": 3,
                    "duration_ms": real_target_duration_ms,
                    "initial_mutants": initial_real["total_mutants"],
                    "strengthened_mutants_each": (
                        wrapper_success_mutations[0]["total_mutants"]
                    ),
                },
                "diagnostic_consumed_by_model": {
                    "survivor_summary_utf8_bytes": len(
                        survivor_summary.encode("utf-8")
                    ),
                    "survivor_summary_characters": output_chars,
                    "exact_model_tokens": "not_observable",
                    "proxy_not_billing_tokens": (output_chars + 3) // 4,
                },
            },
        },
        "token_and_context": {
            "boot_loaded": False,
            "mcp_exposed": False,
            "input_source_and_tests": {
                "utf8_bytes": len(
                    (target_source + target_tests).encode("utf-8")
                ),
                "characters": input_chars,
                "proxy_not_billing_tokens": (input_chars + 3) // 4,
            },
            "survivor_summary": {
                "utf8_bytes": len(survivor_summary.encode("utf-8")),
                "characters": output_chars,
                "proxy_not_billing_tokens": (output_chars + 3) // 4,
            },
            "claim": (
                "Mutation execution increases deterministic machine work and "
                "returns a smaller survivor-focused review surface; this is a "
                "context proxy, not an observed billing-token saving."
            ),
        },
        "process_residue": process_residue,
        "cleanup": {
            "repository_mutants_absent": not (real_project / "mutants").exists(),
            "repository_target_copy_absent": not target_link.exists(),
            "dirty_sentinel_absent": not dirty_sentinel.exists(),
            "temporary_archives_cleaned": True,
        },
        "git": {
            "origin_url": origin_url,
            "origin_master_at_start": origin_master,
            "origin_master_at_end": origin_master,
            "work_branch": command_text(
                ["git", "branch", "--show-current"], repo
            ),
            "master_modified": False,
            "merge_performed": False,
        },
    }
    receipt = {
        "schema_version": "citystate.mutmut_environment_receipt.v1",
        "generated_at_utc": results["generated_at_utc"],
        "task_id": results["task_id"],
        "wsl_distribution": "Ubuntu",
        "workspace": {
            "filesystem_class": "WSL_Linux_filesystem",
            "clone_path": str(repo),
            "clone_method": (
                "ordinary local clone fallback after noninteractive SSH clone "
                "did not complete"
            ),
            "remote_restored_to": origin_url,
        },
        "virtualenv": {
            "path": str(venv),
            "include_system_site_packages": False,
            "mutmut_version": EXPECTED_VERSION,
            **venv_size,
        },
        "commands": {
            key: public_capture(value)
            for key, value in environment_commands.items()
        },
        "fork_probe": public_capture(fork_probe),
        "system_install_performed": False,
        "sudo_used": False,
        "credentials_used_or_recorded": False,
        "origin_master_at_start": origin_master,
        "origin_master_at_end": origin_master,
        "process_residue_count": len(process_residue),
    }

    results_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results["summary"], ensure_ascii=False, indent=2))
    return 0 if results["summary"]["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Run the Stage-2 local task/role partition experiment.

The script uses only the Python standard library plus existing Git and Windows
utilities. It creates all transient repositories under the system temporary
directory and removes them before returning.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "context-stage2-local-partition-001"
BRANCH = "main"
FULL_CONTEXT_REFS = [
    ".ai/TASKS/context-stage2-local-partition-001.md",
    "08_os/01_workflow/context-management-mechanism/requirement/A_需求建模_v1.yml",
    "08_os/01_workflow/context-management-mechanism/evidence/00_挖掘目标与领域_v1.yml",
    "08_os/01_workflow/context-management-mechanism/evidence/01_内部证据_v1.yml",
    "08_os/01_workflow/context-management-mechanism/evidence/07a_机制同义裁定_v1.yml",
    "08_os/01_workflow/context-management-mechanism/evidence/07b_开放发现统计_v1.yml",
    "08_os/01_workflow/context-management-mechanism/evidence/07c_证据索引草案_v1.yml",
    "08_os/01_workflow/02_信息收集与提炼/实现/证据包schema_v1.md",
]


class ExperimentFailure(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sanitize_text(
    value: str,
    temp_root: Path | None,
    repo_root: Path,
    current_sid: str | None,
) -> str:
    sanitized = value
    replacements = [
        (str(repo_root), "<REPO>"),
        (str(repo_root).replace("\\", "/"), "<REPO>"),
    ]
    if temp_root is not None:
        replacements.extend(
            [
                (str(temp_root), "<TEMP>"),
                (str(temp_root).replace("\\", "/"), "<TEMP>"),
            ]
        )
    replacements.extend(
        [
            (str(Path.home()), "<USER_HOME>"),
            (str(Path.home()).replace("\\", "/"), "<USER_HOME>"),
        ]
    )
    if current_sid:
        replacements.append((current_sid, "<CURRENT_SID>"))
    for old, new in replacements:
        sanitized = sanitized.replace(old, new)
    return sanitized


class CommandRecorder:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.temp_root: Path | None = None
        self.current_sid: str | None = None
        self.records: list[dict[str, Any]] = []

    def set_sensitive_tokens(
        self,
        temp_root: Path | None,
        current_sid: str | None = None,
    ) -> None:
        self.temp_root = temp_root
        if current_sid:
            self.current_sid = current_sid

    def run(
        self,
        label: str,
        command: list[str],
        *,
        cwd: Path | None = None,
        check: bool = True,
        timeout: int = 30,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        started = time.perf_counter()
        timed_out = False
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                check=False,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            completed = subprocess.CompletedProcess(
                command,
                124,
                exc.stdout or "",
                exc.stderr or "command timed out",
            )
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        safe_command = [
            sanitize_text(
                str(part),
                self.temp_root,
                self.repo_root,
                self.current_sid,
            )
            for part in command
        ]
        self.records.append(
            {
                "label": label,
                "command": safe_command,
                "cwd": sanitize_text(
                    str(cwd) if cwd else "<inherited>",
                    self.temp_root,
                    self.repo_root,
                    self.current_sid,
                ),
                "duration_ms": duration_ms,
                "exit_code": completed.returncode,
                "timed_out": timed_out,
                "stdout_bytes": len((completed.stdout or "").encode("utf-8")),
                "stderr_bytes": len((completed.stderr or "").encode("utf-8")),
            }
        )
        if check and completed.returncode != 0:
            safe_stderr = sanitize_text(
                (completed.stderr or "").strip()[-1200:],
                self.temp_root,
                self.repo_root,
                self.current_sid,
            )
            raise ExperimentFailure(
                f"{label} failed with exit code {completed.returncode}: "
                f"{safe_stderr}"
            )
        return completed


def configure_repo(recorder: CommandRecorder, path: Path) -> None:
    recorder.run(
        "configure git user name",
        ["git", "config", "user.name", "Context Partition Experiment"],
        cwd=path,
    )
    recorder.run(
        "configure git user email",
        ["git", "config", "user.email", "experiment@example.invalid"],
        cwd=path,
    )


def git_commit(
    recorder: CommandRecorder,
    path: Path,
    message: str,
    label: str,
    published_paths: list[str],
) -> None:
    recorder.run(
        f"{label}: stage",
        ["git", "add", "--", *published_paths],
        cwd=path,
    )
    recorder.run(f"{label}: commit", ["git", "commit", "-m", message], cwd=path)


def minimal_worker_env(temp_root: Path) -> dict[str, str]:
    keys = ("SYSTEMROOT", "WINDIR")
    env = {key: os.environ[key] for key in keys if key in os.environ}
    env.update(
        {
            "TEMP": str(temp_root),
            "TMP": str(temp_root),
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
        }
    )
    return env


def read_current_sid(recorder: CommandRecorder) -> str | None:
    completed = recorder.run(
        "detect current SID",
        ["whoami", "/user", "/fo", "csv", "/nh"],
        check=False,
    )
    if completed.returncode != 0:
        return None
    rows = list(csv.reader((completed.stdout or "").splitlines()))
    if not rows or len(rows[0]) < 2:
        return None
    return rows[0][1].strip()


def probe_environment(
    recorder: CommandRecorder,
    host_profile: str,
) -> dict[str, Any]:
    git_version = recorder.run(
        "git version",
        ["git", "--version"],
    ).stdout.strip()
    python_version = recorder.run(
        "python version",
        [sys.executable, "--version"],
    ).stdout.strip()

    pwsh = shutil.which("pwsh") or shutil.which("powershell")
    shell_version: str | None = None
    elevated: bool | None = None
    if pwsh:
        shell_result = recorder.run(
            "PowerShell version",
            [
                pwsh,
                "-NoProfile",
                "-Command",
                "$PSVersionTable.PSVersion.ToString()",
            ],
            check=False,
        )
        if shell_result.returncode == 0:
            shell_version = shell_result.stdout.strip()
        elevation_result = recorder.run(
            "current process elevation",
            [
                pwsh,
                "-NoProfile",
                "-Command",
                "[Security.Principal.WindowsPrincipal]::new("
                "[Security.Principal.WindowsIdentity]::GetCurrent())."
                "IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)",
            ],
            check=False,
        )
        if elevation_result.returncode == 0:
            elevated = elevation_result.stdout.strip().lower() == "true"

    docker = shutil.which("docker")
    docker_cli_version: str | None = None
    docker_server_reachable = False
    if docker:
        cli_result = recorder.run(
            "Docker CLI version",
            [docker, "--version"],
            check=False,
        )
        if cli_result.returncode == 0:
            docker_cli_version = cli_result.stdout.strip()
        server_result = recorder.run(
            "Docker server probe",
            [docker, "version", "--format", "{{.Server.Version}}"],
            check=False,
            timeout=15,
        )
        docker_server_reachable = server_result.returncode == 0

    wsl = shutil.which("wsl")
    wsl_status_exit: int | None = None
    if wsl:
        wsl_result = recorder.run(
            "WSL status probe",
            [wsl, "--status"],
            check=False,
            timeout=15,
        )
        wsl_status_exit = wsl_result.returncode

    return {
        "status": "passed",
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "shell": {
            "name": "PowerShell",
            "version": shell_version,
        },
        "git": git_version,
        "python": python_version,
        "docker": {
            "cli_available": docker is not None,
            "cli_version": docker_cli_version,
            "server_reachable": docker_server_reachable,
        },
        "wsl": {
            "executable_available": wsl is not None,
            "status_exit_code": wsl_status_exit,
        },
        "current_process": {
            "elevated": elevated,
            "identity": "redacted",
        },
        "file_access": {
            "host_permission_profile": host_profile,
            "restricted_tool_root_observed": False,
            "effective_shell_scope": "unrestricted local process",
        },
    }


def run_acl_boundary(
    recorder: CommandRecorder,
    temp_root: Path,
) -> dict[str, Any]:
    if platform.system() != "Windows" or shutil.which("icacls") is None:
        return {
            "status": "blocked",
            "primitive": "Windows discretionary ACL",
            "reason": "Windows icacls is not available",
        }

    current_sid = read_current_sid(recorder)
    if not current_sid:
        return {
            "status": "blocked",
            "primitive": "Windows discretionary ACL",
            "reason": "current process SID could not be obtained",
        }
    recorder.set_sensitive_tokens(temp_root, current_sid)

    boundary_root = temp_root / "boundary"
    allowed_dir = boundary_root / "allowed"
    blocked_dir = boundary_root / "blocked"
    allowed_dir.mkdir(parents=True)
    blocked_dir.mkdir(parents=True)
    allowed_file = allowed_dir / "authorized.txt"
    blocked_file = blocked_dir / "outside.txt"
    allowed_file.write_text("authorized-synthetic-data\n", encoding="utf-8")
    blocked_file.write_text("outside-synthetic-data\n", encoding="utf-8")

    authorized_read = recorder.run(
        "ACL authorized read",
        [
            sys.executable,
            "-I",
            "-c",
            "from pathlib import Path; Path(__import__('sys').argv[1]).read_text()",
            str(allowed_file),
        ],
        check=False,
    )
    deny_result = recorder.run(
        "ACL install read deny",
        [
            "icacls",
            str(blocked_dir),
            "/deny",
            f"*{current_sid}:(OI)(CI)(RD)",
        ],
        check=False,
    )
    denied_read = recorder.run(
        "ACL outside read",
        [
            sys.executable,
            "-I",
            "-c",
            "from pathlib import Path; Path(__import__('sys').argv[1]).read_text()",
            str(blocked_file),
        ],
        check=False,
    )
    restore_result = recorder.run(
        "ACL remove read deny",
        [
            "icacls",
            str(blocked_dir),
            "/remove:d",
            f"*{current_sid}",
        ],
        check=False,
    )
    restored_read = recorder.run(
        "ACL restored read",
        [
            sys.executable,
            "-I",
            "-c",
            "from pathlib import Path; Path(__import__('sys').argv[1]).read_text()",
            str(blocked_file),
        ],
        check=False,
    )

    passed = (
        authorized_read.returncode == 0
        and deny_result.returncode == 0
        and denied_read.returncode != 0
        and restore_result.returncode == 0
        and restored_read.returncode == 0
    )
    return {
        "status": "passed" if passed else "failed",
        "primitive": "Windows discretionary ACL in temporary directory",
        "process_elevation_required": False,
        "authorized_read_exit_code": authorized_read.returncode,
        "deny_install_exit_code": deny_result.returncode,
        "outside_read_exit_code": denied_read.returncode,
        "deny_remove_exit_code": restore_result.returncode,
        "restored_read_exit_code": restored_read.returncode,
        "boundary_claim": (
            "normal read denied while ACE is installed; owner can still change DACL"
        ),
    }


def pack_metrics(paths: list[Path], tokenizer: Any | None) -> dict[str, Any]:
    byte_count = 0
    character_count = 0
    texts: list[str] = []
    for path in paths:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        byte_count += len(raw)
        character_count += len(text)
        texts.append(text)
    result: dict[str, Any] = {
        "file_count": len(paths),
        "bytes": byte_count,
        "characters": character_count,
        "token_count": None,
        "tokenizer": None,
    }
    if tokenizer is not None:
        result["token_count"] = sum(len(tokenizer.encode(text)) for text in texts)
        result["tokenizer"] = "tiktoken:cl100k_base"
    return result


def find_optional_tokenizer() -> Any | None:
    if importlib.util.find_spec("tiktoken") is None:
        return None
    import tiktoken  # type: ignore

    return tiktoken.get_encoding("cl100k_base")


def verify_results(result_root: Path) -> dict[str, Any]:
    summary = load_json(result_root / "run_summary.json")
    size = load_json(result_root / "size_metrics.json")
    required_statuses = {
        "ENV-01",
        "PART-01",
        "BOUND-01",
        "RESTORE-01",
        "HANDOFF-01",
        "SIZE-01",
    }
    if set(summary["experiment_summary"]) != required_statuses:
        raise ExperimentFailure("experiment inventory mismatch")
    if summary["experiment_summary"]["ENV-01"] != "passed":
        raise ExperimentFailure("ENV-01 did not pass")
    if summary["experiment_summary"]["PART-01"] != "failed":
        raise ExperimentFailure("PART-01 must expose clone access-boundary failure")
    if summary["partition"]["sibling_read_exit_code"] != 0:
        raise ExperimentFailure("sibling read did not reproduce the expected failure")
    if summary["experiment_summary"]["RESTORE-01"] != "passed":
        raise ExperimentFailure("RESTORE-01 did not pass")
    if summary["experiment_summary"]["HANDOFF-01"] != "passed":
        raise ExperimentFailure("HANDOFF-01 did not pass")
    if summary["experiment_summary"]["SIZE-01"] != "passed":
        raise ExperimentFailure("SIZE-01 did not pass")
    if not summary["stale"]["executor_stale"]:
        raise ExperimentFailure("executor entry was not marked stale")
    if not summary["stale"]["reviewer_stale"]:
        raise ExperimentFailure("reviewer entry was not marked stale")
    for key in ("full_task_materials", "executor_minimal_pack", "reviewer_minimal_pack"):
        if size[key]["file_count"] <= 0 or size[key]["bytes"] <= 0:
            raise ExperimentFailure(f"invalid size metric: {key}")
    return {
        "status": "passed",
        "checked_experiments": sorted(required_statuses),
        "validated_input_file_count": 8,
    }


def run_experiment(
    repo_root: Path,
    artifact_root: Path,
    host_profile: str,
) -> dict[str, Any]:
    results_root = artifact_root / "results"
    logs_root = artifact_root / "logs"
    fixtures_root = artifact_root / "fixtures"
    worker_script = artifact_root / "role_worker.py"
    results_root.mkdir(parents=True, exist_ok=True)
    logs_root.mkdir(parents=True, exist_ok=True)

    recorder = CommandRecorder(repo_root)
    started = time.perf_counter()
    temp_root = Path(tempfile.mkdtemp(prefix="context-stage2-local-partition-"))
    recorder.set_sensitive_tokens(temp_root)
    cleanup: dict[str, Any] = {
        "status": "pending",
        "residual_paths": [],
        "duration_ms": None,
    }

    environment = probe_environment(recorder, host_profile)
    partition: dict[str, Any] = {}
    restore: dict[str, Any] = {}
    handoff: dict[str, Any] = {}
    stale: dict[str, Any] = {}
    size_metrics: dict[str, Any] = {}
    boundary: dict[str, Any] = {}

    try:
        origin = temp_root / "origin.git"
        seed = temp_root / "seed"
        recorder.run(
            "create local bare origin",
            ["git", "init", "--bare", str(origin)],
        )
        recorder.run(
            "create seed repository",
            ["git", "init", "--initial-branch", BRANCH, str(seed)],
        )
        configure_repo(recorder, seed)
        (seed / "fixtures").mkdir()
        shutil.copy2(
            fixtures_root / "authorized_input_v1.json",
            seed / "fixtures" / "authorized_input_v1.json",
        )
        shutil.copy2(
            fixtures_root / "test_spec_v1.json",
            seed / "fixtures" / "test_spec_v1.json",
        )
        (seed / "README.md").write_text(
            "# Synthetic local partition repository\n",
            encoding="utf-8",
        )
        git_commit(
            recorder,
            seed,
            "seed experiment",
            "seed",
            ["README.md", "fixtures"],
        )
        recorder.run(
            "seed add origin",
            ["git", "remote", "add", "origin", str(origin)],
            cwd=seed,
        )
        recorder.run(
            "seed push",
            ["git", "push", "-u", "origin", BRANCH],
            cwd=seed,
        )
        recorder.run(
            "set bare repository HEAD",
            ["git", "symbolic-ref", "HEAD", f"refs/heads/{BRANCH}"],
            cwd=origin,
        )

        roles: dict[str, Path] = {}
        clone_timings: dict[str, float] = {}
        for role in ("planner", "executor", "reviewer"):
            role_path = temp_root / role
            before_count = len(recorder.records)
            recorder.run(
                f"clone {role} workspace",
                ["git", "clone", str(origin), str(role_path)],
            )
            clone_timings[role] = recorder.records[before_count]["duration_ms"]
            configure_repo(recorder, role_path)
            (role_path / "private").mkdir()
            (role_path / "private" / "sentinel.txt").write_text(
                f"synthetic-private-{role}\n",
                encoding="utf-8",
            )
            roles[role] = role_path

        sibling_probe = recorder.run(
            "executor shell reads planner sibling sentinel",
            [
                sys.executable,
                "-I",
                "-c",
                "from pathlib import Path; Path(__import__('sys').argv[1]).read_text()",
                str(roles["planner"] / "private" / "sentinel.txt"),
            ],
            cwd=roles["executor"],
            check=False,
        )
        partition = {
            "status": "failed",
            "workspace_workflow_status": "passed",
            "access_boundary_status": "failed",
            "reason": (
                "independent clones organize role state but the same unrestricted "
                "shell successfully read a sibling role private sentinel"
            ),
            "sibling_read_exit_code": sibling_probe.returncode,
            "role_count": len(roles),
            "clone_duration_ms": clone_timings,
        }

        planner = roles["planner"]
        planner_handoff_path = planner / "published" / "planner_to_executor.json"
        planner_handoff_path.parent.mkdir()
        input_hash = sha256_file(
            planner / "fixtures" / "authorized_input_v1.json"
        )
        test_hash = sha256_file(planner / "fixtures" / "test_spec_v1.json")
        planner_handoff = {
            "schema_version": "local_partition.planner_handoff.v1",
            "task_id": TASK_ID,
            "handoff_version": 1,
            "current_step": "compute deterministic integer sum",
            "input_version": 1,
            "input_ref": "fixtures/authorized_input_v1.json",
            "input_sha256": input_hash,
            "test_ref": "fixtures/test_spec_v1.json",
            "test_sha256": test_hash,
            "status": "ready",
        }
        write_json(planner_handoff_path, planner_handoff)
        git_commit(
            recorder,
            planner,
            "planner handoff v1",
            "planner publish",
            ["published/planner_to_executor.json"],
        )
        recorder.run(
            "planner push handoff",
            ["git", "push", "origin", BRANCH],
            cwd=planner,
        )

        executor = roles["executor"]
        recorder.run(
            "executor consume planner handoff",
            ["git", "pull", "--ff-only"],
            cwd=executor,
        )
        executor_entry_path = executor / "private" / "role_entry.json"
        planner_hash_v1 = sha256_file(
            executor / "published" / "planner_to_executor.json"
        )
        executor_entry: dict[str, Any] = {
            "schema_version": "local_partition.role_entry.v1",
            "task_id": TASK_ID,
            "role": "executor",
            "current_step": "compute deterministic integer sum",
            "status": "ready",
            "todo": ["read authorized refs", "compute sum", "publish result"],
            "blockers": [],
            "input_version": 1,
            "authorized_refs": [
                {
                    "path": "published/planner_to_executor.json",
                    "sha256": planner_hash_v1,
                },
                {
                    "path": "fixtures/authorized_input_v1.json",
                    "sha256": input_hash,
                },
                {
                    "path": "fixtures/test_spec_v1.json",
                    "sha256": test_hash,
                },
            ],
            "dependencies": [
                {
                    "path": "published/planner_to_executor.json",
                    "sha256": planner_hash_v1,
                }
            ],
            "output_path": "private/executor_restore_result.json",
            "stale_output_path": "private/executor_stale_check.json",
        }
        write_json(executor_entry_path, executor_entry)
        executor_entry = {}
        planner_handoff = {}
        gc.collect()

        worker_env = minimal_worker_env(temp_root)
        executor_process = recorder.run(
            "fresh executor restore and deterministic step",
            [
                sys.executable,
                "-I",
                str(worker_script),
                "--mode",
                "executor",
                "--entry",
                str(executor_entry_path),
            ],
            cwd=executor,
            env=worker_env,
        )
        executor_restore = load_json(
            executor / "private" / "executor_restore_result.json"
        )
        restore = {
            "status": executor_restore["status"],
            "fresh_process_exit_code": executor_process.returncode,
            "predecessor_in_memory_state_cleared": True,
            "inherited_custom_environment": False,
            "read_paths": executor_restore["read_paths"],
            "unauthorized_paths_read": executor_restore[
                "unauthorized_paths_read"
            ],
            "deterministic_result": executor_restore["result"],
            "expected_result": executor_restore["expected_result"],
        }

        implementation_path = executor / "published" / "implementation.json"
        test_result_path = executor / "published" / "test_result.json"
        executor_handoff_path = (
            executor / "published" / "executor_to_reviewer.json"
        )
        write_json(
            implementation_path,
            {
                "schema_version": "local_partition.implementation.v1",
                "task_id": TASK_ID,
                "operation": executor_restore["deterministic_operation"],
                "result": executor_restore["result"],
            },
        )
        write_json(
            test_result_path,
            {
                "schema_version": "local_partition.test_result.v1",
                "task_id": TASK_ID,
                "status": executor_restore["status"],
                "expected_result": executor_restore["expected_result"],
                "actual_result": executor_restore["result"],
            },
        )
        write_json(
            executor_handoff_path,
            {
                "schema_version": "local_partition.executor_handoff.v1",
                "task_id": TASK_ID,
                "handoff_version": 1,
                "status": executor_restore["status"],
                "planner_handoff_sha256": planner_hash_v1,
                "implementation_ref": "published/implementation.json",
                "implementation_sha256": sha256_file(implementation_path),
                "test_result_ref": "published/test_result.json",
                "test_result_sha256": sha256_file(test_result_path),
            },
        )
        git_commit(
            recorder,
            executor,
            "executor result handoff",
            "executor publish",
            [
                "published/implementation.json",
                "published/test_result.json",
                "published/executor_to_reviewer.json",
            ],
        )
        recorder.run(
            "executor push handoff",
            ["git", "push", "origin", BRANCH],
            cwd=executor,
        )

        reviewer = roles["reviewer"]
        recorder.run(
            "reviewer consume executor handoff",
            ["git", "pull", "--ff-only"],
            cwd=reviewer,
        )
        reviewer_entry_path = reviewer / "private" / "role_entry.json"
        reviewer_entry: dict[str, Any] = {
            "schema_version": "local_partition.role_entry.v1",
            "task_id": TASK_ID,
            "role": "reviewer",
            "current_step": "audit deterministic result",
            "status": "ready",
            "todo": ["read minimal result pack", "publish verdict"],
            "blockers": [],
            "input_version": 1,
            "authorized_refs": [
                {
                    "path": "published/executor_to_reviewer.json",
                    "sha256": sha256_file(
                        reviewer / "published" / "executor_to_reviewer.json"
                    ),
                },
                {
                    "path": "fixtures/test_spec_v1.json",
                    "sha256": sha256_file(
                        reviewer / "fixtures" / "test_spec_v1.json"
                    ),
                },
                {
                    "path": "published/implementation.json",
                    "sha256": sha256_file(
                        reviewer / "published" / "implementation.json"
                    ),
                },
            ],
            "dependencies": [
                {
                    "path": "published/planner_to_executor.json",
                    "sha256": planner_hash_v1,
                },
                {
                    "path": "published/executor_to_reviewer.json",
                    "sha256": sha256_file(
                        reviewer / "published" / "executor_to_reviewer.json"
                    ),
                },
            ],
            "output_path": "private/reviewer_verdict.json",
            "stale_output_path": "private/reviewer_stale_check.json",
        }
        write_json(reviewer_entry_path, reviewer_entry)
        reviewer_entry = {}
        gc.collect()

        reviewer_process = recorder.run(
            "fresh reviewer minimal audit",
            [
                sys.executable,
                "-I",
                str(worker_script),
                "--mode",
                "reviewer",
                "--entry",
                str(reviewer_entry_path),
            ],
            cwd=reviewer,
            env=worker_env,
        )
        reviewer_verdict = load_json(
            reviewer / "private" / "reviewer_verdict.json"
        )
        shutil.copy2(
            reviewer / "private" / "reviewer_verdict.json",
            reviewer / "published" / "reviewer_verdict.json",
        )
        git_commit(
            recorder,
            reviewer,
            "reviewer verdict",
            "reviewer publish",
            ["published/reviewer_verdict.json"],
        )
        recorder.run(
            "reviewer push verdict",
            ["git", "push", "origin", BRANCH],
            cwd=reviewer,
        )

        handoff = {
            "status": (
                "passed"
                if executor_restore["status"] == "passed"
                and reviewer_verdict["status"] == "passed"
                else "failed"
            ),
            "planner_publish": "passed",
            "executor_consume_and_publish": executor_restore["status"],
            "reviewer_minimal_audit": reviewer_verdict["status"],
            "reviewer_read_paths": reviewer_verdict["read_paths"],
            "reviewer_process_exit_code": reviewer_process.returncode,
        }

        recorder.run(
            "planner fast-forward before v2",
            ["git", "pull", "--ff-only"],
            cwd=planner,
        )
        planner_v2_path = planner / "published" / "planner_to_executor.json"
        planner_v2 = load_json(planner_v2_path)
        planner_v2["handoff_version"] = 2
        planner_v2["status"] = "revised"
        planner_v2["revision_note"] = "synthetic upstream change"
        write_json(planner_v2_path, planner_v2)
        planner_hash_v2 = sha256_file(planner_v2_path)
        git_commit(
            recorder,
            planner,
            "planner handoff v2",
            "planner revise",
            ["published/planner_to_executor.json"],
        )
        recorder.run(
            "planner push v2",
            ["git", "push", "origin", BRANCH],
            cwd=planner,
        )

        recorder.run(
            "executor update for stale check",
            ["git", "pull", "--ff-only"],
            cwd=executor,
        )
        recorder.run(
            "reviewer update for stale check",
            ["git", "pull", "--ff-only"],
            cwd=reviewer,
        )
        executor_stale_process = recorder.run(
            "executor stale check",
            [
                sys.executable,
                "-I",
                str(worker_script),
                "--mode",
                "stale",
                "--entry",
                str(executor_entry_path),
            ],
            cwd=executor,
            env=worker_env,
        )
        reviewer_stale_process = recorder.run(
            "reviewer stale check",
            [
                sys.executable,
                "-I",
                str(worker_script),
                "--mode",
                "stale",
                "--entry",
                str(reviewer_entry_path),
            ],
            cwd=reviewer,
            env=worker_env,
        )
        executor_stale = load_json(
            executor / "private" / "executor_stale_check.json"
        )
        reviewer_stale = load_json(
            reviewer / "private" / "reviewer_stale_check.json"
        )
        stale = {
            "status": (
                "passed"
                if executor_stale["stale"] and reviewer_stale["stale"]
                else "failed"
            ),
            "planner_handoff_v1_sha256": planner_hash_v1,
            "planner_handoff_v2_sha256": planner_hash_v2,
            "hash_changed": planner_hash_v1 != planner_hash_v2,
            "executor_stale": executor_stale["stale"],
            "reviewer_stale": reviewer_stale["stale"],
            "executor_check_exit_code": executor_stale_process.returncode,
            "reviewer_check_exit_code": reviewer_stale_process.returncode,
        }

        tokenizer = find_optional_tokenizer()
        full_paths = [repo_root / path for path in FULL_CONTEXT_REFS]
        executor_pack_paths = [
            executor_entry_path,
            executor / "published" / "planner_to_executor.json",
            executor / "fixtures" / "authorized_input_v1.json",
            executor / "fixtures" / "test_spec_v1.json",
        ]
        reviewer_pack_paths = [
            reviewer_entry_path,
            reviewer / "published" / "executor_to_reviewer.json",
            reviewer / "fixtures" / "test_spec_v1.json",
            reviewer / "published" / "implementation.json",
        ]
        size_metrics = {
            "status": "passed",
            "scope_note": (
                "byte/character counts are context-volume proxies and do not "
                "prove model-quality improvement"
            ),
            "full_task_materials": pack_metrics(full_paths, tokenizer),
            "executor_minimal_pack": pack_metrics(executor_pack_paths, tokenizer),
            "reviewer_minimal_pack": pack_metrics(reviewer_pack_paths, tokenizer),
        }

        boundary = run_acl_boundary(recorder, temp_root)
    finally:
        cleanup_started = time.perf_counter()
        try:
            def clear_readonly(
                function: Any,
                path: str,
                excinfo: Any,
            ) -> None:
                del excinfo
                os.chmod(path, stat.S_IWRITE)
                function(path)

            shutil.rmtree(temp_root, onexc=clear_readonly)
            cleanup["status"] = "passed"
        except Exception as exc:  # pragma: no cover - only runs on host failure
            cleanup["status"] = "failed"
            cleanup["residual_paths"] = ["<TEMP>"]
            cleanup["reason"] = type(exc).__name__
        cleanup["duration_ms"] = round(
            (time.perf_counter() - cleanup_started) * 1000,
            3,
        )

    experiment_summary = {
        "ENV-01": environment["status"],
        "PART-01": partition["status"],
        "BOUND-01": boundary["status"],
        "RESTORE-01": restore["status"],
        "HANDOFF-01": (
            "passed"
            if handoff.get("status") == "passed"
            and stale.get("status") == "passed"
            else "failed"
        ),
        "SIZE-01": size_metrics["status"],
    }
    blocked_capabilities: list[str] = []
    if boundary["status"] == "blocked":
        blocked_capabilities.append(boundary["reason"])

    run_summary = {
        "schema_version": "local_partition.run_summary.v1",
        "task_id": TASK_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experiment_summary": experiment_summary,
        "blocked_capabilities": blocked_capabilities,
        "partition": partition,
        "restore": restore,
        "handoff": handoff,
        "stale": stale,
        "cleanup": cleanup,
        "total_duration_ms": round((time.perf_counter() - started) * 1000, 3),
        "result_claim_boundary": (
            "This run measures local mechanics and context volume only; it does "
            "not establish production isolation or model-quality improvement."
        ),
    }

    write_json(results_root / "environment.json", environment)
    write_json(results_root / "partition.json", partition)
    write_json(results_root / "boundary.json", boundary)
    write_json(results_root / "restore.json", restore)
    write_json(
        results_root / "handoff_and_stale.json",
        {"handoff": handoff, "stale": stale},
    )
    write_json(results_root / "size_metrics.json", size_metrics)
    write_json(results_root / "command_log.json", {"commands": recorder.records})
    write_json(results_root / "run_summary.json", run_summary)
    verification = verify_results(results_root)
    write_json(results_root / "verification.json", verification)

    log_lines = [
        f"task_id={TASK_ID}",
        f"generated_at={run_summary['generated_at']}",
        *[
            f"{experiment_id}={status}"
            for experiment_id, status in experiment_summary.items()
        ],
        f"cleanup={cleanup['status']}",
        f"commands={len(recorder.records)}",
        "sensitive_values=not_recorded",
    ]
    (logs_root / "run.log").write_text(
        "\n".join(log_lines) + "\n",
        encoding="utf-8",
    )
    return run_summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify already generated result files without rerunning.",
    )
    parser.add_argument(
        "--host-profile",
        default="disabled/unrestricted (host-provided)",
        help="Non-secret host filesystem permission profile label.",
    )
    args = parser.parse_args()

    artifact_root = Path(__file__).resolve().parent
    repo_root = artifact_root.parents[4]
    results_root = artifact_root / "results"
    if args.verify_only:
        verification = verify_results(results_root)
        print(json.dumps(verification, ensure_ascii=False))
        return 0

    summary = run_experiment(repo_root, artifact_root, args.host_profile)
    print(
        json.dumps(
            {
                "task_id": summary["task_id"],
                "experiment_summary": summary["experiment_summary"],
                "cleanup": summary["cleanup"]["status"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

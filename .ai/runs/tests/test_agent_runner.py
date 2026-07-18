from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT / "agent-run.ps1"
STATUS = ROOT / "agent-status.ps1"
STOP = ROOT / "agent-stop.ps1"
COMMON = ROOT / ".ai" / "runs" / "Runner.Common.ps1"
FIXTURES = Path(__file__).parent / "fixtures"
POWERSHELL = shutil.which("powershell.exe")


def native(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def ps(script: Path, *args: str, cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    return native(
        POWERSHELL,
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        *args,
        cwd=cwd,
        check=check,
    )


def init_repo(tmp_path: Path, task_id: str, *, base_override: str | None = None, branch: str | None = None) -> dict[str, Path | str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    native("git", "init", cwd=repo)
    native("git", "checkout", "-b", "master", cwd=repo)
    native("git", "config", "user.email", "runner-tests@example.invalid", cwd=repo)
    native("git", "config", "user.name", "Runner Tests", cwd=repo)
    (repo / ".ai" / "runs").mkdir(parents=True)
    (repo / ".ai" / "TASKS").mkdir(parents=True)
    shutil.copy2(COMMON, repo / ".ai" / "runs" / "Runner.Common.ps1")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    native("git", "add", ".ai/runs/Runner.Common.ps1", "seed.txt", cwd=repo)
    native("git", "commit", "-m", "seed", cwd=repo)
    base = native("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
    expected = base_override or base
    work_branch = branch or f"dev/{task_id}"
    packet = f'''---
task_id: "{task_id}"
assigned_executor: "codex"
base:
  branch: "master"
  head: "{expected}"
work_branch: "{work_branch}"
validation_commands:
  - "Write-Output validation-ok; exit 0"
---

## 2. definition_of_done

- fixture lifecycle completes

## 5. stop_rules

- stop on base mismatch

allowed:
- `.ai/runs/**`

forbidden:
- `.ai/PROTOCOL.md`
'''
    (repo / ".ai" / "TASKS" / f"{task_id}.md").write_text(packet, encoding="utf-8")
    return {
        "repo": repo,
        "base": base,
        "worktrees": tmp_path / "worktrees",
        "ledger": tmp_path / "ledger",
        "branch": work_branch,
    }


def runner_args(env: dict[str, Path | str], task_id: str, fixture: str, *, wait: bool = True) -> list[str]:
    args = [
        "-TaskId",
        task_id,
        "-Engine",
        "codex",
        "-Tier",
        "citystate_t1",
        "-TestMode",
        "-TestEngineScript",
        str(FIXTURES / fixture),
        "-HeartbeatSeconds",
        "1",
        "-RepoRoot",
        str(env["repo"]),
        "-WorktreeRoot",
        str(env["worktrees"]),
        "-LedgerRoot",
        str(env["ledger"]),
    ]
    if wait:
        args.append("-Wait")
    return args


def read_status(env: dict[str, Path | str], task_id: str) -> dict:
    path = Path(env["repo"]) / ".ai" / "runs" / task_id / "status.json"
    return json.loads(path.read_text(encoding="utf-8"))


def process_alive(pid: int) -> bool:
    run = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{exit 0}}else{{exit 1}}"],
        capture_output=True,
    )
    return run.returncode == 0


def wait_until(predicate, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.2)
    raise AssertionError("condition did not become true before timeout")


@pytest.mark.skipif(POWERSHELL is None, reason="Windows PowerShell is required")
def test_rejects_base_head_mismatch_before_lock(tmp_path: Path) -> None:
    task_id = "fixture-base-mismatch"
    env = init_repo(tmp_path, task_id, base_override="0" * 40)
    run = ps(RUNNER, *runner_args(env, task_id, "fake-engine-success.ps1"), cwd=Path(env["repo"]))
    assert run.returncode != 0
    assert "Base HEAD mismatch" in (run.stdout + run.stderr)
    assert not (Path(env["repo"]) / ".ai" / "runs" / task_id / "LOCK").exists()


@pytest.mark.skipif(POWERSHELL is None, reason="Windows PowerShell is required")
def test_reads_task_packet_from_fetched_review_ref(tmp_path: Path) -> None:
    task_id = "fixture-review-mailbox"
    env = init_repo(tmp_path, task_id)
    repo = Path(env["repo"])
    packet = repo / ".ai" / "TASKS" / f"{task_id}.md"
    native("git", "checkout", "-b", "review-fixture", cwd=repo)
    native("git", "add", packet.relative_to(repo).as_posix(), cwd=repo)
    native("git", "commit", "-m", "review mailbox fixture", cwd=repo)
    review_head = native("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
    native("git", "update-ref", "refs/remotes/origin/ai/review/latest", review_head, cwd=repo)
    native("git", "checkout", "master", cwd=repo)
    assert not packet.exists()

    run = ps(RUNNER, *runner_args(env, task_id, "fake-engine-success.ps1"), cwd=repo)
    assert run.returncode == 0, run.stdout + run.stderr
    session = json.loads((repo / ".ai" / "runs" / task_id / "session.json").read_text(encoding="utf-8"))
    assert session["task_packet"] == f"origin/ai/review/latest:.ai/TASKS/{task_id}.md"


@pytest.mark.skipif(POWERSHELL is None, reason="Windows PowerShell is required")
def test_live_task_and_branch_locks_reject_second_writer(tmp_path: Path) -> None:
    task_id = "fixture-lock"
    env = init_repo(tmp_path, task_id)
    run_dir = Path(env["repo"]) / ".ai" / "runs" / task_id
    run_dir.mkdir(parents=True, exist_ok=True)
    lock = {"owner": "pytest", "pid": os.getpid(), "engine": "codex", "started_at": "2026-07-18T00:00:00Z"}
    (run_dir / "LOCK").write_text(json.dumps(lock), encoding="utf-8")
    run = ps(RUNNER, *runner_args(env, task_id, "fake-engine-success.ps1"), cwd=Path(env["repo"]))
    assert run.returncode != 0
    assert "task lock is active" in (run.stdout + run.stderr)
    (run_dir / "LOCK").unlink()

    digest = hashlib.sha256(str(env["branch"]).lower().encode()).hexdigest()
    branch_dir = Path(env["worktrees"]) / "_branch_locks"
    branch_dir.mkdir(parents=True)
    (branch_dir / f"{digest}.lock").write_text(json.dumps(lock), encoding="utf-8")
    run = ps(RUNNER, *runner_args(env, task_id, "fake-engine-success.ps1"), cwd=Path(env["repo"]))
    assert run.returncode != 0
    assert "branch writer lock is active" in (run.stdout + run.stderr)


@pytest.mark.skipif(POWERSHELL is None, reason="Windows PowerShell is required")
def test_heartbeat_exit_cleanup_validation_and_token_record(tmp_path: Path) -> None:
    task_id = "fixture-success"
    env = init_repo(tmp_path, task_id)
    run = ps(RUNNER, *runner_args(env, task_id, "fake-engine-success.ps1"), cwd=Path(env["repo"]))
    assert run.returncode == 0, run.stdout + run.stderr
    status = read_status(env, task_id)
    required = {
        "task_id", "engine", "tier", "state", "started_at", "pid", "session_id", "worktree",
        "base_branch", "base_head", "last_heartbeat", "exit_code", "handoff_ref",
    }
    assert set(status) == required
    assert status["state"] == "done"
    assert status["exit_code"] == 0
    assert status["session_id"] == "019f-test-session-0001"
    assert status["last_heartbeat"] >= status["started_at"]
    run_dir = Path(env["repo"]) / ".ai" / "runs" / task_id
    assert not (run_dir / "LOCK").exists()
    assert "validation-ok" in (run_dir / "validation.log").read_text(encoding="utf-8")
    assert "synthetic-test-value" not in (run_dir / "run.log").read_text(encoding="utf-8")
    assert "[REDACTED sensitive-looking line]" in (run_dir / "run.log").read_text(encoding="utf-8")
    assert len((run_dir / "final-report.md").read_text(encoding="utf-8").splitlines()) <= 60
    records = list(Path(env["ledger"]).glob("*.json"))
    assert len(records) == 1
    record = json.loads(records[0].read_text(encoding="utf-8"))
    assert record["schema_version"] == "token_profile_run.v1"
    assert record["validation_result"] == "done"
    child_pid = int((Path(status["worktree"]) / "child.pid").read_text())
    wait_until(lambda: not process_alive(child_pid))


@pytest.mark.skipif(POWERSHELL is None, reason="Windows PowerShell is required")
def test_nonzero_exit_is_captured_and_locks_are_released(tmp_path: Path) -> None:
    task_id = "fixture-failure"
    env = init_repo(tmp_path, task_id)
    run = ps(RUNNER, *runner_args(env, task_id, "fake-engine-failure.ps1"), cwd=Path(env["repo"]))
    assert run.returncode != 0
    status = read_status(env, task_id)
    assert status["state"] == "failed"
    assert status["exit_code"] == 7
    assert not (Path(env["repo"]) / ".ai" / "runs" / task_id / "LOCK").exists()
    records = list(Path(env["ledger"]).glob("*.json"))
    assert len(records) == 1
    assert json.loads(records[0].read_text(encoding="utf-8"))["validation_result"] == "failed"


@pytest.mark.skipif(POWERSHELL is None, reason="Windows PowerShell is required")
def test_agent_stop_terminates_process_tree_and_writes_stopped_evidence(tmp_path: Path) -> None:
    task_id = "fixture-stop"
    env = init_repo(tmp_path, task_id)
    launch = ps(RUNNER, *runner_args(env, task_id, "fake-engine-long.ps1", wait=False), cwd=Path(env["repo"]))
    assert launch.returncode == 0, launch.stdout + launch.stderr
    wait_until(lambda: (Path(env["repo"]) / ".ai" / "runs" / task_id / "status.json").exists() and read_status(env, task_id)["state"] == "running")
    status_before = ps(STATUS, "-TaskId", task_id, "-RepoRoot", str(env["repo"]), cwd=Path(env["repo"]))
    assert status_before.returncode == 0
    assert json.loads(status_before.stdout)["process_alive"] is True
    worktree = Path(read_status(env, task_id)["worktree"])
    wait_until(lambda: (worktree / "child.pid").exists())
    child_pid = int((worktree / "child.pid").read_text())
    stopped = ps(STOP, "-TaskId", task_id, "-RepoRoot", str(env["repo"]), cwd=Path(env["repo"]))
    assert stopped.returncode == 0, stopped.stdout + stopped.stderr
    wait_until(lambda: not process_alive(child_pid))
    status = read_status(env, task_id)
    assert status["state"] == "stopped"
    run_dir = Path(env["repo"]) / ".ai" / "runs" / task_id
    assert not (run_dir / "LOCK").exists()
    assert (run_dir / "final-report.md").exists()
    records = list(Path(env["ledger"]).glob("*.json"))
    assert records
    assert any(json.loads(path.read_text(encoding="utf-8"))["validation_result"] == "stopped" for path in records)

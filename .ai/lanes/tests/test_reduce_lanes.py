import hashlib
import json
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "reduce-lanes.ps1"
ENVELOPE_SCHEMA = SCRIPT.parent / "lane_envelope.schema.json"
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def git(repo: Path, *args: str) -> str:
    return run("git", *args, cwd=repo).stdout.strip()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def commit_all(repo: Path, message: str) -> str:
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def new_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "lane-test@example.invalid")
    git(repo, "config", "user.name", "Lane Test")
    schema_target = repo / ".ai" / "lanes" / "lane_envelope.schema.json"
    schema_target.parent.mkdir(parents=True)
    shutil.copyfile(ENVELOPE_SCHEMA, schema_target)
    (repo / "seed.txt").write_text("base\n", encoding="utf-8")
    base = commit_all(repo, "base")
    (repo / "epoch.txt").write_text("epoch\n", encoding="utf-8")
    epoch = commit_all(repo, "epoch")
    return repo, base, epoch


def add_envelope(
    repo: Path,
    lane_dir: str,
    envelope_lane: str,
    seq: int,
    lane_protocol_epoch: str,
    base_review_head: str,
    *,
    role: str = "backend_execution_and_handoff",
    environment_class: str = "codex_desktop",
) -> Path:
    path = repo / ".ai" / "lanes" / lane_dir / "events" / f"{seq:03d}.lane-envelope.yml"
    write_json(
        path,
        {
            "lane_instance_id": envelope_lane,
            "environment_class": environment_class,
            "protocol_role": role,
            "load_profile_id": "backend_executor",
            "message_seq": seq,
            "lane_protocol_epoch": lane_protocol_epoch,
            "base_review_head": base_review_head,
            "written_at": "2026-07-17T00:00:00Z",
        },
    )
    return path


def add_event(repo: Path, lane: str, seq: int, task: str, envelope_commit: str) -> Path:
    envelope_rel = f".ai/lanes/{lane}/events/{seq:03d}.lane-envelope.yml"
    envelope_bytes = git_bytes(repo, envelope_commit, envelope_rel)
    event = {
        "schema_version": "human_ai.communication_event.v1",
        "event_id": f"event-{lane}-{seq}",
        "task_id": task,
        "event_type": "completion_handoff",
        "provider": "Codex",
        "occupied_role": "backend_execution_and_handoff",
        "required_refs": [
            {
                "kind": "git_blob",
                "commit": envelope_commit,
                "path": envelope_rel,
                "content_sha256": hashlib.sha256(envelope_bytes).hexdigest(),
            }
        ],
    }
    path = repo / ".ai" / "lanes" / lane / "events" / f"{seq:03d}.yml"
    write_json(path, event)
    return path


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"], cwd=repo, capture_output=True, check=True
    ).stdout


def reduce(repo: Path, epoch: str, state: Path) -> subprocess.CompletedProcess[str]:
    assert POWERSHELL
    return run(
        POWERSHELL,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
        "-RepositoryRoot",
        str(repo),
        "-LaneRoot",
        str(repo / ".ai" / "lanes"),
        "-StatePath",
        str(state),
        "-CurrentLaneProtocolEpoch",
        epoch,
        cwd=repo,
        check=False,
    )


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_two_same_environment_instances_are_isolated(tmp_path: Path) -> None:
    repo, _base, epoch = new_repo(tmp_path)
    lanes = [f"codex-cli-{uuid.uuid4().hex[:8]}" for _ in range(2)]
    assert lanes[0] != lanes[1]
    for lane in lanes:
        add_envelope(repo, lane, lane, 1, epoch, epoch, environment_class="codex_cli")
    envelope_commit = commit_all(repo, "own envelopes")
    for index, lane in enumerate(lanes):
        add_event(repo, lane, 1, f"task-{index}", envelope_commit)
    event_head = commit_all(repo, "own events")
    state = repo / "STATE.yml"
    own_result = reduce(repo, epoch, state)
    assert own_result.returncode == 0, own_result.stdout + own_result.stderr
    assert len(json.loads(state.read_text(encoding="utf-8"))["lane_inputs"]) == 2

    add_envelope(
        repo,
        lanes[0],
        lanes[1],
        2,
        epoch,
        event_head,
        environment_class="codex_cli",
    )
    cross_envelope_commit = commit_all(repo, "cross envelope")
    add_event(repo, lanes[0], 2, "cross-task", cross_envelope_commit)
    commit_all(repo, "cross event")
    cross_result = reduce(repo, epoch, state)
    assert cross_result.returncode != 0
    assert "cross-lane write rejected" in (cross_result.stdout + cross_result.stderr)


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_two_backend_claims_for_same_task_fail_closed(tmp_path: Path) -> None:
    repo, _base, epoch = new_repo(tmp_path)
    lanes = ["codex-desktop-a1b2c3", "codex-cli-d4e5f6"]
    for lane in lanes:
        add_envelope(repo, lane, lane, 1, epoch, epoch)
    envelope_commit = commit_all(repo, "envelopes")
    for lane in lanes:
        add_event(repo, lane, 1, "shared-task", envelope_commit)
    commit_all(repo, "events")
    result = reduce(repo, epoch, repo / "STATE.yml")
    assert result.returncode != 0
    assert "two backend lanes claimed the same task" in (result.stdout + result.stderr)


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_stale_lane_is_ignored(tmp_path: Path) -> None:
    repo, base, epoch = new_repo(tmp_path)
    stale = "codex-desktop-a1b2c3"
    fresh = "codex-cli-d4e5f6"
    add_envelope(repo, stale, stale, 1, base, base)
    add_envelope(repo, fresh, fresh, 1, epoch, epoch)
    envelope_commit = commit_all(repo, "envelopes")
    add_event(repo, stale, 1, "stale-task", envelope_commit)
    add_event(repo, fresh, 1, "fresh-task", envelope_commit)
    commit_all(repo, "events")
    state = repo / "STATE.yml"
    result = reduce(repo, epoch, state)
    assert result.returncode == 0, result.stdout + result.stderr
    value = json.loads(state.read_text(encoding="utf-8"))
    assert [item["task_id"] for item in value["lane_inputs"]] == ["fresh-task"]


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_canonical_state_inputs_resolve_to_exact_sources(tmp_path: Path) -> None:
    repo, _base, epoch = new_repo(tmp_path)
    lane = "codex-desktop-a1b2c3"
    add_envelope(repo, lane, lane, 1, epoch, epoch)
    envelope_commit = commit_all(repo, "envelope")
    add_event(repo, lane, 1, "trace-task", envelope_commit)
    commit_all(repo, "event")
    state = repo / "STATE.yml"
    result = reduce(repo, epoch, state)
    assert result.returncode == 0, result.stdout + result.stderr
    item = json.loads(state.read_text(encoding="utf-8"))["lane_inputs"][0]
    for key in ("event_ref", "envelope_ref"):
        ref = item[key]
        content = git_bytes(repo, ref["commit"], ref["path"])
        assert hashlib.sha256(content).hexdigest() == ref["content_sha256"]

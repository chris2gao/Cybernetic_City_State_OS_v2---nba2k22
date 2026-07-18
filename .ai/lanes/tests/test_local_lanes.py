import json
import shutil
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


LANE_SCRIPT = Path(__file__).resolve().parents[1] / "lane-local.ps1"
REDUCER = Path(__file__).resolve().parents[1] / "reduce-lanes.ps1"
META_SCHEMA = Path(__file__).resolve().parents[1] / "lane_meta.schema.json"
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def git(repo: Path, *args: str) -> str:
    return run("git", *args, cwd=repo).stdout.strip()


def new_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "local-lane-test@example.invalid")
    git(repo, "config", "user.name", "Local Lane Test")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "--", "seed.txt")
    git(repo, "commit", "-m", "seed")
    return repo, git(repo, "rev-parse", "HEAD")


def lane_command(
    repo: Path, root: Path, epoch: str, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    assert POWERSHELL
    return run(
        POWERSHELL,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(LANE_SCRIPT),
        *args,
        "-RepositoryRoot",
        str(repo),
        "-LocalLaneRoot",
        str(root),
        "-LaneProtocolEpoch",
        epoch,
        "-BaseReviewHead",
        epoch,
        cwd=repo,
        check=check,
    )


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_local_lane_post_read_roundtrip_and_monotonic_sequence(tmp_path: Path) -> None:
    repo, epoch = new_repo(tmp_path)
    root = tmp_path / "local-lanes"
    lane = "codex-desktop-a1b2c3"
    for body in ("first", "second"):
        posted = lane_command(
            repo,
            root,
            epoch,
            "post",
            "-LaneInstanceId",
            lane,
            "-WriterLaneInstanceId",
            lane,
            "-MessageClass",
            "C0",
            "-Body",
            body,
        )
        assert json.loads(posted.stdout)["authoritative"] is False

    read = lane_command(
        repo,
        root,
        epoch,
        "read",
        "-LaneInstanceId",
        lane,
        "-MessageClass",
        "all",
    )
    messages = json.loads(read.stdout)
    assert [item["message_seq"] for item in messages] == [1, 2]
    assert [item["body"] for item in messages] == ["first", "second"]
    assert all(item["authority_boundary"] == "C0_coordination_or_C1_shadow_only" for item in messages)

    meta = json.loads((root / lane / "meta.yml").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(json.loads(META_SCHEMA.read_text(encoding="utf-8"))).iter_errors(meta))
    assert errors == []
    assert meta["transport"] == "local"


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_local_lane_cross_instance_post_is_rejected(tmp_path: Path) -> None:
    repo, epoch = new_repo(tmp_path)
    result = lane_command(
        repo,
        tmp_path / "local-lanes",
        epoch,
        "post",
        "-LaneInstanceId",
        "codex-desktop-a1b2c3",
        "-WriterLaneInstanceId",
        "codex-cli-d4e5f6",
        "-MessageClass",
        "C0",
        check=False,
    )
    assert result.returncode != 0
    assert "cross-lane write rejected" in result.stdout + result.stderr


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_local_transport_is_trace_only_for_canonical_state(tmp_path: Path) -> None:
    repo, epoch = new_repo(tmp_path)
    root = tmp_path / "local-lanes"
    lane = "codex-desktop-a1b2c3"
    lane_command(
        repo,
        root,
        epoch,
        "post",
        "-LaneInstanceId",
        lane,
        "-WriterLaneInstanceId",
        lane,
        "-MessageClass",
        "C1_shadow",
        "-TaskId",
        "shadow-task",
        "-Body",
        "shadow only",
    )
    state = tmp_path / "STATE.yml"
    reduced = run(
        POWERSHELL,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(REDUCER),
        "-RepositoryRoot",
        str(repo),
        "-LaneRoot",
        str(repo / ".ai" / "lanes"),
        "-LocalLaneRoot",
        str(root),
        "-StatePath",
        str(state),
        "-CurrentLaneProtocolEpoch",
        epoch,
        "-Transport",
        "local",
        cwd=repo,
        check=False,
    )
    assert reduced.returncode == 0, reduced.stdout + reduced.stderr
    value = json.loads(state.read_text(encoding="utf-8"))
    assert value["lane_inputs"] == []
    assert len(value["local_lane_traces"]) == 1
    assert value["local_lane_traces"][0]["non_authoritative"] is True
    assert value["local_lane_traces"][0]["message_class"] == "C1_shadow"


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_local_lane_gc_removes_expired_pair_without_reusing_sequence(tmp_path: Path) -> None:
    repo, epoch = new_repo(tmp_path)
    root = tmp_path / "local-lanes"
    lane = "codex-desktop-a1b2c3"
    lane_command(
        repo,
        root,
        epoch,
        "post",
        "-LaneInstanceId",
        lane,
        "-WriterLaneInstanceId",
        lane,
        "-MessageClass",
        "C0",
    )
    event_path = root / lane / "events" / "001.yml"
    event = json.loads(event_path.read_text(encoding="utf-8"))
    event["written_at"] = "2000-01-01T00:00:00Z"
    event_path.write_text(json.dumps(event, indent=2) + "\n", encoding="utf-8")

    collected = lane_command(
        repo,
        root,
        epoch,
        "gc",
        "-LaneInstanceId",
        lane,
        "-WriterLaneInstanceId",
        lane,
        "-RetentionDays",
        "30",
    )
    assert json.loads(collected.stdout)["removed"] == 1
    assert not event_path.exists()
    assert not (root / lane / "events" / "001.lane-envelope.yml").exists()

    second = lane_command(
        repo,
        root,
        epoch,
        "post",
        "-LaneInstanceId",
        lane,
        "-WriterLaneInstanceId",
        lane,
        "-MessageClass",
        "C0",
    )
    assert json.loads(second.stdout)["message_seq"] == 2

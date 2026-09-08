"""Real process/Git probes for the managed route (implementation-team evidence)."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import managed_verify as mv

READER = "01_os/06_execution/task_discipline/packet_input/task_packet_input.py"
ROOT = Path(__file__).resolve().parents[4]


def command(code="pass", name="check", expected=0, timeout=10):
    return {"id": name, "argv": ["@python", "-B", "-c", code],
            "expected_exit_code": expected, "timeout_seconds": timeout}


def git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=True)
    return result.stdout.decode().strip()


@pytest.fixture
def build(tmp_path):
    def create(checks=None, plan_mutation=None, packet_mutation=None):
        repo = tmp_path / "source"
        repo.mkdir()
        git(repo, "init", "-b", "fixture")
        git(repo, "config", "user.name", "Fixture")
        git(repo, "config", "user.email", "fixture@example.invalid")
        git(repo, "config", "core.autocrlf", "false")
        git(repo, "config", "core.hooksPath", ".disabled-fixture-hooks")
        (repo / "source.txt").write_text("original\n", encoding="utf-8")
        git(repo, "add", "--", "source.txt")
        git(repo, "commit", "-qm", "base")
        base = git(repo, "rev-parse", "HEAD")
        for path in (mv.RUNNER, READER):
            (repo / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, repo / path)
        plan = {"schema_version": mv.PLAN_VERSION, "task_packet": "packet.yml", "checks": checks or [command()]}
        packet = {"task_id": "fixture", "branch": "fixture", "exact_base_sha": base,
                  "allowed_changed_paths": [mv.RUNNER, READER, "packet.yml", "plan.json"],
                  "required_tests": [c["id"] for c in plan["checks"]], "prohibitions": [],
                  "verification_plan": "plan.json"}
        if plan_mutation:
            plan_mutation(plan)
        if packet_mutation:
            packet_mutation(packet)
        (repo / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
        (repo / "packet.yml").write_text(yaml.safe_dump({"task_packet": packet}), encoding="utf-8")
        git(repo, "add", "--", mv.RUNNER, READER, "packet.yml", "plan.json")
        git(repo, "commit", "-qm", "candidate")
        return repo, git(repo, "rev-parse", "HEAD"), tmp_path / "attempt"
    return create


def invoke(repo, head, attempt, action="run"):
    proc = subprocess.run([sys.executable, "-B", str(repo / mv.RUNNER), action,
                           "--repo-root", str(repo), "--candidate", head,
                           "--plan", "plan.json", "--attempt", str(attempt)],
                          cwd=repo, capture_output=True, timeout=60,
                          env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    assert not proc.stderr, proc.stderr.decode("utf-8", "replace")
    return proc.returncode, json.loads(proc.stdout)


def record(attempt, filename):
    return json.loads((attempt / filename).read_text(encoding="utf-8"))


def modify_record(attempt, filename, change):
    data = record(attempt, filename)
    change(data)
    (attempt / filename).write_text(json.dumps(data), encoding="utf-8")


def test_success_retains_exact_large_binary_logs_and_replays(build):
    code = "import os; os.write(1, b'A'*200000+b'\\x00\\xffEND'); os.write(2, b'ERR\\x00\\xfe')"
    repo, head, attempt = build([command(code)])
    assert invoke(repo, head, attempt)[0] == 0
    assert (attempt / "001.stdout.bin").read_bytes() == b"A" * 200000 + b"\0\xffEND"
    assert (attempt / "001.stderr.bin").read_bytes() == b"ERR\0\xfe"
    assert invoke(repo, head, attempt, "inspect")[0] == 0
    assert git(repo, "status", "--porcelain", "-uall") == ""


def test_expected_nonzero_is_actual_execution(build):
    repo, head, attempt = build([command("raise SystemExit(7)", expected=7)])
    assert invoke(repo, head, attempt)[0] == 0
    assert record(attempt, "001.finished.json")["exit_code"] == 7


def test_failure_stops_remaining_checks_and_cannot_forge_summary(build):
    repo, head, attempt = build([command("raise SystemExit(2)"), command(name="later")])
    code, result = invoke(repo, head, attempt)
    assert code == 1
    assert [r["status"] for r in result["checks"]] == ["failure", "not_run"]
    assert not (attempt / "002.started.json").exists()
    modify_record(attempt, "result.json", lambda d: d.update(status="success"))
    assert invoke(repo, head, attempt, "inspect")[0] == 3


def test_timeout_is_error_even_if_process_is_killed(build):
    repo, head, attempt = build([command("import time; time.sleep(30)", timeout=1), command(name="later")])
    code, result = invoke(repo, head, attempt)
    assert code == 3 and result["status"] == "error"
    assert record(attempt, "001.finished.json")["error"] == "timeout"
    assert result["checks"][1]["status"] == "not_run"


def test_missing_executable_is_not_success(build):
    check = command()
    check["argv"] = ["missing-citystate-executable-091a"]
    repo, head, attempt = build([check])
    assert invoke(repo, head, attempt)[0] == 3
    assert record(attempt, "001.finished.json")["exit_code"] is None


@pytest.mark.parametrize("damage", ["001.stdout.bin", "001.stderr.bin", "001.started.json", "001.finished.json", "001.source.json", "result.json"])
def test_missing_execution_evidence_never_passes(build, damage):
    repo, head, attempt = build()
    assert invoke(repo, head, attempt)[0] == 0
    (attempt / damage).unlink()
    assert invoke(repo, head, attempt, "inspect")[0] == 3


def test_tampered_log_and_unknown_file_are_rejected(build):
    repo, head, attempt = build()
    assert invoke(repo, head, attempt)[0] == 0
    (attempt / "001.stdout.bin").write_bytes(b"forged")
    assert invoke(repo, head, attempt, "inspect")[0] == 3


def test_attempt_cannot_be_overwritten(build):
    repo, head, attempt = build()
    assert invoke(repo, head, attempt)[0] == 0
    original = (attempt / "result.json").read_bytes()
    assert invoke(repo, head, attempt)[0] == 3
    assert (attempt / "result.json").read_bytes() == original
    assert invoke(repo, head, attempt.with_name("attempt2"))[0] == 0


def test_dirty_source_rejected_before_attempt(build):
    repo, head, attempt = build()
    (repo / "source.txt").write_text("changed")
    assert invoke(repo, head, attempt)[0] == 3
    assert not attempt.exists()


def test_source_mutation_after_check_cannot_pass(build):
    repo, head, attempt = build([command("from pathlib import Path; Path('source.txt').write_text('changed')")])
    code, result = invoke(repo, head, attempt)
    assert code == 3 and result["status"] == "error"
    assert record(attempt, "source_after.json")["error"] == "source_not_clean"


def test_stale_or_symbolic_candidate_rejected(build):
    repo, head, attempt = build()
    assert invoke(repo, "HEAD", attempt)[0] == 3
    assert invoke(repo, "f" * 40, attempt)[0] == 3
    assert not attempt.exists()


def test_required_check_omission_is_admission_error(build):
    repo, head, attempt = build(packet_mutation=lambda d: d["required_tests"].append("omitted"))
    assert invoke(repo, head, attempt)[0] == 3
    assert not attempt.exists()


def test_scope_escape_in_candidate_is_admission_error(build):
    repo, head, attempt = build(packet_mutation=lambda d: d.update(allowed_changed_paths=["plan.json"]))
    assert invoke(repo, head, attempt)[0] == 3


@pytest.mark.parametrize("value", [False, 0, "", {}, None, []])
def test_falsey_check_collection_is_invalid(value):
    with pytest.raises(mv.VerificationError):
        mv.validate_plan({"schema_version": mv.PLAN_VERSION, "task_packet": "packet.yml", "checks": value})


@pytest.mark.parametrize("field,value", [("argv", "python"), ("argv", [True]), ("timeout_seconds", True),
                                        ("timeout_seconds", 0), ("expected_exit_code", False), ("id", ""), ("skip", True)])
def test_invalid_check_fields(field, value):
    row = command()
    row[field] = value
    with pytest.raises(mv.VerificationError):
        mv.validate_plan({"schema_version": mv.PLAN_VERSION, "task_packet": "packet.yml", "checks": [row]})


@pytest.mark.parametrize("raw", [b'{"checks":[],"checks":[]}', b'{"a":NaN}', b'{"a":Infinity}', b'{"a":"\xff"}'])
def test_duplicate_nonfinite_or_invalid_utf8_json(raw):
    with pytest.raises(mv.VerificationError):
        mv.decode_json(raw)


def test_duplicate_check_ids_rejected():
    with pytest.raises(mv.VerificationError):
        mv.validate_plan({"schema_version": mv.PLAN_VERSION, "task_packet": "packet.yml", "checks": [command(), command()]})


def test_source_change_stops_next_check_not_just_final_verdict(build, tmp_path):
    marker = tmp_path / "should_not_run.txt"
    checks = [command("from pathlib import Path; Path('source.txt').write_text('changed')"),
              command(f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')", name="later")]
    repo, head, attempt = build(checks)
    code, result = invoke(repo, head, attempt)
    assert code == 3
    assert not marker.exists()
    assert result["checks"][1]["status"] == "not_run"


@pytest.mark.parametrize("filename", ["input.json", "source_after.json"])
def test_integer_is_not_source_clean_boolean(build, filename):
    repo, head, attempt = build()
    assert invoke(repo, head, attempt)[0] == 0
    key = "source_before" if filename == "input.json" else "state"
    modify_record(attempt, filename, lambda d: d[key].update(clean=1))
    assert invoke(repo, head, attempt, "inspect")[0] == 3


def test_copied_plan_boolean_is_not_expected_exit_integer(build):
    repo, head, attempt = build()
    assert invoke(repo, head, attempt)[0] == 0
    modify_record(attempt, "input.json", lambda d: d["plan"]["checks"][0].update(expected_exit_code=False))
    assert invoke(repo, head, attempt, "inspect")[0] == 3


def test_json_exponent_overflow_is_rejected():
    with pytest.raises(mv.VerificationError):
        mv.decode_json(b'{"elapsed_seconds":1e999}')


def test_ignored_index_flags_fail_closed(build):
    repo, head, attempt = build()
    git(repo, "update-index", "--assume-unchanged", "source.txt")
    (repo / "source.txt").write_text("hidden change", encoding="utf-8")
    assert invoke(repo, head, attempt)[0] == 3
    assert not attempt.exists()


def test_adversarial_status_config_does_not_hide_untracked_file(build):
    repo, head, attempt = build()
    git(repo, "config", "core.untrackedCache", "true")
    git(repo, "config", "status.showUntrackedFiles", "no")
    git(repo, "status", "--porcelain")
    (repo / "new.txt").write_text("untracked", encoding="utf-8")
    assert invoke(repo, head, attempt)[0] == 3
    assert not attempt.exists()

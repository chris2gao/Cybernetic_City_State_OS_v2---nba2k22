"""Separate OS-process recovery evidence; not a GPT/Codex UI-window test."""
import json
from pathlib import Path
import subprocess
import sys

PRMS = Path(__file__).resolve().parents[1]


def test_separate_process_preserves_role_and_exact_human_decision(tmp_path):
    state = tmp_path / "role-state.git"
    counter = 0
    def call(command, *extra, payload=None):
        nonlocal counter
        counter += 1
        output = tmp_path / f"reply-{counter}.json"
        args = [sys.executable, "-B", str(PRMS / "state_cli.py"), command,
                "--state-root", str(state), "--isolated-test-only", "--output", str(output), *extra]
        if payload is not None:
            source = tmp_path / f"input-{counter}.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            args += ["--payload", str(source)]
        result = subprocess.run(args, capture_output=True)
        assert result.returncode == 0, result.stdout.decode("utf-8", "replace")
        return json.loads(output.read_text(encoding="utf-8"))
    reply = call("init-sandbox", "--sandbox-parent", str(tmp_path))
    reply = call("register", "--session", "window-A", "--role", "engineer", "--operation-id", "register",
                 "--expected-head", reply["head"], "--expected-version", "0", "--expected-epoch", "0",
                 payload={"definition": {"role_type_id": "engineer", "version": "1"},
                          "domain_id": "core", "state_repository_id": "fixture-state"})
    reply = call("append", "--session", "window-A", "--role", "engineer", "--operation-id", "decision-op",
                 "--expected-head", reply["authoritative_commit_sha"], "--expected-version", "1", "--expected-epoch", "1",
                 payload={"event_id": "human-decision", "kind": "HUMAN_DECISION", "text": "Q52=B; optional scope is this session only",
                          "task_id": "PRMS", "source_refs": [{"repository": "fixture/source", "commit": "a" * 40, "path": "approval.md"}]})
    reply = call("checkpoint", "--session", "window-A", "--role", "engineer", "--operation-id", "checkpoint",
                 "--expected-head", reply["authoritative_commit_sha"], "--expected-version", "2", "--expected-epoch", "1",
                 payload={"milestone": "D0-complete", "open_items": ["independent platform test"]})
    # Every call above and below starts a new Python process; no module memory survives.
    recovered = call("recover", "--role", "engineer")
    assert recovered["identity"]["role_id"] == "engineer"
    assert recovered["events"][0]["text"] == "Q52=B; optional scope is this session only"
    assert recovered["checkpoint"]["state"]["milestone"] == "D0-complete"
    assert recovered["events"][0]["source_refs"][0]["commit"] == "a" * 40
    assert recovered["unsaved_chat"] == "NOT_OBSERVABLE"
    assert recovered["action_authorized"] is False


def test_cli_refuses_production_self_claim_without_host(tmp_path):
    proc = subprocess.run([sys.executable, "-B", str(PRMS / "state_cli.py"), "claim",
                           "--state-root", str(tmp_path / "absent"), "--output", str(tmp_path / "out.json")],
                          capture_output=True)
    assert proc.returncode == 2
    assert "FENCING_NOT_ENFORCEABLE" in proc.stdout.decode()
    assert not (tmp_path / "absent").exists()

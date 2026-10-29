from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import threading

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import PRMSError, canonical
from state import LocalGitState, WriterGate


@pytest.fixture
def setup(tmp_path):
    store = LocalGitState.initialize_isolated(tmp_path / "state.git", sandbox_parent=tmp_path)
    gate = WriterGate(store)
    first = gate.open_isolated_session("first", ["engineer"])
    second = gate.open_isolated_session("second", ["engineer"])
    gate.apply(first, "engineer", operation_id="register", expected_head=store.head(),
               expected_version=0, expected_epoch=0, kind="REGISTER",
               payload={"definition": {"role_type_id": "engineer", "version": "1"},
                        "domain_id": "core", "state_repository_id": "isolated-state"})
    return store, gate, first, second


def apply(store, gate, session, op, kind, payload, **extra):
    recovery = gate.recover("engineer")
    current = recovery["current"]
    return gate.apply(session, "engineer", operation_id=op, expected_head=store.head(),
                      expected_version=current["state_version"], expected_epoch=current["owner_epoch"],
                      kind=kind, payload=payload, **extra)


def test_durable_events_checkpoint_and_real_git_readback(setup):
    store, gate, first, _ = setup
    event = {"event_id": "decision1", "kind": "HUMAN_DECISION", "text": "approved design B",
             "source_refs": [{"repository": "fixture", "commit": "a" * 40, "path": "decision.md"}]}
    reply = apply(store, gate, first, "append1", "APPEND", event)
    assert store.head() == reply["authoritative_commit_sha"]
    apply(store, gate, first, "checkpoint1", "CHECKPOINT", {"open_items": ["build writer gate"]})
    restored = WriterGate(LocalGitState(store.root)).recover("engineer")
    assert len(restored["events"]) == 1
    assert all(restored["events"][0][key] == value for key, value in event.items())
    assert restored["events"][0]["schema_version"] == "prms.event.v1"
    assert restored["events"][0]["observed_at"] == "UNKNOWN"
    assert restored["checkpoint"]["state"]["open_items"] == ["build writer gate"]
    assert restored["current"]["checkpoint"] == "checkpoint1"
    assert restored["fencing_mode"] == "COOPERATIVE_FENCING"


def test_takeover_and_untrusted_caller_fail_closed(setup):
    store, gate, first, second = setup
    apply(store, gate, second, "claim", "CLAIM", {})
    with pytest.raises(PRMSError, match="STALE_OWNER"):
        apply(store, gate, first, "old-write", "CHECKPOINT", {})
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        apply(store, gate, "first", "self-asserted", "CHECKPOINT", {})
    with pytest.raises(PRMSError, match="FENCING_NOT_ENFORCEABLE"):
        gate.require_enforced()


def test_same_operation_retry_and_changed_payload_conflict(setup):
    store, gate, first, _ = setup
    original_head = store.head()
    kwargs = dict(operation_id="cp", expected_head=original_head, expected_version=1,
                  expected_epoch=1, kind="CHECKPOINT", payload={"milestone": "D0"})
    first_result = gate.apply(first, "engineer", **kwargs)
    retry = gate.apply(first, "engineer", **kwargs)
    assert retry["status"] == "ALREADY_APPLIED"
    assert store.head() == first_result["authoritative_commit_sha"]
    kwargs["payload"] = {"milestone": "forged"}
    with pytest.raises(PRMSError, match="VERSION_CONFLICT"):
        gate.apply(first, "engineer", **kwargs)


def test_interrupted_candidate_does_not_change_current(setup):
    store, gate, first, _ = setup
    before_head, before = store.head(), store.snapshot()
    def fail(_):
        raise OSError("injected interruption before authoritative ref update")
    with pytest.raises(OSError):
        apply(store, gate, first, "interrupted", "CHECKPOINT", {}, before_publish=fail)
    assert store.head() == before_head and store.snapshot() == before


def test_real_git_two_competing_children_only_one_current(setup):
    store, gate, first, _ = setup
    head = store.head()
    rendezvous = threading.Barrier(2)
    def worker(number):
        try:
            return gate.apply(first, "engineer", operation_id=f"competing-{number}",
                              expected_head=head, expected_version=1, expected_epoch=1,
                              kind="CHECKPOINT", payload={"winner": number},
                              before_publish=lambda _: rendezvous.wait(timeout=20))["status"]
        except PRMSError as exc:
            return exc.status
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(worker, [1, 2]))
    assert sorted(results) == ["PUBLISHED", "VERSION_CONFLICT"]
    snapshot = store.snapshot()
    assert len([p for p in snapshot if p.startswith("roles/engineer/checkpoints/")]) == 1


def test_same_principal_git_bypass_is_observable_and_never_called_enforced(setup):
    store, gate, first, _ = setup
    # This deliberately demonstrates the local trust limitation, rather than
    # turning a client-side owner check into fictitious platform enforcement.
    store.commit(store.head(), {"roles/engineer/CURRENT.json": canonical({"bypass": True})}, "direct-writer")
    assert json.loads(store.snapshot()["roles/engineer/CURRENT.json"])["bypass"] is True
    with pytest.raises(PRMSError, match="FENCING_NOT_ENFORCEABLE"):
        gate.require_enforced()


def test_revoked_and_duplicate_host_sessions_are_rejected(setup):
    store, gate, first, _ = setup
    with pytest.raises(PRMSError, match="REJECTED"):
        gate.open_isolated_session("first", ["engineer"])
    gate.revoke_isolated_session(first)
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        apply(store, gate, first, "revoked-write", "CHECKPOINT", {})


def test_source_contract_and_correction_preserve_history(setup):
    store, gate, first, _ = setup
    before = store.head()
    with pytest.raises(PRMSError, match="SOURCE_MISSING"):
        apply(store, gate, first, "invalid-event", "APPEND", {"event_id": "bad", "kind": "OBSERVATION",
                                                              "source_refs": [{"path": "unversioned"}]})
    assert store.head() == before
    source = [{"repository": "fixture/source", "path": "evidence.md", "commit": "a" * 40}]
    apply(store, gate, first, "record-original", "APPEND", {"event_id": "old", "kind": "OBSERVATION",
            "source_refs": source, "text": "original claim"})
    raw_before = store.snapshot()["roles/engineer/events/old.json"]
    apply(store, gate, first, "record-correction", "APPEND", {"event_id": "correction", "kind": "CORRECTION",
            "source_refs": source, "text": "corrected claim", "corrects_event_id": "old"})
    assert store.snapshot()["roles/engineer/events/old.json"] == raw_before
    assert len(gate.recover("engineer")["events"]) == 2


def test_recording_assignment_does_not_expand_host_task_authority(setup):
    store, gate, _, _ = setup
    scoped = gate.open_isolated_session("task-scoped", ["engineer"], allowed_tasks=["approved-task"],
                                        allowed_operations=["CLAIM", "ASSIGN", "CHECKPOINT"])
    apply(store, gate, scoped, "scoped-claim", "CLAIM", {})
    before = store.head()
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        apply(store, gate, scoped, "unapproved-task", "ASSIGN", {"assignment_id": "fake",
                "task_id": "other-task", "human_authority_ref": "self-claimed approved"})
    assert store.head() == before
    apply(store, gate, scoped, "approved-assignment", "ASSIGN", {"assignment_id": "assigned",
          "task_id": "approved-task", "human_authority_ref": "fixture Human task record"})
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        apply(store, gate, scoped, "self-grant", "UPGRADE_DEFINITION", {"version": "2", "compatibility_ref": "asserted"})


def test_test_session_issuer_cannot_authorize_remote_backend():
    class RemoteBackend:
        fencing_mode = "FENCING_NOT_ENFORCEABLE"
    gate = WriterGate(RemoteBackend())
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        gate.open_isolated_session("self-asserted", ["engineer"])


def test_definition_upgrade_preserves_stable_role_and_prior_template(setup):
    store, gate, caller, _ = setup
    frozen = store.head()
    original = store.snapshot(frozen)["roles/engineer/definitions/1.json"]
    for payload in ({"version": "2", "compatibility_ref": "fixture"},
                    {"version": "2", "role_type_id": "other-role", "compatibility_ref": "fixture"}):
        with pytest.raises(PRMSError, match="REJECTED"):
            apply(store, gate, caller, "invalid-upgrade", "UPGRADE_DEFINITION", payload)
        assert store.head() == frozen
    apply(store, gate, caller, "upgrade", "UPGRADE_DEFINITION",
          {"version": "2", "role_type_id": "engineer", "compatibility_ref": "fixture compatible template"})
    restored = gate.recover("engineer")
    assert restored["role_id"] == "engineer" and restored["identity"]["definition"]["version"] == "2"
    assert store.snapshot()["roles/engineer/definitions/1.json"] == original

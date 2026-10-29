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
    assert restored["events"] == [event]
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

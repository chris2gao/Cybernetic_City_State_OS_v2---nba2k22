"""Fault injection of the Git Database protocol, never GitHub permission proof."""
import base64
import hashlib
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from github_state import GitHubGitState
from source import PRMSError


class ProtocolFixture:
    def __init__(self, fault=None):
        self.head = "a" * 40
        self.candidate = "c" * 40
        self.calls = []
        self.blobs = {}
        self.entries = []
        self.fault = fault

    def __call__(self, method, path, payload):
        path = path.removeprefix("repos/fixture/private-state/")
        self.calls.append((method, path, payload))
        if path.startswith("git/ref/"):
            return {"object": {"sha": self.head}}
        if path.startswith("git/commits/"):
            return {"tree": {"sha": "b" * 40}}
        if method == "POST" and path == "git/blobs":
            if self.fault == "prepare":
                raise TimeoutError("blob upload interrupted")
            raw = base64.b64decode(payload["content"])
            sha = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
            self.blobs[sha] = payload["content"]
            return {"sha": sha}
        if method == "POST" and path == "git/trees":
            self.entries = payload["tree"]
            return {"sha": "d" * 40}
        if method == "POST" and path == "git/commits":
            assert payload["parents"] == ["a" * 40]
            return {"sha": self.candidate}
        if method == "PATCH":
            assert payload == {"sha": self.candidate, "force": False}
            if self.fault != "timeout_before":
                self.head = "e" * 40 if self.fault == "same_bytes_other_writer" else self.candidate
            if self.fault:
                raise TimeoutError("PATCH result unknown")
            return {"object": {"sha": self.head}}
        if path.startswith("compare/"):
            return {"status": "diverged"}
        if path.startswith("git/trees/"):
            return {"tree": [dict(x, type="blob") for x in self.entries], "truncated": False}
        if path.startswith("git/blobs/"):
            return {"content": self.blobs[path.rsplit("/", 1)[1]]}
        raise AssertionError((method, path))


def adapter(transport, enabled=True):
    return GitHubGitState(transport, repository="fixture/private-state", ref="refs/heads/role",
                          allowed_state_repository="fixture/private-state", write_enabled=enabled)


def test_default_dormant_adapter_performs_no_write():
    transport = ProtocolFixture()
    with pytest.raises(PRMSError, match="FENCING_NOT_ENFORCEABLE"):
        adapter(transport, False).commit("a" * 40, {"roles/r/CURRENT.json": b"{}"}, "operation")
    assert transport.calls == []


def test_atomic_prepare_then_single_nonforce_publish():
    transport = ProtocolFixture()
    reply = adapter(transport).commit("a" * 40, {"roles/r/CURRENT.json": b"{}"}, "operation")
    assert reply["status"] == "PUBLISHED"
    assert reply["authoritative_commit_sha"] == transport.candidate
    writes = [(method, path) for method, path, _ in transport.calls if method != "GET"]
    assert writes == [("POST", "git/blobs"), ("POST", "git/trees"), ("POST", "git/commits"),
                      ("PATCH", "git/refs/heads/role")]
    assert reply["fencing_mode"] == "FENCING_NOT_ENFORCEABLE"


def test_prepare_failure_never_touches_ref():
    transport = ProtocolFixture("prepare")
    with pytest.raises(TimeoutError):
        adapter(transport).commit("a" * 40, {"roles/r/CURRENT.json": b"{}"}, "operation")
    assert transport.head == "a" * 40
    assert not any(method == "PATCH" for method, _, _ in transport.calls)


@pytest.mark.parametrize("fault,expected", [("timeout_after", "PUBLISHED_READBACK_AFTER_UNKNOWN"),
    ("timeout_before", "PUBLISH_NOT_CONFIRMED"), ("same_bytes_other_writer", "PUBLISH_NOT_CONFIRMED")])
def test_unknown_publish_result_uses_readback_and_never_replays(fault, expected):
    transport = ProtocolFixture(fault)
    store = adapter(transport)
    if expected == "PUBLISH_NOT_CONFIRMED":
        with pytest.raises(PRMSError, match=expected):
            store.commit("a" * 40, {"roles/r/CURRENT.json": b"{}"}, "operation")
    else:
        reply = store.commit("a" * 40, {"roles/r/CURRENT.json": b"{}"}, "operation")
        assert reply["status"] == expected and reply["retry_safety"] == "DO_NOT_REPLAY"
    assert sum(method == "PATCH" for method, _, _ in transport.calls) == 1


def test_readback_rejects_blob_response_inconsistent_with_tree():
    transport = ProtocolFixture()
    store = adapter(transport)
    store.commit("a" * 40, {"roles/r/CURRENT.json": b"{}"}, "operation")
    transport.blobs[next(iter(transport.blobs))] = base64.b64encode(b"forged").decode()
    with pytest.raises(PRMSError, match="SUMMARY_STALE"):
        store.snapshot()

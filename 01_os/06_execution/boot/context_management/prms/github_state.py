"""GitHub Git Database protocol adapter; dormant until separately authorized.

The transport is injected by the trusted host, owns authentication and must not
expose credentials to callers. This adapter provides atomic-tree publication,
not session authentication or GitHub branch-rule enforcement. Those remain an
explicit deployment gate. No repository is created by this module.
"""
from __future__ import annotations

import base64
import json
import re

from source import PRMSError, digest, safe_path
from state import identifier


class GitHubGitState:
    fencing_mode = "FENCING_NOT_ENFORCEABLE"

    def __init__(self, transport, *, repository, ref, allowed_state_repository, write_enabled=False):
        if repository != allowed_state_repository:
            raise PRMSError("AUTHORITY_UNVERIFIED", "state repository not authorized by host")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise PRMSError("REJECTED", "invalid state repository")
        if repository.split("/")[1].startswith("Cybernetic_City_State_OS_v2---"):
            raise PRMSError("REJECTED", "role state must not live in Core or domain code repository")
        if not ref.startswith("refs/heads/") or ".." in ref or not re.fullmatch(r"refs/heads/[A-Za-z0-9][A-Za-z0-9_/-]*", ref):
            raise PRMSError("REJECTED", "invalid state ref")
        self.transport, self.repository, self.ref = transport, repository, ref
        self.write_enabled = write_enabled

    def api(self, method, path, payload=None):
        return self.transport(method, f"repos/{self.repository}/{path}", payload)

    def head(self):
        return self.api("GET", "git/ref/" + self.ref.removeprefix("refs/"))["object"]["sha"]

    def snapshot(self, head=None):
        head = head or self.head()
        if not re.fullmatch(r"[0-9a-f]{40}", head):
            raise PRMSError("REJECTED", "exact state commit required")
        tree = self.api("GET", f"git/trees/{head}?recursive=1")
        if tree.get("truncated"):
            raise PRMSError("SOURCE_MISSING", "state inventory truncated")
        result = {}
        for item in tree["tree"]:
            if item["type"] != "blob":
                continue
            safe_path(item["path"])
            if item["mode"] != "100644":
                raise PRMSError("REJECTED", "unexpected state file mode")
            result[item["path"]] = base64.b64decode(self.api("GET", "git/blobs/" + item["sha"])["content"])
        return result

    def commit(self, expected_head, changes, operation_id, *, before_publish=None):
        identifier(operation_id)
        if not self.write_enabled:
            raise PRMSError("FENCING_NOT_ENFORCEABLE", "state write deployment not authorized/verified")
        if not re.fullmatch(r"[0-9a-f]{40}", expected_head or ""):
            raise PRMSError("REJECTED", "existing exact state parent required")
        if self.head() != expected_head:
            raise PRMSError("VERSION_CONFLICT", "state ref changed before prepare")
        parent = self.api("GET", "git/commits/" + expected_head)
        entries = []
        for path, raw in sorted(changes.items()):
            safe_path(path)
            blob = self.api("POST", "git/blobs", {"content": base64.b64encode(raw).decode(), "encoding": "base64"})
            entries.append({"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        tree = self.api("POST", "git/trees", {"base_tree": parent["tree"]["sha"], "tree": entries})
        candidate = self.api("POST", "git/commits", {"tree": tree["sha"], "parents": [expected_head],
                              "message": f"PRMS operation {operation_id}"})["sha"]
        if before_publish:
            before_publish(candidate)
        try:
            self.api("PATCH", "git/refs/" + self.ref.removeprefix("refs/"), {"sha": candidate, "force": False})
        except Exception as exc:
            # Query the attempted commit's actual operation record; never retry PATCH blindly.
            try:
                current = self.head()
                observed = self.snapshot(current)
                if all(observed.get(p) == raw for p, raw in changes.items()):
                    return {"status": "PUBLISHED_READBACK_AFTER_UNKNOWN", "authoritative_commit_sha": current,
                            "candidate_commit_sha": candidate, "operation_id": operation_id,
                            "retry_safety": "DO_NOT_REPLAY"}
            except Exception:
                pass
            raise PRMSError("PUBLISH_NOT_CONFIRMED", f"uncertain ref result for operation {operation_id}") from exc
        observed = self.snapshot(self.head())
        if any(observed.get(p) != raw for p, raw in changes.items()):
            raise PRMSError("PUBLISH_NOT_CONFIRMED", "content differs from accepted candidate")
        return {"status": "PUBLISHED", "authoritative_commit_sha": candidate,
                "readback_head": self.head(), "operation_id": operation_id,
                "retry_safety": "READ_OPERATION_BEFORE_RETRY", "fencing_mode": self.fencing_mode}

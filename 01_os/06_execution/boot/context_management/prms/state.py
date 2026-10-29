"""Isolated Git state protocol. No production repository creation or service startup.

Local filesystem access is cooperative fencing, never a credential boundary.
Only a separately verified host adapter may provide enforced production access.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from source import PRMSError, canonical, digest, safe_path
from contracts import normalize_event, positive_version, require_mapping, validate_current


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", value):
        raise PRMSError("REJECTED", "invalid stable identifier")
    return value


class LocalGitState:
    """One authoritative ref; Git update-ref checks actual expected parent atomically."""
    fencing_mode = "COOPERATIVE_FENCING"

    def __init__(self, root, ref="refs/heads/prms-state"):
        self.root = Path(root).resolve()
        if not re.fullmatch(r"refs/heads/[A-Za-z0-9][A-Za-z0-9_/-]*", ref):
            raise PRMSError("REJECTED", "invalid state ref")
        self.ref = ref
        if not self.root.exists():
            raise PRMSError("SOURCE_MISSING", "state repo must be explicitly initialized")
        self.git("rev-parse", "--git-dir")

    @classmethod
    def initialize_isolated(cls, root, *, sandbox_parent):
        root, parent = Path(root).resolve(), Path(sandbox_parent).resolve()
        if root == parent or not root.is_relative_to(parent) or root.exists():
            raise PRMSError("REJECTED", "new isolated path under explicit sandbox required")
        root.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(["git", "init", "--bare", str(root)], capture_output=True)
        if result.returncode:
            raise PRMSError("REJECTED", "sandbox git init failed")
        store = cls(root)
        store.commit(None, {"protocol.json": canonical({"schema_version": "prms.state.v1",
                          "fencing": cls.fencing_mode, "scope": "ISOLATED_TEST_ONLY"})}, "initialize")
        return store

    def git(self, *args, data=None, env=None, check=True):
        result = subprocess.run(["git", *args], cwd=self.root, input=data,
                                capture_output=True, env=env)
        if check and result.returncode:
            raise PRMSError("REJECTED", result.stderr.decode("utf-8", "replace")[:160])
        return result

    def head(self):
        value = self.git("rev-parse", "--verify", self.ref, check=False)
        return value.stdout.decode().strip() if value.returncode == 0 else None

    def snapshot(self, head=None):
        head = head or self.head()
        if head is None:
            return {}
        if not re.fullmatch(r"[0-9a-f]{40}", head):
            raise PRMSError("REJECTED", "immutable state commit required")
        result = {}
        for row in self.git("ls-tree", "-r", "-z", head).stdout.split(b"\0"):
            if not row:
                continue
            meta, raw_path = row.split(b"\t", 1)
            path = raw_path.decode("utf-8")
            mode, kind, blob = meta.decode().split()
            safe_path(path)
            if mode != "100644" or kind != "blob":
                raise PRMSError("REJECTED", "state contains unsupported object mode")
            result[path] = self.git("cat-file", "blob", blob).stdout
        return result

    def parents(self, head):
        if not re.fullmatch(r"[0-9a-f]{40}", head):
            raise PRMSError("REJECTED", "immutable audit commit required")
        return self.git("show", "-s", "--format=%P", head).stdout.decode().split()

    def commit(self, expected_head, changes, operation_id, *, before_publish=None):
        """Build complete candidate then CAS. Failure cannot expose a partial CURRENT."""
        identifier(operation_id)
        if expected_head is not None and not re.fullmatch(r"[0-9a-f]{40}", expected_head):
            raise PRMSError("REJECTED", "exact expected state commit required")
        for path, data in changes.items():
            safe_path(path)
            if not isinstance(data, bytes):
                raise PRMSError("REJECTED", "state encoding must be bytes")
        with tempfile.TemporaryDirectory(prefix="prms-index-") as temp:
            env = dict(os.environ)
            env.update(GIT_INDEX_FILE=str(Path(temp) / "index"),
                       GIT_AUTHOR_NAME="PRMS isolated publisher", GIT_AUTHOR_EMAIL="prms@example.invalid",
                       GIT_COMMITTER_NAME="PRMS isolated publisher", GIT_COMMITTER_EMAIL="prms@example.invalid")
            if expected_head:
                self.git("read-tree", expected_head, env=env)
            else:
                self.git("read-tree", "--empty", env=env)
            records = []
            for path, data in sorted(changes.items()):
                blob = self.git("hash-object", "-w", "--stdin", data=data).stdout.decode().strip()
                records.append(f"100644 {blob}\t{path}".encode() + b"\0")
            self.git("update-index", "-z", "--index-info", data=b"".join(records), env=env)
            tree = self.git("write-tree", env=env).stdout.decode().strip()
            args = ["commit-tree", tree]
            if expected_head:
                args += ["-p", expected_head]
            candidate = self.git(*args, data=f"PRMS {operation_id}\n".encode(), env=env).stdout.decode().strip()
            if before_publish:
                before_publish(candidate)
            cas = self.git("update-ref", self.ref, candidate, expected_head or "0" * 40, check=False)
            if cas.returncode:
                raise PRMSError("VERSION_CONFLICT", "authoritative ref moved; re-read owner and state")
            actual = self.head()
            if actual != candidate:
                # A later valid publication may already have advanced the ref.
                ancestor = self.git("merge-base", "--is-ancestor", candidate, actual, check=False)
                if ancestor.returncode:
                    raise PRMSError("PUBLISH_NOT_CONFIRMED", "publication absent from readback")
            actual_tree = self.snapshot(candidate)
            if any(actual_tree.get(p) != data for p, data in changes.items()):
                raise PRMSError("PUBLISH_NOT_CONFIRMED", "state content readback mismatch")
            return {"status": "PUBLISHED", "authoritative_commit_sha": candidate,
                    "readback_head": actual, "operation_id": operation_id,
                    "retry_safety": "READ_OPERATION_BEFORE_RETRY", "fencing_mode": self.fencing_mode}


class WriterGate:
    """Trusted host integration surface; local mode cannot assert forced revocation."""
    def __init__(self, store):
        self.store = store
        self._sessions = {}
        self._issued_session_ids = set()
        self._task_scopes = {}
        self._operation_scopes = {}
        self._copy_scopes = {}

    def require_enforced(self):
        # No caller-supplied flag can manufacture remote permission evidence.
        raise PRMSError("FENCING_NOT_ENFORCEABLE", "local Git permits same-principal direct writes")

    def open_isolated_session(self, session_id, allowed_roles, *, allowed_tasks=None, allowed_operations=None,
                              allowed_copy_scopes=None):
        """Test host ingress only. Production adapters must authenticate externally."""
        if not isinstance(self.store, LocalGitState):
            raise PRMSError("AUTHORITY_UNVERIFIED", "isolated test sessions cannot authorize a remote state backend")
        protocol = json.loads(self.store.snapshot().get("protocol.json", b"{}"))
        if protocol.get("scope") != "ISOLATED_TEST_ONLY":
            raise PRMSError("AUTHORITY_UNVERIFIED", "isolated session issuer requires an explicit test repository")
        identifier(session_id)
        if session_id in self._issued_session_ids:
            raise PRMSError("REJECTED", "session identity already bound")
        roles = frozenset(identifier(r) for r in allowed_roles)
        copies = None
        if allowed_copy_scopes is not None:
            copies = {}
            for scope in allowed_copy_scopes:
                require_mapping(scope, "host copy scope")
                key = (identifier(scope.get("source_role")), identifier(scope.get("target_role")), scope.get("source_commit"))
                approval = scope.get("approval_ref")
                if (not isinstance(key[2], str) or not re.fullmatch(r"[0-9a-f]{40}", key[2])
                        or key[1] not in roles or key in copies or not isinstance(approval, str) or not approval):
                    raise PRMSError("REJECTED", "host copy scope requires a unique frozen source, target and approval")
                copies[key] = approval
        capability = object()
        self._sessions[capability] = (session_id, roles)
        self._issued_session_ids.add(session_id)
        self._task_scopes[capability] = None if allowed_tasks is None else frozenset(allowed_tasks)
        self._operation_scopes[capability] = None if allowed_operations is None else frozenset(allowed_operations)
        self._copy_scopes[capability] = copies
        return capability

    def revoke_isolated_session(self, capability):
        if capability not in self._sessions:
            raise PRMSError("AUTHORITY_UNVERIFIED", "unknown session capability")
        del self._sessions[capability]
        del self._task_scopes[capability]
        del self._operation_scopes[capability]
        del self._copy_scopes[capability]

    def _identity(self, capability, role_id):
        try:
            value = self._sessions.get(capability)
        except TypeError:
            value = None
        if value is None or role_id not in value[1]:
            raise PRMSError("AUTHORITY_UNVERIFIED", "unbound caller or role")
        return value[0]

    def authorize_operation(self, capability, role_id, kind, *, task_id=None):
        session = self._identity(capability, role_id)
        operations = self._operation_scopes[capability]
        if operations is not None and kind not in operations:
            raise PRMSError("AUTHORITY_UNVERIFIED", "operation outside host-provided task authority")
        tasks = self._task_scopes[capability]
        if tasks is not None and kind in {"APPEND", "ASSIGN", "CHECKPOINT"} and task_id not in tasks:
            raise PRMSError("AUTHORITY_UNVERIFIED", "task outside host-provided assignment scope")
        return session

    def authorize_copy(self, capability, source_role, target_role, source_commit, approval_ref):
        session = self.authorize_operation(capability, target_role, "COPY_ALL_MEMORY")
        copies = self._copy_scopes[capability]
        if copies is None:
            if self._task_scopes[capability] is not None:
                raise PRMSError("AUTHORITY_UNVERIFIED", "task-scoped session requires an explicit host copy grant")
        elif copies.get((source_role, target_role, source_commit)) != approval_ref:
            raise PRMSError("AUTHORITY_UNVERIFIED", "copy outside host-bound source/target/approval scope")
        return session

    def apply(self, capability, role_id, *, operation_id, expected_head, expected_version,
              expected_epoch, kind, payload, before_publish=None):
        identifier(role_id)
        identifier(operation_id)
        positive_version(expected_version, "expected_version", allow_zero=True)
        positive_version(expected_epoch, "expected_epoch", allow_zero=True)
        require_mapping(payload, "operation payload")
        session = self.authorize_operation(capability, role_id, kind, task_id=payload.get("task_id"))
        frozen_head = self.store.head()
        snapshot = self.store.snapshot(frozen_head)
        prefix = f"roles/{role_id}/"
        request_digest = digest(canonical({"role": role_id, "kind": kind, "payload": payload,
                                           "session": session, "epoch": expected_epoch,
                                           "version": expected_version}))
        op_path = f"publications/{operation_id}.json"
        if op_path in snapshot:
            old = json.loads(snapshot[op_path])
            if old["request_digest"] != request_digest:
                raise PRMSError("VERSION_CONFLICT", "operation ID reused with different request")
            return {"status": "ALREADY_APPLIED", "readback_head": frozen_head, "operation_id": operation_id}
        if frozen_head != expected_head:
            raise PRMSError("VERSION_CONFLICT", "expected ref no longer current")
        current = json.loads(snapshot.get(prefix + "CURRENT.json", b'{"state_version":0,"owner_epoch":0}'))
        if current["state_version"] != expected_version:
            raise PRMSError("VERSION_CONFLICT", "state version")
        owner = json.loads(snapshot.get(prefix + "owner.json", b'{}'))
        changes = {}
        if kind == "REGISTER":
            if prefix + "identity.json" in snapshot:
                raise PRMSError("VERSION_CONFLICT", "role already registered")
            for key in ["definition", "domain_id", "state_repository_id"]:
                if not payload.get(key):
                    raise PRMSError("REJECTED", "role definition and ownership required")
            identifier(payload["domain_id"])
            if not isinstance(payload["state_repository_id"], str):
                raise PRMSError("REJECTED", "state repository identity must be a string")
            definition = payload["definition"]
            if not isinstance(definition, dict) or not definition.get("role_type_id") or not definition.get("version"):
                raise PRMSError("REJECTED", "versioned RoleDefinition required")
            identifier(definition["role_type_id"])
            identifier(definition["version"])
            changes[prefix + "identity.json"] = canonical({**payload, "role_id": role_id})
            changes[prefix + f'definitions/{definition["version"]}.json'] = canonical(definition)
            epoch = 1
            changes[prefix + "owner.json"] = canonical({"session_id": session, "owner_epoch": epoch})
        elif kind == "CLAIM":
            if prefix + "identity.json" not in snapshot or owner.get("owner_epoch") != expected_epoch:
                raise PRMSError("STALE_OWNER", "claim expected epoch mismatch")
            epoch = expected_epoch + 1
            changes[prefix + "owner.json"] = canonical({"session_id": session, "owner_epoch": epoch})
        else:
            if owner.get("owner_epoch") != expected_epoch or owner.get("session_id") != session:
                raise PRMSError("STALE_OWNER", "session has lost effective ownership")
            epoch = expected_epoch
            if kind == "APPEND":
                event_id = identifier(payload["event_id"])
                event = normalize_event(payload)
                if event["kind"] == "CORRECTION" and prefix + f'events/{identifier(event["corrects_event_id"])}.json' not in snapshot:
                    raise PRMSError("SOURCE_MISSING", "correction original event not found")
                event_path = prefix + f"events/{event_id}.json"
                if event_path in snapshot:
                    raise PRMSError("VERSION_CONFLICT", "immutable event already exists")
                changes[event_path] = canonical(event)
            elif kind == "CHECKPOINT":
                event_paths = sorted(p for p in snapshot if p.startswith(prefix + "events/"))
                checkpoint = {"checkpoint_id": operation_id, "source_commit": frozen_head,
                              "event_manifest": {p: digest(snapshot[p]) for p in event_paths},
                              "state": payload}
                changes[prefix + f"checkpoints/{operation_id}.json"] = canonical(checkpoint)
                current["checkpoint"] = operation_id
            elif kind == "ASSIGN":
                assignment_id = identifier(payload["assignment_id"])
                if not isinstance(payload.get("task_id"), str) or not payload["task_id"] or not isinstance(payload.get("human_authority_ref"), str) or not payload["human_authority_ref"]:
                    raise PRMSError("AUTHORITY_UNVERIFIED", "task and Human assignment provenance required")
                assignment_path = prefix + f"assignments/{assignment_id}.json"
                if assignment_path in snapshot:
                    raise PRMSError("VERSION_CONFLICT", "assignment history is immutable")
                changes[assignment_path] = canonical({**payload, "role_id": role_id,
                    "authority_effect": "RECORDED_REFERENCE_NOT_EXECUTION_GRANT"})
                current["assignment_id"] = assignment_id
            elif kind == "UPGRADE_DEFINITION":
                version = identifier(payload["version"])
                definition_path = prefix + f"definitions/{version}.json"
                identity = json.loads(snapshot[prefix + "identity.json"])
                if (definition_path in snapshot or version == identity["definition"]["version"]
                        or not isinstance(payload.get("compatibility_ref"), str)
                        or not payload["compatibility_ref"] or
                        payload.get("role_type_id") != identity["definition"]["role_type_id"]):
                    raise PRMSError("REJECTED", "new version and compatibility evidence required")
                changes[definition_path] = canonical(payload)
                identity["definition"] = payload
                changes[prefix + "identity.json"] = canonical(identity)
            elif kind == "REFRESH_INDEX":
                from memory import build_index
                index = build_index(snapshot, role_id, frozen_head, expected_version + 1)
                changes[prefix + f"indexes/{operation_id}.json"] = canonical(index)
                current["index_ref"] = prefix + f"indexes/{operation_id}.json"
            else:
                raise PRMSError("REJECTED", "unsupported operation")
        current.update(role_id=role_id, state_version=expected_version + 1, owner_epoch=epoch,
                       operation_id=operation_id, status="PUBLISHED_CURRENT", schema_version="prms.current.v1")
        validate_current(current, role_id)
        changes[prefix + "CURRENT.json"] = canonical(current)
        changes[op_path] = canonical({"operation_id": operation_id, "role_id": role_id,
                                     "request_digest": request_digest, "parent": frozen_head})
        return self.store.commit(frozen_head, changes, operation_id, before_publish=before_publish)

    def recover(self, role_id, head=None):
        identifier(role_id)
        head = head or self.store.head()
        snapshot = self.store.snapshot(head)
        prefix = f"roles/{role_id}/"
        if prefix + "CURRENT.json" not in snapshot:
            raise PRMSError("SOURCE_MISSING", "no published role")
        current = json.loads(snapshot[prefix + "CURRENT.json"])
        validate_current(current, role_id)
        owner = json.loads(snapshot[prefix + "owner.json"])
        if owner.get("owner_epoch") != current["owner_epoch"]:
            raise PRMSError("REJECTED", "owner and CURRENT epoch differ")
        checkpoint_id = current.get("checkpoint")
        checkpoint = None
        if checkpoint_id:
            checkpoint = json.loads(snapshot[prefix + f"checkpoints/{checkpoint_id}.json"])
            for path, expected in checkpoint["event_manifest"].items():
                if path not in snapshot or digest(snapshot[path]) != expected:
                    raise PRMSError("SOURCE_MISSING", "checkpoint event content mismatch")
        events = [json.loads(data) for p, data in sorted(snapshot.items()) if p.startswith(prefix + "events/")]
        newer_events = sorted(p for p in snapshot if p.startswith(prefix + "events/")
                              and (checkpoint is None or p not in checkpoint["event_manifest"]))
        return {"role_id": role_id, "source_commit": head, "current": current,
                "identity": json.loads(snapshot[prefix + "identity.json"]), "events": events,
                "checkpoint": checkpoint, "unsaved_chat": "NOT_OBSERVABLE",
                "checkpoint_uncovered_event_paths": newer_events,
                "fencing_mode": self.store.fencing_mode, "action_authorized": False}

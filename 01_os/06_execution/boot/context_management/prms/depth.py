"""PRMS memory depth, independent of Core mechanism effectiveness levels."""
import base64
import json

from source import PRMSError, canonical, digest
from state import identifier

DEPTHS = {"L0": "mandatory_boot", "L1": "current_role_and_task",
          "L2": "directory_and_source_excerpt", "L3": "selected_original_evidence",
          "L4": "full_role_history_and_audit"}


def audit_history(store, head, role_id, *, max_commits, budget_bytes):
    """Read every reachable commit, retaining each distinct role-record version.

    Bounds never turn a truncated audit into a complete result. Other roles are
    filtered, including their operation records. Original bytes use base64.
    """
    identifier(role_id)
    if type(max_commits) is not int or not 1 <= max_commits <= 1000:
        raise PRMSError("REJECTED", "audit commit bound must be 1..1000")
    pending, visited, items, seen, omitted = [head], [], [], set(), []
    used = 0
    prefix = f"roles/{role_id}/"
    while pending and len(visited) < max_commits:
        commit = pending.pop()
        if commit in visited:
            continue
        visited.append(commit)
        snapshot = store.snapshot(commit)
        for path, raw in sorted(snapshot.items()):
            if not path.startswith(prefix):
                if not path.startswith("publications/") or json.loads(raw).get("role_id") != role_id:
                    continue
            key = (path, digest(raw))
            if key in seen:
                continue
            seen.add(key)
            item = {"path": path, "sha256": key[1], "source_commit": commit,
                    "encoding": "base64", "content": base64.b64encode(raw).decode()}
            cost = len(canonical(item))
            if used + cost > budget_bytes:
                omitted.append({"path": path, "sha256": key[1], "reason": "CONTEXT_BUDGET_INSUFFICIENT"})
            else:
                used += cost
                items.append(item)
        pending.extend(p for p in store.parents(commit) if p not in visited and p not in pending)
    return {"schema_version": "prms.role_audit.v1", "role_id": role_id,
            "frozen_head": head, "visited_commits": visited, "unvisited_commits": pending,
            "items": items, "omitted": omitted, "used_bytes": used,
            "status": "BLOCKED" if pending or omitted else "COMPLETE_WITHIN_ROLE_HISTORY",
            "authority_transferred": False}

"""Session-bound load plans and receipts; reads never imply action permission."""
from __future__ import annotations

from catalog import B0_PATHS, mapping
from source import PRMSError, canonical, digest


def expand_boot(source, path):
    """Follow the existing boot contract, retaining missing paths for fail-closed load."""
    paths = [path]
    if path not in source.tree:
        return paths
    doc = mapping(source, path)
    for item in doc.get("load_order", []):
        value = item.get("path") if isinstance(item, dict) else item
        if not isinstance(value, str):
            raise PRMSError("REJECTED", "invalid canonical boot reference")
        paths.append(value)
    return paths


def plan_context(source, catalog, *, session_id, role, task_id, stage=None, actions=(),
                 required_paths=(), optional_paths=()):
    if not session_id or not role or not task_id:
        raise PRMSError("REJECTED", "session, role and task are required")
    if catalog["source_commit"] != source.commit:
        raise PRMSError("SUMMARY_STALE", "catalog commit")
    mandatory = list(B0_PATHS)
    mandatory += expand_boot(source, B0_PATHS[4])
    # Existing activation registry owns action-to-mechanism relationships.
    triggers = mapping(source, "01_os/03_mechanisms/mechanism_activation/机制触发注册表_v1.yml")
    mechanism_names = {"context_management"}
    formal = set(actions) & set(triggers.get("formal_action_classes", []))
    if formal:
        mechanism_names.add("mechanism_activation")
    for name, rule in triggers.get("mechanisms", {}).items():
        if set(actions) & set(rule.get("mandatory_for_action_classes", [])):
            mechanism_names.add(name)
    for name in sorted(mechanism_names - {"context_management"}):
        mandatory += expand_boot(source, f"01_os/02_boot/{name}/启动清单_v1.yml")
    if stage:
        found = [e["path"] for e in catalog["entries"]
                 if e["kind"] == "WORKFLOW" and e["path"].split("/")[2].startswith(stage + "_")]
        if len(found) != 1:
            raise PRMSError("SOURCE_MISSING", "unresolved workflow stage")
        mandatory += found
    mandatory += list(required_paths)
    paths = list(dict.fromkeys(mandatory))
    plan = {"schema_version": "prms.load_plan.v1", "session_id": session_id,
            "role": role, "task_id": task_id, "commit": source.commit,
            "repository": source.repository, "mandatory_paths": paths,
            "optional_paths": sorted(set(optional_paths) - set(paths)),
            "catalog_digest": digest(canonical(catalog)),
            "source_blobs": {p: source.tree.get(p, {}).get("blob") for p in paths + list(optional_paths)},
            "directory_cards": catalog["entries"], "action_authorized": False}
    plan["plan_digest"] = digest(canonical(plan))
    return plan


def human_choice(plan, *, session_id, selected_paths, decision_source):
    if session_id != plan["session_id"] or not decision_source:
        raise PRMSError("AUTHORITY_UNVERIFIED", "current-session Human choice required")
    if not set(selected_paths) <= set(plan["optional_paths"]):
        raise PRMSError("REJECTED", "selection outside disclosed proposal")
    return {"session_id": session_id, "plan_digest": plan["plan_digest"],
            "selected_paths": sorted(set(selected_paths)), "decision_source": decision_source,
            "authority_effect": "memory_selection_only"}


def assemble_context(source, plan, choice, *, budget_bytes):
    if source.commit != plan["commit"] or source.repository != plan["repository"]:
        raise PRMSError("SUMMARY_STALE", "source drift between discovery and assembly")
    if choice["session_id"] != plan["session_id"] or choice["plan_digest"] != plan["plan_digest"]:
        raise PRMSError("AUTHORITY_UNVERIFIED", "choice is from another session or plan")
    unsigned = dict(plan)
    claimed = unsigned.pop("plan_digest")
    if claimed != digest(canonical(unsigned)):
        raise PRMSError("REJECTED", "modified load plan")
    selected = choice["selected_paths"]
    if not set(selected) <= set(plan["optional_paths"]):
        raise PRMSError("REJECTED", "modified optional selection")
    bodies, missing, not_loaded = [], [], []
    used = 0
    # Directory summaries are real source excerpts already frozen by discovery.
    directory = canonical(plan["directory_cards"])
    used += len(directory)
    for path in plan["mandatory_paths"] + selected:
        try:
            data, proof = source.read(path, plan["source_blobs"].get(path))
        except PRMSError as exc:
            missing.append({"path": path, "status": exc.status})
            continue
        if used + len(data) > budget_bytes:
            not_loaded.append({"path": path, "reason": "CONTEXT_BUDGET_INSUFFICIENT"})
            continue
        used += len(data)
        bodies.append({"text": data.decode("utf-8"), "source": proof, "depth": "FULL"})
    loaded = {b["source"]["path"] for b in bodies}
    required_missing = sorted(set(plan["mandatory_paths"]) - loaded)
    blocked = bool(required_missing or used > budget_bytes)
    return {"schema_version": "prms.context_recovery.v1", "status": "BLOCKED" if blocked else
            ("PARTIAL" if missing or not_loaded else "READY"),
            "session_id": plan["session_id"], "role": plan["role"], "task_id": plan["task_id"],
            "source_commit": source.commit, "repository": source.repository,
            "human_choice": choice, "mandatory_paths": plan["mandatory_paths"],
            "directory_cards": plan["directory_cards"], "directory_bytes": len(directory),
            "full_bodies": bodies, "missing": missing, "not_loaded": not_loaded,
            "required_not_loaded": required_missing,
            "excluded_optional": sorted(set(plan["optional_paths"]) - set(selected)),
            "budget_bytes": budget_bytes, "used_bytes": used,
            "mechanism_effective": "NOT_INFERRED_FROM_LOADING", "action_authorized": False}


def verify_recovery(source, receipt):
    """Re-resolve the referenced source bytes rather than trusting receipt hashes."""
    if source.commit != receipt["source_commit"] or source.repository != receipt["repository"]:
        raise PRMSError("SUMMARY_STALE", "receipt source binding")
    for body in receipt["full_bodies"]:
        proof = body["source"]
        data, actual = source.read(proof["path"], proof["blob"])
        if actual != proof or data != body["text"].encode("utf-8"):
            raise PRMSError("REJECTED", "receipt body not supported by actual source")
    loaded = {b["source"]["path"] for b in receipt["full_bodies"]}
    mandatory_b0 = set(B0_PATHS) | set(expand_boot(source, B0_PATHS[4]))
    directory_bytes = canonical(receipt["directory_cards"])
    actual_bytes = len(directory_bytes) + sum(len(b["text"].encode("utf-8")) for b in receipt["full_bodies"])
    if actual_bytes != receipt["used_bytes"]:
        raise PRMSError("REJECTED", "receipt byte accounting mismatch")
    if receipt["status"] == "READY" and ((set(receipt["mandatory_paths"]) | mandatory_b0) - loaded
            or receipt["used_bytes"] > receipt["budget_bytes"]):
        raise PRMSError("REQUIRED_SOURCE_NOT_LOADED", "invalid READY receipt")
    return {"status": "VERIFIED_FOR_SOURCE_LOADING", "context_status": receipt["status"],
            "action_authorized": False}

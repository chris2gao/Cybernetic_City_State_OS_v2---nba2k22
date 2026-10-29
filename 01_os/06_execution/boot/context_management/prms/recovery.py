"""Compose actual Core reads with a frozen role snapshot for a new window."""
import json

from context import assemble_context, verify_recovery
from source import PRMSError, canonical, digest
from depth import DEPTHS, audit_history


def create_recovery_package(gate, role_id, core_source, *, core_plan, core_choice,
                            history_choice, budget_bytes):
    """Read the published state, never infer it from the old conversation.

    Current task events are required. Additional history is explicitly selected
    for this session. This is context preparation, not authentication or takeover.
    """
    session = core_plan["session_id"]
    if history_choice.get("session_id") != session or not history_choice.get("decision_source"):
        raise PRMSError("AUTHORITY_UNVERIFIED", "current-session history choice required")
    core = assemble_context(core_source, core_plan, core_choice, budget_bytes=budget_bytes)
    verify_recovery(core_source, core, expected_plan=core_plan, expected_choice=core_choice)
    restored = gate.recover(role_id)
    if restored["identity"].get("definition", {}).get("role_type_id") != core_plan["role"]:
        raise PRMSError("REJECTED", "Core context role differs from published RoleDefinition")
    if not isinstance(history_choice.get("selected_event_ids", []), list):
        raise PRMSError("REJECTED", "history selection must be an explicit event-ID list")
    depth = history_choice.get("depth", "L3")
    if depth not in DEPTHS:
        raise PRMSError("REJECTED", "unknown PRMS context depth")
    if depth in ("L0", "L1") and history_choice.get("selected_event_ids"):
        raise PRMSError("REJECTED", "optional history needs L2 or deeper")
    snapshot = gate.store.snapshot(restored["source_commit"])
    prefix = f"roles/{role_id}/"
    warnings = []
    if restored["checkpoint"] is None:
        warnings.append("CURRENT_CHECKPOINT_MISSING")
    elif restored["checkpoint_uncovered_event_paths"]:
        warnings.append("CHECKPOINT_LAGS_DURABLE_EVENTS")
    assignment = None
    assignment_id = restored["current"].get("assignment_id")
    if assignment_id:
        path = prefix + f"assignments/{assignment_id}.json"
        if path not in snapshot:
            raise PRMSError("SOURCE_MISSING", "CURRENT assignment not available")
        assignment = json.loads(snapshot[path])
        if assignment.get("task_id") != core_plan["task_id"]:
            raise PRMSError("REJECTED", "Core task differs from published role assignment")
    else:
        warnings.append("TASK_ASSIGNMENT_MISSING")
    events = {e["event_id"]: e for e in restored["events"]}
    required = {identifier for identifier, e in events.items() if e.get("task_id") == core_plan["task_id"]}
    optional = set(history_choice.get("selected_event_ids", [])) - required
    absent = sorted(optional - set(events))
    if depth == "L4":
        optional |= set(events) - required
    base = {"identity": restored["identity"], "current": restored["current"],
            "assignment": assignment, "checkpoint": restored["checkpoint"]}
    used = core["used_bytes"] + len(canonical(base))
    selected, excluded = [], []
    summaries = []
    if depth == "L2":
        from memory import build_index
        cards = build_index(snapshot, role_id, restored["source_commit"], 1)["summaries"]
        for card in cards:
            if card["id"] not in optional:
                continue
            cost = len(canonical(card))
            if used + cost > budget_bytes:
                excluded.append({"event_id": card["id"], "mandatory": False, "reason": "CONTEXT_BUDGET_INSUFFICIENT"})
            else:
                summaries.append(card)
                used += cost
    # Required facts are never truncated or silently replaced by summaries.
    for identifier in sorted(required) + (sorted(optional & set(events)) if depth in ("L3", "L4") else []):
        event = events[identifier]
        raw = snapshot[prefix + f"events/{identifier}.json"]
        if used + len(raw) > budget_bytes:
            excluded.append({"event_id": identifier, "mandatory": identifier in required,
                             "reason": "CONTEXT_BUDGET_INSUFFICIENT"})
            continue
        used += len(raw)
        selected.append({"event": event, "state_commit": restored["source_commit"],
                         "path": prefix + f"events/{identifier}.json", "sha256": digest(raw)})
    if absent:
        warnings.append("SELECTED_HISTORY_NOT_DURABLE")
    if not restored["events"]:
        warnings.append("NO_DURABLE_EVENTS_UNSAVED_CHAT_NOT_RECOVERABLE")
    audit = None
    if depth == "L4":
        audit = audit_history(gate.store, restored["source_commit"], role_id,
                              max_commits=history_choice.get("max_history_commits", 128),
                              budget_bytes=max(0, budget_bytes - used))
        used += audit["used_bytes"]
    blocked = (core["status"] == "BLOCKED" or used > budget_bytes or any(x["mandatory"] for x in excluded)
               or audit is not None and audit["status"] == "BLOCKED")
    return {"schema_version": "prms.window_recovery.v1", "session_id": session,
            "role_id": role_id, "task_id": core_plan["task_id"], "state_commit": restored["source_commit"],
            "core_source_commit": core_source.commit, "core_context": core, "role_current": base,
            "required_event_ids": sorted(required), "selected_events": selected,
            "context_depth": {"requested": depth, "meaning": DEPTHS[depth],
                              "mandatory_task_evidence_always_full": True},
            "optional_summaries": summaries, "role_history_audit": audit,
            "history_choice": dict(history_choice), "missing_history_ids": absent,
            "excluded_events": excluded, "unselected_history_count": len(events) - len(required | optional.intersection(events)),
            "warnings": warnings, "used_bytes": used, "budget_bytes": budget_bytes,
            "status": "BLOCKED" if blocked else "PARTIAL" if warnings or excluded or core["status"] == "PARTIAL" else "READY",
            "fencing_mode": restored["fencing_mode"], "unsaved_chat": "NOT_OBSERVABLE",
            "action_authorized": False, "owner_takeover_performed": False}


def verify_window_recovery(gate, core_source, package, *, core_plan, core_choice, history_choice):
    if gate.store.head() != package["state_commit"]:
        raise PRMSError("VERSION_CONFLICT", "role state changed since package assembly")
    expected = create_recovery_package(gate, package["role_id"], core_source,
                core_plan=core_plan, core_choice=core_choice, history_choice=history_choice,
                budget_bytes=package["budget_bytes"])
    if canonical(expected) != canonical(package):
        raise PRMSError("REJECTED", "window recovery not supported by actual published state and reads")
    return {"status": "VERIFIED_FOR_CONTEXT_RECOVERY", "context_status": package["status"],
            "model_understanding": "NOT_OBSERVABLE", "action_authorized": False}

"""Domain-specific source expansion layered onto the existing Core assembler.

08 project modules remain candidates. Reading their requested documents does not
publish G2 mechanisms or activate native/domain tools.
"""
from copy import deepcopy

from source import PRMSError, canonical, digest, safe_path
from catalog import discover_g2
from context import verify_recovery


def plan_domain_context(source, catalog, core_plan, *, role, actions=(), required_modules=()):
    if catalog["repository"] != source.repository or catalog["source_commit"] != source.commit:
        raise PRMSError("SUMMARY_STALE", "domain catalog source binding")
    if catalog != discover_g2(source, catalog["domain_id"]):
        raise PRMSError("SUMMARY_STALE", "domain catalog differs from actual frozen sources")
    cards, filtered_refs = [], []
    entries = {e["id"]: e for e in catalog["entries"]}
    required_ids = {e["id"] for e in entries.values()
                    if set(actions) & set(e.get("required_by_trigger", []))
                    and (not e.get("roles") or role in e["roles"])}
    todo = list(required_ids)
    while todo:
        identifier = todo.pop()
        for dependency in entries[identifier].get("dependencies", []):
            dep_id = "G2:" + dependency
            if dep_id not in entries:
                raise PRMSError("SOURCE_MISSING", "required G2 dependency " + dependency)
            if dep_id not in required_ids:
                required_ids.add(dep_id)
                todo.append(dep_id)
    for identifier, entry in entries.items():
        if entry["publication_status"] != "PUBLISHED":
            if identifier in required_ids:
                raise PRMSError("AUTHORITY_UNVERIFIED", "required mechanism is not published")
            continue
        cards.append({"id": identifier, "mandatory": identifier in required_ids,
                      "source": entry["source"], "publication_status": entry["publication_status"],
                      "mechanism_effective": "NOT_INFERRED_FROM_LOADING", "action_authorized": False})
    found_modules = set()
    for candidate in catalog.get("candidates", []):
        module = candidate["module"]
        module_id = module.get("module_id", module.get("id"))
        found_modules.add(module_id)
        if module.get("context_kind") == "CORE_GOVERNANCE_REFERENCE" or any(
                p.startswith("../../01_os/") or p.endswith("AGENT_WORKING_DISCIPLINE.md") for p in module.get("docs", [])):
            # Governance navigation references Core rather than overriding it.
            filtered_refs.append({"module_id": module_id, "reason": "CORE_GOVERNANCE_REFERENCE_USE_B0"})
            continue
        for path in module.get("docs", []):
            if ".." in path.split("/"):
                filtered_refs.append({"module_id": module_id, "path": path, "reason": "OUTSIDE_DOMAIN_BUSINESS_ROOT"})
                continue
            is_directory = path.endswith("/")
            full = safe_path(candidate["module_base"] + "/" + path.rstrip("/"))
            cards.append({"id": f"MODULE:{module_id}:{full}", "module_id": module_id,
                          "mandatory": module_id in required_modules,
                          "source": {"repository": source.repository, "commit": source.commit,
                                     "path": full, "blob": source.tree.get(full, {}).get("blob")},
                          "publication_status": "CANDIDATE_NOT_FORMAL_G2",
                          "source_kind": "DIRECTORY_REFERENCE" if is_directory else "FILE_REFERENCE",
                          "mechanism_effective": "NOT_INFERRED_FROM_LOADING", "action_authorized": False})
    if set(required_modules) - found_modules:
        raise PRMSError("SOURCE_MISSING", "requested module missing in this domain")
    plan = {"schema_version": "prms.domain_load_plan.v1", "domain_id": catalog["domain_id"],
            "repository": source.repository, "source_commit": source.commit,
            "session_id": core_plan["session_id"], "core_plan_digest": core_plan["plan_digest"],
            "cards": cards, "catalog_status": catalog["status"], "role": role,
            "filtered_source_refs": filtered_refs}
    plan["plan_digest"] = digest(canonical(plan))
    return plan


def choose_domain_context(plan, *, session_id, selected_ids, decision_source):
    allowed = {c["id"] for c in plan["cards"] if not c["mandatory"]}
    if session_id != plan["session_id"] or not decision_source or not set(selected_ids) <= allowed:
        raise PRMSError("AUTHORITY_UNVERIFIED", "domain choice is not bound to this session and proposal")
    return {"session_id": session_id, "plan_digest": plan["plan_digest"],
            "selected_ids": sorted(set(selected_ids)), "decision_source": decision_source,
            "authority_effect": "memory_selection_only"}


def assemble_domain_context(source, core_receipt, plan, choice, *, budget_bytes):
    unsigned = dict(plan)
    claimed = unsigned.pop("plan_digest")
    if (claimed != digest(canonical(unsigned)) or choice["plan_digest"] != claimed
            or choice["session_id"] != plan["session_id"] or core_receipt["session_id"] != plan["session_id"]
            or core_receipt["plan_digest"] != plan["core_plan_digest"]):
        raise PRMSError("AUTHORITY_UNVERIFIED", "domain/core/choice binding mismatch")
    if source.repository != plan["repository"] or source.commit != plan["source_commit"]:
        raise PRMSError("SUMMARY_STALE", "domain source drift")
    cards = plan["cards"]
    permitted = {c["id"] for c in cards if not c["mandatory"]}
    if not set(choice["selected_ids"]) <= permitted:
        raise PRMSError("REJECTED", "modified domain selection")
    used = core_receipt["used_bytes"] + len(canonical(cards))
    reads, missing, skipped = [], [], []
    seen = set()
    for card in sorted(cards, key=lambda c: not c["mandatory"]):
        if not card["mandatory"] and card["id"] not in choice["selected_ids"]:
            skipped.append({"id": card["id"], "reason": "NOT_SELECTED"})
            continue
        ref = card["source"]
        if card.get("source_kind") == "DIRECTORY_REFERENCE":
            missing.append({"id": card["id"], "mandatory": card["mandatory"], "status": "DIRECTORY_REQUIRES_EXPLICIT_EXPANSION"})
            continue
        key = (ref["commit"], ref["path"])
        if key in seen:
            continue
        seen.add(key)
        try:
            content_source = source if ref["commit"] == source.commit else source.at(ref["commit"])
            raw, proof = content_source.read(ref["path"], ref["blob"])
        except PRMSError as exc:
            missing.append({"id": card["id"], "mandatory": card["mandatory"], "status": exc.status})
            continue
        if used + len(raw) > budget_bytes:
            missing.append({"id": card["id"], "mandatory": card["mandatory"], "status": "CONTEXT_BUDGET_INSUFFICIENT"})
            continue
        used += len(raw)
        reads.append({"id": card["id"], "source": proof, "text": raw.decode("utf-8"),
                      "publication_status": card["publication_status"], "action_authorized": False})
    blocked = core_receipt["status"] == "BLOCKED" or used > budget_bytes or any(x["mandatory"] for x in missing)
    return {"schema_version": "prms.domain_context_receipt.v1", "session_id": plan["session_id"],
            "domain_id": plan["domain_id"], "repository": source.repository,
            "source_commit": source.commit, "plan_digest": claimed, "choice": deepcopy(choice),
            "status": "BLOCKED" if blocked else "PARTIAL" if missing else core_receipt["status"],
            "domain_catalog_status": plan["catalog_status"], "cards": cards, "reads": reads,
            "filtered_source_refs": plan["filtered_source_refs"],
            "missing": missing, "skipped": skipped, "budget_bytes": budget_bytes, "used_bytes": used,
            "action_authorized": False, "mechanism_effective": "NOT_INFERRED_FROM_LOADING"}


def verify_domain_context(source, receipt, *, core_source, core_receipt,
                          core_plan, core_choice, domain_plan, domain_choice):
    verify_recovery(core_source, core_receipt, expected_plan=core_plan, expected_choice=core_choice)
    expected = assemble_domain_context(source, core_receipt, domain_plan, domain_choice,
                                       budget_bytes=receipt["budget_bytes"])
    if canonical(expected) != canonical(receipt):
        raise PRMSError("REJECTED", "domain context receipt not supported by actual source reads")
    return {"status": "VERIFIED_FOR_SOURCE_LOADING", "context_status": receipt["status"],
            "action_authorized": False}

"""Derived indexes, explicit provenance, lifecycle reuse and full content copy."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

from source import PRMSError, canonical, digest
from state import identifier


def build_index(snapshot, role_id, source_commit, generation):
    identifier(role_id)
    prefix = f"roles/{role_id}/events/"
    entries = []
    for path, raw in sorted(snapshot.items()):
        if not path.startswith(prefix):
            continue
        event = json.loads(raw)
        entries.append({"path": path, "sha256": digest(raw), "source_commit": source_commit,
                        "event_id": event["event_id"], "kind": event["kind"],
                        "task_id": event.get("task_id"), "topic": event.get("topic"),
                        "role_id": role_id, "observed_at": event.get("observed_at"),
                        "text": event.get("text", ""), "source_refs": event.get("source_refs", [])})
    summaries = []
    for e in entries:
        summaries.append({"schema_version": "prms.summary.v1", "id": e["event_id"],
                          "generation": generation, "generator_version": "source-excerpt.v1",
                          "kind": e["kind"], "source_path": e["path"], "source_sha256": e["sha256"],
                          "source_commit": source_commit, "source_refs": e["source_refs"],
                          "summary": e["text"][:512], "omitted_characters": max(0, len(e["text"]) - 512),
                          "scope": {"role_id": role_id, "task_id": e["task_id"], "topic": e["topic"]},
                          "status": "VERIFIED_SOURCE_EXCERPT_NOT_GOVERNANCE_APPROVAL"})
    return {"schema_version": "prms.index.v1", "index_version": generation,
            "generator_version": "event-index.v1", "role_id": role_id,
            "source_commit": source_commit, "scan_scope": prefix, "entries": entries,
            "summaries": summaries, "indexed": len(entries),
            "filtered": len(snapshot) - len(entries), "missing": [],
            "coverage": "COMPLETE_WITHIN_FROZEN_EVENT_SCOPE"}


def stale_dependencies(index, new_snapshot):
    return {s["id"]: "VALID" if s["source_path"] in new_snapshot and
            digest(new_snapshot[s["source_path"]]) == s["source_sha256"] else "SUMMARY_STALE"
            for s in index["summaries"]}


def search_memory(index, query="", *, task_id=None, topic=None, kind=None):
    selected = [e for e in index["entries"] if (task_id is None or e["task_id"] == task_id)
                and (topic is None or e["topic"] == topic) and (kind is None or e["kind"] == kind)]
    hits = [e for e in selected if query.casefold() in e["text"].casefold()]
    return {"status": "MATCHES" if hits else "NO_MATCH_WITHIN_SCANNED_SCOPE", "hits": hits,
            "scan_scope": index["scan_scope"], "source_commit": index["source_commit"],
            "indexed": len(index["entries"]), "filtered": len(index["entries"]) - len(selected),
            "searched": len(selected), "not_matched": len(selected) - len(hits)}


def expand_memory(snapshot, entry):
    raw = snapshot.get(entry["path"])
    if raw is None:
        raise PRMSError("SOURCE_MISSING", entry["path"])
    if digest(raw) != entry["sha256"]:
        raise PRMSError("SUMMARY_STALE", entry["path"])
    return json.loads(raw)


def task_visibility(group_path):
    # Use canonical lifecycle/closure semantics, not a second enum.
    path = Path(__file__).resolve().parents[1] / "working_set/lifecycle.py"
    name = "prms_existing_lifecycle"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    module = sys.modules[name]
    state = module.read_group_state(Path(group_path))
    if not state.is_terminal:
        return {"classification": state.classification, "default_visible": True,
                "archived": False}
    try:
        module.validate_closure_record(state)
    except module.WorkingSetError:
        return {"classification": state.classification, "default_visible": True,
                "archived": False, "reason": "closure_not_verified"}
    # Reference safety and private runtime are mandatory before actual archive.
    return {"classification": state.classification, "default_visible": False,
            "archived": False, "archive_eligibility": "NOT_RUN_REQUIRES_REFERENCE_AND_RUNTIME_CHECKS"}


def copy_all_memory(source_store, target_gate, capability, source_role, target_role, *,
                    source_head, operation_id, target_expected_head, scope_approval_ref):
    identifier(source_role)
    identifier(target_role)
    identifier(operation_id)
    if not scope_approval_ref:
        raise PRMSError("AUTHORITY_UNVERIFIED", "explicit source/target copy scope required")
    session = target_gate._identity(capability, target_role)
    source = source_store.snapshot(source_head)
    target = target_gate.store.snapshot(target_expected_head)
    sp, tp = f"roles/{source_role}/", f"roles/{target_role}/"
    if sp + "identity.json" not in source:
        raise PRMSError("COPY_INCOMPLETE", "source role missing")
    if any(p.startswith(tp) for p in target):
        raise PRMSError("VERSION_CONFLICT", "copy target must be a new independent role")
    changes, manifest, excluded = {}, [], []
    for path, raw in sorted(source.items()):
        if not path.startswith(sp):
            continue
        relative = path[len(sp):]
        if relative in {"owner.json", "CURRENT.json"} or relative.startswith("assignments/"):
            excluded.append({"path": path, "reason": "operational_authority_not_transferable"})
            continue
        copied = tp + "copies/" + operation_id + "/" + relative
        changes[copied] = raw
        manifest.append({"source_path": path, "target_path": copied, "sha256": digest(raw), "bytes": len(raw)})
        # Events remain usable without promoting copied approvals to new permissions.
        if relative.startswith("events/"):
            changes[tp + relative] = raw
    identity = json.loads(source[sp + "identity.json"])
    identity.update(role_id=target_role, copied_from={"role_id": source_role, "commit": source_head},
                    copied_authority_valid=False)
    changes[tp + "identity.json"] = canonical(identity)
    changes[tp + "owner.json"] = canonical({"session_id": session, "owner_epoch": 1})
    changes[tp + "CURRENT.json"] = canonical({"role_id": target_role, "state_version": 1,
            "owner_epoch": 1, "operation_id": operation_id, "status": "PUBLISHED_CURRENT",
            "copy_manifest": tp + f"copies/{operation_id}/manifest.json", "assignment": None})
    changes[tp + f"copies/{operation_id}/manifest.json"] = canonical({"source_commit": source_head,
            "source_role": source_role, "target_role": target_role, "scope_approval_ref": scope_approval_ref,
            "items": manifest, "excluded_authority": excluded, "source_authority_transferred": False})
    if any(digest(changes[e["target_path"]]) != e["sha256"] for e in manifest):
        raise PRMSError("COPY_INCOMPLETE", "target byte verification failed")
    return target_gate.store.commit(target_expected_head, changes, operation_id)


def propose_experience(evidence_refs, counterexamples, scope, target_owner):
    if not evidence_refs or not counterexamples or not scope or not target_owner:
        raise PRMSError("SOURCE_MISSING", "experience needs provenance, scope and falsifiers")
    return {"layer": "K1", "status": "CANDIDATE_PENDING_REVIEW", "evidence_refs": evidence_refs,
            "counterexamples": counterexamples, "scope": scope, "target_owner": target_owner,
            "action_authorized": False}


def promotion_readiness(candidate, *, review_ref=None, human_decision_ref=None, publication_ref=None):
    # Evidence references are navigation only. Caller booleans cannot publish K2.
    return {"status": "AUTHORITY_UNVERIFIED", "layer": "K1",
            "required_external_gate": "existing_target_owner_review_and_protected_publication",
            "provided_refs": [review_ref, human_decision_ref, publication_ref],
            "action_authorized": False}

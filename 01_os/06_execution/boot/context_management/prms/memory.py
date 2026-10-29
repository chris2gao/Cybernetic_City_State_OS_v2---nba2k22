"""Derived indexes, explicit provenance, lifecycle reuse and full content copy."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from pathlib import PurePosixPath
import sys

import yaml

from source import PRMSError, canonical, digest
from state import identifier, WriterGate


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


def source_dependency_status(index, observed_sources):
    """Compare each summary's exact external dependencies to a newly frozen inventory.

    Inventory keys are (repository, path), values are resolved commit/blob facts.
    Missing evidence stays unknown; neither names nor summary text mint a source.
    """
    result = {}
    for summary in index["summaries"]:
        statuses = []
        for ref in summary["source_refs"]:
            if not isinstance(ref, dict) or not all(k in ref for k in ["repository", "path", "commit", "blob"]):
                statuses.append("SOURCE_UNVERIFIED")
                continue
            actual = observed_sources.get((ref["repository"], ref["path"]))
            if actual is None:
                statuses.append("SOURCE_MISSING")
            elif actual.get("blob") != ref["blob"]:
                statuses.append("SUMMARY_STALE")
            else:
                statuses.append("VALID")
        result[summary["id"]] = ("SUMMARY_STALE" if "SUMMARY_STALE" in statuses else
                                 "SOURCE_MISSING" if "SOURCE_MISSING" in statuses else
                                 "SOURCE_UNVERIFIED" if not statuses or "SOURCE_UNVERIFIED" in statuses else "VALID")
    return result


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


def task_series_current(source, run_paths, *, series_id, related_task_ids, series_closeout=None):
    """Recover only explicitly requested run metadata from an immutable source tree."""
    identifier(series_id)
    lifecycle_path = Path(__file__).resolve().parents[1] / "working_set"
    sys.path.insert(0, str(lifecycle_path))
    from lifecycle import classify, TERMINAL, CLOSURE_RECORD_KEYS
    tasks, missing, filtered = [], [], []
    for path in run_paths:
        if not path.startswith(("01_os/_runs/", "01_os/07_content/_runs/")) or not path.endswith("/run.yml"):
            raise PRMSError("REJECTED", "task recovery requires an explicit canonical run path")
        try:
            raw, proof = source.read(path)
        except PRMSError as exc:
            missing.append({"path": path, "status": exc.status})
            continue
        run = yaml.safe_load(raw)
        if not isinstance(run, dict):
            raise PRMSError("REJECTED", "task run must be a mapping")
        task_id = run.get("task_id")
        if task_id not in related_task_ids:
            filtered.append(path)
            continue
        raw_lifecycle = run.get("lifecycle")
        state = classify(raw_lifecycle if isinstance(raw_lifecycle, str) else None)
        closure_verified = False
        closure_proof = None
        if state == TERMINAL and isinstance(run.get("closure_record"), str):
            relative = PurePosixPath(run["closure_record"])
            if relative.is_absolute() or ".." in relative.parts:
                raise PRMSError("REJECTED", "task closure escapes its run")
            closure_path = str(PurePosixPath(path).parent / relative)
            try:
                closure_raw, closure_proof = source.read(closure_path)
                closure = yaml.safe_load(closure_raw)
                closure_verified = isinstance(closure, dict) and any(closure.get(k) for k in CLOSURE_RECORD_KEYS)
            except PRMSError:
                closure_verified = False
        tasks.append({"task_id": task_id, "series_id": series_id, "classification": state,
                      "lifecycle_raw": run.get("lifecycle"), "source": proof,
                      "closure_verified": closure_verified, "closure_source": closure_proof,
                      "default_visible": state != TERMINAL or not closure_verified,
                      "open_items": run.get("open_items", []), "next_steps": run.get("next_steps", []),
                      "stage": run.get("stage"), "approval_refs": run.get("approval_refs", [])})
    declared_closeout = None
    if series_closeout:
        raw, proof = source.read(series_closeout)
        closeout = yaml.safe_load(raw)
        if not isinstance(closeout, dict) or closeout.get("series_id") != series_id or not closeout.get("human_acceptance"):
            raise PRMSError("AUTHORITY_UNVERIFIED", "series closeout not bound to this series")
        declared_closeout = proof
    all_terminal = bool(tasks) and not missing and all(t["classification"] == TERMINAL and t["closure_verified"] for t in tasks)
    absent_tasks = sorted(set(related_task_ids) - {t["task_id"] for t in tasks})
    return {"schema_version": "prms.task_series.v1", "series_id": series_id,
            "source_commit": source.commit, "repository": source.repository, "tasks": tasks,
            "status": "TERMINAL_CONFIRMED" if all_terminal and declared_closeout and not absent_tasks else "ACTIVE_OR_UNCONFIRMED",
            "series_closeout_source": declared_closeout, "missing": missing, "missing_task_ids": absent_tasks,
            "series_membership_basis": "EXPLICIT_REQUESTED_TASK_SET",
            "filtered_paths": filtered, "scan_paths": list(run_paths), "action_authorized": False}


def copy_all_memory(source_store, target_gate, capability, source_role, target_role, *,
                    source_head, operation_id, target_expected_head, scope_approval_ref, before_publish=None):
    identifier(source_role)
    identifier(target_role)
    identifier(operation_id)
    if not isinstance(source_head, str) or not re.fullmatch(r"[0-9a-f]{40}", source_head):
        raise PRMSError("REJECTED", "full copy requires an explicit immutable source commit")
    if not isinstance(scope_approval_ref, str) or not scope_approval_ref:
        raise PRMSError("AUTHORITY_UNVERIFIED", "explicit source/target copy scope required")
    session = target_gate.authorize_copy(capability, source_role, target_role, source_head, scope_approval_ref)
    source = source_store.snapshot(source_head)
    try:
        restored_source = WriterGate(source_store).recover(source_role, source_head)
        source_definition = restored_source["identity"]["definition"]
        definition_path = f'roles/{source_role}/definitions/{identifier(source_definition["version"])}.json'
        if definition_path not in source or json.loads(source[definition_path]) != source_definition:
            raise PRMSError("COPY_INCOMPLETE", "active source RoleDefinition is missing or inconsistent")
    except (PRMSError, KeyError, ValueError, TypeError) as exc:
        raise PRMSError("COPY_INCOMPLETE", "source CURRENT/owner/checkpoint/definition cannot be recovered") from exc
    actual_target_head = target_gate.store.head()
    target = target_gate.store.snapshot(actual_target_head)
    operation_path = f"publications/{operation_id}.json"
    request_digest = digest(canonical({"kind": "COPY_ALL_MEMORY", "source_role": source_role,
            "source_commit": source_head, "target_role": target_role, "session": session,
            "scope_approval_ref": scope_approval_ref}))
    if operation_path in target:
        if json.loads(target[operation_path]).get("request_digest") != request_digest:
            raise PRMSError("VERSION_CONFLICT", "copy operation ID already used")
        return {"status": "ALREADY_APPLIED", "readback_head": actual_target_head, "operation_id": operation_id}
    if actual_target_head != target_expected_head:
        raise PRMSError("VERSION_CONFLICT", "copy target state moved")
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
        # Immutable events/templates stay usable; operational authority is not copied.
        if relative.startswith(("events/", "definitions/")):
            changes[tp + relative] = raw
    identity = json.loads(source[sp + "identity.json"])
    identity.update(role_id=target_role, copied_from={"role_id": source_role, "commit": source_head},
                    copied_authority_valid=False)
    changes[tp + "identity.json"] = canonical(identity)
    # Preserve usable per-task context while discarding operational assignment.
    # Original bytes remain unchanged in copies/<operation>/; these canonical
    # target records are explicitly derived from the frozen source role.
    from task_context import read_task_context
    for path in sorted(source):
        if not path.startswith(sp + 'tasks/') or not path.endswith('/CURRENT.json'):
            continue
        task_id = identifier(path[len(sp + 'tasks/'):].split('/')[0])
        task = read_task_context(source, source_role, task_id)
        context_path = tp + f'tasks/{task_id}/contexts/{operation_id}.json'
        checkpoint_path = tp + f'checkpoints/{operation_id}-task-{task_id}.json'
        record = dict(task['record'])
        record.update(role_id=target_role, state_version=1, operation_id=operation_id,
                      copied_from={'role_id': source_role, 'commit': source_head})
        changes[context_path] = canonical(record)
        checkpoint = task['checkpoint']
        event_manifest = {}
        for original_path, expected in checkpoint['event_manifest'].items():
            target_path = tp + original_path[len(sp):] if original_path.startswith(sp + 'events/') else ''
            if not target_path or digest(changes.get(target_path, b'')) != expected:
                raise PRMSError('COPY_INCOMPLETE', 'task checkpoint original unavailable')
            event_manifest[target_path] = expected
        changes[checkpoint_path] = canonical({**checkpoint, 'event_manifest': event_manifest,
            'copied_from': {'role_id': source_role, 'commit': source_head}})
        changes[tp + f'tasks/{task_id}/CURRENT.json'] = canonical({'role_id': target_role, 'task_id': task_id,
            'context_ref': context_path, 'checkpoint_ref': checkpoint_path, 'assignment_id': None, 'state_version': 1})
    changes[tp + "owner.json"] = canonical({"session_id": session, "owner_epoch": 1})
    changes[tp + "CURRENT.json"] = canonical({"schema_version": "prms.current.v1", "role_id": target_role, "state_version": 1,
            "owner_epoch": 1, "operation_id": operation_id, "status": "PUBLISHED_CURRENT",
            "copy_manifest": tp + f"copies/{operation_id}/manifest.json", "assignment": None})
    changes[tp + f"copies/{operation_id}/manifest.json"] = canonical({"source_commit": source_head,
            "source_role": source_role, "target_role": target_role, "scope_approval_ref": scope_approval_ref,
            "items": manifest, "excluded_authority": excluded, "source_authority_transferred": False})
    changes[operation_path] = canonical({"operation_id": operation_id, "request_digest": request_digest,
                                        "role_id": target_role, "parent": target_expected_head})
    if any(digest(changes[e["target_path"]]) != e["sha256"] for e in manifest):
        raise PRMSError("COPY_INCOMPLETE", "target byte verification failed")
    return target_gate.store.commit(target_expected_head, changes, operation_id, before_publish=before_publish)


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


def reconcile_experience_publication(candidate, source, manifest_path):
    """Consume an already published owner decision, never publish or activate it.

    Candidate-branch records cannot promote themselves. Current target master is
    freshly read, and all subject/review/approval content is resolved from its
    immutable Git objects. Governance records remain records, not Human identity
    authentication or action permission.
    """
    if hasattr(source, "api"):
        current_master = source.api("branches/master")["commit"]["sha"]
    else:
        raw = source.git("ls-remote", "--heads", "origin", "master").decode().split()
        current_master = raw[0] if raw else None
    if source.commit != current_master:
        raise PRMSError("AUTHORITY_UNVERIFIED", "experience target is not current published master")
    manifest = source.json(manifest_path)
    if (manifest.get("schema_version") != "prms.experience_publication.v1"
            or manifest.get("candidate_digest") != digest(canonical(candidate))
            or manifest.get("target_owner") != candidate["target_owner"]):
        raise PRMSError("AUTHORITY_UNVERIFIED", "published experience subject/owner mismatch")
    _, canonical_proof = source.read(manifest["canonical_path"], manifest["canonical_blob"])
    records, proofs = [], [canonical_proof]
    for path in (manifest["human_approval_ref"], manifest["independent_review_ref"]):
        raw, proof = source.read(path)
        record = yaml.safe_load(raw)
        if not isinstance(record, dict) or record.get("subject_blob") != canonical_proof["blob"]:
            raise PRMSError("AUTHORITY_UNVERIFIED", "publication governance evidence subject mismatch")
        records.append(record)
        proofs.append(proof)
    human, review = records
    if (human.get("kind") != "HUMAN_APPROVAL" or human.get("decision") != "APPROVED"
            or review.get("kind") != "INDEPENDENT_REVIEW" or review.get("decision") != "PASS"
            or not review.get("reviewer_session") or not review.get("executor_session")
            or review["reviewer_session"] == review["executor_session"]):
        raise PRMSError("AUTHORITY_UNVERIFIED", "promotion governance gate not satisfied")
    return {"layer": "K2", "status": "PUBLISHED_OWNER_RECORDS_VERIFIED", "source_commit": source.commit,
            "candidate_digest": manifest["candidate_digest"], "target_owner": candidate["target_owner"],
            "actual_reads": proofs, "mechanism_effective": "NOT_INFERRED_FROM_PUBLICATION",
            "action_authorized": False, "Human_identity_authentication": "EXISTING_GOVERNANCE_TRUST_BOUNDARY"}

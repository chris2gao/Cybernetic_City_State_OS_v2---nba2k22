"""G1/G2 discovery from frozen source trees, without runtime activation."""
from __future__ import annotations

import fnmatch
import json
import re

import yaml

from source import PRMSError, canonical, digest, safe_path


G1_ROOTS = ("01_os/01_workflow/", "01_os/02_boot/", "01_os/03_mechanisms/",
            "01_os/04_skills_and_tools/", "01_os/05_registry/")
B0_PATHS = ("AGENTS.md", "AGENT_WORKING_DISCIPLINE.md", "01_os/README.md",
            "01_os/开发入口与单窗口任务规范_v1.md",
            "01_os/02_boot/context_management/启动清单_v1.yml",
            "01_os/05_registry/repository_publisher_authority_v1.yml")


def expand_braces(pattern):
    match = re.search(r"\{([^{}]+)\}", pattern)
    if match is None:
        return [pattern]
    return [p for value in match[1].split(",")
            for p in expand_braces(pattern[:match.start()] + value + pattern[match.end():])]


def matches(path, pattern):
    return any(fnmatch.fnmatchcase(path, p) for p in expand_braces(pattern))


def mapping(source, path):
    value = yaml.safe_load(source.read(path)[0])
    if not isinstance(value, dict):
        raise PRMSError("REJECTED", f"mapping required: {path}")
    return value


def discover_g1(source):
    scoped = sorted(p for p in source.tree if p.startswith(G1_ROOTS))
    registry_paths = [p for p in scoped if re.fullmatch(r"01_os/05_registry/[^/]+\.ya?ml", p)]
    patterns, missing, unresolved = [], [], []
    for path in registry_paths:
        doc = mapping(source, path)
        for entry in doc.get("entries", []):
            pattern = entry.get("path")
            if not isinstance(pattern, str):
                unresolved.append({"registry": path, "reason": "entry_without_path"})
                continue
            patterns.append((pattern, path))
            if "<" in pattern:
                unresolved.append({"registry": path, "path": pattern, "reason": "dynamic_path_set"})
            elif not any(matches(p, pattern) for p in source.tree):
                missing.append({"registry": path, "path": pattern})
    effectiveness_path = "01_os/03_mechanisms/mechanism_activation/机制生效等级与盘点_v1.yml"
    effectiveness = mapping(source, effectiveness_path) if effectiveness_path in source.tree else {}
    levels = {item["mechanism_id"]: item.get("current_level", "UNKNOWN")
              for item in effectiveness.get("inventory", [])}
    entries = []
    for path in scoped:
        kind = None
        if re.fullmatch(r"01_os/03_mechanisms/[^/]+/README\.md", path):
            kind = "MECHANISM"
        elif re.fullmatch(r"01_os/01_workflow/0[1-7]_[^/]+/README\.md", path):
            kind = "WORKFLOW"
        elif re.fullmatch(r"01_os/02_boot/[^/]+/启动清单_v[^/]+\.yml", path):
            kind = "BOOT"
        elif path in registry_paths:
            kind = "REGISTRY"
        elif re.fullmatch(r"01_os/04_skills_and_tools/[^/]+/README\.md", path):
            kind = "OPTIONAL_TOOL"
        if kind is None:
            continue
        data, proof = source.read(path)
        text = data.decode("utf-8")
        registered_by = sorted({reg for pat, reg in patterns if matches(path, pat)})
        loader, dependencies = path if kind in {"BOOT", "WORKFLOW", "REGISTRY"} else None, []
        if kind == "MECHANISM":
            boot_path = f"01_os/02_boot/{path.split('/')[2]}/启动清单_v1.yml"
            if boot_path in source.tree:
                loader = boot_path
                boot = mapping(source, boot_path)
                dependencies = [x.get("path") if isinstance(x, dict) else x for x in boot.get("load_order", [])]
        # Exact source excerpt, never an unverified model-authored summary.
        excerpt = next((x.strip() for x in text.splitlines() if x.strip() and not x.startswith("#")), "")
        entries.append({"id": "G1:" + path, "kind": kind, "layer": "G1", "path": path,
                        "source": proof, "registered_by": registered_by,
                        "status": "REGISTERED_SOURCE" if registered_by or kind == "REGISTRY" else "CANDIDATE_UNREGISTERED",
                        "publication_status": "SOURCE_COMMIT_ONLY_NOT_RELEASE_PROOF",
                        "effectiveness_level": levels.get(path.split("/")[2], "NOT_LISTED_IN_CURRENT_EFFECTIVENESS_INVENTORY") if kind == "MECHANISM" else "NOT_APPLICABLE",
                        "summary": excerpt, "summary_source_blob": proof["blob"],
                        "version": proof["blob"], "owner": "core_owned", "dependencies": dependencies,
                        "applicability": {"repository": source.repository, "scope": "CORE"},
                        "loader_entry": loader, "loader_binding": "DECLARED" if loader else "NOT_DECLARED_IN_THIS_SNAPSHOT",
                        "body_loaded": False, "mechanism_effective": None, "action_authorized": False})
    unregistered_sources = [p for p in scoped if not any(matches(p, pat) for pat, _ in patterns)
                            and p not in registry_paths]
    return {"schema_version": "prms.catalog.v1", "layer": "G1", "source_commit": source.commit,
            "repository": source.repository, "scan_roots": list(G1_ROOTS),
            "scanned_paths": len(scoped), "excluded_paths": len(source.tree) - len(scoped),
            "counts": {k: sum(e["kind"] == k for e in entries)
                       for k in ["MECHANISM", "WORKFLOW", "BOOT", "REGISTRY", "OPTIONAL_TOOL"]},
            "entries": entries, "missing_references": missing,
            "unregistered_candidate_paths": [e["path"] for e in entries if not e["registered_by"] and e["kind"] != "REGISTRY"],
            "unregistered_source_paths": unregistered_sources,
            "registry_consistency": "PARTIAL" if missing or unregistered_sources or unresolved else "CONSISTENT_WITHIN_SCAN_SCOPE",
            "unresolved_path_sets": unresolved, "effectiveness_inventory": effectiveness,
            "coverage": "PARTIAL" if missing or unresolved else "SCANNED_SCOPE_COMPLETE"}


def discover_g2(source, domain_id):
    domain = mapping(source, "08_Domain_Applications/domain.yml")
    if domain.get("domain_id") != domain_id or domain.get("repository") != source.repository:
        raise PRMSError("REJECTED", "domain/repository binding mismatch")
    path = "09_Domain_Global_Mechanisms/domain_mechanisms.yml"
    result = {"layer": "G2", "domain_id": domain_id, "repository": source.repository,
              "source_commit": source.commit, "entries": [], "candidates": [], "issues": [],
              "status": "DOMAIN_CATALOG_UNINITIALIZED"}
    if path in source.tree:
        catalog = mapping(source, path)
        if catalog.get("domain_id") != domain_id or catalog.get("repository") != source.repository:
            raise PRMSError("REJECTED", "G2 catalog identity mismatch")
        ids = set()
        for item in catalog.get("entries", []):
            item = dict(item)
            identifier = item.get("mechanism_id")
            if not identifier or identifier in ids:
                raise PRMSError("REJECTED", "missing/duplicate G2 identity")
            ids.add(identifier)
            if item.get("domain_id") != domain_id or item.get("repo") != source.repository:
                raise PRMSError("REJECTED", "cross-domain or stale G2 source")
            required = ("content_path", "canonical_blob", "owner", "publication_status", "version",
                        "applicability", "dependencies", "evidence_refs")
            if any(k not in item for k in required):
                raise PRMSError("REJECTED", "G2 required fields absent")
            owner = item["owner"]
            if owner != domain_id and owner != {"domain_id": domain_id, "repository": source.repository}:
                raise PRMSError("AUTHORITY_UNVERIFIED", "G2 owner not bound to this domain")
            if not item["content_path"].startswith(("08_Domain_Applications/", "09_Domain_Global_Mechanisms/")):
                raise PRMSError("REJECTED", "G2 cannot replace a Core canonical body")
            body_source = source if item.get("source_commit") == source.commit else source.at(item.get("source_commit", ""))
            _, proof = body_source.read(item["content_path"], item["canonical_blob"])
            evidence, records = [], []
            for ref in item["evidence_refs"]:
                raw, read = source.read(ref)
                evidence.append(read)
                try:
                    record = yaml.safe_load(raw)
                    if isinstance(record, dict):
                        records.append(record)
                except yaml.YAMLError:
                    pass
            item.update(id="G2:" + identifier, layer="G2", source=proof,
                        evidence_reads=evidence, body_loaded=False, action_authorized=False)
            # Published is a governance assertion with inspectable evidence, not activation.
            item["publication_verification"] = "NOT_PUBLISHED"
            if item["publication_status"] == "PUBLISHED":
                matching = [r for r in records if r.get("schema_version") == "prms.publication_evidence.v1"
                    and r.get("subject_blob") == proof["blob"] and r.get("mechanism_id") == identifier
                    and r.get("domain_id") == domain_id and r.get("repository") == source.repository]
                approved = any(r.get("kind") == "HUMAN_APPROVAL" and r.get("decision") == "APPROVED" for r in matching)
                reviewed = any(r.get("kind") == "INDEPENDENT_REVIEW" and r.get("decision") == "PASS"
                    and r.get("reviewer_session") and r.get("executor_session")
                    and r["reviewer_session"] != r["executor_session"] for r in matching)
                if not approved or not reviewed:
                    raise PRMSError("AUTHORITY_UNVERIFIED", "G2 publication lacks matching Human/review records")
                item["publication_verification"] = "MATCHING_PUBLISHED_RECORDS_NOT_IDENTITY_AUTHENTICATION"
            result["entries"].append(item)
        result["status"] = "CATALOG_DISCOVERED_NOT_ACTIVATED"
        for entry in result["entries"]:
            for dependency in entry["dependencies"]:
                if dependency not in ids:
                    result["issues"].append({"entry": entry["id"], "status": "SOURCE_MISSING", "dependency": dependency})
        if result["issues"]:
            result["status"] = "CATALOG_PARTIAL"
    declared_registry = domain.get("project_module_registry")
    module_paths = ([declared_registry] if declared_registry else sorted(p for p in source.tree
                    if p.startswith("08_Domain_Applications/") and
                    re.search(r"/PROJECT_MODULE_REGISTRY_V[0-9]+\.json$", p)))
    for module_path in module_paths:
        if not module_path.startswith("08_Domain_Applications/"):
            raise PRMSError("REJECTED", "module registry must belong to the current domain business root")
        raw, module_proof = source.read(module_path)
        modules = json.loads(raw)
        base = safe_path(modules.get("module_base", "").rstrip("/"))
        if not base.startswith("08_Domain_Applications/"):
            raise PRMSError("REJECTED", "module base must remain domain-owned")
        for item in modules.get("modules", []):
            result["candidates"].append({"kind": "MODULE_INDEX", "module": item,
                                          "module_base": base, "registry_source": module_proof,
                                          "publication_status": "CANDIDATE_NOT_FORMAL_G2"})
    return result


def compatibility(core, installed):
    paths = sorted(p for p in core.tree if p.startswith(G1_ROOTS) or p in B0_PATHS)
    changed = [p for p in paths if installed.tree.get(p, {}).get("blob") != core.tree[p]["blob"]]
    return {"status": "CORE_VERSION_DIVERGED" if changed else "CORE_SOURCE_BLOBS_MATCH",
            "core_commit": core.commit, "installed_commit": installed.commit,
            "checked_paths": len(paths), "different_paths": changed,
            "merge_performed": False}

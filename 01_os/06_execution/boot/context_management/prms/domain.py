"""Explicit new-domain scaffolding. Existing domains are never silently upgraded."""
from pathlib import Path
import re

import yaml

from source import PRMSError


def scaffold_domain(root, domain_id, repository, core_commit):
    root = Path(root).resolve()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]+", domain_id):
        raise PRMSError("REJECTED", "invalid domain ID")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise PRMSError("REJECTED", "invalid repository identity")
    if not re.fullmatch(r"[0-9a-f]{40}", core_commit):
        raise PRMSError("REJECTED", "exact inherited Core commit required")
    content = root / "08_Domain_Applications"
    g2 = root / "09_Domain_Global_Mechanisms"
    domain_path = content / "domain.yml"
    if not (root / "CORE_MANIFEST.yml").is_file():
        raise PRMSError("SOURCE_MISSING", "Core checkout required")
    files = {
        domain_path: yaml.safe_dump({"domain_id": domain_id, "repository": repository,
                  "global_mechanism_catalog": "09_Domain_Global_Mechanisms/domain_mechanisms.yml",
                  "inherited_core_commit": core_commit, "automatic_updates_enabled": False}, sort_keys=False),
        content / "knowledge_catalog.yml": yaml.safe_dump({"schema_version": "prms.domain_knowledge.v1",
                  "domain_id": domain_id, "repository": repository, "candidates": []}, sort_keys=False),
        g2 / "domain_mechanisms.yml": yaml.safe_dump({"schema_version": "prms.domain_catalog.v1",
                  "domain_id": domain_id, "repository": repository, "entries": []}, sort_keys=False),
        g2 / "README.md": f"# {domain_id} domain mechanisms\n\nInitialized empty catalog. No published mechanisms.\n"
                  "This directory holds the domain's loading configuration; its content stays in 08.\n"
                  "Canonical Core mechanisms are referenced, never copied.\n"
                  "Publication, context loading, effectiveness and execution authorization are separate.\n",
    }
    # 08 and 09 are domain-owned (Human decision 2026-11-18, run-20261118-restore-09-001):
    # a scaffold never overwrites any existing file there.
    existing = sorted(path.relative_to(root).as_posix() for path in files if path.exists())
    if existing:
        raise PRMSError("REJECTED", "explicit migration required; existing domain files: " + ", ".join(existing))
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return {"status": "DOMAIN_CATALOG_INITIALIZED_EMPTY", "files": [p.relative_to(root).as_posix() for p in files],
            "published_mechanisms": 0, "state_created": False}

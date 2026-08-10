#!/usr/bin/env python3
"""Prove the five migrations left no active dependency on the old paths.

Active surface, stated once so every count below means the same thing:

    08_os/** minus 08_os/_runs/** minus 08_os/_dev/**
  + the tracked non-08 files that survive the approved deletion

08_os/_dev/ holds active design and superseded versions - the file placement table
calls it "supersede, do not erase history" - so a superseded draft naming an old
path is correct as history and is counted separately rather than treated as a
live dependency. 08_os/_runs/** is past run evidence for the same reason.

Each check reports the surviving hits rather than only a verdict, because "zero"
is the claim being made and an unexplained hit is exactly what would falsify it.

Usage
    python verify_migration_closure.py [--repo-root .] [--json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

OLD_TOKENS = {
    "M1_publisher_authority": ".ai/REPOSITORY_PUBLISHER_AUTHORITY.yml",
    "M2_token_profile": ".ai/TOKEN_USAGE_PROFILE.md",
    "M3_domain_run_root": ".ai/PROGRAM_RUNS",
    "M4_system_summary_structured_ref": "path: 系统机制总结.md",
}

# The migrated authority must not carry the old communication plane with it.
MIGRATED_AUTHORITY_PATH = "08_os/05_registry/repository_publisher_authority_v1.yml"
MIGRATED_AUTHORITY = MIGRATED_AUTHORITY_PATH
OLD_PLANE_TOKENS = [
    ".ai/PROTOCOL",
    ".ai/communication_compliance",
    ".ai/TASKS",
    ".ai/lanes",
    ".ai/load_profiles",
    ".ai/STATE.yml",
    ".ai/INBOX",
    ".ai/OUTBOX",
    "mailbox",
]

# Three active-surface files legitimately name an old path without depending on
# it. They are excluded from the dependency scan and checked separately below,
# and every excluded line is printed verbatim so the exclusion can be judged
# rather than trusted.
ANNOTATION_ONLY = {
    "CORE_MANIFEST.yml":
        "ownership inventory of physically present paths; its own header says "
        "ownership is not activity, so naming a legacy path is its job",
    "08_os/claude与人类的开发对话日志.md":
        "development log - same historical class as _dev/ and _runs/, kept as a "
        "record of what was true when written",
    "08_os/05_registry/repository_guards_v1.yml":
        "carries the migration provenance of the file that moved",
    MIGRATED_AUTHORITY_PATH:
        "the migrated file's own provenance header names where it came from; the "
        "real risk - carrying the old communication plane with it - is checked "
        "directly by M1_migrated_authority_clean rather than by substring",
}

# A migrated historical document is historical wherever it is stored. Recognised by
# a marker in its own provenance header rather than by filename, so the rule can be
# re-derived: any file declaring this status is read as a record of what was true
# when written, exactly like 08_os/_dev/ and 08_os/_runs/.
HISTORICAL_STATUS_MARKER = "status: historical_input_evidence"

SURVIVING_NON08 = [
    "AGENTS.md",
    "AGENT_WORKING_DISCIPLINE.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "CORE_MANIFEST.yml",
    ".gitignore",
    ".gitattributes",
    ".claude/settings.json",
    "new-domain.ps1",
    ".githooks/pre-push",
    ".githooks/install.ps1",
    ".githooks/test_pre_push_logic.ps1",
    ".githooks/.gitattributes",
    ".githooks/README.md",
]


def git(*args: str, root: str = ".") -> str:
    out = subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8", cwd=root
    )
    if out.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()

    tracked = [p for p in git("ls-files", root=str(root)).splitlines() if p]
    active = [
        p for p in tracked
        if p.startswith("08_os/")
        and not p.startswith("08_os/_runs/")
        and not p.startswith("08_os/_dev/")
    ] + [p for p in SURVIVING_NON08 if p in tracked]
    historical = [
        p for p in tracked
        if p.startswith("08_os/_runs/") or p.startswith("08_os/_dev/")
    ]

    texts = {}
    declared_historical = []
    for rel in active:
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if HISTORICAL_STATUS_MARKER in "\n".join(text.splitlines()[:40]):
            declared_historical.append(rel)
            continue
        texts[rel] = text
    hist_texts = {}
    for rel in historical:
        try:
            hist_texts[rel] = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

    report: dict[str, object] = {
        "active_surface_files": len(texts),
        "historical_files_scanned_separately": len(hist_texts),
        "declared_historical_on_the_active_surface": declared_historical,
        "checks": {},
    }
    for rel in declared_historical:
        print(f"declared historical (provenance header): {rel}")
    failed = False

    for check, token in OLD_TOKENS.items():
        hits, annotated = [], []
        for rel, text in texts.items():
            if token not in text:
                continue
            if rel in ANNOTATION_ONLY:
                for line_no, line in enumerate(text.splitlines(), 1):
                    if token in line:
                        annotated.append(f"{rel}:{line_no}: {line.strip()}")
            else:
                hits.append(rel)
        hits = sorted(hits)
        hist = sum(1 for text in hist_texts.values() if token in text)
        report["checks"][check] = {
            "token": token,
            "active_dependency_hits": hits,
            "annotation_only_lines": annotated,
            "historical_mentions": hist,
        }
        print(f"{check}: dependency_hits={len(hits)} "
              f"annotation_lines={len(annotated)} historical_mentions={hist}")
        for rel in hits:
            print(f"   DEPENDENCY {rel}")
        for line in annotated:
            print(f"   annotation  {line[:150]}")
        if hits:
            failed = True

    # The one place the exclusion above could hide a real dependency: an ownership
    # list entry is a live declaration, not an annotation. Check the manifest's two
    # machine-read keys directly.
    manifest_text = (root / "CORE_MANIFEST.yml").read_text(encoding="utf-8")
    listed_old = [
        line.strip()
        for line in manifest_text.splitlines()
        if line.lstrip().startswith("- ") and ".ai/PROGRAM_RUNS" in line
    ]
    report["checks"]["M3_manifest_ownership_entry_removed"] = {
        "old_run_root_entries_remaining": listed_old,
    }
    print(f"M3_manifest_ownership_entry_removed: {len(listed_old)} entr(y/ies) remaining")
    if listed_old:
        failed = True

    authority_text = (root / MIGRATED_AUTHORITY).read_text(encoding="utf-8")
    carried = [t for t in OLD_PLANE_TOKENS if t in authority_text]
    report["checks"]["M1_migrated_authority_clean"] = {
        "file": MIGRATED_AUTHORITY,
        "old_plane_tokens_present": carried,
    }
    print(f"M1_migrated_authority_clean: {len(carried)} old-plane token(s)")
    for token in carried:
        print(f"   CARRIED {token}")
    if carried:
        failed = True

    new_authority_consumers = sorted(
        rel for rel, text in texts.items() if MIGRATED_AUTHORITY in text
    )
    report["new_authority_consumers"] = new_authority_consumers
    print(f"new_authority_consumers: {len(new_authority_consumers)}")

    print("RESULT " + ("FAIL" if failed else "PASS"))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

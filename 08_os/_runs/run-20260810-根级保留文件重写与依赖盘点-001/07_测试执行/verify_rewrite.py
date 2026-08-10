#!/usr/bin/env python3
"""Validation for the root-global retention rewrite.

Four checks, all against physical repository state, none against expectation:

  R1  every repository-relative path referenced by a rewritten retained file
      resolves in the tracked tree at the current head
  R2  legacy startup/communication tokens surviving in the rewritten files are
      listed with file:line so each one can be explained rather than assumed gone
  R3  the retained .githooks executables are byte-identical to the task base
  R4  the rewritten YAML parses and still carries the keys its machine consumer
      reads by name

Exit 0 when R1, R3 and R4 pass. R2 never fails on its own: it prints the hits,
because whether a hit is a live dependency or prose about an obsolete path is a
judgement the report has to make in words.

Usage
    python verify_rewrite.py --base <40-char-sha>
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REWRITTEN = [
    "AGENTS.md",
    "AGENT_WORKING_DISCIPLINE.md",
    "GEMINI.md",
    "CLAUDE.md",
    "README.md",
    "CORE_MANIFEST.yml",
    ".githooks/README.md",
]

FROZEN_INFRA = [
    ".githooks/pre-push",
    ".githooks/install.ps1",
    ".githooks/test_pre_push_logic.ps1",
    ".githooks/.gitattributes",
]

LEGACY_TOKENS = [
    "06_Silicon_Index",
    "05_Carbon_Index",
    "04_Parliament",
    "07_Compiler",
    "system_backbone",
    "AI_Bootstrap_Sequence",
    "load_profiles",
    "TOKEN_USAGE_PROFILE",
    "TOKEN_USAGE_OPERATIONAL_NORMS",
    ".ai/PROTOCOL",
    ".ai/STATE.yml",
    ".ai/INBOX",
    ".ai/OUTBOX",
    ".ai/HUMAN_BRIEF",
    "CODEX_WORK_MECHANISM",
    "CODEX_TASK_INPUT_CONTRACT",
    "LONG_RUN_AUTONOMOUS",
    "HANDOFF_INIT_PROMPT",
    "lane_epoch",
    "communication_compliance",
    "role_memory",
    "token_profile",
    "3号方案",
    "PROJECT_CONTEXT",
    "ARCHITECTURE.md",
    "REPOSITORY_PUBLISHER_AUTHORITY",
    "PROGRAM_RUNS",
    "seven-field",
    "mailbox",
]

# A backticked token that looks like a repository path: ends in a known extension,
# or ends in "/" and therefore names a directory.
PATH_RE = re.compile(
    r"`([0-9A-Za-z_.一-鿿][0-9A-Za-z_./\-一-鿿]*"
    r"(?:\.(?:md|yml|yaml|py|ps1|json|sh)|/))`"
)
MD_LINK_RE = re.compile(r"\]\(([^)]+)\)")

# Documented vendor conventions that deliberately do NOT exist in this repository.
# GEMINI.md describes what Antigravity would load if these were added; naming a
# convention is not depending on a file. Listed explicitly so the check stays
# strict for everything else.
DOCUMENTED_ABSENT = {
    ".agents/",
    ".agent/",
    "_agents/",
    "_agent/",
    ".agents/rules/",
    "rules/",
    "hooks.json",
    "mcp_config.json",
    "skills/",
    "plugins/",
}


def git(*args: str) -> str:
    out = subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8"
    )
    if out.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()

    tracked = set(git("ls-files").splitlines())
    dirs = set()
    for path in tracked:
        parts = path.split("/")
        for i in range(1, len(parts)):
            dirs.add("/".join(parts[:i]) + "/")

    failed = False

    # R1 -----------------------------------------------------------------
    unresolved: list[str] = []
    checked = 0
    for rel in REWRITTEN:
        text = (root / rel).read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            candidates = set(PATH_RE.findall(line))
            candidates |= {
                target
                for target in MD_LINK_RE.findall(line)
                if not target.startswith(("http://", "https://", "#"))
            }
            for cand in candidates:
                cand = cand.split("#", 1)[0]
                if not cand or cand.startswith("~") or "*" in cand:
                    continue
                if cand in DOCUMENTED_ABSENT:
                    continue
                checked += 1
                # Repository-relative, or relative to the referring file's own
                # directory: .githooks/README.md naming `install.ps1` means its
                # sibling, and that is a real resolvable reference.
                sibling = str(Path(rel).parent / cand).replace("\\", "/")
                if cand in tracked or cand in dirs:
                    continue
                if sibling in tracked or sibling + "/" in dirs:
                    continue
                unresolved.append(f"{rel}:{lineno}: {cand}")
    print(f"R1 referenced-path resolution: {checked} checked, "
          f"{len(unresolved)} unresolved")
    for item in unresolved:
        print(f"   UNRESOLVED {item}")
    if unresolved:
        failed = True

    # R2 -----------------------------------------------------------------
    hits: list[str] = []
    for rel in REWRITTEN:
        text = (root / rel).read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            for token in LEGACY_TOKENS:
                if token in line:
                    hits.append(f"{rel}:{lineno}: {token}")
    print(f"R2 legacy tokens surviving in rewritten files: {len(hits)} "
          f"(each must be explained in the report)")
    for item in hits:
        print(f"   HIT {item}")

    # R3 -----------------------------------------------------------------
    diff = git("diff", "--name-only", args.base, "--", *FROZEN_INFRA).split()
    print(f"R3 frozen .githooks infrastructure changed vs base: {len(diff)}")
    for item in diff:
        print(f"   CHANGED {item}")
    if diff:
        failed = True

    # R4 -----------------------------------------------------------------
    try:
        import yaml
    except ImportError:
        print("R4 yaml parse: SKIPPED (PyYAML unavailable)")
        failed = True
    else:
        data = yaml.safe_load((root / "CORE_MANIFEST.yml").read_text(encoding="utf-8"))
        core = data.get("core_owned_paths") or []
        domain = data.get("domain_owned_paths") or []
        problems = []
        for required in (
            "08_os/README.md",
            "08_os/01_workflow/",
            "08_os/02_boot/",
            "08_os/03_mechanisms/",
            "08_os/04_skills_and_tools/",
            "08_os/05_registry/",
            "08_os/06_execution/",
            "08_os/_dev/",
            "08_os/_runs/",
            "08_os/claude与人类的开发对话日志.md",
        ):
            if required not in core:
                problems.append(f"core_owned_paths missing {required}")
        for required in ("08_os/07_content/", ".ai/PROGRAM_RUNS/"):
            if required not in domain:
                problems.append(f"domain_owned_paths missing {required}")
        for left in core:
            for right in domain:
                if left.startswith(right) or right.startswith(left):
                    problems.append(f"ownership overlap {left} <> {right}")
        # every core-owned path must exist; domain-owned paths may be empty in core
        for path in core:
            if path.endswith("/"):
                if not any(t.startswith(path) for t in tracked):
                    problems.append(f"core_owned_paths absent from tree: {path}")
            elif path not in tracked:
                problems.append(f"core_owned_paths absent from tree: {path}")
        print(f"R4 CORE_MANIFEST.yml parse + ownership contract: "
              f"{len(problems)} problem(s)")
        for item in problems:
            print(f"   PROBLEM {item}")
        if problems:
            failed = True

    print("RESULT " + ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

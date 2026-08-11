"""Verify the final repository-wide always-on bootstrap correction."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml


CORRECTION_BASE = "89f7c916529961aef51cd235bc08e8be09a9d239"
FORMER_NAMESPACE = "08" + "_os"
STARTUP_SURFACES = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "01_os/README.md",
    "01_os/开发入口与单窗口任务规范_v1.md",
)
ENTRY_POINTERS = (
    "01_os/README.md",
    "01_os/开发入口与单窗口任务规范_v1.md",
)
EXPECTED_CHANGED_PATHS = {
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "01_os/README.md",
    "01_os/开发入口与单窗口任务规范_v1.md",
    "01_os/_runs/run-20260810-01OS命名空间与默认加载切换-001/run.yml",
    "01_os/_runs/run-20260810-01OS命名空间与默认加载切换-001/04_验证/verify_final_always_on_bootstrap.py",
    "01_os/_runs/run-20260810-01OS命名空间与默认加载切换-001/04_验证/final_bootstrap_quiet_checks_v1.yml",
    "01_os/_runs/run-20260810-01OS命名空间与默认加载切换-001/04_验证/final_bootstrap_validation_receipt_v1.yml",
}
MACHINE_READABLE_EVIDENCE = (
    "01_os/_runs/run-20260810-01OS命名空间与默认加载切换-001/run.yml",
    "01_os/_runs/run-20260810-01OS命名空间与默认加载切换-001/04_验证/final_bootstrap_quiet_checks_v1.yml",
    "01_os/_runs/run-20260810-01OS命名空间与默认加载切换-001/04_验证/final_bootstrap_validation_receipt_v1.yml",
)
COMMUNICATION_TREES = {
    "01_os/02_boot/communication_system": "be6d130ae990f3bbe786f805b987aad433179f12",
    "01_os/03_mechanisms/communication_system": "f0768998f11724f6d03d2a44b11347e911a65b60",
    "01_os/06_execution/boot/communication_system": "ab23f8be8beeebf979c2b75e08efb7cd3e294ff7",
}
REQUIRED_IN_EVERY_SURFACE = (
    "repository-wide always-on",
    "01_os/README.md",
    "01_os/开发入口与单窗口任务规范_v1.md",
    "current Human natural-language request",
    "durable task packet",
    "material repository mutation",
    "business/canonical write",
    "01_os/_runs/**",
)
CONDITIONAL_PATTERNS = (
    re.compile(r"\b(?:when|if) the task touches the OS\b", re.IGNORECASE),
    re.compile(r"处理\s*`01_os`\s*开发任务的新窗口"),
)


def fail(message: str) -> None:
    raise ValueError(message)


def git(repo: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        fail(f"git_failed:{' '.join(args)}:{proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def verify(repo: Path) -> dict[str, int]:
    for pointer in ENTRY_POINTERS:
        if not (repo / pointer).is_file():
            fail(f"missing_entry_pointer:{pointer}")

    conditional_count = 0
    for surface in STARTUP_SURFACES:
        text = (repo / surface).read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for required in REQUIRED_IN_EVERY_SURFACE:
            if required not in normalized:
                fail(f"startup_contract_missing:{surface}:{required}")
        conditional_count += sum(len(pattern.findall(text)) for pattern in CONDITIONAL_PATTERNS)
    if conditional_count:
        fail(f"conditional_OS_bootstrap_residue:{conditional_count}")

    tracked = [
        item.decode("utf-8", "surrogateescape")
        for item in git(repo, "ls-files", "-z").split(b"\0")
        if item
    ]
    path_residue = [path for path in tracked if FORMER_NAMESPACE in path]
    content_residue = [
        path
        for path in tracked
        if (repo / path).is_file()
        and FORMER_NAMESPACE.encode("ascii") in (repo / path).read_bytes()
    ]
    if path_residue or content_residue:
        fail(f"former_namespace_residue:paths={len(path_residue)}:content={len(content_residue)}")

    changed_paths = {
        item.decode("utf-8", "surrogateescape")
        for item in git(repo, "diff", "--name-only", "-z", CORRECTION_BASE, "--").split(b"\0")
        if item
    }
    if changed_paths != EXPECTED_CHANGED_PATHS:
        fail(f"changed_path_scope_mismatch:{sorted(changed_paths ^ EXPECTED_CHANGED_PATHS)}")

    for path in MACHINE_READABLE_EVIDENCE:
        parsed = yaml.safe_load((repo / path).read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            fail(f"machine_readable_evidence_invalid:{path}")

    for path, expected_tree in COMMUNICATION_TREES.items():
        base_tree = git(repo, "rev-parse", f"{CORRECTION_BASE}:{path}").decode().strip()
        if base_tree != expected_tree:
            fail(f"communication_base_tree_mismatch:{path}:{base_tree}")
        if git(repo, "diff", "--name-only", CORRECTION_BASE, "--", path).strip():
            fail(f"communication_tree_changed:{path}")
        if git(repo, "status", "--porcelain=v1", "--untracked-files=all", "--", path).strip():
            fail(f"communication_worktree_changed:{path}")

    return {
        "startup_surfaces": len(STARTUP_SURFACES),
        "entry_pointers": len(ENTRY_POINTERS),
        "conditional_bootstrap_phrases": conditional_count,
        "former_namespace_paths": len(path_residue),
        "former_namespace_content_files": len(content_residue),
        "communication_trees_unchanged": len(COMMUNICATION_TREES),
        "changed_paths_in_scope": len(changed_paths),
        "machine_readable_evidence_parsed": len(MACHINE_READABLE_EVIDENCE),
    }


def main() -> int:
    try:
        result = verify(Path.cwd().resolve())
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        print(f"final_bootstrap_verify_error:{exc}", file=sys.stderr)
        return 1
    print("final_bootstrap_verify_ok " + " ".join(f"{key}={value}" for key, value in result.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

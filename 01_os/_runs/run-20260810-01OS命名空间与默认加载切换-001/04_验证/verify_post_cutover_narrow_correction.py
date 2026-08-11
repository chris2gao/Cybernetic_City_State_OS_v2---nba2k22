"""Verify post-cutover lexical, startup, ownership and routing closure."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml


FORMER_NAMESPACE = "08" + "_os"
CURRENT_NAMESPACE = "01_os"
ROOT_OS_FILES = {
    "01_os/README.md",
    "01_os/claude与人类的开发对话日志.md",
    "01_os/开发入口与单窗口任务规范_v1.md",
}
STARTUP_POINTERS = {
    "AGENT_WORKING_DISCIPLINE.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "CORE_MANIFEST.yml",
    "01_os/README.md",
    "01_os/开发入口与单窗口任务规范_v1.md",
    "01_os/03_mechanisms/communication_system/通讯契约_v1.yml",
    "01_os/03_mechanisms/communication_system/消息契约_v1.yml",
    "01_os/06_execution/boot/communication_system/task_space_initializer/initialize_task_space.py",
}


def fail(message: str) -> None:
    raise ValueError(message)


def git(repo: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", *args], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if proc.returncode != 0:
        fail(f"git_failed:{' '.join(args)}:{proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def verify(repo: Path) -> dict[str, int]:
    tracked = [
        item.decode("utf-8", "surrogateescape")
        for item in git(repo, "ls-files", "-z").split(b"\0")
        if item
    ]
    path_residue = [path for path in tracked if FORMER_NAMESPACE in path]
    content_residue = [
        path for path in tracked
        if (repo / path).is_file() and FORMER_NAMESPACE.encode("ascii") in (repo / path).read_bytes()
    ]
    if path_residue or content_residue:
        fail(f"former_namespace_residue:paths={len(path_residue)}:content={len(content_residue)}")
    if any(not (repo / path).is_file() for path in STARTUP_POINTERS):
        fail("startup_pointer_missing")

    actual_root_files = {
        path.relative_to(repo).as_posix()
        for path in (repo / CURRENT_NAMESPACE).iterdir()
        if path.is_file()
    }
    if actual_root_files != ROOT_OS_FILES:
        fail(f"unexpected_OS_root_file_set:{sorted(actual_root_files ^ ROOT_OS_FILES)}")
    manifest = yaml.safe_load((repo / "CORE_MANIFEST.yml").read_text(encoding="utf-8"))
    core_owned = set(manifest.get("core_owned_paths") or [])
    if not ROOT_OS_FILES.issubset(core_owned):
        fail("OS_root_file_not_owned")

    agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
    if "chatgpt-web-planner-01" in agents or re.search(
        r"expected_recipient_endpoint_id\s*:\s*[A-Za-z0-9]", agents
    ):
        fail("hardcoded_communication_endpoint_in_shared_startup")
    for required in (
        "current task manifest", "endpoint cards", "sender index",
        "Ordinary Human-facing output remains valid", "Human-triggered and Human-relayed",
    ):
        if required not in agents:
            fail(f"shared_handoff_rule_incomplete:{required}")

    startup = "\n".join(
        (repo / path).read_text(encoding="utf-8")
        for path in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "README.md")
    )
    if "awaiting Human retirement" in startup:
        fail("stale_retirement_wording")
    if "PROJECT_CONTEXT.md" in agents or "ARCHITECTURE.md" in agents:
        fail("deleted_document_current_guidance")
    core_manifest_text = (repo / "CORE_MANIFEST.yml").read_text(encoding="utf-8")
    if "The eventual move of 01_os/** to the repository root" in core_manifest_text:
        fail("future_root_lift_still_current")

    moved = {
        "01_os/04_skills_and_tools/模型与供应商能力清单_v1.md":
            "01_os/05_registry/skills_and_tools_v1.yml",
        "01_os/_dev/后续验证候选关注点_20260729_已取代.md":
            "01_os/05_registry/context_management_v1.yml",
    }
    for target, registry in moved.items():
        if not (repo / target).is_file():
            fail(f"moved_document_missing:{target}")
        if target not in (repo / registry).read_text(encoding="utf-8"):
            fail(f"moved_document_unregistered:{target}")
    if (repo / "01_os/可使用的独立模型和角色.md").exists() or (
        repo / "01_os/后续验证候选关注点.md"
    ).exists():
        fail("unowned_OS_root_source_still_present")

    return {
        "tracked_total": len(tracked),
        "tracked_under_01_os": sum(path.startswith("01_os/") for path in tracked),
        "former_namespace_paths": 0,
        "former_namespace_content_files": 0,
        "startup_pointers": len(STARTUP_POINTERS),
        "owned_OS_root_files": len(ROOT_OS_FILES),
        "moved_registered_documents": len(moved),
    }


def main() -> int:
    try:
        result = verify(Path.cwd().resolve())
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"post_cutover_verify_error:{exc}", file=sys.stderr)
        return 1
    print("post_cutover_verify_ok " + " ".join(f"{key}={value}" for key, value in result.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

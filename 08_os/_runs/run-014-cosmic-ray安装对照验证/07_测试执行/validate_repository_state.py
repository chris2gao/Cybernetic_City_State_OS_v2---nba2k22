from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import yaml


BASE = "a6261cf3a8f0e0263b41a6ec32a3dd6c16ed653c"
RUN_REL = Path("08_os/_runs/run-014-cosmic-ray安装对照验证")
ALLOWED_EXACT = {
    "08_os/04_skills_and_tools/README.md",
    "08_os/05_registry/skills_and_tools_v1.yml",
}
ALLOWED_PREFIXES = (
    "08_os/04_skills_and_tools/cosmic-ray/",
    "08_os/06_execution/tools/cosmic_ray/",
    f"{RUN_REL.as_posix()}/",
)
FORBIDDEN_PREFIXES = (
    "08_os/02_boot/",
    "08_os/06_execution/tools/check_jsonschema/",
    "08_os/06_execution/tools/mutmut/",
    "08_os/_runs/run-012-check-jsonschema安装接入验证/",
    "08_os/_runs/run-013-mutmut安装接入验证/",
    "07_Compiler/",
)


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve(strict=True)
    run = repo / RUN_REL
    results = json.loads((run / "07_测试执行/results.json").read_text(encoding="utf-8"))
    matrix = json.loads(
        (run / "07_测试执行/evidence/wrapper_matrix.json").read_text(encoding="utf-8")
    )
    environment = json.loads(
        (run / "07_测试执行/evidence/environment_receipt.json").read_text(encoding="utf-8")
    )
    run_yml = yaml.safe_load((run / "run.yml").read_text(encoding="utf-8"))
    registry = yaml.safe_load(
        (repo / "08_os/05_registry/skills_and_tools_v1.yml").read_text(encoding="utf-8")
    )

    changed = [
        path
        for path in git(repo, "-c", "core.quotepath=false", "diff", "--name-only", BASE, "HEAD")
        .splitlines()
        if path
    ]
    outside = [
        path
        for path in changed
        if path not in ALLOWED_EXACT and not path.startswith(ALLOWED_PREFIXES)
    ]
    forbidden = [path for path in changed if path.startswith(FORBIDDEN_PREFIXES)]
    check(not outside, f"changed paths outside allowlist: {outside}")
    check(not forbidden, f"forbidden paths changed: {forbidden}")
    check(git(repo, "diff", "--check", BASE, "HEAD") == "", "git diff --check failed")

    check(results["passed"] is True, "results did not pass")
    check(
        results["adoption_decision"]["decision"] == "verified_on_demand",
        "adoption decision mismatch",
    )
    check(results["adoption_decision"]["qualified"] is True, "qualification missing")
    check(matrix["passed"] is True and matrix["case_count"] >= 18, "wrapper matrix failed")
    check(matrix["repository_unchanged"] is True, "wrapper changed repository")
    check(matrix["temporary_workspace_cleanup"] is True, "wrapper cleanup failed")
    check(not matrix["process_residue"], "wrapper process residue")
    check(
        results["blob_evidence"]["canonical_target"]["unchanged"],
        "canonical target blob changed",
    )
    check(
        results["blob_evidence"]["enhanced_test"]["unchanged"],
        "enhanced test blob changed",
    )
    check(
        environment["git_evidence_classes"]["local_tracking_used_for_authoritative_relation"]
        is False,
        "local tracking ref was used as authority",
    )

    manifest_path = run / "07_测试执行/evidence/experiments/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    check(manifest["file_count"] >= 1, "evidence manifest empty")
    for entry in manifest["files"]:
        path = manifest_path.parent / entry["path"]
        check(path.is_file(), f"manifest file missing: {entry['path']}")
        check(path.stat().st_size == entry["bytes"], f"size mismatch: {entry['path']}")
        check(sha256(path) == entry["sha256"], f"hash mismatch: {entry['path']}")

    tools = {item["name"]: item for item in registry["tools"]}
    cosmic = tools.get("cosmic-ray")
    check(isinstance(cosmic, dict), "Cosmic Ray missing from registry")
    expected_registry = {
        "version": "8.4.6",
        "status": "verified_on_demand",
        "mount": "on_demand_wsl_cli",
        "default_loaded": False,
        "mcp_exposed": False,
        "distributor": "local",
        "workers": 1,
        "canonical_wrapper": "08_os/06_execution/tools/cosmic_ray/invoke.sh",
    }
    for key, expected in expected_registry.items():
        check(cosmic.get(key) == expected, f"registry {key} mismatch")

    check(run_yml["tool"]["status"] == "verified_on_demand", "run.yml status mismatch")
    check(run_yml["status"] == "candidate_ready_for_independent_review", "run status mismatch")
    wrapper_mode = git(repo, "ls-files", "-s", "08_os/06_execution/tools/cosmic_ray/invoke.sh")
    check(wrapper_mode.startswith("100755 "), "wrapper is not executable in Git")

    canonical_files = [
        repo / "08_os/04_skills_and_tools/cosmic-ray/README.md",
        repo / "08_os/06_execution/tools/cosmic_ray/README.md",
        repo / "08_os/06_execution/tools/cosmic_ray/invoke.sh",
        repo / "08_os/06_execution/tools/cosmic_ray/summarize.py",
        repo / "08_os/05_registry/skills_and_tools_v1.yml",
    ]
    forbidden_text = ["/home/gk", "BEGIN PRIVATE KEY", "ghp_", "password="]
    for path in canonical_files:
        text = path.read_text(encoding="utf-8")
        for needle in forbidden_text:
            check(needle not in text, f"forbidden canonical text {needle!r} in {path}")

    summary = {
        "PASS": 14,
        "changed_paths": len(changed),
        "evidence_files": manifest["file_count"],
        "wrapper_cases": matrix["case_count"],
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

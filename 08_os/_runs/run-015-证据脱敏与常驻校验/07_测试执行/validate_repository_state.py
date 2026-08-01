from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import yaml


BASE = "07cdc1c76b38bc5a65dbcfb72376f1b6008b5626"
RUN = Path("08_os/_runs/run-015-证据脱敏与常驻校验")
RUN_012 = Path("08_os/_runs/run-012-check-jsonschema安装接入验证")
RUN_013 = Path("08_os/_runs/run-013-mutmut安装接入验证")
RUN_014 = Path("08_os/_runs/run-014-cosmic-ray安装对照验证")
VALIDATOR = Path("08_os/06_execution/validators/personal_paths/validate.py")
REGISTRY = Path("08_os/05_registry/repository_validation_v1.yml")
ALLOWED_PREFIXES = (
    f"{RUN_012.as_posix()}/",
    f"{RUN_013.as_posix()}/",
    f"{RUN.as_posix()}/",
    "08_os/06_execution/",
    "08_os/05_registry/",
)


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def candidate_paths(repo: Path) -> list[str]:
    commands = (
        ("diff", "--name-only", "--diff-filter=ACMR", BASE, "HEAD"),
        ("diff", "--name-only", "--diff-filter=ACMR"),
        ("diff", "--cached", "--name-only", "--diff-filter=ACMR"),
        ("ls-files", "--others", "--exclude-standard"),
    )
    paths: set[str] = set()
    for command in commands:
        paths.update(line for line in git(repo, *command).stdout.splitlines() if line)
    return sorted(paths)


def run_path_validator(repo: Path, mode: str, *scopes: str) -> tuple[int, dict[str, Any]]:
    command = [
        sys.executable,
        str(repo / VALIDATOR),
        "--repo-root",
        str(repo),
        "--mode",
        mode,
        "--summary-only",
    ]
    if mode == "changed":
        command.extend(("--base", BASE))
    command.extend(scopes)
    completed = subprocess.run(
        command,
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode not in (0, 1):
        raise AssertionError(f"path validator error: {completed.stderr.strip()}")
    summary = json.loads(completed.stdout.splitlines()[-1])
    return completed.returncode, summary


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve(strict=True)
    changed = candidate_paths(repo)
    outside = [path for path in changed if not path.startswith(ALLOWED_PREFIXES)]
    check(not outside, f"changed paths outside allowlist: {outside}")
    check(not any(path.startswith(f"{RUN_014.as_posix()}/") for path in changed), "run-014 changed")
    check(git(repo, "diff", "--check", BASE, "HEAD").stdout == "", "committed diff --check failed")
    check(git(repo, "diff", "--check").stdout == "", "worktree diff --check failed")
    check(git(repo, "diff", "--cached", "--check").stdout == "", "staged diff --check failed")

    recorded = (repo / RUN / "06_执行/changed_paths.txt").read_text(encoding="utf-8").splitlines()
    check(recorded == changed, "changed_paths.txt does not equal sorted candidate paths")

    run012_code, run012 = run_path_validator(repo, "tracked", RUN_012.as_posix())
    run013_code, run013 = run_path_validator(repo, "tracked", RUN_013.as_posix())
    run014_code, run014 = run_path_validator(repo, "tracked", RUN_014.as_posix())
    changed_code, changed_summary = run_path_validator(repo, "changed")
    full_code, full_summary = run_path_validator(repo, "tracked")
    check(run012_code == 0 and run012["hit_count"] == 0, "run-012 still contains personal paths")
    check(run013_code == 0 and run013["hit_count"] == 0, "run-013 still contains personal paths")
    check(run014_code == 0 and run014["hit_count"] == 0, "run-014 personal-path baseline changed")
    check(changed_code == 0 and changed_summary["hit_count"] == 0, "candidate contains personal paths")

    json.loads((repo / RUN_013 / "01_任务输入/environment_receipt.json").read_text(encoding="utf-8"))
    json.loads((repo / RUN_013 / "07_测试执行/results.json").read_text(encoding="utf-8"))
    results = json.loads((repo / RUN / "07_测试执行/results.json").read_text(encoding="utf-8"))
    recorded_full = results["full_repository"]
    check(full_code == 1, "full repository should retain reported out-of-scope findings")
    check(full_summary["candidate_files"] == recorded_full["tracked_candidate_files"], "full candidate count drift")
    check(full_summary["hit_count"] == recorded_full["hits"], "full hit count drift")
    check(full_summary["hit_files"] == recorded_full["hit_files"], "full hit-file count drift")
    check(full_summary["hit_counts_by_top_level"] == recorded_full["hit_counts_by_top_level"], "full top-level breakdown drift")
    registry = yaml.safe_load((repo / REGISTRY).read_text(encoding="utf-8"))
    run_yml = yaml.safe_load((repo / RUN / "run.yml").read_text(encoding="utf-8"))
    check(run_yml["implementation_base"] == BASE, "run base mismatch")
    check(run_yml["status"] == "candidate_ready_for_independent_review", "run status not ready")
    entries = registry.get("validators", [])
    check(len(entries) == 5, "registry must contain five validator artifacts")
    for entry in entries:
        required = {
            "path",
            "purpose",
            "loader",
            "loader_class",
            "discovery",
            "evidence",
            "cache_dirs",
            "failure_surfacing",
            "deletion_rule",
        }
        check(required.issubset(entry), f"registry entry missing fields: {entry.get('path')}")
        check((repo / entry["path"]).is_file(), f"registered path missing: {entry['path']}")

    binary_count = 0
    for relative in changed:
        path = repo / relative
        if not path.is_file() or path.is_symlink():
            continue
        data = path.read_bytes()
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            binary_count += 1
    check(binary_count == 0, f"binary artifacts in candidate: {binary_count}")

    summary = {
        "status": "passed",
        "changed_paths": len(changed),
        "out_of_scope_paths": len(outside),
        "binary_artifact_count": binary_count,
        "run012_hits": run012["hit_count"],
        "run013_hits": run013["hit_count"],
        "run014_hits": run014["hit_count"],
        "candidate_hits": changed_summary["hit_count"],
        "full_repository_hits": full_summary["hit_count"],
        "registry_entries": len(entries),
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

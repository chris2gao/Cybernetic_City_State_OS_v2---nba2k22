from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import yaml


ORIGINAL_BASE = "492fa24abf9ae9b41d3ccdc86c012fb66f149a36"
CORRECTION_BASE = "f4c76e4e49a148d290e4476b2c2c03da03707bc9"
RUN_PREFIX = "08_os/_runs/run-020-环境能力发现最小版/"
EXACT_ALLOWED = {
    "08_os/03_mechanisms/environment_capability/实现/环境能力receipt_schema_v1.yml",
    "08_os/03_mechanisms/environment_capability/实现/正例与负例说明_v1.md",
    "08_os/_runs/run-020-环境能力发现最小版/run.yml",
}


def run(repo: Path, args: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, cwd=repo, capture_output=True, check=False)


def decode_nul_paths(raw: bytes) -> list[str]:
    return [item.decode("utf-8") for item in raw.split(b"\0") if item]


def allowed(path: str) -> bool:
    return path in EXACT_ALLOWED or path.startswith(f"{RUN_PREFIX}07_测试执行/")


def main() -> int:
    repo = Path(__file__).resolve().parents[4]
    run_root = repo / RUN_PREFIX
    output_path = run_root / "07_测试执行" / "final_validation.json"
    output_path.write_text("{}\n", encoding="utf-8")

    checks: dict[str, Any] = {}

    schema_matrix = run(
        repo,
        ["pwsh", "-NoProfile", "-File", f"{RUN_PREFIX}07_测试执行/validate_candidate.ps1"],
    )
    checks["schema_matrix"] = {"exit_code": schema_matrix.returncode, "passed": schema_matrix.returncode == 0}

    fix_round1 = run(
        repo,
        ["python", f"{RUN_PREFIX}07_测试执行/fix_round1_validation.py"],
    )
    checks["fix_round1_matrix"] = {"exit_code": fix_round1.returncode, "passed": fix_round1.returncode == 0}

    receipt_ref = f"{RUN_PREFIX}08_结论/环境能力receipt_实测_v1.yml"
    independent = run(
        repo,
        ["python", f"{RUN_PREFIX}07_测试执行/independent_receipt_check.py", receipt_ref, "--schema-exit", "0"],
    )
    checks["independent_receipt"] = {
        "exit_code": independent.returncode,
        "passed": independent.returncode == 0,
    }

    personal_paths = run(
        repo,
        [
            "python",
            "08_os/06_execution/validators/personal_paths/validate.py",
            "--repo-root",
            ".",
            "--mode",
            "changed",
            "--base",
            ORIGINAL_BASE,
        ],
    )
    personal_summary: dict[str, Any] = {}
    try:
        personal_summary = json.loads(personal_paths.stdout.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        personal_summary = {"parse": "failed"}
    checks["personal_paths"] = {
        "exit_code": personal_paths.returncode,
        "passed": personal_paths.returncode == 0,
        "candidate_files": personal_summary.get("candidate_files"),
        "hit_count": personal_summary.get("hit_count"),
    }

    diff_check = run(repo, ["git", "diff", "--check"])
    checks["git_diff_check"] = {"exit_code": diff_check.returncode, "passed": diff_check.returncode == 0}

    changed = run(repo, ["git", "diff", "--name-only", "-z", CORRECTION_BASE])
    untracked = run(repo, ["git", "ls-files", "--others", "--exclude-standard", "-z"])
    changed_paths = sorted(set(decode_nul_paths(changed.stdout) + decode_nul_paths(untracked.stdout)))
    out_of_scope = [path for path in changed_paths if not allowed(path)]
    checks["scope"] = {
        "passed": changed.returncode == 0 and untracked.returncode == 0 and not out_of_scope,
        "changed_path_count": len(changed_paths),
        "out_of_scope_paths": out_of_scope,
    }

    readme_diff = run(repo, ["git", "diff", "--unified=0", CORRECTION_BASE, "--", "08_os/03_mechanisms/README.md"])
    diff_lines = readme_diff.stdout.decode("utf-8", errors="replace").splitlines()
    additions = [line for line in diff_lines if line.startswith("+") and not line.startswith("+++")]
    removals = [line for line in diff_lines if line.startswith("-") and not line.startswith("---")]
    checks["mechanism_navigation_delta"] = {
        "passed": readme_diff.returncode == 0 and not additions and not removals,
        "added_lines": len(additions),
        "removed_lines": len(removals),
    }

    parse_targets = {
        "schema": repo / "08_os/03_mechanisms/environment_capability/实现/环境能力receipt_schema_v1.yml",
        "receipt": repo / receipt_ref,
        "schema_results": run_root / "07_测试执行/results.json",
    }
    parse_failures: list[str] = []
    for name, path in parse_targets.items():
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            parse_failures.append(name)
    for name, path in {
        "registry": repo / "08_os/05_registry/environment_capability_v1.yml",
        "run_manifest": run_root / "run.yml",
    }.items():
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError):
            parse_failures.append(name)
    checks["structured_parse"] = {"passed": not parse_failures, "failures": parse_failures}

    runtime_exists = (run_root / "_runtime").exists()
    forbidden_artifacts = [
        path.relative_to(repo).as_posix()
        for path in run_root.rglob("*")
        if path.is_file()
        and ("__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo", ".exe", ".dll"})
    ]
    checks["artifact_hygiene"] = {
        "passed": not runtime_exists and not forbidden_artifacts,
        "runtime_exists": runtime_exists,
        "forbidden_artifacts": forbidden_artifacts,
    }

    all_passed = all(bool(item.get("passed")) for item in checks.values())
    result = {
        "schema_version": "environment_capability_final_validation.v1",
        "base": CORRECTION_BASE,
        "checks": checks,
        "changed_paths": changed_paths,
        "summary": {"all_passed": all_passed},
    }
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_passed": all_passed, "check_count": len(checks)}, sort_keys=True))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

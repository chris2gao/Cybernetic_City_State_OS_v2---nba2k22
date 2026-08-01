from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import time
from typing import Any


def capture(command: list[str], cwd: Path | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "wall_seconds": round(time.perf_counter() - started, 6),
    }


def tree_stats(root: Path) -> dict[str, int]:
    files = [path for path in root.rglob("*") if path.is_file()]
    return {
        "file_count": len(files),
        "bytes": sum(path.stat().st_size for path in files),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("cosmic_venv", type=Path)
    parser.add_argument("mutmut_venv", type=Path)
    parser.add_argument("authoritative_remote_master")
    parser.add_argument("implementation_base")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    cosmic_venv = args.cosmic_venv.resolve(strict=True)
    mutmut_venv = args.mutmut_venv.resolve(strict=True)
    cosmic_python = cosmic_venv / "bin/python"
    cosmic_executable = cosmic_venv / "bin/cosmic-ray"

    version_probe_1 = capture([str(cosmic_executable), "--version"])
    version_probe_2 = capture([str(cosmic_executable), "--version"])
    pytest_probe = capture([str(cosmic_python), "-m", "pytest", "--version"])
    pip_probe = capture([str(cosmic_python), "-m", "pip", "--version"])
    freeze = capture([str(cosmic_python), "-m", "pip", "freeze"])
    repo_head = capture(["git", "rev-parse", "HEAD"], repo)
    repo_branch = capture(["git", "branch", "--show-current"], repo)
    local_tracking = capture(["git", "rev-parse", "refs/remotes/origin/master"], repo)
    metadata = importlib.metadata.metadata("cosmic-ray")
    result = {
        "format": "run-014-cosmic-ray-environment-v1",
        "observed_at": "2026-08-01",
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "cosmic_ray": {
            "expected_version": "8.4.6",
            "installed_version": importlib.metadata.version("cosmic-ray"),
            "requires_python": metadata.get("Requires-Python"),
            "venv": str(cosmic_venv),
            "venv_stats": tree_stats(cosmic_venv),
            "include_system_site_packages": "include-system-site-packages = false"
            in (cosmic_venv / "pyvenv.cfg").read_text(encoding="utf-8"),
            "version_probe_cold_proxy": version_probe_1,
            "version_probe_warm": version_probe_2,
            "pytest_probe": pytest_probe,
            "pip_probe": pip_probe,
            "packages": freeze["stdout"].splitlines(),
            "distribution_requires": importlib.metadata.requires("cosmic-ray") or [],
        },
        "mutmut_comparison": {
            "version": "3.6.0",
            "venv": str(mutmut_venv),
            "venv_stats": tree_stats(mutmut_venv),
        },
        "git_evidence_classes": {
            "implementation_base": args.implementation_base,
            "authoritative_remote_master": args.authoritative_remote_master,
            "local_remote_tracking_ref": local_tracking["stdout"],
            "wsl_experiment_head": repo_head["stdout"],
            "wsl_experiment_branch": repo_branch["stdout"],
            "local_tracking_used_for_authoritative_relation": False,
        },
        "runtime_role": {
            "default_loaded": False,
            "mcp_exposed": False,
            "architecture_schema_injection": False,
            "mount": "on_demand_wsl_cli",
        },
        "measurement_limits": {
            "exact_model_tokens": "not_observable",
            "process_tree_peak_memory": "not_observable_reliably",
            "source_and_test_context": "proxy_not_billing_tokens",
            "cold_probe": "proxy_first_new_process_not_os_page_cache_controlled",
        },
    }
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "cosmic_ray": result["cosmic_ray"]["installed_version"],
                "cosmic_venv": result["cosmic_ray"]["venv_stats"],
                "mutmut_venv": result["mutmut_comparison"]["venv_stats"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

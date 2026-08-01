from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import time
from typing import Any


EXPECTED_COSMIC_RAY_VERSION = "8.4.6"
EXPECTED_PYTHON_VERSION = "3.14.4"
EXPECTED_PYTEST_VERSION = "9.1.1"


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
    du = capture(["du", "-sb", str(root)])
    files = capture(["find", str(root), "-type", "f"])
    symlinks = capture(["find", str(root), "-type", "l"])
    return {
        "file_count": len(files["stdout"].splitlines()),
        "symlink_count": len(symlinks["stdout"].splitlines()),
        "bytes": int(du["stdout"].split()[0]),
    }


def parse_include_system_site_packages(cfg_path: Path) -> bool:
    values: list[str] = []
    for raw_line in cfg_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key.casefold() == "include-system-site-packages":
            values.append(value.casefold())
    if len(values) != 1 or values[0] not in {"true", "false"}:
        raise ValueError(
            "pyvenv.cfg must contain exactly one parseable "
            "include-system-site-packages value"
        )
    return values[0] == "true"


def supplied_runtime_metadata(python_executable: Path) -> dict[str, Any]:
    probe = capture(
        [
            str(python_executable),
            "-c",
            (
                "import importlib.metadata as m,json,platform;"
                "d=m.metadata('cosmic-ray');"
                "print(json.dumps({"
                "'cosmic_ray_version':m.version('cosmic-ray'),"
                "'pytest_version':m.version('pytest'),"
                "'requires_python':d.get('Requires-Python'),"
                "'distribution_requires':m.requires('cosmic-ray') or [],"
                "'platform':{'system':platform.system(),"
                "'release':platform.release(),"
                "'machine':platform.machine(),"
                "'python':platform.python_version()}}))"
            ),
        ]
    )
    if probe["exit_code"] != 0:
        raise RuntimeError("supplied virtualenv metadata probe failed")
    try:
        value = json.loads(probe["stdout"])
    except json.JSONDecodeError as error:
        raise RuntimeError("supplied virtualenv metadata probe was not JSON") from error
    if not isinstance(value, dict):
        raise RuntimeError("supplied virtualenv metadata probe returned the wrong shape")
    return value


def redact(value: Any, replacements: list[tuple[str, str]]) -> Any:
    if isinstance(value, str):
        for actual, placeholder in replacements:
            value = value.replace(actual, placeholder)
        return value
    if isinstance(value, list):
        return [redact(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: redact(item, replacements) for key, item in value.items()}
    return value


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

    include_system_site_packages = parse_include_system_site_packages(
        cosmic_venv / "pyvenv.cfg"
    )
    metadata = supplied_runtime_metadata(cosmic_python)

    version_probe_1 = capture([str(cosmic_executable), "--version"])
    version_probe_2 = capture([str(cosmic_executable), "--version"])
    pytest_probe = capture([str(cosmic_python), "-m", "pytest", "--version"])
    pip_probe = capture([str(cosmic_python), "-m", "pip", "--version"])
    freeze = capture([str(cosmic_python), "-m", "pip", "freeze"])
    repo_head = capture(["git", "rev-parse", "HEAD"], repo)
    repo_branch = capture(["git", "branch", "--show-current"], repo)
    local_tracking = capture(["git", "rev-parse", "refs/remotes/origin/master"], repo)
    if metadata.get("cosmic_ray_version") != EXPECTED_COSMIC_RAY_VERSION:
        raise RuntimeError("Cosmic Ray runtime mismatch")
    if metadata.get("pytest_version") != EXPECTED_PYTEST_VERSION:
        raise RuntimeError("pytest runtime mismatch")
    if metadata.get("platform", {}).get("python") != EXPECTED_PYTHON_VERSION:
        raise RuntimeError("Python runtime mismatch")
    if version_probe_1["stdout"] != f"cosmic-ray, version {EXPECTED_COSMIC_RAY_VERSION}":
        raise RuntimeError("Cosmic Ray version probe mismatch")
    if version_probe_2["stdout"] != f"cosmic-ray, version {EXPECTED_COSMIC_RAY_VERSION}":
        raise RuntimeError("Cosmic Ray warm version probe mismatch")
    if pytest_probe["stdout"] != f"pytest {EXPECTED_PYTEST_VERSION}":
        raise RuntimeError("pytest version probe mismatch")

    result = {
        "format": "run-014-cosmic-ray-environment-v1",
        "observed_at": dt.date.today().isoformat(),
        "platform": metadata["platform"],
        "cosmic_ray": {
            "expected_version": EXPECTED_COSMIC_RAY_VERSION,
            "installed_version": metadata["cosmic_ray_version"],
            "installed_python_version": metadata["platform"]["python"],
            "installed_pytest_version": metadata["pytest_version"],
            "requires_python": metadata.get("requires_python"),
            "venv": str(cosmic_venv),
            "venv_stats": tree_stats(cosmic_venv),
            "include_system_site_packages": include_system_site_packages,
            "version_probe_cold_proxy": version_probe_1,
            "version_probe_warm": version_probe_2,
            "pytest_probe": pytest_probe,
            "pip_probe": pip_probe,
            "packages": freeze["stdout"].splitlines(),
            "distribution_requires": metadata["distribution_requires"],
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
    replacements = [
        (str(cosmic_venv), "${COSMIC_RAY_VENV}"),
        (str(mutmut_venv), "${MUTMUT_VENV}"),
        (str(repo), "${REPOSITORY_ROOT}"),
    ]
    committed_result = redact(result, replacements)
    args.output.write_text(
        json.dumps(committed_result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "cosmic_ray": committed_result["cosmic_ray"]["installed_version"],
                "cosmic_venv": committed_result["cosmic_ray"]["venv_stats"],
                "mutmut_venv": committed_result["mutmut_comparison"]["venv_stats"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


STATUS_RE = re.compile(
    r"^\s*(?P<name>\S+): (?P<status>killed|survived|timeout|suspicious|"
    r"skipped|untested)$",
    re.MULTILINE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_time(path: Path) -> float:
    value = path.read_text(encoding="utf-8").strip()
    return float(value.split("=", 1)[1])


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def git_blob(repo: Path, commit: str, relative: str) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", f"{commit}:{relative}"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def cosmic_run(root: Path, phase: str, repetition: str) -> dict[str, Any]:
    directory = root / phase / "cosmic" / repetition
    normalized = read_json(directory / "normalized.json")
    receipt = read_env(directory / "receipt.env")
    timings = {
        name.removesuffix(".time"): read_time(directory / name)
        for name in ["baseline.time", "init.time", "exec.time", "dump.time", "report.time"]
        if (directory / name).exists()
    }
    return {
        "object_count": normalized["object_count"],
        "status_counts": normalized["status_counts"],
        "semantic_outcome_counts": normalized.get(
            "semantic_outcome_counts",
            normalized["status_counts"],
        ),
        "worker_outcome_counts": normalized["worker_outcome_counts"],
        "semantic_objects_sha256": normalized["semantic_objects_sha256"],
        "raw_dump_sha256": sha256(directory / "session.dump.jsonl"),
        "raw_dump_bytes": (directory / "session.dump.jsonl").stat().st_size,
        "session_sha256": receipt["session_sha256"],
        "session_bytes": int(receipt["session_bytes"]),
        "timings_seconds": timings,
    }


def mutmut_run(root: Path, phase: str, repetition: str) -> dict[str, Any]:
    directory = root / phase / "mutmut" / repetition
    results_text = (directory / "results.txt").read_text(encoding="utf-8")
    matches = list(STATUS_RE.finditer(results_text))
    counts = Counter(match.group("status") for match in matches)
    receipt = read_env(directory / "receipt.env")
    timings = {
        name.removesuffix(".time"): read_time(directory / name)
        for name in ["baseline.time", "exec.time", "report.time"]
        if (directory / name).exists()
    }
    return {
        "object_count": len(matches),
        "status_counts": dict(sorted(counts.items())),
        "results_sha256": hashlib.sha256(results_text.encode("utf-8")).hexdigest(),
        "source_sha256": receipt["source_before_sha256"],
        "mutants_bytes": int(receipt["mutants_bytes"]),
        "mutants_files": int(receipt["mutants_files"]),
        "timings_seconds": timings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    evidence = args.evidence.resolve(strict=True)
    experiments = evidence / "experiments"
    environment = read_json(evidence / "environment_receipt.json")
    wrapper_matrix = read_json(evidence / "wrapper_matrix.json")
    calibration_proof = read_json(evidence / "calibration_survivor_proof.json")
    real_proof = read_json(evidence / "real_survivor_proof.json")

    phases: dict[str, Any] = {}
    for phase in ["weak", "strong", "timeout", "real"]:
        cosmic = {
            repetition: cosmic_run(experiments, phase, repetition)
            for repetition in ["rep1", "rep2"]
        }
        mutmut = {
            repetition: mutmut_run(experiments, phase, repetition)
            for repetition in ["rep1", "rep2"]
        }
        phases[phase] = {
            "cosmic_ray": cosmic,
            "mutmut": mutmut,
            "repeatability": {
                "cosmic_ray_semantic_objects_equal": (
                    cosmic["rep1"]["semantic_objects_sha256"]
                    == cosmic["rep2"]["semantic_objects_sha256"]
                ),
                "mutmut_results_equal": (
                    mutmut["rep1"]["results_sha256"]
                    == mutmut["rep2"]["results_sha256"]
                ),
            },
        }

    expected = {
        "weak": {
            "cosmic_ray": {"killed": 48, "survived": 20},
            "mutmut": {"killed": 5, "survived": 5},
        },
        "strong": {
            "cosmic_ray": {"killed": 56, "survived": 12},
            "mutmut": {"killed": 7, "survived": 3},
        },
        "timeout": {
            "cosmic_ray": {"killed": 9, "survived": 1},
            "mutmut": {"killed": 3, "timeout": 2},
        },
        "real": {
            "cosmic_ray": {"incompetent": 1, "killed": 41, "survived": 16},
            "mutmut": {"killed": 127, "survived": 2},
        },
    }
    for phase, tools in expected.items():
        for tool, counts in tools.items():
            actual = phases[phase][tool]["rep1"]["status_counts"]
            if actual != counts:
                raise AssertionError(f"{phase}/{tool}: expected {counts}, got {actual}")
        if not all(phases[phase]["repeatability"].values()):
            raise AssertionError(f"{phase}: repeatability failed")

    current_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout.strip()
    base = "a6261cf3a8f0e0263b41a6ec32a3dd6c16ed653c"
    target_rel = "01_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py"
    test_rel = (
        "01_os/_runs/run-013-mutmut安装接入验证/07_测试执行/"
        "real_target_tests/tests/inspector_cases.py"
    )
    blob_evidence = {
        "canonical_target": {
            "implementation_base": git_blob(repo, base, target_rel),
            "candidate": git_blob(repo, current_head, target_rel),
        },
        "enhanced_test": {
            "run_013_candidate": git_blob(
                repo,
                "382750bad85231736920ab0f04a992b8a91f408c",
                test_rel,
            ),
            "candidate": git_blob(repo, current_head, test_rel),
        },
    }
    blob_evidence["canonical_target"]["unchanged"] = (
        blob_evidence["canonical_target"]["implementation_base"]
        == blob_evidence["canonical_target"]["candidate"]
    )
    blob_evidence["enhanced_test"]["unchanged"] = (
        blob_evidence["enhanced_test"]["run_013_candidate"]
        == blob_evidence["enhanced_test"]["candidate"]
    )

    source_bytes = (repo / target_rel).stat().st_size
    test_bytes = (repo / test_rel).stat().st_size
    wrapper_passed = (
        wrapper_matrix["passed"]
        and wrapper_matrix["case_count"] >= 18
        and wrapper_matrix["temporary_workspace_cleanup"]
        and wrapper_matrix["repository_unchanged"]
        and not wrapper_matrix["process_residue"]
        and wrapper_matrix["python_version_revalidated_each_invocation"]
        and wrapper_matrix["pytest_version_revalidated_each_invocation"]
        and wrapper_matrix["system_site_packages_rejected"]
        and wrapper_matrix["python_environment_variables_unset"]
        and not wrapper_matrix["untrusted_probe_output_echoed"]
    )
    meaningful_incremental_value = (
        real_proof["classification_counts"]["genuine_gap"]
        + real_proof["classification_counts"]["genuine_semantic_gap"]
        >= 1
        and phases["weak"]["cosmic_ray"]["rep1"]["object_count"]
        > phases["weak"]["mutmut"]["rep1"]["object_count"]
    )
    qualified = (
        environment["cosmic_ray"]["installed_version"] == "8.4.6"
        and environment["cosmic_ray"]["installed_python_version"] == "3.14.4"
        and environment["cosmic_ray"]["installed_pytest_version"] == "9.1.1"
        and environment["cosmic_ray"]["include_system_site_packages"] is False
        and all(
            phase["repeatability"]["cosmic_ray_semantic_objects_equal"]
            for phase in phases.values()
        )
        and calibration_proof["passed"]
        and real_proof["passed"]
        and wrapper_passed
        and all(group["unchanged"] for group in blob_evidence.values())
        and meaningful_incremental_value
    )
    if not qualified:
        raise AssertionError("verified_on_demand qualification was not proven")

    result = {
        "format": "run-014-cosmic-ray-results-v1",
        "task_id": "cosmic-ray-wsl-installation-validation-001",
        "implementation_base": base,
        "evidence_compiled_from_repository_head": current_head,
        "compilation_head_semantics": (
            "repository HEAD whose tracked source and test blobs were checked while "
            "this evidence object was compiled; it is not a claim about the later "
            "publication commit"
        ),
        "calibration_checkpoints": {
            "weak": "c89e1e6c53d12af870d2e128a007987fada39c1f",
            "strong_tests_only": "2481fbaff06cc12a8f37afe537e20f3369f07cb1",
            "production_blob_unchanged_between_checkpoints": True,
        },
        "environment": environment,
        "blob_evidence": blob_evidence,
        "matched_runs": phases,
        "survivor_proofs": {
            "calibration": calibration_proof,
            "real_target": real_proof,
            "mutmut_equivalent_survivors": {
                "count": 2,
                "proof": (
                    "01_os/_runs/run-013-mutmut安装接入验证/07_测试执行/"
                    "equivalence_proof.py"
                ),
                "classification": "unchanged_and_previously_verified",
            },
        },
        "timeout_semantics": {
            "native_cosmic_ray": (
                "one real timeout was recorded as test_outcome=killed and "
                "worker_outcome=normal with output=timeout"
            ),
            "canonical_wrapper": "reclassified_as_timeout_and_exit_72",
            "mutmut": "two timeout mutants surfaced natively as timeout",
            "repeatable": True,
        },
        "wrapper": {
            "matrix_case_count": wrapper_matrix["case_count"],
            "passed": wrapper_passed,
            "canonical": "01_os/06_execution/tools/cosmic_ray/invoke.sh",
            "summary_helper": "01_os/06_execution/tools/cosmic_ray/summarize.py",
            "local_distributor": True,
            "workers": 1,
            "fail_closed_exit": 72,
        },
        "incremental_value": {
            "meaningful": meaningful_incremental_value,
            "decorator_mutants_discovered": 2,
            "decorator_mutants_killed_after_stronger_assertions": 2,
            "real_target_new_executable_gaps": 4,
            "real_target_annotation_or_reachable_context_equivalents": 12,
            "tradeoff": (
                "broader operators and module/decorator reach add signal, while "
                "annotation noise and native timeout misclassification require the wrapper"
            ),
        },
        "resources": {
            "cosmic_ray_venv": environment["cosmic_ray"]["venv_stats"],
            "mutmut_venv": environment["mutmut_comparison"]["venv_stats"],
            "real_target_exec_seconds": {
                "cosmic_ray": [
                    phases["real"]["cosmic_ray"]["rep1"]["timings_seconds"]["exec"],
                    phases["real"]["cosmic_ray"]["rep2"]["timings_seconds"]["exec"],
                ],
                "mutmut": [
                    phases["real"]["mutmut"]["rep1"]["timings_seconds"]["exec"],
                    phases["real"]["mutmut"]["rep2"]["timings_seconds"]["exec"],
                ],
            },
            "context_proxy": {
                "source_bytes": source_bytes,
                "test_bytes": test_bytes,
                "combined_bytes": source_bytes + test_bytes,
                "classification": "proxy_not_billing_tokens",
            },
            "exact_model_tokens": "not_observable",
            "process_tree_peak_memory": "not_observable_reliably",
        },
        "system_role": {
            "status": "verified_on_demand",
            "mount": "on_demand_wsl_cli",
            "default_loaded": False,
            "mcp_exposed": False,
            "architecture_schema_injection": False,
        },
        "adoption_decision": {
            "decision": "verified_on_demand",
            "qualified": qualified,
            "installation_alone_used_as_justification": False,
            "requires_canonical_wrapper": True,
            "revalidation_triggers": [
                "Cosmic Ray or Python version change",
                "wrapper or summary semantics change",
                "target or test semantics change",
                "local distributor behavior change",
            ],
        },
        "official_evidence": [
            "https://pypi.org/project/cosmic-ray/",
            "https://cosmic-ray.readthedocs.io/en/latest/concepts.html",
            "https://cosmic-ray.readthedocs.io/en/latest/reference/tests.html",
        ],
        "evidence_manifest": "evidence/experiments/manifest.json",
        "passed": True,
    }
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "decision": result["adoption_decision"]["decision"],
                "passed": result["passed"],
                "wrapper_cases": result["wrapper"]["matrix_case_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

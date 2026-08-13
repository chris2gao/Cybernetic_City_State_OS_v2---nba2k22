#!/usr/bin/env python3
"""Run the deterministic package only when tracked files equal the candidate tree."""
from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parents[1]


class NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


COMMANDS = [
    (
        "activation_static",
        ["python", "01_os/06_execution/boot/mechanism_activation/validate_mechanism_activation.py", "static", "."],
    ),
    (
        "activation_tests",
        ["python", "-m", "unittest", "discover", "-s", "01_os/06_execution/boot/mechanism_activation", "-p", "test_*.py", "-q"],
    ),
    (
        "communication_static",
        ["python", "01_os/06_execution/boot/communication_system/validator/validate_communication_system.py", "static", "."],
    ),
    (
        "communication_tests",
        ["python", "-m", "unittest", "discover", "-s", "01_os/06_execution/boot/communication_system", "-p", "test_*.py", "-q"],
    ),
    (
        "model_routing_static",
        ["python", "01_os/03_mechanisms/model_routing/实现/verify_model_routing.py", "static", "."],
    ),
    (
        "model_routing_tests",
        ["python", "-m", "unittest", "discover", "-s", "01_os/06_execution/boot/model_routing", "-p", "test_*.py", "-q"],
    ),
    (
        "repository_default_gates",
        ["python", "01_os/06_execution/task_discipline/quiet_verify/quiet_verify.py", "--repo-root", "."],
    ),
    ("diff_check", ["git", "diff", "--check", "HEAD", "--"]),
]


def tracked_tree_matches_head() -> bool:
    return subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--"], cwd=REPO, check=False
    ).returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    spec = yaml.safe_load((RUN / "05_候选冻结/candidate_spec_v1.yml").read_text(encoding="utf-8"))
    candidate = str(spec["candidate_sha"])
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    if head != candidate or not tracked_tree_matches_head():
        raise ValueError("candidate_tree_binding_failed_before_execution")

    observations = []
    total_tests = 0
    for check_id, argv in COMMANDS:
        result = subprocess.run(
            argv, cwd=REPO, text=True, check=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        combined = "\n".join(value.strip() for value in (result.stdout, result.stderr) if value.strip())
        match = re.search(r"Ran (\d+) tests?", combined)
        count = int(match.group(1)) if match else None
        total_tests += count or 0
        observations.append({
            "check_id": check_id,
            "argv": argv,
            "exit_code": result.returncode,
            "tests_run": count,
            "result": "PASS" if result.returncode == 0 else "FAIL",
            "bounded_output_tail": combined.splitlines()[-8:],
        })

    after_matches = tracked_tree_matches_head()
    aggregate = all(item["exit_code"] == 0 for item in observations) and after_matches
    receipt = {
        "schema_version": "citystate.mechanism_activation.bound_candidate_checks.v1",
        "task_id": spec["task_id"],
        "candidate_sha_expected": candidate,
        "candidate_sha_observed": head,
        "tracked_worktree_matches_candidate_before": True,
        "tracked_worktree_matches_candidate_after": after_matches,
        "execution_root": ".",
        "observations": observations,
        "deterministic_tests_run": total_tests,
        "aggregate_result": "VERIFIED" if aggregate else "BLOCKED",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority_effect": "none",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.dump(receipt, Dumper=NoAliasSafeDumper, allow_unicode=True, sort_keys=False),
        encoding="utf-8", newline="\n",
    )
    print(yaml.safe_dump({
        "aggregate_result": receipt["aggregate_result"],
        "deterministic_tests_run": total_tests,
        "candidate_sha": candidate,
    }, sort_keys=False), end="")
    return 0 if aggregate else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Run offline tests and account for every approved scenario without scope inflation."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--run-path", required=True)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    run = root / args.run_path
    contract = json.loads((run / "acceptance_contract.json").read_text(encoding="utf-8"))
    mapping = json.loads((run / "acceptance_map.json").read_text(encoding="utf-8"))
    ids = [x["id"] for x in contract["scenarios"]]
    if len(ids) != 48 or len(set(ids)) != 48 or set(ids) != set(mapping):
        raise ValueError("exact original 28+20 scenario accounting required")
    with tempfile.TemporaryDirectory(prefix="prms-acceptance-") as temp:
        junit = Path(temp) / "results.xml"
        command = [sys.executable, "-B", "-m", "pytest", "01_os/06_execution/boot/context_management/prms/tests",
                   "-q", "-p", "no:cacheprovider", "--basetemp", str(Path(temp) / "pytest"), "--junitxml", str(junit)]
        executed = subprocess.run(command, cwd=root, capture_output=True)
        if not junit.exists():
            sys.stdout.buffer.write(executed.stdout + executed.stderr)
            return executed.returncode or 3
        nodes = []
        for test in ET.parse(junit).iter("testcase"):
            node = test.attrib["classname"].split(".")[-1] + ".py::" + test.attrib["name"]
            outcome = "FAIL" if test.find("failure") is not None or test.find("error") is not None else (
                "NOT_RUN" if test.find("skipped") is not None else "PASS")
            nodes.append({"node": node, "outcome": outcome})
        results = []
        for scenario in contract["scenarios"]:
            spec = mapping[scenario["id"]]
            groups = [[x for x in nodes if x["node"].split("[")[0] == ref] for ref in spec["tests"]]
            if not groups or any(not group for group in groups):
                raise ValueError("mapped test did not execute: " + scenario["id"])
            selected = [x for group in groups for x in group]
            local = "PASS" if all(x["outcome"] == "PASS" for x in selected) else "FAIL_OR_NOT_RUN"
            status = ("PASS_AT_OFFLINE_SCOPE" if local == "PASS" else local) if spec["required_scope"] == "OFFLINE" else "NOT_RUN_REQUIRED_SCOPE"
            results.append({"id": scenario["id"], "name": scenario["name"], "covers": scenario["covers"],
                            "status": status, "required_scope": spec["required_scope"], "offline_analogue": local,
                            "executed_tests": selected, "remaining_proof": spec["remaining_proof"]})
        report = {"schema_version": "prms.acceptance_results.v1",
                  "candidate": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip(),
                  "command": ["@python", "-B", "-m", "pytest", "01_os/06_execution/boot/context_management/prms/tests",
                              "-q", "-p", "no:cacheprovider", "--basetemp", "<new-external-temp>/pytest",
                              "--junitxml", "<new-external-temp>/results.xml"],
                  "unit_test_count": len(nodes), "unit_test_outcomes": dict(Counter(x["outcome"] for x in nodes)),
                  "scenario_count": len(results), "scenario_status_counts": dict(Counter(x["status"] for x in results)),
                  "all_original_acceptance_passed": False,
                  "scope_warning": "Offline success is not GitHub permission, real model-window or independent-review acceptance.",
                  "results": results}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if executed.returncode:
            sys.stderr.buffer.write(executed.stdout + executed.stderr)
        return executed.returncode


if __name__ == "__main__":
    sys.exit(main())

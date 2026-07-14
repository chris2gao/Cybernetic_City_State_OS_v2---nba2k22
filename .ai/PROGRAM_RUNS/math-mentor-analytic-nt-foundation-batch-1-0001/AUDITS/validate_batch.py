"""Re-execute and validate the bounded ANALYTIC_NT Batch 1 evidence."""

from __future__ import annotations

import argparse
import ast
import json
import platform
import subprocess
import sys
from pathlib import Path

import yaml


BASE_HEAD = "1563dc2844efcb6a5e8b73825f17abd7c1d13405"
RUN_REL = Path(
    ".ai/PROGRAM_RUNS/math-mentor-analytic-nt-foundation-batch-1-0001"
)
NODE_DIR_REL = Path(
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB"
)
NODE_IDS = ("ANALYTIC_NT-684", "ANALYTIC_NT-687", "ANALYTIC_NT-688", "ANALYTIC_NT-692")
ALIASES = {
    "ANALYTIC_NT-684": "n_684",
    "ANALYTIC_NT-687": "n_687",
    "ANALYTIC_NT-688": "n_688",
    "ANALYTIC_NT-692": "n_692",
}
CANONICAL_CONCEPTS = {
    "ANALYTIC_NT-684": "prime_number_theorem",
    "ANALYTIC_NT-687": "Dirichlet_L_functions",
    "ANALYTIC_NT-688": "finite_exponential_sums",
    "ANALYTIC_NT-692": "Dirichlet_series",
}
COMMON_EXPECTED = {
    "city_state_engine": "Plan3_Engine_B",
    "mode": "A",
    "math_lane": "MathLane_A",
    "mode_routing_status": "human_approved",
    "formal_definition_status": "human_approved",
    "prerequisites_status": "manual_review_required",
    "mapping_boundary_status": "human_approved",
    "validation_status": "run_with_log",
    "tool_status": "run_with_log",
    "teaching_ready": False,
    "teaching_readiness_status": "manual_review_required",
    "bridge_readiness_status": "manual_review_required",
    "coordinator_consumable": False,
    "p3_reopened": False,
    "bridge_generation_performed": False,
}


def run_checked(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def require_program_ref(repo_root: Path, run_root: Path, value: str) -> Path:
    path = (repo_root / value).resolve()
    path.relative_to(run_root)
    if not path.is_file():
        raise AssertionError(f"durable reference does not resolve: {value}")
    return path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate_node(repo_root: Path, run_root: Path, node_id: str) -> dict:
    node_rel = NODE_DIR_REL / f"{node_id}.yaml"
    node_path = repo_root / node_rel
    node = yaml.safe_load(node_path.read_text(encoding="utf-8-sig"))

    if node["id"] != node_id:
        raise AssertionError(f"{node_id}: identity mismatch")
    if node["migration_review"]["roadmap_alias"] != ALIASES[node_id]:
        raise AssertionError(f"{node_id}: roadmap alias mismatch")
    if node["canonical_concept"] != CANONICAL_CONCEPTS[node_id]:
        raise AssertionError(f"{node_id}: canonical concept mismatch")
    for key, expected in COMMON_EXPECTED.items():
        if node.get(key) != expected:
            raise AssertionError(
                f"{node_id}: {key}={node.get(key)!r}, expected {expected!r}"
            )
    if len(node.get("sub_topics", [])) < 8:
        raise AssertionError(f"{node_id}: fewer than eight subtopics")
    for required_key in (
        "pure_math_definition",
        "assumptions_and_notation",
        "required_prerequisites",
        "mode_a_intuition",
        "mapping_boundary",
        "common_misconceptions",
        "definition_restatement_hook",
        "forcing_question_plan",
        "teaching_flow",
        "tool_truthfulness",
        "v8_sanity_audit",
        "bridge_certification",
    ):
        if required_key not in node:
            raise AssertionError(f"{node_id}: missing {required_key}")

    ast.parse(node["code_implementation"])
    audit = node["tool_truthfulness"]
    required_tool_fields = {
        "tool_status",
        "capability",
        "tool_family",
        "log_ref",
        "report_ref",
        "input_ref",
        "output_ref",
        "error_ref",
        "environment_ref",
        "timestamp",
        "limitations",
    }
    missing_tool_fields = sorted(required_tool_fields - set(audit))
    if missing_tool_fields:
        raise AssertionError(f"{node_id}: missing tool fields {missing_tool_fields}")
    if audit["tool_status"] != "run_with_log" or audit["capability"] != "deterministic_calculation":
        raise AssertionError(f"{node_id}: invalid deterministic tool state")
    if not isinstance(audit["limitations"], list) or not audit["limitations"]:
        raise AssertionError(f"{node_id}: tool limitations are missing")
    if not str(audit.get("timestamp", "")).endswith("Z"):
        raise AssertionError(f"{node_id}: run_with_log UTC timestamp is missing")
    refs = {
        key: require_program_ref(repo_root, run_root, audit[key])
        for key in ("script_ref", "input_ref", "output_ref", "environment_ref", "log_ref")
    }

    command = [
        sys.executable,
        audit["script_ref"],
        "--input",
        audit["input_ref"],
        "--output",
        audit["output_ref"],
        "--log",
        audit["log_ref"],
    ]
    run_checked(command, repo_root)
    output = load_json(refs["output_ref"])
    if output.get("status") != "passed":
        raise AssertionError(f"{node_id}: bounded audit did not pass")
    if output.get("timestamp") != audit["timestamp"]:
        raise AssertionError(f"{node_id}: input/output/log/YAML timestamp mismatch")
    if not output.get("explicitly_not_validated"):
        raise AssertionError(f"{node_id}: audit limitations are missing")

    sandbox = run_checked(
        [
            sys.executable,
            "06_Silicon_Index/factory_pipeline/sandbox_evaluator.py",
            node_rel.as_posix(),
        ],
        repo_root,
    )
    result_lines = [
        line for line in sandbox.stdout.splitlines() if line.startswith("EVALUATOR_RESULT_JSON:")
    ]
    if len(result_lines) != 1:
        raise AssertionError(f"{node_id}: sandbox result payload missing")
    sandbox_payload = json.loads(result_lines[0].split(":", 1)[1])
    if sandbox_payload.get("status") != "passed":
        raise AssertionError(f"{node_id}: sandbox evaluator did not pass")

    if node_id == "ANALYTIC_NT-684":
        counts = {
            int(case["x"]): case["observed_prime_count"]
            for case in output["exact_prime_count_cases"]
            if float(case["x"]).is_integer()
        }
        if [counts[x] for x in (10, 100, 1000, 10000)] != [4, 25, 168, 1229]:
            raise AssertionError("ANALYTIC_NT-684: approved finite prime counts mismatch")
    elif node_id == "ANALYTIC_NT-687":
        if node["scope_restriction"]["included"] != "Dirichlet L-functions only":
            raise AssertionError("ANALYTIC_NT-687: scope is not Dirichlet-only")
        if output["periodicity"]["case_count"] != 129:
            raise AssertionError("ANALYTIC_NT-687: periodicity case count mismatch")
        if output["complete_multiplicativity"]["pair_count"] != 4225:
            raise AssertionError("ANALYTIC_NT-687: multiplicativity grid mismatch")
        if output["catalan_partial_sum"]["absolute_error"] > output["catalan_partial_sum"]["tolerance"]:
            raise AssertionError("ANALYTIC_NT-687: Catalan error exceeds budget")
        if "status=passed" not in refs["log_ref"].read_text(encoding="utf-8-sig"):
            raise AssertionError("ANALYTIC_NT-687: durable log lacks pass status")
    elif node_id == "ANALYTIC_NT-688":
        if output["convention"] != "e(t)=exp(2*pi*i*t)":
            raise AssertionError("ANALYTIC_NT-688: exponential convention mismatch")
        if output["case_count"] != 17:
            raise AssertionError("ANALYTIC_NT-688: declared finite case count mismatch")
    elif node_id == "ANALYTIC_NT-692":
        if output["case_count"] != 4:
            raise AssertionError("ANALYTIC_NT-692: finite polynomial case count mismatch")
        if not all(
            all(key in case for key in ("s", "left_support", "right_support"))
            for case in output["cases"]
        ):
            raise AssertionError("ANALYTIC_NT-692: finite support/input evidence missing")

    if node_id != "ANALYTIC_NT-687" and refs["output_ref"].read_bytes() != refs["log_ref"].read_bytes():
        raise AssertionError(f"{node_id}: output and durable log diverge")

    return {
        "node_ref": node_rel.as_posix(),
        "roadmap_alias": ALIASES[node_id],
        "canonical_concept": CANONICAL_CONCEPTS[node_id],
        "sub_topic_count": len(node["sub_topics"]),
        "audit_scope": output["scope"],
        "audit_status": output["status"],
        "sandbox_status": sandbox_payload["status"],
        "prerequisites_status": node["prerequisites_status"],
        "bridge_readiness_status": node["bridge_readiness_status"],
        "blocking_reasons": node["bridge_certification"]["blocking_reasons"],
        "durable_refs": {key: audit[key] for key in refs},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_root = (repo_root / RUN_REL).resolve()
    nodes = {
        node_id: validate_node(repo_root, run_root, node_id) for node_id in NODE_IDS
    }

    teaching_result_ref = (
        run_root
        / "OUTPUTS/teaching-flow-static/teaching_flow_static_validation_result.json"
    )
    teaching_result = load_json(teaching_result_ref)
    if teaching_result.get("overall_status") != "pass":
        raise AssertionError("teaching-flow static validator did not pass")

    ancestry = run_checked(
        ["git", "merge-base", "--is-ancestor", BASE_HEAD, "HEAD"], repo_root
    )
    del ancestry
    topology = run_checked(
        ["git", "rev-list", "--parents", f"{BASE_HEAD}..HEAD"], repo_root
    )
    commit_lines = [line.split() for line in topology.stdout.splitlines() if line]
    if not commit_lines or any(len(line) != 2 for line in commit_lines):
        raise AssertionError("candidate history contains a merge or lacks reviewable commits")

    result = {
        "validation_id": "math-mentor-analytic-nt-foundation-batch-1-validation-0001",
        "status": "passed",
        "source_head": BASE_HEAD,
        "node_count": len(nodes),
        "nodes": nodes,
        "teaching_flow_static_validator": {
            "status": teaching_result["overall_status"],
            "result_ref": teaching_result_ref.relative_to(repo_root).as_posix(),
            "scope": "generic_protocol_and_existing_TRIG_006_CALCULUS_265_fixture_regression_only",
            "used_as_direct_four_node_teaching_ready_proof": False,
            "execution_was_scoped_without_runtime_activation": True,
        },
        "commit_topology": {
            "source_is_ancestor": True,
            "commit_count_at_validation": len(commit_lines),
            "all_candidate_commits_have_one_parent": True,
        },
        "environment": {
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "pyyaml_version": yaml.__version__,
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "forbidden_runtime_side_effects_observed": [],
        "limitations": [
            "Finite audit passes do not prove the infinite or asymptotic mathematics named by any node.",
            "Bridge readiness remains manual because exact prerequisites and ChatGPT exact-head acceptance are incomplete.",
            "This validation does not activate a Coordinator, runtime, scheduler, learned history, student state, P3, or bridge workflow.",
        ],
    }
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    output_path = args.output if args.output.is_absolute() else repo_root / args.output
    log_path = args.log if args.log.is_absolute() else repo_root / args.log
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialized, encoding="utf-8")
    log_path.write_text(serialized, encoding="utf-8")
    print("status=passed")
    print(f"node_count={len(nodes)}")
    print(f"output_ref={output_path.relative_to(repo_root).as_posix()}")
    print(f"log_ref={log_path.relative_to(repo_root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

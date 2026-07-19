"""Re-execute and validate the KCP PROP_LOGIC Batch 1 candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml


BASE_HEAD = "94b617e67bdbdb958443545d41b90cdbba77e54d"
RUN_REL = Path(".ai/PROGRAM_RUNS/kcp-batch-1-prop-logic-certification-0001")
DB_REL = Path("08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB")
MATH_MENTOR_REL = Path("08_Domain_Applications/Math_Mentor")
NODES = {
    "PROP_LOGIC-001": {
        "file": "PROP_LOGIC-001_Connectives.yaml",
        "uuid": "55137e7b-f2d8-55e9-9848-00698f7ddf0f",
        "roadmap_alias": "prop_1_connectives",
        "prerequisites": [],
    },
    "PROP_LOGIC-002": {
        "file": "PROP_LOGIC-002_Truth_Tables.yaml",
        "uuid": "860929b9-b876-52b0-b852-ae353e938cbe",
        "roadmap_alias": "prop_2_truth_tables",
        "prerequisites": ["PROP_LOGIC-001"],
    },
    "PROP_LOGIC-003": {
        "file": "PROP_LOGIC-003_De_Morgans_Laws.yaml",
        "uuid": "214f32b9-8039-5321-8fa8-eaed6d3bce8a",
        "roadmap_alias": "prop_4_algebra_laws",
        "prerequisites": ["PROP_LOGIC-001", "PROP_LOGIC-002"],
    },
    "PROP_LOGIC-004": {
        "file": "PROP_LOGIC-004_Tautologies.yaml",
        "uuid": "bf097dcc-75fd-5259-8b46-df8ee8b0e2d9",
        "roadmap_alias": "prop_3_tautologies",
        "prerequisites": ["PROP_LOGIC-001", "PROP_LOGIC-002"],
    },
    "PROP_LOGIC-005": {
        "file": "PROP_LOGIC-005_Normal_Forms.yaml",
        "uuid": "67995054-4afd-50e6-aeca-d1b3327625f8",
        "roadmap_alias": "prop_5_normal_forms",
        "prerequisites": ["PROP_LOGIC-001", "PROP_LOGIC-002", "PROP_LOGIC-003"],
    },
}
FORBIDDEN_PATHS = {
    "08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md",
    "08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md",
    "08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md",
    "08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md",
}
CODEX_REPORT_REF = ".ai/CODEX_REPORTS/kcp-batch-1-prop-logic-certification-0001.md"


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def display_ref(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def parse_sandbox(stdout: str) -> dict:
    matches = [
        line.split(":", 1)[1]
        for line in stdout.splitlines()
        if line.startswith("EVALUATOR_RESULT_JSON:")
    ]
    if len(matches) != 1:
        raise AssertionError("sandbox evaluator structured result missing")
    return json.loads(matches[0])


def validate_node(repo_root: Path, run_root: Path, node_id: str, spec: dict) -> dict:
    node_rel = DB_REL / spec["file"]
    node = yaml.safe_load((repo_root / node_rel).read_text(encoding="utf-8-sig"))
    required_scalars = {
        "id": node_id,
        "canonical_uuid": spec["uuid"],
        "mode": "A",
        "math_lane": "MathLane_A",
        "mode_routing_status": "human_approved_task_scoped",
        "formal_definition_status": "semantic_only_review_required",
        "mapping_boundary_status": "semantic_only_review_required",
        "validation_status": "run_with_log",
        "tool_status": "run_with_log",
        "teaching_ready": True,
        "teaching_readiness_status": "local_candidate_pending_exact_head_review",
        "bridge_readiness_status": "manual_review_required",
        "coordinator_consumable": False,
        "consumer_allowed": False,
        "p3_reopened": False,
        "bridge_generation_performed": False,
    }
    for key, expected in required_scalars.items():
        if node.get(key) != expected:
            raise AssertionError(f"{node_id}: {key}={node.get(key)!r}, expected {expected!r}")
    identity = node["identity_evidence"]
    if identity["roadmap_alias"] != spec["roadmap_alias"]:
        raise AssertionError(f"{node_id}: roadmap alias mismatch")
    if identity["central_crosswalk_binding"] != "unclaimed_fail_closed":
        raise AssertionError(f"{node_id}: crosswalk boundary was not preserved")
    if not node.get("sub_topics") or not node.get("pure_math_definition"):
        raise AssertionError(f"{node_id}: formal coverage missing")
    for key in (
        "assumptions_and_notation",
        "required_prerequisites",
        "mode_a_intuition",
        "mapping_boundary",
        "common_misconceptions",
        "definition_restatement_hook",
        "forcing_question_plan",
        "teaching_flow",
        "semantic_acceptance_required",
        "tool_truthfulness",
        "v8_sanity_audit",
        "certification_boundary",
    ):
        if key not in node:
            raise AssertionError(f"{node_id}: missing {key}")
    teaching = node["teaching_flow"]
    for key in (
        "explanation_before_questioning",
        "intuition_before_formal_definition",
        "one_question_per_interactive_turn",
        "repair_once_before_correction",
        "covers_all_sub_topics",
        "definition_restatement_required",
    ):
        if teaching.get(key) is not True:
            raise AssertionError(f"{node_id}: teaching flow flag {key} not true")
    if node["semantic_acceptance_required"].get("status") != "review_required":
        raise AssertionError(f"{node_id}: semantic claims were self-cleared")

    observed_prerequisites = [
        item["node_id"] for item in node["required_prerequisites"].get("resolved", [])
    ]
    if observed_prerequisites != spec["prerequisites"]:
        raise AssertionError(
            f"{node_id}: prerequisites {observed_prerequisites} != {spec['prerequisites']}"
        )

    audit = node["tool_truthfulness"]
    for key in (
        "script_ref",
        "input_ref",
        "output_ref",
        "environment_ref",
        "log_ref",
    ):
        ref = (repo_root / audit[key]).resolve()
        ref.relative_to(run_root)
        if not ref.is_file():
            raise AssertionError(f"{node_id}: unresolved durable ref {audit[key]}")
    output_ref = repo_root / audit["output_ref"]
    before_hash = sha256(output_ref)
    run_checked(
        [
            sys.executable,
            audit["script_ref"],
            "--input",
            audit["input_ref"],
            "--output",
            audit["output_ref"],
            "--log",
            audit["log_ref"],
        ],
        repo_root,
    )
    after_hash = sha256(output_ref)
    if before_hash != after_hash:
        raise AssertionError(f"{node_id}: audit output is not byte-repeatable")
    output = load_json(output_ref)
    if output.get("status") != "passed" or output.get("node_id", node_id) != node_id:
        raise AssertionError(f"{node_id}: deterministic audit did not pass")
    if output.get("timestamp") != audit["timestamp"]:
        raise AssertionError(f"{node_id}: timestamp binding mismatch")

    sandbox = run_checked(
        [sys.executable, "06_Silicon_Index/factory_pipeline/sandbox_evaluator.py", node_rel.as_posix()],
        repo_root,
    )
    sandbox_payload = parse_sandbox(sandbox.stdout)
    if sandbox_payload.get("status") != "passed" or sandbox_payload.get("warnings"):
        raise AssertionError(f"{node_id}: sandbox did not pass cleanly")
    return {
        "node_ref": node_rel.as_posix(),
        "canonical_uuid": spec["uuid"],
        "roadmap_alias": spec["roadmap_alias"],
        "prerequisites": observed_prerequisites,
        "sub_topic_count": len(node["sub_topics"]),
        "teaching_ready_local_candidate": True,
        "semantic_review_status": "review_required",
        "audit_scope": output["scope"],
        "audit_status": "passed",
        "audit_exit_code": 0,
        "audit_repeatability_sha256": after_hash,
        "sandbox_status": "passed",
        "sandbox_exit_code": 0,
        "consumer_allowed": False,
        "central_crosswalk_binding": "unclaimed_fail_closed",
    }


def assert_acyclic(graph: dict[str, list[str]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise AssertionError(f"prerequisite cycle found at {node_id}")
        if node_id in visited:
            return
        visiting.add(node_id)
        for prerequisite in graph[node_id]:
            if prerequisite not in graph:
                raise AssertionError(f"unresolved prerequisite {prerequisite}")
            visit(prerequisite)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in graph:
        visit(node_id)


def validate_control_plane_boundary(repo_root: Path) -> dict:
    crosswalk = load_json(repo_root / MATH_MENTOR_REL / "CANONICAL_NODE_CROSSWALK.json")
    conflicts = load_json(repo_root / MATH_MENTOR_REL / "ALIAS_CONFLICT_REGISTRY.json")
    relevant_uuids = {spec["uuid"] for spec in NODES.values()}
    rows = [row for row in crosswalk["nodes"] if row["canonical_uuid"] in relevant_uuids]
    if len(rows) != 5:
        raise AssertionError("five exact central crosswalk rows did not resolve")
    if any(row["consumer_allowed"] is not False for row in rows):
        raise AssertionError("central consumer boundary opened")
    if any(row["binding_status"] != "unclaimed" for row in rows):
        raise AssertionError("central identity binding unexpectedly changed")
    open_conflicts = [
        conflict
        for conflict in conflicts["conflicts"]
        if conflict["status"] == "open"
        and any(subject["canonical_uuid"] in relevant_uuids for subject in conflict["subjects"])
    ]
    if len(open_conflicts) != 5:
        raise AssertionError("expected five fail-closed central conflicts")
    return {
        "crosswalk_row_count": len(rows),
        "binding_status": "unclaimed",
        "consumer_allowed_count": 0,
        "open_missing_alias_conflict_count": len(open_conflicts),
        "source_digests_are_pre_repair_snapshot": True,
        "task_scoped_evidence_does_not_mutate_p0_registries": True,
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
        node_id: validate_node(repo_root, run_root, node_id, spec)
        for node_id, spec in NODES.items()
    }
    graph = {node_id: result["prerequisites"] for node_id, result in nodes.items()}
    assert_acyclic(graph)
    control_plane = validate_control_plane_boundary(repo_root)

    bulk_log = (run_root / "LOGS/bulk-evaluator-five-node.log").read_text(encoding="utf-8-sig")
    if "Total Evaluated: 5" not in bulk_log or "Passed: 5" not in bulk_log or "exit_code=0" not in bulk_log:
        raise AssertionError("five-node bulk evaluator evidence did not pass")

    changed = run_checked(["git", "diff", "--name-only", BASE_HEAD], repo_root).stdout.splitlines()
    if FORBIDDEN_PATHS.intersection(changed):
        raise AssertionError("forbidden teaching-contract path changed")
    if any("BRIDGE-" in path or "bridge" in Path(path).name.lower() for path in changed):
        raise AssertionError("bridge path changed")
    allowed_node_paths = {(DB_REL / spec["file"]).as_posix() for spec in NODES.values()}
    out_of_scope = [
        path
        for path in changed
        if path not in allowed_node_paths
        and path != CODEX_REPORT_REF
        and not path.startswith(RUN_REL.as_posix() + "/")
    ]
    if out_of_scope:
        raise AssertionError(f"out-of-scope tracked changes: {out_of_scope}")

    run_checked(["git", "merge-base", "--is-ancestor", BASE_HEAD, "HEAD"], repo_root)
    topology = run_checked(["git", "rev-list", "--parents", f"{BASE_HEAD}..HEAD"], repo_root)
    commit_rows = [line.split() for line in topology.stdout.splitlines() if line]
    if not commit_rows or any(len(row) != 2 for row in commit_rows):
        raise AssertionError("candidate history lacks a checkpoint or contains a merge")

    result = {
        "validation_id": "kcp-batch-1-prop-logic-certification-validation-0001",
        "timestamp": "2026-07-19T01:09:19Z",
        "status": "passed",
        "source_head": BASE_HEAD,
        "node_count": 5,
        "nodes": nodes,
        "prerequisite_graph": {"status": "passed", "cycle_count": 0, "graph": graph},
        "control_plane_boundary": control_plane,
        "bulk_evaluator": {"status": "passed", "evaluated": 5, "passed": 5, "exit_code": 0},
        "semantic_review_required_count": 5,
        "teaching_ready_local_candidate_count": 5,
        "consumer_allowed_count": 0,
        "bridge_ready_count": 0,
        "forbidden_path_changes": [],
        "runtime_or_state_activation_performed": False,
        "commit_topology": {
            "source_is_ancestor": True,
            "commit_count_at_validation": len(commit_rows),
            "all_candidate_commits_have_one_parent": True,
        },
        "limitations": [
            "Executable evidence validates only the declared finite truth-functional cases.",
            "All bilingual formal, completeness, uniqueness, mapping, and pedagogy claims remain on the semantic acceptance list.",
            "The unchanged P0 crosswalk is a pre-repair snapshot and remains fail-closed; task-scoped identity evidence does not grant consumer admission.",
            "No bridge, runtime, Coordinator, scheduler, or learner-state capability was activated.",
        ],
    }
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    output = args.output if args.output.is_absolute() else repo_root / args.output
    log = args.log if args.log.is_absolute() else repo_root / args.log
    output.parent.mkdir(parents=True, exist_ok=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(serialized, encoding="utf-8")
    log.write_text("command_status=passed\nexit_code=0\n" + serialized, encoding="utf-8")
    print("status=passed")
    print("node_count=5")
    print("teaching_ready_local_candidate_count=5")
    print("semantic_review_required_count=5")
    print("consumer_allowed_count=0")
    print(f"output_ref={display_ref(output, repo_root)}")
    print(f"log_ref={display_ref(log, repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

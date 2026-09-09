"""Exercise both production CLIs against this task's actual immutable candidate.

This is a readiness-input pilot, not a claim that stage completion, independent
review, master integration or OS-wide execution enforcement has been achieved.
The complete external input and CLI output are written to managed stdout logs.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]
RUN = "01_os/_runs/run-20260907-os-execution-foundation-001"
PACKET = RUN + "/01_任务/task_packet.yml"
DECISION = RUN + "/03_方案设计/semantic_convergence_decision.md"
IMPL = ROOT / "01_os/03_mechanisms/stage_collaborative_deliberation/实现"
sys.path.insert(0, str(IMPL))
import verify_stage_collaborative_deliberation as validator


def main() -> int:
    support = validator.task_scope_support()
    candidate = support.git(ROOT, "rev-parse", "HEAD").decode("ascii").strip()
    support.source_state(ROOT, candidate)
    packet_raw = support.tracked_blob(ROOT, candidate, PACKET)
    packet = support.normalize_packet(support.load_yaml_text(packet_raw.decode("utf-8"))).body
    packet_blob = hashlib.sha1(f"blob {len(packet_raw)}\0".encode("ascii") + packet_raw).hexdigest()
    scope = {"schema_version": 1, "task_id": packet["task_id"], "candidate": candidate,
             "task_packet": {"path": PACKET, "blob_sha": packet_blob},
             "action_id": "semantic_candidate_readiness_pilot", "stage_id": "workflow_stage_06_execution",
             "paths": [DECISION]}
    support.tracked_blob(ROOT, candidate, DECISION)
    profiles = support.load_yaml_text(support.tracked_blob(ROOT, candidate, validator.PROFILE_SET_PATH).decode("utf-8"))
    profile = next(p for p in profiles["profiles"] if p["profile_id"] == scope["stage_id"])
    values = {
        "exact_task_id_branch_and_40_character_base": {k: packet[k] for k in ("task_id", "branch", "exact_base_sha")},
        "Human_execution_authorization": {"basis": "current confirmed task scope", "task_packet": scope["task_packet"], "decision_path": DECISION},
        "closed_allowlist_and_prohibitions": {k: packet[k] for k in ("allowed_changed_paths", "prohibitions")},
        "active_contract_and_test_refs": {"profile": validator.PROFILE_SET_PATH, "plan": packet["verification_plan"]},
        "implementation_changes": support.git(ROOT, "diff", "--name-only", "--no-renames", packet["exact_base_sha"], candidate).decode("utf-8").splitlines(),
        "test_results_and_failure_evidence": "This managed attempt preserves real command logs; this readiness pilot does not predeclare its final result. Prior b047 results are historical only.",
        "deviations_and_granularity_evaluations": "The confirmed semantic scope amendment permits these body changes; master and runtime remain excluded.",
        "open_detail_divergence_events": "No additional scope decision introduced by this bounded readiness-input pilot.",
        "rollback_target": packet["exact_base_sha"],
        "package_completion_pointer_candidate": "Candidate " + candidate + "; final independent acceptance and completion handoff remain pending.",
    }
    if set(values) != set(profile["required_model_fields"]):
        raise ValueError("actual_stage_profile_changed_pilot_needs_explicit_update")
    model = {
        "task_id": scope["task_id"], "stage_id": scope["stage_id"],
        "problem_or_objective": "Verify ordinary scoped readiness on the actual foundation candidate.",
        "Human_intent_understanding": packet["objective"],
        "current_baseline_and_inputs": {"candidate": candidate, "base": packet["exact_base_sha"], "task_packet": scope["task_packet"]},
        "constraints_and_dependencies": packet["prohibitions"],
        "proposed_method_or_solution": "Read immutable candidate packet and profile; invoke v1 and v2 production instance CLIs with exact action binding.",
        "feasibility_support": "Regular Git blobs resolve in this actual clean task worktree; the managed runner records command exits and full stdout/stderr.",
        "expected_output": "Readiness validation of this declaration only; no stage completion or independent acceptance claim.",
        "verification_or_acceptance_method": "Both ordinary CLI calls must return 0; unknown action negative must return nonzero; independent acceptance remains a later Human-relayed gate.",
        "current_exact_model_version": candidate,
        "assumptions_risks_alternatives_unknowns": "Same-writer model/receipt labels do not authenticate Human decisions or real tests; runtime and master adoption remain outside this pilot.",
        "open_load_bearing_items": [{"decision_id": "semantic_scope_convergence_as_confirmed_20260908",
            "load_bearing": True, "disposition": "resolved", "Human_basis": {
                "kind": "current_task_scope", "decision_id": "semantic_scope_convergence_as_confirmed_20260908",
                "task_packet": scope["task_packet"], "action_id": scope["action_id"]}}],
        "ordinary_local_choices": [],
        "stage_specific_model_elements": {key: {"disposition": validator.REPRESENTED, "value": value} for key, value in values.items()},
    }
    receipt = {
        "receipt_schema_version": "stage_collaborative_deliberation.stage_receipt.v1",
        "mechanism_version": 1, "active_contract_version": 1, "boot_manifest_version": 1,
        "registry_version": 1, "loader_version": 1,
        "profile_id_and_version": f'{profile["profile_id"]}@{profile["profile_version"]}',
        "loaded_paths": [PACKET, DECISION, validator.PROFILE_SET_PATH], "missing_partial_or_stale_paths": [],
        "trigger_evaluation_result_ref": "this managed stdout: bounded readiness-input pilot",
        "activation_mode_or_dormant_reason": "already covered task scope; no additional inquiry",
        "main_mechanism_ref": profile["main_mechanism_ref"], "detail_granularity_evaluation_result": "ordinary_local_choice",
        "open_detail_divergence_event_refs": [], "deferred_detail_record_refs": [],
        "gate_results": {"start": "pass", "completion": "pass"},
        "validator_mode_and_exit_code": {"mode": "instance", "exit_code": 0},
        "exact_candidate_version": candidate, "created_by_actor_ref": "actual-candidate-readiness-pilot-not-independent-reviewer",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    instance = {"task_scope": scope, "activation_mode": "dormant", "dormant_reason": "current task model already covers this ordinary action",
                "additional_inquiry_required": False, "current_model": model, "receipt": receipt}
    print(json.dumps({"pilot": "actual_candidate_readiness_not_stage_acceptance", "candidate": candidate,
                      "receipt_limit": "Input gate_results are test declarations, not observed canonical gate completion. This pilot does not request progression.",
                      "input": instance}, ensure_ascii=False, allow_nan=False), flush=True)
    with tempfile.TemporaryDirectory(prefix="os-actual-stage-pilot-") as temp:
        path = Path(temp) / "instance.json"
        for version in ("v1", "v2"):
            script = IMPL / ("verify_stage_collaborative_deliberation.py" if version == "v1" else "verify_stage_collaborative_deliberation_v2.py")
            for negative in (False, True):
                payload = copy.deepcopy(instance)
                if negative:
                    payload["task_scope"]["action_id"] = "not_in_durable_packet"
                path.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False), encoding="utf-8")
                result = subprocess.run([sys.executable, "-B", str(script), "instance", str(path), "--repo-root", str(ROOT),
                                         "--candidate", candidate, "--json-output"], cwd=ROOT,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25, check=False)
                print(json.dumps({"version": version, "negative": negative, "exit_code": result.returncode,
                                  "stdout": result.stdout.decode("utf-8"), "stderr": result.stderr.decode("utf-8")}, ensure_ascii=False), flush=True)
                if result.stderr or (result.returncode == 0) == negative:
                    return 1
    support.source_state(ROOT, candidate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

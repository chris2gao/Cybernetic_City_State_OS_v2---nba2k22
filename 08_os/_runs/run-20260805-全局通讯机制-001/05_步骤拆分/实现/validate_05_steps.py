"""Deterministic Stage 05 step-package validator for run-20260805-全局通讯机制-001.

Applies:
  * the Stage 05 rules of 08_os/01_workflow/05_步骤拆分/实现/最小运行schema_v1.yml
    and the Stage 05 branch of
    08_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py;
  * the exact changed-path allowlist of 01_任务输入/任务包_v1.yml (STAGE05-B01);
  * structural presence of the Stage 06 Human entry gate (STAGE05-B02);
  * structural closure responsibility for 06_执行/06_execution.yml against
    08_os/01_workflow/06_执行/实现/最小运行schema_v1.yml (STAGE05-B03).

Validation only; it authorizes nothing.
Exit codes: 0 pass, 2 findings, 3 load error.
"""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path

import yaml

STAGE05_DIR = Path(__file__).resolve().parents[1]
RUN = STAGE05_DIR.parent
OS_ROOT = RUN.parents[1]
STEPS = STAGE05_DIR / "05_steps.yml"
TESTS = RUN / "04_测试生成" / "04_tests.yml"
PACKET = RUN / "01_任务输入" / "任务包_v1.yml"
SCHEMA = OS_ROOT / "01_workflow" / "05_步骤拆分" / "实现" / "最小运行schema_v1.yml"
SCHEMA06 = OS_ROOT / "01_workflow" / "06_执行" / "实现" / "最小运行schema_v1.yml"
STAGE05_AUTH = STAGE05_DIR / "Human授权_进入阶段五_v1.yml"

STAGE_IDS = [
    "workflow_stage_01_requirement_modeling",
    "workflow_stage_02_information_collection",
    "workflow_stage_03_result_modeling",
    "workflow_stage_04_test_generation",
]
EXITS = {"pass", "retry", "invalidate_upstream"}
RUN_REL = "08_os/_runs/run-20260805-全局通讯机制-001"
GATE_ARTIFACT = f"{RUN_REL}/06_执行/Human授权_进入阶段六_v1.yml"
EXEC_ARTIFACT = f"{RUN_REL}/06_执行/06_execution.yml"


class StrictLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate mapping keys."""


def _no_duplicates(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key: {key!r}", key_node.start_mark
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates
)


def load_strict(path: Path):
    docs = list(yaml.load_all(path.read_text(encoding="utf-8"), Loader=StrictLoader))
    if len(docs) != 1:
        raise ValueError(f"{path.name}: expected exactly 1 YAML document, got {len(docs)}")
    return docs[0]


def allowed_by(pattern: str, path: str) -> bool:
    if pattern.endswith("/**"):
        return path.startswith(pattern[:-2])
    return path == pattern


def check_common(art, schema, findings):
    for field in schema["common_required_fields"]:
        if field not in art:
            findings.append(f"common_required_field_missing:{field}")
    if art.get("status") != "complete":
        findings.append("status_must_equal_complete")
    version = art.get("artifact_version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        findings.append("artifact_version_must_be_positive_integer")
    if art.get("stage_id") != schema["stage_id"]:
        findings.append("stage_id_mismatch")
    if art.get("artifact_kind") != schema["artifact_kind"]:
        findings.append("artifact_kind_mismatch")
    receipt = art.get("deliberation_receipt") or {}
    if receipt.get("profile_id") != schema["stage_id"]:
        findings.append("deliberation_receipt_must_bind_stage_profile")
    route = receipt.get("route")
    if route == "dormant" and receipt.get("session_id"):
        findings.append("dormant_receipt_must_not_create_session")
    if route in {"full", "incremental"} and not (
        receipt.get("task_gate_ref") and receipt.get("Human_authorization_ref")
    ):
        findings.append("full_or_incremental_receipt_requires_task_gate_and_authorization")


def check_predecessor(art, tests_art, findings):
    refs = {r.get("stage_id"): r for r in art.get("input_refs", []) if isinstance(r, dict)}
    ref = refs.get("workflow_stage_04_test_generation")
    if ref is None:
        findings.append("required_predecessor_missing:workflow_stage_04_test_generation")
        return
    if not ref.get("sha256"):
        findings.append("input_refs_must_bind_required_predecessor_sha256")
    else:
        actual = hashlib.sha256(TESTS.read_bytes()).hexdigest()
        if actual != ref["sha256"]:
            findings.append(f"predecessor_sha256_mismatch:{actual}")
    declared = ref.get("normalized_tests_sha256")
    frozen = (tests_art.get("payload") or {}).get("test_package_sha256")
    if declared and frozen and declared != frozen:
        findings.append("predecessor_normalized_digest_mismatch")
    if not (tests_art.get("payload") or {}).get("frozen"):
        findings.append("predecessor_not_frozen")


def check_steps(payload, test_ids, findings):
    budgets = {}
    deps = {}
    covered = set()
    for step in payload.get("steps", []):
        sid = step.get("step_id")
        if sid in budgets:
            findings.append(f"duplicate_step_id:{sid}")
        budgets[sid] = step.get("retry_budget")
        deps[sid] = set(step.get("depends_on") or [])
        ids = step.get("test_ids") or []
        if not ids or not set(ids).issubset(test_ids):
            findings.append(f"stage5_test_binding:{sid}")
        if len(set(ids)) != len(ids):
            findings.append(f"stage5_duplicate_test_id_in_step:{sid}")
        covered.update(ids)
        budget = budgets[sid]
        if not isinstance(budget, int) or isinstance(budget, bool) or not 1 <= budget <= 3:
            findings.append(f"stage5_retry_budget:{sid}")
        if set(step.get("exits") or []) != EXITS:
            findings.append(f"stage5_exits:{sid}")
        if step.get("invalidate_upstream_target") not in STAGE_IDS:
            findings.append(f"stage5_step_invalidation_target:{sid}")
        if not step.get("invalidate_upstream_reason"):
            findings.append(f"stage5_step_invalidation_reason:{sid}")
        for field in ("action", "prerequisites", "intended_changed_paths", "outputs", "validation"):
            if not step.get(field):
                findings.append(f"stage5_step_field_missing:{sid}:{field}")
    return budgets, deps, covered


def check_graph(budgets, deps, findings):
    if not budgets:
        findings.append("stage5_no_steps")
        return
    if any(not d.issubset(budgets) for d in deps.values()):
        findings.append("stage5_dependencies")
        return
    resolved = set()
    while True:
        new = {s for s, d in deps.items() if d.issubset(resolved)} - resolved
        if not new:
            break
        resolved.update(new)
    if resolved != set(budgets):
        findings.append("stage5_dependency_cycle")


def check_matrix(payload, test_ids, covered, findings):
    matrix = payload.get("test_coverage_matrix") or {}
    if set(matrix) != test_ids:
        findings.append("stage5_matrix_test_id_set_mismatch")
    steps = payload.get("steps", [])
    by_id = {s.get("step_id"): s for s in steps}
    for tid, refs in matrix.items():
        if not refs or not set(refs).issubset(by_id):
            findings.append(f"stage5_matrix_step_ref:{tid}")
            continue
        for sid in refs:
            if tid not in (by_id[sid].get("test_ids") or []):
                findings.append(f"stage5_matrix_not_reflected_in_step:{tid}:{sid}")
    for sid, step in by_id.items():
        for tid in step.get("test_ids") or []:
            if sid not in (matrix.get(tid) or []):
                findings.append(f"stage5_step_not_reflected_in_matrix:{sid}:{tid}")
    uncovered = sorted(test_ids - covered)
    if uncovered:
        findings.append("stage5_uncovered_tests:" + ",".join(uncovered))
    return uncovered


def check_duplicates_documented(payload, findings):
    matrix = payload.get("test_coverage_matrix") or {}
    documented = {d.get("test_id") for d in payload.get("duplicate_test_mappings") or []}
    actual = {t for t, s in matrix.items() if len(s) > 1}
    if documented != actual:
        findings.append(
            "stage5_duplicate_rationale_gap:" + ",".join(sorted(actual ^ documented))
        )
    for entry in payload.get("duplicate_test_mappings") or []:
        if not entry.get("rationale"):
            findings.append(f"stage5_duplicate_rationale_empty:{entry.get('test_id')}")


def check_invalidation(payload, findings):
    targets = payload.get("upstream_invalidation_targets") or []
    if not targets or not set(targets).issubset(set(STAGE_IDS)):
        findings.append("stage5_invalidation_targets")
    contract = payload.get("upstream_invalidation_contract") or []
    if {c.get("target_stage") for c in contract} != set(targets):
        findings.append("stage5_invalidation_contract_gap")
    for c in contract:
        if not c.get("exact_artifact") or not c.get("reopen_condition"):
            findings.append(f"stage5_invalidation_contract_incomplete:{c.get('target_stage')}")
        if c.get("silent_mutation") != "prohibited":
            findings.append(f"stage5_invalidation_allows_silent_mutation:{c.get('target_stage')}")


def collect_planned_paths(payload):
    """Every path the plan intends Stage 06 to write."""
    pom = payload.get("path_ownership_model") or {}
    planned = []
    planned += list(pom.get("planned_implementation_path_families") or [])
    for key in (
        "canonical_mechanism_root",
        "canonical_execution_root",
        "canonical_boot_root",
        "canonical_registry_file",
        "stage_06_run_output_root",
        "private_runtime_untracked",
    ):
        if pom.get(key):
            planned.append(pom[key])
    for step in payload.get("steps", []):
        planned += list(step.get("intended_changed_paths") or [])
    gate = payload.get("stage_06_entry_gate") or {}
    if gate.get("artifact"):
        planned.append(gate["artifact"])
    closure = payload.get("stage_06_closure_contract") or {}
    if closure.get("artifact"):
        planned.append(closure["artifact"])
    return planned


def check_planned_paths(payload, packet, findings):
    """STAGE05-B01: planned Stage 06 paths must be inside the task-packet allowlist."""
    allowlist = packet.get("allowed_changed_paths") or []
    if not allowlist:
        findings.append("task_packet_allowlist_missing")
        return
    for path in sorted(set(collect_planned_paths(payload))):
        if "<" in path or ">" in path:
            findings.append(f"planned_path_contains_placeholder:{path}")
            continue
        if not any(allowed_by(p, path) for p in allowlist):
            findings.append(f"planned_path_outside_task_allowlist:{path}")
    pom = payload.get("path_ownership_model") or {}
    if pom.get("authority") is None:
        findings.append("path_ownership_model_authority_missing")
    ref_only = (pom.get("runtime_logical_carrier_reference_only") or {}).get("value")
    if ref_only:
        if (pom.get("runtime_logical_carrier_reference_only") or {}).get(
            "writable_in_this_task"
        ) is not False:
            findings.append("runtime_logical_carrier_must_be_non_writable")
        for step in payload.get("steps", []):
            for path in step.get("intended_changed_paths") or []:
                if path.startswith(ref_only.split("<")[0]):
                    findings.append(
                        f"reference_only_carrier_planned_as_write:{step.get('step_id')}:{path}"
                    )


def check_stage06_gate(payload, findings):
    """STAGE05-B02: the Stage 06 Human gate must be a machine-checkable start condition."""
    gate = payload.get("stage_06_entry_gate")
    if not isinstance(gate, dict):
        findings.append("stage06_entry_gate_missing")
        return
    if gate.get("artifact") != GATE_ARTIFACT:
        findings.append(f"stage06_gate_artifact_unexpected:{gate.get('artifact')}")
    if gate.get("fail_closed") is not True:
        findings.append("stage06_gate_not_fail_closed")
    if gate.get("self_authorization_prohibited") is not True:
        findings.append("stage06_gate_self_authorization_not_prohibited")

    assertions = gate.get("required_assertions") or []
    joined = " ".join(str(a) for a in assertions)
    if "enter_stage_06_execution == true" not in joined:
        findings.append("stage06_gate_missing_true_assertion")
    if "accepted_stage05_step_package_git_blob_sha" not in joined:
        findings.append("stage06_gate_missing_accepted_plan_binding")
    if not gate.get("absent_or_false_behavior"):
        findings.append("stage06_gate_missing_absent_behavior")

    by_id = {s.get("step_id"): s for s in payload.get("steps", [])}
    sid = gate.get("enforced_by_step")
    step = by_id.get(sid)
    if step is None:
        findings.append(f"stage06_gate_enforcing_step_unknown:{sid}")
    else:
        if step.get("blocking_prerequisite_ref") != gate.get("artifact"):
            findings.append(f"stage06_gate_not_bound_to_step:{sid}")
        if step.get("fail_closed_without_blocking_prerequisite") is not True:
            findings.append(f"stage06_gate_step_not_fail_closed:{sid}")
        if step.get("depends_on"):
            findings.append(f"stage06_gate_step_is_not_first:{sid}")

    unchanged = gate.get("stage_05_authorization_unchanged") or {}
    if unchanged.get("enter_stage_06_execution") is not False:
        findings.append("stage05_authorization_claim_must_be_false")
    if unchanged.get("is_not_a_start_condition") is not True:
        findings.append("stage05_authorization_must_not_be_start_condition")
    try:
        auth = load_strict(STAGE05_AUTH)
    except Exception as exc:  # noqa: BLE001
        findings.append(f"stage05_authorization_unreadable:{type(exc).__name__}")
        return
    physical = (auth.get("authorization") or {}).get("enter_stage_06_execution")
    if physical is not False:
        findings.append(f"stage05_authorization_physically_not_false:{physical}")


def check_stage06_closure(payload, schema06, findings):
    """STAGE05-B03: the plan must own materialization and validation of 06_execution.yml."""
    closure = payload.get("stage_06_closure_contract")
    if not isinstance(closure, dict):
        findings.append("stage06_closure_contract_missing")
        return
    if closure.get("artifact") != EXEC_ARTIFACT:
        findings.append(f"stage06_closure_artifact_unexpected:{closure.get('artifact')}")
    if not SCHEMA06.exists():
        findings.append("stage06_schema_file_missing")
    if closure.get("stage_id") != schema06.get("stage_id"):
        findings.append("stage06_closure_stage_id_mismatch")
    if closure.get("artifact_kind") != schema06.get("artifact_kind"):
        findings.append("stage06_closure_artifact_kind_mismatch")

    required = set(schema06.get("payload_required_fields") or [])
    declared = set(closure.get("required_payload_fields") or [])
    if declared != required:
        findings.append(
            "stage06_closure_payload_fields_mismatch:" + ",".join(sorted(required ^ declared))
        )

    rules = set(closure.get("integrity_rules") or [])
    missing_rules = set(schema06.get("stage_specific_rules") or []) - rules
    if missing_rules:
        findings.append("stage06_closure_missing_rules:" + ",".join(sorted(missing_rules)))

    bindings = {b.get("stage_id") for b in closure.get("required_predecessor_bindings") or []}
    if bindings != set(schema06.get("required_predecessors") or []):
        findings.append("stage06_closure_predecessor_binding_gap")

    by_id = {s.get("step_id"): s for s in payload.get("steps", [])}
    owner = closure.get("materialized_and_validated_by_step")
    step = by_id.get(owner)
    if step is None:
        findings.append(f"stage06_closure_owner_step_unknown:{owner}")
    else:
        if step.get("stage_06_closure_responsibility") is not True:
            findings.append(f"stage06_closure_owner_not_flagged:{owner}")
        if EXEC_ARTIFACT not in (step.get("intended_changed_paths") or []):
            findings.append(f"stage06_closure_artifact_not_in_owner_paths:{owner}")
    accum = set(closure.get("accumulated_by_steps") or [])
    if accum != set(by_id) - {owner}:
        findings.append("stage06_closure_accumulation_step_set_mismatch")
    if not closure.get("completion_rule"):
        findings.append("stage06_closure_completion_rule_missing")
    if closure.get("executor_self_check_is_not_acceptance") is not True:
        findings.append("stage06_closure_self_check_acceptance_not_denied")
    record = payload.get("execution_record_accumulation") or {}
    if record.get("retro_fabrication_prohibited") is not True:
        findings.append("stage06_execution_record_retro_fabrication_not_prohibited")


def main() -> int:
    try:
        schema = load_strict(SCHEMA)
        schema06 = load_strict(SCHEMA06)
        art = load_strict(STEPS)
        tests_art = load_strict(TESTS)
        packet = load_strict(PACKET)
    except Exception as exc:  # noqa: BLE001
        print(f"load_error:{type(exc).__name__}:{exc}", file=sys.stderr)
        return 3

    findings: list[str] = []
    test_ids = {t.get("test_id") for t in (tests_art.get("payload") or {}).get("tests", [])}
    check_common(art, schema, findings)
    check_predecessor(art, tests_art, findings)

    payload = art.get("payload") or {}
    for field in schema["payload_required_fields"]:
        if field not in payload:
            findings.append(f"payload_required_field_missing:{field}")

    budgets, deps, covered = check_steps(payload, test_ids, findings)
    check_graph(budgets, deps, findings)
    uncovered = check_matrix(payload, test_ids, covered, findings)
    check_duplicates_documented(payload, findings)
    check_invalidation(payload, findings)
    check_planned_paths(payload, packet, findings)
    check_stage06_gate(payload, findings)
    check_stage06_closure(payload, schema06, findings)

    if payload.get("stage_06_authorized") is not False:
        findings.append("stage5_must_not_authorize_stage06")
    if payload.get("step_count") != len(budgets):
        findings.append("stage5_step_count_mismatch")

    planned = sorted(set(collect_planned_paths(payload)))
    print(f"frozen_test_count={len(test_ids)}")
    print(f"step_count={len(budgets)}")
    print(f"covered_test_count={len(covered)}")
    print(f"uncovered_test_ids={uncovered}")
    print(f"retry_budgets={sorted(set(budgets.values()))}")
    print(f"planned_path_count={len(planned)}")
    print(f"stage06_gate_enforced_by={(payload.get('stage_06_entry_gate') or {}).get('enforced_by_step')}")
    print(
        "stage06_closure_owner="
        f"{(payload.get('stage_06_closure_contract') or {}).get('materialized_and_validated_by_step')}"
    )
    print(f"findings={len(findings)}")
    for f in findings:
        print(f, file=sys.stderr)
    return 2 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

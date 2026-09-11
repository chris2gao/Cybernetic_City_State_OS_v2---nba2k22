#!/usr/bin/env python3
"""Deterministic validator for the staged stage-collaborative-deliberation mechanism."""
from __future__ import annotations
import argparse, hashlib, hmac, json, re, sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

PASS = 0
EXIT = {
    "missing": 10,
    "schema": 11,
    "stale": 12,
    "reference": 13,
    "invariant": 14,
    "unauthorized": 15,
    "profile": 16,
    "receipt": 17,
    "review": 18,
    "internal": 19,
}

FAILURE_TO_EXIT = {
    "missing_partial_or_stale_load_fail_open": 12,
    "unknown_dependency_fail_open": 13,
    "agreement_used_as_fact_proof": 14,
    "grounding_collapsed_into_authority": 14,
    "silence_or_response_as_agreement": 14,
    "residual_objection_erased": 14,
    "option_selection_used_as_truth": 14,
    "recommendation_used_as_authorization": 15,
    "authority_used_as_epistemic_truth": 14,
    "unbound_or_ambiguous_confirmation": 15,
    "silent_or_unscoped_invalidation": 14,
    "unverified_model_agreement_as_independent_confirmation": 18,
    "executor_self_clearance": 18,
    "execution_without_current_authority": 15,
    "premature_completion": 14,
    "collapsed_state_dimensions": 14,
    "unjustified_micro_approval_escalation": 14,
    "headcount_used_as_disposition": 14,
    "unapproved_second_order_scope_expansion": 15,
    "deferred_detail_not_durable": 14,
    "unnormalized_external_material": 14,
    "stage_profile_main_obligation_missing": 16,
    "receipt_detail_visibility_missing": 17,
    "formalistic_round_counting": 16,
    "unjustified_full_activation": 16,
    "load_bearing_gap_silently_skipped": 16,
}

REQUIRED_STATIC_PATHS = [
    "01_os/03_mechanisms/stage_collaborative_deliberation/README.md",
    "01_os/03_mechanisms/stage_collaborative_deliberation/方法论_v1.md",
    "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profile契约_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profiles_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现/结果对象契约_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现/状态转换与不变量契约_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现/路由与失败契约_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现/加载与receipt契约_v1.yml",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation.py",
    "01_os/02_boot/stage_collaborative_deliberation/启动清单_v1.yml",
    "01_os/05_registry/stage_collaborative_deliberation_v1.yml",
    "01_os/06_execution/boot/stage_collaborative_deliberation/README.md",
]
WORKFLOW_PROFILE_REFERENCE_GLOB = "01_os/01_workflow/*/实现/阶段协同推演profile引用_v1.yml"
REQUIRED_RECEIPT_FIELDS = [
    "receipt_schema_version","mechanism_version","active_contract_version",
    "boot_manifest_version","registry_version","loader_version",
    "profile_id_and_version","loaded_paths","missing_partial_or_stale_paths",
    "trigger_evaluation_result_ref","activation_mode_or_dormant_reason",
    "main_mechanism_ref","detail_granularity_evaluation_result",
    "open_detail_divergence_event_refs","deferred_detail_record_refs",
    "gate_results","validator_mode_and_exit_code","exact_candidate_version",
    "created_by_actor_ref","created_at",
]

def load_doc(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    if yaml is None:
        try:
            return json.loads(text)
        except Exception as exc:
            raise RuntimeError("PyYAML unavailable and file is not JSON") from exc
    return yaml.safe_load(text)

def select_case(doc: Any, case_id: str | None) -> Any:
    if isinstance(doc, dict) and "cases" in doc:
        if not case_id:
            raise ValueError("--case-id is required for suite files")
        for case in doc["cases"]:
            if case.get("case_id") == case_id:
                return case
        raise KeyError(f"case not found: {case_id}")
    return doc

def direct_error_code(data: dict[str, Any]) -> int:
    order = [
        ("internal_error", 19), ("review_execution_errors", 18),
        ("receipt_errors", 17), ("profile_gate_errors", 16),
        ("unauthorized_actions", 15), ("invariant_violations", 14),
        ("unresolved_refs", 13), ("stale_components", 12),
        ("schema_mismatch", 11), ("missing_required_paths", 10),
    ]
    for key, code in order:
        value = data.get(key)
        if value:
            return code
    failure_code = data.get("failure_code")
    if failure_code:
        return FAILURE_TO_EXIT.get(failure_code, 14)
    return 0

def validate_static_fixture(data: dict[str, Any]) -> int:
    code = direct_error_code(data)
    if code:
        return code
    snapshot = data.get("snapshot")
    if snapshot is None:
        return 0
    if snapshot.get("required_paths_resolve") is not True:
        return 10
    if snapshot.get("mechanism_version") != 1:
        return 11
    expected = {
        "profiles": 7,
        "object_types": 45,
        "result_names": 47,
        "state_dimensions": 10,
        "active_invariants": 16,
        "failure_codes": 26,
        "workflow_references": 7,
    }
    if any(snapshot.get(k) != v for k, v in expected.items()):
        return 11
    if snapshot.get("activation_state") != "staged_inert":
        return 15
    return 0

def validate_static_repo(repo_root: Path) -> int:
    missing = [p for p in REQUIRED_STATIC_PATHS if not (repo_root / p).exists()]
    if missing:
        return 10
    try:
        profile_set = load_doc(repo_root / REQUIRED_STATIC_PATHS[3])
        result_contract = load_doc(repo_root / REQUIRED_STATIC_PATHS[4])
        invariant_contract = load_doc(repo_root / REQUIRED_STATIC_PATHS[5])
        router_contract = load_doc(repo_root / REQUIRED_STATIC_PATHS[6])
        load_contract = load_doc(repo_root / REQUIRED_STATIC_PATHS[7])
        boot = load_doc(repo_root / REQUIRED_STATIC_PATHS[9])
        registry = load_doc(repo_root / REQUIRED_STATIC_PATHS[10])
    except Exception:
        return 11
    profiles = profile_set.get("profiles", [])
    active_profile_ids = {p.get("profile_id") for p in profiles}
    if len(profiles) != 7 or len(active_profile_ids) != 7 or None in active_profile_ids:
        return 16
    workflow_ref_paths = sorted(repo_root.glob(WORKFLOW_PROFILE_REFERENCE_GLOB))
    if len(workflow_ref_paths) != 7:
        return 16
    try:
        workflow_refs = [load_doc(path) for path in workflow_ref_paths]
    except Exception:
        return 11
    workflow_profile_ids = [ref.get("profile_id") if isinstance(ref, dict) else None for ref in workflow_refs]
    if len(set(workflow_profile_ids)) != 7 or set(workflow_profile_ids) != active_profile_ids:
        return 16
    if result_contract.get("measurements", {}).get("catalog_unique_object_types") != 45:
        return 11
    if invariant_contract.get("measurements", {}).get("active_invariants") != 16:
        return 11
    union = router_contract.get("complete_failure_code_union", [])
    codes = [x["code"] if isinstance(x, dict) else x for x in union]
    if len(codes) != 26 or len(set(codes)) != 26:
        return 11
    required = set(load_contract.get("stage_receipt", {}).get("required_fields", []))
    if not set(REQUIRED_RECEIPT_FIELDS).issubset(required):
        return 17
    versions = {
        boot.get("mechanism_version"), registry.get("mechanism_version"),
        result_contract.get("mechanism_version"), invariant_contract.get("mechanism_version"),
        router_contract.get("mechanism_version"), load_contract.get("mechanism_version"),
    }
    if versions != {1}:
        return 11
    if boot.get("activation_state") != "staged_inert" or registry.get("activation_state") != "staged_inert":
        return 15
    return 0

PROFILE_SET_PATH = "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profiles_v1.yml"
PROFILE_CONTRACT_PATH = "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profile契约_v1.yml"
RESOLVED_DISPOSITIONS = {"resolved", "deferred_non_blocking"}
# Allowed dispositions for a model element, from the profile contract's
# model_space_contract. Field occupancy alone never proves adequacy.
REPRESENTED = "represented_with_supported_value"
EXPLICITLY_IRRELEVANT = "explicitly_irrelevant_with_reason_and_scope"
UNKNOWN_DISPOSED = "unknown_with_blocking_or_deferred_disposition_and_revisit_trigger"
ALLOWED_ELEMENT_DISPOSITIONS = {REPRESENTED, EXPLICITLY_IRRELEVANT, UNKNOWN_DISPOSED}
# Nothing in this set is a Human decision, however it is labelled.
NON_DISPOSITION_BASIS_KINDS = {"silence", "no_response", "inferred", "implied", "assumed"}
# Only the current Human confirms. No model-side actor substitutes for that.
NON_HUMAN_ACTOR_CLASSES = {"executor", "reviewer", "independent_reviewer", "model", "agent"}
# Canonical common-model field names. These are the only spellings used by the
# profile contract, the result projection, the validator and every fixture. No
# synonym or compatibility alias exists.
#
# Three classes, because "checked and there is nothing" is a real answer that
# must be expressible, while "never considered" must not pass:
#   substantive - the key must be present and carry a non-empty value
#   nullable    - the key must be present; none_material is an accepted answer
#   listed      - the key must be present and be a list; [] means "checked, none"
# A single `if not model.get(field)` cannot tell a missing key from a valid
# empty disposition, which is why the classes are separate.
NONE_MATERIAL = "none_material"
SUBSTANTIVE_COMMON_FIELDS = (
    "problem_or_objective",
    # Why now is not the same question as what. A stage that cannot say why it is
    # running at this point in the task is usually running out of momentum.
    "why_this_stage_is_needed_now",
    "Human_intent_understanding",
    "current_baseline_and_inputs",
    "proposed_method_or_solution",
    "feasibility_support",
    "expected_output",
    "verification_or_acceptance_method",
    "current_exact_model_version",
)
NULLABLE_COMMON_FIELDS = (
    "constraints_and_dependencies",
    "assumptions_risks_alternatives_unknowns",
    # none_material is a real answer here: an early stage may genuinely have no
    # downstream consumer yet. "Never considered" is not.
    "downstream_impact",
)
CLOSURE_FIELDS = (
    "plan_vs_actual_delta",
    "material_deviation",
    "residual_risk",
    "downstream_baseline",
)
LISTED_COMMON_FIELDS = ("open_load_bearing_items",)
STAGE_MODEL_COMPLETENESS_FIELDS = (
    SUBSTANTIVE_COMMON_FIELDS + NULLABLE_COMMON_FIELDS + LISTED_COMMON_FIELDS
)


def validate_common_model_completeness(model: dict[str, Any]) -> int:
    """Presence and disposition of every common Current Model field.

    Missing key fails. An explicit empty disposition - none_material, or [] for
    open_load_bearing_items - passes, because it records that the dimension was
    considered and found empty. A present-but-null value fails: it is neither a
    value nor a disposition.
    """
    for field in SUBSTANTIVE_COMMON_FIELDS:
        if field not in model:
            return 16
        if not model.get(field):
            return 16
    for field in NULLABLE_COMMON_FIELDS:
        if field not in model:
            return 16
        value = model.get(field)
        if value is None or value == "":
            return 16
    for field in LISTED_COMMON_FIELDS:
        if field not in model:
            return 16
        if not isinstance(model.get(field), list):
            return 11
    return 0


def repo_root_from_here() -> Path:
    # 01_os/03_mechanisms/stage_collaborative_deliberation/实现/<this file>
    return Path(__file__).resolve().parents[4]


def load_profile_set(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or repo_root_from_here()
    doc = load_doc(root / PROFILE_SET_PATH)
    if not isinstance(doc, dict):
        raise ValueError("profile set must be a mapping")
    return doc


def load_profile_contract(repo_root: Path | None = None) -> dict[str, Any]:
    """Read the contract rather than restating it as constants.

    The allowed feasibility basis kinds live in one place. Copying the table into
    this file would create exactly the drift this mechanism exists to catch: a
    contract that says one thing while the checker enforces another.
    """
    root = repo_root or repo_root_from_here()
    doc = load_doc(root / PROFILE_CONTRACT_PATH)
    if not isinstance(doc, dict):
        raise ValueError("profile contract must be a mapping")
    return doc


def resolve_profile(profile_id_and_version: Any, repo_root: Path | None = None) -> dict[str, Any] | None:
    """Resolve the exact profile named by a receipt's profile_id_and_version.

    Returns None when the reference is malformed or does not resolve, which the
    caller must treat as a failure - a stage cannot be validated against a
    profile that was never identified.
    """
    if not isinstance(profile_id_and_version, str) or "@" not in profile_id_and_version:
        return None
    profile_id, _, raw_version = profile_id_and_version.partition("@")
    try:
        version = int(raw_version)
    except ValueError:
        return None
    for profile in load_profile_set(repo_root).get("profiles", []):
        if not isinstance(profile, dict):
            continue
        if profile.get("profile_id") == profile_id and profile.get("profile_version") == version:
            return profile
    return None


def validate_effective_stage_model(
    data: dict[str, Any], model: dict[str, Any], repo_root: Path | None = None
) -> int:
    """effective_current_stage_model = common_task_stage_model + this profile's
    required_model_fields.

    The common fields are validated once, centrally; the stage-specific fields
    come from the exact profile resolved for this stage, so the common set is
    never copied into the seven profiles. Validating only the common fields
    would let any stage pass another stage's obligations.
    """
    receipt = data.get("receipt")
    reference = receipt.get("profile_id_and_version") if isinstance(receipt, dict) else None
    try:
        profile = resolve_profile(reference, repo_root)
    except Exception:
        return 11
    if profile is None:
        # unidentified or mismatched profile: the stage obligations are unknown
        return 16
    declared = data.get("stage_profile_id_and_version")
    if declared is not None and declared != reference:
        # the instance claims one profile while the receipt binds another
        return 16

    elements = model.get("stage_specific_model_elements")
    if not isinstance(elements, dict):
        return 16
    for field in profile.get("required_model_fields", []):
        element = elements.get(field)
        if not isinstance(element, dict):
            return 16
        disposition = element.get("disposition")
        if disposition not in ALLOWED_ELEMENT_DISPOSITIONS:
            return 16
        if disposition == REPRESENTED and element.get("value") in (None, "", [], {}):
            return 16
        if disposition == EXPLICITLY_IRRELEVANT and not element.get("reason_and_scope"):
            return 16
        if disposition == UNKNOWN_DISPOSED:
            code = validate_deferred_unknown(element)
            if code:
                return code
    return 0


# Every dimension a deferral has to clear before it counts as non-blocking.
DOWNSTREAM_IMPACT_DIMENSIONS = (
    "stage_objective_blocked",
    "decision_blocked",
    "verification_blocked",
    "authority_blocked",
    "downstream_acceptance_blocked",
)


def validate_deferred_unknown(element: dict[str, Any], *, _validated_task_scope: bool = False) -> int:
    """A required stage field disposed as unknown blocks by default.

    UNKNOWN_DISPOSED stays a real capability - some things genuinely are not
    known yet - but the model does not get to declare its own unknown harmless.
    Progression is allowed only for a deferral that is explicitly
    deferred_nonblocking, states its reason and scope, carries a revisit
    trigger, and clears every downstream impact dimension explicitly. Writing
    blocking: false with a revisit_trigger is not a justification.

    An unknown that is itself load-bearing, or that sits on a Human decision
    boundary, additionally needs a current Human basis - and silence, inference
    or a stale basis is not one.
    """
    if element.get("blocking") is not False:
        # blocking unknown, or unstated: default is to block
        return 16
    if element.get("deferral") != "deferred_nonblocking":
        return 16
    if not element.get("reason_and_scope"):
        return 16
    if not element.get("revisit_trigger"):
        return 16

    assessment = element.get("downstream_impact_assessment")
    if not isinstance(assessment, dict):
        return 16
    for dimension in DOWNSTREAM_IMPACT_DIMENSIONS:
        if assessment.get(dimension) is not False:
            # unstated or asserted-blocked both block
            return 16

    if not _validated_task_scope and (element.get("load_bearing") is True or element.get("Human_decision_boundary") is True):
        basis = element.get("Human_basis")
        if not isinstance(basis, dict):
            return 15
        if basis.get("kind") in NON_DISPOSITION_BASIS_KINDS:
            return 14
        if basis.get("stale") is True:
            return 12
        if basis.get("actor_class") != "current_Human":
            return 15
    return 0


# ---------------------------------------------------------------------------
# Human Task Authority v2
# ---------------------------------------------------------------------------
HUMAN_AUTHORITY_SCHEME = "citystate-human-task-authority-v2"
LEGACY_HUMAN_AUTHORITY_SCHEME = "citystate-human-authority-v1"
HUMAN_AUTHORITY_ALGORITHM = "sha256"
TASK_AUTHORITY_BOUND_FIELDS = (
    "task_id", "task_authority_id", "initial_authority_holder_endpoint_id",
    "initial_authority_holder_task_role", "Human_disposition", "task_authority_scope",
)
EVENT_COMMITMENT_BOUND_FIELDS = (
    "task_id", "task_authority_id", "stage_id", "decision_id", "decision_type",
    "exact_model_version", "Human_disposition", "authorized_scope",
)
LEGACY_COMMITMENT_BOUND_FIELDS = (
    "task_id", "stage_id", "decision_id", "decision_type", "exact_model_version",
    "Human_disposition", "authorized_scope",
)
COMMITMENT_BOUND_FIELDS = EVENT_COMMITMENT_BOUND_FIELDS
AUTHORIZATION_DECISION_TYPE = "substantive_execution_authorization"
COMPLETION_DECISION_TYPE = "completion_acceptance"
DECISION_TYPES = {
    AUTHORIZATION_DECISION_TYPE,
    COMPLETION_DECISION_TYPE,
    "material_architecture_or_solution_choice",
    "material_scope_change",
    "Human_risk_acceptance",
    "protected_or_irreversible_action_authorization",
    "delegation_override_or_revocation",
    "review_routing_override",
}
LEGACY_DECISION_TYPES = {AUTHORIZATION_DECISION_TYPE, COMPLETION_DECISION_TYPE}
AFFIRMATIVE_DISPOSITIONS = {"confirmed", "accepted", "authorized"}


def _canonical_payload(scheme: str, fields: tuple[str, ...], bound: dict[str, Any], human_nonce: str) -> bytes:
    payload = {"domain": scheme, "Human_nonce": human_nonce}
    for field in fields:
        payload[field] = bound.get(field)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_commitment_payload(bound: dict[str, Any], human_nonce: str) -> bytes:
    """Canonical v2 decision-event commitment payload."""
    return _canonical_payload(HUMAN_AUTHORITY_SCHEME, EVENT_COMMITMENT_BOUND_FIELDS, bound, human_nonce)


def compute_commitment(bound: dict[str, Any], human_nonce: str) -> str:
    return hashlib.sha256(canonical_commitment_payload(bound, human_nonce)).hexdigest()


def compute_task_commitment(bound: dict[str, Any], human_nonce: str) -> str:
    return hashlib.sha256(_canonical_payload(
        HUMAN_AUTHORITY_SCHEME, TASK_AUTHORITY_BOUND_FIELDS, bound, human_nonce
    )).hexdigest()


def compute_legacy_commitment(bound: dict[str, Any], human_nonce: str) -> str:
    return hashlib.sha256(_canonical_payload(
        LEGACY_HUMAN_AUTHORITY_SCHEME, LEGACY_COMMITMENT_BOUND_FIELDS, bound, human_nonce
    )).hexdigest()


def validate_commitment_structure(commitment: Any, *, allowed_schemes: set[str] | None = None) -> int:
    if not isinstance(commitment, dict):
        return 15
    schemes = allowed_schemes or {HUMAN_AUTHORITY_SCHEME, LEGACY_HUMAN_AUTHORITY_SCHEME}
    if commitment.get("scheme") not in schemes:
        return 15
    if commitment.get("algorithm") != HUMAN_AUTHORITY_ALGORITHM:
        return 15
    digest = commitment.get("digest")
    if not isinstance(digest, str) or len(digest) != 64:
        return 15
    try:
        int(digest, 16)
    except ValueError:
        return 15
    for forbidden in ("Human_nonce", "nonce", "plaintext", "code"):
        if forbidden in commitment:
            return 14
    return 0


def authority_record_scheme(record: dict[str, Any]) -> str:
    return str((record.get("nonce_commitment") or {}).get("scheme") or "")


def validate_authority_record_commitments(record: dict[str, Any]) -> int:
    scheme = authority_record_scheme(record)
    if scheme == HUMAN_AUTHORITY_SCHEME:
        code = validate_commitment_structure(
            record.get("task_nonce_commitment"), allowed_schemes={HUMAN_AUTHORITY_SCHEME}
        )
        if code:
            return code
        return validate_commitment_structure(
            record.get("nonce_commitment"), allowed_schemes={HUMAN_AUTHORITY_SCHEME}
        )
    if scheme == LEGACY_HUMAN_AUTHORITY_SCHEME:
        return validate_commitment_structure(
            record.get("nonce_commitment"), allowed_schemes={LEGACY_HUMAN_AUTHORITY_SCHEME}
        )
    return 15


def resolve_durable_disposition(
    confirmation: dict[str, Any], repo_root: Path | None
) -> tuple[int, dict[str, Any] | None]:
    ref = confirmation.get("durable_disposition_ref")
    expected_blob = confirmation.get("durable_disposition_blob_sha")
    if not ref or not isinstance(ref, str) or not expected_blob or not isinstance(expected_blob, str):
        return 15, None
    root = repo_root or repo_root_from_here()
    target = root / ref
    if not target.is_file():
        return 13, None
    payload = target.read_bytes()
    actual = hashlib.sha1(b"blob %d\0" % len(payload) + payload).hexdigest()
    if actual != expected_blob:
        return 13, None
    try:
        record = load_doc(target)
    except Exception:
        return 11, None
    if not isinstance(record, dict):
        return 11, None
    return 0, record


SYNTHETIC_MARKER = "synthetic_test_record"


def _validate_common_Human_record(record: dict[str, Any]) -> int:
    if record.get("provenance") != "foreground_current_Human_interaction":
        return 15
    if record.get("actor_class") != "current_Human":
        return 15
    if record.get("explicit") is not True:
        return 14
    if record.get("Human_disposition") not in AFFIRMATIVE_DISPOSITIONS:
        return 15
    if record.get("stale") is True or record.get("invalidated") is True:
        return 12
    return 0


def _validate_legacy_record(record: dict[str, Any], confirmation: dict[str, Any], model: dict[str, Any]) -> int:
    code = _validate_common_Human_record(record)
    if code:
        return code
    if record.get("consumed_by") not in (None, record.get("decision_id")):
        return 12
    decision_type = record.get("decision_type")
    if decision_type not in LEGACY_DECISION_TYPES:
        return 15
    if confirmation.get("decision_id") != record.get("decision_id"):
        return 15
    if confirmation.get("decision_type") not in (None, decision_type):
        return 15
    if record.get("exact_model_version") != model.get("current_exact_model_version"):
        return 12
    if confirmation.get("exact_model_version") != record.get("exact_model_version"):
        return 12
    if not record.get("authorized_scope"):
        return 15
    code = validate_commitment_structure(
        record.get("nonce_commitment"), allowed_schemes={LEGACY_HUMAN_AUTHORITY_SCHEME}
    )
    if code:
        return code
    stated = confirmation.get("nonce_commitment")
    code = validate_commitment_structure(stated, allowed_schemes={LEGACY_HUMAN_AUTHORITY_SCHEME})
    if code:
        return code
    return 0 if stated.get("digest") == record["nonce_commitment"].get("digest") else 13


def _validate_v2_record(record: dict[str, Any], confirmation: dict[str, Any], model: dict[str, Any]) -> int:
    code = _validate_common_Human_record(record)
    if code:
        return code
    if record.get("task_authority_revoked") is True or record.get("event_revoked") is True:
        return 12
    task_authority_id = record.get("task_authority_id")
    if not isinstance(task_authority_id, str) or not task_authority_id:
        return 15
    if confirmation.get("task_authority_id") != task_authority_id:
        return 15
    holder = record.get("initial_authority_holder_endpoint_id")
    holder_role = record.get("initial_authority_holder_task_role")
    if not isinstance(holder, str) or not holder or not isinstance(holder_role, str) or not holder_role:
        return 15
    task_scope = record.get("task_authority_scope")
    if (
        not isinstance(task_scope, list) or not task_scope
        or any(not isinstance(item, str) or not item for item in task_scope)
        or len(task_scope) != len(set(task_scope))
    ):
        return 15
    decision_type = record.get("decision_type")
    if decision_type not in DECISION_TYPES:
        return 15
    if confirmation.get("decision_id") != record.get("decision_id"):
        return 15
    if confirmation.get("decision_type") not in (None, decision_type):
        return 15
    if record.get("exact_model_version") != model.get("current_exact_model_version"):
        return 12
    if confirmation.get("exact_model_version") != record.get("exact_model_version"):
        return 12
    if not record.get("authorized_scope"):
        return 15
    code = validate_authority_record_commitments(record)
    if code:
        return code
    stated_task = confirmation.get("task_nonce_commitment")
    stated_event = confirmation.get("nonce_commitment")
    if validate_commitment_structure(stated_task, allowed_schemes={HUMAN_AUTHORITY_SCHEME}):
        return 15
    if validate_commitment_structure(stated_event, allowed_schemes={HUMAN_AUTHORITY_SCHEME}):
        return 15
    if stated_task.get("digest") != record["task_nonce_commitment"].get("digest"):
        return 13
    if stated_event.get("digest") != record["nonce_commitment"].get("digest"):
        return 13
    return 0


def validate_durable_disposition_record(
    record: dict[str, Any], confirmation: dict[str, Any], model: dict[str, Any], *,
    synthetic_authority_context: bool = False,
) -> int:
    if record.get(SYNTHETIC_MARKER) is True and not synthetic_authority_context:
        return 15
    scheme = authority_record_scheme(record)
    if scheme == LEGACY_HUMAN_AUTHORITY_SCHEME:
        if not synthetic_authority_context:
            # v1 is historical/challenge-only after v2 activation.
            return 15
        return _validate_legacy_record(record, confirmation, model)
    if scheme != HUMAN_AUTHORITY_SCHEME:
        return 15
    return _validate_v2_record(record, confirmation, model)


def validate_human_authority(
    model: dict[str, Any], data: dict[str, Any], repo_root: Path | None = None, *,
    synthetic_authority_context: bool = False,
) -> int:
    confirmation = model.get("Human_confirmation")
    if not isinstance(confirmation, dict):
        return 15
    code, record = resolve_durable_disposition(confirmation, repo_root)
    if code:
        return code
    assert record is not None
    task_id = data.get("task_id")
    stage_id = data.get("stage_id")
    receipt = data.get("receipt")
    if stage_id is None and isinstance(receipt, dict):
        stage_id = receipt.get("profile_id_and_version")
    if task_id is not None and record.get("task_id") != task_id:
        return 15
    # v2 task authority spans workflow stages; the event remains exact-stage bound when stage_id is present.
    if stage_id is not None and record.get("stage_id") != stage_id:
        return 15
    return validate_durable_disposition_record(
        record, confirmation, model, synthetic_authority_context=synthetic_authority_context
    )


def verify_human_challenge(record: dict[str, Any], human_nonce: str) -> tuple[bool, str, str]:
    scheme = authority_record_scheme(record)
    if scheme == HUMAN_AUTHORITY_SCHEME:
        task_bound = {field: record.get(field) for field in TASK_AUTHORITY_BOUND_FIELDS}
        event_bound = {field: record.get(field) for field in EVENT_COMMITMENT_BOUND_FIELDS}
        task_recomputed = compute_task_commitment(task_bound, human_nonce)
        event_recomputed = compute_commitment(event_bound, human_nonce)
        task_stored = (record.get("task_nonce_commitment") or {}).get("digest", "")
        event_stored = (record.get("nonce_commitment") or {}).get("digest", "")
        ok = hmac.compare_digest(task_recomputed, task_stored) and hmac.compare_digest(event_recomputed, event_stored)
        return ok, event_recomputed, event_stored
    if scheme == LEGACY_HUMAN_AUTHORITY_SCHEME:
        bound = {field: record.get(field) for field in LEGACY_COMMITMENT_BOUND_FIELDS}
        recomputed = compute_legacy_commitment(bound, human_nonce)
        stored = (record.get("nonce_commitment") or {}).get("digest", "")
        return hmac.compare_digest(recomputed, stored), recomputed, stored
    return False, "", ""


def validate_mandatory_Human_confirmation(model: dict[str, Any]) -> int:
    confirmation = model.get("Human_confirmation")
    if not isinstance(confirmation, dict):
        return 15
    if confirmation.get("explicit") is not True:
        return 14
    if confirmation.get("kind") in NON_DISPOSITION_BASIS_KINDS:
        return 14
    if confirmation.get("actor_class") in NON_HUMAN_ACTOR_CLASSES:
        return 15
    if confirmation.get("actor_class") != "current_Human":
        return 15
    if confirmation.get("scope") not in {None, "current_stage", "current_task"}:
        return 12
    if confirmation.get("stale") is True:
        return 12
    bound = confirmation.get("bound_model_version")
    if not bound or bound != model.get("current_exact_model_version"):
        return 12
    if not confirmation.get("durable_disposition_ref") or not confirmation.get("durable_disposition_blob_sha"):
        return 15
    if not confirmation.get("decision_id"):
        return 15
    stated = confirmation.get("nonce_commitment")
    code = validate_commitment_structure(stated)
    if code:
        return code
    if stated.get("scheme") == HUMAN_AUTHORITY_SCHEME:
        if confirmation.get("authority_protocol") != HUMAN_AUTHORITY_SCHEME:
            return 15
        if not confirmation.get("task_authority_id"):
            return 15
        return validate_commitment_structure(
            confirmation.get("task_nonce_commitment"), allowed_schemes={HUMAN_AUTHORITY_SCHEME}
        )
    return 0


def validate_model_readiness(
    data: dict[str, Any],
    repo_root: Path | None = None,
    *,
    synthetic_authority_context: bool = False,
    _validated_task_scope: bool = False,
) -> int:
    """Readiness of the single Current Model, in every activation mode.

    dormant means "the model is already adequate and no new load-bearing gap
    exists", never "no model was built" - so the model is required here too.
    """
    model = data.get("current_model")
    if not isinstance(model, dict):
        return 16
    # current_stage_model_complete AND proposed_method_or_solution AND
    # feasibility_support AND verification_or_acceptance_method AND explicit
    # current-Human confirmation of the exact model version -> substantive
    # execution allowed. All five are required together.
    code = validate_common_model_completeness(model)
    if code:
        return code
    if not _validated_task_scope:
        code = validate_mandatory_Human_confirmation(model)
        if code:
            return code
        code = validate_human_authority(
            model, data, repo_root,
            synthetic_authority_context=synthetic_authority_context,
        )
        if code:
            return code

    open_items = model.get("open_load_bearing_items") or []
    for item in open_items:
        if not isinstance(item, dict):
            return 11
        disposition = item.get("disposition")
        if disposition not in RESOLVED_DISPOSITIONS:
            # an unresolved blocking load-bearing question is not readiness
            return 16
        if disposition != "resolved":
            continue
        basis = item.get("Human_basis")
        if item.get("load_bearing") and not basis:
            return 15
        if isinstance(basis, dict):
            # silence, non-response or inferred consent never becomes a decision
            if basis.get("kind") in NON_DISPOSITION_BASIS_KINDS:
                return 14
            if basis.get("stale") is True:
                return 12

    # ordinary local reversible choices stay model-owned; demanding Human sign-off
    # on them is the micro-approval escalation the mechanism forbids
    for choice in model.get("ordinary_local_choices") or []:
        if isinstance(choice, dict) and choice.get("requires_Human_confirmation") is True:
            return 14

    # never re-ask something the Human already resolved
    for inquiry in data.get("inquiry_items") or []:
        if isinstance(inquiry, dict) and inquiry.get("re_asks_resolved_input") is True:
            return 14

    # Absence of a load-bearing gap must not force *additional* inquiry rounds.
    # It never waives the mandatory projection and confirmation checked above.
    if not open_items and data.get("additional_inquiry_required") is True:
        return 16
    # round counts must not be reintroduced as a readiness basis by any caller
    if data.get("readiness_basis") == "substantive_round_count":
        return 16

    alignment = model.get("Human_alignment")
    if isinstance(alignment, dict):
        if alignment.get("stale") is True:
            return 12
        bound = alignment.get("bound_model_version")
        if bound and bound != model.get("current_exact_model_version"):
            return 12

    completion = model.get("completion")
    if isinstance(completion, dict):
        bound_output = completion.get("bound_output_version")
        if bound_output and bound_output != model.get("current_exact_output_version"):
            return 12
        if completion.get("progression_requested") is True:
            if completion.get("actual_result") is None:
                return 14
            if not completion.get("verification_result"):
                return 14
    return 0


def validate_base_stage_receipt(receipt: Any) -> int:
    """The complete base stage-receipt validation, as an actually callable unit.

    This is the real base validation that a seven-stage-loop child must compose
    with. It is deliberately a function rather than a flag so that no caller can
    assert its result without running it.
    """
    if not isinstance(receipt, dict):
        return 17
    if any(k not in receipt for k in REQUIRED_RECEIPT_FIELDS):
        return 17
    exit_code = receipt.get("validator_mode_and_exit_code")
    if not isinstance(exit_code, dict) or exit_code.get("exit_code") != 0:
        return 17
    gates = receipt.get("gate_results")
    if not isinstance(gates, dict) or set(gates) != {"start", "completion"}:
        return 17
    if any(gates.get(gate) != "pass" for gate in ("start", "completion")):
        return 17
    if receipt.get("missing_partial_or_stale_paths"):
        return 12
    if not receipt.get("exact_candidate_version"):
        return 17
    return 0


def validate_stage_child_composition(
    data: dict[str, Any], receipt: dict[str, Any], repo_root: Path | None = None
) -> int:
    """CR-005: a seven-stage-loop child runs the complete base stage-receipt
    validation, takes its real exit code, and only when that is 0 overlays the
    Human alignment validation and the stage/profile binding validation.

    A self-reported field such as base_receipt_validation: complete is not
    evidence that the base validation ran, so no such field is consulted.
    """
    if data.get("seven_stage_child") is not True:
        return 0
    base_code = validate_base_stage_receipt(receipt)
    if base_code:
        return base_code

    # overlay 1: Human alignment must be bound to the exact current model version
    model = data.get("current_model") or {}
    binding = receipt.get("alignment_binding")
    if not isinstance(binding, dict):
        return 17
    if binding.get("bound_model_version") != model.get("current_exact_model_version"):
        return 12
    confirmation = model.get("Human_confirmation") or {}
    # Both sides must exist before they are compared. Comparing two absent
    # references succeeds as None == None, which let a child with no Human
    # confirmation at all satisfy the alignment overlay.
    binding_ref = binding.get("Human_confirmation_durable_ref")
    binding_blob = binding.get("Human_confirmation_durable_blob_sha")
    confirmation_ref = confirmation.get("durable_disposition_ref")
    confirmation_blob = confirmation.get("durable_disposition_blob_sha")
    if not binding_ref or not binding_blob:
        return 17
    if not confirmation_ref or not confirmation_blob:
        return 17
    if binding_ref != confirmation_ref or binding_blob != confirmation_blob:
        return 17
    binding_digest = (binding.get("nonce_commitment") or {}).get("digest")
    confirmation_digest = (confirmation.get("nonce_commitment") or {}).get("digest")
    if not binding_digest or not confirmation_digest:
        return 17
    if binding_digest != confirmation_digest:
        return 13

    # overlay 2: the stage/profile binding must resolve to the same exact profile
    profile_binding = receipt.get("profile_binding")
    if not isinstance(profile_binding, dict):
        return 17
    reference = receipt.get("profile_id_and_version")
    if profile_binding.get("profile_id_and_version") != reference:
        return 16
    try:
        profile = resolve_profile(reference, repo_root)
    except Exception:
        return 11
    if profile is None:
        return 16
    if profile_binding.get("mechanism_ref") != profile.get("mechanism_ref"):
        return 13
    return 0


def validate_completion_pointer(data: dict[str, Any]) -> int:
    """RR2-001: after a material candidate change the completion pointer must be
    append-only and bind the exact final semantic candidate, not a superseded one."""
    pointer = data.get("completion_pointer")
    if not isinstance(pointer, dict):
        return 0
    if pointer.get("append_only") is not True:
        return 14
    model = data.get("current_model") or {}
    expected = model.get("current_exact_output_version")
    if expected and pointer.get("bound_candidate_version") != expected:
        return 12
    if pointer.get("supersedes") and not pointer.get("supersedes_record_ref"):
        return 14
    return 0


def validate_instance(
    data: dict[str, Any],
    repo_root: Path | None = None,
    *,
    synthetic_authority_context: bool = False,
) -> int:
    """Production entry point.

    synthetic_authority_context is keyword-only, defaults to false, and is never
    derived from `data`. The CLI never passes it, so nothing reachable from a
    command line or from the instance under validation can turn it on.
    """
    code = direct_error_code(data)
    if code:
        return code
    mode = data.get("activation_mode")
    if mode not in {"dormant","full","incremental"}:
        return 11
    if mode == "dormant" and not data.get("dormant_reason"):
        return 16
    # Readiness, not round counts, decides whether the stage may progress. Fixed
    # minimum substantive rounds (full=5, incremental=2) were removed: how many
    # rounds occurred never proved that the model was adequate, and requiring
    # them manufactured discussion where no load-bearing gap existed.
    code = validate_model_readiness(
        data, repo_root,
        synthetic_authority_context=synthetic_authority_context,
    )
    if code:
        return code
    receipt = data.get("receipt")
    if not isinstance(receipt, dict):
        return 17
    if any(k not in receipt for k in REQUIRED_RECEIPT_FIELDS):
        return 17
    if receipt.get("validator_mode_and_exit_code", {}).get("exit_code") != 0:
        return 17
    # effective_current_stage_model = common fields + this exact profile's fields
    code = validate_effective_stage_model(data, data["current_model"], repo_root)
    if code:
        return code
    code = validate_stage_child_composition(data, receipt, repo_root)
    if code:
        return code
    return validate_completion_pointer(data)


# The old validate_instance API above remains for referenced historical callers.
# New CLI input uses this explicit task-scope path; no missing-field fallback.
class TaskScopeError(ValueError):
    def __init__(self, code: int, reason: str):
        super().__init__(reason)
        self.code = code


TASK_SCOPE_STAGES = {
    "workflow_stage_01_requirement_modeling", "workflow_stage_02_information_collection",
    "workflow_stage_03_result_modeling", "workflow_stage_04_test_generation",
    "workflow_stage_05_step_decomposition", "workflow_stage_06_execution",
    "workflow_stage_07_test_execution",
}


def task_scope_support():
    support = repo_root_from_here() / "01_os/06_execution/task_discipline"
    for directory in (support / "packet_input", support / "managed_verification"):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
    import managed_verify
    return managed_verify


def load_task_scope_doc(path: Path) -> Any:
    support = task_scope_support()
    raw = path.read_bytes()
    if path.suffix.lower() == ".json":
        return support.decode_json(raw)
    doc = support.load_yaml_text(raw.decode("utf-8"))
    support.same_json(doc, doc)  # reject YAML nonfinite/non-JSON scalar values too
    return doc


def _scope_require(condition: bool, code: int, reason: str) -> None:
    if not condition:
        raise TaskScopeError(code, reason)


def _scope_keys(value: Any, keys: set[str], name: str) -> None:
    _scope_require(isinstance(value, dict) and set(value) == keys, 11, name)


def _scope_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _scope_strings(value: Any, *, nonempty: bool = True) -> bool:
    return (isinstance(value, list) and (bool(value) or not nonempty)
            and all(_scope_string(item) for item in value)
            and len(set(value)) == len(value))


def _scope_path(value: Any, *, pattern: bool = False) -> bool:
    if not _scope_string(value) or "\\" in value or ":" in value:
        return False
    if pattern and value.endswith("/**"):
        value = value[:-3]
    parts = value.split("/")
    return (not any(part in {"", ".", ".."} or part.lower() == ".git"
                    or part.endswith((".", " "))
                    or re.fullmatch(r"(?i:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\..*)?", part)
                    for part in parts)
            and not any(ord(char) < 32 or char in '*?[]<>|"' for char in value))


def _scope_candidate_path(repo: Path, candidate: str, path: str, source: Any) -> None:
    """Planned paths may be absent, but existing prefixes cannot be links/files.

    This checks Git tree entries, not the safety of a future mutable filesystem.
    """
    parts = path.split("/")
    prefixes = ["/".join(parts[:index]) for index in range(1, len(parts) + 1)]
    # Mixing ancestor and descendant pathspecs makes ls-tree traverse the
    # ancestor and emit unrelated siblings. Query each exact prefix separately.
    for prefix in prefixes:
        raw = source.git(repo, "ls-tree", "-z", candidate, "--", prefix)
        entries = list(filter(None, raw.split(b"\0")))
        _scope_require(len(entries) <= 1, 13, "ambiguous_path_entry")
        for entry in entries:
            metadata, actual = entry.split(b"\t", 1)
            mode, kind, _oid = metadata.split()
            _scope_require(actual.decode("utf-8") == prefix, 13, "unexpected_path_entry")
            if prefix != path:
                _scope_require(mode == b"040000" and kind == b"tree", 15, "action_parent_not_directory")
            else:
                _scope_require((mode, kind) in {(b"040000", b"tree"), (b"100644", b"blob"),
                                               (b"100755", b"blob")}, 15, "action_link_or_gitlink")


def _scope_allowed(path: str, patterns: list[str]) -> bool:
    return any(path == pattern or (pattern.endswith("/**") and
               path.startswith(pattern[:-3] + "/")) for pattern in patterns)


def _scope_blob(repo: Path, candidate: str, ref: Any, source: Any) -> bytes:
    _scope_keys(ref, {"path", "blob_sha"}, "exact_source_reference_required")
    _scope_require(_scope_path(ref["path"]), 13, "invalid_source_path")
    raw = source.tracked_blob(repo, candidate, ref["path"])
    blob = hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()
    _scope_require(ref["blob_sha"] == blob, 13, "source_blob_mismatch")
    return raw


def _scope_profile(profile_doc: Any, stage_id: str, reference: Any) -> dict[str, Any]:
    _scope_require(isinstance(profile_doc, dict), 11, "profile_mapping_required")
    profiles = profile_doc.get("profiles")
    _scope_require(isinstance(profiles, list) and len(profiles) == 7, 16, "seven_profiles_required")
    identities = []
    for profile in profiles:
        _scope_require(isinstance(profile, dict), 11, "profile_mapping_required")
        _scope_require(_scope_string(profile.get("profile_id")), 16, "profile_id_required")
        _scope_require(type(profile.get("profile_version")) is int and profile["profile_version"] > 0,
                       16, "profile_version_required")
        _scope_require(_scope_strings(profile.get("required_model_fields")), 16,
                       "profile_required_fields_nonempty_unique")
        _scope_require(_scope_string(profile.get("mechanism_ref")), 16, "mechanism_ref_required")
        identities.append(profile["profile_id"])
    _scope_require(set(identities) == TASK_SCOPE_STAGES, 16, "unknown_or_duplicate_profiles")
    selected = [p for p in profiles if p["profile_id"] == stage_id]
    _scope_require(len(selected) == 1, 16, "unknown_stage")
    profile = selected[0]
    _scope_require(reference == f'{stage_id}@{profile["profile_version"]}', 16, "stage_profile_mismatch")
    return profile


def _scope_decision_basis(item: dict[str, Any], repo: Path, candidate: str,
                          scope: dict[str, Any], packet: dict[str, Any],
                          action: dict[str, Any], source: Any) -> None:
    decision = item.get("decision_id")
    basis = item.get("Human_basis")
    _scope_require(_scope_string(decision) and isinstance(basis, dict), 15, "decision_basis_required")
    _scope_require(basis.get("decision_id") == decision, 15, "decision_identity_mismatch")
    if basis.get("kind") == "current_task_scope":
        _scope_keys(basis, {"kind", "decision_id", "task_packet", "action_id"}, "task_scope_decision_schema")
        _scope_require(source.same_json(basis["task_packet"], scope["task_packet"])
                       and basis["action_id"] == action["action_id"]
                       and decision in action.get("covered_decision_ids", []), 15, "decision_not_covered")
    else:
        _scope_keys(basis, {"kind", "decision_id", "source_ref"}, "explicit_decision_schema")
        _scope_require(basis["kind"] == "explicit_statement", 15, "explicit_decision_required")
        expected = {"actor_class": "current_Human", "kind": "explicit_statement", "decision_id": decision,
                    "task_id": packet["task_id"], "action_id": action["action_id"],
                    "exact_base_sha": packet["exact_base_sha"], "target": action["target"],
                    "expected_target_head": action["expected_target_head"], "stage_ids": action["stage_ids"],
                    "paths": action["paths"], "stale": False, "revoked": False}
        recorded = source.load_yaml_text(_scope_blob(repo, candidate, basis["source_ref"], source).decode("utf-8"))
        _scope_require(source.same_json(recorded, expected), 15, "decision_source_mismatch")


def _scope_feasibility(model: dict[str, Any], scope: dict[str, Any],
                       contract: dict[str, Any]) -> None:
    """feasibility_support must carry a stage-allowed basis, not only a value.

    Of the eight substantively required dimensions this was the one with no
    support requirement of its own, so a confident sentence satisfied it.

    The contract arrives already loaded from the exact candidate blob by
    validate_task_scope_instance. Two earlier revisions of this check got the
    source wrong: the first read the filesystem, which would have let a mutable
    working-tree file decide what the candidate may claim; the second read the
    candidate correctly but did it here, adding a second candidate read inside a
    per-field check.
    """
    support = model.get("feasibility_support")
    _scope_require(isinstance(support, dict), 16, "feasibility_support_must_carry_a_basis")
    _scope_require(_scope_string(support.get("value")), 16, "feasibility_value_required")
    basis = support.get("basis")
    _scope_keys(basis, {"kind", "ref"}, "feasibility_basis_schema")
    _scope_require(_scope_string(basis.get("ref")), 16, "feasibility_basis_ref_required")
    table = contract.get("common_task_stage_model", {}).get("feasibility_basis_contract")
    _scope_require(isinstance(table, dict), 11, "feasibility_basis_contract_missing")
    allowed = table.get("basis_kinds_by_stage", {}).get(scope["stage_id"])
    _scope_require(isinstance(allowed, list) and bool(allowed), 11,
                   "feasibility_basis_kinds_missing_for_stage")
    kind = basis.get("kind")
    _scope_require(kind not in set(table.get("prohibited_basis_kinds", ())), 16,
                   "feasibility_basis_kind_prohibited")
    _scope_require(kind in allowed, 16, "feasibility_basis_kind_not_allowed_for_stage")


def _scope_completion(model: dict[str, Any], repo: Path, candidate: str,
                       scope: dict[str, Any], source: Any) -> None:
    completion = model.get("completion", {})
    if "current_exact_output_version" in model:
        _scope_require(model["current_exact_output_version"] == candidate, 12, "output_candidate_mismatch")
    if "progression_requested" in completion:
        _scope_require(type(completion["progression_requested"]) is bool, 11, "typed_progression_flag")
    if "bound_output_version" in completion:
        _scope_require(completion["bound_output_version"] == candidate, 12, "completion_candidate_mismatch")
    if completion.get("progression_requested") is True:
        _scope_require(model.get("current_exact_output_version") == candidate
                       and completion.get("bound_output_version") == candidate, 12, "completion_binding_required")
        _scope_require(_scope_string(completion.get("actual_result")), 14, "actual_result_required")
        _scope_require("verification_result" in completion, 14, "verification_result_required")
        # Binding an output version and a verification record proves what was
        # produced and that some record says it verified. It does not say whether
        # the result matched the plan it was authorised against, what moved, what
        # risk is left, or what the next stage inherits. none_material is a real
        # answer for each; absent and null are not.
        for field in CLOSURE_FIELDS:
            _scope_require(field in completion, 14, "closure_field_required:" + field)
            value = completion[field]
            _scope_require(_scope_string(value) or isinstance(value, (dict, list)) and bool(value),
                           14, "closure_field_empty:" + field)
    if "verification_result" in completion:
        ref = completion["verification_result"]
        _scope_keys(ref, {"commit", "path", "blob_sha"}, "verification_reference_required")
        source.candidate_id(repo, ref["commit"])
        # A later independent evidence commit avoids embedding a commit's own SHA.
        raw = _scope_blob(repo, ref["commit"], {key: ref[key] for key in ("path", "blob_sha")}, source)
        recorded = source.load_yaml_text(raw.decode("utf-8"))
        expected = {"schema_version": "stage_verification_result.v1", "candidate": candidate,
                    "task_id": scope["task_id"], "stage_id": scope["stage_id"], "status": "verified"}
        _scope_require(source.same_json(recorded, expected), 14, "verification_source_mismatch")


def _scope_model(data: dict[str, Any], candidate: str, scope: dict[str, Any],
                 profile: dict[str, Any], repo: Path, packet: dict[str, Any],
                 action: dict[str, Any], source: Any, contract: dict[str, Any]) -> None:
    model = data.get("current_model")
    _scope_require(isinstance(model, dict), 16, "current_model_required")
    _scope_require("Human_confirmation" not in model, 11, "mixed_legacy_confirmation")
    for field in SUBSTANTIVE_COMMON_FIELDS + NULLABLE_COMMON_FIELDS:
        value = model.get(field)
        _scope_require((_scope_string(value) or isinstance(value, (dict, list)) and bool(value)),
                       16, "common_model_field_required:" + field)
    _scope_require(model.get("task_id") == scope["task_id"] and model.get("stage_id") == scope["stage_id"],
                   13, "model_task_stage_mismatch")
    _scope_require(model["current_exact_model_version"] == candidate, 12, "model_candidate_mismatch")
    for owner, field in ((model, "open_load_bearing_items"), (model, "ordinary_local_choices"),
                         (data, "inquiry_items")):
        if field not in owner and field != "open_load_bearing_items":
            continue
        items = owner.get(field)
        _scope_require(isinstance(items, list) and all(isinstance(item, dict) for item in items),
                       11, "typed_list_required:" + field)
        for item in items:
            for flag in ("load_bearing", "requires_Human_confirmation", "re_asks_resolved_input"):
                if flag in item:
                    _scope_require(type(item[flag]) is bool, 11, "boolean_required:" + flag)
            if field == "open_load_bearing_items":
                _scope_require(type(item.get("load_bearing")) is bool, 11, "load_bearing_required")
                if item.get("disposition") == "deferred_non_blocking":
                    _scope_require(item["load_bearing"] is False and _scope_string(item.get("revisit_trigger")),
                                   16, "load_bearing_item_cannot_be_deferred")
                if item["load_bearing"]:
                    _scope_decision_basis(item, repo, candidate, scope, packet, action, source)
    for field in ("Human_alignment", "completion"):
        if field in model:
            _scope_require(isinstance(model[field], dict), 11, "mapping_required:" + field)
    if "additional_inquiry_required" in data:
        _scope_require(type(data["additional_inquiry_required"]) is bool, 11, "typed_inquiry_flag")
    _scope_feasibility(model, scope, contract)
    _scope_completion(model, repo, candidate, scope, source)
    code = validate_model_readiness(data, _validated_task_scope=True)
    _scope_require(code == 0, code, "substantive_readiness_failed")
    elements = model.get("stage_specific_model_elements")
    _scope_require(isinstance(elements, dict), 16, "stage_elements_required")
    for field in profile["required_model_fields"]:
        element = elements.get(field)
        _scope_require(isinstance(element, dict), 16, "stage_field_missing:" + field)
        disposition = element.get("disposition")
        _scope_require(disposition in ALLOWED_ELEMENT_DISPOSITIONS, 16, "stage_disposition_invalid")
        if disposition == REPRESENTED:
            value = element.get("value")
            _scope_require(_scope_string(value) or isinstance(value, (list, dict)) and bool(value),
                           16, "stage_value_required")
        elif disposition == EXPLICITLY_IRRELEVANT:
            _scope_require(_scope_string(element.get("reason_and_scope")), 16, "irrelevance_scope_required")
        else:
            for flag in ("load_bearing", "Human_decision_boundary"):
                if flag in element:
                    _scope_require(type(element[flag]) is bool, 11, "typed_unknown_flag")
            _scope_require(_scope_string(element.get("reason_and_scope"))
                           and _scope_string(element.get("revisit_trigger")), 16, "unknown_scope_required")
            if element.get("load_bearing") is True or element.get("Human_decision_boundary") is True:
                _scope_decision_basis(element, repo, candidate, scope, packet, action, source)
            code = validate_deferred_unknown(element, _validated_task_scope=True)
            _scope_require(code == 0, code, "unknown_not_disposed")


def _scope_receipt(data: dict[str, Any], scope: dict[str, Any], profile: dict[str, Any]) -> None:
    receipt = data.get("receipt")
    _scope_require(isinstance(receipt, dict), 17, "receipt_required")
    result = receipt.get("validator_mode_and_exit_code")
    _scope_require(isinstance(result, dict) and type(result.get("exit_code")) is int
                   and result.get("exit_code") == 0 and result.get("mode") == "instance",
                   17, "receipt_validator_result_invalid")
    for field in ("loaded_paths", "missing_partial_or_stale_paths", "open_detail_divergence_event_refs",
                  "deferred_detail_record_refs"):
        _scope_require(_scope_strings(receipt.get(field), nonempty=False), 17, "receipt_list_required:" + field)
    for field in ("mechanism_version", "active_contract_version", "boot_manifest_version", "registry_version",
                  "loader_version"):
        _scope_require(type(receipt.get(field)) is int and receipt[field] > 0, 17, "receipt_version_invalid")
    for field in ("receipt_schema_version", "trigger_evaluation_result_ref", "activation_mode_or_dormant_reason",
                  "detail_granularity_evaluation_result", "created_by_actor_ref", "created_at"):
        _scope_require(_scope_string(receipt.get(field)), 17, "receipt_field_required:" + field)
    _scope_require(_scope_strings(receipt.get("main_mechanism_ref")), 17, "receipt_mechanism_required")
    code = validate_base_stage_receipt(receipt)
    _scope_require(code == 0, code, "base_receipt_failed")
    _scope_require(receipt["exact_candidate_version"] == scope["candidate"], 12, "receipt_candidate_mismatch")
    if "seven_stage_child" in data:
        _scope_require(type(data["seven_stage_child"]) is bool, 11, "typed_child_flag")
    if data.get("seven_stage_child") is True:
        binding = receipt.get("alignment_binding")
        expected = {"bound_model_version": scope["candidate"], "task_id": scope["task_id"],
                    "action_id": scope["action_id"], "task_packet": scope["task_packet"]}
        _scope_require(binding == expected, 17, "child_scope_alignment_mismatch")
        expected_profile = {"profile_id_and_version": receipt["profile_id_and_version"],
                            "mechanism_ref": profile["mechanism_ref"]}
        _scope_require(receipt.get("profile_binding") == expected_profile, 17, "child_profile_mismatch")
    if "completion_pointer" in data:
        pointer = data["completion_pointer"]
        _scope_require(isinstance(pointer, dict), 11, "pointer_mapping_required")
        _scope_require(set(pointer) <= {"append_only", "bound_candidate_version", "supersedes", "supersedes_record_ref"},
                       11, "pointer_unknown_fields")
        _scope_require(pointer.get("bound_candidate_version") == scope["candidate"], 12, "pointer_candidate_mismatch")
        if "supersedes" in pointer or "supersedes_record_ref" in pointer:
            _scope_require(_scope_string(pointer.get("supersedes"))
                           and _scope_string(pointer.get("supersedes_record_ref")), 14, "supersession_pair_required")
    code = validate_completion_pointer(data)
    _scope_require(code == 0, code, "completion_pointer_failed")


def validate_task_scope_instance(data: Any, repo_root: Path | None, candidate: str | None) -> int:
    """Validate declared stage/action readiness, not execute or authenticate it.

    Scope sources are exact candidate blobs; completion evidence has its own commit.
    A same-writer confirmation record does not
    authenticate the Human; neither a declared action nor this result controls an
    arbitrary future command, independent acceptance, publication or activation.
    """
    source = task_scope_support()
    try:
        _scope_require(isinstance(data, dict) and repo_root is not None, 11, "explicit_repository_required")
        source.same_json(data, data)
        allowed_fields = {"task_scope", "activation_mode", "dormant_reason", "additional_inquiry_required",
                          "current_model", "receipt", "seven_stage_child", "completion_pointer", "inquiry_items",
                          "readiness_basis", "stage_profile_id_and_version"}
        _scope_require(set(data) <= allowed_fields, 11, "unknown_instance_fields")
        repo = repo_root.resolve()
        _scope_require(Path(source.git(repo, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve() == repo,
                       13, "repository_root_required")
        source.candidate_id(repo, candidate)
        scope = data.get("task_scope")
        _scope_keys(scope, {"schema_version", "task_id", "candidate", "task_packet", "action_id", "stage_id", "paths"},
                    "task_scope_schema")
        _scope_require(type(scope["schema_version"]) is int and scope["schema_version"] == 1, 11, "task_scope_version")
        _scope_require(scope["candidate"] == candidate, 12, "expected_candidate_mismatch")
        for field in ("task_id", "action_id", "stage_id"):
            _scope_require(_scope_string(scope[field]), 11, "scope_identity_required")
        _scope_require(_scope_strings(scope["paths"]) and all(_scope_path(p) for p in scope["paths"]),
                       11, "scope_paths_invalid")
        raw = _scope_blob(repo, candidate, scope["task_packet"], source)
        normalized = source.normalize_packet(source.load_yaml_text(raw.decode("utf-8")))
        _scope_require(normalized.source_format == "wrapped_v1", 11, "canonical_wrapped_packet_required")
        packet = normalized.body
        _scope_require(packet["task_id"] == scope["task_id"], 13, "packet_task_mismatch")
        source.candidate_id(repo, packet["exact_base_sha"])
        source.git(repo, "merge-base", "--is-ancestor", packet["exact_base_sha"], candidate)
        allowed = packet["allowed_changed_paths"]
        _scope_require(all(_scope_path(p, pattern=True) for p in allowed), 11, "packet_allowlist_invalid")
        changed = source.git(repo, "diff", "--name-only", "--no-renames", "-z", packet["exact_base_sha"], candidate).decode("utf-8").split("\0")
        _scope_require(all(_scope_path(p) and _scope_allowed(p, allowed) for p in changed if p), 15, "candidate_outside_allowlist")
        actions = packet.get("stage_actions")
        _scope_require(isinstance(actions, list) and bool(actions), 11, "stage_actions_required")
        policy_raw = source.tracked_blob(repo, candidate, "01_os/05_registry/repository_publisher_authority_v1.yml")
        policy = source.load_yaml_text(policy_raw.decode("utf-8"))
        _scope_require(isinstance(policy, dict) and isinstance(policy.get("confirmation_bound_actions"), dict),
                       11, "publisher_policy_required")
        protected = set(policy["confirmation_bound_actions"])
        known = {"publish_or_merge_to_master", "force_push", "rewrite_published_history", "delete_master_or_repository",
                 "change_repository_visibility_or_credentials", "activate_runtime_scheduler_or_coordinator",
                 "access_secrets_credentials_or_key_material"}
        _scope_require(protected == known and policy.get("core_history_rewrite") == "prohibited_regardless_of_confirmation",
                       15, "unrecognized_protected_policy")
        ids = []
        for action in actions:
            required_action = {"action_id", "kind", "target", "expected_target_head", "stage_ids", "paths", "confirmation"}
            _scope_require(isinstance(action, dict) and required_action <= set(action)
                           and set(action) <= required_action | {"covered_decision_ids"}, 11, "stage_action_schema")
            if "covered_decision_ids" in action:
                _scope_require(_scope_strings(action["covered_decision_ids"], nonempty=False), 11, "decision_coverage_list_required")
            _scope_require(_scope_string(action["action_id"]) and _scope_string(action["target"]), 11, "action_identity_required")
            _scope_require(_scope_string(action["kind"]) and action["kind"] in known | {"ordinary_task_work"}, 15, "action_kind_unknown")
            head = action["expected_target_head"]
            _scope_require(head is None or isinstance(head, str) and re.fullmatch(r"[0-9a-f]{40}", head) is not None,
                           11, "expected_target_head_invalid")
            if action["kind"] in {"publish_or_merge_to_master", "force_push", "delete_master_or_repository"}:
                _scope_require(head is not None, 15, "expected_target_head_required")
            _scope_require(_scope_strings(action["stage_ids"]) and _scope_strings(action["paths"]), 11, "action_lists_required")
            _scope_require(set(action["stage_ids"]) <= TASK_SCOPE_STAGES, 16, "unknown_action_stage")
            _scope_require(all(_scope_path(p) and _scope_allowed(p, allowed) for p in action["paths"]), 15, "action_outside_scope")
            for path in action["paths"]:
                _scope_candidate_path(repo, candidate, path, source)
            ids.append(action["action_id"])
        _scope_require(len(set(ids)) == len(ids), 11, "duplicate_action_ids")
        selected = [a for a in actions if a["action_id"] == scope["action_id"]]
        _scope_require(len(selected) == 1, 15, "planned_action_missing")
        action = selected[0]
        _scope_require(scope["stage_id"] in action["stage_ids"] and scope["paths"] == action["paths"], 15, "action_scope_mismatch")
        _scope_require(action["kind"] not in packet["prohibitions"] and action["action_id"] not in packet["prohibitions"],
                       15, "packet_action_prohibited")
        if action["kind"] == "ordinary_task_work":
            branch = packet["branch"]
            _scope_require(branch != "master" and not branch.startswith("refs/") and _scope_path(branch), 15, "nonmaster_task_branch_required")
            _scope_require(action["target"] == "refs/heads/" + branch and action["confirmation"] is None
                           and action["expected_target_head"] is None,
                           15, "ordinary_target_or_confirmation_invalid")
        else:
            _scope_require(action["kind"] != "rewrite_published_history", 15, "core_history_rewrite_prohibited")
            if action["kind"] == "force_push":
                source.candidate_id(repo, action["expected_target_head"])
                source.git(repo, "merge-base", "--is-ancestor", action["expected_target_head"], candidate)
            confirmation = action["confirmation"]
            keys = {"actor_class", "kind", "source_ref", "task_id", "action_id", "exact_base_sha", "target", "expected_target_head",
                    "stage_ids", "paths", "stale", "revoked"}
            _scope_keys(confirmation, keys, "simple_confirmation_required")
            _scope_require(confirmation["actor_class"] == "current_Human" and confirmation["kind"] == "explicit_statement"
                           and confirmation["stale"] is False and confirmation["revoked"] is False, 15, "confirmation_not_current")
            for field, expected in {"task_id": packet["task_id"], "action_id": action["action_id"], "exact_base_sha": packet["exact_base_sha"],
                                    "target": action["target"], "expected_target_head": action["expected_target_head"],
                                    "stage_ids": action["stage_ids"], "paths": action["paths"]}.items():
                _scope_require(confirmation[field] == expected, 15, "confirmation_scope_mismatch:" + field)
            recorded = source.load_yaml_text(_scope_blob(repo, candidate, confirmation["source_ref"], source).decode("utf-8"))
            expected = {k: v for k, v in confirmation.items() if k != "source_ref"}
            _scope_require(source.same_json(recorded, expected), 15, "confirmation_source_mismatch")
        _scope_require(_scope_string(data.get("activation_mode")) and data["activation_mode"] in {"dormant", "full", "incremental"}, 11, "activation_mode_invalid")
        if data["activation_mode"] == "dormant":
            _scope_require(_scope_string(data.get("dormant_reason")), 16, "dormant_reason_required")
        for field in ("ordinary", "authorization_mode", "authority_route", "synthetic_authority_context"):
            _scope_require(field not in data, 11, "route_override_prohibited")
        code = direct_error_code(data)
        _scope_require(code == 0, code, "declared_failure")
        receipt = data.get("receipt")
        _scope_require(isinstance(receipt, dict), 17, "receipt_required")
        profile_doc = source.load_yaml_text(source.tracked_blob(repo, candidate, PROFILE_SET_PATH).decode("utf-8"))
        profile = _scope_profile(profile_doc, scope["stage_id"], receipt.get("profile_id_and_version"))
        # Canonical sources are loaded here, once, from the exact candidate, next
        # to the profile set. Loading the contract deeper in the call graph put a
        # second candidate read inside a per-field check and made it easy for a
        # future check to add a third. Never fall back to a worktree read: a
        # mutable file must not decide what the candidate is allowed to claim.
        contract = source.load_yaml_text(source.tracked_blob(repo, candidate, PROFILE_CONTRACT_PATH).decode("utf-8"))
        _scope_require(isinstance(contract, dict), 11, "profile_contract_mapping_required")
        if "stage_profile_id_and_version" in data:
            _scope_require(data["stage_profile_id_and_version"] == receipt["profile_id_and_version"], 16, "declared_profile_mismatch")
        _scope_model(data, candidate, scope, profile, repo, packet, action, source, contract)
        _scope_receipt(data, scope, profile)
        return 0
    except TaskScopeError as exc:
        return exc.code
    except (ValueError, UnicodeError, TypeError, KeyError, RecursionError):
        return 11
    except (source.VerificationError, OSError):
        return 13

def validate_material_event(data: dict[str, Any]) -> int:
    code = direct_error_code(data)
    if code:
        return code
    for key in ("event_id","exact_source_ref","dependency_graph_version","impact"):
        if key not in data:
            return 10
    impact = data["impact"]
    for key in ("affected","unaffected","unknown"):
        if key not in impact:
            return 11
    if impact["unknown"] and not data.get("unknown_scope_blocked"):
        return 13
    if not data.get("successor_or_reconfirmation_recorded"):
        return 14
    return 0

def validate_review_execution(data: dict[str, Any]) -> int:
    code = direct_error_code(data)
    if code:
        return code
    required = ("task_ref","branch","base","head","allowlist","Human_authorization_ref",
                "executor","independent_reviewer","verification")
    if any(k not in data for k in required):
        return 10
    if data["executor"] == data["independent_reviewer"]:
        return 18
    changed = set(data.get("changed_paths", []))
    allowed = set(data.get("allowlist", []))
    if changed - allowed:
        return 18
    if not data.get("Human_authorization_ref"):
        return 15
    verification = data["verification"]
    if data.get("implementation_complete") and verification.get("status") != "verified":
        return 18
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("static","instance","legacy_instance","material_event","review_execution"))
    parser.add_argument("target")
    parser.add_argument("--case-id")
    parser.add_argument("--json-output", action="store_true")
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--candidate")
    args = parser.parse_args()
    try:
        target = Path(args.target)
        if args.mode == "static" and target.is_dir():
            code = validate_static_repo(target)
        else:
            loader = load_task_scope_doc if args.mode == "instance" else load_doc
            data = select_case(loader(target), args.case_id)
            if not isinstance(data, dict):
                code = 11
            else:
                payload = data.get("data", data)
                if args.mode == "static":
                    code = validate_static_fixture(payload)
                elif args.mode == "instance":
                    code = validate_task_scope_instance(payload, args.repo_root, args.candidate)
                elif args.mode == "legacy_instance":
                    code = validate_instance(payload, args.repo_root)
                elif args.mode == "material_event":
                    code = validate_material_event(payload)
                else:
                    code = validate_review_execution(payload)
        if args.json_output:
            print(json.dumps({"mode": args.mode, "target": args.target, "case_id": args.case_id, "exit_code": code}))
        return code
    except Exception as exc:
        if args.json_output:
            print(json.dumps({"mode": args.mode, "target": args.target, "case_id": args.case_id, "exit_code": 19, "error": str(exc)}))
        return 19

if __name__ == "__main__":
    sys.exit(main())

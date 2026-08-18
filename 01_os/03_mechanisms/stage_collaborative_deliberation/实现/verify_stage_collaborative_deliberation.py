#!/usr/bin/env python3
"""Deterministic validator for the staged stage-collaborative-deliberation mechanism."""
from __future__ import annotations
import argparse, hashlib, hmac, json, sys
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


def validate_deferred_unknown(element: dict[str, Any]) -> int:
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

    if element.get("load_bearing") is True or element.get("Human_decision_boundary") is True:
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
# Human authority: durable disposition + one-time Human-generated nonce
#
# actor_class: current_Human written into a repository object is a claim the
# object makes about itself. It cannot be the thing that grants authority, or
# any model able to write the object can manufacture Human authority. Authority
# comes from a foreground/current-Human interaction that produced an explicit
# disposition, recorded durably, bound to one exact decision, and committed to
# with a nonce the Human generated independently.
#
# Only the commitment is stored. The plaintext nonce never enters Git, a run
# artifact, a communication document, a fixture, a log or a command line.
# ---------------------------------------------------------------------------
HUMAN_AUTHORITY_SCHEME = "citystate-human-authority-v1"
HUMAN_AUTHORITY_ALGORITHM = "sha256"
COMMITMENT_BOUND_FIELDS = (
    "task_id",
    "stage_id",
    "decision_id",
    "decision_type",
    "exact_model_version",
    "Human_disposition",
    "authorized_scope",
)
# authority follows the decision, not the activity: one nonce per authority
# event, and an authorization nonce never doubles as a completion nonce.
AUTHORIZATION_DECISION_TYPE = "substantive_execution_authorization"
COMPLETION_DECISION_TYPE = "completion_acceptance"
DECISION_TYPES = {AUTHORIZATION_DECISION_TYPE, COMPLETION_DECISION_TYPE}
AFFIRMATIVE_DISPOSITIONS = {"confirmed", "accepted", "authorized"}


def canonical_commitment_payload(bound: dict[str, Any], human_nonce: str) -> bytes:
    """Deterministic serialization for the commitment.

    Canonical JSON - UTF-8, sorted keys, fixed separators - rather than string
    concatenation, so no field boundary is ambiguous and no value can be shifted
    between fields to produce the same bytes.
    """
    payload = {"domain": HUMAN_AUTHORITY_SCHEME, "Human_nonce": human_nonce}
    for field in COMMITMENT_BOUND_FIELDS:
        payload[field] = bound.get(field)
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def compute_commitment(bound: dict[str, Any], human_nonce: str) -> str:
    return hashlib.sha256(canonical_commitment_payload(bound, human_nonce)).hexdigest()


def validate_commitment_structure(commitment: Any) -> int:
    if not isinstance(commitment, dict):
        return 15
    if commitment.get("scheme") != HUMAN_AUTHORITY_SCHEME:
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
    # the plaintext must never be persisted alongside its own commitment
    for forbidden in ("Human_nonce", "nonce", "plaintext", "code"):
        if forbidden in commitment:
            return 14
    return 0


def resolve_durable_disposition(
    confirmation: dict[str, Any], repo_root: Path | None
) -> tuple[int, dict[str, Any] | None]:
    """Actually read the durable Human disposition record.

    A reference that is absent, does not resolve, or whose blob does not match
    the recorded sha is not evidence of anything.
    """
    ref = confirmation.get("durable_disposition_ref")
    expected_blob = confirmation.get("durable_disposition_blob_sha")
    if not ref or not isinstance(ref, str):
        return 15, None
    if not expected_blob or not isinstance(expected_blob, str):
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


def validate_durable_disposition_record(
    record: dict[str, Any],
    confirmation: dict[str, Any],
    model: dict[str, Any],
    *,
    synthetic_authority_context: bool = False,
) -> int:
    """The record must bind this exact decision, and still be live.

    A record marked synthetic_test_record: true is never Human authority on the
    production path. The marker is checked first, before any other field, so a
    synthetic record that is otherwise perfectly formed - right task, stage,
    decision, model version, blob and commitment - still cannot authorize
    progression. Path naming and comments are not the control; the semantic
    marker in the record is.

    synthetic_authority_context is keyword-only and defaults to false. It is
    supplied by a test harness that constructed the fixture, never read from the
    instance under validation, so no production input - test_mode,
    allow_synthetic or anything else it writes about itself - can reach it.
    """
    if record.get(SYNTHETIC_MARKER) is True and not synthetic_authority_context:
        return 15
    if record.get("provenance") != "foreground_current_Human_interaction":
        return 15
    if record.get("actor_class") != "current_Human":
        return 15
    if record.get("explicit") is not True:
        return 14
    disposition = record.get("Human_disposition")
    if disposition not in AFFIRMATIVE_DISPOSITIONS:
        return 15
    if record.get("stale") is True or record.get("invalidated") is True:
        return 12
    if record.get("consumed_by") not in (None, record.get("decision_id")):
        # this nonce already carried a different authority event
        return 12

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

    code = validate_commitment_structure(record.get("nonce_commitment"))
    if code:
        return code
    stated = confirmation.get("nonce_commitment")
    code = validate_commitment_structure(stated)
    if code:
        return code
    if stated.get("digest") != record["nonce_commitment"].get("digest"):
        return 13
    return 0


def validate_human_authority(
    model: dict[str, Any],
    data: dict[str, Any],
    repo_root: Path | None = None,
    *,
    synthetic_authority_context: bool = False,
) -> int:
    """Full chain: interaction -> disposition -> nonce -> record -> binding.

    synthetic_authority_context comes from the caller, never from `data`. The
    instance being validated cannot enable it by writing test_mode or
    allow_synthetic about itself.
    """
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
    if stage_id is not None and record.get("stage_id") != stage_id:
        return 15
    return validate_durable_disposition_record(
        record, confirmation, model,
        synthetic_authority_context=synthetic_authority_context,
    )


def verify_human_challenge(
    record: dict[str, Any], human_nonce: str
) -> tuple[bool, str, str]:
    """Recompute the commitment from the record's bound fields and a nonce the
    current Human supplies in the current interaction.

    The nonce must come from the Human now. A plaintext code taken from executor
    output, the repository, a run artifact, a communication document or another
    model's report proves nothing here: any of those sources could have produced
    the record in the first place.
    """
    bound = {field: record.get(field) for field in COMMITMENT_BOUND_FIELDS}
    recomputed = compute_commitment(bound, human_nonce)
    stored = (record.get("nonce_commitment") or {}).get("digest", "")
    return hmac.compare_digest(recomputed, stored), recomputed, stored


def validate_mandatory_Human_confirmation(model: dict[str, Any]) -> int:
    """Every task and every workflow stage must project the current model to the
    current Human and obtain an explicit confirmation bound to the exact current
    model version before any substantive execution.

    This is mandatory even when no load-bearing gap exists - in that case the
    required form is one concise proposal and one explicit confirmation, not a
    fixed number of rounds, a long form, or per-choice micro-approval.

    None of the following ever substitutes for the current stage's confirmation:
    Human silence or non-response, inferred consent, a previous stage's
    confirmation, a confirmation bound to an older model version, or a
    confirmation produced by an executor, reviewer or any other non-Human actor.
    """
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
    # An inline actor_class is a self-assertion. Authority requires a durable
    # disposition reference and a nonce commitment, both checked for real below.
    if not confirmation.get("durable_disposition_ref"):
        return 15
    if not confirmation.get("durable_disposition_blob_sha"):
        return 15
    if not confirmation.get("decision_id"):
        return 15
    return validate_commitment_structure(confirmation.get("nonce_commitment"))


def validate_model_readiness(
    data: dict[str, Any],
    repo_root: Path | None = None,
    *,
    synthetic_authority_context: bool = False,
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
    code = validate_mandatory_Human_confirmation(model)
    if code:
        return code
    # resolve and validate the durable disposition itself; a self-asserted
    # actor_class never reaches this far on its own
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
    parser.add_argument("mode", choices=("static","instance","material_event","review_execution"))
    parser.add_argument("target")
    parser.add_argument("--case-id")
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args()
    try:
        target = Path(args.target)
        if args.mode == "static" and target.is_dir():
            code = validate_static_repo(target)
        else:
            data = select_case(load_doc(target), args.case_id)
            if not isinstance(data, dict):
                code = 11
            else:
                payload = data.get("data", data)
                if args.mode == "static":
                    code = validate_static_fixture(payload)
                elif args.mode == "instance":
                    code = validate_instance(payload)
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

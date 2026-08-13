#!/usr/bin/env python3
"""Pure formal-action resolution, enforcement, and material-claim comparison."""
from __future__ import annotations

import fnmatch
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any


FORMAL_MESSAGE_ACTIONS = {
    "request": "formal_cross_endpoint_task_dispatch",
    "response": "formal_cross_endpoint_response",
    "result": "formal_cross_endpoint_result",
    "correction": "formal_cross_endpoint_correction",
    "blocked": "formal_cross_endpoint_blocked_state",
    "decision_required": "formal_cross_endpoint_decision_handoff",
}

VERIFICATION_RESULTS = {"VERIFIED", "MISMATCH", "STALE", "UNVERIFIABLE", "AMBIGUOUS"}
AUTHENTICATED_PRINCIPAL_SOURCES = {
    "trusted_host_injected_principal",
    "connector_authenticated_principal",
    "local_authenticated_principal",
}
ACCEPTED_OBSERVATION_SOURCES = {
    "actual_Git_object_database",
    "fresh_remote_Git_ref_readback",
    "complete_Git_compare",
    "Git_blob_at_exact_commit",
    "trusted_execution_adapter",
    "CI",
    *AUTHENTICATED_PRINCIPAL_SOURCES,
    "communication_publisher_observation",
    "exact_local_filesystem_observation",
    "product_or_connector_session_metadata",
    "task_bound_Human_attestation_for_unexposed_product_state",
}
REQUIRED_CLAIM_FIELDS = {
    "claim_id",
    "claim_role",
    "action_id_or_review_id",
    "expected_claim_source_ref",
    "expected_value_or_predicate",
    "observed_authoritative_source_class",
    "observed_value",
    "exact_observation_ref",
    "comparator_id",
    "relationship_or_equality_check",
    "verification_result",
}
CONSTITUTION_FIELDS = {
    "action_id",
    "action_class",
    "sender_endpoint_id",
    "intended_recipient_endpoint_id",
    "classification_basis_ref",
    "required_mechanisms",
    "resolver_result_ref",
    "gate_result_ref",
    "mechanism_execution_ref",
    "formal_artifact_ref",
    "activation_context",
    "mechanism_preconditions",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _activation_predicate_satisfied(predicate: str, context: dict[str, Any]) -> bool:
    if predicate == "intended_cross_endpoint_side_effect_is_true":
        return any(bool(context.get(field)) for field in (
            "intended_cross_endpoint_side_effect",
            "Human_relay_requested",
            "non_Human_endpoint_action_requested",
            "current_formal_handoff_claimed",
        ))
    if predicate == "actionable_content_or_formal_state_claim_is_true":
        return bool(context.get("actionable_content") or context.get("formal_state_claim"))
    if predicate == "formal_action_requires_receiver_selection_is_true":
        return context.get("requires_receiver_selection") is True
    raise ActivationError("TRIGGER_PREDICATE_UNKNOWN", predicate=predicate)


class ActivationError(ValueError):
    """A deterministic fail-closed mechanism activation violation."""

    def __init__(self, code: str, **evidence: Any):
        self.code = code
        self.evidence = evidence
        super().__init__(code)


def _mapping(value: Any, code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ActivationError(code)
    return value


def _segment_is_formal(segment: dict[str, Any]) -> bool:
    side_effect = any(bool(segment.get(field)) for field in (
        "intended_cross_endpoint_side_effect",
        "Human_relay_requested",
        "non_Human_endpoint_action_requested",
        "current_formal_handoff_claimed",
    ))
    material = bool(segment.get("actionable_content") or segment.get("formal_state_claim"))
    if segment.get("material_cross_endpoint_intent_ambiguous"):
        raise ActivationError("FORMAL_ACTION_AMBIGUOUS")
    if material and not side_effect and (
        segment.get("intended_recipient_is_Human_only") is True
        and not segment.get("formal_state_claim")
    ):
        return False
    if side_effect != material and (side_effect or material):
        raise ActivationError("FORMAL_ACTION_SEMANTICS_INCOMPLETE")
    return side_effect and material


def classify_planned_action(context: dict[str, Any]) -> dict[str, Any]:
    """Classify structured semantics; labels and keywords are intentionally ignored."""
    context = _mapping(context, "ACTION_CONTEXT_MUST_BE_MAPPING")
    segments = context.get("semantic_segments")
    if segments is None:
        segments = [context]
    if not isinstance(segments, list) or not segments or any(not isinstance(v, dict) for v in segments):
        raise ActivationError("SEMANTIC_SEGMENTS_INVALID")

    formal_indexes: list[int] = []
    formal_types: list[str] = []
    for index, segment in enumerate(segments):
        if _segment_is_formal(segment):
            formal_indexes.append(index)
            message_type = segment.get("formal_message_type", context.get("formal_message_type"))
            if message_type not in FORMAL_MESSAGE_ACTIONS:
                raise ActivationError("FORMAL_MESSAGE_TYPE_REQUIRED")
            formal_types.append(str(message_type))

    if not formal_indexes:
        human_only = all(bool(segment.get("intended_recipient_is_Human_only")) for segment in segments)
        if not human_only:
            raise ActivationError("ORDINARY_DISCUSSION_BOUNDARY_UNPROVEN")
        return {
            "classification": "ordinary_Human_foreground_discussion",
            "action_class": "ordinary_Human_foreground_discussion",
            "formal": False,
            "formal_segment_indexes": [],
            "authority_effect": "none",
        }

    if len(set(formal_types)) != 1:
        raise ActivationError("MULTIPLE_FORMAL_ACTION_CLASSES_REQUIRE_SEPARATE_CONSTITUTION")
    return {
        "classification": "formal_cross_endpoint_action",
        "action_class": FORMAL_MESSAGE_ACTIONS[formal_types[0]],
        "formal": True,
        "formal_segment_indexes": formal_indexes,
        "mixed_action_segmented": len(formal_indexes) != len(segments),
        "authority_effect": "none",
    }


def normalize_recipient(
    context: dict[str, Any],
    *,
    endpoint_cards: dict[str, dict[str, Any]] | None = None,
    aliases: dict[str, str] | None = None,
) -> str:
    """Resolve recipient from exact structured bindings, never lexical guessing."""
    explicit = context.get("intended_recipient_endpoint_id")
    if explicit:
        endpoint = str(explicit)
    elif context.get("recipient_alias"):
        alias = str(context["recipient_alias"])
        if not aliases or alias not in aliases:
            raise ActivationError("FORMAL_ACTION_RECIPIENT_ALIAS_UNRESOLVED")
        endpoint = str(aliases[alias])
    elif context.get("intended_recipient_task_role") and endpoint_cards:
        role = context["intended_recipient_task_role"]
        matches = sorted(
            endpoint_id for endpoint_id, card in endpoint_cards.items()
            if card.get("task_role") == role
        )
        if len(matches) != 1:
            raise ActivationError("FORMAL_ACTION_RECIPIENT_ROLE_AMBIGUOUS", matches=matches)
        endpoint = matches[0]
    else:
        raise ActivationError("FORMAL_ACTION_RECIPIENT_REQUIRED")

    if endpoint_cards is not None and endpoint not in endpoint_cards:
        raise ActivationError("FORMAL_ACTION_RECIPIENT_ENDPOINT_UNKNOWN", endpoint=endpoint)
    return endpoint


def resolve_required_mechanisms(
    context: dict[str, Any],
    trigger_registry: dict[str, Any],
    *,
    endpoint_cards: dict[str, dict[str, Any]] | None = None,
    aliases: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Pure policy decision: classify and compute the mandatory mechanism set."""
    classification = classify_planned_action(context)
    if not classification["formal"]:
        return {
            **classification,
            "action_id": context.get("action_id"),
            "normalized_recipient_endpoint_id": None,
            "required_mechanisms": [],
            "missing_preconditions": [],
            "route_requirements": [],
            "action_allowed_to_enter_enforcement": False,
            "ordinary_Human_discussion_allowed": True,
            "authority_effect": "none",
        }

    recipient = normalize_recipient(context, endpoint_cards=endpoint_cards, aliases=aliases)
    registry = _mapping(trigger_registry, "TRIGGER_REGISTRY_INVALID")
    mechanisms = _mapping(registry.get("mechanisms"), "TRIGGER_MECHANISMS_MISSING")
    action_class = classification["action_class"]
    required: list[str] = []
    missing: list[str] = []
    route_requirements: list[str] = []
    material_context = dict(context)
    material_context["intended_recipient_endpoint_id"] = recipient

    for mechanism_id, entry_value in mechanisms.items():
        entry = _mapping(entry_value, "TRIGGER_ENTRY_INVALID")
        predicates = entry.get("activation_predicates") or []
        if not isinstance(predicates, list) or any(not isinstance(value, str) for value in predicates):
            raise ActivationError("TRIGGER_PREDICATES_INVALID", mechanism_id=mechanism_id)
        predicate_match = bool(predicates) and all(
            _activation_predicate_satisfied(predicate, material_context)
            for predicate in predicates
        )
        mandatory = (
            action_class in (entry.get("mandatory_for_action_classes") or [])
            or predicate_match
        )
        if not mandatory:
            continue
        required.append(str(mechanism_id))
        for field in entry.get("required_inputs") or []:
            if material_context.get(field) in (None, "", []):
                missing.append(f"{mechanism_id}:{field}")
        if mechanism_id == "model_routing":
            route_requirements.append("receiver_setup")

    return {
        **classification,
        "action_id": context.get("action_id"),
        "normalized_recipient_endpoint_id": recipient,
        "required_mechanisms": sorted(required),
        "missing_preconditions": sorted(missing),
        "route_requirements": route_requirements,
        "action_allowed_to_enter_enforcement": not missing,
        "ordinary_Human_discussion_allowed": False,
        "authority_effect": "none",
    }


def evaluate_pre_action_gate(
    resolution: dict[str, Any],
    mechanism_preconditions: dict[str, Any],
    *,
    refs_root: Path | None = None,
) -> dict[str, Any]:
    """Verify required preconditions. A VERIFIED gate is not an authority grant."""
    resolution = _mapping(resolution, "RESOLUTION_INVALID")
    mechanism_preconditions = _mapping(mechanism_preconditions, "MECHANISM_PRECONDITIONS_INVALID")
    failures = list(resolution.get("missing_preconditions") or [])
    if not resolution.get("formal"):
        raise ActivationError("PRE_ACTION_GATE_NOT_APPLICABLE_TO_ORDINARY_DISCUSSION")
    if not resolution.get("action_allowed_to_enter_enforcement"):
        failures.append("resolver_did_not_admit_action")

    verified_refs: dict[str, str] = {}
    for mechanism_id in resolution.get("required_mechanisms") or []:
        precondition = mechanism_preconditions.get(mechanism_id)
        if not isinstance(precondition, dict):
            failures.append(f"{mechanism_id}:precondition_missing")
            continue
        if precondition.get("verification_result") != "VERIFIED":
            failures.append(f"{mechanism_id}:not_verified")
        evidence_ref = precondition.get("evidence_ref")
        if not isinstance(evidence_ref, str) or not evidence_ref:
            failures.append(f"{mechanism_id}:evidence_ref_missing")
        elif refs_root is not None:
            target = (refs_root.resolve() / evidence_ref).resolve()
            try:
                target.relative_to(refs_root.resolve())
            except ValueError:
                failures.append(f"{mechanism_id}:evidence_ref_outside_root")
            else:
                if not target.is_file():
                    failures.append(f"{mechanism_id}:evidence_ref_unreadable")
                else:
                    verified_refs[mechanism_id] = evidence_ref
        else:
            verified_refs[mechanism_id] = evidence_ref
        if precondition.get("freshness_required") is True and precondition.get("freshness_result") != "VERIFIED":
            failures.append(f"{mechanism_id}:freshness_not_verified")

    return {
        "gate_result": "BLOCKED" if failures else "VERIFIED",
        "action_id": resolution.get("action_id"),
        "action_class": resolution.get("action_class"),
        "required_mechanisms": list(resolution.get("required_mechanisms") or []),
        "verified_precondition_refs": verified_refs,
        "blocking_failures": sorted(set(failures)),
        "authority_effect": "none",
    }


def validate_constitution_evidence(
    evidence: dict[str, Any],
    *,
    resolution: dict[str, Any] | None = None,
    gate: dict[str, Any] | None = None,
) -> None:
    evidence = _mapping(evidence, "CONSTITUTION_EVIDENCE_INVALID")
    missing = sorted(CONSTITUTION_FIELDS - set(evidence))
    if missing:
        raise ActivationError("CONSTITUTION_EVIDENCE_FIELDS_MISSING", fields=missing)
    if not evidence.get("action_id") or not evidence.get("sender_endpoint_id"):
        raise ActivationError("CONSTITUTION_IDENTITY_MISSING")
    if not isinstance(evidence.get("required_mechanisms"), list) or not evidence["required_mechanisms"]:
        raise ActivationError("CONSTITUTION_REQUIRED_MECHANISMS_INVALID")
    if evidence.get("authority_effect") not in (None, "none"):
        raise ActivationError("CONSTITUTION_CANNOT_GRANT_AUTHORITY")
    if resolution is not None:
        if evidence.get("action_class") != resolution.get("action_class"):
            raise ActivationError("CONSTITUTION_ACTION_CLASS_MISMATCH")
        if evidence.get("intended_recipient_endpoint_id") != resolution.get("normalized_recipient_endpoint_id"):
            raise ActivationError("CONSTITUTION_RECIPIENT_MISMATCH")
        if evidence.get("required_mechanisms") != resolution.get("required_mechanisms"):
            raise ActivationError("CONSTITUTION_MECHANISM_SET_MISMATCH")
    if gate is not None:
        if gate.get("gate_result") != "VERIFIED":
            raise ActivationError("CONSTITUTION_GATE_NOT_VERIFIED")
        if gate.get("required_mechanisms") != evidence.get("required_mechanisms"):
            raise ActivationError("CONSTITUTION_GATE_MECHANISM_MISMATCH")


def _canonical_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("./"):
        raise ActivationError("PATH_REPRESENTATION_AMBIGUOUS")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ActivationError("PATH_REPRESENTATION_AMBIGUOUS")
    return path.as_posix()


def _subset_equal(expected: Any, observed: Any) -> str:
    if not isinstance(expected, dict) or not isinstance(observed, dict):
        return "UNVERIFIABLE"
    for key, value in expected.items():
        if key not in observed:
            return "UNVERIFIABLE"
        if observed[key] != value:
            return "MISMATCH"
    return "VERIFIED"


def _compare_claim(record: dict[str, Any]) -> str:
    comparator = record["comparator_id"]
    expected = record["expected_value_or_predicate"]
    observed = record["observed_value"]

    if comparator == "exact_sha_role_equality":
        if not isinstance(expected, str) or not isinstance(observed, str):
            return "UNVERIFIABLE"
        if not SHA40.fullmatch(expected) or not SHA40.fullmatch(observed):
            return "UNVERIFIABLE"
        return "VERIFIED" if expected == observed else "MISMATCH"

    if comparator == "exact_base_equality_plus_required_relation":
        if not isinstance(expected, dict) or not isinstance(observed, dict):
            return "UNVERIFIABLE"
        if not SHA40.fullmatch(str(expected.get("sha", ""))) or not SHA40.fullmatch(str(observed.get("sha", ""))):
            return "UNVERIFIABLE"
        if expected["sha"] != observed["sha"]:
            return "MISMATCH"
        if expected.get("required_relation") and observed.get("relation_satisfied") is not True:
            return "MISMATCH" if "relation_satisfied" in observed else "UNVERIFIABLE"
        return "VERIFIED"

    if comparator == "named_ref_fresh_state_relation":
        if not isinstance(expected, dict) or not isinstance(observed, dict):
            return "UNVERIFIABLE"
        if observed.get("fresh") is not True:
            return "STALE" if observed.get("fresh") is False else "UNVERIFIABLE"
        return "VERIFIED" if observed.get("sha") == expected.get("sha") else "MISMATCH"

    if comparator == "complete_path_set_within_authorized_boundary":
        if not isinstance(expected, dict) or not isinstance(observed, dict):
            return "UNVERIFIABLE"
        patterns = expected.get("allowed_patterns")
        paths = observed.get("paths")
        if not isinstance(patterns, list) or not isinstance(paths, list) or observed.get("complete") is not True:
            return "UNVERIFIABLE"
        try:
            canonical = [_canonical_path(path) for path in paths]
        except ActivationError:
            return "AMBIGUOUS"
        if len(canonical) != len(set(canonical)):
            return "AMBIGUOUS"
        for path in canonical:
            if not any(fnmatch.fnmatchcase(path, str(pattern)) for pattern in patterns):
                return "MISMATCH"
        return "VERIFIED"

    if comparator == "byte_integrity_and_semantic_role_binding":
        return _subset_equal(expected, observed)

    if comparator == "execution_result_bound_to_expected_candidate_inputs_and_entrypoint":
        return _subset_equal(expected, observed)

    if comparator == "published_message_identity_and_route_equality":
        return _subset_equal(expected, observed)

    if comparator == "authenticated_actor_satisfies_authorized_principal_binding":
        if record.get("observed_authoritative_source_class") not in AUTHENTICATED_PRINCIPAL_SOURCES:
            return "UNVERIFIABLE"
        if not record.get("subject_principal_observation_ref"):
            return "UNVERIFIABLE"
        if not isinstance(expected, dict) or not isinstance(observed, dict):
            return "UNVERIFIABLE"
        allowed = expected.get("allowed_principals")
        actual = observed.get("authenticated_principal")
        if not isinstance(allowed, list) or not actual:
            return "UNVERIFIABLE"
        if actual not in allowed:
            return "MISMATCH"
        remaining = {key: value for key, value in expected.items() if key != "allowed_principals"}
        return _subset_equal(remaining, observed)

    if comparator == "observed_review_setup_satisfies_required_isolation_profile":
        return _subset_equal(expected, observed)

    raise ActivationError("COMPARATOR_UNKNOWN", comparator_id=comparator)


def evaluate_material_claim(record: dict[str, Any]) -> str:
    """Recompute one two-sided material claim; never trust its declared verdict."""
    record = _mapping(record, "MATERIAL_CLAIM_INVALID")
    missing = sorted(REQUIRED_CLAIM_FIELDS - set(record))
    if missing:
        return "UNVERIFIABLE"
    expected_ref = record.get("expected_claim_source_ref")
    observation_ref = record.get("exact_observation_ref")
    if not isinstance(expected_ref, str) or not expected_ref or expected_ref.startswith("receipt:"):
        return "UNVERIFIABLE"
    if not isinstance(observation_ref, str) or not observation_ref:
        return "UNVERIFIABLE"
    if record.get("observed_authoritative_source_class") not in ACCEPTED_OBSERVATION_SOURCES:
        return "UNVERIFIABLE"
    if record.get("freshness_requirement_when_applicable") and not record.get("freshness_observation_ref"):
        return "STALE"
    return _compare_claim(record)


def validate_material_receipt(receipt: dict[str, Any]) -> dict[str, str]:
    """Recompute all claims and reject any declared/aggregate overclaim."""
    receipt = _mapping(receipt, "MATERIAL_RECEIPT_INVALID")
    claims = receipt.get("material_claims")
    if not isinstance(claims, list) or not claims:
        raise ActivationError("MATERIAL_RECEIPT_CLAIMS_MISSING")
    results: dict[str, str] = {}
    for claim in claims:
        if not isinstance(claim, dict) or not claim.get("claim_id"):
            raise ActivationError("MATERIAL_CLAIM_ID_MISSING")
        result = evaluate_material_claim(claim)
        if result not in VERIFICATION_RESULTS:
            raise ActivationError("MATERIAL_CLAIM_RESULT_INVALID")
        if claim.get("verification_result") != result:
            raise ActivationError(
                "MATERIAL_CLAIM_DECLARED_RESULT_MISMATCH",
                claim_id=claim.get("claim_id"),
                declared=claim.get("verification_result"),
                recomputed=result,
            )
        results[str(claim["claim_id"])] = result
    aggregate = "VERIFIED" if all(value == "VERIFIED" for value in results.values()) else "BLOCKED"
    if receipt.get("aggregate_result") != aggregate:
        raise ActivationError("MATERIAL_RECEIPT_AGGREGATE_MISMATCH", recomputed=aggregate)
    return results


def _git(repo_root: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args], cwd=repo_root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    return proc.returncode, proc.stdout.strip()


def observe_git_commit_claim(
    repo_root: Path,
    *,
    claim_id: str,
    claim_role: str,
    action_id_or_review_id: str,
    expected_source_ref: str,
    expected_sha: str,
) -> dict[str, Any]:
    """Create a claim from the actual Git object database and execute equality."""
    rc, observed = _git(repo_root, "rev-parse", f"{expected_sha}^{{commit}}")
    observed_value = observed if rc == 0 else None
    record = {
        "claim_id": claim_id,
        "claim_role": claim_role,
        "action_id_or_review_id": action_id_or_review_id,
        "expected_claim_source_ref": expected_source_ref,
        "expected_value_or_predicate": expected_sha,
        "observed_authoritative_source_class": "actual_Git_object_database",
        "observed_value": observed_value,
        "exact_observation_ref": f"git:rev-parse:{expected_sha}^{{commit}}",
        "comparator_id": "exact_sha_role_equality",
        "relationship_or_equality_check": "observed_commit_SHA_equals_expected_semantic_role_SHA",
        "verification_result": "UNVERIFIABLE",
    }
    record["verification_result"] = evaluate_material_claim(record)
    return record


def observe_changed_path_claim(
    repo_root: Path,
    *,
    claim_id: str,
    action_id_or_review_id: str,
    expected_source_ref: str,
    base_sha: str,
    candidate_sha: str,
    allowed_patterns: list[str],
) -> dict[str, Any]:
    """Observe the complete NUL-safe Git path set for a bound base/candidate pair."""
    proc = subprocess.run(
        ["git", "diff", "--name-only", "--no-renames", "-z", base_sha, candidate_sha],
        cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    paths = proc.stdout.decode("utf-8", "surrogateescape").split("\0") if proc.returncode == 0 else []
    if paths and paths[-1] == "":
        paths.pop()
    record = {
        "claim_id": claim_id,
        "claim_role": "changed_path_and_diff_scope",
        "action_id_or_review_id": action_id_or_review_id,
        "expected_claim_source_ref": expected_source_ref,
        "expected_value_or_predicate": {"allowed_patterns": allowed_patterns},
        "observed_authoritative_source_class": "complete_Git_compare",
        "observed_value": {
            "base_sha": base_sha,
            "candidate_sha": candidate_sha,
            "paths": paths,
            "complete": proc.returncode == 0,
        },
        "exact_observation_ref": f"git:diff--name-only--no-renames-z:{base_sha}..{candidate_sha}",
        "comparator_id": "complete_path_set_within_authorized_boundary",
        "relationship_or_equality_check": "complete_canonical_path_set_within_authorized_patterns",
        "verification_result": "UNVERIFIABLE",
    }
    record["verification_result"] = evaluate_material_claim(record)
    return record

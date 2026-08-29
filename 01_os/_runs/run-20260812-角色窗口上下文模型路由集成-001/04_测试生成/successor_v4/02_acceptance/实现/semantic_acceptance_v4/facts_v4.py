#!/usr/bin/env python3
"""Typed decision facts for the v4 coverage extension.

Same rule as `semantic_acceptance.decision_facts`: a decision fact carries no
field describing HOW something was written.  `test_v4_representation_boundary.py`
asserts that no class here declares a name in
`semantic_acceptance.decision_facts.RENDERING_FIELD_NAMES`, and that
`predicates_v4.py` never mentions one.

Rendering observations from the v4 adapters go to the same `EvidenceSet` the
accepted engine already carries, so the debugging information still exists — it
is the ACCESS that is removed, not the information.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LifecycleFact:
    """A03/R03.

    `state_roles` holds the normalized A-required roles this declaration covers.
    `declared_state_count` is a count, not a spelling: the exact state names are
    B_ONLY (requirement_traceability_v1.yml), so they are never compared.
    """

    source_id: str
    key_path: str
    state_roles: tuple[str, ...]
    declared_state_count: int
    unmapped_state_count: int


@dataclass(frozen=True)
class LifecycleConditionFact:
    """A03/R03.  One declared condition governing continuation on cached context.

    Ruling F03-D: determinism is a TYPED fact, not the absence of a vague word.
    `deterministic` is true only when all three semantic slots resolved, and the
    slots are carried alongside it so a reader can see WHICH one was missing
    without re-deriving it.

    `unresolved_slots` names the slots that did not resolve.  It is empty exactly
    when `deterministic` is true, which `test_v4_metamorphic.py` asserts, so the
    two fields cannot drift apart into a fact that claims determinism and also
    reports a hole.

    None of these fields describes HOW the condition was written.  Which
    container shape or which admitted spelling produced them is evidence and
    goes to the EvidenceSet, never here.
    """

    source_id: str
    key_path: str
    deterministic: bool
    subject_resolved: bool
    observation_role: str
    consequence_role: str
    unresolved_slots: tuple[str, ...]


@dataclass(frozen=True)
class ContextContractFact:
    """A04/R04.  The declared derivation inputs of a minimum-effective-context contract."""

    source_id: str
    key_path: str
    input_roles: tuple[str, ...]


@dataclass(frozen=True)
class ContextLoadEntryFact:
    """A04/R04.  One entry of a derived load set.

    `exact` answers A's "exact paths/versions or hashes where material".
    `historical_region` and `excluded_material` answer the two prohibitions A
    states after it.
    """

    source_id: str
    key_path: str
    exact: bool
    historical_region: bool
    excluded_material: bool


@dataclass(frozen=True)
class PreloadPositionFact:
    """A04/R04.  A position whose enablement decides whether historical preload happens."""

    source_id: str
    key_path: str
    enablement: str
    key_is_negated: bool
    deciding_leaf: str


@dataclass(frozen=True)
class FreshnessBindingFact:
    """A05/R05.  Whether a dependency fingerprint is bound to the window at all."""

    source_id: str
    key_path: str
    fingerprint_bound: bool


@dataclass(frozen=True)
class FreshnessTriggerFact:
    """A05/R05.  One trigger and the effect declared for it.

    `effect_role` is one of the three roles in V4-FRESH-05, or the empty string
    when the declared effect maps to none of them.  The empty case is UNKNOWN and
    fails closed; it is never silently treated as compliant.
    """

    source_id: str
    key_path: str
    trigger_role: str
    effect_role: str


@dataclass(frozen=True)
class RouteReceiptFact:
    """A07/R07.  One model-routing receipt binding."""

    source_id: str
    key_path: str
    window_bound: bool
    concept_roles: tuple[str, ...]
    authority_is_routing_only: bool
    authority_declared: bool
    # T2-PARENT-IR-002 / A12. What the contract says happens when this receipt is
    # missing, stale or inconsistent, as a typed fact rather than an unread
    # declaration. `failure_policy_role` is resolved through the accepted
    # freshness-effect roles under parity, so an inverted or unrecognised policy
    # resolves to "" and is non-pass exactly like an absent one.
    failure_policy_declared: bool = False
    failure_policy_role: str = ""


@dataclass(frozen=True)
class IndependenceFact:
    """A08/R08.  The declared review-independence constraint."""

    source_id: str
    key_path: str
    distinct_session_enablement: str
    self_review_rejected: bool
    self_review_effect_declared: bool


@dataclass(frozen=True)
class FamilyRequirementFact:
    """A08/R08.  A model-family position, and whether it is a constraint or a choice."""

    source_id: str
    key_path: str
    expressed_as_constraint: bool


@dataclass(frozen=True)
class MechanismSeparationFact:
    """A10/R10.  A region of a composition artifact that copies upstream mutable semantics."""

    source_id: str
    surface: str
    key_path: str
    upstream_role: str
    copied_entry_count: int
    pointer_only: bool


@dataclass(frozen=True)
class FailureCaseFact:
    """A12/R12.  One declared failure case and whether its effect is visibly failing."""

    source_id: str
    key_path: str
    case_role: str
    visible_failure: bool
    effect_declared: bool


@dataclass(frozen=True)
class FallbackPositionFact:
    """A12/R12.  A fallback position whose enablement A R12 constrains."""

    source_id: str
    key_path: str
    enablement: str
    key_is_negated: bool
    deciding_leaf: str


V4_DECISION_FACT_CLASSES = (
    LifecycleFact,
    LifecycleConditionFact,
    ContextContractFact,
    ContextLoadEntryFact,
    PreloadPositionFact,
    FreshnessBindingFact,
    FreshnessTriggerFact,
    RouteReceiptFact,
    IndependenceFact,
    FamilyRequirementFact,
    MechanismSeparationFact,
    FailureCaseFact,
    FallbackPositionFact,
)


V4_FACT_SET_ATTRIBUTES = (
    "v4_lifecycles",
    "v4_lifecycle_conditions",
    "v4_context_contracts",
    "v4_context_load_entries",
    "v4_preload_positions",
    "v4_freshness_bindings",
    "v4_freshness_triggers",
    "v4_route_receipts",
    "v4_independence",
    "v4_family_requirements",
    "v4_mechanism_separation",
    "v4_failure_cases",
    "v4_fallback_positions",
)

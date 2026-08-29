#!/usr/bin/env python3
"""Typed decision facts, and the separate interface rendering evidence uses.

C-08 requires that "decision facts and rendering evidence use separate
interfaces".  The independent review found the opposite: `predicates.py` read
`source_container`, `source_form` and `entry_forms`, all of which record HOW an
artifact was written rather than WHAT it declares.  A comment marking them
"evidence only" is not a separation; a reviewer had to notice the violation by
reading code.

So the separation here is structural.  A decision fact dataclass physically has
no field that names a container, a form, a serialization or a label source, and
`RENDERING_FIELD_NAMES` below is the machine-checkable statement of that.
`test_representation_boundary.py` asserts three things against it:

  * no decision fact class declares any of those names;
  * `predicates.py` contains no reference to any of them;
  * every rendering observation the old fact set carried still EXISTS, on
    `EvidenceSet`, so the separation removed access rather than information.

The last one matters.  Deleting the evidence would have made the boundary easy
and the debugging impossible.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Any

from .provenance import rule

# Names that describe how something was written.  A decision fact may not carry
# one; `EvidenceSet` exists to hold them.
RENDERING_FIELD_NAMES = frozenset(
    {
        "source_container",
        "source_form",
        "entry_forms",
        "entry_form",
        "role_label_source",
        "container",
        "serialized",
        "raw_value",
        "raw_text",
        "line",
        "lines",
    }
)


# --------------------------------------------------------------------------
# decision facts
# --------------------------------------------------------------------------

ROLE_OWNERSHIP_VALUES = tuple(
    rule(
        "V-FACT-01",
        kind="mapping",
        authority="A01/R01_role_contract",
        interpretation="Typed outcomes of the role-ownership adapter.",
        value=("owns_semantics", "references_only"),
    )
)
OWNS_SEMANTICS, REFERENCES_ONLY = ROLE_OWNERSHIP_VALUES

PROVIDER_BINDING_KINDS = tuple(
    rule(
        "V-FACT-02",
        kind="mapping",
        authority="A06/R06_role_to_model_requirements; R08_independence_constraints",
        interpretation="Typed outcomes for a provider/model occurrence's decision role.",
        value=("normative_selector", "negative_constraint", "mention", "provenance", "pointer"),
    )
)
(
    NORMATIVE_SELECTOR,
    NEGATIVE_CONSTRAINT,
    MENTION,
    PROVENANCE_RECORD,
    POINTER_REFERENCE,
) = PROVIDER_BINDING_KINDS

LATEST_SESSION_STATUSES = tuple(
    rule(
        "V-FACT-03",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation="Typed outcomes for latest-session use in formal window identity.",
        value=("absent", "prohibited_as_identity", "allowed_as_identity"),
    )
)
LATEST_ABSENT, LATEST_PROHIBITED, LATEST_ALLOWED = LATEST_SESSION_STATUSES

PREDECESSOR_MATCH_ABSENT = rule(
    "V-FACT-07",
    kind="default",
    authority="A02/R02_window_identity",
    interpretation="No predecessor-match declaration was present in the adapted entry mode.",
    value="absent",
)

CARRIED_FIELD_KINDS = tuple(
    rule(
        "V-FACT-04",
        kind="mapping",
        authority="A09/R09_structured_handoff",
        interpretation="Typed outcomes for fields physically carried by a handoff payload.",
        value=("pointer", "mutable_delivery_state", "private_reasoning", "other"),
    )
)
CARRIED_POINTER, MUTABLE_DELIVERY_STATE, PRIVATE_REASONING, OTHER_CARRIED = CARRIED_FIELD_KINDS

AUTHORITY_FACT_KINDS = tuple(
    rule(
        "V-FACT-05",
        kind="mapping",
        authority="A13/R13_no_authority_escalation",
        interpretation="Typed outcomes for a field that mentions or confers authority.",
        value=("reference", "description", "decision_input", "grant"),
    )
)
AUTHORITY_REFERENCE, AUTHORITY_DESCRIPTION, AUTHORITY_INPUT, AUTHORITY_GRANT = AUTHORITY_FACT_KINDS

CATALOG_DETECTOR_KINDS = tuple(
    rule(
        "V-FACT-06",
        kind="mapping",
        authority="A11/R11_workflow_and_entry_thinness",
        interpretation="Independent typed detectors for a second mutable routing catalog.",
        value=("restatement", "independent_declaration"),
    )
)
CATALOG_RESTATEMENT, CATALOG_INDEPENDENT_DECLARATION = CATALOG_DETECTOR_KINDS


@dataclass(frozen=True)
class RoleFact:
    """A01/R01.  Identity is read verbatim; the label's words are never checked."""

    source_id: str
    surface: str
    role_id: str
    ownership: str  # owns_semantics | references_only
    semantic_fields_present: tuple[str, ...]
    pointer_fields_present: tuple[str, ...]
    key_path: str


@dataclass(frozen=True)
class ProviderBindingFact:
    """A06/R06/R08.  `provider_label` is the subject as written, never matched."""

    source_id: str
    key_path: str
    subject: str | None
    selector_kind: str  # normative_selector | negative_constraint | mention | provenance | pointer
    polarity: str
    provider_label: str


@dataclass(frozen=True)
class WindowIdentityFact:
    """A02/R02.

    `b_only_facts` is a separate field from `bound_facts` on purpose: run_id was
    promoted into an A requirement once (ST04-V3-IR-004) and a shared list is
    what made that a one-line edit.
    """

    source_id: str
    key_path: str
    bound_facts: tuple[str, ...]
    b_only_facts: tuple[str, ...]
    latest_session_pointer_status: str


@dataclass(frozen=True)
class EntryModeFact:
    """A02/R02.  Carries no container: MT01/MT02 assert the container cannot matter."""

    source_id: str
    key_path: str
    mode_id: str
    is_fresh: bool
    is_reentry: bool
    required_facts: tuple[str, ...]
    predecessor_required: bool
    predecessor_match: str


@dataclass(frozen=True)
class DeclarationFact:
    """A09/R09.  The five source forms reduce to one (field, polarity) pair."""

    source_id: str
    field: str
    polarity: str
    key_path: str


@dataclass(frozen=True)
class CarriedFieldFact:
    """A09/R09.  What the payload actually holds, read independently of what it declares."""

    source_id: str
    scope: str
    field: str
    kind: str  # pointer | mutable_delivery_state | private_reasoning | other
    key_path: str


@dataclass(frozen=True)
class AutonomyFact:
    """A14/R14.  `deciding_leaf` locates the enablement inside a nested declaration."""

    source_id: str
    key_path: str
    behaviour: str
    enablement: str
    key_is_negated: bool
    deciding_leaf: str


@dataclass(frozen=True)
class AuthorityFact:
    """A13/R13."""

    source_id: str
    key_path: str
    subject: str | None
    kind: str  # reference | description | decision_input | grant
    enablement: str
    deciding_leaf: str


@dataclass(frozen=True)
class CatalogFact:
    """A11/R11.

    Two independent detectors, each separately traced:

      restatement            a collection restating >= CATALOG_MIN_ENTRIES live
                             identifiers, compared canonically so that case,
                             spacing and punctuation variants do not evade it;
      independent_declaration a collection of entries binding routing identifier
                             fields, which detects a second catalog whose every
                             identifier is unseen.
    """

    source_id: str
    catalog_kind: str
    detector: str  # restatement | independent_declaration
    identifiers_restated: tuple[str, ...]
    entry_count: int


@dataclass(frozen=True)
class UnsupportedFact:
    """A representation the pipeline cannot interpret.  Visible, never silent."""

    source_id: str
    key_path: str
    reason: str


@dataclass(frozen=True)
class UntracedRuleFact:
    """A decision rule with no A or Human authority.

    C-09 forbids applying it.  It is surfaced as a finding so that the missing
    requirement is asked for rather than invented.
    """

    rule_id: str
    kind: str
    interpretation: str


# --------------------------------------------------------------------------
# rendering evidence — reachable, but not from a predicate
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class RenderingObservation:
    """How a fact happened to be written.  Never an input to acceptance."""

    source_id: str
    key_path: str
    observation: str  # e.g. "source_container=list_of_pairs"
    value_repr: str


@dataclass
class EvidenceSet:
    observations: list[RenderingObservation] = dc_field(default_factory=list)

    def add(self, source_id: str, key_path: str, observation: str, value: Any = None) -> None:
        self.observations.append(
            RenderingObservation(source_id, key_path, observation, repr(value))
        )

    def for_path(self, key_path: str) -> list[RenderingObservation]:
        return [o for o in self.observations if o.key_path == key_path]

    def observations_of(self, kind: str) -> list[RenderingObservation]:
        return [o for o in self.observations if o.observation.startswith(kind)]

    def __len__(self) -> int:  # pragma: no cover - convenience
        return len(self.observations)


DECISION_FACT_CLASSES = (
    RoleFact,
    ProviderBindingFact,
    WindowIdentityFact,
    EntryModeFact,
    DeclarationFact,
    CarriedFieldFact,
    AutonomyFact,
    AuthorityFact,
    CatalogFact,
    UnsupportedFact,
    UntracedRuleFact,
)

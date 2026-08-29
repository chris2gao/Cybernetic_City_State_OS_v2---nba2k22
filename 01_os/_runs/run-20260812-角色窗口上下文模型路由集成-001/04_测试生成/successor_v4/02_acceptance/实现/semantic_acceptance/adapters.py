#!/usr/bin/env python3
"""Schema-bound adapters: the only place meaning is attached to structure.

    raw artifact -> parser (core) -> ADAPTER -> typed decision facts

Each adapter declares what it applies to, cites the A requirement that defines
the semantics it produces, and emits typed facts plus rendering evidence on two
separate channels.  An adapter that cannot interpret a construct inside a region
it has claimed emits `UnsupportedFact` rather than guessing or ignoring.

Two properties distinguish this from the extractor the independent review
rejected, and both are asserted mechanically in `test_representation_boundary.py`:

  * no adapter consults the NAME of a subject.  There is no provider list, no
    vendor list, no role-name list.  `NacreCompute-QX` and an established vendor
    take the identical path, because the path never reads the string;

  * every vocabulary an adapter uses comes from `vocabulary.py`, where it is
    bound to an A requirement through `provenance.rule`.  A constant that decides
    acceptance cannot be introduced here.

The failure the reviewer named — "representation bias moved from the predicate
into the extractor" — is addressed by moving the *ability* to decide, not by
moving the code.  An adapter that stops matching produces no facts; it does not
fall back to inference.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .core import (
    Document,
    DISABLED,
    ENABLED,
    NEGATIVE,
    POSITIVE,
    UNKNOWN,
    Leaf,
    Node,
    bound_leaves,
    bound_nodes,
    canonical_identifier,
    classify_enablement,
    extract_declarations_recursive,
    is_descriptive_segment,
    is_double_negated,
    is_negated,
    is_path_like,
    is_pointer_key,
    is_provenance_segment,
    is_schema_meta_key,
    normalize_field_name,
    normalize_keyed_collection,
    path_is_negated,
    subtree_enablement,
    tokens,
    walk_leaves,
    walk_nodes,
)
from .structural_binding import (
    CLAIMABLE_ROLES,
    CONFLICTING_ROLE,
    UNBOUND,
    UNKNOWN_ROLE,
    unsupported_reason,
)
from .decision_facts import (
    OWNS_SEMANTICS,
    REFERENCES_ONLY,
    AUTHORITY_DESCRIPTION,
    AUTHORITY_GRANT,
    AUTHORITY_INPUT,
    AUTHORITY_REFERENCE,
    AuthorityFact,
    AutonomyFact,
    CARRIED_POINTER,
    CATALOG_INDEPENDENT_DECLARATION,
    CATALOG_RESTATEMENT,
    CarriedFieldFact,
    CatalogFact,
    DeclarationFact,
    EntryModeFact,
    EvidenceSet,
    LATEST_ABSENT,
    LATEST_ALLOWED,
    LATEST_PROHIBITED,
    MENTION,
    MUTABLE_DELIVERY_STATE,
    NEGATIVE_CONSTRAINT,
    NORMATIVE_SELECTOR,
    OTHER_CARRIED,
    POINTER_REFERENCE,
    PREDECESSOR_MATCH_ABSENT,
    PRIVATE_REASONING,
    PROVENANCE_RECORD,
    ProviderBindingFact,
    RoleFact,
    UnsupportedFact,
    WindowIdentityFact,
)
from .vocabulary import (
    ALLOW_POLARITY_TOKENS,
    AUTHORITY_NON_GRANT_VALUES,
    AUTOMATION_BEHAVIOUR_TOKENS,
    AUTOMATION_QUALIFIER_TOKENS,
    AUTONOMY_STANDALONE_TOKENS,
    B_ONLY_IDENTITY_FACTS,
    CATALOG_IDENTIFIER_FIELD_TOKENS,
    CATALOG_MIN_ENTRIES,
    BOUND_FACT_FIELD_TOKENS,
    DELIVERY_STATE_TOKENS,
    ENTRY_REGION_TOKENS,
    EXACT_PREDECESSOR_MATCH,
    FRESH_TOKENS,
    GRANT_HEAD_TOKENS,
    IDENTITY_FACT_SYNONYMS,
    IDENTITY_REGION_TOKENS,
    INDEPENDENCE_POSITION_TOKENS,
    LATEST_SESSION_POSITION_TOKENS,
    LATEST_SESSION_SAFE_STATUS,
    MODE_REGION_TOKENS,
    MATCH_QUALIFIER_TOKENS,
    PAYLOAD_SCOPE_TOKENS,
    PREDECESSOR_POSITION_TOKENS,
    PRIVATE_REASONING_TOKENS,
    REENTRY_TOKENS,
    REQUIRED_QUALIFIER_TOKENS,
    ROLE_SCOPE_TOKENS,
    ROLE_COLLECTION_MIN_ENTRIES,
    ROLE_LABEL_FIELD_TOKENS,
    ROLE_SEMANTIC_FIELD_TOKENS,
    SELECTION_SLOT_TOKENS,
    SELECTION_CONTAINER_TOKENS,
    SELECTOR_REGION_TOKENS,
    WINDOW_REGION_TOKENS,
)


@dataclass(frozen=True)
class AdapterSpec:
    """What an adapter applies to, and the authority for what it produces."""

    adapter_id: str
    produces: str
    applicability: str
    a_trace: tuple[str, ...]
    decision_rule_ids: tuple[str, ...]
    ambiguity_policy: str = "fail_closed_as_unsupported"


ADAPTERS: dict[str, AdapterSpec] = {}


def _register(spec: AdapterSpec) -> AdapterSpec:
    ADAPTERS[spec.adapter_id] = spec
    return spec


# --------------------------------------------------------------------------
# shared helpers
# --------------------------------------------------------------------------


def _candidate_nodes(doc: Document) -> list[Node]:
    """Every container in the document, plus the document root itself.

    Discovery reaches a declared block through containers that add no semantic
    content of their own, so wrapping a role table in `contract:` cannot change
    what it is (S01-S03).

    This traversal stays UNFILTERED on purpose. Detectors whose job is to find
    something that should not exist — a second catalog, a second role source, a
    provider pinned outside the live catalog — must keep full visibility, or a
    violation could hide by sitting at a position the binding does not describe.
    Ownership adapters use `_claimable_nodes` instead.
    """
    return bound_nodes(doc)


def _claimable_nodes(doc: Document) -> list[Node]:
    """Containers whose position the structural binding licenses for claim.

    T2-SP-UPSTREAM-CM-v2, and the whole point of correction-003: the five global
    scans that were measured leaking — entry mode, provider ambiguity, carried
    field, authority and autonomy — attach OWNERSHIP to a position. Ownership
    requires the position to be an adapter-owned declaration name. An instance
    identity inside an open keyed collection, an unresolved position and a
    conflicting binding are all refused, whatever the body looks like.
    """
    return [n for n in bound_nodes(doc) if n.structurally_claimable]


def _claimable_leaves(doc: Document) -> list[Leaf]:
    """Scalar leaves the structural binding licenses for an ownership claim."""
    return [lf for lf in bound_leaves(doc) if lf.structurally_claimable]


def _is_pointer_field(key: str, value: Any) -> bool:
    if is_pointer_key(key) or is_path_like(value):
        return True
    if isinstance(value, (dict, list)):
        return any(is_path_like(leaf.value) for leaf in walk_leaves(value))
    return False


def _carries_no_statement(value: Any) -> bool:
    """RETIRED as an ownership rule by T2-SP-UPSTREAM-CM-v2. Kept as a predicate.

    This helper is no longer consulted by `adapt_authority` or `adapt_autonomy`.
    correction-003 introduced it to keep a foreign keyed-collection entry
    identity out of the A13/A14 fact channel, and the independent review found
    that because it reads the BODY rather than the position, it also suppressed
    a genuine authority or autonomy declaration whose value is an empty
    container — contradicting V-EN-02, under which an empty collection at a
    genuine enablement position is an explicit DISABLED decision.

    Structural provenance now carries the ownership question, so the body no
    longer has to. The function stays because it states a true and narrow fact
    about a value, and removing a correct predicate that other code may yet want
    is a separate change from retiring the rule that misused it.

    Original note follows.

    A container with no leaf at all states nothing this system can decode.

    correction-003, 00008 fact-channel audit. `subtree_enablement` returns
    `disabled` for `{}` and for `[]`, but that is a DEFAULT, not a reading: there
    is no leaf, so nothing was decoded. A scalar - including `false` - is a
    statement and stays a decision fact.

    This is what makes A13's own applicability text true in code ("a key that
    speaks about authority without conferring it is a descriptive position and
    produces evidence only") and it is what keeps the fact channel equal across
    the five normalize_keyed_collection-equivalent forms: a keyed-collection
    entry identifier carries an empty body in every one of them, so it must not
    become a decision fact in the two forms that happen to put it in key
    position. Reads presence of a leaf only - no name, no depth, no arity.
    """
    return isinstance(value, (dict, list)) and not any(True for _ in walk_leaves(value))


def _normative_statement(value: Any) -> bool:
    """Does this value carry a normative statement, rather than merely a name?

    correction-003. A01 role semantics are STATEMENTS about duty and
    independence: prose, or a list of prose. A token hit on a key whose value is
    a container of something else is a candidate, never a claim - which is the
    whole distinction the 00004 ruling draws.

    `independence_violation: {}` and `independence_violation: {severity: blocking}`
    both hit `independence` lexically. Neither states an obligation, so neither
    corroborates role ownership. `independence_requirement: "must not review its
    own output"` does.

    Reads the SHAPE of the value only. No subject name, no field-name whitelist
    beyond the vocabulary-bound token set the caller already applied.
    """
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(isinstance(x, str) and x.strip() for x in value)
    return False


def _semantic_role_fields(body: Any) -> tuple[list[str], list[str]]:
    """Role-defining fields and pointer fields carried by one entry.

    A pointer takes precedence over a semantic name: `handoff_ref` names where a
    rule lives and is not the rule (i07 / MT09 are the two directions).

    correction-003: a role-semantic TOKEN makes the field a candidate; the field
    corroborates ownership only when its value decodes as a normative statement
    this adapter owns. That is the entry-boundary corroboration the ruling
    requires, and it is what stops a failure-case identifier from claiming the
    document that happens to contain it.
    """
    semantic: list[str] = []
    pointers: list[str] = []
    if not isinstance(body, dict):
        return semantic, pointers
    for key, value in body.items():
        ks = str(key)
        if _is_pointer_field(ks, value):
            pointers.append(ks)
            continue
        if set(tokens(ks)) & ROLE_SEMANTIC_FIELD_TOKENS and _normative_statement(value):
            semantic.append(ks)
    return semantic, pointers


# --------------------------------------------------------------------------
# A01 / R01 — role contract
# --------------------------------------------------------------------------

ROLE_ADAPTER = _register(
    AdapterSpec(
        adapter_id="role_contract.v1",
        produces="RoleFact",
        applicability=(
            "a keyed collection, at any container depth, at least "
            f"{ROLE_COLLECTION_MIN_ENTRIES} of whose entries bind a role-defining "
            "field (vocabulary.V-ROLE-01). Entry identity is the collection key, or "
            "a declared label field, read verbatim."
        ),
        a_trace=("A01", "R01_role_contract", "R11_workflow_and_entry_thinness"),
        decision_rule_ids=(
            "V-ROLE-01", "V-ROLE-02", "V-ROLE-03", "V-POS-05",
            "V-POS-01", "V-POS-02", "V-POS-03", "V-EN-01", "V-DISC-04",
        ),
    )
)


def _entry_identity(entry_key: str, body: Any) -> str:
    """Identity, read verbatim.  The label's WORDS are never checked."""
    if isinstance(body, dict):
        for lk in body:
            if set(tokens(str(lk))) & ROLE_LABEL_FIELD_TOKENS:
                v = body[lk]
                if isinstance(v, str) and v.strip():
                    return normalize_field_name(v)
    return normalize_field_name(entry_key)


def adapt_roles(doc: Document, evidence: EvidenceSet) -> list[RoleFact]:
    """Role contracts, at structurally claimable collection positions only.

    Codex B2_UNBOUND_ROLE_AND_WINDOW_ADAPTER_CLAIMS. This adapter used the
    unfiltered traversal, on the reasoning that a detector looking for a SECOND
    role source must keep full visibility. That reasoning was wrong about which
    channel it applies to: `adapt_roles` does not report a violation, it emits
    an ownership fact. A wholly unregistered document resolved every position as
    unknown and still produced two `owns_semantics` RoleFacts, which is the
    universal CM-v2 pre-claim gate not being applied.

    Detection of a second role source survives because an unregistered document
    holding role positions is reported by the refusal surface, and an
    unsupported result is not a pass.
    """
    out: list[RoleFact] = []
    claimed: list[str] = []
    for node in _claimable_nodes(doc):
        if any(node.key_path.startswith(c) for c in claimed if c):
            continue
        entries = normalize_keyed_collection(node.value)
        if not entries:
            continue
        owning: list[tuple[str, Any, list[str], list[str]]] = []
        referencing: list[tuple[str, Any, list[str], list[str]]] = []
        for entry_key, body in entries.items():
            semantic, pointers = _semantic_role_fields(body)
            if semantic:
                owning.append((entry_key, body, semantic, pointers))
            elif pointers:
                referencing.append((entry_key, body, semantic, pointers))
        if len(owning) < ROLE_COLLECTION_MIN_ENTRIES:
            continue
        claimed.append(node.key_path)
        for entry_key, body, semantic, pointers in owning + referencing:
            ownership = OWNS_SEMANTICS if semantic else REFERENCES_ONLY
            key_path = f"{node.key_path}.{entry_key}" if node.key_path else entry_key
            evidence.add(
                doc.doc_id,
                key_path,
                "role_label_source="
                + (
                    "label_field"
                    if isinstance(body, dict)
                    and any(set(tokens(str(k))) & ROLE_LABEL_FIELD_TOKENS for k in body)
                    else "mapping_key"
                ),
                entry_key,
            )
            out.append(
                RoleFact(
                    source_id=doc.doc_id,
                    surface=doc.surface,
                    role_id=_entry_identity(entry_key, body),
                    ownership=ownership,
                    semantic_fields_present=tuple(sorted(semantic)),
                    pointer_fields_present=tuple(sorted(pointers)),
                    key_path=key_path,
                )
            )
    return out


# --------------------------------------------------------------------------
# A02 / R02 — window identity and entry modes
# --------------------------------------------------------------------------

WINDOW_ADAPTER = _register(
    AdapterSpec(
        adapter_id="window_contract.v1",
        produces="WindowIdentityFact + EntryModeFact",
        applicability=(
            "a mapping, at any container depth, keyed as a window identity block or "
            "as an entry-mode collection"
        ),
        a_trace=("A02", "R02_window_identity"),
        decision_rule_ids=(
            "V-WIN-01", "V-WIN-02", "V-WIN-03", "V-WIN-04",
            "V-WIN-05", "V-WIN-06", "V-WIN-07", "V-WIN-08",
            "V-WIN-09", "V-WIN-10", "V-WIN-11", "V-WIN-12",
            "V-WIN-13", "V-WIN-14", "V-WIN-15", "V-WIN-16",
            "V-POS-05", "V-EN-01",
        ),
    )
)


def _normalize_identity_fact(name: str) -> str:
    flat = "_".join(tokens(name))
    for norm, syns in IDENTITY_FACT_SYNONYMS.items():
        if flat in syns:
            return norm
    return flat


def _mode_flags(mode_id: str) -> tuple[bool, bool]:
    tok = set(tokens(mode_id))
    is_fresh = bool(tok & FRESH_TOKENS)
    is_reentry = bool(tok & REENTRY_TOKENS)
    if is_reentry:
        is_fresh = False
    return is_fresh, is_reentry


def _window_identity_nodes(doc: Document) -> list[Node]:
    return [
        n
        for n in _claimable_nodes(doc)
        if n.innermost
        and set(tokens(n.innermost)) & WINDOW_REGION_TOKENS
        and set(tokens(n.innermost)) & IDENTITY_REGION_TOKENS
        and isinstance(n.value, dict)
    ]


def _entry_mode_nodes(doc: Document) -> list[Node]:
    return [
        n
        for n in _claimable_nodes(doc)
        if n.innermost
        and set(tokens(n.innermost)) & ENTRY_REGION_TOKENS
        and set(tokens(n.innermost)) & MODE_REGION_TOKENS
    ]


def adapt_window_identity(doc: Document, evidence: EvidenceSet) -> list[WindowIdentityFact]:
    out: list[WindowIdentityFact] = []
    for node in _window_identity_nodes(doc):
        bound: list[str] = []
        for k2, v2 in node.value.items():
            t2 = set(tokens(str(k2)))
            if t2 & BOUND_FACT_FIELD_TOKENS:
                if isinstance(v2, list):
                    bound.extend(_normalize_identity_fact(str(x)) for x in v2 if isinstance(x, str))
                elif isinstance(v2, dict):
                    bound.extend(_normalize_identity_fact(str(x)) for x in v2)
        status = LATEST_ABSENT
        for leaf in walk_leaves(node.value):
            path_tokens = {
                token
                for segment in leaf.segments
                for token in tokens(segment)
            }
            if not (path_tokens & LATEST_SESSION_POSITION_TOKENS):
                continue
            if (
                isinstance(leaf.value, str)
                and normalize_field_name(leaf.value)
                == normalize_field_name(LATEST_SESSION_SAFE_STATUS)
            ):
                if status == LATEST_ABSENT:
                    status = LATEST_PROHIBITED
            elif classify_enablement(leaf.value) in (ENABLED, UNKNOWN):
                # A02 permits no other enabled/unknown latest-session status to
                # establish identity. Ambiguity therefore lands on the failing side.
                status = LATEST_ALLOWED
        if not bound and status == LATEST_ABSENT:
            # correction-003, the zero-anchor rule. The key tokens matched, so
            # this is a CANDIDATE; the A02 decoder derived nothing A02 owns from
            # its direct schema, so it never becomes a claim. Emitting an empty
            # WindowIdentityFact here is what let a failure-case identifier named
            # `missing_or_duplicate_window_id` fail P02 from inside another
            # region. Absence is not silent: a tree with no corroborated block at
            # all still fails P02 with "no window identity block found".
            evidence.add(
                doc.doc_id,
                node.key_path,
                "window_identity_candidate_declined_zero_anchor",
                sorted(str(k) for k in node.value),
            )
            continue
        b_only = tuple(sorted({f for f in bound if f in B_ONLY_IDENTITY_FACTS}))
        a_facts = tuple(sorted({f for f in bound if f not in B_ONLY_IDENTITY_FACTS}))
        evidence.add(doc.doc_id, node.key_path, "identity_block_depth", node.depth)
        out.append(
            WindowIdentityFact(
                source_id=doc.doc_id,
                key_path=node.key_path,
                bound_facts=a_facts,
                b_only_facts=b_only,
                latest_session_pointer_status=status,
            )
        )
    return out


def adapt_entry_modes(doc: Document, evidence: EvidenceSet) -> list[EntryModeFact]:
    out: list[EntryModeFact] = []
    for node in _entry_mode_nodes(doc):
        value = node.value
        if isinstance(value, dict):
            container = "mapping"
        elif isinstance(value, list):
            if value and isinstance(value[0], (list, tuple)):
                container = "list_of_pairs"
            elif value and isinstance(value[0], dict):
                container = "list_of_records"
            else:
                container = "list_of_names"
        else:
            continue
        for mode_id, body in normalize_keyed_collection(value).items():
            is_fresh, is_reentry = _mode_flags(mode_id)
            required: list[str] = []
            predecessor_required = False
            predecessor_match = PREDECESSOR_MATCH_ABSENT
            if isinstance(body, dict):
                for k2, v2 in body.items():
                    t2 = set(tokens(str(k2)))
                    if t2 & BOUND_FACT_FIELD_TOKENS:
                        if isinstance(v2, list):
                            required.extend(
                                _normalize_identity_fact(str(x)) for x in v2 if isinstance(x, str)
                            )
                    if t2 & PREDECESSOR_POSITION_TOKENS:
                        if t2 & REQUIRED_QUALIFIER_TOKENS and classify_enablement(v2) == ENABLED:
                            predecessor_required = True
                        if t2 & MATCH_QUALIFIER_TOKENS and isinstance(v2, str):
                            predecessor_match = v2.strip().lower()
                if any(
                    set(tokens(f)) & PREDECESSOR_POSITION_TOKENS for f in required
                ):
                    predecessor_required = True
            key_path = f"{node.key_path}.{mode_id}"
            evidence.add(doc.doc_id, key_path, f"source_container={container}", mode_id)
            out.append(
                EntryModeFact(
                    source_id=doc.doc_id,
                    key_path=key_path,
                    mode_id=normalize_field_name(mode_id),
                    is_fresh=is_fresh,
                    is_reentry=is_reentry,
                    required_facts=tuple(sorted(set(required))),
                    predecessor_required=predecessor_required,
                    predecessor_match=predecessor_match,
                )
            )
    return out


# --------------------------------------------------------------------------
# A06 / R06 / R08 — provider independence
# --------------------------------------------------------------------------

PROVIDER_ADAPTER = _register(
    AdapterSpec(
        adapter_id="provider_binding.v1",
        produces="ProviderBindingFact",
        applicability=(
            "a selection region (vocabulary.V-PROV-01) whose value slot, directly or "
            "through a declared selection slot (V-PROV-02) or polarity branch "
            "(V-PROV-03), holds a subject"
        ),
        a_trace=("A06", "R06_role_to_model_requirements", "R08_independence_constraints"),
        decision_rule_ids=(
            "V-PROV-01", "V-PROV-02", "V-PROV-03", "V-PROV-04",
            "V-PROV-05", "V-PROV-06", "V-POS-01", "V-POS-02",
            "V-POS-03", "V-POS-04", "V-POL-01", "V-POL-02", "V-EN-01",
        ),
    )
)


def _subject_role(segments: tuple[str, ...]) -> str | None:
    for i, seg in enumerate(segments):
        if set(tokens(seg)) & ROLE_SCOPE_TOKENS and i + 1 < len(segments):
            return normalize_field_name(segments[i + 1])
    return None


def _selector_ancestor(segments: tuple[str, ...]) -> str | None:
    for seg in reversed(segments):
        if set(tokens(seg)) & SELECTOR_REGION_TOKENS:
            return seg
    return None


def _explicit_selector_ancestor(segments: tuple[str, ...]) -> str | None:
    """A selection region whose structure this adapter has claimed.

    A generic `model_route_binding` may contain pointers and receipt schema, so a
    selector subject is not inferred from every descendant. A key explicitly
    declaring selection/choice/policy is different: once claimed, an unknown
    positive slot must become UNSUPPORTED instead of disappearing.
    """
    for seg in reversed(segments):
        tok = set(tokens(seg))
        if tok & SELECTOR_REGION_TOKENS and tok & SELECTION_CONTAINER_TOKENS:
            return seg
    return None


def _is_independence_constraint_segment(segment: str) -> bool:
    """Recognise a constraint without interpreting an opaque role identifier."""
    tok = set(tokens(segment))
    return bool(tok & INDEPENDENCE_POSITION_TOKENS and tok & SELECTOR_REGION_TOKENS)


def _binding_kind(segments: tuple[str, ...], selector_seg: str, value: Any) -> str:
    if is_pointer_key(selector_seg) or is_path_like(value):
        return POINTER_REFERENCE
    if any(is_provenance_segment(s) for s in segments):
        return PROVENANCE_RECORD
    if any(is_descriptive_segment(s) for s in segments):
        return MENTION
    if any(_is_independence_constraint_segment(s) for s in segments):
        return MENTION
    if path_is_negated(segments):
        return NEGATIVE_CONSTRAINT
    if is_schema_meta_key(selector_seg) or any(is_schema_meta_key(s) for s in segments[:-1]):
        return MENTION
    for seg in segments:
        tok = set(tokens(seg))
        if tok & ALLOW_POLARITY_TOKENS:
            return NORMATIVE_SELECTOR
    return NORMATIVE_SELECTOR


def adapt_provider_bindings(doc: Document, evidence: EvidenceSet) -> list[ProviderBindingFact]:
    if doc.fmt != "yaml" or not doc.parsed:
        return []
    out: list[ProviderBindingFact] = []
    seen: set[str] = set()
    for leaf in walk_leaves(doc.data):
        segs = leaf.segments
        if not segs:
            continue
        innermost = segs[-1]
        parent = segs[-2] if len(segs) >= 2 else ""
        label: str | None = None
        selector_seg: str | None = None

        if parent and set(tokens(parent)) & SELECTOR_REGION_TOKENS and leaf.value is True:
            # the key IS the subject and the value marks selection
            selector_seg, label = parent, normalize_field_name(innermost)
        elif (
            set(tokens(innermost)) & SELECTOR_REGION_TOKENS
            and isinstance(leaf.value, str)
            and leaf.value.strip()
        ):
            # the key opens the region, the value is the subject
            selector_seg, label = innermost, normalize_field_name(leaf.value)
        elif (
            set(tokens(innermost)) & SELECTION_SLOT_TOKENS
            and isinstance(leaf.value, str)
            and leaf.value.strip()
        ):
            # the subject sits in a declared selection slot inside a region
            ancestor = _selector_ancestor(segs[:-1])
            if ancestor is None:
                continue
            selector_seg, label = ancestor, normalize_field_name(leaf.value)
        elif leaf.value is True:
            # In an explicitly claimed selection container, a truth-marked key
            # is the opaque subject. No provider vocabulary is consulted.
            ancestor = _explicit_selector_ancestor(segs[:-1])
            if ancestor is None:
                continue
            selector_seg, label = ancestor, normalize_field_name(innermost)
        else:
            continue
        if not label or selector_seg is None:
            continue
        if leaf.key_path in seen:
            continue
        seen.add(leaf.key_path)

        kind = _binding_kind(segs, selector_seg, leaf.value)
        polarity = NEGATIVE if kind == NEGATIVE_CONSTRAINT else POSITIVE
        evidence.add(doc.doc_id, leaf.key_path, f"binding_source_form={selector_seg}", leaf.value)
        out.append(
            ProviderBindingFact(
                source_id=doc.doc_id,
                key_path=leaf.key_path,
                subject=_subject_role(segs),
                selector_kind=kind,
                polarity=polarity,
                provider_label=label,
            )
        )
    return out


def adapt_provider_ambiguities(doc: Document, evidence: EvidenceSet) -> list[UnsupportedFact]:
    """Surface unrecognized positive slots inside a claimed selector schema.

    This is the fail-visible half of C-08. Merely returning no binding would make
    `provider_selection: {target: novel_subject}` a silent pass when `target` was
    not in V-PROV-02. The adapter has claimed the surrounding schema, so it must
    either understand each active leaf or reject the representation.
    """
    if doc.fmt != "yaml" or not doc.parsed:
        return []
    out: list[UnsupportedFact] = []
    seen: set[str] = set()
    for node in _claimable_nodes(doc):
        if not node.innermost:
            continue
        node_tokens = set(tokens(node.innermost))
        if not (
            node_tokens & SELECTOR_REGION_TOKENS
            and node_tokens & SELECTION_CONTAINER_TOKENS
        ):
            continue
        for leaf in walk_leaves(node.value):
            segments = node.segments + leaf.segments
            innermost = leaf.innermost
            parent = leaf.segments[-2] if len(leaf.segments) >= 2 else ""
            recognized = bool(
                set(tokens(innermost)) & SELECTION_SLOT_TOKENS
                or (parent and set(tokens(parent)) & SELECTOR_REGION_TOKENS and leaf.value is True)
                or leaf.value is True
            )
            if recognized:
                continue
            if (
                path_is_negated(segments)
                or any(is_provenance_segment(s) for s in segments)
                or any(is_descriptive_segment(s) for s in segments)
                or any(is_schema_meta_key(s) for s in segments)
                or any(_is_independence_constraint_segment(s) for s in segments)
                or is_pointer_key(innermost)
                or is_path_like(leaf.value)
                or classify_enablement(leaf.value) == DISABLED
            ):
                continue
            key_path = f"{node.key_path}.{leaf.key_path}" if leaf.key_path else node.key_path
            if key_path in seen:
                continue
            seen.add(key_path)
            evidence.add(doc.doc_id, key_path, "unsupported_selector_slot", leaf.value)
            out.append(
                UnsupportedFact(
                    source_id=doc.doc_id,
                    key_path=key_path,
                    reason=(
                        "claimed provider/model selection region contains an "
                        "unrecognized active value slot"
                    ),
                )
            )
    return out


# --------------------------------------------------------------------------
# A09 / R09 — handoff payload
# --------------------------------------------------------------------------

HANDOFF_ADAPTER = _register(
    AdapterSpec(
        adapter_id="handoff_contract.v1",
        produces="DeclarationFact + CarriedFieldFact",
        applicability=(
            "a payload scope (vocabulary.V-HAND-03) or a scope declaring its own "
            "required-field set, at any container depth"
        ),
        a_trace=("A09", "R09_structured_handoff"),
        decision_rule_ids=(
            "V-HAND-01", "V-HAND-02", "V-HAND-03", "V-HAND-04",
            "V-POS-02", "V-POS-05", "V-POS-06", "V-POL-01", "V-EN-01",
        ),
    )
)


def _is_payload_scope(key: str, value: Any) -> bool:
    if set(tokens(key)) & PAYLOAD_SCOPE_TOKENS:
        return True
    if isinstance(value, dict):
        for k in value:
            t = set(tokens(str(k)))
            if t & BOUND_FACT_FIELD_TOKENS:
                return True
    return False


def _carried_field_kind(name: str, value: Any) -> str:
    """Pointer / mutable state / private reasoning / other.

    A REFERENCE to delivery state is a pointer and is exactly what R09 asks a
    handoff to carry; a VALUE of delivery state is the mutable runtime state R09
    forbids.  Fails closed: a pointer-NAMED key whose value is not a path is
    still carried state, so a field cannot be laundered by renaming it `*_ref`.
    """
    tok = set(tokens(name))
    reasoning_like = bool(tok & PRIVATE_REASONING_TOKENS)
    state_like = bool(tok & DELIVERY_STATE_TOKENS)
    if reasoning_like or state_like:
        if is_pointer_key(name) and is_path_like(value):
            return CARRIED_POINTER
        return PRIVATE_REASONING if reasoning_like else MUTABLE_DELIVERY_STATE
    if is_pointer_key(name) or is_path_like(value):
        return CARRIED_POINTER
    return OTHER_CARRIED


def adapt_carried_fields(doc: Document, evidence: EvidenceSet) -> list[CarriedFieldFact]:
    if doc.fmt != "yaml" or not doc.parsed or not isinstance(doc.data, dict):
        return []
    out: list[CarriedFieldFact] = []

    def scan(scope_name: str, scope: Any) -> None:
        """Recurses through mappings AND lists.

        The leaf-and-mapping-only walk could not see a delivery state carried
        inside a list of event records (S31), which is the same state written in
        a different container.
        """
        if isinstance(scope, dict):
            for key, value in scope.items():
                ks = str(key)
                if is_negated(ks) or is_schema_meta_key(ks):
                    continue
                child = f"{scope_name}.{ks}"
                if isinstance(value, (dict, list)):
                    scan(child, value)
                    continue
                out.append(
                    CarriedFieldFact(
                        source_id=doc.doc_id,
                        scope=scope_name,
                        field=normalize_field_name(ks),
                        kind=_carried_field_kind(ks, value),
                        key_path=child,
                    )
                )
        elif isinstance(scope, list):
            for i, item in enumerate(scope):
                scan(f"{scope_name}[{i}]", item)

    for node in _claimable_nodes(doc):
        if not node.innermost:
            continue
        if _is_payload_scope(node.innermost, node.value):
            evidence.add(doc.doc_id, node.key_path, "payload_scope_depth", node.depth)
            scan(node.key_path, node.value)
    return out


#: The ownership scans, by the name `facts.py` gates them under. A refusal is
#: only worth reporting for a scan that would actually have been offered this
#: document — reporting one that never runs here manufactures a coverage hole
#: out of a document the scan has no opinion about.
OWNERSHIP_SCANS = frozenset(
    {
        "entry_mode",
        "provider_ambiguity",
        "carried_field",
        "authority",
        "autonomy",
        # Codex B2: role and window ownership are claims like any other, so a
        # refusal in those channels has to be visible too. Without this a
        # second role source could hide simply by living in a document the
        # evaluator never registered — the gate would refuse it correctly and
        # nobody would hear.
        "role",
        "window",
        # The declaration channel belongs here too. `adapt_declarations` refuses
        # a non-claimable position, but a refusal recorded only in the evidence
        # set is not evaluator-visible: no predicate reads evidence. Without
        # this entry a document whose ONLY claim candidate is a declaration
        # would be refused silently, which is the exact shape of the failure
        # the visible-refusal surface exists to prevent.
        "declaration",
    }
)


def _role_collection_candidate(value: Any) -> bool:
    """Would `adapt_roles` have selected this container?

    The same applicability test the adapter applies — a keyed collection at
    least `ROLE_COLLECTION_MIN_ENTRIES` of whose entries bind a role-defining
    field — evaluated one step before the claim gate, so the refusal report
    cannot drift away from what the adapter actually wanted.
    """
    entries = normalize_keyed_collection(value)
    if not entries:
        return False
    owning = sum(1 for body in entries.values() if _semantic_role_fields(body)[0])
    return owning >= ROLE_COLLECTION_MIN_ENTRIES


def _ownership_locator_wants(position: Node | Leaf, scans: frozenset[str]) -> bool:
    """Would one of the applicable ownership scans have selected this position?

    Used only to decide whether a refusal is worth reporting. It reads the same
    locator conditions the adapters use, so the report cannot drift away from
    what the adapters actually do. Leaves count as well as containers: A13 and
    A14 both claim scalar positions.
    """
    seg = position.innermost
    if not seg:
        return False
    tok = set(tokens(seg))
    if "entry_mode" in scans and tok & ENTRY_REGION_TOKENS and tok & MODE_REGION_TOKENS:
        return True
    if (
        "provider_ambiguity" in scans
        and tok & SELECTOR_REGION_TOKENS
        and tok & SELECTION_CONTAINER_TOKENS
    ):
        return True
    if "carried_field" in scans and _is_payload_scope(seg, position.value):
        return True
    if "authority" in scans and _is_authority_position(seg):
        return True
    if "autonomy" in scans and _autonomy_behaviour(seg) is not None:
        return True
    if (
        "window" in scans
        and tok & WINDOW_REGION_TOKENS
        and tok & IDENTITY_REGION_TOKENS
        and isinstance(position.value, dict)
    ):
        return True
    if "role" in scans and _role_collection_candidate(position.value):
        return True
    # The declaration channel is deliberately absent here. A negated key is not
    # by itself a declaration position: the five declaration forms are consumed
    # at the scope that holds them, so a token scan would flag the inner keys of
    # a record form that was already read correctly one level up. Declaration
    # refusals are reported by `adapt_declaration_refusals`, from what the
    # declaration adapter actually dropped.
    return False


def adapt_structural_refusals(
    doc: Document,
    evidence: EvidenceSet,
    scans: frozenset[str] = OWNERSHIP_SCANS,
) -> list[UnsupportedFact]:
    """Make the fail-closed direction visible instead of an absence.

    A position that a token-level locator would have reached, but which the
    evaluator's structural binding refuses, becomes an UnsupportedFact carrying
    the reason. Without this the correct behaviour and a silent coverage hole
    would look identical from outside, which is the failure mode 00008 named.

    Reported at DOCUMENT level and keyed by the BINDING RULE that produced the
    refusal, never by the payload position. A foreign keyed collection rendered
    as a mapping and as a list of records must produce byte-identical facts, and
    a per-position report would carry list indices into the fact channel and
    break that equivalence.

    Reported: `unknown` and `conflicting` at a position one of the five
    ownership scans wanted — including inside a document that does have a
    profile, because a profile with a hole in it is exactly the case that would
    otherwise look identical to correct silence.

    Not reported: `instance_identity`. The evaluator has described that position
    and said what it is. Nothing is missing, and the collection above it is
    where the owning adapter enumerates from.
    """
    if doc.fmt != "yaml" or not doc.parsed:
        return []
    prov = doc.provenance or UNBOUND
    out: list[UnsupportedFact] = []

    if not prov.bound:
        evidence.add(doc.doc_id, "", "structural_binding", "document_not_bound")

    positions = list(bound_nodes(doc)) + list(bound_leaves(doc))
    wanted = [p for p in positions if _ownership_locator_wants(p, scans)]

    # Two states mean the binding does not describe a position an ownership
    # scan wanted, and both are reported whether or not the document has a
    # profile. `unknown` inside a bound profile is exactly the coverage hole
    # that would otherwise be indistinguishable from correct silence.
    #
    # `instance_identity` is NOT reported: the evaluator has described that
    # position and said what it is, so nothing is missing.
    reasons: dict[str, str] = {}
    for p in wanted:
        if p.role in (UNKNOWN_ROLE, CONFLICTING_ROLE):
            reasons.setdefault(p.role_source, p.role)

    for source in sorted(reasons):
        evidence.add(doc.doc_id, "", "structural_binding", source)
        out.append(
            UnsupportedFact(
                source_id=doc.doc_id,
                key_path="",
                reason=unsupported_reason(reasons[source], source),
            )
        )
    return out


def adapt_declarations(doc: Document, evidence: EvidenceSet) -> list[DeclarationFact]:
    """Prohibition and permission declarations, at declaration positions only.

    T2-SP-UPSTREAM-CM-v2: a negated key sitting inside a foreign keyed-collection
    entry is that entry's own text, not a declaration this system owns. Before
    this gate, `failure_states.some_case.prohibited_x: true` produced a
    DeclarationFact from a region no adapter owns — the same cross-region leak
    correction-003 measured at the other five sites, in the one channel that had
    not been routed through structural provenance yet.
    """
    if doc.fmt != "yaml" or not doc.parsed:
        return []
    prov = doc.provenance or UNBOUND
    out: list[DeclarationFact] = []
    for decl in extract_declarations_recursive(doc.data):
        role, source = prov.resolve(decl.scope_segments)
        if role not in CLAIMABLE_ROLES:
            # Recorded here for a reader, and reported as a decision fact by
            # `adapt_declaration_refusals`. Evidence alone would not do: no
            # predicate reads the evidence set, so a refusal that lived only
            # there would be invisible to the evaluator.
            evidence.add(doc.doc_id, decl.key_path, "declaration_position_refused", role)
            continue
        evidence.add(doc.doc_id, decl.key_path, f"source_form={decl.source_form}", decl.field)
        out.append(
            DeclarationFact(
                source_id=doc.doc_id,
                field=decl.field,
                polarity=decl.polarity,
                key_path=decl.key_path,
            )
        )
    return out


def adapt_declaration_refusals(
    doc: Document, evidence: EvidenceSet
) -> list[UnsupportedFact]:
    """Declaration positions the structural binding refused, as decision facts.

    The declaration channel needs its own refusal surface because a declaration
    candidate is not recognisable from a key token alone: the five declaration
    forms are consumed at the scope that HOLDS them, so scanning for negated
    keys would flag the inner keys of a record form that was already read
    correctly one level up. This function therefore asks the extractor, and
    reports exactly what `adapt_declarations` dropped.

    Reported at document level, keyed by the binding rule that refused, so a
    prohibition written as a mapping and as a list of records produces the same
    fact.
    """
    if doc.fmt != "yaml" or not doc.parsed:
        return []
    prov = doc.provenance or UNBOUND
    reasons: dict[str, str] = {}
    for decl in extract_declarations_recursive(doc.data):
        role, source = prov.resolve(decl.scope_segments)
        if role in CLAIMABLE_ROLES:
            continue
        reasons.setdefault(source, role)
    out: list[UnsupportedFact] = []
    for source in sorted(reasons):
        evidence.add(doc.doc_id, "", "declaration_binding", source)
        out.append(
            UnsupportedFact(
                source_id=doc.doc_id,
                key_path="",
                reason=unsupported_reason(reasons[source], source),
            )
        )
    return out


# --------------------------------------------------------------------------
# A13 / R13 — authority
# --------------------------------------------------------------------------

AUTHORITY_ADAPTER = _register(
    AdapterSpec(
        adapter_id="authority_position.v1",
        produces="AuthorityFact",
        applicability=(
            "a key whose head CONFERS authority (vocabulary.V-AUTH-01). A key that "
            "speaks about authority without conferring it is a descriptive position "
            "and produces evidence only."
        ),
        a_trace=("A13", "R13_no_authority_escalation", "R01_role_contract"),
        decision_rule_ids=(
            "V-AUTH-01", "V-AUTH-02", "V-POS-01", "V-POS-03",
            "V-POL-01", "V-POL-02", "V-EN-01",
        ),
    )
)


def _grant_head(segment: str) -> bool:
    return bool(set(tokens(segment)) & GRANT_HEAD_TOKENS)


def _is_authority_position(segment: str) -> bool:
    """A key that confers authority, either by naming a grant or by double negation.

    `master_write_not_forbidden: true` names no grant head at all, yet it asserts
    exactly the permission it twice denies.  Under the old presence-based polarity
    rule it read as a prohibition and passed (S25).  Parity (vocabulary.V-POL-02)
    makes it an affirmative statement, and an affirmative statement that an action
    is permitted is a grant of that action under A13.
    """
    return _grant_head(segment) or is_double_negated(segment)


def adapt_authority(doc: Document, evidence: EvidenceSet) -> list[AuthorityFact]:
    if doc.fmt != "yaml" or not doc.parsed:
        return []
    out: list[AuthorityFact] = []
    claimed: list[str] = []

    def emit(segments: tuple[str, ...], key_path: str, value: Any) -> None:
        seg = segments[-1] if segments else ""
        # T2-SP-UPSTREAM-CM-v2 retires the body-shape suppression that stood
        # here. correction-003 added `_carries_no_statement` to stop a foreign
        # keyed-collection entry identity from becoming an authority fact, but
        # it read the BODY, so it also demoted a genuine A13 position whose value
        # is an empty container — and V-EN-02 says an empty collection at a
        # genuine enablement position is an explicit DISABLED decision, not an
        # absence. Ownership is now decided structurally before this adapter
        # runs, so the body no longer has to carry that argument and V-EN-02
        # holds again.
        state, where = subtree_enablement(value, AUTHORITY_NON_GRANT_VALUES)
        if is_pointer_key(seg) or is_path_like(value):
            kind = AUTHORITY_REFERENCE
        elif is_descriptive_segment(seg):
            kind = AUTHORITY_DESCRIPTION
        elif is_negated(seg) or path_is_negated(segments[:-1]):
            kind = AUTHORITY_DESCRIPTION
        elif is_schema_meta_key(seg) or any(is_schema_meta_key(s) for s in segments[:-1]):
            kind = AUTHORITY_INPUT
        elif state in (ENABLED, UNKNOWN):
            kind = AUTHORITY_GRANT
        else:
            kind = AUTHORITY_DESCRIPTION
        evidence.add(doc.doc_id, key_path, "authority_raw_value", value)
        out.append(
            AuthorityFact(
                source_id=doc.doc_id,
                key_path=key_path,
                subject=_subject_role(segments),
                kind=kind,
                enablement=state,
                deciding_leaf=where,
            )
        )

    # container grant positions first, so a nested grant is judged as one position
    for node in _claimable_nodes(doc):
        if node.innermost and _is_authority_position(node.innermost):
            claimed.append(node.key_path)
            emit(node.segments, node.key_path, node.value)

    for leaf in _claimable_leaves(doc):
        seg = leaf.innermost
        if not seg or not _is_authority_position(seg):
            continue
        if any(leaf.key_path.startswith(c + ".") or leaf.key_path == c for c in claimed):
            continue
        emit(leaf.segments, leaf.key_path, leaf.value)
    return out


# --------------------------------------------------------------------------
# A14 / R14 — autonomy
# --------------------------------------------------------------------------

AUTONOMY_ADAPTER = _register(
    AdapterSpec(
        adapter_id="autonomy_position.v1",
        produces="AutonomyFact",
        applicability=(
            "a key naming autonomy machinery (vocabulary.V-AUTO-01), or a qualifier "
            "beside a behaviour (V-AUTO-02 + V-AUTO-03). Enablement is read from the "
            "whole subtree, so a nested `{enabled: true}` is enablement."
        ),
        a_trace=("A14", "R14_Human_triggered_progression"),
        decision_rule_ids=(
            "V-AUTO-01", "V-AUTO-02", "V-AUTO-03", "V-POS-01",
            "V-POL-01", "V-POL-02", "V-EN-01",
        ),
    )
)


def _autonomy_behaviour(segment: str) -> str | None:
    tok = set(tokens(segment))
    if tok & AUTONOMY_STANDALONE_TOKENS:
        return "_".join(sorted(tok & AUTONOMY_STANDALONE_TOKENS))
    if tok & AUTOMATION_QUALIFIER_TOKENS and tok & AUTOMATION_BEHAVIOUR_TOKENS:
        return "_".join(sorted(tok & AUTOMATION_BEHAVIOUR_TOKENS))
    return None


def adapt_autonomy(doc: Document, evidence: EvidenceSet) -> list[AutonomyFact]:
    if doc.fmt != "yaml" or not doc.parsed:
        return []
    out: list[AutonomyFact] = []
    claimed: list[str] = []

    def emit(segments: tuple[str, ...], key_path: str, value: Any) -> None:
        seg = segments[-1] if segments else ""
        behaviour = _autonomy_behaviour(seg)
        if behaviour is None:
            return
        if any(is_schema_meta_key(s) for s in segments[:-1]):
            return
        if is_descriptive_segment(seg):
            evidence.add(doc.doc_id, key_path, "autonomy_descriptive_position", value)
            return
        # T2-SP-UPSTREAM-CM-v2 retires the body-shape suppression here for the
        # same reason as A13: it was standing in for an ownership fact the
        # information model did not have, and it cost V-EN-02 to do it. A
        # genuine A14 position holding an empty collection is an explicit
        # disabled decision again.
        state, where = subtree_enablement(value)
        out.append(
            AutonomyFact(
                source_id=doc.doc_id,
                key_path=key_path,
                behaviour=behaviour,
                enablement=state,
                key_is_negated=is_negated(seg) or path_is_negated(segments[:-1]),
                deciding_leaf=where,
            )
        )

    for node in _claimable_nodes(doc):
        if node.innermost and _autonomy_behaviour(node.innermost):
            claimed.append(node.key_path)
            emit(node.segments, node.key_path, node.value)

    for leaf in _claimable_leaves(doc):
        if not leaf.innermost or not _autonomy_behaviour(leaf.innermost):
            continue
        if any(leaf.key_path.startswith(c + ".") or leaf.key_path == c for c in claimed):
            continue
        emit(leaf.segments, leaf.key_path, leaf.value)
    return out


# --------------------------------------------------------------------------
# A11 — no second mutable catalog
# --------------------------------------------------------------------------

CATALOG_ADAPTER = _register(
    AdapterSpec(
        adapter_id="catalog_claim.v1",
        produces="CatalogFact",
        applicability=(
            "a structured collection on the workflow-or-entry surface that either "
            "restates live routing identifiers (detector=restatement) or binds "
            "routing identifier fields on its own entries "
            "(detector=independent_declaration)"
        ),
        a_trace=("A11", "R11_workflow_and_entry_thinness", "R10_existing_mechanism_separation"),
        decision_rule_ids=("V-CAT-01", "V-CAT-02", "V-DISC-02", "V-POS-05"),
    )
)


def live_catalog_identifiers(docs: list[Document]) -> list[str]:
    """Identifiers owned by the live catalog document, read from its own fields."""
    out: set[str] = set()
    for doc in docs:
        if doc.surface != "catalog_owner" or doc.fmt != "yaml" or not doc.parsed:
            continue
        for node in _candidate_nodes(doc):
            value = node.value
            items = value if isinstance(value, list) else [value]
            for item in items:
                if not isinstance(item, dict):
                    continue
                for k, v in item.items():
                    if not (set(tokens(str(k))) & CATALOG_IDENTIFIER_FIELD_TOKENS):
                        continue
                    if isinstance(v, str) and canonical_identifier(v):
                        out.add(v.strip())
    return sorted(out)


def _identifier_entries(node_value: Any) -> int:
    """How many direct entries bind a routing identifier field.

    This is the detector that sees a second catalog every one of whose
    identifiers is unfamiliar (S42).  It reads the SHAPE of an entry, never the
    value bound to it, so an unseen label is detected exactly like a live one.
    """
    items = node_value if isinstance(node_value, list) else list(
        node_value.values()
    ) if isinstance(node_value, dict) else []
    count = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            if not (set(tokens(str(k))) & CATALOG_IDENTIFIER_FIELD_TOKENS):
                continue
            # A pointer names where the catalog lives; it does not bind an entry
            # to an identifier.  `model_route_ref` is a reference, and counting it
            # made a pointer-only role matrix look like a routing catalog.
            if _is_pointer_field(str(k), v):
                continue
            count += 1
            break
    return count


def adapt_catalog_claims(
    doc: Document, identifiers: list[str], evidence: EvidenceSet
) -> list[CatalogFact]:
    out: list[CatalogFact] = []
    canonical = {canonical_identifier(i): i for i in identifiers if canonical_identifier(i)}

    # detector 1: a collection restating live identifiers
    if canonical:
        best: set[str] = set()
        best_forms: list[str] = []
        for group in doc.collections():
            found: set[str] = set()
            for s in group:
                if not isinstance(s, str) or is_path_like(s):
                    continue
                cs = canonical_identifier(s)
                if not cs:
                    continue
                for cid, original in canonical.items():
                    if cid == cs:
                        found.add(original)
            if len(found) > len(best):
                best, best_forms = found, [str(s)[:40] for s in group[:6]]
        if len(best) >= CATALOG_MIN_ENTRIES:
            evidence.add(doc.doc_id, "", "entry_forms", best_forms)
            out.append(
                CatalogFact(
                    source_id=doc.doc_id,
                    catalog_kind="model_catalog",
                    detector=CATALOG_RESTATEMENT,
                    identifiers_restated=tuple(sorted(best)),
                    entry_count=len(best),
                )
            )

    # detector 2: a collection declaring its own routing entries
    if doc.fmt == "yaml" and doc.parsed:
        for node in _candidate_nodes(doc):
            count = _identifier_entries(node.value)
            if count >= CATALOG_MIN_ENTRIES:
                evidence.add(doc.doc_id, node.key_path, "entry_forms", "identifier_bound_entries")
                out.append(
                    CatalogFact(
                        source_id=doc.doc_id,
                        catalog_kind="model_catalog",
                        detector=CATALOG_INDEPENDENT_DECLARATION,
                        identifiers_restated=(),
                        entry_count=count,
                    )
                )
                break
    return out

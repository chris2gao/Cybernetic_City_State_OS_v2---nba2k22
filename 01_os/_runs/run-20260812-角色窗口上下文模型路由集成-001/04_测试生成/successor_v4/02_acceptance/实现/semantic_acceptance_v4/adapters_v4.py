#!/usr/bin/env python3
"""Schema-bound adapters for the v4 coverage extension.

Same contract as `semantic_acceptance.adapters`:

  * each adapter declares its applicability and returns nothing when a document
    does not claim the region.  An unclaimed document is inert;
  * once a region IS claimed, an active shape the adapter cannot interpret is
    emitted as an `UnsupportedFact`, so it becomes a visible P00 rather than a
    silent pass.  That asymmetry is the whole of C-08;
  * container shape never reaches a decision fact.  Every keyed collection goes
    through `core.normalize_keyed_collection`, which reduces mapping,
    list-of-records and list-of-pairs to one dict, so NG-01 holds by
    construction rather than by test;
  * polarity is normalized before judgement, and enablement uses the accepted
    engine's closed NEGATIVE set, so an unrecognised value lands on the failing
    side (NG-07, ST04-V3-IR-008).
"""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from semantic_acceptance.core import (
    DISABLED,
    Document,
    ENABLED,
    UNKNOWN,
    bound_leaves,
    bound_nodes,
    canonical_identifier,
    classify_enablement,
    is_path_like,
    is_pointer_key,
    negation_count,
    normalize_keyed_collection,
    path_is_negated,
    strip_negation,
    subtree_enablement,
    tokens,
    walk_leaves,
    walk_nodes,
)
from semantic_acceptance.decision_facts import EvidenceSet, UnsupportedFact
from semantic_acceptance.vocabulary import DECLARING_SURFACES, SELECTION_SLOT_TOKENS

from .facts_v4 import (
    ContextContractFact,
    ContextLoadEntryFact,
    FailureCaseFact,
    FallbackPositionFact,
    FamilyRequirementFact,
    FreshnessBindingFact,
    FreshnessTriggerFact,
    IndependenceFact,
    LifecycleConditionFact,
    LifecycleFact,
    MechanismSeparationFact,
    PreloadPositionFact,
    RouteReceiptFact,
)
from . import vocabulary_v4 as V

# --------------------------------------------------------------------------
# shared structural helpers
# --------------------------------------------------------------------------


def _applicable(doc: Document) -> bool:
    """Declared applicability, shared by every adapter in this module.

    YAML only, parsed, mapping at the root, and on a surface that declares
    semantics. A markdown document contributes no v4 decision facts; that is a
    stated boundary, not an oversight, and it is why an unclaimed document is
    inert rather than silently compliant.
    """
    return (
        doc.fmt == "yaml"
        and doc.parsed
        and isinstance(doc.data, dict)
        and doc.surface in DECLARING_SURFACES
    )


def _seg_tokens(segment: str) -> set[str]:
    return set(tokens(segment))


def _path_tokens(key_path: str) -> set[str]:
    out: set[str] = set()
    for seg in key_path.split("."):
        out |= _seg_tokens(seg)
    return out


def _claim_sites(doc: Document) -> list[Any]:
    """The only traversal a v4 adapter may use to PICK a claim site.

    T2-PARENT-IR-001. `bound_nodes` says this in its own docstring, and the
    accepted adapters obey it through `_claimable_nodes`; the v4 adapters used
    raw `walk_nodes` and so chose claim sites by key-token intersection alone,
    with no reference to the evaluator's structural binding. The independent
    review demonstrated the consequence: rewriting `failure_states` into the
    admitted single-entry-mapping form exposes the failure-case instance
    identity `missing_or_stale_route_receipt` as a route-receipt region, and
    P24 moves pass -> fail on a representation change that changes nothing.

    Only `declaration_name` positions are claimable. An `instance_identity`, an
    unresolved position and a conflicting binding all fail closed here, which is
    correction-003's evaluator-owned coordinate applied where v4 makes its
    claims rather than only where the accepted engine makes its own.

    `walk_nodes` remains correct for structural sub-scans INSIDE a value that
    has already been claimed, and those uses are left alone.
    """
    return [n for n in bound_nodes(doc) if n.structurally_claimable]


def _claim_leaves(doc: Document) -> list[Any]:
    """Scalar claim sites, gated the same way as `_claim_sites`.

    Several v4 adapters select a fact because a LEAF's key matches semantic
    vocabulary. That is the same act of choosing a claim site as selecting a
    container, so it obeys the same rule.
    """
    return [lf for lf in bound_leaves(doc) if lf.structurally_claimable]


def _regions(doc: Document, region_tokens: Iterable[str]) -> Iterator[Any]:
    """Yield every claimable node whose innermost segment claims the region."""
    want = set(region_tokens)
    for node in _claim_sites(doc):
        innermost = node.segments[-1] if node.segments else ""
        if _seg_tokens(innermost) & want:
            yield node


def _regions_with_parent(doc: Document, region_tokens: Iterable[str]) -> Iterator[tuple[Any, Any]]:
    """Yield (parent_mapping, node) for every node whose key claims the region.

    The parent is needed because a region-level effect is a SIBLING of the
    region, not a child of it: `invalidation_conditions: [...]` sits beside
    `stale_effect: fail_closed`, both under `lifecycle`. Yielding the region
    alone loses the effect and reports every compliant entry as UNKNOWN.

    T2-PARENT-IR-001: the parent scan below is a structural sub-scan and may use
    `walk_nodes`, but the node actually YIELDED is a claim site and is taken from
    `_claim_sites`, so an instance identity or an unbound position cannot become
    a region here either.
    """
    want = set(region_tokens)
    claimable = {id(n.value): n for n in _claim_sites(doc)}
    containers: list[Any] = [doc.data]
    for node in walk_nodes(doc.data):
        if isinstance(node.value, dict):
            containers.append(node.value)
    for parent in containers:
        for key in parent:
            if not (_seg_tokens(str(key)) & want):
                continue
            claimed = claimable.get(id(parent[key]))
            if claimed is not None:
                yield parent, claimed


class _RootNode:
    """A node view for a top-level key, which `walk_nodes` reports at depth one."""

    def __init__(self, key: str, value: Any) -> None:
        self.segments = (key,)
        self.key_path = key
        self.value = value
        self.innermost = key


def _subregion(
    node: Any,
    position_tokens: Iterable[str],
    not_under: Iterable[Iterable[str]] = (),
) -> Any | None:
    """The first descendant of `node` occupying one of the given structural positions.

    `not_under` names sibling structural positions this search must not descend
    THROUGH. V4-FND-04-b, second corrected root cause: `LOAD_SET_REGION_TOKENS`
    contains the bare token `set`, and a conforming contract may reasonably
    declare `derivation_inputs.approved_reference_set` as a structured record
    rather than the scalar `required`. The unrestricted search then found that
    record first, claimed it as the derived load set, and emitted a REQUIREMENT
    leaf (`...approved_reference_set.source`) as a load ENTRY with exact=false —
    failing a conforming candidate on A04.

    Measured before the fix, on baseline_v4 with that one field expanded:
    P22 pass -> fail, with `minimum_effective_context.derivation_inputs.
    approved_reference_set.source` reported as a non-exact load entry.

    A region locator that reaches inside a different declared region of the same
    contract is over-broad by construction, not by bad luck with one token: any
    token shared between two locators reproduces it. Terminating descent at a
    sibling region is the structural fix; narrowing the token list would only
    move the collision.
    """
    want = set(position_tokens)
    barriers = [set(t) for t in not_under]
    if not isinstance(node.value, (dict, list)):
        return None
    base_depth = len(node.key_path.split(".")) if node.key_path else 0
    for child in walk_nodes(node.value, key_path=node.key_path):
        segments = child.key_path.split(".")[base_depth:]
        if barriers and any(
            _seg_tokens(seg) & barrier for seg in segments[:-1] for barrier in barriers
        ):
            continue
        if _seg_tokens(child.innermost) & want:
            return child
    return None


def _value_tokens(value: Any) -> set[str]:
    """Every token appearing in a value, at any depth, as a set."""
    out: set[str] = set()
    if isinstance(value, str):
        return set(tokens(value))
    if isinstance(value, dict):
        for k, v in value.items():
            out |= _seg_tokens(str(k)) | _value_tokens(v)
        return out
    if isinstance(value, list):
        for item in value:
            out |= _value_tokens(item)
        return out
    if value is not None:
        out |= set(tokens(str(value)))
    return out


# --------------------------------------------------------------------------
# V4-FND-02 / ruling F02-A_WITH_CONSTRAINTS: parity, not presence
# --------------------------------------------------------------------------
#
# The v4 matchers were already whole-token, not substring: `_seg_tokens` calls
# the accepted `tokens()`, so ST04-V3-IR-005's "source inside resource" cannot
# happen here. What they did not do is read NEGATION.
# `tokens("not_prohibited")` is ['not', 'prohibited'], the intersection with a
# rejection vocabulary is non-empty, and a document PERMITTING self-review was
# scored as rejecting it.
#
# The accepted engine already has the rule - `negation_count`, `is_negated`,
# `strip_negation`, `path_is_negated`, and V-POL-02's "parity, not presence".
# It applies it to KEY names. These two helpers apply the same accepted rule to
# VALUES, by composition. No vendored byte changes.

ASSERTED, INVERTED, ABSENT = "asserted", "inverted", "absent"


def _vocabulary_assertion(value: Any, vocabulary: Iterable[str]) -> str:
    """Does `value` assert a term of `vocabulary`, deny one, or neither?

    Returns ASSERTED for an even negation count, INVERTED for an odd one, and
    ABSENT when no term of the vocabulary appears at all.  ABSENT is not
    "denied": a caller that needs the difference between "said no" and "said
    nothing" gets it, because absence is never a pass.
    """
    want = set(vocabulary)
    if isinstance(value, str):
        toks = tokens(value)
        if not (set(toks) & want):
            return ABSENT
        # Parity counts MODIFYING negations only. Most rejection vocabularies
        # overlap the negation-token set - "prohibited" is both the term being
        # matched and a negation marker - so counting every negation token would
        # read the plain word "prohibited" as a negation of itself. Excluding the
        # matched terms is what makes "prohibited" asserted, "not_prohibited"
        # inverted, and "never_not_prohibited" asserted again.
        modifiers = [t for t in toks if t not in want]
        n = sum(1 for t in modifiers if negation_count(t))
        return INVERTED if n % 2 == 1 else ASSERTED
    if isinstance(value, dict):
        for k, v in value.items():
            inner = _vocabulary_assertion(v, want)
            if inner != ABSENT:
                # A negated key negates its own subtree, the accepted
                # `path_is_negated` rule read one level down.
                if negation_count(str(k)) % 2 == 1:
                    return INVERTED if inner == ASSERTED else ASSERTED
                return inner
            if set(tokens(str(k))) & want:
                return INVERTED if negation_count(str(k)) % 2 == 1 else ASSERTED
        return ABSENT
    if isinstance(value, list):
        for item in value:
            inner = _vocabulary_assertion(item, want)
            if inner != ABSENT:
                return inner
        return ABSENT
    if value is None:
        return ABSENT
    return _vocabulary_assertion(str(value), want)


def _enablement_with_parity(value: Any) -> str:
    """`classify_enablement`, with the accepted parity rule applied to values.

    The accepted classifier is a closed NEGATIVE set over the value string, and
    that is correct: an unrecognised value must land on the failing side
    (ST04-V3-IR-008, -010). But it reads the whole string, so `not_permitted`
    is unrecognised and therefore ENABLED - a prohibition read as a permission.

    Parity fixes it without weakening the closed-negative policy: strip the
    negation markers, classify the FIELD the value is about with the accepted
    classifier, then invert once per odd parity. An unrecognised base value is
    still ENABLED, so an unfamiliar spelling is still not trusted.
    """
    if isinstance(value, str):
        toks = tokens(value)
        negations = [t for t in toks if negation_count(t)]
        rest = [t for t in toks if not negation_count(t)]
        if negations and rest:
            # A negation modifying a base term: classify the base with the
            # accepted classifier, then invert once per odd parity.
            state = classify_enablement("_".join(rest))
            if len(negations) % 2 == 0:
                return state
            if state == ENABLED:
                return DISABLED
            if state == DISABLED:
                return ENABLED
            return UNKNOWN
        # No base term to modify - the value IS the negative word, or a stack of
        # them. The accepted closed-negative classifier already decides this
        # correctly: "prohibited" is in its negative set, "not_prohibited" is
        # not and therefore lands on the failing side.
    return classify_enablement(value)


def _role_of(name: str, role_map: dict[str, frozenset[str]]) -> str:
    """Map a declared identifier onto a normalized role, or "" when unmapped.

    Unmapped is a real outcome, not a dropped one: every caller records the
    unmapped count so that an unrecognised declaration stays visible instead of
    quietly reducing the covered set.

    T2-PARENT-IR-003: this was a plain token-set intersection, so `not_stale`
    matched the `stale` role and an inverted declaration produced the positive
    role. Ruling F02-A requires every v4 polarity-bearing vocabulary decision to
    go through whole-token negation parity, and this is one of the two functions
    every such decision passes through. An INVERTED assertion returns unmapped,
    which is already a real outcome every caller counts; it is never the role.
    """
    for role, synonyms in role_map.items():
        assertion = _vocabulary_assertion(name, synonyms)
        if assertion == ASSERTED:
            return role
        if assertion == INVERTED:
            return ""
    return ""


def _effect_value(value: Any) -> Any:
    """The effect attached to a named condition, written either way.

    `trigger: fresh_read` and `trigger: {effect: fresh_read}` are the same
    declaration; the container may not decide.
    """
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            if _seg_tokens(str(child_key)) & set(V.EFFECT_FIELD_TOKENS):
                return child_value
        return value
    return value


def _region_default_effect(container: Any) -> Any:
    """The effect a region declares once for all of its entries.

    V4-FRESH-09. `conditions: [a, b]` beside `stale_effect: fail_closed` declares
    the same thing as a per-entry effect on each of a and b. Reading only the
    per-entry form makes the compliant list form fail, which is the container
    bias ST04-V3-IR-003 named.
    """
    if not isinstance(container, dict):
        return None
    want = set(V.DEFAULT_EFFECT_POSITION_TOKENS)
    qualifiers = set(V.DEFAULT_EFFECT_QUALIFIER_TOKENS)
    canonical_want = {canonical_identifier(w) for w in want}

    # Exact canonical match first. `effect`, `on_failure` and `outcome` are
    # unambiguous and must win over any token-level match.
    for key, value in container.items():
        if canonical_identifier(str(key)) in canonical_want:
            return value

    # Then an effect token qualified only by V4-FRESH-10 qualifiers, so
    # `stale_effect` matches and `authority_effect` does not.
    for key, value in container.items():
        tok = _seg_tokens(str(key))
        if not (tok & want):
            continue
        if tok <= (want | qualifiers):
            return value
    return None


def _effect_role(effect: Any, role_map: dict[str, frozenset[str]]) -> str:
    """The normalized role a declared effect maps onto, or "" when unmapped.

    T2-PARENT-IR-003: this read a flat deep token set, so `not_changed`
    normalized to `changed` and `not_fail_closed` to the compliant
    `stale_status`. `_observation_role` and `_consequence_role` both delegate
    here, so parity applied once here covers every v4 observation and
    consequence decision. An INVERTED assertion is never the positive role.
    """
    for role, synonyms in role_map.items():
        assertion = _vocabulary_assertion(effect, synonyms)
        if assertion == ASSERTED:
            return role
        if assertion == INVERTED:
            return ""
    return ""


# --------------------------------------------------------------------------
# A03 / R03_window_lifecycle
# --------------------------------------------------------------------------


def adapt_lifecycle(doc: Document, ev: EvidenceSet) -> list[LifecycleFact]:
    if not _applicable(doc):
        return []
    out: list[LifecycleFact] = []
    for node in _regions(doc, V.LIFECYCLE_REGION_TOKENS):
        states = _subregion(node, V.LIFECYCLE_STATE_REGION_TOKENS)
        target = states if states is not None else node
        collection = normalize_keyed_collection(target.value)
        if not collection:
            continue
        node = target
        roles: list[str] = []
        unmapped = 0
        for state_name in collection:
            role = _role_of(str(state_name), V.LIFECYCLE_STATE_ROLES)
            if role:
                roles.append(role)
            else:
                unmapped += 1
        ev.add(doc.doc_id, node.key_path, "source_container=lifecycle_collection", type(node.value).__name__)
        out.append(
            LifecycleFact(
                source_id=doc.doc_id,
                key_path=node.key_path,
                state_roles=tuple(sorted(set(roles))),
                declared_state_count=len(collection),
                unmapped_state_count=unmapped,
            )
        )
    return out


SLOT_SUBJECT, SLOT_OBSERVATION, SLOT_CONSEQUENCE = "subject", "observation", "consequence"


def _slot_value(record: Any, slot_tokens: Iterable[str]) -> Any:
    """The value a structured condition declares in one named slot position.

    Returns `None` when the record does not occupy that position at all. A slot
    that is present but empty is NOT the same as an absent slot and is reported
    as unresolved by the caller, because "declared and blank" is a hole the
    author can see and "never declared" is one they cannot.
    """
    if not isinstance(record, dict):
        return None
    want = set(slot_tokens)
    for key, value in record.items():
        if _seg_tokens(str(key)) & want:
            return value
    return None


#: Distinguishes "declared as nothing" from "not declared at all". `None` is a
#: value an author can write and must not be read as absence.
_ABSENT = object()


def _value_at_key_tokens(container: Any, want: set[str]) -> Any:
    """The complete value declared at the first position whose key claims `want`.

    Returns `_ABSENT` when no such position exists. A structural sub-scan inside
    an already-claimed region, so raw descent is correct here; what it must not
    do is flatten, because the whole point is to hand back the declaration as
    written - list, mapping or scalar alike.
    """
    if isinstance(container, dict):
        for key, value in container.items():
            if _seg_tokens(str(key)) & want:
                return value
        for value in container.values():
            found = _value_at_key_tokens(value, want)
            if found is not _ABSENT:
                return found
    elif isinstance(container, list):
        for item in container:
            found = _value_at_key_tokens(item, want)
            if found is not _ABSENT:
                return found
    return _ABSENT


def _declared_elements(value: Any) -> list[Any]:
    """One declaration read as its elements. A scalar is a single element.

    T2-PARENT-SR-001: a policy is not always one word. `[fail_closed, best_effort]`
    is one declaration containing two, and reading it as an undivided blob lets the
    compliant half speak for the whole.
    """
    if isinstance(value, list):
        return list(value)
    if isinstance(value, dict):
        return list(value.values())
    return [value]


def _complete_effect_role(effect: Any, role_map: dict[str, frozenset[str]]) -> str:
    """The role a declaration asserts, or "" when it does not assert exactly one.

    T2-PARENT-SR-001. `_effect_role` returns on the FIRST role a value asserts,
    which is correct for a single declared effect and wrong for a composite one:
    `[fail_closed, best_effort]` resolved to the compliant role and passed, even
    though the same declaration permits the behaviour A12 forbids.

    Every element must independently resolve, and to the same role. An element
    that resolves to nothing - unknown, unrecognised, or inverted - makes the
    whole declaration unresolved, and so does a genuine disagreement between two
    recognised roles. Order cannot matter, because a set is compared rather than
    a first hit. No spelling is enumerated anywhere in this function.
    """
    elements = _declared_elements(effect)
    if not elements:
        return ""
    roles: set[str] = set()
    for element in elements:
        role = _effect_role(element, role_map)
        if not role:
            return ""
        roles.add(role)
    return roles.pop() if len(roles) == 1 else ""


def _observable_positions(doc: Document) -> set[str]:
    """Every position this document itself declares as observable.

    T2-PARENT-IR-004. Mapping keys, and the identifier-like scalar values a
    document lists as its own bound facts or required reads, are things a
    machine can go and look at. A string that appears ONLY inside a subject slot
    is not one of them, so subject slots are excluded from the set they would
    otherwise vouch for themselves with.

    This is not a subject vocabulary. Nothing here is a list of blessed subject
    words; the question asked is only whether the named position exists in the
    candidate, which is why an arbitrary sentence fails and a real field passes
    no matter what either of them is called.
    """
    exclude = set(V.CONDITION_SUBJECT_SLOT_TOKENS)
    out: set[str] = set()
    for node in walk_nodes(doc.data):
        if node.segments:
            out.add(canonical_identifier(str(node.segments[-1])))
    for leaf in walk_leaves(doc.data):
        seg = str(leaf.segments[-1]) if leaf.segments else ""
        if _seg_tokens(seg) & exclude:
            continue
        if seg:
            out.add(canonical_identifier(seg))
        if isinstance(leaf.value, str) and leaf.value and " " not in leaf.value.strip():
            out.add(canonical_identifier(leaf.value))
    out.discard("")
    return out


def _resolves_ordered_path(doc: Document, parts: list[str]) -> bool:
    """Walk the document by the exact ordered components of a dotted subject.

    T2-PARENT-SR-002. The previous test asked only whether each component name
    occurred SOMEWHERE in the document, which is a bag and not a path. The
    baseline declares `context_binding.dependency_fingerprints` and separately
    `model_route_binding.route_receipt`, so the bag accepted the invented
    `context_binding.route_receipt`, and accepted it reversed too.

    A path resolves only by descending: each component must be a key of the
    mapping the previous component reached, or - for the final component only -
    a declared entry of the list it reached. Anything spliced, reversed or
    dangling stops the walk. No component is compared with a vocabulary; the
    walk either arrives somewhere real or it does not.

    The walk is done over the document's BOUND traversal rather than over the raw
    mapping. That is what makes it independent of representation and of transparent
    wrappers at once: `bound_nodes` and `bound_leaves` already report each position
    by the segment path with declared transparent containers removed, which is the
    same coordinate the structural binding's own selectors are matched against.
    Walking `doc.data` by hand instead re-derived that reduction badly, and the
    inherited I03 list-of-pairs variant and the reviewer's S02 transparent window
    wrapper each caught a different half of it.
    """
    want = tuple(canonical_identifier(p) for p in parts)

    for node in bound_nodes(doc):
        if tuple(canonical_identifier(str(s)) for s in node.segments) == want:
            return True

    for leaf in bound_leaves(doc):
        segments = tuple(canonical_identifier(str(s)) for s in leaf.segments)
        if segments == want:
            return True
        # A terminal component may name a declared ENTRY of the list at the
        # parent path, which is how `bound_facts` and `required_fields` state
        # their members. The parent path must still match exactly.
        if (
            segments == want[:-1]
            and isinstance(leaf.value, str)
            and canonical_identifier(leaf.value) == want[-1]
        ):
            return True

    return False


def _subject_is_machine_bound(doc: Document, subject: Any) -> bool:
    """Does the declared subject resolve to a position the candidate declares?

    Ruling F03-D requires a machine-observable subject or binding and states
    `arbitrary_prose_is_deterministic: false`. The previous test was
    `bool(subject) and bool(_value_tokens(subject))` - any non-empty string -
    which the independent review broke with
    `whatever_the_operator_feels_has_drifted_enough`.

    A subject resolves when its canonical form names a declared position, or
    when every component of a dotted path does. Unknown, dangling and
    subjective bindings do not resolve and are non-pass.
    """
    if subject is None:
        return False
    if isinstance(subject, dict):
        return any(_subject_is_machine_bound(doc, v) for v in subject.values())
    if isinstance(subject, list):
        return any(_subject_is_machine_bound(doc, v) for v in subject)
    text = str(subject).strip()
    if not text:
        return False
    parts = [p for p in text.split(".") if p]
    if len(parts) > 1:
        return _resolves_ordered_path(doc, parts)
    return canonical_identifier(text) in _observable_positions(doc)


def _condition_definitions(container: Any) -> dict[str, Any]:
    """Explicit structured definitions a bare-string condition may resolve to.

    Read from the lifecycle region's own definition position. Every admitted
    container shape reaches the same mapping through the accepted
    `normalize_keyed_collection`, so a definitions block written as a mapping,
    a list of records or a list of pairs are the same declaration.
    """
    if not isinstance(container, dict):
        return {}
    want = set(V.CONDITION_DEFINITION_REGION_TOKENS)
    for key, value in container.items():
        if _seg_tokens(str(key)) & want:
            return normalize_keyed_collection(value)
    return {}


def _observation_role(value: Any) -> str:
    """The normalized observation role a declared comparison maps onto, or "".

    Unknown maps to "", and "" is never deterministic. This is the inversion
    ruling F03-D turns on: the old closed NEGATIVE vocabulary made unknown mean
    deterministic, and rejected option F03-A would have made an unknown SUBJECT
    mean non-deterministic while an unknown comparison still passed.
    """
    if value is None:
        return ""
    return _effect_role(value, V.CONDITION_OBSERVATION_ROLES)


def _consequence_role(value: Any) -> str:
    """Slot 3, read through the accepted A05 effect roles.

    A R03's "stale" consequence and A R05's freshness effects are the same
    typed outcome, so the same role map decides both rather than a second
    vocabulary that would drift from it. `continue_cached` is a recognised role
    and deliberately NOT a compliant one: a condition whose declared consequence
    is to carry on from cache is fully understood and still fails.
    """
    if value is None:
        return ""
    return _effect_role(value, V.FRESHNESS_EFFECT_ROLES)


def adapt_lifecycle_conditions(doc: Document, ev: EvidenceSet) -> list[LifecycleConditionFact]:
    """A03/R03 continuation conditions, as typed determinism facts (F03-D).

    A condition is deterministic only when all three slots resolve:

      1. a machine-observable subject / binding,
      2. an explicit observable change or comparison,
      3. the required stale / fresh-read lifecycle consequence.

    The subject is read VERBATIM out of its declared position and is never
    compared with a vocabulary; what makes it machine-observable is that the
    author named it in a subject position, or that a bare string resolves to a
    structured definition which does. Comparing the subject against a blessed
    word list is rejected option F03-A and is not done here.

    Representation is free. Mapping, list-of-records, list-of-pairs and
    list-of-single-entry mappings reach this function as the same collection
    through the accepted `normalize_keyed_collection`, and slot 3 may be declared
    once for the whole region. What is not free is declaring nothing: a bare
    string with no structured definition leaves slots 1 and 2 unresolved and is
    reported non-deterministic with those slot names attached.
    """
    if not _applicable(doc):
        return []
    out: list[LifecycleConditionFact] = []
    for node in _regions(doc, V.LIFECYCLE_REGION_TOKENS):
        region = _subregion(node, V.FRESHNESS_TRIGGER_REGION_TOKENS)
        if region is None:
            continue
        region_container = node.value if isinstance(node.value, dict) else None
        region_default_effect = _region_default_effect(region_container)
        definitions = _condition_definitions(region_container)

        collection = normalize_keyed_collection(region.value)
        items: list[tuple[str, Any]] = list(collection.items())
        if not items and isinstance(region.value, list):
            items = [(str(i), v) for i, v in enumerate(region.value)]

        for name, value in items:
            record = value if isinstance(value, dict) else None
            # A bare string is admitted only by resolving to an explicit
            # structured definition. Nothing is read out of its own spelling.
            if record is None or not (
                _slot_value(record, V.CONDITION_SUBJECT_SLOT_TOKENS) is not None
                or _slot_value(record, V.CONDITION_OBSERVATION_SLOT_TOKENS) is not None
            ):
                resolved = definitions.get(str(name))
                if isinstance(resolved, dict):
                    record = resolved

            subject = _slot_value(record, V.CONDITION_SUBJECT_SLOT_TOKENS)
            subject_resolved = _subject_is_machine_bound(doc, subject)

            observation_role = _observation_role(
                _slot_value(record, V.CONDITION_OBSERVATION_SLOT_TOKENS)
            )

            consequence_declared = _effect_value(value) if record is not None else None
            consequence_role = _consequence_role(
                _slot_value(record, V.EFFECT_FIELD_TOKENS)
                if _slot_value(record, V.EFFECT_FIELD_TOKENS) is not None
                else (consequence_declared if isinstance(consequence_declared, (str, dict, list)) else None)
            )
            if not consequence_role:
                consequence_role = _consequence_role(region_default_effect)

            unresolved: list[str] = []
            if not subject_resolved:
                unresolved.append(SLOT_SUBJECT)
            if not observation_role:
                unresolved.append(SLOT_OBSERVATION)
            if consequence_role not in set(V.COMPLIANT_FRESHNESS_EFFECTS):
                unresolved.append(SLOT_CONSEQUENCE)

            ev.add(doc.doc_id, f"{region.key_path}.{name}", "source_form=lifecycle_condition", value)
            out.append(
                LifecycleConditionFact(
                    source_id=doc.doc_id,
                    key_path=f"{region.key_path}.{name}",
                    deterministic=not unresolved,
                    subject_resolved=subject_resolved,
                    observation_role=observation_role,
                    consequence_role=consequence_role,
                    unresolved_slots=tuple(unresolved),
                )
            )
    return out


# --------------------------------------------------------------------------
# A04 / R04_minimum_effective_context
# --------------------------------------------------------------------------


def _normalize_field_mapping(node_value: Any) -> list[str]:
    """The FIELD NAMES of a field-to-value record, across every admitted shape.

    V4-FND-04-b, corrected root cause. `normalize_keyed_collection` is the right
    primitive for a keyed collection of ENTITIES: it lets a record declare its
    own identity through `COLLECTION_ID_FIELD_TOKENS`, so `[{id: a}, {id: b}]`
    keys by `a` and `b`. `derivation_inputs` is not that. It is a mapping from a
    field NAME to a value, and `role_id` — the very name A R04 asks for — is an
    id-field token. So `[{role_id: required}]` was normalized to an entity keyed
    `required`, the field name was consumed as an identity carrier, and the
    `role` input role vanished while the other four survived because their names
    are not id-field tokens. That asymmetry was the finding's open question and
    this is its whole answer.

    The fix is not to stop normalizing container shape; it is to normalize the
    shape a FIELD MAPPING actually has. The same four admitted shapes reduce to
    the same field names here as they do there, minus the entity-identity rule
    that does not apply to a field mapping:

        {a: v, b: v}          mapping
        [{a: v}, {b: v}]      list of single-entry mappings
        [[a, v], [b, v]]      list of pairs
        [a, b]                list of bare field names

    A multi-key record inside the list keeps every key, because in a field
    mapping each key IS a field.
    """
    if isinstance(node_value, dict):
        return [str(k) for k in node_value]
    if isinstance(node_value, str):
        return [node_value]
    if not isinstance(node_value, list):
        return []
    names: list[str] = []
    for item in node_value:
        if isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[0], str):
            names.append(item[0])
        elif isinstance(item, dict):
            names.extend(str(k) for k in item)
        elif isinstance(item, str):
            names.append(item)
    return names


def adapt_context_contract(doc: Document, ev: EvidenceSet) -> list[ContextContractFact]:
    if not _applicable(doc):
        return []
    out: list[ContextContractFact] = []
    for node in _regions(doc, V.CONTEXT_REGION_TOKENS):
        region = _subregion(node, V.DERIVATION_INPUT_REGION_TOKENS)
        if region is None:
            continue
        names = _normalize_field_mapping(region.value)
        if not names:
            continue
        roles = {r for r in (_role_of(n, V.CONTEXT_DERIVATION_INPUT_ROLES) for n in names) if r}
        ev.add(doc.doc_id, region.key_path, "source_container=context_inputs", type(region.value).__name__)
        out.append(
            ContextContractFact(
                source_id=doc.doc_id,
                key_path=region.key_path,
                input_roles=tuple(sorted(roles)),
            )
        )
    return out


def _entry_is_exact(text: str) -> bool:
    """A R04: exact paths/versions or hashes where material.

    A wildcard marker makes an entry unbounded regardless of anything else. An
    entry carrying a version or hash marker is exact. A concrete path with no
    wildcard is already exact — A asks for exactness, not for a hash on every
    line.
    """
    for marker in V.UNBOUNDED_PATH_MARKERS:
        if marker in text:
            return False
    if text.endswith("/"):
        return False
    if _seg_tokens(text) & set(V.EXACTNESS_MARKER_TOKENS):
        return True
    return is_path_like(text)


def adapt_context_load_entries(doc: Document, ev: EvidenceSet) -> list[ContextLoadEntryFact]:
    if not _applicable(doc):
        return []
    out: list[ContextLoadEntryFact] = []
    historical = set(V.HISTORICAL_PRELOAD_TOKENS)
    excluded = set(V.EXCLUDED_CONTEXT_TOKENS)
    # A nested region can be claimed twice — `minimum_effective_context` and its
    # own `load_set` child both carry a context token — and would then emit the
    # same entry twice. A duplicated fact is not wrong, but a count a reviewer
    # cannot reconcile against the document is evidence they have to re-derive.
    seen_entries: set[str] = set()
    for node in _regions(doc, V.CONTEXT_REGION_TOKENS):
        region = _subregion(
            node,
            V.LOAD_SET_REGION_TOKENS,
            not_under=(V.DERIVATION_INPUT_REGION_TOKENS,),
        )
        if region is None:
            continue
        entries: list[tuple[str, str]] = []
        if isinstance(region.value, list):
            for i, item in enumerate(region.value):
                if isinstance(item, str):
                    entries.append((f"{region.key_path}[{i}]", item))
                elif isinstance(item, dict):
                    for k, v in item.items():
                        if isinstance(v, str):
                            entries.append((f"{region.key_path}[{i}].{k}", v))
        elif isinstance(region.value, dict):
            for leaf in walk_leaves(region.value, key_path=region.key_path):
                if isinstance(leaf.value, str):
                    entries.append((leaf.key_path, leaf.value))
        for key_path, text in entries:
            if key_path in seen_entries:
                continue
            seen_entries.add(key_path)
            tok = _seg_tokens(text)
            ev.add(doc.doc_id, key_path, "source_form=load_entry", text)
            out.append(
                ContextLoadEntryFact(
                    source_id=doc.doc_id,
                    key_path=key_path,
                    exact=_entry_is_exact(text),
                    historical_region=bool(tok & historical),
                    excluded_material=bool(tok & excluded),
                )
            )
    return out


def adapt_preload_positions(doc: Document, ev: EvidenceSet) -> list[PreloadPositionFact]:
    if not _applicable(doc):
        return []
    out: list[PreloadPositionFact] = []
    behaviour = set(V.PRELOAD_BEHAVIOUR_TOKENS)
    for node in _claim_sites(doc):
        if not (_seg_tokens(node.innermost) & behaviour):
            continue
        enablement, leaf = subtree_enablement(node.value)
        negated = path_is_negated(node.segments)
        ev.add(doc.doc_id, node.key_path, "source_form=preload_position", node.value)
        out.append(
            PreloadPositionFact(
                source_id=doc.doc_id,
                key_path=node.key_path,
                enablement=enablement,
                key_is_negated=negated,
                deciding_leaf=leaf,
            )
        )
    for leaf in _claim_leaves(doc):
        if not (_seg_tokens(leaf.segments[-1] if leaf.segments else "") & behaviour):
            continue
        if any(f.key_path == leaf.key_path for f in out):
            continue
        ev.add(doc.doc_id, leaf.key_path, "source_form=preload_leaf", leaf.value)
        out.append(
            PreloadPositionFact(
                source_id=doc.doc_id,
                key_path=leaf.key_path,
                enablement=_enablement_with_parity(leaf.value),
                key_is_negated=path_is_negated(leaf.segments),
                deciding_leaf="",
            )
        )
    return out


# --------------------------------------------------------------------------
# A05 / R05_context_freshness_and_reentry
# --------------------------------------------------------------------------


def adapt_freshness_binding(doc: Document, ev: EvidenceSet) -> list[FreshnessBindingFact]:
    if not _applicable(doc):
        return []
    out: list[FreshnessBindingFact] = []
    fingerprint = set(V.FINGERPRINT_TOKENS)

    # A R05 binds the fingerprint to the WINDOW, not to the freshness region, so
    # the binding is a document-level fact.  An earlier draft looked for the
    # fingerprint only inside an already-claimed freshness region and therefore
    # missed `context_binding.dependency_fingerprints: required` — a scalar leaf
    # that `walk_nodes` never yields, because it yields containers only.
    bound_at = ""
    for leaf in _claim_leaves(doc):
        seg = leaf.segments[-1] if leaf.segments else ""
        if _seg_tokens(seg) & fingerprint and leaf.value not in (None, "", [], {}, False):
            bound_at = leaf.key_path
            break
    if not bound_at:
        for node in _claim_sites(doc):
            if _seg_tokens(node.innermost) & fingerprint and node.value not in (None, "", [], {}):
                bound_at = node.key_path
                break

    regions = list(_regions(doc, V.FRESHNESS_REGION_TOKENS))
    if not regions and not bound_at:
        return []
    if not regions:
        ev.add(doc.doc_id, bound_at, "source_form=freshness_binding_leaf", True)
        return [FreshnessBindingFact(doc.doc_id, bound_at, True)]

    for node in regions:
        ev.add(doc.doc_id, node.key_path, "source_form=freshness_region", type(node.value).__name__)
        out.append(
            FreshnessBindingFact(
                source_id=doc.doc_id,
                key_path=node.key_path,
                fingerprint_bound=bool(bound_at),
            )
        )
    return out


def adapt_freshness_triggers(doc: Document, ev: EvidenceSet) -> list[FreshnessTriggerFact]:
    if not _applicable(doc):
        return []
    out: list[FreshnessTriggerFact] = []
    for parent, node in _regions_with_parent(doc, V.FRESHNESS_REGION_TOKENS):
        region = _subregion(node, V.FRESHNESS_TRIGGER_REGION_TOKENS)
        if region is None:
            region = node
        collection = normalize_keyed_collection(region.value)
        if not collection:
            continue
        default_effect = _region_default_effect(parent)
        if default_effect is None:
            default_effect = _region_default_effect(node.value)
        if default_effect is None and region is not node:
            default_effect = _region_default_effect(region.value)
        for name, value in collection.items():
            trigger_role = _role_of(str(name), V.FRESHNESS_TRIGGER_ROLES)
            if not trigger_role:
                continue
            effect = _effect_value(value)
            effect_role = _effect_role(effect, V.FRESHNESS_EFFECT_ROLES)
            if not effect_role and default_effect is not None:
                effect = default_effect
                effect_role = _effect_role(effect, V.FRESHNESS_EFFECT_ROLES)
            ev.add(doc.doc_id, f"{region.key_path}.{name}", "source_form=freshness_trigger", effect)
            out.append(
                FreshnessTriggerFact(
                    source_id=doc.doc_id,
                    key_path=f"{region.key_path}.{name}",
                    trigger_role=trigger_role,
                    effect_role=effect_role,
                )
            )
    return out


# --------------------------------------------------------------------------
# A07 / R07_model_route_binding
# --------------------------------------------------------------------------


def adapt_route_receipts(doc: Document, ev: EvidenceSet) -> list[RouteReceiptFact]:
    if not _applicable(doc):
        return []
    out: list[RouteReceiptFact] = []
    window_tokens = set(V.ROUTED_WINDOW_TOKENS)
    authority_syn = V.RECEIPT_CONCEPT_ROLES["authority"]
    required_pos = set(V.REQUIRED_FIELDS_POSITION_TOKENS)

    # A R07 binds the receipt to the WINDOW that uses the route. A receipt
    # declared inside the document that owns window identity is bound to it; an
    # earlier draft looked only at the receipt's own key path and reported the
    # window contract's own receipt as unbound.
    doc_declares_window = False
    for node in _claim_sites(doc):
        if _seg_tokens(node.innermost) & window_tokens:
            doc_declares_window = True
            break

    for node in _regions(doc, V.RECEIPT_REGION_TOKENS):
        if not isinstance(node.value, dict):
            continue
        roles: set[str] = set()
        authority_declared = False
        authority_ok = False
        for leaf in walk_leaves(node.value, key_path=node.key_path):
            seg = leaf.segments[-1] if leaf.segments else ""
            seg_tok = _seg_tokens(seg)
            for role, synonyms in V.RECEIPT_CONCEPT_ROLES.items():
                if seg_tok & synonyms and leaf.value not in (None, "", [], {}):
                    roles.add(role)
            # V4-RCT-06: a receipt may enumerate its concepts as field NAMES
            # under a required-fields position instead of as keys. Both forms
            # declare the same concepts, so both are read.
            if (seg_tok & required_pos) and isinstance(leaf.value, str):
                for role, synonyms in V.RECEIPT_CONCEPT_ROLES.items():
                    if _seg_tokens(leaf.value) & synonyms:
                        roles.add(role)
            if seg_tok & authority_syn:
                authority_declared = True
                if canonical_identifier(str(leaf.value)) == canonical_identifier(
                    V.ROUTING_ONLY_AUTHORITY_VALUE
                ):
                    authority_ok = True
        window_bound = bool(
            doc_declares_window
            or (_path_tokens(node.key_path) & window_tokens)
            or (_value_tokens(node.value) & window_tokens)
        )
        # T2-PARENT-IR-002 / A12. The contract's own missing/stale/inconsistent
        # policy, read as a typed fact. This is a sub-scan inside a region that
        # has already been claimed, so raw traversal is correct here; what is NOT
        # correct is leaving the declaration unread, which is how `best_effort`
        # left all fourteen predicates passing. The value is resolved through the
        # accepted freshness-effect roles, so parity applies and
        # `not_fail_closed` resolves to "" rather than to the compliant role.
        # The COMPLETE declared value, not the first scalar under it.
        # `walk_leaves` yields a list's items as separate leaves, so taking the
        # first one is exactly how `[fail_closed, best_effort]` became
        # `fail_closed` and passed. The value is fetched structurally instead.
        policy_value = _value_at_key_tokens(
            node.value, set(V.ROUTE_RECEIPT_FAILURE_POLICY_TOKENS)
        )
        policy_declared = policy_value is not _ABSENT
        # T2-PARENT-SR-001: the COMPLETE declaration decides, not its first
        # asserted role. `[fail_closed, best_effort]` is a contradiction and
        # fails closed regardless of the order the two are written in.
        policy_role = (
            _complete_effect_role(policy_value, V.FRESHNESS_EFFECT_ROLES)
            if policy_declared
            else ""
        )

        ev.add(doc.doc_id, node.key_path, "source_container=route_receipt", type(node.value).__name__)
        ev.add(
            doc.doc_id,
            node.key_path,
            "route_receipt_failure_policy",
            {"declared": policy_declared, "role": policy_role},
        )
        out.append(
            RouteReceiptFact(
                source_id=doc.doc_id,
                key_path=node.key_path,
                window_bound=window_bound,
                concept_roles=tuple(sorted(roles)),
                authority_is_routing_only=authority_ok,
                authority_declared=authority_declared,
                failure_policy_declared=policy_declared,
                failure_policy_role=policy_role,
            )
        )
    return out


# --------------------------------------------------------------------------
# A08 / R08_independence_constraints
# --------------------------------------------------------------------------


def adapt_independence(doc: Document, ev: EvidenceSet) -> list[IndependenceFact]:
    if not _applicable(doc):
        return []
    out: list[IndependenceFact] = []
    distinct = set(V.DISTINCT_SESSION_TOKENS)
    session = set(V.SESSION_POSITION_TOKENS)
    subject = set(V.DISTINCTNESS_SUBJECT_TOKENS)
    review_tok = set(V.SELF_REVIEW_SUBJECT_TOKENS["review"])
    same_tok = set(V.SELF_REVIEW_SUBJECT_TOKENS["sameness"])
    rejection = set(V.SELF_REVIEW_REJECTION_TOKENS)
    for node in _regions(doc, V.INDEPENDENCE_REGION_TOKENS):
        if not isinstance(node.value, (dict, list)):
            continue
        distinct_enablement = "unknown"
        found_distinct = False
        rejected = False
        effect_declared = False
        for leaf in walk_leaves(node.value, key_path=node.key_path):
            seg = leaf.segments[-1] if leaf.segments else ""
            seg_tok = _seg_tokens(seg)
            path_tok = _path_tokens(leaf.key_path)
            val_tok = _value_tokens(leaf.value)
            here = seg_tok | path_tok | val_tok

            # Both halves of A R08's sentence must be present: a distinctness
            # marker, and the session/window subject it applies to. Either half
            # may sit in the key or in the value, so both are searched.
            if (here & distinct) and (here & session) and (here & subject):
                found_distinct = True
                if _enablement_with_parity(leaf.value) == DISABLED and not (val_tok & distinct):
                    distinct_enablement = "disabled"
                else:
                    distinct_enablement = "enabled"

            # A self-review position is a review token co-occurring with a
            # sameness token — `self_review`, `same_window_review` and
            # `same_author_review` without enumerating every spelling.
            key_here = seg_tok | path_tok
            if (key_here & review_tok) and (key_here & same_tok):
                effect_declared = True
                # V4-FND-02 / F02-A: parity, not presence. `not_prohibited`
                # contains a rejection token and asserts the opposite of one.
                # A key-level negation applies too, so `same_window_review_not_
                # prohibited: true` inverts as well.
                assertion = _vocabulary_assertion(leaf.value, rejection)
                if assertion == ASSERTED and not path_is_negated(leaf.segments):
                    rejected = True
                elif assertion == ASSERTED and path_is_negated(leaf.segments):
                    rejected = False
                elif assertion == INVERTED:
                    rejected = False
        if not found_distinct:
            distinct_enablement = "unknown"
        ev.add(doc.doc_id, node.key_path, "source_container=independence", type(node.value).__name__)
        out.append(
            IndependenceFact(
                source_id=doc.doc_id,
                key_path=node.key_path,
                distinct_session_enablement=distinct_enablement,
                self_review_rejected=rejected,
                self_review_effect_declared=effect_declared,
            )
        )
    return out


def adapt_family_requirements(doc: Document, ev: EvidenceSet) -> list[FamilyRequirementFact]:
    if not _applicable(doc):
        return []
    out: list[FamilyRequirementFact] = []
    family = set(V.MODEL_FAMILY_TOKENS)
    constraint = set(V.CONSTRAINT_POSITION_TOKENS)
    selection = set(SELECTION_SLOT_TOKENS)
    # One fact per family POSITION, not per leaf beneath it.
    #
    # A leaf-level pass reported `different_model_family.delivered_to:
    # model_routing` as a hard-coded family, because the leaf inherits the
    # family token from its ancestor while carrying no constraint token of its
    # own. That is a false positive of exactly the shape ST04-V3-IR-006 named:
    # judging a sub-field as though it were the declaration.
    seen: set[str] = set()

    def _emit(key_path: str, value: Any, own_tokens: set[str]) -> None:
        if key_path in seen:
            return
        seen.add(key_path)
        here = own_tokens | _path_tokens(key_path) | _value_tokens(value)
        ev.add(doc.doc_id, key_path, "source_form=family_position", value)
        out.append(
            FamilyRequirementFact(
                source_id=doc.doc_id,
                key_path=key_path,
                expressed_as_constraint=bool(here & constraint) and not bool(here & selection),
            )
        )

    for node in _claim_sites(doc):
        if _seg_tokens(node.innermost) & family:
            _emit(node.key_path, node.value, _seg_tokens(node.innermost))
    for leaf in _claim_leaves(doc):
        seg = leaf.segments[-1] if leaf.segments else ""
        if not (_seg_tokens(seg) & family):
            continue
        if any(leaf.key_path.startswith(p + ".") for p in seen):
            continue
        _emit(leaf.key_path, leaf.value, _seg_tokens(seg))
    return out


# --------------------------------------------------------------------------
# A10 / R10_existing_mechanism_separation
# --------------------------------------------------------------------------


def _pointer_only(value: Any) -> bool:
    """True when every leaf under `value` is a pointer or a path.

    A10 permits referencing an upstream contract and forbids copying it, so this
    is the whole distinction. It reuses the accepted engine's pointer test rather
    than introducing a second, differently-spelled one.
    """
    leaves = list(walk_leaves(value)) if isinstance(value, (dict, list)) else []
    if not leaves:
        return False
    for leaf in leaves:
        seg = leaf.segments[-1] if leaf.segments else ""
        if is_pointer_key(seg):
            continue
        if isinstance(leaf.value, str) and is_path_like(leaf.value):
            continue
        return False
    return True


def adapt_mechanism_separation(doc: Document, ev: EvidenceSet) -> list[MechanismSeparationFact]:
    if not _applicable(doc):
        return []
    if doc.surface not in V.COMPOSITION_SURFACES:
        return []
    out: list[MechanismSeparationFact] = []
    mutable = set(V.UPSTREAM_MUTABLE_TOKENS)
    for node in _claim_sites(doc):
        if not (_seg_tokens(node.innermost) & mutable):
            continue
        upstream_role = ""
        path_tok = _path_tokens(node.key_path)
        for role, synonyms in V.UPSTREAM_MECHANISM_ROLE_TOKENS.items():
            if path_tok & synonyms:
                upstream_role = role
                break
        if not upstream_role:
            continue
        collection = normalize_keyed_collection(node.value)
        count = len(collection) if collection else (
            len(node.value) if isinstance(node.value, list) else 0
        )
        pointer_only = _pointer_only(node.value)
        ev.add(doc.doc_id, node.key_path, "source_container=upstream_region", type(node.value).__name__)
        if pointer_only or count < V.SEPARATION_MIN_COPIED_ENTRIES:
            continue
        out.append(
            MechanismSeparationFact(
                source_id=doc.doc_id,
                surface=doc.surface,
                key_path=node.key_path,
                upstream_role=upstream_role,
                copied_entry_count=count,
                pointer_only=pointer_only,
            )
        )
    return out


# --------------------------------------------------------------------------
# A12 / R12_failure_surfacing
# --------------------------------------------------------------------------


def adapt_failure_cases(doc: Document, ev: EvidenceSet) -> list[FailureCaseFact]:
    if not _applicable(doc):
        return []
    out: list[FailureCaseFact] = []
    visible = set(V.VISIBLE_FAILURE_TOKENS)
    for parent, node in _regions_with_parent(doc, V.FAILURE_REGION_TOKENS):
        collection = normalize_keyed_collection(node.value)
        if not collection:
            continue
        default_effect = _region_default_effect(parent)
        if default_effect is None:
            default_effect = _region_default_effect(node.value)
        for name, value in collection.items():
            case_role = _role_of(str(name), V.FAILURE_CASE_ROLES)
            if not case_role:
                continue
            effect = _effect_value(value)
            if not (_value_tokens(effect) & visible) and default_effect is not None:
                effect = default_effect
            effect_tokens = _value_tokens(effect)
            declared = effect not in (None, "", [], {})
            ev.add(doc.doc_id, f"{node.key_path}.{name}", "source_form=failure_case", effect)
            out.append(
                FailureCaseFact(
                    source_id=doc.doc_id,
                    key_path=f"{node.key_path}.{name}",
                    case_role=case_role,
                    visible_failure=bool(effect_tokens & visible),
                    effect_declared=declared,
                )
            )
    return out


def adapt_fallback_positions(doc: Document, ev: EvidenceSet) -> list[FallbackPositionFact]:
    if not _applicable(doc):
        return []
    out: list[FallbackPositionFact] = []
    fallback = set(V.SILENT_FALLBACK_TOKENS)
    seen: set[str] = set()
    for node in _claim_sites(doc):
        if not (_seg_tokens(node.innermost) & fallback):
            continue
        enablement, leaf = subtree_enablement(node.value)
        seen.add(node.key_path)
        ev.add(doc.doc_id, node.key_path, "source_form=fallback_position", node.value)
        out.append(
            FallbackPositionFact(
                source_id=doc.doc_id,
                key_path=node.key_path,
                enablement=enablement,
                key_is_negated=path_is_negated(node.segments),
                deciding_leaf=leaf,
            )
        )
    for leaf in _claim_leaves(doc):
        seg = leaf.segments[-1] if leaf.segments else ""
        if not (_seg_tokens(seg) & fallback) or leaf.key_path in seen:
            continue
        ev.add(doc.doc_id, leaf.key_path, "source_form=fallback_leaf", leaf.value)
        out.append(
            FallbackPositionFact(
                source_id=doc.doc_id,
                key_path=leaf.key_path,
                enablement=_enablement_with_parity(leaf.value),
                key_is_negated=path_is_negated(leaf.segments),
                deciding_leaf="",
            )
        )
    return out


# --------------------------------------------------------------------------
# unsupported-shape reporting
# --------------------------------------------------------------------------


def adapt_v4_ambiguities(doc: Document, ev: EvidenceSet) -> list[UnsupportedFact]:
    """A claimed region whose active shape no v4 adapter can interpret.

    C-08's asymmetry: an unclaimed document is inert, but once a region IS
    claimed, a shape the adapter cannot read becomes a visible P00 instead of a
    silent pass.
    """
    if not _applicable(doc):
        return []
    out: list[UnsupportedFact] = []
    claimed = (
        (V.LIFECYCLE_REGION_TOKENS, "lifecycle"),
        (V.CONTEXT_REGION_TOKENS, "context_contract"),
        (V.FRESHNESS_REGION_TOKENS, "freshness"),
        (V.RECEIPT_REGION_TOKENS, "route_receipt"),
        (V.INDEPENDENCE_REGION_TOKENS, "independence"),
        (V.FAILURE_REGION_TOKENS, "failure_surfacing"),
    )
    for region_tokens, region_name in claimed:
        for node in _regions(doc, region_tokens):
            if isinstance(node.value, (dict, list, str)) or node.value is None:
                continue
            ev.add(doc.doc_id, node.key_path, f"source_form=unreadable_{region_name}", node.value)
            out.append(
                UnsupportedFact(
                    doc.doc_id,
                    node.key_path,
                    f"v4_{region_name}_region_shape_not_interpretable",
                )
            )
    return out

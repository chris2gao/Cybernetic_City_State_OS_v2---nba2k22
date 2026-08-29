#!/usr/bin/env python3
"""Structural position provenance: whose slot is this mapping key?

T2-SP-UPSTREAM-CM-v2.  correction-003 measured that the representation layer
exposed no coordinate saying whether a mapping key is an author-chosen entry
identity inside an open keyed collection, or a declaration name owned by a
semantic contract.  Without it, adapter applicability collapsed into ancestor
name inspection or body-shape guessing, and a foreign `failure_states` entry
with a nonempty body could make five unrelated global adapters emit facts.

This module supplies that coordinate, and nothing else.

Three properties make it different from the heuristics correction-003 rejected:

1.  **The evaluator owns the binding, not the payload.**  The binding file lives
    beside this module, inside the evaluator package.  A payload that contains
    text shaped like a binding declares nothing: it is never read as authority.
    Adding a document with a brand-new collection name requires no change here
    and no change in any adapter — that is the test that separates a declared
    schema from a name whitelist.

2.  **Document identity is an opaque lookup key.**  The binding maps a discovery
    identity to a profile.  No token of that identity is ever segmented, matched
    or interpreted; two identities are either equal or unrelated.  Path
    membership stays in `surface_declaration.yml` and stays surface-only.

3.  **Selectors are structural and depth-free.**  A selector matches on the tail
    of a mapping-key path, so wrapping a declared block in a container that adds
    no semantic content of its own cannot change the role of anything inside it
    (S01-S03).  There is no depth threshold anywhere in this file.

Unknown is not a soft default.  An unresolved, unbound or conflicting position
cannot be claimed by any adapter, and the refusal is visible.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


# --------------------------------------------------------------------------
# position roles
# --------------------------------------------------------------------------

INSTANCE_IDENTITY = "instance_identity"
DECLARATION_NAME = "declaration_name"
UNKNOWN_ROLE = "unknown"
CONFLICTING_ROLE = "conflicting"

POSITION_ROLES = (INSTANCE_IDENTITY, DECLARATION_NAME, UNKNOWN_ROLE, CONFLICTING_ROLE)

#: The only role an adapter may attach business meaning to.  Everything else,
#: including `unknown`, fails closed.
CLAIMABLE_ROLES = frozenset({DECLARATION_NAME})

BINDING_FILE_NAME = "structural_binding_v1.yml"


class StructuralBindingError(Exception):
    """The evaluator's own binding is malformed.  Never raised by a payload."""


WILDCARD = "*"


@dataclass(frozen=True)
class ContainerRule:
    """One container position, and the role its direct child keys occupy.

    `selector` is a root-anchored sequence of mapping keys, matched against a
    path whose declared transparent wrappers have already been removed. So
    `("entry_modes",)` matches `entry_modes`, and matches
    `contract.entry_modes` exactly when `contract` is a declared transparent
    container — which is the wrapper invariance, expressed with no depth term
    and with no credit given to an undeclared ancestor.
    """

    selector: tuple[str, ...]
    child_keys: str
    note: str = ""

    def matches(self, segments: tuple[str, ...]) -> bool:
        """ANCHORED at the document root, against an already-reduced path.

        T2-SP-UPSTREAM Codex B1_UNDECLARED_ANCESTOR_TAIL_PROMOTION. This used to
        match the TAIL of a path, which meant a selector saying "the
        runtime_controls block of this document" also said "any container
        anywhere named runtime_controls". An author could then place that name
        inside `foreign_extension` — a container the evaluator models nowhere —
        and the position became claimable. The undeclared ancestor supplied no
        authority, yet it cost none either, which is the same absence-as-
        authority defect in a different clause.

        Reaching a declared container through intervening containers is now the
        job of positively declared transparent wrappers, and of nothing else.
        Callers pass a path already reduced by `Profile.effective_segments`, so
        wrapper invariance stays depth-free while an undeclared ancestor keeps
        the position out of every rule.
        """
        if len(self.selector) != len(segments):
            return False
        for want, got in zip(self.selector, segments):
            if want != WILDCARD and want != got:
                return False
        return True

    @property
    def specificity(self) -> int:
        """Longer, less wild selectors win.  Ties are conflicts, not guesses."""
        return len(self.selector) * 2 - sum(1 for s in self.selector if s == WILDCARD)


@dataclass(frozen=True)
class Profile:
    """A reusable structural shape.  Profiles are named by the evaluator."""

    profile_id: str
    root_child_keys: str
    containers: tuple[ContainerRule, ...]
    #: Containers the evaluator POSITIVELY declares to carry no structure of
    #: their own. Traversing one does not change what is inside it.
    #:
    #: T2-SP-UPSTREAM-FG-00006. An earlier revision treated "no rule matched any
    #: ancestor" as proof that every container on the way down was transparent.
    #: That is absence used as authority, and it let a collider inside a wholly
    #: unmodelled foreign container be promoted to a declaration name. Wrapper
    #: traversal now requires a positive declaration; silence is silence again.
    transparent_containers: tuple[tuple[str, ...], ...] = ()

    def _match(self, segments: tuple[str, ...]) -> list[ContainerRule]:
        """Every most-specific rule anchored on the reduced form of `segments`."""
        reduced = self.effective_segments(segments)
        best: list[ContainerRule] = []
        best_score = -1
        for rule in self.containers:
            if not rule.matches(reduced):
                continue
            if rule.specificity > best_score:
                best, best_score = [rule], rule.specificity
            elif rule.specificity == best_score:
                best.append(rule)
        return best

    def _is_transparent(self, prefix: tuple[str, ...]) -> bool:
        """Is the container at `prefix` declared to carry no structure?

        Anchored on the reduced path, like every other selector, so a declared
        wrapper nested inside another declared wrapper is still a wrapper and
        no depth term appears anywhere.
        """
        if not prefix:
            return False
        reduced = self._reduce(prefix[:-1]) + prefix[-1:]
        for selector in self.transparent_containers:
            if ContainerRule(selector, UNKNOWN_ROLE).matches(reduced):
                return True
        return False

    def _reduce(self, ancestors: tuple[str, ...]) -> tuple[str, ...]:
        """Drop the declared transparent containers from an ancestor path.

        Walks left to right so a wrapper only counts as declared relative to
        what is already known to be above it. Nothing is counted, compared to a
        threshold, or inferred from a name the evaluator has not written down.
        """
        out: list[str] = []
        for seg in ancestors:
            candidate = tuple(out) + (seg,)
            if self._transparent_selector_matches(candidate):
                continue
            out.append(seg)
        return tuple(out)

    def _transparent_selector_matches(self, reduced_prefix: tuple[str, ...]) -> bool:
        for selector in self.transparent_containers:
            if ContainerRule(selector, UNKNOWN_ROLE).matches(reduced_prefix):
                return True
        return False

    def contradiction_at(self, prefix: tuple[str, ...]) -> str | None:
        """Is this container described BOTH as transparent and as structural?

        Positive transparency is itself a structural claim: it says this
        container carries nothing of its own. A container rule says the
        opposite — that this container's child keys have a role it governs.
        Both cannot be true of one container, and the contradiction must not be
        settled by which check the code happens to run first.

        Returned as a reason string so the refusal can name the two clauses
        that disagree, rather than reporting a bare `conflicting`.
        """
        if not prefix:
            return None
        reduced = self._reduce(prefix[:-1]) + prefix[-1:]
        if not self._transparent_selector_matches(reduced):
            return None
        rules = [r for r in self.containers if r.matches(reduced)]
        if not rules:
            return None
        roles = ",".join(sorted({r.child_keys for r in rules}))
        sel = "/".join(reduced) or "<root>"
        return f"transparent_and_structural:{sel}:{roles}"

    def first_contradiction(self, segments: tuple[str, ...]) -> str | None:
        """The first contradicted container on the way to `segments`, if any."""
        for i in range(1, len(segments) + 1):
            reason = self.contradiction_at(segments[:i])
            if reason is not None:
                return reason
        return None

    def effective_segments(self, segments: tuple[str, ...]) -> tuple[str, ...]:
        """`segments` with declared transparent containers removed.

        This is the whole of wrapper invariance, and it is depth-free because
        it counts nothing: it walks the path once and drops the ancestors the
        evaluator positively declared to be carrying nothing. A container the
        evaluator has said nothing about is NOT dropped — silence about a
        container is not a statement that it is transparent.

        A contradicted container is never dropped. Eliding it would let the
        transparency clause quietly win over the structural clause and promote
        what is inside it, which is the failure mode this method must not have.
        """
        if not segments or not self.transparent_containers:
            return segments
        out: list[str] = []
        for seg in segments[:-1]:
            candidate = tuple(out) + (seg,)
            if (
                self._transparent_selector_matches(candidate)
                and self._structural_selector_matches(candidate) is False
            ):
                continue
            out.append(seg)
        return tuple(out) + segments[-1:]

    def _structural_selector_matches(self, reduced_prefix: tuple[str, ...]) -> bool:
        for rule in self.containers:
            if rule.matches(reduced_prefix):
                return True
        return False

    def role_of(self, segments: tuple[str, ...]) -> tuple[str, str]:
        """Role of the position at `segments`, plus a short provenance string.

        The role of a key is decided by the container that HOLDS it, never by
        the key itself.  That is what stops a key's own spelling from deciding
        whether it may be claimed.
        """
        if not segments:
            # The document root is a container, not a position.
            return DECLARATION_NAME, "document_root"

        # A container the binding describes two incompatible ways poisons every
        # position at or under it. This runs before anything else so that no
        # later step can resolve the disagreement by accident of ordering.
        contradiction = self.first_contradiction(segments)
        if contradiction is not None:
            return CONFLICTING_ROLE, f"{self.profile_id}:{contradiction}"

        # Declared transparent containers drop out first, so everything below
        # judges the position as if the wrappers the evaluator vouched for were
        # not written. Undeclared containers survive this step untouched.
        effective = self.effective_segments(segments)
        via_wrapper = "" if effective == segments else "_through_declared_wrappers"

        parent = effective[:-1]
        if not parent:
            return (
                self.root_child_keys,
                f"{self.profile_id}:root_child_keys{via_wrapper}",
            )

        best = self._match(parent)
        if not best:
            # Nothing describes the container that holds this position. That is
            # not evidence of anything except that it is undescribed, and
            # undescribed is unclaimable.
            #
            # Codex B1: there used to be a second promotion path here, granting
            # `declaration_name` when the position's OWN path matched a rule.
            # With tail matching that let an undeclared ancestor host a declared
            # name and hand it claimability. Anchored matching plus declared
            # transparent wrappers already covers every legitimate way to reach
            # a declared container, so a second route is not needed and is not
            # safe to keep: two routes to claimability is one more than the
            # number of things that can be audited at once.
            return UNKNOWN_ROLE, f"{self.profile_id}:no_rule_for_container"
        roles = {r.child_keys for r in best}
        if len(roles) > 1:
            return CONFLICTING_ROLE, (
                f"{self.profile_id}:conflicting_rules:" + ",".join(sorted(roles))
            )
        sel = "/".join(best[0].selector) or "<root>"
        return best[0].child_keys, f"{self.profile_id}:{sel}"


@dataclass(frozen=True)
class PositionProvenance:
    """The resolved structural provenance for ONE document.

    `profile` is None when the evaluator's binding has no entry for this
    document's discovery identity.  That is not an error and not a default to
    `declaration_name`: every position in an unbound document is `unknown`, and
    therefore unclaimable.  A new document is invisible to the adapters until
    the evaluator declares its structure, which is the fail-closed direction.
    """

    doc_identity: str
    profile: Profile | None
    binding_source: str

    @property
    def bound(self) -> bool:
        return self.profile is not None

    def role_of(self, segments: tuple[str, ...]) -> str:
        return self.resolve(segments)[0]

    def resolve(self, segments: tuple[str, ...]) -> tuple[str, str]:
        if self.profile is None:
            return UNKNOWN_ROLE, f"{self.binding_source}:document_not_bound"
        return self.profile.role_of(tuple(segments))

    def claimable(self, segments: tuple[str, ...]) -> bool:
        return self.role_of(tuple(segments)) in CLAIMABLE_ROLES


#: Used when a Document was built without going through discovery.  It refuses
#: every position, so forgetting to attach provenance cannot silently re-open
#: the leak correction-003 measured.
UNBOUND = PositionProvenance(
    doc_identity="", profile=None, binding_source="no_structural_binding_attached"
)


@dataclass(frozen=True)
class StructuralBinding:
    """The evaluator's whole binding: identity -> profile."""

    source: str
    document_profiles: dict[str, str]
    profiles: dict[str, Profile]

    def for_document(self, doc_identity: str) -> PositionProvenance:
        """Opaque lookup.  `doc_identity` is compared, never parsed."""
        profile_id = self.document_profiles.get(doc_identity)
        if profile_id is None:
            return PositionProvenance(doc_identity, None, self.source)
        profile = self.profiles.get(profile_id)
        if profile is None:
            raise StructuralBindingError(
                f"{self.source}: document {doc_identity!r} names unknown profile {profile_id!r}"
            )
        return PositionProvenance(doc_identity, profile, self.source)


def _role_value(raw: Any, where: str) -> str:
    if raw not in (INSTANCE_IDENTITY, DECLARATION_NAME, UNKNOWN_ROLE):
        raise StructuralBindingError(
            f"{where}: role must be one of "
            f"{INSTANCE_IDENTITY}/{DECLARATION_NAME}/{UNKNOWN_ROLE}, got {raw!r}"
        )
    return str(raw)


def _selector(raw: Any, where: str) -> tuple[str, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list) or any(not isinstance(x, str) or not x for x in raw):
        raise StructuralBindingError(
            f"{where}: selector must be a list of nonempty mapping-key strings"
        )
    return tuple(raw)


def parse_binding(raw: Any, source: str) -> StructuralBinding:
    if not isinstance(raw, dict):
        raise StructuralBindingError(f"{source}: binding must be a mapping")

    profiles: dict[str, Profile] = {}
    raw_profiles = raw.get("profiles") or {}
    if not isinstance(raw_profiles, dict):
        raise StructuralBindingError(f"{source}: profiles must be a mapping")
    for pid, body in raw_profiles.items():
        where = f"{source}:profiles.{pid}"
        if not isinstance(body, dict):
            raise StructuralBindingError(f"{where}: profile must be a mapping")
        root_child = _role_value(body.get("root_child_keys", UNKNOWN_ROLE), where)
        rules: list[ContainerRule] = []
        for i, c in enumerate(body.get("containers") or []):
            cw = f"{where}.containers[{i}]"
            if not isinstance(c, dict):
                raise StructuralBindingError(f"{cw}: container rule must be a mapping")
            rules.append(
                ContainerRule(
                    selector=_selector(c.get("selector"), cw),
                    child_keys=_role_value(c.get("child_keys"), cw),
                    note=str(c.get("note", "")),
                )
            )
        transparent: list[tuple[str, ...]] = []
        for i, t in enumerate(body.get("transparent_containers") or []):
            tw = f"{where}.transparent_containers[{i}]"
            if not isinstance(t, dict):
                raise StructuralBindingError(f"{tw}: transparent rule must be a mapping")
            sel = _selector(t.get("selector"), tw)
            if not sel:
                raise StructuralBindingError(
                    f"{tw}: a transparent container needs a selector; an empty one "
                    "would declare the whole document transparent"
                )
            transparent.append(sel)
        profiles[str(pid)] = Profile(
            str(pid), root_child, tuple(rules), tuple(transparent)
        )

    raw_docs = raw.get("document_profiles") or {}
    if not isinstance(raw_docs, dict):
        raise StructuralBindingError(f"{source}: document_profiles must be a mapping")
    doc_profiles = {str(k): str(v) for k, v in raw_docs.items()}
    for ident, pid in doc_profiles.items():
        if pid not in profiles:
            raise StructuralBindingError(
                f"{source}: document {ident!r} names unknown profile {pid!r}"
            )
    return StructuralBinding(source, doc_profiles, profiles)


def evaluator_binding_path() -> Path:
    """Beside this module, never beside the payload.

    This single line is what makes payload self-minting impossible: the path is
    computed from the evaluator's own location, so nothing a corpus contains can
    redirect it, shadow it, or add a profile to it.
    """
    return Path(__file__).resolve().parent / BINDING_FILE_NAME


def load_structural_binding(path: Path | None = None) -> StructuralBinding:
    target = path or evaluator_binding_path()
    if not target.is_file():
        raise StructuralBindingError(
            f"evaluator structural binding is missing at {target}"
        )
    raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    return parse_binding(raw, source=target.name)


def unsupported_reason(role: str, provenance_note: str) -> str:
    """Why a position was refused, in the words of the structural layer."""
    if role == INSTANCE_IDENTITY:
        return (
            "position is a keyed-collection instance identity under the evaluator "
            f"structural binding, so no adapter may claim it ({provenance_note})"
        )
    if role == CONFLICTING_ROLE:
        return (
            "conflicting structural binding rules resolve this position, so it "
            f"fails closed ({provenance_note})"
        )
    return (
        "no authoritative structural binding resolves this position, so it fails "
        f"closed as unknown ({provenance_note})"
    )

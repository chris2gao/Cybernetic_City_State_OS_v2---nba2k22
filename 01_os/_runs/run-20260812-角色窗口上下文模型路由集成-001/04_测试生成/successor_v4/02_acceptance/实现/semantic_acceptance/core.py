#!/usr/bin/env python3
"""Representation layer: parsing and structural normalization only.

The pipeline C-08 requires is

    raw artifact -> parser -> schema-bound adapter -> typed decision facts

and this module is the first two boxes.  It knows about YAML, Markdown, keys,
containers and depth.  It knows nothing about roles, providers, authority or
automation: every semantic vocabulary lives in `vocabulary.py`, where each entry
is bound to an A requirement through `provenance.rule`.

The independent review's AB-01 finding was that representation bias had merely
MOVED from predicates into the extractor.  The structural answer is that meaning
may only be attached at an adapter (`adapters.py`), and an adapter may only use a
declared, traced vocabulary.  Everything below this line is deliberately unable
to decide anything.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field as dc_field, replace
from pathlib import Path
from typing import Any, Iterable, Iterator

import yaml

from .provenance import rule
from .structural_binding import (
    CLAIMABLE_ROLES,
    UNBOUND,
    UNKNOWN_ROLE,
    PositionProvenance,
    StructuralBinding,
    load_structural_binding,
)
from .vocabulary import (
    COLLECTION_ID_FIELD_TOKENS,
    DECLARATION_FIELD_NAME_TOKENS,
    DESCRIPTIVE_POSITION_TOKENS,
    ENABLEMENT_NEGATIVE_VALUES,
    NEGATION_TOKENS,
    POINTER_TOKENS,
    PROVENANCE_TOKENS,
    SCHEMA_META_TOKENS,
)


# --------------------------------------------------------------------------
# strict YAML
# --------------------------------------------------------------------------


class DuplicateKeyError(Exception):
    """A duplicate mapping key makes a document's meaning ambiguous."""


class StrictLoader(yaml.SafeLoader):
    pass


def _no_duplicate_keys(loader, node, deep=False):
    out: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in out:
            raise DuplicateKeyError(f"duplicate key: {key!r}")
        out[key] = loader.construct_object(value_node, deep=deep)
    return out


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicate_keys
)


def load_yaml_strict(text: str) -> Any:
    """Parse with a real YAML parser.  No regex ever substitutes for this."""
    return yaml.load(text, Loader=StrictLoader)


def load_yaml_strict_single(text: str) -> Any:
    """Strict parse that additionally rejects a multi-document stream.

    `yaml.load` silently keeps only the first document.  The receipt contract
    needs the stricter reading, because a second document is unreviewed content
    riding along inside a validated file.
    """
    docs = list(yaml.load_all(text, Loader=StrictLoader))
    if len(docs) > 1:
        raise ValueError(f"multi-document YAML stream: {len(docs)} documents")
    return docs[0] if docs else None


def dump_yaml(value: Any) -> str:
    return yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=4096)


# --------------------------------------------------------------------------
# token-level segment analysis
# --------------------------------------------------------------------------

_TOKEN_SPLIT_PATTERN = rule(
    "V-PARSE-03",
    kind="mapping",
    authority="C-08 end_to_end_semantic_boundary",
    interpretation=(
        "Whole-token segmentation for declaration-position keys. Subject values "
        "are never segmented or compared with a completeness vocabulary."
    ),
    value=r"[^0-9a-z一-鿿]+",
)
_TOKEN_SPLIT = re.compile(_TOKEN_SPLIT_PATTERN)


def tokens(segment: str) -> list[str]:
    """Split a key segment into whole tokens.

    ST04-V3-IR-005 was caused by matching the letters "source" inside the word
    "resource".  Tokenizing first makes that impossible: `resource_constraints`
    yields ['resource', 'constraints'] and never yields 'source'.
    """
    return [t for t in _TOKEN_SPLIT.split(str(segment).strip().lower()) if t]


def negation_count(segment: str) -> int:
    """How many negation markers the key name carries.

    Parity, not presence, is what decides polarity (vocabulary.V-POL-02).  The
    presence rule read `master_write_not_forbidden` and `scheduler_not_prohibited`
    as prohibitions; both are grants of exactly the thing they double-negate.
    """
    return sum(1 for t in tokens(segment) if t in NEGATION_TOKENS)


def is_negated(segment: str) -> bool:
    """True when the key's own name declares a prohibition.

    An odd number of negation markers negates; an even non-zero number is a
    double negative and asserts the positive.
    """
    return negation_count(segment) % 2 == 1


def is_double_negated(segment: str) -> bool:
    n = negation_count(segment)
    return n >= 2 and n % 2 == 0


def strip_negation(segment: str) -> str:
    """The field a negated key is ABOUT.

    Handles prefix and suffix placement symmetrically, which the previous
    harness did not: it anchored the marker at the end of the leaf only, so
    `field_prohibited` was recognised and `prohibited_field` was not.
    """
    tok = tokens(segment)
    kept = [t for t in tok if t not in NEGATION_TOKENS]
    return "_".join(kept) if kept else ""


def path_negation_count(segments: Iterable[str]) -> int:
    return sum(negation_count(s) for s in segments)


def path_is_negated(segments: Iterable[str]) -> bool:
    return path_negation_count(segments) % 2 == 1


# --------------------------------------------------------------------------
# enablement: tri-state, closed NEGATIVE set
# --------------------------------------------------------------------------

ENABLEMENT_STATES = tuple(
    rule(
        "V-EN-03",
        kind="mapping",
        authority="C-03; A13/R13_no_authority_escalation; A14/R14_Human_triggered_progression",
        interpretation="Typed outcomes of closed-negative enablement classification.",
        value=("enabled", "disabled", "unknown"),
    )
)
ENABLED, DISABLED, UNKNOWN = ENABLEMENT_STATES

def classify_enablement(
    value: Any, negative_values: Iterable[str] = ENABLEMENT_NEGATIVE_VALUES
) -> str:
    """enabled / disabled / unknown.

    ST04-V3-IR-008 and ST04-V3-IR-010 were both produced by a closed POSITIVE
    vocabulary: any unrecognised value fell through to "not enabled", so
    `'granted'` and `'after_handoff_publication'` read as safe.  Only a closed
    NEGATIVE set is safe, because then the unrecognised case lands on the
    failing side.
    """
    negatives = frozenset(negative_values)
    if value is None:
        return DISABLED
    if value is True:
        return ENABLED
    if value is False:
        return DISABLED
    if isinstance(value, str):
        s = value.strip().lower()
        if not s:
            return DISABLED
        if s in negatives:
            return DISABLED
        return ENABLED
    if isinstance(value, (int, float)):
        return DISABLED if value == 0 else ENABLED
    if isinstance(value, (list, dict, tuple, set)):
        return DISABLED if len(value) == 0 else ENABLED
    return UNKNOWN


def subtree_enablement(
    value: Any, negative_values: Iterable[str] = ENABLEMENT_NEGATIVE_VALUES
) -> tuple[str, str]:
    """Enablement of a whole subtree, with the leaf that decided it.

    A scalar is judged directly.  A container is judged by its leaves, and a leaf
    reached through a negated key asserts a prohibition rather than enabling
    anything.  This is what closes the nested-enablement family the independent
    suite reached and the leaf-only walker could not see at all:

        scheduler: {enabled: true}                      S36
        scheduler: {enabled: true, prohibited: true}    S40  (contradiction fails closed)
        automation_controls: {cadence: {trigger: ...}}  S41
        permissions: {master_write_authorized: {state: granted}}   S23
        capabilities: {publish_master: true}            S24
    """
    if not isinstance(value, (dict, list, tuple)):
        return classify_enablement(value, negative_values), ""
    decided = DISABLED
    where = ""
    for leaf in walk_leaves(value):
        if path_is_negated(leaf.segments):
            continue
        state = classify_enablement(leaf.value, negative_values)
        if state == ENABLED:
            return ENABLED, leaf.key_path
        if state == UNKNOWN and decided != ENABLED:
            decided, where = UNKNOWN, leaf.key_path
    return decided, where


_PATH_PATTERN = rule(
    "V-PARSE-04",
    kind="mapping",
    authority="C-08; A09/R09_structured_handoff",
    interpretation=(
        "A scalar is path-shaped only when it is a relative-looking token ending "
        "in one of the declared durable artifact formats. This separates a state "
        "pointer from carried mutable state; the key name alone is insufficient."
    ),
    value=r"[\w一-鿿\-./]+\.(ya?ml|md|py|json|txt)$",
)
_PATH_RX = re.compile(_PATH_PATTERN)


def is_path_like(value: Any) -> bool:
    return isinstance(value, str) and bool(_PATH_RX.match(value.strip()))


def is_pointer_key(segment: str) -> bool:
    return bool(set(tokens(segment)) & POINTER_TOKENS)


def is_provenance_segment(segment: str) -> bool:
    """Whole-token test.

    `evidence_refs` is provenance.  `resource_constraints` is not, because its
    tokens are {resource, constraints} and neither is `source`.  The previous
    harness used re.search over the raw segment and therefore silenced an entire
    subtree whenever an ancestor key happened to contain those six letters
    (ST04-V3-IR-005).
    """
    return bool(set(tokens(segment)) & PROVENANCE_TOKENS)


def is_descriptive_segment(segment: str) -> bool:
    """A key naming commentary about a subject rather than a declaration of it.

    `authority_note`, `authority_description` and `scheduler_note` are statements
    ABOUT a subject.  Reading them as declarations produced three independent
    false positives (S18, S20, S37).  Length is not the test: "unchanged" is one
    word and is still commentary.
    """
    return bool(set(tokens(segment)) & DESCRIPTIVE_POSITION_TOKENS)


def is_schema_meta_key(segment: str) -> bool:
    """A key that declares a schema rather than carrying data."""
    return bool(set(tokens(strip_negation(segment) or segment)) & SCHEMA_META_TOKENS)


# --------------------------------------------------------------------------
# structural walking
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Leaf:
    segments: tuple[str, ...]  # mapping keys only; list indices are not segments
    key_path: str  # human-readable, includes list indices
    value: Any
    # T2-SP-UPSTREAM-CM-v2. Structural position provenance, resolved before any
    # adapter runs. `unknown` is the safe default: a leaf reached through a
    # traversal that carries no binding cannot be claimed.
    role: str = UNKNOWN_ROLE
    role_source: str = "not_resolved"

    @property
    def innermost(self) -> str:
        return self.segments[-1] if self.segments else ""

    @property
    def structurally_claimable(self) -> bool:
        return self.role in CLAIMABLE_ROLES


def walk_leaves(
    node: Any,
    segments: tuple[str, ...] = (),
    key_path: str = "",
    _ancestors: frozenset[int] = frozenset(),
) -> Iterator[Leaf]:
    """Yield every scalar leaf with its mapping-key path.

    List indices deliberately do NOT become segments: `prohibited_provider[0]`
    and `prohibited_provider` must be judged identically, which is half of
    container-shape invariance (NG-01).
    """
    if isinstance(node, (dict, list)):
        node_id = id(node)
        if node_id in _ancestors:
            return
        ancestors = _ancestors | {node_id}
    else:
        ancestors = _ancestors
    if isinstance(node, dict):
        for k, v in node.items():
            ks = str(k)
            child_path = f"{key_path}.{ks}" if key_path else ks
            yield from walk_leaves(v, segments + (ks,), child_path, ancestors)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_leaves(v, segments, f"{key_path}[{i}]", ancestors)
    else:
        yield Leaf(segments, key_path, node)


@dataclass(frozen=True)
class Node:
    """A mapping-or-list value reached by mapping keys, with its own key."""

    segments: tuple[str, ...]
    key_path: str
    value: Any
    # T2-SP-UPSTREAM-CM-v2. correction-003 measured that these three fields were
    # the whole information model, and that no function of them could separate a
    # keyed-collection entry identity from an adapter-owned declaration position
    # without ancestor-name or body-shape inference. `role` is that missing
    # coordinate. It is resolved from the evaluator's own structural binding,
    # never from anything the document says about itself.
    role: str = UNKNOWN_ROLE
    role_source: str = "not_resolved"

    @property
    def innermost(self) -> str:
        return self.segments[-1] if self.segments else ""

    @property
    def depth(self) -> int:
        return len(self.segments)

    @property
    def structurally_claimable(self) -> bool:
        """May an adapter attach business meaning here?

        Only a declaration position. An instance identity, an unresolved
        position and a conflicting binding all fail closed, and the refusal is
        surfaced by the adapter as visible unsupported evidence rather than
        vanishing.
        """
        return self.role in CLAIMABLE_ROLES


def walk_nodes(
    node: Any,
    segments: tuple[str, ...] = (),
    key_path: str = "",
    _ancestors: frozenset[int] = frozenset(),
) -> Iterator[Node]:
    """Every container value in the document, with its mapping-key path.

    Discovery walks containers rather than only the document root, so wrapping a
    declared block in a container that adds no semantic content of its own cannot
    change what the block is (S01-S03). There is no fixed depth threshold: a
    threshold would simply move the escape to depth+1. YAML can contain recursive
    aliases, so only an actual ancestor cycle ends traversal.
    """
    if not isinstance(node, (dict, list)):
        return
    node_id = id(node)
    if node_id in _ancestors:
        return
    ancestors = _ancestors | {node_id}
    if isinstance(node, dict):
        for k, v in node.items():
            ks = str(k)
            child_path = f"{key_path}.{ks}" if key_path else ks
            if isinstance(v, (dict, list)):
                yield Node(segments + (ks,), child_path, v)
            yield from walk_nodes(v, segments + (ks,), child_path, ancestors)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            child_path = f"{key_path}[{i}]"
            yield from walk_nodes(v, segments, child_path, ancestors)


def bound_nodes(doc: "Document") -> list[Node]:
    """Every container in a document, each carrying its resolved structural role.

    This is the only traversal an adapter may use to pick a claim site. The
    plain `walk_nodes` stays available for structural sub-scans inside a value
    that has already been claimed, where the segments are relative and a role
    would be meaningless.
    """
    if doc.fmt != "yaml" or not doc.parsed or not isinstance(doc.data, dict):
        return []
    prov = doc.provenance or UNBOUND
    out: list[Node] = []
    root_role, root_src = prov.resolve(())
    out.append(Node((), "", doc.data, root_role, root_src))
    for n in walk_nodes(doc.data):
        role, src = prov.resolve(n.segments)
        out.append(Node(n.segments, n.key_path, n.value, role, src))
    return out


def bound_leaves(doc: "Document") -> list[Leaf]:
    """Every scalar leaf of a document, each carrying its resolved role."""
    if doc.fmt != "yaml" or not doc.parsed:
        return []
    prov = doc.provenance or UNBOUND
    out: list[Leaf] = []
    for leaf in walk_leaves(doc.data):
        role, src = prov.resolve(leaf.segments)
        out.append(Leaf(leaf.segments, leaf.key_path, leaf.value, role, src))
    return out


def yaml_structured_strings(node: Any) -> list[str]:
    """Every mapping key and every scalar string, from the PARSED structure.

    ST04-V3-IR-007: catalog detection that reads serialized lines misses a
    mapping key containing a space and misses a Markdown heading entirely.
    Reading the parsed structure removes the whole failure family at once.
    """
    out: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            out.append(str(k))
            out.extend(yaml_structured_strings(v))
    elif isinstance(node, list):
        for v in node:
            out.extend(yaml_structured_strings(v))
    elif isinstance(node, str):
        out.append(node)
    return out


def collection_strings(node: Any) -> list[list[str]]:
    """Structured strings grouped by the collection that holds them.

    A catalog is a COLLECTION of identifiers (vocabulary.V-CAT-01).  Grouping by
    collection is what distinguishes a restated catalog from a document that
    happens to mention one identifier in passing, without any threshold on how
    many mentions are tolerated.
    """
    groups: list[list[str]] = []
    if isinstance(node, dict):
        own = [str(k) for k in node]
        own += [v for v in node.values() if isinstance(v, str)]
        if own:
            groups.append(own)
        for v in node.values():
            groups.extend(collection_strings(v))
    elif isinstance(node, list):
        own = [v for v in node if isinstance(v, str)]
        for v in node:
            if isinstance(v, dict):
                own.extend(str(k) for k in v)
        if own:
            groups.append(own)
        for v in node:
            groups.extend(collection_strings(v))
    return groups


# --------------------------------------------------------------------------
# container-shape normalization
# --------------------------------------------------------------------------

def normalize_keyed_collection(node: Any) -> dict[str, Any]:
    """Reduce every keyed-collection container to one mapping.

    Accepted, and required to produce identical output:

        {a: {...}, b: {...}}                     mapping of mappings
        [{id: a, ...}, {id: b, ...}]             list of records
        [[a, {...}], [b, {...}]]                 list of pairs
        [{a: {...}}, {b: {...}}]                 list of single-entry mappings
        [a, b]                                   list of bare identifiers

    ST04-V2-IR-002 and ST04-V3-IR-003 are both "the author enumerated two of
    these and a third was rejected".  Enumeration is the defect; this function
    is the fix, and MT-entry-mode-container asserts the invariance directly.
    """
    if isinstance(node, dict):
        return {str(k): v for k, v in node.items()}
    if not isinstance(node, list):
        return {}
    out: dict[str, Any] = {}
    for item in node:
        if isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[0], str):
            out[item[0]] = item[1] if isinstance(item[1], dict) else {}
            continue
        if isinstance(item, dict):
            ident = None
            for ik in COLLECTION_ID_FIELD_TOKENS:
                v = item.get(ik)
                if isinstance(v, str) and v.strip():
                    ident = v.strip()
                    break
            if ident is not None:
                out[ident] = {
                    k: v for k, v in item.items() if k not in COLLECTION_ID_FIELD_TOKENS
                } or dict(item)
                continue
            if len(item) == 1:
                k, v = next(iter(item.items()))
                out[str(k)] = v if isinstance(v, dict) else {}
                continue
            continue
        if isinstance(item, str):
            out[item] = {}
    return out


def canonical_identifier(value: str) -> str:
    """Case, spacing and punctuation equivalents collapse to one identifier.

    `GPT-5.6 Sol`, `gpt 5.6 sol`, `GPT_5_6_SOL` and `GPT–5.6 Sol` are the same
    routing identifier written four ways.  Treating them as different is the same
    defect as treating a nested wrapper as a different document (S44).
    """
    return "".join(tokens(value))


# --------------------------------------------------------------------------
# polarity reduction
# --------------------------------------------------------------------------

POLARITY_STATES = tuple(
    rule(
        "V-POL-03",
        kind="mapping",
        authority="A09/R09_structured_handoff; A13/R13_no_authority_escalation",
        interpretation="Typed outcomes after applying traced negation-parity rules.",
        value=("positive", "negative", "unknown"),
    )
)
POSITIVE, NEGATIVE, UNKNOWN_POLARITY = POLARITY_STATES

@dataclass(frozen=True)
class Declaration:
    field: str
    polarity: str
    source_form: str  # evidence only; must never decide a predicate
    key_path: str
    # T2-SP-UPSTREAM-CM-v2. Mapping keys of the scope this declaration was
    # written in, so its structural position can be resolved. List indices are
    # deliberately absent, exactly as in `Leaf.segments`.
    scope_segments: tuple[str, ...] = ()


def _record_declaration(item: dict, key_path: str) -> Declaration | None:
    """`{field: X, prohibited: true}` -> (X, negative).  Never (prohibited, ...).

    ST04-V3-IR-002: the previous collector added the QUALIFIER's key name to the
    prohibition set instead of the field the qualifier applies to, so the record
    form produced `declared=['prohibited']`.
    """
    name = None
    for nk in DECLARATION_FIELD_NAME_TOKENS:
        v = item.get(nk)
        if isinstance(v, str) and v.strip():
            name = v.strip()
            break
    if name is None:
        scalars = [
            (k, v) for k, v in item.items() if isinstance(v, str) and not is_negated(str(k))
        ]
        if len(scalars) == 1:
            name = scalars[0][1]
    if name is None:
        return None
    for k, v in item.items():
        if is_negated(str(k)):
            state = classify_enablement(v)
            polarity = NEGATIVE if state == ENABLED else POSITIVE
            return Declaration(normalize_field_name(name), polarity, "list_of_records", key_path)
    return None


def normalize_field_name(name: str) -> str:
    return "_".join(tokens(name))


def extract_declarations(
    scope: Any, scope_path: str = "", scope_segments: tuple[str, ...] = ()
) -> list[Declaration]:
    """All (field, polarity) declarations in a scope, from any source form.

    The five forms below MUST produce the same field/polarity pair.  Only
    `source_form` differs, and `source_form` is evidence, never a decision input.

    Every declaration produced for one declaring key is stamped with that key's
    mapping-key segments, so `adapt_declarations` can ask the structural binding
    whether the position was a declaration name at all.
    """
    out: list[Declaration] = []
    if not isinstance(scope, dict):
        return out

    # Every branch below ends in `continue`, so the stamp is applied to the
    # entries the PREVIOUS declaring key produced, plus once after the loop.
    pending: tuple[int, tuple[str, ...]] | None = None

    def stamp() -> None:
        if pending is None:
            return
        start, segs = pending
        for i in range(start, len(out)):
            out[i] = replace(out[i], scope_segments=segs)

    for key, value in scope.items():
        stamp()
        pending = None
        ks = str(key)
        path = f"{scope_path}.{ks}" if scope_path else ks
        if not is_negated(ks):
            continue
        pending = (len(out), scope_segments + (ks,))
        base = strip_negation(ks)

        # form 1: negation prefix or suffix on a concrete field name
        #   prohibited_private_reasoning: true   /   private_reasoning_disabled: true
        if base and not is_schema_meta_key(ks) and not isinstance(value, (dict, list)):
            state = classify_enablement(value)
            if state == ENABLED:
                out.append(
                    Declaration(normalize_field_name(base), NEGATIVE, "negation_affix", path)
                )
                continue
            if isinstance(value, str) and value.strip():
                out.append(
                    Declaration(normalize_field_name(value), NEGATIVE, "negation_affix", path)
                )
                continue
            # `prohibited_X: false` says X is NOT prohibited.
            out.append(
                Declaration(normalize_field_name(base), POSITIVE, "negation_affix", path)
            )
            continue

        # form 2: scalar naming the prohibited field
        #   prohibition: private_reasoning
        if isinstance(value, str) and value.strip():
            out.append(
                Declaration(normalize_field_name(value), NEGATIVE, "scalar", path)
            )
            continue

        # form 3: mapping of field -> truth
        #   prohibited_fields: {private_reasoning: true}
        if isinstance(value, dict):
            for k2, v2 in value.items():
                state = classify_enablement(v2)
                polarity = NEGATIVE if state == ENABLED else POSITIVE
                out.append(
                    Declaration(normalize_field_name(str(k2)), polarity, "mapping", f"{path}.{k2}")
                )
            continue

        # forms 4 and 5: list of names, or list of records
        if isinstance(value, list):
            for i, item in enumerate(value):
                ip = f"{path}[{i}]"
                if isinstance(item, str) and item.strip():
                    out.append(
                        Declaration(normalize_field_name(item), NEGATIVE, "list", ip)
                    )
                elif isinstance(item, dict):
                    rec = _record_declaration(item, ip)
                    if rec is not None:
                        out.append(rec)
            continue
    stamp()
    return out


def extract_declarations_recursive(
    data: Any, scope_path: str = "", scope_segments: tuple[str, ...] = ()
) -> list[Declaration]:
    """`extract_declarations` over every mapping in the document.

    A prohibition wrapped in a transparent container is the same prohibition
    (S03).  Scanning only the document root made the wrapper delete it.

    T2-SP-UPSTREAM-CM-v2 threads the mapping-key segments alongside the display
    path, so a caller can ask the structural binding what kind of position a
    declaration was written at.  List indices stay out of the segments for the
    same reason they stay out of `Leaf.segments`: `[0]` is a rendering, not a
    position.
    """
    out: list[Declaration] = []
    if isinstance(data, dict):
        out.extend(extract_declarations(data, scope_path, scope_segments))
        for k, v in data.items():
            ks = str(k)
            child = f"{scope_path}.{ks}" if scope_path else ks
            if is_negated(ks) and not is_schema_meta_key(ks):
                # Already consumed at THIS scope, in whichever of the five
                # declaration forms it was written. Recursing into it would
                # extract the same prohibition a second time at a position one
                # level deeper than the one it was actually declared at — for
                # the list-of-records form, at `prohibited_fields.prohibited`,
                # which is not where anybody declared anything. One declaration
                # must have one position, or the structural gate is asked about
                # a place the author never wrote to.
                continue
            if isinstance(v, (dict, list)):
                out.extend(
                    extract_declarations_recursive(v, child, scope_segments + (ks,))
                )
    elif isinstance(data, list):
        for i, item in enumerate(data):
            out.extend(
                extract_declarations_recursive(
                    item, f"{scope_path}[{i}]", scope_segments
                )
            )
    return out


# --------------------------------------------------------------------------
# Markdown block parsing
# --------------------------------------------------------------------------

MARKDOWN_BLOCK_PATTERNS = rule(
    "V-PARSE-05",
    kind="mapping",
    authority="C-08 end_to_end_semantic_boundary; A11/R11_workflow_and_entry_thinness",
    interpretation=(
        "Structural Markdown blocks admitted by the parser. No serialized line "
        "directly decides acceptance; parsed blocks are still offered to an "
        "adapter. Key-value labels have no arbitrary authored length ceiling."
    ),
    value={
        "atx": r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$",
        "setext": r"^\s{0,3}(=+|-+)\s*$",
        "bullet": r"^\s*[-*+]\s+(.+?)\s*$",
        "ordered": r"^\s*\d+[.)]\s+(.+?)\s*$",
        "table_row": r"^\s*\|(.+)\|\s*$",
        "table_sep": r"^\s*\|[\s:\-|]+\|\s*$",
        "key_value": r"^\s*([^:：#|][^:：]*)[:：]\s*(.*)$",
        "definition_marker": r"^\s*[:：](\s+.*)?$",
    },
)
_ATX = re.compile(MARKDOWN_BLOCK_PATTERNS["atx"])
_SETEXT = re.compile(MARKDOWN_BLOCK_PATTERNS["setext"])
_BULLET = re.compile(MARKDOWN_BLOCK_PATTERNS["bullet"])
_ORDERED = re.compile(MARKDOWN_BLOCK_PATTERNS["ordered"])
_TABLE_ROW = re.compile(MARKDOWN_BLOCK_PATTERNS["table_row"])
_TABLE_SEP = re.compile(MARKDOWN_BLOCK_PATTERNS["table_sep"])
_KEY_VALUE = re.compile(MARKDOWN_BLOCK_PATTERNS["key_value"])
_DEF_MARKER = re.compile(MARKDOWN_BLOCK_PATTERNS["definition_marker"])


@dataclass
class MarkdownBlocks:
    headings: list[str] = dc_field(default_factory=list)
    list_items: list[str] = dc_field(default_factory=list)
    table_cells: list[str] = dc_field(default_factory=list)
    definition_terms: list[str] = dc_field(default_factory=list)
    key_value_keys: list[str] = dc_field(default_factory=list)
    key_value_values: list[str] = dc_field(default_factory=list)
    table_rows: list[list[str]] = dc_field(default_factory=list)

    def structured_strings(self) -> list[str]:
        return (
            self.headings
            + self.list_items
            + self.table_cells
            + self.definition_terms
            + self.key_value_keys
            + self.key_value_values
        )

    def collections(self) -> list[list[str]]:
        """Grouped by the block that holds them; see core.collection_strings."""
        groups: list[list[str]] = [
            list(self.headings),
            list(self.list_items),
            list(self.definition_terms),
            list(self.key_value_keys),
        ]
        groups.extend(list(row) for row in self.table_rows)
        if self.table_rows:
            # a table column is also one collection: three rows each naming one
            # identifier is a catalog, and grouping only by row would miss it.
            width = max(len(r) for r in self.table_rows)
            for col in range(width):
                groups.append([r[col] for r in self.table_rows if len(r) > col])
        return [g for g in groups if g]


def parse_markdown_blocks(text: str) -> MarkdownBlocks:
    """A block parser, not a line-level keyword scan.

    ST04-V2-IR-005 and ST04-V3-IR-007 are both "an equally structured entry form
    was not in the recognised list".  The forms below are recognised as blocks,
    so a catalog cannot hide by choosing headings instead of a table.
    """
    blocks = MarkdownBlocks()
    lines = text.splitlines()
    in_fence = False
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue

        m = _ATX.match(raw)
        if m:
            blocks.headings.append(m.group(1).strip())
            continue

        if i + 1 < len(lines) and _SETEXT.match(lines[i + 1]) and not _BULLET.match(raw):
            blocks.headings.append(stripped)
            continue

        if _TABLE_ROW.match(raw) and not _TABLE_SEP.match(raw):
            cells = [c.strip() for c in _TABLE_ROW.match(raw).group(1).split("|")]
            cells = [c for c in cells if c]
            blocks.table_cells.extend(cells)
            if cells:
                blocks.table_rows.append(cells)
            continue

        m = _BULLET.match(raw) or _ORDERED.match(raw)
        if m:
            item = m.group(1).strip()
            blocks.list_items.append(item)
            kv = _KEY_VALUE.match(item)
            if kv:
                blocks.key_value_keys.append(kv.group(1).strip())
                if kv.group(2).strip():
                    blocks.key_value_values.append(kv.group(2).strip())
            continue

        # definition-list term: the next non-empty line begins with a marker
        for j in range(i + 1, min(i + 3, len(lines))):
            nxt = lines[j].strip()
            if not nxt:
                continue
            if _DEF_MARKER.match(lines[j]):
                blocks.definition_terms.append(stripped)
            break

        kv = _KEY_VALUE.match(raw)
        if kv:
            blocks.key_value_keys.append(kv.group(1).strip())
            if kv.group(2).strip():
                blocks.key_value_values.append(kv.group(2).strip())
    return blocks


# --------------------------------------------------------------------------
# documents
# --------------------------------------------------------------------------

YAML_SUFFIXES = frozenset(
    rule(
        "V-PARSE-01",
        kind="mapping",
        authority="C-08 end_to_end_semantic_boundary",
        interpretation=(
            "File suffixes routed to the strict YAML parser. This chooses a parser, "
            "not an acceptance outcome; unsupported suffixes remain visible as other."
        ),
        value={".yml", ".yaml"},
    )
)
MARKDOWN_SUFFIXES = frozenset(
    rule(
        "V-PARSE-02",
        kind="mapping",
        authority="C-08 end_to_end_semantic_boundary",
        interpretation=(
            "File suffixes routed to the structural Markdown parser. Meaning is "
            "still attached only by a registered adapter."
        ),
        value={".md", ".markdown"},
    )
)


@dataclass
class Document:
    doc_id: str
    rel_path: str
    fmt: str  # yaml | markdown | other
    surface: str  # mechanism | boot | registry | catalog_owner | workflow_or_entry | other
    data: Any = None
    blocks: MarkdownBlocks | None = None
    parse_error: str | None = None
    # T2-SP-UPSTREAM-CM-v2. Attached by discovery from the evaluator's own
    # binding, keyed by this document's opaque discovery identity. `None` means
    # nothing was attached, which resolves every position to `unknown`.
    provenance: PositionProvenance | None = None

    @property
    def parsed(self) -> bool:
        return self.parse_error is None

    def structured_strings(self) -> list[str]:
        if self.fmt == "yaml" and self.parsed:
            return yaml_structured_strings(self.data)
        if self.fmt == "markdown" and self.blocks is not None:
            return self.blocks.structured_strings()
        return []

    def collections(self) -> list[list[str]]:
        if self.fmt == "yaml" and self.parsed:
            return collection_strings(self.data)
        if self.fmt == "markdown" and self.blocks is not None:
            return self.blocks.collections()
        return []


SURFACE_DECLARATION_NAME = rule(
    "V-DISC-03",
    kind="mapping",
    authority="C-08; the candidate fixture's declared discovery contract",
    interpretation=(
        "The unique root-relative document that declares surface membership. "
        "Discovery fails if it is absent instead of inferring from directories."
    ),
    value="surface_declaration.yml",
)


def load_surface_declaration(root: Path) -> dict[str, Any]:
    path = root / SURFACE_DECLARATION_NAME
    if not path.is_file():
        raise FileNotFoundError(
            f"{SURFACE_DECLARATION_NAME} is the declared discovery route and is missing under {root}"
        )
    return load_yaml_strict(path.read_text(encoding="utf-8"))


def _surface_of(rel: str, decl: dict[str, Any]) -> str:
    rel_norm = rel.replace("\\", "/")
    if rel_norm == decl.get("catalog_owner"):
        return "catalog_owner"
    for surface, prefixes in (decl.get("surface_prefixes") or {}).items():
        for prefix in prefixes:
            if rel_norm.startswith(prefix):
                return surface
    return "other"


def discover_documents(
    root: Path, binding: StructuralBinding | None = None
) -> list[Document]:
    """Content-first discovery.

    Surface MEMBERSHIP comes from the declared prefixes, because A11 is itself
    stated in terms of "workflow stages and the stable development entry" — a
    surface, not a file name.  What a document MEANS is decided by an adapter in
    `adapters.py`, never by its file name, its directory or a schema_version
    token.  ST04-IR-003 was closed on that basis and stays closed.
    """
    decl = load_surface_declaration(root)
    # The binding is the EVALUATOR's, so it is loaded from the evaluator package
    # and not from `root`. A corpus cannot supply, shadow or extend it.
    struct = binding if binding is not None else load_structural_binding()
    docs: list[Document] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel == SURFACE_DECLARATION_NAME:
            continue
        surface = _surface_of(rel, decl)
        if surface == "other":
            continue
        suffix = path.suffix.lower()
        if suffix in YAML_SUFFIXES:
            fmt = "yaml"
        elif suffix in MARKDOWN_SUFFIXES:
            fmt = "markdown"
        else:
            fmt = "other"
        doc = Document(
            doc_id=rel,
            rel_path=rel,
            fmt=fmt,
            surface=surface,
            # `rel` is an opaque lookup key here. It is compared for equality
            # and never segmented or interpreted; surface membership above is
            # the only place a path is read structurally.
            provenance=struct.for_document(rel),
        )
        text = path.read_text(encoding="utf-8")
        if fmt == "yaml":
            try:
                doc.data = load_yaml_strict(text)
            except Exception as exc:  # a document that will not parse is visible, not silent
                doc.parse_error = f"{type(exc).__name__}: {exc}"
        elif fmt == "markdown":
            doc.blocks = parse_markdown_blocks(text)
        docs.append(doc)
    return docs

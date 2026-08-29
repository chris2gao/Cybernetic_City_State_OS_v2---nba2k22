#!/usr/bin/env python3
"""Orchestration: documents in, typed decision facts out.

Schema: 03_语义模型/normalized_semantic_fact_model_v1.yml

This module used to be 773 lines of extraction heuristics, and the independent
review's AB-01 finding was aimed squarely at it: "facts.py still decides
semantics with closed token sets, recognized path positions and shape rules …
representation bias moved into the extractor".

It is now a router.  It decides which adapter is offered which document and
nothing else.  Every judgement lives in `adapters.py` behind a declared
applicability, and every vocabulary those adapters use is bound to an A
requirement in `vocabulary.py`.  There is deliberately no code path here that can
"best-effort infer" anything: a document no adapter claims contributes no facts,
and a document that will not parse becomes a visible `UnsupportedFact`.

`FactSet` carries decision facts only.  Rendering observations go to
`FactSet.evidence`, which no predicate receives.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from pathlib import Path

from .adapters import (
    adapt_authority,
    adapt_autonomy,
    adapt_carried_fields,
    adapt_catalog_claims,
    adapt_declaration_refusals,
    adapt_declarations,
    adapt_entry_modes,
    adapt_provider_ambiguities,
    adapt_provider_bindings,
    adapt_roles,
    adapt_structural_refusals,
    adapt_window_identity,
    live_catalog_identifiers,
)
from .core import Document, discover_documents, tokens, walk_nodes
from .decision_facts import (
    AuthorityFact,
    AutonomyFact,
    CarriedFieldFact,
    CatalogFact,
    DeclarationFact,
    EntryModeFact,
    EvidenceSet,
    ProviderBindingFact,
    RoleFact,
    UnsupportedFact,
    UntracedRuleFact,
    WindowIdentityFact,
)
from .provenance import untraced_rules
from .vocabulary import DECLARING_SURFACES, HANDOFF_RECORD_TOKENS


@dataclass
class FactSet:
    """Typed decision facts.  Nothing here records how anything was written."""

    documents: list[Document] = dc_field(default_factory=list)
    roles: list[RoleFact] = dc_field(default_factory=list)
    provider_bindings: list[ProviderBindingFact] = dc_field(default_factory=list)
    window_identities: list[WindowIdentityFact] = dc_field(default_factory=list)
    entry_modes: list[EntryModeFact] = dc_field(default_factory=list)
    declarations: list[DeclarationFact] = dc_field(default_factory=list)
    carried_fields: list[CarriedFieldFact] = dc_field(default_factory=list)
    autonomy: list[AutonomyFact] = dc_field(default_factory=list)
    authority: list[AuthorityFact] = dc_field(default_factory=list)
    catalogs: list[CatalogFact] = dc_field(default_factory=list)
    unsupported: list[UnsupportedFact] = dc_field(default_factory=list)
    untraced_rules: list[UntracedRuleFact] = dc_field(default_factory=list)
    live_catalog_identifiers: list[str] = dc_field(default_factory=list)
    evidence: EvidenceSet = dc_field(default_factory=EvidenceSet)

    def docs_by_surface(self, surface: str) -> list[Document]:
        return [d for d in self.documents if d.surface == surface]


def _is_handoff_document(doc: Document) -> bool:
    """A document carrying a handoff record, at any container depth.

    Gated deliberately narrowly.  Collecting prohibition declarations from every
    document would let one artifact's prohibitions satisfy A09 on another's
    behalf, which is a weakening of exactly the kind AB-02 names.
    """
    if doc.fmt != "yaml" or not doc.parsed or not isinstance(doc.data, dict):
        return False
    for node in walk_nodes(doc.data):
        tok = set(tokens(node.innermost))
        if HANDOFF_RECORD_TOKENS <= tok:
            return True
    return False


def build_fact_set(root: Path) -> FactSet:
    docs = discover_documents(root)
    fs = FactSet(documents=docs)
    fs.live_catalog_identifiers = live_catalog_identifiers(docs)
    ev = fs.evidence

    for r in untraced_rules():
        fs.untraced_rules.append(
            UntracedRuleFact(rule_id=r.rule_id, kind=r.kind, interpretation=r.interpretation)
        )

    for doc in docs:
        if doc.fmt == "yaml" and not doc.parsed:
            fs.unsupported.append(
                UnsupportedFact(doc.doc_id, "", f"yaml_parse_failed: {doc.parse_error}")
            )
            continue

        fs.roles.extend(adapt_roles(doc, ev))
        fs.window_identities.extend(adapt_window_identity(doc, ev))
        fs.entry_modes.extend(adapt_entry_modes(doc, ev))

        # A structurally refused position is reported, not dropped. Correct
        # behaviour and an incomplete binding must not look the same.
        #
        # The report is limited to the scans this document is actually offered
        # below. Reporting a payload-scope refusal on a document that no
        # handoff scan ever reads would invent a coverage hole out of a
        # container that scan has no opinion about.
        scans = {"entry_mode", "role", "window"}
        if doc.surface in DECLARING_SURFACES:
            scans |= {"provider_ambiguity", "authority", "autonomy"}
        if _is_handoff_document(doc):
            scans |= {"carried_field"}
        fs.unsupported.extend(
            adapt_structural_refusals(doc, ev, frozenset(scans))
        )

        if doc.surface in DECLARING_SURFACES:
            fs.provider_bindings.extend(adapt_provider_bindings(doc, ev))
            fs.unsupported.extend(adapt_provider_ambiguities(doc, ev))
            fs.autonomy.extend(adapt_autonomy(doc, ev))
            fs.authority.extend(adapt_authority(doc, ev))

        if _is_handoff_document(doc):
            fs.carried_fields.extend(adapt_carried_fields(doc, ev))
            fs.declarations.extend(adapt_declarations(doc, ev))
            # A declaration the structural binding refused is a decision fact,
            # not a note. The evidence set is rendering detail that no predicate
            # reads, so a refusal recorded only there would leave a document
            # whose only claim candidate is a declaration silently empty.
            fs.unsupported.extend(adapt_declaration_refusals(doc, ev))

        if doc.surface == "workflow_or_entry":
            fs.catalogs.extend(
                adapt_catalog_claims(doc, fs.live_catalog_identifiers, ev)
            )
    return fs

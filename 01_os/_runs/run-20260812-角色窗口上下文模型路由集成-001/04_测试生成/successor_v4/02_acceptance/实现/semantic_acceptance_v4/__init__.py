"""successor_v4 coverage extension.

The independently accepted methodology at
19c39ed37f14c97cfa132ffafabcb9afa33dd7f0 implements seven A-level predicates
(A01, A02, A06, A09, A11, A13, A14) and states, in its own coverage note, that
"a full replacement package would extend the same fact model" to the remaining
criteria.  This package is that extension.  It covers A03, A04, A05, A07, A08,
A10 and A12.

Three properties are preserved by construction, not by review judgement:

  * the vendored engine is byte-identical to the accepted package.  Nothing here
    edits it.  Extension happens by registering additional predicates into the
    shared `semantic_acceptance.predicates.REGISTRY` and by attaching additional
    typed fact lists to the FactSet instance;
  * every decision-bearing constant is declared through
    `semantic_acceptance.provenance.rule` with an authority naming an A
    requirement, so the C-09 ledger covers v4 rules on the same terms;
  * v4 decision facts carry no field named in
    `semantic_acceptance.decision_facts.RENDERING_FIELD_NAMES`, so the C-08
    representation boundary holds for the extension too.
"""

from __future__ import annotations

__all__ = [
    "vocabulary_v4",
    "facts_v4",
    "adapters_v4",
    "predicates_v4",
    "evaluate_v4",
]

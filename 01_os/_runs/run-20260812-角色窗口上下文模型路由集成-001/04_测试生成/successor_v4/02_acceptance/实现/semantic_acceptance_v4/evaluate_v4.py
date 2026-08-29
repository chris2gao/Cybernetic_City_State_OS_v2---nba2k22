#!/usr/bin/env python3
"""Full-coverage evaluation entry point: the accepted seven plus the v4 seven.

    python -m semantic_acceptance_v4.evaluate_v4 <candidate-root> [--json]

The accepted engine's `build_fact_set` is called unchanged and its FactSet is
then augmented with the v4 fact lists.  Augmentation is by attribute rather than
by editing the FactSet dataclass, because the vendored engine is byte-identical
to the independently accepted package and stays that way; `v4_facts.py` in an
earlier draft that edited `facts.py` would have destroyed exactly the evidence
that makes the vendoring checkable.

Quiet-output discipline (01_os/开发入口与单窗口任务规范_v1.md#1.2): one line per
predicate on success, detail only where something failed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from semantic_acceptance.evaluate import as_dict, overall, render
from semantic_acceptance.facts import FactSet, build_fact_set
from semantic_acceptance.predicates import PredicateResult, evaluate_all

from . import adapters_v4 as A
from . import predicates_v4  # noqa: F401  - registers P21..P27
from .facts_v4 import V4_FACT_SET_ATTRIBUTES


def augment_fact_set(fs: FactSet) -> FactSet:
    """Attach the v4 typed fact lists to an already-built FactSet."""
    for name in V4_FACT_SET_ATTRIBUTES:
        setattr(fs, name, [])
    ev = fs.evidence

    for doc in fs.documents:
        fs.v4_lifecycles.extend(A.adapt_lifecycle(doc, ev))
        fs.v4_lifecycle_conditions.extend(A.adapt_lifecycle_conditions(doc, ev))
        fs.v4_context_contracts.extend(A.adapt_context_contract(doc, ev))
        fs.v4_context_load_entries.extend(A.adapt_context_load_entries(doc, ev))
        fs.v4_preload_positions.extend(A.adapt_preload_positions(doc, ev))
        fs.v4_freshness_bindings.extend(A.adapt_freshness_binding(doc, ev))
        fs.v4_freshness_triggers.extend(A.adapt_freshness_triggers(doc, ev))
        fs.v4_route_receipts.extend(A.adapt_route_receipts(doc, ev))
        fs.v4_independence.extend(A.adapt_independence(doc, ev))
        fs.v4_family_requirements.extend(A.adapt_family_requirements(doc, ev))
        fs.v4_mechanism_separation.extend(A.adapt_mechanism_separation(doc, ev))
        fs.v4_failure_cases.extend(A.adapt_failure_cases(doc, ev))
        fs.v4_fallback_positions.extend(A.adapt_fallback_positions(doc, ev))
        fs.unsupported.extend(A.adapt_v4_ambiguities(doc, ev))
    return fs


def build_full_fact_set(root: Path) -> FactSet:
    return augment_fact_set(build_fact_set(root))


def evaluate_full(root: Path) -> list[PredicateResult]:
    return evaluate_all(build_full_fact_set(root))


def result_vector(results: list[PredicateResult]) -> dict[str, str]:
    return {r.predicate_id: r.status for r in results}


def as_full_dict(root: Path, results: list[PredicateResult]) -> dict[str, Any]:
    payload = as_dict(root, results)
    payload["coverage"] = coverage_summary(results)
    return payload


A_CRITERIA_BY_PREDICATE = {
    "P01": "A01",
    "P02": "A02",
    "P03": "A06",
    "P04": "A09",
    "P05": "A13",
    "P06": "A14",
    "P07": "A11",
    "P21": "A03",
    "P22": "A04",
    "P23": "A05",
    "P24": "A07",
    "P25": "A08",
    "P26": "A10",
    "P27": "A12",
}

ALL_A_CRITERIA = tuple(f"A{n:02d}" for n in range(1, 15))


def coverage_summary(results: list[PredicateResult]) -> dict[str, Any]:
    """What this package claims to cover, stated as its own exact proposition.

    AGENT_WORKING_DISCIPLINE.md#5: a passing test proves its own exact
    proposition and nothing wider. The accepted methodology covered seven of the
    fourteen A success criteria and said so; this package covers fourteen and
    says so here rather than leaving a reader to count.
    """
    covered = sorted({A_CRITERIA_BY_PREDICATE[r.predicate_id] for r in results if r.predicate_id in A_CRITERIA_BY_PREDICATE})
    return {
        "a_success_criteria_total": len(ALL_A_CRITERIA),
        "a_success_criteria_covered": covered,
        "a_success_criteria_not_covered": [a for a in ALL_A_CRITERIA if a not in covered],
        "predicate_to_criterion": dict(sorted(A_CRITERIA_BY_PREDICATE.items())),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path, help="candidate surface root")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    results = evaluate_full(args.root)
    if args.json:
        print(json.dumps(as_full_dict(args.root, results), ensure_ascii=False, indent=2))
    else:
        print(render(results, args.verbose))
    return 0 if overall(results) == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

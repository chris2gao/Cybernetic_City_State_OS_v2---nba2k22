"""C-09: every decision-bearing rule has an authority, and none is invented.

AB-02's proof was `CATALOG_RESTATEMENT_THRESHOLD = 3`.  It was not wrong because
3 is a bad number; it was wrong because nothing said 3, and it weakened A11 by
exactly the amount nobody had authorised.  A predicate-level `P07 -> A11` label
did not catch it, because the label was true and the constant beneath it was not
covered by the label.

So the check here is not "is there a trace somewhere".  It is: enumerate the
constants that can change an acceptance outcome, and require each one to name its
authority, its interpretation, and what it rejected.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import _bootstrap
from _bootstrap import BASELINE

from semantic_acceptance import provenance, vocabulary
from semantic_acceptance.corpus import copy_tree
from semantic_acceptance.evaluate import evaluate_tree, overall
from semantic_acceptance.facts import build_fact_set
from semantic_acceptance.predicates import PASS, REGISTRY, UNSUPPORTED
from semantic_acceptance.provenance import HUMAN_REQUIRED, DecisionRule


def test_every_declared_rule_carries_an_authority_and_an_interpretation():
    assert provenance.REGISTRY, "no decision rules declared"
    thin = [
        r.rule_id
        for r in provenance.REGISTRY.values()
        if not r.authority.strip() or not r.interpretation.strip()
    ]
    assert thin == [], thin


def test_no_rule_is_untraced():
    """A rule marked HUMAN_REQUIRED is a stop, not a default."""
    untraced = [r.rule_id for r in provenance.untraced_rules()]
    assert untraced == [], untraced


def test_the_deleted_threshold_is_gone_and_its_replacement_is_traced():
    """The specific constant the review named."""
    import semantic_acceptance.predicates as p

    assert not hasattr(p, "CATALOG_RESTATEMENT_THRESHOLD")
    rule = provenance.REGISTRY["V-CAT-01"]
    assert rule.value == 2
    assert "A11" in rule.authority
    assert any("CATALOG_RESTATEMENT_THRESHOLD" in r for r in rule.rejected_alternatives)


def test_every_threshold_records_what_it_rejected():
    """A number with no rejected alternative was never a decision, only a guess."""
    thin = [
        r.rule_id
        for r in provenance.REGISTRY.values()
        if r.kind == "threshold" and not r.rejected_alternatives
    ]
    assert thin == [], thin


def test_b_only_facts_cannot_reach_a_decision():
    """ST04-V3-IR-004 in structural form.

    run_id is recorded on a separate field from the A-required facts, so a
    predicate cannot require it by accident; and the predicate that consumes
    window identity checks only the A-required tuple.
    """
    assert "run" not in vocabulary.A_REQUIRED_IDENTITY_FACTS
    assert "run" in vocabulary.B_ONLY_IDENTITY_FACTS
    fs = build_fact_set(BASELINE)
    assert fs.window_identities
    for wi in fs.window_identities:
        assert "run" not in wi.bound_facts
        assert "run" in wi.b_only_facts


def test_every_predicate_carries_an_a_trace():
    for pid, (_title, a_trace, _fn) in REGISTRY.items():
        assert a_trace, pid


def test_an_untraced_rule_is_reported_and_not_applied():
    """The mechanism, exercised rather than asserted.

    A temporary untraced rule must surface as P09 UNSUPPORTED, which means the
    tree stops being accepted until a Human supplies the requirement.  This is
    what prevents the next missing authority from being quietly invented.
    """
    injected = "V-TEST-UNTRACED"
    provenance.REGISTRY[injected] = DecisionRule(
        rule_id=injected,
        kind="threshold",
        authority=HUMAN_REQUIRED,
        interpretation="a threshold no requirement supports",
        value=3,
    )
    try:
        results = evaluate_tree(BASELINE)
        p09 = [r for r in results if r.predicate_id == "P09"]
        assert p09, [r.predicate_id for r in results]
        assert p09[0].status == UNSUPPORTED
        assert overall(results) != PASS
    finally:
        provenance.REGISTRY.pop(injected, None)
    assert overall(evaluate_tree(BASELINE)) == PASS


def test_the_ledger_can_be_emitted_and_is_self_consistent():
    ledger = provenance.as_ledger()
    assert ledger["rule_count"] == len(provenance.REGISTRY)
    assert ledger["untraced_rule_count"] == 0
    ids = [r["rule_id"] for r in ledger["rules"]]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


if __name__ == "__main__":
    for _name, _fn in sorted(list(globals().items())):
        if _name.startswith("test_"):
            _fn()
    print("decision provenance ok")

#!/usr/bin/env python3
"""Combined accepted-plus-v4 decision provenance audit.  P2-2 work item 2.

C-09 says a constant may decide acceptance only if it is declared in
`semantic_acceptance.provenance` with an authority naming an A requirement or an
explicit Human decision.  `vendored_baseline_tests/test_provenance.py` enforces
that for the accepted package.  Nothing enforced it for the COMBINED package,
and the difference was not academic:

    the committed 01_semantic_binding/decision_provenance_v4.yml carried 76
    rules.  Importing both packages and regenerating the ledger yields 128.
    All 52 missing ids are V4-* - the rules that decide P21 through P27.

The ledger had been generated with only the accepted package imported, so the
durable provenance record for a fourteen-predicate package documented seven
predicates' worth of constants.  Every V4-* rule did carry an authority; none
was untraced.  The hole was coverage, not authority, which is why nothing
failed and why only a combined audit could see it.

This module regenerates the ledger from both packages and requires the
committed file to equal it.  `write_ledger()` is the single writer, so the
committed artifact and the assertion can never drift apart.
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

import _bootstrap_v4  # noqa: F401
from _bootstrap_v4 import SUCCESSOR_V4_ROOT

from semantic_acceptance.core import dump_yaml, load_yaml_strict
from semantic_acceptance.provenance import HUMAN_REQUIRED, as_ledger, untraced_rules

LEDGER_PATH = SUCCESSOR_V4_ROOT / "01_semantic_binding" / "decision_provenance_v4.yml"


HEADER = {
    "schema_version": "citystate.stage04.decision_provenance.v4",
    "task_id": "os-v2-t2-completion-001",
    "generated_by": (
        "semantic_acceptance.provenance.as_ledger() with BOTH semantic_acceptance "
        "and semantic_acceptance_v4 fully imported"
    ),
    "generation_is_machine_derived_not_authored": True,
    "coverage": (
        "the accepted seven-predicate constants and the v4 seven-predicate "
        "constants, in one ledger"
    ),
}


def _import_every_module():
    """Rules register on import, so a partial import is a partial ledger.

    This is the defect this module exists to prevent: importing the packages by
    name alone leaves submodules unimported and their `rule()` calls unmade, and
    the resulting ledger looks complete because nothing counts what is absent.
    """
    import semantic_acceptance
    import semantic_acceptance_v4

    for pkg in (semantic_acceptance, semantic_acceptance_v4):
        base = Path(pkg.__file__).parent
        for mod in pkgutil.iter_modules([str(base)]):
            importlib.import_module(f"{pkg.__name__}.{mod.name}")


def build_ledger() -> dict:
    _import_every_module()
    led = as_ledger()
    untraced = [r.rule_id for r in untraced_rules()]
    payload = dict(HEADER)
    payload["rule_count"] = led["rule_count"]
    payload["untraced_rule_count"] = len(untraced)
    payload["untraced_rule_ids"] = sorted(untraced)
    payload["rules"] = led["rules"]
    return payload


def write_ledger() -> Path:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_bytes(dump_yaml(build_ledger()).encode("utf-8"))
    return LEDGER_PATH


# ---------------------------------------------------------------------------
# the audit
# ---------------------------------------------------------------------------


def test_no_decision_rule_is_untraced():
    """C-09's actual proposition: nothing decides acceptance without authority."""
    led = build_ledger()
    assert led["untraced_rule_count"] == 0, led["untraced_rule_ids"]


def test_no_applied_rule_defers_its_authority_to_a_human_decision_never_made():
    """`HUMAN_REQUIRED` marks a rule no A text supports.  Such a rule is
    reported, never applied.  If one is in the ledger it must also be in the
    untraced list, or something is deciding on an authority that does not exist.
    """
    led = build_ledger()
    deferred = [r["rule_id"] for r in led["rules"] if r.get("authority") == HUMAN_REQUIRED]
    assert set(deferred) <= set(led["untraced_rule_ids"]), {
        "deferred": sorted(deferred),
        "untraced": led["untraced_rule_ids"],
    }


def test_rule_ids_are_unique():
    led = build_ledger()
    ids = [r["rule_id"] for r in led["rules"]]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    assert dupes == [], dupes


def test_the_ledger_covers_both_packages():
    """A combined ledger that contained no V4-* id would be the accepted-only
    ledger wearing a v4 filename, which is exactly the state this audit found.
    """
    led = build_ledger()
    ids = {r["rule_id"] for r in led["rules"]}
    v4_ids = {i for i in ids if i.startswith("V4-")}
    accepted_ids = ids - v4_ids
    assert v4_ids, "no V4-* rules in the ledger: the v4 package was not imported"
    assert accepted_ids, "no accepted rules in the ledger"


def test_every_v4_predicate_rule_family_is_present():
    """Each v4 predicate's rule family must actually be in the ledger.

    Stated as families rather than a count, because a count would pass while a
    whole family was missing as long as some other family grew.
    """
    led = build_ledger()
    ids = {r["rule_id"] for r in led["rules"]}
    families = ("V4-LIFE-", "V4-CTX-", "V4-FRESH-", "V4-RCT-", "V4-IND-", "V4-SEP-", "V4-FAIL-")
    missing = [f for f in families if not any(i.startswith(f) for i in ids)]
    assert missing == [], missing


def test_the_committed_ledger_is_current():
    """Evidence currency.  A committed ledger that no longer matches the code is
    a record of a package that no longer exists, and the reader cannot tell.
    """
    assert LEDGER_PATH.is_file(), str(LEDGER_PATH)
    committed = load_yaml_strict(LEDGER_PATH.read_text(encoding="utf-8"))
    fresh = build_ledger()

    committed_ids = {r["rule_id"] for r in committed.get("rules", [])}
    fresh_ids = {r["rule_id"] for r in fresh["rules"]}
    assert committed_ids == fresh_ids, {
        "missing_from_committed": sorted(fresh_ids - committed_ids),
        "stale_in_committed": sorted(committed_ids - fresh_ids),
    }
    assert committed.get("rule_count") == fresh["rule_count"], {
        "committed": committed.get("rule_count"), "fresh": fresh["rule_count"],
    }
    assert committed.get("rules") == fresh["rules"], "rule bodies differ from the code"


def test_no_vendor_name_reaches_the_ledger():
    """The accepted package asserts this of itself; the v4 half was never checked."""
    text = dump_yaml(build_ledger()).lower()
    vendors = ("openai", "anthropic", "claude", "gpt", "gemini", "codex", "mistral", "llama")
    found = [v for v in vendors if v in text]
    assert found == [], found

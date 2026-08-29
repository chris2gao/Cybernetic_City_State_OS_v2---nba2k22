#!/usr/bin/env python3
"""Requirement trace and test inventory.  P2-2 work items 4 and 5.

Two artifacts the parent checkpoint listed as not started:

    01_semantic_binding/requirement_trace_v4.yml
    02_acceptance/04_tests_v4.yml

Both are generated from the code and the test modules rather than authored, and
both are asserted current here.  An authored trace is a claim about the package;
a derived one is a reading of it, and only the second stays true when someone
changes the package and forgets the document.

What the trace answers is narrow and worth stating plainly: for each of the
fourteen A success criteria, which predicate decides it, which decision rules
name it as their authority, and which test modules exercise it.  It does not
claim the coverage is adequate.  Adequacy is a review judgement; this file only
makes the mapping checkable.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import re
from pathlib import Path

import _bootstrap_v4  # noqa: F401
from _bootstrap_v4 import SUCCESSOR_V4_ROOT

from semantic_acceptance.core import dump_yaml, load_yaml_strict
from semantic_acceptance.provenance import as_ledger

TRACE_PATH = SUCCESSOR_V4_ROOT / "01_semantic_binding" / "requirement_trace_v4.yml"
INVENTORY_PATH = SUCCESSOR_V4_ROOT / "02_acceptance" / "04_tests_v4.yml"
TESTS_DIR = Path(__file__).resolve().parent
VENDORED_TESTS_DIR = TESTS_DIR.parent / "vendored_baseline_tests"


def _import_every_module():
    import semantic_acceptance
    import semantic_acceptance_v4

    for pkg in (semantic_acceptance, semantic_acceptance_v4):
        base = Path(pkg.__file__).parent
        for mod in pkgutil.iter_modules([str(base)]):
            importlib.import_module(f"{pkg.__name__}.{mod.name}")


def _criteria_map() -> dict[str, str]:
    from semantic_acceptance_v4.evaluate_v4 import A_CRITERIA_BY_PREDICATE

    return dict(A_CRITERIA_BY_PREDICATE)


def _all_criteria() -> tuple[str, ...]:
    from semantic_acceptance_v4.evaluate_v4 import ALL_A_CRITERIA

    return tuple(ALL_A_CRITERIA)


def _predicate_titles() -> dict[str, str]:
    """Titles from the live predicate registry, not restated by hand."""
    from semantic_acceptance.predicates import REGISTRY

    out: dict[str, str] = {}
    for key, entry in REGISTRY.items():
        pid = getattr(entry, "predicate_id", None) or str(key)
        title = getattr(entry, "title", "") or ""
        out[str(pid)] = str(title)
    return out


def _test_sources() -> dict[str, str]:
    out = {}
    for d in (TESTS_DIR, VENDORED_TESTS_DIR):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("test_*.py")):
            out[f"{d.name}/{p.name}"] = p.read_text(encoding="utf-8")
    return out


def build_trace() -> dict:
    _import_every_module()
    by_pred = _criteria_map()
    by_crit: dict[str, list[str]] = {}
    for pid, crit in by_pred.items():
        by_crit.setdefault(crit, []).append(pid)

    titles = _predicate_titles()
    rules = as_ledger()["rules"]
    sources = _test_sources()

    entries = []
    for crit in _all_criteria():
        preds = sorted(by_crit.get(crit, []))
        # A rule belongs to a criterion when its own authority names it.  This
        # is the rule's statement about itself, not an inference from its id.
        rule_ids = sorted(
            r["rule_id"] for r in rules
            if crit in str(r.get("authority", ""))
        )
        exercised_by = sorted(
            name for name, text in sources.items()
            if any(re.search(rf"\b{p}\b", text) for p in preds)
        )
        entries.append({
            "criterion": crit,
            "deciding_predicates": preds,
            "predicate_titles": {p: titles.get(p, "") for p in preds},
            "rules_naming_this_criterion_as_authority": rule_ids,
            "test_modules_referencing_those_predicates": exercised_by,
        })

    return {
        "schema_version": "citystate.stage04.requirement_trace.v4",
        "task_id": "os-v2-t2-completion-001",
        "generated_by": "03_validation/v4_tests/test_v4_trace_and_inventory.build_trace()",
        "generation_is_machine_derived_not_authored": True,
        "what_this_does_not_claim": (
            "that the listed coverage is adequate. It states the mapping only; "
            "adequacy is an independent review judgement."
        ),
        "criteria_total": len(_all_criteria()),
        "criteria_with_a_deciding_predicate": sum(1 for e in entries if e["deciding_predicates"]),
        "criteria": entries,
    }


def build_inventory() -> dict:
    modules = []
    total = 0
    for name, text in _test_sources().items():
        funcs = sorted(set(re.findall(r"^def (test_[a-zA-Z0-9_]+)\(", text, re.M)))
        total += len(funcs)
        doc = ""
        m = re.search(r'^"""(.*?)$', text, re.M | re.S)
        if m:
            doc = m.group(1).strip().splitlines()[0].strip()
        modules.append({
            "module": name,
            "purpose": doc,
            "test_count": len(funcs),
            "tests": funcs,
        })

    return {
        "schema_version": "citystate.stage04.test_inventory.v4",
        "task_id": "os-v2-t2-completion-001",
        "generated_by": "03_validation/v4_tests/test_v4_trace_and_inventory.build_inventory()",
        "generation_is_machine_derived_not_authored": True,
        "scope": (
            "every test_*.py under 03_validation/v4_tests and "
            "03_validation/vendored_baseline_tests"
        ),
        "runners_are_separate_processes": (
            "vendored_baseline_tests must run in an interpreter that never "
            "imported semantic_acceptance_v4 (V4-FND-01), so the two suites are "
            "two commands and this inventory does not imply one run"
        ),
        "module_count": len(modules),
        "test_count_total": total,
        "modules": modules,
    }


def write_artifacts() -> tuple[Path, Path]:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRACE_PATH.write_bytes(dump_yaml(build_trace()).encode("utf-8"))
    INVENTORY_PATH.write_bytes(dump_yaml(build_inventory()).encode("utf-8"))
    return TRACE_PATH, INVENTORY_PATH


# ---------------------------------------------------------------------------
# assertions
# ---------------------------------------------------------------------------


def test_every_a_criterion_has_a_deciding_predicate():
    trace = build_trace()
    orphans = [e["criterion"] for e in trace["criteria"] if not e["deciding_predicates"]]
    assert orphans == [], orphans


def test_no_criterion_is_decided_by_two_predicates():
    """Two deciders for one criterion means the verdict depends on which one
    the reader looks at.  If that is ever intended it needs saying explicitly.
    """
    trace = build_trace()
    doubled = {e["criterion"]: e["deciding_predicates"]
               for e in trace["criteria"] if len(e["deciding_predicates"]) > 1}
    assert doubled == {}, doubled


def test_every_deciding_predicate_is_exercised_by_some_test_module():
    trace = build_trace()
    untested = [e["criterion"] for e in trace["criteria"]
                if e["deciding_predicates"] and not e["test_modules_referencing_those_predicates"]]
    assert untested == [], untested


def test_the_committed_trace_is_current():
    assert TRACE_PATH.is_file(), str(TRACE_PATH)
    committed = load_yaml_strict(TRACE_PATH.read_text(encoding="utf-8"))
    assert committed == build_trace(), "requirement_trace_v4.yml no longer matches the code"


def test_the_committed_inventory_is_current():
    assert INVENTORY_PATH.is_file(), str(INVENTORY_PATH)
    committed = load_yaml_strict(INVENTORY_PATH.read_text(encoding="utf-8"))
    assert committed == build_inventory(), "04_tests_v4.yml no longer matches the test modules"


def test_the_inventory_counts_agree_with_itself():
    inv = build_inventory()
    assert inv["test_count_total"] == sum(m["test_count"] for m in inv["modules"])
    assert inv["module_count"] == len(inv["modules"])

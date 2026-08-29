"""C-08: the semantic boundary is end to end, and that is machine-checkable.

AB-01 was not "a predicate happened to read a container field".  It was that
nothing structurally prevented it, so the violation had to be found by a human
reading code.  These tests make the boundary an assertion.

The strongest one is `test_the_subject_name_is_never_consulted`.  Vocabulary
freedom cannot be proved by grepping for vendor names — a list can always be
spelled differently.  It can be proved behaviourally: if the pipeline classifies
sixteen arbitrary subject strings identically, then the subject's spelling is not
an input.  That is the property ST04-V3-IR-005 and S09/S13 both violated.
"""

from __future__ import annotations

import ast
import tempfile
from dataclasses import fields as dataclass_fields
from pathlib import Path

import _bootstrap
from _bootstrap import BASELINE, PROTOTYPE_ROOT

from semantic_acceptance import adapters, predicates as predicates_module, provenance
from semantic_acceptance.corpus import ROLES, copy_tree, load, save
from semantic_acceptance.core import canonical_identifier
from semantic_acceptance.decision_facts import (
    DECISION_FACT_CLASSES,
    RENDERING_FIELD_NAMES,
)
from semantic_acceptance.evaluate import evaluate_tree, overall, result_vector
from semantic_acceptance.facts import build_fact_set
from semantic_acceptance.predicates import FAIL, PASS
from semantic_acceptance import vocabulary

PKG = PROTOTYPE_ROOT / "semantic_acceptance"

# Deliberately unlike anything in any list, including each other.
ARBITRARY_SUBJECTS = (
    "Halcyon-Reasoner-3",
    "zzq_nonexistent_vendor_9",
    "NacreCompute-QX",
    "ObsidianInference-R",
    "Kestrel-Engine",
    "JuniperReasoner",
    "мод-7",
    "模型甲",
    "a",
    "X" * 120,
    "vendor with spaces",
    "UPPER_SNAKE_THING",
    "dotted.name.v2",
    "trailing-dash-",
    "9781",
    "emoji-free-but-odd_%$#",
)


def test_decision_facts_declare_no_rendering_field():
    offenders = []
    for cls in DECISION_FACT_CLASSES:
        for f in dataclass_fields(cls):
            if f.name in RENDERING_FIELD_NAMES:
                offenders.append(f"{cls.__name__}.{f.name}")
    assert offenders == [], offenders


def _referenced_names(path: Path) -> set[str]:
    """Every identifier the module actually uses, ignoring docstrings and comments."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.keyword) and node.arg:
            names.add(node.arg)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            # a string subscript such as fact["source_form"] would also be a read
            parent_used = node.value
            if parent_used in RENDERING_FIELD_NAMES:
                names.add(parent_used)
    return names


def test_predicates_reference_no_rendering_field():
    """The exact violation the independent review found, now impossible to miss."""
    used = _referenced_names(PKG / "predicates.py")
    leaked = sorted(used & RENDERING_FIELD_NAMES)
    assert leaked == [], leaked


def test_rendering_evidence_still_exists_it_is_only_unreachable_from_a_predicate():
    """Separating the interfaces must not delete the observation.

    Removing the evidence would make the boundary trivial to hold and the next
    failure impossible to diagnose.
    """
    fs = build_fact_set(BASELINE)
    assert len(fs.evidence) > 0, "no rendering evidence recorded at all"
    kinds = {o.observation.split("=")[0] for o in fs.evidence.observations}
    assert "source_container" in kinds, sorted(kinds)
    assert "role_label_source" in kinds, sorted(kinds)


def test_the_subject_name_is_never_consulted():
    """Sixteen unlike subjects, one classification.

    A positive pin fails for every subject and a provenance record passes for
    every subject.  If any spelling behaved differently, a vocabulary would be
    deciding, which is precisely AB-01.
    """
    with tempfile.TemporaryDirectory() as td:
        pinned, recorded = set(), set()
        for i, subject in enumerate(ARBITRARY_SUBJECTS):
            tree = copy_tree(BASELINE, Path(td) / f"pin_{i}")
            doc = load(tree, ROLES)
            doc["roles"]["independent_review"]["preferred_provider"] = subject
            save(tree, ROLES, doc)
            pinned.add(result_vector(evaluate_tree(tree))["P03"])

            tree = copy_tree(BASELINE, Path(td) / f"prov_{i}")
            doc = load(tree, ROLES)
            doc["roles"]["independent_review"]["evidence_refs"]["provider_of_record"] = subject
            save(tree, ROLES, doc)
            recorded.add(result_vector(evaluate_tree(tree))["P03"])
        assert pinned == {FAIL}, pinned
        assert recorded == {PASS}, recorded


def test_no_vocabulary_entry_is_a_routing_identifier():
    """No declared vocabulary may contain a value the live catalog owns."""
    fs = build_fact_set(BASELINE)
    live = {canonical_identifier(i) for i in fs.live_catalog_identifiers}
    assert live, "the baseline live catalog exposed no identifiers"
    offenders = []
    for name in dir(vocabulary):
        value = getattr(vocabulary, name)
        if isinstance(value, (frozenset, set, tuple)):
            for entry in value:
                if isinstance(entry, str) and canonical_identifier(entry) in live:
                    offenders.append(f"{name}:{entry}")
    assert offenders == [], offenders


def test_every_adapter_declares_applicability_and_an_a_trace():
    """An adapter without a declared applicability is an inference engine."""
    assert adapters.ADAPTERS, "no adapters registered"
    for adapter_id, spec in adapters.ADAPTERS.items():
        assert spec.applicability.strip(), adapter_id
        assert spec.a_trace, adapter_id
        assert spec.decision_rule_ids, adapter_id
        assert all(rule_id in provenance.REGISTRY for rule_id in spec.decision_rule_ids)
        assert spec.ambiguity_policy == "fail_closed_as_unsupported", adapter_id


def test_an_unclaimed_document_contributes_nothing_rather_than_being_guessed():
    """C-08's fail-visible half, in the direction that must NOT fail.

    A document no adapter claims is inert.  It does not get best-effort
    interpretation, and it does not silently become a second source.
    """
    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "unclaimed")
        (tree / "workflow" / "opaque_v1.yml").write_text(
            "schema_version: workflow.opaque.v1\n"
            "narrative:\n"
            "  - an unfamiliar shape carrying no declaration this pipeline adapts\n"
            "measurements:\n"
            "  alpha: 3\n"
            "  beta: 4\n",
            encoding="utf-8",
        )
        before = result_vector(evaluate_tree(BASELINE))
        after = result_vector(evaluate_tree(tree))
        assert after == before, {k: (before.get(k), v) for k, v in after.items() if before.get(k) != v}
        assert overall(evaluate_tree(tree)) == PASS


def test_an_unparseable_document_is_visible_not_inert():
    """The other direction: uninterpretable is reported, never skipped."""
    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "unparseable")
        (tree / "workflow" / "broken_v1.yml").write_text(
            "key: value\n  bad: indent: here\n", encoding="utf-8"
        )
        results = evaluate_tree(tree)
        assert any(r.predicate_id == "P00" for r in results)
        assert overall(results) != PASS


def test_transparent_containers_have_no_arbitrary_depth_escape():
    """Eight wrappers reproduce the former depth-seven false negative."""
    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "deep_wrappers")
        wrapped = load(tree, ROLES)
        for depth in range(8):
            wrapped = {f"opaque_layer_{depth}": wrapped}
        save(tree, ROLES, wrapped)
        assert result_vector(evaluate_tree(tree)) == result_vector(evaluate_tree(BASELINE))


def test_unknown_active_slot_inside_claimed_selector_is_visible():
    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "unknown_selector_slot")
        doc = load(tree, ROLES)
        doc["roles"]["independent_review"]["provider_selection"] = {
            "opaque_target": "NacreCompute-QX"
        }
        save(tree, ROLES, doc)
        results = evaluate_tree(tree)
        assert any(r.predicate_id == "P00" for r in results)
        assert overall(results) != PASS


def test_long_prose_never_downgrades_an_active_decision_position():
    prose = "this deliberately long sentence remains an active value in a declared decision slot"
    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "long_provider")
        doc = load(tree, ROLES)
        doc["roles"]["independent_review"]["preferred_provider"] = prose
        save(tree, ROLES, doc)
        assert result_vector(evaluate_tree(tree))["P03"] == FAIL

        tree = copy_tree(BASELINE, Path(td) / "long_authority")
        doc = load(tree, ROLES)
        doc["roles"]["backend_execution"]["master_write_authorized"] = prose
        save(tree, ROLES, doc)
        assert result_vector(evaluate_tree(tree))["P05"] == FAIL


def test_word_count_prose_heuristic_is_absent_from_decision_modules():
    offenders = []
    for module in ("core.py", "adapters.py", "facts.py", "predicates.py"):
        tree = ast.parse((PKG / module).read_text(encoding="utf-8"))
        if any(isinstance(node, ast.Name) and node.id == "is_prose" for node in ast.walk(tree)):
            offenders.append(module)
    assert offenders == [], offenders


if __name__ == "__main__":
    for _name, _fn in sorted(list(globals().items())):
        if _name.startswith("test_"):
            _fn()
    print("representation boundary ok")

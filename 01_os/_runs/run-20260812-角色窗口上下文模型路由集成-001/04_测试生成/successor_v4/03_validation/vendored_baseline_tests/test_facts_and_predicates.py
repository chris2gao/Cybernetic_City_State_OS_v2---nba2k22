"""The baseline surface must be accepted, and each predicate must have teeth."""

from __future__ import annotations

import tempfile
from pathlib import Path

import _bootstrap
from _bootstrap import BASELINE

from semantic_acceptance.corpus import ROLES, copy_tree, load, save
from semantic_acceptance.evaluate import evaluate_tree, overall, result_vector
from semantic_acceptance.facts import build_fact_set
from semantic_acceptance.predicates import FAIL, PASS


def _vector(root: Path) -> dict[str, str]:
    return result_vector(evaluate_tree(root))


def test_baseline_is_accepted():
    results = evaluate_tree(BASELINE)
    failures = [(r.predicate_id, r.detail) for r in results if r.status != PASS]
    assert failures == [], failures
    assert overall(results) == PASS


def test_baseline_extracts_the_expected_fact_kinds():
    fs = build_fact_set(BASELINE)
    assert fs.roles, "no role definitions extracted"
    assert fs.window_identities, "no window identity extracted"
    assert fs.entry_modes, "no entry modes extracted"
    assert fs.declarations, "no prohibition declarations extracted"
    assert fs.autonomy, "no autonomy positions extracted"
    assert fs.authority, "no authority positions extracted"
    assert fs.live_catalog_identifiers, "the live catalog exposed no identifiers"
    assert not fs.unsupported, fs.unsupported


def test_baseline_provider_bindings_cover_the_non_selector_kinds():
    """PC-03b and PC-03c: provenance and pointer bindings exist and are permitted."""
    fs = build_fact_set(BASELINE)
    kinds = {b.selector_kind for b in fs.provider_bindings}
    assert "provenance" in kinds, sorted(kinds)
    assert "pointer" in kinds, sorted(kinds)
    assert "normative_selector" not in kinds, [
        (b.key_path, b.provider_label) for b in fs.provider_bindings if b.selector_kind == "normative_selector"
    ]


def test_predicates_are_not_vacuous():
    """Every predicate must fail on at least one construction.

    A predicate that cannot fail proves nothing, and a green suite made of such
    predicates is exactly the failure mode the v3 reviewer described as
    "overconstrained and semantically weak at the same time".
    """
    from semantic_acceptance.corpus import (
        i05_resource_neighbor_provider_pin,
        i08_generic_id_second_role_source,
        i09_yaml_mapping_model_catalog,
        i11_non_boolean_autonomy,
        i12_carried_delivery_state,
        i13_string_authority_grant,
    )

    def break_window(tree: Path) -> None:
        from semantic_acceptance.corpus import WINDOWS

        doc = load(tree, WINDOWS)
        doc["window_identity"]["bound_facts"] = ["task_id"]
        save(tree, WINDOWS, doc)

    cases = {
        "P01": i08_generic_id_second_role_source,
        "P02": break_window,
        "P03": i05_resource_neighbor_provider_pin,
        "P04": i12_carried_delivery_state,
        "P05": i13_string_authority_grant,
        "P06": i11_non_boolean_autonomy,
        "P07": i09_yaml_mapping_model_catalog,
    }
    with tempfile.TemporaryDirectory() as td:
        for pid, mutate in cases.items():
            tree = copy_tree(BASELINE, Path(td) / f"vacuity_{pid}")
            mutate(tree)
            vec = _vector(tree)
            assert vec[pid] == FAIL, (pid, vec)


def test_reentry_without_exact_predecessor_fails():
    from semantic_acceptance.corpus import WINDOWS

    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "loose_predecessor")
        doc = load(tree, WINDOWS)
        doc["entry_modes"]["reentry"]["predecessor_match"] = "loose"
        save(tree, WINDOWS, doc)
        assert _vector(tree)["P02"] == FAIL


def test_latest_session_as_identity_fails():
    from semantic_acceptance.corpus import WINDOWS

    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "latest_identity")
        doc = load(tree, WINDOWS)
        doc["window_identity"]["latest_session_pointer"] = {
            "status": "allowed_as_formal_identity"
        }
        save(tree, WINDOWS, doc)
        assert _vector(tree)["P02"] == FAIL


def test_boolean_authority_grant_fails_like_the_string_one():
    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "bool_grant")
        doc = load(tree, ROLES)
        doc["roles"]["backend_execution"]["master_write_authorized"] = True
        save(tree, ROLES, doc)
        assert _vector(tree)["P05"] == FAIL


def test_unparseable_document_is_visible_not_silent():
    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "broken_yaml")
        (tree / "mechanism" / "broken_v1.yml").write_text(
            "key: value\n  bad: indent: here\n", encoding="utf-8"
        )
        results = evaluate_tree(tree)
        statuses = {r.predicate_id: r.status for r in results}
        assert "P00" in statuses, statuses
        assert overall(results) != PASS


def test_duplicate_keys_are_rejected():
    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "dupe_keys")
        (tree / "mechanism" / "dupe_v1.yml").write_text(
            "authority_effect: none\nauthority_effect: granted\n", encoding="utf-8"
        )
        results = evaluate_tree(tree)
        assert any(r.predicate_id == "P00" for r in results)

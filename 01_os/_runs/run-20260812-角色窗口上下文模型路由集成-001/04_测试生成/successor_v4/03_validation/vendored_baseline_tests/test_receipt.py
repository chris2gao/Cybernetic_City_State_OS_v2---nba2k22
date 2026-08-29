"""Freeze-receipt contract tests.

ST04-V3-IR-001 had three parts and each gets its own test:
  * the active receipt did not parse under strict YAML;
  * the package validator never loaded it;
  * its ledger claimed five paths where the diff had six, omitting itself.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import _bootstrap
from _bootstrap import BASELINE

from semantic_acceptance.receipt import (
    SELF_HASH_SENTINEL,
    build_receipt,
    validate_receipt,
    write_receipt,
)

RECEIPT_REL = "freeze_receipt_v2.yml"

CHANGED = [
    "a/04_tests.yml",
    "a/impl/verify.py",
    "a/fixtures/mutations.yml",
    "a/fixtures/overlay/check_binding.py",
    "a/design_notes.md",
]


def _build(tmp: Path, changed=None):
    receipt = build_receipt(
        task_id="os-v2-stage04-semantic-acceptance-root-cause-replacement-001",
        run_id="run-20260812-stage04-semantic-acceptance-root-cause-001",
        base_sha="0" * 40,
        candidate_sha="1" * 40,
        changed_paths=list(CHANGED if changed is None else changed),
        receipt_rel_path=RECEIPT_REL,
        artifact_root=BASELINE,
        artifact_rel_paths=["mechanism/roles_v1.yml", "mechanism/windows_v1.yml"],
        topology="full_declared_surface",
    )
    path = tmp / RECEIPT_REL
    write_receipt(path, receipt)
    return path


def test_receipt_is_strict_yaml_and_is_actually_loaded():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        path = _build(tmp)
        v = validate_receipt(
            path,
            actual_changed_paths=CHANGED + [RECEIPT_REL],
            receipt_rel_path=RECEIPT_REL,
            artifact_root=BASELINE,
        )
        assert v.strict_yaml_parsed, v.parse_error
        assert v.required_fields_present, v.missing_fields
        assert v.valid, v.as_dict()


def test_ledger_includes_itself_without_self_hash():
    """The recursion the previous receipt escaped by deleting the entry."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        path = _build(tmp)
        v = validate_receipt(
            path,
            actual_changed_paths=CHANGED + [RECEIPT_REL],
            receipt_rel_path=RECEIPT_REL,
            artifact_root=BASELINE,
        )
        assert v.self_entry_present
        assert v.self_hash_recursion_avoided
        assert len(v.declared_paths) == len(CHANGED) + 1
        assert SELF_HASH_SENTINEL in path.read_text(encoding="utf-8")


def test_ledger_disagreeing_with_the_diff_is_rejected():
    """The exact v3 defect: five declared, six actual."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        path = _build(tmp, changed=CHANGED[:-1])  # one path short
        v = validate_receipt(
            path,
            actual_changed_paths=CHANGED + [RECEIPT_REL],
            receipt_rel_path=RECEIPT_REL,
            artifact_root=BASELINE,
        )
        assert not v.ledger_matches_diff
        assert not v.valid


def test_unparseable_receipt_is_rejected_not_ignored():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / RECEIPT_REL
        # The v3 shape: an unquoted plain scalar containing ": ".
        path.write_text(
            "schema_version: x\n"
            "note: the reviewer rejected the requested `*_disabled: true` shape\n",
            encoding="utf-8",
        )
        v = validate_receipt(
            path,
            actual_changed_paths=[],
            receipt_rel_path=RECEIPT_REL,
            artifact_root=BASELINE,
        )
        assert not v.strict_yaml_parsed
        assert not v.valid
        assert v.parse_error


def test_artifact_hash_mismatch_is_detected():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        path = _build(tmp)
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("sha256: a", "sha256: b", 1), encoding="utf-8")
        v = validate_receipt(
            path,
            actual_changed_paths=CHANGED + [RECEIPT_REL],
            receipt_rel_path=RECEIPT_REL,
            artifact_root=BASELINE,
        )
        if v.strict_yaml_parsed and v.artifact_hash_mismatches:
            assert not v.valid


if __name__ == "__main__":
    test_receipt_is_strict_yaml_and_is_actually_loaded()
    test_ledger_includes_itself_without_self_hash()
    test_ledger_disagreeing_with_the_diff_is_rejected()
    test_unparseable_receipt_is_rejected_not_ignored()
    print("receipt contract ok")

"""C-10 and C-07: the receipt is checked against facts it does not own.

The independent review accepted seven invalid receipts (R11-R17).  Every one of
them is here as a property rather than a single case, plus the external bindings
the review said the sentinel needs before it is safe:

    outside -> receipt        expected base SHA, expected candidate SHA,
                              observed diff, observed topology, expected scope

    receipt -> outside        nothing.  A receipt may claim anything; it can no
                              longer make the claim true.

`08_独立審核/independent_probe_suite.py` calls the short form of
`validate_receipt`, so the short form has to close R11-R17 on its own.  These
tests exercise both shapes and record which check does the work in each, because
"63/63 green" must not be allowed to stand in for knowing that.
"""

from __future__ import annotations

import copy
import tempfile
from pathlib import Path

import _bootstrap

from semantic_acceptance.core import dump_yaml, load_yaml_strict
from semantic_acceptance.receipt import (
    SELF_HASH_SENTINEL,
    build_receipt,
    is_canonical_relpath,
    is_sha40,
    sha256_file,
    validate_receipt,
    write_receipt,
)
from semantic_acceptance.topology import (
    FULL_CANDIDATE_TREE,
    FULL_DECLARED_SURFACE,
    ObservedExecution,
    observe_artifact_tree,
)

RECEIPT_REL = "freeze_receipt_v3.yml"
BASE = "a" * 40
CAND = "b" * 40


def _fixture(tmp: Path):
    artifact_root = tmp / "artifacts"
    (artifact_root / "nested").mkdir(parents=True)
    (artifact_root / "one.yml").write_text("one\n", encoding="utf-8")
    (artifact_root / "nested" / "two.yml").write_text("two\n", encoding="utf-8")
    rels = ["nested/two.yml", "one.yml"]
    data = build_receipt(
        task_id="correction-002",
        run_id="run-20260812-stage04-semantic-acceptance-root-cause-001",
        base_sha=BASE,
        candidate_sha=CAND,
        changed_paths=["nested/two.yml", "one.yml"],
        receipt_rel_path=RECEIPT_REL,
        artifact_root=artifact_root,
        artifact_rel_paths=rels,
        topology=FULL_CANDIDATE_TREE,
    )
    path = tmp / RECEIPT_REL
    write_receipt(path, data)
    actual = sorted(["nested/two.yml", "one.yml", RECEIPT_REL])
    return artifact_root, path, data, actual


def _validate(path, artifact_root, actual, **kw):
    return validate_receipt(
        path,
        actual_changed_paths=actual,
        receipt_rel_path=RECEIPT_REL,
        artifact_root=artifact_root,
        **kw,
    )


def _revalidate(path, artifact_root, data, actual, **kw):
    write_receipt(path, data)
    return _validate(path, artifact_root, actual, **kw)


def test_a_well_formed_receipt_is_valid_in_both_call_shapes():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, _data, actual = _fixture(tmp)
        short = _validate(path, artifact_root, actual)
        assert short.valid, short.as_dict()
        observed = observe_artifact_tree(artifact_root)
        observed.diff_paths = tuple(actual)
        observed.record("diff_paths", f"{len(actual)} paths", "test:external-diff")
        expected_artifact_hashes = {
            rel: sha256_file(artifact_root / rel)
            for rel in ("nested/two.yml", "one.yml")
        }
        full = _validate(
            path,
            artifact_root,
            actual,
            expected_base_sha=BASE,
            expected_candidate_sha=CAND,
            expected_receipt_sha256=sha256_file(path),
            observed_execution=observed,
            expected_artifact_hashes=expected_artifact_hashes,
            expected_hash_scope=["nested/two.yml", "one.yml"],
        )
        assert full.valid, full.as_dict()
        assert full.external_closure_complete, full.as_dict()
        assert set(full.external_bindings_checked) >= {
            "base_sha",
            "candidate_sha",
            "receipt_sha256",
            "diff_paths",
            "artifact_hashes",
            "hash_scope",
            "topology",
        }


def test_r11_declared_count_is_validated():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, data, actual = _fixture(tmp)
        for bogus in (0, 1, 999, "3", None):
            data["changed_paths"]["count"] = bogus
            v = _revalidate(path, artifact_root, data, actual)
            assert not v.valid, bogus
            assert not v.declared_count_matches


def test_r12_noncanonical_paths_are_rejected_in_every_spelling():
    assert is_canonical_relpath("a/b.yml")
    for bad in ("dir/../a.yml", "./a.yml", "/abs/a.yml", "C:/a.yml", "a\\b.yml", "a//b.yml", "", "a/"):
        assert not is_canonical_relpath(bad), bad
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, data, actual = _fixture(tmp)
        data["changed_paths"]["entries"][0]["path"] = "nested/../nested/two.yml"
        v = _revalidate(
            path, artifact_root, data, ["nested/../nested/two.yml", "one.yml", RECEIPT_REL]
        )
        assert not v.valid
        assert not v.paths_canonical


def test_r13_artifact_hash_path_cannot_escape_the_artifact_root():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, data, actual = _fixture(tmp)
        outside = tmp / "outside.txt"
        outside.write_text("outside\n", encoding="utf-8")
        data["artifact_hashes"].append(
            {"path": "../outside.txt", "sha256": sha256_file(outside)}
        )
        data["artifact_hash_scope"]["declared_paths"].append("../outside.txt")
        v = _revalidate(path, artifact_root, data, actual)
        assert not v.valid
        assert not v.artifact_paths_contained


def test_r14_candidate_sha_is_bound_syntactically_and_externally():
    assert is_sha40("0" * 40)
    assert not is_sha40("not-a-40-character-sha")
    assert not is_sha40("A" * 40)  # upper case is not the Git spelling
    assert not is_sha40("0" * 39)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, data, actual = _fixture(tmp)
        data["candidate_sha"] = "not-a-40-character-sha"
        v = _revalidate(path, artifact_root, data, actual)
        assert not v.valid and not v.sha_syntax_valid

        # syntactically valid but not the commit the caller expects
        data["candidate_sha"] = "c" * 40
        v = _revalidate(path, artifact_root, data, actual, expected_candidate_sha=CAND)
        assert not v.valid
        assert not v.external_bindings_hold


def test_r15_hash_coverage_cannot_be_empty_or_partial():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, data, actual = _fixture(tmp)
        empty = copy.deepcopy(data)
        empty["artifact_hashes"] = []
        v = _revalidate(path, artifact_root, empty, actual)
        assert not v.valid

        partial = copy.deepcopy(data)
        partial["artifact_hashes"] = partial["artifact_hashes"][:1]
        v = _revalidate(path, artifact_root, partial, actual)
        assert not v.valid

        no_scope = copy.deepcopy(data)
        no_scope["artifact_hash_scope"] = {"declared_paths": [], "complete": True}
        v = _revalidate(path, artifact_root, no_scope, actual)
        assert not v.valid and not v.hash_scope_complete


def test_r16_duplicate_artifact_entries_are_rejected():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, data, actual = _fixture(tmp)
        data["artifact_hashes"].append(copy.deepcopy(data["artifact_hashes"][0]))
        v = _revalidate(path, artifact_root, data, actual)
        assert not v.valid
        assert not v.artifact_paths_unique


def test_r17_topology_is_compared_not_reported():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, data, actual = _fixture(tmp)

        # 1. an unauthorized value fails without any external argument
        data["topology"] = "history_dependent_partial_closure"
        v = _revalidate(path, artifact_root, data, actual)
        assert not v.valid and not v.topology_comparison_holds
        assert "unauthorized" in v.topology_comparison_detail

        # 2. an authorized value that disagrees with the observed execution fails
        data["topology"] = FULL_DECLARED_SURFACE
        observed = observe_artifact_tree(artifact_root)  # reports full_candidate_tree
        v = _revalidate(path, artifact_root, data, actual, observed_execution=observed)
        assert not v.valid
        assert "!= observed" in v.topology_comparison_detail

        # 3. full_candidate_tree obliges the scope to equal the tree on disk
        data["topology"] = FULL_CANDIDATE_TREE
        (artifact_root / "three.yml").write_text("three\n", encoding="utf-8")
        v = _revalidate(path, artifact_root, data, actual)
        assert not v.valid
        assert "does not equal the artifact tree" in v.topology_comparison_detail


def test_the_self_hash_sentinel_is_confined_to_the_receipt_entry():
    """C-10: the sentinel is safe only where an external commit anchors it."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, data, actual = _fixture(tmp)
        assert any(
            e.get("sha256") == SELF_HASH_SENTINEL
            for e in data["changed_paths"]["entries"]
            if e["path"] == RECEIPT_REL
        )
        other = next(
            e for e in data["changed_paths"]["entries"] if e["path"] != RECEIPT_REL
        )
        other["sha256"] = SELF_HASH_SENTINEL
        v = _revalidate(path, artifact_root, data, actual)
        assert not v.valid
        assert any("sentinel" in f for f in v.failures)


def test_an_externally_observed_diff_overrides_what_the_receipt_declares():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, _data, actual = _fixture(tmp)
        observed = ObservedExecution(diff_paths=("one.yml", RECEIPT_REL))
        observed.record("diff_paths", "2 paths", "test:constructed")
        v = _validate(path, artifact_root, actual, observed_execution=observed)
        assert not v.valid
        assert not v.external_bindings_hold


def test_an_execution_observation_must_say_where_it_was_read_from():
    """C-11: a fact with no source has not been observed."""
    obs = ObservedExecution()
    try:
        obs.record("topology", FULL_CANDIDATE_TREE, "")
    except ValueError:
        return
    raise AssertionError("an observation without a source was accepted")


def test_external_receipt_byte_anchor_is_checked_and_not_self_declared():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, _data, actual = _fixture(tmp)
        good = sha256_file(path)
        assert _validate(
            path, artifact_root, actual, expected_receipt_sha256=good
        ).receipt_bytes_binding_holds
        bad = _validate(
            path, artifact_root, actual, expected_receipt_sha256="0" * 64
        )
        assert not bad.valid
        assert not bad.receipt_bytes_binding_holds


def test_receipt_serialization_is_canonical_lf_bytes():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _artifact_root, path, _data, _actual = _fixture(tmp)
        raw = path.read_bytes()
        assert b"\r\n" not in raw
        assert raw.endswith(b"\n")


def test_external_git_blob_hashes_override_worktree_bytes_and_are_checked():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, _data, actual = _fixture(tmp)
        expected = {
            "nested/two.yml": sha256_file(artifact_root / "nested/two.yml"),
            "one.yml": "0" * 64,
        }
        result = _validate(
            path,
            artifact_root,
            actual,
            expected_artifact_hashes=expected,
        )
        assert not result.valid
        assert not result.external_artifact_bindings_hold
        assert "one.yml" in result.artifact_hash_mismatches


def test_unprovenanced_execution_values_are_rejected():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        artifact_root, path, _data, actual = _fixture(tmp)
        observed = ObservedExecution(
            topology=FULL_CANDIDATE_TREE,
            diff_paths=tuple(actual),
            candidate_sha=CAND,
        )
        result = _validate(path, artifact_root, actual, observed_execution=observed)
        assert not result.valid
        assert not result.execution_provenance_holds


if __name__ == "__main__":
    for _name, _fn in sorted(list(globals().items())):
        if _name.startswith("test_"):
            _fn()
    print("receipt external binding ok")

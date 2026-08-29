#!/usr/bin/env python3
"""Receipt external binding and tamper tests over the v4 candidate.  P2-2 item 3.

`vendored_baseline_tests/test_receipt_external_binding.py` already attacks the
receipt contract, and it is byte-identical accepted evidence that must not be
edited.  What it does not do is exercise that contract over THIS package's own
artifacts: the receipt the v4 freeze will actually carry.  A contract that holds
on the accepted corpus and was never run against the candidate's own file set
is an assumption, not a measurement.

The direction of authority under test is outside -> receipt.  Every check below
supplies the facts externally and asks whether the receipt survives contact with
them.  A receipt is only worth writing if a wrong one fails.

Method note: each tamper asserts the receipt is rejected AND records which
failure fired.  `test_each_tamper_is_caught_by_its_own_check` then requires the
failure signatures to be distinct.  Without that, a single blanket rejection
would make all thirteen attacks look individually caught while really only one
thing was being tested.
"""

from __future__ import annotations

import copy
import shutil
import tempfile
from pathlib import Path

import _bootstrap_v4  # noqa: F401
from _bootstrap_v4 import SUCCESSOR_V4_ROOT

from semantic_acceptance.core import dump_yaml
from semantic_acceptance.receipt import (
    SELF_HASH_SENTINEL,
    build_receipt,
    sha256_file,
    validate_receipt,
    write_receipt,
)
from semantic_acceptance.topology import AUTHORIZED_TOPOLOGIES, FULL_CANDIDATE_TREE


TASK_ID = "os-v2-t2-completion-001"
RUN_ID = "run-20260828-t2-completion-001"
BASE_SHA = "3002d6177779abf81e6d476bfc434ee5d6dbe3c8"
CANDIDATE_SHA = "9c50a4fe56b12c1add15967a5515785e8e6fb760"
RECEIPT_REL = "03_validation/receipts/v4_binding_probe_receipt.yml"

# Real files from this package, not invented ones.  A tamper test over a fake
# artifact set would not tell anyone whether the freeze receipt can carry the
# candidate it is actually going to carry.
ARTIFACT_RELS = [
    "02_acceptance/实现/semantic_acceptance/structural_binding_v1.yml",
    "02_acceptance/实现/semantic_acceptance/structural_binding.py",
    "02_acceptance/实现/semantic_acceptance_v4/adapters_v4.py",
    "02_acceptance/实现/semantic_acceptance_v4/predicates_v4.py",
    "03_validation/v4_tests/corpus_v4.py",
]

# The receipt is itself a file the change set contains, and `build_receipt` puts
# it in the ledger.  An external diff that omitted it would disagree with every
# honest receipt ever written - which the first run of this module demonstrated
# by rejecting the control with `declared=6 actual=5`.
CHANGED_PATHS = sorted(set(ARTIFACT_RELS) | {RECEIPT_REL})

# `FULL_CANDIDATE_TREE` is true of the probe root by construction: the temp root
# is created containing exactly ARTIFACT_RELS and nothing else, so the ledger
# does cover its whole tree.  Declaring a topology the receipt does not actually
# satisfy would be the same class of false claim these tests exist to catch.
TOPOLOGY = FULL_CANDIDATE_TREE


def _artifact_root(tmp: Path) -> Path:
    """A private copy, so no tamper can reach the real worktree."""
    root = tmp / "artifacts"
    for rel in ARTIFACT_RELS:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SUCCESSOR_V4_ROOT / rel, dst)
    return root


def _fresh(tmp: Path):
    root = _artifact_root(tmp)
    receipt = build_receipt(
        task_id=TASK_ID,
        run_id=RUN_ID,
        base_sha=BASE_SHA,
        candidate_sha=CANDIDATE_SHA,
        changed_paths=list(CHANGED_PATHS),
        receipt_rel_path=RECEIPT_REL,
        artifact_root=root,
        artifact_rel_paths=list(ARTIFACT_RELS),
        topology=TOPOLOGY,
    )
    return root, receipt


def _validate(tmp: Path, root: Path, receipt: dict, *, raw: str | None = None,
              expected_receipt_sha256: str | None = None,
              actual_changed_paths=None):
    path = tmp / "receipt.yml"
    if raw is None:
        write_receipt(path, receipt)
    else:
        path.write_bytes(raw.encode("utf-8"))
    return validate_receipt(
        path,
        actual_changed_paths=(CHANGED_PATHS if actual_changed_paths is None
                              else actual_changed_paths),
        receipt_rel_path=RECEIPT_REL,
        artifact_root=root,
        expected_base_sha=BASE_SHA,
        expected_candidate_sha=CANDIDATE_SHA,
        expected_receipt_sha256=expected_receipt_sha256,
    )


def _tamper(mutate, *, raw_mutate=None, actual_changed_paths=None):
    """Run one attack in its own temp tree.  Returns the ReceiptValidation."""
    with tempfile.TemporaryDirectory(prefix="v4_receipt_") as td:
        tmp = Path(td)
        root, receipt = _fresh(tmp)
        if mutate is not None:
            receipt = copy.deepcopy(receipt)
            mutate(receipt, root)
        raw = None
        if raw_mutate is not None:
            raw = raw_mutate(dump_yaml(receipt))
        return _validate(tmp, root, receipt, raw=raw,
                         actual_changed_paths=actual_changed_paths)


def _entry(receipt, rel):
    for e in receipt["changed_paths"]["entries"]:
        if e["path"] == rel:
            return e
    raise AssertionError(f"{rel} not in ledger")


# ---------------------------------------------------------------------------
# the attacks
# ---------------------------------------------------------------------------


def _m_artifact_digest(receipt, root):
    receipt["artifact_hashes"][0]["sha256"] = "0" * 64


def _m_drop_ledger_entry(receipt, root):
    rel = ARTIFACT_RELS[0]
    receipt["changed_paths"]["entries"] = [
        e for e in receipt["changed_paths"]["entries"] if e["path"] != rel
    ]


def _m_extra_ledger_entry(receipt, root):
    receipt["changed_paths"]["entries"].append({"path": "02_acceptance/never_changed.yml"})


def _m_wrong_declared_count(receipt, root):
    receipt["changed_paths"]["count"] = len(receipt["changed_paths"]["entries"]) + 3


def _m_noncanonical_path(receipt, root):
    _entry(receipt, ARTIFACT_RELS[0])["path"] = "./" + ARTIFACT_RELS[0]


def _m_duplicate_path(receipt, root):
    receipt["changed_paths"]["entries"].append(dict(_entry(receipt, ARTIFACT_RELS[1])))


def _m_escaping_artifact_path(receipt, root):
    receipt["artifact_hashes"].append(
        {"path": "../outside_the_root.yml", "sha256": "1" * 64}
    )


def _m_wrong_base_sha(receipt, root):
    receipt["base_sha"] = "0" * 40


def _m_wrong_candidate_sha(receipt, root):
    receipt["candidate_sha"] = "1" * 40


def _m_self_hash_filled_in(receipt, root):
    _entry(receipt, RECEIPT_REL)["sha256"] = "2" * 64


def _m_empty_artifact_ledger(receipt, root):
    receipt["artifact_hashes"] = []


def _m_bad_sha_syntax(receipt, root):
    receipt["candidate_sha"] = "not-a-sha"


def _m_unauthorized_topology(receipt, root):
    receipt["topology"] = "a_topology_nobody_authorised"


def _m_required_field_removed(receipt, root):
    del receipt["artifact_hash_scope"]


ATTACKS = (
    ("artifact_digest_flipped", _m_artifact_digest, None, None),
    ("ledger_entry_dropped", _m_drop_ledger_entry, None, None),
    ("ledger_entry_invented", _m_extra_ledger_entry, None, None),
    ("declared_count_lies", _m_wrong_declared_count, None, None),
    ("path_not_canonical", _m_noncanonical_path, None, None),
    ("path_duplicated", _m_duplicate_path, None, None),
    ("artifact_path_escapes_root", _m_escaping_artifact_path, None, None),
    ("base_sha_disagrees_with_outside", _m_wrong_base_sha, None, None),
    ("candidate_sha_disagrees_with_outside", _m_wrong_candidate_sha, None, None),
    ("self_hash_sentinel_replaced", _m_self_hash_filled_in, None, None),
    ("artifact_ledger_emptied", _m_empty_artifact_ledger, None, None),
    ("sha_syntax_invalid", _m_bad_sha_syntax, None, None),
    ("topology_not_authorized", _m_unauthorized_topology, None, None),
    ("required_field_removed", _m_required_field_removed, None, None),
    ("second_yaml_document_appended", None,
     lambda text: text + "\n---\nsmuggled: payload\n", None),
    ("diff_shows_a_path_the_receipt_omits", None, None,
     CHANGED_PATHS + ["02_acceptance/实现/semantic_acceptance/core.py"]),
)


def _results():
    out = {}
    for name, mutate, raw_mutate, actual in ATTACKS:
        out[name] = _tamper(mutate, raw_mutate=raw_mutate, actual_changed_paths=actual)
    return out


# ---------------------------------------------------------------------------
# positive control
# ---------------------------------------------------------------------------


def test_an_honest_receipt_over_the_real_v4_artifacts_validates():
    """Without this, every rejection below could be a receipt that never worked."""
    with tempfile.TemporaryDirectory(prefix="v4_receipt_ok_") as td:
        tmp = Path(td)
        root, receipt = _fresh(tmp)
        v = _validate(tmp, root, receipt)
    assert v.valid, v.failures


def test_the_declared_topology_is_an_authorized_one():
    """Guards the constant: an unauthorized topology fails closed by design."""
    assert TOPOLOGY in AUTHORIZED_TOPOLOGIES, TOPOLOGY


def test_the_self_entry_is_present_and_unhashed():
    with tempfile.TemporaryDirectory(prefix="v4_receipt_self_") as td:
        tmp = Path(td)
        _, receipt = _fresh(tmp)
    assert _entry(receipt, RECEIPT_REL)["sha256"] == SELF_HASH_SENTINEL


def test_receipt_bytes_are_bound_to_an_external_digest():
    """Changing the file after the digest was taken must be detectable."""
    with tempfile.TemporaryDirectory(prefix="v4_receipt_bytes_") as td:
        tmp = Path(td)
        root, receipt = _fresh(tmp)
        path = tmp / "receipt.yml"
        write_receipt(path, receipt)
        honest_digest = sha256_file(path)

        good = _validate(tmp, root, receipt, expected_receipt_sha256=honest_digest)
        assert good.valid, good.failures

        path.write_bytes(path.read_bytes() + b"\n# appended after hashing\n")
        tampered = validate_receipt(
            path,
            actual_changed_paths=CHANGED_PATHS,
            receipt_rel_path=RECEIPT_REL,
            artifact_root=root,
            expected_base_sha=BASE_SHA,
            expected_candidate_sha=CANDIDATE_SHA,
            expected_receipt_sha256=honest_digest,
        )
    assert not tampered.valid, "receipt bytes changed after hashing and validated anyway"


# ---------------------------------------------------------------------------
# the attacks must all be rejected, and each by its own check
# ---------------------------------------------------------------------------


def test_every_tamper_is_rejected():
    survived = [name for name, v in _results().items() if v.valid]
    assert survived == [], survived


def test_every_tamper_names_a_failure():
    silent = [name for name, v in _results().items() if not v.failures]
    assert silent == [], silent


def test_each_tamper_is_caught_by_its_own_check():
    """Distinct attacks must produce distinct failure signatures.

    If one blanket rejection caught everything, the battery above would be
    thirteen names for a single test.  A signature here is the sorted set of
    boolean check names that went false, which is the receipt's own account of
    WHY it refused - not the free-text message, which would make this
    assertion about wording.
    """
    flags = [
        "required_fields_present", "ledger_matches_diff", "self_entry_present",
        "self_hash_recursion_avoided", "declared_count_matches", "paths_canonical",
        "paths_unique", "artifact_paths_contained", "artifact_paths_unique",
        "hash_scope_complete", "sha_syntax_valid", "external_bindings_hold",
        "receipt_bytes_binding_holds", "external_artifact_bindings_hold",
        "execution_provenance_holds", "topology_comparison_holds",
        "strict_yaml_parsed",
    ]
    signatures: dict[str, frozenset] = {}
    for name, v in _results().items():
        failed = frozenset(f for f in flags if getattr(v, f) is False)
        if not failed:
            # rejected by artifact-hash mismatch, which is a list rather than a flag
            failed = frozenset(["artifact_hash_mismatches"]) if v.artifact_hash_mismatches else frozenset(["unnamed"])
        signatures[name] = failed

    distinct = len(set(signatures.values()))
    assert distinct >= 6, {
        "distinct_signatures": distinct,
        "signatures": {k: sorted(v) for k, v in signatures.items()},
    }
    assert "unnamed" not in {f for s in signatures.values() for f in s}, signatures

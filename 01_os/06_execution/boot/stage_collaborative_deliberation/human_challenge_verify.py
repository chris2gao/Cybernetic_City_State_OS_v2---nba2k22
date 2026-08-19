#!/usr/bin/env python3
"""Human task-authority challenge verifier (v2 with legacy v1 read support).

For a downstream fresh model that finds the authority provenance of a decision
insufficient. It reads the durable decision record, asks the *current* Human for
the Human Task Authority Code for the task, or the legacy v1 Authorization/Completion Code for a historical decision,
recomputes the commitment from the record's bound fields plus the supplied code,
and compares.

The code is read from stdin only. It is never accepted as a command-line
argument, never echoed, never written to the log and never persisted. Only the
verification result and the commitment that was checked are recorded.

A plaintext code obtained from executor output, the repository, a run artifact,
a communication document or another model's report is not proof here: any of
those could have produced the record being challenged. The code must come from
the current Human in the current interaction.

Usage:
    python human_challenge_verify.py <repo-root> <decision-record-path>
    # then paste the code when prompted, or pipe it on stdin

Exit codes:
    0  verified
    1  mismatch - Human authority verification failed
    2  record could not be read or is structurally invalid
"""
from __future__ import annotations

import getpass
import importlib.util
import json
import sys
from pathlib import Path

VALIDATOR = (
    Path(__file__).resolve().parents[3]
    / "03_mechanisms/stage_collaborative_deliberation/实现"
    / "verify_stage_collaborative_deliberation.py"
)


def load_validator():
    spec = importlib.util.spec_from_file_location("scd_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_nonce() -> str:
    """stdin only. getpass keeps it off the terminal when interactive."""
    if sys.stdin.isatty():
        return getpass.getpass("Human Task Authority / legacy authority code (not echoed): ").strip()
    return sys.stdin.readline().strip()


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    repo_root, record_path = Path(sys.argv[1]), Path(sys.argv[2])
    v = load_validator()

    target = record_path if record_path.is_absolute() else repo_root / record_path
    if not target.is_file():
        print(json.dumps({"result": "record_not_found", "record": str(record_path)}))
        return 2
    try:
        record = v.load_doc(target)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"result": "record_unreadable", "error": type(exc).__name__}))
        return 2
    if not isinstance(record, dict):
        print(json.dumps({"result": "record_not_a_mapping"}))
        return 2
    if v.validate_authority_record_commitments(record):
        print(json.dumps({"result": "commitment_structure_invalid"}))
        return 2

    nonce = read_nonce()
    if not nonce:
        print(json.dumps({"result": "no_code_supplied"}))
        return 2
    if len(nonce) < 2:
        print(json.dumps({"result": "code_too_short", "minimum_length_characters": 2}))
        return 2

    ok, _recomputed, stored = v.verify_human_challenge(record, nonce)
    del nonce  # the plaintext leaves memory scope here and is never stored

    # Only the outcome and the commitment that was checked are reported. The
    # recomputed digest of a wrong guess is not printed either: it would be an
    # oracle for offline search against the stored commitment.
    print(json.dumps({
        "result": "verified" if ok else "mismatch",
        "scheme": v.authority_record_scheme(record),
        "algorithm": v.HUMAN_AUTHORITY_ALGORITHM,
        "commitment_checked": stored,
        "decision_id": record.get("decision_id"),
        "decision_type": record.get("decision_type"),
        "task_id": record.get("task_id"),
        "stage_id": record.get("stage_id"),
        "exact_model_version": record.get("exact_model_version"),
        "record_ref": str(record_path),
        "plaintext_persisted": False,
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

"""Unit and fault-injection regression tests for validate_batch_execution (Gate G7).
Verifies offline replay against the gold 100-item live receipts and fail-closed fault injection.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

_RESEARCH_DIR = Path(__file__).resolve().parent.parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

from validate_batch_execution import validate_batch_execution, validate_stage_directory

GOLD_RUN_DIR = (_RESEARCH_DIR / "../../../.." / "01_os/07_content/_runs/run-20261102-nba2k22-rea-100-live-benchmark-001/07_测试执行").resolve()


def test_g7_replay_gold_100_live_mutation_receipts_offline():
    """Gate G7: Off-line replay of 100 gold live mutation receipts must pass all checks."""
    stage_dir = GOLD_RUN_DIR / "mutation_100"
    assert stage_dir.is_dir(), f"Gold mutation stage dir not found: {stage_dir}"

    res = validate_stage_directory(stage_dir, expected_count=100, expected_mode="mutation")
    assert res["validation_passed"] is True, f"Validation errors: {res['errors']}"
    assert res["checks"]["receipt_count"] == 100
    assert res["checks"]["unknown_count"] == 0
    assert res["checks"]["conservation_holds"] is True
    assert res["checks"]["outcomes_breakdown"].get("SUCCESS_APPLIED") == 100
    assert res["checks"]["plan_digest_verified"] is True
    assert res["checks"]["claims_count"] == 7
    assert res["checks"]["raw_chunk_messages_count"] == 7


def test_g7_replay_gold_100_live_noop_receipts_offline():
    """Gate G7: Off-line replay of 100 gold live No-op receipts must pass all checks."""
    stage_dir = GOLD_RUN_DIR / "noop_100"
    assert stage_dir.is_dir(), f"Gold noop stage dir not found: {stage_dir}"

    res = validate_stage_directory(stage_dir, expected_count=100, expected_mode="noop")
    assert res["validation_passed"] is True, f"Validation errors: {res['errors']}"
    assert res["checks"]["receipt_count"] == 100
    assert res["checks"]["unknown_count"] == 0
    assert res["checks"]["conservation_holds"] is True
    assert res["checks"]["outcomes_breakdown"].get("UNCHANGED_ALREADY_TARGET") == 100


def test_g7_fault_injection_tampered_plan_digest():
    """Gate G7: Fails closed when manifest plan_digest is tampered."""
    stage_dir = GOLD_RUN_DIR / "mutation_100"
    batch_file = list(stage_dir.glob("batch_*.json"))[0]
    batch = json.loads(batch_file.read_text(encoding="utf-8-sig"))

    receipts = [
        json.loads(line) for line in
        (stage_dir / "journal/receipts.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    manifest = json.loads(list(stage_dir.glob("manifest_*.json"))[0].read_text(encoding="utf-8-sig"))
    # Injected tampered digest
    manifest["plan_digest"] = "0000000000000000000000000000000000000000000000000000000000000000"

    res = validate_batch_execution(
        batch=batch,
        chunks=[],
        raw_messages=[],
        receipts=receipts,
        manifest=manifest,
        expected_mode="mutation"
    )
    assert res["validation_passed"] is False
    assert any("plan_digest mismatch" in err for err in res["errors"])


def test_g7_fault_injection_missing_getter_values():
    """Gate G7: Fails closed if getter values are missing (no silent skipping)."""
    stage_dir = GOLD_RUN_DIR / "mutation_100"
    batch = json.loads(list(stage_dir.glob("batch_*.json"))[0].read_text(encoding="utf-8-sig"))
    receipts = [
        json.loads(line) for line in
        (stage_dir / "journal/receipts.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    tampered_receipts = deepcopy(receipts)
    # Strip getter fields from receipt 0
    tampered_receipts[0].pop("getter_before", None)
    tampered_receipts[0].pop("actual_before", None)

    res = validate_batch_execution(
        batch=batch,
        chunks=[],
        raw_messages=[],
        receipts=tampered_receipts,
        expected_mode="mutation"
    )
    assert res["validation_passed"] is False
    assert any("Missing getter_before" in err for err in res["errors"])


def test_g7_fault_injection_unknown_outcome_detected():
    """Gate G7: Critical safety invariant: detects UNKNOWN or UNKNOWN_EXECUTION_OUTCOME and fails."""
    stage_dir = GOLD_RUN_DIR / "mutation_100"
    batch = json.loads(list(stage_dir.glob("batch_*.json"))[0].read_text(encoding="utf-8-sig"))
    receipts = [
        json.loads(line) for line in
        (stage_dir / "journal/receipts.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    tampered_receipts = deepcopy(receipts)
    tampered_receipts[10]["outcome"] = "UNKNOWN_EXECUTION_OUTCOME"

    res = validate_batch_execution(
        batch=batch,
        chunks=[],
        raw_messages=[],
        receipts=tampered_receipts,
        expected_mode="mutation"
    )
    assert res["validation_passed"] is False
    assert res["checks"]["unknown_count"] == 1
    assert any("UNKNOWN outcome detected" in err for err in res["errors"])


def test_g7_fault_injection_value_mismatch():
    """Gate G7: Fails closed when after value does not match requested target."""
    stage_dir = GOLD_RUN_DIR / "mutation_100"
    batch = json.loads(list(stage_dir.glob("batch_*.json"))[0].read_text(encoding="utf-8-sig"))
    receipts = [
        json.loads(line) for line in
        (stage_dir / "journal/receipts.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    tampered_receipts = deepcopy(receipts)
    # Requested was 56, forge getter_after as 55
    tampered_receipts[0]["getter_after"] = 55

    res = validate_batch_execution(
        batch=batch,
        chunks=[],
        raw_messages=[],
        receipts=tampered_receipts,
        expected_mode="mutation"
    )
    assert res["validation_passed"] is False
    assert any("Target value mismatch" in err for err in res["errors"])


def test_g7_fault_injection_missing_receipt():
    """Gate G7: Fails closed when an intent receipt is missing (e.g. 99 instead of 100)."""
    stage_dir = GOLD_RUN_DIR / "mutation_100"
    batch = json.loads(list(stage_dir.glob("batch_*.json"))[0].read_text(encoding="utf-8-sig"))
    receipts = [
        json.loads(line) for line in
        (stage_dir / "journal/receipts.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    # Drop one receipt
    incomplete_receipts = deepcopy(receipts[:-1])

    res = validate_batch_execution(
        batch=batch,
        chunks=[],
        raw_messages=[],
        receipts=incomplete_receipts,
        expected_mode="mutation"
    )
    assert res["validation_passed"] is False
    assert res["checks"]["missing_intents_count"] == 1
    assert any("Count mismatch" in err for err in res["errors"])

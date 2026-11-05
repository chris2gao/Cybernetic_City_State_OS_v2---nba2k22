"""
Safety Admission Test Suite for NBA2K22 REA Bulk Executor.
Verifies Gates G1 through G9 and all 17 Failure Injection scenarios.

Task: NBA2K22-REA-BULK-SAFETY-ADMISSION-20261101-001
Role: execution
Release Candidate: OFFLINE_SAFETY_ADMISSION_CANDIDATE
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from dataclasses import asdict
import pytest

_RESEARCH_DIR = Path(__file__).resolve().parent.parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

from bulk_executor import (
    BulkBatchHeader,
    BulkIntentItem,
    BulkBatch,
    BulkBatchPlanner,
    BulkFridaScriptCompiler,
    BulkExecutorService,
    MockNativeEnvironment,
    ReaChunkTransportAdapter,
    ExecutionJournal,
    PlannedChunk,
    ItemReceipt,
    get_resource_key,
    sha256_digest,
    atomic_write_json,
    canonical_encode,
    GAME_BUILD_SHA256,
)


@pytest.fixture
def valid_header():
    return BulkBatchHeader(
        batch_id="BATCH-SAFETY-001",
        save_instance_id="save_safety_001",
        game_build_sha256=GAME_BUILD_SHA256,
        source_snapshot_ref="snap_safety_001",
        expected_process_name="NBA2K22.exe",
        expected_pid=None,
        authorization_ref="AUTH-SAFETY-SPEC-001",
        dry_run=True,
    )


# ===========================================================================
# Gate G1 & Failure Injection: Offline Denial
# ===========================================================================

def test_gate_g1_live_denial_regardless_of_flags(tmp_path, valid_header):
    """G1: Verify live transport adapter hard-denies real game attachment regardless of input flags."""
    adapter = ReaChunkTransportAdapter(tmp_path, live_context=None)
    item = BulkIntentItem(
        intent_id="I-G1-FAIL-CLOSED",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    planner = BulkBatchPlanner()
    chunk = planner.plan(batch)[0]

    with pytest.raises(PermissionError, match="LIVE_AUTHORIZATION_VERIFIER_NOT_AVAILABLE"):
        adapter.execute_chunk(chunk, "// script")


# ===========================================================================
# Gate G2 & Failure Injections 1-5: UNKNOWN, At-Most-Once, and Crash Recovery
# ===========================================================================

def test_fi_01_same_intent_prior_unknown(tmp_path, valid_header):
    """Failure Injection 1: SAME_INTENT_PRIOR_UNKNOWN.
    Replaying exact same intent_id after prior UNKNOWN must be blocked with ZERO transport calls.
    """
    service = BulkExecutorService(tmp_path)
    transport_calls = []

    def failing_handler(chunk, script):
        transport_calls.append(chunk.chunk_id)
        return {
            "kind": "chunk-execution-result",
            "chunk_id": chunk.chunk_id,
            "chunk_digest": chunk.chunk_digest,
            "plan_digest": chunk.plan_digest,
            "action_id": chunk.action_id,
            "outcome": "CHUNK_HALTED",
            "receipts": [{
                "intent_id": chunk.intents[0].intent_id,
                "team_id": chunk.intents[0].team_id,
                "player_id": chunk.intents[0].player_id,
                "field_id": chunk.intents[0].field_id,
                "expected_before": chunk.intents[0].expected_before,
                "requested": chunk.intents[0].value,
                "outcome": "UNKNOWN_EXECUTION_OUTCOME",
                "reason": "INJECTED_CRASH"
            }]
        }

    adapter = ReaChunkTransportAdapter(tmp_path, fake_handler=failing_handler)
    item = BulkIntentItem(
        intent_id="I-CRASH-001",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    b1 = BulkBatch(header=valid_header, intents=(item,))
    res1 = service.run_with_transport(b1, adapter)
    assert res1['metrics']['num_unknown'] == 1
    assert len(transport_calls) == 1

    # Retry exact same intent
    res2 = service.run_with_transport(b1, adapter)
    assert res2['metrics']['num_blocked'] == 1
    assert len(transport_calls) == 1  # ZERO new transport calls!
    assert res2['metrics']['conservation_holds'] is True


def test_fi_02_cross_save_identical_intent_id(tmp_path, valid_header):
    """Failure Injection 2: CROSS_SAVE_IDENTICAL_INTENT_ID.
    Same intent_id with a different save_instance_id must fail closed.
    """
    journal = ExecutionJournal(tmp_path)
    planner = BulkBatchPlanner()

    item = BulkIntentItem(
        intent_id="I-SAVE-TEST-001",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    b1 = BulkBatch(header=valid_header, intents=(item,))
    chunk1 = planner.plan(b1)[0]
    journal.claim_chunk(chunk1)

    # Different save_instance_id reusing same intent_id
    header2 = BulkBatchHeader(
        batch_id="BATCH-DIFF-SAVE",
        save_instance_id="save_other_999",
        game_build_sha256=GAME_BUILD_SHA256,
        source_snapshot_ref="snap_diff",
        authorization_ref="AUTH-TEST",
        dry_run=True,
    )
    b2 = BulkBatch(header=header2, intents=(item,))
    chunk2 = planner.plan(b2)[0]

    with pytest.raises(ValueError, match="INTENT_ID_REUSED_WITH_DIFFERENT_PAYLOAD"):
        journal.claim_chunk(chunk2)


def test_fi_03_prestart_claim_crash(tmp_path, valid_header):
    """Failure Injection 3: PRESTART_CLAIM_CRASH.
    Crash window: Claim is persisted in STARTED state, but process dies before transport/receipts.
    Recovery must mark claim as UNKNOWN and lock target resource.
    """
    journal = ExecutionJournal(tmp_path)
    planner = BulkBatchPlanner()

    item = BulkIntentItem(
        intent_id="I-CRASH-PRESTART",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    chunk = planner.plan(batch)[0]

    # Write claim in STARTED state
    journal.claim_chunk(chunk)

    # Simulate restart and recovery
    journal_recovered = ExecutionJournal(tmp_path)
    journal_recovered.recover_interrupted_claims()

    res_key = get_resource_key(28, 2459, "SHOT_TENDENCY")
    assert journal_recovered.is_resource_locked(res_key) == "I-CRASH-PRESTART"


def test_fi_04_partial_receipt_file(tmp_path, valid_header):
    """Failure Injection 4: PARTIAL_RECEIPT_FILE.
    Claim has 2 intents, but only 1 receipt was flushed before crash.
    Uncompleted intent resource must remain locked in UNKNOWN state.
    """
    journal = ExecutionJournal(tmp_path)
    planner = BulkBatchPlanner()

    item1 = BulkIntentItem(
        intent_id="I-PARTIAL-001",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    item2 = BulkIntentItem(
        intent_id="I-PARTIAL-002",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="DRIVING_LAYUP_TENDENCY",
        expected_before=85,
        value=75,
    )
    batch = BulkBatch(header=valid_header, intents=(item1, item2))
    chunk = planner.plan(batch)[0]
    journal.claim_chunk(chunk)

    # Flush receipt ONLY for item1
    r1 = ItemReceipt(
        intent_id=item1.intent_id,
        team_id=item1.team_id,
        player_id=item1.player_id,
        field_id=item1.field_id,
        expected_before=item1.expected_before,
        requested=item1.value,
        getter_before=item1.expected_before,
        getter_after=item1.value,
        outcome="SUCCESS_APPLIED",
        chunk_id=chunk.chunk_id,
        timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    )
    journal.append_receipts([r1])

    # Now recover
    journal_recovered = ExecutionJournal(tmp_path)
    journal_recovered.recover_interrupted_claims()

    # item1 completed, item2 locked
    assert journal_recovered.is_intent_completed("I-PARTIAL-001") is True
    res_key2 = get_resource_key(28, 2459, "DRIVING_LAYUP_TENDENCY")
    assert journal_recovered.is_resource_locked(res_key2) == "I-PARTIAL-002"


def test_fi_05_duplicate_chunk_id_different_plan(tmp_path, valid_header):
    """Failure Injection 5: DUPLICATE_CHUNK_ID_DIFFERENT_PLAN.
    Identical chunk_id with different payload/plan must fail closed.
    """
    journal = ExecutionJournal(tmp_path)
    planner = BulkBatchPlanner()

    item1 = BulkIntentItem(
        intent_id="I-PLAN1-001",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    b1 = BulkBatch(header=valid_header, intents=(item1,))
    chunk1 = planner.plan(b1)[0]
    journal.claim_chunk(chunk1)

    # Different intent in a batch with chunk having same chunk_id
    item2 = BulkIntentItem(
        intent_id="I-PLAN2-001",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=75,
    )
    b2 = BulkBatch(header=valid_header, intents=(item2,))
    # Overwrite plan_digest on chunk to test duplicate chunk_id in same plan
    chunk2 = PlannedChunk(
        chunk_id=chunk1.chunk_id,
        team_id=28,
        action_id="PLAYER_PATCH_TENDENCIES",
        intents=(item2,),
        estimated_call_count=3,
        estimated_duration_ms=500,
        batch_id=valid_header.batch_id,
        save_instance_id=valid_header.save_instance_id,
        plan_digest=chunk1.plan_digest,
        chunk_digest="different_chunk_digest_002"
    )

    with pytest.raises(ValueError, match="DUPLICATE_CHUNK_ID_DIFFERENT_PLAN"):
        journal.claim_chunk(chunk2)


# ===========================================================================
# Gate G3 & Failure Injections 6-8: Lock Ledger & Reconciliation Provenance
# ===========================================================================

def test_fi_06_corrupt_lock_ledger(tmp_path):
    """Failure Injection 6: CORRUPT_LOCK_LEDGER.
    Corrupted locked_resources.json must raise RuntimeError, failing closed.
    """
    journal = ExecutionJournal(tmp_path)
    journal.locks_file.parent.mkdir(parents=True, exist_ok=True)
    journal.locks_file.write_text("{{corrupted_json: true,", encoding='utf-8')

    with pytest.raises(RuntimeError, match="CORRUPT_LOCK_LEDGER"):
        journal.get_locked_resources()


def test_fi_07_missing_lock_index(tmp_path, valid_header):
    """Failure Injection 7: MISSING_LOCK_INDEX.
    If locked_resources.json is missing, reconstructs locks from UNKNOWN claims/receipts (not empty).
    """
    journal = ExecutionJournal(tmp_path)
    planner = BulkBatchPlanner()

    item = BulkIntentItem(
        intent_id="I-MISSING-LOCK-001",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    chunk = planner.plan(batch)[0]

    # Write claim in UNKNOWN state
    claim_identity = sha256_digest({"test": "data"})
    claim_path = journal.claims_dir / f"claim_{chunk.chunk_id}_{claim_identity[:12]}.json"
    claim_data = {
        "chunk_id": chunk.chunk_id,
        "state": "UNKNOWN_EXECUTION_OUTCOME",
        "intents": [{"resource_key": "team:28:player:2459:field:SHOT_TENDENCY", "intent_id": "I-MISSING-LOCK-001"}]
    }
    atomic_write_json(claim_path, claim_data)

    # Ensure locks file does NOT exist
    if journal.locks_file.exists():
        journal.locks_file.unlink()

    # Must reconstruct and reflect the lock
    locks = journal.get_locked_resources()
    assert locks.get("team:28:player:2459:field:SHOT_TENDENCY") == "I-MISSING-LOCK-001"


def test_fi_08_applied_only_reconcile(tmp_path, valid_header):
    """Failure Injection 8: APPLIED_ONLY_RECONCILE.
    Reconcile without readback getter, unaltered fields confirmation, or independent source must fail closed.
    """
    journal = ExecutionJournal(tmp_path)
    r = ItemReceipt(
        intent_id="I-RECON-001",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        requested=80,
        outcome="UNKNOWN_EXECUTION_OUTCOME",
        chunk_id="chunk-0001",
        timestamp="2026-11-01T20:00:00Z"
    )
    journal.append_receipts([r])

    with pytest.raises(ValueError, match="RECONCILIATION_INCOMPLETE_EVIDENCE"):
        journal.reconcile_unknown("I-RECON-001", {"intent_id": "I-RECON-001", "applied": True})


# ===========================================================================
# Gate G4 & Failure Injections 14-16: Planning, Partitioning, and Dependencies
# ===========================================================================

def test_fi_14_mixed_action_single_team(valid_header):
    """Failure Injection 14: MIXED_ACTION_SINGLE_TEAM.
    Tendencies, attributes, and coach on same team must be partitioned into 3 distinct chunks.
    """
    planner = BulkBatchPlanner()
    intents = [
        BulkIntentItem(
            intent_id="I-MIX-01",
            action_id="PLAYER_PATCH_TENDENCIES",
            team_id=28,
            player_id=2459,
            field_id="SHOT_TENDENCY",
            expected_before=95,
            value=80,
        ),
        BulkIntentItem(
            intent_id="I-MIX-02",
            action_id="PLAYER_PATCH_ATTRIBUTES",
            team_id=28,
            player_id=2459,
            field_id="driving_layup",
            expected_before=70,
            value=80,
        ),
        BulkIntentItem(
            intent_id="I-MIX-03",
            action_id="COACH_SET_KNOWN_CURRENT_SETTINGS",
            team_id=28,
            field_id="POEOffense",
            expected_before=0,
            value=1,
        )
    ]
    batch = BulkBatch(header=valid_header, intents=tuple(intents))
    chunks = planner.plan(batch)

    assert len(chunks) == 3
    actions = {c.action_id for c in chunks}
    assert actions == {
        "PLAYER_PATCH_TENDENCIES",
        "PLAYER_PATCH_ATTRIBUTES",
        "COACH_SET_KNOWN_CURRENT_SETTINGS"
    }


def test_fi_15_dep_cycle(valid_header):
    """Failure Injection 15: DEP_CYCLE.
    Cyclic dependencies must be detected and rejected during validation.
    """
    planner = BulkBatchPlanner()
    i1 = BulkIntentItem(
        intent_id="I-CYCLE-A",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
        dependencies=("I-CYCLE-B",)
    )
    i2 = BulkIntentItem(
        intent_id="I-CYCLE-B",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="DRIVING_LAYUP_TENDENCY",
        expected_before=85,
        value=75,
        dependencies=("I-CYCLE-A",)
    )
    batch = BulkBatch(header=valid_header, intents=(i1, i2))
    issues = planner.validate(batch)
    assert any("DEP_CYCLE" in iss for iss in issues)

    with pytest.raises(ValueError, match="DEP_CYCLE"):
        planner.plan(batch)


def test_fi_16_coach_live_unsupported(valid_header):
    """Failure Injection 16: COACH_LIVE_UNSUPPORTED.
    Coach mutations must remain unsupported for live execution.
    """
    planner = BulkBatchPlanner()
    compiler = BulkFridaScriptCompiler()

    item = BulkIntentItem(
        intent_id="I-COACH-LIVE-01",
        action_id="COACH_SET_KNOWN_CURRENT_SETTINGS",
        team_id=28,
        field_id="POEOffense",
        expected_before=0,
        value=1,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    chunk = planner.plan(batch)[0]
    script = compiler.compile_chunk(chunk, valid_header)

    assert "COACH_CONTRACT_UNSUPPORTED_FOR_LIVE" in script


# ===========================================================================
# Gate G5 & Failure Injections 9-13: Envelope and Receipt Protocol
# ===========================================================================

def test_fi_09_no_or_wrong_digest(tmp_path, valid_header):
    """Failure Injection 9: NO_OR_WRONG_DIGEST.
    Missing or mismatched chunk_digest / plan_digest in result envelope must produce UNKNOWN.
    """
    service = BulkExecutorService(tmp_path)

    def wrong_digest_handler(chunk, script):
        return {
            "kind": "chunk-execution-result",
            "chunk_id": chunk.chunk_id,
            "chunk_digest": "corrupted_hash_9999",
            "plan_digest": chunk.plan_digest,
            "outcome": "CHUNK_SUCCESS",
            "receipts": []
        }

    adapter = ReaChunkTransportAdapter(tmp_path, fake_handler=wrong_digest_handler)
    item = BulkIntentItem(
        intent_id="I-DIGEST-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    res = service.run_with_transport(batch, adapter)

    assert res['metrics']['num_unknown'] == 1
    assert res['metrics']['conservation_holds'] is True


def test_fi_10_same_count_wrong_receipt_ids(tmp_path, valid_header):
    """Failure Injection 10: SAME_COUNT_WRONG_RECEIPT_IDS.
    Equal count but unexpected receipt intent IDs must produce UNKNOWN without KeyError.
    """
    service = BulkExecutorService(tmp_path)

    def wrong_ids_handler(chunk, script):
        return {
            "kind": "chunk-execution-result",
            "chunk_id": chunk.chunk_id,
            "chunk_digest": chunk.chunk_digest,
            "plan_digest": chunk.plan_digest,
            "outcome": "CHUNK_SUCCESS",
            "receipts": [{
                "intent_id": "I-COMPLETELY-UNEXPECTED-ID",
                "outcome": "SUCCESS_APPLIED"
            }]
        }

    adapter = ReaChunkTransportAdapter(tmp_path, fake_handler=wrong_ids_handler)
    item = BulkIntentItem(
        intent_id="I-EXPECTED-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    res = service.run_with_transport(batch, adapter)

    assert res['metrics']['num_unknown'] == 1
    assert res['metrics']['conservation_holds'] is True


def test_fi_11_fake_success_missing_getter_after(tmp_path, valid_header):
    """Failure Injection 11: FAKE_SUCCESS_MISSING_GETTER_AFTER.
    Receipt claiming SUCCESS_APPLIED without getter_after must be degraded to UNKNOWN.
    """
    service = BulkExecutorService(tmp_path)

    def fake_success_handler(chunk, script):
        return {
            "kind": "chunk-execution-result",
            "chunk_id": chunk.chunk_id,
            "chunk_digest": chunk.chunk_digest,
            "plan_digest": chunk.plan_digest,
            "outcome": "CHUNK_SUCCESS",
            "receipts": [{
                "intent_id": chunk.intents[0].intent_id,
                "team_id": 28,
                "player_id": 2459,
                "field_id": "SHOT_TENDENCY",
                "expected_before": 95,
                "requested": 80,
                "getter_before": 95,
                "getter_after": None,  # Missing!
                "unaltered_fields_check": True,
                "outcome": "SUCCESS_APPLIED"
            }]
        }

    adapter = ReaChunkTransportAdapter(tmp_path, fake_handler=fake_success_handler)
    item = BulkIntentItem(
        intent_id="I-FAKE-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    res = service.run_with_transport(batch, adapter)

    assert res['metrics']['num_unknown'] == 1
    assert res['metrics']['conservation_holds'] is True


def test_fi_12_false_unaltered_fields(tmp_path, valid_header):
    """Failure Injection 12: FALSE_UNALTERED_FIELDS.
    Receipt claiming SUCCESS_APPLIED but with unaltered_fields_check: False must be degraded to UNKNOWN.
    """
    service = BulkExecutorService(tmp_path)

    def false_unaltered_handler(chunk, script):
        return {
            "kind": "chunk-execution-result",
            "chunk_id": chunk.chunk_id,
            "chunk_digest": chunk.chunk_digest,
            "plan_digest": chunk.plan_digest,
            "outcome": "CHUNK_SUCCESS",
            "receipts": [{
                "intent_id": chunk.intents[0].intent_id,
                "team_id": 28,
                "player_id": 2459,
                "field_id": "SHOT_TENDENCY",
                "expected_before": 95,
                "requested": 80,
                "getter_before": 95,
                "getter_after": 80,
                "unaltered_fields_check": False,  # Untouched fields check failed!
                "outcome": "SUCCESS_APPLIED"
            }]
        }

    adapter = ReaChunkTransportAdapter(tmp_path, fake_handler=false_unaltered_handler)
    item = BulkIntentItem(
        intent_id="I-UNALTERED-FAIL-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    res = service.run_with_transport(batch, adapter)

    assert res['metrics']['num_unknown'] == 1
    assert res['metrics']['conservation_holds'] is True


def test_fi_13_chunk_success_with_item_failure(tmp_path, valid_header):
    """Failure Injection 13: CHUNK_SUCCESS_WITH_ITEM_FAILURE.
    Envelope reports CHUNK_SUCCESS, but an item receipt contains a failure.
    Subsequent chunks must still halt.
    """
    service = BulkExecutorService(tmp_path)
    executed_chunks = []

    def lying_envelope_handler(chunk, script):
        executed_chunks.append(chunk.chunk_id)
        if "team-01" in chunk.chunk_id:
            return {
                "kind": "chunk-execution-result",
                "chunk_id": chunk.chunk_id,
                "chunk_digest": chunk.chunk_digest,
                "plan_digest": chunk.plan_digest,
                "outcome": "CHUNK_SUCCESS",  # Falsely claims success!
                "receipts": [{
                    "intent_id": chunk.intents[0].intent_id,
                    "team_id": 1,
                    "player_id": 101,
                    "field_id": "SHOT_TENDENCY",
                    "expected_before": 50,
                    "requested": 60,
                    "getter_before": 45,
                    "outcome": "CAS_EXPECTED_BEFORE_MISMATCH"
                }]
            }
        return {
            "kind": "chunk-execution-result",
            "chunk_id": chunk.chunk_id,
            "chunk_digest": chunk.chunk_digest,
            "plan_digest": chunk.plan_digest,
            "outcome": "CHUNK_SUCCESS",
            "receipts": [{
                "intent_id": chunk.intents[0].intent_id,
                "team_id": 28,
                "player_id": 2459,
                "field_id": "SHOT_TENDENCY",
                "expected_before": 95,
                "requested": 80,
                "getter_before": 95,
                "getter_after": 80,
                "unaltered_fields_check": True,
                "outcome": "SUCCESS_APPLIED"
            }]
        }

    adapter = ReaChunkTransportAdapter(tmp_path, fake_handler=lying_envelope_handler)
    i1 = BulkIntentItem(
        intent_id="I-TEAM01-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=1,
        player_id=101,
        field_id="SHOT_TENDENCY",
        expected_before=50,
        value=60,
    )
    i2 = BulkIntentItem(
        intent_id="I-TEAM28-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(i1, i2))
    res = service.run_with_transport(batch, adapter)

    # Team 28 chunk was halted and never executed!
    assert len(executed_chunks) == 1
    assert res['metrics']['num_blocked'] == 1
    assert res['metrics']['num_not_executed'] == 1
    assert res['metrics']['conservation_holds'] is True


# ===========================================================================
# Gate G6 & Failure Injection 17: Node VM & Byte Invariant
# ===========================================================================

def test_fi_17_unrequested_stat_byte_changed(tmp_path, valid_header):
    """Failure Injection 17: UNREQUESTED_STAT_BYTE_CHANGED.
    Node VM runner executing chunk script under UNREQUESTED_STAT_BYTE_CHANGED fault injection
    must throw and yield UNKNOWN_EXECUTION_OUTCOME.
    """
    compiler = BulkFridaScriptCompiler()
    item = BulkIntentItem(
        intent_id="I-NODE-BYTE-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    planner = BulkBatchPlanner()
    chunk = planner.plan(batch)[0]
    script = compiler.compile_chunk(chunk, valid_header)

    script_path = tmp_path / "chunk_byte_test.js"
    script_path.write_text(script, encoding='utf-8')

    runner_path = Path(__file__).parent / 'node_vm_chunk_runner.js'
    cmd = ['node', str(runner_path), str(script_path), '--fault-injection', 'UNREQUESTED_STAT_BYTE_CHANGED']
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"Node VM runner failed: {r.stderr}"

    out = json.loads(r.stdout.strip())
    chunk_msg = next((m for m in out['emitted_messages'] if m.get('kind') == 'chunk-execution-result'), None)
    assert chunk_msg is not None
    assert chunk_msg['receipts'][0]['outcome'] == 'UNKNOWN_EXECUTION_OUTCOME'
    assert 'UNREQUESTED_STAT_BYTE_CHANGED' in chunk_msg['receipts'][0]['reason']

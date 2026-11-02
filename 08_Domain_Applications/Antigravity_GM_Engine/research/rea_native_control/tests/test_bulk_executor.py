"""Comprehensive unit and integration test suite for REA deterministic bulk executor.

Verifies the 10 gates of the verification plan:
1. Exact qualified fields and bounds fail-closed.
2. Hard CAS mismatch rejects before setter; partial/unknown never silent retry.
3. Synthetic multi-team deterministic receipts and strict conservation.
4. Duplicate/conflicting intent plan hashes and dependencies.
5. One controlled attached session per bounded chunk.
6. Read budget, call budget, and duration bounds.
7. Qualified handlers only; unsupported domains explicit.
8. Crash, abort, resume without double-write.
9. Receipt provenance and independent reconciliation.
10. Integrity and safe boundaries.
"""
import copy
from dataclasses import asdict
import json
from pathlib import Path
import pytest
import sys

_RESEARCH_DIR = Path(__file__).resolve().parent.parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

import contracts
from bulk_executor import (
    BulkBatch,
    BulkBatchHeader,
    BulkIntentItem,
    BulkBatchPlanner,
    BulkFridaScriptCompiler,
    BulkExecutorService,
    ExecutionJournal,
    FieldCatalogLoader,
    MockNativeEnvironment,
    PlannedChunk,
    GAME_BUILD_SHA256,
    generate_synthetic_batch,
    sha256_digest,
)


@pytest.fixture
def catalog():
    return FieldCatalogLoader.get_catalog()


@pytest.fixture
def planner(catalog):
    return BulkBatchPlanner(catalog)


@pytest.fixture
def valid_header():
    return BulkBatchHeader(
        batch_id="TEST-BATCH-001",
        save_instance_id="save_test_001",
        game_build_sha256=GAME_BUILD_SHA256,
        authorization_ref="AUTH-TEST-001",
        source_snapshot_ref="snap_test_001",
        dry_run=True,
    )


# ---------------------------------------------------------------------------
# Test Gate 1: Exact Qualified Fields and Bounds Fail-Closed
# ---------------------------------------------------------------------------

def test_exact_qualified_fields_and_bounds_fail_closed(planner, valid_header):
    # Valid tendency
    item_valid = BulkIntentItem(
        intent_id="I-001",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item_valid,))
    assert planner.validate(batch) == []

    # Out of bounds tendency (>100)
    item_oob = BulkIntentItem(
        intent_id="I-002",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=101,
    )
    batch_oob = BulkBatch(header=valid_header, intents=(item_oob,))
    issues = planner.validate(batch_oob)
    assert any("out of range" in iss.lower() or "must be integer in" in iss for iss in issues)

    # Valid attribute (25..99)
    item_attr_valid = BulkIntentItem(
        intent_id="I-003",
        action_id="COACH.STRATEGY.PLAYER_ATTRIBUTE",
        team_id=28,
        player_id=2459,
        field_id="driving_layup",
        expected_before=85,
        value=90,
    )
    assert planner.validate(BulkBatch(header=valid_header, intents=(item_attr_valid,))) == []

    # Out of bounds attribute (<25)
    item_attr_oob = BulkIntentItem(
        intent_id="I-004",
        action_id="COACH.STRATEGY.PLAYER_ATTRIBUTE",
        team_id=28,
        player_id=2459,
        field_id="driving_layup",
        expected_before=85,
        value=20,
    )
    issues_attr = planner.validate(BulkBatch(header=valid_header, intents=(item_attr_oob,)))
    assert any("must be integer in" in iss for iss in issues_attr)

    # Unknown field ID
    item_unknown_field = BulkIntentItem(
        intent_id="I-005",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="NON_EXISTENT_MAGIC_STAT",
        expected_before=50,
        value=60,
    )
    issues_unk = planner.validate(BulkBatch(header=valid_header, intents=(item_unknown_field,)))
    assert any("UNSUPPORTED_DOMAIN" in iss or "unknown" in iss for iss in issues_unk)

    # Game build mismatch fail-closed
    bad_header = BulkBatchHeader(
        batch_id="TEST-BAD-BUILD",
        save_instance_id="save_001",
        game_build_sha256="deadbeef" * 8,
        authorization_ref="AUTH-001",
        source_snapshot_ref="snap_001",
    )
    issues_build = planner.validate(BulkBatch(header=bad_header, intents=(item_valid,)))
    assert any("game_build_sha256 mismatch" in iss for iss in issues_build)


# ---------------------------------------------------------------------------
# Test Gate 2: Hard CAS Mismatch Rejection and No Silent Retry
# ---------------------------------------------------------------------------

def test_hard_cas_mismatch_blocks_setter_and_halts_chunk(tmp_path, valid_header):
    service = BulkExecutorService(tmp_path)
    env = MockNativeEnvironment()
    # Mock player current value is 95
    env.set_player_field(28, 2459, "SHOT_TENDENCY", 95)

    # Caller declares expected_before = 90 (mismatch!)
    item_cas_fail = BulkIntentItem(
        intent_id="I-CAS-FAIL",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=90,  # Mismatch!
        value=80,
    )
    item_after = BulkIntentItem(
        intent_id="I-FOLLOWUP",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="DRIVING_LAYUP_TENDENCY",
        expected_before=70,
        value=75,
    )
    batch = BulkBatch(header=valid_header, intents=(item_cas_fail, item_after))
    res = service.run_offline_test(batch, mock_env=env)

    # Assert CAS mismatch caught
    receipts = service.journal.load_receipts()
    assert len(receipts) == 2
    r_cas = next(r for r in receipts if r.intent_id == "I-CAS-FAIL")
    assert r_cas.outcome == "CAS_EXPECTED_BEFORE_MISMATCH"
    assert r_cas.getter_before == 95

    # Assert Setter was NEVER executed on Lillard (value remains 95)
    assert env.get_player_field(28, 2459, "SHOT_TENDENCY") == 95

    # Assert following item was NOT executed due to chunk halt
    r_after = next(r for r in receipts if r.intent_id == "I-FOLLOWUP")
    assert r_after.outcome == "NOT_EXECUTED"

    # Conservation holds
    assert res['metrics']['conservation_holds'] is True
    assert res['metrics']['num_blocked'] == 1
    assert res['metrics']['num_not_executed'] == 1


# ---------------------------------------------------------------------------
# Test Gate 3: No-op Detection (UNCHANGED_ALREADY_TARGET)
# ---------------------------------------------------------------------------

def test_noop_detection_unchanged_already_target(tmp_path, valid_header):
    service = BulkExecutorService(tmp_path)
    env = MockNativeEnvironment()
    env.set_player_field(28, 2459, "SHOT_TENDENCY", 80)

    # Target is already 80, expected_before is 80
    item_noop = BulkIntentItem(
        intent_id="I-NOOP",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=80,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item_noop,))
    res = service.run_offline_test(batch, mock_env=env)

    receipts = service.journal.load_receipts()
    assert len(receipts) == 1
    assert receipts[0].outcome == "UNCHANGED_ALREADY_TARGET"
    assert receipts[0].unaltered_fields_check is True
    assert res['metrics']['num_noop'] == 1
    assert res['metrics']['num_success'] == 0


# ---------------------------------------------------------------------------
# Test Gate 4: Duplicate, Conflicting Intents and Missing Dependencies
# ---------------------------------------------------------------------------

def test_duplicate_and_conflicting_intents(planner, valid_header):
    item1 = BulkIntentItem(
        intent_id="I-DUP",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    item2 = BulkIntentItem(
        intent_id="I-DUP",  # Duplicate ID
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    issues_dup = planner.validate(BulkBatch(header=valid_header, intents=(item1, item2)))
    assert any("duplicate intent_id" in iss for iss in issues_dup)

    # Contradictory targets on same player and field
    item3 = BulkIntentItem(
        intent_id="I-DIFF-1",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    item4 = BulkIntentItem(
        intent_id="I-DIFF-2",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=85,  # Contradictory value!
    )
    issues_contra = planner.validate(BulkBatch(header=valid_header, intents=(item3, item4)))
    assert any("CONTRADICTORY_INTENT" in iss for iss in issues_contra)

    # Missing dependency
    item5 = BulkIntentItem(
        intent_id="I-DEP",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
        dependencies=("NON_EXISTENT_PREDECESSOR",),
    )
    issues_dep = planner.validate(BulkBatch(header=valid_header, intents=(item5,)))
    assert any("MISSING_DEPENDENCY" in iss for iss in issues_dep)


# ---------------------------------------------------------------------------
# Test Gate 5: Bounded Session Chunking and Call Budgets
# ---------------------------------------------------------------------------

def test_bounded_chunking_and_call_budgets(planner, valid_header):
    # Create 120 items across 2 teams (70 items for team 1, 50 items for team 28)
    intents = []
    for i in range(70):
        intents.append(BulkIntentItem(
            intent_id=f"T1-{i:03d}",
            action_id="COACH.STRATEGY.PLAYER_TENDENCY",
            team_id=1,
            player_id=100 + (i % 10),
            field_id="SHOT_TENDENCY",
            expected_before=50,
            value=60,
        ))
    for i in range(50):
        intents.append(BulkIntentItem(
            intent_id=f"T28-{i:03d}",
            action_id="COACH.STRATEGY.PLAYER_TENDENCY",
            team_id=28,
            player_id=200 + (i % 10),
            field_id="SHOT_TENDENCY",
            expected_before=50,
            value=60,
        ))
    batch = BulkBatch(header=valid_header, intents=tuple(intents))

    # With max_chunk_size = 50:
    # Team 1 (70 items) should be split into 2 chunks (50 + 20)
    # Team 28 (50 items) should be 1 chunk (50)
    chunks = planner.plan(batch, max_chunk_size=50, max_call_budget=200)
    assert len(chunks) == 3
    assert chunks[0].team_id == 1 and len(chunks[0].intents) == 50
    assert chunks[1].team_id == 1 and len(chunks[1].intents) == 20
    assert chunks[2].team_id == 28 and len(chunks[2].intents) == 50

    # Ensure each chunk respects max_call_budget
    for c in chunks:
        assert c.estimated_call_count <= 200


# ---------------------------------------------------------------------------
# Test Gate 6: Script Compilation and Safety Assertions
# ---------------------------------------------------------------------------

def test_chunk_script_compilation(planner, valid_header):
    compiler = BulkFridaScriptCompiler()
    item = BulkIntentItem(
        intent_id="I-COMP-001",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    chunks = planner.plan(batch)
    script = compiler.compile_chunk(chunks[0], valid_header)

    # Assert essential REA safety elements are embedded
    assert "PeekMessageA" in script
    assert "0x978360" in script  # Native UI Getter
    assert "0x990a10" in script  # Native UI Setter
    assert "CAS_EXPECTED_BEFORE_MISMATCH" in script
    assert "UNCHANGED_ALREADY_TARGET" in script
    assert "CHUNK_PAYLOAD" in script
    assert "rosterPlayer" in script


# ---------------------------------------------------------------------------
# Test Gate 7: Unsupported Domains Explicitly Rejected
# ---------------------------------------------------------------------------

def test_unsupported_domains_explicitly_rejected(planner, valid_header):
    # Player tendency with missing player_id (e.g. Free Agent or malformed)
    item_missing_pid = BulkIntentItem(
        intent_id="I-NO-PID",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=None,
        field_id="SHOT_TENDENCY",
        expected_before=50,
        value=60,
    )
    issues = planner.validate(BulkBatch(header=valid_header, intents=(item_missing_pid,)))
    assert any("requires integer player_id" in iss for iss in issues)

    # Badges or non-roster entity field
    item_raw = BulkIntentItem(
        intent_id="I-RAW",
        action_id="RAW_MEMORY_WRITER",
        team_id=28,
        player_id=2459,
        field_id="RAW_BYTE_OFFSET_0x1234",
        expected_before=0,
        value=1,
    )
    issues_raw = planner.validate(BulkBatch(header=valid_header, intents=(item_raw,)))
    assert any("UNSUPPORTED_DOMAIN" in iss for iss in issues_raw)


# ---------------------------------------------------------------------------
# Test Gate 8: Failure Injection, Unknown Handling & Journal Resume
# ---------------------------------------------------------------------------

def test_failure_injection_and_resume_without_double_write(tmp_path, valid_header):
    service = BulkExecutorService(tmp_path)
    env = MockNativeEnvironment()
    env.set_player_field(28, 2459, "SHOT_TENDENCY", 95)
    env.set_player_field(28, 2459, "DRIVING_LAYUP_TENDENCY", 70)

    # Inject timeout/crash on item 1
    env.failure_injections["I-CRASH-001"] = "TIMEOUT_OR_CRASH"

    item1 = BulkIntentItem(
        intent_id="I-CRASH-001",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    item2 = BulkIntentItem(
        intent_id="I-BLOCKED-002",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="DRIVING_LAYUP_TENDENCY",
        expected_before=70,
        value=75,
    )
    batch = BulkBatch(header=valid_header, intents=(item1, item2))
    res = service.run_offline_test(batch, mock_env=env)

    assert res['metrics']['num_unknown'] == 1
    assert res['metrics']['num_not_executed'] == 1
    assert res['metrics']['conservation_holds'] is True

    # Assert journal recorded UNKNOWN
    receipts = service.journal.load_receipts()
    assert receipts[0].outcome == "UNKNOWN_EXECUTION_OUTCOME"
    assert receipts[1].outcome == "NOT_EXECUTED"

    # Verify that an intent in UNKNOWN cannot be silently marked completed
    assert service.journal.is_intent_completed("I-CRASH-001") is False


# ---------------------------------------------------------------------------
# Test Gate 9: Strict Conservation Law Under Mixed Stress Scenario
# ---------------------------------------------------------------------------

def test_strict_conservation_law_under_mixed_stress(tmp_path, valid_header):
    service = BulkExecutorService(tmp_path)
    env = MockNativeEnvironment()

    # Pre-populate 10 items on 10 distinct players in team 10
    intents = []
    for i in range(10):
        iid = f"MIX-{i:02d}"
        pid = 100 + i
        if i < 4:
            # Success items
            env.set_player_field(10, pid, "SHOT_TENDENCY", 50)
            intents.append(BulkIntentItem(
                intent_id=iid,
                action_id="COACH.STRATEGY.PLAYER_TENDENCY",
                team_id=10,
                player_id=pid,
                field_id="SHOT_TENDENCY",
                expected_before=50,
                value=60,
            ))
        elif i < 7:
            # No-op items (current == expected == value)
            env.set_player_field(10, pid, "SHOT_TENDENCY", 50)
            intents.append(BulkIntentItem(
                intent_id=iid,
                action_id="COACH.STRATEGY.PLAYER_TENDENCY",
                team_id=10,
                player_id=pid,
                field_id="SHOT_TENDENCY",
                expected_before=50,
                value=50,  # No-op!
            ))
        elif i == 7:
            # CAS mismatch item (halts the rest of chunk!)
            env.set_player_field(10, pid, "SHOT_TENDENCY", 99)
            intents.append(BulkIntentItem(
                intent_id=iid,
                action_id="COACH.STRATEGY.PLAYER_TENDENCY",
                team_id=10,
                player_id=pid,
                field_id="SHOT_TENDENCY",
                expected_before=50,  # Mismatch (env is 99)
                value=60,
            ))
        else:
            # Remaining items (will be NOT_EXECUTED)
            env.set_player_field(10, pid, "SHOT_TENDENCY", 50)
            intents.append(BulkIntentItem(
                intent_id=iid,
                action_id="COACH.STRATEGY.PLAYER_TENDENCY",
                team_id=10,
                player_id=pid,
                field_id="SHOT_TENDENCY",
                expected_before=50,
                value=60,
            ))

    batch = BulkBatch(header=valid_header, intents=tuple(intents))
    res = service.run_offline_test(batch, mock_env=env)

    m = res['metrics']
    assert m['num_planned'] == 10
    assert m['num_success'] == 4
    assert m['num_noop'] == 3
    assert m['num_blocked'] == 1
    assert m['num_unknown'] == 0
    assert m['num_not_executed'] == 2

    # Conservation equation check
    accounted = m['num_success'] + m['num_noop'] + m['num_blocked'] + m['num_unknown'] + m['num_not_executed']
    assert accounted == m['num_planned']
    assert m['conservation_holds'] is True


# ---------------------------------------------------------------------------
# Test Gate 10: Plan Digest Immutability and Determinism
# ---------------------------------------------------------------------------

def test_plan_digest_immutability(valid_header):
    item = BulkIntentItem(
        intent_id="I-DIGEST",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    b1 = BulkBatch(header=valid_header, intents=(item,))
    d1 = sha256_digest({'header': asdict(b1.header), 'intents': [asdict(i) for i in b1.intents]})

    # Exact same content produces exact same digest
    b2 = BulkBatch(header=valid_header, intents=(item,))
    d2 = sha256_digest({'header': asdict(b2.header), 'intents': [asdict(i) for i in b2.intents]})
    assert d1 == d2

    # Changing even a single parameter (e.g. value 80 -> 81) changes digest completely
    item_mod = BulkIntentItem(
        intent_id="I-DIGEST",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=81,  # Modified
    )
    b3 = BulkBatch(header=valid_header, intents=(item_mod,))
    d3 = sha256_digest({'header': asdict(b3.header), 'intents': [asdict(i) for i in b3.intents]})
    assert d1 != d3


# ---------------------------------------------------------------------------
# Test Gate 11: Coach and Player Script Generation & Routing
# ---------------------------------------------------------------------------

def test_coach_and_player_script_generation_routing(planner, valid_header):
    compiler = BulkFridaScriptCompiler()
    # Chunk with 1 player item and 1 coach item on Team 28
    item_player = BulkIntentItem(
        intent_id="I-ROUTING-PLAYER",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    item_coach = BulkIntentItem(
        intent_id="I-ROUTING-COACH",
        action_id="COACH.STRATEGY.POE_O1",
        team_id=28,
        field_id="POEOffense",
        expected_before=0,
        value=1,
    )
    batch = BulkBatch(header=valid_header, intents=(item_player, item_coach))
    chunks = planner.plan(batch)
    assert len(chunks) == 1
    script = compiler.compile_chunk(chunks[0], valid_header)

    # Verify Player routing code
    assert "rosterPlayer" in script
    assert "call('player.get_stat_ui'" in script
    assert "call('player.set_stat_ui'" in script

    # Verify Coach routing code
    assert "franchiseRecord" in script
    assert "call('coach.apply_gameplan'" in script
    assert "coach_items" in script


# ---------------------------------------------------------------------------
# Test Gate 12: UNKNOWN Resource Locking and Reconciliation
# ---------------------------------------------------------------------------

def test_unknown_resource_locking_and_reconciliation(tmp_path, valid_header):
    service = BulkExecutorService(tmp_path)
    env = MockNativeEnvironment()
    env.set_player_field(28, 2459, "SHOT_TENDENCY", 95)

    # 1. First run: inject crash on Lillard SHOT_TENDENCY
    env.failure_injections["I-LOCK-001"] = "TIMEOUT_OR_CRASH"
    item1 = BulkIntentItem(
        intent_id="I-LOCK-001",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    b1 = BulkBatch(header=valid_header, intents=(item1,))
    res1 = service.run_offline_test(b1, mock_env=env)
    assert res1['metrics']['num_unknown'] == 1

    # Verify target resource is locked
    res_key = "team:28:player:2459:field:SHOT_TENDENCY"
    assert service.journal.is_resource_locked(res_key) == "I-LOCK-001"

    # 2. Second run: a different intent attempts to modify the same locked resource
    item2 = BulkIntentItem(
        intent_id="I-BLOCKED-BY-LOCK",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=82,
    )
    b2 = BulkBatch(header=valid_header, intents=(item2,))
    res2 = service.run_offline_test(b2, mock_env=env)

    # Verify item2 is BLOCKED without calling Setter!
    assert res2['metrics']['num_blocked'] == 1
    receipts2 = [r for r in service.journal.load_receipts() if r.intent_id == "I-BLOCKED-BY-LOCK"]
    assert len(receipts2) == 1
    assert receipts2[0].outcome == "BLOCKED_BY_PRIOR_UNKNOWN_CLAIM"

    # 3. Third step: Reconcile the UNKNOWN intent with independent evidence
    recon_evidence = {
        "intent_id": "I-LOCK-001",
        "team_id": 28,
        "player_id": 2459,
        "field_id": "SHOT_TENDENCY",
        "applied": False,
        "evidence_id": "ev_reconciliation_obs_001"
    }
    updated_receipt = service.journal.reconcile_unknown("I-LOCK-001", recon_evidence)
    assert updated_receipt.outcome == "RECONCILED_REJECTED"

    # Verify resource lock is released!
    assert service.journal.is_resource_locked(res_key) is None

    # 4. Fourth step: Now intent3 on the same resource can proceed and succeed!
    item3 = BulkIntentItem(
        intent_id="I-UNBLOCKED-NOW",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    b3 = BulkBatch(header=valid_header, intents=(item3,))
    res3 = service.run_offline_test(b3, mock_env=env)
    assert res3['metrics']['num_success'] == 1


# ---------------------------------------------------------------------------
# Test Gate 13: At-Most-Once Execution and Resume
# ---------------------------------------------------------------------------

def test_at_most_once_execution_and_resume(tmp_path, valid_header):
    service = BulkExecutorService(tmp_path)
    env = MockNativeEnvironment()
    env.set_player_field(28, 2459, "SHOT_TENDENCY", 95)

    item = BulkIntentItem(
        intent_id="I-ONCE-001",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    batch = BulkBatch(header=valid_header, intents=(item,))

    # First execution -> SUCCESS_APPLIED
    res1 = service.run_offline_test(batch, mock_env=env)
    assert res1['metrics']['num_success'] == 1

    # Second execution of same batch with same journal -> REUSED_HISTORICAL_RECEIPT (no second setter)
    res2 = service.run_offline_test(batch, mock_env=env)
    assert res2['metrics']['num_reused'] == 1
    assert res2['metrics']['num_success'] == 0
    assert res2['metrics']['conservation_holds'] is True


# ---------------------------------------------------------------------------
# Test Gate 14: Checkpoint014 Transport Live Mutation Fail-Closed
# ---------------------------------------------------------------------------

def test_rea_chunk_transport_adapter_default_prohibits_live(tmp_path, valid_header, planner):
    from bulk_executor import ReaChunkTransportAdapter
    adapter = ReaChunkTransportAdapter(tmp_path, live_context=None)
    item = BulkIntentItem(
        intent_id="I-FAIL-CLOSED",
        action_id="COACH.STRATEGY.PLAYER_TENDENCY",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    chunk = planner.plan(BulkBatch(header=valid_header, intents=(item,)))[0]

    with pytest.raises(PermissionError) as exc_info:
        adapter.execute_chunk(chunk, "// script")
    assert "LIVE_MUTATION_NOT_AUTHORIZED" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Test Gate 15: 10,000-Item Synthetic Stress Benchmark Auto-Generation
# ---------------------------------------------------------------------------

def test_10k_synthetic_benchmark_auto_generation(tmp_path):
    from bulk_executor import run_10k_benchmark
    bench_out = tmp_path / "test_benchmark.json"
    res = run_10k_benchmark(output_path=bench_out)

    assert bench_out.is_file()
    assert res['scale']['total_intents'] == 10000
    assert res['outcome_conservation']['conservation_holds'] is True

    # Check 3-way metric separation
    assert 'mock_execution_timings' in res
    assert 'session_overhead_estimates' in res
    assert 'projected_live_native_duration' in res

    # Verify mock throughput is high
    assert res['mock_execution_timings']['mock_throughput_ops_per_sec'] > 10000.0

    # Verify session overhead reduction is significant
    assert res['session_overhead_estimates']['session_overhead_reduction_percent'] > 95.0


# ===========================================================================
# Round 2 Remediation Acceptance Gates (G1 - G6)
# ===========================================================================

# ---------------------------------------------------------------------------
# Gate G1: Default Denial of Live Execution
# ---------------------------------------------------------------------------

def test_gate_g1_default_denial(tmp_path, valid_header, planner):
    from bulk_executor import ReaChunkTransportAdapter, cli_execute_authorized
    import argparse

    # 1. ReaChunkTransportAdapter with live_context enabled fails closed
    live_ctx = contracts.LiveExecutionContext(
        authorization_ref="AUTH-TEST",
        allowed_action_ids=frozenset(["PLAYER_PATCH_TENDENCIES"]),
        maximum_game_calls=500,
        enabled=True
    ) if hasattr(contracts, 'LiveExecutionContext') else type('LiveCtx', (), {'enabled': True, 'authorization_ref': 'AUTH-TEST'})()

    adapter = ReaChunkTransportAdapter(tmp_path, live_context=live_ctx)
    item = BulkIntentItem(
        intent_id="I-G1-001",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80,
    )
    chunk = planner.plan(BulkBatch(header=valid_header, intents=(item,)))[0]

    with pytest.raises(PermissionError) as exc_info:
        adapter.execute_chunk(chunk, "// script")
    assert "LIVE_AUTHORIZATION_VERIFIER_NOT_AVAILABLE" in str(exc_info.value)

    # 2. cli_execute_authorized exits fail-closed
    batch_file = tmp_path / "batch.json"
    batch_file.write_text(json.dumps({
        "batch_id": "BATCH-G1",
        "save_instance_id": "save_g1",
        "game_build_sha256": GAME_BUILD_SHA256,
        "authorization_ref": "AUTH-G1",
        "source_snapshot_ref": "snap_g1",
        "dry_run": False,
        "intents": [{
            "intent_id": "I-G1-002",
            "action_id": "PLAYER_PATCH_TENDENCIES",
            "team_id": 28,
            "player_id": 2459,
            "field_id": "SHOT_TENDENCY",
            "expected_before": 95,
            "value": 80
        }]
    }), encoding='utf-8')

    args = argparse.Namespace(
        batch_file=str(batch_file),
        allow_live_mutation=True,
        runtime_dir=str(tmp_path),
        expected_pid=None
    )
    with pytest.raises(SystemExit) as exit_info:
        cli_execute_authorized(args)
    assert exit_info.value.code == 1


# ---------------------------------------------------------------------------
# Gate G2: End-to-End Fake Transport Integration
# ---------------------------------------------------------------------------

def test_gate_g2_e2e_fake_transport(tmp_path, valid_header):
    from bulk_executor import ReaChunkTransportAdapter

    service = BulkExecutorService(tmp_path)
    fake_calls = []

    def fake_handler(chunk, script):
        fake_calls.append(chunk.chunk_id)
        receipts = []
        for it in chunk.intents:
            receipts.append({
                "intent_id": it.intent_id,
                "team_id": it.team_id,
                "player_id": it.player_id,
                "field_id": it.field_id,
                "expected_before": it.expected_before,
                "requested": it.value,
                "getter_before": it.expected_before,
                "getter_after": it.value,
                "raw_after": it.value,
                "outcome": "SUCCESS_APPLIED",
                "unaltered_fields_check": True
            })
        return {
            "kind": "chunk-execution-result",
            "chunk_id": chunk.chunk_id,
            "chunk_digest": chunk.chunk_digest,
            "plan_digest": chunk.plan_digest,
            "action_id": chunk.action_id,
            "outcome": "CHUNK_SUCCESS",
            "receipts": receipts,
            "evidence_id": f"fake_ev_{chunk.chunk_id}"
        }

    adapter = ReaChunkTransportAdapter(tmp_path, fake_handler=fake_handler)

    # Multi-chunk batch across 2 teams (Team 1 and Team 28)
    intents = [
        BulkIntentItem(
            intent_id="I-G2-T1-01",
            action_id="PLAYER_PATCH_TENDENCIES",
            team_id=1,
            player_id=101,
            field_id="SHOT_TENDENCY",
            expected_before=50,
            value=60
        ),
        BulkIntentItem(
            intent_id="I-G2-T1-02",
            action_id="PLAYER_PATCH_ATTRIBUTES",
            team_id=1,
            player_id=101,
            field_id="driving_layup",
            expected_before=70,
            value=80
        ),
        BulkIntentItem(
            intent_id="I-G2-T28-01",
            action_id="PLAYER_PATCH_TENDENCIES",
            team_id=28,
            player_id=2459,
            field_id="SHOT_TENDENCY",
            expected_before=95,
            value=80
        )
    ]
    batch = BulkBatch(header=valid_header, intents=tuple(intents))

    result = service.run_with_transport(batch, adapter)

    # Verify Fake transport received execution calls for both teams
    assert len(fake_calls) == 2
    assert result['metrics']['num_planned'] == 3
    assert result['metrics']['num_success'] == 3
    assert result['metrics']['conservation_holds'] is True

    # Verify receipts in journal
    receipts = service.journal.load_receipts()
    assert len(receipts) == 3
    assert all(r.outcome == 'SUCCESS_APPLIED' for r in receipts)


# ---------------------------------------------------------------------------
# Gate G3: Protocol Negative Tests (Missing/Duplicate/Mismatched Digests)
# ---------------------------------------------------------------------------

def test_gate_g3_protocol_negative_handling(tmp_path, valid_header):
    from bulk_executor import ReaChunkTransportAdapter

    service = BulkExecutorService(tmp_path)

    # 1. Protocol failure: Transport raises exception
    def failing_handler(chunk, script):
        raise ConnectionResetError("Frida session disconnected unexpectedly")

    adapter_fail = ReaChunkTransportAdapter(tmp_path, fake_handler=failing_handler)
    item1 = BulkIntentItem(intent_id="I-G3-01", action_id="PLAYER_PATCH_TENDENCIES", team_id=1, player_id=101, field_id="SHOT_TENDENCY", expected_before=50, value=60)
    item2 = BulkIntentItem(intent_id="I-G3-02", action_id="PLAYER_PATCH_TENDENCIES", team_id=28, player_id=2459, field_id="SHOT_TENDENCY", expected_before=95, value=80)
    b1 = BulkBatch(header=valid_header, intents=(item1, item2))

    res1 = service.run_with_transport(b1, adapter_fail)
    assert res1['metrics']['num_unknown'] == 1
    assert res1['metrics']['num_not_executed'] == 1
    assert res1['metrics']['conservation_holds'] is True

    # Verify resource of first intent is locked
    assert service.journal.is_resource_locked("team:1:player:101:field:SHOT_TENDENCY") == "I-G3-01"

    # 2. Protocol failure: Mismatched chunk_digest
    def bad_digest_handler(chunk, script):
        return {
            "kind": "chunk-execution-result",
            "chunk_id": chunk.chunk_id,
            "chunk_digest": "corrupted_digest_hash_0000",
            "plan_digest": chunk.plan_digest,
            "outcome": "CHUNK_SUCCESS",
            "receipts": []
        }

    service2 = BulkExecutorService(tmp_path / "j2")
    adapter_bad_digest = ReaChunkTransportAdapter(tmp_path, fake_handler=bad_digest_handler)
    res2 = service2.run_with_transport(b1, adapter_bad_digest)
    assert res2['metrics']['num_unknown'] == 1
    assert res2['metrics']['num_not_executed'] == 1
    assert res2['metrics']['conservation_holds'] is True

    # 3. Protocol failure: Duplicate receipt in chunk
    def duplicate_receipt_handler(chunk, script):
        return {
            "kind": "chunk-execution-result",
            "chunk_id": chunk.chunk_id,
            "chunk_digest": chunk.chunk_digest,
            "plan_digest": chunk.plan_digest,
            "outcome": "CHUNK_SUCCESS",
            "receipts": [
                {"intent_id": chunk.intents[0].intent_id, "outcome": "SUCCESS_APPLIED"},
                {"intent_id": chunk.intents[0].intent_id, "outcome": "SUCCESS_APPLIED"}
            ]
        }

    service3 = BulkExecutorService(tmp_path / "j3")
    adapter_dup = ReaChunkTransportAdapter(tmp_path, fake_handler=duplicate_receipt_handler)
    res3 = service3.run_with_transport(b1, adapter_dup)
    assert res3['metrics']['num_unknown'] == 1
    assert res3['metrics']['num_not_executed'] == 1
    assert res3['metrics']['conservation_holds'] is True


# ---------------------------------------------------------------------------
# Gate G4: Node VM Native Execution & Memory Invariant Injections
# ---------------------------------------------------------------------------

def test_gate_g4_node_vm_native_contracts_and_fault_injections(tmp_path, valid_header):
    import subprocess
    compiler = BulkFridaScriptCompiler()

    # 1. Normal execution in Node VM
    item = BulkIntentItem(
        intent_id="I-G4-LILLARD",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    planner = BulkBatchPlanner()
    chunk = planner.plan(batch)[0]
    script = compiler.compile_chunk(chunk, valid_header)

    script_path = tmp_path / "chunk_lillard.js"
    script_path.write_text(script, encoding='utf-8')

    runner_path = Path(__file__).parent / 'node_vm_chunk_runner.js'
    cmd = ['node', str(runner_path), str(script_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"Node VM runner failed: {r.stderr}"

    out = json.loads(r.stdout.strip())
    assert out.get('success') is True
    messages = out.get('emitted_messages', [])
    assert len(messages) >= 1
    chunk_msg = next((m for m in messages if m.get('kind') == 'chunk-execution-result'), None)
    assert chunk_msg is not None
    assert chunk_msg['outcome'] == 'CHUNK_SUCCESS'
    assert len(chunk_msg['receipts']) == 1
    assert chunk_msg['receipts'][0]['outcome'] == 'SUCCESS_APPLIED'
    assert chunk_msg['receipts'][0]['getter_after'] == 80

    # 2. Fault injection: CAS Mismatch in Node VM -> zero setter
    cmd_cas = ['node', str(runner_path), str(script_path), '--fault-injection', 'CAS_MISMATCH']
    r_cas = subprocess.run(cmd_cas, capture_output=True, text=True)
    out_cas = json.loads(r_cas.stdout.strip())
    chunk_cas = next((m for m in out_cas['emitted_messages'] if m.get('kind') == 'chunk-execution-result'), None)
    assert chunk_cas is not None
    assert chunk_cas['outcome'] == 'CHUNK_HALTED'
    assert chunk_cas['receipts'][0]['outcome'] == 'CAS_EXPECTED_BEFORE_MISMATCH'

    # 3. Fault injection: Unrequested stat byte changed -> throws UNREQUESTED_STAT_BYTE_CHANGED
    cmd_unreq = ['node', str(runner_path), str(script_path), '--fault-injection', 'UNREQUESTED_STAT_BYTE_CHANGED']
    r_unreq = subprocess.run(cmd_unreq, capture_output=True, text=True)
    out_unreq = json.loads(r_unreq.stdout.strip())
    chunk_unreq = next((m for m in out_unreq['emitted_messages'] if m.get('kind') == 'chunk-execution-result'), None)
    assert chunk_unreq is not None
    assert chunk_unreq['receipts'][0]['outcome'] == 'UNKNOWN_EXECUTION_OUTCOME'
    assert 'UNREQUESTED_STAT_BYTE_CHANGED' in chunk_unreq['receipts'][0]['reason']

    # 4. Fault injection: Corrupt delegate vtable -> throws UNRECOVERED_PLAYER_STAT_DELEGATE
    cmd_del = ['node', str(runner_path), str(script_path), '--fault-injection', 'CORRUPT_DELEGATE']
    r_del = subprocess.run(cmd_del, capture_output=True, text=True)
    out_del = json.loads(r_del.stdout.strip())
    # Fails in PeekMessageA hook callback
    ctrl_msg = next((m for m in out_del['emitted_messages'] if m.get('kind') == 'native-control-result'), None)
    assert ctrl_msg is not None
    assert ctrl_msg['outcome'] == 'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY'


# ---------------------------------------------------------------------------
# Gate G5: Recovery & Crash Window Handling
# ---------------------------------------------------------------------------

def test_gate_g5_recovery_and_journal_fault_injection(tmp_path, valid_header):
    journal_dir = tmp_path / "journal_recovery"
    claims_dir = journal_dir / "claims"
    claims_dir.mkdir(parents=True, exist_ok=True)

    # 1. Simulate process crash before receipts: write claim in STARTED state
    interrupted_claim = {
        "claim_id": "chunk-0001-team-28-player-patch-tendencies",
        "batch_id": "BATCH-CRASH-TEST",
        "plan_digest": "plan_digest_001",
        "chunk_id": "chunk-0001-team-28-player-patch-tendencies",
        "chunk_digest": "chunk_digest_001",
        "save_instance_id": "save_test_001",
        "action_id": "PLAYER_PATCH_TENDENCIES",
        "team_id": 28,
        "state": "STARTED",
        "created_at": "2026-11-01T20:00:00Z",
        "intents": [
            {
                "intent_id": "I-CRASH-SAVED-CLAIM",
                "resource_key": "team:28:player:2459:field:SHOT_TENDENCY",
                "expected_before": 95,
                "value": 80
            }
        ]
    }
    (claims_dir / "chunk-0001-team-28-player-patch-tendencies.json").write_text(json.dumps(interrupted_claim), encoding='utf-8')

    # Initialize ExecutionJournal -> startup recovery must detect crash and lock resource!
    journal = ExecutionJournal(journal_dir)
    res_key = "team:28:player:2459:field:SHOT_TENDENCY"
    assert journal.is_resource_locked(res_key) == "I-CRASH-SAVED-CLAIM"

    # Verify claim state was updated to UNKNOWN_EXECUTION_OUTCOME
    saved_claim = json.loads((claims_dir / "chunk-0001-team-28-player-patch-tendencies.json").read_text(encoding='utf-8'))
    assert saved_claim['state'] == 'UNKNOWN_EXECUTION_OUTCOME'

    # 2. Corrupt lock ledger fail-closed
    journal.locks_file.write_text("{CORRUPTED_JSON_INVALID", encoding='utf-8')
    with pytest.raises(RuntimeError) as exc_info:
        ExecutionJournal(journal_dir)
    assert "CORRUPT_LOCK_LEDGER" in str(exc_info.value)

    # 3. Intent ID reused with changed payload fail-closed
    journal_dir2 = tmp_path / "journal_reuse"
    journal2 = ExecutionJournal(journal_dir2)
    planner = BulkBatchPlanner()
    item_orig = BulkIntentItem(intent_id="I-REUSE-PAYLOAD", action_id="PLAYER_PATCH_TENDENCIES", team_id=28, player_id=2459, field_id="SHOT_TENDENCY", expected_before=95, value=80)
    chunk_orig = planner.plan(BulkBatch(header=valid_header, intents=(item_orig,)))[0]
    journal2.claim_chunk(chunk_orig)

    # Attempt to claim same intent_id with value 85 instead of 80
    item_changed = BulkIntentItem(intent_id="I-REUSE-PAYLOAD", action_id="PLAYER_PATCH_TENDENCIES", team_id=28, player_id=2459, field_id="SHOT_TENDENCY", expected_before=95, value=85)
    chunk_changed = planner.plan(BulkBatch(header=valid_header, intents=(item_changed,)))[0]
    with pytest.raises(ValueError) as exc_info2:
        journal2.claim_chunk(chunk_changed)
    assert "INTENT_ID_REUSED_WITH_DIFFERENT_PAYLOAD" in str(exc_info2.value)


# ---------------------------------------------------------------------------
# Gate G6: Benchmark Dynamic Aggregation & Metric Separation
# ---------------------------------------------------------------------------

def test_gate_g6_benchmark_dynamic_aggregation(tmp_path):
    from bulk_executor import run_10k_benchmark
    bench_file = tmp_path / "dyn_bench.json"
    res = run_10k_benchmark(output_path=bench_file)

    oc = res['outcome_conservation']
    assert oc['metric_type'] == 'DYNAMICALLY_AGGREGATED_RECEIPTS'
    assert oc['total_accounted'] == 10000
    assert oc['num_planned'] == 10000
    assert oc['conservation_holds'] is True

    # Check distinct labeling across 3 tiers
    assert res['mock_execution_timings']['metric_type'] == 'MEASURED_MOCK'
    assert res['session_overhead_estimates']['metric_type'] == 'ESTIMATED_THEORETICAL'
    assert res['projected_live_native_duration']['metric_type'] == 'PROJECTED_NOT_RUN'


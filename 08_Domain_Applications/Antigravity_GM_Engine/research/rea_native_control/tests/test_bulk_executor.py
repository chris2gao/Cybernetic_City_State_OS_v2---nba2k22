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
        expected_before=50,
        value=65,
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

"""End-to-End Offline Closed Loop Integration Tests (Gates G8, G9, G10).

Validates the full cycle:
1. Multi-role draft intent accumulation (GM, Coach).
2. Immutable cycle sealing into RoleActionBatch with deterministic digest.
3. Pure translation via DecisionBatchBridge into BulkBatch, segregating unsupported actions.
4. BoundedSessionExecutor execution via Fake REA transport with Claim-before-Setter.
5. Independent fail-closed validation via validate_batch_execution.
6. Feedback of receipts into DecisionOutbox, updating status and outcome summaries.
7. Crash resilience and UNKNOWN resource lock preservation.
"""
from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile
import pytest

_RESEARCH_DIR = Path(__file__).resolve().parent.parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

import contracts
from bulk_executor import (
    BulkBatch,
    BulkBatchPlanner,
    ExecutionJournal,
    ItemReceipt,
    sha256_digest
)
from bounded_session_transport import BoundedSessionExecutor
from decision_batch_bridge import DecisionBatchBridge, BridgeResult
from decision_outbox import DecisionOutbox
from role_batches import (
    ActionIntent,
    BatchContext,
    RoleActionBatch
)
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService
from validate_batch_execution import validate_batch_execution


def make_context(catalog_version: str) -> BatchContext:
    return BatchContext(
        world_id="WORLD-001",
        save_instance_id="MyLEAGUE0003",
        generation_id="GEN-001",
        season_id="2021-22",
        phase="REGULAR_SEASON",
        snapshot_ref="snapshot_gold_001",
        catalog_version=catalog_version
    )


def make_profiles():
    gm = RoleCapabilityProfile(
        role_type="GM",
        actor_uid="gm_user_01",
        team_scope=(1, 25, 28),
        world_id="WORLD-001",
        save_instance_id="MyLEAGUE0003",
        generation_id="GEN-001",
        season_id="2021-22",
        phase="REGULAR_SEASON",
        snapshot_ref="snapshot_gold_001",
        allowed_actions=frozenset([
            "PLAYER.EDIT.TENDENCY_BATCH",
            "GM.TRADE.MIXED"
        ])
    )
    coach = RoleCapabilityProfile(
        role_type="COACH",
        actor_uid="coach_user_01",
        team_scope=(1,),
        world_id="WORLD-001",
        save_instance_id="MyLEAGUE0003",
        generation_id="GEN-001",
        season_id="2021-22",
        phase="REGULAR_SEASON",
        snapshot_ref="snapshot_gold_001",
        allowed_actions=frozenset([
            "COACH.STRATEGY.RUN_PLAY"
        ])
    )
    return gm, coach


def test_g9_full_offline_decision_to_execution_closed_loop(tmp_path):
    """Gate G9: End-to-end multi-role decision accumulation, sealing, bridge translation,
    mock execution, fail-closed validation, and outbox feedback.
    """
    db_path = tmp_path / "outbox.db"
    outbox = DecisionOutbox(db_path)
    service = RoleCapabilityService()
    bridge = DecisionBatchBridge(service)
    ctx = make_context(service.version)
    gm, coach = make_profiles()
    profiles = (gm, coach)
    phase_grants = {
        ("gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH"),
        ("gm_user_01", "GM.TRADE.MIXED"),
        ("coach_user_01", "COACH.STRATEGY.RUN_PLAY")
    }

    cycle_id = "CYCLE-E2E-CLOSED-LOOP-001"
    outbox.open_cycle(cycle_id, ctx)

    # Step 1: Accumulate draft intents
    # GM edits Giannis Antetokounmpo (1607) tendencies
    intent_giannis = ActionIntent.decided(
        "I-GM-GIANNIS-TENDENCIES",
        "gm_user_01",
        "PLAYER.EDIT.TENDENCY_BATCH",
        {
            "team_id": 1,
            "player_id": 1607,
            "expected_before": 70,
            "values": {
                "SHOT_TENDENCY": 75,
                "SHOT_CLOSE_TENDENCY": 90
            }
        }
    )
    outbox.add_intent(cycle_id, intent_giannis, gm, phase_grants, decision_reason="Optimize shot selection")

    # GM edits Damian Lillard (2459) tendency
    intent_lillard = ActionIntent.decided(
        "I-GM-LILLARD-TENDENCIES",
        "gm_user_01",
        "PLAYER.EDIT.TENDENCY_BATCH",
        {
            "team_id": 28,
            "player_id": 2459,
            "expected_before": 75,
            "values": {
                "SHOT_TENDENCY": 80
            }
        }
    )
    outbox.add_intent(cycle_id, intent_lillard, gm, phase_grants, decision_reason="Load management pacing")

    # Coach sets strategy
    intent_coach = ActionIntent.decided(
        "I-COACH-RUN-PLAY",
        "coach_user_01",
        "COACH.STRATEGY.RUN_PLAY",
        {
            "team_id": 1,
            "expected_before": 50,
            "settings": {
                "RunPlayTendency": 65
            }
        }
    )
    outbox.add_intent(cycle_id, intent_coach, coach, phase_grants, decision_reason="Increase set play frequency")

    # GM submits unsupported / pending trade intent
    intent_trade = ActionIntent.decided(
        "I-GM-TRADE-PROPOSAL",
        "gm_user_01",
        "GM.TRADE.MIXED",
        {
            "team_a": 1,
            "team_b": 28,
            "players_a": [1607],
            "players_b": [2459],
            "picks_a": [],
            "picks_b": []
        },
        agreement_ref="AGREEMENT-OFFLINE-001"
    )
    outbox.add_intent(cycle_id, intent_trade, gm, phase_grants, decision_reason="Exploratory trade proposal")

    # Check inspection before sealing
    inspection = outbox.inspect_conflicts_and_dependencies(cycle_id)
    assert inspection["has_blocking_issues"] is False
    assert len(inspection["conflicts"]) == 0
    assert len(inspection["missing_dependencies"]) == 0

    # Step 2: Seal Cycle into RoleActionBatch
    batch_id = f"ROLE-BATCH-{cycle_id}"
    sealed_batch = outbox.seal_cycle(cycle_id, aggregate_batch_id=batch_id, expected_revision=5)
    assert sealed_batch.batch_id == batch_id
    assert len(sealed_batch.intents) == 4

    cycle_info = outbox.get_cycle(cycle_id)
    assert cycle_info["status"] == "SEALED"
    assert cycle_info["sealed_digest"] != ""

    # Step 3: Pure Role to Native Bridge Translation
    bridge_res = bridge.bridge_batch(
        sealed_batch,
        profiles=profiles,
        phase_grants=phase_grants,
        expected_pid=5720
    )
    assert bridge_res.has_executable_batch is True
    assert bridge_res.bulk_batch is not None
    assert len(bridge_res.bulk_batch.intents) == 4  # 2 Giannis + 1 Lillard + 1 Coach
    assert len(bridge_res.unsupported_intents) == 1  # 1 Trade
    assert bridge_res.unsupported_intents[0]["intent_id"] == "I-GM-TRADE-PROPOSAL"

    # Step 4: Execute via BoundedSessionExecutor with Fake REA Transport
    journal_dir = tmp_path / "journal"
    runtime_dir = tmp_path / "runtime"

    def fake_session_runner(chunks, script):
        """Simulates successful single-attach execution of session chunks."""
        results = {}
        for c in chunks:
            chunk_receipts = []
            for item in c.intents:
                chunk_receipts.append({
                    "intent_id": item.intent_id,
                    "team_id": item.team_id,
                    "player_id": item.player_id,
                    "field_id": item.field_id,
                    "expected_before": item.expected_before,
                    "getter_before": item.expected_before,
                    "requested": item.value,
                    "getter_after": item.value,
                    "raw_after": item.value,
                    "outcome": "SUCCESS_APPLIED",
                    "unaltered_fields_check": True
                })
            results[c.chunk_id] = {
                "kind": "chunk-execution-result",
                "chunk_id": c.chunk_id,
                "chunk_digest": c.chunk_digest,
                "plan_digest": c.plan_digest,
                "action_id": c.action_id,
                "batch_id": c.batch_id,
                "save_instance_id": c.save_instance_id,
                "outcome": "CHUNK_SUCCESS",
                "receipts": chunk_receipts
            }
        return {
            "outcome": "SESSION_SUCCESS",
            "evidence_id": "evidence-e2e-fake-001",
            "runtime_directory": str(runtime_dir),
            "chunk_results": results,
            "wall_time_ms": 18.5
        }

    executor = BoundedSessionExecutor(
        journal_dir=journal_dir,
        runtime_dir=runtime_dir,
        fake_runner=fake_session_runner
    )

    exec_summary = executor.execute_batch(bridge_res.bulk_batch, max_chunk_size=50)
    assert exec_summary["metrics"]["conservation_holds"] is True
    assert exec_summary["metrics"]["num_success"] == 4
    assert exec_summary["metrics"]["num_unknown"] == 0

    # Step 5: Independent Verification via validate_batch_execution
    chunks = executor.planner.plan(bridge_res.bulk_batch, max_chunk_size=50)
    journal_receipts = executor.journal.load_receipts()

    # Build raw messages envelope
    raw_messages = [
        {
            "type": "send",
            "payload": {
                "kind": "chunk-execution-result",
                "chunk_id": c.chunk_id,
                "chunk_digest": c.chunk_digest,
                "plan_digest": c.plan_digest,
                "action_id": c.action_id,
                "batch_id": c.batch_id,
                "save_instance_id": c.save_instance_id,
                "outcome": "CHUNK_SUCCESS",
                "receipts": [asdict(r) for r in journal_receipts if r.chunk_id == c.chunk_id]
            }
        }
        for c in chunks
    ]

    claims = [
        json.loads(c_path.read_text(encoding="utf-8"))
        for c_path in journal_dir.glob("claims/claim_*.json")
    ]
    manifest_file = journal_dir / f"batch_{bridge_res.bulk_batch.header.batch_id}.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.exists() else None

    v_res = validate_batch_execution(
        batch=bridge_res.bulk_batch,
        chunks=chunks,
        raw_messages=raw_messages,
        receipts=journal_receipts,
        manifest=manifest,
        claims=claims,
        expected_mode="mutation"
    )
    assert v_res["validation_passed"] is True, f"Validation failed: {v_res['errors']}"
    assert v_res["checks"]["unknown_count"] == 0
    assert v_res["checks"]["plan_digest_verified"] is True

    # Step 6: Map Receipts back to Role ActionIntents
    outbox_receipts = bridge.map_receipts_to_outbox(journal_receipts, bridge_res)
    assert len(outbox_receipts) == 4

    outbox_lookup = {r["intent_id"]: r for r in outbox_receipts}
    assert outbox_lookup["I-GM-GIANNIS-TENDENCIES"]["outcome"] == "SUCCESS_APPLIED"
    assert outbox_lookup["I-GM-LILLARD-TENDENCIES"]["outcome"] == "SUCCESS_APPLIED"
    assert outbox_lookup["I-COACH-RUN-PLAY"]["outcome"] == "SUCCESS_APPLIED"
    assert outbox_lookup["I-GM-TRADE-PROPOSAL"]["outcome"] == "NOT_EXECUTED"
    assert "UNSUPPORTED" in outbox_lookup["I-GM-TRADE-PROPOSAL"]["reason"]

    # Step 7: Record Receipts in Outbox and check Outcome Summary
    record_res = outbox.record_execution_receipts(
        cycle_id,
        outbox_receipts,
        evidence_ref="evidence-e2e-fake-001"
    )
    assert record_res["intents_updated"] == 4
    assert record_res["status"] == "STOPPED_PARTIAL"

    summary = outbox.get_outcome_summary(cycle_id)
    assert summary["cycle_id"] == cycle_id
    assert summary["cycle_status"] == "STOPPED_PARTIAL"
    assert summary["all_succeeded_or_noop"] is False
    assert summary["total_intents"] == 4
    assert summary["status_breakdown"]["SUCCESS"] == 3
    assert summary["status_breakdown"]["NOT_EXECUTED"] == 1
    assert summary["exception_count"] == 1
    assert summary["exceptions"][0]["intent_id"] == "I-GM-TRADE-PROPOSAL"
    assert summary["exceptions"][0]["status"] == "NOT_EXECUTED"

    # Export e2e receipts artifact
    export_payload = {
        "schema_version": "nba2k22.decision_outbox.e2e_receipts.v1",
        "task_id": "NBA2K22-REA-DECISION-OUTBOX-20261102-001",
        "cycle_id": cycle_id,
        "sealed_batch_id": sealed_batch.batch_id,
        "sealed_digest": cycle_info["sealed_digest"],
        "bulk_batch_id": bridge_res.bulk_batch.header.batch_id,
        "bulk_plan_digest": bridge_res.bulk_batch.plan_digest,
        "execution_summary": exec_summary,
        "validation_result": v_res,
        "outbox_summary": summary,
        "outbox_receipts": outbox_receipts
    }

    out_artifact = _RESEARCH_DIR / "../../../.." / "01_os/07_content/_runs/run-20261102-nba2k22-rea-decision-outbox-001/07_测试执行/offline_end_to_end_receipts.json"
    out_artifact.resolve().parent.mkdir(parents=True, exist_ok=True)
    out_artifact.write_text(json.dumps(export_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    assert out_artifact.is_file()


def test_g8_unknown_outcome_locks_resource_and_prevents_replay(tmp_path):
    """Gate G8: UNKNOWN execution outcome sets UNKNOWN_LOCKED state and prevents subsequent execution on resource."""
    db_path = tmp_path / "outbox_unknown.db"
    outbox = DecisionOutbox(db_path)
    service = RoleCapabilityService()
    bridge = DecisionBatchBridge(service)
    ctx = make_context(service.version)
    gm, _ = make_profiles()
    phase_grants = {("gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH")}

    cycle_id = "CYCLE-UNKNOWN-001"
    outbox.open_cycle(cycle_id, ctx)

    intent = ActionIntent.decided(
        "I-UNKNOWN-PLAYER",
        "gm_user_01",
        "PLAYER.EDIT.TENDENCY_BATCH",
        {"team_id": 1, "player_id": 1607, "expected_before": 50, "values": {"SHOT_TENDENCY": 99}}
    )
    outbox.add_intent(cycle_id, intent, gm, phase_grants)
    sealed_batch = outbox.seal_cycle(cycle_id, aggregate_batch_id=f"ROLE-BATCH-{cycle_id}")

    bridge_res = bridge.bridge_batch(
        sealed_batch,
        profiles=(gm,),
        phase_grants=phase_grants
    )

    journal_dir = tmp_path / "journal_unknown"

    def runner_with_unknown(chunks, script):
        results = {}
        for c in chunks:
            results[c.chunk_id] = {
                "kind": "chunk-execution-result",
                "chunk_id": c.chunk_id,
                "chunk_digest": c.chunk_digest,
                "plan_digest": c.plan_digest,
                "action_id": c.action_id,
                "batch_id": c.batch_id,
                "save_instance_id": c.save_instance_id,
                "outcome": "CHUNK_HALTED",
                "halt_reason": "SETTER_EXCEPTION:ProcessHung",
                "receipts": [
                    {
                        "intent_id": it.intent_id,
                        "team_id": it.team_id,
                        "player_id": it.player_id,
                        "field_id": it.field_id,
                        "expected_before": it.expected_before,
                        "getter_before": it.expected_before,
                        "requested": it.value,
                        "outcome": "UNKNOWN_EXECUTION_OUTCOME",
                        "reason": "ProcessHung"
                    }
                    for it in c.intents
                ]
            }
        return {
            "outcome": "SESSION_SUCCESS",
            "evidence_id": "evidence-unknown-001",
            "runtime_directory": str(tmp_path),
            "chunk_results": results,
            "wall_time_ms": 10.0
        }

    executor = BoundedSessionExecutor(
        journal_dir=journal_dir,
        fake_runner=runner_with_unknown
    )

    exec_summary = executor.execute_batch(bridge_res.bulk_batch)
    assert exec_summary["metrics"]["num_unknown"] == 1

    # Outbox updates to UNKNOWN_LOCKED
    outbox_receipts = bridge.map_receipts_to_outbox(executor.journal.load_receipts(), bridge_res)
    rec_res = outbox.record_execution_receipts(cycle_id, outbox_receipts)
    assert rec_res["status"] == "UNKNOWN_LOCKED"

    summary = outbox.get_outcome_summary(cycle_id)
    assert summary["cycle_status"] == "UNKNOWN_LOCKED"
    assert summary["status_breakdown"]["UNKNOWN"] == 1

    # Check journal has locked the resource
    res_key = "team:1:player:1607:field:SHOT_TENDENCY"
    assert executor.journal.is_resource_locked(res_key) != ""

    # Second cycle attempting the same resource should be blocked by prior UNKNOWN claim
    cycle2_id = "CYCLE-UNKNOWN-002"
    outbox.open_cycle(cycle2_id, ctx)
    intent2 = ActionIntent.decided(
        "I-RETRY-LOCKED",
        "gm_user_01",
        "PLAYER.EDIT.TENDENCY_BATCH",
        {"team_id": 1, "player_id": 1607, "expected_before": 50, "values": {"SHOT_TENDENCY": 99}}
    )
    outbox.add_intent(cycle2_id, intent2, gm, phase_grants)
    sealed2 = outbox.seal_cycle(cycle2_id, aggregate_batch_id=f"ROLE-BATCH-{cycle2_id}")
    bridge_res2 = bridge.bridge_batch(
        sealed2,
        profiles=(gm,),
        phase_grants=phase_grants
    )

    exec_summary2 = executor.execute_batch(bridge_res2.bulk_batch)
    assert exec_summary2["metrics"]["num_blocked"] == 1
    assert exec_summary2["metrics"]["num_success"] == 0


def test_g8_crash_recovery_and_immutability(tmp_path):
    """Gate G8: Re-opening outbox after crash preserves sealed state and prevents tampering."""
    db_path = tmp_path / "crash_test.db"
    outbox1 = DecisionOutbox(db_path)
    service = RoleCapabilityService()
    ctx = make_context(service.version)
    gm, _ = make_profiles()
    phase_grants = {("gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH")}

    cycle_id = "CYCLE-CRASH-001"
    outbox1.open_cycle(cycle_id, ctx)
    outbox1.add_intent(cycle_id, ActionIntent.decided(
        "I-CRASH-1", "gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH",
        {"team_id": 1, "player_id": 1607, "expected_before": 50, "values": {"SHOT_TENDENCY": 70}}
    ), gm, phase_grants)
    sealed = outbox1.seal_cycle(cycle_id, aggregate_batch_id=f"ROLE-BATCH-{cycle_id}")

    # Re-instantiate outbox pointing to same DB (simulating restart)
    outbox2 = DecisionOutbox(db_path)
    cycle = outbox2.get_cycle(cycle_id)
    assert cycle["status"] == "SEALED"
    assert cycle["sealed_batch_id"] == sealed.batch_id
    assert cycle["sealed_digest"] != ""

    # Tampering after seal fails
    with pytest.raises(ValueError, match="CANNOT_ADD_INTENT_TO_SEALED_CYCLE"):
        outbox2.add_intent(cycle_id, ActionIntent.decided(
            "I-TAMPER", "gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH",
            {"team_id": 1, "player_id": 1607, "expected_before": 50, "values": {"SHOT_TENDENCY": 85}}
        ), gm, phase_grants)

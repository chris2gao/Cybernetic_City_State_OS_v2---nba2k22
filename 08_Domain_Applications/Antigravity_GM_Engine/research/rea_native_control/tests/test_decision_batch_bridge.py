"""Unit and mapping tests for DecisionBatchBridge (Gate G6)."""
from dataclasses import asdict
import json
from pathlib import Path
import sys
import pytest

_RESEARCH_DIR = Path(__file__).resolve().parent.parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

from decision_batch_bridge import DecisionBatchBridge, BridgeResult
from role_batches import (
    ActionIntent,
    BatchContext,
    RoleActionBatch
)
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService


def make_context(catalog_version):
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
        team_scope=(1, 28),
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


def test_g6_bridge_translates_supported_actions():
    """Gate G6: Pure role to native adapter maps recognized actions to BulkIntentItems."""
    bridge = DecisionBatchBridge()
    ctx = make_context(bridge.service.version)
    gm, coach = make_profiles()
    profiles = (gm, coach)
    phase_grants = {
        ("gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH"),
        ("coach_user_01", "COACH.STRATEGY.RUN_PLAY")
    }

    # 1. GM Intent: batch map tendency for player 1607 (MIL)
    i1 = ActionIntent.decided(
        "I-GM-BATCH",
        "gm_user_01",
        "PLAYER.EDIT.TENDENCY_BATCH",
        {
            "team_id": 1,
            "player_id": 1607,
            "values": {
                "SHOT_TENDENCY": 75,
                "SHOT_CLOSE_TENDENCY": 90
            }
        }
    )

    # 2. Coach Intent: strategy setting (MIL)
    i2 = ActionIntent.decided(
        "I-COACH-STRATEGY",
        "coach_user_01",
        "COACH.STRATEGY.RUN_PLAY",
        {"team_id": 1, "settings": {"RunPlayTendency": 65}}
    )

    role_batch = RoleActionBatch("ROLE-BATCH-001", ctx, (i1, i2))
    result = bridge.bridge_batch(
        role_batch,
        profiles=profiles,
        phase_grants=phase_grants,
        expected_pid=5720
    )

    assert result.planning_issues == ()
    assert result.has_executable_batch is True
    assert result.bulk_batch is not None
    assert len(result.bulk_batch.intents) == 3  # 2 from i1, 1 from i2

    # Check intent items
    bulk_items = {it.field_id: it for it in result.bulk_batch.intents}
    assert "SHOT_TENDENCY" in bulk_items
    assert "SHOT_CLOSE_TENDENCY" in bulk_items
    assert "RunPlayTendency" in bulk_items

    # Check bi-directional mapping
    assert "I-GM-BATCH" in result.role_to_bulk_map
    assert len(result.role_to_bulk_map["I-GM-BATCH"]) == 2
    assert "I-COACH-STRATEGY" in result.role_to_bulk_map

    for b_id in result.role_to_bulk_map["I-GM-BATCH"]:
        assert result.bulk_to_role_map[b_id] == "I-GM-BATCH"


def test_g6_bridge_partitions_unsupported_actions_without_fake_success():
    """Gate G6: Unsupported actions are cleanly isolated as pending, not executed or faked."""
    bridge = DecisionBatchBridge()
    ctx = make_context(bridge.service.version)
    gm, coach = make_profiles()
    profiles = (gm, coach)
    phase_grants = {
        ("gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH"),
        ("gm_user_01", "GM.TRADE.MIXED")
    }

    # Supported intent
    i_supp = ActionIntent.decided(
        "I-SUPP",
        "gm_user_01",
        "PLAYER.EDIT.TENDENCY_BATCH",
        {"team_id": 1, "player_id": 1607, "values": {"SHOT_TENDENCY": 75}}
    )

    # Unsupported intent (trade requirement)
    i_unsupp = ActionIntent.decided(
        "I-TRADE",
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
        agreement_ref="AGREEMENT-001"
    )

    role_batch = RoleActionBatch("ROLE-BATCH-PARTITION", ctx, (i_supp, i_unsupp))
    result = bridge.bridge_batch(
        role_batch,
        profiles=profiles,
        phase_grants=phase_grants
    )

    assert result.has_executable_batch is True
    assert len(result.bulk_batch.intents) == 1
    assert result.bulk_batch.intents[0].player_id == 1607

    # Check unsupported partition
    assert len(result.unsupported_intents) == 1
    un = result.unsupported_intents[0]
    assert un["intent_id"] == "I-TRADE"
    assert "UNSUPPORTED" in un["reason"]


def test_g6_bridge_receipt_mapping_back_to_outbox():
    """Gate G6: Translates BulkBatch execution receipts back to original role ActionIntent IDs."""
    bridge = DecisionBatchBridge()
    ctx = make_context(bridge.service.version)
    gm, coach = make_profiles()
    phase_grants = {
        ("gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH"),
        ("gm_user_01", "GM.TRADE.MIXED")
    }

    i_tend = ActionIntent.decided(
        "I-TEND-MAP",
        "gm_user_01",
        "PLAYER.EDIT.TENDENCY_BATCH",
        {
            "team_id": 1,
            "player_id": 1607,
            "values": {"SHOT_TENDENCY": 75}
        }
    )
    i_trade = ActionIntent.decided(
        "I-TRADE-MAP",
        "gm_user_01",
        "GM.TRADE.MIXED",
        {"team_a": 1, "team_b": 28, "players_a": [], "players_b": [], "picks_a": [], "picks_b": []}
    )

    role_batch = RoleActionBatch("ROLE-BATCH-RECEIPTS", ctx, (i_tend, i_trade))
    res = bridge.bridge_batch(role_batch, profiles=(gm, coach), phase_grants=phase_grants)

    bulk_iid = res.role_to_bulk_map["I-TEND-MAP"][0]

    # Mock bulk receipts
    bulk_receipts = [
        {
            "intent_id": bulk_iid,
            "outcome": "SUCCESS_APPLIED",
            "getter_before": 70,
            "getter_after": 75,
            "reason": "OK"
        }
    ]

    outbox_receipts = bridge.map_receipts_to_outbox(bulk_receipts, res)
    assert len(outbox_receipts) == 2

    lookup = {r["intent_id"]: r for r in outbox_receipts}
    assert lookup["I-TEND-MAP"]["outcome"] == "SUCCESS_APPLIED"
    assert lookup["I-TEND-MAP"]["actual_after"] == 75

    assert lookup["I-TRADE-MAP"]["outcome"] == "NOT_EXECUTED"
    assert "UNSUPPORTED" in lookup["I-TRADE-MAP"]["reason"]

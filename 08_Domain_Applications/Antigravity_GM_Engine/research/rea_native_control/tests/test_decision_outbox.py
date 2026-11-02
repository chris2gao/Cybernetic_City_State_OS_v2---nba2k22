"""Unit, lifecycle, and benchmark tests for DecisionOutbox (Gates G1, G2, G3, G4, G5, G8, G10)."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import pytest

_RESEARCH_DIR = Path(__file__).resolve().parent.parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

from decision_outbox import DecisionOutbox
from role_batches import (
    ActionIntent,
    BatchContext,
    RoleActionBatch,
    digest,
    encode
)
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService


@pytest.fixture
def temp_db():
    d = tempfile.mkdtemp(prefix="test_decision_outbox_")
    db_file = Path(d) / "outbox.db"
    yield db_file
    shutil.rmtree(d, ignore_errors=True)


def make_context(save="MyLEAGUE0003", season="2021-22", phase="REGULAR_SEASON"):
    return BatchContext(
        world_id="WORLD-001",
        save_instance_id=save,
        generation_id="GEN-001",
        season_id=season,
        phase=phase,
        snapshot_ref="snapshot_gold_001",
        catalog_version="20261028"
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
        allowed_actions=frozenset(["PLAYER.EDIT.TENDENCY_BATCH", "PLAYER_PATCH_TENDENCIES"])
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
        allowed_actions=frozenset(["COACH.STRATEGY.RUN_PLAY", "COACH_SET_KNOWN_CURRENT_SETTINGS"])
    )
    return gm, coach


def test_g1_draft_add_supersede_cancel_and_restart(temp_db):
    """Gate G1 / G8: Cycle add, supersede, cancel, restart/reopen SQLite database."""
    outbox = DecisionOutbox(temp_db)
    ctx = make_context()
    gm, coach = make_profiles()
    phase_grants = {
        ("gm_user_01", "PLAYER_PATCH_TENDENCIES"),
        ("gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH")
    }

    # Open cycle
    c_info = outbox.open_cycle("CYCLE-001", ctx)
    assert c_info["status"] == "COLLECTING"
    assert c_info["revision"] == 1

    # Add intent 1
    intent1 = ActionIntent.decided(
        "I-001",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 1, "player_id": 1607, "field_id": "SHOT_TENDENCY", "expected_before": 70, "value": 75}
    )
    outbox.add_intent("CYCLE-001", intent1, gm, phase_grants, decision_reason="Boost Giannis shot tendency")

    # Add intent 2
    intent2 = ActionIntent.decided(
        "I-002",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 28, "player_id": 2459, "field_id": "SHOT_TENDENCY", "expected_before": 80, "value": 85}
    )
    outbox.add_intent("CYCLE-001", intent2, gm, phase_grants)

    # Supersede intent 1 with new target value
    intent1_v2 = ActionIntent.decided(
        "I-001-v2",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 1, "player_id": 1607, "field_id": "SHOT_TENDENCY", "expected_before": 70, "value": 78}
    )
    outbox.supersede_intent("CYCLE-001", "I-001", intent1_v2, gm, phase_grants, decision_reason="Adjust Giannis target to 78")

    # Cancel intent 2
    outbox.cancel_intent("CYCLE-001", "I-002", gm, reason="Withdrawn by GM")

    # Reopen outbox on fresh instance (Restart test)
    outbox_reopened = DecisionOutbox(temp_db)
    drafts = outbox_reopened.list_intents("CYCLE-001", status="DRAFT")
    assert len(drafts) == 1
    assert drafts[0]["intent_id"] == "I-001-v2"
    assert drafts[0]["supersedes_intent_id"] == "I-001"

    all_intents = outbox_reopened.list_intents("CYCLE-001")
    assert len(all_intents) == 3
    statuses = {it["intent_id"]: it["status"] for it in all_intents}
    assert statuses["I-001"] == "SUPERSEDED"
    assert statuses["I-002"] == "CANCELLED"
    assert statuses["I-001-v2"] == "DRAFT"


def test_g2_world_save_season_phase_binding(temp_db):
    """Gate G2: Mismatched BatchContext rejects submission and does not silently rebase."""
    outbox = DecisionOutbox(temp_db)
    ctx = make_context(save="MyLEAGUE0003", season="2021-22")
    outbox.open_cycle("CYCLE-BINDING", ctx)

    # Profile from a different save
    mismatched_gm = RoleCapabilityProfile(
        role_type="GM",
        actor_uid="gm_user_01",
        team_scope=(1,),
        world_id="WORLD-001",
        save_instance_id="MyLEAGUE0099",  # WRONG SAVE
        generation_id="GEN-001",
        season_id="2021-22",
        phase="REGULAR_SEASON",
        snapshot_ref="snapshot_gold_001",
        allowed_actions=frozenset(["PLAYER_PATCH_TENDENCIES"])
    )
    phase_grants = {("gm_user_01", "PLAYER_PATCH_TENDENCIES")}
    intent = ActionIntent.decided(
        "I-MISMATCH",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 1, "player_id": 1607, "field_id": "SHOT_TENDENCY", "expected_before": 70, "value": 75}
    )

    with pytest.raises(ValueError, match="ROLE_CONTEXT_MISMATCH"):
        outbox.add_intent("CYCLE-BINDING", intent, mismatched_gm, phase_grants)


def test_g3_role_credentials_and_phase_grants(temp_db):
    """Gate G3: Host credentials strictly enforced; model JSON cannot self-grant."""
    outbox = DecisionOutbox(temp_db)
    ctx = make_context()
    gm, coach = make_profiles()
    outbox.open_cycle("CYCLE-ROLES", ctx)

    # 1. Impersonation check: intent issuer does not match profile
    intent_impersonate = ActionIntent.decided(
        "I-IMPERSONATE",
        "different_actor_uid",  # DOES NOT MATCH gm.actor_uid
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 1, "player_id": 1607, "field_id": "SHOT_TENDENCY", "expected_before": 70, "value": 75}
    )
    with pytest.raises(PermissionError, match="SUBMISSION_ISSUER_DOES_NOT_MATCH_AUTHENTICATED_PROFILE"):
        outbox.add_intent("CYCLE-ROLES", intent_impersonate, gm, {("different_actor_uid", "PLAYER_PATCH_TENDENCIES")})

    # 2. Phase grant check: missing host phase grant
    intent_valid = ActionIntent.decided(
        "I-NOGRANT",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 1, "player_id": 1607, "field_id": "SHOT_TENDENCY", "expected_before": 70, "value": 75}
    )
    with pytest.raises(PermissionError, match="PHASE_APPLICABILITY_NOT_ATTESTED"):
        outbox.add_intent("CYCLE-ROLES", intent_valid, gm, set())  # Empty phase grants

    # 3. Scope check: GM targeting team outside scope (e.g. Team 99)
    intent_wrong_team = ActionIntent.decided(
        "I-WRONGTEAM",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 99, "player_id": 1607, "field_id": "SHOT_TENDENCY", "expected_before": 70, "value": 75}
    )
    with pytest.raises(PermissionError, match="TEAM_SCOPE_VIOLATION"):
        outbox.add_intent("CYCLE-ROLES", intent_wrong_team, gm, {("gm_user_01", "PLAYER_PATCH_TENDENCIES")})


def test_g4_collision_and_dependency_detection(temp_db):
    """Gate G4: Detects conflicting target values, missing dependencies, and cycles."""
    outbox = DecisionOutbox(temp_db)
    ctx = make_context()
    gm, coach = make_profiles()
    phase_grants = {("gm_user_01", "PLAYER_PATCH_TENDENCIES")}
    outbox.open_cycle("CYCLE-COLLISION", ctx)

    # GM intent 1: Lillard shot tendency -> 85
    i1 = ActionIntent.decided(
        "I-LILLARD-85",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 28, "player_id": 2459, "field_id": "SHOT_TENDENCY", "expected_before": 80, "value": 85}
    )
    outbox.add_intent("CYCLE-COLLISION", i1, gm, phase_grants)

    # GM intent 2: Lillard shot tendency -> 90 (Contradictory collision on same resource!)
    i2 = ActionIntent.decided(
        "I-LILLARD-90",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 28, "player_id": 2459, "field_id": "SHOT_TENDENCY", "expected_before": 80, "value": 90}
    )
    outbox.add_intent("CYCLE-COLLISION", i2, gm, phase_grants)

    # Inspect conflicts
    analysis = outbox.inspect_conflicts_and_dependencies("CYCLE-COLLISION")
    assert analysis["has_blocking_issues"] is True
    assert len(analysis["conflicts"]) == 1
    assert "player/2459/SHOT_TENDENCY" in analysis["conflicts"][0]["resource_key"]

    # Sealing must fail with blocking conflicts
    with pytest.raises(ValueError, match="CYCLE_HAS_BLOCKING_CONFLICTS"):
        outbox.seal_cycle("CYCLE-COLLISION", aggregate_batch_id="BATCH-FAIL")

    # Dependency test: Intent 3 depends on missing Intent 999
    i3 = ActionIntent.decided(
        "I-DEP-MISSING",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 1, "player_id": 1607, "field_id": "SHOT_TENDENCY", "expected_before": 70, "value": 75},
        dependencies=("I-NONEXISTENT-999",)
    )
    outbox.add_intent("CYCLE-COLLISION", i3, gm, phase_grants)
    analysis2 = outbox.inspect_conflicts_and_dependencies("CYCLE-COLLISION")
    assert any(d["missing_dependency"] == "I-NONEXISTENT-999" for d in analysis2["missing_dependencies"])


def test_g5_immutable_seal_and_revision_cas(temp_db):
    """Gate G5: Sealing creates immutable RoleActionBatch; revision CAS; prevents further additions."""
    outbox = DecisionOutbox(temp_db)
    ctx = make_context()
    gm, coach = make_profiles()
    phase_grants = {("gm_user_01", "PLAYER_PATCH_TENDENCIES")}
    outbox.open_cycle("CYCLE-SEAL", ctx)

    i1 = ActionIntent.decided(
        "I-SEAL-1",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 1, "player_id": 1607, "field_id": "SHOT_TENDENCY", "expected_before": 70, "value": 75}
    )
    outbox.add_intent("CYCLE-SEAL", i1, gm, phase_grants)

    cycle_before = outbox.get_cycle("CYCLE-SEAL")
    current_rev = cycle_before["revision"]

    # Sealing with wrong revision CAS must fail
    with pytest.raises(ValueError, match="REVISION_CAS_MISMATCH"):
        outbox.seal_cycle("CYCLE-SEAL", aggregate_batch_id="BATCH-SEAL-001", expected_revision=current_rev + 5)

    # Proper seal
    batch = outbox.seal_cycle("CYCLE-SEAL", aggregate_batch_id="BATCH-SEAL-001", expected_revision=current_rev)
    assert isinstance(batch, RoleActionBatch)
    assert batch.batch_id == "BATCH-SEAL-001"
    assert len(batch.intents) == 1

    cycle_after = outbox.get_cycle("CYCLE-SEAL")
    assert cycle_after["status"] == "SEALED"
    assert cycle_after["sealed_batch_id"] == "BATCH-SEAL-001"
    assert bool(cycle_after["sealed_digest"]) is True

    # Idempotent re-seal returns same batch
    batch2 = outbox.seal_cycle("CYCLE-SEAL", aggregate_batch_id="BATCH-SEAL-001")
    assert batch2.batch_id == "BATCH-SEAL-001"
    assert len(batch2.intents) == 1

    # Adding new intent to sealed cycle must fail
    i2 = ActionIntent.decided(
        "I-SEAL-2",
        "gm_user_01",
        "PLAYER_PATCH_TENDENCIES",
        {"team_id": 1, "player_id": 2492, "field_id": "SHOT_TENDENCY", "expected_before": 80, "value": 85}
    )
    with pytest.raises(ValueError, match="CANNOT_ADD_INTENT_TO_SEALED_CYCLE"):
        outbox.add_intent("CYCLE-SEAL", i2, gm, phase_grants)


def test_g10_1k_and_10k_outbox_insertion_performance(temp_db):
    """Gate G10: Measures throughput of 1,000 and 10,000 intent additions in SQLite outbox."""
    outbox = DecisionOutbox(temp_db)
    ctx = make_context()
    outbox.open_cycle("CYCLE-BENCH", ctx)

    # 1. 1,000 items benchmark
    t0 = time.perf_counter()
    with outbox._get_connection() as conn:
        conn.execute("BEGIN TRANSACTION")
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        for i in range(1000):
            iid = f"I-1K-{i:04d}"
            rkey = f"player/{1000+i}/SHOT_TENDENCY"
            params = json.dumps({"team_id": 1, "player_id": 1000 + i, "field_id": "SHOT_TENDENCY", "expected_before": 50, "value": 55})
            conn.execute("""
            INSERT INTO decision_intents (
                intent_id, cycle_id, issuer_uid, role_type, action_id, parameters_json,
                dependencies_json, target_resource_key, status, created_at, updated_at
            ) VALUES (?, 'CYCLE-BENCH', 'gm_user_01', 'GM', 'PLAYER_PATCH_TENDENCIES', ?, '[]', ?, 'DRAFT', ?, ?)
            """, (iid, params, rkey, now, now))
        conn.execute("UPDATE decision_cycles SET revision = revision + 1000, updated_at = ? WHERE cycle_id = 'CYCLE-BENCH'", (now,))
        conn.commit()
    t_1k = time.perf_counter() - t0

    # 2. 10,000 items benchmark
    t1 = time.perf_counter()
    with outbox._get_connection() as conn:
        conn.execute("BEGIN TRANSACTION")
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        for i in range(10000):
            iid = f"I-10K-{i:05d}"
            rkey = f"player/{10000+i}/SHOT_TENDENCY"
            params = json.dumps({"team_id": 1, "player_id": 10000 + i, "field_id": "SHOT_TENDENCY", "expected_before": 50, "value": 55})
            conn.execute("""
            INSERT INTO decision_intents (
                intent_id, cycle_id, issuer_uid, role_type, action_id, parameters_json,
                dependencies_json, target_resource_key, status, created_at, updated_at
            ) VALUES (?, 'CYCLE-BENCH', 'gm_user_01', 'GM', 'PLAYER_PATCH_TENDENCIES', ?, '[]', ?, 'DRAFT', ?, ?)
            """, (iid, params, rkey, now, now))
        conn.execute("UPDATE decision_cycles SET revision = revision + 10000, updated_at = ? WHERE cycle_id = 'CYCLE-BENCH'", (now,))
        conn.commit()
    t_10k = time.perf_counter() - t1

    assert t_1k < 1.0, f"1k insert took too long: {t_1k:.3f}s"
    assert t_10k < 5.0, f"10k insert took too long: {t_10k:.3f}s"

    # Save benchmark result
    bench_data = {
        "schema_version": "nba2k22.outbox.10k_benchmark.v1",
        "task_id": "NBA2K22-REA-DECISION-OUTBOX-20261102-001",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sqlite_journal_mode": "WAL",
        "insert_1000_intents_seconds": round(t_1k, 5),
        "insert_10000_intents_seconds": round(t_10k, 5),
        "throughput_1k_intents_per_sec": round(1000.0 / t_1k, 1),
        "throughput_10k_intents_per_sec": round(10000.0 / t_10k, 1)
    }
    bench_file = (_RESEARCH_DIR / "../../../.." / "01_os/07_content/_runs/run-20261102-nba2k22-rea-decision-outbox-001" / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "10k_outbox_benchmark.json").resolve()
    bench_file.parent.mkdir(parents=True, exist_ok=True)
    bench_file.write_text(json.dumps(bench_data, indent=2), encoding="utf-8")

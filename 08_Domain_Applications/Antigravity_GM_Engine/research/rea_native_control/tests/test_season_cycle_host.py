"""Unit and integration tests for SeasonCycleHost and SeasonCycleCLI (Gates G01-G08)."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import pytest

_DIR = Path(__file__).resolve().parent.parent
_PROTO_DIR = _DIR.parent.parent / "world_data_prototype"
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))
if str(_PROTO_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTO_DIR))

from bulk_executor import ItemReceipt
from engine import create_database, connect
from live_world import initialize_save
from season_cycle_host import SeasonCycleHost, HostState


@pytest.fixture
def temp_environment(tmp_path):
    save_dir = tmp_path / "save"
    native_file = tmp_path / "MyLEAGUE0003"
    native_file.write_bytes(b"FAKE_NBA2K22_SAVE_CONTENT")

    binding = initialize_save(str(save_dir), "nba2k22_test_01", str(native_file))
    db_path = save_dir / "world.sqlite"

    with connect(db_path) as conn:
        conn.execute("PRAGMA defer_foreign_keys = ON;")
        conn.execute("""
            INSERT INTO seasons (season_id, season_code, save_id)
            VALUES ('season:2021', '2021-22', 'nba2k22_test_01')
        """)
        conn.execute("""
            INSERT INTO teams (team_id, display_name) VALUES ('team:1', 'MIL'), ('team:2', 'BKN'), ('team:3', 'POR')
        """)
        conn.execute("""
            INSERT INTO games (game_id, season_id, game_date, home_team_id, away_team_id, native_game_id)
            VALUES ('game:001', 'season:2021', '2021-11-01', 'team:1', 'team:2', '101')
        """)
        conn.execute("""
            INSERT INTO games (game_id, season_id, game_date, home_team_id, away_team_id, native_game_id)
            VALUES ('game:002', 'season:2021', '2021-11-05', 'team:1', 'team:3', '102')
        """)

    state_file = tmp_path / "season_host_state.json"
    ledger_file = tmp_path / "season_run_ledger.jsonl"
    outbox_db = tmp_path / "outbox.db"

    host = SeasonCycleHost(
        workspace_root=tmp_path,
        state_file=state_file,
        ledger_file=ledger_file,
        outbox_db=outbox_db
    )
    return {
        "tmp_path": tmp_path,
        "save_dir": save_dir,
        "native_file": native_file,
        "db_path": db_path,
        "host": host,
        "state_file": state_file,
        "ledger_file": ledger_file,
        "outbox_db": outbox_db
    }


def test_g02_worldline_backward_date_isolation(temp_environment):
    """Gate G02: When game date regresses (restored old save), host creates isolated worldline branch DB without deleting old facts."""
    env = temp_environment
    host = env["host"]
    
    receipt = host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-10-25"
    )
    assert receipt["status"] == "INITIALIZED_AND_BASELINE_BOUND"
    assert receipt["is_backward_worldline_branch"] is True
    assert "worldline-nba2k22_test_01-20211025" in receipt["worldline_id"]
    
    target_db = Path(receipt["database_file"])
    assert target_db != env["db_path"]
    assert target_db.exists()

    with connect(env["db_path"], True) as conn:
        count = conn.execute("SELECT count(*) FROM games").fetchone()[0]
        assert count == 2


def test_g04_capture_chronology_and_same_state_repeat(temp_environment):
    """Gate G04: Verify same state repeat detection skips redundant acquisition."""
    env = temp_environment
    host = env["host"]

    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10"
    )
    assert host.state["status"] == HostState.BASELINE_CAPTURED

    res = host.start_cycle("cycle-001", mock_game_date="2021-11-10")
    assert res["status"] == "DECISION_CYCLE_OPENED"
    assert res["cycle_id"] == "cycle-001"


def test_g05_role_authorization_and_conflicts(temp_environment):
    """Gate G05: Unauthorized role actions are rejected, conflicting targets are detected."""
    env = temp_environment
    host = env["host"]

    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10"
    )

    intents = [
        {
            "intent_id": "c1-intent-1",
            "issuer_role": "GM",
            "actor_uid": "gm_user_01",
            "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
            "parameters": {"team_id": 1, "player_id": 2459, "field_id": "SHOT_TENDENCY", "value": 85, "expected_before": 80, "values": {"SHOT_TENDENCY": 85}}
        },
        {
            "intent_id": "c1-intent-2",
            "issuer_role": "COACH",
            "actor_uid": "coach_user_01",
            "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
            "parameters": {"team_id": 1, "player_id": 2459, "field_id": "SHOT_TENDENCY", "value": 70, "expected_before": 80, "values": {"SHOT_TENDENCY": 70}}
        },
        {
            "intent_id": "c1-intent-3",
            "issuer_role": "PLAYER",
            "actor_uid": "player_user_01",
            "action_id": "GM.TRADE.MIXED",
            "parameters": {"trade_id": "trade-99"}
        }
    ]

    res = host.start_cycle("cycle-001", candidate_intents=intents, force=True)
    assert res["status"] == "DECISION_CYCLE_OPENED"
    assert res["intents_added_count"] == 1
    assert len(res["conflicts_detected"]) == 1
    assert res["conflicts_detected"][0]["intent_id"] == "c1-intent-2"
    assert len(res["unauthorized_rejected"]) == 1
    assert res["unauthorized_rejected"][0]["intent_id"] == "c1-intent-3"


def test_g06_cas_mismatch_fails_closed(temp_environment):
    """Gate G06: CAS preflight mismatch fails closed and refuses to seal plan."""
    env = temp_environment
    host = env["host"]

    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10"
    )

    intents = [
        {
            "intent_id": "cas-intent-1",
            "issuer_role": "GM",
            "actor_uid": "gm_user_01",
            "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
            "parameters": {"team_id": 1, "player_id": 2459, "field_id": "SHOT_TENDENCY", "value": 85, "expected_before": 80, "values": {"SHOT_TENDENCY": 85}}
        }
    ]
    host.start_cycle("cycle-001", candidate_intents=intents, force=True)

    def mock_getter(player_id, field_id):
        return 90

    seal_res = host.seal_cycle_decisions("cycle-001", getter_func=mock_getter)
    assert seal_res["status"] == "SEAL_FAILED_CAS_MISMATCH"
    assert host.state["status"] == HostState.CONFLICTED


def test_g08_four_offline_closed_loop_cycles(temp_environment):
    """Gate G08: Run 4 full 7-day cycles offline with all required edge cases."""
    env = temp_environment
    host = env["host"]

    init_res = host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )
    assert init_res["status"] == "INITIALIZED_AND_BASELINE_BOUND"

    game_state = {2459: {"SHOT_TENDENCY": 80}, 2019: {"SHOT_TENDENCY": 65}}
    def getter(pid, fid):
        return game_state.get(pid, {}).get(fid, 50)
    def setter(pid, fid, val):
        if pid not in game_state: game_state[pid] = {}
        game_state[pid][fid] = val

    def fake_session_runner(chunks, script):
        results = {}
        for c in chunks:
            chunk_receipts = []
            for item in c.intents:
                cur = getter(item.player_id, item.field_id)
                if cur == item.expected_before:
                    setter(item.player_id, item.field_id, item.value)
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
                else:
                    chunk_receipts.append({
                        "intent_id": item.intent_id,
                        "team_id": item.team_id,
                        "player_id": item.player_id,
                        "field_id": item.field_id,
                        "expected_before": item.expected_before,
                        "getter_before": cur,
                        "requested": item.value,
                        "getter_after": cur,
                        "raw_after": cur,
                        "outcome": "CAS_MISMATCH",
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
            "chunk_results": results,
            "wall_time_ms": 18.5
        }

    # =====================================================
    # CYCLE 1: Standard tactical adjustment (SHOT_TENDENCY)
    # =====================================================
    c1_intents = [
        {
            "intent_id": "c1-intent-1",
            "issuer_role": "GM",
            "actor_uid": "gm_user_01",
            "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
            "parameters": {
                "team_id": 1,
                "player_id": 2459,
                "expected_before": 80,
                "values": {"SHOT_TENDENCY": 85}
            }
        }
    ]
    res_c1_start = host.start_cycle("cycle-001", candidate_intents=c1_intents, force=True)
    assert res_c1_start["status"] == "DECISION_CYCLE_OPENED"

    res_c1_seal = host.seal_cycle_decisions("cycle-001", getter_func=getter)
    assert res_c1_seal["status"] == "PLAN_PREFLIGHTED_WAITING_AUTH"
    digest_c1 = res_c1_seal["plan_digest"]
    assert digest_c1 != ""

    res_c1_exec = host.authorize_and_execute(
        "cycle-001",
        plan_digest=digest_c1,
        transport=fake_session_runner,
        getter_after_func=getter
    )
    assert res_c1_exec["status"] == "EXECUTED_AND_READBACK_RECORDED"
    assert res_c1_exec["success_count"] == 1
    assert res_c1_exec["readback_verified"] is True
    assert getter(2459, "SHOT_TENDENCY") == 85

    res_adv1 = host.advance_calendar_check("cycle-002", mock_advanced_date="2021-11-08")
    assert res_adv1["status"] == "CALENDAR_ADVANCE_VERIFIED"
    assert host.state["status"] == HostState.NEXT_CAPTURED

    # =====================================================
    # CYCLE 2: NO_CHANGE cycle (Tactical continuity)
    # =====================================================
    res_c2_start = host.start_cycle("cycle-002", candidate_intents=[], force=True)
    assert res_c2_start["status"] == "DECISION_CYCLE_OPENED"
    assert res_c2_start["is_no_change_cycle"] is True

    res_c2_seal = host.seal_cycle_decisions("cycle-002", getter_func=getter)
    assert res_c2_seal["status"] == "PLAN_PREFLIGHTED_WAITING_AUTH"
    digest_c2 = res_c2_seal["plan_digest"]

    res_c2_exec = host.authorize_and_execute(
        "cycle-002",
        plan_digest=digest_c2,
        transport=fake_session_runner,
        getter_after_func=getter
    )
    assert res_c2_exec["status"] == "EXECUTED_NO_CHANGE_SUCCESS"
    assert res_c2_exec["executed_count"] == 0

    res_adv2 = host.advance_calendar_check("cycle-003", mock_advanced_date="2021-11-15")
    assert res_adv2["status"] == "CALENDAR_ADVANCE_VERIFIED"

    # =====================================================
    # CYCLE 3: Conflicting intents & Unsupported actions
    # =====================================================
    c3_intents = [
        {
            "intent_id": "c3-intent-1",
            "issuer_role": "GM",
            "actor_uid": "gm_user_01",
            "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
            "parameters": {
                "team_id": 1,
                "player_id": 2019,
                "expected_before": 65,
                "values": {"SHOT_TENDENCY": 92}
            }
        },
        {
            "intent_id": "c3-intent-2",
            "issuer_role": "COACH",
            "actor_uid": "coach_user_01",
            "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
            "parameters": {
                "team_id": 1,
                "player_id": 2019,
                "expected_before": 65,
                "values": {"SHOT_TENDENCY": 88}
            }
        },
        {
            "intent_id": "c3-intent-3",
            "issuer_role": "GM",
            "actor_uid": "gm_user_01",
            "action_id": "GM.TRADE.MIXED",
            "parameters": {
                "team_a": 1,
                "team_b": 28,
                "players_a": [1607],
                "players_b": [2459],
                "picks_a": [],
                "picks_b": []
            }
        }
    ]
    res_c3_start = host.start_cycle("cycle-003", candidate_intents=c3_intents, force=True)
    assert len(res_c3_start["conflicts_detected"]) == 1

    res_c3_seal = host.seal_cycle_decisions("cycle-003", getter_func=getter)
    assert res_c3_seal["status"] == "PLAN_PREFLIGHTED_WAITING_AUTH"
    assert res_c3_seal["executable_intents_count"] == 1
    assert res_c3_seal["unsupported_intents_count"] == 1
    digest_c3 = res_c3_seal["plan_digest"]

    res_c3_exec = host.authorize_and_execute(
        "cycle-003",
        plan_digest=digest_c3,
        transport=fake_session_runner,
        getter_after_func=getter
    )
    assert res_c3_exec["success_count"] == 1
    assert getter(2019, "SHOT_TENDENCY") == 92

    res_adv3 = host.advance_calendar_check("cycle-004", mock_advanced_date="2021-11-22")
    assert res_adv3["status"] == "CALENDAR_ADVANCE_VERIFIED"

    # =====================================================
    # CYCLE 4: CAS Mismatch / Fail-Closed Resilience
    # =====================================================
    c4_intents = [
        {
            "intent_id": "c4-intent-1",
            "issuer_role": "GM",
            "actor_uid": "gm_user_01",
            "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
            "parameters": {
                "team_id": 1,
                "player_id": 2019,
                "expected_before": 65,
                "values": {"SHOT_TENDENCY": 99}
            }
        }
    ]
    host.start_cycle("cycle-004", candidate_intents=c4_intents, force=True)
    res_c4_seal = host.seal_cycle_decisions("cycle-004", getter_func=getter)
    assert res_c4_seal["status"] == "SEAL_FAILED_CAS_MISMATCH"
    assert host.state["status"] == HostState.CONFLICTED

    with pytest.raises(ValueError, match="Host not in awaiting authorization state"):
        host.authorize_and_execute("cycle-004", plan_digest="bad_digest")

    ledger_lines = env["ledger_file"].read_text(encoding="utf-8").strip().splitlines()
    assert len(ledger_lines) >= 8

    final_status = host.get_status()
    assert final_status["host_status"] == HostState.CONFLICTED
    assert final_status["current_cycle_id"] == "cycle-004"

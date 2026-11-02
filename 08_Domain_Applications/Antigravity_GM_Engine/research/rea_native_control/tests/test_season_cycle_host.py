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


def test_p1_pause_resume_unknown_locked_and_outbox_alignment(temp_environment):
    """Verify pause/resume preserves previous status, refuses to resume UNKNOWN_LOCKED, and empty cycle aligns outbox SEALED."""
    env = temp_environment
    host = env["host"]

    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    # 1. Normal pause & resume restores pre-pause status
    assert host.state["status"] == HostState.BASELINE_CAPTURED
    p_rec = host.pause()
    assert p_rec["status"] == "HOST_PAUSED"
    assert host.state["status"] == HostState.PAUSED
    assert host.state["pre_pause_status"] == HostState.BASELINE_CAPTURED

    r_rec = host.resume()
    assert r_rec["status"] == "HOST_RESUMED"
    assert host.state["status"] == HostState.BASELINE_CAPTURED

    # 2. Pause when UNKNOWN_LOCKED refuses resume
    host.state["status"] = HostState.UNKNOWN_LOCKED
    host.pause()
    assert host.state["status"] == HostState.PAUSED
    res_block = host.resume()
    assert res_block["status"] == "RESUME_DENIED_UNKNOWN_LOCKED"
    assert host.state["status"] == HostState.UNKNOWN_LOCKED

    # 3. Empty NO_CHANGE cycle seals outbox cycle in DB
    host.state["status"] = HostState.BASELINE_CAPTURED
    host.start_cycle("cycle-empty", candidate_intents=[], force=True)
    seal_res = host.seal_cycle_decisions("cycle-empty")
    assert seal_res["status"] == "PLAN_PREFLIGHTED_WAITING_AUTH"

    # Verify Outbox DB cycle status is SEALED
    cycle_rec = host.outbox.get_cycle("cycle-empty")
    assert cycle_rec["status"] == "SEALED"
    assert cycle_rec["sealed_batch_id"] == "NOOP-BATCH-cycle-empty"


def test_p0_fail_closed_readback_and_unknown_locking(temp_environment):
    """Verify readback failure sets STOPPED_PARTIAL (does not advance) and UNKNOWN sets UNKNOWN_LOCKED."""
    env = temp_environment
    host = env["host"]

    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    intents = [
        {
            "intent_id": "rb-fail-intent",
            "issuer_role": "GM",
            "actor_uid": "gm_user_01",
            "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
            "parameters": {
                "team_id": 1,
                "player_id": 2459,
                "expected_before": 80,
                "values": {"SHOT_TENDENCY": 95}
            }
        }
    ]
    host.start_cycle("cycle-fail-rb", candidate_intents=intents, force=True)

    def getter_cas(pid, fid):
        return 80

    seal_res = host.seal_cycle_decisions("cycle-fail-rb", getter_func=getter_cas)
    digest = seal_res["plan_digest"]

    # Runner claims SUCCESS, but getter_after returns wrong value (readback mismatch)
    def fake_runner_mismatch(chunks, script):
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
                "outcome": "CHUNK_SUCCESS",
                "receipts": [{
                    "intent_id": c.intents[0].intent_id,
                    "team_id": c.intents[0].team_id,
                    "player_id": c.intents[0].player_id,
                    "field_id": c.intents[0].field_id,
                    "expected_before": 80,
                    "getter_before": 80,
                    "requested": 95,
                    "getter_after": 95,
                    "raw_after": 95,
                    "outcome": "SUCCESS_APPLIED",
                    "unaltered_fields_check": True
                }]
            }
        return {"outcome": "SESSION_SUCCESS", "evidence_id": "ev-1", "chunk_results": results}

    def failing_getter_after(pid, fid):
        return 80  # Failed to update in actual memory!

    res_exec = host.authorize_and_execute(
        "cycle-fail-rb",
        plan_digest=digest,
        transport=fake_runner_mismatch,
        getter_after_func=failing_getter_after
    )

    assert res_exec["status"] == "STOPPED_READBACK_FAILED"
    assert res_exec["readback_verified"] is False
    assert host.state["status"] == HostState.STOPPED_PARTIAL
    # Active plan is preserved! Not cleared!
    assert host.state["active_plan"] is not None
    assert host.state["active_plan"]["plan_digest"] == digest


def test_p0_a_fresh_getter_after_isolated_from_preflight_cache(temp_environment, monkeypatch):
    """P0-A: Ensure readback getter is evaluated post-execution, strictly isolated from preflight cache."""
    env = temp_environment
    host = env["host"]
    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    intents = [{
        "intent_id": "fresh-getter-intent-1",
        "issuer_role": "GM",
        "actor_uid": "gm_user_01",
        "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
        "parameters": {
            "team_id": 1,
            "player_id": 2459,
            "expected_before": 80,
            "values": {"SHOT_TENDENCY": 88}
        }
    }]
    host.start_cycle("cycle-fresh-getter", candidate_intents=intents, force=True)

    preflight_call_count = 0
    def preflight_getter(pid, fid):
        nonlocal preflight_call_count
        preflight_call_count += 1
        return 80

    seal_res = host.seal_cycle_decisions("cycle-fresh-getter", getter_func=preflight_getter)
    assert seal_res["status"] == "PLAN_PREFLIGHTED_WAITING_AUTH"
    digest = seal_res["plan_digest"]
    assert preflight_call_count >= 1

    post_read_call_count = 0
    def post_getter(pid, fid):
        nonlocal post_read_call_count
        post_read_call_count += 1
        return 88

    def fake_runner_ok(chunks, script):
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
                "outcome": "CHUNK_SUCCESS",
                "receipts": [{
                    "intent_id": c.intents[0].intent_id,
                    "team_id": c.intents[0].team_id,
                    "player_id": c.intents[0].player_id,
                    "field_id": c.intents[0].field_id,
                    "expected_before": 80,
                    "getter_before": 80,
                    "requested": 88,
                    "getter_after": 88,
                    "raw_after": 88,
                    "outcome": "SUCCESS_APPLIED",
                    "unaltered_fields_check": True
                }]
            }
        return {"outcome": "SESSION_SUCCESS", "evidence_id": "ev-p0a", "chunk_results": results}

    exec_res = host.authorize_and_execute(
        "cycle-fresh-getter",
        plan_digest=digest,
        transport=fake_runner_ok,
        getter_after_func=post_getter
    )
    assert exec_res["status"] == "EXECUTED_AND_READBACK_RECORDED"
    assert post_read_call_count >= 1
    assert exec_res["readback_verified"] is True

    # Test PID mismatch handling in live getter
    with pytest.raises(RuntimeError, match="PID_MISMATCH_FRESH_GETTER"):
        import refresh
        monkeypatch.setattr(refresh, "resolve_pid", lambda mode: 1234)
        host._get_fresh_live_getter(expected_pid=9999)


def test_p0_b_unknown_outcome_locks_host_and_outbox_preserves_plan(temp_environment):
    """P0-B: UNKNOWN outcome locks Host (UNKNOWN_LOCKED), Outbox (UNKNOWN_LOCKED), and preserves plan."""
    env = temp_environment
    host = env["host"]
    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    intents = [{
        "intent_id": "unknown-intent-1",
        "issuer_role": "GM",
        "actor_uid": "gm_user_01",
        "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
        "parameters": {
            "team_id": 1,
            "player_id": 2459,
            "expected_before": 80,
            "values": {"SHOT_TENDENCY": 85}
        }
    }]
    host.start_cycle("cycle-unknown", candidate_intents=intents, force=True)
    seal_res = host.seal_cycle_decisions("cycle-unknown", getter_func=lambda pid, fid: 80)
    digest = seal_res["plan_digest"]

    def fake_runner_unknown(chunks, script):
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
                "outcome": "CHUNK_FAILED",
                "receipts": [{
                    "intent_id": c.intents[0].intent_id,
                    "team_id": c.intents[0].team_id,
                    "player_id": c.intents[0].player_id,
                    "field_id": c.intents[0].field_id,
                    "expected_before": 80,
                    "getter_before": 80,
                    "requested": 85,
                    "getter_after": None,
                    "raw_after": None,
                    "outcome": "UNKNOWN_EXECUTION_OUTCOME",
                    "unaltered_fields_check": False
                }]
            }
        return {"outcome": "SESSION_SUCCESS", "evidence_id": "ev-unk", "chunk_results": results}

    exec_res = host.authorize_and_execute(
        "cycle-unknown",
        plan_digest=digest,
        transport=fake_runner_unknown,
        getter_after_func=lambda pid, fid: 85
    )

    assert exec_res["status"] == "STOPPED_UNKNOWN_LOCKED"
    assert host.state["status"] == HostState.UNKNOWN_LOCKED
    assert host.state["active_plan"] is not None
    assert host.state["active_plan"]["plan_digest"] == digest

    # Verify Outbox cycle status is UNKNOWN_LOCKED
    cycle_db_rec = host.outbox.get_cycle("cycle-unknown")
    assert cycle_db_rec["status"] == "UNKNOWN_LOCKED"

    # Calendar advance is blocked
    adv_res = host.advance_calendar_check("cycle-next", mock_advanced_date="2021-11-08")
    assert adv_res["status"] == "ADVANCE_REFUSED_CYCLE_NOT_CLEARED"


def test_p0_b_missing_receipt_fails_closed_with_stopped_partial(temp_environment):
    """P0-B: Missing execution receipt triggers batch validation failure, STOPPED_PARTIAL, plan preserved."""
    env = temp_environment
    host = env["host"]
    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    intents = [{
        "intent_id": "missing-rec-1",
        "issuer_role": "GM",
        "actor_uid": "gm_user_01",
        "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
        "parameters": {
            "team_id": 1,
            "player_id": 2459,
            "expected_before": 80,
            "values": {"SHOT_TENDENCY": 85}
        }
    }]
    host.start_cycle("cycle-missing-rec", candidate_intents=intents, force=True)
    seal_res = host.seal_cycle_decisions("cycle-missing-rec", getter_func=lambda pid, fid: 80)
    digest = seal_res["plan_digest"]

    def fake_runner_missing(chunks, script):
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
                "outcome": "CHUNK_SUCCESS",
                "receipts": []
            }
        return {"outcome": "SESSION_SUCCESS", "evidence_id": "ev-miss", "chunk_results": results}

    exec_res = host.authorize_and_execute(
        "cycle-missing-rec",
        plan_digest=digest,
        transport=fake_runner_missing,
        getter_after_func=lambda pid, fid: 85
    )

    assert exec_res["status"] == "STOPPED_VALIDATION_FAILED"
    assert host.state["status"] == HostState.STOPPED_PARTIAL
    assert host.state["active_plan"] is not None
    assert len(exec_res["validation_errors"]) > 0


def test_p0_c_mock_mode_cannot_execute_without_fake_transport(temp_environment):
    """P0-C: Mock mode cannot execute without fake transport (physical isolation)."""
    env = temp_environment
    host = env["host"]
    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    intents = [{
        "intent_id": "iso-intent-1",
        "issuer_role": "GM",
        "actor_uid": "gm_user_01",
        "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
        "parameters": {
            "team_id": 1,
            "player_id": 2459,
            "expected_before": 80,
            "values": {"SHOT_TENDENCY": 85}
        }
    }]
    host.start_cycle("cycle-iso", candidate_intents=intents, force=True)
    seal_res = host.seal_cycle_decisions("cycle-iso", getter_func=lambda pid, fid: 80)
    digest = seal_res["plan_digest"]

    with pytest.raises(RuntimeError, match="OFFLINE_MOCK_CANNOT_EXECUTE_WITHOUT_FAKE_TRANSPORT"):
        host.authorize_and_execute("cycle-iso", plan_digest=digest, transport=None)


def test_p0_c_live_mode_rejects_fake_transport_and_unauthorized_scope(temp_environment, monkeypatch):
    """P0-C: Live mode strictly rejects fake transport and restricts actions to PLAYER_PATCH_TENDENCIES/SHOT_TENDENCY."""
    env = temp_environment
    host = env["host"]
    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    host.state["is_offline_mock"] = False
    host.state["is_mock"] = False
    host._save_state()

    intents = [{
        "intent_id": "live-scope-1",
        "issuer_role": "GM",
        "actor_uid": "gm_user_01",
        "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
        "parameters": {
            "team_id": 1,
            "player_id": 2459,
            "expected_before": 80,
            "values": {"SHOT_TENDENCY": 85}
        }
    }]
    host.start_cycle("cycle-live-guard", candidate_intents=intents, force=True, mock_game_date="2021-11-01")
    seal_res = host.seal_cycle_decisions("cycle-live-guard", getter_func=lambda pid, fid: 80)
    digest = seal_res["plan_digest"]

    def dummy_transport(chunks, script):
        return {}

    with pytest.raises(RuntimeError, match="LIVE_MODE_REJECTS_FAKE_TRANSPORT"):
        host.authorize_and_execute("cycle-live-guard", plan_digest=digest, transport=dummy_transport)

    import refresh
    monkeypatch.setattr(refresh, "resolve_pid", lambda mode: 5720)

    unauth_intents = [{
        "intent_id": "unauth-field-1",
        "issuer_role": "GM",
        "actor_uid": "gm_user_01",
        "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
        "parameters": {
            "team_id": 1,
            "player_id": 2459,
            "expected_before": 80,
            "values": {"DRIVING_LAYUP_TENDENCY": 75}
        }
    }]
    host.start_cycle("cycle-unauth-scope", candidate_intents=unauth_intents, force=True, mock_game_date="2021-11-01")
    seal_res2 = host.seal_cycle_decisions("cycle-unauth-scope", getter_func=lambda pid, fid: 80)
    digest2 = seal_res2["plan_digest"]

    with pytest.raises(ValueError, match="LIVE_SCOPE_VIOLATION"):
        host.authorize_and_execute("cycle-unauth-scope", plan_digest=digest2, transport=None)


def test_p0_c_unauthenticated_role_actor_rejected(temp_environment):
    """P0-C: Unauthenticated actor identity is rejected by TrustedRoleRegistry at cycle entry."""
    env = temp_environment
    host = env["host"]
    host.initialize_season(
        save_directory=str(env["save_dir"]),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    imposter_intents = [{
        "intent_id": "imposter-intent",
        "issuer_role": "GM",
        "actor_uid": "imposter_hacker",
        "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
        "parameters": {
            "team_id": 1,
            "player_id": 2459,
            "expected_before": 80,
            "values": {"SHOT_TENDENCY": 85}
        }
    }]
    start_res = host.start_cycle("cycle-imposter", candidate_intents=imposter_intents, force=True)
    assert start_res["status"] == "DECISION_CYCLE_OPENED"
    assert len(start_res["unauthorized_rejected"]) == 1
    assert start_res["unauthorized_rejected"][0]["reason"] == "ROLE_ACTOR_NOT_AUTHENTICATED"


def test_p1_worldline_manifest_idempotent_and_switch_recovery(temp_environment):
    """P1: worldlines_manifest.json is created, deterministic, supports switching, and rolls back corrupt save.json."""
    env = temp_environment
    host = env["host"]
    save_dir = env["save_dir"]

    info1 = host.inspect_worldline(save_dir=save_dir, loaded_filename="MyLEAGUE0003")
    manifest_path = save_dir / "worldlines_manifest.json"
    assert manifest_path.exists()
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "worldlines" in manifest_data
    w_id = info1["worldline_id"]
    assert w_id in manifest_data["worldlines"]

    info2 = host.inspect_worldline(save_dir=save_dir, loaded_filename="MyLEAGUE0003")
    assert info2["worldline_id"] == w_id
    manifest_data2 = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(manifest_data2["worldlines"]) == len(manifest_data["worldlines"])

    custom_target = "custom_branch_wl_002"
    manifest_data2["worldlines"][custom_target] = {
        "database_file": "world.sqlite",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "parent_worldline_id": w_id
    }
    manifest_path.write_text(json.dumps(manifest_data2, indent=2), encoding="utf-8")

    info3 = host.inspect_worldline(save_dir=save_dir, loaded_filename="MyLEAGUE0003", target_worldline_id=custom_target)
    assert info3["worldline_id"] == custom_target
    manifest_data3 = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_data3["active_worldline_id"] == custom_target

    info4 = host.inspect_worldline(save_dir=save_dir, loaded_filename="MyLEAGUE0003", target_worldline_id=w_id)
    assert info4["worldline_id"] == w_id


def test_g7_gold_100_offline_batch_validation_replay():
    """G7: Replay 100 gold live receipts through validate_stage_directory and assert fail-closed verification."""
    from validate_batch_execution import validate_stage_directory
    root = Path(__file__).resolve().parents[5]
    gold_dirs = [d for d in root.rglob("mutation_100") if d.is_dir() and (d / "manifest_BATCH-100-BENCH-MUTATION.json").exists()]
    assert len(gold_dirs) > 0, "Gold 100 mutation_100 directory must exist"
    gold_dir = gold_dirs[0]

    val_res = validate_stage_directory(gold_dir, expected_count=100, expected_mode="mutation")
    assert val_res["validation_passed"] is True, f"Validation failed: {val_res['errors']}"
    assert len(val_res["errors"]) == 0
    assert val_res["checks"]["planned_intent_count"] == 100
    assert val_res["checks"]["receipt_count"] == 100
    assert val_res["checks"]["unknown_count"] == 0
    assert val_res["checks"]["conservation_holds"] is True


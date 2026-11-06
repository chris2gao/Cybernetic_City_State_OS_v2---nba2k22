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
            INSERT INTO teams (team_id, display_name) VALUES
            ('team:1', 'MIL'), ('team:2', 'BKN'), ('team:3', 'POR'),
            ('team:25', 'GSW'), ('team:28', 'LAL')
        """)
        conn.execute("""
            INSERT INTO games (game_id, season_id, game_date, home_team_id, away_team_id, native_game_id)
            VALUES ('game:001', 'season:2021', '2021-11-01', 'team:1', 'team:2', '101')
        """)
        conn.execute("""
            INSERT INTO games (game_id, season_id, game_date, home_team_id, away_team_id, native_game_id)
            VALUES ('game:002', 'season:2021', '2021-11-05', 'team:1', 'team:3', '102')
        """)

    auth_manifest = {
        "schema_version": "nba2k22.rea.role_authorizations.v1",
        "save_id": "nba2k22_test_01",
        "worldline_id": "worldline-main",
        "bound_database_file": "world.sqlite",
        "authorized_worldlines": ["worldline-main", "*"],
        "authorized_databases": ["world.sqlite", "*"],
        "allow_wildcard_scope": True,  # F2: explicit human-declared wildcard scope for test fixture
        "human_authorization_ref": "HUMAN_TEST_AUTH_20261102",
        "provenance": "SAVE_DB_VERIFIED_DELEGATION",
        "roles": [
            {"role_type": "GM", "team_id": 1, "actor_uid": "gm_user_01", "provenance": "SAVE_DB_VERIFIED_DELEGATION", "human_authorization_ref": "HUMAN_TEST_AUTH_20261102"},
            {"role_type": "GM", "team_id": 25, "actor_uid": "gm_user_01", "provenance": "SAVE_DB_VERIFIED_DELEGATION", "human_authorization_ref": "HUMAN_TEST_AUTH_20261102"},
            {"role_type": "GM", "team_id": 28, "actor_uid": "gm_user_01", "provenance": "SAVE_DB_VERIFIED_DELEGATION", "human_authorization_ref": "HUMAN_TEST_AUTH_20261102"},
            {"role_type": "COACH", "team_id": 1, "actor_uid": "coach_user_01", "provenance": "SAVE_DB_VERIFIED_DELEGATION", "human_authorization_ref": "HUMAN_TEST_AUTH_20261102"}
        ]
    }
    (save_dir / "role_authorizations.json").write_text(json.dumps(auth_manifest, indent=2), encoding="utf-8")

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


@pytest.mark.parametrize(("live_date", "changes", "omit", "expected"), [
    pytest.param("2021-11-05", {}, (), "INITIAL_BASELINE_REUSED", id="confirmed-same-final"),
    pytest.param("2021-11-05", {"status": "NO_FINAL_GAMES_IN_MEMORY", "latest_memory_game_id": None},
                 ("native_game_id", "latest_db_native_game_id"), "BASELINE_CONTEXT_CHANGED", id="no-native-final-db-has-final"),
    pytest.param("2021-11-05", {"status": "UNKNOWN"}, (), "BASELINE_CONTEXT_CHANGED", id="unknown-status"),
    pytest.param("2021-11-05", {}, ("status",), "BASELINE_CONTEXT_CHANGED", id="missing-status"),
    pytest.param("2021-11-05", {}, ("new_final_game_detected",), "BASELINE_CONTEXT_CHANGED", id="missing-flag"),
    pytest.param("2021-11-05", {"new_final_game_detected": None}, (), "BASELINE_CONTEXT_CHANGED", id="null-flag"),
    pytest.param("2021-11-05", {"new_final_game_detected": 0}, (), "BASELINE_CONTEXT_CHANGED", id="non-bool-flag"),
    pytest.param("2021-11-05", {"latest_memory_game_id": "game:001"}, (), "BASELINE_CONTEXT_CHANGED", id="canonical-id-mismatch"),
    pytest.param("2021-11-05", {"native_game_id": 101}, (), "BASELINE_CONTEXT_CHANGED", id="native-id-mismatch"),
    pytest.param("2021-11-05", {}, ("latest_db_native_game_id",), "BASELINE_CONTEXT_CHANGED", id="missing-db-native-id"),
    pytest.param("2021-11-06", {}, (), "BASELINE_CONTEXT_CHANGED", id="date-changed"),
    pytest.param("2021-11-05", {"new_final_game_detected": True}, (), "BASELINE_CONTEXT_CHANGED", id="new-final"),
    pytest.param("2021-11-05", {"status": "INCOMPLETE_GAME_IN_PROGRESS"}, (), "REJECTED_GAME_IN_PROGRESS", id="game-in-progress"),
    pytest.param("2021-11-05", {"status": "NO_FINAL_GAMES_IN_MEMORY", "latest_memory_game_id": None,
                               "latest_db_game_id": None},
                 ("native_game_id", "latest_db_native_game_id"), "BASELINE_CONTEXT_CHANGED", id="empty-history-unverified"),
])
def test_first_live_decision_reuses_only_matching_baseline(temp_environment, monkeypatch, live_date, changes, omit, expected):
    import calendar_sim_orchestrator
    from calendar_sim_orchestrator import CalendarSimOrchestrator
    from engine import ingest_capture
    import refresh
    import schedule_reader

    host = temp_environment["host"]
    host.initialize_season(str(temp_environment["save_dir"]), "MyLEAGUE0003", mock_game_date="2021-11-05")
    host.state["is_offline_mock"] = False
    progress = {"status": "SAME_STATE_REPEAT", "new_final_game_detected": False,
                "latest_memory_game_id": "game:002", "latest_db_game_id": "game:002",
                "native_game_id": 102, "latest_db_native_game_id": "102"}
    progress.update(changes)
    for field in omit:
        progress.pop(field)
    def unexpected(*args, **kwargs):
        pytest.fail("First round attempted a recapture, process read or Native Getter")

    if (not changes and not omit) or (changes.get("status") == "NO_FINAL_GAMES_IN_MEMORY" and progress["latest_db_game_id"]):
        # Exercise the production detector against a real fixture SQLite final in both cases.
        with connect(host.state["database_file"]) as conn:
            ingest_capture(conn, {
                "save_id": "nba2k22_test_01", "run_id": "test_final", "unit_id": "test_final",
                "source_key": "BOUND_TEST", "observed_at": "2026-11-05T00:00:00Z",
                "evidence_grade": "RESEARCH_FIXTURE", "decoder_version": "1.0",
                "season": {"season_id": "season:2021", "season_code": "2021-22"},
                "facts": {"game_state_observations": [
                    {"game_id": "game:002", "status_code": "FINAL", "is_final": 1, "was_simulated": 1}
                ]},
                "artifacts": [{"sha256": "1" * 64, "payload_kind": "TEST", "payload_ref": "test.bin",
                               "byte_count": 1, "source_version": "1", "restricted": 1}],
            })
        entries = [] if changes else [{"status": 2, "record_shape_valid": True, "native_game_id": 102}]
        monkeypatch.setattr(CalendarSimOrchestrator, "inspect_process_liveness", lambda *_: {})
        monkeypatch.setattr(calendar_sim_orchestrator, "collect_schedule",
                            lambda *args, **kwargs: {"manifest": {"entries": entries}})
    else:
        monkeypatch.setattr(CalendarSimOrchestrator, "inspect_calendar_progress", lambda *_: progress)

    class FixtureReader:
        read = staticmethod(unexpected)

    before_state = dict(host.state)
    before_files = {name: temp_environment[name].read_bytes() for name in ("state_file", "ledger_file", "outbox_db")}
    monkeypatch.setattr(refresh, "resolve_pid", lambda _: 8536)
    monkeypatch.setattr(schedule_reader, "collect_schedule",
                        lambda *args, **kwargs: {"calendar": {"current_native_iso_date": live_date}})

    monkeypatch.setattr(CalendarSimOrchestrator, "trigger_world_capture", unexpected)
    monkeypatch.setattr(host, "_get_live_getter", unexpected)
    result = host.start_cycle("cycle-001", reader=FixtureReader())
    if expected != "INITIAL_BASELINE_REUSED":
        assert result["status"] == expected
        assert host.outbox.get_cycle("cycle-001") is None
        assert host.state == before_state
        assert all(temp_environment[name].read_bytes() == data for name, data in before_files.items())
        return
    assert result["progress_status"] == "INITIAL_BASELINE_REUSED"
    sealed = host.seal_cycle_decisions("cycle-001")
    assert sealed["status"] == "NO_CHANGE_WAITING_HUMAN_CALENDAR_ADVANCE"
    assert sealed["executable_intents_count"] == 0
    assert host.state["status"] == HostState.WAITING_CALENDAR_ADVANCE
    assert host.outbox.get_cycle("cycle-001")["status"] == "COMPLETED"


def test_live_no_change_does_not_close_over_a_concurrent_intent(temp_environment, monkeypatch):
    from season_cycle_host import ActionIntent

    host = temp_environment["host"]
    cycle_id = "cycle-001"
    host.initialize_season(str(temp_environment["save_dir"]), "MyLEAGUE0003", mock_game_date="2021-11-05")
    host.start_cycle(cycle_id, mock_game_date="2021-11-05")
    profile, _ = host._make_profiles(host._make_context(cycle_id))
    intent = ActionIntent.decided(
        "late-intent", "gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH",
        {"team_id": 1, "player_id": 2459, "field_id": "SHOT_TENDENCY",
         "value": 85, "expected_before": 80, "values": {"SHOT_TENDENCY": 85}},
    )
    phase_grants = host.role_registry.get_phase_grants()
    host.state["is_offline_mock"] = False
    list_intents = host.outbox.list_intents

    def insert_after_empty_snapshot(requested_cycle, *, status=None):
        result = list_intents(requested_cycle, status=status)
        if status is None and not result:
            host.outbox.add_intent(cycle_id, intent, profile, phase_grants)
        return result

    monkeypatch.setattr(host.outbox, "list_intents", insert_after_empty_snapshot)
    monkeypatch.setattr(host, "_get_live_getter", lambda: pytest.fail("No Native Getter expected"))
    with pytest.raises(RuntimeError, match="NO_CHANGE_INTENTS_CHANGED"):
        host.seal_cycle_decisions(cycle_id)
    assert host.state["status"] == HostState.DECISION_OPEN
    assert host.outbox.get_cycle(cycle_id)["status"] == "COLLECTING"
    assert [row["intent_id"] for row in list_intents(cycle_id, status="DRAFT")] == ["late-intent"]


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
    assert res_c3_exec["status"] == "STOPPED_PARTIAL"
    assert getter(2019, "SHOT_TENDENCY") == 92
    assert host.outbox.get_cycle("cycle-003")["status"] == "STOPPED_PARTIAL"
    assert host.state["status"] == HostState.STOPPED_PARTIAL


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


@pytest.mark.parametrize("case", ["verified", "invalid-evidence", "interrupted"])
def test_p0_a_fresh_getter_after_isolated_from_preflight_cache(temp_environment, monkeypatch, case):
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
                    "unaltered_fields_check": case != "invalid-evidence"
                }]
            }
        return {"outcome": "SESSION_SUCCESS", "evidence_id": "ev-p0a", "chunk_results": results}

    if case == "interrupted":
        from season_cycle_host import BoundedSessionExecutor

        def interrupt(*args, **kwargs):
            raise KeyboardInterrupt

        monkeypatch.setattr(BoundedSessionExecutor, "execute_batch", interrupt)
        stale_state = dict(host.state)
        with pytest.raises(KeyboardInterrupt):
            host.authorize_and_execute("cycle-fresh-getter", digest, transport=fake_runner_ok)
        restarted = SeasonCycleHost(state_file=env["state_file"], ledger_file=env["ledger_file"],
                                    outbox_db=env["outbox_db"])
        assert restarted.state["status"] == HostState.UNKNOWN_LOCKED
        with pytest.raises(ValueError, match="Host not in awaiting authorization state"):
            restarted.authorize_and_execute("cycle-fresh-getter", digest, transport=fake_runner_ok)
        host.state = stale_state
        with pytest.raises(ValueError, match="EXECUTION_ALREADY_CLAIMED_NO_REPLAY"):
            host.authorize_and_execute("cycle-fresh-getter", digest, transport=fake_runner_ok)
        return

    exec_res = host.authorize_and_execute(
        "cycle-fresh-getter",
        plan_digest=digest,
        transport=fake_runner_ok,
        getter_after_func=post_getter
    )
    assert post_read_call_count >= 1
    assert exec_res["readback_verified"] is True
    cycle = host.outbox.get_cycle("cycle-fresh-getter")
    rows = host.outbox.list_intents("cycle-fresh-getter")
    if case == "invalid-evidence":
        assert exec_res["status"] == "STOPPED_VALIDATION_FAILED"
        assert cycle["status"] == "STOPPED_PARTIAL"
        assert [row["status"] for row in rows] == ["FAILED"]
        return
    assert exec_res["status"] == "EXECUTED_AND_READBACK_RECORDED"
    assert cycle["status"] == "COMPLETED"
    assert [row["status"] for row in rows] == ["SUCCESS"]

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
    host.state["is_offline_mock"] = False
    host.state["is_mock"] = False

    def dummy_transport(chunks, script):
        return {}

    with pytest.raises(RuntimeError, match="LIVE_MODE_REJECTS_FAKE_TRANSPORT"):
        host.authorize_and_execute("cycle-live-guard", plan_digest=digest, transport=dummy_transport)

    import refresh
    monkeypatch.setattr(refresh, "resolve_pid", lambda mode: 5720)
    with pytest.raises(ValueError, match="AUTHORIZATION_PENDING_HUMAN"):
        host.authorize_and_execute("cycle-live-guard", plan_digest=digest)

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
    monkeypatch.setattr(host, "_approved_live_context", lambda pid: {"team_id": 1, "actor_uid": "gm_user_01"})
    with pytest.raises(ValueError, match="LIVE_SCOPE_VIOLATION"):
        host.seal_cycle_decisions("cycle-unauth-scope", getter_func=lambda pid, fid: 80)


@pytest.mark.parametrize("case", [
    "verified", "noop", "raw-conflict", "raw-missing", "epoch-drift",
    "approval-hash", "approval-scope", "approval-expired", "cas-drift", "role-expired",
])
def test_s4_bound_single_batch_reconciliation(temp_environment, monkeypatch, case):
    from datetime import timedelta
    import hashlib
    import contracts
    import refresh
    from bounded_session_transport import SessionBatchTransport
    from live_world import read_binding

    env = temp_environment
    host = env["host"]
    cycle = "s4-fixture"
    host.initialize_season(str(env["save_dir"]), "MyLEAGUE0003", mock_game_date="2021-11-05")
    binding, binding_sha = read_binding(env["save_dir"], "MyLEAGUE0003")
    now = datetime.now(timezone.utc)
    auth_path = env["save_dir"] / "role_authorizations.json"
    grant = {
        "save_id": binding["save_id"], "worldline_id": binding["worldline_id"],
        "bound_database_file": Path(host.state["database_file"]).name,
        "binding_sha256": binding_sha, "human_authorization_ref": "SYNTHETIC_TEST_ONLY",
        "authorized_at": (now - timedelta(minutes=1)).isoformat(),
        "expires_at": (now + timedelta(minutes=5)).isoformat(),
        "action_id": "PLAYER_PATCH_TENDENCIES", "field_id": "SHOT_TENDENCY", "player_ids": [2459],
        "roles": [{"role_type": "GM", "team_id": 1, "actor_uid": "gm_user_01"}],
    }
    target = 80 if case == "noop" else 81
    host.start_cycle(cycle, candidate_intents=[{
        "intent_id": "s4-item", "issuer_role": "GM", "actor_uid": "gm_user_01",
        "action_id": "PLAYER.EDIT.TENDENCY_BATCH",
        "parameters": {"team_id": 1, "player_id": 2459, "expected_before": 80,
                       "values": {"SHOT_TENDENCY": target}},
    }], force=True)
    auth_path.write_text(json.dumps(grant), encoding="utf-8")
    host.approved_role_manifest_sha256 = hashlib.sha256(auth_path.read_bytes()).hexdigest()
    host.state["is_offline_mock"] = False
    host.state["is_mock"] = False
    epoch = {"pid": 5720, "creation_filetime": 100}
    progress = {"today_native_iso_date": "2021-11-05"}
    value = 80
    call_count = 0
    monkeypatch.setattr(refresh, "resolve_pid", lambda _: 5720)
    monkeypatch.setattr(refresh, "_context", lambda _: {"epoch": dict(epoch), "game_progress": progress})
    monkeypatch.setattr(host, "_get_fresh_live_getter", lambda expected_pid=None: (lambda *_: value))

    def synthetic_transport(self, script, chunks, header):
        nonlocal value, call_count
        call_count += 1
        assert self.live_context.authorization_ref == "SYNTHETIC_BATCH_APPROVAL"
        assert self.live_context.expected_pid == 5720
        chunk, = chunks
        item, = chunk.intents
        value = item.value
        row = {"intent_id": item.intent_id, "team_id": item.team_id, "player_id": item.player_id,
               "field_id": item.field_id, "expected_before": item.expected_before, "requested": item.value,
               "outcome": "UNCHANGED_ALREADY_TARGET" if case == "noop" else "SUCCESS_APPLIED",
               "getter_before": 80, "getter_after": target, "raw_after": target, "unaltered_fields_check": True}
        result = {"kind": "chunk-execution-result", "chunk_id": chunk.chunk_id, "chunk_digest": chunk.chunk_digest,
                  "plan_digest": chunk.plan_digest, "action_id": chunk.action_id, "batch_id": chunk.batch_id,
                  "save_instance_id": chunk.save_instance_id, "outcome": "CHUNK_SUCCESS", "receipts": [row]}
        raw_row = dict(row)
        if case == "raw-conflict":
            raw_row["getter_after"] = target + 1
        raw_result = dict(result, receipts=[raw_row])
        session = self.runtime_directory / "fixture"
        session.mkdir()
        if case != "raw-missing":
            (session / "evidence.json").write_text(json.dumps(
                {"normalized_result": {"messages": [{"type": "send", "payload": raw_result}]}}), encoding="utf-8")
        (session / "target.json").write_text(json.dumps(
            {"pid": 5720, "exe_sha256": contracts.BUILD}), encoding="utf-8")
        return {"outcome": "SESSION_SUCCESS", "evidence_id": "fixture", "chunk_results": {chunk.chunk_id: result}}

    monkeypatch.setattr(SessionBatchTransport, "execute_session", synthetic_transport)
    if case == "role-expired":
        grant["expires_at"] = (now - timedelta(seconds=1)).isoformat()
        auth_path.write_text(json.dumps(grant), encoding="utf-8")
        host.approved_role_manifest_sha256 = hashlib.sha256(auth_path.read_bytes()).hexdigest()
        with pytest.raises(ValueError, match="LIVE_DELEGATION_OUTSIDE_APPROVED_TIME"):
            host.seal_cycle_decisions(cycle)
        assert call_count == 0
        return
    sealed = host.seal_cycle_decisions(cycle)
    assert sealed["plan_digest"] != sealed["native_plan_digest"]
    with pytest.raises(ValueError, match="EXACT_LIVE_BATCH_AUTHORIZATION_REQUIRED"):
        host.authorize_and_execute(cycle, sealed["plan_digest"])
    approval = {key: sealed[key] for key in ("cycle_id", "plan_digest", "native_plan_digest", "live_context", "items")}
    approval.update(schema_version="nba2k22.s4.batch_approval.v1", approval_ref="SYNTHETIC_BATCH_APPROVAL",
                    approved_at=(now - timedelta(seconds=10)).isoformat(),
                    expires_at=(now + timedelta(minutes=5)).isoformat())
    if case == "approval-scope":
        approval["items"][0]["value"] += 1
    if case == "approval-expired":
        approval["expires_at"] = (now - timedelta(seconds=1)).isoformat()
    approval_path = env["tmp_path"] / "private-batch-approval.json"
    approval_path.write_text(json.dumps(approval), encoding="utf-8")
    approval_pin = hashlib.sha256(approval_path.read_bytes()).hexdigest() if case != "approval-hash" else "0" * 64
    kwargs = {"live_batch_approval": approval_path, "approved_live_batch_sha256": approval_pin}
    if case == "epoch-drift":
        epoch["creation_filetime"] = 101
        with pytest.raises(RuntimeError, match="LIVE_CONTEXT_CHANGED_SINCE_APPROVAL"):
            host.authorize_and_execute(cycle, sealed["plan_digest"], **kwargs)
        assert call_count == 0
        assert host.outbox.get_cycle(cycle)["status"] == "SEALED"
        return
    blocked = {"approval-hash": "LIVE_BATCH_APPROVAL_HASH_MISMATCH",
               "approval-scope": "LIVE_BATCH_APPROVAL_SCOPE_MISMATCH",
               "approval-expired": "LIVE_BATCH_APPROVAL_OUTSIDE_APPROVED_TIME"}
    if case in blocked:
        with pytest.raises(ValueError, match=blocked[case]):
            host.authorize_and_execute(cycle, sealed["plan_digest"], **kwargs)
        assert call_count == 0 and host.outbox.get_cycle(cycle)["status"] == "SEALED"
        return
    if case == "cas-drift":
        value = 79
        with pytest.raises(RuntimeError, match="LIVE_CAS_CHANGED_SINCE_APPROVAL"):
            host.authorize_and_execute(cycle, sealed["plan_digest"], **kwargs)
        assert call_count == 0 and host.outbox.get_cycle(cycle)["status"] == "SEALED"
        return
    summary = host.authorize_and_execute(cycle, sealed["plan_digest"], **kwargs)
    assert call_count == 1
    rows = host.outbox.list_intents(cycle)
    if case in ("raw-conflict", "raw-missing"):
        assert summary["status"] == "STOPPED_UNKNOWN_LOCKED"
        assert rows[0]["status"] == "UNKNOWN"
    else:
        assert summary["status"] == "EXECUTED_AND_READBACK_RECORDED"
        assert host.outbox.get_cycle(cycle)["status"] == "COMPLETED"
        assert rows[0]["status"] == ("NOOP" if case == "noop" else "SUCCESS")
    with pytest.raises(ValueError, match="Host not in awaiting authorization state"):
        host.authorize_and_execute(cycle, sealed["plan_digest"], **kwargs)
    assert call_count == 1


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


def test_trusted_role_registry_save_provenance_and_database_verification(temp_environment):
    """Verify TrustedRoleRegistry binds to save directory, generates role_authorizations.json, and validates teams against save DB."""
    env = temp_environment
    host = env["host"]
    save_dir = env["save_dir"]

    # 1. Initialize season binds registry to save_dir and creates role_authorizations.json
    host.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    auth_file = save_dir / "role_authorizations.json"
    assert auth_file.is_file(), "role_authorizations.json must be persisted in save directory"
    auth_data = json.loads(auth_file.read_text(encoding="utf-8"))
    assert auth_data["save_id"] == "nba2k22_test_01"
    assert auth_data["bound_database_file"].endswith(".sqlite")
    assert len(auth_data["roles"]) >= 2

    # 2. Valid team in save database authenticates
    assert host.role_registry.is_actor_authenticated("GM", 1, "gm_user_01") is True
    assert host.role_registry.is_actor_authenticated("COACH", 1, "coach_user_01") is True

    # 3. Invalid actor for valid team rejected
    assert host.role_registry.is_actor_authenticated("GM", 1, "fake_actor") is False

    # 4. Team that does NOT exist in the save database is rejected even if actor matches
    assert host.role_registry.is_actor_authenticated("GM", 9999, "gm_user_01") is False

    # 5. Modifying role_authorizations.json with custom actor updates bindings faithfully
    custom_roles = [
        {"role_type": "GM", "team_id": 2, "actor_uid": "custom_gm_bkn", "provenance": "CUSTOM_AUTHORIZED_DELEGATION"}
    ]
    auth_data["roles"] = custom_roles
    auth_file.write_text(json.dumps(auth_data, indent=2), encoding="utf-8")

    # Re-bind registry to save
    host.role_registry.bind_save_context(save_dir, "nba2k22_test_01", "worldline-main", save_dir / "world.sqlite")
    assert host.role_registry.is_actor_authenticated("GM", 2, "custom_gm_bkn") is True
    # Old mapping no longer authenticated
    assert host.role_registry.is_actor_authenticated("GM", 1, "gm_user_01") is False


def test_validate_batch_execution_rejects_reconstructed_mock_as_native_evidence():
    """Verify validate_batch_execution refuses to accept host-reconstructed chunk messages as genuine native transport IPC."""
    import contracts
    from bulk_executor import BulkBatch, BulkBatchHeader, BulkIntentItem, ItemReceipt
    from validate_batch_execution import validate_batch_execution

    header = BulkBatchHeader(
        batch_id="TEST-BATCH-RECON",
        save_instance_id="save-01",
        game_build_sha256=contracts.BUILD,
        authorization_ref="AUTH-01",
        source_snapshot_ref="SNAP-01",
        expected_process_name="NBA2K22.exe",
        expected_pid=5720,
        dry_run=False
    )
    intents = (
        BulkIntentItem(
            intent_id="i-1",
            action_id="PLAYER_PATCH_TENDENCIES",
            team_id=1,
            field_id="SHOT_TENDENCY",
            expected_before=80,
            value=85,
            player_id=2459
        ),
    )
    batch = BulkBatch(header=header, intents=intents)
    from bulk_executor import BulkBatchPlanner
    chunks = BulkBatchPlanner().plan(batch, max_chunk_size=50)

    receipts = [
        ItemReceipt(
            intent_id="i-1",
            team_id=1,
            player_id=2459,
            field_id="SHOT_TENDENCY",
            expected_before=80,
            requested=85,
            getter_before=80,
            getter_after=85,
            raw_after=85,
            outcome="SUCCESS_APPLIED",
            chunk_id=chunks[0].chunk_id,
            timestamp="2026-11-02T12:00:00Z",
            unaltered_fields_check=True
        )
    ]
    readback = {
        "all_100_persisted_in_game": True,
        "missed_count": 0,
        "verified_items": [{
            "intent_id": "i-1",
            "player_id": 2459,
            "readback_getter": 85,
            "target_tendency": 85,
            "confirmed": True
        }]
    }

    # 1. Reconstructed mock message tagged with OFFLINE_MOCK_RECONSTRUCTED must be rejected if require_native_transport_evidence=True
    reconstructed_raw = [{
        "kind": "chunk-execution-result",
        "provenance": "OFFLINE_MOCK_RECONSTRUCTED",
        "chunk_id": chunks[0].chunk_id,
        "chunk_digest": chunks[0].chunk_digest,
        "plan_digest": chunks[0].plan_digest,
        "action_id": chunks[0].action_id,
        "batch_id": chunks[0].batch_id,
        "save_instance_id": chunks[0].save_instance_id,
        "outcome": "CHUNK_SUCCESS",
        "receipts": [{"intent_id": "i-1", "outcome": "SUCCESS_APPLIED"}]
    }]

    res_reject = validate_batch_execution(
        batch=batch,
        chunks=chunks,
        raw_messages=reconstructed_raw,
        receipts=receipts,
        independent_readback=readback,
        require_native_transport_evidence=True
    )
    assert res_reject["validation_passed"] is False
    assert any("RECONSTRUCTED_MOCK_CANNOT_SATISFY_NATIVE_TRANSPORT_EVIDENCE" in e for e in res_reject["errors"])
    assert res_reject["checks"]["raw_evidence_is_reconstructed"] is True
    assert res_reject["checks"]["native_transport_evidence_verified"] is False

    # 2. Live mode without any raw messages must fail closed (NATIVE_TRANSPORT_EVIDENCE_MISSING)
    res_missing = validate_batch_execution(
        batch=batch,
        chunks=chunks,
        raw_messages=[],
        receipts=receipts,
        independent_readback=readback,
        require_native_transport_evidence=True
    )
    assert res_missing["validation_passed"] is False
    assert any("NATIVE_TRANSPORT_EVIDENCE_MISSING" in e for e in res_missing["errors"])
    assert res_missing["checks"]["native_transport_evidence_verified"] is False

    # 3. Offline mock mode (require_native_transport_evidence=False) safely skips raw transport without false claims
    res_mock_ok = validate_batch_execution(
        batch=batch,
        chunks=chunks,
        raw_messages=[],
        receipts=receipts,
        independent_readback=readback,
        require_native_transport_evidence=False
    )
    assert res_mock_ok["validation_passed"] is True
    assert res_mock_ok["checks"]["native_transport_evidence_verified"] is False
    assert res_mock_ok["checks"]["raw_evidence_status"] == "OFFLINE_MOCK_TRANSPORT_SKIPPED"




def test_h1_authorization_file_missing_default_denies_and_generates_template(tmp_path):
    """H1: When role_authorizations.json is missing, Live mode generates template only, default denies, and blocks execution."""
    save_dir = tmp_path / "save_missing"
    native_file = tmp_path / "MyLEAGUE0003"
    native_file.write_bytes(b"FAKE_SAVE")
    initialize_save(str(save_dir), "save_missing_01", str(native_file))

    host = SeasonCycleHost(
        workspace_root=tmp_path,
        state_file=tmp_path / "state_missing.json",
        ledger_file=tmp_path / "ledger_missing.jsonl",
        outbox_db=tmp_path / "outbox_missing.db"
    )

    init_res = host.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    auth_file = save_dir / "role_authorizations.json"
    template_file = save_dir / "role_authorizations.template.json"
    assert not auth_file.exists(), "Must NOT create role_authorizations.json automatically in live mode"
    assert template_file.is_file(), "Template file must be created for operator reference"
    tpl_data = json.loads(template_file.read_text(encoding="utf-8"))
    assert tpl_data["status"] == "TEMPLATE_PENDING_HUMAN_AUTHORIZATION"
    assert host.role_registry.is_authorized is False
    assert host.role_registry.authorization_status == "AUTHORIZATION_FILE_MISSING"

    # Candidate intents rejected fail-closed
    intents = [{
        "intent_id": "missing-intent-1",
        "issuer_role": "GM",
        "actor_uid": "gm_user_01",
        "action_id": "PLAYER_PATCH_TENDENCIES",
        "parameters": {"team_id": 1, "player_id": 2019, "values": {"SHOT_TENDENCY": 80}}
    }]
    cycle_res = host.start_cycle("cycle-missing-auth", candidate_intents=intents, force=True)
    assert cycle_res["status"] == "DECISION_CYCLE_OPENED"
    assert len(cycle_res["unauthorized_rejected"]) == 1
    assert cycle_res["unauthorized_rejected"][0]["reason"] == "ROLE_ACTOR_NOT_AUTHENTICATED"


def test_h1_template_cannot_become_active_authorization(tmp_path):
    """H1: Configuration template with TEMPLATE_PENDING_HUMAN_AUTHORIZATION cannot be used as active authorization."""
    save_dir = tmp_path / "save_tpl"
    native_file = tmp_path / "MyLEAGUE0003"
    native_file.write_bytes(b"FAKE_SAVE")
    initialize_save(str(save_dir), "save_tpl_01", str(native_file))

    template_content = {
        "schema_version": "nba2k22.rea.role_authorizations.v1",
        "save_id": "save_tpl_01",
        "worldline_id": "worldline-main",
        "bound_database_file": "world.sqlite",
        "status": "TEMPLATE_PENDING_HUMAN_AUTHORIZATION",
        "human_authorization_ref": None,
        "provenance": "PENDING_OPERATOR_SIGNING",
        "roles": [{"role_type": "GM", "team_id": 1, "actor_uid": "gm_user_01"}]
    }
    (save_dir / "role_authorizations.json").write_text(json.dumps(template_content, indent=2), encoding="utf-8")

    from season_cycle_host import TrustedRoleRegistry
    reg = TrustedRoleRegistry()
    success = reg.bind_save_context(save_dir, "save_tpl_01", "worldline-main", save_dir / "world.sqlite")
    assert success is False
    assert reg.is_authorized is False
    assert reg.authorization_status == "TEMPLATE_CANNOT_BECOME_ACTIVE_AUTHORIZATION"


def test_h1_mock_authorization_strictly_isolated_from_live():
    """H1: Mock role authorization injection is physically blocked in Live mode."""
    from season_cycle_host import TrustedRoleRegistry
    live_registry = TrustedRoleRegistry(is_mock=False)
    with pytest.raises(ValueError, match="LIVE_MODE_REJECTS_MOCK_AUTHORIZATION"):
        live_registry.inject_mock_authorizations([{"role_type": "GM", "team_id": 1, "actor_uid": "mock_gm"}])

    mock_registry = TrustedRoleRegistry(is_mock=True)
    mock_registry.inject_mock_authorizations([{"role_type": "GM", "team_id": 1, "actor_uid": "mock_gm"}])
    assert mock_registry.authorization_status == "AUTHORIZED_MOCK"
    assert mock_registry.is_authorized is True
    assert mock_registry.get_actor("GM", 1) == "mock_gm"


def test_h2_database_missing_read_failure_and_empty_teams_fail_closed(tmp_path):
    """H2: Database missing, unreadable, or empty teams table fails closed."""
    from season_cycle_host import TrustedRoleRegistry
    reg = TrustedRoleRegistry()

    # Case A: Non-existent database file
    reg.database_path = tmp_path / "nonexistent.sqlite"
    assert reg._verify_team_in_database(28) is False

    # Case B: Corrupted / invalid SQLite file
    corrupt_db = tmp_path / "corrupt.sqlite"
    corrupt_db.write_bytes(b"NOT_A_SQLITE_DATABASE_HEADER")
    reg.database_path = corrupt_db
    assert reg._verify_team_in_database(28) is False

    # Case C: Database exists but has 0 rows in teams table
    empty_db = tmp_path / "empty_teams.sqlite"
    create_database(empty_db, "save_empty_teams_01")
    reg.save_id = "save_empty_teams_01"
    reg.database_path = empty_db
    assert reg._verify_team_in_database(28) is False
    assert reg._get_teams_from_database() == set()

    # Case D: Database save_id mismatch
    reg.save_id = "different_save_id_expected"
    assert reg._verify_team_in_database(28) is False


def test_h2_team_native_format_positive_and_invalid_id_negative(tmp_path):
    """H2: Correctly parses current schema team:native:<ID> and rejects invalid IDs."""
    from season_cycle_host import TrustedRoleRegistry, parse_team_numeric_id
    assert parse_team_numeric_id("team:native:28") == 28
    assert parse_team_numeric_id("team:native:0") == 0
    assert parse_team_numeric_id("team:25") == 25
    assert parse_team_numeric_id(1) == 1
    assert parse_team_numeric_id("invalid") is None
    assert parse_team_numeric_id(None) is None

    db_path = tmp_path / "teams_native.sqlite"
    create_database(db_path, "save_native_teams_01")
    with connect(db_path) as conn:
        conn.execute("INSERT INTO teams (team_id, display_name) VALUES ('team:native:28', 'LAL'), ('team:native:0', 'PHI'), ('team:native:25', 'GSW')")

    reg = TrustedRoleRegistry(save_id="save_native_teams_01", database_path=db_path)
    db_teams = reg._get_teams_from_database()
    assert 28 in db_teams
    assert 0 in db_teams
    assert 25 in db_teams

    assert reg._verify_team_in_database(28) is True
    assert reg._verify_team_in_database("team:native:28") is True
    assert reg._verify_team_in_database(0) is True
    assert reg._verify_team_in_database(9999) is False
    assert reg._verify_team_in_database(-1) is False
    assert reg._verify_team_in_database("malformed") is False


def test_h3_save_worldline_and_db_context_mismatch_fails_closed(temp_environment):
    """H3: Context binding mismatches (save_id, worldline_id, database_file, provenance) fail closed."""
    env = temp_environment
    save_dir = env["save_dir"]
    auth_file = save_dir / "role_authorizations.json"
    base_auth = json.loads(auth_file.read_text(encoding="utf-8"))

    from season_cycle_host import TrustedRoleRegistry
    reg = TrustedRoleRegistry()

    # 1. save_id mismatch
    bad_save = dict(base_auth)
    bad_save["save_id"] = "different_save_99"
    auth_file.write_text(json.dumps(bad_save), encoding="utf-8")
    assert reg.bind_save_context(save_dir, "nba2k22_test_01", "worldline-main", save_dir / "world.sqlite") is False
    assert reg.authorization_status == "AUTHORIZATION_SAVE_ID_MISMATCH"

    # 2. worldline_id mismatch
    bad_wl = dict(base_auth)
    bad_wl["worldline_id"] = "isolated_worldline_strict"
    bad_wl["authorized_worldlines"] = ["isolated_worldline_strict"]
    auth_file.write_text(json.dumps(bad_wl), encoding="utf-8")
    assert reg.bind_save_context(save_dir, "nba2k22_test_01", "worldline-main", save_dir / "world.sqlite") is False
    assert reg.authorization_status == "AUTHORIZATION_WORLDLINE_MISMATCH"

    # 3. database_file mismatch
    bad_db = dict(base_auth)
    bad_db["bound_database_file"] = "other_database.sqlite"
    bad_db["authorized_databases"] = ["other_database.sqlite"]
    auth_file.write_text(json.dumps(bad_db), encoding="utf-8")
    assert reg.bind_save_context(save_dir, "nba2k22_test_01", "worldline-main", save_dir / "world.sqlite") is False
    assert reg.authorization_status == "AUTHORIZATION_DATABASE_FILE_MISMATCH"

    # 4. human authorization provenance missing
    bad_prov = dict(base_auth)
    bad_prov["human_authorization_ref"] = None
    bad_prov["provenance"] = None
    auth_file.write_text(json.dumps(bad_prov), encoding="utf-8")
    assert reg.bind_save_context(save_dir, "nba2k22_test_01", "worldline-main", save_dir / "world.sqlite") is False
    assert reg.authorization_status == "AUTHORIZATION_PROVENANCE_MISSING"

    # Restore valid auth file
    auth_file.write_text(json.dumps(base_auth), encoding="utf-8")


def test_h4_ambiguous_multiple_actors_fails_closed_and_missing_actor_uid_rejected(temp_environment):
    """H4: Multiple actors for a single role profile fail closed with explicit ambiguity error; missing actor_uid is rejected."""
    env = temp_environment
    host = env["host"]
    save_dir = env["save_dir"]
    auth_file = save_dir / "role_authorizations.json"
    base_auth = json.loads(auth_file.read_text(encoding="utf-8"))

    # Case A: Ambiguous multiple GM actors
    ambiguous_auth = dict(base_auth)
    ambiguous_auth["roles"] = [
        {"role_type": "GM", "team_id": 1, "actor_uid": "gm_alice", "provenance": "SAVE_DB_VERIFIED_DELEGATION", "human_authorization_ref": "HUMAN_GRANT_01"},
        {"role_type": "GM", "team_id": 25, "actor_uid": "gm_bob", "provenance": "SAVE_DB_VERIFIED_DELEGATION", "human_authorization_ref": "HUMAN_GRANT_01"}
    ]
    auth_file.write_text(json.dumps(ambiguous_auth), encoding="utf-8")
    host.role_registry.bind_save_context(save_dir, "nba2k22_test_01", "worldline-main", save_dir / "world.sqlite")

    ctx = host._make_context("test-ambiguity-cycle")
    with pytest.raises(ValueError, match="AMBIGUOUS_MULTIPLE_ACTORS_FOR_ROLE"):
        host.role_registry.get_profiles(ctx)

    # Restore valid auth file
    auth_file.write_text(json.dumps(base_auth), encoding="utf-8")
    host.role_registry.bind_save_context(save_dir, "nba2k22_test_01", "worldline-main", save_dir / "world.sqlite")

    host.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-01"
    )

    # Case B: Missing actor_uid for an unregistered team cannot be authenticated
    unregistered_team_intent = [{
        "intent_id": "unregistered-team-intent-1",
        "issuer_role": "GM",
        "action_id": "PLAYER_PATCH_TENDENCIES",
        "parameters": {"team_id": 999, "player_id": 2019, "values": {"SHOT_TENDENCY": 80}}
    }]
    c_res = host.start_cycle("cycle-missing-actor", candidate_intents=unregistered_team_intent, force=True)
    assert len(c_res["unauthorized_rejected"]) == 1
    assert c_res["unauthorized_rejected"][0]["reason"] == "ACTOR_UID_MISSING_AND_UNAUTHENTICATED"


def test_h4_fixed_default_roles_cannot_automatically_obtain_live_permissions():
    """H4: TrustedRoleRegistry has no hardcoded default actors; unconfigured registry default denies."""
    from season_cycle_host import TrustedRoleRegistry
    reg = TrustedRoleRegistry(is_mock=False)
    assert reg.is_authorized is False
    assert reg._actors == {}
    assert reg.get_authenticated_teams("GM") == ()
    assert reg.get_authenticated_teams("COACH") == ()
    assert reg.is_actor_authenticated("GM", 1, "gm_user_01") is False
    assert reg.is_actor_authenticated("COACH", 1, "coach_user_01") is False


def test_raw_transport_missing_or_forged_evidence_rejected_in_live(temp_environment):
    """Verify live validation rejects missing, forged, or mismatched raw REA transport evidence."""
    import contracts
    from bulk_executor import BulkBatch, BulkBatchHeader, BulkIntentItem, ItemReceipt, PlannedChunk
    from validate_batch_execution import validate_batch_execution

    header = BulkBatchHeader(
        batch_id="BATCH-TEST-NATIVE-FAIL",
        save_instance_id="MyLEAGUE0003",
        game_build_sha256=contracts.BUILD,
        authorization_ref="AUTH-TEST-NATIVE",
        source_snapshot_ref="SNAP-TEST-NATIVE",
        expected_process_name="NBA2K22.exe",
        expected_pid=5720,
        dry_run=False
    )
    item = BulkIntentItem(
        intent_id="i-test-1",
        player_id=2019,
        field_id="SHOT_TENDENCY",
        expected_before=65,
        value=75,
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=1
    )
    batch = BulkBatch(header=header, intents=(item,))
    planned_chunks = [PlannedChunk(
        chunk_id="chunk-test-1",
        team_id=1,
        action_id="PLAYER_PATCH_TENDENCIES",
        intents=(item,),
        estimated_call_count=1,
        estimated_duration_ms=100,
        batch_id="BATCH-TEST-NATIVE-FAIL",
        save_instance_id="MyLEAGUE0003",
        plan_digest=batch.plan_digest,
        chunk_digest="b" * 64
    )]
    receipts = [ItemReceipt(
        intent_id="i-test-1",
        team_id=1,
        player_id=2019,
        field_id="SHOT_TENDENCY",
        expected_before=65,
        requested=75,
        outcome="SUCCESS_APPLIED",
        chunk_id="chunk-test-1",
        timestamp="2026-11-02T12:00:00Z",
        getter_before=65,
        getter_after=75,
        raw_after=75,
        unaltered_fields_check=True
    )]
    readback = {
        "missed_count": 0,
        "all_100_persisted_in_game": True,
        "verified_items": [{
            "intent_id": "i-test-1",
            "player_id": 2019,
            "readback_getter": 75,
            "target_tendency": 75,
            "confirmed": True
        }]
    }

    # 1. Unknown chunk_id in raw evidence
    mismatched_chunk_msg = [{
        "type": "send",
        "payload": {
            "kind": "chunk-execution-result",
            "chunk_id": "chunk-wrong-id",
            "chunk_digest": "b" * 64,
            "plan_digest": batch.plan_digest,
            "action_id": "PLAYER_PATCH_TENDENCIES",
            "batch_id": "BATCH-TEST-NATIVE-FAIL",
            "save_instance_id": "MyLEAGUE0003",
            "outcome": "CHUNK_SUCCESS",
            "receipts": [{"intent_id": "i-test-1"}]
        }
    }]
    res_bad_id = validate_batch_execution(
        batch=batch,
        chunks=planned_chunks,
        raw_messages=mismatched_chunk_msg,
        receipts=receipts,
        independent_readback=readback,
        require_native_transport_evidence=True
    )
    assert res_bad_id["validation_passed"] is False
    assert any("unknown or missing chunk_id" in e for e in res_bad_id["errors"])

    # 2. Corrupted chunk_digest in raw evidence
    corrupt_digest_msg = [{
        "type": "send",
        "payload": {
            "kind": "chunk-execution-result",
            "chunk_id": "chunk-test-1",
            "chunk_digest": "corrupted_digest_xxx",
            "plan_digest": batch.plan_digest,
            "action_id": "PLAYER_PATCH_TENDENCIES",
            "batch_id": "BATCH-TEST-NATIVE-FAIL",
            "save_instance_id": "MyLEAGUE0003",
            "outcome": "CHUNK_SUCCESS",
            "receipts": [{"intent_id": "i-test-1"}]
        }
    }]
    res_bad_digest = validate_batch_execution(
        batch=batch,
        chunks=planned_chunks,
        raw_messages=corrupt_digest_msg,
        receipts=receipts,
        independent_readback=readback,
        require_native_transport_evidence=True
    )
    assert res_bad_digest["validation_passed"] is False
    assert any("Raw chunk_digest mismatch" in e for e in res_bad_digest["errors"])


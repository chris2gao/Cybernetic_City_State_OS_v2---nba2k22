"""Offline contracts for deterministic E0 assignment and the R0 comparison gate."""
import copy
import hashlib
import json
import sqlite3

import pytest

from e0_r0 import FAMILIES, assign, bound_units, compare_controls, control_result, field_registry, opportunity


def test_r0_separates_zero_minutes_and_missing():
    assert opportunity(0, 0) == ("DNP_OR_ZERO_RECORDED_MINUTES", None)
    assert opportunity(None, 10) == ("NOT_OBSERVED", None)
    assert opportunity(2, 0) == ("INCONSISTENT_ZERO_MINUTES", None)
    assert opportunity(0, 12) == ("OBSERVED", 0)
    assert opportunity(3, 18) == ("OBSERVED", 6)


def test_hlc_reproducible_with_distinct_teams_and_opponent_exposure():
    pool = [dict(uid=uid, team=team, eligible=True, shot_tendency=50, position="CENTER",
                 mean_minutes=27, next_games=3) for uid, team in ((1, 10), (2, 20), (3, 30), (4, 10))]
    games = [dict(game_id="a", scheduled_date="2021-12-21", home=10, away=20)]
    result = assign(pool, games, "fixed-seed")
    assert result == assign(pool[::-1], games, "fixed-seed")
    assert len({x["team"] for x in result["targets"]}) == 3
    assert {x["arm"]: x["proposed_value"] for x in result["targets"]} == {"H": 55, "L": 45, "C": 50}
    assert result["opponent_exposures"][0]["direct_treatment_opponent"] is True
    assert assign([dict(x, shot_tendency=2) for x in pool], games)["targets"] == []


def control(**changes):
    row = dict(worldline="A", save_identity="SaveA", db_identity="DB-A", no_intervention=True,
               frozen_origin_sha256="a" * 64, initial_state_sha256="b" * 64, mode="CALENDAR_SIM_ONLY",
               window_start="2021-12-21", window_end_exclusive="2021-12-28",
               expected_native_game_ids=["12"], games=[dict(native_game_id="12", home_points=100,
               away_points=98, player_box_sha256="c" * 64, played_date="2021-12-21",
               simulation_mode="CALENDAR_SIM_ONLY")])
    return dict(row, **changes)


def test_r0_comparison_counts_variation_without_claiming_determinism():
    left = control()
    right = control(worldline="B", save_identity="SaveB", db_identity="DB-B")
    assert compare_controls(left, right)["interpretation"] == "MATCHED_THIS_PAIR_ONLY"
    right["games"][0].update(home_points=101, player_box_sha256="d" * 64)
    result = compare_controls(left, right)
    assert (result["score_differences"], result["player_box_differences"]) == (1, 1)
    assert result["interpretation"] == "VARIATION_OBSERVED"


@pytest.mark.parametrize("case", ["shared-db", "different-start", "missing-game", "3d", "wrong-date", "duplicate", "changed-setting"])
def test_r0_rejects_noncomparable_controls(case):
    left = control()
    right = control(worldline="B", save_identity="SaveB", db_identity="DB-B")
    if case == "shared-db":
        right["db_identity"] = left["db_identity"]
    elif case == "different-start":
        right["frozen_origin_sha256"] = "d" * 64
    elif case == "missing-game":
        right["games"] = []
    elif case == "3d":
        right["games"][0]["simulation_mode"] = "3D"
    elif case == "wrong-date":
        right["games"][0]["played_date"] = "2021-12-28"
    elif case == "duplicate":
        right["games"] *= 2
    elif case == "changed-setting":
        right["initial_state_sha256"] = "d" * 64
    with pytest.raises(ValueError):
        compare_controls(left, right)


def test_source_gate_pins_exact_units_and_refuses_missing_families():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE capture_units(unit_id,source_key,payload_sha256,unit_status,observed_at,run_id)")
    conn.execute("CREATE TABLE capture_runs(run_id,season_id,source_grade)")
    conn.execute("INSERT INTO capture_runs VALUES('run','season','LIVE_READ')")
    units = []
    for family, source in FAMILIES.items():
        unit = dict(unit_id=family, source_key=source, payload_sha256="1" * 64, unit_status="success",
                    observed_at="2026-11-06T00:00:00Z", season_id="season", source_grade="LIVE_READ")
        conn.execute("INSERT INTO capture_units VALUES(?,?,?,?,?,'run')",
                     tuple(unit[k] for k in ("unit_id", "source_key", "payload_sha256", "unit_status", "observed_at")))
        units.append(dict(family=family, unit=unit, commit_status="COMMITTED_SUCCESS_VERIFIED", status="ACQUIRED"))
    binding = dict(save_id="A", database_file="a.sqlite", native_save_filename="A")
    raw = json.dumps(binding).encode()
    report = dict(binding, sources=units, status="COMPLETED_REQUESTED_SOURCES", game_writes=False,
                  binding_sha256=hashlib.sha256(raw).hexdigest())
    assert set(bound_units(conn, report, binding, raw)) == set(FAMILIES)
    changed = copy.deepcopy(report)
    changed["sources"][0]["unit"]["payload_sha256"] = "2" * 64
    with pytest.raises(ValueError, match="Unverified exact SQL capture unit"):
        bound_units(conn, changed, binding, raw)
    with pytest.raises(ValueError, match="Missing or duplicate"):
        bound_units(conn, dict(report, sources=units[1:]), binding, raw)
    with pytest.raises(ValueError, match="does not bind"):
        bound_units(conn, dict(report, save_id="B"), binding, raw)


def test_only_shot_tendency_has_historical_live_writer_grade():
    registry = field_registry()
    players = [r for r in registry if r["unit"] == "player"]
    assert len(players) == 99
    assert sum(r["action_grade"] == "READ_ONLY" for r in players) == 51
    assert len([r for r in registry if r["unit"] == "team"]) == 10
    assert [r["field_id"] for r in registry if r["action_grade"] == "LIVE_SETTER_VERIFIED"] == ["SHOT_TENDENCY"]
    assert all(not r["allowed_doses"] for r in registry if r["field_id"] != "SHOT_TENDENCY")


def test_control_result_requires_exact_post_capture_boxes_and_stop_date(tmp_path):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE games(game_id,native_game_id,home_team_id,away_team_id,season_id);
        CREATE TABLE game_source_checks(game_id,unit_id,played_native_iso_date,game_type_label,box_mode);
        CREATE TABLE game_state_observations(game_id,unit_id,home_points,away_points,is_final,was_simulated);
        CREATE TABLE team_game_boxes(game_id,unit_id,team_id,points);
        CREATE TABLE player_game_boxes(game_id,unit_id,player_id,team_id,points,fg_made,fg_attempted,
            three_made,three_attempted,ft_made,ft_attempted,offensive_rebounds,defensive_rebounds,
            assists,steals,blocks,turnovers,fouls,minutes_raw);
        INSERT INTO games VALUES('g','12','H','A','season');
        INSERT INTO game_source_checks VALUES('g','post','2021-12-22','NORMAL','FULL_NATIVE_BOX');
        INSERT INTO game_state_observations VALUES('g','post',100,98,1,1);
        INSERT INTO team_game_boxes VALUES('g','post','H',100),('g','post','A',98);
        INSERT INTO player_game_boxes(game_id,unit_id,player_id,team_id,fg_attempted,minutes_raw)
            VALUES('g','post','p1','H',5,25),('g','post','p2','A',4,22),('g','pre','p2','A',99,47);
    """)
    anchor = control(pre_capture_observed_at="2026-11-06T08:00:00Z")
    manifest = dict(window_start="2021-12-28", source_report_sha256="a" * 64,
                    units={"schedule": dict(unit_id="post", season_id="season", observed_at="2026-11-06T09:00:00Z")})
    inventory = {"sim_mode": "CALENDAR_SIM_ONLY"}
    binding = dict(worldline_id="A", native_save_filename="SaveA")
    args = (inventory, binding, tmp_path / "a.sqlite", anchor)
    actual = control_result(conn, manifest, *args)
    assert actual["games"][0]["native_game_id"] == "12"
    conn.execute("UPDATE player_game_boxes SET fg_attempted=42 WHERE unit_id='pre'")
    assert control_result(conn, manifest, *args) == actual
    with pytest.raises(ValueError, match="stop date"):
        control_result(conn, dict(manifest, window_start="2021-12-29"), *args)
    conn.execute("UPDATE team_game_boxes SET unit_id='pre' WHERE team_id='A'")
    with pytest.raises(ValueError, match="exact-unit boxes"):
        control_result(conn, manifest, *args)

from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys
from types import SimpleNamespace

import pytest

WORLDDATA = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(WORLDDATA), str(WORLDDATA.parent / "research/rea_native_control")]
from factor_analysis import screen_settled_events
from factor_assignment import event_study
from factor_adapters import adapter_contract, prepare_coach_patch
from factor_analysis import screen_coach_window
from factor_coach import COACH_CAPTURE_FAMILIES, capture_coach_exposure
from factor_inventory import StudyInputs
from factor_runner import window_operations
from factor_management import MANAGEMENT_CAPTURE_FAMILIES, _TERMS, capture_management_event
from factor_settlement import DEVELOPMENT_CAPTURE_FAMILIES, capture_development_event


SHA = "a" * 64
SCHEMA = """
    CREATE TABLE capture_runs(run_id,source_grade,season_id);
    CREATE TABLE capture_units(unit_id,payload_sha256,unit_status,observed_at,source_key,run_id);
    CREATE TABLE game_mode_observations(unit_id,today_native_iso_date,today_minutes_since_midnight_raw,mode_label,league_label);
    CREATE TABLE native_player_sources(player_source_id,unit_id,player_id,native_unique_id_raw,
                                        native_team_id,current_core_roster_status);
    CREATE TABLE player_attribute_snapshots(source_player_id,unit_id,player_id,stamina_raw);
    CREATE TABLE player_health_observations(source_player_id,unit_id,player_id,fatigue_raw,wear_and_tear_raw);
"""


def write_source_report(conn, directory, bound, index, families):
    directory.mkdir()
    units = {}
    for family in families:
        unit = f"{bound['worldline_id']}-{index}-{family}"
        row = {"unit_id": unit, "payload_sha256": SHA, "unit_status": "success",
               "observed_at": f"2026-01-01T00:00:0{index}Z", "source_key": family,
               "source_grade": "LIVE_READ", "season_id": bound["season_id"]}
        conn.execute("INSERT INTO capture_runs VALUES (?,?,?)", (unit, row["source_grade"], row["season_id"]))
        conn.execute("INSERT INTO capture_units VALUES (?,?,?,?,?,?)", (
            unit, SHA, "success", row["observed_at"], family, unit))
        units[family] = row
    report = {"status": "COMPLETED_REQUESTED_SOURCES", "game_writes": False, "save_id": bound["save_id"],
              "native_save_filename": bound["loaded_filename"], "binding_sha256": bound["binding_sha256"],
              "process_epoch": bound["epoch"],
              "sources": [{"family": family, "status": "ACQUIRED", "commit_status": "COMMITTED_SUCCESS_VERIFIED",
                           "unit": unit} for family, unit in units.items()]}
    raw = json.dumps(report).encode()
    (directory / "refresh-report.json").write_bytes(raw)
    return sha256(raw).hexdigest(), {family: row["unit_id"] for family, row in units.items()}


def settlement_fixture(tmp_path, arm, *, progression=False):
    tmp_path.mkdir()
    epoch = {"pid": 7, "creation_filetime": 100, "module_base": "0x140000000",
             "module_size": 1000, "pe_timestamp": 1652287197, "game_season_year": 2022}
    binding = {"save_id": "save-" + arm, "worldline_id": "world-" + arm, "loaded_filename": "MyLEAGUE0005",
               "binding_sha256": SHA}
    host = SimpleNamespace(save_id=binding["save_id"], loaded_filename="MyLEAGUE0005", binding_hash=SHA,
                           binding=binding, database=tmp_path / "world.sqlite")
    before_binding = dict(binding, epoch=epoch, season_id="2021-22")
    after_binding = dict(binding, epoch=dict(epoch, game_season_year=2023) if progression else epoch,
                         season_id="2022-23" if progression else "2021-22")
    paths = [tmp_path / "before", tmp_path / "after"]
    pins = []
    with closing(sqlite3.connect(host.database)) as conn, conn:
        conn.executescript(SCHEMA)
        for index, (directory, bound) in enumerate(zip(paths, (before_binding, after_binding), strict=True)):
            pin, units = write_source_report(conn, directory, bound, index, DEVELOPMENT_CAPTURE_FAMILIES)
            conn.execute("INSERT INTO game_mode_observations VALUES (?,?,?,?,?)",
                         (units["game-mode"], "2022-06-30", 600 + index * 20, "FRANCHISE", "NBA"))
            for family in ("player-skills", "player-state"):
                unit = units[family]
                conn.execute("INSERT INTO native_player_sources VALUES (?,?,?,?,?,?)",
                             (unit + "-player", unit, "player:101", 101, 4, "CURRENT_CORE_ROSTER"))
                if family == "player-skills":
                    conn.execute("INSERT INTO player_attribute_snapshots VALUES (?,?,?,?)",
                                 (unit + "-player", unit, "player:101", 60 + (3 if arm == "H" else 1) * index))
                else:
                    conn.execute("INSERT INTO player_health_observations VALUES (?,?,?,?,?)",
                                 (unit + "-player", unit, "player:101", None, 10 + index))
            pins.append(pin)
    factor = SimpleNamespace(factor_id="TEST_FACTOR", protocol="PROGRESSION" if progression else "TRAINING")
    proof = {"schema": "nba2k22.vae.development_settlement.v1", "mode": "LIVE", "factor_id": factor.factor_id,
             "protocol": factor.protocol, "binding": binding, "before_season_id": before_binding["season_id"],
             "after_season_id": after_binding["season_id"], "origin_sha256": SHA, "uid": 101, "team_id": 4, "arm": arm,
             "endpoints": ["skill.stamina_raw", "health.fatigue_raw", "health.wear_and_tear_raw"],
             "before_report_sha256": pins[0], "after_report_sha256": pins[1],
             "settlement": {"kind": f"NATIVE_{factor.protocol}_SETTLED", "verified": True,
                            "independent_review_ref": "synthetic test", "event_id": "settlement-" + arm,
                            "source_unit": "event-source-" + arm, "source_sha256": SHA,
                            "event_date": "2022-06-30", "minutes": 610},
             "treatment": {"status": "CONTROL_UNCHANGED" if arm == "C" else "APPLIED_VERIFIED",
                           "source_sha256": SHA, "requested": 51, "observed": 51}}

    def capture(**overrides):
        raw = json.dumps(proof).encode()
        options = dict(proof_raw=raw, approved_proof_sha256=sha256(raw).hexdigest(),
                       before_directory=paths[0], after_directory=paths[1],
                       before_binding=before_binding, after_binding=after_binding)
        return capture_development_event(host, factor, **(options | overrides))

    return factor, proof, capture


def test_training_reads_sql_and_keeps_fatigue_missing(tmp_path):
    factor, _, high = settlement_fixture(tmp_path / "high", "H")
    _, _, control = settlement_fixture(tmp_path / "control", "C")
    rows = [high(), control()]
    refs = {row["worldline_id"]: {key: row[key] for key in ("event_id", "event_date", "source_unit")} for row in rows}
    plan = event_study(factor, list(refs), refs)
    skill = screen_settled_events(plan, rows, "skill.stamina_raw", mode="LIVE")
    fatigue = screen_settled_events(plan, rows, "health.fatigue_raw", mode="LIVE")
    assert skill["effects"] == {"H_minus_C": 2} and skill["status"] == "UNDERPOWERED"
    assert fatigue["effects"] == {} and fatigue["status"] == "NO_MEASURABLE_ENDPOINT"
    assert rows[0]["before"]["health.wear_and_tear_raw"] == 10
    assert rows[0]["before_source_units"]["player-state"]["unit_id"] == "world-H-0-player-state"
    with pytest.raises(ValueError, match="EVENT_WORLDLINES_REQUIRE_DISTINCT_SETTLEMENT_SOURCES"):
        refs["world-C"]["source_unit"] = refs["world-H"]["source_unit"]
        screen_settled_events(plan, rows, "skill.stamina_raw", mode="LIVE")


@pytest.mark.parametrize("invalid,reason", [
    ("day_advanced", "SETTLEMENT_PROOF_SCOPE_MISMATCH"),
    ("source_reuse", "REQUIRES_INDEPENDENT_EVENT_SOURCE"),
    ("outside", "SETTLEMENT_OUTSIDE_OBSERVED_INTERVAL"),
    ("report_sha", "CAPTURE_REPORT_HASH_MISMATCH"),
    ("fixture", "SETTLEMENT_PROOF_SCOPE_MISMATCH"),
])
def test_configuration_or_calendar_cannot_substitute_for_settlement(tmp_path, invalid, reason):
    _, proof, capture = settlement_fixture(tmp_path / "train", "H")
    if invalid == "day_advanced":
        proof["settlement"]["kind"] = "CALENDAR_ADVANCED"
    elif invalid == "source_reuse":
        proof["settlement"]["source_unit"] = "world-H-1-game-mode"
    elif invalid == "outside":
        proof["settlement"]["minutes"] = 625
    elif invalid == "report_sha":
        proof["after_report_sha256"] = SHA
    else:
        proof["mode"] = "FIXTURE"
    with pytest.raises(ValueError, match=reason):
        capture()


def test_growth_accepts_year_rollover_with_same_process_and_player(tmp_path):
    _, proof, capture = settlement_fixture(tmp_path / "growth", "H", progression=True)
    row = capture()
    assert row["protocol"] == "PROGRESSION" and row["before_identity"] == row["after_identity"] == "player:101"
    assert row["after"]["skill.stamina_raw"] == 63
    proof["treatment"]["status"] = "SETTER_UNVERIFIED"
    assert capture()["setter_verified"] is False
    with pytest.raises(PermissionError, match="PROOF_PIN_MISMATCH"):
        capture(approved_proof_sha256=SHA)


def management_fixture(tmp_path, trade):
    binding = {"save_id": "save", "worldline_id": "world", "loaded_filename": "MyLEAGUE0005", "binding_sha256": SHA}
    epoch = {"pid": 7, "creation_filetime": 100, "module_base": "0x140000000", "module_size": 1000, "pe_timestamp": 1652287197}
    bound = dict(binding, epoch=epoch, season_id="2021-22")
    host = SimpleNamespace(save_id="save", loaded_filename=binding["loaded_filename"], binding_hash=SHA, binding=binding,
                           database=tmp_path / "world.sqlite")
    paths = [tmp_path / "before", tmp_path / "after"]
    pins = []
    with closing(sqlite3.connect(host.database)) as conn, conn:
        conn.executescript(SCHEMA + f"""
            CREATE TABLE player_contract_observations(source_player_id,unit_id,player_id,
                 native_contract_team_id_raw,contract_team_status,{','.join(_TERMS)});
            CREATE TABLE native_transaction_observations(native_transaction_id,unit_id,native_type_code,
                 date_word_raw,data_count_raw,active_prefix_status);
            CREATE TABLE native_transaction_item_observations(unit_id,native_transaction_id,source_item_index,
                 native_type_code,integer_word_raw);
        """)
        for index, directory in enumerate(paths):
            pin, units = write_source_report(conn, directory, bound, index, MANAGEMENT_CAPTURE_FAMILIES)
            pins.append(pin)
            team = 4 + index if trade else 4
            unit = units["player-details"]
            conn.execute("INSERT INTO game_mode_observations VALUES (?,?,?,?,?)",
                         (units["game-mode"], "2022-02-01", 600 + index * 20, "FRANCHISE", "NBA"))
            conn.execute("INSERT INTO native_player_sources VALUES (?,?,?,?,?,?)",
                         (unit + "-player", unit, "player:101", 101, team, "CURRENT_CORE_ROSTER"))
            terms = [1] * len(_TERMS)
            terms[_TERMS.index("extension_length_raw")] = 1 + index if not trade else 0
            conn.execute("INSERT INTO player_contract_observations VALUES (" + ",".join("?" * (len(_TERMS) + 5)) + ")",
                         (unit + "-player", unit, "player:101", team, "NATIVE_CORE_TEAM_POINTER_OBSERVED", *terms))
        conn.execute("INSERT INTO native_transaction_observations VALUES (?,?,?,?,?,?)",
                     ("transaction-after", units["news"], 7, 123, 2, "WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE"))
        conn.executemany("INSERT INTO native_transaction_item_observations VALUES (?,?,?,?,?)",
                         [(units["news"], "transaction-after", 0, 3, 98), (units["news"], "transaction-after", 1, 4, 17)])
    factor = SimpleNamespace(factor_id="TEST_MANAGEMENT", protocol="TRADE_DRAFT" if trade else "CONTRACT")
    proof = {"schema": "nba2k22.vae.management_settlement.v1", "mode": "LIVE", "factor_id": factor.factor_id,
             "protocol": factor.protocol, "binding": binding, "before_season_id": bound["season_id"],
             "after_season_id": bound["season_id"], "origin_sha256": SHA, "uid": 101, "team_id": 4, "arm": "H",
             "endpoints": ["ownership_moved"] if trade else ["extension_length_raw"],
             "before_report_sha256": pins[0], "after_report_sha256": pins[1],
             "settlement": {"kind": "NATIVE_PLAYER_TRADE_SETTLED" if trade else "NATIVE_CONTRACT_EXTENDED",
                            "verified": True, "independent_review_ref": "synthetic test", "event_id": "event",
                            "source_unit": "independent-event-source", "source_sha256": SHA,
                            "event_date": "2022-02-01", "minutes": 610, "after_team_id": 5 if trade else 4,
                            "native_transaction_id": "transaction-after",
                            "transaction_signature": {"type_code": 7, "date_word": 123, "items": [[3, 98], [4, 17]]}},
             "treatment": {"status": "APPLIED_VERIFIED", "source_sha256": SHA, "requested": 51, "observed": 51}}

    def capture():
        raw = json.dumps(proof).encode()
        return capture_management_event(host, factor, proof_raw=raw, approved_proof_sha256=sha256(raw).hexdigest(),
                                        before_directory=paths[0], after_directory=paths[1],
                                        before_binding=bound, after_binding=bound)

    return host, proof, capture


@pytest.mark.parametrize("trade", [False, True])
def test_management_joins_exact_new_transaction_to_native_roster_and_contract(tmp_path, trade):
    _, proof, capture = management_fixture(tmp_path, trade)
    row = capture()
    assert row["native_transaction_id"] == "transaction-after"
    assert row["before_identity"] == row["after_identity"] == "player:101"
    assert row["after_team_id"] == (5 if trade else 4)
    assert row["after"] == ({"ownership_moved": 1} if trade else {"extension_length_raw": 2})
    proof["settlement"]["transaction_signature"]["items"][0][1] = 97
    with pytest.raises(ValueError, match="MANAGEMENT_TRANSACTION_NOT_NEW_UNIQUE_AND_EXACT"):
        capture()


def test_management_rejects_reused_transaction_and_owner_disagreement(tmp_path):
    host, _, capture = management_fixture(tmp_path, True)
    with closing(sqlite3.connect(host.database)) as conn, conn:
        conn.execute("INSERT INTO native_transaction_observations VALUES (?,?,?,?,?,?)",
                     ("transaction-before", "world-0-news", 7, 123, 2, "WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE"))
        conn.executemany("INSERT INTO native_transaction_item_observations VALUES (?,?,?,?,?)",
                         [("world-0-news", "transaction-before", 0, 3, 98), ("world-0-news", "transaction-before", 1, 4, 17)])
    with pytest.raises(ValueError, match="MANAGEMENT_TRANSACTION_NOT_NEW_UNIQUE_AND_EXACT"):
        capture()
    with closing(sqlite3.connect(host.database)) as conn, conn:
        conn.execute("UPDATE player_contract_observations SET native_contract_team_id_raw=4 WHERE unit_id='world-1-player-details'")
    with pytest.raises(ValueError, match="MANAGEMENT_CONTRACT_OWNER_AND_ROSTER_DISAGREE"):
        capture()


def coach_fixture(tmp_path):
    inputs = WORLDDATA.parents[2] / "01_os/07_content/_runs/run-20261108-nba2k22-full-factor-plan-001"
    study = StudyInputs.load(inputs)
    binding = {"save_id": "save", "worldline_id": "world", "loaded_filename": "MyLEAGUE0005", "binding_sha256": SHA,
               "epoch": {"pid": 7}, "season_id": "2021-22"}
    host = SimpleNamespace(save_id="save", loaded_filename="MyLEAGUE0005", binding_hash=SHA, binding=binding,
                           database=tmp_path / "world.sqlite")
    directory = tmp_path / "pre"
    targets = {1: 13, 2: 15, 3: 14}
    assignments = {team: {"factor_id": "COACH_DEFAULT_004", "team_id": team, "uid": None,
                          "arm": arm, "baseline": 14, "target": targets[team], "live_writer_qualified": False}
                   for team, arm in zip((1, 2, 3), "HLC", strict=True)}
    games = [{"game_id": game, "date": "2022-01-02", "home_team": team, "away_team": 3,
              "home": assignments[team], "away": assignments[3]} for game, team in ((10, 1), (11, 2))]
    plan = {"worldline_id": "world", "start": "2022-01-01", "stop_exclusive": "2022-01-03",
            "teams": assignments, "factors": ["COACH_DEFAULT_004"], "games": games}
    with closing(sqlite3.connect(host.database)) as conn, conn:
        conn.executescript(SCHEMA + """
            CREATE TABLE teams(team_id,native_team_id);
            CREATE TABLE gameplan_observations(plan_id,team_id,opponent_team_id,unit_id,
                 poe_defense_1_raw,is_in_use_raw,is_tainted_raw);
        """)
        report_sha, units = write_source_report(conn, directory, binding, 0, COACH_CAPTURE_FAMILIES)
        conn.execute("INSERT INTO game_mode_observations VALUES (?,?,?,?,?)",
                     (units["game-mode"], "2022-01-01", 0, "FRANCHISE", "NBA"))
        conn.executemany("INSERT INTO teams VALUES (?,?)", [(f"team-{team}", team) for team in targets])
        for game in games:
            for team, opponent in ((game["home_team"], 3), (3, game["home_team"])):
                conn.execute("INSERT INTO gameplan_observations VALUES (?,?,?,?,?,?,?)",
                             (f"plan-{team}-{opponent}", f"team-{team}", f"team-{opponent}", units["planning"], 14, 1, 0))
    proof = {"schema": "nba2k22.vae.coach_exposure.v1", "mode": "LIVE",
             "binding": {key: binding[key] for key in ("save_id", "worldline_id", "loaded_filename", "binding_sha256", "epoch")},
             "planning_report_sha256": report_sha, "independent_review_ref": "synthetic test",
             "current_projection": [{"team_id": team, "read_action": "READ_COACH_CURRENT", "read_only": True,
                                     "source_sha256": SHA, "data": {"team_id": team, "reciprocal_owner_matches": True,
                                      "known_current_settings": {"POEDefense": value}}} for team, value in targets.items()],
             "consumers": [{"game_id": game["game_id"], "team_id": team, "opponent_team_id": opponent,
                            "factor_id": "COACH_DEFAULT_004", "value": targets[team], "game_date": game["date"],
                            "verified": True, "source_sha256": SHA}
                           for game in games for team, opponent in ((game["home_team"], 3), (3, game["home_team"]))]}
    def capture():
        raw = json.dumps(proof).encode()
        return capture_coach_exposure(host, study, plan, directory=directory, report_sha256=report_sha, binding=binding,
                                       proof_raw=raw, approved_proof_sha256=sha256(raw).hexdigest())
    outcome = {"mode": "LIVE", "worldline_id": "world", "today": plan["stop_exclusive"], "games": [
        dict(game, unit=f"unit-{game['game_id']}", team_box_unit=f"unit-{game['game_id']}",
             player_box_unit=f"unit-{game['game_id']}", score_conserved=True, final=True, was_simulated=True,
             team_boxes=[{"team_id": team, "uid": None, "disposition": "PLAYED",
                          "metrics": {"FGA": {1: 12, 2: 8, 3: 10}[team], "MIN": 240}}
                         for team in (game["home_team"], 3)])
        for game in games]}
    return study, proof, plan, capture, outcome


def test_coach_effect_requires_consumed_projection_and_team_units(tmp_path):
    study, proof, plan, capture, outcome = coach_fixture(tmp_path)
    exposure = capture()
    assert any(not row["stored_matches_projection"] and row["qualified"] for row in exposure["exposures"])
    operations = window_operations(plan)
    setters = [{"status": "APPLIED", "source_ref": SHA, "value": op["target"]} for op in operations]
    analysis = screen_coach_window(plan, operations, setters, outcome, exposure)
    result = analysis["factors"]["COACH_DEFAULT_004"]
    assert result["metrics"]["FGA"]["estimates"] == {"H_minus_C": 2, "L_minus_C": -2}
    assert result["status"] == "UNDERPOWERED"
    proof["consumers"] = []
    unknown = screen_coach_window(plan, operations, setters, outcome, capture())["factors"]["COACH_DEFAULT_004"]
    assert unknown["status"] == "CONSUMER_UNVERIFIED" and not unknown["observations"]
    assert unknown["unqualified_consumer_games"] == [10, 11]
    contract = adapter_contract(study.factors["COACH_DEFAULT_004"])
    with pytest.raises(ValueError, match="COACH_NATIVE_TEAM_AND_FIELD_REQUIRED"):
        prepare_coach_patch(contract, "BenchDepth", 1, bytes(352), 0, 13)


def test_coach_projection_and_game_consumer_mismatches_stop(tmp_path):
    _, proof, _, capture, _ = coach_fixture(tmp_path)
    proof["consumers"][0]["value"] = 14
    with pytest.raises(ValueError, match="COACH_GAME_CONSUMER_ASSIGNMENT_MISMATCH"):
        capture()
    proof["consumers"][0]["value"] = 13
    proof["current_projection"][0]["data"]["reciprocal_owner_matches"] = False
    with pytest.raises(ValueError, match="COACH_CURRENT_PROJECTION_READBACK_MISMATCH"):
        capture()

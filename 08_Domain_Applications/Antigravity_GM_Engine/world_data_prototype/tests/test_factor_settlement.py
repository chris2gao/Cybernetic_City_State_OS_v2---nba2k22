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
            directory.mkdir()
            units = {}
            for family in DEVELOPMENT_CAPTURE_FAMILIES:
                unit = f"{arm}-{index}-{family}"
                row = {"unit_id": unit, "payload_sha256": SHA, "unit_status": "success",
                       "observed_at": f"2026-01-01T00:00:0{index}Z", "source_key": family,
                       "source_grade": "LIVE_READ", "season_id": bound["season_id"]}
                conn.execute("INSERT INTO capture_runs VALUES (?,?,?)", (unit, row["source_grade"], row["season_id"]))
                conn.execute("INSERT INTO capture_units VALUES (?,?,?,?,?,?)", (
                    unit, SHA, "success", row["observed_at"], family, unit))
                units[family] = row
            conn.execute("INSERT INTO game_mode_observations VALUES (?,?,?,?,?)",
                         (units["game-mode"]["unit_id"], "2022-06-30", 600 + index * 20, "FRANCHISE", "NBA"))
            for family in ("player-skills", "player-state"):
                unit = units[family]["unit_id"]
                conn.execute("INSERT INTO native_player_sources VALUES (?,?,?,?,?,?)",
                             (unit + "-player", unit, "player:101", 101, 4, "CURRENT_CORE_ROSTER"))
                if family == "player-skills":
                    conn.execute("INSERT INTO player_attribute_snapshots VALUES (?,?,?,?)",
                                 (unit + "-player", unit, "player:101", 60 + (3 if arm == "H" else 1) * index))
                else:
                    conn.execute("INSERT INTO player_health_observations VALUES (?,?,?,?,?)",
                                 (unit + "-player", unit, "player:101", None, 10 + index))
            report = {"status": "COMPLETED_REQUESTED_SOURCES", "game_writes": False, "save_id": host.save_id,
                      "native_save_filename": host.loaded_filename, "binding_sha256": host.binding_hash,
                      "process_epoch": bound["epoch"],
                      "sources": [{"family": family, "status": "ACQUIRED", "commit_status": "COMMITTED_SUCCESS_VERIFIED",
                                   "unit": unit} for family, unit in units.items()]}
            raw = json.dumps(report).encode()
            (directory / "refresh-report.json").write_bytes(raw)
            pins.append(sha256(raw).hexdigest())
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
    assert rows[0]["before_source_units"]["player-state"]["unit_id"] == "H-0-player-state"
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
        proof["settlement"]["source_unit"] = "H-1-game-mode"
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

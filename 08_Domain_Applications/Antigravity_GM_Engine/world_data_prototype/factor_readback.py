"""Read verified WorldData units into the VAE multi-factor outcome contract."""
from contextlib import closing
import hashlib
import json

from calendar_sim_orchestrator import CalendarSimOrchestrator, captured_game_headers
from engine import connect
from live_world import bound_database

_BOX_METRICS = {
    "FGA": "fg_attempted", "FG3A": "three_attempted", "FTA": "ft_attempted", "MIN": "minutes_raw",
    "AST": "assists", "TOV": "turnovers", "PF": "fouls", "STL": "steals", "BLK": "blocks", "PTS": "points",
}


class FactorWorldDataPort:
    """Acquire the minimum bound sources through the existing WorldData refresh path."""
    def __init__(self, host, binding, runtime):
        self.host = host
        self.binding = binding
        self.runtime = runtime

    def __call__(self, phase, plan, setters):
        from refresh import refresh_world
        if phase not in ("pre", "post"):
            raise ValueError("FACTOR_CAPTURE_UNKNOWN_PHASE")
        state = self.host.state
        orchestrator = CalendarSimOrchestrator(state["save_directory"], state["loaded_filename"], state["database_file"])
        if (orchestrator.save_id != self.binding["save_id"]
                or orchestrator.loaded_filename != self.binding["loaded_filename"]
                or orchestrator.binding_hash != self.binding["binding_sha256"]
                or orchestrator.binding["worldline_id"] != self.binding["worldline_id"]
                or orchestrator.database != bound_database(orchestrator.save_directory, orchestrator.binding)):
            raise ValueError("FACTOR_CAPTURE_HOST_SAVE_BINDING_MISMATCH")
        directory = self.runtime / phase
        self.runtime.mkdir(parents=True, exist_ok=True)
        refresh_world(self.binding["pid"], orchestrator.save_directory, orchestrator.loaded_filename,
                      directory, families=("schedule", "game-mode", "player-skills"))
        report_sha = hashlib.sha256((directory / "refresh-report.json").read_bytes()).hexdigest()
        if phase == "pre":
            return capture_treatment_readback(orchestrator, directory, report_sha, plan, self.binding, setters,
                                              raw_reader=self.host.read_factor_qualification_snapshot)
        return capture_game_outcomes(orchestrator, directory, report_sha, plan, self.binding)


def _source_units(conn, report, season, families=("schedule", "game-mode", "player-skills")):
    units = {}
    for family in families:
        candidates = [row["unit"] for row in report["sources"] if row["family"] == family
                      and row["status"] == "ACQUIRED" and row["commit_status"] == "COMMITTED_SUCCESS_VERIFIED"]
        if len(candidates) != 1:
            raise ValueError("FACTOR_CAPTURE_REQUIRED_SOURCE_MISSING")
        candidate, = candidates
        row = conn.execute("""
            SELECT u.unit_id,u.payload_sha256,u.unit_status,u.observed_at,u.source_key,r.source_grade,r.season_id
            FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.unit_id=?
        """, (candidate["unit_id"],)).fetchone()
        if (row is None or row["source_grade"] != "LIVE_READ" or row["unit_status"] != "success"
                or row["season_id"] != season or any(row[k] != candidate[k] for k in row.keys())):
            raise ValueError("FACTOR_CAPTURE_UNIT_NOT_BOUND")
        units[family] = candidate["unit_id"]
    return units


def _bound_report(host, directory, report_sha256, plan, binding):
    data = (directory / "refresh-report.json").read_bytes()
    if hashlib.sha256(data).hexdigest() != report_sha256:
        raise ValueError("FACTOR_CAPTURE_REPORT_HASH_MISMATCH")
    report = json.loads(data)
    if (report["status"] != "COMPLETED_REQUESTED_SOURCES" or report["game_writes"] is not False
            or report["save_id"] != host.save_id or report["save_id"] != binding["save_id"]
            or report["native_save_filename"] != host.loaded_filename
            or report["binding_sha256"] != host.binding_hash or report["binding_sha256"] != binding["binding_sha256"]
            or report["process_epoch"] != binding["epoch"]
            or plan["worldline_id"] != host.binding.get("worldline_id")
            or plan["worldline_id"] != binding["worldline_id"]):
        raise ValueError("FACTOR_CAPTURE_IDENTITY_MISMATCH")
    return report


def capture_treatment_readback(host, directory, report_sha256, plan, binding, setters, *, raw_reader=None):
    from factor_runner import digest, window_operations
    from native_factor_slots import resolve_tendency_slot

    report = _bound_report(host, directory, report_sha256, plan, binding)
    applied = {}
    raw_observations = {}
    with closing(connect(host.database, True)) as conn:
        units = _source_units(conn, report, binding["season_id"])
        mode = conn.execute("""
            SELECT today_native_iso_date,mode_label,league_label FROM game_mode_observations WHERE unit_id=?
        """, (units["game-mode"],)).fetchone()
        if mode is None or tuple(mode) != (plan["start"], "FRANCHISE", "NBA"):
            raise ValueError("FACTOR_PRE_CAPTURE_WRONG_NATIVE_DATE_OR_MODE")
        for operation, receipt in zip(window_operations(plan), setters, strict=True):
            if receipt["status"] not in ("APPLIED", "NOOP"):
                continue
            field = resolve_tendency_slot(operation["factor_id"])
            column = "p." + field.native_key.lower() + "_raw" if field.named else "n.native_unique_id_raw"
            observed = conn.execute(f"""
                SELECT {column} FROM native_player_sources n
                JOIN player_tendency_snapshots p ON p.source_player_id=n.player_source_id AND p.unit_id=n.unit_id
                WHERE n.unit_id=? AND n.native_unique_id_raw=? AND n.native_team_id=?
                  AND n.current_core_roster_status='CURRENT_CORE_ROSTER' AND n.player_id IS NOT NULL
            """, (units["player-skills"], operation["uid"], operation["team_id"])).fetchall()
            if len(observed) != 1:
                raise ValueError("FACTOR_PRE_WINDOW_ROSTER_IDENTITY_NOT_OBSERVED")
            key = digest(operation)
            value = observed[0][0]
            if not field.named:
                if raw_reader is None:
                    raise ValueError("FACTOR_UNKNOWN_SLOT_REQUIRES_INDEPENDENT_RAW_READ")
                snapshot = raw_reader(pid=binding["pid"], epoch=binding["epoch"], team_id=operation["team_id"],
                                      uid=operation["uid"], field=field.native_key, binding_sha256=binding["binding_sha256"])
                image = bytes.fromhex(snapshot["neighborhood_hex"])
                if (snapshot["status"] != "READ_ONLY_SLOT_OBSERVED"
                        or any(snapshot[key] != binding[key] for key in ("save_id", "worldline_id", "loaded_filename",
                                                                        "binding_sha256", "epoch"))
                        or (snapshot["today"], snapshot["minutes"], snapshot["uid"], snapshot["team_id"], snapshot["factor_id"])
                           != (plan["start"], 0, operation["uid"], operation["team_id"], field.factor_id)
                        or hashlib.sha256(image).hexdigest() != snapshot["neighborhood_sha256"]
                        or field.decode(image) != snapshot["raw_value"]):
                    raise ValueError("FACTOR_PRE_WINDOW_RAW_SLOT_SOURCE_MISMATCH")
                value = snapshot["raw_value"]
                raw_observations[key] = snapshot
            if value != operation["target"]:
                raise ValueError("FACTOR_PRE_WINDOW_EXPOSURE_NOT_OBSERVED")
            applied[key] = value
    return {"mode": "LIVE", "worldline_id": binding["worldline_id"], "today": plan["start"],
            "source_unit": units["player-skills"], "report_sha256": report_sha256, "applied_values": applied,
            "raw_slot_observations": raw_observations}


def capture_game_outcomes(host, directory, report_sha256, plan, binding):
    report = _bound_report(host, directory, report_sha256, plan, binding)
    headers = captured_game_headers(directory, report)
    games, rejected = [], {}
    with closing(connect(host.database, True)) as conn:
        units = _source_units(conn, report, binding["season_id"])
        mode = conn.execute("""
            SELECT today_native_iso_date,mode_label,league_label FROM game_mode_observations WHERE unit_id=?
        """, (units["game-mode"],)).fetchone()
        if mode is None or tuple(mode) != (plan["stop_exclusive"], "FRANCHISE", "NBA"):
            raise ValueError("FACTOR_POST_CAPTURE_WRONG_NATIVE_DATE_OR_MODE")
        for fixture in plan["games"]:
            try:
                games.append(_game(conn, host, units, binding["season_id"], fixture, headers))
            except ValueError as error:
                rejected[str(fixture["game_id"])] = str(error)
    return {"mode": "LIVE", "worldline_id": binding["worldline_id"], "today": plan["stop_exclusive"],
            "source_unit": units["schedule"], "report_sha256": report_sha256, "games": games, "rejected": rejected}


def _game(conn, host, units, season, fixture, headers):
    unit = units["schedule"]
    native_id = str(fixture["game_id"])
    row = conn.execute("""
        SELECT g.game_id,g.home_team_id,g.away_team_id,h.native_team_id AS home,a.native_team_id AS away,
               x.header_sha256,x.scheduled_native_iso_date AS scheduled,x.played_native_iso_date AS played,x.box_mode
        FROM games g JOIN game_source_checks x USING(game_id)
        JOIN teams h ON h.team_id=g.home_team_id JOIN teams a ON a.team_id=g.away_team_id
        WHERE g.season_id=? AND g.native_game_id=? AND x.unit_id=? AND x.game_type_label='NORMAL'
    """, (season, native_id, unit)).fetchone()
    if (row is None or row["box_mode"] != "FULL_NATIVE_BOX" or row["scheduled"] != fixture["date"]
            or row["played"] != fixture["date"] or int(row["home"]) != fixture["home_team"]
            or int(row["away"]) != fixture["away_team"]):
        raise ValueError("FACTOR_GAME_ID_DATE_OR_BOX_SOURCE_MISMATCH")
    header = headers.get(native_id)
    if header is None or hashlib.sha256(header).hexdigest() != row["header_sha256"]:
        raise ValueError("FACTOR_GAME_HEADER_HASH_MISMATCH")
    integrity = host.verify_game_sql_integrity(row["game_id"], expected_unit_id=unit, native_header=header)
    if not integrity.get("verified_in_db") or integrity["unit_id"] != unit or integrity["team_boxes_count"] != 2:
        raise ValueError("FACTOR_GAME_SQL_READBACK_FAILED")
    boxes = []
    for side in ("home", "away"):
        team = row[f"{side}_team_id"]
        native_team = int(row[side])
        totals = conn.execute("""
            SELECT count(*) n,count(points) known_points,sum(points) points,
                   count(fg_attempted) known_fga,sum(fg_attempted) fga
            FROM player_game_boxes WHERE game_id=? AND team_id=? AND unit_id=?
        """, (row["game_id"], team, unit)).fetchone()
        team_box = conn.execute("SELECT * FROM team_game_boxes WHERE game_id=? AND team_id=? AND unit_id=?",
                                (row["game_id"], team, unit)).fetchone()
        if (totals["n"] < 1 or totals["n"] != totals["known_points"] or totals["n"] != totals["known_fga"]
                or totals["points"] != integrity[f"{side}_points"] or totals["fga"] != team_box["fg_attempted"]):
            raise ValueError("FACTOR_PLAYER_TEAM_BOX_TOTALS_DO_NOT_CONSERVE")
        assigned = fixture[side]
        uid = assigned["uid"] if assigned else None
        candidate = team_box if uid is None else None
        if uid is not None:
            matches = conn.execute("""
                SELECT player_id FROM native_player_sources
                WHERE unit_id=? AND native_unique_id_raw=? AND native_team_id=?
                  AND current_core_roster_status='CURRENT_CORE_ROSTER' AND player_id IS NOT NULL
            """, (units["player-skills"], uid, native_team)).fetchall()
            if len(matches) == 1:
                candidate = conn.execute("""
                    SELECT * FROM player_game_boxes WHERE game_id=? AND unit_id=? AND team_id=? AND player_id=?
                """, (row["game_id"], unit, team, matches[0]["player_id"])).fetchone()
        disposition = "UNOBSERVED"
        metrics = {}
        if candidate is not None and (uid is None or candidate["minutes_raw"] is not None):
            if uid is not None and candidate["minutes_raw"] == 0:
                if candidate["in_use"] == 0 and candidate["fg_attempted"] == 0:
                    disposition = "DNP"
                    metrics = {"MIN": 0, "FGA": 0}
            else:
                disposition = "PLAYED"
                metrics = {key: candidate[column] for key, column in _BOX_METRICS.items()}
                metrics["TEAM_FGA"] = team_box["fg_attempted"]
        boxes.append({"team_id": native_team, "uid": uid, "disposition": disposition, "metrics": metrics})
    return {**fixture, "unit": unit, "team_box_unit": unit, "player_box_unit": unit, "team_boxes": boxes,
            "score_conserved": True, "final": True, "was_simulated": True}

"""Read exact WorldData units for a frozen VAE round; never dispatch a game action."""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sys

from experiment_round import digest

WORLD = Path(__file__).resolve().parents[4] / "08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype"


def require(test, reason):
    if not test:
        raise ValueError(reason)


def read_report(capture_directory, report_sha, host, identity, *, historical):
    path = capture_directory / "refresh-report.json"
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == report_sha, "Post-capture report SHA mismatch")
    report = json.loads(data)
    require(report["status"] == "COMPLETED_REQUESTED_SOURCES" and report["game_writes"] is False
            and report["save_id"] == identity["save"] == host.save_id
            and report["native_save_filename"] == host.loaded_filename
            and report["database_file"] == host.database.name
            and report["binding_sha256"] == host.binding_hash
            and host.binding.get("worldline_id", host.save_id) == identity["worldline"],
            "Post-capture save or worldline binding differs")
    if not historical:
        require("epoch" in identity and report["process_epoch"] == identity["epoch"]
                and host.binding_hash == identity.get("binding_sha256"), "Live epoch or binding differs")
    return report


def exact_units(conn, report, season):
    units = {}
    for family in ("schedule", "game-mode", "player-skills"):
        selected = [row for row in report["sources"] if row["family"] == family]
        require(len(selected) == 1, f"Missing or duplicate post-capture family: {family}")
        row = selected[0]
        require(row["status"] == "ACQUIRED" and row["commit_status"] == "COMMITTED_SUCCESS_VERIFIED",
                f"Source is not a freshly verified acquisition: {family}")
        pinned = row["unit"]
        actual = conn.execute("""
            SELECT u.unit_id,u.payload_sha256,u.unit_status,u.observed_at,u.source_key,r.source_grade,r.season_id
            FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.unit_id=?
        """, (pinned["unit_id"],)).fetchone()
        require(actual is not None and actual["unit_status"] == "success" and actual["source_grade"] == "LIVE_READ"
                and actual["season_id"] == season
                and all(actual[key] == pinned[key] for key in actual.keys()), f"Source unit mismatch: {family}")
        units[family] = pinned["unit_id"]
    return units


def player_opportunity(row):
    # A missing row or ambiguous zero-minute line cannot establish DNP.
    if row is None or not row["in_use"] or row["minutes_raw"] is None or row["minutes_raw"] <= 0:
        return {"disposition": "UNOBSERVED", "minutes": None, "fga": None}
    if row["fg_attempted"] is None:
        return {"disposition": "UNOBSERVED", "minutes": None, "fga": None}
    return {"disposition": "PLAYED", "minutes": row["minutes_raw"], "fga": row["fg_attempted"]}


def game_capture(conn, host, expected, assignments, unit, skills_unit, season, header):
    native = str(expected["game_id"])
    row = conn.execute("""
        SELECT g.game_id,g.home_team_id,g.away_team_id,x.header_sha256,
               h.native_team_id AS home,a.native_team_id AS away,
               x.scheduled_native_iso_date,x.played_native_iso_date,x.box_mode
        FROM games g JOIN game_source_checks x USING(game_id)
        JOIN teams h ON h.team_id=g.home_team_id JOIN teams a ON a.team_id=g.away_team_id
        WHERE g.season_id=? AND g.native_game_id=? AND x.unit_id=? AND x.game_type_label='NORMAL'
    """, (season, native, unit)).fetchone()
    require(row is not None and int(row["home"]) == expected["home"] and int(row["away"]) == expected["away"]
            and row["scheduled_native_iso_date"] == expected["day"]
            and row["played_native_iso_date"] == expected["day"], "Frozen schedule identity differs")
    require(row["box_mode"] == "FULL_NATIVE_BOX", f"Box mode {row['box_mode']}")
    require(header is not None and hashlib.sha256(header).hexdigest() == row["header_sha256"],
            "Archived native header missing or inconsistent")
    game = row["game_id"]
    integrity = host.verify_game_sql_integrity(game, expected_unit_id=unit, native_header=header)
    require(integrity.get("verified_in_db") is True and integrity.get("unit_id") == unit,
            integrity.get("reason", "SQL readback failed"))
    require(integrity["team_boxes_count"] == 2, "Expected exactly two team Boxes")
    teams = []
    for side in ("home", "away"):
        team_id = row[f"{side}_team_id"]
        assigned = assignments[expected[side]]
        totals = conn.execute("""
            SELECT count(*) AS n,count(points) AS known_points,sum(points) AS points, sum(fg_attempted) AS fga,
                   count(fg_attempted) AS known_fga
            FROM player_game_boxes WHERE game_id=? AND unit_id=? AND team_id=?
        """, (game, unit, team_id)).fetchone()
        box = conn.execute("""
            SELECT fg_attempted FROM team_game_boxes WHERE game_id=? AND unit_id=? AND team_id=?
        """, (game, unit, team_id)).fetchone()
        require(totals["n"] > 0 and totals["n"] == totals["known_points"]
                and totals["points"] == integrity[f"{side}_points"], f"Player/team {side} points do not conserve")
        require(totals["n"] == totals["known_fga"] and totals["fga"] == box["fg_attempted"],
                f"Player/team {side} FGA do not conserve")
        matches = conn.execute("""
            SELECT player_id,native_team_id FROM native_player_sources
            WHERE unit_id=? AND native_unique_id_raw=? AND current_core_roster_status='CURRENT_CORE_ROSTER'
        """, (skills_unit, assigned["uid"])).fetchall()
        player = None
        if (len(matches) == 1 and matches[0]["player_id"] is not None
                and matches[0]["native_team_id"] == expected[side]):
            player = conn.execute("""
                SELECT minutes_raw,fg_attempted,in_use FROM player_game_boxes
                WHERE game_id=? AND unit_id=? AND team_id=? AND player_id=?
            """, (game, unit, team_id, matches[0]["player_id"])).fetchone()
        teams.append({"team_id": expected[side], "candidate_uid": assigned["uid"], "team_fga": box["fg_attempted"],
                      **player_opportunity(player)})
    return {**expected, "final": True, "was_simulated": True, "unit": unit,
            "team_box_unit": unit, "player_box_unit": unit, "score_conserved": True, "team_boxes": teams}


def readback(plan, directory, save_directory, slot, report_sha):
    sys.path.insert(0, str(WORLD))
    from calendar_sim_orchestrator import CalendarSimOrchestrator, captured_game_headers
    from engine import connect

    body = {key: value for key, value in plan.items() if key != "research_plan_digest"}
    require(digest(body) == plan["research_plan_digest"], "Plan SHA mismatch")
    scope = plan["evidence_scope"]
    historical = scope == "HISTORICAL_R0_REPLAY_NOT_AUTHORIZED"
    require(historical or scope == "FRESH_WORLDDATA_CANDIDATE_NOT_AUTHORIZED", "Unsupported plan evidence scope")
    expected_ids = [game["game_id"] for game in plan["games"]]
    require(bool(expected_ids) and len(expected_ids) == len(set(expected_ids)), "Missing or duplicate planned Game IDs")
    host = CalendarSimOrchestrator(save_directory, slot)
    identity = plan["identity"]
    report = read_report(directory, report_sha, host, identity, historical=historical)
    headers = captured_game_headers(directory, report)
    assignments = {row["team_id"]: row for row in plan["assignments"]}
    verified, rejected = [], {}
    season = identity["season"]
    with closing(connect(host.database, True)) as conn:
        units = exact_units(conn, report, season)
        mode = conn.execute("""
            SELECT today_native_iso_date,mode_label,league_label FROM game_mode_observations WHERE unit_id=?
        """, (units["game-mode"],)).fetchone()
        require(mode is not None and tuple(mode) == (plan["stop"], "FRANCHISE", "NBA"),
                "Post-capture date or NBA franchise mode differs")
        for game in plan["games"]:
            try:
                verified.append(game_capture(conn, host, game, assignments, units["schedule"],
                                             units["player-skills"], season, headers.get(str(game["game_id"]))))
            except ValueError as error:
                rejected[str(game["game_id"])] = str(error)
    status = "PARTIAL_READBACK_BLOCKS_ANALYSIS" if rejected else "COMPLETE_READBACK"
    audit = {"status": status, "plan_digest": plan["research_plan_digest"], "scope": plan["evidence_scope"],
             "source_report_sha256": report_sha, "units": units, "verified_game_ids": [row["game_id"] for row in verified],
             "rejected_games": rejected, "analysis_status": "WITHHELD"}
    # Historical arms are hypothetical. Live effects also need separate verified Setter readback.
    if not rejected and not historical:
        audit["analysis_status"] = "AWAITING_EXACT_SETTER_RECEIPTS"
    return audit, {"identity": identity, "today": plan["stop"], "games": verified}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("capture_directory", type=Path)
    parser.add_argument("save_directory", type=Path)
    parser.add_argument("slot")
    parser.add_argument("report_sha256")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.plan.read_bytes())
    audit, capture = readback(payload.get("plan", payload), args.capture_directory,
                              args.save_directory, args.slot, args.report_sha256)
    with args.output.open("x", encoding="utf-8", newline="\n") as file:
        json.dump({"audit": audit, "capture": capture}, file, indent=2, ensure_ascii=False)
    print(json.dumps({"status": audit["status"], "verified_games": len(audit["verified_game_ids"]),
                      "rejected_games": len(audit["rejected_games"]), "analysis_status": audit["analysis_status"]}))
    raise SystemExit(2 if audit["rejected_games"] else 0)

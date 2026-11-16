"""Read-only screening after a complete and independently pinned VAE window."""
import argparse
from contextlib import closing
from datetime import datetime
import json
from pathlib import Path
import sys

from experiment_round import analyze, digest
from read_observed_window import WORLD, exact_units, read_report, readback, require
from verify_round_application import pinned_json, read_bundle


def instant(value):
    result = datetime.fromisoformat(value)
    require(result.utcoffset() is not None, "Evidence timestamp lacks timezone")
    return result


def exposure_readback(plan, rows, treatments):
    observed = {(row["team_id"], row["uid"]): row["value"] for row in rows}
    applied = {(row["team_id"], row["uid"]): row["observed_after"] for row in treatments}
    expected = {}
    for row in plan["assignments"]:
        key = (row["team_id"], row["uid"])
        if row["arm"] in {"H", "L"}:
            require(key in applied and applied[key] == row["planned_value"], "Missing exact treatment dose")
            expected[key] = applied[key]
        else:
            require(row["arm"] in {"C", "RESERVE"}, "Unsupported arm")
            expected[key] = row["baseline"]
    require(set(applied) == {(row["team_id"], row["uid"]) for row in plan["assignments"] if row["arm"] in {"H", "L"}},
            "Unexpected treatment outside assigned arms")
    require(len(observed) == len(rows) and len(expected) == len(plan["assignments"]) and observed == expected,
            "Missing, duplicate or drifted pre-window dose")
    return len(expected)


def read_pre_window(plan, directory, save_directory, slot, report_sha, application):
    if str(WORLD) not in sys.path:
        sys.path.insert(0, str(WORLD))
    from calendar_sim_orchestrator import CalendarSimOrchestrator
    from engine import connect

    host = CalendarSimOrchestrator(save_directory, slot)
    identity = plan["identity"]
    report = read_report(directory, report_sha, host, identity, historical=False)
    units_by_family = {row["family"]: row["unit"] for row in report["sources"]
                       if row["family"] in {"game-mode", "schedule", "player-skills"}}
    treatments = application["treatments"]
    capture_first = min(instant(unit["observed_at"]) for unit in units_by_family.values())
    require(capture_first > max(instant(row["read_timestamp"]) for row in treatments),
            "Pre-window acquisition must follow the last S4 Getter")
    with closing(connect(host.database, True)) as conn:
        season = identity["season"]
        units = exact_units(conn, report, season)
        mode = conn.execute("""
            SELECT today_native_iso_date,mode_label,league_label FROM game_mode_observations WHERE unit_id=?
        """, (units["game-mode"],)).fetchone()
        require(mode is not None and tuple(mode) == (plan["start"], "FRANCHISE", "NBA"),
                "Pre-window date or NBA franchise mode differs")
        games = conn.execute("""
            SELECT g.native_game_id, h.native_team_id AS home, a.native_team_id AS away,
                   x.scheduled_native_iso_date AS day, s.status_code, s.is_final, x.played_native_iso_date
            FROM games g JOIN game_source_checks x USING(game_id)
            JOIN game_state_observations s ON s.game_id=x.game_id AND s.unit_id=x.unit_id
            JOIN teams h ON h.team_id=g.home_team_id JOIN teams a ON a.team_id=g.away_team_id
            WHERE g.season_id=? AND x.unit_id=? AND x.game_type_label='NORMAL'
              AND x.scheduled_native_iso_date>=? AND x.scheduled_native_iso_date<?
        """, (season, units["schedule"], plan["start"], plan["stop"])).fetchall()
        expected = {(row["game_id"], row["home"], row["away"], row["day"]) for row in plan["games"]}
        actual = {(int(row["native_game_id"]), int(row["home"]), int(row["away"]), row["day"]) for row in games}
        require(len(actual) == len(games) and actual == expected
                and all(row["status_code"] == "0" and row["is_final"] == 0 and row["played_native_iso_date"] is None
                        for row in games), "Pre-window games differ or have already begun")
        players = []
        for target in plan["assignments"]:
            rows = conn.execute("""
                SELECT n.native_team_id AS team_id,n.native_unique_id_raw AS uid,p.shot_tendency_raw AS value
                FROM native_player_sources n JOIN player_tendency_snapshots p
                  ON p.source_player_id=n.player_source_id AND p.unit_id=n.unit_id
                WHERE n.unit_id=? AND n.native_unique_id_raw=? AND n.player_id IS NOT NULL
                  AND n.current_core_roster_status='CURRENT_CORE_ROSTER'
            """, (units["player-skills"], target["uid"])).fetchall()
            require(len(rows) == 1, "Pre-window roster UID is missing or ambiguous")
            players.append(dict(rows[0]))
    count = exposure_readback(plan, players, treatments)
    return {"verified_players": count, "sources": units, "sha256": report_sha,
            "last_observed_at": max(instant(unit["observed_at"]) for unit in units_by_family.values()).isoformat()}


def screen(plan, directory, pins, save_directory, slot):
    treatment = read_bundle(plan, directory / "s4", pins["treatment_sha256"])
    pre = read_pre_window(plan, directory / "pre", save_directory, slot, pins["pre_sha256"], treatment)
    audit, capture = readback(plan, directory / "post", save_directory, slot, pins["post_sha256"])
    if audit["status"] != "COMPLETE_READBACK":
        return {"status": "STOPPED_PARTIAL_READBACK", "audit": audit}
    post_report = pinned_json(directory / "post/refresh-report.json", pins["post_sha256"])
    require(instant(post_report["started_at"]) > instant(pre["last_observed_at"]),
            "Post-window capture does not follow the pre-window observations")
    result = analyze(plan, capture)
    return {"status": "SCREENING_RECORDED", "plan_digest": plan["research_plan_digest"],
            "evidence_pins": pins, "pre_window": pre, "treatment_digest": digest(treatment), "readback": audit,
            "analysis": result, "scope": "Actual doses observed before window; exposure across the window is unverified"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("private_directory", type=Path)
    parser.add_argument("save_directory", type=Path)
    parser.add_argument("slot")
    parser.add_argument("--treatment-sha256", required=True)
    parser.add_argument("--pre-sha256", required=True)
    parser.add_argument("--post-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.plan.read_bytes())
    pins = {key: getattr(args, key) for key in ("treatment_sha256", "pre_sha256", "post_sha256")}
    result = screen(payload.get("plan", payload), args.private_directory, pins, args.save_directory, args.slot)
    with args.output.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
    print(json.dumps({"status": result["status"]}))
    raise SystemExit(0 if result["status"] == "SCREENING_RECORDED" else 2)

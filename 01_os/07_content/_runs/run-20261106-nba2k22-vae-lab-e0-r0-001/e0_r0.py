"""Read-only E0 analysis over retained WorldData. Outputs belong outside the checkout."""
import argparse
from collections import Counter, defaultdict
from contextlib import closing
from datetime import date, datetime, timedelta
import hashlib
import itertools
import json
from pathlib import Path
import sqlite3
import sys

SEED = "E0-SHOT-TENDENCY-WP-V1-20261106"
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype"))
from competition_views import game_box_snapshot

FAMILIES = {
    "schedule": "BOUND_COMPLETE_DESCRIPTOR_SCHEDULE_AND_PLAYERS",
    "player-skills": "BOUND_PUBLIC_PLAYER_SKILLS",
    "player-state": "BOUND_PLAYER_VITALS_HEALTH_MORALE",
    "lineups": "BOUND_NATIVE_TEAM_LINEUPS_AND_PLAYER_ROTATION",
    "settings": "BOUND_SETTINGS_AND_RULES",
    "game-mode": "BOUND_NATIVE_GAME_MODE_PERIOD",
}


def field_registry():
    engine = ROOT / "08_Domain_Applications/Antigravity_GM_Engine"
    player_ref = "docs/game_mechanics/catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json"
    coach_ref = "research/rea_native_control/data/coach_settings.json"
    player = json.loads((engine / player_ref).read_bytes())
    coach = json.loads((engine / coach_ref).read_bytes())["fields"]
    result = []
    for slot in player["native_slots"]:
        field = slot.get("project_native_name")
        named = slot["project_name_status"] == "NAMED_NATIVE"
        shot = field == "SHOT_TENDENCY"
        result.append({
            "field_id": field if named else "UNNAMED_SLOT_" + slot["offset_hex"],
            "unit": "player", "source": player_ref, "worldline": "WP",
            "action_grade": "LIVE_SETTER_VERIFIED" if shot else "TECHNICALLY_MAPPED_UNVERIFIED" if named else "READ_ONLY",
            "metric": "FGA_PER_36" if shot else "UNKNOWN", "opportunity": "RECENT_AND_SCHEDULED" if shot else "UNKNOWN",
            "confounders": ["position", "minutes", "injury", "rotation", "opponent"] if shot else [],
            "interference": ["teammates", "opponents"], "allowed_doses": [-5, 0, 5] if shot else [],
            "dose_status": "PROPOSED_NOT_AUTHORIZED" if shot else "NO_DOSE_AUTHORIZED",
            "power_grade": "UNDERPOWERED_SCREEN_ONLY" if shot else "UNTESTED",
        })
    for field, definition in sorted(coach.items()):
        result.append({"field_id": field, "unit": "team", "source": coach_ref, "worldline": "WC",
                       "action_grade": "TECHNICALLY_MAPPED_UNVERIFIED", "metric": "UNKNOWN",
                       "opportunity": "UNKNOWN", "confounders": [], "interference": ["team", "opponents"],
                       "allowed_doses": [], "power_grade": "UNTESTED",
                       "native_representation": "ENUM" if "enum" in definition else "RAW"})
    return result


def encode(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def fingerprint(data):
    return hashlib.sha256(encode(data).encode()).hexdigest()


def file_identity(path):
    stat = path.stat()
    if not stat.st_ino:
        raise ValueError("Filesystem cannot verify a distinct file identity")
    return fingerprint([stat.st_dev, stat.st_ino])


def file_sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def binding_worldline(binding):
    # Standalone WorldData binds one save ID to one database without a Host worldline.
    return binding.get("worldline_id", binding["save_id"])


def control_start(manifest, inventory, binding, db_path):
    game_ids = sorted(str(row["native_game_id"]) for row in inventory["fixtures"])
    if not game_ids or len(set(game_ids)) != len(game_ids):
        raise ValueError("Control start requires a nonempty unique Native schedule")
    return {
        "worldline": binding_worldline(binding), "save_identity": binding["native_save_filename"],
        "db_identity": file_identity(db_path), "mode": inventory["sim_mode"],
        "initial_state_sha256": manifest["observable_start_fingerprint"],
        "pre_capture_observed_at": manifest["units"]["schedule"]["observed_at"],
        "start_source_report_sha256": manifest["source_report_sha256"],
        "window_start": manifest["window_start"], "window_end_exclusive": manifest["window_end_exclusive"],
        "expected_native_game_ids": game_ids,
    }


def freeze_controls(left, right, left_save, right_save, *, source=None, origin_sha256=None):
    """Bind two independently captured starts to a verified common disk image."""
    common = ("initial_state_sha256", "mode", "window_start", "window_end_exclusive", "expected_native_game_ids")
    distinct = ("worldline", "save_identity", "db_identity", "start_source_report_sha256")
    if (any(not left.get(k) or left[k] != right.get(k) for k in common)
            or any(not left.get(k) or not right.get(k) or left[k] == right[k] for k in distinct)
            or left["mode"] != "CALENDAR_SIM_ONLY"
            or date.fromisoformat(left["window_end_exclusive"]) - date.fromisoformat(left["window_start"])
            != timedelta(days=7)):
        raise ValueError("W0 captures do not show the same start in separate saves and databases")
    if (left_save.name.casefold(), right_save.name.casefold()) != (
        left["save_identity"].casefold(), right["save_identity"].casefold()
    ):
        raise ValueError("Disk slot names differ from the observed save bindings")
    if (source is None) == (origin_sha256 is None):
        raise ValueError("Supply either a preserved source file or a previously recorded origin digest")
    paths = (left_save, right_save) if source is None else (source, left_save, right_save)
    if len({file_identity(path) for path in paths}) != len(paths):
        raise ValueError("W0 source and copies must be separate disk files")
    origin = file_sha256(source) if source is not None else origin_sha256
    if any(file_sha256(path) != origin for path in (left_save, right_save)):
        raise ValueError("W0 copies do not match the frozen origin bytes")
    return [dict(row, frozen_origin_sha256=origin) for row in (left, right)]


def bound_units(conn, report, binding, binding_bytes):
    if (report["status"] != "COMPLETED_REQUESTED_SOURCES" or report.get("game_writes") is not False
            or report["save_id"] != binding["save_id"] or report["database_file"] != binding.get("database_file", "world.sqlite")
            or report["native_save_filename"] != binding["native_save_filename"]
            or hashlib.sha256(binding_bytes).hexdigest() != report["binding_sha256"]):
        raise ValueError("Refresh evidence does not bind the requested no-write database")
    rows = [r for r in report["sources"] if r["family"] in FAMILIES]
    if sorted(r["family"] for r in rows) != sorted(FAMILIES):
        raise ValueError("Missing or duplicate source family")
    units = {}
    for row in rows:
        family, expected = row["family"], row["unit"]
        if row["commit_status"] != "COMMITTED_SUCCESS_VERIFIED" or row["status"] != "ACQUIRED":
            raise ValueError(f"Source not freshly acquired for the bound batch: {family}")
        actual = conn.execute("""
            SELECT u.unit_id,u.source_key,u.payload_sha256,u.unit_status,u.observed_at,r.season_id,r.source_grade
            FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.unit_id=?
        """, (expected["unit_id"],)).fetchone()
        if (not actual or any(actual[key] != expected[key] for key in actual.keys())
                or actual["source_key"] != FAMILIES[family]
                or actual["unit_status"] != "success" or actual["source_grade"] != "LIVE_READ"):
            raise ValueError(f"Unverified exact SQL capture unit: {family}")
        units[family] = dict(actual)
    if len({u["season_id"] for u in units.values()}) != 1:
        raise ValueError("Cross-season capture evidence")
    return units


def opportunity(fga, minutes):
    if fga is None or minutes is None:
        return "NOT_OBSERVED", None
    if minutes == 0:
        return "DNP_OR_ZERO_RECORDED_MINUTES" if fga == 0 else "INCONSISTENT_ZERO_MINUTES", None
    if minutes < 0 or fga < 0:
        return "INCONSISTENT_BOX", None
    return "OBSERVED", 36 * fga / minutes


def assign(pool, fixtures, seed=SEED):
    strata = defaultdict(list)
    for row in pool:
        if row["eligible"] and 5 <= row["shot_tendency"] <= 95:
            strata[(row["position"], int(row["mean_minutes"] // 6))].append(row)
    choices = []
    for stratum, group in strata.items():
        # One representative per team in a stratum, chosen reproducibly before treatment assignment.
        reps = {}
        for row in sorted(group, key=lambda x: fingerprint([seed, "representative", x["uid"]])):
            reps.setdefault(row["team"], row)
        for triplet in itertools.combinations(reps.values(), 3):
            ids = sorted(row["uid"] for row in triplet)
            shot_gap = max(row["shot_tendency"] for row in triplet) - min(row["shot_tendency"] for row in triplet)
            minutes_gap = max(row["mean_minutes"] for row in triplet) - min(row["mean_minutes"] for row in triplet)
            if shot_gap <= 10 and minutes_gap <= 6:
                choices.append((shot_gap, minutes_gap, fingerprint([seed, "triplet", ids]), stratum, triplet))
    if not choices:
        return {"status": "INSUFFICIENT_MATCHED_OPPORTUNITY", "seed": seed, "targets": []}
    _, _, _, stratum, triple = min(choices, key=lambda x: x[:3])
    ranked = sorted(triple, key=lambda row: fingerprint([seed, "assign", row["uid"]]))
    targets = [dict(uid=row["uid"], team=row["team"], arm=arm, baseline=row["shot_tendency"],
                    proposed_value=row["shot_tendency"] + delta, position=row["position"],
                    opportunity_games=row["next_games"], mean_minutes=row["mean_minutes"])
               for row, (arm, delta) in zip(ranked, (("H", 5), ("L", -5), ("C", 0)))]
    arms = {row["team"]: row["arm"] for row in targets}
    exposures = [{"game_id": g["game_id"], "date": g["scheduled_date"], "home_arm": arms.get(g["home"], "UNASSIGNED"),
                  "away_arm": arms.get(g["away"], "UNASSIGNED"),
                  "direct_treatment_opponent": arms.get(g["home"]) in ("H", "L") or arms.get(g["away"]) in ("H", "L")}
                 for g in fixtures if g["home"] in arms or g["away"] in arms]
    return {"status": "HISTORICAL_PROPOSAL_ONLY_NO_SEAL", "seed": seed, "stratum": stratum,
            "targets": targets, "opponent_exposures": exposures, "power_grade": "UNDERPOWERED_SCREEN_ONLY"}


def compare_controls(left, right):
    required = ("frozen_origin_sha256", "initial_state_sha256", "mode", "window_start",
                "window_end_exclusive", "expected_native_game_ids")
    if (any(not left.get(k) or left.get(k) != right.get(k) for k in required)
            or any(not row.get("worldline") or not row.get("save_identity") or not row.get("db_identity")
                   or row.get("no_intervention") is not True for row in (left, right))
            or any(left[k] == right[k] for k in ("worldline", "save_identity", "db_identity"))):
        raise ValueError("Controls must be isolated copies of the same verified no-write start")
    if (left["mode"] != "CALENDAR_SIM_ONLY"
            or date.fromisoformat(left["window_end_exclusive"]) - date.fromisoformat(left["window_start"])
            != timedelta(days=7)):
        raise ValueError("Controls require a seven-day calendar window")
    def results(row):
        values = {}
        for game in row["games"]:
            gid = game["native_game_id"]
            if gid in values or game["simulation_mode"] != "CALENDAR_SIM_ONLY":
                raise ValueError("Duplicate or wrong-mode game")
            if not row["window_start"] <= game["played_date"] < row["window_end_exclusive"]:
                raise ValueError("Game outside the frozen window")
            qualified = all(type(game[k]) is int and game[k] >= 0 for k in ("home_points", "away_points"))
            unavailable = (game.get("score_status") == "NO_COMPLETE_QUALIFIED_SCORE"
                           and game["home_points"] is None and game["away_points"] is None
                           and bool(game.get("native_box_sha256")))
            if ((not qualified and not unavailable)
                    or len(game["player_box_sha256"]) != 64
                    or any(c not in "0123456789abcdef" for c in game["player_box_sha256"])):
                raise ValueError("Incomplete score or player-box evidence")
            native_hash = game.get("native_box_sha256", game["player_box_sha256"])
            if len(native_hash) != 64 or any(c not in "0123456789abcdef" for c in native_hash):
                raise ValueError("Invalid Native box fingerprint")
            values[gid] = (game["home_points"], game["away_points"], game["player_box_sha256"],
                           game["played_date"], native_hash, qualified)
        return values
    a, b = results(left), results(right)
    expected = set(left["expected_native_game_ids"])
    if not a or len(expected) != len(left["expected_native_game_ids"]) or set(a) != expected or set(b) != expected:
        raise ValueError("Exact completed game coverage differs; calibration not comparable")
    qualified = [k for k in a if a[k][5] and b[k][5]]
    score_diff = sum(a[k][:2] != b[k][:2] for k in qualified)
    box_diff = sum(a[k][2] != b[k][2] for k in a)
    date_diff = sum(a[k][3] != b[k][3] for k in a)
    native_diff = sum(a[k][4] != b[k][4] for k in a)
    return {"paired_games": len(a), "score_differences": score_diff, "player_box_differences": box_diff,
            "paired_qualified_scores": len(qualified), "unqualified_score_games": len(a) - len(qualified),
            "native_box_differences": native_diff,
            "score_calibration_status": "COMPLETE" if len(qualified) == len(a) else "INCOMPLETE_CANONICAL_COVERAGE",
            "qualified_score_difference_summary": {
                "mean_absolute_home_points": sum(abs(a[k][0] - b[k][0]) for k in qualified) / len(qualified) if qualified else None,
                "mean_absolute_away_points": sum(abs(a[k][1] - b[k][1]) for k in qualified) / len(qualified) if qualified else None,
                "winner_disagreements": sum((a[k][0] > a[k][1]) != (b[k][0] > b[k][1]) for k in qualified),
                "scope": "Descriptive paired games from two worldlines; no independent-game power estimate",
            },
            "played_date_differences": date_diff,
            "interpretation": "VARIATION_OBSERVED" if score_diff or box_diff or native_diff or date_diff else "MATCHED_THIS_PAIR_ONLY",
            "control_repeats": 2, "suggested_repeats_if_variable": 4}


def control_games(conn, season, schedule_unit, start, end, db_path):
    """Project verified full boxes from the exact post-window capture unit."""
    results = []
    for game in conn.execute("""
        SELECT g.game_id,g.native_game_id,g.home_team_id,g.away_team_id,
               x.played_native_iso_date AS played_date,s.home_points,s.away_points
        FROM game_source_checks x JOIN games g USING(game_id)
        JOIN game_state_observations s ON s.game_id=x.game_id AND s.unit_id=x.unit_id
        WHERE x.unit_id=? AND g.season_id=? AND x.game_type_label='NORMAL'
          AND x.box_mode='FULL_NATIVE_BOX' AND s.is_final=1 AND s.was_simulated=1
          AND x.played_native_iso_date>=? AND x.played_native_iso_date<?
        ORDER BY g.native_game_id
    """, (schedule_unit, season, start, end)):
        boxes = [dict(row) for row in conn.execute("""
            SELECT player_id,team_id,points,fg_made,fg_attempted,three_made,three_attempted,
                   ft_made,ft_attempted,offensive_rebounds,defensive_rebounds,assists,
                   steals,blocks,turnovers,fouls,minutes_raw
            FROM player_game_boxes WHERE game_id=? AND unit_id=? ORDER BY player_id
        """, (game["game_id"], schedule_unit))]
        teams = {game["home_team_id"], game["away_team_id"]}
        team_scores = {row["team_id"]: row["points"] for row in conn.execute("""
            SELECT team_id,points FROM team_game_boxes WHERE game_id=? AND unit_id=?
        """, (game["game_id"], schedule_unit))}
        snapshot = game_box_snapshot(db_path, game["game_id"], unit_id=schedule_unit)
        scores = snapshot["scores"]
        native = [dict(row) for row in conn.execute("""
            SELECT side,native_player_id,native_team_id,in_use,points,fg_made,fg_attempted,
                   three_made,three_attempted,ft_made,ft_attempted,offensive_rebounds,
                   defensive_rebounds,assists,steals,blocks,turnovers,fouls,minutes_raw
            FROM native_box_observations WHERE game_id=? AND unit_id=?
            ORDER BY side,native_player_id,row_index
        """, (game["game_id"], schedule_unit))]
        expected_scores = {game["home_team_id"]: scores["captured_native_points"]["HOME"],
                           game["away_team_id"]: scores["captured_native_points"]["AWAY"]}
        if ({r["team_id"] for r in boxes} != teams or not all(r["player_id"] for r in boxes)
                or len({r["player_id"] for r in boxes}) != len(boxes)
                or {r["side"] for r in native} != {"HOME", "AWAY"}
                or any(value is None for value in expected_scores.values())
                or team_scores != expected_scores):
            raise ValueError("Missing, duplicate or inconsistent exact-unit boxes")
        results.append({
            "native_game_id": str(game["native_game_id"]), "played_date": game["played_date"],
            "home_points": scores["home_points"], "away_points": scores["away_points"],
            "score_status": scores["value_status"],
            "canonical_coverage": {side: row["status"] for side, row in snapshot["coverage"].items()},
            "native_box_sha256": fingerprint(native),
            "player_box_sha256": fingerprint(boxes), "simulation_mode": "CALENDAR_SIM_ONLY",
        })
    return results


def control_result(conn, manifest, inventory, binding, db_path, anchor):
    start, end = anchor["window_start"], anchor["window_end_exclusive"]
    if (anchor["no_intervention"] is not True
            or anchor["worldline"] != binding_worldline(binding)
            or anchor["save_identity"] != binding["native_save_filename"]
            or anchor["db_identity"] != file_identity(db_path)
            or manifest["window_start"] != end
            or date.fromisoformat(end) - date.fromisoformat(start) != timedelta(days=7)
            or inventory["sim_mode"] != "CALENDAR_SIM_ONLY"):
        raise ValueError("Post-capture save, worldline, no-write declaration or stop date differs from frozen control")
    schedule = manifest["units"]["schedule"]
    post_observed_at = datetime.fromisoformat(schedule["observed_at"])
    pre_observed_at = datetime.fromisoformat(anchor["pre_capture_observed_at"])
    if (post_observed_at.utcoffset() is None or pre_observed_at.utcoffset() is None
            or post_observed_at <= pre_observed_at):
        raise ValueError("Post-window schedule unit must be newer than the frozen baseline")
    games = control_games(conn, schedule["season_id"], schedule["unit_id"], start, end, db_path)
    expected = anchor["expected_native_game_ids"]
    if not expected or sorted(r["native_game_id"] for r in games) != sorted(expected):
        raise ValueError("Post-capture full boxes do not cover the frozen game IDs")
    return {**anchor, "mode": "CALENDAR_SIM_ONLY", "schedule_unit": schedule["unit_id"],
            "source_report_sha256": manifest["source_report_sha256"], "games": games}


def build(conn, report, binding, binding_bytes):
    units = bound_units(conn, report, binding, binding_bytes)
    ids = {k: v["unit_id"] for k, v in units.items()}
    season = units["schedule"]["season_id"]
    save = conn.execute("SELECT save_id,schema_version FROM saves").fetchall()
    if len(save) != 1 or save[0]["save_id"] != binding["save_id"] or save[0]["schema_version"] != 24:
        raise ValueError("Unexpected WorldData save or schema")
    mode = conn.execute("""
        SELECT mode_label,league_label,period_label,today_native_iso_date
        FROM game_mode_observations WHERE unit_id=?
    """, (ids["game-mode"],)).fetchone()
    if not mode or (mode["mode_label"], mode["league_label"]) != ("FRANCHISE", "NBA"):
        raise ValueError("Only observed NBA Franchise data qualifies")
    today = date.fromisoformat(mode["today_native_iso_date"])
    recent = (today - timedelta(days=21)).isoformat()
    end = (today + timedelta(days=7)).isoformat()
    fixtures = [dict(r) for r in conn.execute("""
        SELECT g.game_id,g.native_game_id,x.scheduled_native_iso_date AS scheduled_date,
               home.native_team_id AS home,away.native_team_id AS away
        FROM game_source_checks x JOIN games g USING(game_id)
        JOIN teams home ON home.team_id=g.home_team_id JOIN teams away ON away.team_id=g.away_team_id
        JOIN game_state_observations s ON s.game_id=x.game_id AND s.unit_id=x.unit_id
        WHERE x.unit_id=? AND g.season_id=? AND x.game_type_label='NORMAL' AND s.is_final=0
          AND x.scheduled_native_iso_date>=? AND x.scheduled_native_iso_date<?
        ORDER BY scheduled_date,g.game_id
    """, (ids["schedule"], season, today.isoformat(), end))]
    for row in fixtures:
        row["home"], row["away"] = int(row["home"]), int(row["away"])
    if len({g["game_id"] for g in fixtures}) != len(fixtures):
        raise ValueError("Duplicate scheduled game")
    game_cte = """
        WITH latest_full AS (
          SELECT g.game_id,x.unit_id,x.played_native_iso_date AS played_date,
                 ROW_NUMBER() OVER(PARTITION BY g.game_id ORDER BY u.observed_at DESC,x.unit_id DESC) AS rn
          FROM games g JOIN game_source_checks x USING(game_id)
          JOIN game_state_observations s ON s.game_id=x.game_id AND s.unit_id=x.unit_id
          JOIN capture_units u ON u.unit_id=x.unit_id JOIN capture_runs cr ON cr.run_id=u.run_id
          WHERE g.season_id=? AND u.source_key='BOUND_COMPLETE_DESCRIPTOR_SCHEDULE_AND_PLAYERS'
            AND u.observed_at<=? AND u.unit_status='success' AND cr.source_grade='LIVE_READ'
            AND x.game_type_label='NORMAL' AND x.box_mode='FULL_NATIVE_BOX'
            AND s.is_final=1 AND s.was_simulated=1 AND x.played_native_iso_date<?
        )
    """
    game_args = (season, units["schedule"]["observed_at"], today.isoformat())
    total_final = conn.execute(game_cte + " SELECT count(*) FROM latest_full WHERE rn=1", game_args).fetchone()[0]
    team_box_counts = Counter()
    for row in conn.execute(game_cte + """
        SELECT b.game_id,b.team_id,b.fg_attempted FROM latest_full g JOIN team_game_boxes b
          ON b.game_id=g.game_id AND b.unit_id=g.unit_id WHERE g.rn=1
    """, game_args):
        if row["fg_attempted"] is not None:
            team_box_counts[(row["game_id"], row["team_id"])] = row["fg_attempted"]
    history = defaultdict(list)
    statuses = Counter()
    sharing = 0
    for r in conn.execute(game_cte + """
        SELECT b.player_id,b.team_id,b.game_id,b.fg_attempted,b.minutes_raw,g.played_date
        FROM latest_full g JOIN player_game_boxes b ON b.game_id=g.game_id AND b.unit_id=g.unit_id
        WHERE g.rn=1 ORDER BY b.game_id,b.player_id
    """, game_args):
        status, rate = opportunity(r["fg_attempted"], r["minutes_raw"])
        statuses[status] += 1
        if rate is None:
            continue
        team_fga = team_box_counts.get((r["game_id"], r["team_id"]))
        sharing += int(team_fga is not None and team_fga > 0 and r["fg_attempted"] <= team_fga)
        if r["played_date"] >= recent:
            history[(r["player_id"], r["team_id"])].append(r["minutes_raw"])

    roster_rows = conn.execute("""
        SELECT n.native_unique_id_raw AS uid,n.native_team_id AS team,n.current_roster_slot AS slot,
               n.player_id,n.canonical_link_status,t.team_id,p.shot_tendency_raw AS shot_tendency,
               v.primary_position AS position,h.injury1_status_label AS injury1,
               h.injury2_status_label AS injury2, rot.playing_time_raw AS rotation_raw
        FROM native_player_sources n LEFT JOIN teams t ON CAST(t.native_team_id AS INTEGER)=n.native_team_id
        LEFT JOIN player_tendency_snapshots p ON p.source_player_id=n.player_source_id AND p.unit_id=n.unit_id
        LEFT JOIN player_vitals_observations v ON v.player_id=n.player_id AND v.unit_id=?
        LEFT JOIN player_health_observations h ON h.player_id=n.player_id AND h.unit_id=?
        LEFT JOIN native_player_rotation_observations rot ON rot.player_id=n.player_id AND rot.unit_id=?
        WHERE n.unit_id=? AND n.current_core_roster_status='CURRENT_CORE_ROSTER'
        ORDER BY n.native_team_id,n.native_unique_id_raw
    """, (ids["player-state"], ids["player-state"], ids["lineups"], ids["player-skills"])).fetchall()
    uid_count = Counter(r[0] for r in conn.execute(
        "SELECT native_unique_id_raw FROM native_player_sources WHERE unit_id=?", (ids["player-skills"],)
    ))
    next_by_team = Counter(t for g in fixtures for t in (g["home"], g["away"]))
    pool, exclusions = [], Counter()
    for raw in roster_rows:
        row = dict(raw)
        minutes = history[(row["player_id"], row["team_id"])]
        reasons = []
        if not row["player_id"] or uid_count[row["uid"]] != 1 or row["uid"] <= 0 or row["team_id"] is None:
            reasons.append("IDENTITY_WITHHELD")
        if row["slot"] is None or not 0 <= row["slot"] < 15:
            reasons.append("WRITER_ROSTER_SLOT_UNVERIFIED")
        if row["position"] not in ("POINT_GUARD", "SHOOTING_GUARD", "SMALL_FORWARD", "POWER_FORWARD", "CENTER"):
            reasons.append("POSITION_UNKNOWN")
        if (row["injury1"], row["injury2"]) != ("HEALTHY", "HEALTHY"):
            reasons.append("HEALTH_NOT_CONFIRMED")
        if row["shot_tendency"] is None or not 0 <= row["shot_tendency"] <= 100:
            reasons.append("SHOT_TENDENCY_NOT_OBSERVED")
        if sum(m >= 10 for m in minutes) < 3:
            reasons.append("RECENT_OPPORTUNITY_INSUFFICIENT")
        if next_by_team[row["team"]] < 2:
            reasons.append("SCHEDULE_OPPORTUNITY_INSUFFICIENT")
        row.update(eligible=not reasons, exclusions=reasons, recent_observed_games=len(minutes),
                   recent_games_10min=sum(m >= 10 for m in minutes),
                   mean_minutes=round(sum(minutes) / len(minutes), 4) if minutes else None,
                   next_games=next_by_team[row["team"]])
        exclusions.update(reasons)
        pool.append(row)
    if len({(r["team"], r["uid"]) for r in pool}) != len(pool):
        raise ValueError("Nonunique roster row after exact-unit join")
    # Unit-level sources and completeness are retained independently. This is not a new atomic game capture.
    counts = {"team_count": len({r["team"] for r in pool}), "roster_players": len(pool),
              "unique_native_uids": len({r["uid"] for r in pool}), "eligible": sum(r["eligible"] for r in pool),
              "eligible_teams": len({r["team"] for r in pool if r["eligible"]}),
              "historical_final_games": total_final, "scheduled_games_7d": len(fixtures),
              "shot_tendency_observed": sum(r["shot_tendency"] is not None for r in pool),
              "rotation_observed": sum(r["rotation_raw"] is not None for r in pool),
              "player_boxes_by_opportunity": statuses, "same_game_unit_team_shot_share_available": sharing,
              "exclusions_nonexclusive": exclusions}
    manifest = {"status": "HISTORICAL_BASELINE_NOT_CURRENT_W0", "save_id": binding["save_id"],
                "worldline": binding_worldline(binding), "batch_id": report["batch_id"],
                "basis": "retained no-write WorldData; current S4 process cannot stand in for pristine W0",
                "window_start": today.isoformat(), "window_end_exclusive": end,
                "units": units, "counts": counts, "R0_completed_repeats": 0, "worldline_independence": "NOT_VERIFIED"}
    settings = [tuple(r) for r in conn.execute("""
        SELECT field_id,scope_code,raw_word_u32,value_status FROM game_setting_observations
        WHERE unit_id=? ORDER BY field_id,scope_code,raw_word_u32,value_status
    """, (ids["settings"],))]
    if not settings:
        raise ValueError("No exact-unit settings observations")
    manifest["observable_start_fingerprint"] = fingerprint({
        "mode": dict(mode), "settings": settings, "fixtures": fixtures, "historical_final_games": total_final,
        "roster": [{k: row[k] for k in ("uid", "team", "slot", "position", "shot_tendency", "rotation_raw",
                                      "injury1", "injury2")} for row in pool],
    })
    manifest["observable_start_fingerprint_scope"] = "Observed anchors only; not proof of a pristine save or independent copies"
    groups = defaultdict(list)
    for r in pool:
        groups[r["team"]].append(r["uid"])
    inventory = {"metrics": counts, "sim_mode": "CALENDAR_SIM_ONLY", "native_mode": dict(mode),
                 "fixtures": fixtures, "teammates": dict(groups), "coach_to_team_rule": "one coach context per team cluster",
                 "field_scope": {"shot_tendency": "LIVE_SETTER_VERIFIED_HISTORICAL_ONLY",
                                 "other_slots": "READ_ONLY_OR_UNTESTED", "touches": "UNOBSERVED"}}
    return manifest, pool, inventory, assign(pool, fixtures)


def main():
    if sys.argv[1:2] == ["freeze-controls"]:
        parser = argparse.ArgumentParser(description="Verify and freeze two private W0 start captures")
        for name in ("left", "right", "left_save", "right_save", "output"):
            parser.add_argument(name, type=Path)
        origin = parser.add_mutually_exclusive_group(required=True)
        origin.add_argument("--source", type=Path, help="Preserved original disk image")
        origin.add_argument("--origin-sha256", help="Common digest recorded before either simulation")
        args = parser.parse_args(sys.argv[2:])
        out = args.output.resolve()
        if out.is_relative_to(ROOT) or out.exists():
            parser.error("Output must be a new private directory outside the checkout")
        anchors = freeze_controls(json.loads(args.left.read_bytes()), json.loads(args.right.read_bytes()),
                                  args.left_save, args.right_save, source=args.source,
                                  origin_sha256=args.origin_sha256)
        out.mkdir()
        for name, anchor in zip(("W0-A", "W0-B"), anchors):
            (out / f"{name}.json").write_bytes((encode(anchor) + "\n").encode())
        print(encode({"window_start": anchors[0]["window_start"],
                      "window_end_exclusive": anchors[0]["window_end_exclusive"],
                      "scheduled_games": len(anchors[0]["expected_native_game_ids"])}))
        return
    if sys.argv[1:2] == ["compare"]:
        parser = argparse.ArgumentParser(description="Compare two private, verified R0 control results")
        parser.add_argument("left", type=Path)
        parser.add_argument("right", type=Path)
        args = parser.parse_args(sys.argv[2:])
        print(encode(compare_controls(json.loads(args.left.read_bytes()), json.loads(args.right.read_bytes()))))
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--report-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    controls = parser.add_mutually_exclusive_group()
    controls.add_argument("--control-preflight", action="store_true", help="Export a bound W0 pre-simulation start")
    controls.add_argument("--control-start", type=Path, help="Verified private W0 start anchor for a post-window capture")
    args = parser.parse_args()
    out = args.output.resolve()
    if out.is_relative_to(ROOT) or out.exists():
        parser.error("Output must be a new private directory outside the checkout")
    raw_report, raw_binding = args.report.read_bytes(), args.binding.read_bytes()
    if hashlib.sha256(raw_report).hexdigest() != args.report_sha256:
        parser.error("Report hash mismatch")
    binding = json.loads(raw_binding)
    if args.database.resolve() != (args.binding.resolve().parent / binding.get("database_file", "world.sqlite")).resolve():
        parser.error("Database path differs from the binding")
    with closing(sqlite3.connect(args.database.resolve().as_uri() + "?mode=ro", uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("BEGIN")
        manifest, pool, inventory, assignment = build(conn, json.loads(raw_report), binding, raw_binding)
        manifest["source_report_sha256"] = args.report_sha256
        if args.control_preflight:
            manifest["status"] = "W0_START_CAPTURE_AWAITING_PAIR_VERIFICATION"
            manifest["basis"] = "Fresh bound no-write capture; identical-start pair verification pending"
            assignment["status"] = "W0_CANDIDATE_ONLY_PAIR_NOT_VERIFIED_NO_SEAL"
        elif args.control_start:
            manifest["status"] = "W0_POST_WINDOW_CAPTURE"
            manifest["basis"] = "Actual no-write post-window capture; frozen eligibility remains at the pre-simulation start"
            assignment["status"] = "POST_WINDOW_EXPLORATORY_ONLY_NOT_FROZEN_WP"
        control = (control_result(conn, manifest, inventory, binding, args.database,
                                  json.loads(args.control_start.read_bytes()))
                   if args.control_start else None)
    data = {"eligibility_pool.jsonl": "".join(encode(r) + "\n" for r in pool),
            "observation_inventory.json": encode(inventory) + "\n",
            "WP_candidate_assignment.json": encode(assignment) + "\n",
            "experiment_field_registry.json": encode(field_registry()) + "\n"}
    if control:
        data["R0_control_result.json"] = encode(control) + "\n"
    if args.control_preflight:
        data["R0_start_capture.json"] = encode(control_start(manifest, inventory, binding, args.database)) + "\n"
    manifest["artifact_sha256"] = {name: hashlib.sha256(body.encode()).hexdigest() for name, body in data.items()}
    data["R0_baseline_manifest.json"] = encode(manifest) + "\n"
    out.mkdir()
    for name, body in data.items():
        (out / name).write_bytes(body.encode())
    print(encode({"counts": manifest["counts"], "assignment": assignment["status"],
                  "assigned_arms": [r["arm"] for r in assignment["targets"]], "window_start": manifest["window_start"],
                  "window_end_exclusive": manifest["window_end_exclusive"]}))


if __name__ == "__main__":
    main()

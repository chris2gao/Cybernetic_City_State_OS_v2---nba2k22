"""Build a private, reproducible round from the existing R0/WorldData export."""
import argparse
from collections import defaultdict
from contextlib import closing
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import sqlite3
from statistics import mean, pstdev

from experiment_round import plan

FEATURES = ("team_margin", "minutes", "fga", "shot_tendency", "opponent_margin", "scheduled_games")
SOURCE_FILES = ("R0_baseline_manifest.json", "observation_inventory.json", "eligibility_pool.jsonl")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_features(database, manifest, games, candidates, *, minimum_opportunities=2):
    """Use only same-unit finals from the already verified R0 schedule source."""
    schedule = manifest["units"]["schedule"]
    start = manifest["window_start"]
    recent = (date.fromisoformat(start) - timedelta(days=21)).isoformat()
    margins, minutes, attempts = defaultdict(list), defaultdict(list), defaultdict(list)
    with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        save_ids = conn.execute("SELECT save_id FROM saves").fetchall()
        if [row[0] for row in save_ids] != [manifest["save_id"]]:
            raise ValueError("WorldData database does not match the retained R0 export")
        for family, unit in manifest["units"].items():
            actual = conn.execute("""
                SELECT u.payload_sha256,u.observed_at,u.unit_status,u.source_key,r.source_grade,r.season_id
                FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.unit_id=?
            """, (unit["unit_id"],)).fetchone()
            if actual is None or any(actual[key] != unit[key] for key in actual.keys()):
                raise ValueError(f"WorldData source unit differs from R0 export: {family}")
        base = """
            WITH full_games AS (
                SELECT g.game_id, g.home_team_id, g.away_team_id, x.unit_id,
                       ROW_NUMBER() OVER(PARTITION BY g.game_id ORDER BY u.observed_at DESC,x.unit_id DESC) AS rank
                FROM games g JOIN game_source_checks x USING(game_id)
                JOIN game_state_observations s ON s.game_id=g.game_id AND s.unit_id=x.unit_id
                JOIN capture_units u ON u.unit_id=x.unit_id JOIN capture_runs cr ON cr.run_id=u.run_id
                WHERE g.season_id=? AND u.source_key='BOUND_COMPLETE_DESCRIPTOR_SCHEDULE_AND_PLAYERS'
                  AND u.observed_at<=? AND u.unit_status='success' AND cr.source_grade='LIVE_READ'
                  AND x.game_type_label='NORMAL' AND x.box_mode='FULL_NATIVE_BOX'
                  AND s.is_final=1 AND s.was_simulated=1
                  AND x.played_native_iso_date>=? AND x.played_native_iso_date<?
            )
        """
        bounds = (schedule["season_id"], schedule["observed_at"], recent, start)
        for row in conn.execute(base + """
            SELECT g.home_team_id,g.away_team_id,h.points AS home_points,a.points AS away_points
            FROM full_games g
            JOIN team_game_boxes h ON h.game_id=g.game_id AND h.unit_id=g.unit_id AND h.team_id=g.home_team_id
            JOIN team_game_boxes a ON a.game_id=g.game_id AND a.unit_id=g.unit_id AND a.team_id=g.away_team_id
            WHERE g.rank=1 AND h.points IS NOT NULL AND a.points IS NOT NULL
        """, bounds):
            gap = row["home_points"] - row["away_points"]
            margins[row["home_team_id"]].append(gap)
            margins[row["away_team_id"]].append(-gap)
        for row in conn.execute(base + """
            SELECT b.player_id,b.team_id,b.minutes_raw,b.fg_attempted FROM full_games g
            JOIN player_game_boxes b ON b.game_id=g.game_id AND b.unit_id=g.unit_id
            WHERE g.rank=1 AND b.minutes_raw>=10 AND b.fg_attempted IS NOT NULL
        """, bounds):
            key = (row["player_id"], row["team_id"])
            minutes[key].append(row["minutes_raw"])
            attempts[key].append(row["fg_attempted"])

    strengths = {team: mean(margins[row["team_id"]]) for team, row in candidates.items() if margins[row["team_id"]]}
    if set(strengths) != set(candidates):
        raise ValueError(f"Missing same-unit team strength for {len(candidates) - len(strengths)} teams")
    opponents = defaultdict(list)
    for game in games:
        opponents[game["home"]].append(game["away"])
        opponents[game["away"]].append(game["home"])
    results = {}
    for team, row in candidates.items():
        key = (row["player_id"], row["team_id"])
        if len(minutes[key]) < 3 or len(opponents[team]) < minimum_opportunities:
            raise ValueError(f"Insufficient observed baseline or schedule opportunities for team {team}")
        results[team] = dict(team_margin=strengths[team], minutes=mean(minutes[key]), fga=mean(attempts[key]),
                             shot_tendency=row["shot_tendency"], scheduled_games=len(opponents[team]),
                             opponent_margin=mean(strengths[other] for other in opponents[team]))
    return results


def assign_blocks(features, candidates):
    centers = {k: mean(row[k] for row in features.values()) for k in FEATURES}
    scales = {k: pstdev(row[k] for row in features.values()) or 1 for k in FEATURES}

    def distance(first, second):
        return (sum(((features[first][k] - features[second][k]) / scales[k]) ** 2 for k in FEATURES)
                + (candidates[first]["position"] != candidates[second]["position"]))

    remaining = set(features)
    groups = []
    while remaining:
        pivot = min(remaining, key=lambda team: (features[team]["team_margin"], team))
        neighbors = sorted(remaining - {pivot}, key=lambda team: (distance(pivot, team), team))[:4]
        group = [pivot, *neighbors]
        remaining.difference_update(group)
        groups.append(group)
    return groups, centers, scales


def build(directory, database, capture_status, *, excluded_uids=frozenset(), stop_override=None):
    sources = {name: (directory / name).read_bytes() for name in SOURCE_FILES}
    manifest = json.loads(sources[SOURCE_FILES[0]])
    inventory = json.loads(sources[SOURCE_FILES[1]])
    pool = [json.loads(line) for line in sources[SOURCE_FILES[2]].splitlines()]
    games = [dict(game_id=int(row["native_game_id"]), day=row["scheduled_date"],
                  home=row["home"], away=row["away"], state="PENDING") for row in inventory["fixtures"]]
    stop = manifest["window_end_exclusive"]
    if stop_override is not None:
        if not manifest["window_start"] < stop_override <= stop:
            raise ValueError("Shortened round is outside the captured candidate window")
        stop = stop_override
        games = [row for row in games if row["day"] < stop]
    team_ids = {team for game in games for team in (game["home"], game["away"])}
    candidates = {}
    for row in pool:
        if (row["team"] not in team_ids or row["uid"] in excluded_uids
                or not row["eligible"] or not 5 <= row["shot_tendency"] <= 95):
            continue
        prior = candidates.get(row["team"])
        if prior is None or (-row["mean_minutes"], row["uid"]) < (-prior["mean_minutes"], prior["uid"]):
            candidates[row["team"]] = row
    if len(team_ids) != 30 or set(candidates) != team_ids:
        raise ValueError(f"30-team plan requires all teams eligible; have {len(candidates)} of {len(team_ids)}")
    features = source_features(database, manifest, games, candidates,
                               minimum_opportunities=1 if stop_override is not None else 2)
    groups, centers, scales = assign_blocks(features, candidates)
    scope = "HISTORICAL_R0_REPLAY_NOT_AUTHORIZED"
    identity = dict(save=manifest["save_id"], worldline=manifest["worldline"],
                    season=manifest["units"]["schedule"]["season_id"],
                    source_report_sha256=manifest["source_report_sha256"])
    if capture_status:
        status = json.loads(capture_status.read_bytes())
        if (status["status"] != "CAPTURE_COMPLETE" or status["before"] != status["after"]
                or status["source_report_sha256"] != manifest["source_report_sha256"]
                or status["before"]["game_progress"]["today_native_iso_date"] != manifest["window_start"]):
            raise ValueError("Current capture receipt does not match the observed anchor")
        scope = "FRESH_WORLDDATA_CANDIDATE_NOT_AUTHORIZED"
        identity["binding_sha256"] = status["binding_sha256"]
        identity["epoch"] = status["before"]["epoch"]
        identity["capture_receipt_sha256"] = sha(capture_status.read_bytes())
    snapshot = {"evidence_scope": scope, "identity": identity, "start": manifest["window_start"],
                "stop": stop, "teams": [], "games": games,
                "provenance": {"r0_export_sha256": {name: sha(raw) for name, raw in sources.items()},
                               "unit_refs": manifest["units"], "centers": centers, "scales": scales,
                               "group_rule": "minimum margin pivot, four nearest standardized feature vectors",
                               "candidate_rule": "maximum observed mean minutes, then lowest UID"}}
    for block, group in enumerate(groups, 1):
        for team in group:
            row = candidates[team]
            snapshot["teams"].append({
                "team_id": team, "stratum": f"block-{block}", "features": features[team],
                "candidate": {"uid": row["uid"], "shot_tendency": row["shot_tendency"],
                              "unique_native_binding": True, "healthy": True, "slot": row["slot"],
                              "position": row["position"], "recent_10min_appearances": row["recent_games_10min"]},
            })
    return snapshot


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("r0_export", type=Path)
    parser.add_argument("database", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--capture-status", type=Path)
    parser.add_argument("--seed", type=int, default=20261107)
    args = parser.parse_args()
    snapshot = build(args.r0_export, args.database, args.capture_status)
    result = plan(snapshot, args.seed)
    with args.output.open("x", encoding="utf-8", newline="\n") as target:
        json.dump({"snapshot": snapshot, "plan": result}, target, ensure_ascii=False, indent=2)
    print(json.dumps({"scope": result["evidence_scope"], "plan_digest": result["research_plan_digest"],
                      "teams": len(result["assignments"]), "games": len(result["games"])}))

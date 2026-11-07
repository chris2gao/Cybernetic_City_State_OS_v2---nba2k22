"""Deterministic team-cluster SHOT_TENDENCY screening plan and same-unit analyzer."""
import argparse
from collections import Counter, defaultdict
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
from statistics import mean

ARMS = ("H", "L", "C", "RESERVE", "RESERVE")
DOSE = {"H": 5, "L": -5, "C": 0, "RESERVE": 0}
FIELD = "SHOT_TENDENCY"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def rank(seed, domain, value):
    return digest([seed, domain, value])


def plan(snapshot, seed):
    start, stop = (date.fromisoformat(snapshot[key]) for key in ("start", "stop"))
    if not 1 <= (stop - start).days <= 7:
        raise ValueError("Window must contain one to seven game days")
    teams = snapshot["teams"]
    team_ids = {team["team_id"] for team in teams}
    if len(teams) != 30 or len(team_ids) != 30:
        raise ValueError("30 distinct teams required")
    games = sorted(snapshot["games"], key=lambda game: game["game_id"])
    if not games or len({game["game_id"] for game in games}) != len(games):
        raise ValueError("Missing or duplicate game IDs")
    opportunity = Counter()
    for game in games:
        pair = {game["home"], game["away"]}
        if (not start <= date.fromisoformat(game["day"]) < stop or len(pair) != 2
                or not pair <= team_ids or game["state"] != "PENDING"):
            raise ValueError("Frozen schedule must contain pending in-window games")
        opportunity.update(pair)
    strata = defaultdict(list)
    for team in teams:
        strata[team["stratum"]].append(team)
    if len(strata) != 6 or any(len(group) != 5 for group in strata.values()):
        raise ValueError("Provide six pre-treatment strata of five teams")
    candidates = [team["candidate"] for team in teams]
    if len({player["uid"] for player in candidates}) != 30:
        raise ValueError("One distinct preselected UID per team required")
    assignments = {}
    for stratum, group in sorted(strata.items()):
        ordered = sorted(group, key=lambda team: (rank(seed, stratum, team["team_id"]), team["team_id"]))
        for arm, team in zip(ARMS, ordered, strict=True):
            player = team["candidate"]
            baseline = player["shot_tendency"]
            if (type(player["uid"]) is not int or not 1 <= player["uid"] <= 65535
                    or not player["unique_native_binding"] or not player["healthy"]
                    or type(player["slot"]) is not int or not 0 <= player["slot"] <= 14
                    or player["recent_10min_appearances"] < 3 or not player["position"]
                    or type(baseline) is not int or not 5 <= baseline <= 95
                    or opportunity[team["team_id"]] < 2):
                raise ValueError(f"Preselected candidate ineligible: {team['team_id']}")
            assignments[team["team_id"]] = {
                "team_id": team["team_id"], "uid": player["uid"], "stratum": stratum,
                "arm": arm, "position": player["position"], "baseline": baseline,
                "planned_value": baseline + DOSE[arm], "planned_opportunities": opportunity[team["team_id"]],
                "applied_value": None,
            }
    write_candidates = [
        {"team_id": row["team_id"], "uid": row["uid"], "field": FIELD,
         "expected_before": row["baseline"], "target": row["planned_value"],
         "requires_existing_exact_batch_approval": True}
        for _, row in sorted(assignments.items()) if row["arm"] in {"H", "L"}
    ]
    payload = {
        "schema": "nba2k22.vae.round_plan.v1", "evidence_scope": snapshot["evidence_scope"],
        "status": "CANDIDATE_NOT_AUTHORIZED", "identity": snapshot["identity"],
        "start": start.isoformat(), "stop": stop.isoformat(), "selected_end_inclusive": (stop - timedelta(days=1)).isoformat(),
        "seed": seed, "factor": FIELD, "design": "six pre-treatment five-team blocks; H/L/C and two reserve",
        "input_sha256": digest(snapshot), "assignments": [assignments[key] for key in sorted(assignments)],
        "write_candidates": write_candidates,
        "games": [dict(game, home_arm=assignments[game["home"]]["arm"],
                       away_arm=assignments[game["away"]]["arm"]) for game in games],
        "planned_expected_game_ids": [game["game_id"] for game in games],
        "preregistration": {"hypothesis_version": "SHOT_TENDENCY_HLC_V1",
                            "primary": "candidate FGA per scheduled opportunity",
                            "contrast": "stratum-averaged H minus C and L minus C",
                            "secondary": ["minutes", "FGA/36", "candidate team FGA share", "teammate FGA"],
                            "reassign_after_randomization": False, "effect_gate": "SCREENING_ONLY",
                            "multiple_testing": "prespecify confirmatory family and dependence-aware FDR in follow-up"},
    }
    return dict(payload, research_plan_digest=digest(payload))


def analyze(plan_data, capture):
    """Screen exact simulated finals from one observation unit per game."""
    if capture["identity"] != plan_data["identity"] or capture["today"] != plan_data["stop"]:
        raise ValueError("Capture identity or date differs from plan")
    expected = {game["game_id"]: game for game in plan_data["games"]}
    rows = {game["game_id"]: game for game in capture["games"]}
    if len(rows) != len(capture["games"]) or set(rows) != set(expected):
        raise ValueError("Partial, extra or duplicate results")
    assignments = {row["team_id"]: row for row in plan_data["assignments"]}
    sample = []
    for game_id, scheduled in sorted(expected.items()):
        row = rows[game_id]
        if (any(row[key] != scheduled[key] for key in ("home", "away", "day"))
                or not row["final"] or not row["was_simulated"] or not row["unit"]
                or row["team_box_unit"] != row["unit"] or row["player_box_unit"] != row["unit"]
                or not row["score_conserved"]):
            raise ValueError(f"Final/same-unit Box gate failed: {game_id}")
        if {team["team_id"] for team in row["team_boxes"]} != {scheduled["home"], scheduled["away"]} or len(row["team_boxes"]) != 2:
            raise ValueError("Expected one Box per team")
        for team in row["team_boxes"]:
            assigned = assignments[team["team_id"]]
            if team["candidate_uid"] != assigned["uid"]:
                raise ValueError("Player UID differs from preregistration")
            minutes, fga, team_fga = (team[k] for k in ("minutes", "fga", "team_fga"))
            if type(team_fga) is not int or team_fga < 0:
                raise ValueError("Invalid team FGA")
            disposition = team["disposition"]
            if disposition == "DNP":
                if minutes != 0 or fga != 0:
                    raise ValueError("A verified DNP must have zero minutes and FGA")
            elif disposition == "PLAYED":
                if (type(minutes) not in {int, float} or not 0 < minutes <= 100
                        or type(fga) is not int or not 0 <= fga <= team_fga):
                    raise ValueError("Invalid played Box observation")
            elif disposition != "UNOBSERVED" or minutes is not None or fga is not None:
                raise ValueError("Unsupported missing-data disposition")
            opponent_arm = scheduled["away_arm"] if team["team_id"] == scheduled["home"] else scheduled["home_arm"]
            sample.append({"game_id": game_id, "source_unit": row["unit"], "team_id": team["team_id"],
                           "uid": assigned["uid"], "stratum": assigned["stratum"], "arm": assigned["arm"],
                           "opponent_arm": opponent_arm, "disposition": disposition,
                           "fga": fga, "minutes": minutes, "fga_per_36": fga * 36 / minutes if minutes else None,
                           "team_shot_share": fga / team_fga if fga is not None and team_fga else None,
                           "teammate_fga": team_fga - fga if fga is not None else None})
    by_team = defaultdict(list)
    for observation in sample:
        by_team[observation["team_id"]].append(observation["fga"])
    arm_means = defaultdict(dict)
    for team_id, values in by_team.items():
        assignment = assignments[team_id]
        if assignment["arm"] != "RESERVE":
            arm_means[assignment["stratum"]][assignment["arm"]] = (
                mean(values) if all(value is not None for value in values) else None)
    contrasts = {}
    for arm in ("H", "L"):
        usable = [group[arm] - group["C"] for group in arm_means.values()
                  if group.get(arm) is not None and group.get("C") is not None]
        contrasts[f"{arm}_minus_C"] = {"estimate": mean(usable) if usable else None,
                                      "complete_strata": len(usable), "ci": None}
    return {"classification": "UNDERPOWERED_SCREENING_ONLY", "planned_game_count": len(expected),
            "contrasts": contrasts, "opponent_exposure": {
                f"{a}/{b}": count for (a, b), count in sorted(Counter(
                    (row["arm"], row["opponent_arm"]) for row in sample).items())},
            "observations": sample, "source_digest": digest(capture),
            "interpretation": "No inference from fixture or one dependent screening window"}


def fixture():
    start = date(2021, 12, 31)
    teams = [{"team_id": team, "stratum": f"block-{(team - 1)//5 + 1}",
              "candidate": {"uid": 10000 + team, "shot_tendency": 56 + (team % 5),
                            "unique_native_binding": True, "healthy": True, "slot": 2,
                            "position": ["PG", "SG", "SF", "PF", "C"][(team - 1)//6],
                            "recent_10min_appearances": 4}}
             for team in range(1, 31)]
    games = []
    rotation = list(range(1, 31))
    for round_index, day_offset in enumerate((0, 2, 4, 6)):
        for home, away in zip(rotation[:15], reversed(rotation[15:]), strict=True):
            games.append({"game_id": 8000 + len(games), "day": (start + timedelta(days=day_offset)).isoformat(),
                          "home": home if round_index % 2 == 0 else away,
                          "away": away if round_index % 2 == 0 else home, "state": "PENDING"})
        rotation = [rotation[0], rotation[-1], *rotation[1:-1]]
    return {"evidence_scope": "SYNTHETIC_FIXTURE_NOT_A_LIVE_ROUND",
            "identity": {"save": "fixture-slot", "worldline": "fixture-worldline",
                         "season": "fixture-2021-22", "binding": "fixture-binding"},
            "start": start.isoformat(), "stop": (start + timedelta(days=7)).isoformat(),
            "teams": teams, "games": games}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--seed", type=int, default=20261107)
    args = parser.parse_args()
    payload = json.loads(args.snapshot.read_bytes()) if args.snapshot else fixture()
    print(json.dumps(plan(payload, args.seed), ensure_ascii=False, indent=2))

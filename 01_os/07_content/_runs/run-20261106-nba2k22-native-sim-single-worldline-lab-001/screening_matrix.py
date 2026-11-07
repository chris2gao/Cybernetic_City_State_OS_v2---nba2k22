"""Generate the reproducible 30-team synthetic single-worldline example."""
import json
import random


TEAMS = (
    "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
    "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
    "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS",
)
SEED = 3701
ARMS = ("H", "L", "C", "RESERVE", "RESERVE")
DELTA = {"H": 10, "L": -10, "C": 0, "RESERVE": 0}


def make_matrix():
    rng = random.Random(SEED)
    teams = list(TEAMS)
    rng.shuffle(teams)
    rows = {}
    for stratum in range(6):
        arms = list(ARMS)
        rng.shuffle(arms)
        for team, arm in zip(teams[stratum * 5:stratum * 5 + 5], arms):
            before = 55 + 4 * stratum
            rows[team] = {
                "team": team, "stratum": stratum + 1, "arm": arm,
                "primary_player": f"fixture:{team}:01" if arm != "RESERVE" else None,
                "position_proxy": ("G", "F", "C")[stratum % 3],
                "baseline_opportunity": {"minutes_per_game": 18 + 3 * stratum, "eligible_games": 8},
                "baseline_tendency": before, "candidate_tendency": before + DELTA[arm],
                "teammate_spillover": arm in {"H", "L"}, "game_ids": [],
            }
    pairings = list(TEAMS)
    games = []
    for round_number in range(6):
        block = f"B{round_number // 3 + 1}"
        for home, away in zip(pairings[:15], reversed(pairings[15:])):
            game_id = f"fixture:{round_number + 1}:{home}:{away}"
            rows[home]["game_ids"].append(game_id)
            rows[away]["game_ids"].append(game_id)
            home_arm, away_arm = rows[home]["arm"], rows[away]["arm"]
            games.append({
                "game_id": game_id, "block": block, "home": home, "away": away,
                "home_own_exposure": home_arm, "home_opponent_exposure": away_arm,
                "away_own_exposure": away_arm, "away_opponent_exposure": home_arm,
                "opposite_treatment": {home_arm, away_arm} == {"H", "L"},
                "carryover": "PRIOR_BLOCK_POSSIBLE" if block == "B2" else "BASELINE_REQUIRED",
            })
        pairings = pairings[:1] + pairings[-1:] + pairings[1:-1]
    return {
        "schema": "nba2k22.single_worldline_screening_fixture.v1",
        "mode": "SYNTHETIC_EXAMPLE_NO_WRITE_AUTHORITY",
        "worldline": "fixture:single-worldline",
        "seed": SEED, "field": "SHOT_TENDENCY",
        "certification": {
            "SHOT_TENDENCY": "LIVE_WRITE_CERTIFIED_SCOPED_S4",
            "minutes_and_team_fga": "ELIGIBLE_READONLY",
            "TOUCHES_TENDENCY": "NOT_YET_CERTIFIED",
            "COACH_RUN_PLAYS": "NOT_YET_CERTIFIED",
            "other_player_or_coach_fields": "NOT_YET_CERTIFIED",
        },
        "teams": [rows[team] for team in TEAMS],
        "games": games,
    }


if __name__ == "__main__":
    print(json.dumps(make_matrix(), sort_keys=True, separators=(",", ":")))

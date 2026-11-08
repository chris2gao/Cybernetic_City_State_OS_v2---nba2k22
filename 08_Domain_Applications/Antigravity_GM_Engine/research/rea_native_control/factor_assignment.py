"""Build multi-factor team-cluster assignments and retain interference by actual GameID."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache
from hashlib import sha256
from itertools import combinations


@dataclass(frozen=True)
class Exposure:
    worldline_id: str
    factor_id: str
    team_id: int
    uid: int | None
    effective_on: str
    applied: int | float
    receipt_ref: str
    ended_on: str | None = None

    def applies(self, worldline, day):
        return self.worldline_id == worldline and self.effective_on <= day and (
            self.ended_on is None or day < self.ended_on)


def windows_for_schedule(fixtures, teams, first, final_regular_day):
    """Find maximal nonoverlapping seven-day windows with exact one/two-day controls."""
    by_day = defaultdict(list)
    special = set()
    for game_id, row in fixtures.items():
        day = date.fromisoformat(row["date"])
        if row["phase"] != "REGULAR_SEASON":
            special.add(day)
        elif row["scheduled_state"] == "PENDING":
            by_day[day].append((game_id, int(row["home_team_id"]), int(row["away_team_id"])))
    last = date.fromisoformat(final_regular_day)

    @lru_cache(None)
    def parts(start, end):
        if start == end:
            return ()
        for span in (2, 1):
            stop = start + timedelta(days=span)
            games = [game for step in range(span) for game in by_day[start + timedelta(days=step)]]
            if stop > end or not games or not by_day[stop] or len(games) + len(by_day[stop]) > 45:
                continue
            suffix = parts(stop, end)
            if suffix is not None:
                return ((start, stop, tuple(games), tuple(by_day[stop])),) + suffix
        return None

    @lru_cache(None)
    def search(start):
        end = start + timedelta(days=7)
        if end > last:
            return ()
        skip = search(start + timedelta(days=1))
        if any(start <= day <= end for day in special):
            return skip
        path = parts(start, end)
        if path is None:
            return skip
        games = [game for part in path for game in part[2]]
        opportunities = Counter(team for _, home, away in games for team in (home, away))
        if set(opportunities) != set(teams) or min(opportunities.values()) < 2:
            return skip
        take = (path,) + search(end)
        def score(items):
            return len(items), sum(len(part[2]) for window in items for part in window)
        return take if score(take) >= score(skip) else skip

    return [
        {"start": path[0][0].isoformat(), "stop_exclusive": path[-1][1].isoformat(),
         "real_game_ids": [game[0] for part in path for game in part[2]],
         "subwindows": [{"start": a.isoformat(), "stop_exclusive": b.isoformat(),
                         "planned_finals": [item[0] for item in finals],
                         "next_day_controls": [item[0] for item in controls]}
                        for a, b, finals, controls in path]}
        for path in search(date.fromisoformat(first))]


def allocate_window(study, window, factor_ids, values, history, *, worldline, seed, qualifications=None):
    """Allocate distinct same-family factors; qualified amounts and actual exposure remain separate."""
    factors = [study.factors[key] for key in factor_ids]
    if not 1 <= len(factors) <= 5 or len(set(factor_ids)) != len(factors):
        raise ValueError("DISTINCT_FACTORS_REQUIRED")
    category = factors[0].category
    if category not in ("player_tendency", "coach") or any(row.category != category for row in factors):
        raise ValueError("CROSS_FAMILY_REQUIRES_EXPLICIT_FACTORIAL_OR_EVENT_DESIGN")
    fixtures = [study.fixtures[gid] for gid in window["real_game_ids"]]
    if (len(set(window["real_game_ids"])) != len(fixtures)
            or any(row["phase"] != "REGULAR_SEASON" or row["scheduled_state"] != "PENDING"
                   or not window["start"] <= row["date"] < window["stop_exclusive"] for row in fixtures)):
        raise ValueError("WINDOW_FIXTURES_NOT_BOUND_PENDING_REGULAR")
    opportunities = Counter(int(row[key]) for row in fixtures for key in ("home_team_id", "away_team_id"))
    by_team = defaultdict(list)
    for player in study.players:
        if player["eligible_now"] == "True":
            by_team[int(player["native_team_id"])].append(player)
    if len(opportunities) != 30 or set(opportunities) != set(by_team) or min(opportunities.values()) < 2:
        raise ValueError("FIVE_FACTOR_DESIGN_REQUIRES_REAL_TEAM_OPPORTUNITIES")
    prior = [row for row in history if row.worldline_id == worldline and row.effective_on <= window["start"]]
    team_prior = defaultdict(list)
    treated_uids = Counter()
    for row in prior:
        team_prior[row.team_id].append(row)
        if row.uid is not None:
            treated_uids[row.uid] += 1

    def rank(*keys):
        return sha256("|".join(map(str, (seed, worldline, window["start"], *keys))).encode()).digest()

    teams = sorted(by_team, key=lambda team: (-opportunities[team], -len(by_team[team]), rank(team)))
    groups = [[] for _ in range(5)]
    for index, team in enumerate(teams):
        block, position = divmod(index, 5)
        groups[position if block % 2 == 0 else 4 - position].append(team)

    def choose(team, factor, arm):
        choices = by_team[team] if category == "player_tendency" else (None,)
        scored = []
        for player in choices:
            uid = int(player["native_uid"]) if player else None
            unit_id = uid if uid is not None else team
            value = values.get((factor.factor_id, unit_id))
            limits = factor.native.get("legal_boundary")
            target = value if arm == "C" else None
            if category == "player_tendency" and type(value) is int and limits:
                proposal = value + (5 if arm == "H" else -5)
                if arm != "C" and limits[0] <= proposal <= limits[1]:
                    target = proposal
            score = (arm != "C" and target is None, treated_uids[uid],
                     -float(player["mean_minutes_recent_10min"] or 0) if player else 0,
                     rank(factor.factor_id, team, uid))
            scored.append((score, uid, value, target))
        _, uid, value, target = min(scored, key=lambda row: row[0])
        return {"factor_id": factor.factor_id, "team_id": team, "uid": uid, "arm": arm, "baseline": value,
                "target": target, "opportunities": opportunities[team],
                "reference_only": True, "live_writer_qualified": factor.live_qualified or (
                    qualifications is not None and factor.factor_id in qualifications.factor_ids),
                "prior_team_treatments": [exposure.__dict__ for exposure in team_prior[team]],
                "prior_uid_treatment_count": treated_uids[uid]}

    assignments = {}
    for factor, cohort in zip(factors, groups):
        choices = {(team, arm): choose(team, factor, arm) for team in cohort for arm in "HLC"}
        ranked = []
        for high in combinations(cohort, 2):
            for low in combinations([team for team in cohort if team not in high], 2):
                if any(not 0 <= team <= 29 for team in (*high, *low)):
                    continue
                selected = [choices[team, "H" if team in high else "L" if team in low else "C"] for team in cohort]
                totals = Counter()
                for item in selected:
                    totals[item["arm"]] += item["opportunities"]
                score = (sum(item["arm"] != "C" and item["target"] is None for item in selected),
                         sum(bool(item["prior_team_treatments"]) for item in selected if item["arm"] == "C"),
                         max(totals.values()) - min(totals.values()), rank(factor.factor_id, *high, *low))
                ranked.append((score, selected))
        if not ranked:
            raise ValueError(f"NO_ELIGIBLE_HLC_COHORT: {factor.factor_id}")
        assignments.update((item["team_id"], item) for item in min(ranked, key=lambda item: item[0])[1])

    games = []
    cross_factor = 0
    for row in fixtures:
        home_team, away_team = int(row["home_team_id"]), int(row["away_team_id"])
        home, away = assignments.get(home_team), assignments.get(away_team)
        cross = bool(home and away and home["factor_id"] != away["factor_id"])
        cross_factor += cross
        games.append({"game_id": int(row["game_id"]), "date": row["date"], "home_team": home_team,
                      "away_team": away_team, "home": home, "away": away, "cross_factor_opponent": cross,
                      "previous_home_treatments": [item.__dict__ for item in team_prior[home_team]],
                      "previous_away_treatments": [item.__dict__ for item in team_prior[away_team]],
                      "active_previous_home_treatments": [item.__dict__ for item in team_prior[home_team]
                                                         if item.applies(worldline, row["date"])],
                      "active_previous_away_treatments": [item.__dict__ for item in team_prior[away_team]
                                                         if item.applies(worldline, row["date"])]})
    result = {"worldline_id": worldline, "start": window["start"], "stop_exclusive": window["stop_exclusive"],
            "factors": list(factor_ids), "teams": assignments, "games": games, "subwindows": window["subwindows"],
            "cross_factor_opponent_games": cross_factor,
            "treatment_slots": sum(item["arm"] != "C" for item in assignments.values()),
            "unqualified_treatment_slots": sum(item["arm"] != "C" and (
                not item["live_writer_qualified"] or item["target"] is None) for item in assignments.values()),
            "estimand": "EXPLORATORY_WITH_CARRYOVER" if prior else "EXPLORATORY_SCREEN",
            "live_authorized": False}
    if qualifications is not None:
        result["qualification_sha256"] = qualifications.sha256
    return result


def event_study(record, worldlines, event_refs):
    """Bind non-game opportunities to distinct worlds and an observed event source."""
    if len(worldlines) != len(set(worldlines)) or len(worldlines) < 2:
        raise ValueError("INDEPENDENT_WORLDLINES_REQUIRED")
    if set(worldlines) != set(event_refs):
        raise ValueError("EVENT_BINDING_REQUIRED_FOR_EACH_WORLDLINE")
    if any(not proof.get("event_id") or not proof.get("source_unit") or not proof.get("event_date")
           for proof in event_refs.values()):
        raise ValueError("EVENT_OBSERVATION_INCOMPLETE")
    return {"factor_id": record.factor_id, "protocol": record.protocol, "event_refs": event_refs,
            "classification": "EVENT_BOUND_REFERENCE", "live_authorized": False}

"""Separate same-unit game screening from independent-world event and factorial estimates."""
from collections import defaultdict
from math import isfinite
from random import Random
from statistics import mean


def _real(value):
    return type(value) in (int, float) and isfinite(value)


def dose_response(rows, endpoint):
    """Descriptive raw-dose slope with one mean per assigned team."""
    grouped = defaultdict(list)
    doses = defaultdict(set)
    for row in rows:
        dose, value = row["dose"], row["metrics"].get(endpoint)
        if _real(dose) and _real(value):
            doses[row["team_id"]].add(dose)
            grouped[row["team_id"], dose].append(value)
    if any(len(values) != 1 for values in doses.values()):
        raise ValueError("DOSE_RESPONSE_TEAM_HAS_MULTIPLE_WINDOW_DOSES")
    points = [(dose, mean(values)) for (_, dose), values in grouped.items()]
    result = {"status": "UNDERPOWERED", "team_clusters": len(points), "slope_per_raw_step": None,
              "confidence_interval": None, "scope": "DESCRIPTIVE_TEAM_MEANS_WITH_OPPONENT_AND_BASELINE_CONFOUNDING"}
    if len(points) < 3 or len({dose for dose, _ in points}) < 2:
        return result
    center_x, center_y = mean(point[0] for point in points), mean(point[1] for point in points)
    result.update(slope_per_raw_step=sum((x - center_x) * (y - center_y) for x, y in points) /
                                     sum((x - center_x) ** 2 for x, _ in points),
                  dose_range=[min(x for x, _ in points), max(x for x, _ in points)])
    return result


def screen_game_window(plan, operations, setter_receipts, capture, *, qualified_team_games=None):
    if capture["worldline_id"] != plan["worldline_id"] or capture["today"] != plan["stop_exclusive"]:
        raise ValueError("ANALYSIS_CAPTURE_WORLD_OR_DATE_MISMATCH")
    planned = {row["game_id"]: row for row in plan["games"]}
    supplied = {row["game_id"]: row for row in capture["games"]}
    if len(supplied) != len(capture["games"]) or not set(supplied) <= set(planned):
        raise ValueError("ANALYSIS_UNEXPECTED_OR_DUPLICATE_GAME")
    if len(operations) != len(setter_receipts):
        raise ValueError("ANALYSIS_SETTER_RECEIPT_COUNT_MISMATCH")
    verified = {
        (op["factor_id"], op["team_id"], op["uid"]): op["target"]
        for op, receipt in zip(operations, setter_receipts, strict=True)
        if receipt["status"] == "APPLIED" and receipt.get("value") == op["target"]
        and op["target"] != op["expected_before"] and receipt.get("source_ref")
    }
    missing_games = set(planned) - set(supplied)
    invalid_games = set()
    opportunities = defaultdict(set)
    eligible = defaultdict(list)
    endpoints = plan.get("pre_registered_metrics", ("FGA", "MIN"))
    for game_id, expected in planned.items():
        for side in ("home", "away"):
            target = expected[side]
            if target:
                opportunities[target["factor_id"]].add(game_id)
        if game_id not in supplied:
            continue
        actual = supplied[game_id]
        unit = actual.get("unit")
        if (not unit or actual.get("team_box_unit") != unit or actual.get("player_box_unit") != unit
                or actual.get("score_conserved") is not True or actual.get("final") is not True
                or actual.get("was_simulated") is not True
                or any(actual.get(k) != expected[k] for k in ("date", "home_team", "away_team"))):
            invalid_games.add(game_id)
            continue
        by_team = {row["team_id"]: row for row in actual["team_boxes"]}
        if len(actual["team_boxes"]) != 2 or set(by_team) != {expected["home_team"], expected["away_team"]}:
            invalid_games.add(game_id)
            continue
        for side in ("home", "away"):
            target = expected[side]
            if target is None:
                continue
            if qualified_team_games is not None and (game_id, target["team_id"]) not in qualified_team_games:
                continue
            row = by_team[target["team_id"]]
            key = (target["factor_id"], target["team_id"], target["uid"])
            if (row.get("uid") != target["uid"] or row.get("disposition") not in ("PLAYED", "DNP")
                    or (target["arm"] != "C" and key not in verified)):
                continue
            if row["disposition"] == "DNP" and any(value not in (None, 0) for value in row["metrics"].values()):
                raise ValueError("DNP_METRICS_CONTRADICT_ZERO_OPPORTUNITY")
            opponent = expected["away" if side == "home" else "home"]
            eligible[target["factor_id"]].append({
                "game_id": game_id, "unit": unit, "team_id": target["team_id"], "uid": target["uid"],
                "arm": target["arm"], "dose": verified.get(key), "metrics": row["metrics"],
                "disposition": row["disposition"], "opponent": opponent,
                "previous_home_treatments": expected.get("previous_home_treatments", []),
                "previous_away_treatments": expected.get("previous_away_treatments", []),
            })
    results = {}
    for factor_id in plan["factors"]:
        rows = eligible[factor_id]
        metric_results = {}
        for endpoint in endpoints:
            grouped = defaultdict(list)
            for row in rows:
                value = row["metrics"].get(endpoint)
                if _real(value):
                    grouped[row["arm"], row["team_id"]].append(value)
            arm_values = defaultdict(list)
            for (arm, team), values in grouped.items():
                arm_values[arm].append(mean(values))
            estimates = {
                f"{arm}_minus_C": (mean(arm_values[arm]) - mean(arm_values["C"])
                                    if arm_values[arm] and arm_values["C"] else None)
                for arm in ("H", "L")
            }
            metric_results[endpoint] = {"estimates": estimates,
                                       "team_clusters": {arm: len(arm_values[arm]) for arm in "HLC"},
                                       "confidence_interval": None,
                                       "limitation": "SINGLE_WORLDLINE_TEAM_AND_OPPONENT_DEPENDENCE"}
            if factor_id in plan.get("dose_response_factors", ()):
                metric_results[endpoint]["dose_response"] = dose_response(rows, endpoint)
        has_endpoint = any(value is not None for row in metric_results.values() for value in row["estimates"].values())
        if not opportunities[factor_id]:
            status = "NO_OPPORTUNITY"
        elif not any(key[0] == factor_id for key in verified):
            status = "SETTER_UNVERIFIED"
        elif not has_endpoint:
            status = "NO_MEASURABLE_ENDPOINT"
        else:
            status = "UNDERPOWERED"
        results[factor_id] = {"status": status, "metrics": metric_results, "observations": rows,
                              "planned_opportunities": len(opportunities[factor_id])}
    return {"mode": capture["mode"], "worldline_id": plan["worldline_id"], "factors": results,
            "qualified_game_count": len(supplied) - len(invalid_games), "missing_game_ids": sorted(missing_games),
            "excluded_game_ids": sorted(invalid_games)}


def screen_coach_window(plan, operations, setter_receipts, capture, exposure):
    """Require accepted game-consumer evidence for each included Coach/team observation."""
    if (exposure["mode"] != capture["mode"] or exposure["worldline_id"] != plan["worldline_id"]
            or exposure["start"] != plan["start"] or exposure["stop_exclusive"] != plan["stop_exclusive"]
            or not exposure["proof_sha256"] or not exposure["planning_report_sha256"]):
        raise ValueError("COACH_ANALYSIS_EXPOSURE_SCOPE_MISMATCH")
    expected = {(game["game_id"], game[side]["team_id"]): game[side]
                for game in plan["games"] for side in ("home", "away") if game[side] is not None}
    evidence = {(row["game_id"], row["team_id"]): row for row in exposure["exposures"]}
    if len(evidence) != len(exposure["exposures"]) or evidence.keys() != expected.keys():
        raise ValueError("COACH_ANALYSIS_EXPOSURE_GAME_SET_MISMATCH")
    qualified = set()
    for key, row in evidence.items():
        target = expected[key]
        if (target["uid"] is not None or row["factor_id"] != target["factor_id"]
                or row["applied_value"] != target["target"]):
            raise ValueError("COACH_ANALYSIS_EXPOSURE_ASSIGNMENT_MISMATCH")
        if row["qualified"] is True and row["status"] == "CONSUMER_VERIFIED" and row["consumer_source"]:
            qualified.add(key)
    analysis = screen_game_window(plan, operations, setter_receipts, capture, qualified_team_games=qualified)
    for factor, result in analysis["factors"].items():
        relevant = {key for key, target in expected.items() if target["factor_id"] == factor}
        result["unqualified_consumer_games"] = sorted({key[0] for key in relevant - qualified})
        if not relevant & qualified:
            result["status"] = "CONSUMER_UNVERIFIED"
    return dict(analysis, coach_exposure_sha256=exposure["proof_sha256"])


def screen_settled_events(study_plan, rows, endpoint, *, mode, minimum_effect=None, seed=0):
    """Compare only verified treatments with same-identity settlement snapshots."""
    if mode not in ("LIVE", "FIXTURE"):
        raise ValueError("EVENT_EVIDENCE_MODE_REQUIRED")
    refs = study_plan["event_refs"]
    worlds = [row["worldline_id"] for row in rows]
    if len(worlds) != len(set(worlds)) or set(worlds) != set(refs):
        raise ValueError("EVENT_ROWS_MUST_MATCH_FROZEN_WORLDLINES")
    if len({proof["source_unit"] for proof in refs.values()}) != len(refs):
        raise ValueError("EVENT_WORLDLINES_REQUIRE_DISTINCT_SETTLEMENT_SOURCES")
    qualified, excluded = [], {}
    for row in rows:
        world = row["worldline_id"]
        proof = refs[world]
        if (row["mode"] != mode or row["factor_id"] != study_plan["factor_id"]
                or any(row[key] != proof[key] for key in ("event_id", "event_date", "source_unit"))
                or row["before_identity"] != row["after_identity"] or not row["before_identity"]):
            raise ValueError("EVENT_SNAPSHOT_IDENTITY_OR_SOURCE_MISMATCH")
        if row["opportunity"] is not True:
            excluded[world] = "NO_OPPORTUNITY"
        elif row["setter_verified"] is not True or row["observed_value"] != row["requested_value"]:
            excluded[world] = "SETTER_UNVERIFIED"
        else:
            qualified.append(row)
    result = compare_independent_worldlines(qualified, endpoint, minimum_effect=minimum_effect, seed=seed)
    return dict(result, mode=mode, event_protocol=study_plan["protocol"], excluded=excluded)


def compare_independent_worldlines(rows, endpoint, *, factorial=False, minimum_effect=None, seed=0):
    """Use at most one independently rebound observation unit per worldline."""
    arm_names = ("00", "10", "01", "11") if factorial else ("C", "H", "L")
    by_arm = defaultdict(list)
    worlds = set()
    source_refs = set()
    common_origin = None
    for row in rows:
        if (row["worldline_id"] in worlds or row["arm"] not in arm_names
                or not row["origin_sha256"] or not row["before_source"] or not row["after_source"]
                or row["before_source"] == row["after_source"] or not row["event_id"]
                or source_refs & {row["before_source"], row["after_source"]}):
            raise ValueError("INDEPENDENT_WORLD_EVENT_PROOF_REQUIRED")
        common_origin = common_origin or row["origin_sha256"]
        if row["origin_sha256"] != common_origin:
            raise ValueError("INDEPENDENT_WORLD_ORIGIN_MISMATCH")
        worlds.add(row["worldline_id"])
        source_refs.update((row["before_source"], row["after_source"]))
        before, after = (row[key].get(endpoint) for key in ("before", "after"))
        if _real(before) and _real(after):
            by_arm[row["arm"]].append(after - before)
    if minimum_effect is not None and (not _real(minimum_effect) or minimum_effect <= 0):
        raise ValueError("POSITIVE_PREREGISTERED_EFFECT_BOUND_REQUIRED")
    contrasts = ({"interaction": {"11": 1, "10": -1, "01": -1, "00": 1}} if factorial
                 else {"H_minus_C": {"H": 1, "C": -1}, "L_minus_C": {"L": 1, "C": -1}})
    effects, intervals, classifications = {}, {}, {}
    rng = Random(seed)
    for label, weights in contrasts.items():
        if not all(by_arm[arm] for arm in weights):
            continue
        effects[label] = sum(weight * mean(by_arm[arm]) for arm, weight in weights.items())
        if min(len(by_arm[arm]) for arm in weights) < 6 or minimum_effect is None:
            classifications[label] = "UNDERPOWERED"
            continue
        samples = sorted(sum(weight * mean(rng.choices(by_arm[arm], k=len(by_arm[arm])))
                             for arm, weight in weights.items()) for _ in range(2000))
        lo, hi = samples[49], samples[1949]
        intervals[label] = [lo, hi]
        if -minimum_effect <= lo <= hi <= minimum_effect:
            classifications[label] = "NO_SIGNAL_DETECTED"
        elif lo > minimum_effect or hi < -minimum_effect:
            classifications[label] = "SIGNAL_FOR_CONFIRMATION"
        else:
            classifications[label] = "UNDERPOWERED"
    status = "NO_MEASURABLE_ENDPOINT" if not effects else (
        "CONTRASTS_WITH_PREREGISTERED_BOUNDS" if intervals else "UNDERPOWERED")
    return {"effects": effects, "worldline_counts": {arm: len(by_arm[arm]) for arm in arm_names},
            "status": status, "confidence_interval": intervals or None, "classifications": classifications}


def adjust_fdr(pre_registered_p_values):
    """Benjamini–Hochberg for an explicitly frozen family of valid p-values."""
    if any(not _real(value) or not 0 <= value <= 1 for value in pre_registered_p_values.values()):
        raise ValueError("INVALID_PREREGISTERED_P_VALUES")
    ordered = sorted(pre_registered_p_values, key=pre_registered_p_values.__getitem__)
    adjusted = {}
    running = 1.0
    for rank in range(len(ordered), 0, -1):
        key = ordered[rank - 1]
        running = min(running, pre_registered_p_values[key] * len(ordered) / rank)
        adjusted[key] = running
    return adjusted

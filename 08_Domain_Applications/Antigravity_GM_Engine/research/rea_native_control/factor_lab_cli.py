"""Rebuild engineering coverage and a same-input multi-factor plan without attaching to the game."""
import argparse
from datetime import date, timedelta
import json
from pathlib import Path

from factor_adapters import adapter_contract
from factor_assignment import allocate_window, windows_for_schedule
from factor_inventory import StudyInputs
from native_factor_slots import resolve_tendency_slot


def report(plan_dir, retained_path):
    study = StudyInputs.load(plan_dir)
    retained = json.loads(retained_path.read_bytes())
    if (retained["save_id"] != study.baseline["save_id"]
            or retained["source_report_sha256"] != study.baseline["source_report_sha256"]
            or retained["source_unit"] != study.baseline["source_units"]["player-skills"]["unit_id"]):
        raise ValueError("RETAINED_TENDENCY_VALUES_NOT_BOUND")
    eligible = {int(row["native_uid"]): int(row["native_team_id"]) for row in study.players if row["eligible_now"] == "True"}
    values = {}
    for factor, rows in retained["values"].items():
        record = study.factors[factor]
        if record.category != "player_tendency" or record.native["getter"]["status"] != "WORLDDATA_NAMED_STORAGE_READ":
            raise ValueError("RETAINED_TENDENCY_UNSUPPORTED_SOURCE")
        for uid, value in rows.items():
            uid = int(uid)
            if uid not in eligible or type(value) is not int or not 0 <= value <= 255:
                raise ValueError("RETAINED_TENDENCY_PLAYER_OR_RAW_VALUE_INVALID")
            values[factor, uid] = value
    first = date.fromisoformat(study.baseline["native_today"])
    if study.baseline["native_minutes_since_midnight"]:
        first += timedelta(days=1)
    windows = windows_for_schedule(study.fixtures, set(eligible.values()), first.isoformat(), study.baseline["last_regular_date"])
    reference = [window for window in study.reference["windows"] if window["worldline_id"] == "WL-TENDENCY-01"]
    if [(w["start"], set(w["real_game_ids"])) for w in windows] != [(w["start"], set(w["real_game_ids"])) for w in reference]:
        raise ValueError("ENGINEERING_REBUILD_CHANGED_REFERENCE_CAPACITY")
    reference_first = reference[0]["fields"]
    # Keep the original unknown-slot assignment in the full reference series.
    # Use a separately identified same-GameID example with observed doses on all five fields.
    unknown_slot = resolve_tendency_slot("UNKNOWN_RAW_BYTE_016").factor_id
    named_slot = resolve_tendency_slot("SHOT_THREE_TENDENCY").factor_id
    first_factors = [named_slot if factor == unknown_slot else factor for factor in reference_first]
    first_window = allocate_window(study, windows[0], first_factors, values, (),
                                   worldline="WL-TENDENCY-01", seed=study.reference["seed"])
    if any(row["baseline"] is None or row["target"] is None for row in first_window["teams"].values()):
        raise ValueError("OBSERVED_FIRST_WINDOW_REQUIRES_ALL_EXACT_DOSES")
    first_window["purpose"] = "OBSERVED_DOSE_ALTERNATIVE_FOR_THE_SAME_GAME_IDS"
    first_window["reference_factor_replacement"] = {"reference": unknown_slot, "alternative": named_slot}
    replay = []
    for reference_window in study.reference["windows"]:
        if "team_assignments" not in reference_window:
            continue
        candidate = allocate_window(study, reference_window, reference_window["fields"], values, (),
                                    worldline=reference_window["worldline_id"], seed=study.reference["seed"])
        # Team records retain UIDs, fields, doses and cohort sizes. Game rows
        # point to the two team records and preserve the interference flag.
        replay.append({"window_id": reference_window["window_id"], "worldline_id": candidate["worldline_id"],
                       "start": candidate["start"], "stop_exclusive": candidate["stop_exclusive"],
                       "team_assignments": candidate["teams"], "fields": candidate["factors"],
                       "games": [{key: game[key] for key in ("game_id", "date", "home_team", "away_team",
                                                            "cross_factor_opponent")} for game in candidate["games"]],
                       "subwindows": candidate["subwindows"], "live_authorized": False,
                       "future_treatment_history": "REQUIRED_BEFORE_EACH_LIVE_WINDOW"})
    engineering_coverage = study.crosswalk()
    for key, row in engineering_coverage.items():
        contract = adapter_contract(study.factors[key])
        row.update(category=study.factors[key].category, object_kind=contract.object_kind, unit=contract.unit,
                   action_candidate=contract.action, layout=contract.layout, endpoint=contract.endpoint,
                   engineering_gap=contract.engineering_gap, owner="NBA2K22_ISSUE_40_EXECUTION",
                   getter=study.factors[key].native["getter"], legal_boundary=study.factors[key].native["legal_boundary"],
                   engine_scope=study.factors[key].native["calendar"],
                   actual_runnable=False)
    seats = [item for window in reference for item in window["team_assignments"].values() if item["arm"] in ("H", "L")]
    unique = len({row["uid"] for row in seats})
    return {"reference_save": {"experiment_slot": study.baseline["loaded_slot"],
                               "cold_backup_slot": study.baseline["frozen_origin"],
                               "native_today": study.baseline["native_today"],
                               "source_report_sha256": study.baseline["source_report_sha256"]},
            "reference_capacity": {"windows": len(windows), "games": sum(len(w["real_game_ids"]) for w in windows),
                                   "treatment_seats": len(seats), "unique_hl_uids": unique,
                                   "repeated_uid_seats": len(seats) - unique},
            "first_window": first_window, "recompiled_team_windows": replay, "coverage": engineering_coverage,
            "independent_world_windows": [window for window in study.reference["windows"]
                                          if "team_assignments" not in window],
            "event_reservations": study.reference["event_reservations"],
            "reference_schedule_sha256": study.baseline["output_sha256"]["remaining_schedule.csv"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_dir", type=Path)
    parser.add_argument("retained_values", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    result = report(args.plan_dir, args.retained_values)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    coverage = result.pop("coverage")
    for name, payload in (("GAME_ID_EXPERIMENT_PLAN.json", result), ("implementation_coverage.json", coverage)):
        (args.output_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8", newline="\n")
    print(json.dumps(result["reference_capacity"]))

from collections import Counter
from dataclasses import replace
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

runtime = Path(__file__).resolve().parent
output = runtime.parent
repo = runtime.parents[4]
native = repo / "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control"
sys.path.insert(0, str(native))
from factor_inventory import StudyInputs
from factor_assignment import allocate_window, Exposure, windows_for_schedule
from factor_runner import digest, window_operations
from native_factor_slots import resolve_tendency_slot

receipt = json.loads((runtime / "fresh-capture-receipt.json").read_bytes())
assert receipt["status"] == "CAPTURE_COMPLETE"
report = json.loads((runtime / "fresh-capture/refresh-report.json").read_bytes())
assert hashlib.sha256((runtime / "fresh-capture/refresh-report.json").read_bytes()).hexdigest() == receipt["source_report_sha256"]
unit = {row["family"]: row["unit"]["unit_id"] for row in report["sources"] if row["commit_status"] == "COMMITTED_SUCCESS_VERIFIED"}
pool = [json.loads(line) for line in (runtime / "fresh-eligible/eligibility_pool.jsonl").read_text(encoding="utf-8").splitlines()]
subjects = json.loads((runtime / "fresh-16-slot-values.json").read_bytes())["rows"]
by_uid = {row["uid"]: row for row in subjects}
values = {(key, row["uid"]): value for row in subjects for key, value in row["values"].items()}
players = tuple({"native_uid": str(row["uid"]), "native_team_id": str(row["team"]),
                 "eligible_now": str(row["eligible"]), "mean_minutes_recent_10min": str(row["mean_minutes"] or 0)}
                for row in pool)
with sqlite3.connect((runtime / "world-0005/world.sqlite").as_uri() + "?mode=ro", uri=True) as conn:
    conn.row_factory = sqlite3.Row
    rows = list(conn.execute("""
        SELECT CAST(g.native_game_id AS INT) game_id,x.scheduled_native_iso_date day,
               CAST(h.native_team_id AS INT) home,CAST(a.native_team_id AS INT) away,
               x.game_type_label game_type,s.status_code,s.is_final,x.played_native_iso_date played
        FROM games g JOIN game_source_checks x USING(game_id)
        JOIN game_state_observations s ON s.game_id=x.game_id AND s.unit_id=x.unit_id
        JOIN teams h ON h.team_id=g.home_team_id JOIN teams a ON a.team_id=g.away_team_id
        WHERE x.unit_id=? ORDER BY x.scheduled_native_iso_date, CAST(g.native_game_id AS INT)
    """, (unit["schedule"],)))
fixtures = {row["game_id"]: {"game_id": row["game_id"], "date": row["day"], "home_team_id": row["home"],
                            "away_team_id": row["away"], "phase": "REGULAR_SEASON" if row["game_type"] == "NORMAL" else "SCHEDULED_SPECIAL",
                            "scheduled_state": "PENDING" if row["status_code"] == "0" and row["played"] is None else "NOT_FINAL_REQUIRES_RECHECK"}
            for row in rows if not row["is_final"]}
original = StudyInputs.load(repo / "01_os/07_content/_runs/run-20261108-nba2k22-full-factor-plan-001")
study = replace(original, fixtures=fixtures, players=players)
windows, history = [], []
groups = ((1,66,2,3,27), (4,17,5,18,6), (22,7,23,8,24))
regular = [row for row in fixtures.values() if row["phase"] == "REGULAR_SEASON"]
team_ids = {row["team"] for row in pool if row["eligible"]}
bounded_windows = windows_for_schedule(fixtures, team_ids, "2021-11-16", max(row["date"] for row in regular))
for index, fields in enumerate(groups):
    start = date(2021,11,16) + timedelta(days=7*index)
    stop = start + timedelta(days=7)
    ids = sorted(row["game_id"] for row in regular if start.isoformat() <= row["date"] < stop.isoformat())
    found = next(row for row in bounded_windows if row["start"]==start.isoformat())
    subwindows = found["subwindows"]
    window = {"start":start.isoformat(), "stop_exclusive":stop.isoformat(), "real_game_ids":ids, "subwindows":subwindows}
    factor_ids = [f"TENDENCY_NATIVE_{number:03d}" for number in fields]
    plan = allocate_window(study, window, factor_ids, values, history, worldline="WL0005-RESEARCH-POSTQUAL-20261111", seed=original.reference["seed"])
    windows.append(plan)
    for op in window_operations(plan):
        if op["expected_before"] is None or op["target"] is None:
            print(json.dumps({"unresolved_dose":op,"legal":study.factors[op["factor_id"]].native["legal_boundary"]}))
            raise ValueError("FRESH_WINDOW_HAS_UNRESOLVED_DOSE")
        history.append(Exposure(plan["worldline_id"], op["factor_id"], op["team_id"], op["uid"], plan["start"],
                                op["target"], "PLANNED_NOT_APPLIED", None))
qualifications, selected = [], set()
used_research = {row["uid"] for plan in windows for row in plan["teams"].values()}
for number in (*groups[0], *groups[1], *groups[2], 16):
    factor = f"TENDENCY_NATIVE_{number:03d}"
    slot = resolve_tendency_slot(factor)
    choices = [row for row in pool if row["eligible"] and 0<=row["team"]<=29 and row["uid"] not in selected
               and row["uid"] in by_uid and slot.minimum <= values[factor,row["uid"]] <= slot.maximum]
    actor = min(choices, key=lambda row:(row["uid"] in used_research, row["team"], row["uid"]))
    selected.add(actor["uid"])
    before = values[factor,actor["uid"]]
    qualifications.append({"factor_id":factor,"field_id":slot.native_key,"team_id":actor["team"],"uid":actor["uid"],
                           "expected_before":before,"target":before+1 if before<slot.maximum else before-1})
summary = {"schema":"nba2k22.live.first_batch_candidate.v1","status":"FRESH_STATE_FROZEN",
           "source_report_sha256":receipt["source_report_sha256"],"raw_values_sha256":receipt["raw_slot_values_sha256"],
           "source_save_sha256":receipt["native_slot_sha256"],"cold_backup_sha256":receipt["cold_backup_sha256"],
           "pid":receipt["scene"]["epoch"]["pid"],"epoch":receipt["scene"]["epoch"],
           "native_today":receipt["scene"]["game_progress"],"slot":"MyLEAGUE0005",
           "remaining_regular_games":sum(row["phase"]=="REGULAR_SEASON" for row in fixtures.values()),
           "remaining_special_events":sum(row["phase"]!="REGULAR_SEASON" for row in fixtures.values()),
           "eligible_players":sum(row["eligible"] for row in pool),"qualifications":qualifications,
           "windows":windows,"planned_games":[len(plan["games"]) for plan in windows],
           "caps":{"qualification_setters":16,"research_setters":60,"calendar_calls":12},
           "qualification_worldline":"QUALIFICATION_ONLY_REQUIRES_HUMAN_RELOAD_BEFORE_RESEARCH",
           "unexecuted_transition":{"date":"2021-11-15","minutes":1170,
             "pending_game_ids":[row["game_id"] for row in fixtures.values() if row["date"]=="2021-11-15"]}}
(output / "FIRST_BATCH_FROZEN_PLAN.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print(json.dumps({key:summary[key] for key in ("planned_games","remaining_regular_games","remaining_special_events","eligible_players","unexecuted_transition")}))

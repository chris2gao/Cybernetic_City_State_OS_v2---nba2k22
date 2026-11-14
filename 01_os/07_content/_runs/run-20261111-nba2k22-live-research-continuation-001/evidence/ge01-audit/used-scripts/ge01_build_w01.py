"""Reuse pinned E0 eligibility and the existing five-factor allocator; no game access."""
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from types import ModuleType

REPO = Path(__file__).resolve().parents[5]
DOMAIN = REPO / "08_Domain_Applications/Antigravity_GM_Engine"
sys.path[:0] = [str(DOMAIN / "world_data_prototype"), str(DOMAIN / "research/rea_native_control")]
from factor_inventory import StudyInputs
from factor_assignment import allocate_window, windows_for_schedule
from factor_runner import digest, window_operations
from native_factor_slots import resolve_tendency_slot

ROOT = Path("C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime")
FRESH = ROOT / "clean-0005-01"
R0_SHA = "87826a88acd9bf927c97a74dee36c56f7e31c887"
R0_PATH = "01_os/07_content/_runs/run-20261106-nba2k22-vae-lab-e0-r0-001/e0_r0.py"


def load(path):
    return json.loads(path.read_bytes())


def write(name, value):
    with (ROOT / name).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    receipt = load(FRESH / "FRESH_BASELINE_RECEIPT.json")
    assert receipt["status"] == "CAPTURE_COMPLETE"
    report_path = FRESH / "fresh-capture/refresh-report.json"
    assert hashlib.sha256(report_path.read_bytes()).hexdigest() == receipt["source_report_sha256"]
    binding_raw = (FRESH / "world-0005/save.json").read_bytes()
    binding = json.loads(binding_raw)
    raw = subprocess.check_output(["git", "show", f"{R0_SHA}:{R0_PATH}"], cwd=REPO)
    module = ModuleType("ge01_pinned_e0")
    module.__file__ = str(REPO / R0_PATH)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    database = FRESH / "world-0005/world.sqlite"
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("BEGIN")
        manifest, pool, inventory, _ = module.build(conn, load(report_path), binding, binding_raw)
        schedule_unit = next(row["unit"]["unit_id"] for row in load(report_path)["sources"] if row["family"] == "schedule")
        rows = list(conn.execute("""
            SELECT CAST(g.native_game_id AS INT) game_id,x.scheduled_native_iso_date day,
                   CAST(h.native_team_id AS INT) home,CAST(a.native_team_id AS INT) away,
                   x.game_type_label game_type,s.status_code,s.is_final,x.played_native_iso_date played
            FROM games g JOIN game_source_checks x USING(game_id)
            JOIN game_state_observations s ON s.game_id=x.game_id AND s.unit_id=x.unit_id
            JOIN teams h ON h.team_id=g.home_team_id JOIN teams a ON a.team_id=g.away_team_id
            WHERE x.unit_id=? ORDER BY x.scheduled_native_iso_date,CAST(g.native_game_id AS INT)
        """, (schedule_unit,)))
    fixtures = {row["game_id"]: {"game_id": row["game_id"], "date": row["day"], "home_team_id": row["home"],
                                "away_team_id": row["away"], "phase": "REGULAR_SEASON" if row["game_type"] == "NORMAL" else "SCHEDULED_SPECIAL",
                                "scheduled_state": "PENDING" if row["status_code"] == "0" and row["played"] is None else "OTHER"}
                for row in rows if not row["is_final"]}
    original = StudyInputs.load(REPO / "01_os/07_content/_runs/run-20261108-nba2k22-full-factor-plan-001")
    players = tuple({"native_uid": str(row["uid"]), "native_team_id": str(row["team"]),
                     "eligible_now": str(row["eligible"]), "mean_minutes_recent_10min": str(row["mean_minutes"] or 0)} for row in pool)
    study = replace(original, fixtures=fixtures, players=players)
    subjects = load(FRESH / "fresh-16-slot-values.json")["rows"]
    values = {(factor, row["uid"]): value for row in subjects for factor, value in row["values"].items()}
    teams = {row["team"] for row in pool if row["eligible"]}
    last_regular = max(row["date"] for row in fixtures.values() if row["phase"] == "REGULAR_SEASON")
    windows = windows_for_schedule(fixtures, teams, "2021-11-16", last_regular)
    window = next(row for row in windows if row["start"] == "2021-11-16")
    factors = [f"TENDENCY_NATIVE_{number:03d}" for number in (1, 66, 2, 3, 27)]
    plan = allocate_window(study, window, factors, values, [], worldline=binding["worldline_id"], seed=original.reference["seed"])
    operations = [dict(op, native_key=resolve_tendency_slot(op["factor_id"]).native_key,
                       width_bits=8, neighborhood_bytes=99,
                       historical_qualification="APPLIED_WITH_INDEPENDENT_READBACK_20261111; ACCEPTANCE_TO_BE_EXPLICIT_IN_ENVELOPE")
                  for op in window_operations(plan)]
    assert len(operations) == 20 and all(type(row["expected_before"]) is int and type(row["target"]) is int for row in operations)
    calendars = [{"phase": "ENTRY_TRANSITION", "start": "2021-11-15", "stop_exclusive": "2021-11-16",
                  "entry_minutes": receipt["scene"]["game_progress"]["today_minutes_since_midnight_raw"],
                  "planned_finals": sorted(row["game_id"] for row in fixtures.values() if row["date"] == "2021-11-15"),
                  "next_day_controls": sorted(row["game_id"] for row in fixtures.values() if row["date"] == "2021-11-16")}]
    calendars += [dict(item, phase="W01", entry_minutes=0) for item in plan["subwindows"]]
    proposal = {"schema": "nba2k22.ge01.w01.proposal.v1", "status": "PROPOSED_AWAITING_HUMAN_CONFIRMATION",
                "baseline": receipt, "binding": binding, "database": str(database),
                "baseline_choice": "Human explicitly adopts current memory, including the 16 qualification offsets, as new T0",
                "human_baseline_decision_verbatim": "我们为什么不以这个为蓝本作为干净的存档，因为改了的数值也不影响什么，取决于后面我们是否还是用这份存档当作原始存档，我建议就以这个为原始的，开始。",
                "background_offsets": receipt["qualification_comparison"],
                "scientific_scope": "H/L/C conditional on this adopted T0; pre-T0 offsets retained as background, no assertion they have zero effect",
                "source": {"PR43": "5a1d270d82196fb78fb4f64e7a832813e1b9a6b5", "R0": R0_SHA,
                           "R0_source_path": R0_PATH, "R0_blob_sha256": hashlib.sha256(raw).hexdigest(),
                           "fresh_report_sha256": receipt["source_report_sha256"]},
                "eligibility_counts": manifest["counts"], "operations": operations, "calendar_windows": calendars,
                "W01_game_ids": sorted(window["real_game_ids"]), "maximum_setters": 20,
                "maximum_calendar_dispatches": len(calendars), "saves_or_restores": 0, "new_qualification_writes": 0,
                "engine_thread": "TO_BE_BOUND_BY_READ_ONLY_FRAME_OBSERVATION_BEFORE_DISPATCH",
                "unknown_policy": "RESERVE_AND_RECONCILE_NO_AUTOMATIC_REPLAY",
                "done": "20 planned treatment outcomes retained; all W01 finals and same-source boxes verified; new bound WorldData and H/L/C analysis with missingness/exposure limits",
                "created_at": datetime.now(timezone.utc).isoformat(), "plan_digest": digest(plan)}
    write("GE01_W01_PLAN.json", plan)
    write("GE01_W01_ENVELOPE_PROPOSAL.json", proposal)
    write("GE01_FRESH_ELIGIBILITY.json", {"manifest": manifest, "pool": pool, "inventory": inventory})
    print(json.dumps({"eligible": sum(row["eligible"] for row in pool), "W01_games": len(window["real_game_ids"]),
                      "setters": len(operations), "calendar_dispatches": len(calendars),
                      "entry_games": calendars[0]["planned_finals"], "plan_digest": digest(plan)}))


if __name__ == "__main__":
    main()

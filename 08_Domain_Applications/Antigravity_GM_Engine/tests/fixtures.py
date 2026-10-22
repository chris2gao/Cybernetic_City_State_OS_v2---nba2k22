"""Explicit synthetic data only; never a source for a production career."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_core.data_reader import DataReader


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def project(root, complete=False):
    root = Path(root)
    for name in ("gameplay_policy.json", "gm_policy.json"):
        put(root / "config" / name, json.loads((ROOT / "config" / name).read_text(encoding="utf-8")))
    career, batch = "synthetic_career", "SYNTHETIC_BATCH_1"
    published = root / "published"
    directory = published / "saves" / career / "batches" / batch
    put(published / "index.json", {"careers": {career: {"latest": f"saves/{career}/latest.json"}}})
    pointer = {"save_id": career, "batch_id": batch, "batch_path": f"saves/{career}/batches/{batch}",
               "data_updated_at": "2026-01-01T00:00:00Z", "uploaded_at": "2026-01-01T00:01:00Z",
               "upload_status": "UPLOADED", "purpose": "production", "game_date": "2021-11-20",
               "source_commit": "f" * 40}
    put(published / "saves" / career / "latest.json", pointer)
    states, staff = [], []
    for index in range(30):
        abbreviation = f"T{index:02d}"
        state = {"team_id": index, "team_abbr": abbreviation, "total_salary": 15_000_000 + index,
                 "budget": 20_000_000, "staff_budget": 1_000_000, "cash": 100_000,
                 "fan_interest": 0.5, "ticket_courtside": 100, "ticket_lower": 50, "ticket_upper": 20,
                 "total_wins": 12 if complete else None, "total_losses": 8 if complete else None,
                 "total_games": 20 if complete else None, "ortg": 110 if complete else None,
                 "drtg": 105 if complete else None, "data_source": "LIVE_MEMORY",
                 "poe_off_pace": 3, "poe_fastbreak": 3, "poe_off_reb": 3, "poe_def_reb": 3,
                 "poe_on_ball": 7, "poe_off_ball": 1, "poe_pnr_def": 1, "poe_help_def": 2}
        roster = [{"player_name": f"Synthetic {index}-{slot}", "team_id": index, "face_id": index * 10 + slot,
                   "position": position, "salary_current_year": 1_000_000 * (slot + 1), "contract_years_left": 2,
                   "overall_rating": 82 if complete else None, "age": 26 if complete else None,
                   "potential": 90 if complete else None, "data_source": "LIVE_MEMORY",
                   "three_point_rating": 80, "pass_accuracy_rating": 75, "speed_rating": 70, "perimeter_defense_rating": 72}
                  for slot, position in enumerate(("PG", "SG", "SF", "PF", "C"))]
        put(directory / "teams" / f"{abbreviation}.json", {
            "identity": {"team_id": index, "abbreviation": abbreviation, "name": f"Synthetic Team {index}", "city": "Test"},
            "state": state, "roster": roster})
        states.append(state)
        staff.append({"team_id": index, "name": f"Synthetic coach {index}", "role": "HEAD_COACH",
                      "contract_years": 2, "salary": 100_000, "offense": 80, "defense": 80})
    put(directory / "league.json", {"teams": states, "rules": {"salary_cap": 16_000_000, "luxury_tax_threshold": 18_000_000}})
    put(directory / "calculations.json", {"method": "SYNTHETIC_FIXTURE"})
    sources = [{"id": name, "status": "VERIFIED_PARTIAL_FIELDS"} for name in
               ("team_state", "active_rosters_contracts", "global_players")]
    sources.append({"id": "games_box_scores_standings", "status": "VERIFIED_OBSERVED_FIELDS" if complete else "NOT_OBSERVED"})
    put(directory / "source_coverage.json", {"sources": sources, "synthetic": True})
    put(directory / "staff.json", {"ownership_verified": complete, "records": staff if complete else []})
    return DataReader(root).read(career)


def proposal(data):
    return {"decision_id": "SYNTHETIC_REVIEW", "version": 1, "career_id": data.source.career_id,
            "source_batch_id": data.source.batch_id, "teams": ["T00"], "operation": "STRATEGY", "status": "PROPOSED",
            "evidence": [{"file": "teams/T00.json", "field": "state.total_salary", "availability": "OBSERVED",
                          "source_batch_id": data.source.batch_id}], "calculation_refs": [],
            "expected_effect": "Synthetic review only, not a real game decision", "data_gaps": [],
            "requested_approval": ["Review this synthetic strategic direction"]}

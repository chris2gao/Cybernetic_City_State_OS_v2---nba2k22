"""Rebuild the coverage ledger from pinned Git sources, without a second registry."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
NBA = "bb73a06e710158c538caf809a771eca291eee028"
STAGE02 = "c812042e087f4c7000d27ac42d3839741039c188"
DESIGN = "de874b64f40808269f8d68e3474989197d47e8fa"
S4 = "01_os/07_content/_runs/run-20261106-nba2k22-host-rea-authorized-live-loop-001/mainline-integration/portable-live-closeout.json"
DOMAIN = "08_Domain_Applications/Antigravity_GM_Engine/"
STAGE_MATRIX = "01_os/07_content/_runs/run-20261101-nba2k22-vae-stage02-mechanism-metric-evidence-001/06_执行/field_evidence_matrix.json"
TENDENCY = DOMAIN + "docs/game_mechanics/catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json"
COACH = DOMAIN + "research/rea_native_control/data/coach_settings.json"


def source(commit, path):
    raw = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)
    return json.loads(raw), {"commit": commit, "path": path, "sha256": hashlib.sha256(raw).hexdigest()}


def build():
    matrix, matrix_ref = source(STAGE02, STAGE_MATRIX)
    slots, slots_ref = source(DESIGN, TENDENCY)
    coach, coach_ref = source(DESIGN, COACH)
    _, live_ref = source(NBA, S4)
    rows = []
    for field in matrix["fields"]:
        field_id = field["field_id"]
        eligible = field_id == "TENDENCY_NATIVE_001"
        unknown = field["family"] == "player_tendency" and field["seed_status"] != "NAMED_NATIVE"
        row = {
            "field_id": field_id, "inventory": "stage02_observation",
            "name": field.get("display_name"), "canonical_key": field.get("canonical_seed_key"),
            "family": field["family"], "source_ordinal": field["ordinal"],
            "mapping": field["seed_status"], "declared_raw_range": field.get("seed_raw_range"),
            "engine_scope": field["applicability"],
            "sweep_source_grade": field.get("gpt", {}).get("source_grade"),
            "sweep_native_claim": field.get("gemini", {}).get("executor_claimed_native_grade"),
            "evidence_axes": field["evidence_axes"],
            "contradictions": field.get("known_conflicts", []),
            "candidate_metrics": field.get("proposed_metrics", []),
            "remaining_gap": field.get("data_gap"),
            "setter_qualification": ("S4_BOUNDED_LIVE_VERIFIED" if eligible else
                                     "READ_ONLY_UNKNOWN" if unknown else "WRITER_UNVERIFIED"),
            "effect_status": "UNTESTED",
            "experiment_factor_id": "SHOT_TENDENCY" if eligible else None,
            "eligible_for_live_round_now": False,
        }
        if eligible:
            if row["name"] != "SHOT_TENDENCY":
                raise ValueError("S4 identity crosswalk changed")
            row.update(
                native_writer={"source": "s4_live", "action": "PLAYER_PATCH_TENDENCIES",
                               "field": "SHOT_TENDENCY", "same_team_items": [1, 3]},
                endpoint_contract={
                    "mode": "CALENDAR_SIM", "assignment_unit": "team",
                    "experimental_subject": "one preselected native player UID per team",
                    "opportunity": "frozen scheduled game, explicit roster and minutes disposition",
                    "primary": ["PLAYER_FGA_PER_SCHEDULED_OPPORTUNITY"],
                    "secondary": ["MINUTES", "FGA_PER_36", "TEAM_FGA_SHARE", "TEAMMATE_FGA"],
                    "unknown": ["ACTUAL_TOUCHES", "SHOT_LOCATION"],
                },
                confirmed_scope="historical native Setter and Getter/CAS on bounded S4 path",
                remaining_gap="fresh save and schedule, batch authority, calendar safety gate, causal evidence",
                next_test="first bounded H/L/C screen",
            )
        rows.append(row)
    for name, projection in sorted(coach["fields"].items()):
        rows.append({
            "field_id": "COACH_PROJECTION/" + name, "inventory": "coach_projection",
            "name": name, "family": "coach_projection", "projection": projection,
            "setter_qualification": "WRITER_UNVERIFIED", "effect_status": "UNTESTED",
            "experiment_factor_id": None, "eligible_for_live_round_now": False,
            "remaining_gap": "explicit Stage02 semantic crosswalk and per-field writer/effect qualification",
        })
    observation = [row for row in rows if row["inventory"] == "stage02_observation"]
    tendencies = [row for row in observation if row["family"] == "player_tendency"]
    named = sum(row["mapping"] == "NAMED_NATIVE" for row in tendencies)
    source_range = slots["player_native_range"]
    if (len(observation), len(tendencies), named, len(tendencies) - named, len(coach["fields"])) != (
        matrix["total_fields"], source_range["total"], source_range["named"], source_range["unknown"], 10
    ) or len({row["field_id"] for row in rows}) != len(rows):
        raise ValueError("Inventory sources no longer reconcile")
    return {
        "schema": "nba2k22.vae.mechanism_research_ledger.v1",
        "sources": {"stage02": matrix_ref, "tendency_catalog": slots_ref, "coach_projection": coach_ref,
                    "s4_live": live_ref, "single_field_sweep": matrix["source_bindings"]},
        "coverage": {"stage02_observation_fields": len(observation),
                     "stage02_family_counts": matrix["family_counts"],
                     "tendency_subset": {"total": len(tendencies), "named": named,
                                         "unknown_read_only": len(tendencies) - named},
                     "coach_projection_candidates": len(coach["fields"]),
                     "projection_overlap": "CROSSWALK_OPEN_DO_NOT_ADD_AS_UNIQUE_FACTORS",
                     "historical_bounded_live_writer_fields": sum(
                         row["setter_qualification"] == "S4_BOUNDED_LIVE_VERIFIED" for row in rows),
                     "currently_granted": 0, "screened_in_program": 0, "replicated_in_program": 0,
                     "confirmed_causal_in_program": 0,
                     "operational_endpoint_count": None,
                     "operational_endpoint_count_reason": "requires verified per-mode source and current coverage"},
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))

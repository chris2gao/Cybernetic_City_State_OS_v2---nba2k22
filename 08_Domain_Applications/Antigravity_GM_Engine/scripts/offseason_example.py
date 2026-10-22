"""Prepare a clearly synthetic 30-team input for future authorized offline tests.

This command does not run the planner, tests, game capture, or any writer.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_core.offseason_io import local_output


def example():
    teams = [{"team_id": 100 + i * 2, "payroll_current": 80000000,
              "projected_next_year_committed_payroll": 80000000,
              "validated_cap_room": 20000000, "signing_spending_limit": 12000000,
              "available_slots": 2, "cash": None, "budget": None,
              "game_eligibility": {}, "exception_budgets": {},
              "strategy": {"source": "SYNTHETIC_CONFIG_NOT_GM_APPROVAL", "candidate_offers": {}}}
             for i in range(30)]
    candidates = []
    limits = {}
    for cid, home, status in (("synthetic_a", 100, "VERIFIED_UFA"),
                              ("synthetic_b", 102, "VERIFIED_UFA"),
                              ("synthetic_c", 104, "VERIFIED_RFA")):
        candidates.append({"candidate_id": cid, "display_name": f"SYNTHETIC {cid}",
            "verified_player_identity": {"entity_id": cid, "scheme": "SYNTHETIC",
                                          "continuity_ref": f"synthetic_fixture:{cid}"},
            "previous_team_id": home, "origin": "EXPIRING", "contract_years_left": 1,
            "next_season_salary_slots": [0], "option_status": "NO_OPTION", "extension_status": "NONE",
            "expiry_verified_for": "2021-2022", "expiry_evidence_ref": "SYNTHETIC_TRANSITION",
            "free_agency_status": status, "bird_rights_status": "SYNTHETIC_VERIFIED",
            "asking_salary": 6000000, "home_preference": 0,
            "roster_provenance": "SYNTHETIC_ROSTER", "qualifying_offer": {
                "valid": True, "evidence_ref": "SYNTHETIC_QO", "matching_right": True,
                "matching_right_evidence_ref": "SYNTHETIC_RFA_MATCHING"}})
        limits[cid] = {path: {"minimum_salary": 1000000, "maximum_salary": 10000000,
                             "maximum_years": 4, "maximum_raise_bps": 500,
                             "evidence_ref": "SYNTHETIC_LIMITS_NOT_NBA_RULES"}
                       for path in ("CAP_SPACE", "VERIFIED_BIRD")}
        for team in teams:
            team["game_eligibility"][cid] = {"CAP_SPACE": {"status": "SYNTHETIC_VERIFIED",
                                                           "evidence_ref": "SYNTHETIC_CAP_ELIGIBILITY"}}
            team["strategy"]["candidate_offers"][cid] = {"role_score": 80 if team["team_id"] == 106 else 0}
            if team["team_id"] == home:
                team["game_eligibility"][cid]["VERIFIED_BIRD"] = {
                    "status": "SYNTHETIC_VERIFIED", "evidence_ref": "SYNTHETIC_BIRD"}
    return {"schema_version": 1, "purpose": "SIMULATION", "synthetic": True,
        "source_profile": "SYNTHETIC_OFFSEASON_V1", "save_id": "synthetic_offseason",
        "completed_season": "2021-2022", "target_season": "2022-2023",
        "offseason_run_id": "SYNTHETIC_EXAMPLE", "proposal_version": 1,
        "source_batch_id": "SYNTHETIC_BATCH", "data_updated_at": "2026-10-17T00:00:00+00:00",
        "game_state_version": "SYNTHETIC_STATE_V1", "policy_id": "PLAYER_RULES_20261017_V3",
        "rules_version": "SYNTHETIC_RULES_V1", "game_phase": "SYNTHETIC_OFFSEASON_FROZEN",
        "native_ai_control_status": "SYNTHETIC_CONTAINED", "free_agent_pool_coverage": "SYNTHETIC_ONLY",
        "season_rules": {"2022-2023": {"status": "SYNTHETIC_VERIFIED", "evidence_ref": "SYNTHETIC_SEASON",
            "cap": 100000000, "tax_line": 120000000, "apron": 130000000,
            "heuristic_salary_bps": 10000, "candidate_limits": limits}},
        "teams": teams, "candidates": candidates}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="New directory below _exports")
    args = parser.parse_args()
    output = local_output(ROOT, args.output)
    output.mkdir(parents=True, exist_ok=False)
    data = example()
    (output / "synthetic_input.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    context = {key: data[key] for key in ("save_id", "completed_season", "target_season", "source_batch_id",
        "data_updated_at", "game_state_version", "policy_id", "rules_version", "game_phase", "native_ai_control_status")}
    (output / "synthetic_context.json").write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "SYNTHETIC_INPUT_ONLY", "output": str(output)}))


if __name__ == "__main__":
    main()

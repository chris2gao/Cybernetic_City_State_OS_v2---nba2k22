# -*- coding: utf-8 -*-
"""
NBA2K22 · NATIVE-INGREDIENTS-GEMINI-R02 Verification Suite
Automated verification for OS Managed Verify run and inspect.
"""

import sys
import os
import json
import hashlib
from pathlib import Path

PINNED_POLICY_SHA256 = "c95b696c0210b944520eec96d2a288ba8dc26fd2a6deeb1326ea6d55d4798abc"
PINNED_IMAGE_SHA256 = "1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5"
TOTAL_BUDGET = 3058

def get_research_dir():
    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / "08_Domain_Applications" / "Antigravity_GM_Engine" / "research" / "native_access" / "NATIVE_INGREDIENTS_GEMINI_R02"

def check_policy_and_provenance():
    rdir = get_research_dir()
    policy_file = rdir / "policy_manifest.json"
    if not policy_file.exists():
        print("FAIL: policy_manifest.json missing", file=sys.stderr)
        return False
        
    actual_hash = hashlib.sha256(policy_file.read_bytes()).hexdigest()
    if actual_hash != PINNED_POLICY_SHA256:
        print(f"FAIL: policy hash mismatch: {actual_hash} != {PINNED_POLICY_SHA256}", file=sys.stderr)
        return False
        
    res_file = rdir / "gemini_r02_discovery_results.json"
    if not res_file.exists():
        print("FAIL: gemini_r02_discovery_results.json missing", file=sys.stderr)
        return False
        
    with open(res_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    prov = data.get("provenance", {})
    if prov.get("expected_image_sha256") != PINNED_IMAGE_SHA256:
        print("FAIL: image hash mismatch in provenance", file=sys.stderr)
        return False
        
    if prov.get("save_binding_status") != "SAVE_UNBOUND":
        print("FAIL: save binding status is not SAVE_UNBOUND", file=sys.stderr)
        return False
        
    boot = data.get("phases", {}).get("BOOTSTRAP", {})
    if boot.get("bytes_read") != 1208:
        print("FAIL: bootstrap bytes read != 1208", file=sys.stderr)
        return False
        
    if boot.get("active_slot_count") != 67 or boot.get("empty_slot_count") != 8:
        print("FAIL: unexpected active/empty slot counts", file=sys.stderr)
        return False
        
    print("PASS: CHECK_POLICY_AND_PROVENANCE")
    return True

def check_gm_chain_closure():
    rdir = get_research_dir()
    with open(rdir / "gemini_r02_discovery_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    gm = data.get("phases", {}).get("PHASE_A_GM", {})
    if gm.get("bytes_read") != 816:
        print("FAIL: PHASE_A_GM bytes read != 816", file=sys.stderr)
        return False
        
    dc_recs = gm.get("dead_cap_records", [])
    if len(dc_recs) != 3:
        print("FAIL: dead cap records length != 3", file=sys.stderr)
        return False
        
    # Check DeadCap owners: DC0 -> Team 4, DC1 -> Team 4, DC2 -> Team 9
    if dc_recs[0]["owner_team_index"] != 4 or dc_recs[1]["owner_team_index"] != 4 or dc_recs[2]["owner_team_index"] != 9:
        print("FAIL: DeadCap owner team indices mismatch", file=sys.stderr)
        return False
        
    # Check DeadCap next pointers: DC1 points to DC0, DC0 points to 0x0
    if dc_recs[1]["next_pointer"] != dc_recs[0]["address"] or dc_recs[0]["next_pointer"] != "0x0":
        print("FAIL: DeadCap next pointers do not form valid list", file=sys.stderr)
        return False
        
    te_recs = gm.get("trade_exception_records", [])
    if len(te_recs) != 3:
        print("FAIL: trade exception records length != 3", file=sys.stderr)
        return False
        
    # Check TPE owners: TE0 -> Team 2, TE1 -> Team 3, TE2 -> Team 3
    if te_recs[0]["owner_team_index"] != 2 or te_recs[1]["owner_team_index"] != 3 or te_recs[2]["owner_team_index"] != 3:
        print("FAIL: TPE owner team indices mismatch", file=sys.stderr)
        return False
        
    # Check TPE next pointers: TE1 points to TE2, TE2 points to 0x0
    if te_recs[1]["next_pointer"] != te_recs[2]["address"] or te_recs[2]["next_pointer"] != "0x0":
        print("FAIL: TPE next pointers do not form valid list", file=sys.stderr)
        return False
        
    # Check Team Heads
    team_heads = {h["team_index"]: h for h in gm.get("team_heads", [])}
    if team_heads[4]["dead_cap_head"] != dc_recs[1]["address"]:
        print("FAIL: Team 4 DeadCap head does not point to DC1", file=sys.stderr)
        return False
    if team_heads[9]["dead_cap_head"] != dc_recs[2]["address"]:
        print("FAIL: Team 9 DeadCap head does not point to DC2", file=sys.stderr)
        return False
    if team_heads[2]["trade_exception_head"] != te_recs[0]["address"]:
        print("FAIL: Team 2 TPE head does not point to TE0", file=sys.stderr)
        return False
    if team_heads[3]["trade_exception_head"] != te_recs[1]["address"]:
        print("FAIL: Team 3 TPE head does not point to TE1", file=sys.stderr)
        return False
        
    print("PASS: CHECK_GM_CHAIN_CLOSURE")
    return True

def check_player_full_names_and_selectors():
    rdir = get_research_dir()
    with open(rdir / "gemini_r02_discovery_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    pl = data.get("phases", {}).get("PHASE_B_PLAYER", {})
    if pl.get("bytes_read") != 836:
        print("FAIL: PHASE_B_PLAYER bytes read != 836", file=sys.stderr)
        return False
        
    players = pl.get("players", [])
    if len(players) != 2:
        print("FAIL: expected 2 players", file=sys.stderr)
        return False
        
    p0, p1 = players[0], players[1]
    if p0["full_name"] != "Ben Simmons" or p1["full_name"] != "Seth Curry":
        print(f"FAIL: full names mismatch: '{p0['full_name']}', '{p1['full_name']}'", file=sys.stderr)
        return False
        
    # Check 25 selectors and hole
    if len(p0["all_25_selectors"]) != 25 or len(p1["all_25_selectors"]) != 25:
        print("FAIL: selectors array length != 25", file=sys.stderr)
        return False
        
    if p1["all_25_selectors"][4] != -1 or p1["all_25_selectors"][5] == -1:
        print("FAIL: expected hole at selector 4 for Seth Curry", file=sys.stderr)
        return False
        
    # Check stat83 games played
    stats = pl.get("stat_rows", [])
    if len(stats) != 12:
        print("FAIL: stat rows length != 12", file=sys.stderr)
        return False
        
    gp_sim = [r["stat83_games_played"] for r in stats[:5]]
    if gp_sim != [16, 58, 57, 79, 81]:
        print(f"FAIL: unexpected Simmons games played: {gp_sim}", file=sys.stderr)
        return False
        
    gp_curry = [r["stat83_games_played"] for r in stats[5:]]
    if gp_curry != [16, 57, 64, 74, 70, 44, 2]:
        print(f"FAIL: unexpected Curry games played: {gp_curry}", file=sys.stderr)
        return False
        
    print("PASS: CHECK_PLAYER_FULL_NAMES_AND_SELECTORS")
    return True

def check_draft_relations_and_teams():
    rdir = get_research_dir()
    with open(rdir / "gemini_r02_discovery_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    draft = data.get("phases", {}).get("PHASE_C_DRAFT", {})
    if draft.get("bytes_read") != 198:
        print("FAIL: PHASE_C_DRAFT bytes read != 198", file=sys.stderr)
        return False
        
    rows = draft.get("draft_rows", [])
    if len(rows) != 6:
        print("FAIL: expected 6 draft rows", file=sys.stderr)
        return False
        
    # Pick 0 is simple own pick, Pick 1 is traded pick
    if rows[0]["is_traded"] or not rows[1]["is_traded"]:
        print("FAIL: draft traded discrimination failed", file=sys.stderr)
        return False
        
    if rows[0]["token_hex"] != "0xffffffff" or rows[1]["token_hex"] != "0x2e0001f":
        print("FAIL: draft tokens mismatch", file=sys.stderr)
        return False
        
    teams = draft.get("draft_teams", [])
    if len(teams) != 3:
        print("FAIL: expected 3 draft teams", file=sys.stderr)
        return False
        
    team_ids = [t["team_id"] for t in teams]
    if team_ids != [14, 31, 2]:
        print(f"FAIL: unexpected team IDs: {team_ids}", file=sys.stderr)
        return False
        
    print("PASS: CHECK_DRAFT_RELATIONS_AND_TEAMS")
    return True

def check_audit_log_and_budget():
    rdir = get_research_dir()
    audit_file = rdir / "read_audit_log.json"
    if not audit_file.exists():
        print("FAIL: read_audit_log.json missing", file=sys.stderr)
        return False
        
    with open(audit_file, "r", encoding="utf-8") as f:
        log = json.load(f)
        
    if len(log) != 41:
        print(f"FAIL: expected 41 audit calls, got {len(log)}", file=sys.stderr)
        return False
        
    total_bytes = sum(e["size"] for e in log)
    if total_bytes != TOTAL_BUDGET:
        print(f"FAIL: total bytes read {total_bytes} != {TOTAL_BUDGET}", file=sys.stderr)
        return False
        
    if any(e["status"] != "SUCCESS" for e in log):
        print("FAIL: one or more audit calls failed", file=sys.stderr)
        return False
        
    # Check companion files
    if not (rdir / "food_gap_delta.json").exists():
        print("FAIL: food_gap_delta.json missing", file=sys.stderr)
        return False
    if not (rdir / "codex_next_round_materials.json").exists():
        print("FAIL: codex_next_round_materials.json missing", file=sys.stderr)
        return False
    if not (rdir / "NATIVE_INGREDIENTS_GEMINI_R02_REPORT.md").exists():
        print("FAIL: NATIVE_INGREDIENTS_GEMINI_R02_REPORT.md missing", file=sys.stderr)
        return False
        
    print("PASS: CHECK_AUDIT_LOG_AND_BUDGET")
    return True

def main():
    check_id = sys.argv[1] if len(sys.argv) > 1 else "ALL"
    checks = {
        "CHECK_POLICY_AND_PROVENANCE": check_policy_and_provenance,
        "CHECK_GM_CHAIN_CLOSURE": check_gm_chain_closure,
        "CHECK_PLAYER_FULL_NAMES_AND_SELECTORS": check_player_full_names_and_selectors,
        "CHECK_DRAFT_RELATIONS_AND_TEAMS": check_draft_relations_and_teams,
        "CHECK_AUDIT_LOG_AND_BUDGET": check_audit_log_and_budget
    }
    
    if check_id == "ALL":
        for name, fn in checks.items():
            if not fn():
                sys.exit(1)
        sys.exit(0)
    elif check_id in checks:
        if not checks[check_id]():
            sys.exit(1)
        sys.exit(0)
    else:
        print(f"Unknown check id: {check_id}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

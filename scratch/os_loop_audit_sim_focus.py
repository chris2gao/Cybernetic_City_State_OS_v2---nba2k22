import os, sys, re, json, hashlib, sqlite3

local_dir = r'08_Domain_Applications/Antigravity_GM_Engine/database/tactics/20261123_simulated_gameplan_focus_execution'
exports_dir = r'C:\nba2k22\exports\20261123_simulated_gameplan_focus_execution'
db_path = r'C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite'

team_order = [
    (0, "PHI", "Philadelphia 76ers", "56_PHI_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (1, "MIL", "Milwaukee Bucks", "53_MIL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (2, "WAS", "Washington Wizards", "76_WAS_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (3, "CHI", "Chicago Bulls", "63_CHI_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (4, "CLE", "Cleveland Cavaliers", "66_CLE_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (5, "BOS", "Boston Celtics", "51_BOS_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (6, "LAC", "LA Clippers", "61_LAC_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (8, "MEM", "Memphis Grizzlies", "58_MEM_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (9, "ATL", "Atlanta Hawks", "65_ATL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (10, "MIA", "Miami Heat", "52_MIA_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (11, "NOP", "New Orleans Pelicans", "68_NOP_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (12, "UTA", "Utah Jazz", "60_UTA_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (13, "SAC", "Sacramento Kings", "73_SAC_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (14, "NYK", "New York Knicks", "71_NYK_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (15, "LAL", "Los Angeles Lakers", "62_LAL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (16, "ORL", "Orlando Magic", "78_ORL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (17, "DAL", "Dallas Mavericks", "55_DAL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (18, "BKN", "Brooklyn Nets", "59_BKN_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (19, "DEN", "Denver Nuggets", "57_DEN_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (20, "IND", "Indiana Pacers", "70_IND_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (21, "DET", "Detroit Pistons", "77_DET_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (22, "TOR", "Toronto Raptors", "64_TOR_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (23, "HOU", "Houston Rockets", "79_HOU_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (24, "OKC", "Oklahoma City Thunder", "72_OKC_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (25, "SAS", "San Antonio Spurs", "74_SAS_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (26, "PHX", "Phoenix Suns", "54_PHX_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (27, "MIN", "Minnesota Timberwolves", "67_MIN_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (28, "POR", "Portland Trail Blazers", "69_POR_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (29, "GSW", "Golden State Warriors", "50_GSW_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (31, "CHA", "Charlotte Hornets", "75_CHA_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md")
]

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT team_id, roster_slot, player_name, face_id FROM player_source_details")
db_players = {}
for tid, slot, name, fid in cur.fetchall():
    if tid not in db_players: db_players[tid] = set()
    db_players[tid].add(fid)
conn.close()

def sha256_file(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

print("================================================================================")
print("              CITY-STATE OS LOOP CONVERGENCE AUDIT: SIMULATED FOCUS")
print("================================================================================")

audit_receipt = {
    "total_teams": len(team_order),
    "teams_passed": 0,
    "teams_failed": 0,
    "total_checks": 0,
    "passed_checks": 0,
    "failed_checks": 0,
    "discrepancies": [],
    "team_details": []
}

expected_offsets = [376, 378, 380, 382, 383, 384, 385, 386, 387]
expected_types = ["uint16", "uint16", "uint16", "uint8", "uint8", "uint8", "uint8", "uint8", "uint8"]

for idx, (tid, abbr, tname, doc_name) in enumerate(team_order, 1):
    fname = f"{tid:02d}_{abbr}_sim_focus_mod.json"
    local_p = os.path.join(local_dir, fname)
    export_p = os.path.join(exports_dir, fname)
    
    team_res = {
        "team_id": tid,
        "team_abbr": abbr,
        "filename": fname,
        "checks_passed": 0,
        "checks_failed": 0,
        "status": "PASS"
    }
    
    # 1. Existence
    audit_receipt["total_checks"] += 2
    if os.path.exists(local_p):
        audit_receipt["passed_checks"] += 1
        team_res["checks_passed"] += 1
    else:
        audit_receipt["failed_checks"] += 1
        team_res["checks_failed"] += 1
        audit_receipt["discrepancies"].append(f"Missing local file: {local_p}")
        
    if os.path.exists(export_p):
        audit_receipt["passed_checks"] += 1
        team_res["checks_passed"] += 1
    else:
        audit_receipt["failed_checks"] += 1
        team_res["checks_failed"] += 1
        audit_receipt["discrepancies"].append(f"Missing export file: {export_p}")
        
    if not os.path.exists(local_p) or not os.path.exists(export_p):
        team_res["status"] = "FAIL"
        audit_receipt["teams_failed"] += 1
        audit_receipt["team_details"].append(team_res)
        continue
        
    # 2. SHA-256 Mirror Match
    audit_receipt["total_checks"] += 1
    h_local = sha256_file(local_p)
    h_export = sha256_file(export_p)
    if h_local == h_export:
        audit_receipt["passed_checks"] += 1
        team_res["checks_passed"] += 1
    else:
        audit_receipt["failed_checks"] += 1
        team_res["checks_failed"] += 1
        audit_receipt["discrepancies"].append(f"SHA mismatch for {fname}: local={h_local} != export={h_export}")
        
    # 3. Content Inspection
    with open(local_p, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Check top metadata
    audit_receipt["total_checks"] += 4
    if data.get('protocol_version') == 'v2.0_full_dimensional_native_mod':
        audit_receipt["passed_checks"] += 1
        team_res["checks_passed"] += 1
    else:
        audit_receipt["failed_checks"] += 1
        team_res["checks_failed"] += 1
        audit_receipt["discrepancies"].append(f"{fname}: protocol_version invalid")
        
    if data.get('team_id') == tid and data.get('team_abbr') == abbr:
        audit_receipt["passed_checks"] += 1
        team_res["checks_passed"] += 1
    else:
        audit_receipt["failed_checks"] += 1
        team_res["checks_failed"] += 1
        audit_receipt["discrepancies"].append(f"{fname}: team identity mismatch")
        
    if data.get('source_research_doc') == doc_name:
        audit_receipt["passed_checks"] += 1
        team_res["checks_passed"] += 1
    else:
        audit_receipt["failed_checks"] += 1
        team_res["checks_failed"] += 1
        audit_receipt["discrepancies"].append(f"{fname}: source_research_doc mismatch")
        
    writes = data.get('writes', [])
    if len(writes) == 9:
        audit_receipt["passed_checks"] += 1
        team_res["checks_passed"] += 1
    else:
        audit_receipt["failed_checks"] += 1
        team_res["checks_failed"] += 1
        audit_receipt["discrepancies"].append(f"{fname}: writes length != 9 (found {len(writes)})")
        
    # 4. Check all 9 writes
    opt_pids = []
    for w_idx, w in enumerate(writes):
        audit_receipt["total_checks"] += 3
        # offset check
        if w.get('offset') == expected_offsets[w_idx]:
            audit_receipt["passed_checks"] += 1
            team_res["checks_passed"] += 1
        else:
            audit_receipt["failed_checks"] += 1
            team_res["checks_failed"] += 1
            audit_receipt["discrepancies"].append(f"{fname}: write[{w_idx}] offset {w.get('offset')} != expected {expected_offsets[w_idx]}")
            
        # type check
        if w.get('type') == expected_types[w_idx]:
            audit_receipt["passed_checks"] += 1
            team_res["checks_passed"] += 1
        else:
            audit_receipt["failed_checks"] += 1
            team_res["checks_failed"] += 1
            audit_receipt["discrepancies"].append(f"{fname}: write[{w_idx}] type {w.get('type')} != expected {expected_types[w_idx]}")
            
        # value range check
        val = w.get('val_raw')
        if w_idx in [0, 1, 2]:
            opt_pids.append(val)
            # check if player is in this team's roster
            if val in db_players.get(tid, set()):
                audit_receipt["passed_checks"] += 1
                team_res["checks_passed"] += 1
            else:
                audit_receipt["failed_checks"] += 1
                team_res["checks_failed"] += 1
                audit_receipt["discrepancies"].append(f"{fname}: Scoring Option {w_idx+1} player_id {val} not in team {tid} roster!")
        elif w_idx == 3: # poe_offense (1..6)
            if 1 <= val <= 6:
                audit_receipt["passed_checks"] += 1
                team_res["checks_passed"] += 1
            else:
                audit_receipt["failed_checks"] += 1
                team_res["checks_failed"] += 1
                audit_receipt["discrepancies"].append(f"{fname}: poe_offense {val} out of bounds [1..6]")
        elif w_idx == 4: # poe_offense_tempo (7..9)
            if 7 <= val <= 9:
                audit_receipt["passed_checks"] += 1
                team_res["checks_passed"] += 1
            else:
                audit_receipt["failed_checks"] += 1
                team_res["checks_failed"] += 1
                audit_receipt["discrepancies"].append(f"{fname}: poe_offense_tempo {val} out of bounds [7..9]")
        elif w_idx == 5: # poe_offense_rebound (10..12)
            if 10 <= val <= 12:
                audit_receipt["passed_checks"] += 1
                team_res["checks_passed"] += 1
            else:
                audit_receipt["failed_checks"] += 1
                team_res["checks_failed"] += 1
                audit_receipt["discrepancies"].append(f"{fname}: poe_offense_rebound {val} out of bounds [10..12]")
        elif w_idx == 6: # poe_defense (13..15)
            if 13 <= val <= 15:
                audit_receipt["passed_checks"] += 1
                team_res["checks_passed"] += 1
            else:
                audit_receipt["failed_checks"] += 1
                team_res["checks_failed"] += 1
                audit_receipt["discrepancies"].append(f"{fname}: poe_defense {val} out of bounds [13..15]")
        elif w_idx == 7: # poe_defense_physicality (16..18)
            if 16 <= val <= 18:
                audit_receipt["passed_checks"] += 1
                team_res["checks_passed"] += 1
            else:
                audit_receipt["failed_checks"] += 1
                team_res["checks_failed"] += 1
                audit_receipt["discrepancies"].append(f"{fname}: poe_defense_physicality {val} out of bounds [16..18]")
        elif w_idx == 8: # poe_defense_rebound (19..21)
            if 19 <= val <= 21:
                audit_receipt["passed_checks"] += 1
                team_res["checks_passed"] += 1
            else:
                audit_receipt["failed_checks"] += 1
                team_res["checks_failed"] += 1
                audit_receipt["discrepancies"].append(f"{fname}: poe_defense_rebound {val} out of bounds [19..21]")

    # Check distinct options
    audit_receipt["total_checks"] += 1
    if len(set(opt_pids)) == 3:
        audit_receipt["passed_checks"] += 1
        team_res["checks_passed"] += 1
    else:
        audit_receipt["failed_checks"] += 1
        team_res["checks_failed"] += 1
        audit_receipt["discrepancies"].append(f"{fname}: Duplicate player IDs in scoring options: {opt_pids}")
        
    if team_res["checks_failed"] == 0:
        team_res["status"] = "PASS"
        audit_receipt["teams_passed"] += 1
        print(f"[{idx:02d}/30] Team {abbr} ({tid:02d}) AUDIT PASSED ({team_res['checks_passed']}/{team_res['checks_passed']} checks) | SHA: {h_local[:10]}...")
    else:
        team_res["status"] = "FAIL"
        audit_receipt["teams_failed"] += 1
        print(f"[{idx:02d}/30] Team {abbr} ({tid:02d}) AUDIT FAILED ({team_res['checks_failed']} errors)!")
        
    audit_receipt["team_details"].append(team_res)

print("\n================================================================================")
print(f"AUDIT SUMMARY: Teams Passed: {audit_receipt['teams_passed']}/30 | Checks: {audit_receipt['passed_checks']}/{audit_receipt['total_checks']}")
if audit_receipt['failed_checks'] == 0:
    print("STATUS: ZERO DISCREPANCIES (100% MATHEMATICAL CONVERGENCE)")
else:
    print(f"STATUS: FAILED with {audit_receipt['failed_checks']} errors!")
    for d in audit_receipt['discrepancies']:
        print(f"  - {d}")
print("================================================================================")

# Write audit receipt
receipt_path = os.path.join(local_dir, "30_TEAMS_SIM_FOCUS_VERIFICATION_RECEIPT.json")
with open(receipt_path, 'w', encoding='utf-8') as f:
    json.dump(audit_receipt, f, indent=2, ensure_ascii=False)
    
export_receipt_path = os.path.join(exports_dir, "30_TEAMS_SIM_FOCUS_VERIFICATION_RECEIPT.json")
with open(export_receipt_path, 'w', encoding='utf-8') as f:
    json.dump(audit_receipt, f, indent=2, ensure_ascii=False)
    
print(f"Verification receipt saved to:")
print(f"  Local:   {receipt_path}")
print(f"  Exports: {export_receipt_path}")

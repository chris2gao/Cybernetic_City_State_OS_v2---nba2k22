# -*- coding: utf-8 -*-
"""
NBA2K22 · NATIVE-INGREDIENTS-GEMINI-R01 Verification Suite
Automated verification for OS Managed Verify run and inspect.
"""

import sys
import os
import json
import hashlib
from pathlib import Path

EXPECTED_IMAGE_SHA256 = "1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5"
TOTAL_BUDGET = 5300

def get_research_dir():
    # Relative to repository root
    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / "08_Domain_Applications" / "Antigravity_GM_Engine" / "research" / "native_access" / "NATIVE_INGREDIENTS_GEMINI_R01"

def check_bind_and_provenance():
    rdir = get_research_dir()
    res_file = rdir / "ingredient_discovery_results.json"
    if not res_file.exists():
        print("FAIL: ingredient_discovery_results.json missing", file=sys.stderr)
        return False
        
    with open(res_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    prov = data.get("provenance", {})
    if prov.get("expected_image_sha256") != EXPECTED_IMAGE_SHA256:
        print("FAIL: unexpected image sha256 in provenance", file=sys.stderr)
        return False
        
    if prov.get("save_binding_status") != "GAME_CONTEXT_MATCHED_NOT_SAVE_BOUND":
        print("FAIL: invalid save binding status", file=sys.stderr)
        return False
        
    r01 = data.get("phases", {}).get("R01-BIND", {})
    if r01.get("bytes_read") != 1208:
        print("FAIL: R01-BIND bytes read != 1208", file=sys.stderr)
        return False
        
    if r01.get("active_slot_count") != 67 or r01.get("empty_slot_count") != 8:
        print("FAIL: unexpected active/empty slot counts in R01-BIND", file=sys.stderr)
        return False
        
    descriptors = r01.get("descriptors", [])
    if len(descriptors) != 75:
        print("FAIL: descriptors length != 75", file=sys.stderr)
        return False
        
    print("PASS: CHECK_BIND_AND_PROVENANCE")
    return True

def check_player_history_chain():
    rdir = get_research_dir()
    with open(rdir / "ingredient_discovery_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    r02 = data.get("phases", {}).get("R02-PLAYER-HISTORY", {})
    if r02.get("bytes_read") > 1262:
        print("FAIL: R02 bytes exceeded budget", file=sys.stderr)
        return False
        
    players = r02.get("players", [])
    if len(players) != 2:
        print("FAIL: expected 2 players in R02", file=sys.stderr)
        return False
        
    stat_rows = r02.get("slot24_career_stats_rows", [])
    if len(stat_rows) != 12:
        print("FAIL: expected 12 stat rows in R02", file=sys.stderr)
        return False
        
    # Check decrementing seasons for player 0 (high byte of uint16)
    p0_seasons = [int(r["season_code_hex"], 16) >> 8 for r in stat_rows if r["player_index"] == 0]
    if p0_seasons != [0x7A, 0x79, 0x78, 0x77, 0x76]:
        print(f"FAIL: p0 seasons not strictly decrementing: {p0_seasons}", file=sys.stderr)
        return False
        
    shot_charts = r02.get("slot26_shot_charts", [])
    if len(shot_charts) != 3 or any(sc["record_size"] != 114 for sc in shot_charts):
        print("FAIL: invalid shot charts in R02", file=sys.stderr)
        return False
        
    print("PASS: CHECK_PLAYER_HISTORY_CHAIN")
    return True

def check_draft_and_coach_book():
    rdir = get_research_dir()
    with open(rdir / "ingredient_discovery_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    r03 = data.get("phases", {}).get("R03-DRAFT-RELATIONS", {})
    if r03.get("bytes_read") > 486:
        print("FAIL: R03 bytes exceeded budget", file=sys.stderr)
        return False
        
    draft_recs = r03.get("draft_records", [])
    if len(draft_recs) != 6:
        print("FAIL: expected 6 draft records in R03", file=sys.stderr)
        return False
        
    # Pick 0 is simple pick (owner == orig), pick 1 is traded pick (owner != orig)
    if draft_recs[0]["is_traded"] or not draft_recs[1]["is_traded"]:
        print("FAIL: traded pick discrimination failed in R03", file=sys.stderr)
        return False
        
    teams = r03.get("team_identities", [])
    if len(teams) < 1 or teams[0].get("team_id") != 14:
        print("FAIL: expected team ID 14 in R03 teams", file=sys.stderr)
        return False
        
    r04 = data.get("phases", {}).get("R04-COACH-BOOK", {})
    if r04.get("bytes_read") != 1080:
        print("FAIL: R04 bytes read != 1080", file=sys.stderr)
        return False
        
    playbooks = r04.get("playbooks", [])
    if len(playbooks) != 3:
        print("FAIL: expected 3 playbooks in R04", file=sys.stderr)
        return False
        
    keys = [pb["low7_lookup_key"] for pb in playbooks]
    if keys != [0, 1, 2]:
        print(f"FAIL: unexpected playbook keys: {keys}", file=sys.stderr)
        return False
        
    if any(pb["play_count"] != 68 or pb["record_length_verified"] != 360 for pb in playbooks):
        print("FAIL: playbook play_count != 68 or length != 360", file=sys.stderr)
        return False
        
    print("PASS: CHECK_DRAFT_AND_COACH_BOOK")
    return True

def check_gm_cap_and_record_book():
    rdir = get_research_dir()
    with open(rdir / "ingredient_discovery_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    r05 = data.get("phases", {}).get("R05-GM-CAP", {})
    if r05.get("bytes_read") > 744:
        print("FAIL: R05 bytes exceeded budget", file=sys.stderr)
        return False
        
    dc_recs = r05.get("dead_cap_records", [])
    if len(dc_recs) != 3:
        print("FAIL: expected 3 DeadCap records in R05", file=sys.stderr)
        return False
        
    if dc_recs[0]["year1_payout"] != 92857 or not dc_recs[0]["is_stretched"]:
        print("FAIL: expected stretched payout of 92857 in DeadCap 0", file=sys.stderr)
        return False
        
    te_recs = r05.get("trade_exception_records", [])
    if len(te_recs) != 3:
        print("FAIL: expected 3 TradeException records in R05", file=sys.stderr)
        return False
        
    names = [te["associated_player_name"] for te in te_recs]
    if "Theis" not in names[0] or "Porter" not in names[1] or "McGee" not in names[2]:
        print(f"FAIL: TradeException names mismatch: {names}", file=sys.stderr)
        return False
        
    r06 = data.get("phases", {}).get("R06-RECORD-BOOK", {})
    if r06.get("bytes_read") != 520:
        print("FAIL: R06 bytes read != 520", file=sys.stderr)
        return False
        
    rb_recs = r06.get("record_book_entries", [])
    if len(rb_recs) != 10:
        print("FAIL: expected 10 RecordBook entries in R06", file=sys.stderr)
        return False
        
    if "Wilt Chamberlain" not in rb_recs[0]["record_holder"] or rb_recs[0]["record_value"] != 100.0:
        print("FAIL: Record 0 is not Wilt Chamberlain 100.0", file=sys.stderr)
        return False
        
    if "Kobe Bryant" not in rb_recs[1]["record_holder"] or rb_recs[1]["record_value"] != 81.0:
        print("FAIL: Record 1 is not Kobe Bryant 81.0", file=sys.stderr)
        return False
        
    if rb_recs[0]["historical_player_id"] != 15584 or rb_recs[2]["historical_player_id"] != 15584:
        print("FAIL: Wilt Chamberlain historical ID mismatch", file=sys.stderr)
        return False
        
    print("PASS: CHECK_GM_CAP_AND_RECORD_BOOK")
    return True

def check_audit_log_and_budget():
    rdir = get_research_dir()
    audit_file = rdir / "read_audit_log.json"
    if not audit_file.exists():
        print("FAIL: read_audit_log.json missing", file=sys.stderr)
        return False
        
    with open(audit_file, "r", encoding="utf-8") as f:
        audit_log = json.load(f)
        
    if len(audit_log) != 52:
        print(f"FAIL: expected 52 audit calls, got {len(audit_log)}", file=sys.stderr)
        return False
        
    total_bytes = sum(entry["actual_size"] for entry in audit_log)
    if total_bytes != 5172:
        print(f"FAIL: expected 5172 total bytes read, got {total_bytes}", file=sys.stderr)
        return False
        
    if total_bytes > TOTAL_BUDGET:
        print(f"FAIL: total bytes read {total_bytes} exceeds budget {TOTAL_BUDGET}", file=sys.stderr)
        return False
        
    if any(entry["status"] != "SUCCESS" for entry in audit_log):
        print("FAIL: found failed or rejected audit entries", file=sys.stderr)
        return False
        
    # Check other artifacts
    matrix_file = rdir / "ingredient_gap_matrix.json"
    packets_file = rdir / "codex_next_round_packets.json"
    report_file = rdir / "NATIVE_INGREDIENT_DISCOVERY_REPORT.md"
    
    if not matrix_file.exists() or not packets_file.exists() or not report_file.exists():
        print("FAIL: one or more required artifacts missing", file=sys.stderr)
        return False
        
    with open(packets_file, "r", encoding="utf-8") as f:
        packets = json.load(f)
    if len(packets.get("packets", [])) != 3:
        print("FAIL: expected 3 codex breakthrough packets", file=sys.stderr)
        return False
        
    print("PASS: CHECK_AUDIT_LOG_AND_BUDGET")
    return True

def main():
    check_id = sys.argv[1] if len(sys.argv) > 1 else "ALL"
    checks = {
        "CHECK_BIND_AND_PROVENANCE": check_bind_and_provenance,
        "CHECK_PLAYER_HISTORY_CHAIN": check_player_history_chain,
        "CHECK_DRAFT_AND_COACH_BOOK": check_draft_and_coach_book,
        "CHECK_GM_CAP_AND_RECORD_BOOK": check_gm_cap_and_record_book,
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

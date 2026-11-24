import json
import glob
import os

target_dir = r"E:\workspace\Cybernetic_City_State_OS_v2 - nba2k22\08_Domain_Applications\Antigravity_GM_Engine\database\tactics\20261124_stars_realism_execution"
files = sorted(glob.glob(os.path.join(target_dir, "*_stars_realism_mod.json")))

print(f"=== [AUDIT START] Found {len(files)} JSON spec files ===")
assert len(files) == 30, f"Expected 30 files, found {len(files)}"

total_players = 0
total_mods = 0
total_coaching_writes = 0
errors = []

expected_team_ids = {0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31}
found_team_ids = set()

sentinels_verified = {
    "jokic": False,
    "haliburton": False,
    "klay": False,
    "gobert": False,
    "brunson": False,
    "sengun": False,
    "maxey": False,
    "wagner": False
}

for fpath in files:
    fname = os.path.basename(fpath)
    with open(fpath, "r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except Exception as e:
            errors.append(f"JSON Syntax error in {fname}: {e}")
            continue

    # 1. Header checks
    if data.get("protocol_version") != "v2.0_full_dimensional_native_mod":
        errors.append(f"{fname}: Invalid protocol_version: {data.get('protocol_version')}")
    
    tid = data.get("team_id")
    found_team_ids.add(tid)
    
    coaching = data.get("coaching_writes", [])
    total_coaching_writes += len(coaching)
    
    players = data.get("player_writes", [])
    total_players += len(players)
    
    # 2. Inspect coaching writes
    for cw in coaching:
        val = cw.get("val_raw")
        if val in [65535, None]:
            errors.append(f"{fname}: Dummy/placeholder coaching write: {cw}")
            
    # 3. Inspect player writes
    for p in players:
        pname = p.get("player_name")
        playbook = p.get("tactical_playbook", {})
        play_types = playbook.get("play_types", [])
        
        # Assert 4 play types in 0..15
        if len(play_types) != 4:
            errors.append(f"{fname} - {pname}: play_types count != 4 ({play_types})")
        for pt in play_types:
            if not (0 <= pt <= 15):
                errors.append(f"{fname} - {pname}: play_type {pt} out of bounds 0..15")
                
        mods = p.get("modifications", [])
        total_mods += len(mods)
        for m in mods:
            field = m.get("field")
            val = m.get("val_raw")
            
            # Check placeholders
            if val in [65535, None]:
                errors.append(f"{fname} - {pname}: Dummy/placeholder mod in {field}: {val}")
                
            # Check foul ceiling
            if field in ["foul", "foul_tendency"]:
                if val > 50:
                    errors.append(f"{fname} - {pname}: Foul tendency {val} > 50 ceiling violation!")

            # Sentinel checks
            if pname == "Nikola Jokic" and field == "roll_vs_pop":
                if val == 50:
                    sentinels_verified["jokic"] = True
            elif pname == "Tyrese Haliburton" and field == "shot_tendency":
                if val == 80:
                    sentinels_verified["haliburton"] = True
            elif pname == "Klay Thompson" and field == "touches":
                if val == 78:
                    sentinels_verified["klay"] = True
            elif pname == "Rudy Gobert" and field == "roll_vs_pop":
                if val == 0:
                    sentinels_verified["gobert"] = True
            elif pname == "Jalen Brunson" and field == "potential":
                if val == 216:
                    sentinels_verified["brunson"] = True
            elif pname == "Alperen Sengun" and field == "potential":
                if val == 204:
                    sentinels_verified["sengun"] = True
            elif pname == "Tyrese Maxey" and field == "potential":
                if val == 204:
                    sentinels_verified["maxey"] = True
            elif pname == "Franz Wagner" and field == "potential":
                if val == 198:
                    sentinels_verified["wagner"] = True

# Verify team set
missing_teams = expected_team_ids - found_team_ids
if missing_teams:
    errors.append(f"Missing teams: {missing_teams}")

print(f"Total teams audited: {len(found_team_ids)} / 30")
print(f"Total players calibrated: {total_players}")
print(f"Total player modifications: {total_mods}")
print(f"Total coaching writes: {total_coaching_writes}")
print("Sentinels Verification Status:")
for sname, sbool in sentinels_verified.items():
    print(f"  - Sentinel '{sname}': {'PASS [OK]' if sbool else 'FAIL [NOT FOUND]'}")
    if not sbool:
        errors.append(f"Sentinel verification failed for: {sname}")

print("\nAudit Error Summary:")
if not errors:
    print(">>> 100% AUDIT PASS! ZERO ERRORS, ZERO PLACEHOLDERS, ZERO FOUL CEILING BREACHES. <<<")
else:
    print(f">>> FAILED with {len(errors)} errors:")
    for err in errors:
        print(f"  * {err}")
    exit(1)

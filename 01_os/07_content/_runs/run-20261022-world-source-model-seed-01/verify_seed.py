#!/usr/bin/env python3
"""Standalone offline documentation checks. Not a live-game test."""
import json
import pathlib
import sys
ROOT = pathlib.Path(__file__).resolve().parents[4]
DEV = ROOT / "08_Domain_Applications/Antigravity_GM_Engine/docs/development"
def read(name):
    return json.loads((DEV / name).read_text(encoding="utf-8"))
def main(test):
    c=read("GAME_UI_FIELD_CATALOG_V0.json")
    n=read("GAME_NATIVE_OBJECT_HINTS_V0.json")
    a=read("GAME_ACTION_DISCOVERY_SEED_V0.json")
    f=c["fields"]
    tests={
        "CATALOG_PARSE_AND_KEYS":lambda: len({x["field_id"] for x in f})==len(f) and all(x.get("field_id") and x.get("source_refs") for x in f),
        "SOURCE_PROVENANCE":lambda: all(x.get("unknowns") and x.get("next_probe") and not x.get("current_save_live_verified") for x in f),
        "DOMAIN_AND_LIFECYCLE":lambda: set(c["coverage"]["by_domain"])=={"Player","Game","Team","CoachStaff","World","Operations","History"} and c["coverage"]["rows"]==len(f),
        "AGE_AND_WORLD":lambda: all(any(x["field_id"]==k for x in f) for k in ("PLAYER.birth_year","PLAYER.original_draft_year","PLAYER.years_pro","PLAYER.world_draft_season","PLAYER.age_derived","PLAYER.display_age_observed")) and c["semantics"]["world_branching"] is False,
        "ACTION_FAIL_CLOSED":lambda: all(not x.get("current_task_real_write") and not x.get("production_enabled_by_this_catalog") for x in a["entries"]),
        "ALLOWLIST_AND_HANDOFF":lambda: len(n["slot_inventory_historical"])==75 and (DEV/"FLASH_DISCOVERY_FILL_CONTRACT_V0.md").exists()
    }
    if test not in tests: raise SystemExit("unknown check: "+test)
    if not tests[test](): raise SystemExit("FAIL: "+test)
    print("PASS: "+test+" (documentation static only)")
if __name__ == "__main__":
    main(sys.argv[1])

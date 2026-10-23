#!/usr/bin/env python3
"""Offline static checks for NBA2K22 source model seed. No game access."""
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[4]
DEV=ROOT/"08_Domain_Applications/Antigravity_GM_Engine/docs/development"
def load(name):return json.loads((DEV/name).read_text(encoding="utf-8"))
def main(name):
 c=load("GAME_UI_FIELD_CATALOG_V0.json");n=load("GAME_NATIVE_OBJECT_HINTS_V0.json")
 a=load("GAME_ACTION_DISCOVERY_SEED_V0.json");q=load("FLASH_R00_PRIORITY_QUEUE_V0.json")
 f=c["fields"];keys={x["field_id"] for x in f};groups={x["id"] for x in n["field_adjacency_groups"]}
 check={
 "CATALOG_PARSE_AND_KEYS":lambda:len(f)==888 and len(keys)==len(f) and all(x.get("source_refs") for x in f),
 "SOURCE_PROVENANCE":lambda:all(x.get("unknowns") and x.get("next_probe") and not x.get("current_save_live_verified") and not x.get("full_enumeration_certified") for x in f),
 "DOMAIN_AND_LIFECYCLE":lambda:len(c["coverage"]["by_domain"])==7 and sum(c["coverage"]["by_domain"].values())==888,
 "AGE_AND_WORLD":lambda:all(x in keys for x in ("PLAYER.birth_year","PLAYER.original_draft_year","PLAYER.years_pro","PLAYER.world_draft_season","PLAYER.age_derived","PLAYER.display_age_observed")) and c["semantics"]["world_branching"] is False and c["semantics"]["age_formula_candidate"]=="original_draft_year - birth_year + years_pro",
 "ACTION_FAIL_CLOSED":lambda:len(a["entries"])==207 and all(not x.get("current_task_real_write") and not x.get("production_enabled_by_this_catalog") and not x.get("current_task_readback_verified") and not x.get("current_task_save_reload_verified") for x in a["entries"]),
 "ALLOWLIST_AND_HANDOFF":lambda:len(n["slot_inventory_historical"])==75 and len(q["items"])==12 and (DEV/"FLASH_R00_PRIORITY_QUEUE_V0.json").is_file(),
 "PAGE_LINK_INTEGRITY":lambda:all(x.get("ui_pages") and all(p in c["pages"] for p in x["ui_pages"]) for x in f) and all(p.get("page_kind") and p.get("target_pc22_ui_confirmed") is False and p.get("current_save_ui_inspected") is False for p in c["pages"].values()),
 "TYPE_PROVENANCE":lambda:all(x.get("type_evidence_ref") in x["source_refs"] for x in f if x["value_type"]!="UNKNOWN") and all(x.get("meaning_evidence_ref") in x["source_refs"] for x in f if x.get("meaning")),
 "CANONICAL_RELATIONS":lambda:all(x.get("canonicalization_state") and (x.get("canonical_field_ref") is None or x["canonical_field_ref"]==x["field_id"]) for x in f),
 "NEIGHBORHOOD_AND_QUEUE":lambda:all(not x.get("discovery_group_ref") or x["discovery_group_ref"] in groups for x in f) and all(x.get("read_only_method") and x.get("expected_evidence") and x.get("negative_control") and x.get("stop_condition") and x.get("game_write_authorized") is False for x in q["items"])
 }
 if name not in check:raise SystemExit("UNKNOWN "+name)
 if not check[name]():raise SystemExit("FAIL "+name)
 print("PASS "+name+" documentation_static_only")
if __name__=="__main__":main(sys.argv[1])

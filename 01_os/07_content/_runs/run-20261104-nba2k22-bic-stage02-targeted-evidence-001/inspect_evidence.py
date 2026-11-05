"""Stage02 targeted offline evidence. No acquisition or game calls."""
import argparse,collections,hashlib,json,sqlite3,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
D=ROOT/"08_Domain_Applications/Antigravity_GM_Engine"
sys.path.insert(0,str(D/"world_data_prototype"))
import query
from observation_scope import query_at
BASE="66f8f73f1a91597f4562b834c2acad332ad9de5b"
parser=argparse.ArgumentParser()
parser.add_argument('--historical-root',required=True,type=Path)
LOCAL=parser.parse_args().historical_root
REL=Path("01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002")
DB=LOCAL/REL/"_runtime/world-saves/nba2k22_test_01/world-v24.sqlite"
def write(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(4*1024*1024),b""):h.update(block)
    return h.hexdigest()
def source(path):
    full="08_Domain_Applications/Antigravity_GM_Engine/"+path
    blob=subprocess.check_output(["git","rev-parse",BASE+":"+full],cwd=ROOT,text=True).strip()
    return {"commit":BASE,"path":full,"blob":blob}
stamp=datetime.now(timezone.utc).isoformat()
r1={"task":"E02-R1","checked_at":stamp,"database_relative_locator":str(REL/"_runtime/world-saves/nba2k22_test_01/world-v24.sqlite").replace("\\","/"),"access":"SQLite mode=ro, query_only=ON; existing query APIs use mode=ro","code_sources":[source("world_data_prototype/query.py"),source("world_data_prototype/observation_scope.py"),source("world_data_prototype/engine.py")],"fresh_capture":False,"game_access":False}
if not DB.is_file():
    r1.update(status="MISSING_REAL_DATASET",required_source="Historical WorldData schema24 database with source ledger, save binding, player/team and mode units")
    write("STAGE02_DEV01_REAL_READ_EVIDENCE.json",r1)
else:
    before=digest(DB)
    c=sqlite3.connect(DB.as_uri()+"?mode=ro",uri=True);c.row_factory=sqlite3.Row;c.execute("PRAGMA query_only=ON")
    header=dict(c.execute("SELECT * FROM saves").fetchone())
    manifest=json.loads((LOCAL/REL/"06_执行/increment37/baseline-manifest.json").read_bytes())
    r1.update(status="HISTORICAL_DATASET_READ_WITH_BINDING_GAPS",database_sha256=before,database_bytes=DB.stat().st_size,historical_manifest={"relative_path":str(REL/"06_执行/increment37/baseline-manifest.json").replace("\\","/"),"sha256":digest(LOCAL/REL/"06_执行/increment37/baseline-manifest.json"),"claimed_code_head":manifest["code_head"],"recorded_database_sha256":manifest["database_sha256"]},matches_historical_manifest=before==manifest["database_sha256"],header=header)
    players=[dict(r) for r in c.execute("SELECT * FROM players WHERE display_name IN ('Nikola Jokic','Pascal Siakam') ORDER BY player_id")]
    cutoff=c.execute("SELECT MAX(observed_at) FROM capture_units WHERE unit_status='success'").fetchone()[0]
    r1["cutoff"]=cutoff;r1["players"]=[]
    for player in players:
        start=time.perf_counter();scoped=query_at(DB,cutoff,"player_card",player["player_id"]);card=scoped["result"]
        elapsed=time.perf_counter()-start
        families=card["families"];values=[(family,key,value) for family,fields in families.items() if isinstance(fields,dict) for key,value in fields.items() if isinstance(value,dict)]
        units=sorted({value["unit_id"] for _,_,value in values if value.get("unit_id")})
        native=card["native_identity_observation"]
        selected=c.execute("SELECT native_team_id FROM native_player_sources WHERE player_id=? ORDER BY unit_id DESC LIMIT 1",(player["player_id"],)).fetchone()
        team=c.execute("SELECT team_id,display_name FROM teams WHERE native_team_id=?",(str(selected[0]),)).fetchone() if selected else None
        team_summary=None
        if team:
            tc=query_at(DB,cutoff,"team_card",team["team_id"])["result"]
            team_summary={"identity":dict(team),"field_units":sorted({v["unit_id"] for fs in tc["families"].values() for v in fs.values() if isinstance(v,dict) and v.get("unit_id")}),"playbook_slots":len(tc["playbook_slots"]),"staff_count":len(tc["assigned_staff"]),"lineup_result_type":type(tc["native_lineups"]).__name__}
        modes=[dict(r) for r in c.execute("SELECT unit_id,season_id,mode_label,league_label,period_label,today_native_iso_date FROM game_mode_observations ORDER BY unit_id LIMIT 8")]
        r1["players"].append({"identity":player,"native_identity_observation":native,"observation_scope":scoped["observation_scope"],"card_elapsed_seconds":elapsed,"restricted_fields":card["restricted_fields"],"scalar_field_count":len(values),"missing_fields":[family+"."+key for family,key,v in values if v.get("status")=="NOT_OBSERVED"],"representative_observations":[{"field":family+"."+key,**v} for family,key,v in values if v.get("value") is not None][:4],"scalar_unit_ids":units,"badge_count":len(families["player_badge_values"]),"badge_examples":families["player_badge_values"][:3],"team_summary":team_summary,"mode_observations":modes,"mode_same_unit_scalar_matches":sorted(set(units)&{r["unit_id"] for r in modes})})
    negatives=[]
    for name,fn in [
        ("missing_player",lambda:query.player_card(DB,"player:STAGE02_NONEXISTENT")),
        ("invalid_naive_cutoff",lambda:query_at(DB,"2021-11-20","player_card",players[0]["player_id"])),
        ("restricted_table",lambda:query.history_page(DB,"player_restricted_observations")),
        ("before_first_observation",lambda:query_at(DB,"2000-01-01T00:00:00Z","player_card",players[0]["player_id"]))]:
        try:
            v=fn()
            negatives.append({"name":name,"returned":v if name=="missing_player" else {"scope":v.get("observation_scope"),"status":v.get("result",{}).get("status")},"exit":"RETURNED"})
        except (ValueError,PermissionError) as e:
            negatives.append({"name":name,"exception":type(e).__name__,"message":str(e),"exit":"EXPECTED_REJECTION"})
    r1["negatives"]=negatives
    r1["capture_grades"]=[dict(r) for r in c.execute("SELECT source_grade,count(*) AS count FROM capture_runs GROUP BY source_grade")]
    r1["season_ids"]=[r[0] for r in c.execute("SELECT season_id FROM seasons")]
    r1["direct_sql_command"]="SELECT * FROM saves; SELECT * FROM players WHERE display_name IN ('Nikola Jokic','Pascal Siakam'); bounded capture-unit and game-mode queries as retained in inspect_evidence.py"
    r1["limitations"]=["Header source_grade=UNBOUND and null build/fingerprint require independent save-binding provenance before authenticated production admission","Player native_identity_status and canonical linkage must retain their actual states","FRANCHISE/REGULARSEASON describes league context; not proof that each game is Fast Sim or 3D","Per-field unit and time differ; mode from another unit cannot silently certify a field"]
    c.close();after=digest(DB);assert before==after
    r1["database_sha256_after"]=after;r1["database_unchanged"]=True
    write("STAGE02_DEV01_REAL_READ_EVIDENCE.json",r1)
profile=json.loads((D/"world_data_prototype/player_detail_native_profile.json").read_bytes())
reference=json.loads((D/"docs/game_mechanics/catalogs/PLAYER_BADGES_R04_A_REFERENCE.json").read_bytes())
fixture=json.loads((D/"world_data_prototype/tests/fixtures/player_details_20261025/source_manifest.json").read_bytes())
r2={"task":"E02-R2","checked_at":stamp,"sources":[source(p) for p in ["world_data_prototype/player_detail_codec.py","world_data_prototype/player_detail_native_profile.json","world_data_prototype/query.py","world_data_prototype/tests/fixtures/player_details_20261025/source_manifest.json","docs/game_mechanics/catalogs/PLAYER_BADGES_R04_A_REFERENCE.json"]],"profile_status":profile["status"],"field_counts":dict(collections.Counter(f["kind"]+("_RESERVED" if f["reserved"] else "") for f in profile["badge_fields"].values())),"fact_path":"PLAYERDATA packed bitfield -> native_badges native_code/owned_state/tier_label -> player_badge_values capture unit -> query.player_badges latest per badge","read_evidence":"R1 badge examples are historical persisted observations with their original source_grade and unit; no current game claim","historical_fixture":fixture,"research_scope_notice":reference["source_scope_notice"],"rules":[{"rule":"Current base ownership and level decode","grade":"STATIC_SOURCE","support":"Literal bit widths, enum dispatch and UNKNOWN fallback; R1 supplies persisted examples","limits":"Effective context and UI remain separate"},{"rule":"Historical capture of badge pool","grade":"HISTORICAL_LIVE_OBSERVATION","support":"source_manifest asserts complete native pool and 98 nonreserved fields","limits":"Curated fixture is RESEARCH_FIXTURE; original live raw/receipt not independently reconstructed here"},{"rule":"Badge basketball descriptions / MyPLAYER thresholds","grade":"RESEARCH_REFERENCE","support":"R04 reference and scope warnings","limits":"No PC22 MyLEAGUE acquisition proof"},{"rule":"MyLEAGUE eligibility, XP, natural upgrade predicates","grade":"UNKNOWN","support":None,"limits":"No verified predicate identified in inspected codec/profile/reference; this is not an exhaustive absence proof"},{"rule":"Animation trigger and success-rate causal effects","grade":"UNKNOWN","support":None,"limits":"Base level and card values alone cannot establish effect; controlled mode-specific trials required"}],"closure":"Per badge and level, fix build/mode, identify qualification/XP consumer and counterexamples; separately observe effective context/UI/behavior under authorized trials"}
write("STAGE02_DEV02_BADGE_EVIDENCE_GAPS.json",r2)
cells={"00":10,"10":14,"01":12,"11":22}
a=((cells["10"]-cells["00"])+(cells["11"]-cells["01"]))/2
b=((cells["01"]-cells["00"])+(cells["11"]-cells["10"]))/2
interaction=cells["11"]-cells["10"]-cells["01"]+cells["00"]
assert (a,b,interaction)==(7,5,6)
zero={"00":10,"10":10,"01":10,"11":10}
assert zero["11"]-zero["10"]-zero["01"]+zero["00"]==0
r3={"task":"E02-R3","checked_at":stamp,"source_refs":[source(p) for p in ["world_data_prototype/calendar_sim_orchestrator.py","world_data_prototype/game_mode_reader.py","world_data_prototype/query.py","research/rea_native_control/bulk_executor.py"]],"synthetic_2x2":{"label":"SYNTHETIC_ARITHMETIC_ONLY","cells":cells,"factor_A_marginal_mean_difference":a,"factor_B_marginal_mean_difference":b,"interaction_difference_in_differences":interaction,"interaction_convention":"Difference of A effect at B=1 and B=0. With +/-1 coding regression AB coefficient is this contrast /4.","zero_effect_cells":zero,"zero_effect_interaction":0,"uncertainty":"No replication or variance model; no CI or p-value estimated","exit_code":0},"comparable_units":["same save and season with explicit observation cutoff and source unit","completed game with team/opponent and player identity, game-mode evidence and final status","team/season clusters for repeated players and games"],"unsupported_controls":["No verified RNG seed or controlled independent replication","No clone/restore operation performed","Roster, coach, injuries, fatigue, schedule/opponent and natural growth remain potential confounders"],"negative_designs":[{"scenario":"Only diagonal cells 00 and 11 observed","result":"NOT_CAUSALLY_IDENTIFIED","reason":"A and B perfectly co-vary"},{"scenario":"Repeated players in same team-season treated as independent treatment units","result":"NOT_CAUSALLY_IDENTIFIED","reason":"Shared assignment and schedule cluster"},{"scenario":"FRANCHISE tag substituted for Fast Sim vs CPU3D vs HumanAI per-game tag","result":"MODE_NOT_ESTABLISHED","reason":"League context is not game simulation mode"},{"scenario":"Setter readback and Box score used to infer off-ball behavior","result":"TACTICAL_EXECUTION_UNKNOWN","reason":"No timestamped observed behavior/animation/possession trace"}],"future_live_authorization":["exact save/build and team/player/field bounds","before values, CAS/readback, immutable receipts, failure rollback and unknown outcome handling","explicit date advancement and restore permissions","mode-specific behavior observation/recording scope"],"historical_report":"307-pass VAE report remains original scope; source definition is in Stage02 planning S-VAE-REPORT","formal_stage02_pass":False}
write("STAGE02_DEV03_EXPERIMENT_FEASIBILITY.json",r3)
print(json.dumps({"R1":r1["status"],"R2":"EVIDENCE_LAYERED_WITH_UNKNOWNS","R3":"SYNTHETIC_CONTRASTS_CHECKED","formal_stage02_pass":False}))

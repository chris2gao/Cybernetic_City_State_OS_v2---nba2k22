"""Verify actual fact backup/recovery independently of game memory and save files."""
import gzip,json,platform,shutil,subprocess,sys,time
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from database_operations import backup_facts,restore_facts,storage_profile,project_observations,file_sha256,inventory
from cadence import ANNUAL_FAMILIES
from query import player_card,native_player_skills,native_player_details,native_affiliations,native_player_state,game_box,team_card
from engine import connect
r=Path(__file__).resolve().parent;out=r/'fact-recovery-actual-01';out.mkdir(exist_ok=False);save=r/'world-saves/nba2k22_test_01';binding_raw=(save/'save.json').read_bytes();binding=json.loads(binding_raw);db=save/binding['database_file'];source_hash=file_sha256(db);started=time.monotonic()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
manifest=backup_facts(db,out/'backup');write(out/'backup-summary.json',{k:v for k,v in manifest.items() if k!='inventory'})
receipt=restore_facts(out/'backup',out/'recovered-world.sqlite',expected_save_id=binding['save_id']);write(out/'restore-receipt.json',receipt);restored=out/'recovered-world.sqlite'
checks={}
checks['player_card']=player_card(db,'player:native:1612')==player_card(restored,'player:native:1612')
for name,query in [('skills',native_player_skills),('details',native_player_details),('state',native_player_state),('affiliation',native_affiliations)]:checks[name]=query(db,subject_name='Stephen Curry')==query(restored,subject_name='Stephen Curry')
checks['team_card']=team_card(db,'team:native:0')==team_card(restored,'team:native:0')
with connect(db,True) as c:game=c.execute('SELECT game_id FROM player_game_boxes ORDER BY game_id LIMIT 1').fetchone()[0]
checks['game_box']=game_box(db,game)==game_box(restored,game)
assert all(checks.values());assert file_sha256(db)==source_hash and (save/'save.json').read_bytes()==binding_raw
profile=json.loads((r/'storage-measurement-bundled-01/storage-profile.json').read_bytes());annual=set(ANNUAL_FAMILIES.values());excluded=['BOUND_GAME_PLAYER_WORLD'];models={}
for captures in (20,40):
    calls={u['source_key']:1 if u['source_key'] in annual else captures for u in profile['latest_source_units'] if u['source_key'] not in excluded}
    models[str(captures)]=project_observations(profile,source_calls_per_season=calls,years=100)
write(out/'fixed-population-100-season-projections.json',{'status':'PROJECTIONS_NOT_100_SEASON_EXECUTION','annual_policy_source':'cadence.ANNUAL_FAMILIES; Human annual history/award instruction','excluded_superseded_bootstrap_sources':excluded,'models':models})
with (out/'backup/facts.sqlite').open('rb') as src,gzip.open(out/'verified-fact-backup.sqlite.gz','wb') as target:shutil.copyfileobj(src,target)
report={'status':'REAL_FACT_DATABASE_BACKUP_AND_NEW_RECOVERY_VERIFIED','candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),
    'environment':{'python':platform.python_version(),'platform':platform.system()},'save_id':binding['save_id'],'schema_version':manifest['inventory']['schema_version'],'table_count':len(manifest['inventory']['tables']),
    'source_database_sha256_unchanged':source_hash,'active_binding_unchanged':True,'restored_rows_verified':receipt['rows_verified'],'all_table_inventory_match':inventory(db)==manifest['inventory'],
    'public_query_results_equal':checks,'backup_seconds':manifest['elapsed_seconds'],'recovery_seconds':receipt['elapsed_seconds'],'all_elapsed_seconds':time.monotonic()-started,
    'backup_bytes':manifest['byte_count'],'compressed_backup_bytes':(out/'verified-fact-backup.sqlite.gz').stat().st_size,'backup_sha256':manifest['sha256'],
    'fact_database_source_coverage':'All original fact and owner metadata tables; external raw source files not bundled','game_access':False,'source_raw_artifacts_restored':False,'full_goal_complete':False,'executed_100_season_test':False}
assert report['all_table_inventory_match'];write(out/'actual-recovery-report.json',report)
print(json.dumps({k:report[k] for k in ('status','restored_rows_verified','backup_seconds','recovery_seconds','backup_bytes','compressed_backup_bytes')}))

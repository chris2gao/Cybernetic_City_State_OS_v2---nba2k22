import importlib.util,json,shutil,subprocess,sys
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;run=r.parent;dest=run/'06_执行/increment35';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from schema_model import VERSION,TABLES
from refresh import SOURCES
from live_world import read_binding,bound_database
from database_operations import file_sha256
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
binding,bhash=read_binding(r/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(r/'world-saves/nba2k22_test_01',binding);digest=file_sha256(db);assert digest=='f76b943e4c716748b4df1c8f6c94779fb57ebb312bbeeb9e4d4dfd97a024b218'
assert VERSION==24 and len(TABLES)==100 and len(SOURCES)==20 and 'player-overall' not in SOURCES and 'native_player_overall_observations' not in TABLES
for name in ('overall_reader','overall_codec'):assert importlib.util.find_spec(name) is None
verification=dest/'verification';verification.mkdir(exist_ok=False);commands={'player_skills':[sys.executable,'-m','unittest','discover','-s',str(app/'tests'),'-p','test_player_skills.py','-q'],'sqlite_smoke':[sys.executable,str(app/'cli.py'),'smoke']};exits={}
for name,command in commands.items():
    result=subprocess.run(command,capture_output=True);(verification/(name+'.stdout.log')).write_bytes(result.stdout);(verification/(name+'.stderr.log')).write_bytes(result.stderr);exits[name]=result.returncode;assert result.returncode==0,name
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:400];write(dest/'preflight.json',json.loads(preflight.stdout));assert file_sha256(db)==digest
write(dest/'verification-report.json',{'status':'HUMAN_OVERALL_DEFERRAL_APPLIED_ACTIVE_V24_RESTORED_AND_VERIFIED','schema_version':VERSION,'tables':len(TABLES),'columns':sum(len(t.columns) for t in TABLES.values()),'registered_source_families':len(SOURCES),'overall_reader_importable':False,'overall_schema_or_source_active':False,'database_unchanged':True,'database_sha256':digest,'save_id':binding['save_id'],'binding_sha256':bhash,'commands':commands,'exit_codes':exits,'overall_game_values_acquired':0,'game_writes':False,'computer_use_used':False,'capacity_work_executed':False,'full_goal_complete':False})
scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('inspect_coverage35.py','inspect_overall_metadata35.py','inspect_overall_code35.py','extract_overall_getters35.py','build_overall_profile35.py','defer_overall35.py','verify_deferral35.py'):shutil.copyfile(r/name,scripts/name)
print(json.dumps({'status':'HUMAN_DEFERRAL_VERIFIED','schema_version':VERSION,'tables':len(TABLES),'source_families':len(SOURCES),'exit_codes':exits,'database_unchanged':True}))

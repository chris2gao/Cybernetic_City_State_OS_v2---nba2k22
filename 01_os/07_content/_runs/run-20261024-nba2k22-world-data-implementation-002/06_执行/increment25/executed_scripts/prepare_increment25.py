import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();run=Path(__file__).resolve().parent.parent;runtime=run/'_runtime';dest=run/'06_执行/increment25';dest.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from live_world import read_binding,bound_database
from database_operations import file_sha256
binding,binding_hash=read_binding(runtime/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(runtime/'world-saves/nba2k22_test_01',binding);digest=file_sha256(db)
assert digest=='46eec932562bb5b722c490bb71011b4d21db87a4f86d1be742ba5435ea87514d'
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:500]
for name,value in [('preflight-before',json.loads(preflight.stdout)),('before',{'binding_sha256':binding_hash,'database_sha256':digest,'save_id':binding['save_id'],'schema_version':18,'database_snapshot_manifest':'../increment24/world-v18.snapshot.json','game_writes':False})]:(dest/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preflight_exit_code':0,'database_unchanged_from_increment24':True}))

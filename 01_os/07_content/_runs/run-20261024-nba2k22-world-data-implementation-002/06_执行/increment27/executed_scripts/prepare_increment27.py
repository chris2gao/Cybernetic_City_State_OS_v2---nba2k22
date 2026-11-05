import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();run=Path(__file__).resolve().parent.parent;runtime=run/'_runtime';dest=run/'06_执行/increment27';dest.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from live_world import read_binding,bound_database
from database_operations import file_sha256
binding,binding_hash=read_binding(runtime/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(runtime/'world-saves/nba2k22_test_01',binding);digest=file_sha256(db);assert digest=='d7296d67dcb7c1896a1e3ec242650769c2f84f848dec46049824d89a5395a117'
result=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert result.returncode==0,result.stderr[:500]
for name,value in [('preflight-before',json.loads(result.stdout)),('before',{'binding':binding,'binding_sha256':binding_hash,'database_sha256':digest,'baseline_snapshot_manifest':'../increment26/world-v19.snapshot.json','game_writes':False})]:(dest/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preflight_exit_code':0,'before_database_hash_verified':True,'save_id':binding['save_id']}))

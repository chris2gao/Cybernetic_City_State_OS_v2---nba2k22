import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;run=runtime.parent;dest=run/'06_执行/increment30';dest.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from live_world import read_binding,bound_database
from database_operations import file_sha256
binding,bhash=read_binding(runtime/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(runtime/'world-saves/nba2k22_test_01',binding);digest=file_sha256(db);assert digest=='f0f000957404b9a9c536a1a73be7045d1536e253c689d7dcde12158dd776f0b2'
result=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert result.returncode==0,result.stderr[:500]
for name,value in [('preflight-before',json.loads(result.stdout)),('before',{'binding':binding,'binding_sha256':bhash,'database_sha256':digest,'baseline_snapshot_manifest':'../increment29/world-v21.snapshot.json','prior_turn_classification':'PROGRESS: published actual Native global lineups, complete rotation fields and immutable v21 query evidence','game_writes':False})]:(dest/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preflight':result.returncode,'database_hash_verified':True}))

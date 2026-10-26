import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;run=runtime.parent;dest=run/'06_执行/increment29';dest.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from live_world import read_binding,bound_database
from database_operations import file_sha256
binding,bhash=read_binding(runtime/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(runtime/'world-saves/nba2k22_test_01',binding);digest=file_sha256(db);assert digest=='c6e6befe0109c52d25e7eb3b35ebeee4a954df1ff5f782cff9ade9028f518309'
result=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert result.returncode==0,result.stderr[:500]
for name,value in [('preflight-before',json.loads(result.stdout)),('before',{'binding':binding,'binding_sha256':bhash,'database_sha256':digest,'baseline_snapshot_manifest':'../increment28/world-v20.snapshot.json','prior_turn_classification':'PROGRESS: published actual typed finance source, immutable v20 copy and verified query evidence','game_writes':False})]:(dest/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preflight':result.returncode,'database_hash_verified':True}))

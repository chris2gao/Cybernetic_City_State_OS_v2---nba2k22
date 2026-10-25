"""Retain preflight and exact immutable before-image before the live refresh."""
import gzip,json,shutil,subprocess,sys
from pathlib import Path
repo=Path.cwd();run=Path(__file__).resolve().parent.parent;runtime=run/'_runtime';dest=run/'06_执行/increment24';dest.mkdir(parents=True,exist_ok=False)
app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from database_operations import file_sha256
from live_world import read_binding,bound_database
expected='0780e661605c98d280348b2436d1cf49190effa537c675ddbde0e5b64c053082'
binding,binding_hash=read_binding(runtime/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(runtime/'world-saves/nba2k22_test_01',binding)
assert file_sha256(db)==expected
baseline=runtime/'increment24-baseline.sqlite'
with gzip.open(runtime/'increment23-world-v18.sqlite.gz','rb') as src,baseline.open('xb') as dst:shutil.copyfileobj(src,dst,4*1024*1024)
assert file_sha256(baseline)==expected
result=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8')
assert result.returncode==0,result.stderr[:500]
(dest/'preflight-before.json').write_text(json.dumps(json.loads(result.stdout),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(dest/'before.json').write_text(json.dumps({'database_sha256':expected,'binding_sha256':binding_hash,'binding':binding,'baseline_file':baseline.name,'game_writes':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preflight_exit_code':result.returncode,'baseline_sha256_verified':True,'save_id':binding['save_id']}))

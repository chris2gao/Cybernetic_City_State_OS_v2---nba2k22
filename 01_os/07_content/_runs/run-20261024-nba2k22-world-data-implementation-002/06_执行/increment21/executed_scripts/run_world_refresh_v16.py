"""Explicit Owner invocation; thirteen bounded readers, no game writes/scheduler."""
import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from database_operations import file_sha256
from live_world import read_binding,bound_database,_json
from refresh import refresh_world,RefreshFailed
runtime=Path(__file__).resolve().parent;save=runtime/'world-saves/nba2k22_test_01';binding,binding_hash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
before=file_sha256(db)
if before!='466d3eeaf7bda194cdba7f26f6013227a9c2a569084ee450a665792746135932':raise RuntimeError('actual facts changed before the planned batch; inspect instead of assuming baseline')
_json(runtime/'world-refresh-before.json',{'database_sha256':before,'binding_sha256':binding_hash,'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip()})
try:
    result=refresh_world(int(sys.argv[1]),save,'MyLEAGUE0003',runtime/'world-refresh-live-01')
    report={'status':'EXPLICIT_NATIVE_WORLD_REFRESH_FINISHED','result':result}
except RefreshFailed as error:report={'status':'EXPLICIT_NATIVE_WORLD_REFRESH_PARTIAL','result':error.report}
except Exception as error:report={'status':'WORLD_REFRESH_FAILED','error_type':type(error).__name__,'reason':str(error)}
report.update({'database_sha256_after':file_sha256(db),'binding_unchanged':read_binding(save,'MyLEAGUE0003')[1]==binding_hash,'game_writes':False,'scheduler_started':False,'full_goal_complete':False})
_json(runtime/'world-refresh-worker-report.json',report)

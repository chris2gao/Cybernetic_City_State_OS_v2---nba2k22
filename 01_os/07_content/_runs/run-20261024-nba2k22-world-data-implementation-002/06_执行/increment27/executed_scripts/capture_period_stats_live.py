"""One explicit period-stat family; no migration, annual refresh or game write."""
import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from live_world import read_binding,bound_database,_json
from database_operations import file_sha256
from refresh import refresh_world
save=runtime/'world-saves/nba2k22_test_01';binding,binding_hash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);before=file_sha256(db)
if before!='d7296d67dcb7c1896a1e3ec242650769c2f84f848dec46049824d89a5395a117':raise RuntimeError('facts differ from retained increment26 baseline')
report={'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip(),'game_pid':int(sys.argv[1]),'before_database_sha256':before,'before_binding_sha256':binding_hash,'game_writes':False,'annual_history_refreshed':False,'full_goal_complete':False};_json(runtime/'period-stats-before.json',report)
try:
    report['refresh']=refresh_world(int(sys.argv[1]),save,'MyLEAGUE0003',runtime/'period-stats-live-01',families=['period-stats']);report['status']='CURRENT_PERIOD_STAT_REFRESH_FINISHED'
except Exception as error:report.update({'status':'CURRENT_PERIOD_STAT_REFRESH_FAILED','error_type':type(error).__name__,'reason':str(error)})
after,after_hash=read_binding(save,'MyLEAGUE0003');report.update({'after_database_sha256':file_sha256(bound_database(save,after)),'binding_sha256_unchanged':after_hash==binding_hash});_json(runtime/'period-stats-worker-report.json',report)

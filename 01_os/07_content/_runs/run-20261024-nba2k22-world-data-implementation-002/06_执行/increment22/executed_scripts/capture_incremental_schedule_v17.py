"""Explicit Owner v16 copy-upgrade and two bounded schedule captures."""
import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from database_operations import file_sha256
from live_world import _json,read_binding,bound_database,upgrade_bound_save
from schedule_reader import capture_season
from refresh import _context
runtime=Path(__file__).resolve().parent;save=runtime/'world-saves/nba2k22_test_01';pid=int(sys.argv[1]);binding,binding_hash=read_binding(save,'MyLEAGUE0003');old=bound_database(save,binding)
if file_sha256(old)!='5862abf394bf831b6f37cfd0f52c274f7d05bbfd41701f22761228505e93761c':raise RuntimeError('actual pre-migration facts changed; inspect instead of assuming baseline')
report={'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),'before_binding_sha256':binding_hash,'before_database_sha256':file_sha256(old),'game_writes':False,'full_goal_complete':False}
_json(runtime/'incremental-v17-before.json',report)
try:
    report['migration']=upgrade_bound_save(save,'MyLEAGUE0003');report['context_before']=_context(pid)
    _json(runtime/'incremental-v17-migration.json',report['migration'])
    report['seed']=capture_season(pid,save,'MyLEAGUE0003',runtime/'schedule-v17-seed')
    _json(runtime/'incremental-v17-seed.json',report['seed'])
    report['incremental']=capture_season(pid,save,'MyLEAGUE0003',runtime/'schedule-v17-incremental')
    report['context_after']=_context(pid)
    if report['context_before']['epoch']!=report['context_after']['epoch']:raise RuntimeError('process/build/year changed across explicit verification captures')
    report['status']='NATIVE_V17_COPY_UPGRADE_AND_INCREMENTAL_SCHEDULE_FINISHED'
except Exception as error:report.update({'status':'NATIVE_V17_INCREMENTAL_SCHEDULE_FAILED','error_type':type(error).__name__,'reason':str(error)})
current,_=read_binding(save,'MyLEAGUE0003');report['after_database_sha256']=file_sha256(bound_database(save,current));report['old_database_sha256_unchanged']=file_sha256(old)==report['before_database_sha256']
_json(runtime/'incremental-v17-worker-report.json',report)

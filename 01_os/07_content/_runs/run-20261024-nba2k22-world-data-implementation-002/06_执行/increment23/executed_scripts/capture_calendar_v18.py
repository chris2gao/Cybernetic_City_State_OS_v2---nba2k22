"""Explicit dedicated-save copy-upgrade and one calendar-aware schedule acquisition."""
import subprocess,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from database_operations import file_sha256
from live_world import _json,read_binding,bound_database,upgrade_bound_save
from schedule_reader import capture_season
from refresh import _context
r=Path(__file__).resolve().parent;save=r/'world-saves/nba2k22_test_01';pid=int(sys.argv[1]);binding,binding_hash=read_binding(save,'MyLEAGUE0003');old=bound_database(save,binding)
if file_sha256(old)!='ba0d03601940d6739aae90b885a6a13363e551298d6197bf30d990eb5219bade':raise RuntimeError('pre-migration v17 facts changed; inspect instead of assuming baseline')
report={'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),'before_binding_sha256':binding_hash,'before_database_sha256':file_sha256(old),'game_writes':False,'full_goal_complete':False};_json(r/'calendar-v18-before.json',report)
try:
    report['migration']=upgrade_bound_save(save,'MyLEAGUE0003');_json(r/'calendar-v18-migration.json',report['migration']);report['context_before']=_context(pid)
    report['capture']=capture_season(pid,save,'MyLEAGUE0003',r/'calendar-v18-live');report['context_after']=_context(pid)
    if report['context_before']['epoch']!=report['context_after']['epoch']:raise RuntimeError('process/build/year changed across calendar capture')
    report['status']='NATIVE_V18_CALENDAR_AND_GAME_CLASSIFICATION_CAPTURE_FINISHED'
except Exception as error:report.update({'status':'NATIVE_V18_CALENDAR_CAPTURE_FAILED','error_type':type(error).__name__,'reason':str(error)})
current,_=read_binding(save,'MyLEAGUE0003');report.update({'after_database_sha256':file_sha256(bound_database(save,current)),'old_database_sha256_unchanged':file_sha256(old)==report['before_database_sha256']});_json(r/'calendar-v18-worker-report.json',report)

import json,subprocess,sys,traceback
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;dest=r.parent/'06_执行/increment32';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from live_world import read_binding,bound_database,upgrade_bound_save,_json
from process_session import owner_identity,resolve_pid,reconnect
from database_operations import file_sha256
from refresh import refresh_world
save=r/'world-saves/nba2k22_test_01';report={'game_writes':False,'computer_use_used':False,'full_goal_complete':False,'worker_identity':owner_identity()}
try:
    head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip();tested=json.loads((dest/'verification-final/operations_report.json').read_bytes());assert tested['candidate_code_head']==head and tested['exit_codes']=={'tests':0,'sqlite_smoke':0};report['candidate_code_head']=head
    before=json.loads((dest/'before.json').read_bytes());binding,bhash=read_binding(save,'MyLEAGUE0003');old=bound_database(save,binding);assert bhash==before['binding_sha256'] and file_sha256(old)==before['database_sha256'];connection=reconnect(save,'MyLEAGUE0003',r/'reconnect-history-32');report['process_epoch']=connection['epoch'];report['game_progress']=connection['game_progress']
    report['upgrade']=upgrade_bound_save(save,'MyLEAGUE0003');new_binding,_=read_binding(save,'MyLEAGUE0003');assert {k:v for k,v in binding.items() if k!='database_file'}=={k:v for k,v in new_binding.items() if k!='database_file'};assert file_sha256(old)==before['database_sha256']
    batch=refresh_world(None,save,'MyLEAGUE0003',r/'staff-history-refresh-32',families=['staff-history']);assert batch['status']=='COMPLETED_REQUESTED_SOURCES';digest=file_sha256(bound_database(save,new_binding));report['unit']=batch['sources'][0]['unit'];report['counts']=batch['sources'][0]['counts']
    skip=refresh_world(None,save,'MyLEAGUE0003',r/'staff-history-skip-32',families=['staff-history']);assert skip['sources'][0]['status']=='ANNUAL_ALREADY_REFRESHED';assert skip['sources'][0]['unit']==report['unit'];assert file_sha256(bound_database(save,new_binding))==digest
    report.update(status='ACTUAL_ANNUAL_STAFF_HISTORY_V23_AND_SAME_YEAR_SKIP_SUCCEEDED',after_database_sha256=digest,old_database_retained_unchanged=True,save_identity_unchanged=True,annual_skip_database_unchanged=True)
except Exception as e:
    report.update(status='STAFF_HISTORY_WORKER_FAILED',error_type=type(e).__name__,reason=str(e));(dest/'worker-traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
_json(dest/'worker-result.json',report)

import json,subprocess,sys,traceback
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;dest=r.parent/'06_执行/increment34';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from live_world import read_binding,bound_database,upgrade_bound_save,_json
from process_session import owner_identity,reconnect
from database_operations import file_sha256
from refresh import refresh_world
save=r/'world-saves/nba2k22_test_01';report={'game_writes':False,'computer_use_used':False,'full_goal_complete':False,'worker_identity':owner_identity()}
try:
    head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip();tested=json.loads((dest/'verification/operations_report.json').read_bytes());assert tested['candidate_code_head']==head and tested['exit_codes']=={'tests':0,'sqlite_smoke':0};report['candidate_code_head']=head
    before=json.loads((dest/'before.json').read_bytes());binding,bhash=read_binding(save,'MyLEAGUE0003');old=bound_database(save,binding);assert bhash==before['binding_sha256'] and file_sha256(old)==before['database_sha256'];connection=reconnect(save,'MyLEAGUE0003',r/'reconnect-current-coach-34');report['initial_process_epoch']=connection['epoch']
    report['upgrade']=upgrade_bound_save(save,'MyLEAGUE0003');new_binding,_=read_binding(save,'MyLEAGUE0003');assert {k:v for k,v in binding.items() if k!='database_file'}=={k:v for k,v in new_binding.items() if k!='database_file'};assert file_sha256(old)==before['database_sha256'];report['sources']=[]
    for number in (1,2):
        batch=refresh_world(None,save,'MyLEAGUE0003',r/f'current-coach-refresh-34-{number}',families=['coach-stats']);assert batch['status']=='COMPLETED_REQUESTED_SOURCES' and batch['sources'][0]['status']=='ACQUIRED';report['sources'].append({'unit':batch['sources'][0]['unit'],'counts':batch['sources'][0]['counts'],'process_epoch':batch['process_epoch'],'game_progress':batch['game_progress']})
    assert report['sources'][0]['unit']['unit_id']!=report['sources'][1]['unit']['unit_id'];report.update(status='ACTUAL_ORDINARY_CURRENT_COACH_V24_TWO_OBSERVATIONS_SUCCEEDED',after_database_sha256=file_sha256(bound_database(save,new_binding)),old_database_retained_unchanged=True,save_identity_unchanged=True)
except Exception as e:
    report.update(status='CURRENT_COACH_WORKER_FAILED',error_type=type(e).__name__,reason=str(e));(dest/'worker-traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
_json(dest/'worker-result.json',report)

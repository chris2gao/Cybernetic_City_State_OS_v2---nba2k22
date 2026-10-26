import json,subprocess,sys,traceback
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;dest=runtime.parent/'06_执行/increment31';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from process_session import reconnect,owner_identity,owner_is_live
from refresh import refresh_world
from live_world import read_binding,bound_database,_json
from database_operations import file_sha256
from engine import connect
save=runtime/'world-saves/nba2k22_test_01';report={'game_writes':False,'date_advanced':False,'full_goal_complete':False}
try:
    head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip();tested=json.loads((dest/'verification/operations_report.json').read_bytes());assert tested['candidate_code_head']==head and tested['exit_codes']=={'tests':0,'sqlite_smoke':0};report['candidate_code_head']=head;report['worker_identity']=owner_identity();assert owner_is_live(report['worker_identity'])
    before=json.loads((dest/'before.json').read_bytes());binding,bhash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);assert bhash==before['binding_sha256'] and file_sha256(db)==before['database_sha256']
    first=reconnect(save,'MyLEAGUE0003',runtime/'reconnect-31-first');assert file_sha256(db)==before['database_sha256']
    second=reconnect(save,'MyLEAGUE0003',runtime/'reconnect-31-second');assert file_sha256(db)==before['database_sha256'];assert second['process_changed'] is False and second['game_progress_changed'] is False
    old=json.loads((dest.parent/'increment30/actual-staff-report.json').read_bytes())['process_epoch'];current=first['epoch'];assert current['pid']!=old['pid'] or current['creation_filetime']!=old['creation_filetime']
    # One explicit engineering verification capture, not a restart-triggered or
    # Human gameplay refresh. Only public GAMEMODE and its metadata are read.
    batch=refresh_world(None,save,'MyLEAGUE0003',runtime/'restart-capture-31',families=['game-mode']);assert batch['status']=='COMPLETED_REQUESTED_SOURCES';assert batch['process_epoch']==current;digest=file_sha256(db)
    recovered=refresh_world(None,save,'MyLEAGUE0003',runtime/'restart-resume-31',resume_report=runtime/'restart-capture-31/refresh-report.json');assert recovered['status']=='COMPLETED_REQUESTED_SOURCES' and recovered['sources'][0]['status']=='RETAINED_PRIOR_OBSERVATION';assert file_sha256(db)==digest
    with connect(db,True) as conn:
        units=[dict(r) for r in conn.execute('SELECT * FROM capture_units ORDER BY unit_id')];old_by_id={r['unit_id']:r for r in before['units']};assert all(r==old_by_id[r['unit_id']] for r in units if r['unit_id'] in old_by_id) and len(units)==len(old_by_id)+1
        annual=[dict(r) for r in conn.execute('SELECT run_id,refresh_family,refresh_period_year FROM capture_runs WHERE refresh_family IS NOT NULL ORDER BY run_id')];assert annual==before['annual_buckets']
        counts={t:conn.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in before['row_counts']}
    report.update(status='ACTUAL_RESTART_AUTO_RECONNECT_AND_RECEIPT_RECOVERY_VERIFIED',old_process_epoch=old,current_process_epoch=current,game_progress=first['game_progress'],reconnect_database_unchanged=True,reconnect_fact_units=0,verification_capture_unit=batch['sources'][0]['unit']['unit_id'],successful_units=len(units),old_unit_receipts_preserved=len(old_by_id),resume_created_units=0,resume_database_unchanged=True,annual_buckets_unchanged=True,binding_unchanged=True,after_database_sha256=digest,after_total_rows=sum(counts.values()),row_deltas={t:counts[t]-before['row_counts'][t] for t in counts if counts[t]!=before['row_counts'][t]},actual_gameplay_month_advance_tested=False,controller_death_test='Deterministic fixtures; actual worker was not killed')
except Exception as error:
    report.update(status='RESTART_WORKER_FAILED',error_type=type(error).__name__,reason=str(error));(dest/'worker-traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
_json(dest/'worker-result.json',report)

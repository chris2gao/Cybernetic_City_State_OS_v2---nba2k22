import json,subprocess,sys,traceback
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;run=r.parent;dest=run/'06_执行/increment33';dest.mkdir(parents=True,exist_ok=True);app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from staff_history_semantics import verify_semantics_code
from award_reader import read_native_fields
from refresh import _context
from process_session import resolve_pid,owner_identity
from live_reader import ReadOnlyGameProcess
from live_world import read_binding,bound_database,_json
from database_operations import file_sha256
reader=None;report={'computer_use_used':False,'game_writes':False,'staff_value_reads':0,'annual_source_refreshed':False,'worker_identity':owner_identity()}
try:
    preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:300];_json(dest/'preflight.json',json.loads(preflight.stdout))
    head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip();report['candidate_code_head']=head
    binding,bhash=read_binding(r/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(r/'world-saves/nba2k22_test_01',binding);digest=file_sha256(db);assert digest=='c243f31c3f5f1525800691e9b1ed12f1ebf001cad682b4870b0950a2058033b1';pid=resolve_pid();before=_context(pid);reader=ReadOnlyGameProcess(pid);proof=verify_semantics_code(reader)
    entries=json.loads((r/'staff-history-metadata-32/type_entries.json').read_bytes());old=json.loads((r/'staff-history-metadata-32/metadata.json').read_bytes());metadata=[]
    for name,size in (('COACHSTATDATA',12),('COACHSTATMANAGERDATA',2)):
        entry=next(e for e in entries if e['name']==name);value=read_native_fields(reader,entry,size,read_enums=False);expected=next(v for v in old if v['name']==name)
        assert [(f['name_crc'],f['words'][1:6]) for f in value['fields']]==[(f['name_crc'],f['words'][1:6]) for f in expected['fields']];metadata.append(value)
    reader.close();after=_context(pid);assert before['epoch']==after['epoch'] and before['game_progress']==after['game_progress'];assert file_sha256(db)==digest
    report.update(status='ACTUAL_NATIVE_STAFF_STORAGE_ROLES_CODE_AND_METADATA_VERIFIED',proof=proof,context_before=before,context_after=after,read_trace=reader.trace,metadata=metadata,database_sha256=digest,database_unchanged=True,binding_sha256=bhash,save_id=binding['save_id'],native_save_filename=binding['native_save_filename'])
except Exception as e:report.update(status='STAFF_STORAGE_ROLE_VERIFICATION_FAILED',error_type=type(e).__name__,reason=str(e));(dest/'worker-traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
finally:
    if reader:reader.close()
_json(dest/'native-code-proof.json',report)

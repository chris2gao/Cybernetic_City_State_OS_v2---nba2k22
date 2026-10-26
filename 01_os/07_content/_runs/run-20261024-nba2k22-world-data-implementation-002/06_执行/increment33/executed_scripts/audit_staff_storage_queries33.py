import hashlib,json,shutil,subprocess,sys
from collections import Counter
from contextlib import closing
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;dest=r.parent/'06_执行/increment33';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from query import native_staff_history
from engine import connect
from database_operations import file_sha256
from live_world import read_binding,bound_database
from process_session import owner_is_live
from staff_history_semantics import PROFILE,reference_roles
from observation_scope import query_at
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
proof=json.loads((dest/'native-code-proof.json').read_bytes());tested=json.loads((dest/'verification/operations_report.json').read_bytes());head=tested['candidate_code_head'];assert head==proof['candidate_code_head'] and tested['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 265 tests' in (dest/'verification/tests.stderr.log').read_text(encoding='utf-8');assert proof['status']=='ACTUAL_NATIVE_STAFF_STORAGE_ROLES_CODE_AND_METADATA_VERIFIED' and not owner_is_live(proof['worker_identity'])
for name,digest in tested['code_sha256'].items():
    relative=(app/name).relative_to(repo).as_posix();blob=subprocess.run(['git','show',head+':'+relative],capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
binding,bhash=read_binding(r/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(r/'world-saves/nba2k22_test_01',binding);digest=file_sha256(db);assert digest==proof['database_sha256']=='c243f31c3f5f1525800691e9b1ed12f1ebf001cad682b4870b0950a2058033b1' and bhash==proof['binding_sha256'];unit='native-staff-history:bbfad4dcf2acda8b0c224761'
with closing(connect(db,True)) as c:
    raw={row['staff_stat_link_id']:dict(row) for row in c.execute('''SELECT l.*,s.next_free_raw,s.stat_year FROM native_staff_stat_links l LEFT JOIN native_coach_stat_observations s ON s.coach_stat_id=l.coach_stat_id AND s.unit_id=l.unit_id WHERE l.unit_id=?''',(unit,))};units=c.execute('SELECT count(*) FROM capture_units').fetchone()[0]
queries=dest/'queries';queries.mkdir(exist_ok=True);cursor=-1;subjects=refs=resolved=0;position_counts=Counter();markers=Counter()
while True:
    page=native_staff_history(db,unit_id=unit,after_index=cursor,limit=50);subjects+=len(page['records'])
    for row in page['records']:
        assert len(row['references'])==40
        for ref in row['references']:
            original=raw[ref['staff_stat_link_id']]
            for key,value in original.items():assert ref[key]==value
            assert ref['storage_roles']==reference_roles(ref['array_position'],ref['next_free_raw'],page['source']['decoder_version']);assert ref['stat_year'] is None;refs+=1;markers[ref['storage_roles']['next_free_marker_status']]+=1
            if ref['coach_stat_id'] is not None:resolved+=1;position_counts[ref['array_position']]+=1
    if not page['has_more']:break
    cursor=page['next_after_index']
assert subjects==1470 and refs==58800 and resolved==217 and units==40
for position in (0,1,38,39):
    value=native_staff_history(db,unit_id=unit,reference_position=position,limit=2);assert all(len(s['references'])==1 and s['references'][0]['array_position']==position for s in value['records']);write(queries/f'position-{position}.json',value)
before=query_at(db,'2026-10-26T09:13:49.850724+00:00','native_staff_history',reference_position=0);assert before['result']['status']=='NOT_OBSERVED';write(queries/'before-source-as-of.json',before)
command=[sys.executable,str(app/'cli.py'),'staff-history',str(db),'--reference-position','0','--limit','2','--as-of','2026-10-26T09:13:49.850725+00:00'];cli=subprocess.run(command,capture_output=True,text=True,encoding='utf-8');assert cli.returncode==0,cli.stderr[:300];value=json.loads(cli.stdout);assert value['result']['reference_position']==0;write(queries/'actual-cli-position-0-as-of.json',value);assert file_sha256(db)==digest
report={'status':'ACTUAL_CODE_VERIFIED_DERIVED_STAFF_QUERY_ROLES_AND_RAW_HISTORY_PRESERVATION','candidate_code_head':head,'schema_version':23,'tables':99,'columns':1756,'tests':265,'source_unit':unit,'subjects_compared':subjects,'raw_reference_rows_compared':refs,'resolved_references_compared':resolved,'resolved_references_by_position':dict(position_counts),'marker_classifications':dict(markers),'code_windows_verified':len(PROFILE['code_proofs']),'code_bytes_verified':sum(len(bytes.fromhex(p['code_hex'])) for p in PROFILE['code_proofs']),'metadata_types_verified':['COACHSTATDATA','COACHSTATMANAGERDATA'],'calendar_year_mapping':'UNKNOWN','last_position39_meaning':'UNKNOWN; NOT_ASSUMED_CAREER_TOTAL','annual_units_added':0,'database_sha256_unchanged':digest,'source_observation_times_unchanged':True,'game_value_reads':0,'game_writes':False,'getter_or_mutator_invocations':0,'computer_use_used':False,'capacity_work_executed':False,'full_goal_complete':False,'independent_acceptance':False}
report.pop('game_value_reads');report.update(annual_staff_or_stat_value_reads=0,connection_context_controls_read=True)
write(dest/'actual-query-report.json',report)
scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('inspect_staff_history_callers33.py','extract_staff_history_functions33.py','extract_staff_setter33.py','build_staff_history_semantics33.py','verify_staff_storage_roles33.py','start_staff_storage_roles33.ps1','verify_staff_storage_terminal33.ps1','audit_staff_storage_queries33.py'):shutil.copyfile(r/name,scripts/name)
for name in ('staff-history-callers33.json','staff-history-mutator-callers33.json','staff-history-functions33.json','staff-history-setter33.json'):shutil.copyfile(r/name,dest/name)
print(json.dumps({k:report[k] for k in ('status','tests','subjects_compared','raw_reference_rows_compared','resolved_references_by_position','marker_classifications','code_windows_verified')}))

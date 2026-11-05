"""Match committed code, actual source projection, current contract and unchanged DB."""
import hashlib,json,subprocess,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;run=runtime.parent;dest=run/'06_执行/increment25';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from database_operations import file_sha256
from query import native_player_seasons
from observation_scope import query_at
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
tested=json.loads((dest/'verification/operations_report.json').read_bytes());actual=json.loads((dest/'actual-stat-reference-report.json').read_bytes());proof=json.loads((dest/'native-contract-report.json').read_bytes());head=tested['candidate_code_head'];assert head==actual['candidate_code_head']==proof['candidate_code_head']=='2ce59cf6907df9a048c1a1aea6c2eb8e1f7d79fc'
for name,digest in tested['code_sha256'].items():
    relative=str((app/name).relative_to(repo)).replace('\\','/');blob=subprocess.run(['git','show',head+':'+relative],capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
assert tested['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 197 tests' in (dest/'verification/tests.stderr.log').read_text(encoding='utf-8')
profile=json.loads((app/'stat_reference_native_profile.json').read_bytes());windows={w['role']:w for w in profile['code_windows']}
for observed in proof['contract']['windows']:
    expected=windows[observed['role']];assert observed['sha256']==expected['sha256'] and observed['rva']==expected['rva'] and observed['bytes']==len(bytes.fromhex(expected['code_hex']))
assert len(windows)==4 and sum(w['bytes'] for w in proof['contract']['windows'])==469
assert actual['references_checked_against_raw_bytes']==84750 and actual['raw_stat_field_comparisons']==146300 and actual['resolved_references']==3325 and actual['resolved_after_gaps']==1029 and actual['shared_stat_records']==56
assert actual['db_rows_written']==actual['getter_invocations']==0 and not actual['annual_history_refreshed'] and json.loads((dest/'worker-terminal.json').read_bytes())['worker_process_absent']
db=runtime/'world-saves/nba2k22_test_01/world-v18.sqlite';digest=file_sha256(db);snapshot=json.loads((run/'06_执行/increment24/world-v18.snapshot.json').read_bytes());assert digest==actual['database_sha256_unchanged']==snapshot['database_sha256']
unit=actual['source_unit']['unit_id'];assert native_player_seasons(db,limit=1)['unit']['unit_id']==unit
assert query_at(db,'2000-01-01T00:00:00Z','native_player_seasons',unit_id=unit)['result']['status']=='NOT_OBSERVED'
source=runtime/'annual-live-v11/honors-first'
for name in ('player-stat-bank.bin','player-public-projection.bin','ingest-result.json'):assert file_sha256(dest/'sources'/name)==file_sha256(source/name)
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:500];write(dest/'preflight.json',json.loads(preflight.stdout))
artifact=run/'increment25_work_unit.yml';validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],capture_output=True,text=True,encoding='utf-8');assert validation.returncode==0,validation.stdout[:500]+validation.stderr[:500]
receipt=json.loads((run/'06_执行/increment24/mwu_load_receipt.json').read_bytes());receipt.update({'artifact':artifact.name,'validator_exit_code':0,'validator_output':validation.stdout.strip()});write(dest/'mwu_load_receipt.json',receipt)
write(dest/'delivery_check.json',{'status':'NATIVE_STAT_REFERENCE_QUERY_CODE_AND_ACTUAL_SOURCE_EVIDENCE_CONSISTENT','candidate_code_head':head,'code_hashes_matched_to_commit':len(tested['code_sha256']),'tests':197,'source_players':3390,'references_verified':84750,'raw_stat_field_comparisons':146300,'current_code_bytes_verified':469,'native_getter_invocations':0,'pinned_unit_hidden_before_observation':True,'database_sha256_unchanged':digest,'snapshot_manifest':'../increment24/world-v18.snapshot.json','annual_history_refreshed':False,'game_writes':False,'capacity_work_executed':False,'master_modified':False,'full_goal_complete':False})
for name in (Path(__file__).name,'verify_stat_worker_terminal.ps1','inspect_annual_stat_units.py'):(dest/'executed_scripts'/name).write_bytes((runtime/name).read_bytes())
print(json.dumps({'status':'NATIVE_STAT_REFERENCE_QUERY_CODE_AND_ACTUAL_SOURCE_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':197,'references_verified':84750,'raw_stat_field_comparisons':146300,'database_sha256_unchanged':True}))

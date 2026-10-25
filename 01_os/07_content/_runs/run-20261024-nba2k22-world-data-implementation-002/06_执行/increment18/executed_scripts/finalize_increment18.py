import gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path
repo=Path.cwd();run=Path(__file__).resolve().parent.parent;runtime=run/'_runtime';dest=run/'06_执行/increment18';verified=dest/'verification';actual=runtime/'fact-recovery-actual-01'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for name in ('actual-recovery-report.json','backup-summary.json','restore-receipt.json','current-query-timings.json','verified-fact-backup.sqlite.gz'):shutil.copyfile(actual/name,dest/name)
shutil.copyfile(actual/'backup/manifest.json',dest/'backup_manifest.json');early=dest/'early_capacity_observations';early.mkdir()
shutil.copyfile(actual/'fixed-population-100-season-projections.json',early/'preliminary-models.json')
shutil.copyfile(runtime/'storage-measurement-01/storage-profile.json',early/'primary-runtime-profile.json');shutil.copyfile(runtime/'storage-measurement-bundled-01/storage-profile.json',early/'dbstat-runtime-profile.json')
(early/'README.md').write_text('Historical exploratory observations of roughly one month of test data, completed before Human capacity deferral. These are not a complete-season baseline,100-season stress result or retention decision. Further capacity/A-B work is deferred. See ../../../human_capacity_cadence_20261025.md and world_data_prototype/CAPACITY_AND_RETENTION_POLICY.md.\n',encoding='utf-8',newline='\n')
scripts=dest/'executed_scripts';scripts.mkdir()
for name in ('verify_actual_fact_recovery.py','measure_current_fact_queries.py','measure_current_storage.py','summarize_storage_models.py','inspect_sqlite_runtime.py'):shutil.copyfile(runtime/name,scripts/name)
shutil.copyfile(runtime/'bundled-operations-tests.log',verified/'bundled-operation-tests.stderr.log')
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if preflight.returncode:raise RuntimeError('preflight failed: '+preflight.stderr[:500])
write(dest/'preflight.json',json.loads(preflight.stdout));artifact=run/'increment18_work_unit.yml'
validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if validation.returncode:raise RuntimeError('MWU failed: '+validation.stdout[:500]+validation.stderr[:500])
receipt=json.loads((run/'06_执行/increment17/mwu_load_receipt.json').read_bytes());receipt.update({'artifact':artifact.name,'validator_exit_code':0,'validator_output':validation.stdout.strip()});write(dest/'mwu_load_receipt.json',receipt)
report=json.loads((verified/'operations_report.json').read_bytes());recovery=json.loads((dest/'actual-recovery-report.json').read_bytes());manifest=json.loads((dest/'backup_manifest.json').read_bytes());head=subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip()
assert head==report['candidate_code_head']==recovery['candidate_code_head'];app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
for name,digest in report['code_sha256'].items():
    blob=subprocess.run(['git','show',head+':'+str((app/name).relative_to(repo)).replace('\\','/')],cwd=repo,capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest,name
assert report['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 127 tests' in (verified/'tests.stderr.log').read_text(encoding='utf-8')
assert 'Ran 8 tests' in (verified/'bundled-operation-tests.stderr.log').read_text(encoding='utf-8')
digest=hashlib.sha256()
with gzip.open(dest/'verified-fact-backup.sqlite.gz','rb') as stream:
    while block:=stream.read(4*1024*1024):digest.update(block)
assert digest.hexdigest()==manifest['sha256']==recovery['backup_sha256'];assert all(recovery['public_query_results_equal'].values())
write(dest/'delivery_check.json',{'status':'VERIFIED_FACT_RECOVERY_CANDIDATE_AND_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':127,'bundled_operation_tests':8,
    'code_hashes_matched_to_commit':len(report['code_sha256']),'table_count':recovery['table_count'],'all_table_rows_verified':recovery['restored_rows_verified'],
    'archive_hash_verified':True,'active_binding_unchanged':True,'game_access':False,'master_modified':False,'full_goal_complete':False,
    'capacity_work_state':'DEFERRED_BY_HUMAN_UNTIL_ACTUAL_COMPLETE_SEASON','retention_years_decision':'NOT_YET_MADE','human_capacity_instruction':'../../human_capacity_cadence_20261025.md'})
shutil.copyfile(__file__,scripts/'finalize_increment18.py');(dest/'.gitattributes').write_text('*.gz -text\n*.json -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nearly_capacity_observations/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({'status':'VERIFIED_FACT_RECOVERY_CANDIDATE_AND_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':127,'rows':recovery['restored_rows_verified'],'capacity_work_state':'DEFERRED_BY_HUMAN_UNTIL_ACTUAL_COMPLETE_SEASON'}))

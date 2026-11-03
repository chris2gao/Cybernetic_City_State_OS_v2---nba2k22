import gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path
repo=Path.cwd();run=Path(__file__).resolve().parent.parent;dest=run/'06_执行/increment19';verified=dest/'verification-corrected'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if preflight.returncode:raise RuntimeError('preflight failed: '+preflight.stderr[:500])
write(dest/'preflight.json',json.loads(preflight.stdout));artifact=run/'increment19_work_unit.yml';validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if validation.returncode:raise RuntimeError('MWU failed: '+validation.stdout[:500]+validation.stderr[:500])
receipt=json.loads((run/'06_执行/increment18/mwu_load_receipt.json').read_bytes());receipt.update({'artifact':artifact.name,'validator_exit_code':0,'validator_output':validation.stdout.strip()});write(dest/'mwu_load_receipt.json',receipt)
report=json.loads((verified/'operations_report.json').read_bytes());actual=json.loads((dest/'actual-observation-history-report.json').read_bytes());head=subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip();assert head==report['candidate_code_head']
app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';equivalent=0
for name,digest in report['code_sha256'].items():
    relative=str((app/name).relative_to(repo)).replace('\\','/');blob=subprocess.run(['git','show',head+':'+relative],cwd=repo,capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest,name
    if not name.startswith('tests/'):
        executed=subprocess.run(['git','show',actual['candidate_code_head']+':'+relative],cwd=repo,capture_output=True,check=True).stdout;assert hashlib.sha256(executed).hexdigest()==digest,name;equivalent+=1
assert report['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 139 tests' in (verified/'tests.stderr.log').read_text(encoding='utf-8');assert all(actual['latest_plain_and_temporal_query_results_equal'].values())
digest=hashlib.sha256()
with gzip.open(run/'06_执行/increment17/world-v16.sqlite.gz','rb') as stream:
    while block:=stream.read(4*1024*1024):digest.update(block)
assert digest.hexdigest()==actual['source_database_sha256_unchanged']
write(dest/'delivery_check.json',{'status':'OBSERVATION_HISTORY_CANDIDATE_SOURCE_AND_EVIDENCE_CONSISTENT','candidate_code_head':head,'actual_execution_head':actual['candidate_code_head'],'executed_non_test_sources_identical_to_final_candidate':equivalent,
    'code_hashes_matched_to_commit':len(report['code_sha256']),'tests':139,'reference_database_archive_hash_verified':True,'active_binding_unchanged':True,'game_access':False,'capacity_work_executed':False,'full_goal_complete':False,'master_modified':False})
shutil.copyfile(__file__,dest/'executed_scripts/finalize_increment19.py')
print(json.dumps({'status':'OBSERVATION_HISTORY_CANDIDATE_SOURCE_AND_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':139,'equivalent_runtime_files':equivalent}))

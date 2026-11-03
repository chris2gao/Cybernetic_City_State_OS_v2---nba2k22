"""Match executed runtime, verification receipts and the unchanged actual DB archive."""
import gzip,hashlib,json,subprocess,sys
from pathlib import Path
repo=Path.cwd();run=next(p for p in Path(__file__).resolve().parents if p.name=='run-20261024-nba2k22-world-data-implementation-002');dest=run/'06_执行/increment20';verified=dest/'verification'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if preflight.returncode:raise RuntimeError('preflight failed: '+preflight.stderr[:500])
write(dest/'preflight.json',json.loads(preflight.stdout));artifact=run/'increment20_work_unit.yml'
validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if validation.returncode:raise RuntimeError('MWU failed: '+validation.stdout[:500]+validation.stderr[:500])
receipt=json.loads((run/'06_执行/increment19/mwu_load_receipt.json').read_bytes());receipt.update({'artifact':artifact.name,'validator_exit_code':0,'validator_output':validation.stdout.strip()});write(dest/'mwu_load_receipt.json',receipt)
report=json.loads((verified/'operations_report.json').read_bytes());actual=json.loads((dest/'actual-competition-report.json').read_bytes());head=report['candidate_code_head'];actual_head=actual['candidate_code_head']
app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
for name,digest in report['code_sha256'].items():
    relative=str((app/name).relative_to(repo)).replace('\\','/');blob=subprocess.run(['git','show',head+':'+relative],cwd=repo,capture_output=True,check=True).stdout
    assert hashlib.sha256(blob).hexdigest()==digest,name
    executed=subprocess.run(['git','show',actual_head+':'+relative],cwd=repo,capture_output=True,check=True).stdout
    assert hashlib.sha256(executed).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
assert report['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 151 tests' in (verified/'tests.stderr.log').read_text(encoding='utf-8')
assert actual['latest_season_as_of_parity'] and actual['before_first_totals_hidden'] and actual['active_binding_unchanged']
digest=hashlib.sha256()
with gzip.open(run/'06_执行/increment17/world-v16.sqlite.gz','rb') as stream:
    while block:=stream.read(4*1024*1024):digest.update(block)
assert digest.hexdigest()==actual['source_database_sha256_unchanged']
write(dest/'delivery_check.json',{'status':'COMPETITION_QUERY_CANDIDATE_SOURCE_AND_EVIDENCE_CONSISTENT','candidate_code_head':head,'code_hashes_matched_to_commit':len(report['code_sha256']),'tests':151,
    'games_checked':actual['games_checked'],'rate_comparisons':actual['derived_rate_comparisons'],'reference_database_archive_hash_verified':True,'active_binding_unchanged':True,
    'game_access':False,'new_captures':False,'capacity_work_executed':False,'schema_migration':False,'full_goal_complete':False,'master_modified':False})
(dest/'executed_scripts/finalize_increment20.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'status':'COMPETITION_QUERY_CANDIDATE_SOURCE_AND_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':151,'games_checked':actual['games_checked'],'rate_comparisons':actual['derived_rate_comparisons']}))

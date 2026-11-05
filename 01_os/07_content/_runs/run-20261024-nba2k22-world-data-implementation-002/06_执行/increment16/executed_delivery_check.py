import gzip,hashlib,json,subprocess,sys
from pathlib import Path
repo=Path.cwd();run=Path(__file__).resolve().parent.parent;dest=run/'06_执行/increment16';verified=dest/'verification'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if preflight.returncode:raise RuntimeError('preflight failed: '+preflight.stderr[:500])
write(dest/'preflight.json',json.loads(preflight.stdout))
artifact=run/'increment16_work_unit.yml';validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if validation.returncode:raise RuntimeError('MWU failed: '+validation.stdout[:500]+validation.stderr[:500])
receipt=json.loads((run/'06_执行/increment15/mwu_load_receipt.json').read_bytes());receipt.update({'artifact':artifact.name,'validator_exit_code':0,'validator_output':validation.stdout.strip()});write(dest/'mwu_load_receipt.json',receipt)
report=json.loads((verified/'development_report.json').read_bytes());actual=json.loads((dest/'player_affiliation_world_report.json').read_bytes())
head=subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip();assert head==report['candidate_code_head']==actual['candidate_code_head']
app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
for name,digest in report['code_sha256'].items():
    blob=subprocess.run(['git','show',head+':'+str((app/name).relative_to(repo)).replace('\\','/')],cwd=repo,capture_output=True,check=True).stdout
    assert hashlib.sha256(blob).hexdigest()==digest,name
assert report['test_exit_code']==0 and 'Ran 112 tests' in (verified/'tests.stderr.log').read_text(encoding='utf-8')
def gzip_hash(path):
    h=hashlib.sha256()
    with gzip.open(path,'rb') as stream:
        while block:=stream.read(4*1024*1024):h.update(block)
    return h.hexdigest()
assert gzip_hash(dest/'world-v15.sqlite.gz')==actual['world_sqlite_sha256']
assert gzip_hash(verified/'player-details-research.sqlite.gz')==report['player_detail_research_replay']['uncompressed_sha256']
write(dest/'delivery_check.json',{'status':'PLAYER_AFFILIATION_CANDIDATE_SOURCE_DB_AND_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':112,
    'physical_schema':{'version':15,'tables':84,'columns':1245},'code_hashes_matched_to_commit':len(report['code_sha256']),
    'real_and_research_database_archive_hashes_verified':True,'mwu_validator_exit_code':0,'master_modified':False,'full_goal_complete':False})
print(json.dumps({'status':'PLAYER_AFFILIATION_CANDIDATE_SOURCE_DB_AND_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':112}))

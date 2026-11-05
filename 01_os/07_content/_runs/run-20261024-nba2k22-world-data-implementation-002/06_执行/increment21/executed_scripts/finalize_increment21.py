"""Match committed code, actual live receipts and retained multipart evidence."""
import hashlib,json,subprocess,sys,zlib
from pathlib import Path
repo=Path.cwd();run=next(p for p in Path(__file__).resolve().parents if p.name=='run-20261024-nba2k22-world-data-implementation-002');dest=run/'06_执行/increment21';verified=dest/'verification';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
report=json.loads((verified/'operations_report.json').read_bytes());actual=json.loads((dest/'actual-world-refresh-report.json').read_bytes());batch=json.loads((dest/'refresh-report.json').read_bytes());head=report['candidate_code_head'];assert head==actual['candidate_code_head']
for name,digest in report['code_sha256'].items():
    relative=str((app/name).relative_to(repo)).replace('\\','/');blob=subprocess.run(['git','show',head+':'+relative],cwd=repo,capture_output=True,check=True).stdout
    assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
for name,digest in batch['code_sha256'].items():assert report['code_sha256'][name]==digest,name
assert report['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 161 tests' in (verified/'tests.stderr.log').read_text(encoding='utf-8')
assert actual['successful_adapters']==10 and actual['verified_annual_skips']==3 and actual['context_checkpoints']==26 and actual['prior_rows_preserved']==843987 and actual['binding_unchanged'] and actual['annual_ledger_unchanged']
def check_parts(manifest,raw_expected=None):
    encoded=hashlib.sha256();decoded=hashlib.sha256();decoder=zlib.decompressobj(31)
    for part in manifest['parts']:
        assert Path(part['file']).name==part['file'];path=dest/part['file'];digest=hashlib.sha256();size=0
        with path.open('rb') as stream:
            while block:=stream.read(4*1024*1024):
                digest.update(block);encoded.update(block);size+=len(block);pending=block
                while pending:decoded.update(decoder.decompress(pending,4*1024*1024));pending=decoder.unconsumed_tail
        assert size==part['bytes'] and digest.hexdigest()==part['sha256'],part['file']
    decoded.update(decoder.flush());assert decoder.eof and not decoder.unused_data and encoded.hexdigest()==manifest['stream_sha256']
    if raw_expected:assert decoded.hexdigest()==raw_expected
    return len(manifest['parts'])
snapshot=json.loads((dest/'world-v16.snapshot.json').read_bytes());assert snapshot['database_sha256']==actual['after_database_sha256'];parts=check_parts(snapshot,snapshot['database_sha256']);native_parts=check_parts(json.loads((dest/'native-sources.archive.json').read_bytes()))
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if preflight.returncode:raise RuntimeError('preflight failed: '+preflight.stderr[:500])
write(dest/'preflight.json',json.loads(preflight.stdout));artifact=run/'increment21_work_unit.yml'
validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if validation.returncode:raise RuntimeError('MWU failed: '+validation.stdout[:500]+validation.stderr[:500])
receipt=json.loads((run/'06_执行/increment20/mwu_load_receipt.json').read_bytes());receipt.update({'artifact':artifact.name,'validator_exit_code':0,'validator_output':validation.stdout.strip()});write(dest/'mwu_load_receipt.json',receipt)
write(dest/'delivery_check.json',{'status':'MANUAL_WORLD_REFRESH_CANDIDATE_CODE_AND_NATIVE_EVIDENCE_CONSISTENT','candidate_code_head':head,'code_hashes_matched_to_commit':len(report['code_sha256']),'tests':161,'verified_new_units':10,'verified_annual_skips':3,'context_checkpoints':26,'preserved_prior_rows':843987,
    'snapshot_archive_parts_verified':parts,'native_source_archive_parts_verified':native_parts,'snapshot_decompressed_sha256_verified':True,'binding_unchanged':True,'game_writes':False,'scheduler_started':False,'capacity_work_executed':False,'full_goal_complete':False,'master_modified':False})
(dest/'executed_scripts/finalize_increment21.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'status':'MANUAL_WORLD_REFRESH_CANDIDATE_CODE_AND_NATIVE_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':161,'preserved_prior_rows':843987,'new_units':10,'annual_skips':3,'archive_parts_verified':parts+native_parts}))

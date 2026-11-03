"""Check tested/executed candidate, source hashes and complete retained streams."""
import hashlib,json,subprocess,sys,zlib
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;run=runtime.parent;dest=run/'06_执行/increment24';verified=dest/'verification';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
report=json.loads((verified/'operations_report.json').read_bytes());actual=json.loads((dest/'actual-auxiliary-report.json').read_bytes());head=report['candidate_code_head'];assert head==actual['candidate_code_head']=='912304120b12fe80d8234d52ede32e88fac02d5a'
for name,digest in report['code_sha256'].items():
    relative=str((app/name).relative_to(repo)).replace('\\','/');blob=subprocess.run(['git','show',head+':'+relative],capture_output=True,check=True).stdout
    assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
assert report['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 188 tests' in (verified/'tests.stderr.log').read_text(encoding='utf-8')
assert actual['prior_rows_preserved']==1361150 and actual['prior_tables_preserved']==86 and actual['raw_team_total_comparisons']==120
assert actual['read_trace_results']['organization']=={'box_read_calls':0,'box_read_bytes':0,'player_interval_read_calls':0} and actual['cumulative_phase_not_inferred']
worker=json.loads((dest/'worker-report.json').read_bytes());batch=worker['refresh']
for name,digest in batch['code_sha256'].items():assert hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
def check_parts(manifest,raw_expected=None):
    encoded=hashlib.sha256();decoded=hashlib.sha256();decoder=zlib.decompressobj(31)
    for part in manifest['parts']:
        assert Path(part['file']).name==part['file'];digest=hashlib.sha256();size=0
        with (dest/part['file']).open('rb') as stream:
            while block:=stream.read(4*1024*1024):
                digest.update(block);encoded.update(block);size+=len(block);pending=block
                while pending:decoded.update(decoder.decompress(pending,4*1024*1024));pending=decoder.unconsumed_tail
        assert size==part['bytes'] and digest.hexdigest()==part['sha256']
    decoded.update(decoder.flush());assert decoder.eof and not decoder.unused_data and encoded.hexdigest()==manifest['stream_sha256']
    if raw_expected:assert decoded.hexdigest()==raw_expected
    return len(manifest['parts'])
snapshot=json.loads((dest/'world-v18.snapshot.json').read_bytes());assert snapshot['database_sha256']==actual['after_database_sha256'];parts=check_parts(snapshot,snapshot['database_sha256']);native_parts=check_parts(json.loads((dest/'native-sources.archive.json').read_bytes()))
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:500];write(dest/'preflight.json',json.loads(preflight.stdout))
artifact=run/'increment24_work_unit.yml';validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],capture_output=True,text=True,encoding='utf-8');assert validation.returncode==0,validation.stdout[:500]+validation.stderr[:500]
receipt=json.loads((run/'06_执行/increment23/mwu_load_receipt.json').read_bytes());receipt.update({'artifact':artifact.name,'validator_exit_code':0,'validator_output':validation.stdout.strip()});write(dest/'mwu_load_receipt.json',receipt)
write(dest/'delivery_check.json',{'status':'AUXILIARY_HEADER_READ_CANDIDATE_AND_ACTUAL_EVIDENCE_CONSISTENT','candidate_code_head':head,'code_hashes_matched_to_commit':len(report['code_sha256']),'tests':188,'preserved_prior_rows':1361150,'organization_box_read_calls':0,'organization_raw_team_total_comparisons':120,'snapshot_archive_parts_verified':parts,'native_source_archive_parts_verified':native_parts,'snapshot_decompressed_sha256_verified':True,'save_binding_unchanged':True,'game_writes':False,'capacity_work_executed':False,'scheduler_started':False,'master_modified':False,'full_goal_complete':False})
(dest/'executed_scripts/finalize_increment24.py').write_bytes(Path(__file__).read_bytes())
(dest/'executed_scripts/verify_auxiliary_worker_terminal.ps1').write_bytes((runtime/'verify_auxiliary_worker_terminal.ps1').read_bytes())
print(json.dumps({'status':'AUXILIARY_HEADER_READ_CANDIDATE_AND_ACTUAL_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':188,'preserved_prior_rows':1361150,'archive_parts_verified':parts+native_parts}))

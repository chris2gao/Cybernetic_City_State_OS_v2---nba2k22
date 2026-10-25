"""Match executed calendar code, actual raw comparisons and complete archives."""
import hashlib,json,subprocess,sys,zlib
from pathlib import Path
repo=Path.cwd();run=next(p for p in Path(__file__).resolve().parents if p.name=='run-20261024-nba2k22-world-data-implementation-002');dest=run/'06_执行/increment23';verified=dest/'verification-corrected';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
report=json.loads((verified/'operations_report.json').read_bytes());actual=json.loads((dest/'actual-calendar-report.json').read_bytes());head=report['candidate_code_head'];assert head==actual['candidate_code_head']
for name,digest in report['code_sha256'].items():
    relative=str((app/name).relative_to(repo)).replace('\\','/');blob=subprocess.run(['git','show',head+':'+relative],cwd=repo,capture_output=True,check=True).stdout
    assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
assert report['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 182 tests' in (verified/'tests.stderr.log').read_text(encoding='utf-8')
assert actual['prior_rows_preserved']==1351190 and actual['prior_tables_preserved']==85 and actual['games_checked']==1232 and actual['frozen_boxes_reused']==202 and actual['native_boxes_read']==36
assert actual['calendar_hidden_before_its_observation'] and actual['cumulative_phase_not_inferred']
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
save=run/'_runtime/world-saves/nba2k22_test_01';old=json.loads((save/'save.before-v18.json').read_bytes());new=json.loads((save/'save.json').read_bytes());assert {k:v for k,v in old.items() if k!='database_file'}=={k:v for k,v in new.items() if k!='database_file'};write(dest/'binding-declarations.json',{'before':old,'after':new,'identity_fields_unchanged':True,'old_database_retained':True})
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if preflight.returncode:raise RuntimeError('preflight failed: '+preflight.stderr[:500])
write(dest/'preflight.json',json.loads(preflight.stdout));artifact=run/'increment23_work_unit.yml'
validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],cwd=repo,capture_output=True,text=True,encoding='utf-8')
if validation.returncode:raise RuntimeError('MWU failed: '+validation.stdout[:500]+validation.stderr[:500])
receipt=json.loads((run/'06_执行/increment22/mwu_load_receipt.json').read_bytes());receipt.update({'artifact':artifact.name,'validator_exit_code':0,'validator_output':validation.stdout.strip()});write(dest/'mwu_load_receipt.json',receipt)
write(dest/'delivery_check.json',{'status':'NATIVE_CALENDAR_CANDIDATE_CODE_AND_RAW_EVIDENCE_CONSISTENT','candidate_code_head':head,'code_hashes_matched_to_commit':len(report['code_sha256']),'tests':182,'preserved_prior_rows':1351190,'raw_game_header_comparisons':actual['field_comparisons_with_raw_bytes'],'games_checked':1232,
    'snapshot_archive_parts_verified':parts,'native_source_archive_parts_verified':native_parts,'snapshot_decompressed_sha256_verified':True,'save_identity_preserved':True,'game_writes':False,'scheduler_started':False,'capacity_work_executed':False,'full_goal_complete':False,'master_modified':False})
(dest/'executed_scripts/finalize_increment23.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'status':'NATIVE_CALENDAR_CANDIDATE_CODE_AND_RAW_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':182,'preserved_prior_rows':1351190,'raw_field_comparisons':actual['field_comparisons_with_raw_bytes'],'archive_parts_verified':parts+native_parts}))

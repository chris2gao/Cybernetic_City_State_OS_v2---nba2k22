import hashlib,json,subprocess,sys,zlib
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;run=runtime.parent;dest=run/'06_执行/increment27';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
tested=json.loads((dest/'verification/operations_report.json').read_bytes());actual=json.loads((dest/'actual-period-stat-report.json').read_bytes());head=tested['candidate_code_head'];assert head==actual['candidate_code_head']=='3c8860a79fef8835704ac37b2d54034d25abc0e7'
for name,digest in tested['code_sha256'].items():
    relative=str((app/name).relative_to(repo)).replace('\\','/');blob=subprocess.run(['git','show',head+':'+relative],capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
assert tested['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 216 tests' in (dest/'verification/tests.stderr.log').read_text(encoding='utf-8')
assert actual['prior_rows_preserved']==1374426 and actual['prior_tables_preserved']==87 and actual['source_player_count']==3390 and actual['captured_reference_count']==3390 and actual['core_roster_sources']==461 and actual['core_roster_resolved_records']==370 and actual['core_roster_missing_records']==91
assert actual['raw_stat_field_comparisons']==11840 and actual['private_free_player_interval_checks']==50850 and actual['annual_bucket_units_unchanged'] and actual['save_binding_unchanged']
terminal=json.loads((dest/'worker-terminal.json').read_bytes());launch=json.loads((dest/'worker-launch.json').read_bytes());assert terminal['worker_process_absent'] and terminal['worker_pid']==launch['worker_pid']
assert actual['process_epoch']['pid']==launch['game_pid']==5092 and actual['process_epoch']['creation_filetime']!=actual['prior_process_epoch']['creation_filetime']
def check_parts(manifest,raw_expected=None):
    encoded=hashlib.sha256();decoded=hashlib.sha256();decoder=zlib.decompressobj(31)
    for part in manifest['parts']:
        assert Path(part['file']).name==part['file'];digest=hashlib.sha256();size=0
        with (dest/part['file']).open('rb') as src:
            while block:=src.read(4*1024*1024):
                digest.update(block);encoded.update(block);size+=len(block);pending=block
                while pending:decoded.update(decoder.decompress(pending,4*1024*1024));pending=decoder.unconsumed_tail
        assert size==part['bytes'] and digest.hexdigest()==part['sha256']
    decoded.update(decoder.flush());assert decoder.eof and not decoder.unused_data and encoded.hexdigest()==manifest['stream_sha256']
    if raw_expected:assert decoded.hexdigest()==raw_expected
    return len(manifest['parts'])
snapshot=json.loads((dest/'world-v19.snapshot.json').read_bytes());assert snapshot['database_sha256']==actual['after_database_sha256'];parts=check_parts(snapshot,snapshot['database_sha256']);native_parts=check_parts(json.loads((dest/'native-sources.archive.json').read_bytes()))
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:500];write(dest/'preflight.json',json.loads(preflight.stdout))
artifact=run/'increment27_work_unit.yml';validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],capture_output=True,text=True,encoding='utf-8');assert validation.returncode==0,validation.stdout[:500]+validation.stderr[:500]
receipt=json.loads((run/'06_执行/increment26/mwu_load_receipt.json').read_bytes());receipt.update({'artifact':artifact.name,'validator_exit_code':0,'validator_output':validation.stdout.strip()});write(dest/'mwu_load_receipt.json',receipt)
write(dest/'delivery_check.json',{'status':'FRESH_PROCESS_CURRENT_PERIOD_STAT_CODE_AND_ACTUAL_TYPED_EVIDENCE_CONSISTENT','candidate_code_head':head,'code_hashes_matched_to_commit':len(tested['code_sha256']),'tests':216,'preserved_prior_rows':1374426,'source_player_count':3390,'core_roster_subjects':461,'core_records':370,'core_missing_references':91,'raw_stat_field_comparisons':11840,'private_free_player_read_checks':50850,'snapshot_parts_verified':parts,'native_source_parts_verified':native_parts,'snapshot_decompressed_sha256_verified':True,'restarted_process_recalibrated':True,'save_binding_unchanged':True,'annual_buckets_unchanged':True,'game_writes':False,'getter_invocations':0,'capacity_work_executed':False,'master_modified':False,'full_goal_complete':False})
for name in (Path(__file__).name,'verify_period_worker_terminal.ps1'):(dest/'executed_scripts'/name).write_bytes((runtime/name).read_bytes())
print(json.dumps({'status':'FRESH_PROCESS_CURRENT_PERIOD_STAT_CODE_AND_ACTUAL_TYPED_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':216,'prior_rows_preserved':1374426,'raw_stat_field_comparisons':11840,'archive_parts_verified':parts+native_parts}))

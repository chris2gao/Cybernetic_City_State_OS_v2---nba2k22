import hashlib,json,shutil,subprocess,sys,zlib
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;run=r.parent;dest=run/'06_执行/increment34';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from database_operations import file_sha256
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
tested=json.loads((dest/'verification/operations_report.json').read_bytes());actual=json.loads((dest/'actual-current-coach-report.json').read_bytes());terminal=json.loads((dest/'worker-terminal.json').read_bytes());head=tested['candidate_code_head'];assert head==actual['candidate_code_head']=='27f2f17a9a9887c18315ac78e4d9a7289d729a23';assert tested['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 273 tests' in (dest/'verification/tests.stderr.log').read_text(encoding='utf-8')
assert terminal['worker_process_absent'] and actual['prior_rows_preserved']==1464967 and actual['prior_tables_preserved']==99 and actual['successful_units']==42 and actual['annual_buckets_unchanged'] and len(actual['sources'])==2
assert actual['signed_reference_comparisons']==sum(s['source_staff_count'] for s in actual['sources']) and actual['counter_and_marker_comparisons']==5*sum(s['resolved_subjects'] for s in actual['sources']) and actual['annual_reference_and_private_interval_checks']==6*sum(s['source_staff_count'] for s in actual['sources']) and actual['award_free_stat_interval_checks']==2*sum(s['distinct_stat_projections'] for s in actual['sources'])
for name,digest in tested['code_sha256'].items():
    relative=(app/name).relative_to(repo).as_posix();blob=subprocess.run(['git','show',head+':'+relative],capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
manifest=json.loads((dest/'world-v24.snapshot.json').read_bytes());encoded=hashlib.sha256();decoded=hashlib.sha256();decoder=zlib.decompressobj(31)
for part in manifest['parts']:
    assert file_sha256(dest/part['file'])==part['sha256'] and (dest/part['file']).stat().st_size==part['bytes']
    with (dest/part['file']).open('rb') as src:
        while block:=src.read(4*1024*1024):
            encoded.update(block);pending=block
            while pending:decoded.update(decoder.decompress(pending,4*1024*1024));pending=decoder.unconsumed_tail
decoded.update(decoder.flush());assert decoder.eof and not decoder.unused_data and encoded.hexdigest()==manifest['stream_sha256'] and decoded.hexdigest()==actual['database_sha256']==manifest['database_sha256']
native=json.loads((dest/'native-current-coach-evidence.archive.json').read_bytes());assert file_sha256(dest/native['file'])==native['sha256']
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:400];write(dest/'preflight.json',json.loads(preflight.stdout))
artifact=run/'increment34_work_unit.yml';validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],capture_output=True,text=True,encoding='utf-8');assert validation.returncode==0,validation.stdout[:400]+validation.stderr[:400];receipt=json.loads((dest.parent/'increment33/mwu_load_receipt.json').read_bytes());receipt.update(artifact=artifact.name,validator_exit_code=0,validator_output=validation.stdout.strip());write(dest/'mwu_load_receipt.json',receipt)
shutil.copyfile(Path(__file__),dest/'executed_scripts'/Path(__file__).name)
write(dest/'delivery_check.json',{'status':'CURRENT_COACH_WIN_LOSS_V24_SOURCE_TYPED_QUERY_HISTORY_AND_SNAPSHOT_CONSISTENT','candidate_code_head':head,'code_hashes_matched_to_commit':len(tested['code_sha256']),'tests':273,'schema_version':24,'tables':100,'columns':1775,'source_units':[s['unit_id'] for s in actual['sources']],'old_rows_preserved':1464967,'signed_references_compared':actual['signed_reference_comparisons'],'counters_and_marker_compared':actual['counter_and_marker_comparisons'],'snapshot_decompressed_sha256_verified':True,'annual_buckets_unchanged':True,'annual_positions1_to39_read':False,'annual_award_value_bytes_read':False,'computer_use_used':False,'game_writes':False,'capacity_work_executed':False,'full_goal_complete':False,'independent_acceptance':False})
print(json.dumps({'status':'DELIVERY_VERIFIED','tests':273,'tables':100,'signed_references_compared':actual['signed_reference_comparisons'],'snapshot_parts':len(manifest['parts']),'full_goal_complete':False}))

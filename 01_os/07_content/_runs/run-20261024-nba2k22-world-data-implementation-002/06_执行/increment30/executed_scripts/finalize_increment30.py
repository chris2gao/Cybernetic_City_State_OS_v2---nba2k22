import hashlib,json,subprocess,sys,zlib
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;run=runtime.parent;dest=run/'06_执行/increment30';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
tested=json.loads((dest/'verification/operations_report.json').read_bytes());actual=json.loads((dest/'actual-staff-report.json').read_bytes());head=tested['candidate_code_head'];assert head==actual['candidate_code_head']=='0e9e1366c82fde7a483bc6652eb8124630a77eb1'
for name,digest in tested['code_sha256'].items():
    relative=(app/name).relative_to(repo).as_posix();blob=subprocess.run(['git','show',head+':'+relative],capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
assert tested['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 246 tests' in (dest/'verification/tests.stderr.log').read_text(encoding='utf-8')
assert actual['prior_rows_preserved']==1397842 and actual['prior_tables_preserved']==92 and actual['core_teams']==30 and actual['team_slot_pointer_checks']==240 and actual['typed_scalar_label_comparisons']==actual['full_staff_source_slots']*174 and actual['annual_bucket_units_unchanged'] and actual['save_identity_unchanged'] and actual['old_database_retained_unchanged'] and actual['prior_finance_and_lineup_sources_unchanged'] and actual['player_value_reads']==actual['annual_staff_stat_references_read']==0
terminal=json.loads((dest/'worker-terminal.json').read_bytes());launch=json.loads((dest/'worker-launch.json').read_bytes());assert terminal['worker_process_absent'] and terminal['worker_pid']==launch['worker_pid'] and actual['process_epoch']['pid']==launch['game_pid']
def check_parts(manifest,expected=None):
    encoded=hashlib.sha256();decoded=hashlib.sha256();decoder=zlib.decompressobj(31)
    for part in manifest['parts']:
        assert Path(part['file']).name==part['file'];digest=hashlib.sha256();size=0
        with (dest/part['file']).open('rb') as src:
            while block:=src.read(4*1024*1024):
                digest.update(block);encoded.update(block);size+=len(block);pending=block
                while pending:decoded.update(decoder.decompress(pending,4*1024*1024));pending=decoder.unconsumed_tail
        assert size==part['bytes'] and digest.hexdigest()==part['sha256']
    decoded.update(decoder.flush());assert decoder.eof and not decoder.unused_data and encoded.hexdigest()==manifest['stream_sha256']
    if expected:assert decoded.hexdigest()==expected
    return len(manifest['parts'])
snapshot=json.loads((dest/'world-v22.snapshot.json').read_bytes());assert snapshot['database_sha256']==actual['after_database_sha256'];snap_parts=check_parts(snapshot,snapshot['database_sha256']);native_parts=check_parts(json.loads((dest/'native-sources.archive.json').read_bytes()))
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:500];write(dest/'preflight.json',json.loads(preflight.stdout))
artifact=run/'increment30_work_unit.yml';validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],capture_output=True,text=True,encoding='utf-8');assert validation.returncode==0,validation.stdout[:500]+validation.stderr[:500]
receipt=json.loads((run/'06_执行/increment29/mwu_load_receipt.json').read_bytes());receipt.update(artifact=artifact.name,validator_exit_code=0,validator_output=validation.stdout.strip());write(dest/'mwu_load_receipt.json',receipt)
master=subprocess.run(['git','rev-parse','origin/master'],capture_output=True,text=True,check=True).stdout.strip();assert master=='7742568ac677b3c16079887463f05e81cb1191ed'
write(dest/'delivery_check.json',{'status':'PUBLIC_NATIVE_STAFF_CODE_SCALARS_ROLES_AND_V22_HISTORY_CONSISTENT','candidate_code_head':head,'code_hashes_matched_to_commit':len(tested['code_sha256']),'tests':246,'prior_rows_preserved':1397842,'core_teams':30,'full_staff_source_slots':actual['full_staff_source_slots'],'qualified_canonical_aliases':actual['qualified_canonical_aliases'],'typed_scalar_label_comparisons':actual['typed_scalar_label_comparisons'],'team_slot_pointer_checks':240,'private_free_staff_interval_checks':actual['private_free_staff_interval_checks'],'snapshot_parts_verified':snap_parts,'native_source_parts_verified':native_parts,'snapshot_decompressed_sha256_verified':True,'process_recalibrated':True,'save_identity_unchanged':True,'annual_buckets_unchanged':True,'prior_finance_and_lineup_sources_unchanged':True,'game_writes':False,'getter_invocations':0,'player_value_reads':0,'annual_staff_stat_references_read':0,'computer_use_used':False,'capacity_work_executed':False,'origin_master':master,'master_modified':False,'full_goal_complete':False})
(dest/'executed_scripts'/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps({'status':'PUBLIC_NATIVE_STAFF_CODE_SCALARS_ROLES_AND_V22_HISTORY_CONSISTENT','candidate_code_head':head,'tests':246,'prior_rows_preserved':1397842,'typed_scalar_label_comparisons':actual['typed_scalar_label_comparisons'],'archive_parts_verified':snap_parts+native_parts}))

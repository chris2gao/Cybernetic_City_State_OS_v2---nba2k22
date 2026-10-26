import hashlib,json,subprocess,sys,zlib
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;run=runtime.parent;dest=run/'06_执行/increment29';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
tested=json.loads((dest/'verification/operations_report.json').read_bytes());actual=json.loads((dest/'actual-lineup-report.json').read_bytes());head=tested['candidate_code_head'];assert head==actual['candidate_code_head']=='1cc410befcebf9fb8848ad0dcabfc91e31666fb7'
for name,digest in tested['code_sha256'].items():
    relative=(app/name).relative_to(repo).as_posix();blob=subprocess.run(['git','show',head+':'+relative],capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
assert tested['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 235 tests' in (dest/'verification/tests.stderr.log').read_text(encoding='utf-8')
assert actual['prior_rows_preserved']==1382123 and actual['prior_tables_preserved']==88 and actual['core_teams']==30 and actual['global_slots']==390 and actual['named_lineup_slots']==1200 and actual['advanced_matrix_comparisons']==7200 and actual['pointer_reference_comparisons']==1590 and actual['annual_bucket_units_unchanged'] and actual['save_identity_unchanged'] and actual['old_database_retained_unchanged'] and actual['prior_finance_source_unchanged']
assert actual['player_rotation_value_comparisons']==actual['full_player_sources']*3 and actual['private_free_player_interval_checks']==actual['full_player_sources']*15
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
snapshot=json.loads((dest/'world-v21.snapshot.json').read_bytes());assert snapshot['database_sha256']==actual['after_database_sha256'];snap_parts=check_parts(snapshot,snapshot['database_sha256']);native_parts=check_parts(json.loads((dest/'native-sources.archive.json').read_bytes()))
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:500];write(dest/'preflight.json',json.loads(preflight.stdout))
artifact=run/'increment29_work_unit.yml';validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],capture_output=True,text=True,encoding='utf-8');assert validation.returncode==0,validation.stdout[:500]+validation.stderr[:500]
receipt=json.loads((run/'06_执行/increment28/mwu_load_receipt.json').read_bytes());receipt.update(artifact=artifact.name,validator_exit_code=0,validator_output=validation.stdout.strip());write(dest/'mwu_load_receipt.json',receipt)
master=subprocess.run(['git','rev-parse','origin/master'],capture_output=True,text=True,check=True).stdout.strip();assert master=='7742568ac677b3c16079887463f05e81cb1191ed'
write(dest/'delivery_check.json',{'status':'NATIVE_GLOBAL_LINEUP_CODE_RAW_REFERENCES_ROTATION_AND_V21_HISTORY_CONSISTENT','candidate_code_head':head,'code_hashes_matched_to_commit':len(tested['code_sha256']),'tests':235,'prior_rows_preserved':1382123,'core_teams':30,'global_slots':390,'named_lineup_slots':1200,'advanced_matrix_comparisons':7200,'player_rotation_value_comparisons':actual['player_rotation_value_comparisons'],'private_free_player_interval_checks':actual['private_free_player_interval_checks'],'snapshot_parts_verified':snap_parts,'native_source_parts_verified':native_parts,'snapshot_decompressed_sha256_verified':True,'process_recalibrated':True,'save_identity_unchanged':True,'annual_buckets_unchanged':True,'prior_finance_source_unchanged':True,'game_writes':False,'getter_invocations':0,'computer_use_used':False,'capacity_work_executed':False,'origin_master':master,'master_modified':False,'full_goal_complete':False})
(dest/'executed_scripts'/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps({'status':'NATIVE_GLOBAL_LINEUP_CODE_RAW_REFERENCES_ROTATION_AND_V21_HISTORY_CONSISTENT','candidate_code_head':head,'tests':235,'prior_rows_preserved':1382123,'advanced_matrix_comparisons':7200,'archive_parts_verified':snap_parts+native_parts}))

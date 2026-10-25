import hashlib,json,subprocess,sys,zlib
from datetime import date
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;run=runtime.parent;dest=run/'06_执行/increment26';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
tested=json.loads((dest/'verification/operations_report.json').read_bytes());actual=json.loads((dest/'actual-game-mode-report.json').read_bytes());head=tested['candidate_code_head'];assert head==actual['candidate_code_head']=='3057547feaec7d4dbc73588a26b4513d40a76681'
for name,digest in tested['code_sha256'].items():
    relative=str((app/name).relative_to(repo)).replace('\\','/');blob=subprocess.run(['git','show',head+':'+relative],capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
assert tested['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 206 tests' in (dest/'verification/tests.stderr.log').read_text(encoding='utf-8')
assert actual['prior_rows_preserved']==1374390 and actual['prior_tables_preserved']==86 and actual['raw_field_comparisons']==21 and actual['code_proof_bytes_verified']==800 and actual['cumulative_phase_not_inferred']
terminal=json.loads((dest/'worker-terminal.json').read_bytes());assert terminal['all_recorded_workers_absent'] and len(terminal['processes'])==3
for item in terminal['processes']:assert item['worker_pid']==json.loads((dest/item['launch_file']).read_bytes())['worker_pid'] and not item['process_present']
paired=json.loads((dest/'paired-native-dates.json').read_bytes());assert paired['status']=='CURRENT_PAIRED_NAMED_NATIVE_DATE_FIELDS_CAPTURED' and paired['context_before']['epoch']==paired['context_after']['epoch']==actual['process_epoch']
for field,raw in [('game_mode_today',bytes.fromhex(paired['mode_prefix_hex'])[20:24]),('season_date',bytes.fromhex(paired['season_prefix_hex'])[:4])]:
    word=int.from_bytes(raw,'little');minutes=word>>5&2047;month=word>>21&15;day=word>>16&31;year=2000+(word>>25)
    values={'word_raw':word,'id_raw':word&31,'minutes_since_midnight_raw':minutes,'day_raw':day,'month_raw':month,'base_year_offset_raw':word>>25,'native_iso_date':date(year,month+1,day).isoformat(),'native_time_hhmm':f'{minutes//60:02d}:{minutes%60:02d}'}
    assert all(paired[field][k]==v for k,v in values.items())
assert paired['game_mode_today']['native_iso_date']=='2021-11-20' and paired['season_date']['native_iso_date']=='2021-11-19' and paired['game_mode_period']==paired['season_period']=='REGULARSEASON'
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
sys.path.insert(0,str(app))
from database_operations import file_sha256
from query import league_calendar
db=runtime/'world-saves/nba2k22_test_01/world-v19.sqlite';assert file_sha256(db)==snapshot['database_sha256'] and league_calendar(db)['records'][0]['current_word_raw']==paired['season_date']['word_raw']
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:500];write(dest/'preflight.json',json.loads(preflight.stdout))
artifact=run/'increment26_work_unit.yml';validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],capture_output=True,text=True,encoding='utf-8');assert validation.returncode==0,validation.stdout[:500]+validation.stderr[:500]
receipt=json.loads((run/'06_执行/increment25/mwu_load_receipt.json').read_bytes());receipt.update({'artifact':artifact.name,'validator_exit_code':0,'validator_output':validation.stdout.strip()});write(dest/'mwu_load_receipt.json',receipt)
write(dest/'delivery_check.json',{'status':'NATIVE_GAME_MODE_STAGE_CODE_AND_ACTUAL_TYPED_EVIDENCE_CONSISTENT','candidate_code_head':head,'code_hashes_matched_to_commit':len(tested['code_sha256']),'tests':206,'preserved_prior_rows':1374390,'raw_field_comparisons':21,'paired_date_raw_field_comparisons':16,'paired_named_date_difference_verified':True,'prior_season_date_word_matches_fresh_pair':True,'fixed_date_offset_contract_asserted':False,'native_selector_code_bytes':800,'snapshot_parts_verified':parts,'native_source_parts_verified':native_parts,'snapshot_decompressed_sha256_verified':True,'save_identity_preserved':True,'game_writes':False,'getter_invocations':0,'annual_history_refreshed':False,'capacity_work_executed':False,'master_modified':False,'full_goal_complete':False})
for name in (Path(__file__).name,'check_game_mode_workers.ps1','read_paired_native_dates.py','start_paired_native_dates.ps1'):(dest/'executed_scripts'/name).write_bytes((runtime/name).read_bytes())
print(json.dumps({'status':'NATIVE_GAME_MODE_STAGE_CODE_AND_ACTUAL_TYPED_EVIDENCE_CONSISTENT','candidate_code_head':head,'tests':206,'prior_rows_preserved':1374390,'archive_parts_verified':parts+native_parts}))

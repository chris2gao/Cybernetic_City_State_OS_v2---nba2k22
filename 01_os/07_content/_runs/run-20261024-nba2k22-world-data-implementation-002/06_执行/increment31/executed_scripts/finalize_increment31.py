import hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;run=runtime.parent;dest=run/'06_执行/increment31';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
sys.path.insert(0,str(app))
from process_session import owner_is_live
from database_operations import file_sha256
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
tested=json.loads((dest/'verification/operations_report.json').read_bytes());actual=json.loads((dest/'worker-result.json').read_bytes());before=json.loads((dest/'before.json').read_bytes());terminal=json.loads((dest/'worker-terminal.json').read_bytes());head=tested['candidate_code_head']
assert head==actual['candidate_code_head']==before['candidate_code_head'];assert tested['exit_codes']=={'tests':0,'sqlite_smoke':0} and 'Ran 254 tests' in (dest/'verification/tests.stderr.log').read_text(encoding='utf-8')
assert actual['status']=='ACTUAL_RESTART_AUTO_RECONNECT_AND_RECEIPT_RECOVERY_VERIFIED' and terminal['worker_process_absent'] and not owner_is_live(actual['worker_identity'])
assert actual['reconnect_database_unchanged'] and actual['resume_database_unchanged'] and actual['annual_buckets_unchanged'] and actual['binding_unchanged'] and actual['reconnect_fact_units']==actual['resume_created_units']==0 and actual['old_unit_receipts_preserved']==38 and actual['successful_units']==39
for name,digest in tested['code_sha256'].items():
    relative=(app/name).relative_to(repo).as_posix();blob=subprocess.run(['git','show',head+':'+relative],capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest and hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
save=runtime/'world-saves/nba2k22_test_01';assert file_sha256(save/before['database_file'])==actual['after_database_sha256']
# Retain the small acquisition's source evidence alongside increment30's full
# v22 snapshot; this is not a new full snapshot or a proven restoration recipe.
paths=['reconnect-31-first','reconnect-31-second','restart-capture-31','restart-resume-31'];archive=dest/'restart-native-evidence.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
    for name in paths:tar.add(runtime/name,arcname=name)
archive_members=[]
with tarfile.open(archive,'r:gz') as tar:
    for member in tar:
        if member.isfile():
            digest=hashlib.sha256();src=tar.extractfile(member)
            while block:=src.read(1024*1024):digest.update(block)
            archive_members.append({'file':member.name,'bytes':member.size,'sha256':digest.hexdigest()})
write(dest/'native-evidence.archive.json',{'file':archive.name,'bytes':archive.stat().st_size,'sha256':file_sha256(archive),'members':archive_members,'base_database_snapshot':'../increment30/world-v22.snapshot.json','new_unit':actual['verification_capture_unit'],'post_delta_database_sha256':actual['after_database_sha256'],'contains_game_save':False,'restricted_owner_evidence':True})
scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('prepare_increment31.py','run_restart_worker31.py','start_restart_worker31.ps1','verify_restart_terminal31.ps1','finalize_increment31.py'):shutil.copyfile(runtime/name,scripts/name)
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:500];write(dest/'preflight.json',json.loads(preflight.stdout))
artifact=run/'increment31_work_unit.yml';validation=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],capture_output=True,text=True,encoding='utf-8');assert validation.returncode==0,validation.stdout[:500]+validation.stderr[:500]
receipt=json.loads((dest.parent/'increment30/mwu_load_receipt.json').read_bytes());receipt.update(artifact=artifact.name,validator_exit_code=0,validator_output=validation.stdout.strip());write(dest/'mwu_load_receipt.json',receipt)
write(dest/'delivery_check.json',{'status':'FRESH_PROCESS_AUTO_RECONNECT_AND_INTERRUPTED_REFRESH_RECOVERY_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':head,'code_hashes_matched_to_commit':len(tested['code_sha256']),'tests':254,'worker_terminal_verified':True,'source_archive_sha256':file_sha256(archive),'actual_process_restart_verified':True,'reconnect_created_units':0,'resume_created_units':0,'one_public_mode_verification_unit':actual['verification_capture_unit'],'annual_buckets_unchanged':True,'save_binding_unchanged':True,'full_goal_complete':False,'game_writes':False,'screenshots_requested':0,'computer_use_result':'TOP_LEVEL_WINDOW_TEXT_ONLY; NO_GAME_FIELDS','real_later_month_or_controller_death_tested':False,'capacity_work_executed':False,'master_modified':False})
print(json.dumps({'status':'DELIVERY_VERIFIED','tests':254,'code_head':head,'new_unit':actual['verification_capture_unit'],'archive_bytes':archive.stat().st_size,'full_goal_complete':False}))

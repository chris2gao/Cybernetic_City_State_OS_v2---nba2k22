import hashlib,json,shutil,subprocess,sys
from pathlib import Path
root=Path.cwd();run=root/'01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002';out=run/'06_执行/increment36';app=root/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
report=json.loads((out/'verification-report.json').read_text(encoding='utf-8'));operations=json.loads((out/'verification/operations.json').read_text(encoding='utf-8'))
assert all(r['exit_code']==0 for r in operations.values()) and 'Ran 286 tests' in (out/'verification/tests.stderr.log').read_text(encoding='utf-8')
assert (report['tables'],report['columns'],report['rows'],report['successful_units'])==(100,1775,1470952,42)
assert report['database_sha256_before']==report['database_sha256_after']=='f76b943e4c716748b4df1c8f6c94779fb57ebb312bbeeb9e4d4dfd97a024b218'
assert report['team_rows_compared']==30 and report['player_metric_count']==37 and report['metric_row_comparisons']>10000
assert report['standings_unit_id']=='organization:d89edd8d725f12db37509bed' and report['player_unit_id']=='live-world:62052310fffb4ca792946781'
for name,expected in report['code_sha256'].items():
    relative=(app/name).relative_to(root).as_posix();blob=subprocess.run(['git','show',report['candidate_code_head']+':'+relative],capture_output=True,check=True).stdout
    assert hashlib.sha256(blob).hexdigest()==expected==hashlib.sha256((app/name).read_bytes()).hexdigest(),name
artifact=run/'increment36_work_unit.yml';cmd=[sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu']
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr
receipt=json.loads((out.parent/'increment35/mwu_load_receipt.json').read_text(encoding='utf-8'));receipt.update(artifact=artifact.name,validator_exit_code=r.returncode,validator_output=r.stdout.strip());write(out/'mwu_load_receipt.json',receipt)
start=subprocess.run([sys.executable,str(run/'_runtime/preflight36.py')],capture_output=True,text=True,encoding='utf-8');assert start.returncode==0,start.stdout+start.stderr
for name in ('verify_league36.py','preflight36.py','finalize_increment36.py'):shutil.copyfile(run/'_runtime'/name,out/'executed_scripts'/name)
write(out/'delivery_check.json',{'status':'SINGLE_SOURCE_LEAGUE_QUERY_INCREMENT_VERIFIED','candidate_code_head':report['candidate_code_head'],'code_hashes_matched_to_commit':len(report['code_sha256']),'tests':286,'source_units':[report['standings_unit_id'],report['player_unit_id']],'team_rows_compared':30,'player_metric_count':37,'metric_row_comparisons':report['metric_row_comparisons'],'database_hash_unchanged':True,'new_capture_units':0,'new_live_game_reads':0,'computer_use_used':False,'capacity_work_executed':False,'full_goal_complete':False,'independent_acceptance':False})
print(json.dumps({'status':'DELIVERY_VERIFIED','tests':286,'player_metrics':37,'metric_row_comparisons':report['metric_row_comparisons'],'full_goal_complete':False}))

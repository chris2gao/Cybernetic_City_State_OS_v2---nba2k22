import fnmatch,hashlib,inspect,json,re,shutil,subprocess,sys
from pathlib import Path
root=Path.cwd();run=root/'01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002';out=run/'06_执行/increment37';app=root/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
import query
from observation_scope import PUBLIC_QUERIES
def git(*args):return subprocess.run(['git',*args],capture_output=True,text=True,encoding='utf-8',check=True).stdout.strip()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def yaml_lines(value,indent=0):
    result=[]
    for key,item in value.items():
        if isinstance(item,dict):result.append(' '*indent+key+':');result.extend(yaml_lines(item,indent+2))
        elif isinstance(item,list):
            if not item:result.append(' '*indent+key+': []')
            else:
                result.append(' '*indent+key+':');result.extend(' '*(indent+2)+'- '+json.dumps(v,ensure_ascii=False) for v in item)
        else:result.append(' '*indent+key+': '+json.dumps(item,ensure_ascii=False))
    return result
report=json.loads((out/'verification-report.json').read_bytes());head=report['candidate_code_head'];base='5cff5f7a6d826ed851954e83021e65372dcd2663';branch='task/nba2k22-world-data-full-implementation-20261024'
assert head=='cbdaba0cb263083ea04171f8222aab65a00e3d30' and git('rev-parse','HEAD')==head
assert report['tests']==301 and report['tables']==100 and report['columns']==1775 and report['rows']==1470952 and report['successful_units']==42 and report['real_filtered_rows_compared']==230
for name,digest in report['code_sha256'].items():assert hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
remote=git('ls-remote','origin','refs/heads/master','refs/heads/'+branch);refs={line.split()[1]:line.split()[0] for line in remote.splitlines()};assert refs['refs/heads/'+branch]==head and refs['refs/heads/master']=='7742568ac677b3c16079887463f05e81cb1191ed'
assert git('config','--get','core.hooksPath')=='.githooks'
preflight=subprocess.run([sys.executable,str(run/'_runtime/preflight37.py')],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stdout+preflight.stderr
artifact=run/'increment37_work_unit.yml';v=subprocess.run([sys.executable,'01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(artifact),'--require-mwu'],capture_output=True,text=True,encoding='utf-8');assert v.returncode==0,v.stdout+v.stderr
receipt=json.loads((out.parent/'increment36/mwu_load_receipt.json').read_bytes());receipt.update(artifact=artifact.name,validator_exit_code=0,validator_output=v.stdout.strip());write(out/'mwu_load_receipt.json',receipt)
apis=[]
for name in sorted(set(PUBLIC_QUERIES)|{'fact_fields'}):
    fn=getattr(query,name);apis.append({'name':name,'signature':str(inspect.signature(fn)),'module':fn.__module__})
write(out/'query-api-catalog.json',{'code_head':head,'role_policy':'GM public endpoints; owner diagnostics and direct SQLite access require owner handling','functions':apis})
help_result=subprocess.run([sys.executable,str(app/'cli.py'),'--help'],capture_output=True,text=True,encoding='utf-8');assert help_result.returncode==0;(out/'cli-help.txt').write_text(help_result.stdout,encoding='utf-8',newline='\n')
commands=re.findall(r"sub.add_parser\('([a-z0-9-]+)'",(app/'cli.py').read_text(encoding='utf-8'));write(out/'cli-command-catalog.json',{'code_head':head,'commands':commands,'actual_help_exit_code':0})
paths=git('diff','--name-only',base,head).splitlines();patterns=['08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/**','08_Domain_Applications/Antigravity_GM_Engine/research/native_access/**','08_Domain_Applications/Antigravity_GM_Engine/docs/development/NBA2K22_WORLD_DATA_**','01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/**']
outside=[p for p in paths if not any(fnmatch.fnmatchcase(p,pattern) for pattern in patterns)];assert not outside,outside[:5]
binary_count=sum(line.startswith('-\t-\t') for line in git('diff','--numstat',base,head).splitlines());write(out/'candidate-changed-paths.json',{'source_base':base,'source_head':head,'changed_paths':paths,'out_of_scope_paths':outside,'binary_artifact_count':binary_count})
pointer={'completion_pointer':{'packet_id':'nba2k22-world-data-full-implementation-01','status':'ready_for_independent_review','delivery_scope':'regular_season_engineering_baseline_only','source_branch':branch,'source_base':base,'source_head':head,'tested_code_head':head,'validation':{'tests':'301 regression tests and SQLite smoke passed; actual DDL/dictionary/integrity/FK/snapshot and 230 real filtered rows verified','candidate_caused_failures':0,'diff_scope':'passed','hook_guard':'passed'},'repository':{'changed_paths':paths,'out_of_scope_paths':0,'binary_artifact_count':binary_count,'worktree_clean':not bool(git('status','--porcelain')),'worktree_state_note':'Closeout evidence/documentation is still being committed; final delivery cleanliness is checked after publication'},'publication':{'transport':'local_git','replacement_gate':'not_applicable','expected_remote_head':head,'resulting_remote_head':refs['refs/heads/'+branch],'compare_and_swap':'not_applicable','fast_forward_verified':True,'push_performed':True,'master_modified':False,'force_push':False},'evidence_ref':'06_执行/increment37/verification-report.json','human_scope_ref':'human_baseline_closeout_20261026.md','full_underlying_system_complete':False,'full_lifecycle_acceptance':False,'independent_review':'NOT_RUN','master_integration':'NOT_PERFORMED','next_owner':'Human'}}
conclusions=run/'08_结论';conclusions.mkdir(exist_ok=True);(conclusions/'engineering_baseline_completion.yml').write_text('\n'.join(yaml_lines(pointer))+'\n',encoding='utf-8',newline='\n')
manifest={'format':'NBA2K22_REGULAR_SEASON_ENGINEERING_BASELINE_V1','code_head':head,'source_branch':branch,'scope':'Human-requested regular-season baseline closeout; full system not complete','schema_version':24,'tables':100,'columns':1775,'rows_including_metadata_and_links':1470952,'successful_capture_units':42,'save_id':'nba2k22_test_01','native_save_filename':'MyLEAGUE0003','bound_database':str(run/'_runtime/world-saves/nba2k22_test_01/world-v24.sqlite'),'database_sha256':report['database_sha256_after'],'snapshot_manifest_ref':'06_执行/increment34/world-v24.snapshot.json','source_inventory_ref':'06_执行/increment37/source-coverage.json','table_inventory_ref':'06_执行/increment37/table-inventory.json','field_maturity_ref':'06_执行/increment37/field-maturity.json','verification_ref':'06_执行/increment37/verification-report.json','handoff_ref':'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/BASELINE_HANDOFF.md','independent_review':'NOT_RUN','master_integration':'NOT_PERFORMED','stop_further_development_per_Human':True}
write(out/'baseline-manifest.json',manifest)
for name in ('finalize_baseline37.py',):shutil.copyfile(run/'_runtime'/name,out/'executed_scripts'/name)
print(json.dumps({'status':'BASELINE_DOCUMENTATION_AND_CANDIDATE_POINTER_VALIDATED','source_head':head,'public_query_functions':len(apis),'cli_commands':len(commands),'changed_paths':len(paths),'out_of_scope_paths':len(outside),'binary_artifact_count':binary_count,'full_system_complete':False}))

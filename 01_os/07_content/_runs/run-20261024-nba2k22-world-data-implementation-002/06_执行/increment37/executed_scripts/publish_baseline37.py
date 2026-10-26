import fnmatch,hashlib,json,shutil,subprocess,sys
from pathlib import Path
root=Path.cwd();run=root/'01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002';out=run/'06_执行/increment37';runtime=run/'_runtime';app=root/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
def git(*args):return subprocess.run(['git',*args],capture_output=True,text=True,encoding='utf-8',check=True).stdout.strip()
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def yaml_lines(value,indent=0):
    result=[]
    for key,item in value.items():
        if isinstance(item,dict):result.append(' '*indent+key+':');result.extend(yaml_lines(item,indent+2))
        elif isinstance(item,list):
            if not item:result.append(' '*indent+key+': []')
            else:result.append(' '*indent+key+':');result.extend(' '*(indent+2)+'- '+json.dumps(v,ensure_ascii=False) for v in item)
        else:result.append(' '*indent+key+': '+json.dumps(item,ensure_ascii=False))
    return result
branch='task/nba2k22-world-data-full-implementation-20261024';base='5cff5f7a6d826ed851954e83021e65372dcd2663';head=git('rev-parse','HEAD');report=json.loads((out/'verification-report.json').read_bytes());code=report['candidate_code_head']
assert git('branch','--show-current')==branch and not git('status','--porcelain');assert git('config','--get','core.hooksPath')=='.githooks'
for name,digest in report['code_sha256'].items():assert hashlib.sha256((app/name).read_bytes()).hexdigest()==digest,name
before=git('ls-remote','origin','refs/heads/master','refs/heads/'+branch);prior={line.split()[1]:line.split()[0] for line in before.splitlines()};assert prior['refs/heads/'+branch]==code and prior['refs/heads/master']=='7742568ac677b3c16079887463f05e81cb1191ed'
subprocess.run(['git','merge-base','--is-ancestor',code,head],check=True)
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(root),'--json'],capture_output=True,text=True,encoding='utf-8');(runtime/'publication-preflight37.stdout.log').write_text(preflight.stdout,encoding='utf-8');(runtime/'publication-preflight37.stderr.log').write_text(preflight.stderr,encoding='utf-8');assert preflight.returncode==0,preflight.stdout[-800:]+preflight.stderr[-300:]
cmd=['git','-c','http.version=HTTP/1.1','-c','http.postBuffer=268435456','-c','http.lowSpeedLimit=1024','-c','http.lowSpeedTime=60','push','origin',branch]
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(runtime/'baseline-candidate-push37.stdout.log').write_text(r.stdout,encoding='utf-8');(runtime/'baseline-candidate-push37.stderr.log').write_text(r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout[-600:]+r.stderr[-600:]
after=git('ls-remote','origin','refs/heads/master','refs/heads/'+branch);refs={line.split()[1]:line.split()[0] for line in after.splitlines()};assert refs['refs/heads/'+branch]==head and refs['refs/heads/master']==prior['refs/heads/master'];assert not git('status','--porcelain')
paths=git('diff','--name-only',base,head).splitlines();patterns=['08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/**','08_Domain_Applications/Antigravity_GM_Engine/research/native_access/**','08_Domain_Applications/Antigravity_GM_Engine/docs/development/NBA2K22_WORLD_DATA_**','01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/**'];outside=[p for p in paths if not any(fnmatch.fnmatchcase(p,pattern) for pattern in patterns)];assert not outside
binary_count=sum(line.startswith('-\t-\t') for line in git('diff','--numstat',base,head).splitlines())
publication={'transport':'local_git','replacement_gate':'not_applicable','expected_remote_head':head,'resulting_remote_head':refs['refs/heads/'+branch],'previous_remote_head':prior['refs/heads/'+branch],'compare_and_swap':'not_applicable','fast_forward_verified':True,'push_performed':True,'master_modified':False,'force_push':False}
pointer={'completion_pointer':{'packet_id':'nba2k22-world-data-full-implementation-01','status':'ready_for_independent_review','delivery_scope':'regular_season_engineering_baseline_only','source_branch':branch,'source_base':base,'source_head':head,'tested_code_head':code,'validation':{'tests':'301 regression tests and SQLite smoke passed; actual DDL/dictionary/integrity/FK/snapshot and 230 real filtered rows verified','candidate_caused_failures':0,'diff_scope':'passed','hook_guard':'passed'},'repository':{'changed_paths':paths,'out_of_scope_paths':0,'binary_artifact_count':binary_count,'worktree_clean':True,'worktree_state_note':'Measured clean before/after publishing source_head; this later receipt/pointer commit adds only closeout metadata'},'publication':publication,'evidence_ref':'06_执行/increment37/verification-report.json','human_scope_ref':'human_baseline_closeout_20261026.md','full_underlying_system_complete':False,'full_lifecycle_acceptance':False,'independent_review':'NOT_RUN','master_integration':'NOT_PERFORMED','next_owner':'Human'}}
(run/'08_结论/engineering_baseline_completion.yml').write_text('\n'.join(yaml_lines(pointer))+'\n',encoding='utf-8',newline='\n')
write(out/'candidate-publication.json',{'candidate_source_head':head,'tested_code_head':code,'candidate_worktree_clean_before_after':True,'preflight_exit_code':preflight.returncode,'push_exit_code':r.returncode,'remote_master_before':prior['refs/heads/master'],'remote_master_after':refs['refs/heads/master'],'publication':publication,'source_diff_paths':len(paths),'out_of_scope_paths':0,'binary_artifact_count':binary_count,'independent_review':'NOT_RUN','full_system_complete':False})
write(out/'candidate-changed-paths.json',{'source_base':base,'source_head':head,'changed_paths':paths,'out_of_scope_paths':outside,'binary_artifact_count':binary_count})
for source,target in [('baseline-candidate-push37.stdout.log','candidate-push.stdout.log'),('baseline-candidate-push37.stderr.log','candidate-push.stderr.log'),('publication-preflight37.stdout.log','candidate-preflight.stdout.log'),('publication-preflight37.stderr.log','candidate-preflight.stderr.log')]:shutil.copyfile(runtime/source,out/target)
shutil.copyfile(Path(__file__),out/'executed_scripts'/Path(__file__).name)
print(json.dumps({'status':'BASELINE_CANDIDATE_PUBLISHED_AND_READ_BACK','candidate_source_head':head,'tested_code_head':code,'worktree_clean_at_candidate_publication':True,'changed_paths':len(paths),'master_unchanged':True,'next_owner':'Human'}))

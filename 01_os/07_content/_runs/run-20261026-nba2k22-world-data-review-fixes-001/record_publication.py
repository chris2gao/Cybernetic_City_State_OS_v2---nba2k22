"""Record observed source publication; never write or merge master."""
import json
from pathlib import Path
import subprocess

root=Path.cwd();run=Path(__file__).resolve().parent
def git(*args):return subprocess.check_output(['git',*args],text=True,encoding='utf-8').strip()
branch='task/nba2k22-world-data-review-fixes-20261026'
candidate=git('rev-parse','HEAD')
assert candidate=='b3aa16981d73804604cf68a87b27a3eb721f696a'
assert git('branch','--show-current')==branch
remote={line.split()[1]:line.split()[0] for line in git('ls-remote','origin','refs/heads/master','refs/heads/'+branch).splitlines()}
assert remote['refs/heads/'+branch]==candidate
assert remote['refs/heads/master']=='7742568ac677b3c16079887463f05e81cb1191ed'
tested='b847f717df6702fe6251872d64aed476ac707f6f'
app='08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
assert not git('diff','--name-only',tested,candidate,'--',app)
paths=git('diff','--name-only','17ec1cea88c2bb6c36264792f70c94bef9a8bdb4',candidate).splitlines()
prefix=run.relative_to(root).as_posix()
assert paths and all(p.startswith(app+'/') or p.startswith(prefix+'/') for p in paths)
receipt={'status':'SOURCE_BRANCH_PUBLISHED_AND_READ_BACK','delivery_candidate':candidate,'source_branch':branch,'remote_source_head_at_readback':remote['refs/heads/'+branch],'remote_master_head':remote['refs/heads/master'],'master_changed':False,'master_write_or_merge':'NOT_PERFORMED','tested_candidate':tested,'application_tree_equal_to_tested_candidate':True,'application_tree':git('rev-parse',candidate+':'+app),'changed_paths_allowlist_pass':True,'changed_path_count':len(paths),'core_hooks_path':git('config','--get','core.hooksPath'),'normal_push_exit_code':0,'workflow_publication_gate_exit_code':0,'independent_review':'NOT_RUN','human_final_acceptance':'NOT_CLAIMED','receipt_commit_follows_delivery_candidate':True,'meaning':'Review source_head pins the published delivery candidate. A subsequent receipt-only commit records this observation without changing the tested application. Final remote receipt head is read back separately.'}
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
write(run/'08_结论/publication-receipt.json',receipt)
p=run/'08_结论/review_fixes_completion.yml'
pointer=json.loads(p.read_text(encoding='utf-8'))
pointer['completion_pointer']['source_head']=candidate
pointer['completion_pointer']['verified_application_tree']=receipt['application_tree']
pointer['completion_pointer']['application_tree_equal_to_tested_candidate']=True
write(p,pointer)
print(json.dumps({k:receipt[k] for k in ('status','delivery_candidate','remote_master_head','application_tree_equal_to_tested_candidate','changed_paths_allowlist_pass')}))

"""Fetch immutable Git content only, and run published normalization/Core static checks."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
CORE=Path('C:/Users/gk/.codex/worktrees/nba2k22-bic-os-core-08d8e534')
S01='f1a7159540ec5c586e044de48217f96149d9be0b'
S25='f082f853ca4388d498371a101621ce176e6e22ee'
REQ='01_os/07_content/_runs/run-20261104-nba2k22-basketball-intelligence-core-requirement-001/'
PLAN='01_os/07_content/_runs/run-20261104-nba2k22-bic-batch1-planning-001/'
sources=[]
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def save_source(commit,path,target):
    data=git('show',commit+':'+path);p=OUT/target;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    sources.append({'commit':commit,'path':path,'git_blob':git('rev-parse',commit+':'+path).decode().strip(),'sha256':hashlib.sha256(data).hexdigest(),'copy':p.relative_to(OUT).as_posix()})
for name in ('01a_A0_consensus_v1.json','01a_Human_confirmation_v1.json','01b_requirement_result_A_candidate_v2.json','01b_Human_confirmation_v2.json'):
    save_source('90d1801003e7a49531ef377137a2a975125bdd06',REQ+'requirement/'+name,'sources/requirement/'+name)
save_source(S01,REQ+'stage01_canonicalize_v1.py','sources/stage01_canonicalize_v1.py')
for name in ('02_evidence_CANDIDATE_v1.json','02_evidence_SOURCE_REVIEW_v1.json','03_result_B_CANDIDATE_v2.json','04_tests_CANDIDATE_v2.json','05_steps_CANDIDATE_v2.json','BATCH1_ADMISSION_LEDGER_v1.json'):
    save_source(S25,PLAN+name,'sources/planning/'+name)
(OUT/'SOURCE_MANIFEST.json').write_text(json.dumps({'sources':sources},indent=2)+'\n',encoding='utf-8',newline='\n')
commands=[('stage01_normalize',[sys.executable,'-B','-X','utf8',str(OUT/'sources/stage01_canonicalize_v1.py'),'--repo-root',str(ROOT),'--core-root',str(CORE),'--output-dir',str(OUT/'stage01')]),('core_static',[sys.executable,'-B','-X','utf8',str(CORE/'01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py'),'static',str(CORE),'--json-output'])]
receipts=[]
for name,cmd in commands:
    start=time.perf_counter();result=subprocess.run(cmd,cwd=ROOT,capture_output=True)
    (OUT/(name+'.stdout.log')).write_bytes(result.stdout);(OUT/(name+'.stderr.log')).write_bytes(result.stderr)
    receipts.append({'name':name,'command':cmd,'exit_code':result.returncode,'seconds':time.perf_counter()-start,'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(result.stderr).hexdigest()})
(OUT/'initial_validation_receipts.json').write_text(json.dumps({'checked_at':datetime.now(timezone.utc).isoformat(),'core_sha':subprocess.check_output(['git','-C',str(CORE),'rev-parse','HEAD']).decode().strip(),'commands':receipts},indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps([{'name':r['name'],'exit_code':r['exit_code'],'seconds':r['seconds']} for r in receipts]))

"""Run exact-candidate official validation; retain rejection without converting it to PASS."""
import argparse,hashlib,json,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
CORE=Path('C:/Users/gk/.codex/worktrees/nba2k22-bic-os-core-08d8e534')
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);a=p.parse_args()
cmd=[sys.executable,'-B','-X','utf8',str(CORE/'01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py'),'validate',str(OUT/'stage_candidates'),'--repo-root',str(ROOT),'--candidate',a.candidate,'--json-output']
start=time.perf_counter();result=subprocess.run(cmd,cwd=ROOT,capture_output=True)
for name,data in [('stdout',result.stdout),('stderr',result.stderr)]: (OUT/('core_validate.'+name+'.log')).write_bytes(data)
receipt={'checked_at':datetime.now(timezone.utc).isoformat(),'candidate':a.candidate,'core_sha':subprocess.check_output(['git','-C',str(CORE),'rev-parse','HEAD']).decode().strip(),'runner_sha256':hashlib.sha256((CORE/'01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py').read_bytes()).hexdigest(),'command':cmd,'exit_code':result.returncode,'seconds':time.perf_counter()-start,'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(result.stderr).hexdigest(),'result':json.loads(result.stdout),'formal_seven_stage_pass':result.returncode==0,'publication_history_gate':'NOT_REACHED_IF_STRUCTURAL_STAGE_STATE_REJECTED','interpretation':'Candidate artifacts deliberately retain pending owner acceptance. Rejection is an observed formal non-pass, not a failed offline engineering test.'}
(OUT/'formal_validation_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'candidate':a.candidate,'official_exit_code':result.returncode,'findings':receipt['result']['findings']}))

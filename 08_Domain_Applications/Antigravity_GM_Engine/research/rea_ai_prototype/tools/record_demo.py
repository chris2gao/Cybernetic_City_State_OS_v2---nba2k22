"""Capture actual offline CLI/test outputs; no game attach."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];repo=root.parents[3];run=repo/'01_os/07_content/_runs/run-20261027-nba2k22-rea-ai-prototype-exploration-001'
output=run/'06_执行';logs=run/'07_测试执行';output.mkdir(parents=True,exist_ok=True);logs.mkdir(parents=True,exist_ok=True)
commands=[('semantic-tests',[sys.executable,'-B','-X','utf8','-m','unittest','discover','-s',str(root/'tests'),'-v']),('demo',[sys.executable,'-B','-X','utf8',str(root/'cli.py'),'demo','--verify','--output',str(output/'demo_receipts.json')]),('knowledge-coach',[sys.executable,'-B','-X','utf8',str(root/'cli.py'),'knowledge','show','AI_COACH_DEFENSE_M1','--role','COACH']),('evidence-contract',[sys.executable,'-B','-X','utf8',str(root/'verify_evidence.py')])]
records=[]
for name,command in commands:
 completed=subprocess.run(command,cwd=repo,capture_output=True,timeout=90)
 (logs/(name+'.stdout.log')).write_bytes(completed.stdout);(logs/(name+'.stderr.log')).write_bytes(completed.stderr)
 records.append({'check':name,'exit_code':completed.returncode,'stdout_sha256':hashlib.sha256(completed.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(completed.stderr).hexdigest()})
 if completed.returncode:raise RuntimeError(name+' failed; inspect captured log')
(logs/'development_checks.json').write_text(json.dumps({'scope':'actual development-time offline checks; exact-candidate managed verification follows','checks':records},indent=2),encoding='utf-8')
pkg=Path(os.environ['APPDATA'])/'npm/node_modules/rea-agents/package.json'
runtime={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version.split()[0],'node':subprocess.check_output(['C:/Program Files/nodejs/node.exe','--version']).decode().strip(),'REA_package_version':json.loads(pkg.read_text())['version'],'official_REA_reference_commit':'570abe95f2a35b5c580a5ec2fca90c33d4114bdc','official_commit_verification':'gh api commit identity queried in current task; reference separate from installed npm package','game_build_sha256':'1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5','authorization':'HUMAN_LIVE_INSPECTION_APPROVAL.md','business_native_calls':0,'business_memory_writes':0,'game_scene_changes':0,'independent_review':'NOT_ESTABLISHED'}
(output/'runtime_facts.json').write_text(json.dumps(runtime,indent=2),encoding='utf-8')
print(json.dumps({'checks':records,'runtime':runtime,'demo_receipts':str(output/'demo_receipts.json')}))

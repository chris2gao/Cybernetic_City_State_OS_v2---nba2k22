"""Capture full OS verification output outside strict attempts; no retry or cleanup."""
import json, pathlib, subprocess, sys, tempfile, uuid
ROOT=pathlib.Path(__file__).resolve().parents[4]
RUN='01_os/07_content/_runs/run-20261022-world-source-model-seed-01-fix2/'
def main():
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    out=pathlib.Path(tempfile.mkdtemp(prefix='seed_fix2_verification_'))
    attempt=out/'attempt'
    py=sys.executable
    pre=[py,'-B','01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',RUN+'task_packet.yml','--repo-root',str(ROOT),'--json']
    commands=[]
    for name,argv in [('preflight',pre)]+[(mode,[py,'-B','01_os/06_execution/task_discipline/managed_verification/managed_verify.py',mode,'--repo-root',str(ROOT),'--candidate',sha,'--plan',RUN+'verification_plan.json','--attempt',str(attempt)]) for mode in ['run','inspect']]:
        p=subprocess.run(argv,cwd=ROOT,capture_output=True)
        (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
        commands.append({'mode':name,'exit_code':p.returncode})
        print(name,'exit_code='+str(p.returncode),flush=True)
        if p.returncode:
            print(p.stdout.decode('utf-8',errors='replace')[-2400:]);print(p.stderr.decode('utf-8',errors='replace')[-800:])
            break
    receipt={'candidate_sha':sha,'external_directory':str(out),'attempt':str(attempt),'commands':commands}
    (out/'invocation_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
    raise SystemExit(0 if len(commands)==3 and all(x['exit_code']==0 for x in commands) else 1)
if __name__=='__main__':main()

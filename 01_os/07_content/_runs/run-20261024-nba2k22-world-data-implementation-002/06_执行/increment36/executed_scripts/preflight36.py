import json,subprocess,sys
from pathlib import Path
root=Path.cwd();run=root/'01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002';out=run/'06_执行/increment36';out.mkdir(parents=True,exist_ok=True)
cmd=[sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(root),'--allow-dirty','--json']
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(out/'preflight.stdout.log').write_text(r.stdout,encoding='utf-8');(out/'preflight.stderr.log').write_text(r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout[-800:]+r.stderr[-300:]
report=json.loads(r.stdout);(out/'preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'exit_code':r.returncode,'status':report.get('status'),'keys':list(report)},ensure_ascii=False))

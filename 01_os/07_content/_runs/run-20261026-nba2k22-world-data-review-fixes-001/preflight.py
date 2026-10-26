import json,subprocess,sys
from pathlib import Path
root=Path.cwd();run=Path(__file__).resolve().parent;out=run/'evidence';out.mkdir(exist_ok=True)
r=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(root),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8')
(out/'preflight.stdout.log').write_text(r.stdout,encoding='utf-8');(out/'preflight.stderr.log').write_text(r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout[-900:]+r.stderr[-300:]
value=json.loads(r.stdout);(out/'preflight.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'exit_code':r.returncode,'hard_failures':value['hard_failures']}))

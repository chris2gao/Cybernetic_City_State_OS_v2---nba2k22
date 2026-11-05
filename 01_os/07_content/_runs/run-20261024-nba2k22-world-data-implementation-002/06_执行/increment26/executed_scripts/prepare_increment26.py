import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();run=Path(__file__).resolve().parent.parent;dest=run/'06_执行/increment26';dest.mkdir(parents=True,exist_ok=False)
result=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert result.returncode==0,result.stderr[:500]
(dest/'preflight-before.json').write_text(json.dumps(json.loads(result.stdout),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Increment26 bounded Native-selector preflight passed.')

import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();run=Path(__file__).resolve().parent.parent;dest=run/'06_执行/increment28';dest.mkdir(parents=True,exist_ok=False)
result=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert result.returncode==0,result.stderr[:500]
(dest/'preflight-before.json').write_text(json.dumps(json.loads(result.stdout),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(dest/'ui-observation-attempt.json').write_text(json.dumps({'tool':'computer-use @oai/sky through node_repl','target_app':'process:E:\\games\\NBA 2K22\\NBA2K22.exe','window_id':327854,'window_title':'NBA 2K22','window_restored':True,'game_button_or_key_inputs_sent':False,'accessibility_result':'Window title and root window element only; no game data page text','screenshot_errors':['FrameArrived timed out: timed out waiting on channel','window capture timed out: timed out waiting on channel'],'ui_data_observed':False,'ui_acceptance_claimed':False,'scope_after_failure':'Continue bounded Native metadata work; no display-mode/settings workaround'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Increment28 Native finance metadata preflight passed; UI observation remains unproved.')

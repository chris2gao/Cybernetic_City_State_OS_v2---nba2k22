import argparse,hashlib,json,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();root=Path(__file__).parent;out=Path(a.out)
subprocess.run([sys.executable,'-B','-X','utf8',str(root/'build_preflight_probe.py'),'--out',str(out),'--team','20'],check=True,capture_output=True)
prefix=(out/'native_preflight.js').read_text(encoding='utf-8').split('const events=[],errors=[],hooks=[];')[0]
prefix=prefix.replace('playbook_ids:','referenced_object_ids:').replace('current_gameplan_book_ids:','current_gameplan_referenced_ids:')
source=prefix+'\n'+(root/'gui_thread_bridge.js').read_text(encoding='utf-8')+'\n'+(root/'coach_visible.js').read_text(encoding='utf-8');path=out/'coach_visible.js'
if path.exists():raise FileExistsError('Fresh exact-script package required')
path.write_text(source,encoding='utf-8');print(json.dumps({'script_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_call_budget':1,'scope':'IND Rick Carlisle defense14 ->13; retain for Human inspection'}))

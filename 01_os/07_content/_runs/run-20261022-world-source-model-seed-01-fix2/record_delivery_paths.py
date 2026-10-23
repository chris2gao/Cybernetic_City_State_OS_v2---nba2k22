"""Record the exact pending delivery path set, including closure evidence itself."""
import json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[4]
HERE=pathlib.Path(__file__).resolve().parent
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT).decode('utf-8')
path=HERE/'changed_paths.json'
body=json.loads(path.read_bytes())
changed=set(filter(None,git('diff','--name-only','-z',body['base_sha'],'HEAD').split('\0')))
dirty=[p for p in git('status','--porcelain','-z','--untracked-files=all').split('\0') if p]
assert all(p[:2] not in ('R ',' R','C ',' C') for p in dirty),'handle renames explicitly'
changed.update(p[3:] for p in dirty)
body['final_delivery_paths']=sorted(changed)
body['final_delivery_path_count']=len(changed)
body['closure_note']='Repair source SHA is separately fixed. Final delivery additionally carries these exact evidence/closure paths; no hidden or inherited broad allowlist.'
path.write_bytes((json.dumps(body,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print('Exact pending delivery path count:',len(changed))

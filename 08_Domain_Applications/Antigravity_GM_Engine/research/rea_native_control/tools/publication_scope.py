"""Task-local scope/secret-pattern capture, not a game or functional test."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--stage',action='store_true');p.add_argument('--manifest',required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];repo=root.parents[3];base='f8746503a29b86b7cdb3a0d624a0cd5603c69f19'
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
paths=sorted(set(git('diff','--name-only','-z',base).decode().split('\0')+git('ls-files','--others','--exclude-standard','-z').decode().split('\0'))-{''})
allowed=['08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/','01_os/07_content/_runs/run-20261027-nba2k22-myleague-native-control-discovery-001/'];rows=[]
for name in paths:
 if not any(name.startswith(prefix) for prefix in allowed):raise ValueError('Changed path outside task scope: '+name)
 path=repo/name
 if path.suffix.lower() in {'.exe','.dll','.iff','.dds','.scne','.db','.sqlite','.env','.pem','.key'}:raise ValueError('Excluded artifact: '+name)
 b=path.read_bytes()
 if re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bghp_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}|\bsk-proj-[A-Za-z0-9_-]{24,}',b):raise ValueError('Secret-like pattern; do not print')
 rows.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
manifest=Path(a.manifest);manifest.parent.mkdir(parents=True,exist_ok=True);manifest.write_text(json.dumps({'base':base,'files':rows},indent=2)+'\n',encoding='utf-8');spec=manifest.with_suffix('.nul');spec.write_bytes(b'\0'.join(x.encode() for x in paths)+b'\0')
if a.stage:subprocess.run(['git','add','--pathspec-from-file='+str(spec),'--pathspec-file-nul'],cwd=repo,check=True,capture_output=True)
print(json.dumps({'scope_verified':True,'files':len(rows),'bytes':sum(r['bytes'] for r in rows),'secret_pattern_matches':0,'game_assets_or_saves':0,'staged':a.stage}))

"""Scope/content audit of this task's delta; never prints matched sensitive text."""
import argparse,fnmatch,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--stage',action='store_true');p.add_argument('--pathspec',required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[5];base='4dbfde51bda76a3dbb3454d5ae42135592c8332e'
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
paths=sorted(set(git('diff','--name-only','-z',base).decode().split('\0')+git('ls-files','--others','--exclude-standard','-z').decode().split('\0'))-{''})
allowed=['08_Domain_Applications/Antigravity_GM_Engine/research/rea_ai_prototype/*','08_Domain_Applications/Antigravity_GM_Engine/docs/development/REA_AI_MECHANISM_KNOWLEDGE_*','01_os/07_content/_runs/run-20261027-nba2k22-rea-ai-prototype-exploration-001/*']
for path in paths:
 assert any(fnmatch.fnmatchcase(path,pattern) for pattern in allowed),path
 assert Path(path).suffix.lower() not in {'.exe','.dll','.iff','.dds','.scne','.sqlite','.db'},path
 data=(repo/path).read_bytes()
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bghp_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}|\bsk-proj-[A-Za-z0-9_-]{24,}',data),'secret-like literal: stop without printing'
 if '/evidence/' in path and path.endswith('.json'):assert not re.search(rb'0x[0-9a-fA-F]{12,16}',data),'address-like token needs classification in '+path
spec=Path(a.pathspec);spec.write_bytes(b'\0'.join(path.encode() for path in paths)+b'\0')
if a.stage:subprocess.run(['git','add','--pathspec-from-file='+str(spec),'--pathspec-file-nul'],cwd=repo,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(json.dumps({'delta_paths':len(paths),'bytes':sum((repo/p).stat().st_size for p in paths),'scope_verified':True,'secret_pattern_matches':0,'game_asset_payloads':0,'staged':a.stage}))

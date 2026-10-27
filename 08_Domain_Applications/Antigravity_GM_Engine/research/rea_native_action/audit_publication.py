import argparse,fnmatch,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--stage',action='store_true');p.add_argument('--pathspec',required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[4];base='7397332bac36406704a290f70099f02025174ce9'
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
paths=sorted(set(git('diff','--name-only','-z',base).decode().split('\0')+git('ls-files','--others','--exclude-standard','-z').decode().split('\0'))-{''})
allowed=['08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/*','08_Domain_Applications/Antigravity_GM_Engine/research/rea_ai_prototype/*','01_os/07_content/_runs/run-20261027-nba2k22-rea-native-ai-action-invocation-001/*']
for path in paths:
 assert any(fnmatch.fnmatchcase(path,rule) for rule in allowed),path
 assert Path(path).suffix.lower() not in {'.exe','.dll','.iff','.dds','.scne','.db','.sqlite'},path
 raw=(repo/path).read_bytes();assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bghp_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}|\bsk-proj-[A-Za-z0-9_-]{24,}',raw),'secret-like value; do not print'
 if '/evidence/live/' in path and path.endswith('.json'):assert not re.search(rb'0x[0-9a-fA-F]{12,16}',raw),'runtime address-like token in '+path
spec=Path(a.pathspec);spec.write_bytes(b'\0'.join(x.encode() for x in paths)+b'\0')
if a.stage:subprocess.run(['git','add','--pathspec-from-file='+str(spec),'--pathspec-file-nul'],cwd=repo,check=True,capture_output=True)
print(json.dumps({'scope_verified':True,'delta_paths':len(paths),'bytes':sum((repo/x).stat().st_size for x in paths),'secret_pattern_matches':0,'runtime_address_like_tokens':0,'staged':a.stage}))

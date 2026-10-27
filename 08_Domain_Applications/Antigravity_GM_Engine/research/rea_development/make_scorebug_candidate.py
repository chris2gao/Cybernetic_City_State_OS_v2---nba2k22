"""One-member resource experiment outside game directories; never deploys."""
import argparse,hashlib,json,re,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
source=Path('E:/Games/NBA 2K22/Mods/newscorebug.iff');candidate=out/'rea-scorebug-preview.iff'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='494ed356b69219ab43bfb69fd4b1d61dc30c24e990ba7ba71a100bbd6d4eb852'
if candidate.exists():raise RuntimeError('preserve candidate; choose fresh output')
target='scorebug_intro.SCNE'
with zipfile.ZipFile(source) as original,zipfile.ZipFile(candidate,'w') as edited:
 for info in original.infolist():
  raw=original.read(info)
  if info.filename==target:
   raw,count=re.subn(rb'("VC_MinTextScale"\s*:\s*)0\.75',rb'\g<1>0.70',raw,count=1)
   assert count==1
  edited.writestr(info,raw)
with zipfile.ZipFile(source) as original,zipfile.ZipFile(candidate) as edited:
 assert original.namelist()==edited.namelist()
 changed=[n for n in original.namelist() if hashlib.sha256(original.read(n)).digest()!=hashlib.sha256(edited.read(n)).digest()]
 assert changed==[target]
result={'original_path':str(source),'candidate_path':str(candidate),'original_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'changed_members':changed,'change':'first VC_MinTextScale 0.75 -> 0.70 in scorebug_intro.SCNE','game_deployment':False,'game_rendering_verified':False,'limitations':['resource-layout experiment only; not a text data injection test','repacking success does not prove game loading or rendering compatibility']}
(out/'scorebug-candidate.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))

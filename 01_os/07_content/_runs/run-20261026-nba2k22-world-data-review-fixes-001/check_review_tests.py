import json,subprocess,sys
from pathlib import Path
run=Path(__file__).resolve().parent;out=run/'evidence';out.mkdir(exist_ok=True)
command=[sys.executable,'-X','utf8','-m','unittest','discover','-s','08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests','-p','test_review_*.py']
with (out/'review-tests.stdout.log').open('w',encoding='utf-8') as stdout,(out/'review-tests.stderr.log').open('w',encoding='utf-8') as stderr:r=subprocess.run(command,stdout=stdout,stderr=stderr)
text=(out/'review-tests.stderr.log').read_text(encoding='utf-8');(out/'review-tests.json').write_text(json.dumps({'command':command,'exit_code':r.returncode,'scope':'F-02/F-03 controlled fixtures at this iteration; F-01 still in progress'},indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'exit_code':r.returncode,'tail':text[-1200:]}));sys.exit(r.returncode)

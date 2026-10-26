import json,shutil,subprocess,sys,time
from pathlib import Path
run=Path(__file__).resolve().parent;out=run/'evidence';out.mkdir(exist_ok=True)
if (out/'regression.json').exists():
    index=1
    while (out/('regression-attempt-'+str(index))).exists():index+=1
    saved=out/('regression-attempt-'+str(index));saved.mkdir()
    for name in ('regression.json','tests.stdout.log','tests.stderr.log','smoke.stdout.log','smoke.stderr.log'):
        if (out/name).exists():shutil.copyfile(out/name,saved/name)
checks={'tests':[sys.executable,'-X','utf8','-m','unittest','discover','-s','08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests','-p','test_*.py'],'smoke':[sys.executable,'-X','utf8','08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py','smoke']};report={}
for name,command in checks.items():
    start=time.monotonic()
    with (out/(name+'.stdout.log')).open('w',encoding='utf-8') as stdout,(out/(name+'.stderr.log')).open('w',encoding='utf-8') as stderr:r=subprocess.run(command,stdout=stdout,stderr=stderr)
    report[name]={'command':command,'exit_code':r.returncode,'seconds':round(time.monotonic()-start,2)};(out/'regression.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'check':name,**report[name]}),flush=True)
    if r.returncode:print((out/(name+'.stderr.log')).read_text(encoding='utf-8')[-1800:]);sys.exit(r.returncode)

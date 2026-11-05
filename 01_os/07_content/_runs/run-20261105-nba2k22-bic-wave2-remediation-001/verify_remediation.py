"""Wave2 remediation regression and historical evidence reproduction."""
import argparse,hashlib,json,subprocess,sys,time,types
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
D=Path('08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype')
parser=argparse.ArgumentParser();parser.add_argument('--historical-database',type=Path);args=parser.parse_args()
raw=OUT/'_runtime';raw.mkdir(exist_ok=True)
names=['test_bic_baseline.py','test_bic_experiments.py','test_observation_scope.py','test_player_details.py','test_bic_remediation.py','test_bic_wave2.py','test_bic_wave2_remediation.py']
cmd=[sys.executable,'-B','-m','pytest',*[str(D/'tests'/name) for name in names],'-q','-W','always']
start=time.perf_counter()
with (raw/'tests.stdout.log').open('wb') as out,(raw/'tests.stderr.log').open('wb') as err:
    result=subprocess.run(cmd,cwd=ROOT,stdout=out,stderr=err)
seconds=time.perf_counter()-start
for name in ('tests.stdout.log','tests.stderr.log'):
    (OUT/name).write_bytes((raw/name).read_bytes().replace(str(Path(sys.prefix)).encode(),b'<python-runtime>'))
sys.path.insert(0,str(ROOT/D));sys.path.insert(0,str(ROOT/D/'tests'))
from bic_baseline import player_baseline,team_baseline
from bic_diagnostics import diagnose_and_plan
from bic_plans import native_capabilities
from test_observation_scope import ObservationScopeTests,T1
catalog=native_capabilities(ROOT)
old=types.ModuleType('reviewed_wave2')
oldcode=subprocess.check_output(['git','show','b308660b:'+str(D/'bic_diagnostics.py').replace('\\','/')],cwd=ROOT)
exec(compile(oldcode,'<reviewed-wave2>','exec'),old.__dict__)
fixture=ObservationScopeTests();fixture.setUp()
try:
    baseline=player_baseline(fixture.db,'p1',save_id='save',season_id='s1',as_of=T1)
    timings={}
    for label,fn in [('reviewed',old.diagnose_player),('remediated',diagnose_and_plan)]:
        start=time.perf_counter()
        for _ in range(5):
            fn(baseline,catalog=catalog)
        timings[label]={'iterations':5,'seconds':time.perf_counter()-start}
finally:fixture.doCleanups()
cases=[]
dataset=None
if args.historical_database:
    db=args.historical_database
    def digest(path):
        h=hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
        return h.hexdigest()
    dataset={'name':db.name,'bytes':db.stat().st_size,'before':digest(db)}
    for pid in ('player:native:7236','player:native:4170'):
        baseline=player_baseline(db,pid,save_id='nba2k22_test_01',season_id='season:native-year:2022',as_of='2026-10-27T00:00:00Z',max_age_seconds=7*86400)
        diagnosis=diagnose_and_plan(baseline,catalog=catalog)
        cases.append({'player':baseline['facts'].get('player'),'data_status':baseline['data_status'],'binding':baseline['binding'],'observation_scope':baseline['observation_scope'],'findings':diagnosis['findings'],'play_type_fit':diagnosis['play_type_fit'],'verified_mechanisms':diagnosis['verified_mechanisms']})
    dataset['after']=digest(db);assert dataset['before']==dataset['after']
(OUT/'historical_cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
(OUT/'performance.json').write_text(json.dumps({'timings':timings,'scope':'Five warm synthetic diagnosis calls after baseline/catalog loading; small-fixture only'},indent=2)+'\n',encoding='utf-8',newline='\n')
receipt={'checked_at':datetime.now(timezone.utc).isoformat(),'base_commit':'b308660b3112738a4df52e412448d821c3d4b932','command':['python']+cmd[1:],'exit_code':result.returncode,'seconds':seconds,'dataset':dataset,'historical_cases':len(cases),'raw_stdout_sha256':hashlib.sha256((raw/'tests.stdout.log').read_bytes()).hexdigest(),'public_stdout_sha256':hashlib.sha256((OUT/'tests.stdout.log').read_bytes()).hexdigest(),'redaction':'Only Python installation prefix; original logs remain in ignored _runtime','formal_os_pass':False}
(OUT/'verification_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'exit_code':result.returncode,'historical_cases':len(cases),'seconds':seconds}))
sys.exit(result.returncode)

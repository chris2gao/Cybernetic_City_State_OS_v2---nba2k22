"""Run Wave2 offline checks and optional historical case diagnostics."""
import argparse,hashlib,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
D=Path("08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype")
parser=argparse.ArgumentParser();parser.add_argument('--historical-database',type=Path);args=parser.parse_args()
raw=OUT/'_runtime';raw.mkdir(exist_ok=True)
tests=['test_bic_baseline.py','test_bic_experiments.py','test_observation_scope.py','test_player_details.py','test_bic_remediation.py','test_bic_wave2.py']
cmd=[sys.executable,'-B','-m','pytest',*[str(D/'tests'/name) for name in tests],'-q','-W','always']
start=time.perf_counter()
with (raw/'tests.stdout.log').open('wb') as out,(raw/'tests.stderr.log').open('wb') as err:
    completed=subprocess.run(cmd,cwd=ROOT,stdout=out,stderr=err)
seconds=time.perf_counter()-start
for name in ('tests.stdout.log','tests.stderr.log'):
    (OUT/name).write_bytes((raw/name).read_bytes().replace(str(Path(sys.prefix)).encode(),b'<python-runtime>'))
sys.path.insert(0,str(ROOT/D))
from bic_baseline import player_baseline,team_baseline
from bic_diagnostics import diagnose_and_plan,diagnose_team,synthetic_validation
from bic_plans import native_capabilities
from engine import connect
from contextlib import closing
catalog=native_capabilities(ROOT)
cases=[]
dataset=None
if args.historical_database:
    db=args.historical_database
    def fingerprint(path):
        digest=hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(4*1024*1024),b''):digest.update(block)
        return digest.hexdigest()
    dataset={'name':db.name,'bytes':db.stat().st_size,'sha256_before':fingerprint(db)}
    for pid,label,focus in [('player:native:7236','Pascal Siakam','Inside/midrange role'),('player:native:4170','Nikola Jokic','Inside finishing and passing role')]:
        scope=dict(save_id='nba2k22_test_01',season_id='season:native-year:2022',as_of='2026-10-27T00:00:00Z',max_age_seconds=7*86400)
        player=player_baseline(db,pid,**scope)
        fields=['player_vitals_observations.height_raw','player_attribute_snapshots.shot_close_raw','player_attribute_snapshots.mid_range_shot_raw','player_attribute_snapshots.passing_iq_raw','player_attribute_snapshots.interior_defense_raw','player_tendency_snapshots.shot_mid_range_tendency_raw']
        requirements=[{'field':field,'source':'Human Wave2 historical case research focus; observation inspection, no threshold','rationale':focus+' / '+field} for field in fields]
        intent={'kind':'OFFENSE_FOCUS','parameters':{},'rationale':'Candidate review of offense context; target/before not inferred'}
        start=time.perf_counter()
        diagnosis=diagnose_and_plan(player,catalog=catalog,role_requirements=requirements,intents=[intent])
        player_time=time.perf_counter()-start
        full=raw/(pid.split(':')[-1]+'-diagnosis.json');full.write_text(json.dumps(diagnosis,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
        teamcase=None
        if player['native_identity_history']:
            native_team=player['native_identity_history'][-1]['native_team_id']
            with closing(connect(db,True)) as c:
                teamrow=c.execute('SELECT team_id FROM teams WHERE native_team_id=?',(str(native_team),)).fetchone()
            if teamrow:
                team=team_baseline(db,teamrow['team_id'],**scope)
                start=time.perf_counter()
                td=diagnose_team(team,[player],roles={pid:requirements})
                teamcase={'team_id':teamrow['team_id'],'team_name':team['facts'].get('team',{}).get('display_name'),'fixed_roster':td['fixed_roster'],'roster_membership_status':td['players'][0]['roster_membership_status'],'complementarity':td['complementarity'],'defense_matchups':td['defense_matchups'],'elapsed_seconds':time.perf_counter()-start}
        badge=diagnosis['badge_facts']
        cases.append({'player_id':pid,'player_name':label,'source_data_status':player['data_status'],'binding':player['binding'],'findings':diagnosis['findings'],'relative_basketball_profile':diagnosis['relative_basketball_profile'],'coverage':diagnosis['coverage'],'badge_summary':{'status':badge['status'],'count':len(badge['badges']),'examples':badge['badges'][:2],'limits':badge['limits']},'play_type_observation_count':len(diagnosis['observed_play_types']),'season_observation_count':len(diagnosis['game_observations']),'native_plans':diagnosis['native_plans'],'controlled_validation_requirements':diagnosis['experiment_requirements'],'diagnosis_elapsed_seconds':player_time,'team':teamcase,'full_local_output_sha256':hashlib.sha256(full.read_bytes()).hexdigest()})
    dataset['sha256_after']=fingerprint(db)
    assert dataset['sha256_before']==dataset['sha256_after']
(OUT/'historical_cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
sample=synthetic_validation({'00':[10],'10':[14],'01':[12],'11':[22]})
(OUT/'synthetic_validation.json').write_text(json.dumps(sample,indent=2)+'\n',encoding='utf-8',newline='\n')
receipt={'checked_at':datetime.now(timezone.utc).isoformat(),'command':['python']+cmd[1:],'exit_code':completed.returncode,'elapsed_seconds':seconds,'historical_cases':len(cases),'dataset':dataset,'catalog_source':catalog['source'],'catalog_build':catalog['game_build_sha256'],'raw_stdout_sha256':hashlib.sha256((raw/'tests.stdout.log').read_bytes()).hexdigest(),'public_stdout_sha256':hashlib.sha256((OUT/'tests.stdout.log').read_bytes()).hexdigest(),'log_redaction':'Only Python installation prefix; original local _runtime bytes retained','live_operations':0,'formal_os_pass':False}
(OUT/'verification_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'exit_code':completed.returncode,'historical_cases':len(cases),'test_seconds':seconds}))
sys.exit(completed.returncode)

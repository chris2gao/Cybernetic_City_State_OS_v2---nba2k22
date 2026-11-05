"""Execute only the BIC offline checks and preserve raw subprocess receipts."""
import argparse,hashlib,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
D=ROOT/"08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype"
checks=[]
command=[sys.executable,"-B","-m","pytest",*[str((D/('tests/'+name)).relative_to(ROOT)) for name in ('test_bic_baseline.py','test_bic_experiments.py','test_observation_scope.py','test_player_details.py')],"-q","--disable-warnings"]
start=time.perf_counter()
with (OUT/"offline_tests.stdout.log").open("wb") as out,(OUT/"offline_tests.stderr.log").open("wb") as err:
    result=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err)
checks.append({"command":command[2:],"exit_code":result.returncode,"elapsed_seconds":time.perf_counter()-start,"stdout":"offline_tests.stdout.log","stderr":"offline_tests.stderr.log"})
sys.path.insert(0,str(D))
from bic_baseline import player_baseline,team_baseline,coverage_report,badge_intelligence
from engine import connect
from contextlib import closing
parser=argparse.ArgumentParser()
parser.add_argument('--historical-database',type=Path)
args=parser.parse_args()
DB=args.historical_database
examples=[]
if DB is not None and DB.exists():
    for player in ("player:native:4170","player:native:7236"):
        start=time.perf_counter()
        baseline=player_baseline(DB,player,save_id="nba2k22_test_01",season_id="season:native-year:2022",as_of="2026-10-27T00:00:00Z")
        player_seconds=time.perf_counter()-start
        team_id=None
        if baseline['native_identity_history']:
            native_team=baseline['native_identity_history'][-1]['native_team_id']
            with closing(connect(DB,True)) as conn:
                row=conn.execute('SELECT team_id FROM teams WHERE native_team_id=?',(str(native_team),)).fetchone()
                team_id=row['team_id'] if row else None
        team=None
        if team_id:
            start=time.perf_counter()
            team=team_baseline(DB,team_id,save_id='nba2k22_test_01',season_id='season:native-year:2022',as_of='2026-10-27T00:00:00Z')
            team={'identity':team['facts'].get('team'),'coverage':coverage_report(team),'elapsed_seconds':time.perf_counter()-start}
        examples.append({"player":baseline["facts"].get("player"),"binding":baseline["binding"],"coverage":coverage_report(baseline),"badge_examples":badge_intelligence(baseline)["badges"][:2],"native_identity_observations":len(baseline["native_identity_history"]),"elapsed_seconds":player_seconds,"team":team,"evidence_status":"HISTORICAL_READONLY_DATA_WITH_BINDING_GAPS"})
(OUT/"historical_examples.json").write_text(json.dumps(examples,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
report={"checked_at":datetime.now(timezone.utc).isoformat(),"checks":checks,"historical_examples":len(examples),"formal_os_acceptance":"NOT_CLAIMED","live_game_operations":0,"files":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("*.log")}}
(OUT/"verification_receipt.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"test_exit_code":result.returncode,"historical_examples":len(examples)}))
sys.exit(result.returncode)

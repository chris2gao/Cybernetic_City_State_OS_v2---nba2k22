import json,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from league_ingest import capture_league
from live_world import _json
run=Path(__file__).resolve().parent;out=run/'league-live-v12';out.mkdir(exist_ok=False);save=run/'world-saves/nba2k22_test_01'
pid=int(sys.argv[1]);results={}
try:
    results['history']=capture_league(pid,save,'MyLEAGUE0003',out/'history-first',mode='HISTORY_AWARDS')
    results['history_repeat']=capture_league(pid,save,'MyLEAGUE0003',out/'history-repeat',mode='HISTORY_AWARDS')
    if results['history']['status']!='ingested' or results['history_repeat']['status']!='already_refreshed':raise RuntimeError('annual history first/repeat failed')
    results['news']=capture_league(pid,save,'MyLEAGUE0003',out/'news-first',mode='NEWS_TRANSACTIONS')
    if results['news']['status']!='ingested':raise RuntimeError('news ingestion failed')
    report={'status':'LEAGUE_HISTORY_AWARDS_AND_ORDINARY_EVENTS_CAPTURED','pid':pid,'results':results,'game_writes':False}
except Exception as error:
    report={'status':'LEAGUE_CAPTURE_FAILED','error_type':type(error).__name__,'reason':str(error),'completed':results,'game_writes':False}
_json(out/'league-report.json',report)

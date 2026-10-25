"""Human-authorized elevated read-only annual first capture and repeated skip."""
import hashlib,json,sys
from pathlib import Path

repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
sys.path.insert(0,str(app))
from records_reader import capture_records
from award_reader import capture_native_honors
from live_world import _json
from engine import connect

run=Path(__file__).resolve().parent;save=run/'world-saves/nba2k22_test_01'
out=run/'annual-live-v11';out.mkdir(exist_ok=False)
pid=int(sys.argv[1]);results={}
try:
    for family,method in (('records',capture_records),('honors',capture_native_honors)):
        first=method(pid,save,'MyLEAGUE0003',out/(family+'-first'))
        if first['status']!='ingested':raise RuntimeError('first annual capture not ingested')
        again=method(pid,save,'MyLEAGUE0003',out/(family+'-repeat'))
        if again['status']!='already_refreshed' or again['previous_unit_id']!=first['unit_id']:raise RuntimeError('annual repeat did not skip')
        if any(not r['label'].startswith('CADENCE_') for r in again['read_trace'] if r['operation']=='ReadProcessMemory'):raise RuntimeError('full annual source unexpectedly acquired on repeat')
        results[family]={'first':first,'repeat':again}
    report={'status':'ANNUAL_FIRST_CAPTURE_AND_REPEAT_SKIP_VERIFIED','pid':pid,'results':results,
        'game_writes':False,'full_goal_complete':False}
except Exception as error:
    report={'status':'ANNUAL_CAPTURE_FAILED','error_type':type(error).__name__,'reason':str(error),'completed':results,'game_writes':False}
_json(out/'annual-report.json',report)

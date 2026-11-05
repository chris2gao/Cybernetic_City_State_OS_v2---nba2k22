import sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from player_detail_reader import capture_player_details
from live_world import _json
run=Path(__file__).resolve().parent;out=run/'player-details-live-v13'
try:
    result=capture_player_details(int(sys.argv[1]),run/'world-saves/nba2k22_test_01','MyLEAGUE0003',out)
    report={'status':'NATIVE_PLAYER_DETAILS_INGESTED','result':result,'game_writes':False}
except Exception as error:report={'status':'NATIVE_PLAYER_DETAILS_FAILED','error_type':type(error).__name__,'reason':str(error),'game_writes':False}
_json(run/'player-details-worker-report-v13.json',report)

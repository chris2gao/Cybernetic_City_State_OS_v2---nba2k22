import sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from player_skill_reader import capture_player_skills
from live_world import _json
run=Path(__file__).resolve().parent
try:report={'status':'NATIVE_PLAYER_SKILL_INGESTED','result':capture_player_skills(int(sys.argv[1]),run/'world-saves/nba2k22_test_01','MyLEAGUE0003',run/'player-skill-live-v16'),'game_writes':False}
except Exception as error:report={'status':'NATIVE_PLAYER_SKILL_FAILED','error_type':type(error).__name__,'reason':str(error),'game_writes':False}
_json(run/'player-skill-worker-report-v16.json',report)

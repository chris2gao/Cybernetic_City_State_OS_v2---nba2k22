"""Two explicit existing source families, fresh process, immutable prior facts."""
import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from database_operations import file_sha256
from live_world import read_binding,bound_database,_json
from refresh import refresh_world
save=runtime/'world-saves/nba2k22_test_01';binding,binding_hash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
expected='0780e661605c98d280348b2436d1cf49190effa537c675ddbde0e5b64c053082'
if file_sha256(db)!=expected:raise RuntimeError('before-image differs from the retained increment23 database')
report={'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip(),'game_pid':int(sys.argv[1]),'before_database_sha256':expected,'before_binding_sha256':binding_hash,'game_writes':False,'full_goal_complete':False}
_json(runtime/'auxiliary-refresh-before.json',report)
try:
    report['refresh']=refresh_world(int(sys.argv[1]),save,'MyLEAGUE0003',runtime/'organization-header-refresh-live-01',families=['schedule','organization'])
    report['status']='REQUESTED_SCHEDULE_AND_ORGANIZATION_REFRESH_FINISHED'
except Exception as error:report.update({'status':'REQUESTED_REFRESH_FAILED','error_type':type(error).__name__,'reason':str(error)})
after,after_hash=read_binding(save,'MyLEAGUE0003');report.update({'after_database_sha256':file_sha256(bound_database(save,after)),'binding_sha256_unchanged':binding_hash==after_hash,'before_image_sha256_unchanged':file_sha256(runtime/'increment24-baseline.sqlite')==expected});_json(runtime/'auxiliary-refresh-worker-report.json',report)

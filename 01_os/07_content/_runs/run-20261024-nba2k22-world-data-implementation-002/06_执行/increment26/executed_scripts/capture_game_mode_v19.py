"""Copy-upgrade facts and acquire one explicit game-mode refresh source."""
import json,struct,subprocess,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from live_world import _json,read_binding,bound_database,upgrade_bound_save
from database_operations import file_sha256
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from refresh import refresh_world
pid=int(sys.argv[1]);save=runtime/'world-saves/nba2k22_test_01';binding,binding_hash=read_binding(save,'MyLEAGUE0003');old=bound_database(save,binding)
if file_sha256(old)!='46eec932562bb5b722c490bb71011b4d21db87a4f86d1be742ba5435ea87514d':raise RuntimeError('before migration facts differ from retained increment24/25 baseline')
report={'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip(),'game_pid':pid,'before_database_sha256':file_sha256(old),'before_binding_sha256':binding_hash,'game_writes':False,'getter_invocations':0,'full_goal_complete':False}
_json(runtime/'game-mode-v19-before.json',report)
try:
    report['migration']=upgrade_bound_save(save,'MyLEAGUE0003');reader=ReadOnlyGameProcess(pid)
    try:
        root=int.from_bytes(reader.read(reader.module_base+ROSTER_RVA,8,'MODE_AUDIT_ROSTER_ROOT'),'little');count,address=struct.unpack('<QQ',reader.read(root+16,16,'MODE_AUDIT_PLAYER_INTERVAL_DESCRIPTOR'));report['player_interval']={'address':address,'count':count,'stride':1264}
    finally:reader.close()
    report['interval_read_trace']=reader.trace
    report['refresh']=refresh_world(pid,save,'MyLEAGUE0003',runtime/'game-mode-v19-live',families=['game-mode']);report['status']='NATIVE_GAME_MODE_V19_COPY_UPGRADE_AND_CAPTURE_FINISHED'
except Exception as error:report.update({'status':'GAME_MODE_V19_UPGRADE_OR_CAPTURE_FAILED','error_type':type(error).__name__,'reason':str(error)})
current,_=read_binding(save,'MyLEAGUE0003');report.update({'after_database_sha256':file_sha256(bound_database(save,current)),'old_database_sha256_unchanged':file_sha256(old)==report['before_database_sha256']});_json(runtime/'game-mode-v19-worker-report.json',report)

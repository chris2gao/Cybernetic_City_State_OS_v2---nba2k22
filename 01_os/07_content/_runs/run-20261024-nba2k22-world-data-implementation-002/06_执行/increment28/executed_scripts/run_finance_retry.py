import json,subprocess,sys,traceback
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;dest=runtime.parent/'06_执行/increment28';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from live_world import read_binding,bound_database,_json
from database_operations import file_sha256
from refresh import refresh_world
from engine import connect
save=runtime/'world-saves/nba2k22_test_01';report={'pid':int(sys.argv[1]),'game_writes':False,'full_goal_complete':False}
try:
    head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip();report['candidate_code_head']=head
    before=json.loads((dest/'before.json').read_bytes());binding,_=read_binding(save,'MyLEAGUE0003');database=bound_database(save,binding);old=save/'world-v19.sqlite'
    assert database.name=='world-v20.sqlite' and file_sha256(old)==before['database_sha256']
    assert {k:v for k,v in binding.items() if k!='database_file'}=={k:v for k,v in before['binding'].items() if k!='database_file'}
    with connect(database,True) as c:assert c.execute('SELECT count(*) FROM native_team_finance_observations').fetchone()[0]==0 and c.execute('PRAGMA user_version').fetchone()[0]==20
    report['before_finance_database_sha256']=file_sha256(database);report['upgrade']=json.loads((dest/'worker-result.json').read_bytes())['upgrade'];report['copy_upgrade_executed_in_prior_attempt']=True
    batch=refresh_world(int(sys.argv[1]),save,'MyLEAGUE0003',runtime/'finance-refresh-02',families=['finance']);report.update(status='FINANCE_UPGRADE_AND_CAPTURE_SUCCEEDED',batch_id=batch['batch_id'],unit_id=batch['sources'][0]['unit']['unit_id'],after_database_sha256=file_sha256(database),old_database_sha256=file_sha256(old))
except Exception as error:
    report.update(status='FINANCE_RETRY_WORKER_FAILED',error_type=type(error).__name__,reason=str(error));(dest/'retry-worker-traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
_json(dest/'retry-worker-result.json',report)

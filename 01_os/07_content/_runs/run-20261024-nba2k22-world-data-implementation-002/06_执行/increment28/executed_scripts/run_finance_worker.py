import json,subprocess,sys,traceback
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;dest=runtime.parent/'06_执行/increment28';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from live_world import read_binding,bound_database,upgrade_bound_save,_json
from database_operations import file_sha256
from refresh import refresh_world
save=runtime/'world-saves/nba2k22_test_01';report={'pid':int(sys.argv[1]),'game_writes':False,'full_goal_complete':False}
try:
    head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip();report['candidate_code_head']=head
    binding,binding_hash=read_binding(save,'MyLEAGUE0003');old=bound_database(save,binding);digest=file_sha256(old)
    assert digest=='9153a9a517372006168e5f1c32d29aed3580e1b3da84dc7105ad010e9b2809d7' and old.name=='world-v19.sqlite'
    _json(dest/'before.json',{'binding':binding,'binding_sha256':binding_hash,'database_sha256':digest,'candidate_code_head':head,'baseline_snapshot_manifest':'../increment27/world-v19.snapshot.json','game_writes':False})
    report['upgrade']=upgrade_bound_save(save,'MyLEAGUE0003');assert file_sha256(old)==digest
    new_binding,_=read_binding(save,'MyLEAGUE0003');assert {k:v for k,v in binding.items() if k!='database_file'}=={k:v for k,v in new_binding.items() if k!='database_file'}
    batch=refresh_world(int(sys.argv[1]),save,'MyLEAGUE0003',runtime/'finance-refresh-01',families=['finance']);report.update(status='FINANCE_UPGRADE_AND_CAPTURE_SUCCEEDED',batch_id=batch['batch_id'],unit_id=batch['sources'][0]['unit']['unit_id'],after_database_sha256=file_sha256(bound_database(save,new_binding)),old_database_sha256=file_sha256(old))
except Exception as error:
    report.update(status='FINANCE_WORKER_FAILED',error_type=type(error).__name__,reason=str(error));(dest/'worker-traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
_json(dest/'worker-result.json',report)

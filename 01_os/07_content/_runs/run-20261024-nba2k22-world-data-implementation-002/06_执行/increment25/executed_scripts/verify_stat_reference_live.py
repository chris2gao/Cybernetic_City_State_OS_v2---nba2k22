"""Current code/metadata verification only; no annual data acquisition or writes."""
from datetime import datetime,timezone
import json,struct,subprocess,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;dest=runtime.parent/'06_执行/increment25';sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from stat_reference import verify_native_reference_contract
from refresh import _context
from live_world import read_binding,bound_database,_json
from database_operations import file_sha256
save=runtime/'world-saves/nba2k22_test_01';binding,binding_hash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);before=file_sha256(db);pid=int(sys.argv[1]);reader=None
report={'observed_at':datetime.now(timezone.utc).isoformat(),'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip(),'game_pid':pid,'before_database_sha256':before,'binding_sha256':binding_hash,'game_writes':False,'annual_data_refreshed':False,'getter_invocations':0,'full_goal_complete':False}
try:
    report['context_before']=_context(pid);reader=ReadOnlyGameProcess(pid);root=int.from_bytes(reader.read(reader.module_base+ROSTER_RVA,8,'STAT_CONTRACT_PLAYER_ROOT'),'little');count,address=struct.unpack('<QQ',reader.read(root+16,16,'STAT_CONTRACT_SLOT1_DESCRIPTOR'));report['player_interval']={'address':address,'count':count,'stride':1264}
    report['contract']=verify_native_reference_contract(reader);reader.close();report['context_after']=_context(pid)
    if report['context_before']['epoch']!=report['context_after']['epoch']:raise RuntimeError('process/build/year changed across code verification')
    report['status']='CURRENT_NATIVE_STAT_REFERENCE_CODE_AND_METADATA_VERIFIED'
except Exception as error:report.update(status='STAT_REFERENCE_CODE_VERIFICATION_FAILED',error_type=type(error).__name__,reason=str(error))
finally:
    if reader:reader.close()
report['read_trace']=reader.trace if reader else [];report['after_database_sha256']=file_sha256(db);_,after_binding=read_binding(save,'MyLEAGUE0003');report['binding_unchanged']=after_binding==binding_hash;_json(dest/'native-contract-report.json',report)

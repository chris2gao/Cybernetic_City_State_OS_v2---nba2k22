import json,sys
from pathlib import Path
r=Path(__file__).parent;sys.path.insert(0,str(Path.cwd()/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from process_session import resolve_pid
from live_reader import ReadOnlyGameProcess
from league_reader import read_native_enum
from live_world import _json
from refresh import _context
out=r/'staff-slot-enum-32';out.mkdir(exist_ok=False);entry=next(e for e in json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates'] if e['name']=='ROSTERDATA_COLDEF');pid=resolve_pid();before=_context(pid);reader=ReadOnlyGameProcess(pid)
try:value=read_native_enum(reader,entry);_json(out/'enum.json',value);_json(out/'type_entry.json',entry)
finally:reader.close()
after=_context(pid);assert before['epoch']==after['epoch'];_json(out/'report.json',{'status':'ROSTER_COLDEF_ENUM_CAPTURED','epoch':before['epoch'],'read_trace':reader.trace,'game_writes':False,'staff_values_read':0,'player_values_read':0})

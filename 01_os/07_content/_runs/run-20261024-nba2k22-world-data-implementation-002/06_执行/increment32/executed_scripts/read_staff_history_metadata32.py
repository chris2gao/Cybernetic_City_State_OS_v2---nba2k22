import json,sys,traceback
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from live_reader import ReadOnlyGameProcess
from process_session import resolve_pid
from award_reader import read_native_fields
from refresh import _context
from live_world import _json
out=r/'staff-history-metadata-32';out.mkdir(exist_ok=False);reader=None;report={'game_writes':False,'staff_values_read':0,'player_values_read':0}
try:
    pid=resolve_pid();before=_context(pid);reader=ReadOnlyGameProcess(pid);mapping=json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];entries=[next(e for e in mapping if e['name']==name) for name in ('COACHSTATDATA','COACHSTATMANAGERDATA','COACHDATA')];values=[]
    for entry in entries:
        value=read_native_fields(reader,entry,read_enums=False)
        for f in value['fields']:
            pointer=f['words'][6]|f['words'][7]<<32
            if f['words'][5]>>16==1 and pointer>=0x10000:
                raw=reader.read(pointer,24,'STAFF_HISTORY_ARRAY_DIMENSION');f['array_dimension_hex']=raw.hex();assert reader.read(pointer,24,'STAFF_HISTORY_ARRAY_DIMENSION_RECHECK')==raw
        values.append(value)
    reader.close();after=_context(pid);assert before['epoch']==after['epoch'] and before['game_progress']==after['game_progress'];_json(out/'metadata.json',values);_json(out/'type_entries.json',entries);report.update(status='CURRENT_NATIVE_STAFF_HISTORY_TYPES_VERIFIED',before=before,after=after,read_trace=reader.trace)
except Exception as e:report.update(status='STAFF_HISTORY_METADATA_FAILED',error_type=type(e).__name__,reason=str(e));(out/'traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
finally:
    if reader:reader.close()
_json(out/'report.json',report)

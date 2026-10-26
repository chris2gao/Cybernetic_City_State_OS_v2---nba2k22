import json,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from league_reader import read_native_enum
from live_reader import ReadOnlyGameProcess
from live_world import _json
from refresh import _context
metadata=json.loads((runtime/'staff-metadata-30-labeled.json').read_bytes());mapping=json.loads((runtime/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];referenced={f['enum_pointer']-0x140000000 for f in metadata['fields'] if f['enum_pointer']};entries=[e for e in mapping if e['type_rva'] in referenced and e['constructor_rva']==0x1e53e90];out=runtime/'staff-enums-30';out.mkdir(exist_ok=False);reader=None;report={'pid':int(sys.argv[1]),'game_writes':False,'player_value_reads':0,'staff_value_reads':0}
try:
    before=_context(int(sys.argv[1]));reader=ReadOnlyGameProcess(int(sys.argv[1]));values=[read_native_enum(reader,e) for e in entries];reader.close();after=_context(int(sys.argv[1]));assert before['epoch']==after['epoch'];_json(out/'metadata.json',values);_json(out/'type_entries.json',entries);report.update(status='CURRENT_STAFF_REFERENCED_NATIVE_ENUMS_CAPTURED',enum_count=len(values),context_before=before,context_after=after,read_trace=reader.trace)
except Exception as error:report.update(status='STAFF_ENUM_PROBE_FAILED',reason=str(error),error_type=type(error).__name__,read_trace=reader.trace if reader else getattr(error,'read_trace',[]))
finally:
    if reader:reader.close()
_json(out/'report.json',report)

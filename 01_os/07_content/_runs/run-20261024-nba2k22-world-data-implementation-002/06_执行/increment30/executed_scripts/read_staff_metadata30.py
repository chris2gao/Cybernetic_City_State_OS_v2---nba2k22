import hashlib,json,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from award_reader import read_native_fields
from live_reader import ReadOnlyGameProcess
from live_world import _json
from refresh import _context
mapping=json.loads((runtime/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];entry=next(e for e in mapping if e['name']=='COACHDATA');out=runtime/'staff-metadata-30';out.mkdir(exist_ok=False);reader=None;report={'pid':int(sys.argv[1]),'game_writes':False,'player_value_reads':0,'staff_value_reads':0}
try:
    before=_context(int(sys.argv[1]));reader=ReadOnlyGameProcess(int(sys.argv[1]));value=read_native_fields(reader,entry,352,read_enums=False);reader.close();after=_context(int(sys.argv[1]));assert before['epoch']==after['epoch'];_json(out/'metadata.json',value);_json(out/'type_entry.json',entry);report.update(status='CURRENT_NATIVE_COACHDATA_METADATA_CAPTURED',context_before=before,context_after=after,read_trace=reader.trace)
except Exception as error:report.update(status='STAFF_METADATA_PROBE_FAILED',reason=str(error),error_type=type(error).__name__,read_trace=reader.trace if reader else getattr(error,'read_trace',[]))
finally:
    if reader:reader.close()
_json(out/'report.json',report)

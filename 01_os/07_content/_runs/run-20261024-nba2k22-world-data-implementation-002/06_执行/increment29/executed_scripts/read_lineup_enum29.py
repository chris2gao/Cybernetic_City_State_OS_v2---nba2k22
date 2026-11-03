import json,sys,zlib
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from league_reader import read_native_enum
from live_reader import ReadOnlyGameProcess
from live_world import _json
metadata=json.loads((runtime/'lineup-metadata-29/metadata.json').read_bytes());field=next(f for f in metadata[1]['fields'] if f['name_crc']==zlib.crc32(b'ForceNonStarter'));mapping=json.loads((runtime/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];entry=next(e for e in mapping if e['type_rva']==field['enum_pointer']-0x140000000);out=runtime/'lineup-enum-29';out.mkdir(exist_ok=False);reader=None;report={'pid':int(sys.argv[1]),'game_writes':False,'player_value_reads':0}
try:
    reader=ReadOnlyGameProcess(int(sys.argv[1]));value=read_native_enum(reader,entry);reader.close();_json(out/'metadata.json',value);_json(out/'type_entry.json',entry);report.update(status='CURRENT_LINEUP_PLAYER_FORCE_NON_STARTER_ENUM_CAPTURED',read_trace=reader.trace)
except Exception as error:report.update(status='LINEUP_ENUM_PROBE_FAILED',reason=str(error),error_type=type(error).__name__)
finally:
    if reader:reader.close()
_json(out/'report.json',report)

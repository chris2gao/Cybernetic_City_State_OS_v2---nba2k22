import json,struct,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from finance_reader import PROFILE
from award_reader import read_native_fields
from live_reader import ReadOnlyGameProcess
from live_world import _json
out=runtime/'finance-dimensions-01';out.mkdir(exist_ok=False);reader=None;report={'pid':int(sys.argv[1]),'game_writes':False,'player_value_reads':0}
try:
    reader=ReadOnlyGameProcess(int(sys.argv[1]));entry=PROFILE['types'][0];metadata=read_native_fields(reader,entry,4696,read_enums=False);fields={f['name_crc']:f for f in metadata['fields']};dims={}
    for name,spec in PROFILE['identity'].items():
        if 'extent' not in spec:continue
        f=fields[spec['binding']['name_crc']];w=f['words'];ptr=w[6]|w[7]<<32;raw=reader.read(ptr,24,'FINANCE_DIAG_NAME_DIMENSION:'+name);again=reader.read(ptr,24,'FINANCE_DIAG_NAME_DIMENSION_RECHECK:'+name);assert raw==again
        dims[name]={'words':w,'runtime_control_hex':raw.hex(),'static_control_hex':spec['dimension_control_hex'],'extent_u32':struct.unpack_from('<I',raw)[0]}
    report.update(status='CURRENT_FINANCE_NAME_DIMENSIONS_CAPTURED',dimensions=dims,read_trace=reader.trace)
except Exception as error:report.update(status='FINANCE_DIMENSION_PROBE_FAILED',reason=str(error),error_type=type(error).__name__)
finally:
    if reader:reader.close()
_json(out/'report.json',report)

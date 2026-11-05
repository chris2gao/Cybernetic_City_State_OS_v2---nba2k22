import json,sys
from pathlib import Path
repo=Path.cwd();r=Path(__file__).resolve().parent;sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from league_reader import read_native_enum
from live_reader import ReadOnlyGameProcess
from live_world import _json
from refresh import _context
out=r/'finance-metadata-02';out.mkdir(exist_ok=False);names={'TEAMDATA_BUDGET_TIER','TEAMDATA_FACILITY_LEVEL'};entries=[e for e in json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates'] if e['name'] in names];assert {e['name'] for e in entries}==names
reader=None;report={'pid':int(sys.argv[1]),'game_writes':False,'player_value_reads':0}
try:
    report['context_before']=_context(int(sys.argv[1]));reader=ReadOnlyGameProcess(int(sys.argv[1]));values=[read_native_enum(reader,e) for e in entries];reader.close();report['context_after']=_context(int(sys.argv[1]))
    if report['context_before']['epoch']!=report['context_after']['epoch']:raise ValueError('process/build/year changed')
    _json(out/'metadata.json',values);_json(out/'type_entries.json',entries);report.update(status='CURRENT_FINANCE_ENUMS_CAPTURED',read_trace=reader.trace)
except Exception as error:report.update(status='FINANCE_ENUM_CAPTURE_FAILED',reason=str(error),error_type=type(error).__name__,read_trace=reader.trace if reader else getattr(error,'read_trace',[]))
finally:
    if reader:reader.close()
_json(out/'report.json',report)

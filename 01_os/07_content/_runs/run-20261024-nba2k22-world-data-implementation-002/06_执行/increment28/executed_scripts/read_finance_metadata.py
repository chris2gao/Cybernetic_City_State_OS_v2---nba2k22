import hashlib,json,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from award_reader import read_native_fields
from game_mode_reader import collect_game_mode
from live_reader import ReadOnlyGameProcess
from live_world import _json
from refresh import _context
out=runtime/'finance-metadata-01';out.mkdir(exist_ok=False);names={'TEAMDATA'};mapping=json.loads((runtime/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];entries=[t for t in mapping if t['name'] in names];assert {e['name'] for e in entries}==names
report={'pid':int(sys.argv[1]),'game_writes':False,'player_value_reads':0,'getter_invocations':0};reader=None
try:
    report['context_before']=_context(int(sys.argv[1]));reader=ReadOnlyGameProcess(int(sys.argv[1]));metadata=[read_native_fields(reader,entry,4696,read_enums=False) for entry in entries];mode,blobs=collect_game_mode(reader);reader.close();report['context_after']=_context(int(sys.argv[1]))
    if report['context_before']['epoch']!=report['context_after']['epoch']:raise ValueError('process/build/year changed')
    _json(out/'metadata.json',metadata);_json(out/'type_entries.json',entries);_json(out/'game-mode-context.json',mode)
    for name,raw in blobs.items():(out/name).write_bytes(raw)
    report.update({'status':'CURRENT_TEAM_FINANCE_METADATA_CAPTURED','read_trace':reader.trace,'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
except Exception as error:report.update({'status':'FINANCE_METADATA_FAILED','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
finally:
    if reader:reader.close()
_json(out/'report.json',report)

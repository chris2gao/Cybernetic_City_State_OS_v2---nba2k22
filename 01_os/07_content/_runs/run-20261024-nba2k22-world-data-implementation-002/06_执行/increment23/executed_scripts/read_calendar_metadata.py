"""Native type metadata plus the bounded public SEASON prefix; no player values."""
import hashlib,json,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from award_reader import read_native_fields
from league_reader import read_native_enum
from live_reader import ReadOnlyGameProcess,SEASON_RVA
from live_world import _json
from refresh import _context
r=Path(__file__).resolve().parent;out=r/'calendar-metadata-01';out.mkdir(exist_ok=False)
names={'SCHEDULEDATE_MONTH','SCHEDULEDATE','SEASON_GAMESTATUS','SEASON_GAMETEAM','SEASON_GAMETYPE','SEASON_TIMEPERIOD','SEASON_GAME','SEASON_INDEX','SEASON_SCHEDULE','SEASON','FRANCHISE'}
entries=[t for t in json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates'] if t['name'] in names];assert {e['name'] for e in entries}==names
reader=None;report={'pid':int(sys.argv[1]),'game_writes':False,'player_value_reads':0}
try:
    report['context_before']=_context(int(sys.argv[1]));reader=ReadOnlyGameProcess(int(sys.argv[1]));metadata=[]
    for entry in entries:metadata.append(read_native_enum(reader,entry) if entry['constructor_rva']==31800976 else read_native_fields(reader,entry,read_enums=False))
    pointer=reader.read(reader.module_base+SEASON_RVA,8,'CALENDAR_SEASON_POINTER');root=int.from_bytes(pointer,'little');prefix=reader.read(root,40,'CALENDAR_PUBLIC_SEASON_PREFIX')
    if reader.read(root,40,'CALENDAR_PUBLIC_SEASON_PREFIX_RECHECK')!=prefix or reader.read(reader.module_base+SEASON_RVA,8,'CALENDAR_SEASON_POINTER_RECHECK')!=pointer:raise ValueError('calendar source changed')
    (out/'season-prefix.bin').write_bytes(prefix);_json(out/'metadata.json',metadata);_json(out/'type_entries.json',entries);reader.close();report['context_after']=_context(int(sys.argv[1]))
    if report['context_before']['epoch']!=report['context_after']['epoch']:raise ValueError('process/build/year changed')
    report.update({'status':'CURRENT_CALENDAR_METADATA_AND_PREFIX_CAPTURED','read_trace':reader.trace,'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
except Exception as error:report.update({'status':'CALENDAR_METADATA_FAILED','reason':str(error),'error_type':type(error).__name__,'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
finally:
    if reader:reader.close()
_json(out/'report.json',report)

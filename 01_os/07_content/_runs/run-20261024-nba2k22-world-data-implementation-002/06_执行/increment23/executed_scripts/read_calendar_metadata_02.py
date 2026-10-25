"""Complete only the selected calendar/schedule/Box-bank metadata and scalar controls."""
import hashlib,json,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from award_reader import read_native_fields
from league_reader import read_native_enum
from live_reader import ReadOnlyGameProcess,SEASON_RVA
from live_world import _json
from refresh import _context
r=Path(__file__).resolve().parent;out=r/'calendar-metadata-02';out.mkdir(exist_ok=False);old=json.loads((r/'calendar-metadata-labeled.json').read_bytes());mapping=json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];lookup={t['type_rva']:t for t in mapping}
names={'SCHEDULEDATE_MONTH','SCHEDULEDATE','SEASON_GAMESTATUS','SEASON_GAMETEAM','SEASON_GAMETYPE','SEASON_TIMEPERIOD','SEASON_GAME','SEASON_SCHEDULE','SEASON','SIM_FORCE_WINNER_TYPE'}
season=next(t for t in old if t['name']=='SEASON');field=next(f for f in season['fields'] if f['literal_names']==['BoxScoreStatBank']);bank=lookup[field['enum_pointer']-0x140000000];names.add(bank['name']);entries=[t for t in mapping if t['name'] in names]
reader=None;report={'pid':int(sys.argv[1]),'game_writes':False,'player_value_reads':0}
try:
    report['context_before']=_context(int(sys.argv[1]));reader=ReadOnlyGameProcess(int(sys.argv[1]));metadata=[];dimensions=[]
    for entry in entries:
        value=read_native_enum(reader,entry) if entry['constructor_rva']==31800976 else read_native_fields(reader,entry,read_enums=False);metadata.append(value)
        for f in value.get('fields',[]):
            w=f['words'];rank=w[5]>>16
            if 0<rank<=4:
                pointer=w[6]|w[7]<<32;raw=reader.read(pointer,24,'CALENDAR_ARRAY_DIMENSION')
                if reader.read(pointer,24,'CALENDAR_ARRAY_DIMENSION_RECHECK')!=raw:raise ValueError('array dimensions unstable')
                dimensions.append({'type':entry['name'],'name_crc':f['name_crc'],'rank':rank,'raw_hex':raw.hex()})
    pointer=reader.read(reader.module_base+SEASON_RVA,8,'CALENDAR_SEASON_POINTER');root=int.from_bytes(pointer,'little');prefix=reader.read(root,40,'CALENDAR_PUBLIC_SEASON_PREFIX')
    if reader.read(root,40,'CALENDAR_PUBLIC_SEASON_PREFIX_RECHECK')!=prefix:raise ValueError('calendar source changed')
    (out/'season-prefix.bin').write_bytes(prefix);_json(out/'metadata.json',metadata);_json(out/'dimensions.json',dimensions);_json(out/'type_entries.json',entries);reader.close();report['context_after']=_context(int(sys.argv[1]))
    if report['context_before']['epoch']!=report['context_after']['epoch']:raise ValueError('process/build/year changed')
    report.update({'status':'CURRENT_CALENDAR_METADATA_AND_DIMENSIONS_CAPTURED','read_trace':reader.trace,'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
except Exception as error:report.update({'status':'CALENDAR_METADATA_FAILED','reason':str(error),'error_type':type(error).__name__,'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
finally:
    if reader:reader.close()
_json(out/'report.json',report)

"""Selected time-period metadata and virtual getter bytes; no method invocation."""
import hashlib,json,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from award_reader import read_native_fields
from league_reader import read_native_enum
from live_reader import ReadOnlyGameProcess
from live_world import _json
from refresh import _context
out=runtime/'stat-mode-metadata-01';out.mkdir(exist_ok=False);names={'GAMEMODE','GAMEMODE_TIMEPERIOD','GAMEMODE_MODE','GAMEMODE_LEAGUE'};mapping=json.loads((runtime/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];entries=[t for t in mapping if t['name'] in names];assert {e['name'] for e in entries}==names
report={'pid':int(sys.argv[1]),'game_writes':False,'getter_invocations':0,'player_value_reads':0};reader=None
try:
    report['context_before']=_context(int(sys.argv[1]));reader=ReadOnlyGameProcess(int(sys.argv[1]));metadata=[]
    for entry in entries:metadata.append(read_native_enum(reader,entry) if entry['constructor_rva']==31800976 else read_native_fields(reader,entry,read_enums=False))
    pointer=reader.read(reader.module_base+0x6327f58,8,'STAT_MODE_OBJECT_POINTER');address=int.from_bytes(pointer,'little')
    if address<0x10000:raise ValueError('stat mode object unavailable')
    vtable_raw=reader.read(address,8,'STAT_MODE_OBJECT_VTABLE');vtable=int.from_bytes(vtable_raw,'little')
    if not reader.module_base<=vtable<reader.module_base+reader.module_size-0x340:raise ValueError('stat mode vtable outside current module')
    target_raw=reader.read(vtable+0x338,8,'STAT_MODE_VIRTUAL_GETTER_POINTER');target=int.from_bytes(target_raw,'little')
    if not reader.module_base<=target<reader.module_base+reader.module_size-96:raise ValueError('stat mode getter target outside current module')
    code=reader.read(target,96,'STAT_MODE_VIRTUAL_GETTER_CODE')
    controls=((reader.module_base+0x6327f58,pointer,'POINTER'),(address,vtable_raw,'VTABLE'),(vtable+0x338,target_raw,'TARGET'),(target,code,'CODE'))
    for at,raw,label in controls:
        if reader.read(at,len(raw),'STAT_MODE_RECHECK:'+label)!=raw:raise ValueError('stat mode context changed')
    (out/'virtual-getter.bin').write_bytes(code);_json(out/'metadata.json',metadata);_json(out/'type_entries.json',entries);report.update({'object_address':address,'vtable_rva':vtable-reader.module_base,'getter_rva':target-reader.module_base});reader.close();report['context_after']=_context(int(sys.argv[1]))
    if report['context_before']['epoch']!=report['context_after']['epoch']:raise ValueError('process/build/year changed')
    report.update({'status':'CURRENT_STAT_MODE_METADATA_AND_GETTER_BYTES_CAPTURED','read_trace':reader.trace,'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
except Exception as error:report.update({'status':'STAT_MODE_METADATA_FAILED','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
finally:
    if reader:reader.close()
_json(out/'report.json',report)

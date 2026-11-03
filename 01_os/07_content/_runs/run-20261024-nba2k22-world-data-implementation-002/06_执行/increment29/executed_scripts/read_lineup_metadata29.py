import json,math,struct,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from award_reader import read_native_fields
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _json
from schedule_reader import bounded_block
from refresh import _context
finance=json.loads((app/'finance_native_profile.json').read_bytes());detail=json.loads((app/'player_detail_native_profile.json').read_bytes());known=json.loads((runtime/'finance-metadata-labeled.json').read_bytes())[0]
names={'LineupPlayer','Starter','LineupBench','LineupTall','LineupQuick','LineupDefense','Lineup3Pter','LineupFreeThrow','LineupCustom','CustomLineupName','AdvancedRotationPlayerId'}
labels={f['name_crc']:f['literal_names'][0] for f in known['fields'] if len(f['literal_names'])==1};out=runtime/'lineup-metadata-29';out.mkdir(exist_ok=False);reader=None;report={'pid':int(sys.argv[1]),'game_writes':False,'player_value_reads':0}
try:
    before=_context(int(sys.argv[1]));reader=ReadOnlyGameProcess(int(sys.argv[1]));metadata=[]
    for entry,size in ((finance['types'][0],4696),(detail['types'][0],1264)):metadata.append(read_native_fields(reader,entry,size,read_enums=False))
    arrays={};controls=[]
    for f in metadata[0]['fields']:
        name=labels.get(f['name_crc'])
        if name not in names:continue
        rank=f['words'][5]>>16;ptr=f['words'][6]|f['words'][7]<<32;assert rank in (1,2);raw=reader.read(ptr,rank*24,'LINEUP_ARRAY_DIMENSIONS:'+name);assert reader.read(ptr,rank*24,'LINEUP_ARRAY_DIMENSIONS_RECHECK:'+name)==raw
        dims=[struct.unpack_from('<I',raw,i*24)[0] for i in range(rank)];arrays[name]={'binding':f,'dimensions':dims,'runtime_dimension_control_hex':raw.hex()}
    assert set(arrays)==names
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'LINEUP_PROBE_ROSTER_POINTER');root=int.from_bytes(pointer,'little');directory=reader.read(root+128,16,'LINEUP_PROBE_TEAM_DESCRIPTOR');count,base=struct.unpack('<QQ',directory);assert 1<=count<=1024;samples=[]
    for index in range(count):
        address=base+index*4696;ident=reader.read(address+3240,2,'LINEUP_PROBE_TEAM_ID');tid=int.from_bytes(ident,'little')
        if tid not in (0,7,8,31):continue
        sample={'native_team_id':tid,'pool_index':index,'arrays':{}}
        for name,spec in arrays.items():
            width=2 if name in ('AdvancedRotationPlayerId','CustomLineupName') else 8;size=math.prod(spec['dimensions'])*width;assert 0<size<=1024 and spec['binding']['offset']+size<=4696
            raw=bounded_block(reader,address+spec['binding']['offset'],size,'LINEUP_PROBE_ARRAY:'+name);assert bounded_block(reader,address+spec['binding']['offset'],size,'LINEUP_PROBE_ARRAY_RECHECK:'+name)==raw
            sample['arrays'][name]=list(struct.unpack('<'+str(size//2)+'H',raw)) if width==2 and name!='CustomLineupName' else raw.hex()
            (out/f'team-{tid}-{name}.bin').write_bytes(raw)
        samples.append(sample)
    assert reader.read(root+128,16,'LINEUP_PROBE_DIRECTORY_RECHECK')==directory and reader.read(reader.module_base+ROSTER_RVA,8,'LINEUP_PROBE_ROOT_RECHECK')==pointer
    reader.close();after=_context(int(sys.argv[1]));assert before['epoch']==after['epoch'];_json(out/'metadata.json',metadata);_json(out/'arrays.json',arrays);_json(out/'samples.json',samples)
    report.update(status='NATIVE_LINEUP_METADATA_AND_BOUNDED_TEAM_ARRAYS_CAPTURED',context_before=before,context_after=after,read_trace=reader.trace)
except Exception as error:report.update(status='LINEUP_METADATA_PROBE_FAILED',reason=str(error),error_type=type(error).__name__,read_trace=reader.trace if reader else getattr(error,'read_trace',[]))
finally:
    if reader:reader.close()
_json(out/'report.json',report)

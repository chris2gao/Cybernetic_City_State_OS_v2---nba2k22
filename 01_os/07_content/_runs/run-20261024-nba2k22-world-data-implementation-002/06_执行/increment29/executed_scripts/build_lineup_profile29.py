import json,mmap,re,struct,zlib
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';current=json.loads((runtime/'lineup-metadata-29/metadata.json').read_bytes());arrays=json.loads((runtime/'lineup-metadata-29/arrays.json').read_bytes());finance=json.loads((app/'finance_native_profile.json').read_bytes());detail=json.loads((app/'player_detail_native_profile.json').read_bytes());known=json.loads((runtime/'finance-metadata-labeled.json').read_bytes())[0]
team={f['name_crc']:f for f in current[0]['fields']};players={f['name_crc']:f for f in current[1]['fields']};labels={f['literal_names'][0]:f['name_crc'] for f in known['fields'] if len(f['literal_names'])==1}
flag_names=['HasAdvancedRotation','UsesCustomLineupName','EnableLineupCustom']+['ManualBuild'+n for n in ('Starter','LineupBench','LineupTall','LineupQuick','LineupDefense','Lineup3Pter','LineupFreeThrow','LineupCustom')]
flags={name:team[labels[name]] for name in flag_names};counts={name:team[labels[name]] for name in ('NumberOfLineupPlayers',)}
identity={name:players[zlib.crc32(name.encode())] for name in ('UnlocalizedFirstName','UnlocalizedLastName','CurrentTeam_Internal','UniqueId','PreservedId','PlayingTime','ForceNonStarter')}
private={name:players[zlib.crc32(name.encode())] for name in ('OriginalPotential','PotentialRaw','MinPotential','MaxPotential','PreviousPotentialRaw')}
for name,spec in arrays.items():
    controls=bytes.fromhex(spec['runtime_dimension_control_hex']);spec['dimension_strides']=[struct.unpack_from('<Q',controls,i*24+8)[0] for i in range(len(spec['dimensions']))]
    if name not in ('AdvancedRotationPlayerId','CustomLineupName'):assert len(spec['dimensions'])==1 and spec['dimension_strides']==[8]
enum=json.loads((runtime/'lineup-enum-29/metadata.json').read_bytes());enum_entry=json.loads((runtime/'lineup-enum-29/type_entry.json').read_bytes());wanted={v['name_crc'] for v in enum['values']};labels={}
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    for match in re.finditer(rb'(?<=\x00)[A-Za-z_][A-Za-z0-9_:]{0,95}\x00',data):
        raw=match.group()[:-1];crc=zlib.crc32(raw)
        if crc in wanted:labels.setdefault(crc,set()).add(raw.decode())
enum_labels={}
for value in enum['values']:
    names=sorted(labels.get(value['name_crc'],[]));assert len(names)==1,names;enum_labels[str(value['value'])]={'label':names[0],'name_crc':value['name_crc']}
profile={'layout':'NATIVE_TEAM_LINEUPS_AND_STORED_ROTATION_V1','types':[finance['types'][0],detail['types'][0],enum_entry],'arrays':arrays,'team_flags':flags,'team_counts':counts,'team_identity':finance['identity'],'player_fields':identity,'private_player_fields':private,'enum_labels':{enum['name']:enum_labels},'pointer_storage_bytes':8,'advanced_player_namespace':'UNVERIFIED; raw IDs are not canonical players','playing_time_units':'Native PlayingTime seven-bit value; UI minutes, units and actual deployment are not independently observed','advanced_axes':'Native array axes/dimensions/strides only; period/minute/position labels are not inferred'}
profile['team_flag_columns']={name:re.sub(r'(?<!^)(?=[A-Z])','_',name).lower()+'_raw' for name in flags}
(app/'lineup_native_profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'arrays':{n:{'dimensions':s['dimensions'],'strides':s['dimension_strides']} for n,s in arrays.items()},'enum_labels':enum_labels,'playing_time':{k:identity['PlayingTime'][k] for k in ('offset','size','width','start_bit')}}))

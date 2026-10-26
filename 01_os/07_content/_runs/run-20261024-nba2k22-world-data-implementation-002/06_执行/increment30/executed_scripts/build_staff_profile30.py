import hashlib,json,mmap,re,zlib
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';metadata=json.loads((runtime/'staff-metadata-30-labeled.json').read_bytes());entry=json.loads((runtime/'staff-metadata-30/type_entry.json').read_bytes());enum_entries=json.loads((runtime/'staff-enums-30/type_entries.json').read_bytes());enums=json.loads((runtime/'staff-enums-30/metadata.json').read_bytes());finance=json.loads((app/'finance_native_profile.json').read_bytes());team=json.loads((runtime/'finance-metadata-labeled.json').read_bytes())[0]
entry.update(expected_size=352,expected_field_count=metadata['field_count'],field_signature_sha256=hashlib.sha256(json.dumps(sorted((f['name_crc'],f['offset'],f['size'],f['format'],f['words'][5]) for f in metadata['fields']),separators=(',',':')).encode()).hexdigest())
names={f['literal_names'][0]:f for f in metadata['fields'] if len(f['literal_names'])==1};assert len(names)==metadata['field_count'];wanted={v['name_crc'] for e in enums for v in e['values']};literals={}
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    for match in re.finditer(rb'(?<=\x00)[A-Za-z_][A-Za-z0-9_:]{0,95}\x00',data):
        raw=match.group()[:-1];crc=zlib.crc32(raw)
        if crc in wanted:literals.setdefault(crc,set()).add(raw.decode())
labels={}
for e in enums:
    labels[e['name']]={}
    for value in e['values']:
        candidates=sorted(literals.get(value['name_crc'],[]));labels[e['name']][str(value['value'])]={'label':candidates[0] if len(candidates)==1 else None,'literal_candidates':candidates,'name_crc':value['name_crc']}
enum_by_rva={e['type_rva']:e['name'] for e in enum_entries};omitted={n:f for n,f in names.items() if n.startswith('Max') or 'Potential' in n};excluded=[(260,265)];tactical_prefixes=('System','Sim','POE','Freelance')
tactical_names=set(json.loads((repo/'08_Domain_Applications/Antigravity_GM_Engine/config/coach_tactics_profile.json').read_bytes())['fields'])|set('OffBallDefAggressiveness OnBallDefAggressiveness Fastbreak Crashboard BenchDepth LineupFormFactor RunPlayTendency DoubleTeamTendency ZoneUsage ShotInsideTendency ShotCloseTendency ShotMediumTendency ShotThreeTendency DriveTendency PostUpTendency AlleyOopTendency PreferenceSystemProficiency EarlyOffense'.split())
fields={};shared=[];padding=[]
for name,f in names.items():
    if name.lstrip('_').lower().startswith('padding'):padding.append(name);continue
    if name in omitted or f['width']==0 or name in ('FirstName','LastName','SeasonStats','UniqueId','PersonType','Status'):continue
    a=f['offset']+f['start_bit']//8;b=f['offset']+(f['start_bit']+f['width']+7)//8
    if any(a<hi and lo<b for lo,hi in excluded):shared.append(name);continue
    assert 0<=a<b<=352 and f['width']<=32
    column=re.sub(r'(?<!^)(?=[A-Z])','_',name).lower();primitive=f['primitive_literal_candidates'];assert len(primitive)==1
    fields[name]={'column':column,'group':'tactics' if name in tactical_names or name.startswith(tactical_prefixes) or 284<=f['offset']<344 else 'profile','binding':f,'primitive':primitive[0],'enum':enum_by_rva.get(f['enum_pointer']-0x140000000) if f['enum_pointer'] else None,'byte_range':[a,b]}
identity={name:names[name] for name in ('FirstName','LastName','UniqueId','CurrentTeam_Internal','PreviousTeam','MyTeamTeam','PersonType','Status')};coach=next(f for f in team['fields'] if f['literal_names']==['Coach_Internal'])
profile={'layout':'NATIVE_COMPLETE_PUBLIC_STAFF_POOL_V1','types':[entry,finance['types'][0]]+enum_entries,'identity':identity,'fields':fields,'enum_labels':labels,'enum_by_type_rva':{str(k):v for k,v in enum_by_rva.items()},'team_identity':finance['identity'],'team_coach_array':coach,'team_coach_dimensions':[8],'team_coach_strides':[8],'name_extents':{'FirstName':20,'LastName':20},'excluded_staff_grade_fields':omitted,'excluded_staff_byte_ranges':excluded,'shared_byte_fields_not_acquired':shared,'ordinary_annual_separation':'SeasonStats s16 array references are not read by this ordinary source; annual staff history remains a separate gap','privacy_scope':'No PLAYER values are read. Existing generic Potential ingestion restriction is retained; staff growth/max-grade bytes and the shared TightLipped byte are excluded without renaming around it.','units':'Native unsigned/bitfield values and exact enum labels; UI wages, grade presentation, legal hiring and behavior/effects remain separate'}
profile['padding_fields_not_acquired']=padding
(app/'staff_native_profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'public_scalar_count':len(fields),'groups':{g:sum(f['group']==g for f in fields.values()) for g in ('profile','tactics')},'enum_count':len(labels),'person_type':labels['COACHDATA_PERSONTYPE'],'status':labels['COACHDATA_STATUS'],'excluded_staff_byte_ranges':excluded,'shared_fields':shared}))

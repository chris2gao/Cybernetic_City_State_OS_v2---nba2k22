import hashlib,json,mmap,re,struct,zlib
from pathlib import Path
r=Path(__file__).resolve().parent;folder=r/'calendar-metadata-02';report=json.loads((folder/'report.json').read_bytes());assert report['status']=='CURRENT_CALENDAR_METADATA_AND_DIMENSIONS_CAPTURED',report
metadata=json.loads((folder/'metadata.json').read_bytes());entries=json.loads((folder/'type_entries.json').read_bytes());dimensions=json.loads((folder/'dimensions.json').read_bytes());wanted={v['name_crc'] for t in metadata for v in t.get('fields',[])+t.get('values',[])};names={}
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    for match in re.finditer(rb'(?<=\x00)[A-Za-z_][A-Za-z0-9_:]{0,95}\x00',data):
        value=match.group()[:-1];crc=zlib.crc32(value)
        if crc in wanted:names.setdefault(crc,set()).add(value.decode())
assert all(len(names.get(crc,[]))==1 for crc in wanted)
label=lambda crc:next(iter(names[crc]));by_name={t['name']:t for t in metadata};bindings={};enums={};dims={}
for t in metadata:
    if 'fields' in t:
        bindings[t['name']]={label(f['name_crc']):{**f,'native_name':label(f['name_crc'])} for f in t['fields']}
    else:enums[t['name']]={str(v['value']):{'name_crc':v['name_crc'],'label':label(v['name_crc'])} for v in t['values']}
for item in dimensions:
    if item['rank']==1:dims.setdefault(item['type'],{})[label(item['name_crc'])]=[struct.unpack_from('<I',bytes.fromhex(item['raw_hex']))[0]]
for entry in entries:
    t=by_name[entry['name']]
    if 'fields' in t:
        signature=sorted((f['name_crc'],f['offset'],f['size'],f['format'],f['words'][5]) for f in t['fields']);entry.update({'expected_size':t['struct_size'],'expected_field_count':len(t['fields']),'field_signature_sha256':hashlib.sha256(json.dumps(signature,separators=(',',':')).encode()).hexdigest()})
bank=next(t['name'] for t in metadata if t['name'] not in {'SEASON','SEASON_GAME','SEASON_SCHEDULE','SCHEDULEDATE'} and 'fields' in t);code=json.loads((r/'calendar-code-inspection.json').read_bytes());proof=[]
for value in code:
    if value.get('rva')==2941009:
        raw=bytes.fromhex(value['code_hex'])[:46];proof.append({'meaning':'Native date consumer extracts day/month/year offset and passes 2000+offset to the date constructor','rva':value['rva'],'hex':raw.hex(),'sha256':hashlib.sha256(raw).hexdigest()})
    if value.get('rva')==26533552:
        raw=bytes.fromhex(value['code_hex'])[:48];proof.append({'meaning':'Native date constructor subtracts 2000 and checks the 7-bit year-offset range','rva':value['rva'],'hex':raw.hex(),'sha256':hashlib.sha256(raw).hexdigest()})
profile={'status':'CURRENT_NATIVE_CALENDAR_FIELDS_ENUMS_ARRAY_EXTENTS_AND_YEAR_EPOCH_CODE; NO_UI_OR_TIMEZONE_ACCEPTANCE','module_timestamp':1652287197,'types':entries,'bindings':bindings,'enum_labels':enums,'array_dimensions':dims,'bank_type':bank,'year_epoch':2000,'code_proofs':proof}
assert dims['SEASON_SCHEDULE']['Games']==[1742] and len(proof)==2
path=Path.cwd()/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/calendar_native_profile.json';path.write_text(json.dumps(profile,indent=2)+'\n',encoding='utf-8',newline='\n')
(r/'calendar-metadata-02-labeled.json').write_text(json.dumps([{**t,'field_names':[label(f['name_crc']) for f in t.get('fields',[])]} for t in metadata],indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'types':[e['name'] for e in entries],'game_capacity':dims['SEASON_SCHEDULE']['Games'],'bank_type':bank,'bank_fields':{name:{k:f[k] for k in ('offset','size','width','start_bit')} for name,f in bindings[bank].items()},'dimensions':dims,'force_enum':enums['SIM_FORCE_WINNER_TYPE'],'proof_code_blocks':len(proof)}))

import json,mmap,re,zlib
from pathlib import Path
runtime=Path(__file__).parent;metadata=json.loads((runtime/'staff-metadata-30/metadata.json').read_bytes());wanted={f['name_crc'] for f in metadata['fields']}|{f['words'][1] for f in metadata['fields']};labels={}
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    for match in re.finditer(rb'(?<=\x00)[A-Za-z_][A-Za-z0-9_:]{0,95}\x00',data):
        raw=match.group()[:-1];crc=zlib.crc32(raw)
        if crc in wanted:labels.setdefault(crc,set()).add(raw.decode())
for f in metadata['fields']:f['literal_names']=sorted(labels.get(f['name_crc'],[]));f['primitive_literal_candidates']=sorted(labels.get(f['words'][1],[]))
(runtime/'staff-metadata-30-labeled.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n')
fields=[{k:f[k] for k in ('literal_names','primitive_literal_candidates','offset','size','width','start_bit','words','enum_pointer')} for f in metadata['fields'] if f['offset']<144 or re.search(r'Id|Salary|Contract|Birth|Year|Age|Rating|Offense|Defense|Position|Potential|Team|Staff|Scout|Trade|Train|Business|System|Sign|Retire|Active|Fired|Available',','.join(f['literal_names']),re.I)]
print(json.dumps({'field_count':metadata['field_count'],'selected_fields':fields[:65],'selected_count':len(fields)}))

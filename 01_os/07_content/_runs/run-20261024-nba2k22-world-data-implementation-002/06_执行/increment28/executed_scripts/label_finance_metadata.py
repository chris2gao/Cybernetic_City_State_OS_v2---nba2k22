import json,mmap,re,zlib
from pathlib import Path
r=Path(__file__).resolve().parent;source=r/'finance-metadata-01';metadata=json.loads((source/'metadata.json').read_bytes());wanted={f['name_crc'] for t in metadata for f in t['fields']}|{f['words'][1] for t in metadata for f in t['fields']};labels={}
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    for match in re.finditer(rb'(?<=\x00)[A-Za-z_][A-Za-z0-9_:]{0,95}\x00',data):
        literal=match.group()[:-1];crc=zlib.crc32(literal)
        if crc in wanted:labels.setdefault(crc,set()).add(literal.decode())
for t in metadata:
    for f in t['fields']:f['literal_names']=sorted(labels.get(f['name_crc'],[]));f['primitive_literal_candidates']=sorted(labels.get(f['words'][1],[]))
(r/'finance-metadata-labeled.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n')
target_offsets={0xCBC,0xFF4,0x1014,0x1018,0x1010,0xFD8,0xFDC,0xFE4};fields=[f for t in metadata for f in t['fields'] if f['offset'] in target_offsets or any(re.search(r'Salar|Budget|Cash|Revenue|Income|Finance|Expense|Cap|Tax|Pay|Profit|Ticket|Money|Price',name,re.I) for name in f['literal_names'])]
print(json.dumps({'selected_fields':[{k:f[k] for k in ('literal_names','offset','size','width','start_bit','format','primitive_literal_candidates','enum_pointer')} for f in fields],'field_count':sum(len(t['fields']) for t in metadata)}))

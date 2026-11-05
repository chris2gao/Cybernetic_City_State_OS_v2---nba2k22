import json,mmap,re,zlib
from pathlib import Path
r=Path(__file__).parent;values=json.loads((r/'staff-history-metadata-32/metadata.json').read_bytes());wanted={f['name_crc'] for t in values for f in t['fields']}|{f['words'][1] for t in values for f in t['fields']};labels={}
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    for match in re.finditer(rb'(?<=\x00)[A-Za-z_][A-Za-z0-9_:]{0,95}\x00',data):
        raw=match.group()[:-1];crc=zlib.crc32(raw)
        if crc in wanted:labels.setdefault(crc,set()).add(raw.decode())
for t in values:
    for f in t['fields']:f['literal_names']=sorted(labels.get(f['name_crc'],[]));f['primitive_literal_candidates']=sorted(labels.get(f['words'][1],[]))
(r/'staff-history-32-labeled.json').write_text(json.dumps(values,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps([{'name':t['name'],'struct_size':t['struct_size'],'fields':[f for f in t['fields'] if t['name']!='COACHDATA' or 'SeasonStats' in f['literal_names']]} for t in values]))

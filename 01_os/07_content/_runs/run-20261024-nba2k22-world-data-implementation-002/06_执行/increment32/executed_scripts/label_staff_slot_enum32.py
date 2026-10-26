import json,mmap,re,zlib
from pathlib import Path
r=Path(__file__).parent;e=json.loads((r/'staff-slot-enum-32/enum.json').read_bytes());wanted={v['name_crc'] for v in e['values']};labels={}
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    for match in re.finditer(rb'(?<=\x00)[A-Za-z_][A-Za-z0-9_:]{0,95}\x00',data):
        raw=match.group()[:-1];crc=zlib.crc32(raw)
        if crc in wanted:labels.setdefault(crc,set()).add(raw.decode())
for v in e['values']:v['literal_names']=sorted(labels.get(v['name_crc'],[]))
(r/'staff-slot-enum-32-labeled.json').write_text(json.dumps(e,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(e['values']))

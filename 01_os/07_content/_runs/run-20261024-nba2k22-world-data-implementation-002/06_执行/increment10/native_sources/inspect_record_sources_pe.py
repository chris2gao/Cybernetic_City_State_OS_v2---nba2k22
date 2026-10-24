"""Bounded known game-PE getter and public type-name investigation."""
import json,mmap,re,struct
from pathlib import Path
game=Path('E:/games/NBA 2K22/NBA2K22.exe')
with game.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,0x3c)[0];count=struct.unpack_from('<H',data,pe+6)[0]
    opt_size=struct.unpack_from('<H',data,pe+20)[0];sections=[]
    for i in range(count):
        at=pe+24+opt_size+i*40;vsize,rva,size,offset=struct.unpack_from('<4I',data,at+8);sections.append((rva,size,offset))
    def at_rva(rva):
        for start,size,offset in sections:
            if start<=rva<start+size:return offset+rva-start
        raise ValueError('unmapped code RVA')
    getter=at_rva(0xf400a0)
    candidates=[m.group()[:-1].decode('ascii') for m in re.finditer(rb'[A-Z][A-Z0-9_]{4,79}\x00',data)
        if any(token in m.group() for token in (b'AWARD',b'RECORD',b'NEWS'))]
    result={'module_timestamp':struct.unpack_from('<I',data,pe+8)[0],
        'record_getter_rva':0xf400a0,'record_getter_hex':data[getter:getter+160].hex(),
        'type_name_candidates':sorted(set(candidates))[:60],'matching_string_count':len(candidates)}
out=Path(__file__).parent/'record-sources-pe-inspection.json';out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result))

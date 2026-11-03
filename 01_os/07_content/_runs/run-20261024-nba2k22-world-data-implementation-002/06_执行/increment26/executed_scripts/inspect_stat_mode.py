"""Static switch inputs and Native metadata candidates; no getter invocation."""
import hashlib,json,mmap,re,struct
from pathlib import Path
r=Path(__file__).resolve().parent
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,60)[0];count=struct.unpack_from('<H',data,pe+6)[0];size=struct.unpack_from('<H',data,pe+20)[0];sections=[]
    for i in range(count):
        at=pe+24+size+40*i;_,rva,length,offset=struct.unpack_from('<4I',data,at+8);sections.append((rva,length,offset))
    def read(rva,size):
        for start,length,offset in sections:
            if start<=rva and rva+size<=start+length:return data[offset+rva-start:offset+rva-start+size]
        raise ValueError('unmapped static range')
    raw=read(0xb27d90,117);jump=struct.unpack('<3I',read(0xb27ddc,12));indices=read(0xb27de8,29);cases={value+2:jump[index] for value,index in enumerate(indices)}
    result={'selector_rva':0xb27d90,'selector_code_hex':raw.hex(),'sha256':hashlib.sha256(raw).hexdigest(),'virtual_slot_offset':0x338,'singleton_pointer_rva':0x6327f58,'one_result_inputs':[k for k,v in cases.items() if v==0xb27dc9],'zero_result_inputs':[k for k,v in cases.items() if v==0xb27dd3],'unproved_input_meaning':True}
mapping=json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];names=[t['name'] for t in mapping if re.search(r'(PHASE|STAGE|PERIOD|GAME.*MODE|MODE.*TYPE|SEASON_INDEX|LEAGUE.*STATE)',t['name'])]
(r/'stat-mode-switch.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'switch':result,'metadata_names':names[:55]}))

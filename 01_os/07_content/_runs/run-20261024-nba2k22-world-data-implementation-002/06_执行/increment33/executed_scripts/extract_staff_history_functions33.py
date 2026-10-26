import bisect,hashlib,json,mmap,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
r=Path(__file__).parent;md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,60)[0];n=struct.unpack_from('<H',data,pe+6)[0];sz=struct.unpack_from('<H',data,pe+20)[0];sections={}
    for j in range(n):
        at=pe+24+sz+40*j;name=data[at:at+8].split(b'\0')[0].decode();_,va,length,offset=struct.unpack_from('<4I',data,at+8);sections[name]=(va,length,offset)
    va,length,offset=sections['.pdata'];funcs=[struct.unpack_from('<III',data,offset+j)[:2] for j in range(0,length-11,12)];starts=[a for a,b in funcs]
    va,length,offset=sections['.text'];code=data[offset:offset+length];targets=[0xeafda0,0xeaf580,0xeafaf4];result=[]
    for target in targets:
        j=bisect.bisect_right(starts,target)-1;lo,hi=funcs[j];assert lo<=target<hi and hi-lo<=4096;raw=code[lo-va:hi-va];ins=[{'rva':hex(i.address),'asm':i.mnemonic+' '+i.op_str} for i in md.disasm(raw,lo)]
        result.append({'rva':lo,'code_hex':raw.hex(),'sha256':hashlib.sha256(raw).hexdigest(),'instructions':ins})
(r/'staff-history-functions33.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps([{'rva':hex(t['rva']),'instructions':t['instructions'] if t['rva']==0xeafda0 else t['instructions'][-26:]} for t in result]))

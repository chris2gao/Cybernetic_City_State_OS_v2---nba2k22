import bisect,hashlib,json,mmap,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
r=Path(__file__).parent;md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,60)[0];n=struct.unpack_from('<H',data,pe+6)[0];sz=struct.unpack_from('<H',data,pe+20)[0];sections={}
    for j in range(n):
        at=pe+24+sz+40*j;name=data[at:at+8].split(b'\0')[0].decode();_,va,length,offset=struct.unpack_from('<4I',data,at+8);sections[name]=(va,length,offset)
    va,length,offset=sections['.pdata'];funcs=[struct.unpack_from('<III',data,offset+j)[:2] for j in range(0,length-11,12)];starts=[a for a,b in funcs]
    va,length,offset=sections['.text'];code=data[offset:offset+length];candidates={};at=0
    while (at:=code.find(b'\x88\x00\x00\x00',at))>=0:
        address=va+at;j=bisect.bisect_right(starts,address)-1
        if j>=0 and address<funcs[j][1]:
            lo,hi=funcs[j]
            if hi-lo<=8192:candidates[lo]=(lo,hi)
        at+=4
    hits=[]
    for lo,hi in candidates.values():
        raw=code[lo-va:hi-va];ins=list(md.disasm(raw,lo));matches=[]
        for i in ins:
            if i.mnemonic not in ('movsx','movzx'):continue
            for op in i.operands:
                if op.type==3 and op.mem.disp==136 and op.size==2:matches.append(i.address)
        if matches:hits.append({'rva':lo,'size':hi-lo,'sha256':hashlib.sha256(raw).hexdigest(),'code_hex':raw.hex(),'matches':matches,'instructions':[{'rva':i.address,'asm':i.mnemonic+' '+i.op_str} for i in ins]})
(r/'staff-stat-consumer-candidates32.json').write_text(json.dumps(hits,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'candidate_count':len(hits),'functions':[{'rva':hex(h['rva']),'size':h['size'],'instructions':h['instructions'] if h['size']<450 else [i for i in h['instructions'] if any(abs(i['rva']-m)<70 for m in h['matches'])]} for h in hits[:24]]}))

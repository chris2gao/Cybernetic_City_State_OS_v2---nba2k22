import bisect,hashlib,json,mmap,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
r=Path(__file__).parent;md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,60)[0];n=struct.unpack_from('<H',data,pe+6)[0];sz=struct.unpack_from('<H',data,pe+20)[0];sections={}
    for j in range(n):
        at=pe+24+sz+40*j;name=data[at:at+8].split(b'\0')[0].decode();_,va,length,offset=struct.unpack_from('<4I',data,at+8);sections[name]=(va,length,offset)
    va,length,offset=sections['.pdata'];funcs=[struct.unpack_from('<III',data,offset+j)[:2] for j in range(0,length-11,12)];starts=[a for a,b in funcs];va,length,offset=sections['.text'];code=data[offset:offset+length];result=[]
    for target in (0x93fdf0,0x93fe30,0x97d250):
        j=bisect.bisect_right(starts,target)-1;lo,hi=funcs[j];assert lo<=target<hi and hi-lo<=4096;raw=code[lo-va:hi-va];constants=[];ins=[]
        for i in md.disasm(raw,lo):
            ins.append({'rva':hex(i.address),'asm':i.mnemonic+' '+i.op_str})
            for op in i.operands:
                if op.type==3 and i.reg_name(op.mem.base)=='rip':
                    address=i.address+i.size+op.mem.disp
                    for srva,slen,soffset in sections.values():
                        if srva<=address<srva+slen:
                            data_raw=data[soffset+address-srva:soffset+address-srva+16];constants.append({'rva':address,'hex':data_raw.hex(),'first_f32':struct.unpack_from('<f',data_raw)[0]})
        result.append({'rva':lo,'code_hex':raw.hex(),'sha256':hashlib.sha256(raw).hexdigest(),'instructions':ins,'constants':constants})
(r/'overall-getters35.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps([{'rva':hex(t['rva']),'instructions':t['instructions'],'constants':t['constants']} for t in result]))

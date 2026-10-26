"""Bounded static callers; no Native getter invocation or process attachment."""
import bisect,hashlib,json,mmap,struct,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
r=Path(__file__).parent;md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,60)[0];n=struct.unpack_from('<H',data,pe+6)[0];sz=struct.unpack_from('<H',data,pe+20)[0];sections={}
    for j in range(n):
        at=pe+24+sz+40*j;name=data[at:at+8].split(b'\0')[0].decode();_,va,length,offset=struct.unpack_from('<4I',data,at+8);sections[name]=(va,length,offset)
    va,length,offset=sections['.pdata'];funcs=[struct.unpack_from('<III',data,offset+j)[:2] for j in range(0,length-11,12)];starts=[a for a,b in funcs]
    va,length,offset=sections['.text'];code=data[offset:offset+length];getter='--getter' in sys.argv;targets={0xeaf930,0xf3c3a0} if getter else {0xeafda0,0xeafaa0,0xeaf580};calls=[];at=0
    while at<len(code):
        a=code.find(b'\xe8',at);b=code.find(b'\xe9',at);found=[p for p in (a,b) if p>=0]
        if not found:break
        at=min(found)
        if at+5<=len(code):
            target=va+at+5+struct.unpack_from('<i',code,at+1)[0]
            if target in targets:
                address=va+at;j=bisect.bisect_right(starts,address)-1
                if j>=0 and address<funcs[j][1] and funcs[j][1]-funcs[j][0]<=32768:
                    lo,hi=funcs[j];raw=code[lo-va:hi-va];ins=list(md.disasm(raw,lo))
                    if any(i.address==address and i.mnemonic in ('call','jmp') for i in ins):calls.append({'target':hex(target),'call_rva':hex(address),'function_rva':hex(lo),'function_size':hi-lo,'context':[{'rva':hex(i.address),'asm':i.mnemonic+' '+i.op_str} for i in ins if address-90<=i.address<=address+32]})
        at+=1
    pointer_refs=[]
    for name,(secva,length,offset) in sections.items():
        if name=='.text':continue
        for target in targets:
            raw=struct.pack('<Q',0x140000000+target);pos=offset
            while (pos:=data.find(raw,pos,offset+length))>=0:
                pointer_refs.append({'section':name,'target':hex(target),'rva':hex(secva+pos-offset)});pos+=8
    result={'status':'STATIC_CALLERS_NOT_YEAR_SEMANTICS','targets':[hex(t) for t in sorted(targets)],'direct_calls':calls,'data_pointer_refs':pointer_refs,'scope':'Selected verified coach stat functions; bounded function contexts; no game values read'}
name='staff-history-callers33.json' if getter else 'staff-history-mutator-callers33.json';(r/name).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'file':name,'direct_call_or_tail_count':len(calls),'data_pointer_refs':pointer_refs}))

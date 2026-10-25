"""Bounded static consumers and direct call sites; never invoke game code."""
import bisect,hashlib,json,mmap,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
r=Path(__file__).resolve().parent;md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,60)[0];count=struct.unpack_from('<H',data,pe+6)[0];size=struct.unpack_from('<H',data,pe+20)[0];sections={}
    for i in range(count):
        at=pe+24+size+40*i;name=data[at:at+8].split(b'\0')[0].decode();_,rva,length,offset=struct.unpack_from('<4I',data,at+8);sections[name]=(rva,length,offset)
    rva,length,offset=sections['.pdata'];functions=[struct.unpack_from('<III',data,offset+i)[:2] for i in range(0,length-11,12)];starts=[a for a,b in functions]
    trva,length,offset=sections['.text'];code=data[offset:offset+length]
    def function(address):
        j=bisect.bisect_right(starts,address)-1
        return functions[j] if j>=0 and address<functions[j][1] else None
    def decode(address):
        bounds=function(address)
        if bounds is None:
            leaf=[]
            for i in md.disasm(code[address-trva:address-trva+64],address):
                leaf.append({'rva':hex(i.address),'asm':i.mnemonic+' '+i.op_str})
                if i.mnemonic=='ret':break
            raw=code[address-trva:i.address+i.size-trva]
            return {'rva':hex(address),'bounds':None,'code_hex':raw.hex(),'sha256':hashlib.sha256(raw).hexdigest(),'bounded_leaf_candidates':leaf}
        if bounds[1]-bounds[0]>8192:return {'rva':hex(address),'bounds':bounds,'not_decoded':'outside bounded function limit'}
        raw=code[bounds[0]-trva:bounds[1]-trva]
        strings=[]
        for i in md.disasm(raw,bounds[0]):
            for op in i.operands:
                if op.type==3 and i.reg_name(op.mem.base)=='rip':
                    target=i.address+i.size+op.mem.disp
                    for section_rva,section_length,section_offset in sections.values():
                        if section_rva<=target<section_rva+section_length:
                            value=data[section_offset+target-section_rva:section_offset+target-section_rva+240].split(b'\0')[0]
                            if 6<=len(value)<240 and all(32<=v<127 or v in (9,10,13) for v in value):strings.append({'instruction_rva':hex(i.address),'string_rva':hex(target),'text':value.decode('ascii')})
        return {'rva':hex(address),'bounds':bounds,'sha256':hashlib.sha256(raw).hexdigest(),'code_hex':raw.hex(),'strings':strings,'instructions':[{'rva':hex(i.address),'asm':i.mnemonic+' '+i.op_str} for i in md.disasm(raw,bounds[0])]}
    candidates=json.loads((r/'current-stat-getter-candidates.json').read_bytes())['small_candidates'];targets={h['function'][0] for h in candidates}|{0xf22420,0xf3f880,0xb27d90,0xf21710,0xf21f50,0x11d5de0};calls={a:[] for a in targets};at=0
    while (at:=code.find(b'\xe8',at))>=0:
        if at+5<=len(code):
            destination=trva+at+5+struct.unpack_from('<i',code,at+1)[0]
            if destination in calls:
                bounds=function(trva+at)
                if bounds and bounds[1]-bounds[0]<=8192:
                    instructions=list(md.disasm(code[bounds[0]-trva:bounds[1]-trva],bounds[0]));actual=next((i for i in instructions if i.address==trva+at and i.mnemonic=='call'),None)
                    if actual:calls[destination].append({'call_rva':hex(actual.address),'function':bounds,'context':[{'rva':hex(i.address),'asm':i.mnemonic+' '+i.op_str} for i in instructions if actual.address-60<=i.address<=actual.address+28]})
        at+=1
    result={'format':'STATIC_CANDIDATES_NOT_NAMED_SEMANTICS','targets':[decode(a) for a in sorted(targets)],'direct_calls':{hex(k):v for k,v in calls.items()}}
(r/'stat-consumer-code.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
mapping=json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];types=[t['name'] for t in mapping if any(s in t['name'].upper() for s in ('STAT','PLAYOFF','PERIOD','SEASON'))]
print(json.dumps({'target_count':len(targets),'resolver_function':[t for t in result['targets'] if t['rva']=='0x11d5de0']}))

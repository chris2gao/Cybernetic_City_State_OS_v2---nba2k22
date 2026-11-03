import bisect,json,mmap,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
r=Path(__file__).resolve().parent;md=Cs(CS_ARCH_X86,CS_MODE_64);wanted=(0xf46950,0x194deb0,2941009)
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,60)[0];count=struct.unpack_from('<H',data,pe+6)[0];size=struct.unpack_from('<H',data,pe+20)[0];sections=[]
    for i in range(count):
        at=pe+24+size+40*i;vs,rva,length,offset=struct.unpack_from('<4I',data,at+8);sections.append((rva,length,offset,data[at:at+8].split(b'\0')[0].decode()))
    def raw(address,size):
        for rva,length,offset,_ in sections:
            if rva<=address and address+size<=rva+length:return data[offset+address-rva:offset+address-rva+size]
        raise ValueError('outside PE section')
    _,length,offset,_=next(s for s in sections if s[3]=='.pdata');functions=[struct.unpack_from('<III',data,offset+i)[:2] for i in range(0,length-11,12)];starts=[a for a,b in functions];results=[]
    for address in wanted:
        j=bisect.bisect_right(starts,address)-1;bounds=functions[j] if j>=0 and address<functions[j][1] else None;amount=min(192,(bounds[1]-address) if bounds else 96);code=raw(address,amount)
        results.append({'rva':address,'function':bounds,'code_hex':code.hex(),'instructions':[{'rva':i.address,'asm':i.mnemonic+' '+i.op_str} for i in md.disasm(code,address)]})
    metadata=json.loads((r/'calendar-metadata-labeled.json').read_bytes());mapped=json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];lookup={t['type_rva']:t for t in mapped};extra=[]
    game=next(t for t in metadata if t['name']=='SEASON_GAME');force=next(f for f in game['fields'] if f['literal_names']==['ForceWinner']);extra.append(lookup[force['enum_pointer']-0x140000000])
    for t in metadata:
        if t['name'] not in ('SEASON','SEASON_SCHEDULE'):continue
        for f in t['fields']:
            if f['literal_names'] not in (['Games'],['LineScore'],['Schedule']):continue
            w=f['words'];pointer=w[6]|w[7]<<32;entry={'type':t['name'],'field':f['literal_names'][0],'words':w}
            if (w[5]>>16)>0 and 0x140000000<=pointer<0x150000000:entry['dimension_bytes_hex']=raw(pointer-0x140000000,24).hex()
            results.append(entry)
(r/'calendar-code-inspection.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8',newline='\n');(r/'calendar-extra-type-entries.json').write_text(json.dumps(extra,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'code':results,'extra_types':[e['name'] for e in extra]},ensure_ascii=False))

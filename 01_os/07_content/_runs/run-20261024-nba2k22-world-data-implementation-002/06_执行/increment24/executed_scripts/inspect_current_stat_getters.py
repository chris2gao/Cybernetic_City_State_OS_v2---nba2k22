"""Static candidates for existing current stat-index accesses; no code invocation."""
import bisect,hashlib,json,mmap,re,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
r=Path(__file__).resolve().parent;md=Cs(CS_ARCH_X86,CS_MODE_64);hits=[];counts={}
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,60)[0];count=struct.unpack_from('<H',data,pe+6)[0];size=struct.unpack_from('<H',data,pe+20)[0];sections={}
    for i in range(count):
        at=pe+24+size+40*i;name=data[at:at+8].split(b'\0')[0].decode();_,rva,length,offset=struct.unpack_from('<4I',data,at+8);sections[name]=(rva,length,offset)
    rva,length,offset=sections['.pdata'];functions=[struct.unpack_from('<III',data,offset+i)[:2] for i in range(0,length-11,12)];starts=[a for a,b in functions]
    rva,length,offset=sections['.text'];text=data[offset:offset+length];seen=set()
    for disp in (252,3712):
        matches=list(re.finditer(rb'\x0f\xb7[\x80-\xbf].?'+re.escape(struct.pack('<I',disp)),text));counts[str(disp)]=len(matches)
        for match in matches:
            address=rva+match.start();j=bisect.bisect_right(starts,address)-1;bounds=functions[j] if j>=0 and address<functions[j][1] else None
            if not bounds or bounds in seen or bounds[1]-bounds[0]>512:continue
            seen.add(bounds);code=text[bounds[0]-rva:bounds[1]-rva];hits.append({'displacement':disp,'function':bounds,'code_hex':code.hex(),'sha256':hashlib.sha256(code).hexdigest(),'instructions':[{'rva':i.address,'asm':i.mnemonic+' '+i.op_str} for i in md.disasm(code,bounds[0])]})
(r/'current-stat-getter-candidates.json').write_text(json.dumps({'match_counts':counts,'small_candidates':hits},indent=2)+'\n',encoding='utf-8',newline='\n')
mapping=json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];types=[t['name'] for t in mapping if re.search(r'(PLAYER|TEAM).*STAT.*(TYPE|INDEX|SCOPE|PERIOD)|STAT.*(TYPE|PERIOD)',t['name'])]
print(json.dumps({'match_counts':counts,'small_candidate_count':len(hits),'stat_type_names':types[:35],'samples':[{'displacement':h['displacement'],'function':h['function'],'instructions':h['instructions'][:22]} for h in hits[:5]]}))

import bisect,hashlib,json,mmap,re,struct,zlib
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
r=Path(__file__).resolve().parent;source=r/'calendar-metadata-01';report=json.loads((source/'report.json').read_bytes());assert report['status']=='CURRENT_CALENDAR_METADATA_AND_PREFIX_CAPTURED',report
metadata=json.loads((source/'metadata.json').read_bytes());wanted={f['name_crc'] for t in metadata for f in t.get('fields',[])}|{v['name_crc'] for t in metadata for v in t.get('values',[])};labels={};candidates=[];md=Cs(CS_ARCH_X86,CS_MODE_64)
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    for match in re.finditer(rb'(?<=\x00)[A-Za-z_][A-Za-z0-9_:]{0,95}\x00',data):
        literal=match.group()[:-1];crc=zlib.crc32(literal)
        if crc in wanted:labels.setdefault(crc,set()).add(literal.decode())
    pe=struct.unpack_from('<I',data,60)[0];count=struct.unpack_from('<H',data,pe+6)[0];opt=pe+24;size=struct.unpack_from('<H',data,pe+20)[0];sections={}
    for index in range(count):
        at=opt+size+40*index;name=data[at:at+8].split(b'\0')[0].decode();_,rva,length,offset=struct.unpack_from('<4I',data,at+8);sections[name]=(rva,length,offset)
    rva,length,offset=sections['.pdata'];functions=[struct.unpack_from('<III',data,offset+i)[:2] for i in range(0,length-11,12)];starts=[a for a,b in functions]
    rva,length,offset=sections['.text'];text=data[offset:offset+length]
    for match in re.finditer(rb'\xc1[\xe8-\xef]\x19',text):
        address=rva+match.start();j=bisect.bisect_right(starts,address)-1;bounds=functions[j] if j>=0 and address<functions[j][1] else None
        tail=text[match.start():match.start()+40]
        if not any(struct.pack('<I',value) in tail for value in (1900,2000)):continue
        start=bounds[0] if bounds and bounds[1]-bounds[0]<=2048 else address;stop=min(bounds[1] if bounds else address+64,start+2048);code=text[start-rva:stop-rva]
        candidates.append({'rva':address,'function':bounds,'code_rva':start,'code_hex':code.hex(),'sha256':hashlib.sha256(code).hexdigest(),'instructions':[{'rva':i.address,'asm':i.mnemonic+' '+i.op_str} for i in md.disasm(code,start)]})
for t in metadata:
    for f in t.get('fields',[]):f['literal_names']=sorted(labels.get(f['name_crc'],[]))
    for v in t.get('values',[]):v['literal_names']=sorted(labels.get(v['name_crc'],[]))
(r/'calendar-metadata-labeled.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n');(r/'calendar-year-code-candidates.json').write_text(json.dumps(candidates,indent=2)+'\n',encoding='utf-8',newline='\n')
small=[]
for t in metadata:
    if t['name']=='FRANCHISE':fields=[f for f in t.get('fields',[]) if any(re.search(r'Date|Stage|Phase|Period|Season',n) for n in f['literal_names'])]
    else:fields=t.get('fields',[])
    small.append({'name':t['name'],'size':t.get('struct_size'),'fields':[{k:f[k] for k in ('literal_names','offset','size','width','start_bit','enum_pointer')} for f in fields[:35]],'values':[{'value':v['value'],'names':v['literal_names']} for v in t.get('values',[])]})
print(json.dumps({'types':small,'year_code_candidates':[{'rva':c['rva'],'function':c['function'],'instructions':c['instructions'][:20]} for c in candidates[:4]],'year_candidate_count':len(candidates)},ensure_ascii=False))

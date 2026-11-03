import json,mmap,re,zlib
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
r=Path(__file__).resolve().parent;source=r/'stat-mode-metadata-01';metadata=json.loads((source/'metadata.json').read_bytes());wanted={f['name_crc'] for t in metadata for f in t.get('fields',[])}|{v['name_crc'] for t in metadata for v in t.get('values',[])};labels={}
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    for match in re.finditer(rb'(?<=\x00)[A-Za-z_][A-Za-z0-9_:]{0,95}\x00',data):
        literal=match.group()[:-1];crc=zlib.crc32(literal)
        if crc in wanted:labels.setdefault(crc,set()).add(literal.decode())
for t in metadata:
    for f in t.get('fields',[]):f['literal_names']=sorted(labels.get(f['name_crc'],[]))
    for v in t.get('values',[]):v['literal_names']=sorted(labels.get(v['name_crc'],[]))
(r/'stat-mode-metadata-labeled.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n');report=json.loads((source/'report.json').read_bytes());md=Cs(CS_ARCH_X86,CS_MODE_64);instructions=[]
for i in md.disasm((source/'virtual-getter.bin').read_bytes(),report['getter_rva']):
    instructions.append({'rva':hex(i.address),'asm':i.mnemonic+' '+i.op_str})
    if i.mnemonic=='ret':break
print(json.dumps({'types':[{'name':t['name'],'size':t.get('struct_size'),'fields':[{'names':f['literal_names'],'offset':f['offset'],'enum_pointer':f['enum_pointer']} for f in t.get('fields',[])],'values':[{'value':v['value'],'names':v['literal_names']} for v in t.get('values',[])]} for t in metadata],'current_virtual_getter':instructions[:35]}))

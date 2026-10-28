import argparse,json,re,struct
from pathlib import Path
from capstone.x86 import X86_OP_IMM
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--target',type=lambda s:int(s,0),required=True);p.add_argument('--out',required=True);a=p.parse_args();im=Image();code=im.read(im.text['rva'],im.text['size']);refs=[]
for m in re.finditer(rb'[\xe8\xe9]....',code,re.S):
 rv=im.text['rva']+m.start();dest=rv+5+struct.unpack_from('<i',m.group(),1)[0]
 if dest!=a.target:continue
 rg=im.function_range(rv)
 if not rg or rg[1]-rg[0]>32768:continue
 ins=im.instructions(*rg);hit=next((i for i in ins if i.address-im.base==rv and i.mnemonic in ('call','jmp') and i.operands[0].type==X86_OP_IMM and i.operands[0].imm-im.base==a.target),None)
 if not hit:continue
 idx=ins.index(hit);window=ins[max(0,idx-12):idx+5]
 refs.append(dict(callsite_rva=rv,kind=hit.mnemonic,unwind_chain=im.unwind_chain(rv),window=im.instruction_rows(window[0].address-im.base,window[-1].address-im.base+window[-1].size)))
 if len(refs)>=48:break
pointer_refs=[];needle=struct.pack('<Q',im.base+a.target)
for sec in im.sections:
 if sec['name'] not in ('.rdata','.data'):continue
 at=sec['raw']
 while len(pointer_refs)<32:
  at=im.data.find(needle,at,sec['raw']+sec['size'])
  if at<0:break
  pointer_refs.append(dict(section=sec['name'],rva=sec['rva']+at-sec['raw']));at+=8
result=dict(game_build_sha256=im.sha256,target_rva=a.target,source_kind='STATIC_BINARY',direct_call_or_tailjump_refs=refs,image_pointer_refs=pointer_refs,limits=dict(direct_refs=48,pointer_refs=32,unwind_bytes=32768),limitations=['static caller identity does not establish AI runtime dispatch','indirect computed callers may be absent'])
path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(dict(target_rva=a.target,callers=[dict(site=r['callsite_rva'],primary=r['unwind_chain'][-1]['begin']) for r in refs],pointer_refs=pointer_refs)))

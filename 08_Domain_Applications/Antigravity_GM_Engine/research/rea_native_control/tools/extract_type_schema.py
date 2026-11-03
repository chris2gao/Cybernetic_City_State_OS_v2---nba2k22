"""Read PC22 static type registration tables, matching property CRCs to local names."""
import argparse,json,re,struct,sys,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'rea_native_action'))
from pe_local import Image
from capstone.x86 import X86_OP_MEM,X86_REG_RIP
p=argparse.ArgumentParser();p.add_argument('--registration',nargs='+',type=lambda s:int(s,0),required=True);p.add_argument('--out',required=True);a=p.parse_args();im=Image();rd=im.section('.rdata');names={}
for m in re.finditer(rb'[A-Za-z][A-Za-z0-9_]{1,64}\x00',im.data[rd['raw']:rd['raw']+rd['size']]):
 name=m.group()[:-1].decode();names.setdefault(zlib.crc32(name.encode()),set()).add(name)
types=[]
for rv in a.registration:
 regs={}
 for i in im.instructions(rv,rv+51):
  if i.mnemonic=='lea' and i.operands[-1].type==X86_OP_MEM and i.operands[-1].mem.base==X86_REG_RIP:regs[i.op_str.split(',')[0]]=i.address+i.size+i.operands[-1].mem.disp-im.base
 if not {'r8','rdx','r9','rcx'}<=set(regs):raise ValueError('Registration contract not recovered')
 info=im.read(regs['rdx'],24);count,size=struct.unpack_from('<II',info,16)
 if not 0<count<=800:raise ValueError('Static field table count outside budget')
 name=im.read(regs['r9'],100).split(b'\0')[0].decode('ascii');rows=[]
 for i in range(count):
  b=im.read(regs['r8']+i*40,40);crc,typ,offset,element_size,fmt,flags=struct.unpack_from('<6I',b);refs=[]
  for off in (24,32):
   raw=struct.unpack_from('<Q',b,off)[0];refs.append(raw-im.base if im.base<=raw<im.base+0x70000000 else None)
  rows.append({'crc':crc,'name_candidates':sorted(names.get(crc,[])),'type_crc':typ,'offset':offset,'element_size':element_size,'format':fmt,'flags_raw':flags,'image_ref_rvas':refs})
 types.append({'registration_rva':rv,'name':name,'runtime_descriptor_rva':regs['rcx'],'static_fields_rva':regs['r8'],'static_info_rva':regs['rdx'],'object_size':size,'field_count':count,'fields':rows})
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'source_kind':'PC22_STATIC_TYPE_REGISTRATIONS_NOT_LIVE','game_build_sha256':im.sha256,'types':types,'limitations':['CRC name matches are hypotheses if multiple names collide','format and static image refs are preserved raw; do not assume every ref is a getter','No current save or game process was read']},indent=2),encoding='utf-8');print(json.dumps({'types':[{'name':t['name'],'bytes':t['object_size'],'fields':t['field_count'],'named':sum(bool(f['name_candidates']) for f in t['fields'])} for t in types]}))

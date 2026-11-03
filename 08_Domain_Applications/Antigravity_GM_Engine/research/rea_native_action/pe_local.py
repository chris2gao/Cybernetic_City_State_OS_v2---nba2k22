"""Pinned local PE facts, without loading a native analysis database or target code."""
import bisect,hashlib,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
BUILD='1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'
EXE=Path('E:/Games/NBA 2K22/NBA2K22.exe')
class Image:
 def __init__(self,path=EXE):
  self.data=Path(path).read_bytes();self.sha256=hashlib.sha256(self.data).hexdigest()
  if self.sha256!=BUILD:raise ValueError('pinned game build mismatch')
  pe=struct.unpack_from('<I',self.data,60)[0];opt=struct.unpack_from('<H',self.data,pe+20)[0]
  self.base=struct.unpack_from('<Q',self.data,pe+24+24)[0];self.sections=[]
  for i in range(struct.unpack_from('<H',self.data,pe+6)[0]):
   o=pe+24+opt+i*40;vs,rv,size,raw=struct.unpack_from('<IIII',self.data,o+8)
   self.sections.append(dict(name=self.data[o:o+8].split(b'\0')[0].decode(),rva=rv,size=size,raw=raw,virtual_size=vs))
  self.text=self.section('.text');pd=self.section('.pdata')
  self.ranges=sorted(struct.unpack_from('<III',self.data,o) for o in range(pd['raw'],pd['raw']+pd['size']-11,12))
  self.starts=[e[0] for e in self.ranges];self.cs=Cs(CS_ARCH_X86,CS_MODE_64);self.cs.detail=True
 def section(self,name):return next(s for s in self.sections if s['name']==name)
 def offset(self,rva):
  s=next(s for s in self.sections if s['rva']<=rva<s['rva']+s['size']);return s['raw']+rva-s['rva']
 def read(self,rva,size):return self.data[self.offset(rva):self.offset(rva)+size]
 def function_range(self,rva):
  i=bisect.bisect_right(self.starts,rva)-1
  return self.ranges[i][:2] if i>=0 and self.ranges[i][0]<=rva<self.ranges[i][1] else None
 def unwind_chain(self,rva):
  i=bisect.bisect_right(self.starts,rva)-1
  if i<0 or not self.ranges[i][0]<=rva<self.ranges[i][1]:return []
  entry=self.ranges[i];chain=[]
  for _ in range(8):
   lo,hi,unwind=entry;header=self.read(unwind,4);flags=header[0]>>3
   chain.append(dict(begin=lo,end=hi,unwind_rva=unwind,flags=flags))
   if not flags&4:return chain
   offset=4+((header[2]+1)&~1)*2;entry=struct.unpack('<III',self.read(unwind+offset,12))
   if any(r['begin']==entry[0] and r['end']==entry[1] for r in chain):raise ValueError('cyclic chained unwind')
  raise ValueError('unwind chain budget exceeded')
 def instructions(self,start,end):return list(self.cs.disasm(self.read(start,end-start),self.base+start))
 def instruction_rows(self,start,end):
  import re
  rows=[]
  for i in self.instructions(start,end):
   ops=re.sub(r'0x[0-9a-f]+',lambda m:'RVA+'+hex(int(m.group(),16)-self.base) if self.base<=int(m.group(),16)<self.base+0x20000000 else m.group(),i.op_str)
   rows.append(dict(rva=i.address-self.base,mnemonic=i.mnemonic,operands=ops.replace('0xffffffffffffffff','-1')))
  return rows

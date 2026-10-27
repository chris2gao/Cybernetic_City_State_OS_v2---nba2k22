"""Bounded offline PE registration/string-xref discovery; no target execution."""
import argparse,bisect,hashlib,json,re,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64

parser=argparse.ArgumentParser()
parser.add_argument('--exe',default='E:/Games/NBA 2K22/NBA2K22.exe')
parser.add_argument('--out',required=True)
args=parser.parse_args()
data=Path(args.exe).read_bytes()
assert hashlib.sha256(data).hexdigest()=='1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'
pe=struct.unpack_from('<I',data,60)[0]
n=struct.unpack_from('<H',data,pe+6)[0]
opt=struct.unpack_from('<H',data,pe+20)[0]
sections=[]
for i in range(n):
 h=pe+24+opt+40*i
 vs,rva,size,off=struct.unpack_from('<IIII',data,h+8)
 sections.append(dict(name=data[h:h+8].split(b'\0')[0].decode('ascii'),rva=rva,raw_size=size,raw_offset=off))
def offset(rva):
 return next(s['raw_offset']+rva-s['rva'] for s in sections if s['rva']<=rva<s['rva']+s['raw_size'])
def string(rva):
 try:
  off=offset(rva); raw=data[off:off+180].split(b'\0')[0]
  return raw.decode('ascii') if raw and all(32<=b<127 for b in raw) else None
 except (StopIteration,UnicodeDecodeError):return None
text=next(s for s in sections if s['name']=='.text')
code=data[text['raw_offset']:text['raw_offset']+text['raw_size']]
def rip(at):return text['rva']+at+7+struct.unpack_from('<i',code,at+3)[0]
registrations=[]
pattern=rb'\x4c\x8d\x0d....[\s\S]{0,20}?\x4c\x8d\x05....\x48\x8d\x15....\x48\x8d\x0d....[\xe8\xe9]....'
for m in re.finditer(pattern,code,re.S):
 b=m.group(); p=b.find(b'\x4c\x8d\x05',7)
 pos=m.start();call=pos+p+21
 ctor=text['rva']+call+5+struct.unpack_from('<i',code,call+1)[0]
 if ctor not in (31801136,31800976):continue
 name=string(rip(pos))
 if name is None:continue
 registrations.append(dict(name=name,type_rva=rip(pos+p+14),name_rva=rip(pos),field_array_rva=rip(pos+p+7),schema_rva=rip(pos+p),initializer_rva=text['rva']+pos,initializer_hex=b.hex(),constructor_rva=ctor,kind='struct' if ctor==31801136 else 'enum'))
wanted=[r for r in registrations if re.search(r'BADGE|MENTOR|GROWTH|PROGRESS|TICKER|PRESENTATION|BROADCAST|HALFTIME|INTERVIEW|STADIUM|GLOBALDATA|TUNEDATA$|STAT.*OVERLAY',r['name'],re.I)]
# Candidate string-to-code xrefs are restricted to RIP-relative LEA encodings.
terms=re.compile(r'FRANCHISE_MENTOR::|PLAYERCARD_BADGES_INTERFACE::GetBadge|CAREERMODE_PROGRESSION::BADGES::GetBadge|PRESENTATION::DEFERRED_TASK_MANAGER::|ActiveScorebug == null|StartingLineupOverlayLowerThird|HALFTIME_SHOWN|FranchiseTickerAllowed')
strings={}
for m in re.finditer(rb'[\x20-\x7e]{5,180}\x00',data):
 s=m.group()[:-1].decode('ascii')
 if terms.search(s):
  rv=next((sec['rva']+m.start()-sec['raw_offset'] for sec in sections if sec['raw_offset']<=m.start()<sec['raw_offset']+sec['raw_size']),None)
  if rv is not None:strings[rv]=s
pdata=next(s for s in sections if s['name']=='.pdata')
entries=[struct.unpack_from('<III',data,o) for o in range(pdata['raw_offset'],pdata['raw_offset']+pdata['raw_size']-11,12)]
entries=sorted(e for e in entries if 4096<=e[0]<e[1]<=35602432)
starts=[e[0] for e in entries]
decoder=Cs(CS_ARCH_X86,CS_MODE_64)
xrefs=[]
for m in re.finditer(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]....',code,re.S):
 target=rip(m.start())
 if target not in strings:continue
 rv=text['rva']+m.start(); idx=bisect.bisect_right(starts,rv)-1
 body=entries[idx] if idx>=0 and entries[idx][0]<=rv<entries[idx][1] else None
 ins=next(decoder.disasm(m.group(),0x140000000+rv,count=1),None)
 if not ins or ins.size!=7:continue
 xrefs.append(dict(string=strings[target],string_rva=target,instruction_rva=rv,instruction_hex=m.group().hex(),instruction=f'{ins.mnemonic} {ins.op_str}',function_range=list(body[:2]) if body else None,interpretation='candidate reference to literal; not execution or caller proof'))
result=dict(exe_sha256=hashlib.sha256(data).hexdigest(),registration_count=len(registrations),relevant_registrations=wanted,xrefs=xrefs,limitations=['offline helper, not REA output','registration template and RIP-relative LEA coverage only','pdata ranges are unwind metadata, not a recovered CFG','names do not prove availability or runtime effects'])
out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
(out/'native-seams.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'registrations':len(registrations),'relevant_count':len(wanted),'relevant':[{k:v for k,v in r.items() if k in ['name','type_rva','kind']} for r in wanted[:65]],'xref_count':len(xrefs),'xref_examples':xrefs[:12]}))

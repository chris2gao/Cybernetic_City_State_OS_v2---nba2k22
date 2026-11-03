"""Only exact M1/M2/M3 literal probes and references; no whole-game catalog or execution."""
import argparse,bisect,hashlib,json,re,struct,time
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
p=argparse.ArgumentParser();p.add_argument('--exe',default='E:/Games/NBA 2K22/NBA2K22.exe');p.add_argument('--out',required=True);p.add_argument('--followup',action='store_true');a=p.parse_args();start=time.monotonic()
data=Path(a.exe).read_bytes();sha=hashlib.sha256(data).hexdigest();assert sha=='1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'
pe=struct.unpack_from('<I',data,60)[0];n=struct.unpack_from('<H',data,pe+6)[0];opt=struct.unpack_from('<H',data,pe+20)[0];sections=[]
for i in range(n):
 off=pe+24+opt+i*40;vs,rva,size,raw=struct.unpack_from('<IIII',data,off+8);sections.append({'name':data[off:off+8].split(b'\0')[0].decode(),'rva':rva,'size':size,'raw':raw})
def to_rva(off):return next(s['rva']+off-s['raw'] for s in sections if s['raw']<=off<s['raw']+s['size'])
text=next(s for s in sections if s['name']=='.text');rdata=next(s for s in sections if s['name']=='.rdata');pdata=next(s for s in sections if s['name']=='.pdata')
queries={'M1':['FRANCHISE_MENTOR::MANAGER::LinkMentor','FRANCHISE_MENTOR::MANAGER::SetMentorsInCurrentTeam'],
 'M2':['POEDefense','POEOffense','AI_COACH::','AI_COACHING::','COACHING::'],
 'M3':['FRANCHISE_TRADE','TRADE::','AI_TRADE','AI::TRADE','ValidateTrade','CommitTrade']}
if a.followup:queries={'M2':['COACH::','GAMEPLAN_MANAGER::','SetPOE','DEFENSIVE_SETTINGS::','AI_COACH'], 'M3':['EVALUATE_AI_TRADES','TRADE_MANAGER::','TradeException','FRANCHISE_TRADE_ELEMENT::GetException']}
found={};query_results=[]
for mechanism,terms in queries.items():
 for term in terms:
  needle=term.encode();at=rdata['raw'];hits=[]
  while len(hits)<12:
   at=data.find(needle,at,rdata['raw']+rdata['size'])
   if at<0:break
   left=data.rfind(b'\0',max(rdata['raw'],at-180),at)+1;right=data.find(b'\0',at,min(at+240,len(data)))
   if right>at and right-left<=240:
    raw=data[left:right]
    if raw and all(32<=b<127 for b in raw):
     rv=to_rva(left);literal=raw.decode('ascii');hits.append({'rva':rv,'literal':literal});found[rv]={'mechanism':mechanism,'literal':literal}
   at+=len(needle)
  query_results.append({'mechanism':mechanism,'exact_term':term,'retained_hits':hits,'cap':12,'scope':'.rdata only; zero hits means not found in this bounded lexical query'})
entries=sorted(struct.unpack_from('<III',data,o) for o in range(pdata['raw'],pdata['raw']+pdata['size']-11,12) if 4096<=struct.unpack_from('<I',data,o)[0]<35602432)
starts=[e[0] for e in entries];code=data[text['raw']:text['raw']+text['size']];decoder=Cs(CS_ARCH_X86,CS_MODE_64);refs=[]
for m in re.finditer(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]....',code,re.S):
 rv=text['rva']+m.start();target=rv+7+struct.unpack_from('<i',m.group(),3)[0]
 if target not in found:continue
 index=bisect.bisect_right(starts,rv)-1;entry=entries[index] if index>=0 else None
 if not entry or not entry[0]<=rv<entry[1]:continue
 item=found[target];refs.append({'mechanism':item['mechanism'],'literal':item['literal'],'instruction_rva':rv,'literal_rva':target,'unwind_range_rva':list(entry[:2]),'reference_kind':'RIP_RELATIVE_LEA_NOT_EXECUTION','proof':'STATIC_BINARY_REFERENCE_ONLY'})
 if len(refs)>=120:break
assert time.monotonic()-start<90
result={'source_kind':'STATIC_BINARY','exe_sha256':sha,'elapsed_ms':round((time.monotonic()-start)*1000),'scope':{'exact_query_count':sum(map(len,queries.values())),'literal_hit_cap_per_query':12,'reference_cap':120,'file_bytes_read':len(data),'lexical_section_bytes':rdata['size'],'xref_section_bytes':text['size'],'timeout_seconds':90,'attempt':1},'queries':query_results,'references':refs,'absolute_addresses_published':False,'game_process_attached':False,'limitations':['exact-term lexical search is not complete code coverage','unwind ranges may be function fragments','literal references are not AI callsite or ABI proof','no game bytes, raw object values or executable copied to output']}
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/('static_ai_followup.json' if a.followup else 'static_ai_seams.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'sha256':sha,'elapsed_ms':result['elapsed_ms'],'queries':[{k:v for k,v in q.items() if k!='retained_hits'}|{'hit_count':len(q['retained_hits'])} for q in query_results],'references':len(refs),'reference_examples':refs[:8]}))

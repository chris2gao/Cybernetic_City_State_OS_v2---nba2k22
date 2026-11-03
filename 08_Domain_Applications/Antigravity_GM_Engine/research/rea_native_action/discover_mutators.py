"""Targeted C1-C6 mutation names and COACHDATA +316 instruction hypotheses."""
import argparse,json,re,struct,time
from pathlib import Path
from capstone import CS_AC_WRITE
from capstone.x86 import X86_OP_MEM
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--write-cap',type=int,default=240);p.add_argument('--followup-names',action='store_true');a=p.parse_args();start=time.monotonic();im=Image()
if not 1<=a.write_cap<=1024:raise ValueError('write cap must be 1..1024')
queries={
 'C1':['POEDefense','POEOffense','SetPoe','SetPOE','SetDefense','SetOffense','COACH::','COACHDATA::','GAMEPLAN_MANAGER::'],
 'C2':['SetRotation','SetMinutes','SetTraining','ROTATION::','TRAINING::'],
 'C3':['SetAttribute','SetTendency','SetBadge','PLAYER::Set','PLAYERDATA::Set'],
 'C4':['ValidateTrade','CommitTrade','ExecuteTrade','AcceptTrade','FRANCHISE_TRADE::'],
 'C5':['SignPlayer','CommitContract','AcceptContract','FRANCHISE_CONTRACT::'],
 'C6':['DraftPlayer','SelectDraftPick','MakeDraftPick','FRANCHISE_DRAFT::']}
if a.followup_names:queries={
 'C2':['FRANCHISE_TRAINING::','Rotation','AllocateMinutes','PlayerMinutes'],
 'C3':['PLAYERDATA::','ModifyAttribute','AttributeValue','BadgeLevel','ApplyPlayer'],
 'C4':['TRADE::','TradePlayers','ProcessTrade','TRADE_MANAGER','AI_TRADE','EVALUATE_AI_TRADES'],
 'C5':['SIGNING::','CONTRACT::','SignFreeAgent','FreeAgent::','FREE_AGENCY::','FRANCHISE_CONTRACT'],
 'C6':['DRAFT::','DraftPlayer','DraftSelection','FRANCHISE_DRAFT','AI_DRAFT']}
rd=im.section('.rdata');end=rd['raw']+rd['size'];literals={};query_rows=[]
for cat,terms in queries.items():
 for term in terms:
  at=rd['raw'];hits=[]
  while len(hits)<16:
   at=im.data.find(term.encode(),at,end)
   if at<0:break
   left=im.data.rfind(b'\0',max(rd['raw'],at-180),at)+1;right=im.data.find(b'\0',at,min(at+200,end))
   raw=im.data[left:right] if right>at else b''
   if raw and len(raw)<=240 and all(32<=b<127 for b in raw):
    rv=rd['rva']+left-rd['raw'];row=dict(category=cat,rva=rv,literal=raw.decode());hits.append(row);literals[rv]=row
   at+=len(term)
  query_rows.append(dict(category=cat,term=term,hits=hits,hit_cap=16,coverage='EXACT_ASCII_SUBSTRING_IN_RDATA_NOT_COMPLETE_INVENTORY'))
text=im.read(im.text['rva'],im.text['size']);refs=[]
for m in re.finditer(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]....',text,re.S):
 rv=im.text['rva']+m.start();target=rv+7+struct.unpack_from('<i',m.group(),3)[0]
 if target in literals:refs.append(dict(**literals[target],instruction_rva=rv,unwind_range_rva=im.function_range(rv)))
 if len(refs)>=240:break
# A disp32 byte match is only a candidate instruction end. Decode from the
# containing unwind range and require a real memory operand with write access.
candidates={};byte_hits=0
for m in ([] if a.followup_names else re.finditer(re.escape(struct.pack('<I',316)),text)):
 byte_hits+=1;rv=im.text['rva']+m.start();rg=im.function_range(rv)
 if rg and rg[1]-rg[0]<=32768:candidates[rg]=True
writes=[]
for (lo,hi) in candidates:
 ins=im.instructions(lo,hi)
 for idx,i in enumerate(ins):
  if not any(o.type==X86_OP_MEM and o.mem.disp==316 and o.access&CS_AC_WRITE for o in i.operands):continue
  neighbors=ins[max(0,idx-5):idx+4]
  nearby_bits=any(any(token in n.op_str for token in ('0x1f','0xffffffe0','0xfff07fff','0xf8000','0x7fff','0x1f000')) and n.mnemonic in ('and','or','shl','shr','bts','btr') for n in neighbors)
  writes.append(dict(instruction_rva=i.address-im.base,mnemonic=i.mnemonic,operands=i.op_str,unwind_range_rva=[lo,hi],nearby_poe_bit_pattern=nearby_bits,window=im.instruction_rows(neighbors[0].address-im.base,neighbors[-1].address-im.base+neighbors[-1].size),classification='OFFSET_WRITE_HYPOTHESIS_NOT_YET_COACH_OBJECT_OR_ABI_PROOF'))
  if len(writes)>=a.write_cap:break
 if len(writes)>=a.write_cap:break
result=dict(game_build_sha256=im.sha256,source_kind='STATIC_BINARY',elapsed_ms=round((time.monotonic()-start)*1000),queries=query_rows,references=refs,coach_offset_write_candidates=writes,bounds=dict(name_hit_cap=16,reference_cap=240,write_cap=a.write_cap,write_cap_reached=len(writes)==a.write_cap,max_unwind_bytes=32768,disp316_byte_hits=byte_hits,decoded_unwind_ranges=len(candidates)),game_calls=0,game_attach=False,limitations=['names and shared offsets do not prove business function identity','unwind entries may be fragments','no AI caller or calling-thread proof yet'])
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'mutator_discovery.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(dict(elapsed_ms=result['elapsed_ms'],queries=[dict(category=q['category'],term=q['term'],hits=len(q['hits'])) for q in query_rows],references=len(refs),offset_writes=len(writes),poe_bit_candidates=[dict(rva=w['instruction_rva'],function=w['unwind_range_rva']) for w in writes if w['nearby_poe_bit_pattern']][:20])))

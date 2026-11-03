"""C4-only string/assert anchors; bounded original native transaction discovery."""
import argparse,json,re,struct,time
from pathlib import Path
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();start=time.monotonic();im=Image();rd=im.section('.rdata');region=im.read(rd['rva'],rd['size']);strings={}
for m in re.finditer(rb'[\x20-\x7e]{5,240}\x00',region):
 text=m.group()[:-1].decode()
 if not any(term in text.lower() for term in ('trade','transaction')):continue
 if not ('::' in text or any(term in text.lower() for term in ('commit','validat','accept','execute','process','proposal','offer','franchise','tradeplayer','trade_player'))):continue
 rv=rd['rva']+m.start();strings[rv]=text
 if len(strings)>=256:break
code=im.read(im.text['rva'],im.text['size']);refs=[]
for m in re.finditer(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]....',code,re.S):
 rv=im.text['rva']+m.start();target=rv+7+struct.unpack_from('<i',m.group(),3)[0]
 if target not in strings:continue
 refs.append(dict(literal=strings[target],literal_rva=target,instruction_rva=rv,unwind_range_rva=im.function_range(rv),unwind_chain=im.unwind_chain(rv)))
 if len(refs)>=400:break
result=dict(source_kind='STATIC_BINARY',game_build_sha256=im.sha256,strings=[dict(rva=k,literal=v) for k,v in strings.items()],references=refs,limits=dict(domain='C4_TRADE_TRANSACTION_ONLY',string_cap=256,reference_cap=400),elapsed_ms=round((time.monotonic()-start)*1000),native_calls=0,limitations=['UI/event anchors may lead to shared core but are not themselves AI transaction proof','bounded lexical discovery misses functions without names/asserts'])
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'trade_core_anchors.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
selected=[];seen=set()
for r in refs:
 name=r['literal'];rg=r['unwind_range_rva']
 if not rg or tuple(rg) in seen or any(term in name for term in ('Overlay','TextHandler','QueryDb','MYGM_TASKS','FRANCHISE_TRADE_ELEMENT::Get','Menu_')):continue
 seen.add(tuple(rg));selected.append(dict(literal=name,range=rg,primary=r['unwind_chain'][-1]['begin']))
print(json.dumps({'strings':len(strings),'references':len(refs),'elapsed_ms':result['elapsed_ms'],'core_candidates':selected[:60]},indent=2))

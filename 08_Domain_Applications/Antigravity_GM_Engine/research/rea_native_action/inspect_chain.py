import argparse,hashlib,json
from pathlib import Path
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--rva',type=lambda s:int(s,0),required=True);p.add_argument('--out',required=True);a=p.parse_args();im=Image();chain=im.unwind_chain(a.rva)
if not chain:raise ValueError('primary function unwind required')
primary=chain[-1]['begin'];rows=[]
for lo,hi,unwind in im.ranges:
 if not primary<=lo<primary+24576:continue
 c=im.unwind_chain(lo)
 if not c or c[-1]['begin']!=primary:continue
 if hi-primary>24576 or len(rows)>=32:raise ValueError('function fragment scope exceeded')
 rows.append(dict(range_rva=[lo,hi],unwind_chain=c,instructions=im.instruction_rows(lo,hi)))
result=dict(source_kind='STATIC_BINARY',game_build_sha256=im.sha256,primary_entry_rva=primary,fragments=rows,max_span_bytes=24576,max_fragments=32,limitations=['one-byte return/tail epilogues outside pdata may still need bounded explicit inspection'])
path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'primary':primary,'fragments':[r['range_rva'] for r in rows],'instructions':sum(len(r['instructions']) for r in rows)}))

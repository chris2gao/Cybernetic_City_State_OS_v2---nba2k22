import argparse,hashlib,json
from pathlib import Path
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--rva',nargs='+',type=lambda s:int(s,0),required=True);p.add_argument('--out',required=True);p.add_argument('--leaf-window-bytes',type=int,default=0);a=p.parse_args();im=Image();rows=[]
if len(a.rva)>16:raise ValueError('max 16 candidates')
for rv in a.rva:
 rg=im.function_range(rv)
 boundary='PE_UNWIND_RANGE_MAY_BE_FRAGMENT'
 if not rg and 1<=a.leaf_window_bytes<=512:rg=(rv,rv+a.leaf_window_bytes);boundary='EXPLICIT_WINDOW_NO_UNWIND_FUNCTION_EXTENT_UNKNOWN'
 if not rg or rg[1]-rg[0]>8192:raise ValueError('bounded unwind range unavailable; select an explicit <=512-byte leaf window if appropriate')
 lo,hi=rg;body=im.read(lo,hi-lo)
 chain=im.unwind_chain(rv)
 parent=chain[-1] if chain else None
 parent_rows=im.instruction_rows(parent['begin'],parent['end']) if parent and parent['begin']!=lo and parent['end']-parent['begin']<=8192 else []
 rows.append(dict(requested_rva=rv,unwind_range_rva=list(rg),boundary_evidence=boundary,unwind_chain=chain,chained_primary_instructions=parent_rows,body_sha256=hashlib.sha256(body).hexdigest(),instructions=im.instruction_rows(lo,hi),status='STATIC_FRAGMENT_REQUIRES_CONTEXT_AND_ABI_VERIFICATION'))
result=dict(game_build_sha256=im.sha256,source_kind='STATIC_BINARY',functions=rows)
path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'functions':[{'range':r['unwind_range_rva'],'instructions':len(r['instructions'])} for r in rows],'output':str(path)}))

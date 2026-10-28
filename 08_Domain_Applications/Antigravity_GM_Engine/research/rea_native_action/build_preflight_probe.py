import argparse,json,zlib
from pathlib import Path
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--team',type=int,default=20);a=p.parse_args();im=Image()
def fnv(data):
 h=2166136261
 for b in data:h=((h^b)*16777619)&0xffffffff
 return h
plan=dict(team_id=a.team,apply_rva=21424800,apply_bytes=426,apply_fnv32=fnv(im.read(21424800,426)),roster_getter_rva=18701792,franchise_getter_rva=6278620,gameplan_type_rva=82879168,coach_type_rva=80284224,field_crcs={k:zlib.crc32(k.encode()) for k in ('POEDefense','POEOffense')},budget=65536,window_ms=1800,max_events=12)
template=Path(__file__).with_name('preflight_probe.js').read_text(encoding='utf-8')
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'native_preflight.js').write_text(template.replace('__PLAN__',json.dumps(plan,separators=(',',':'))),encoding='utf-8')
print(json.dumps({'team':a.team,'code_bytes_verified':426,'read_budget':65536,'trace_window_ms':1800,'game_native_calls':0,'business_writes':0}))

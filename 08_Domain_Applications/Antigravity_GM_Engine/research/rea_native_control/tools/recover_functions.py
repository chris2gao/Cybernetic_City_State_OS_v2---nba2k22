"""Recover bounded chained unwind fragments; never open the running process."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'rea_native_action'))
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--rva',nargs='+',type=lambda s:int(s,0),required=True);p.add_argument('--out',required=True);a=p.parse_args();im=Image();result=[]
if len(a.rva)>32:raise ValueError('32 selected functions per batch')
for requested in a.rva:
 chain=im.unwind_chain(requested)
 if not chain:
  result.append({'requested_rva':requested,'status':'NO_UNWIND_ENTRY_EXTENT_UNKNOWN'});continue
 primary=chain[-1]['begin'];fragments=[]
 for lo,hi,uw in im.ranges:
  if not primary<=lo<primary+24576:continue
  c=im.unwind_chain(lo)
  if c and c[-1]['begin']==primary:
   if hi-primary>24576 or len(fragments)>=32:raise ValueError('Function extent exceeds selected bound')
   fragments.append({'range_rva':[lo,hi],'instructions':im.instruction_rows(lo,hi)})
 end=max(f['range_rva'][1] for f in fragments);body=im.read(primary,end-primary)
 result.append({'requested_rva':requested,'entry_rva':primary,'span_bytes':end-primary,'body_sha256':hashlib.sha256(body).hexdigest(),'fragments':fragments,'status':'STATIC_BODY_UNTESTED','caution':'Jump-table bytes after RET may be present in pdata extents; do not treat every decoded byte as executable control flow'})
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'source_kind':'PINNED_PC22_STATIC_ONLY','game_build_sha256':im.sha256,'functions':result,'game_access':False},indent=2),encoding='utf-8');print(json.dumps({'functions':[{'entry':r.get('entry_rva',r['requested_rva']),'bytes':r.get('span_bytes'),'fragments':len(r.get('fragments',[]))} for r in result]}))

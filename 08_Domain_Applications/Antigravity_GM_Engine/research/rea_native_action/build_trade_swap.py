"""Prepare the authorized, single native swap; never attach during generation."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();root=Path(__file__).parent;out=Path(a.out);im=Image()
subprocess.run([sys.executable,'-B','-X','utf8',str(root/'build_trade_observe.py'),'--out',str(out)],check=True,capture_output=True)
prefix=(out/'trade_observe.js').read_text(encoding='utf-8').split("send({kind:'native-trade-roster-observation'")[0].replace('"read_budget":262144','"read_budget":1048576')
def fnv(b):
 h=2166136261
 for v in b:h=((h^v)*16777619)&0xffffffff
 return h
signatures=[{'rva':r,'bytes':n,'fnv32':fnv(im.read(r,n))} for r,n in [(19786784,494),(19843376,688),(19798016,1965),(19829680,8192),(19837872,228),(20101184,891)]]
source=prefix+'\nplan.native_signatures='+json.dumps(signatures)+';\n'+(root/'gui_thread_bridge.js').read_text(encoding='utf-8')+'\n'+(root/'trade_swap.js').read_text(encoding='utf-8');path=out/'trade_swap.js'
if path.exists():raise FileExistsError('Fresh exact-script package required')
path.write_text(source,encoding='utf-8');print(json.dumps({'script_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_call_budget':4,'game_commit_call_budget':1,'commit_rva':20101184,'scope':'MIL Nwora9842 -> WAS; WAS Gill9879 -> MIL; retain; no save/date/controller writes'}))

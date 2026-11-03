import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();root=Path(__file__).parent;out=Path(a.out);im=Image()
def fnv(data):
 h=2166136261
 for b in data:h=((h^b)*16777619)&0xffffffff
 return h
subprocess.run([sys.executable,'-B','-X','utf8',str(root/'build_trade_observe.py'),'--out',str(out)],check=True,capture_output=True)
prefix=(out/'trade_observe.js').read_text(encoding='utf-8').split("send({kind:'native-trade-roster-observation'")[0]
signatures=[{'rva':19786784,'bytes':494,'fnv32':fnv(im.read(19786784,494))},{'rva':19843376,'bytes':688,'fnv32':fnv(im.read(19843376,688))}]
source=prefix+'\nplan.native_signatures='+json.dumps(signatures)+';\n'+(root/'gui_thread_bridge.js').read_text(encoding='utf-8')+'\n'+(root/'trade_builder_probe.js').read_text(encoding='utf-8')
path=out/'trade_builder_probe.js';path.write_text(source,encoding='utf-8');print(json.dumps({'script_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_call_budget':3,'game_commit_calls':0,'players':['MIL Jordan Nwora','WAS Anthony Gill'],'status':'PREPARED_NOT_EXECUTED'}))

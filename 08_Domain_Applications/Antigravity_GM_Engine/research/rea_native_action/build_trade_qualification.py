"""Build a four-call private proposal/full native legality check, without commit."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();root=Path(__file__).parent;out=Path(a.out)
subprocess.run([sys.executable,'-B','-X','utf8',str(root/'build_trade_builder_probe.py'),'--out',str(out)],check=True,capture_output=True)
s=(out/'trade_builder_probe.js').read_text(encoding='utf-8')
s=s.replace("experiment_id:'EXP-NATIVE-TRADE-BUILD-01'","experiment_id:'EXP-NATIVE-TRADE-QUALIFY-01'")
insert="""
 const active=pointer(read(base.add(0x11c1ad0+7+0x51699c1),8)),activeMode=u32(read(active.add(0x150),4));
 if(!activeMode)throw Error('NATIVE_WRAPPER_LOCAL_MODE_NOT_ACTIVE');
 const franchise=pointer(read(base.add(0x12e945b+7+0x5042016),8));
 if(!u32(read(franchise.add(8),4))||u32(read(franchise.add(0xac),4)))throw Error('NATIVE_TRANSACTION_LIFECYCLE_NOT_READY');
 const ctx=getter(0xbaa7e0),out=Memory.alloc(4);out.writeU32(0);
 if(ctx.isNull())throw Error('NATIVE_CONTEXT_NULL');
 const check=new NativeFunction(base.add(19798016),'int',['pointer','int','pointer','int','int','pointer'],{abi:'win64',exceptions:'steal'});
 preview.native_calls++;preview.full_native_legality_result=check(proposal,0,ctx,1,0,out);preview.native_output_code=out.readU32();preview.local_game_delegate_mode=activeMode;
"""
s=s.replace("preview.native_validate_result=valid;","preview.native_validate_result=valid;"+insert)
s=s.replace("valid===1&&preview.canaries_intact&&preview.game_objects_unchanged?'PRIVATE_NATIVE_PROPOSAL_ABI_AND_VALIDATE_VERIFIED'","valid===1&&preview.full_native_legality_result===1&&preview.canaries_intact&&preview.game_objects_unchanged?'PRIVATE_NATIVE_FULL_LEGALITY_VERIFIED'")
im=Image();h=2166136261
for b in im.read(19798016,1965):h=((h^b)*16777619)&0xffffffff
s=s.replace('const preview=',f'if(fingerprint(read(base.add(19798016),1965))!=={h})throw Error("CHECK_CODE_CHANGED");\nconst preview=')
path=out/'trade_qualify.js';path.write_text(s,encoding='utf-8');print(json.dumps({'script_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_call_budget':4,'game_commit_calls':0}))

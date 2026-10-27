import argparse,json
from native_action import NativeActionSpec,Status
from invoker import NativeActionInvoker
p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
s=sub.add_parser('preflight');s.add_argument('--offline',action='store_true',required=True)
s=sub.add_parser('invoke');s.add_argument('--script',required=True);s.add_argument('--approval',required=True);s.add_argument('--output',required=True)
a=p.parse_args()
if a.command=='preflight':print(json.dumps({'status':Status.CANDIDATE_ONLY,'spec':NativeActionSpec().to_dict(),'real_native_call_executed':False,'next':'build_preflight_probe.py for current read-only instance; build_invoker.py for exact bounded review; invoke only with Human-approved script receipt'},indent=2))
else:
 result=NativeActionInvoker(a.script,a.approval).execute(a.output);print(json.dumps(result,indent=2))
 if result['receipt']['status']!='REAL_GAME_EFFECT_VERIFIED':raise SystemExit(1)

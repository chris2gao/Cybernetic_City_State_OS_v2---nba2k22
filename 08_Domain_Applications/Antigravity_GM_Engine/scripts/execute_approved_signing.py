"""Execution-only signing candidate. NOT RUN / NOT TESTED; writes disabled.

GM supplies a final player/team/contract. This contains no offer simulation.
--inspect-unvalidated permits a future player-triggered read-only field plan;
it cannot enable writes or grant game approval.
"""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import approved_signing_executor as signing
from approved_trade_executor import dump,now


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',required=True,type=Path)
    parser.add_argument('--phase',choices=('plan','execute','verify'),default='plan')
    parser.add_argument('--inspect-unvalidated',action='store_true')
    parser.add_argument('--approve-game-writes',action='store_true')
    args=parser.parse_args()
    if args.approve_game_writes!=(args.phase=='execute'):
        parser.error('Explicit game-write approval required for execute only')
    if args.phase=='execute' and (not signing.SIGNING_LAYOUT_VALIDATED or not signing.SIGNING_EXECUTION_ENABLED):
        parser.error('Signing is deferred pending technical validation; no game handle opened')
    if args.inspect_unvalidated and args.phase!='plan':
        parser.error('Unvalidated inspection is read-only plan mode only')
    if not signing.SIGNING_LAYOUT_VALIDATED and not args.inspect_unvalidated:
        parser.error('Await the player signing task; only an explicitly requested read-only inspection can run before validation')
    request=json.loads(args.request.read_text(encoding='utf-8-sig'))
    if request.get('example_only'):
        raise ValueError('Example template cannot be applied')
    for field in ('save_id','action_id'):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',request[field]):
            raise ValueError('Invalid '+field)
    if not re.fullmatch(r'20\d{2}-20\d{2}',request['season']):
        raise ValueError('Explicit target season required')
    output=ROOT/'_exports/execution'/request['save_id']/request['action_id']
    output.mkdir(parents=True,exist_ok=True)
    # Import a real-process module only after the mode and technical gates passed.
    from memory import GameMemory
    with GameMemory(read_only=True) as mem:
        if args.phase=='verify':
            plan=json.loads((output/'plan.json').read_text(encoding='utf-8'))
            capture_request={**request,'player':plan['player_identity']}
            context=signing.capture_signing_context(mem,capture_request,allow_already_target=True)
            if context['process']!=plan['process']:
                raise ValueError('Process changed; old signing addresses cannot be reused')
            result=signing.verify_signing_plan(mem,plan)
            dump(output/'subsequent_readback.json',result)
            print(json.dumps({'status':'READBACK_VERIFIED' if result['verified'] else 'READBACK_FAILED'}))
            return
        context=signing.capture_signing_context(mem,request,allow_already_target=True)
        plan=signing.build_signing_plan(context,request)
    if args.phase=='plan':
        dump(output/'request.json',request)
        dump(output/'context.json',context)
        dump(output/'plan.json',plan)
        print(json.dumps({'status':plan['status'],'game_writes':0,'output':str(output)}))
        return
    if (output/'WRITE_ATTEMPTED').exists():
        raise ValueError('A signing write was already attempted; inspect, never replay')
    original_request=json.loads((output/'request.json').read_text(encoding='utf-8'))
    original_plan=json.loads((output/'plan.json').read_text(encoding='utf-8'))
    if original_request!=request or original_plan['player_identity']!=plan['player_identity']:
        raise ValueError('Approved request or pinned model identity changed')
    with GameMemory(read_only=False) as mem:
        current_context=signing.capture_signing_context(mem,request,allow_already_target=True)
        if current_context!=context:
            raise ValueError('Signing objects changed between read-only and write handles')
        receipt=signing.execute_signing_plan(mem,plan,output,human_approval_confirmed=True)
    print(json.dumps({'status':receipt['status'],'write_calls':receipt['write_calls']}))


if __name__=='__main__':
    main()

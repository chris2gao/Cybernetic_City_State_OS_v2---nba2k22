"""Deferred approved-signing plan preparation; no game connection or writes.

Without a machine-captured context this records the approved offer and the live
validation gaps. Context-based plans remain unvalidated; live execution is disabled.
"""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from approved_signing_executor import VERSION,contract_values,build_signing_plan
from approved_trade_executor import dump,now


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',type=Path,required=True)
    parser.add_argument('--context',type=Path)
    parser.add_argument('--approve-game-writes',action='store_true')
    args=parser.parse_args()
    if args.approve_game_writes:
        parser.error('Signing execution is deferred; this preparation CLI never opens the game')
    request=json.loads(args.request.read_text(encoding='utf-8-sig'))
    if request.get('example_only'):
        raise ValueError('Fill the example with a future specific approved signing first')
    for key in ('save_id','action_id'):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',request[key]):
            raise ValueError('Invalid '+key)
    if args.context:
        context=json.loads(args.context.read_text(encoding='utf-8-sig'))
        plan=build_signing_plan(context,request)
    else:
        plan={'executor_version':VERSION,'created_at':now(),'status':'AWAITING_OFFSEASON_LIVE_CONTEXT',
              'request':request,'validated_integer_contract_values':contract_values(request['contract']),
              'patches':None,'game_writes':0,'source_admission':'NOT_IMPLEMENTED_OR_VALIDATED',
              'note':'No original bytes or player addresses invented; wait for player-triggered signing validation.'}
    output=ROOT/'_exports/execution'/request['save_id']/request['action_id']/'signing_preparation'
    output.mkdir(parents=True,exist_ok=True)
    destination=output/'plan.json'
    if destination.exists():
        old=json.loads(destination.read_text(encoding='utf-8'))
        comparable=lambda p:{k:v for k,v in p.items() if k!='created_at'}
        if comparable(old)!=comparable(plan):
            raise ValueError('Signing preparation already exists with a different version; preserve it and use a new action ID')
    else:
        dump(destination,plan)
    print(json.dumps({'status':plan['status'],'game_writes':0,'output':str(destination)},ensure_ascii=False))


if __name__=='__main__':
    main()

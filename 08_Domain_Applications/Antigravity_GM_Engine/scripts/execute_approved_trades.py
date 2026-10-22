"""Player-approved trades: live plan -> explicit execute -> independent verify.

Names and team abbreviations suffice when uniquely resolvable. Plan pins observed
face/DOB/contracts. Never saves a game, advances time, or calculates/syncs finances.
"""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from memory import GameMemory
from approved_trade_executor import observe,build_plan,execute_plan,verify_plan,dump,now,VERSION,EXECUTION_ENABLED
from trade_request import metadata,normalize


def contextualize(plan,request):
    return {**plan,'save_id':request['save_id'],'game_date':request.get('game_date'),
            'approval_basis':request['approval_basis'],'source_batch':request['source_batch'],
            'source_commit':request['source_commit'],'policy_id':request['policy_id']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',required=True,type=Path)
    parser.add_argument('--phase',choices=('plan','execute','verify'),default='plan')
    parser.add_argument('--approve-game-writes',action='store_true')
    args=parser.parse_args()
    if args.approve_game_writes!=(args.phase=='execute'):
        parser.error('--approve-game-writes is required for execute and forbidden for other phases')
    if args.phase=='execute' and not EXECUTION_ENABLED:
        parser.error('Execution disabled; no game handle opened')
    original=json.loads(args.request.read_text(encoding='utf-8-sig'))
    meta=metadata(original,args.request.stem)
    output=(ROOT/meta['output']).resolve()
    if not output.is_relative_to((ROOT/'_exports/execution').resolve()):
        raise ValueError('Evidence must stay inside _exports/execution')
    policy=json.loads((ROOT/'config/gameplay_policy.json').read_text(encoding='utf-8'))
    if meta['policy_id'] and meta['policy_id']!=policy['policy_id']:
        raise ValueError('Rules changed since the concrete request')
    pinned_path=output/'resolved_request.json'
    request=None
    if args.phase in ('execute','verify') and pinned_path.is_file():
        pin=json.loads(pinned_path.read_text(encoding='utf-8'))
        if pin['input_request']!=original:
            raise ValueError('Request changed after plan; generate a fresh plan for the changed scope')
        request=pin['resolved_request']
        if request['policy_id']!=policy['policy_id']:
            raise ValueError('Pinned plan uses a different rule version')
    elif args.phase=='execute':
        raise ValueError('Run --phase plan first; execute requires pinned live identities')
    output.mkdir(parents=True,exist_ok=True)
    summary={'executor_version':VERSION,'phase':args.phase,'started_at':now(),
             'status':'PRECONDITION_FAILED','game_write_calls':0,'save_id':meta['save_id'],
             'game_date':meta['game_date'],'save_identity':'PLAYER_SELECTED_NOT_AUTOMATIC_ID',
             'database':'NOT_SYNCED','persistence':'PERSISTENCE_NOT_VERIFIED','actions':[]}
    logs=io.StringIO()
    try:
        with contextlib.redirect_stdout(logs),GameMemory(read_only=True) as mem:
            state=observe(mem,meta['season_year'])
            if request is None:
                request=normalize(original,state,mem,args.request.stem)
                request['policy_id']=policy['policy_id']
            if original.get('expected_pid') is not None and original['expected_pid']!=state['pid']:
                raise ValueError('Current process differs from requested PID')
            summary.update(source_batch=request['source_batch'],source_commit=request['source_commit'],
                           approval_basis=request['approval_basis'])
            actions=request['actions']
            for action in actions:
                if args.phase!='verify' and (output/action['action_id']/'WRITE_ATTEMPTED').exists():
                    raise RuntimeError('Prior write attempt exists; use verify, never replay')
            if args.phase=='verify':
                for action in actions:
                    folder=output/action['action_id']
                    plan=json.loads((folder/'plan.json').read_text(encoding='utf-8'))
                    if any(plan['process'][k]!=state[k] for k in ('pid','module_base','creation_time','root')):
                        raise RuntimeError('Old addresses cannot be reused after restart; re-identify in a new read-only request')
                    result=verify_plan(mem,plan,state)
                    dump(folder/'subsequent_readback.json',result)
                    summary['actions'].append({'action_id':action['action_id'],
                        'status':'EXECUTED_VERIFIED' if result['verified'] else 'PARTIALLY_APPLIED',
                        'verification':result})
                summary['status']='VERIFIED' if all(a['status']=='EXECUTED_VERIFIED' for a in summary['actions']) else 'VERIFICATION_FAILED'
            else:
                plans=[contextualize(build_plan(mem,state,a),request) for a in actions]
                if args.phase=='plan':
                    dump(pinned_path,{'input_request':original,'resolved_request':request,'planned_at':now()})
                for plan in plans:
                    folder=output/plan['action_id']
                    folder.mkdir(parents=True,exist_ok=True)
                    dump(folder/'plan.json',plan)
                summary['actions']=[{'action_id':p['action_id'],'status':p['status'],
                                     'planned_write_calls':len(p['patches'])} for p in plans]
                summary['status']='PLANNED'
        if args.phase=='execute':
            with contextlib.redirect_stdout(logs),GameMemory(read_only=False) as mem:
                live=observe(mem,meta['season_year'])
                if any(live[k]!=state[k] for k in ('pid','module_base','creation_time','root')):
                    raise RuntimeError('Process/roster changed after preflight')
                plans=[contextualize(build_plan(mem,live,a),request) for a in actions]
                summary['actions']=[]
                for index,plan in enumerate(plans):
                    receipt=execute_plan(mem,plan,live,output/plan['action_id'],human_approval_confirmed=True)
                    receipt.update(approval_basis=request['approval_basis'] or 'Operator explicitly invoked --approve-game-writes for this request',
                                   source_batch=request['source_batch'],source_commit=request['source_commit'])
                    dump(output/plan['action_id']/'receipt.json',receipt)
                    summary['game_write_calls']+=receipt['write_calls']
                    summary['actions'].append(receipt)
                    dump(output/'execute_summary.json',summary)
                    if receipt['status'] not in ('EXECUTED_VERIFIED','NO_WRITE_NEEDED'):
                        break
                    if index+1<len(plans):
                        refreshed=observe(mem,meta['season_year'])
                        if any(refreshed[k]!=state[k] for k in ('pid','module_base','creation_time','root')):
                            raise RuntimeError('Roster directory changed between transactions')
                        live=refreshed
                summary['status']=('EXECUTED_VERIFIED' if len(summary['actions'])==len(actions) and
                    all(a['status'] in ('EXECUTED_VERIFIED','NO_WRITE_NEEDED') for a in summary['actions']) else 'PARTIALLY_APPLIED')
    except Exception as exc:
        summary['error']=f'{type(exc).__name__}: {exc}'
        summary['error_cause']=str(exc.__cause__) if exc.__cause__ else None
        if summary['game_write_calls']:
            summary['status']='PARTIALLY_APPLIED'
        (output/f'{args.phase}_error.txt').write_text(traceback.format_exc(),encoding='utf-8')
    summary['completed_at']=now()
    (output/f'{args.phase}.log').write_text(logs.getvalue(),encoding='utf-8')
    dump(output/f'{args.phase}_summary.json',summary)
    print(json.dumps({k:summary.get(k) for k in ('phase','status','game_write_calls','error','error_cause')},ensure_ascii=False))
    for action in summary['actions']:
        print(json.dumps({'action_id':action['action_id'],'status':action['status'],
                          'planned_write_calls':action.get('planned_write_calls'),'write_calls':action.get('write_calls'),
                          'verified':action.get('verification',{}).get('verified'),'error':action.get('error')},ensure_ascii=False))
    return 0 if summary['status'] in ('PLANNED','EXECUTED_VERIFIED','VERIFIED') else 1


if __name__=='__main__':
    sys.exit(main())

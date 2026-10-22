"""W02 incident repair: verify approved ownership, fix only 3 evidenced count bytes.

This is not a transaction replay. No player, pick, salary, finance, lineup pointer,
strategy, date, save, or database writes are performed by this repair.
"""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from memory import GameMemory
from approved_trade_executor import observe, build_plan, verify_plan, dump, now, read_exact
from roster_associations import describe, active_count_byte, verify_code


def prepare(mem,request):
    verify_code(mem)
    state=observe(mem)
    if set(a['action_id'] for a in request['actions']) != {'GM-W02-A01','GM-W02-R02-A01'}:
        raise ValueError('Only the two incident actions are supported')
    if request['save_id']!='mc_haliburton_2021' or request['season']!='2021-2022':
        raise ValueError('Wrong selected save/season')
    plans=[build_plan(mem,state,a,allow_count_repair=True) for a in request['actions']]
    if any(p['status']!='NO_WRITE_NEEDED' for p in plans):
        raise ValueError('Approved transfers are not all at target; count-only repair is not applicable')
    counts={tid:describe(raw) for tid,raw in state['team_raw'].items()}
    import struct
    diagnostic=[]
    for tid,description in counts.items():
        if description['valid']:
            continue
        raw=state['team_raw'][tid]
        members=list(struct.unpack_from('<25Q',raw))
        active=list(struct.unpack_from('<13Q',raw,0xd0))
        diagnostic.append({'team_id':tid,**description,
            'active_nonregular': [{'pointer':hex(p),'roster_slot':members.index(p) if p in members else None}
                                 for p in active if p and p not in members[:15]]})
    diagnostic_dir=(ROOT/request['output']).resolve()/'count_repair_v1'
    dump(diagnostic_dir/'preflight_diagnostic.json',diagnostic)
    allowed={(3,'regular_count_matches'),(21,'regular_count_matches'),(3,'active_count_matches')}
    for tid,description in counts.items():
        for key,value in description['checks'].items():
            if not value and (tid,key) not in allowed:
                raise ValueError(f'Unexpected roster anomaly {tid}/{key}')
    if (counts[3]['regular_count'],counts[21]['regular_count'],counts[3]['active_count'])!=(14,15,12):
        raise ValueError('Current roster differs from the evidenced incident')
    changes=[]
    for tid,offset,goal,allowed_original in (
        (3,0xcb1,14,(15,14)),(21,0xcb1,15,(14,15)),
        (3,0x1047,active_count_byte(state['team_raw'][3][0x1047],12),(0xd1,0xc1))):
        original=state['team_raw'][tid][offset]
        if original not in allowed_original:
            raise ValueError('Count original changed unexpectedly')
        if original!=goal:
            changes.append({'team_id':tid,'offset':offset,'address':state['teams'][tid]['address']+offset,
                            'before':bytes([original]).hex(),'after':bytes([goal]).hex()})
    return state,plans,counts,changes


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',required=True,type=Path)
    parser.add_argument('--approve-game-writes',action='store_true')
    args=parser.parse_args()
    request=json.loads(args.request.read_text(encoding='utf-8-sig'))
    folder=(ROOT/request['output']).resolve()/'count_repair_v1'
    if not folder.is_relative_to((ROOT/'_exports/execution').resolve()):
        raise ValueError('Repair evidence path leaves local execution tree')
    folder.mkdir(parents=True,exist_ok=True)
    attempt=folder/'WRITE_ATTEMPTED'
    if args.approve_game_writes and attempt.exists():
        raise RuntimeError('Repair previously attempted; preserve evidence and inspect only')
    report={'started_at':now(),'status':'PRECONDITION_FAILED','write_calls':0,'journal':[],
            'scope':'THREE_COUNT_BYTES_ONLY_NO_TRADE_REPLAY','database':'NOT_SYNCED',
            'persistence':'NOT_SAVED_BY_THIS_SCRIPT','player_ui_validation':'PENDING',
            'approval_basis':request['approval_basis']}
    logs=io.StringIO()
    phase='execute' if args.approve_game_writes else 'plan'
    try:
        with contextlib.redirect_stdout(logs),GameMemory(read_only=True) as mem:
            state,plans,counts,changes=prepare(mem,request)
        report['process']={k:state[k] for k in ('pid','module_base','creation_time','root')}
        report['before_counts']=counts
        report['patches']=changes
        report['status']='PLANNED' if changes else 'NO_WRITE_NEEDED'
        dump(folder/f'{phase}_receipt.json',report)
        if args.approve_game_writes and changes:
            with contextlib.redirect_stdout(logs),GameMemory(read_only=False) as mem:
                live,plans,counts,actual_changes=prepare(mem,request)
                if any(live[k]!=state[k] for k in ('pid','module_base','creation_time','root')) or actual_changes!=changes:
                    raise RuntimeError('Process or count originals changed')
                # Retain full local before evidence for this new process. No old pointers replayed.
                dump(folder/'before.json',{'process':report['process'],
                    'teams':{str(t):raw.hex() for t,raw in live['team_raw'].items()},
                    'players':[{k:p[k] for k in ('name','address','raw_before')} for plan in plans for p in plan['players']],
                    'picks':[{k:p[k] for k in ('year','round','address','raw_before')} for plan in plans for p in plan['picks']]})
                for item in changes:
                    original=read_exact(mem,item['address'],1)
                    if original.hex()!=item['before']:
                        raise RuntimeError('Repair compare-before failed')
                    step={**item,'status':'WRITE_RESULT_UNKNOWN'}
                    report['journal'].append(step)
                    report['status']='WRITE_RESULT_UNKNOWN'
                    attempt.touch(exist_ok=True)
                    dump(folder/'execute_receipt.json',report)
                    report['write_calls']+=1
                    result=mem.write_bytes(item['address'],bytes.fromhex(item['after']))
                    actual=mem.read_bytes(item['address'],1)
                    step['readback']=actual.hex() if actual else None
                    step['api_success']=result
                    if not result or actual is None or actual.hex()!=item['after']:
                        raise OSError('Repair write/readback failed; stop, no retry')
                    step['status']='READBACK_MATCHED'
                    dump(folder/'execute_receipt.json',report)
                after=observe(mem)
                verify_code(mem)
                # Ensure no player, pick or pointer array changed during this count-only repair.
                checks={}
                for tid,old in live['team_raw'].items():
                    current=bytearray(after['team_raw'][tid])
                    expected=bytearray(old)
                    for item in changes:
                        if item['team_id']==tid:
                            expected[item['offset']]=int(item['after'],16)
                    checks[f'team_{tid}_only_approved_bytes']=current==expected
                    checks[f'team_{tid}_roster_counts']=describe(bytes(current))['valid']
                checks['approved_transactions_unchanged']=all(verify_plan(mem,plan,live)['verified'] for plan in plans)
                report['after_counts']={tid:describe(raw) for tid,raw in after['team_raw'].items()}
                report['checks']=checks
                report['status']='REPAIR_MEMORY_VERIFIED_UI_PENDING' if all(checks.values()) else 'PARTIALLY_APPLIED'
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'
        report['error_cause']=str(exc.__cause__) if exc.__cause__ else None
        if report['write_calls']:
            report['status']='PARTIALLY_APPLIED' if any(x['status']=='READBACK_MATCHED' for x in report['journal']) else 'WRITE_RESULT_UNKNOWN'
        (folder/f'{phase}_error.txt').write_text(traceback.format_exc(),encoding='utf-8')
    report['completed_at']=now()
    dump(folder/f'{phase}_receipt.json',report)
    (folder/f'{phase}.log').write_text(logs.getvalue(),encoding='utf-8')
    print(json.dumps({k:report.get(k) for k in ('status','write_calls','patches','error','error_cause')},ensure_ascii=False))
    return 0 if report['status'] in ('PLANNED','NO_WRITE_NEEDED','REPAIR_MEMORY_VERIFIED_UI_PENDING') else 1


if __name__=='__main__':
    sys.exit(main())

"""Local coaching batch CLI. Default mode is entirely offline."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from coaching_cli import export_path,write_json
from gm_core.coaching_batch import propose_batch
from gm_core.data_reader import attach_coaching_opponents
from coaching_batch_executor import CoachingBatchExecutor,BatchApproval


def main():
    parser=argparse.ArgumentParser(description='1–30 team approval-bound coaching batch; default offline dry-run')
    parser.add_argument('--snapshot',required=True)
    parser.add_argument('--opponent-source',action='append',default=[],help='Optional same-batch per-team opponent file; no automatic 870-record load')
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--batch')
    source.add_argument('--requests',help='JSON list of default requests or {requests,hold_team_ids}')
    parser.add_argument('--batch-id')
    parser.add_argument('--decision-id')
    parser.add_argument('--version',type=int)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--preflight',action='store_true',help='Read-only live validation of all targets; no RW handle')
    mode.add_argument('--execute',action='store_true')
    mode.add_argument('--rollback',action='store_true')
    for key in ('career-id','batch-id','decision-id','plan-digest'):
        parser.add_argument('--approve-'+key)
    parser.add_argument('--approve-version',type=int)
    parser.add_argument('--approve-action-id',action='append',default=[])
    parser.add_argument('--coach-editor-closed',action='store_true')
    parser.add_argument('--test-save-confirmed',action='store_true')
    parser.add_argument('--state-root',default='_exports/coaching_batch_execution')
    parser.add_argument('--output',help='Result JSON under this repository _exports')
    parser.add_argument('--proposal-output',help='Generated batch JSON under _exports')
    args=parser.parse_args()
    snapshot=json.loads(Path(args.snapshot).read_text(encoding='utf-8'))
    for path in args.opponent_source:
        opponent=json.loads(Path(path).read_text(encoding='utf-8'))
        try:attach_coaching_opponents(snapshot,opponent)
        except (ValueError,KeyError,TypeError) as exc:parser.error(str(exc))
    if args.batch:
        batch=json.loads(Path(args.batch).read_text(encoding='utf-8'))
    else:
        if not all((args.batch_id,args.decision_id,args.version)):
            parser.error('--requests requires --batch-id --decision-id --version')
        request=json.loads(Path(args.requests).read_text(encoding='utf-8'))
        batch=propose_batch(snapshot,request if isinstance(request,list) else request['requests'],
            args.batch_id,args.decision_id,args.version,() if isinstance(request,list) else request.get('hold_team_ids',()))
    executor=CoachingBatchExecutor()
    if args.execute or args.rollback:
        approval=BatchApproval(args.approve_career_id,args.approve_batch_id,args.approve_decision_id,
            args.approve_version,tuple(args.approve_action_id),args.approve_plan_digest,
            args.coach_editor_closed,args.test_save_confirmed)
        result=executor.run(batch,snapshot,approval,export_path(args.state_root),args.rollback)
    elif args.preflight:
        result=executor.preflight(batch,snapshot)
    else:
        result=executor.inspect(batch,snapshot)
    if args.proposal_output:
        write_json(args.proposal_output,batch)
    rendered=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:write_json(args.output,result)
    print(rendered,end='')
    return 1 if result.get('valid') is False else 0


if __name__=='__main__':raise SystemExit(main())

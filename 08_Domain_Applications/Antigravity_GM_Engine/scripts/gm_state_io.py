"""DEV14 deterministic native state and save lifecycle CLI. No implicit shared save."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gm_state_io.common import load, binding, canonical
from gm_state_io.registry import Registry
from gm_state_io.workspace import Workspaces, lifecycle_lock


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    r=sub.add_parser('registry')
    r.add_argument('--domain')
    r.add_argument('--limit',type=int,default=20)
    r.add_argument('--offset',type=int,default=0)
    s=sub.add_parser('save')
    s.add_argument('action',choices=('list','status','create','adopt','activate','deactivate','retire','reset','recover','recover-capture'))
    s.add_argument('--save-id')
    s.add_argument('--dry-run',action='store_true')
    s.add_argument('--generation')
    s.add_argument('--confirm-manifest')
    s.add_argument('--confirm-existing-save')
    st=sub.add_parser('stage')
    st.add_argument('--career',required=True)
    st.add_argument('--source-batch',required=True)
    st.add_argument('--proposal',type=Path,required=True)
    st.add_argument('--query-root',type=Path,default=ROOT/'database/query_snapshots')
    st.add_argument('--published-root',type=Path,default=ROOT/'published')
    for name in ('validate','preflight','apply','rollback','receipt'):
        x=sub.add_parser(name)
        x.add_argument('--career',required=True)
        x.add_argument('--change-set',required=True)
        if name in ('apply','rollback'):
            x.add_argument('--approval',type=Path,required=True,help='Exact approved binding/digest/action list; file alone grants no authority')
            x.add_argument('--approve-game-writes',action='store_true')
            x.add_argument('--player-approval-reference',required=True)
            x.add_argument('--loaded-save-confirmation',required=True,help='save_id:save_instance_id:generation_id explicitly confirmed by player')
            x.add_argument('--editors-closed',action='store_true')
    re=sub.add_parser('reconcile')
    re.add_argument('--career',required=True)
    re.add_argument('--batch',required=True)
    review=sub.add_parser('review',help='Human-operated foreground review and supervised execution; no portable approval token')
    review.add_argument('--career',required=True)
    review.add_argument('--change-set',required=True)
    review.add_argument('--operation',choices=('apply','rollback'),default='apply')
    ca=sub.add_parser('capture')
    ca.add_argument('--career',required=True)
    ca.add_argument('--approve-capture',action='store_true')
    ca.add_argument('--approve-publish',action='store_true')
    ca.add_argument('--loaded-save-confirmation',required=True)
    ca.add_argument('--capture-args',default='[]',help='JSON argument list for existing run_data_update.ps1 only')
    ca.add_argument('--capture-args-base64',help='UTF-8 JSON list encoded for Windows PowerShell native argument transport')
    lease=sub.add_parser('lease-check')
    lease.add_argument('--career',required=True)
    return p


def summary(plan):
    result={k:plan[k] for k in ('change_set_id','save_id','save_instance_id','generation_id','source_batch_id',
                               'decision_id','version','registry_version','status','digest','actions_requested',
                               'actions_effective','unchanged','native_blocks_planned','approval_required')}
    result['diff_preview']=[dict(action_id=a['action_id'],object_key=a['object_key'],selector=a['selector'],
                                 field_key=a['field_key'],before=a['expected_observed_raw'],after=a['target_value'],
                                 reason=a['reason'][:200]) for a in plan['actions'][:20]]
    result['diff_preview_truncated']=len(plan['actions'])>20
    return result


def run(a):
    manager=Workspaces()
    if a.command=='save':
        if a.action=='list':
            return dict(workspaces=manager.list())
        if a.action=='status':
            return manager.read(a.save_id) if a.save_id else manager.active()
        if a.action=='deactivate':
            manager.deactivate()
            return dict(status='INACTIVE_DATA_PRESERVED')
        if not a.save_id:
            raise ValueError('SAVE_ID_REQUIRED')
        if a.action=='create':return manager.create(a.save_id)
        if a.action=='adopt':return manager.adopt(a.save_id,a.confirm_existing_save)
        if a.action=='activate':return manager.activate(a.save_id)
        if a.action=='retire':return manager.retire(a.save_id,a.confirm_manifest)
        if a.action=='reset':
            if a.dry_run:return manager.reset_plan(a.save_id)
            return manager.reset(a.save_id,a.generation,a.confirm_manifest)
        if a.action=='recover':return manager.recover(a.save_id,a.confirm_manifest)
        if a.action=='recover-capture':return manager.recover_capture(a.save_id,a.confirm_manifest)
    if a.command=='lease-check':
        from gm_state_io.lifecycle import verify_lease
        return dict(status='LIFECYCLE_LEASE_VERIFIED',**binding(verify_lease(a.career)))
    if a.command=='capture':
        if not a.approve_capture:
            raise PermissionError('PLAYER_CAPTURE_TRIGGER_REQUIRED')
        if a.capture_args_base64:
            if a.capture_args!='[]':
                raise ValueError('CHOOSE_ONE_CAPTURE_ARGUMENT_ENCODING')
            args=json.loads(base64.b64decode(a.capture_args_base64,validate=True).decode('utf-8'))
        else:
            args=json.loads(a.capture_args)
        allowed={'-GameDate','-GameDateUnknown','-Season','-Month','-Event','-Name','-GamesOnDateComplete','-Validation','-Publish'}
        if not isinstance(args,list) or any(not isinstance(x,str) for x in args):
            raise ValueError('CAPTURE_ARGS_MUST_BE_STRINGS')
        i=0
        switches={'-GameDateUnknown','-GamesOnDateComplete','-Validation','-Publish'}
        while i<len(args):
            if args[i] not in allowed:
                raise ValueError('ONLY_EXISTING_FULL_PIPELINE_PARAMETERS_ALLOWED')
            i+=1 if args[i] in switches else 2
        if '-Publish' in args and not a.approve_publish:
            raise PermissionError('EXPLICIT_PUBLISH_AUTHORIZATION_REQUIRED')
        from gm_state_io.lifecycle import capture_lease
        with capture_lease(a.career,a.loaded_save_confirmation):
            result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/run_data_update.ps1'),'-SaveId',a.career,*args],cwd=ROOT)
            if result.returncode:
                raise RuntimeError('FULL_PIPELINE_FAILED:'+str(result.returncode))
        return dict(status='FULL_PIPELINE_COMPLETED',capture_profile='full_verified_v1')
    registry=Registry()
    if a.command=='registry':
        if not 1<=a.limit<=50 or a.offset<0:
            raise ValueError('REGISTRY_LIMIT_1_50')
        rows=[v for k,v in sorted(registry.fields.items()) if not a.domain or v['domain']==a.domain]
        page=rows[a.offset:a.offset+a.limit]
        while len(page)>1 and len(canonical(page).encode('utf-8'))>18000:
            page.pop()
        next_offset=a.offset+len(page)
        return dict(registry_version=registry.version,total=len(rows),rows=page,next_offset=next_offset if len(rows)>next_offset else None)
    if a.command in ('stage','reconcile'):
        from gm_state_io.capture_bridge import load_audited_source
        manager.active(a.career)
        source=load_audited_source(a.career,a.source_batch if a.command=='stage' else a.batch,
                                   getattr(a,'query_root',None),getattr(a,'published_root',None))
        if a.command=='stage':
            from gm_state_io.plan import stage
            return summary(stage(load(a.proposal),source,registry))
        from gm_state_io.reconcile import reconcile
        return reconcile(source,registry)
    from gm_state_io.plan import load_plan
    with lifecycle_lock():
        plan=load_plan(a.change_set,registry,a.career)
        if a.command=='validate':return dict(summary(plan),mode='OFFLINE_NO_GAME_HANDLES',valid=True)
        from gm_state_io.executor import Executor, ExternalApproval, receipt
        if a.command=='receipt':return receipt(a.change_set)
        executor=Executor(registry)
        if a.command=='preflight':return executor.preflight(plan)
        if a.command=='review':
            from gm_state_io.approval import review, TRUST
            with review(plan,rollback=a.operation=='rollback') as (approval,supervision):
                result=executor.run(plan,approval,rollback=a.operation=='rollback',supervision=supervision)
            return dict(result,approval_state='HUMAN_APPROVED',approval_trust=TRUST)
        # Explicit player acceptance of caller/OS trust: the reference records
        # actual chat approval, not an unforgeable credential. JSON alone is not
        # approval. Do not make the player type into a separate terminal.
        if not a.approve_game_writes:
            raise PermissionError('MODEL_PROVIDED_CLAIM_ONLY_SPECIFIC_PLAYER_TRIGGER_REQUIRED')
        payload=load(a.approval)
        expected={'save_id','save_instance_id','generation_id','source_batch_id','decision_id','version','action_ids','digest'}
        if set(payload)!=expected:
            raise ValueError('EXACT_APPROVAL_BINDING_REQUIRED')
        payload['action_ids']=tuple(payload['action_ids'])
        approval=ExternalApproval(**payload,player_approval_reference=a.player_approval_reference,
            loaded_save_confirmation=a.loaded_save_confirmation,editors_closed=a.editors_closed)
        result=executor.run(plan,approval,rollback=a.command=='rollback')
        return dict(result,approval_state='HUMAN_APPROVED_OPERATOR_ATTESTED',approval_trust='MANUAL_OPERATOR_TRUST_ONLY')


def main():
    try:
        result=run(parser().parse_args())
        print(json.dumps(result,ensure_ascii=False,allow_nan=False))
    except (ValueError,RuntimeError,PermissionError,FileNotFoundError,KeyError) as exc:
        print(json.dumps(dict(status='REFUSED',error=str(exc)),ensure_ascii=False))
        return 2
    return 0


if __name__=='__main__':
    raise SystemExit(main())

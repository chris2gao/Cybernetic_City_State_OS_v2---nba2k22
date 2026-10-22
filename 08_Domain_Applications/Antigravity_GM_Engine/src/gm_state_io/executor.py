"""Approval-bound generic block transaction, reusing the coaching process lock.

RO preflight of the whole batch precedes RW. All preimages are durable before
the first write. Failed operations conditionally restore only their own bytes.
"""
from dataclasses import dataclass
import json
from pathlib import Path
from uuid import uuid4
import save_context
from .common import atomic_json, binding, canonical, now
from .plan import load_plan
from .store import connect
from .workspace import Workspaces, lifecycle_lock


@dataclass(frozen=True)
class ExternalApproval:
    save_id: str
    save_instance_id: str
    generation_id: str
    source_batch_id: str
    decision_id: str
    version: int
    action_ids: tuple
    digest: str
    player_approval_reference: str
    loaded_save_confirmation: str
    editors_closed: bool = False


def require_approval(plan, approval):
    keys=('save_id','save_instance_id','generation_id','source_batch_id','decision_id','version','digest')
    if (type(approval) is not ExternalApproval or type(approval.version) is not int
        or any(getattr(approval,k)!=plan[k] for k in keys)
        or len(approval.action_ids)!=len(set(approval.action_ids))
        or set(approval.action_ids)!={a['action_id'] for a in plan['actions']}
        or not approval.player_approval_reference.strip() or approval.editors_closed is not True):
        raise PermissionError('SPECIFIC_EXTERNAL_PLAYER_APPROVAL_REQUIRED')
    # The game currently has no independently certified unique career-ID reader.
    expected=plan['save_id']+':'+plan['save_instance_id']+':'+plan['generation_id']
    if approval.loaded_save_confirmation != expected:
        raise PermissionError('GAME_SAVE_BINDING_UNVERIFIED_EXPLICIT_LOADED_SAVE_CONFIRMATION_REQUIRED')


def merge_physical(resolved):
    groups={}
    occupied={}
    for b, at in resolved:
        key=(at,b['size'])
        for byte in range(at,at+b['size']):
            if byte in occupied and occupied[byte]!=key:
                raise ValueError('INCOMPATIBLE_OVERLAPPING_NATIVE_BLOCKS')
            occupied[byte]=key
        if key not in groups:
            groups[key]=dict(b,runtime_address_local_only=at,references=[b])
            continue
        old=groups[key]
        if b['before']!=old['before'] or b['mask']&old['mask']:
            raise ValueError('CONFLICTING_PHYSICAL_MASK_OR_PREIMAGE')
        v=int.from_bytes(bytes.fromhex(old['after']),'little')
        n=int.from_bytes(bytes.fromhex(b['after']),'little')
        old['after']=((v&~b['mask'])|(n&b['mask'])).to_bytes(b['size'],'little').hex()
        old['mask'] |= b['mask']
        old['references'].append(b)
    return list(groups.values())


class Executor:
    def __init__(self, registry, session_factory=None, lock_root=None):
        self.registry=registry
        if session_factory is None:
            from .adapters import NativeSession
            session_factory=lambda read_only:NativeSession(read_only,registry)
        self.session_factory=session_factory
        self.lock_root=lock_root

    def targets(self, session, plan, rollback=False):
        session.verify_context(plan)
        by_key={o['object_key']:o for o in plan['objects']}
        resolved=[]
        addresses={}
        for b in plan['blocks']:
            if b['object_key'] not in addresses:
                addresses[b['object_key']]=session.resolve(by_key[b['object_key']])
            at=addresses[b['object_key']]+b['offset']
            resolved.append((b,at))
        merged=merge_physical(resolved)
        for b in merged:
            expected=bytes.fromhex(b['after'] if rollback else b['before'])
            if session.read(b['runtime_address_local_only'],b['size'])!=expected:
                raise ValueError('STALE_SOURCE_FULL_BLOCK')
        session.verify_context(plan)
        return list(reversed(merged)) if rollback else merged

    def preflight(self, plan):
        with lifecycle_lock():
            Workspaces().active(plan['save_id'],plan)
            session=self.session_factory(True)
            try:
                blocks=self.targets(session,plan)
                return dict(status='PREFLIGHT_VERIFIED_READ_ONLY',blocks=len(blocks),write_handles=0,
                            digest=plan['digest'],game_save_binding='UNVERIFIED_REQUIRES_PLAYER_CONFIRMATION')
            finally:
                session.close()

    def run(self, plan, approval, *, rollback=False, supervision=None):
        # Player decision 2026-10-20: trust the operator's reference to explicit
        # chat approval; do not require a separate OS issuer or foreground TTY.
        # Optional review tokens remain scoped, but are not a mandatory gate.
        if supervision is not None:
            from .approval import require_supervision
            require_supervision(plan, approval, supervision, rollback)
        require_approval(plan,approval)  # before any native handle or DB authority claim
        with lifecycle_lock():
            manager=Workspaces()
            manager.active(plan['save_id'],plan)
            # Do not trust callers that edited the stored status to APPROVED.
            stored=load_plan(plan['change_set_id'],self.registry,plan['save_id'])
            if stored!=plan:
                raise ValueError('PLAN_NOT_STAGED_IN_ACTIVE_CONTROL_DB')
            paths=save_context.save_paths(plan['save_id'])
            with connect(paths['control_db_path']) as c:
                previous=c.execute('SELECT * FROM execution_runs WHERE change_set_id=? ORDER BY started_at DESC LIMIT 1',(plan['change_set_id'],)).fetchone()
            if previous:
                status=previous['status']
                if not rollback and status in ('MEMORY_VERIFIED','ROLLED_BACK_VERIFIED_IN_MEMORY'):
                    probe=self.session_factory(True)
                    try:
                        self.targets(probe,plan,rollback=status=='MEMORY_VERIFIED')
                        return dict(status='NO_WRITE_NEEDED',prior_status=status,current_state='REVALIDATED_READ_ONLY',game_writes=0)
                    finally:
                        probe.close()
                if rollback and status=='ROLLED_BACK_VERIFIED_IN_MEMORY':
                    probe=self.session_factory(True)
                    try:
                        self.targets(probe,plan)
                        return dict(status='NO_WRITE_NEEDED',current_state='REVALIDATED_READ_ONLY',game_writes=0)
                    finally:
                        probe.close()
                if not rollback or status!='MEMORY_VERIFIED':
                    raise ValueError('INCOMPLETE_OR_FAILED_RUN_REQUIRES_MANUAL_REVIEW_NEW_PLAN')
            elif rollback:
                raise ValueError('VERIFIED_COMMIT_REQUIRED_FOR_ROLLBACK')
            manager.idle()
            run_id=uuid4().hex
            journal_path=Path(paths['data_dir'])/'state_io_journals'/(run_id+'.json')
            from coaching_execution_lock import CoachingExecutionLock
            lock=CoachingExecutionLock(dict(process_binding=plan['process_binding'],career_id=plan['save_id']),
                                      journal_path,plan['digest'],root=self.lock_root)
            session=None
            journal=None
            run_recorded=False
            try:
                probe=self.session_factory(True)
                try:
                    self.targets(probe,plan,rollback)
                finally:
                    probe.close()
                # Caller attests actual player approval; no isolated human issuer.
                with connect(paths['control_db_path']) as c:
                    c.execute('INSERT INTO approval_records VALUES (?,?,?,?,?,?,?,?)',
                              (uuid4().hex,plan['change_set_id'],approval.digest,canonical(dict(**binding(plan),
                               approval_state='HUMAN_APPROVED',approval_trust='MANUAL_OPERATOR_TRUST_ONLY')),
                               canonical(sorted(approval.action_ids)),approval.player_approval_reference,now(),
                               'ROLLBACK' if rollback else 'APPLY'))
                    c.execute('INSERT INTO execution_runs VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                              (run_id,plan['change_set_id'],plan['digest'],plan['process_binding'],now(),'PREPARED',None,None,None,str(journal_path),'ROLLBACK' if rollback else 'APPLY'))
                run_recorded=True
                session=self.session_factory(False)
                targets=self.targets(session,plan,rollback)
                journal=dict(run_id=run_id,change_set_id=plan['change_set_id'],**binding(plan),
                             digest=plan['digest'],registry_version=plan['registry_version'],process_binding=plan['process_binding'],
                             source_batch_id=plan['source_batch_id'],decision_id=plan['decision_id'],version=plan['version'],
                             status='PREPARED',operation='ROLLBACK' if rollback else 'APPLY',
                             approval_state='HUMAN_APPROVED',approval_trust='MANUAL_OPERATOR_TRUST_ONLY',
                             game_save_binding='PLAYER_CONFIRMED_NOT_INDEPENDENTLY_IDENTIFIED',
                             player_approval_reference=approval.player_approval_reference,blocks=targets,write_log=[],
                             persisted_in_save=False,result_is_game_observation=False,physical_atomicity=False)
                journal['rotation_bias_changes']=[dict(action_id=a['action_id'],selector=a['selector'],
                    intangible_before=a['expected_observed_raw'][0],intangible_after=a['target_value'],
                    source_batch_id=plan['source_batch_id'],displayed_ovr='UNKNOWN',minutes_feedback='LATER_PLAYER_TRIGGERED_BATCH')
                    for a in plan['actions'] if a['field_key']=='rotation.intangibles']
                from . import VERSION
                journal['engine_version']=VERSION
                journal['native_evidence']=(plan.get('source_context') or {}).get('native_evidence')
                atomic_json(journal_path,journal)
                with connect(paths['control_db_path']) as c:
                    c.executemany('INSERT INTO execution_blocks VALUES (?,?,?,?,?,?,?,?)',
                                  [(run_id,b['storage_target_key'],canonical(b['identity']),str(b['mask']),b['before'],b['after'],None,'PREPARED') for b in targets])
                    c.execute("UPDATE execution_runs SET status='APPLYING' WHERE run_id=?",(run_id,))
                attempted=[]
                try:
                    lock.mark_write_started()
                    for b in targets:
                        session.verify_context_light() if hasattr(session,'verify_context_light') else None
                        at=b['runtime_address_local_only']
                        before=bytes.fromhex(b['after'] if rollback else b['before'])
                        after=bytes.fromhex(b['before'] if rollback else b['after'])
                        if session.read(at,len(before))!=before:
                            raise ValueError('CONCURRENT_SHARED_BLOCK_CHANGE')
                        attempted.append((b,before,after))
                        if not session.write(at,after) or session.read(at,len(after))!=after:
                            raise ValueError('WRITE_OR_READBACK_FAILED')
                        b['readback_raw']=after.hex()
                        b['state']='READBACK_VERIFIED'
                    session.verify_context(plan)
                    for b,_,after in attempted:
                        if session.read(b['runtime_address_local_only'],len(after))!=after:
                            raise ValueError('LATE_READBACK_CHANGED')
                    journal['status']='ROLLED_BACK_VERIFIED_IN_MEMORY' if rollback else 'MEMORY_VERIFIED'
                except BaseException as exc:
                    restored=True
                    for b,before,after in reversed(attempted):
                        try:
                            session.verify_context(plan)
                            current=session.read(b['runtime_address_local_only'],len(before))
                            if current==before:
                                b['state']='RESTORED'
                                continue
                            if current!=after or not session.write(b['runtime_address_local_only'],before) or session.read(b['runtime_address_local_only'],len(before))!=before:
                                restored=False
                                b['state']='PARTIAL_UNRECOVERED'
                            else:
                                b['state']='RESTORED'
                        except BaseException:
                            restored=False
                            b['state']='PARTIAL_UNRECOVERED'
                    journal['status']='FAILED_ROLLED_BACK_TO_OPERATION_PREIMAGE' if restored else 'PARTIAL_UNRECOVERED'
                    journal['error_code']=str(exc)
                # A final journal/DB failure keeps the host process lock and the
                # PREPARED/APPLYING row, so no other save can silently continue.
                atomic_json(journal_path,journal)
                with connect(paths['control_db_path']) as c:
                    c.execute('UPDATE execution_runs SET status=?,completed_at=?,readback_summary=?,error_code=? WHERE run_id=?',
                              (journal['status'],now(),canonical(dict(blocks=len(targets),verified=sum(b.get('state')=='READBACK_VERIFIED' for b in targets))),journal.get('error_code'),run_id))
                    for b in targets:
                        c.execute('UPDATE execution_blocks SET readback_raw=?,state=? WHERE run_id=? AND storage_target_key=?',
                                  (b.get('readback_raw'),b.get('state','NOT_ATTEMPTED'),run_id,b['storage_target_key']))
                if journal['status']!='PARTIAL_UNRECOVERED':
                    lock.mark_resolved()
                if 'error_code' in journal:
                    raise RuntimeError(journal['status']+':'+journal['error_code'])
                return dict(status=journal['status'],run_id=run_id,blocks_written=len(targets),journal_path=str(journal_path),
                            approval_state=journal['approval_state'],approval_trust=journal['approval_trust'],
                            persisted_in_save=False,result_is_game_observation=False,
                            game_save_binding=journal['game_save_binding'])
            except BaseException as exc:
                if run_recorded and not lock.write_started:
                    # A RO->RW race or denied RW handle is a clean refusal, not
                    # an unresolved memory transaction requiring manual repair.
                    refused=dict(journal or {},run_id=run_id,change_set_id=plan['change_set_id'],
                                 status='REFUSED_BEFORE_WRITE',error_code=str(exc),game_writes=0,
                                 persisted_in_save=False,result_is_game_observation=False)
                    atomic_json(journal_path,refused)
                    with connect(paths['control_db_path']) as c:
                        c.execute('UPDATE execution_runs SET status=?,completed_at=?,error_code=? WHERE run_id=?',
                                  ('REFUSED_BEFORE_WRITE',now(),str(exc),run_id))
                    lock.mark_resolved()
                raise
            finally:
                if session:
                    session.close()
                lock.close()


def receipt(change_set_id):
    w=Workspaces().active()
    with connect(save_context.save_paths(w['save_id'])['control_db_path']) as c:
        rows=c.execute('SELECT run_id,status,started_at,completed_at,readback_summary,error_code,journal_path FROM execution_runs WHERE change_set_id=? ORDER BY started_at DESC LIMIT 20',(change_set_id,)).fetchall()
    return dict(change_set_id=change_set_id,runs=[dict(r) for r in rows],result_is_game_observation=False)

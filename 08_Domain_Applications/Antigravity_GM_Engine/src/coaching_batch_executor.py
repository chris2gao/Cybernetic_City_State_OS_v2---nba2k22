"""Approval-bound multi-object transaction: preflight every target before RW."""
from dataclasses import dataclass
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
from coach_codec import load_profile
from coach_locator import CoachLocator,live_memory,read_exact
from coaching_executor import atomic_json,source_provenance
from coaching_targets import validate_session,resolve_target
from gm_core.coaching import CONTEXT
from gm_core.coaching_batch import batch_digest,validate_batch


@dataclass(frozen=True)
class BatchApproval:
    career_id:str
    batch_id:str
    decision_id:str
    version:int
    action_ids:tuple
    digest:str
    coach_editor_closed_confirmed:bool=False
    isolated_test_confirmed:bool=False


def require_batch_approval(batch,approval):
    if (type(approval) is not BatchApproval or type(approval.version) is not int
        or any(getattr(approval,k)!=batch.get(k) for k in ('career_id','batch_id','decision_id','version'))
        or len(approval.action_ids)!=len(set(approval.action_ids))
        or set(approval.action_ids)!={a['action_id'] for a in batch.get('actions',[])}
        or approval.digest!=batch_digest(batch)):
        raise PermissionError('SPECIFIC_EXTERNAL_BATCH_APPROVAL_REQUIRED')
    if approval.coach_editor_closed_confirmed is not True:
        raise PermissionError('COACH_EDITOR_MUST_BE_CLOSED_BEFORE_EXECUTION')


class CoachingBatchExecutor:
    def __init__(self,memory_factory=live_memory,locator_factory=CoachLocator,profile=None,*,lock_root=None):
        self.memory_factory=memory_factory
        self.locator_factory=locator_factory
        self.profile=profile or load_profile()
        self.lock_root=lock_root

    def inspect(self,batch,snapshot):
        return validate_batch(batch,snapshot,self.profile)

    def _validated(self,batch,snapshot,isolated_allowed=False):
        result=self.inspect(batch,snapshot)
        if not result['valid']:
            raise ValueError(';'.join(result['errors']))
        if result['blocked_action_ids'] and not isolated_allowed:
            raise PermissionError('PRODUCTION_FIELDS_NOT_READY:'+','.join(result['blocked_action_ids']))
        for action in batch['actions']:
            if action['scope']=='COACH_DEFAULT' and any(not self.profile['fields'][c['field']]['writable'] for c in action['changes']):
                raise PermissionError('FIELD_READ_ONLY')
        return result

    def _check_targets(self,loc,batch,snapshot,prepared,rollback=False):
        validate_session(loc,snapshot)
        actions={a['action_id']:a for a in batch['actions']}
        targets=[]
        addresses=set()
        for row in prepared:
            action=actions[row['action_id']]
            for block in row['blocks']:
                address=resolve_target(loc,action,block,snapshot)
                span=set(range(address,address+block['size']))
                if span&addresses:
                    raise RuntimeError('OVERLAPPING_BATCH_TARGETS')
                addresses|=span
                expected=bytes.fromhex(block['after'] if rollback else block['before'])
                if read_exact(loc.mem,address,block['size'])!=expected:
                    raise RuntimeError('STALE_FULL_SHARED_BLOCK:'+row['action_id'])
                targets.append((action,block,address))
        validate_session(loc,snapshot)
        return targets

    def preflight(self,batch,snapshot,rollback=False):
        result=self._validated(batch,snapshot)
        mem=self.memory_factory(read_only=True)
        try:
            loc=self.locator_factory(mem,self.profile).calibrate()
            targets=self._check_targets(loc,batch,snapshot,result['prepared_actions'],rollback)
            return dict(status='ALL_TARGETS_PREFLIGHT_VERIFIED_READ_ONLY',batch_digest=batch_digest(batch),
                targets=len(targets),write_handles=0)
        finally:
            mem.close()

    def run(self,batch,snapshot,approval,state_root,rollback=False):
        from gm_state_io.lifecycle import operation
        with operation(batch['career_id'],'coaching_apply'):
            return self._run(batch,snapshot,approval,state_root,rollback)

    def _run(self,batch,snapshot,approval,state_root,rollback=False):
        require_batch_approval(batch,approval)
        isolated=snapshot.get('environment')=='ISOLATED_TEST'
        if isolated and approval.isolated_test_confirmed is not True:
            raise PermissionError('ISOLATED_SAVE_CONFIRMATION_REQUIRED')
        result=self._validated(batch,snapshot,isolated and approval.isolated_test_confirmed)
        digest=batch_digest(batch)
        if not batch['actions']:
            if rollback:raise ValueError('HOLD_BATCH_HAS_NO_TRANSACTION_TO_ROLL_BACK')
            return dict(status='NO_WRITE_NEEDED',batch_id=batch['batch_id'],batch_digest=digest,
                teams=[dict(team_id=t,status='HOLD') for t in batch['hold_team_ids']],write_handles=0)
        key=hashlib.sha256(json.dumps([batch[k] for k in ('career_id','batch_id','decision_id','version')]).encode()).hexdigest()
        state=Path(state_root).resolve()
        state.mkdir(parents=True,exist_ok=True)
        path=state/(key+'.json')
        lock_path=state/(hashlib.sha256(batch['career_id'].encode()).hexdigest()+'.batch.lock')
        try:
            lock=lock_path.open('x',encoding='utf-8')
        except FileExistsError as exc:
            raise RuntimeError('BATCH_LOCKED_OR_CRASH_REVIEW_REQUIRED') from exc
        mem=None
        shared_lock=None
        try:
            from coaching_execution_lock import CoachingExecutionLock
            shared_lock=CoachingExecutionLock(snapshot,path,digest,self.lock_root)
            lock.write(digest)
            lock.flush()
            import os
            os.fsync(lock.fileno())
            previous=json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
            if previous and previous['batch_digest']!=digest:
                raise RuntimeError('BATCH_ID_ALREADY_BOUND_TO_DIFFERENT_PLAN')
            if previous and not rollback:
                if previous['status'] in ('COMMITTED_VERIFIED_IN_MEMORY','ROLLED_BACK_VERIFIED_IN_MEMORY'):
                    return dict(previous,idempotent=True,current_state='NOT_REVALIDATED_CACHED_RECEIPT')
                raise RuntimeError('INCOMPLETE_BATCH_REQUIRES_MANUAL_REVIEW')
            if rollback and (not previous or previous['status']!='COMMITTED_VERIFIED_IN_MEMORY'):
                if previous and previous['status']=='ROLLED_BACK_VERIFIED_IN_MEMORY':
                    return dict(previous,idempotent=True,current_state='NOT_REVALIDATED_CACHED_RECEIPT')
                raise RuntimeError('COMMITTED_BATCH_REQUIRED_FOR_ROLLBACK')
            # Entire target set is checked under RO; none can be written early.
            probe=self.memory_factory(read_only=True)
            try:
                loc=self.locator_factory(probe,self.profile).calibrate()
                self._check_targets(loc,batch,snapshot,result['prepared_actions'],rollback)
            finally:
                probe.close()
            mem=self.memory_factory(read_only=False)
            loc=self.locator_factory(mem,self.profile).calibrate()
            targets=self._check_targets(loc,batch,snapshot,result['prepared_actions'],rollback)
            if rollback:
                # Undo the last committed block first, including the UI flag.
                targets=list(reversed(targets))
            records=[dict(action_id=a['action_id'],team_id=a['team_id'],scope=a['scope'],
                opponent_team_id=a.get('opponent_team_id'),block=b,
                runtime_address_local_only=hex(at)) for a,b,at in targets]
            journal=dict(schema_version=1,batch_id=batch['batch_id'],batch_digest=digest,
                decision_id=batch['decision_id'],version=batch['version'],context={k:batch[k] for k in CONTEXT},
                external_approval=dict(action_ids=list(approval.action_ids),digest=approval.digest,
                    origin='LOCAL_OPERATOR_EXTERNAL_PLAYER_APPROVAL',coach_editor_closed=True),
                source_provenance=source_provenance(),blocks=records,write_log=[],
                timestamp=datetime.now(timezone.utc).isoformat(),status='ROLLBACK_PREPARED' if rollback else 'PREPARED',
                physical_atomicity=False,persistence='IN_MEMORY_ONLY_NOT_GAME_SAVE_COMMIT')
            # Every target preimage is durable before the first write.
            atomic_json(path,journal)
            attempted=[]
            try:
                shared_lock.mark_write_started()
                for action,block,address in targets:
                    validate_session(loc,snapshot)
                    if resolve_target(loc,action,block,snapshot)!=address:
                        raise RuntimeError('RUNTIME_TARGET_MOVED')
                    before=bytes.fromhex(block['after'] if rollback else block['before'])
                    after=bytes.fromhex(block['before'] if rollback else block['after'])
                    if read_exact(mem,address,len(before))!=before:
                        raise RuntimeError('CONCURRENT_SHARED_BLOCK_CHANGE')
                    attempted.append((action,block,address,before,after))
                    if not mem.write_bytes(address,after):
                        raise RuntimeError('WRITE_FAILED')
                    if read_exact(mem,address,len(after))!=after:
                        raise RuntimeError('READBACK_MISMATCH')
                    journal['write_log'].append(dict(action_id=action['action_id'],offset=block['offset'],readback=after.hex()))
                    atomic_json(path,journal)
                validate_session(loc,snapshot)
                for action,block,address,_,after in attempted:
                    if resolve_target(loc,action,block,snapshot)!=address or read_exact(mem,address,len(after))!=after:
                        raise RuntimeError('LATE_TARGET_OR_READBACK_CHANGE')
                journal['status']='ROLLED_BACK_VERIFIED_IN_MEMORY' if rollback else 'COMMITTED_VERIFIED_IN_MEMORY'
                journal['teams']=[dict(team_id=t,status='HOLD') for t in batch['hold_team_ids']]
                journal['teams'] += [dict(team_id=t,status='RESTORED' if rollback else 'APPLIED')
                    for t in sorted({a['team_id'] for a in batch['actions']})]
            except BaseException as exc:
                restored=True
                for action,block,address,before,after in reversed(attempted):
                    try:
                        validate_session(loc,snapshot)
                        if resolve_target(loc,action,block,snapshot)!=address:
                            restored=False
                            continue
                        current=read_exact(mem,address,len(after))
                        if current==before:
                            continue
                        if current!=after:
                            restored=False
                            continue
                        if not mem.write_bytes(address,before) or read_exact(mem,address,len(before))!=before:
                            restored=False
                    except BaseException:
                        restored=False
                journal['status']='FAILED_ROLLED_BACK_TO_OPERATION_PREIMAGE' if restored else 'PARTIAL_UNRECOVERED_MANUAL_REVIEW'
                journal['error']=str(exc)
                atomic_json(path,journal)
                if restored:
                    shared_lock.mark_resolved()
                raise RuntimeError(journal['status']+':'+str(exc)) from exc
            atomic_json(path,journal)
            shared_lock.mark_resolved()
            return journal
        finally:
            if mem:
                mem.close()
            if shared_lock:
                shared_lock.close()
            lock.close()
            lock_path.unlink()

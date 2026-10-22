"""Local, approval-bound transactions. No approval is ever read from proposal flags."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
import sys
from pathlib import Path
from coach_codec import load_profile
from coach_locator import CoachLocator, live_memory, read_exact
from gm_core.coaching import CONTEXT, validate_plan

def plan_digest(plan):
    return hashlib.sha256(json.dumps(plan,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

@dataclass(frozen=True)
class PlayerApproval:
    career_id: str
    decision_id: str
    version: int
    action_ids: tuple
    digest: str
    isolated_test_confirmed: bool = False
    coach_editor_closed_confirmed: bool = False

def require_approval(plan,approval):
    if (type(approval) is not PlayerApproval or approval.career_id!=plan.get("career_id")
            or approval.decision_id!=plan.get("decision_id") or type(approval.version) is not int
            or approval.version!=plan.get("version") or plan.get("action_id") not in approval.action_ids
            or approval.digest!=plan_digest(plan)):
        raise PermissionError("SPECIFIC_EXTERNAL_PLAYER_APPROVAL_REQUIRED")

def atomic_json(path,data):
    path=Path(path)
    temp=path.with_name(path.name+".tmp")
    with temp.open("x",encoding="utf-8") as stream:
        json.dump(data,stream,ensure_ascii=False,indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp,path)

def transaction_key(plan):
    return hashlib.sha256(json.dumps([plan[k] for k in ("career_id","decision_id","version","action_id")]).encode()).hexdigest()

def source_provenance():
    root=Path(__file__).resolve().parents[1]
    files=("src/coach_codec.py","src/coach_locator.py","src/coaching_reader.py",
           "src/coaching_executor.py","src/gm_core/coaching.py","config/coach_tactics_profile.json",
           "src/coaching_batch_executor.py","src/coaching_targets.py","src/defense_codec.py",
           "src/gm_core/coaching_batch.py","src/coaching_overall.py","src/coaching_execution_lock.py")
    return dict(version="COACH_EXECUTOR_V2",command=list(sys.argv),
                source_files_sha256={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files})

class CoachingExecutor:
    def __init__(self, memory_factory=live_memory, locator_factory=CoachLocator, profile=None, *, lock_root=None):
        self.memory_factory,self.locator_factory=memory_factory,locator_factory
        self.profile=profile or load_profile()
        self.lock_root=lock_root

    def inspect(self,plan,snapshot):
        result=validate_plan(plan,snapshot,self.profile)
        return dict(**result,plan_digest=plan_digest(plan),mode="DRY_RUN",
                    meaning="Offline preflight only; no process handle or approval",
                    interface_precondition="PLAYER_CONFIRMED_COACH_EDITOR_CLOSED_BEFORE_EXECUTION")

    def _session(self,snapshot,expected_pid):
        mem=self.memory_factory(read_only=False)
        try:
            if mem.pid!=expected_pid or mem.creation_time!=snapshot["process_creation_time"]:
                raise RuntimeError("STALE_PID")
            locator=self.locator_factory(mem,self.profile).calibrate()
            if locator.evidence!=snapshot["native_evidence"]:
                raise RuntimeError("MODULE_OR_NATIVE_EVIDENCE_CHANGED")
            if locator.context_identity()!=snapshot["context_identity"]:
                raise RuntimeError("WRONG_SAVE_COACH_OR_ROSTER")
            if locator.playbooks!=snapshot["playbooks"]:
                raise RuntimeError("LOADED_PLAYBOOK_DIRECTORY_CHANGED")
            return locator
        except BaseException:
            mem.close()
            raise

    def run(self,plan,snapshot,approval,state_root,rollback=False):
        from gm_state_io.lifecycle import operation
        with operation(plan['career_id'],'coaching_apply'):
            return self._run(plan,snapshot,approval,state_root,rollback)

    def _run(self,plan,snapshot,approval,state_root,rollback=False):
        # Every gate above the memory factory is intentional.
        require_approval(plan,approval)
        validation=validate_plan(plan,snapshot,self.profile)
        if not validation["valid"]:
            raise ValueError(";".join(validation["errors"]))
        if approval.coach_editor_closed_confirmed is not True:
            raise PermissionError("COACH_EDITOR_MUST_BE_CLOSED_BEFORE_EXECUTION")
        if plan["scope"]!="COACH_DEFAULT":
            raise PermissionError("MATCHUP_EXECUTION_BLOCKED_NOT_ACTIVATED")
        fields=[self.profile["fields"][c["field"]] for c in plan["changes"]]
        if any(not f["writable"] for f in fields):
            raise PermissionError("FIELD_READ_ONLY")
        isolated=snapshot.get("environment")=="ISOLATED_TEST"
        if isolated:
            if not approval.isolated_test_confirmed:
                raise PermissionError("ISOLATED_SAVE_CONFIRMATION_REQUIRED")
        elif any(not f["production_enabled"] for f in fields):
            raise PermissionError("PRODUCTION_DISABLED_PENDING_TEST_SAVE_ACCEPTANCE")
        key=transaction_key(plan)
        state_root=Path(state_root).resolve()
        state_root.mkdir(parents=True,exist_ok=True)
        journal_path=state_root/(key+".json")
        lock_path=state_root/(key+".lock")
        try:
            lock=lock_path.open("x",encoding="utf-8")
        except FileExistsError as exc:
            raise RuntimeError("TRANSACTION_LOCKED_OR_CRASH_RECOVERY_REQUIRED") from exc
        locator=None
        shared_lock=None
        try:
            from coaching_execution_lock import CoachingExecutionLock
            shared_lock=CoachingExecutionLock(snapshot,journal_path,plan_digest(plan),self.lock_root)
            lock.write(key)
            lock.flush()
            os.fsync(lock.fileno())
            prior=json.loads(journal_path.read_text(encoding="utf-8")) if journal_path.exists() else None
            digest=plan_digest(plan)
            if prior and prior.get("plan_digest")!=digest:
                raise RuntimeError("ACTION_ID_ALREADY_BOUND_TO_DIFFERENT_PLAN")
            if not rollback and prior:
                if prior.get("status") in ("EXECUTED_VERIFIED","ROLLED_BACK"):
                    return dict(prior,idempotent=True,current_state="NOT_REVALIDATED_CACHED_RECEIPT")
                raise RuntimeError("INCOMPLETE_TRANSACTION_REQUIRES_REVIEW")
            if rollback and (not prior or prior.get("status")!="EXECUTED_VERIFIED"):
                if prior and prior.get("status")=="ROLLED_BACK":
                    return dict(prior,idempotent=True,current_state="NOT_REVALIDATED_CACHED_RECEIPT")
                raise RuntimeError("VERIFIED_EXECUTION_REQUIRED_FOR_ROLLBACK")
            blocks=validation["prepared_blocks"]
            if prior and prior.get("blocks")!=blocks:
                raise RuntimeError("JOURNAL_PREIMAGE_MISMATCH")
            # All source comparisons are initially read-only, even after approval.
            probe=self.memory_factory(read_only=True)
            try:
                loc=self.locator_factory(probe,self.profile).calibrate()
                if probe.pid!=snapshot.get("process_pid") or probe.creation_time!=snapshot["process_creation_time"]:
                    raise RuntimeError("STALE_PID")
                if loc.evidence!=snapshot["native_evidence"]:
                    raise RuntimeError("MODULE_OR_NATIVE_EVIDENCE_CHANGED")
                if loc.context_identity()!=snapshot["context_identity"]:
                    raise RuntimeError("WRONG_SAVE_COACH_OR_ROSTER")
                if loc.playbooks!=snapshot["playbooks"]:
                    raise RuntimeError("LOADED_PLAYBOOK_DIRECTORY_CHANGED")
                address=loc.coaches[plan["team_id"]]["address"]
                for b in blocks:
                    expected=bytes.fromhex(b["after"] if rollback else b["before"])
                    if read_exact(probe,address+b["offset"],b["size"])!=expected:
                        raise RuntimeError("STALE_FULL_SHARED_BLOCK")
                expected_pid=probe.pid
            finally:
                probe.close()
            # Only now, after specific approval AND all read-only checks, request write rights.
            locator=self._session(snapshot,expected_pid)
            address=locator.coaches[plan["team_id"]]["address"]
            journal=dict(schema_version=1,plan_digest=digest,transaction_key=key,
                         context={k:plan[k] for k in CONTEXT},decision_id=plan["decision_id"],
                         version=plan["version"],action_id=plan["action_id"],
                         codec_version=self.profile["codec_version"],native_evidence=locator.evidence,
                         source_provenance=source_provenance(),
                         external_approval=dict(career_id=approval.career_id,decision_id=approval.decision_id,
                                                version=approval.version,action_ids=list(approval.action_ids),
                                                plan_digest=approval.digest,origin="LOCAL_OPERATOR_EXTERNAL_INPUT"),
                         isolation="ISOLATED_TEST" if isolated else "FORMAL_PLAYER_APPROVED",
                         interface_precondition="PLAYER_CONFIRMED_COACH_EDITOR_CLOSED_BEFORE_EXECUTION",
                         effect_status="SIM_EFFECT_PENDING_PLAYER_MONTH",
                         timestamp=datetime.now(timezone.utc).isoformat(),status="PREPARED",
                         blocks=blocks,runtime_local_only=dict(pid=locator.mem.pid,address=hex(address)),
                         write_log=[])
            # Revalidate the entire set after opening RW, before persisting or performing any write.
            locator.context_identity()
            for b in blocks:
                expect=bytes.fromhex(b["after"] if rollback else b["before"])
                if read_exact(locator.mem,address+b["offset"],b["size"])!=expect:
                    raise RuntimeError("STALE_FULL_SHARED_BLOCK")
            if not rollback:
                atomic_json(journal_path,journal)
            else:
                journal["status"]="ROLLBACK_PREPARED"
                atomic_json(journal_path,journal)
            attempted=[]
            try:
                shared_lock.mark_write_started()
                for b in blocks:
                    locator.context_identity()
                    at=address+b["offset"]
                    before=bytes.fromhex(b["after"] if rollback else b["before"])
                    after=bytes.fromhex(b["before"] if rollback else b["after"])
                    if read_exact(locator.mem,at,b["size"])!=before:
                        raise RuntimeError("CONCURRENT_SHARED_BLOCK_CHANGE")
                    attempted.append((at,before,after))
                    if not locator.mem.write_bytes(at,after):
                        raise RuntimeError("WRITE_FAILED")
                    if read_exact(locator.mem,at,b["size"])!=after:
                        raise RuntimeError("READBACK_MISMATCH")
                    journal["write_log"].append(dict(offset=b["offset"],readback=after.hex()))
                    atomic_json(journal_path,journal)
                locator.context_identity()
                # Recheck earlier writes too; do not certify a block subsequently overwritten by AI.
                for at,_,after in attempted:
                    if read_exact(locator.mem,at,len(after))!=after:
                        raise RuntimeError("LATE_READBACK_MISMATCH")
                journal["status"]="ROLLED_BACK" if rollback else "EXECUTED_VERIFIED"
                journal["persistence"]="NOT_VERIFIED_BY_MEMORY_READBACK"
            except BaseException as exc:
                restored=True
                for at,before,after in reversed(attempted):
                    try:
                        locator.context_identity()
                        current=read_exact(locator.mem,at,len(after))
                        if current==before:
                            continue
                        if current!=after:
                            restored=False
                            continue
                        if not locator.mem.write_bytes(at,before) or read_exact(locator.mem,at,len(before))!=before:
                            restored=False
                    except BaseException:
                        restored=False
                journal["status"]="FAILED_ROLLED_BACK" if restored else "PARTIAL_UNRECOVERED"
                journal["error"]=str(exc)
                atomic_json(journal_path,journal)
                if restored:
                    shared_lock.mark_resolved()
                raise RuntimeError(journal["status"]+":"+str(exc)) from exc
            atomic_json(journal_path,journal)
            shared_lock.mark_resolved()
            return journal
        finally:
            if locator:
                locator.close()
            if shared_lock:
                shared_lock.close()
            lock.close()
            lock_path.unlink()

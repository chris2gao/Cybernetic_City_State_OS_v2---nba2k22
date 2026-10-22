"""Host-local exclusion shared by every coaching writer and journal directory.

Only local runtime metadata is written. No process handle is opened here.
An abandoned or unresolved lock is intentionally retained for manual review.
"""
import json
import os
from pathlib import Path
import re
import tempfile
from uuid import uuid4
from coaching_targets import process_binding

DEFAULT_LOCK_ROOT=Path(tempfile.gettempdir())/'Antigravity_GM_Engine'/'coaching_execution_locks_v1'


class CoachingExecutionLock:
    def __init__(self,snapshot,journal_path,digest,root=None):
        binding=snapshot.get('process_binding')
        if binding is None:
            binding=process_binding(snapshot['process_pid'],snapshot['process_creation_time'])
        if not isinstance(binding,str) or not re.fullmatch('[0-9a-f]{64}',binding):
            raise ValueError('VALID_PROCESS_BINDING_REQUIRED_FOR_EXECUTION_LOCK')
        directory=Path(root) if root is not None else DEFAULT_LOCK_ROOT
        directory.mkdir(parents=True,exist_ok=True)
        self.path=directory/(binding+'.lock')
        self.token=uuid4().hex
        self.write_started=False
        self.resolved=False
        self.record=dict(schema_version=1,token=self.token,process_binding=binding,
            career_id=snapshot['career_id'],journal_path_local_only=str(Path(journal_path).resolve()),
            plan_digest=digest,status='ACQUIRED_BEFORE_GAME_HANDLES')
        try:
            self.file=self.path.open('x',encoding='utf-8')
        except FileExistsError as exc:
            raise RuntimeError('COACHING_EXECUTION_LOCKED_OR_MANUAL_REVIEW_REQUIRED') from exc
        try:
            self._persist()
        except BaseException:
            self.file.close()
            self.path.unlink()
            raise

    def _persist(self):
        self.file.seek(0)
        json.dump(self.record,self.file,sort_keys=True)
        self.file.truncate()
        self.file.flush()
        os.fsync(self.file.fileno())

    def mark_write_started(self):
        self.record['status']='WRITE_PHASE_UNRESOLVED_UNTIL_JOURNAL_FINALIZED'
        self._persist()
        self.write_started=True

    def mark_resolved(self):
        # Called only after a durable terminal journal: commit or full restore.
        self.resolved=True

    def close(self):
        self.file.close()
        if self.write_started and not self.resolved:
            return
        # Never remove a replacement lock left by another owner or reviewer.
        try:
            record=json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError,ValueError):
            return
        if record.get('token')==self.token:
            self.path.unlink()

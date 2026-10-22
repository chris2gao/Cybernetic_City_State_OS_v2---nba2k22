"""Cross-entry-point exclusion using fake game memory and temporary runtime paths."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from test_coaching_safety import World
from coaching_execution_lock import CoachingExecutionLock
from coaching_executor import CoachingExecutor
from coaching_batch_executor import CoachingBatchExecutor,BatchApproval
from gm_core.coaching_batch import propose_batch,batch_digest


class SharedExecutionLockTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.locks=self.root/'shared_runtime'
        self.world=World()
        self.batch=self.proposal(self.world.snapshot)

    def proposal(self,snapshot,batch_id='B_SHARED'):
        return propose_batch(snapshot,[dict(team_id=8,targets={'POEOffense':1},action_id='GS_A',
            expected_effect='Synthetic transaction exclusion only')],batch_id,'D_SHARED',1)

    def approval(self,batch):
        return BatchApproval(batch['career_id'],batch['batch_id'],batch['decision_id'],batch['version'],
            tuple(a['action_id'] for a in batch['actions']),batch_digest(batch),True,True)

    def single(self):
        return CoachingExecutor(self.world.memory,self.world.locator,lock_root=self.locks)

    def multiple(self):
        return CoachingBatchExecutor(self.world.memory,self.world.locator,lock_root=self.locks)

    def run_single(self):
        return self.single().run(self.world.plan,self.world.snapshot,self.world.approval(),self.root/'single')

    def run_batch(self,batch=None,snapshot=None,state='batch'):
        batch=batch or self.batch
        return self.multiple().run(batch,snapshot or self.world.snapshot,self.approval(batch),self.root/state)

    def test_held_lock_blocks_both_writers_other_journal_roots_and_career_labels(self):
        lock=CoachingExecutionLock(self.world.snapshot,self.root/'holder.json','test',self.locks)
        try:
            with self.assertRaisesRegex(RuntimeError,'COACHING_EXECUTION_LOCKED'):
                self.run_single()
            with self.assertRaisesRegex(RuntimeError,'COACHING_EXECUTION_LOCKED'):
                self.run_batch(state='different_journal_root')
            snapshot=copy.deepcopy(self.world.snapshot)
            snapshot['career_id']='ANOTHER_LABEL_FOR_SAME_PROCESS'
            with self.assertRaisesRegex(RuntimeError,'COACHING_EXECUTION_LOCKED'):
                self.run_batch(self.proposal(snapshot),snapshot,state='third_root')
            self.assertEqual(self.world.opens,[])
            self.assertEqual(self.world.writes,[])
        finally:
            lock.close()

    def test_legacy_writer_owns_lock_before_rw_callback_can_start_batch(self):
        factory=self.world.memory
        prevented=[]
        def interleaved(read_only=True):
            if not read_only:
                with self.assertRaisesRegex(RuntimeError,'COACHING_EXECUTION_LOCKED'):
                    self.run_batch(state='nested_batch')
                prevented.append(True)
            return factory(read_only)
        self.world.memory=interleaved
        self.assertEqual(self.run_single()['status'],'EXECUTED_VERIFIED')
        self.assertEqual(prevented,[True])
        self.assertEqual(self.world.opens,[True,False])

    def test_durable_success_releases_lock_for_other_entry_point(self):
        self.run_single()
        self.assertEqual(list(self.locks.glob('*.lock')),[])
        self.assertEqual(self.run_batch()['status'],'COMMITTED_VERIFIED_IN_MEMORY')
        self.assertEqual(list(self.locks.glob('*.lock')),[])

    def test_unresolved_legacy_and_batch_writes_retain_lock_for_other_roots(self):
        for kind in ('single','batch'):
            with self.subTest(kind=kind):
                self.world=World()
                self.batch=self.proposal(self.world.snapshot)
                self.locks=self.root/(kind+'_shared')
                self.world.corrupt_after_write=True
                with self.assertRaisesRegex(RuntimeError,'PARTIAL_UNRECOVERED'):
                    self.run_single() if kind=='single' else self.run_batch(state='partial_batch')
                retained=list(self.locks.glob('*.lock'))
                self.assertEqual(len(retained),1)
                record=json.loads(retained[0].read_text(encoding='utf-8'))
                self.assertEqual(record['status'],'WRITE_PHASE_UNRESOLVED_UNTIL_JOURNAL_FINALIZED')
                self.assertTrue(Path(record['journal_path_local_only']).is_file())
                opens=list(self.world.opens)
                with self.assertRaisesRegex(RuntimeError,'COACHING_EXECUTION_LOCKED'):
                    self.run_batch(self.proposal(self.world.snapshot,'NEW_BATCH'),state='new_location')
                self.assertEqual(self.world.opens,opens)

    def test_prewrite_identity_failure_releases_lock(self):
        self.world.context={'wrong':True}
        with self.assertRaisesRegex(RuntimeError,'WRONG_SAVE'):
            self.run_batch()
        self.assertEqual(self.world.writes,[])
        self.assertEqual(list(self.locks.glob('*.lock')),[])

    def test_final_journal_write_failure_retains_shared_guard(self):
        from coaching_batch_executor import atomic_json
        def disk_failure(path,value):
            if value['status']=='COMMITTED_VERIFIED_IN_MEMORY':
                raise OSError('synthetic final journal failure')
            atomic_json(path,value)
        with patch('coaching_batch_executor.atomic_json',side_effect=disk_failure):
            with self.assertRaisesRegex(OSError,'final journal failure'):
                self.run_batch()
        self.assertEqual(len(list(self.locks.glob('*.lock'))),1)
        opens=list(self.world.opens)
        with self.assertRaisesRegex(RuntimeError,'COACHING_EXECUTION_LOCKED'):
            self.run_batch(self.proposal(self.world.snapshot,'AFTER_DISK_ERROR'),state='new_root')
        self.assertEqual(self.world.opens,opens)

    def test_other_python_process_cannot_claim_existing_runtime_lock(self):
        snapshot=self.root/'snapshot.json'
        snapshot.write_text(json.dumps(self.world.snapshot),encoding='utf-8')
        child=self.root/'claim_lock.py'
        child.write_text('''import json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from coaching_execution_lock import CoachingExecutionLock
try:
    lock=CoachingExecutionLock(json.loads(Path(sys.argv[2]).read_text()),Path(sys.argv[3])/'child.json','child',sys.argv[3])
except RuntimeError as exc:
    print(str(exc))
    raise SystemExit(9)
else:
    lock.close()
''',encoding='utf-8')
        lock=CoachingExecutionLock(self.world.snapshot,self.root/'holder.json','test',self.locks)
        try:
            result=subprocess.run([sys.executable,str(child),str(Path(__file__).resolve().parents[1]/'src'),
                str(snapshot),str(self.locks)],capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,9,result.stderr[:300])
            self.assertIn('COACHING_EXECUTION_LOCKED',result.stdout)
        finally:
            lock.close()


if __name__=='__main__':unittest.main()

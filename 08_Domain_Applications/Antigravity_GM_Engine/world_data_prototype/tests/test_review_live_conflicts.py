"""F-03 controlled adapter receipts in isolated DBs; NOT real Windows reads."""
from copy import deepcopy
import hashlib,importlib,json,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from cli import synthetic_payload
from engine import create_database,connect,ingest_synthetic_capture,ingest_or_quarantine,ingest_acquired_capture,CaptureQuarantined,quarantine_unit_id
from live_world import _AcquisitionReceipt
from query import inspect_conflicts,history
from refresh import SOURCES

class ControlledProcess:
    def __init__(self):self.trace=[{'success':True,'operation':'CONTROLLED_TEST_ADAPTER_NOT_WINDOWS_MEMORY'}]

def receipt(payload):
    # Replace only the reader boundary in this isolated test. Production retains
    # its exact Windows-reader type check; receipt validation itself is real.
    with patch('live_world.ReadOnlyGameProcess',ControlledProcess):return _AcquisitionReceipt(payload,ControlledProcess())

class ReviewLiveConflictsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'test-only.sqlite';create_database(self.db,'save')
        baseline=synthetic_payload('save');baseline['game_state']['is_final']=1
        with connect(self.db) as c:ingest_synthetic_capture(c,baseline)
        self.proposal={'save_id':'save','run_id':'proposal','unit_id':'proposal','source_key':'CONTROLLED_TEST_SOURCE','evidence_grade':'LIVE_READ','observed_at':'2026-10-26T00:00:00Z','season':baseline['season'],'decoder_version':'CONTROLLED_TEST_ONLY','save_binding_ref':'CONTROLLED_TEST_ONLY',
            'artifacts':[{'sha256':hashlib.sha256(b'controlled-test-evidence').hexdigest(),'payload_kind':'CONTROLLED_ADAPTER_FIXTURE_NOT_NATIVE','payload_ref':'isolated-fixture.bin','byte_count':24}],
            'facts':{'player_game_boxes':[{'game_id':'game-1','player_id':'player-a','team_id':'team-a','points':99}]}}
    def assertOriginal(self,c):
        self.assertEqual(c.execute('SELECT points FROM player_game_boxes').fetchall()[0][0],22);self.assertEqual(c.execute('SELECT count(*) FROM player_game_boxes').fetchone()[0],1)
        self.assertIsNone(c.execute("SELECT unit_id FROM capture_units WHERE unit_id='proposal'").fetchone())
    def test_verified_live_conflict_is_independent_and_grade_preserved(self):
        with connect(self.db) as c:
            self.assertEqual(ingest_or_quarantine(c,self.proposal,_live_receipt=receipt(self.proposal)),'quarantined_pending_human');self.assertOriginal(c)
            row=c.execute('SELECT r.source_grade,u.completeness,u.payload_sha256 FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.unit_id=?',(quarantine_unit_id(self.proposal),)).fetchone();self.assertEqual(row['source_grade'],'LIVE_READ');self.assertEqual(row['completeness'],'PARTIAL')
            artifacts=c.execute('SELECT sha256,unit_id FROM source_artifacts WHERE unit_id=?',(quarantine_unit_id(self.proposal),)).fetchall();self.assertEqual(artifacts[0]['sha256'],self.proposal['artifacts'][0]['sha256'])
        record=inspect_conflicts(self.db,proposed_unit_id='proposal')['records'][0];evidence=json.loads(record['evidence_a']);self.assertTrue(evidence['receipt_verified']);self.assertEqual(evidence['proposed_source_key'],'CONTROLLED_TEST_SOURCE');self.assertIn('frozen game conflict',evidence['error']);self.assertEqual(evidence['proposed_game_ids'],['game-1'])
    def test_actual_schedule_adapter_boundary_raises_explicit_non_success(self):
        import schedule_reader
        with connect(self.db) as c:
            with self.assertRaises(CaptureQuarantined) as event:schedule_reader.ingest_capture(c,self.proposal,_live_receipt=receipt(self.proposal))
            self.assertEqual(event.exception.quarantine_unit_id,quarantine_unit_id(self.proposal));self.assertOriginal(c);self.assertEqual(c.execute('SELECT count(*) FROM fact_conflicts').fetchone()[0],1)
    def test_replayed_proposal_is_idempotent(self):
        capability=receipt(self.proposal)
        with connect(self.db) as c:
            for _ in range(2):self.assertEqual(ingest_or_quarantine(c,self.proposal,_live_receipt=capability),'quarantined_pending_human')
            self.assertOriginal(c);self.assertEqual(c.execute('SELECT count(*) FROM fact_conflicts').fetchone()[0],1);self.assertEqual(c.execute("SELECT count(*) FROM capture_units WHERE source_key LIKE 'quarantine:%'").fetchone()[0],1)
    def test_missing_or_forged_receipt_never_creates_conflict(self):
        for capability in (None,object()):
            with connect(self.db) as c:
                with self.assertRaisesRegex(ValueError,'acquisition adapter'):ingest_or_quarantine(c,self.proposal,_live_receipt=capability)
                self.assertOriginal(c);self.assertEqual(c.execute('SELECT count(*) FROM fact_conflicts').fetchone()[0],0)
    def test_receipt_cannot_be_reused_for_changed_or_cross_save_payload(self):
        capability=receipt(self.proposal);changed=deepcopy(self.proposal);changed['facts']['player_game_boxes'][0]['points']=100
        with connect(self.db) as c:
            with self.assertRaisesRegex(ValueError,'acquisition adapter'):ingest_or_quarantine(c,changed,_live_receipt=capability)
            changed=deepcopy(self.proposal);changed['save_id']='other'
            with self.assertRaisesRegex(ValueError,'cross-save'):ingest_or_quarantine(c,changed,_live_receipt=receipt(changed))
            self.assertEqual(c.execute('SELECT count(*) FROM fact_conflicts').fetchone()[0],0)
    def test_restricted_payload_and_public_diagnostic_access_rejected(self):
        changed=deepcopy(self.proposal);changed['facts']['player_game_boxes'][0]['potential_raw']=99
        with connect(self.db) as c:
            with self.assertRaises(PermissionError):ingest_or_quarantine(c,changed,_live_receipt=receipt(changed))
            self.assertEqual(c.execute('SELECT count(*) FROM fact_conflicts').fetchone()[0],0)
        with self.assertRaises(PermissionError):inspect_conflicts(self.db,role='GM')
        with self.assertRaises(PermissionError):history(self.db,'fact_conflicts')
    def test_every_registered_live_adapter_uses_verified_conflict_boundary(self):
        modules={v[0] for v in SOURCES.values()}|{'live_world'}
        self.assertEqual(len(modules),20)
        for name in modules:
            with self.subTest(module=name):self.assertIs(importlib.import_module(name).ingest_capture,ingest_acquired_capture)

if __name__=='__main__':unittest.main()

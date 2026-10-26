"""Restart/recovery controller fixtures; no live or UI claims from these tests."""
from copy import deepcopy
import hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from process_session import resolve_pid,pid_argument,reconnect
from refresh import refresh_world,RefreshFailed
import test_refresh as fixture
EPOCH=fixture.EPOCH

PROGRESS={'today_native_iso_date':'2021-11-20','today_minutes_since_midnight_raw':0,'period_raw':29,'mode_raw':1,'league_raw':0}
CONTEXT={'epoch':EPOCH,'game_progress':PROGRESS,'read_trace':[]}


class SessionTests(unittest.TestCase):
    def test_auto_discovery_requires_one_game_and_explicit_pid_never_falls_back(self):
        for pids in ([],[10,20]):
            with patch('process_session.discover_game_processes',return_value=pids),self.assertRaises(RuntimeError):resolve_pid()
        with patch('process_session.discover_game_processes',return_value=[30]) as discovery:
            self.assertEqual(resolve_pid(),30);self.assertEqual(resolve_pid('auto'),30);self.assertEqual(resolve_pid(25),25);self.assertEqual(discovery.call_count,2)
        for pid in (True,0,-1,3.5,'25'):
            with self.assertRaises(ValueError):resolve_pid(pid)
        self.assertIsNone(pid_argument('auto'));self.assertEqual(pid_argument('12'),12)


class RecoveryTests(unittest.TestCase):
    setUp=fixture.RefreshTests.setUp
    unit=fixture.RefreshTests.unit
    adapter=fixture.RefreshTests.adapter
    def batch(self,out,*,context=CONTEXT,**kwargs):
        with patch('refresh._context',return_value=deepcopy(context)),patch('refresh._capture',side_effect=self.adapter),patch('refresh.resolve_pid',return_value=context['epoch']['pid']):
            return refresh_world(None,self.save,'MyLEAGUE0003',out,**kwargs)
    def test_reconnect_after_restart_never_creates_fact_or_annual_unit(self):
        with patch('refresh._context',return_value=deepcopy(CONTEXT)),patch('process_session.resolve_pid',return_value=123):
            first=reconnect(self.save,'MyLEAGUE0003',self.root/'connect1')
        changed=deepcopy(CONTEXT);changed['epoch']['pid']=789;changed['epoch']['creation_filetime']+=1
        with patch('refresh._context',return_value=changed),patch('process_session.resolve_pid',return_value=789):
            second=reconnect(self.save,'MyLEAGUE0003',self.root/'connect2')
        self.assertIsNone(first['process_changed']);self.assertTrue(second['process_changed']);self.assertFalse(second['game_progress_changed']);self.assertEqual(second['fact_units_created'],0)
        from engine import connect
        with connect(self.db,True) as conn:self.assertEqual(conn.execute('SELECT count(*) FROM capture_units').fetchone()[0],0)
    def test_resume_restarted_process_retains_original_times_and_does_not_recapture(self):
        old=self.batch(self.out,families=['schedule','settings']);changed=deepcopy(CONTEXT);changed['epoch']['creation_filetime']+=9
        result=self.batch(self.root/'resumed',context=changed,resume_report=self.out/'refresh-report.json')
        self.assertEqual([e['status'] for e in result['sources']],['RETAINED_PRIOR_OBSERVATION']*2);self.assertEqual(self.counter,2)
        self.assertEqual(result['sources'][0]['unit'],old['sources'][0]['unit']);self.assertFalse(result['sources'][0]['fresh_native_capture'])
    def test_changed_native_date_or_explicit_update_or_missing_old_progress_recaptures(self):
        for cause in ('date','update','legacy'):
            out=self.root/cause;old=self.batch(out,families=['schedule']);context=deepcopy(CONTEXT)
            if cause=='date':context['game_progress']['today_native_iso_date']='2021-12-20'
            if cause=='legacy':old.pop('game_progress');(out/'refresh-report.json').write_text(json.dumps(old))
            before=self.counter;result=self.batch(self.root/(cause+'-new'),context=context,resume_report=out/'refresh-report.json',data_updated=cause=='update')
            self.assertEqual(self.counter,before+1);self.assertEqual(result['sources'][0]['status'],'ACQUIRED')
    def test_live_or_unknown_prior_controller_is_never_started_twice(self):
        old=self.batch(self.out,families=['schedule']);old['status']='RUNNING';(self.out/'refresh-report.json').write_text(json.dumps(old))
        with patch('refresh.owner_is_live',return_value=True),self.assertRaises(ValueError):self.batch(self.root/'live',resume_report=self.out/'refresh-report.json')
        self.assertFalse((self.root/'live').exists())
        with patch('refresh.owner_is_live',side_effect=PermissionError('unknown owner state')),self.assertRaises(PermissionError):self.batch(self.root/'unknown',resume_report=self.out/'refresh-report.json')
    def test_killed_controller_child_receipt_reconciled_against_database(self):
        old=self.batch(self.out,families=['schedule']);entry=old['sources'][0];result={'status':'ingested','unit_id':entry['unit']['unit_id']}
        marker=b'SYNTHETIC_ARTIFACT';(self.out/entry['directory']/'source.bin').write_bytes(marker)
        from engine import connect
        with connect(self.db) as conn:conn.execute('INSERT INTO source_artifacts(artifact_id,unit_id,sha256,payload_kind,payload_ref,byte_count) VALUES(?,?,?,?,?,?)',('synthetic-artifact',result['unit_id'],hashlib.sha256(marker).hexdigest(),'SYNTHETIC_FIXTURE',entry['directory']+'/source.bin',len(marker)))
        (self.out/entry['directory']/'ingest-result.json').write_text(json.dumps(result));entry.pop('unit');entry['status']='RUNNING';entry.pop('adapter_claim',None);old['status']='RUNNING'
        (self.out/'refresh-report.json').write_text(json.dumps(old))
        with patch('refresh.owner_is_live',return_value=False):resumed=self.batch(self.root/'recover',resume_report=self.out/'refresh-report.json')
        self.assertEqual(resumed['sources'][0]['status'],'RETAINED_PRIOR_OBSERVATION');self.assertEqual(self.counter,1)
        (self.out/entry['directory']/'ingest-result.json').unlink()
        with patch('refresh.owner_is_live',return_value=False):without_child_file=self.batch(self.root/'recover-without-result',resume_report=self.out/'refresh-report.json')
        self.assertEqual(without_child_file['sources'][0]['status'],'RETAINED_PRIOR_OBSERVATION');self.assertEqual(self.counter,1)
        (self.out/entry['directory']/'source.bin').write_bytes(b'CHANGED')
        with patch('refresh.owner_is_live',return_value=False),self.assertRaises(RefreshFailed):self.batch(self.root/'bad-artifact',resume_report=self.out/'refresh-report.json')
    def test_bad_child_receipt_and_changed_binding_cannot_be_retained(self):
        old=self.batch(self.out,families=['schedule']);old['sources'][0]['unit']['payload_sha256']='f'*64;(self.out/'refresh-report.json').write_text(json.dumps(old))
        with self.assertRaises(RefreshFailed):self.batch(self.root/'bad-receipt',resume_report=self.out/'refresh-report.json')
        old['binding_sha256']='f'*64;(self.out/'refresh-report.json').write_text(json.dumps(old))
        with self.assertRaises(ValueError):self.batch(self.root/'bad-binding',resume_report=self.out/'refresh-report.json')
    def test_mid_batch_date_change_stops_before_next_source(self):
        changed=deepcopy(CONTEXT);changed['game_progress']['today_native_iso_date']='2021-12-20'
        with patch('refresh._context',side_effect=[deepcopy(CONTEXT),changed]),patch('refresh._capture',side_effect=self.adapter),self.assertRaises(RefreshFailed):
            refresh_world(123,self.save,'MyLEAGUE0003',self.out,families=['schedule','settings'])
        self.assertEqual(self.counter,1)


if __name__=='__main__':unittest.main()

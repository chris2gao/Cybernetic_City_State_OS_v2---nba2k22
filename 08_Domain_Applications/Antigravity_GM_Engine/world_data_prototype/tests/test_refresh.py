"""Synthetic controller/ledger tests; mocked adapters never establish live evidence."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import importlib,json,sys,unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import connect
from live_world import initialize_save
from refresh import refresh_world,RefreshFailed,SOURCES,_unit_receipt

EPOCH={'pid':123,'creation_filetime':456,'module_base':'0x140000000','module_size':100000000,'pe_timestamp':1652287197,'game_season_year':2022}

class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);native=self.root/'MyLEAGUE0003';native.write_bytes(b'SYNTHETIC_SAVE')
        self.save=self.root/'save';initialize_save(self.save,'fixture',native);self.db=self.save/'world.sqlite';self.out=self.root/'batch';self.counter=0
    def unit(self,family,grade='LIVE_READ',year=2022):
        # Deliberately insert a synthetic ledger row directly to test receipt matching.
        # This does not go through or substitute for the production acquisition path.
        self.counter+=1;key='synthetic-unit-'+str(self.counter);source=SOURCES[family][2];annual=SOURCES[family][3]
        with connect(self.db) as conn:
            conn.execute('INSERT OR IGNORE INTO seasons(season_id,season_code,save_id) VALUES(?,?,?)',('season:native-year:'+str(year),'NATIVE_YEAR:'+str(year),'fixture'))
            conn.execute('INSERT INTO capture_runs(run_id,season_id,observed_at,source_grade,refresh_family,refresh_period_year) VALUES(?,?,?,?,?,?)',(key,'season:native-year:'+str(year),'2026-10-25T00:00:00Z',grade,annual,year if annual else None))
            conn.execute('INSERT INTO capture_units(unit_id,run_id,source_key,payload_sha256,unit_status,observed_at) VALUES(?,?,?,?,?,?)',(key,key,source,'0'*64,'success','2026-10-25T00:00:00Z'))
        return key
    def adapter(self,family,pid,save,filename,directory):
        directory.mkdir();key=self.unit(family);return {'status':'ingested','unit_id':key,'counts':{'SYNTHETIC':1}}
    def run_batch(self,**kwargs):
        with patch('refresh._context',return_value={'epoch':deepcopy(EPOCH),'read_trace':[]}),patch('refresh._capture',side_effect=self.adapter):return refresh_world(123,self.save,'MyLEAGUE0003',self.out,**kwargs)
    def test_all_registered_adapters_exist_and_order_keeps_identity_source_first(self):
        self.assertEqual(len(SOURCES),14);self.assertEqual(next(iter(SOURCES)),'schedule');self.assertEqual(sum(bool(v[3]) for v in SOURCES.values()),3)
        for module,function,_,_ in SOURCES.values():self.assertTrue(callable(getattr(importlib.import_module(module),function)))
    def test_successful_batch_normalizes_order_and_checks_each_epoch(self):
        with patch('refresh._context',return_value={'epoch':deepcopy(EPOCH),'read_trace':[]}) as context,patch('refresh._capture',side_effect=self.adapter):
            value=refresh_world(123,self.save,'MyLEAGUE0003',self.out,families=['player-skills','schedule'])
        self.assertEqual(value['status'],'COMPLETED_REQUESTED_SOURCES');self.assertEqual(value['requested_families'],['schedule','player-skills']);self.assertEqual(context.call_count,4)
        self.assertTrue(all(r['commit_status']=='COMMITTED_SUCCESS_VERIFIED' for r in value['sources']));self.assertFalse(value['scheduler_started']);self.assertFalse(value['full_goal_complete'])
    def test_annual_skip_must_reference_existing_same_year_live_receipt(self):
        key=self.unit('records')
        with patch('refresh._context',return_value={'epoch':deepcopy(EPOCH),'read_trace':[]}),patch('refresh._capture',return_value={'status':'already_refreshed','previous_unit_id':key}):
            value=refresh_world(123,self.save,'MyLEAGUE0003',self.out,families=['records'])
        self.assertEqual(value['sources'][0]['status'],'ANNUAL_ALREADY_REFRESHED')
        with connect(self.db,True) as conn:self.assertEqual(conn.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)
    def test_adapter_failure_preserves_prior_commit_and_lists_selective_rerun(self):
        def fail(family,*args):
            if family=='organization':raise OSError('synthetic inaccessible source')
            return self.adapter(family,*args)
        with patch('refresh._context',return_value={'epoch':deepcopy(EPOCH),'read_trace':[]}),patch('refresh._capture',side_effect=fail),self.assertRaises(RefreshFailed) as caught:
            refresh_world(123,self.save,'MyLEAGUE0003',self.out,families=['schedule','organization','settings'])
        value=caught.exception.report;self.assertEqual([s['status'] for s in value['sources']],['ACQUIRED','FAILED','PENDING']);self.assertEqual(value['rerun_families'],['organization','settings'])
        self.assertEqual(value['sources'][1]['commit_status'],'UNKNOWN_UNTIL_RECEIPT_VERIFIED')
        with connect(self.db,True) as conn:self.assertEqual(conn.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)
        self.assertEqual(json.loads((self.out/'refresh-report.json').read_bytes())['status'],'STOPPED_PARTIAL')
    def test_process_restart_after_commit_stops_without_erasing_receipt(self):
        changed=deepcopy(EPOCH);changed['creation_filetime']+=1
        with patch('refresh._context',side_effect=[{'epoch':EPOCH,'read_trace':[]},{'epoch':changed,'read_trace':[]}]),patch('refresh._capture',side_effect=self.adapter),self.assertRaises(RefreshFailed) as caught:
            refresh_world(123,self.save,'MyLEAGUE0003',self.out,families=['schedule','settings'])
        first=caught.exception.report['sources'][0];self.assertEqual(first['status'],'ACQUIRED');self.assertEqual(first['post_capture_context_status'],'FAILED_AFTER_VERIFIED_COMMIT');self.assertEqual(caught.exception.report['rerun_families'],['settings'])
    def test_save_binding_change_stops_before_next_native_checkpoint(self):
        def change(family,*args):
            value=self.adapter(family,*args);path=self.save/'save.json';binding=json.loads(path.read_bytes());binding['synthetic_change']=True;path.write_text(json.dumps(binding),encoding='utf-8');return value
        with patch('refresh._context',return_value={'epoch':EPOCH,'read_trace':[]}) as context,patch('refresh._capture',side_effect=change),self.assertRaises(RefreshFailed) as caught:
            refresh_world(123,self.save,'MyLEAGUE0003',self.out,families=['schedule','settings'])
        self.assertEqual(context.call_count,1);self.assertIn('binding changed',caught.exception.report['failure']['reason'])
    def test_uncommitted_fixture_wrong_source_and_wrong_year_are_rejected(self):
        for kind in ('missing','fixture','wrong-source','wrong-year'):
            with self.subTest(kind=kind):
                key='missing' if kind=='missing' else self.unit('organization' if kind=='wrong-source' else 'schedule',grade='RESEARCH_FIXTURE' if kind=='fixture' else 'LIVE_READ',year=2021 if kind=='wrong-year' else 2022)
                with self.assertRaises(ValueError):_unit_receipt(self.db,{'status':'ingested','unit_id':key},'schedule',2022)
    def test_ordinary_skip_and_wrong_annual_bucket_are_rejected(self):
        with self.assertRaises(ValueError):_unit_receipt(self.db,{'status':'already_refreshed','previous_unit_id':self.unit('schedule')},'schedule',2022)
        key=self.unit('records',year=2021)
        with self.assertRaises(ValueError):_unit_receipt(self.db,{'status':'already_refreshed','previous_unit_id':key},'records',2022)
    def test_invalid_plan_and_filename_do_not_open_process(self):
        with patch('refresh._context') as context:
            for families in ([],['schedule','schedule'],['unknown']):
                with self.assertRaises(ValueError):refresh_world(123,self.save,'MyLEAGUE0003',self.out,families=families)
            with self.assertRaises(ValueError):refresh_world(123,self.save,'MyLEAGUE0004',self.out)
            with self.assertRaises(ValueError):refresh_world(True,self.save,'MyLEAGUE0003',self.out)
        context.assert_not_called();self.assertFalse(self.out.exists())
    def test_existing_output_is_never_overwritten(self):
        self.out.mkdir();marker=self.out/'preserve';marker.write_text('original')
        with self.assertRaises(FileExistsError):self.run_batch(families=['schedule'])
        self.assertEqual(marker.read_text(),'original')

if __name__=='__main__':unittest.main()

"""Annual collection behavior; seeded SQL controls below are NOT live evidence."""
import json
from pathlib import Path
import sqlite3
import struct
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from cadence import annual_status,attach_annual_period,observed_game_season_year,validate_refresh_metadata
from engine import connect,create_database,ingest_capture
from live_reader import ROSTER_RVA


class SeasonControl:
    module_base=0x140000000
    def __init__(self,changed=False):
        self.trace=[];self.closed=False;self.changed=changed
        self.values={self.module_base+ROSTER_RVA:struct.pack('<Q',0x10000),
            0x10000+8*16:struct.pack('<QQ',1,0x20000),0x10000+28*16:struct.pack('<QQ',2,0x30000),
            0x20000+0xCA8:b'\0\0',0x20000+0xE80:b'\1\0',0x30000+62+4:bytes([201])}
    def read(self,address,length,label):
        self.trace.append((address,length,label))
        value=self.values[address]
        if self.changed and label=='CADENCE_CONTEXT_RECHECK':return bytes([1])*length
        if len(value)!=length:raise AssertionError('unbounded season control read')
        return value
    def close(self):self.closed=True


class AnnualCadenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'test-save')

    def seed(self,conn,token,year=2022,family='RECORD_BOOK',grade='LIVE_READ',status='success'):
        # Direct SQL exercises the race guard, not acquisition provenance.
        with conn:
            conn.execute("INSERT OR IGNORE INTO seasons(season_id,season_code) VALUES('s','TEST')")
            conn.execute('''INSERT INTO capture_runs(run_id,season_id,observed_at,source_grade,refresh_family,refresh_period_year,refresh_kind)
                VALUES(?,?,?,?,?,?,?)''',(token,'s','2026-10-24T00:00:00Z',grade,family,year,'BASELINE'))
            conn.execute('''INSERT INTO capture_units(unit_id,run_id,source_key,payload_sha256,unit_status,observed_at)
                VALUES(?,?,?,?,?,?)''',(token,token,'TEST_SQL_CONTROL','0'*64,status,'2026-10-24T00:00:00Z'))

    def test_success_once_retry_after_failure_and_new_year(self):
        with connect(self.db) as c:
            self.seed(c,'failed',status='failed')
            self.assertIsNone(annual_status(c,'RECORD_BOOK',2022))
            self.seed(c,'ok')
            self.assertEqual(annual_status(c,'RECORD_BOOK',2022)['previous_unit_id'],'ok')
            with self.assertRaisesRegex(sqlite3.IntegrityError,'annual refresh already captured'):self.seed(c,'duplicate')
            self.assertIsNone(c.execute("SELECT 1 FROM capture_runs WHERE run_id='duplicate'").fetchone())
            self.seed(c,'next-year',year=2023)
            self.seed(c,'other-family',family='NATIVE_HONOR_STATS')
        other=Path(self.tmp.name)/'other.sqlite';create_database(other,'other-save')
        with connect(other) as c:self.assertIsNone(annual_status(c,'RECORD_BOOK',2022))

    def test_research_replay_does_not_consume_live_period(self):
        with connect(self.db) as c:
            self.seed(c,'research',grade='RESEARCH_FIXTURE')
            self.assertIsNone(annual_status(c,'RECORD_BOOK',2022))
            self.seed(c,'real')
            self.seed(c,'later-research',grade='RESEARCH_FIXTURE')
            self.assertEqual(annual_status(c,'RECORD_BOOK',2022)['previous_unit_id'],'real')

    def test_period_is_game_year_with_all_eight_bits_and_context_recheck(self):
        reader=SeasonControl();self.assertEqual(observed_game_season_year(reader),2101)
        self.assertLess(sum(length for _,length,_ in reader.trace),200)
        with self.assertRaisesRegex(ValueError,'context changed'):observed_game_season_year(SeasonControl(changed=True))

    def test_live_history_requires_matching_period_metadata(self):
        payload={'evidence_grade':'LIVE_READ','source_key':'BOUND_RECORD_BOOK'}
        with self.assertRaisesRegex(ValueError,'requires annual period'):validate_refresh_metadata(payload)
        for value in (True,0,10000,'2022',None):
            with self.assertRaises(ValueError):attach_annual_period(dict(payload),'RECORD_BOOK',value)
        with self.assertRaisesRegex(ValueError,'mismatch'):attach_annual_period(dict(payload),'NATIVE_HONOR_STATS',2022)
        validate_refresh_metadata(attach_annual_period(payload,'RECORD_BOOK',2022))
        validate_refresh_metadata({'evidence_grade':'LIVE_READ','source_key':'BOUND_WORLD'})

    def test_repeated_capture_skips_both_expensive_sources_and_closes_handle(self):
        import award_reader
        import records_reader
        with connect(self.db) as c:
            self.seed(c,'record-period',year=2101)
            self.seed(c,'honor-period',year=2101,family='NATIVE_HONOR_STATS')
        for module,method,collector in ((records_reader,'capture_records','collect_records'),
                (award_reader,'capture_native_honors','collect_native_honors')):
            reader=SeasonControl();out=Path(self.tmp.name)/method
            with patch.object(module,'read_binding',return_value=({'save_id':'test-save'},'0'*64)),\
                    patch.object(module,'bound_database',return_value=self.db),\
                    patch.object(module,'ReadOnlyGameProcess',return_value=reader),\
                    patch.object(module,collector,side_effect=AssertionError('full source must not be reacquired')) as full:
                result=getattr(module,method)(999,'unused','MyLEAGUE0003',out)
            self.assertEqual(result['status'],'already_refreshed');self.assertTrue(reader.closed)
            full.assert_not_called();self.assertFalse(result['full_source_acquisition'])
            self.assertEqual(json.loads((out/'ingest-result.json').read_text())['refresh_period_year'],2101)


if __name__=='__main__':unittest.main()

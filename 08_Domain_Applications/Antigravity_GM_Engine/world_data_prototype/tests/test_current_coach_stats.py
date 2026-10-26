"""Ordinary coach counters: physical annual exclusion and immutable refresh history."""
import copy,json,struct,sys,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from current_coach_stat_reader import collect_current_coach_stats,current_coach_payload,decode_current_stat,COUNTER_COLUMNS
from engine import create_database,connect,ingest_capture
from query import current_coach_stats,staff_card
from observation_scope import query_at
import test_staff as fixture


class Memory:
    module_base=0x140000000
    def __init__(self,changed=None,duplicate=False,empty=False,wins=12):self.calls=[];self.changed=changed;self.duplicate=duplicate;self.empty=empty;self.wins=wins
    def read(self,address,size,label):
        from live_reader import ROSTER_RVA
        self.calls.append((address,size,label))
        if address==self.module_base+ROSTER_RVA:return struct.pack('<Q',0x200000)
        if address==0x200000+19*16:return struct.pack('<QQ',0 if self.empty else 3,0 if self.empty else 0x300000)
        if address==0x200000+21*16:return struct.pack('<QQ',2,0x400000)
        if 0x300000<=address<0x300000+3*352:
            index,off=divmod(address-0x300000,352)
            if off==48:
                raw=['Alice','Bob',''][index].encode('utf-16le');return raw+bytes(80-len(raw))
            if off==216:return struct.pack('<H',100 if index==0 or self.duplicate and index==1 else 101+index)
            if off==136:return struct.pack('<h',-1 if self.changed=='ref' and label.endswith(':RECHECK') else [0,0,5][index])
            raise AssertionError('ordinary source requested annual references or private fields')
        if address==0x400000:
            full=struct.pack('<5H2B',65535,self.wins,8,3,2,237,239)
            if size!=10:raise AssertionError('ordinary source requested annual award bytes')
            return bytes(10) if self.changed=='stats' and label.endswith(':RECHECK') else full[:10]
        raise AssertionError((address,size,label))


class CurrentCoachTests(unittest.TestCase):
    def collect(self,memory=None):
        with patch('current_coach_stat_reader.verify_metadata',return_value=[]),patch('current_coach_stat_reader.verify_semantics_code',return_value={}),patch('current_coach_stat_reader.collect_game_mode',side_effect=lambda reader:fixture.mode()):return collect_current_coach_stats(memory or Memory())
    def payload(self,token='one',stamp='2026-10-26T00:00:00Z',memory=None):
        m,_=self.collect(memory);p=current_coach_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m,[{'sha256':'a'*64,'payload_kind':'SYNTHETIC_CURRENT_COACH'}],stamp,token,{'staff:native:100':'Alice'});p['facts']['staff_members']=[{'staff_id':'staff:native:100','display_name':'Alice'}];return p
    def database(self,tmp,p=None):
        db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
        with connect(db) as conn:ingest_capture(conn,p or self.payload())
        return db
    def test_exact_physical_projection_excludes_other_references_awards_and_player_values(self):
        memory=Memory();m,blobs=self.collect(memory);self.assertEqual(m['annual_other_reference_positions_read'],0);self.assertEqual(m['annual_award_value_bytes_read'],0);self.assertEqual(len(blobs['staff-0.bin']),84);self.assertEqual(len(blobs['stat-0.bin']),10)
        for address,size,label in memory.calls:
            if 0x300000<=address<0x300000+1056:self.assertIn(((address-0x300000)%352,size),((48,80),(136,2),(216,2)))
            self.assertNotIn('PLAYER',label)
        for raw in (bytes(9),bytes(12)):
            with self.assertRaises(ValueError):decode_current_stat(raw)
    def test_shared_reference_missing_source_and_duplicate_uid_stay_explicit(self):
        p=self.payload();rows=p['facts']['native_current_coach_stat_observations'];self.assertEqual(rows[0]['subject_reference_count'],2);self.assertEqual(rows[0]['coach_wins_raw'],12);self.assertIsNone(rows[2]['coach_wins_raw']);self.assertIsNone(rows[2]['source_stat_index']);self.assertEqual(rows[2]['native_allocation_marker_status'],'NOT_OBSERVED');self.assertTrue(all(r['stat_year'] is None for r in rows));self.assertNotIn('refresh_family',p)
        duplicate=self.payload(memory=Memory(duplicate=True));self.assertTrue(all(r['staff_id'] is None for r in duplicate['facts']['native_current_coach_stat_observations']))
    def test_mid_capture_reference_stats_or_progress_change_is_rejected(self):
        for changed in ('ref','stats'):
            with self.subTest(changed=changed),self.assertRaises(ValueError):self.collect(Memory(changed=changed))
        mode=fixture.mode();other=copy.deepcopy(mode);other[0]['season_year']=2023
        with patch('current_coach_stat_reader.verify_metadata',return_value=[]),patch('current_coach_stat_reader.verify_semantics_code',return_value={}),patch('current_coach_stat_reader.collect_game_mode',side_effect=[mode,other]),self.assertRaises(ValueError):collect_current_coach_stats(Memory())
    def test_partial_source_rows_and_annual_field_injection_fail(self):
        for broken in ('directory','stats','share','award'):
            m,_=self.collect()
            if broken=='directory':m['staff'].pop()
            if broken=='stats':m['stats'].clear()
            if broken=='share':m['stats'][0]['subject_reference_count']=1
            if broken=='award':m['stats'][0]['coach_won_title_raw']=1
            with self.subTest(broken=broken),self.assertRaises(ValueError):current_coach_payload({'save_id':'fixture','native_save_filename':'x'},m,[],'2026-10-26T00:00:00Z','bad',{})
    def test_two_ordinary_same_year_refreshes_preserve_both_observations_and_asof(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp);p=self.payload('two','2026-10-27T00:00:00Z',Memory(wins=13))
            with connect(db) as conn:ingest_capture(conn,p)
            self.assertEqual(current_coach_stats(db)['records'][0]['coach_wins_raw'],13);old=query_at(db,'2026-10-26T12:00:00Z','current_coach_stats')['result'];self.assertEqual(old['records'][0]['coach_wins_raw'],12);self.assertEqual(staff_card(db,'staff:native:100')['native_increment_stats']['records'][0]['coach_wins_raw'],13)
            with connect(db,True) as conn:self.assertEqual(conn.execute('SELECT count(*) FROM capture_runs WHERE refresh_family IS NOT NULL').fetchone()[0],0);self.assertEqual(conn.execute('SELECT count(*) FROM native_current_coach_stat_observations').fetchone()[0],6)
    def test_query_default_resolved_paging_all_sources_cli_and_before_source(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp);page=current_coach_stats(db,limit=1);self.assertTrue(page['has_more']);unit=page['source']['unit_id'];self.assertEqual(len(current_coach_stats(db,resolved_only=False)['records']),3);self.assertEqual(current_coach_stats(db,unit_id=unit,after_index=0)['records'][0]['source_staff_index'],1)
            with self.assertRaises(ValueError):current_coach_stats(db,after_index=0)
            self.assertEqual(query_at(db,'2026-10-25T23:59:59Z','current_coach_stats')['result']['status'],'NOT_OBSERVED')
            import cli
            output=StringIO()
            with patch.object(sys,'argv',['cli.py','coach-stats',str(db),'--all-sources','--as-of','2026-10-26T00:00:00Z']),redirect_stdout(output):cli.main()
            self.assertEqual(len(json.loads(output.getvalue())['result']['records']),3)
    def test_sql_rejects_partial_or_invented_year_and_rolls_back_unit(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp)
            for broken in ('partial','year'):
                p=self.payload('bad-'+broken,'2026-10-27T00:00:00Z');row=p['facts']['native_current_coach_stat_observations'][0]
                if broken=='partial':row['source_stat_index']=None
                else:row['stat_year']=2022
                with connect(db) as conn:
                    with self.assertRaises(Exception):ingest_capture(conn,p)
                    self.assertEqual(conn.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)
    def test_empty_source_is_observed_without_invented_people_or_zero_counters(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp,self.payload(memory=Memory(empty=True)));value=current_coach_stats(db,resolved_only=False);self.assertEqual(value['status'],'OBSERVED');self.assertEqual(value['source_staff_count'],0);self.assertEqual(value['records'],[])


if __name__=='__main__':unittest.main()

"""Annual coach history source tests; fixture success is not live/UI evidence."""
import copy,json,struct,sys,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from staff_history_reader import collect_staff_history,staff_history_payload,classify_reference,decode_coach_stat,capture_staff_history
from engine import create_database,connect,ingest_capture
from query import native_staff_history
from observation_scope import query_at
import test_staff as fixture


class Memory:
    module_base=0x140000000
    def __init__(self,changed=False,duplicate=False):
        self.calls=[];self.changed=changed;self.duplicate=duplicate;self.refs=[[-1]*40,[-1]*40];self.refs[0][2]=0;self.refs[0][3]=1;self.refs[1][1]=0;self.refs[1][4]=5
    def read(self,address,size,label):
        self.calls.append((address,size,label))
        from live_reader import ROSTER_RVA
        if address==self.module_base+ROSTER_RVA:return struct.pack('<Q',0x200000)
        if address==0x200000+19*16:return struct.pack('<QQ',2,0x300000)
        if address==0x200000+21*16:return struct.pack('<QQ',3,0x400000)
        if 0x300000<=address<0x300000+2*352:
            index,off=divmod(address-0x300000,352)
            if off==48:
                raw=['Alice','Bob'][index].encode('utf-16le');return raw+bytes(80-len(raw))
            if off==136:
                value=struct.pack('<40hH',*self.refs[index],100 if index==0 or self.duplicate else 101)
                return bytes(82) if self.changed and label.endswith(':RECHECK') else value
        if address in (0x400000,0x40000c):return struct.pack('<5H2B',65535,11,22,33,44,255,7)
        raise AssertionError((address,size,label))


class StaffHistoryTests(unittest.TestCase):
    def collect(self,memory=None):
        with patch('staff_history_reader.verify_metadata',return_value=[]),patch('staff_history_reader.collect_game_mode',side_effect=lambda reader:fixture.mode()):return collect_staff_history(memory or Memory())
    def payload(self,token='one',stamp='2026-10-26T00:00:00Z',memory=None):
        m,_=self.collect(memory);p=staff_history_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m,[{'sha256':'a'*64,'payload_kind':'SYNTHETIC_STAFF_HISTORY'}],stamp,token,{'staff:native:100':'Alice'});p['facts']['staff_members']=[{'staff_id':'staff:native:100','display_name':'Alice'}];return p
    def db(self,tmp):
        db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
        with connect(db) as conn:ingest_capture(conn,self.payload())
        return db
    def test_signed_references_zero_and_after_negative_are_independent(self):
        m,_=self.collect();self.assertEqual([r['source_stat_index'] for r in m['stats']],[0,1]);self.assertEqual(m['stats'][0]['subject_reference_count'],2);self.assertEqual(classify_reference(-32768,3),'NEGATIVE_NATIVE_GETTER_REJECTED');self.assertTrue(classify_reference(0,3).startswith('RESOLVED'));self.assertEqual(classify_reference(3,3),'OUTSIDE_CURRENT_NATIVE_BANK')
        p=self.payload();self.assertEqual(len(p['facts']['native_staff_stat_links']),80);self.assertIsNotNone(p['facts']['native_staff_stat_links'][2]['coach_stat_id']);self.assertIsNone(p['facts']['native_staff_stat_links'][0]['coach_stat_id'])
    def test_private_bytes_never_requested_and_control_changes_rejected(self):
        memory=Memory();self.collect(memory)
        for address,size,label in memory.calls:
            if 0x300000<=address<0x300000+704:
                off=(address-0x300000)%352;self.assertIn((off,size),((48,80),(136,82)))
        with self.assertRaises(ValueError):self.collect(Memory(changed=True))
    def test_all_fields_stored_without_flag_boolean_year_or_ownership_invention(self):
        raw=struct.pack('<5H2B',65535,11,22,33,44,255,7);d=decode_coach_stat(raw);self.assertEqual(d['coach_won_title_raw'],255);self.assertEqual(d['coach_won_coach_of_the_year_raw'],7)
        m,_=self.collect();self.assertTrue(all(r['stat_year'] is None for r in m['stats']));self.assertEqual(m['stats'][0]['subject_reference_count'],2)
        p=self.payload(memory=Memory(duplicate=True));self.assertTrue(all(r['staff_id'] is None for r in p['facts']['native_staff_history_subjects']))
    def test_incomplete_references_stats_and_wrong_shared_counts_rejected(self):
        for broken in ('refs','stats','count','year'):
            m,_=self.collect()
            if broken=='refs':m['staff'][0]['references'].pop()
            if broken=='stats':m['stats'].pop()
            if broken=='count':m['stats'][0]['subject_reference_count']=1
            if broken=='year':m['stats'][0]['stat_year']=2021
            with self.subTest(broken=broken),self.assertRaises(ValueError):staff_history_payload({'save_id':'fixture','native_save_filename':'x'},m,[],'2026-10-26T00:00:00Z','bad',{})
    def test_typed_query_paging_asof_cli_and_immutable_history(self):
        with TemporaryDirectory() as tmp:
            db=self.db(tmp);r=native_staff_history(db,limit=1);self.assertTrue(r['has_more']);self.assertEqual(len(r['records'][0]['references']),40);unit=r['source']['unit_id'];self.assertEqual(native_staff_history(db,unit_id=unit,after_index=0)['records'][0]['source_staff_index'],1)
            with self.assertRaises(ValueError):native_staff_history(db,after_index=0)
            self.assertEqual(query_at(db,'2026-10-25T23:59:59Z','native_staff_history')['result']['status'],'NOT_OBSERVED')
            self.assertEqual(native_staff_history(db,staff_id='staff:native:100')['records'][0]['observed_name'],'Alice')
            import cli
            output=StringIO()
            with patch.object(sys,'argv',['cli.py','staff-history',str(db),'--limit','1','--as-of','2026-10-26T00:00:00Z']),redirect_stdout(output):cli.main()
            self.assertEqual(json.loads(output.getvalue())['result']['source_staff_count'],2)
            with connect(db) as conn:
                with self.assertRaises(Exception):conn.execute('UPDATE native_coach_stat_observations SET coach_wins_raw=999')
    def test_cross_unit_stat_link_rolls_back_and_annual_bucket_is_explicit(self):
        with TemporaryDirectory() as tmp:
            db=self.db(tmp);p=self.payload('two','2026-10-26T01:00:00Z');p['facts']['native_staff_stat_links'][2]['coach_stat_id']='native-staff-history:one:stat:0'
            with connect(db) as conn:
                with self.assertRaises(Exception):ingest_capture(conn,p)
                self.assertEqual(conn.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)
                row=conn.execute('SELECT refresh_family,refresh_period_year FROM capture_runs').fetchone();self.assertEqual(tuple(row),('STAFF_SEASON_HISTORY',2022))
    def test_same_year_skip_never_reads_staff_history_values(self):
        from live_world import initialize_save
        with TemporaryDirectory() as tmp:
            root=Path(tmp);native=root/'MyLEAGUE0003';native.write_bytes(b'SYNTHETIC');save=root/'save';initialize_save(save,'fixture',native)
            reader=type('Reader',(),{'trace':[],'close':lambda self:None})()
            with patch('staff_history_reader.ReadOnlyGameProcess',return_value=reader),patch('staff_history_reader.prepare_annual_capture',return_value=(2022,{'status':'already_refreshed','previous_unit_id':'fixture'})),patch('staff_history_reader.collect_staff_history') as collect:
                result=capture_staff_history(123,save,'MyLEAGUE0003',root/'skip')
            collect.assert_not_called();self.assertEqual(result['status'],'already_refreshed')


if __name__=='__main__':unittest.main()

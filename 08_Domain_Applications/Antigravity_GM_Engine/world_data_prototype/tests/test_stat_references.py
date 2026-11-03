"""Independent Native stat slots, source-unit isolation and historical query rules."""
import copy,json,struct,sys,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
import test_honors as honors_fixture
from engine import create_database,connect,ingest_capture
from query import native_player_seasons
from observation_scope import query_at
from stat_reference import resolve_reference,verify_native_reference_contract,PROFILE_PATH

class StatReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'fixture')
        self.payload=honors_fixture.HonorsTests().payload();self.source=min(self.payload['facts']['native_player_sources'],key=lambda r:r['source_player_index']);self.source_index=self.source['source_player_index']
        stats=self.payload['facts']['native_player_stat_observations'];model=stats[0]
        for index,year in ((0,2010),(32756,2007)):
            stats[:]=[r for r in stats if r['source_stat_index']!=index];row=copy.deepcopy(model);row.update(stat_observation_id='extra:'+str(index),source_stat_index=index,stat_year=year,compact_year_raw=year-1900);stats.append(row)
        links={r['history_slot_index']:r for r in self.payload['facts']['native_player_stat_links'] if r['player_source_id']==self.source['player_source_id']}
        for position,index,status,stat in ((1,0,'ZERO_HISTORY_SLOT_UNVERIFIED',None),(2,65535,'SENTINEL_NO_ACCEPTED_LINK',None),(3,32756,'HISTORY_INDEX_AFTER_EMPTY_SLOT','extra:32756'),(4,32768,'OUTSIDE_NATIVE_STAT_COUNT',None),(5,30000,'OUTSIDE_NATIVE_STAT_COUNT',None)):
            links[position].update(native_stat_index_raw=index,link_status=status,stat_observation_id=stat)
        with connect(self.db) as c:ingest_capture(c,self.payload)

    def read(self,**kwargs):return native_player_seasons(self.db,source_index=self.source_index,**kwargs)

    def test_zero_after_gap_and_non_sentinel_32756_resolve_without_rewriting_capture(self):
        found=self.read();row=found['records'][0];refs={r['array_position']:r for r in row['stat_references']}
        self.assertTrue(row['reference_array_complete']);self.assertEqual(len(refs),25)
        self.assertEqual(refs[1]['resolution_status'],'RESOLVED_SAME_UNIT_NATIVE_RECORD');self.assertEqual(refs[1]['record']['source_stat_index'],0)
        self.assertEqual(refs[1]['capture_link_status'],'ZERO_HISTORY_SLOT_UNVERIFIED');self.assertIsNone(refs[1]['capture_stat_observation_id'])
        self.assertEqual(refs[3]['record']['source_stat_index'],32756);self.assertTrue(all(r['phase_code'] is None for r in refs.values()))
        self.assertEqual(refs[2]['resolution_status'],'NEGATIVE_SIGNED_INDEX_REJECTED_BY_NATIVE_GETTER');self.assertIsNone(refs[2]['record'])
        self.assertEqual(refs[4]['resolution_status'],'NEGATIVE_SIGNED_INDEX_REJECTED_BY_NATIVE_GETTER');self.assertEqual(refs[5]['resolution_status'],'NO_SAME_UNIT_SOURCE_RECORD')

    def test_year_filter_uses_raw_record_year_without_career_aggregation(self):
        found=self.read(year=2010);refs=found['records'][0]['stat_references'];self.assertTrue(refs);self.assertTrue(all(r['record']['stat_year']==2010 for r in refs));self.assertIn(1,[r['array_position'] for r in refs])
        self.assertEqual(self.read(year=2155)['records'],[])

    def test_shared_references_retain_each_source_subject(self):
        found=native_player_seasons(self.db,limit=100);self.assertGreater(len(found['records']),1)
        self.assertEqual(len({r['source_player_index'] for r in found['records']}),len(found['records']));self.assertIn('shared',found['ownership_and_allocation'])

    def test_pagination_requires_pinned_unit_and_never_falls_back(self):
        first=native_player_seasons(self.db,limit=1);self.assertTrue(first['has_more'])
        with self.assertRaisesRegex(ValueError,'pin unit_id'):native_player_seasons(self.db,after_index=first['next_after_index'])
        second=native_player_seasons(self.db,unit_id=first['unit']['unit_id'],after_index=first['next_after_index'],limit=1);self.assertGreater(second['records'][0]['source_player_index'],first['records'][0]['source_player_index'])
        self.assertEqual(native_player_seasons(self.db,unit_id='absent')['status'],'NOT_OBSERVED')

    def test_new_unit_utc_recency_and_old_cutoff_do_not_mix_records(self):
        newer=honors_fixture.HonorsTests().payload(token='newer');newer['observed_at']='2026-10-24T23:30:00-02:00'
        with connect(self.db) as c:ingest_capture(c,newer)
        self.assertEqual(native_player_seasons(self.db)['unit']['unit_id'],newer['unit_id'])
        old=query_at(self.db,'2026-10-25T00:30:00Z','native_player_seasons')['result'];self.assertEqual(old['unit']['unit_id'],self.payload['unit_id'])
        hidden=query_at(self.db,'2000-01-01T00:00:00Z','native_player_seasons')['result'];self.assertEqual(hidden['status'],'NOT_OBSERVED')
        pinned=self.read(unit_id=self.payload['unit_id']);self.assertEqual(pinned['records'][0]['stat_references'][1]['record']['stat_year'],2010)

    def test_query_is_read_only_and_exposes_no_restricted_material(self):
        before=self.db.read_bytes();out=json.dumps(self.read()).lower();self.assertEqual(before,self.db.read_bytes())
        for field in ('potential','payload_ref','raw_player','artifact_sha256'):self.assertNotIn(field,out)

    def test_invalid_arguments_and_indices_are_rejected_or_withheld(self):
        for kwargs in ({'limit':0},{'limit':True},{'after_index':-2},{'source_index':False},{'year':True},{'year':2156}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):native_player_seasons(self.db,**kwargs)
        self.assertEqual(resolve_reference(0,25,{}),'OUTSIDE_VERIFIED_ARRAY_DIMENSION')
        for index in (-1,65536,True):
            with self.assertRaises(ValueError):resolve_reference(index,0,None)

    def test_metadata_code_contract_rejects_changed_code_without_getter_calls(self):
        profile=json.loads(PROFILE_PATH.read_bytes());field={'name_crc':profile['season_stats_name_crc'],**profile['season_stats_field'],'array_dimension_control_hex':profile['array_dimension_control_hex']}
        class Memory:
            module_base=0x140000000
            def read(self,address,size,label):
                if address==self.module_base+profile['roster_pointer_rva']:return struct.pack('<Q',0x100000)
                if address==0x100000+24*16:return struct.pack('<QQ',100,0x200000)
                return bytes.fromhex(next(w['code_hex'] for w in profile['code_windows'] if self.module_base+w['rva']==address))
        with patch('award_reader.read_native_fields',return_value={'fields':[field],'status':'FIXTURE_METADATA'}):
            self.assertEqual(verify_native_reference_contract(Memory())['getter_invocations'],0)
            class Changed(Memory):
                def read(self,address,size,label):return b'\0'*size
            with self.assertRaisesRegex(ValueError,'code changed'):verify_native_reference_contract(Changed())

    def test_cli_historical_query_uses_same_source_scope(self):
        import cli
        out=StringIO()
        with patch.object(sys,'argv',['cli','native-player-seasons',str(self.db),'--source-index',str(self.source_index),'--year','2010','--as-of','2026-10-25T00:30:00Z']),redirect_stdout(out):cli.main()
        parsed=json.loads(out.getvalue());self.assertEqual(parsed['result']['unit']['unit_id'],self.payload['unit_id']);self.assertTrue(parsed['result']['records'])

if __name__=='__main__':unittest.main()

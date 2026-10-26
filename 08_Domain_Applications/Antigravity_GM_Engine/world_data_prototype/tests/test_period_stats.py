"""Current selector, same-unit stat facts, missing references and annual separation."""
import copy,json,struct,sys,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
import test_game_mode as mode_fixture
from game_mode_reader import decode_game_mode
from period_stats_reader import collect_period_stats,period_stats_payload,period_projection_ranges,ordinary_stat_record,STAT_PROFILE
from award_reader import AWARD_COLUMNS
from engine import create_database,connect,ingest_capture
from query import current_period_stats,native_honors
from observation_scope import query_at
from live_world import RESTRICTED_PLAYER_RANGES

def stat_raw(year=122):
    raw=bytearray(48)
    for name,value in (('CompactYear',year),('GamesPlayed',2),('FieldGoalsMade',3),('ThreePointShotsMade',1),('FreeThrowsMade',2),('TotalPoints',9),('MVP',1)):
        f=STAT_PROFILE['stat_fields'][name];off=f['offset'];size=f['size'];shift=f['start_bit'];mask=((1<<f['width'])-1)<<shift;word=int.from_bytes(raw[off:off+size],'little');raw[off:off+size]=((word&~mask)|(value<<shift)).to_bytes(size,'little')
    return bytes(raw)

class PeriodMemory:
    module_base=0x140000000
    def __init__(self,indices=(0,65535),position=0,year=122,count=10,changed=None):
        from live_reader import ROSTER_RVA
        self.root=0x200000;self.pointer_address=self.module_base+ROSTER_RVA;self.position=position;self.indices=indices;self.count=count;self.stat=stat_raw(year);self.changed=changed;self.calls=[];self.players=[];self.projections=[]
        for i,index in enumerate(indices):
            name=('Alice','Bob')[i];raw=bytearray(1264);raw[40:40+len(name)*2]=name.encode('utf-16le');struct.pack_into('<H',raw,244,i+1);struct.pack_into('<I',raw,760,i+10);struct.pack_into('<H',raw,252+position*2,index);self.projections.append(bytes(raw))
            self.players.append({'source_player_index':i,'native_unique_id_raw':i+1,'preserved_id_raw':i+10,'observed_name':name,'name_status':'OBSERVED_UTF16_PREFIX','native_team_id':0 if i==0 else None,'current_core_roster_status':'CURRENT_CORE_ROSTER' if i==0 else 'NOT_CURRENT_CORE_ROSTER','current_roster_slot':0 if i==0 else None})
    def pool(self,reader,*,ranges,metadata):
        manifest={'season_year':2022,'descriptors':{1:{'count':2,'address':0x100000,'stride':1264},8:{'count':32,'address':0x400000,'stride':4696}},'players':self.players,'core_team_pointer_map':{},'projection_ranges':ranges,'projection_stride':sum(b-a for a,b in ranges),'restricted_player_bytes_read':0,'game_writes':False}
        return manifest,{'player-detail-public-projections.bin':b''.join(b''.join(raw[a:b] for a,b in ranges) for raw in self.projections)}
    def mode(self,reader):
        period=29 if self.position==0 else 28
        if self.changed=='mode' and self.calls:period=30 if self.position==0 else 29
        raw=mode_fixture.prefix(period);return {'season_year':2022,'observation':decode_game_mode(raw)},{'game-mode-public-prefix.bin':raw}
    def read(self,address,size,label):
        self.calls.append((address,size,label))
        if address==self.pointer_address:return struct.pack('<Q',self.root)
        if address==self.root+24*16:return struct.pack('<QQ',self.count,0x300000)
        if address==self.root+16:return struct.pack('<QQ',2,0x100000)
        if address==self.root+8*16:return struct.pack('<QQ',32,0x400000)
        if label.startswith('PERIOD_STAT_RECORD'):
            return bytes(48) if self.changed=='stat' and 'RECHECK' in label else self.stat
        if label.startswith('PERIOD_STAT_SUBJECT_RECHECK'):
            index=(address-0x100000)//1264;offset=(address-0x100000)%1264;raw=self.projections[index][offset:offset+size]
            return bytes(size) if self.changed=='subject' else raw
        raise AssertionError('unexpected source read')

class PeriodStatsTests(unittest.TestCase):
    def collect(self,memory):
        with patch('period_stats_reader.collect_game_mode',side_effect=memory.mode),patch('period_stats_reader.verify_period_stat_metadata',return_value={'metadata':[]}),patch('period_stats_reader.collect_public_player_pool',side_effect=memory.pool):return collect_period_stats(memory)
    def payload(self,m=None,token='one',stamp='2026-10-25T00:00:00Z'):
        if m is None:m=self.collect(PeriodMemory())[0]
        payload=period_stats_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m,[{'sha256':'a'*64,'payload_kind':'SYNTHETIC_PERIOD_SOURCE'}],stamp,token,{'player:native:10':'Alice'})
        payload['facts']['players']=[{'player_id':'player:native:10','display_name':'Alice'}];return payload
    def database(self,tmp,payload):
        db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
        with connect(db) as c:ingest_capture(c,payload)
        return db

    def test_projection_reads_only_identity_and_one_selected_reference(self):
        for position in (0,24):
            ranges=period_projection_ranges(position);self.assertEqual(sum(b-a for a,b in ranges),96);self.assertIn((252+position*2,254+position*2),ranges);self.assertFalse(any(a<hi and lo<b for a,b in ranges for lo,hi in RESTRICTED_PLAYER_RANGES))
        for position in (1,25,True,None):
            with self.assertRaises(ValueError):period_projection_ranges(position)

    def test_current_selector_zero_and_special_slot24_keep_native_year(self):
        m,blobs=self.collect(PeriodMemory(position=24,year=0));self.assertEqual(m['selected_array_position'],24);self.assertEqual(m['stat_records'][0]['stat_year'],1900);self.assertEqual(m['season_year'],2022)
        with TemporaryDirectory() as tmp:
            db=self.database(tmp,self.payload(m));row=current_period_stats(db)['records'][0];self.assertEqual(row['record']['stat_year'],1900);self.assertIn('DIFFERS',row['record_year_status']);self.assertIsNone(row['phase_code']);self.assertEqual(row['selected_reference']['history_slot_index'],24)

    def test_shared_zero_index_is_read_once_then_rechecked_and_keeps_two_subjects(self):
        memory=PeriodMemory(indices=(0,0));m,_=self.collect(memory);self.assertEqual(len(m['stat_records']),1);self.assertEqual(len(m['stat_links']),2);self.assertEqual(sum(label.startswith('PERIOD_STAT_RECORD') for _,_,label in memory.calls),2)
        with TemporaryDirectory() as tmp:
            db=self.database(tmp,self.payload(m));all_sources=current_period_stats(db,current_roster_only=False)['records'];self.assertEqual(len(all_sources),2);self.assertEqual(all_sources[0]['record']['stat_observation_id'],all_sources[1]['record']['stat_observation_id'])

    def test_negative_outside_and_32756_non_sentinel_follow_native_bounds(self):
        m,_=self.collect(PeriodMemory(indices=(32768,20),count=10));self.assertEqual(m['stat_records'],[]);self.assertEqual([x['link_status'] for x in m['stat_links']],['NEGATIVE_SIGNED_INDEX_REJECTED_BY_NATIVE_GETTER','OUTSIDE_CURRENT_NATIVE_STAT_COUNT'])
        m,_=self.collect(PeriodMemory(indices=(32756,65535),count=40000));self.assertEqual(m['stat_records'][0]['source_stat_index'],32756)
        with TemporaryDirectory() as tmp:
            db=self.database(tmp,self.payload(self.collect(PeriodMemory(indices=(65535,65535)))[0]));self.assertIsNone(current_period_stats(db)['records'][0]['record'])

    def test_changed_stat_subject_or_mode_rejects_entire_acquisition(self):
        for changed in ('stat','subject','mode'):
            with self.subTest(changed=changed),self.assertRaisesRegex(ValueError,'changed'):self.collect(PeriodMemory(changed=changed))

    def test_payload_rejects_wrong_slot_duplicate_missing_columns_and_annual_flags(self):
        original=self.collect(PeriodMemory())[0]
        for change in ('slot','duplicate','column','award'):
            m=copy.deepcopy(original)
            if change=='slot':m['stat_links'][0]['history_slot_index']=24
            if change=='duplicate':m['stat_links'][1]=copy.deepcopy(m['stat_links'][0])
            if change=='column':m['stat_records'][0].pop('points_raw')
            if change=='award':m['stat_records'][0]['mvp_raw']=1
            with self.subTest(change=change),self.assertRaises(ValueError):self.payload(m)

    def test_award_bits_are_not_imported_or_publicly_exposed_by_ordinary_source(self):
        self.assertNotIn('mvp_raw',ordinary_stat_record(stat_raw()))
        with TemporaryDirectory() as tmp:
            db=self.database(tmp,self.payload());out=current_period_stats(db);text=json.dumps(out).lower()
            for key in AWARD_COLUMNS:self.assertNotIn(key,text)
            self.assertNotIn('potential',text);self.assertNotIn('payload_ref',text)
            with connect(db,True) as c:self.assertTrue(all(row[0] is None for row in c.execute('SELECT mvp_raw FROM native_player_stat_observations')))
            self.assertEqual(native_honors(db)['status'],'NOT_OBSERVED')

    def test_source_unit_pages_roster_filter_and_cutoffs_do_not_mix(self):
        with TemporaryDirectory() as tmp:
            one=self.payload();db=self.database(tmp,one);two=self.payload(self.collect(PeriodMemory(position=24,year=0))[0],'two','2026-10-24T23:30:00-02:00')
            with connect(db) as c:ingest_capture(c,two)
            latest=current_period_stats(db);self.assertEqual(latest['unit']['unit_id'],two['unit_id']);self.assertEqual(len(latest['records']),1)
            old=query_at(db,'2026-10-25T00:30:00Z','current_period_stats')['result'];self.assertEqual(old['unit']['unit_id'],one['unit_id']);self.assertEqual(old['game_mode']['current_stat_array_position'],0)
            self.assertEqual(query_at(db,'2000-01-01T00:00:00Z','current_period_stats')['result']['records'],[])
            page=current_period_stats(db,current_roster_only=False,limit=1);self.assertTrue(page['has_more'])
            with self.assertRaises(ValueError):current_period_stats(db,after_index=page['next_after_index'])
            second=current_period_stats(db,current_roster_only=False,unit_id=page['unit']['unit_id'],after_index=page['next_after_index'],limit=1);self.assertGreater(second['records'][0]['source_player_index'],page['records'][0]['source_player_index'])

    def test_missing_same_unit_context_is_rejected_without_fallback(self):
        payload=self.payload();payload['facts']['game_mode_observations']=[]
        with TemporaryDirectory() as tmp:
            db=self.database(tmp,payload)
            with self.assertRaisesRegex(ValueError,'same-unit Native mode'):current_period_stats(db)
            self.assertEqual(current_period_stats(db,unit_id='absent')['status'],'NOT_OBSERVED')

    def test_invalid_query_args_and_cli_use_same_public_source(self):
        import cli
        with TemporaryDirectory() as tmp:
            db=self.database(tmp,self.payload());out=StringIO()
            with patch.object(sys,'argv',['cli','current-period-stats',str(db),'--all-sources','--as-of','2026-10-25T00:30:00Z']),redirect_stdout(out):cli.main()
            result=json.loads(out.getvalue())['result'];self.assertEqual(len(result['records']),2);self.assertEqual(result['unit']['source_grade'],'RESEARCH_FIXTURE')
            for kwargs in ({'limit':0},{'source_index':False},{'current_roster_only':None},{'after_index':-2}):
                with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):current_period_stats(db,**kwargs)

if __name__=='__main__':unittest.main()

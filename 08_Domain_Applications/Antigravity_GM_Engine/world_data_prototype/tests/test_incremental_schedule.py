"""Frozen-source reuse preserves age; mock memory is not live Native evidence."""
from copy import deepcopy
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib,struct,sys,unittest,sqlite3
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from test_schedule import ScheduleMemory
from test_live_world import WorldMemory
from schedule_reader import collect_schedule,schedule_facts,frozen_game_sources
from live_world import collect_world,world_payload
from engine import create_database,connect,_insert,ingest_capture
from schema_model import TABLES
from query import game_box
from observation_scope import query_at
from readers import _module

class CurrentRosterMemory(WorldMemory):
    def __init__(self):
        super().__init__();core=sorted((set(range(30))-{7})|{31});team_bytes=bytearray(4696*30)
        for i,tid in enumerate(core):
            record=memoryview(team_bytes)[i*4696:(i+1)*4696];struct.pack_into('<H',record,0xCA8,tid)
            record[0x2B4:0x2B4+40]='Team'.encode('utf-16le').ljust(40,b'\0');record[0x2E6:0x2E6+36]='City'.encode('utf-16le').ljust(36,b'\0')
        players=bytearray(self.segments[self.players]);active=list(range(0,self.player_count,2))
        for pos,index in enumerate(active):
            owner=0 if pos<13 else 1;slot=pos%13;pointer=self.teams+owner*4696
            struct.pack_into('<Q',team_bytes,owner*4696+slot*8,self.players+index*1264)
            struct.pack_into('<Q',players,index*1264+96,pointer);struct.pack_into('<Q',players,index*1264+168,pointer)
        self.segments.pop(self.teams,None);self.segments.pop(self.teams+4696,None);self.segments[self.teams]=bytes(team_bytes);self.segments[self.players]=bytes(players)
        self.segments[self.root+8*16]=struct.pack('<QQ',30,self.teams)

class IncrementalScheduleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'fixture')
    def fixture_source(self,unit='full',grade='LIVE_READ',partial=False,stamp='2026-10-24T00:00:00Z'):
        memory=ScheduleMemory();found=collect_schedule(memory);decoder=_module('boxscore_decoder').BoxScoreDecoder;full=decoder.decode_full_boxscore(memory.game,found['boxes'][0])
        ids={p['player_id'] for side in ('home_players','away_players') for p in full[side] if p['in_use']};facts=schedule_facts(found,{'season_id':'s'},ids)
        facts['teams']=[{'team_id':'team:native:'+str(full[side+'_team_id']),'native_team_id':str(full[side+'_team_id'])} for side in ('home','away')]
        facts['players']=[{'player_id':'player:native:'+str(n),'native_player_id':str(n),'display_name':'Fixture '+str(n)} for n in ids]
        if partial:facts['player_game_boxes']=facts['player_game_boxes'][1:]
        # Synthetic ledger setup bypasses the acquisition API only to exercise cache validation.
        with connect(self.db) as conn:
            conn.execute("INSERT OR IGNORE INTO seasons(season_id,season_code) VALUES('s','fixture')")
            _insert(conn,'capture_runs',{'run_id':unit,'season_id':'s','observed_at':stamp,'source_grade':grade})
            _insert(conn,'capture_units',{'unit_id':unit,'run_id':unit,'source_key':'BOUND_COMPLETE_DESCRIPTOR_SCHEDULE_AND_PLAYERS','payload_sha256':'0'*64,'unit_status':'success','observed_at':stamp})
            for table,spec in TABLES.items():
                for index,value in enumerate(facts.get(table,[])):
                    row=dict(value)
                    if any(c.name=='unit_id' for c in spec.columns):row['unit_id']=unit
                    if spec.key not in row:row[spec.key]=unit+':'+table+':'+str(index)
                    if table in ('teams','players','games'):
                        if conn.execute('SELECT 1 FROM '+table+' WHERE '+spec.key+'=?',(row[spec.key],)).fetchone():continue
                    _insert(conn,table,row)
        return memory,found
    def test_matching_header_skips_native_box_reads_and_emits_explicit_reuse(self):
        memory=ScheduleMemory();cache={1:{'unit_id':'prior','header_sha256':hashlib.sha256(memory.game).hexdigest()}}
        found=collect_schedule(memory,frozen_cache=cache);self.assertEqual(found['boxes'],{});self.assertEqual(found['manifest']['frozen_boxes_reused'],1)
        self.assertFalse(any('FINAL_BOX' in label or 'BOX_RECHECK' in label for _,_,label in memory.calls))
        facts=schedule_facts(found,{'season_id':'s'},set());self.assertEqual(facts['player_game_boxes'],[]);self.assertEqual(len(facts['game_state_observations']),1)
        check=next(r for r in facts['game_source_checks'] if r['game_status_raw']==2);self.assertEqual(check['prior_full_unit_id'],'prior');self.assertNotIn('box_sha256',check)
    def test_changed_header_fingerprint_requires_full_native_box(self):
        found=collect_schedule(ScheduleMemory(),frozen_cache={1:{'unit_id':'prior','header_sha256':'0'*64}});self.assertEqual(len(found['boxes']),1);self.assertEqual(found['reused'],{})
    def test_cache_requires_live_complete_mapping_and_never_falls_back_from_new_partial(self):
        self.fixture_source();self.assertIn(1,frozen_game_sources(self.db,'s'))
        self.fixture_source('partial',partial=True,stamp='2026-10-25T00:00:00Z');self.assertEqual(frozen_game_sources(self.db,'s'),{})
    def test_research_fixture_is_not_a_live_frozen_cache(self):
        self.fixture_source(grade='RESEARCH_FIXTURE');self.assertEqual(frozen_game_sources(self.db,'s'),{})
    def add_reuse(self,hash_value=None,game='s:game:1'):
        with connect(self.db) as conn:
            _insert(conn,'capture_runs',{'run_id':'check','season_id':'s','observed_at':'2026-10-25T00:00:00Z','source_grade':'LIVE_READ'})
            _insert(conn,'capture_units',{'unit_id':'check','run_id':'check','source_key':'BOUND_COMPLETE_DESCRIPTOR_SCHEDULE_AND_PLAYERS','payload_sha256':'1'*64,'unit_status':'success','observed_at':'2026-10-25T00:00:00Z'})
            old=conn.execute("SELECT header_sha256 FROM game_source_checks WHERE game_id='s:game:1'").fetchone()[0]
            _insert(conn,'game_source_checks',{'check_id':'new-check','game_id':game,'unit_id':'check','header_sha256':hash_value or old,'box_mode':'REUSED_FROZEN_BOX','prior_full_unit_id':'full','game_status_raw':2,'reuse_basis':'SYNTHETIC_HEADER_CHECK_ONLY'})
    def test_header_reuse_does_not_refresh_box_source_time_or_mix_units(self):
        self.fixture_source();self.add_reuse();value=game_box(self.db,'s:game:1')
        self.assertEqual(value['selected_unit_id'],'full');self.assertEqual(value['capture']['observed_at'],'2026-10-24T00:00:00Z');self.assertEqual(value['latest_header_check']['unit_id'],'check')
        for key in ('states','period_scores','player_boxes','team_boxes'):self.assertTrue(all(r['unit_id']=='full' for r in value[key]))
        old=query_at(self.db,'2026-10-24T00:00:00Z','game_box','s:game:1')['result'];self.assertEqual(old['latest_header_check']['unit_id'],'full')
    def test_reuse_wrong_hash_or_other_game_is_rejected_atomically(self):
        self.fixture_source()
        for kwargs in ({'hash_value':'0'*64},{'game':'s:game:2'}):
            with self.subTest(kwargs=kwargs),self.assertRaisesRegex(sqlite3.IntegrityError,'matching frozen full source'):self.add_reuse(**kwargs)
        with connect(self.db,True) as conn:self.assertIsNone(conn.execute("SELECT 1 FROM capture_units WHERE unit_id='check'").fetchone())
    def test_current_player_context_has_no_historical_game_box_anchor(self):
        memory=CurrentRosterMemory()
        with patch('cadence.observed_game_season_year',return_value=2022):found,context,blobs=collect_world(memory,None,target_native_ids=set(),current_context_only=True)
        self.assertIsNone(found);self.assertEqual(sum(l['selected_pool_index'] is not None for l in context['player_links']),26)
        self.assertFalse(any('ONE_GAME' in label or 'ONE_SEASON_GAME' in label or 'WORLD_BOX' in label for _,_,label in memory.calls));self.assertEqual(memory.excluded_reads,0)
        payload=world_payload({'save_id':'fixture','native_save_filename':'SYNTHETIC'},None,context,blobs,[],'2026-10-25T00:00:00Z','current')
        self.assertNotIn('player_game_boxes',payload['facts']);self.assertEqual(len(payload['facts']['players']),26)
    def test_new_season_does_not_relabel_old_native_cumulative_rows(self):
        memory=CurrentRosterMemory()
        with patch('cadence.observed_game_season_year',return_value=2099):_,context,blobs=collect_world(memory,None,target_native_ids=set(),current_context_only=True)
        payload=world_payload({'save_id':'fixture','native_save_filename':'SYNTHETIC'},None,context,blobs,[],'2026-10-25T00:00:00Z','new-season')
        self.assertEqual(payload['facts']['player_season_totals'],[]);self.assertEqual(payload['season']['season_id'],'season:native-year:2099')
    def test_duplicate_current_roster_player_is_rejected(self):
        memory=CurrentRosterMemory();raw=bytearray(memory.segments[memory.teams]);raw[8:16]=raw[:8];memory.segments[memory.teams]=bytes(raw)
        with patch('cadence.observed_game_season_year',return_value=2022),self.assertRaisesRegex(ValueError,'appears twice'):collect_world(memory,None,target_native_ids=set(),current_context_only=True)
    def test_cli_explicit_recheck_reaches_the_reader(self):
        from cli import main
        with patch.object(sys,'argv',['cli.py','capture-season','123','save','MyLEAGUE0003','out','--recheck-frozen']),patch('schedule_reader.capture_season',return_value={'status':'SYNTHETIC'}) as capture,redirect_stdout(StringIO()):main()
        self.assertTrue(capture.call_args.kwargs['recheck_frozen'])

if __name__=='__main__':unittest.main()

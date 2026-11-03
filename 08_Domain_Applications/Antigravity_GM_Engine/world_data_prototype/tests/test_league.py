"""Historical awards, ordinary event capture, immutable history and role projection."""
from copy import deepcopy
import json,sqlite3,struct,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import connect,create_database,ingest_capture
from league_ingest import existing_history_awards,league_payload
from league_reader import PROFILE_PATH,decode_history_record,decode_social_message,decode_native_date,unsigned_fields,free_chain_candidate
from query import awards,export_jsonl,league_history,native_news,native_transactions

PROFILE=json.loads(PROFILE_PATH.read_bytes())
BINDING={'save_id':'test-save','native_save_filename':'MyLEAGUE0003'}
STAMP='2026-10-24T00:00:00Z'

def history_row(index,code,year,first='Historical',last='Person',team='Historic Team'):
    raw=bytearray(152)
    for name,text in (('PlayerFirstName',first),('PlayerLastName',last),('PrimaryTeamName',team)):
        f=PROFILE['bindings']['LEAGUEHISTORYDATA'][name];value=text.encode('latin1')
        raw[f['offset']:f['offset']+len(value)]=value
    struct.pack_into('<I',raw,128,code);struct.pack_into('<H',raw,136,65535);struct.pack_into('<H',raw,138,72)
    struct.pack_into('<I',raw,148,year)
    return decode_history_record(bytes(raw),index,PROFILE)

def history_manifest():
    rows=[history_row(0,8,2021),history_row(1,13,2021,first='A'),history_row(2,13,2021,first='B'),
        history_row(3,2,2021),history_row(4,8,2022),history_row(5,0,0)]
    return {'capture_mode':'HISTORY_AWARDS','season_year':2022,'game_writes':False,'player_struct_reads':0,
        'history':rows,'history_descriptor':{'count':len(rows)},'manager_slot40_candidate':{'first_word':None,'free_chain':None},
        'award_winner_matrix':[{'award_slot_index':a,'recipient_slot_index':r,'native_player_index_raw':65535} for a in range(15) for r in range(5)]}

def news_manifest():
    messages=[]
    for bank in range(2):
        for i in range(2000):
            raw=bytearray(124)
            if i==0:
                struct.pack_into('<I',raw,36,(114<<16)|(5<<26));struct.pack_into('<I',raw,32,99)
                raw[40:54]='private'.encode('utf-16-le')
            row=decode_social_message(bytes(raw),bank,i,PROFILE)
            row['active_prefix_status']='WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE' if bank==0 and i==0 else 'OUTSIDE_DECLARED_COUNT_PREFIX';messages.append(row)
    transactions=[]
    for i in range(250):
        transactions.append({'source_slot_index':i,'values':unsigned_fields(bytes(320),PROFILE['bindings']['FRANCHISE_TRANSACTION']),
            'items':[dict(source_item_index=j,**unsigned_fields(bytes(8),PROFILE['bindings']['FRANCHISE_TRANSACTION_RECORD'])) for j in range(39)],
            'date':decode_native_date(bytes(4),PROFILE['bindings']['SCHEDULEDATE']),'type_label':'TEST_ZERO_STORAGE',
            'active_prefix_status':'OUTSIDE_DECLARED_COUNT_PREFIX'})
    return {'capture_mode':'NEWS_TRANSACTIONS','season_year':2022,'game_writes':False,'player_struct_reads':0,
        'messages':messages,'social_active_counts':[1,0],'transactions':transactions,'transaction_count':0}


class LeagueIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'test-save')
    def bundle(self,manifest,token,existing=None):
        return league_payload(BINDING,manifest,[{'sha256':'0'*64,'payload_kind':'EXPLICIT_SYNTHETIC_CODEC_TEST'}],STAMP,token,existing)

    def test_archival_awards_have_inline_recipients_not_inferred_current_ids(self):
        p=self.bundle(history_manifest(),'first')
        with connect(self.db) as c:ingest_capture(c,p)
        result=awards(self.db,year=2021);self.assertEqual(len(result['awards']),2)
        self.assertEqual(sum(len(a['recipients']) for a in result['awards']),3)
        for a in result['awards']:
            self.assertEqual(a['award_type'],'NATIVE_ROSTER_HISTORY')
            for recipient in a['recipients']:
                self.assertIsNone(recipient['player_id']);self.assertIsNone(recipient['team_id']);self.assertIsNone(recipient['rank_index'])
                self.assertIsNotNone(recipient['player_first_name'])
        self.assertEqual(awards(self.db,year=2022)['awards'],[])
        page=league_history(self.db,limit=2);self.assertTrue(page['has_more'])
        later=league_history(self.db,unit_id=page['unit_id'],after_index=page['next_after_index'],limit=100)
        self.assertEqual(len(page['records'])+len(later['records']),5)
        self.assertEqual(len(league_history(self.db,type_label='POINTS')['records']),1)

    def test_reobservation_preserves_events_and_changed_history_is_quarantined(self):
        m=history_manifest()
        with connect(self.db) as c:
            ingest_capture(c,self.bundle(m,'one'));old=existing_history_awards(c)
            same=self.bundle(m,'two',old);self.assertEqual(same['facts']['season_award_instances'],[]);ingest_capture(c,same)
            changed=deepcopy(m);changed['history'][0]['names']['PlayerLastName']='Changed'
            conflict=self.bundle(changed,'three',existing_history_awards(c));ingest_capture(c,conflict)
            self.assertEqual(c.execute('SELECT count(*) FROM season_award_instances').fetchone()[0],2)
            self.assertEqual(c.execute('SELECT count(*) FROM fact_conflicts').fetchone()[0],1)
            self.assertEqual(c.execute('SELECT count(*) FROM native_league_history_observations').fetchone()[0],18)
            self.assertEqual(c.execute("SELECT award_link_status FROM native_league_history_observations WHERE history_observation_id='native-league:three:history:0'").fetchone()[0],'IMMUTABLE_AWARD_CONFLICT_RECORDED')

    def test_bad_recipient_source_rolls_back_unit_and_referenced_seasons(self):
        p=self.bundle(history_manifest(),'bad');p['facts']['award_recipients'][0]['source_history_id']='another-unit-record'
        with connect(self.db) as c:
            with self.assertRaisesRegex(sqlite3.IntegrityError,'matching same-unit native history'):ingest_capture(c,p)
            self.assertEqual(c.execute('SELECT count(*) FROM seasons').fetchone()[0],0)
            self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],0)

    def test_news_storage_has_safe_pinned_projection_and_zero_transactions(self):
        p=self.bundle(news_manifest(),'news')
        with connect(self.db) as c:
            ingest_capture(c,p)
            self.assertEqual(c.execute('SELECT count(*) FROM game_news_entries').fetchone()[0],1)
            self.assertEqual(c.execute('SELECT count(*) FROM game_news_entries WHERE text_body IS NOT NULL OR occurrence_time IS NOT NULL').fetchone()[0],0)
            self.assertEqual(c.execute('SELECT count(*) FROM external_transaction_events').fetchone()[0],0)
        page=native_news(self.db,limit=1);self.assertTrue(page['has_more'])
        second=native_news(self.db,unit_id=page['unit_id'],after_index=page['next_after_index'],limit=100)
        self.assertEqual(len(second['records']),1);self.assertEqual(second['records'][0]['active_prefix_status'],'OUTSIDE_DECLARED_COUNT_PREFIX')
        public=json.dumps(page)+json.dumps(second)
        for forbidden in ('data1_raw','data_u32_raw','string1_fragment','private','player_index','payload_ref'):self.assertNotIn(forbidden,public)
        self.assertEqual(native_transactions(self.db)['native_control']['transaction_count'],0)
        for table in ('native_social_message_observations','native_transaction_item_observations','game_news_entries'):
            with self.assertRaises(PermissionError):export_jsonl(self.db,Path(self.tmp.name)/table,table)

    def test_incomplete_sources_and_invalid_year_registry_reject(self):
        m=history_manifest();m['award_winner_matrix'].pop()
        with self.assertRaisesRegex(ValueError,'incomplete award matrix'):self.bundle(m,'bad')
        p=self.bundle(history_manifest(),'bad-season');p['referenced_seasons']=[{'season_id':'x','season_code':'x','save_id':'wrong'}]
        with connect(self.db) as c:
            with self.assertRaisesRegex(ValueError,'invalid referenced season'):ingest_capture(c,p)

    def test_array_layout_and_free_chain_retain_noncontiguous_slots(self):
        self.assertEqual(PROFILE['bindings']['FRANCHISE_SOCIALMEDIA::DATA']['Message']['array_dimensions'],[2,2000])
        self.assertEqual(PROFILE['bindings']['FRANCHISE']['SeasonAwardWinnerIndex']['array_dimensions'],[15,5])
        raw=bytearray(3*152);struct.pack_into('<H',raw,136,2);struct.pack_into('<H',raw,2*152+136,65535)
        self.assertEqual(free_chain_candidate(raw,3,0)['indices'],[0,2])
        struct.pack_into('<H',raw,2*152+136,0)
        self.assertEqual(free_chain_candidate(raw,3,0)['status'],'INVALID_CANDIDATE_CHAIN')


if __name__=='__main__':unittest.main()

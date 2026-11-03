"""Native market fixture replay and non-inference/identity behavior."""
import copy,hashlib,json,struct,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from market_reader import market_payload,draft_codec,DRAFT_PROFILE,decode_waived_record,decode_prospect_slot
from engine import create_database,connect,ingest_capture
from query import market_snapshot,prospect_card
FIXTURE=BASE/'tests/fixtures/market_20261024'


class DraftMemory:
    base_address=0x140000000
    def __init__(self,manifest):
        self.table=manifest['descriptors']['42'];self.raw=(FIXTURE/'draft-assets.bin').read_bytes();self.asset_reads=0;self.code_bad=False
    def read_bytes(self,address,size):
        for i,item in enumerate(DRAFT_PROFILE['code_evidence']):
            if address==self.base_address+item['module_rva']:
                return b'\0'*size if self.code_bad else (FIXTURE/f'draft-code-{i}.bin').read_bytes()
        off=address-self.table['address']
        if 0<=off and off+size<=len(self.raw):self.asset_reads+=1;return self.raw[off:off+size]
        raise AssertionError('unexpected source address')


class MarketTests(unittest.TestCase):
    def manifest(self):return json.loads((FIXTURE/'manifest.json').read_bytes())
    def payload(self,m=None,token='a',stamp='2026-10-24T00:00:00Z'):
        return market_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m or self.manifest(),
            [{'sha256':hashlib.sha256((FIXTURE/'manifest.json').read_bytes()).hexdigest(),'payload_kind':'ACTUAL_MARKET_RESEARCH_FIXTURE'}],stamp,token)

    def test_real_complete_pick_groups_and_no_invented_people_results_or_availability(self):
        m=self.manifest();mem=DraftMemory(m)
        rows,year=draft_codec().read_assets(mem,{'draft_assets':mem.table},{t['address']:t['native_team_id'] for t in m['teams']},m['season_year'])
        self.assertEqual(year,2022);self.assertEqual(sum(r['mapping_status']=='VERIFIED_SIMPLE_FUTURE_PICK' for _,r,_ in rows),300)
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,self.payload())
            snap=market_snapshot(db)
            self.assertEqual(len(snap['future_picks']),300);self.assertEqual(len(snap['draft_pool_slots']),90)
            self.assertTrue(all(p['protection_status']=='UNKNOWN' and p['swap_status']=='UNKNOWN' for p in snap['future_picks']))
            self.assertEqual(sum(w['owner_mapping_status']=='CORE_TEAM_POINTER' for w in snap['waived_salary_source_observations']),32)
            with connect(db,True) as c:
                for table in ('draft_prospects','players','draft_results','external_transaction_events','market_state_observations'):
                    self.assertEqual(c.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
                self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
            with self.assertRaisesRegex(ValueError,'no truncation'):market_snapshot(db,limit=1)
            encoded=json.dumps(snap).lower();self.assertNotIn('potential',encoded);self.assertNotIn('"address"',encoded)

    def test_named_templates_keep_unknown_year_and_do_not_merge_zero_ids_or_create_players(self):
        raw=bytearray((FIXTURE/'prospect-0.public.bin').read_bytes())
        raw[:80]=b'\0'*80;raw[:16]='Prospect'.encode('utf-16le');raw[40:54]='Fixture'.encode('utf-16le')
        first=decode_prospect_slot(raw,0);second=decode_prospect_slot(raw,1)
        m=self.manifest();m['prospects']=[first,second]
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture');p=self.payload(m)
            with connect(db) as c:ingest_capture(c,p)
            with connect(db,True) as c:
                self.assertEqual(c.execute('SELECT count(*) FROM draft_prospects WHERE draft_year IS NULL').fetchone()[0],2)
                self.assertEqual(c.execute('SELECT count(*) FROM players').fetchone()[0],0)
            card=prospect_card(db,p['facts']['draft_prospects'][0]['prospect_id'])
            self.assertEqual(len(card['play_type_slots']),4);self.assertIsNone(card['prospect']['draft_year'])
            self.assertNotIn('potential',json.dumps(card).lower())

    def test_changed_native_getter_stops_before_reading_asset_rows(self):
        m=self.manifest();mem=DraftMemory(m);mem.code_bad=True
        with self.assertRaisesRegex(RuntimeError,'version mismatch'):
            draft_codec().read_assets(mem,{'draft_assets':mem.table},{t['address']:t['native_team_id'] for t in m['teams']},m['season_year'])
        self.assertEqual(mem.asset_reads,0)

    def test_duplicate_native_pick_index_rejects_complete_looking_table(self):
        m=self.manifest();mem=DraftMemory(m)
        same=[a for a in m['draft_assets'] if a['mapping_status']=='VERIFIED_SIMPLE_FUTURE_PICK' and a['draft_year']==2022 and a['draft_round']==1]
        first,second=same[:2];raw=bytearray(mem.raw);off=second['source_row_index']*32+28
        meta=struct.unpack_from('<I',raw,off)[0];struct.pack_into('<I',raw,off,(meta&~0xFF00)|(first['native_pick_index']<<8));mem.raw=bytes(raw)
        with self.assertRaisesRegex(RuntimeError,'Duplicate or invalid'):
            draft_codec().read_assets(mem,{'draft_assets':mem.table},{t['address']:t['native_team_id'] for t in m['teams']},m['season_year'])

    def test_waived_inline_names_do_not_use_first_word_as_player_pointer(self):
        m=self.manifest();raw=bytearray((FIXTURE/'waived-0.bin').read_bytes());struct.pack_into('<Q',raw,0,0xDEADBEEF)
        row=decode_waived_record(raw,0,{t['address']:t['native_team_id'] for t in m['teams']})
        self.assertEqual(row['observed_player_name'],'Demetrius Jackson');self.assertIsNone(row['native_player_id'])
        self.assertEqual([row[f'salary_year_{i}_raw'] for i in (1,2,3)],[92857,92857,92857])

    def test_changed_ownership_appends_without_fabricating_a_trade_event(self):
        m=self.manifest();asset=next(a for a in m['draft_assets'] if a['mapping_status']=='VERIFIED_SIMPLE_FUTURE_PICK')
        current=asset['current_owner_team_id'];new_owner=next(t['native_team_id'] for t in m['teams'] if t['native_team_id']!=current)
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,self.payload(m))
            asset['current_owner_team_id']=new_owner
            with connect(db) as c:ingest_capture(c,self.payload(m,'b','2026-10-25T00:00:00Z'))
            with connect(db,True) as c:
                self.assertEqual(c.execute('SELECT count(*) FROM draft_pick_assets').fetchone()[0],300)
                self.assertEqual(c.execute('SELECT count(*) FROM draft_pick_ownerships').fetchone()[0],600)
                self.assertEqual(c.execute('SELECT count(*) FROM external_transaction_events').fetchone()[0],0)
            self.assertEqual(len(market_snapshot(db)['future_picks']),300)


if __name__=='__main__':unittest.main()

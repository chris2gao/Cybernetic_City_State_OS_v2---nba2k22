"""Current native stat metadata, exact source references and privacy contracts."""
import copy,hashlib,json,sqlite3,struct,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from award_reader import honors_payload,decode_stat_record,classify_stat_link,PROFILE_PATH,AWARD_COLUMNS
from engine import create_database,connect,ingest_capture
from query import native_honors,player_card
from live_world import RESTRICTED_PLAYER_RANGES
from family_codec import public_player_families
from readers import NATIVE,_module
FIXTURE=BASE/'tests/fixtures/honors_20261025';PROFILE=json.loads(PROFILE_PATH.read_bytes())


class HonorsTests(unittest.TestCase):
    def manifest(self):return json.loads((FIXTURE/'manifest.json').read_bytes())
    def payload(self,m=None,token='fixture'):
        m=m or self.manifest();canon={'player:native:'+str(p['preserved_id_raw']):p['observed_name'] for p in m['players'] if p['current_core_roster_status']=='CURRENT_CORE_ROSTER'}
        p=honors_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m,
            [{'sha256':hashlib.sha256((FIXTURE/'manifest.json').read_bytes()).hexdigest(),'payload_kind':'ACTUAL_CURATED_NATIVE_STATS_AND_PUBLIC_PROJECTIONS'}],
            '2026-10-25T00:00:00Z',token,canon)
        p['facts']['players']=[{'player_id':k,'display_name':v,'native_player_id':k.rsplit(':',1)[1],'native_identity_status':'UNVERIFIED'} for k,v in canon.items()]
        return p

    def test_every_native_stat_word_and_public_subject_projection_roundtrips(self):
        m=self.manifest();raw=(FIXTURE/'stat-sample.bin').read_bytes();public=(FIXTURE/'player-public-sample.bin').read_bytes();stride=144
        for i,row in enumerate(m['stat_records']):self.assertEqual(decode_stat_record(raw[i*48:(i+1)*48],PROFILE['stat_fields']),{k:v for k,v in row.items() if k!='source_stat_index'})
        for i,p in enumerate(m['players']):
            rawid=public[i*stride+80:i*stride+82];preserved=public[i*stride+82:i*stride+86]
            self.assertEqual(int.from_bytes(rawid,'little'),p['native_unique_id_raw']);self.assertEqual(int.from_bytes(preserved,'little'),p['preserved_id_raw'])
        self.assertEqual(m['season_stats_array_count'],25)
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture');p=self.payload()
            with connect(db) as c:
                self.assertEqual(ingest_capture(c,p),'ingested');self.assertEqual(ingest_capture(c,p),'already_applied')
                self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall());self.assertEqual(c.execute('SELECT count(*) FROM season_award_instances').fetchone()[0],0)
            snap=native_honors(db,flag='mvp_raw');self.assertTrue(snap['records'])
            self.assertEqual(snap['canonical_award_instances'],'NOT_ESTABLISHED_BY_THIS_QUERY')
            self.assertTrue(all(r['mvp_raw']==1 for r in snap['records']));self.assertNotIn('payload_ref',json.dumps(snap))
            curry=next(x for x in m['players'] if x['observed_name']=='Stephen Curry' and x['current_core_roster_status']=='CURRENT_CORE_ROSTER')
            identity=player_card(db,'player:native:'+str(curry['preserved_id_raw']))['native_identity_observation']
            self.assertEqual(identity['native_unique_id_raw'],curry['native_unique_id_raw'])

    def test_all_25_slots_and_after_empty_references_are_retained(self):
        self.assertEqual(classify_stat_link(12,24,100,True),'HISTORY_INDEX_AFTER_EMPTY_SLOT')
        self.assertEqual(classify_stat_link(0,2,100),'ZERO_HISTORY_SLOT_UNVERIFIED')
        self.assertEqual(classify_stat_link(32756,2,40000),'HISTORY_INDEX_CANDIDATE')
        p=self.payload();self.assertEqual(len(p['facts']['native_player_stat_links']),25*len(self.manifest()['players']))
        m=self.manifest();m['stat_links'].pop()
        with self.assertRaisesRegex(ValueError,'reference array'):self.payload(m)

    def test_compact_year_uses_eight_bits_in_native_and_existing_decoder(self):
        native=_module('season_stats_decoder').SeasonStatsDecoder
        for code in (127,128,200,255):
            raw=bytearray(48);raw[5]=code
            self.assertEqual(decode_stat_record(raw,PROFILE['stat_fields'])['stat_year'],1900+code)
            self.assertEqual(native.decode_player_stats_record(raw)['season_year'],1900+code)

    def test_shared_and_unowned_award_words_remain_source_observations(self):
        m=self.manifest();p=self.payload()
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,p)
            snap=native_honors(db,limit=1000)
            self.assertTrue(any(r['subject_status']=='NO_BOUND_SOURCE_SUBJECT' for r in snap['records']))
            self.assertTrue(any(len(r['source_subjects'])>1 for r in snap['records']))
            page=native_honors(db,limit=1);self.assertTrue(page['has_more'])
            second=native_honors(db,unit_id=page['unit']['unit_id'],after_index=page['next_after_index'],limit=1)
            self.assertGreater(second['records'][0]['source_stat_index'],page['records'][0]['source_stat_index'])

    def test_cross_unit_or_wrong_stat_index_cannot_borrow_native_references(self):
        p=self.payload();q=self.payload(token='new');old=p['facts']['native_player_stat_links'][0]
        q['facts']['native_player_stat_links'][0]['player_source_id']=old['player_source_id']
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,p)
            with connect(db) as c:
                with self.assertRaisesRegex(sqlite3.IntegrityError,'cross-unit native player'):ingest_capture(c,q)
            q=self.payload(token='wrong');link=next(r for r in q['facts']['native_player_stat_links'] if r['stat_observation_id'])
            link['native_stat_index_raw']+=1
            with connect(db) as c:
                with self.assertRaisesRegex(sqlite3.IntegrityError,'mismatched native stat'):ingest_capture(c,q)
            with connect(db,True) as c:self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)

    def test_public_families_do_not_depend_on_any_native_potential_storage(self):
        sample=next(iter(json.loads((NATIVE/'fixtures/sample_player_career_slice.json').read_bytes()).values()))
        raw=bytes.fromhex(sample['raw_player_hex']);expected=public_player_families(raw);changed=bytearray(raw)
        for low,high in RESTRICTED_PLAYER_RANGES:changed[low:high]=bytes([0xD7])*(high-low)
        self.assertEqual(public_player_families(changed),expected)

    def test_duplicate_unique_ids_withhold_canonical_alias_instead_of_rewriting_identity(self):
        m=self.manifest();current=next(p for p in m['players'] if p['current_core_roster_status']=='CURRENT_CORE_ROSTER');other=next(p for p in m['players'] if p is not current)
        other['native_unique_id_raw']=current['native_unique_id_raw'];p=self.payload(m)
        row=next(r for r in p['facts']['native_player_sources'] if r['source_player_index']==current['source_player_index'])
        self.assertIsNone(row['player_id']);self.assertEqual(row['canonical_link_status'],'SOURCE_ONLY_CANONICAL_LINK_WITHHELD')


if __name__=='__main__':unittest.main()

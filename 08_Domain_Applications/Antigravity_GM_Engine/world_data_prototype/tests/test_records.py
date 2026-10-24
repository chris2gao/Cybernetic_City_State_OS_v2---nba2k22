"""Record-book words, qualified history and pinned pagination boundaries."""
import copy,hashlib,json,struct,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from records_reader import decode_record_word,records_payload
from engine import create_database,connect,ingest_capture
from query import record_book
FIXTURE=BASE/'tests/fixtures/records_20261024'


class RecordTests(unittest.TestCase):
    def manifest(self):return json.loads((FIXTURE/'manifest.json').read_bytes())
    def payload(self,m=None,token='fixture'):
        return records_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m or self.manifest(),
            [{'sha256':hashlib.sha256((FIXTURE/'manifest.json').read_bytes()).hexdigest(),'payload_kind':'ACTUAL_CURATED_RECORD_BOOK'}],
            '2026-10-24T00:00:00Z',token)

    def test_actual_word_replay_exact_metric_and_no_fabricated_identity_awards_or_season(self):
        m=self.manifest();p=self.payload();raw=(FIXTURE/'record-sample.bin').read_bytes()
        for i,row in enumerate(m['record_rows']):self.assertEqual(decode_record_word(raw[i*52:(i+1)*52],row['source_row_index']),row)
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:
                self.assertEqual(ingest_capture(c,p),'ingested');self.assertEqual(ingest_capture(c,p),'already_applied')
                self.assertEqual(c.execute('SELECT count(*) FROM season_award_instances').fetchone()[0],0)
                self.assertEqual(c.execute('SELECT count(*) FROM players').fetchone()[0],0)
                self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
            snap=record_book(db,category_code=0x8f,subject_name='Wilt Chamberlain')
            first=snap['records'][0];self.assertEqual(first['native_value_real'],100.0)
            self.assertEqual(first['record_date_candidate'],'1962-03-02')
            self.assertIsNone(first['occurred_at']);self.assertIsNone(first['season_id']);self.assertIsNone(first['holder_player_id'])
            self.assertEqual(first['observed_in_season_id'],'season:native-year:2022')
            self.assertNotIn('"address"',json.dumps(snap));self.assertNotIn('payload_ref',json.dumps(snap))

    def test_pinned_pages_do_not_duplicate_skip_or_silently_change_source_unit(self):
        m=self.manifest();p=self.payload()
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,p)
            first=record_book(db,limit=50);unit=first['unit']['unit_id'];all_rows=list(first['records']);page=first
            later=self.payload(token='later');later['observed_at']='2026-10-25T00:00:00Z'
            with connect(db) as c:ingest_capture(c,later)
            self.assertEqual(record_book(db)['unit']['unit_id'],later['unit_id'])
            while page['has_more']:
                page=record_book(db,unit_id=unit,after_index=page['next_after_index'],limit=50);all_rows.extend(page['records'])
            self.assertEqual([r['source_row_index'] for r in all_rows],[r['source_row_index'] for r in m['record_rows']])
            self.assertTrue(all(r['unit_id']==unit for r in all_rows))
            self.assertEqual(record_book(db,category_code=65535)['records'],[])

    def test_floats_are_not_rounded_and_nonfinite_bits_stay_diagnostic(self):
        raw=bytearray((FIXTURE/'record-sample.bin').read_bytes()[:52]);struct.pack_into('<f',raw,40,1.23456789)
        r=decode_record_word(raw,0);self.assertEqual(r['value_real'],struct.unpack_from('<f',raw,40)[0]);self.assertNotEqual(r['value_real'],round(r['value_real'],3))
        raw[40:44]=bytes.fromhex('0100c07f');r=decode_record_word(raw,0)
        self.assertIsNone(r['value_real']);self.assertEqual(r['raw_value_u32'],0x7fc00001)
        self.assertEqual(r['decode_status'],'NONFINITE_SOURCE_METRIC')
        m=self.manifest();m['record_rows']=[r];self.assertIsNone(self.payload(m)['facts']['season_record_entries'][0]['native_value_real'])

    def test_invalid_date_and_name_do_not_become_occurred_event_or_fake_holder(self):
        raw=bytearray((FIXTURE/'record-sample.bin').read_bytes()[:52]);struct.pack_into('<H',raw,44,((2022-1920)<<9)|(2<<5)|30)
        r=decode_record_word(raw,0);self.assertIsNone(r['date_candidate']);self.assertIn('INVALID_GREGORIAN',r['date_status'])
        raw[0]=1;r=decode_record_word(raw,0);self.assertEqual(r['decode_status'],'INVALID_SOURCE_NAME_PREFIX')
        self.assertIsNone(r['first_name']);self.assertEqual(decode_record_word(bytes(52),0)['decode_status'],'EMPTY_ALL_ZERO')
        with self.assertRaises(ValueError):decode_record_word(bytes(51),0)

    def test_duplicate_missing_coverage_and_corrupt_metric_rejected(self):
        m=self.manifest();m['record_rows'].append(copy.deepcopy(m['record_rows'][0]))
        with self.assertRaisesRegex(ValueError,'duplicate'):self.payload(m)
        m=self.manifest();m['capture_coverage']='COMPLETE_NATIVE_COUNT'
        with self.assertRaisesRegex(ValueError,'incomplete native'):self.payload(m)
        m=self.manifest();m['record_rows'][0]['value_real']=99
        with self.assertRaisesRegex(ValueError,'raw word'):self.payload(m)


if __name__=='__main__':unittest.main()

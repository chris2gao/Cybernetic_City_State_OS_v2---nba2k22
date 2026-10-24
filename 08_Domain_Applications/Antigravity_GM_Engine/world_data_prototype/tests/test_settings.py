"""Settings raw-word fidelity, alias semantics and atomic history boundaries."""
import copy,hashlib,json,math,sqlite3,struct,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from settings_reader import settings_payload,catalog_layout,decode_word,range_status,slider_location,SLIDER_RVA
from engine import create_database,connect,ingest_capture
from query import settings_snapshot,rules_snapshot,history
FIXTURE=BASE/'tests/fixtures/settings_20261024'


class SettingsTests(unittest.TestCase):
    def manifest(self):return json.loads((FIXTURE/'manifest.json').read_bytes())
    def payload(self,m=None,token='fixture'):
        return settings_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m or self.manifest(),
            [{'sha256':hashlib.sha256((FIXTURE/'manifest.json').read_bytes()).hexdigest(),'payload_kind':'ACTUAL_SETTINGS_WORD_RESEARCH'}],
            '2026-10-24T00:00:00Z',token)

    def test_actual_words_aliases_scopes_rules_and_public_queries(self):
        m=self.manifest();p=self.payload()
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:
                self.assertEqual(ingest_capture(c,p),'ingested');self.assertEqual(ingest_capture(c,p),'already_applied')
            snapshot=settings_snapshot(db);rules=rules_snapshot(db)
            self.assertEqual(len(snapshot['settings']),546);self.assertEqual(len(rules['rules']),35)
            for scope in ('CURRENT:USER','CURRENT:CPU','CUSTOM:USER','CUSTOM:CPU'):
                self.assertEqual(len(settings_snapshot(db,scope_code=scope)['settings']),126)
            self.assertTrue(any('OUTSIDE_REGISTERED' in r['registered_range_status'] for r in snapshot['settings']))
            self.assertFalse(snapshot['targets_defaults_applied'])
            self.assertNotIn('payload_ref',json.dumps(snapshot));self.assertNotIn('"address"',json.dumps(snapshot))
            # A global salary-factor setting is public configuration, not the
            # hidden PLAYER attribute. No PLAYER values exist in this unit.
            self.assertEqual(history(db,'players'),[])
            with self.assertRaisesRegex(ValueError,'no truncation'):settings_snapshot(db,limit=1)
            with self.assertRaisesRegex(ValueError,'no truncation'):rules_snapshot(db,limit=1)
            with self.assertRaises(PermissionError):history(db,'native_fields')
            with connect(db,True) as c:self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())

    def test_fixture_bytes_decode_every_word(self):
        m=self.manifest();table=(FIXTURE/'tunedata-saved.bin').read_bytes()
        for row in m['rows']:
            raw=(table[row['source_offset']:row['source_offset']+4] if row['pointer_rva']==SLIDER_RVA else
                 (FIXTURE/f'word-{row["pointer_rva"]:x}-{row["source_offset"]:x}-{row["encoding"]}.bin').read_bytes())
            for key,value in decode_word(raw,row['encoding']).items():self.assertEqual(row[key],value)

    def test_catalog_defaults_targets_not_used_and_alias_cells_deduplicated(self):
        layout=catalog_layout();cell=next(aliases for (rva,offset,encoding),aliases in layout.items() if rva==0x632B4B0 and offset==0x14)
        self.assertEqual({a['catalog'] for a in cell},{'world','settings'})
        self.assertTrue(all('default' not in a and 'target' not in a for aliases in layout.values() for a in aliases))
        m=self.manifest();before=self.payload(m)
        for row in m['rows']:
            for alias in row['aliases']:alias.update(default=999999,target=999999)
        after=self.payload(m)
        # Metadata revision ID may differ with changed input annotations; all
        # observed typed words and sanitized exported aliases remain identical.
        for a,b in zip(before['facts']['game_setting_observations'],after['facts']['game_setting_observations']):
            self.assertEqual(a['raw_word_u32'],b['raw_word_u32']);self.assertEqual(a['aliases_json'],b['aliases_json'])

    def test_nonfinite_float_and_out_of_candidate_range_are_never_zero_or_clamped(self):
        for word in (0x7F800000,0xFF800000,0x7FC00001):
            decoded=decode_word(word.to_bytes(4,'little'),'float')
            self.assertIn('text_value',decoded);self.assertNotIn('real_value',decoded);self.assertEqual(decoded['raw_word_u32'],word)
        self.assertEqual(decode_word(struct.pack('<f',-2.5),'float')['real_value'],-2.5)
        self.assertIn('OUTSIDE_REGISTERED',range_status({'integer_value':40},[{'min':50,'max':100}]))
        m=self.manifest();r=m['rows'][1]
        for key in ('integer_value','real_value','text_value'):r.pop(key,None)
        r.update(decode_word(bytes.fromhex('0100c07f'),'float'));r['registered_range_status']=range_status(r,r['aliases'])
        p=self.payload(m)
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,p)
            found=next(x for x in settings_snapshot(db)['settings'] if x['setting_obs_id']==p['facts']['game_setting_observations'][1]['setting_obs_id'])
            self.assertIsNone(found['real_value']);self.assertEqual(found['raw_word_u32'],0x7FC00001)

    def test_scope_boundaries_and_corrupt_decoded_value_rejected(self):
        self.assertEqual(slider_location(4),('CURRENT',0,'USER'));self.assertEqual(slider_location(8),('CURRENT',0,'CPU'))
        self.assertEqual(slider_location(1012),('CUSTOM',0,'USER'));self.assertEqual(slider_location(2016),('CUSTOM',125,'CPU'))
        self.assertIsNone(slider_location(2020))
        m=self.manifest();m['rows'][0]['integer_value']+=1
        with self.assertRaisesRegex(ValueError,'raw word'):self.payload(m)

    def test_rule_cannot_borrow_older_setting_or_disagree_with_word(self):
        p=self.payload();q=self.payload(token='new')
        q['facts']['league_rule_observations'][0]['setting_obs_id']=p['facts']['league_rule_observations'][0]['setting_obs_id']
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,p)
            with connect(db) as c:
                with self.assertRaisesRegex(sqlite3.IntegrityError,'same-unit matching'):ingest_capture(c,q)
            q=self.payload(token='bad');q['facts']['league_rule_observations'][0]['integer_value']+=1
            with connect(db) as c:
                with self.assertRaisesRegex(sqlite3.IntegrityError,'same-unit matching'):ingest_capture(c,q)
            with connect(db,True) as c:self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)


if __name__=='__main__':unittest.main()

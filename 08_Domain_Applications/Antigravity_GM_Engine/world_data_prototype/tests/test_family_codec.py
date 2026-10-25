"""Registered bit-layout and captured-source integration, no live/UI claim."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from family_codec import extract_unsigned,public_player_families,profile_layout_receipt,registered_rating_candidate
from readers import replay_player_families
from engine import create_database,connect,ingest_capture
from query import player_card,history


class RegisteredFamilyTests(unittest.TestCase):
    def test_display_candidate_is_separate_from_raw_and_not_ui_observed(self):
        self.assertEqual(registered_rating_candidate(174)['value'],83)
        self.assertEqual(registered_rating_candidate(174)['target_ui_validation'],'NOT_OBSERVED')
        self.assertEqual(registered_rating_candidate(256)['status'],'OUTSIDE_REGISTERED_BYTE_STORAGE')

    def test_shared_byte_is_disjoint_bits_with_cross_byte_extension(self):
        raw=bytearray(1264)
        raw[833]=0xD3;raw[834]=0x01
        data=public_player_families(raw)
        self.assertEqual(data['contracts']['original_contract_years_raw'],5)
        self.assertEqual(data['contracts']['extension_length_raw'],3)
        self.assertFalse(profile_layout_receipt()['registered_bits_overlap'])
        receipt=profile_layout_receipt()
        self.assertEqual(receipt['current_native_contract_bindings']['original_contract_years']['native_name'],'ContractLength')
        self.assertEqual(receipt['current_native_contract_bindings']['extension_length']['start_bit'],15)
        self.assertIn('salary scale, sentinels and target UI separate',receipt['current_game_semantics'])

    def test_truncated_cross_byte_field_is_not_silently_decoded(self):
        with self.assertRaisesRegex(ValueError,'incomplete'):
            extract_unsigned(bytes(2),{'offset':1,'start_bit':7,'bits':3})
        with self.assertRaises(ValueError):extract_unsigned(bytes(8),{'offset':-1,'bits':8})

    def test_potential_never_escapes_and_unregistered_tendencies_stay_absent(self):
        source=bytearray(1264);source[1089]=255
        data=public_player_families(source)
        self.assertFalse(any('potential' in k for f in ('attributes','contracts','tendencies') for k in data[f]))
        self.assertEqual(len(data['tendencies']),48)
        self.assertNotIn('raw_0x4ba',data['tendencies'])
        self.assertEqual(data['family_completeness']['badges'],'UNKNOWN_ENCODING_NOT_DECODED')

    def test_four_playtypes_preserve_order_and_nibbles(self):
        raw=bytearray(1264);raw[0x168]=0x51;raw[0x169]=0xF2
        values=public_player_families(raw)['play_types']
        self.assertEqual([x['native_play_code'] for x in values],['1','5','2','15'])
        self.assertEqual([x['slot_index'] for x in values],[0,1,2,3])

    def test_real_research_samples_to_contract_tendency_and_playtype_tables(self):
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'sample-save')
            payloads=list(replay_player_families('sample-save',observed_at='2026-10-24T00:00:00Z'))
            self.assertEqual(len(payloads),3)
            for payload in payloads:
                with connect(db) as c:self.assertEqual(ingest_capture(c,payload),'ingested')
            with connect(db) as c:
                self.assertEqual(c.execute('SELECT count(*) FROM players').fetchone()[0],3)
                self.assertEqual(c.execute('SELECT count(*) FROM player_contract_observations').fetchone()[0],3)
                self.assertEqual(c.execute('SELECT count(*) FROM player_play_type_slots').fetchone()[0],12)
                self.assertEqual(c.execute('SELECT count(*) FROM player_badge_values').fetchone()[0],0)
                self.assertEqual(c.execute('SELECT count(*) FROM field_gaps').fetchone()[0],3)
                self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
            player=payloads[0]['facts']['players'][0]['player_id']
            card=player_card(db,player)
            self.assertTrue(all(v.get('source_grade')=='RESEARCH_FIXTURE' for v in card['families']['player_contract_observations'].values() if v.get('value') is not None))
            self.assertEqual(len(history(db,'player_tendency_snapshots')),3)


if __name__=='__main__':unittest.main()

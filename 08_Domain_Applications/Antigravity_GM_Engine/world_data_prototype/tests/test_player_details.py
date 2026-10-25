"""Full native widths, base badge encoding, source identity and immutable replay."""
from copy import deepcopy
import json,sqlite3,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_capture
from player_detail_codec import PROFILE,native_badges,native_contracts
from player_detail_reader import detail_payload,projection_ranges,reconstruct_projection
from query import native_player_details,player_badges,player_card
from live_world import RESTRICTED_PLAYER_RANGES

def put(raw,field,value):
    start=field['offset'];bits=field['start_bit'];width=field['width'];size=(bits+width+7)//8
    word=int.from_bytes(raw[start:start+size],'little');mask=((1<<width)-1)<<bits
    raw[start:start+size]=((word&~mask)|(value<<bits)).to_bytes(size,'little')

def test_manifest():
    players=[];contracts=[];badges=[]
    for i,name in enumerate(('Native Test','Source Only')):
        raw=bytearray(1264);put(raw,PROFILE['contract_fields']['bird_years'],31);put(raw,PROFILE['contract_fields']['years_left_on_contract'],29);put(raw,PROFILE['contract_fields']['euro_stash_years_left'],7)
        put(raw,PROFILE['badge_fields']['CatchAndShoot'],4)
        players.append({'source_player_index':i,'native_unique_id_raw':i+1,'preserved_id_raw':i+101,'observed_name':name,'name_status':'OBSERVED_UTF16_PREFIX',
            'native_team_id':0 if i==0 else None,'current_core_roster_status':'CURRENT_CORE_ROSTER' if i==0 else 'NOT_CURRENT_CORE_ROSTER','current_roster_slot':0 if i==0 else None})
        contracts.append({'source_player_index':i,**native_contracts(bytes(raw)),'native_contract_team_id_raw':0 if i==0 else None,'contract_team_status':'TEST_SOURCE'})
        badges.extend({'source_player_index':i,**r} for r in native_badges(bytes(raw)))
    return {'season_year':2022,'descriptors':{'1':{'count':2}},'players':players,'contract_rows':contracts,'badge_rows':badges,'game_writes':False,'restricted_player_bytes_read':0}

class NativePlayerDetailTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'save')
    def payload(self,m=None,token='one',canonical=None):
        return detail_payload({'save_id':'save','native_save_filename':'MyLEAGUE0003'},m or test_manifest(),[{'sha256':'0'*64,'payload_kind':'EXPLICIT_SYNTHETIC_CODEC_TEST'}],
            '2026-10-25T00:00:00Z',token,canonical or {'player:native:101':'Native Test'})
    def with_player(self,p):p['facts']['players']=[{'player_id':'player:native:101','display_name':'Native Test'}];return p

    def test_full_contract_widths_and_distinct_packed_lengths(self):
        raw=bytearray(1264)
        for name,value in (('bird_years',31),('years_left_on_contract',29),('euro_stash_years_left',7),('original_contract_years',5),('extension_length',3)):
            put(raw,PROFILE['contract_fields'][name],value)
        decoded=native_contracts(bytes(raw))
        self.assertEqual([decoded[k+'_raw'] for k in ('bird_years','years_left_on_contract','euro_stash_years_left','original_contract_years','extension_length')],[31,29,7,5,3])

    def test_base_badge_boolean_levels_zero_unknown_and_reserved(self):
        raw=bytearray(1264);put(raw,PROFILE['badge_fields']['CatchAndShoot'],4);put(raw,PROFILE['badge_fields']['AlphaDog'],1)
        badges={b['badge_key']:b for b in native_badges(bytes(raw))}
        self.assertEqual(len(badges),98);self.assertNotIn('NONE',badges)
        self.assertEqual(badges['CatchAndShoot']['tier_label'],'HALL_OF_FAME');self.assertIsNone(badges['AlphaDog']['tier_label'])
        self.assertEqual(badges['AlphaDog']['owned_state'],'owned');self.assertEqual(badges['CornerSpecialist']['owned_state'],'not_owned')
        put(raw,PROFILE['badge_fields']['CatchAndShoot'],7);unknown=next(b for b in native_badges(bytes(raw)) if b['badge_key']=='CatchAndShoot')
        self.assertIsNone(unknown['tier_label']);self.assertEqual(unknown['native_code'],7);self.assertEqual(unknown['owned_state'],'unknown')

    def test_public_projection_and_decoding_ignore_all_private_intervals(self):
        raw=bytearray(1264);before=(native_contracts(bytes(raw)),native_badges(bytes(raw)))
        for low,high in RESTRICTED_PLAYER_RANGES:raw[low:high]=b'\xff'*(high-low)
        self.assertEqual(before,(native_contracts(bytes(raw)),native_badges(bytes(raw))))
        ranges=projection_ranges();self.assertTrue(all(not(low<b and a<high) for low,high in ranges for a,b in RESTRICTED_PLAYER_RANGES))
        public=reconstruct_projection(b''.join(raw[a:b] for a,b in ranges),ranges)
        for low,high in RESTRICTED_PLAYER_RANGES:self.assertEqual(public[low:high],bytes(high-low))

    def test_full_source_only_and_matched_canonical_queries(self):
        p=self.with_player(self.payload())
        with connect(self.db) as c:self.assertEqual(ingest_capture(c,p),'ingested')
        page=native_player_details(self.db,limit=1);self.assertTrue(page['has_more']);self.assertEqual(len(page['records'][0]['base_badges']),98)
        second=native_player_details(self.db,unit_id=page['unit_id'],after_index=page['next_after_index']);self.assertIsNone(second['records'][0]['player_id'])
        self.assertEqual(second['records'][0]['contract']['bird_years_raw'],31)
        self.assertEqual(len(player_badges(self.db,'player:native:101')),98)
        self.assertEqual(len(player_card(self.db,'player:native:101')['families']['player_badge_values']),98)

    def test_cross_unit_detail_child_rejects_and_rolls_back(self):
        with connect(self.db) as c:
            first=self.with_player(self.payload());ingest_capture(c,first)
            bad=self.payload(token='two');bad['facts']['player_badge_values'][0]['source_player_id']='player-detail:one:player:0'
            with self.assertRaisesRegex(sqlite3.IntegrityError,'cross-unit or mismatched'):ingest_capture(c,bad)
            self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)
            self.assertEqual(c.execute('SELECT count(*) FROM player_badge_values').fetchone()[0],196)

    def test_duplicate_native_identity_withholds_canonical_binding(self):
        m=test_manifest();m['players'][1]['native_unique_id_raw']=m['players'][0]['native_unique_id_raw'];p=self.payload(m)
        self.assertTrue(all(r['player_id'] is None for r in p['facts']['native_player_sources']))
        self.assertTrue(all(r['player_id'] is None for r in p['facts']['player_badge_values']))

    def test_missing_badge_is_not_silently_unowned(self):
        m=test_manifest();m['badge_rows'].pop()
        with self.assertRaisesRegex(ValueError,'incomplete/duplicate'):self.payload(m)

if __name__=='__main__':unittest.main()

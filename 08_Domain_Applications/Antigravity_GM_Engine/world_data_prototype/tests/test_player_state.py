"""Typed native state, absent sources, float/signed storage and source identity."""
from copy import deepcopy
import math,sqlite3,struct,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_capture
from player_state_codec import PROFILE,decode_player_state
from player_state_reader import state_payload,state_projection_ranges
from player_detail_reader import collect_public_player_pool
from live_world import RESTRICTED_PLAYER_RANGES
from query import native_player_state,player_card

def put(raw,group,column,value):
    f=PROFILE['groups'][group][column];start=f['offset'];shift=f['start_bit'];width=f['width'];size=(shift+width+7)//8
    word=int.from_bytes(raw[start:start+size],'little');mask=((1<<width)-1)<<shift;raw[start:start+size]=((word&~mask)|(value<<shift)).to_bytes(size,'little')

def raw_state():
    raw=bytearray(1264);raw[:8]='Test'.encode('utf-16-le');raw[40:50]='State'.encode('utf-16-le')
    struct.pack_into('<f',raw,88,185.5);struct.pack_into('<f',raw,308,75.25)
    put(raw,'vitals','birth_year_raw',2000);put(raw,'vitals','birth_month_raw',12);put(raw,'vitals','birth_day_raw',31)
    put(raw,'health','injury1_type_raw',1);put(raw,'health','injury1_status_raw',4);put(raw,'health','injury1_duration_minutes_raw',9999)
    put(raw,'health','fatigue_raw',127);put(raw,'morale','morale_event_adjustment_raw',255);put(raw,'morale','org_role_raw',6)
    return bytes(raw)

def manifest():
    players=[];states=[]
    for i,name in enumerate(('State Test','Other Source')):
        players.append({'source_player_index':i,'native_unique_id_raw':i+1,'preserved_id_raw':i+100,'observed_name':name,'name_status':'OBSERVED_UTF16_PREFIX','native_team_id':0 if i==0 else None,
            'current_core_roster_status':'CURRENT_CORE_ROSTER' if i==0 else 'NOT_CURRENT_CORE_ROSTER','current_roster_slot':0 if i==0 else None})
        states.append({'source_player_index':i,**decode_player_state(raw_state(),struct.pack('<HH',19785,20500),appearance_status='NATIVE_APPEARANCE_PUBLIC_FIELDS_OBSERVED')})
    return {'season_year':2022,'descriptors':{'1':{'count':2}},'players':players,'state_rows':states,'game_writes':False,'restricted_player_bytes_read':0}

class NativePlayerStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'save')
    def payload(self,token='one',m=None):
        return state_payload({'save_id':'save','native_save_filename':'MyLEAGUE0003'},m or manifest(),[{'sha256':'0'*64,'payload_kind':'EXPLICIT_SYNTHETIC_CODEC_TEST'}],
            '2026-10-25T00:00:00Z',token,{'player:native:100':'State Test'})

    def test_named_height_units_float_storage_and_signed_adjustment(self):
        state=decode_player_state(raw_state(),struct.pack('<HH',19785,20500),appearance_status='OBSERVED')
        self.assertEqual(state['vitals']['height_cm_native_derived'],197.85);self.assertEqual(state['vitals']['wingspan_cm_native_derived'],205.0)
        self.assertEqual(state['vitals']['weight_real'],185.5);self.assertEqual(state['morale']['morale_real'],75.25)
        self.assertEqual(state['morale']['morale_event_adjustment_raw'],255);self.assertEqual(state['morale']['morale_event_adjustment_signed'],-1)
        self.assertEqual(state['morale']['org_role_label'],'FOUNDATION');self.assertEqual(state['vitals']['first_name'],'State')

    def test_injury_slots_do_not_manufacture_availability_energy_or_recovery(self):
        state=decode_player_state(raw_state());health=state['health']
        self.assertEqual(health['injury1_type_label'],'APPENDECTOMY');self.assertEqual(health['injury1_status_label'],'OUT')
        self.assertEqual(health['injury2_status_label'],'HEALTHY');self.assertEqual(health['injury1_duration_minutes_raw'],9999)
        for column in ('availability','severity','recovery_days','energy_raw'):self.assertNotIn(column,health)
        for column in ('morale_raw','role_code','role_satisfaction_raw'):self.assertNotIn(column,state['morale'])
        self.assertIsNone(state['vitals']['height_raw']);self.assertNotIn('birth_date',state['vitals']);self.assertNotIn('age_raw',state['vitals'])

    def test_nonfinite_float_and_unknown_enums_are_retained(self):
        raw=bytearray(raw_state());struct.pack_into('<I',raw,88,0x7fc00001);struct.pack_into('<I',raw,308,0x7f800000);put(raw,'health','injury1_status_raw',7)
        state=decode_player_state(bytes(raw));self.assertIsNone(state['vitals']['weight_real']);self.assertIn('7fc00001',state['vitals']['weight_value_text'])
        self.assertEqual(state['morale']['morale_word_raw'],0x7f800000);self.assertIsNone(state['morale']['morale_real']);self.assertIsNone(state['health']['injury1_status_label'])

    def test_private_intervals_never_affect_state_and_public_ranges_exclude_them(self):
        raw=bytearray(raw_state());before=decode_player_state(bytes(raw))
        for low,high in RESTRICTED_PLAYER_RANGES:raw[low:high]=b'\xff'*(high-low)
        self.assertEqual(before,decode_player_state(bytes(raw)))
        self.assertTrue(all(not(low<b and a<high) for low,high in state_projection_ranges() for a,b in RESTRICTED_PLAYER_RANGES))
        with self.assertRaisesRegex(ValueError,'invalid/private'):collect_public_player_pool(None,ranges=[(0,1264)],metadata=[])

    def test_typed_ingest_source_only_query_and_latest_family_card(self):
        p=self.payload();p['facts']['players']=[{'player_id':'player:native:100','display_name':'State Test'}]
        with connect(self.db) as c:ingest_capture(c,p)
        page=native_player_state(self.db,limit=1);self.assertTrue(page['has_more']);self.assertEqual(page['records'][0]['health']['fatigue_raw'],127)
        later=native_player_state(self.db,unit_id=page['unit_id'],after_index=page['next_after_index']);self.assertIsNone(later['records'][0]['player_id'])
        card=player_card(self.db,'player:native:100');self.assertEqual(card['families']['player_morale_observations']['morale_real']['value'],75.25)

    def test_cross_unit_state_child_rolls_back(self):
        first=self.payload();first['facts']['players']=[{'player_id':'player:native:100','display_name':'State Test'}]
        with connect(self.db) as c:
            ingest_capture(c,first);bad=self.payload('two');bad['facts']['player_health_observations'][0]['source_player_id']='player-state:one:player:0'
            with self.assertRaisesRegex(sqlite3.IntegrityError,'cross-unit or mismatched'):ingest_capture(c,bad)
            self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)

    def test_missing_state_subject_cannot_refresh_partial_family(self):
        m=manifest();m['state_rows'].pop()
        with self.assertRaisesRegex(ValueError,'incomplete/duplicate'):self.payload(m=m)

if __name__=='__main__':unittest.main()

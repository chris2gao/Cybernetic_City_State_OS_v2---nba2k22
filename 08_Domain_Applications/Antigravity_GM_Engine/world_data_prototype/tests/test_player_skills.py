"""Public full skill families, source-only subjects and exact ordered play slots."""
from copy import deepcopy
import sqlite3,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_capture
from player_skill_codec import PROFILE,decode_skills
from player_skill_reader import skill_payload,skill_projection_ranges
from query import native_player_skills,player_card
from live_world import RESTRICTED_PLAYER_RANGES

def manifest():
    players=[];rows=[]
    for i,name in enumerate(('Skill Test','Source Only')):
        players.append({'source_player_index':i,'native_unique_id_raw':i+1,'preserved_id_raw':i+100,'observed_name':name,'name_status':'OBSERVED_UTF16_PREFIX',
            'native_team_id':0 if i==0 else None,'current_core_roster_status':'CURRENT_CORE_ROSTER' if i==0 else 'NOT_CURRENT_CORE_ROSTER','current_roster_slot':0 if i==0 else None})
        raw=bytearray(1264)
        for group in ('attributes','tendencies'):
            for name,f in PROFILE[group].items():raw[f['offset']]=f['offset']%256
        raw[360:363]=(0x0cfa|(1<<18)).to_bytes(3,'little');rows.append({'source_player_index':i,**decode_skills(bytes(raw))})
    return {'season_year':2022,'descriptors':{'1':{'count':2}},'players':players,'skill_rows':rows,'game_writes':False,'restricted_player_bytes_read':0}

class PlayerSkillTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'save')
    def payload(self,token='one',m=None):
        p=skill_payload({'save_id':'save','native_save_filename':'MyLEAGUE0003'},m or manifest(),[{'sha256':'0'*64,'payload_kind':'EXPLICIT_SYNTHETIC_SKILL_CODEC_TEST'}],
            '2026-10-25T00:00:00Z',token,{'player:native:100':'Skill Test'})
        p['facts']['players']=[{'player_id':'player:native:100','display_name':'Skill Test'}];return p
    def test_complete_current_families_keep_raw_values_and_unknown_play_code(self):
        row=manifest()['skill_rows'][0];self.assertEqual(len(row['attributes']),56);self.assertEqual(len(row['tendencies']),100)
        self.assertEqual(row['attributes']['emotion_raw'],1106%256);self.assertEqual(row['attributes']['reaction_time_raw'],1111%256)
        self.assertEqual(len({f['offset'] for f in PROFILE['tendencies'].values()}),99)
        self.assertEqual([r['native_play_code'] for r in row['play_types']],['10','15','12','0'])
        self.assertIsNone(row['play_types'][1]['native_play_label']);self.assertEqual(row['play_types'][3]['native_play_label'],'NONE');self.assertEqual(row['tendencies']['is_play_initiator_raw'],1)
    def test_all_private_intervals_are_physically_excluded_and_independent(self):
        raw=bytearray(1264);before=decode_skills(bytes(raw))
        for a,b in RESTRICTED_PLAYER_RANGES:raw[a:b]=b'\xff'*(b-a)
        self.assertEqual(decode_skills(bytes(raw)),before)
        self.assertTrue(all(not(a<d and c<b) for a,b in skill_projection_ranges() for c,d in RESTRICTED_PLAYER_RANGES))
        self.assertTrue(all(not(a<368 and 364<b) for a,b in skill_projection_ranges()))
    def test_source_only_and_current_subjects_query_all_four_slots(self):
        with connect(self.db) as c:ingest_capture(c,self.payload())
        first=native_player_skills(self.db,limit=1);self.assertTrue(first['has_more']);self.assertEqual(first['records'][0]['player_id'],'player:native:100')
        second=native_player_skills(self.db,unit_id=first['unit_id'],after_index=first['next_after_index']);self.assertIsNone(second['records'][0]['player_id'])
        self.assertEqual(len(second['records'][0]['play_types']),4);self.assertIsNone(second['records'][0]['attributes']['overall_raw'])
        with connect(self.db,True) as c:self.assertEqual(c.execute('SELECT count(*) FROM players').fetchone()[0],1)
    def test_missing_subject_columns_or_slot_rejects_complete_family(self):
        for mutate in (lambda m:m['skill_rows'].pop(),lambda m:m['skill_rows'][0]['attributes'].pop('emotion_raw'),lambda m:m['skill_rows'][0]['play_types'].pop()):
            m=manifest();mutate(m)
            with self.assertRaisesRegex(ValueError,'incomplete'):self.payload(m=m)
    def test_mismatched_play_enum_label_is_rejected(self):
        m=manifest();m['skill_rows'][0]['play_types'][1]['native_play_label']='INVENTED'
        with self.assertRaisesRegex(ValueError,'play code/label'):self.payload(m=m)
    def test_each_typed_family_rejects_cross_unit_source_atomically(self):
        with connect(self.db) as c:
            ingest_capture(c,self.payload())
            for i,table in enumerate(('player_attribute_snapshots','player_tendency_snapshots','player_play_type_slots')):
                bad=self.payload('bad'+str(i));bad['facts'][table][0]['source_player_id']='player-skill:one:player:0'
                with self.assertRaisesRegex(sqlite3.IntegrityError,'cross-unit'):ingest_capture(c,bad)
                self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)
    def test_latest_field_history_does_not_refresh_unobserved_overall(self):
        one=self.payload()
        with connect(self.db) as c:
            ingest_capture(c,one);two=self.payload('two');two['observed_at']='2026-10-26T00:00:00Z';two['facts']['player_attribute_snapshots'][0]['emotion_raw']=255;ingest_capture(c,two)
        card=player_card(self.db,'player:native:100');self.assertEqual(card['families']['player_attribute_snapshots']['emotion_raw']['value'],255)
        self.assertIsNone(card['families']['player_attribute_snapshots']['overall_raw']['value'])
        pinned=native_player_skills(self.db,unit_id=one['unit_id']);self.assertNotEqual(pinned['records'][0]['attributes']['emotion_raw'],255)

if __name__=='__main__':unittest.main()

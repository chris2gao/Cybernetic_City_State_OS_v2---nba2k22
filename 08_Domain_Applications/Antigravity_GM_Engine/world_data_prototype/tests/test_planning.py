"""Captured plan/training source replay and same-unit identity boundaries."""
import copy,hashlib,json,sqlite3,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from planning_reader import planning_payload,decode_plan,training_player_values,classify_training_slots
from engine import create_database,connect,ingest_capture
from query import planning_snapshot,gameplan_card
FIXTURE=BASE/'tests/fixtures/planning_20261024'


class PlanningTests(unittest.TestCase):
    def manifest(self):return json.loads((FIXTURE/'manifest.json').read_bytes())
    def payload(self,m=None,token='fixture'):
        return planning_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m or self.manifest(),
            [{'sha256':hashlib.sha256((FIXTURE/'manifest.json').read_bytes()).hexdigest(),'payload_kind':'ACTUAL_CURATED_PLAN_RESEARCH'}],
            '2026-10-24T00:00:00Z',token)

    def test_actual_stored_plan_training_and_associations_roundtrip_without_effect_claim(self):
        m=self.manifest();p=self.payload()
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,p)
            snap=planning_snapshot(db);plan=m['plans'][0]
            card=gameplan_card(db,'team:native:'+str(plan['native_team_id']),'team:native:'+str(plan['native_opponent_team_id']))
            self.assertEqual(len(card['rotations']),23);self.assertEqual(len(card['defenses']),23)
            self.assertEqual(card['plan']['help_defense_raw'],plan['header']['values']['HelpDefense'])
            self.assertEqual(card['game_effect'],'NOT_INFERRED_FROM_COMMIT_FLAG')
            self.assertTrue(snap['families']['player_training_observations']);self.assertTrue(snap['families']['mentorship_relations'])
            self.assertTrue(all(r['association_status']=='OBSERVED_PAIR_ACTIVITY_NOT_VERIFIED' for r in snap['families']['mentorship_relations']))
            self.assertNotIn('potential',json.dumps(card).lower());self.assertNotIn('"address"',json.dumps(snap).lower())
            with self.assertRaisesRegex(ValueError,'no truncation'):planning_snapshot(db,limit=1)
            with connect(db,True) as c:self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())

    def test_unpacked_gameplan_bytes_and_uncommitted_flag_are_not_coach_bits(self):
        m=self.manifest();raw=bytearray((FIXTURE/'gameplan.bin').read_bytes());before=decode_plan(raw,m['defense_catalog'])
        raw[0]=0;raw[0x13C]^=1
        after=decode_plan(raw,m['defense_catalog'])
        self.assertEqual(after['header']['is_in_use'],0);self.assertEqual(after['header']['values'],before['header']['values'])
        raw[0x184]=(raw[0x184]+1)%256
        self.assertNotEqual(decode_plan(raw,m['defense_catalog'])['header']['values']['HelpDefense'],before['header']['values']['HelpDefense'])

    def test_wrong_roster_owner_rejects_atomic_unit(self):
        p=self.payload();plan=p['facts']['gameplan_observations'][0]
        other=next(r['player_id'] for r in p['facts']['roster_memberships'] if r['team_id']==plan['opponent_team_id'])
        p['facts']['gameplan_rotation_observations'][0]['player_id']=other
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:
                with self.assertRaisesRegex(sqlite3.IntegrityError,'same-unit roster owner'):ingest_capture(c,p)
            with connect(db,True) as c:self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],0)

    def test_child_cannot_borrow_a_parent_from_an_older_unit(self):
        p=self.payload();plan=p['facts']['gameplan_observations'][0]
        q=self.payload(token='new');q['facts']={'gameplan_rotation_observations':[{'plan_id':plan['plan_id'],'slot_index':0,
            'native_rotation_id_raw':65535,'identity_status':'EMPTY_SENTINEL'}]}
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,p)
            with connect(db) as c:
                with self.assertRaisesRegex(sqlite3.IntegrityError,'cross-unit gameplan child'):ingest_capture(c,q)

    def test_duplicate_training_id_is_staged_without_selecting_first(self):
        m=self.manifest();slot=copy.deepcopy(next(p for p in m['player_training_slots'] if p['identity_status']=='UNIQUE_CURRENT_ROSTER_ID'))
        duplicate=copy.deepcopy(slot);duplicate['source_slot_index']=999
        m['player_training_slots']=classify_training_slots([slot,duplicate],{p['native_player_id'] for p in m['players']})
        p=self.payload(m);self.assertEqual(len(p['facts']['player_training_slot_observations']),2)
        self.assertEqual(p['facts']['player_training_observations'],[])
        self.assertTrue(all(p['identity_status']=='DUPLICATE_NATIVE_ID' for p in m['player_training_slots']))
        raw=(FIXTURE/'player-training-flags.bin').read_bytes();self.assertIn('intensity_raw',training_player_values(raw))

    def test_ambiguous_mentee_is_not_assigned_one_arbitrary_mentor(self):
        m=self.manifest();first=copy.deepcopy(m['mentor_relations'][0]);second=copy.deepcopy(first);second['source_slot_index']+=1
        m['mentor_relations']=[first,second];p=self.payload(m)
        self.assertEqual(p['facts']['mentorship_relations'],[])
        self.assertEqual(len(p['facts']['native_mentor_relation_observations']),2)


if __name__=='__main__':unittest.main()

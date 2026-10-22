"""Synthetic SQLite/source integration only: no real saves, capture or upload."""
import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from test_coaching_safety import fixture,PROFILE
from config import CORE_TEAM_IDS
from coaching_source import (ensure_coaching_schema,store_coaching_source,load_coaching_source,
    validate_source,coaching_public_files,capture_coaching_source,audit_coaching_source)


def synthetic_source():
    _,source,_=fixture()
    template=source['teams'][0]
    source['teams']=[]
    source['context_identity']={}
    source['observed_at']='2026-10-17T01:00:00+00:00'
    source['process_binding']='SYNTHETIC_PROCESS_NOT_GAME'
    source['capture_profile']=copy.deepcopy(PROFILE)
    source['defensive_field_catalog']=copy.deepcopy(PROFILE['defensive_fields'])
    for tid in sorted(CORE_TEAM_IDS):
        team=copy.deepcopy(template)
        identity=dict(team_id=tid,role='HEAD_COACH',identity_tag='SYNTHETIC_'+str(tid))
        team.update(team_id=tid,abbreviation='T'+str(tid),coach_identity=identity,roster_signature='FAKE_ROSTER_'+str(tid),
            readiness={n:f['readiness'] for n,f in PROFILE['fields'].items()},
            freelance_sets=[team['values'][n] for n in PROFILE['freelance_slot_order']],
            gameplans=[dict(opponent_team_id=opp,is_in_use=0,defensive_matchups=[],rotations=[],values={})
                for opp in sorted(CORE_TEAM_IDS) if opp!=tid])
        source['teams'].append(team)
        source['context_identity'][str(tid)]=dict(coach_identity=identity,roster_signature=team['roster_signature'])
    return source


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.conn=sqlite3.connect(':memory:')
        self.source=synthetic_source()
    def tearDown(self):self.conn.close()
    def store(self):store_coaching_source(self.conn,'TEST_BATCH',self.source['career_id'],self.source)
    def test_same_batch_storage_roundtrip_has_no_runtime_pid(self):
        self.store()
        restored=load_coaching_source(self.conn,'TEST_BATCH')
        self.assertEqual(len(restored['teams']),30)
        self.assertNotIn('process_pid',restored)
        self.assertNotIn('process_creation_time',restored)
        self.assertNotIn('defensive_matchups',restored['teams'][0]['gameplans'][0])
        self.assertEqual(restored['process_binding'],self.source['process_binding'])
    def test_missing_team_or_field_or_duplicate_owner_rejected(self):
        for kind in ('team','field','owner'):
            source=copy.deepcopy(self.source)
            if kind=='team':source['teams'].pop()
            elif kind=='field':source['teams'][0]['values'].pop('Tempo')
            else:source['teams'][0]['coach_identity']['identity_tag']=source['teams'][1]['coach_identity']['identity_tag']
            with self.assertRaises(ValueError):validate_source(source)
    def test_wrong_save_batch_timestamp_and_raw_value_fail(self):
        with self.assertRaises(ValueError):
            store_coaching_source(self.conn,'OTHER_BATCH',self.source['career_id'],self.source)
        self.store()
        with self.assertRaises(ValueError):load_coaching_source(self.conn,'TEST_BATCH','OTHER_SAVE')
        with self.assertRaises(ValueError):load_coaching_source(self.conn,'TEST_BATCH',data_updated_at='LATER')
        self.source['teams'][0]['values']['POEOffense']=2
        with self.assertRaisesRegex(ValueError,'RAW_BLOCK_VALUE_MISMATCH'):validate_source(self.source)
    def test_failed_capture_preserves_prior_source(self):
        self.store()
        self.conn.commit()
        self.source['teams'].pop()
        with self.assertRaises(ValueError):self.store()
        self.conn.rollback()
        self.assertEqual(len(load_coaching_source(self.conn,'TEST_BATCH')['teams']),30)
    def test_percent_out_of_ui_range_rejects_capture_preserving_last_good(self):
        from coach_codec import block_key
        self.store()
        self.conn.commit()
        for name in ('HelpDefense','RunPlayTendency','ZoneUsage','BenchUtilization'):
            with self.subTest(field=name):
                source=copy.deepcopy(self.source)
                field=source['capture_profile']['fields'][name]
                self.assertEqual(field['observation_raw_range'],[0,100])
                row=source['teams'][0]
                key=block_key(field['offset'],field['storage_bytes'])
                old=int.from_bytes(bytes.fromhex(row['blocks'][key]),'little')
                mask=((1<<field['width'])-1)<<field['start_bit']
                row['blocks'][key]=((old&~mask)|(101<<field['start_bit'])).to_bytes(field['storage_bytes'],'little').hex()
                row['values'][name]=101
                with self.assertRaisesRegex(ValueError,'OUTSIDE_OBSERVED_UI_RAW_RANGE'):
                    store_coaching_source(self.conn,'TEST_BATCH',source['career_id'],source)
                self.conn.rollback()
                self.assertEqual(load_coaching_source(self.conn,'TEST_BATCH')['teams'][0]['values'][name],
                                 self.source['teams'][0]['values'][name])
    def test_bench_observation_is_not_limited_to_old_test_values(self):
        from coach_codec import block_key
        source=copy.deepcopy(self.source)
        field=source['capture_profile']['fields']['BenchDepth']
        self.assertNotIn('raw_range',field)
        row=source['teams'][0]
        row['values']['BenchDepth']=11
        row['blocks'][block_key(field['offset'],field['storage_bytes'])]='0b'
        self.assertEqual(validate_source(source)['status'],'OBSERVED')
    def test_source_cannot_use_write_capable_handle(self):
        with self.assertRaisesRegex(PermissionError,'READ_ONLY_HANDLE'):
            capture_coaching_source(type('Mem',(),{'read_only':False})(),{})
    def test_small_public_files_no_player_matchups_or_opponent_offense(self):
        files=coaching_public_files(self.source,'PUBLISHED_BATCH','2026-10-17T01:01:00+00:00')
        self.assertEqual(len(files),33)
        teams=files['coaching/teams.json']
        self.assertEqual(teams['source_batch_id'],'PUBLISHED_BATCH')
        self.assertEqual(len(teams['teams'][0]['values']),19)
        self.assertNotIn('gameplans',teams['teams'][0])
        self.assertNotIn('SimPace',files['coaching/field_dictionary.json']['default_fields'])
        self.assertEqual(len(teams['teams'][0]['sim_read_only']),5)
        opponent=next(v for k,v in files.items() if k.startswith('coaching/opponents/T'))
        self.assertNotIn('values',opponent['records'][0])
        self.assertNotIn('defensive_matchups',opponent['records'][0])
    def test_export_uses_captured_profile_not_later_readiness(self):
        self.source['capture_profile']['fields']['PreferredSystem']['production_enabled']=False
        files=coaching_public_files(self.source,'PUBLISHED_BATCH','2026-10-17T01:01:00+00:00')
        self.assertFalse(files['coaching/field_dictionary.json']['default_fields']['PreferredSystem']['production_enabled'])
    def test_native_source_audit_rejects_later_value(self):
        self.store()
        live=copy.deepcopy(self.source)
        with patch('coaching_source.capture_coaching_source',return_value=live):
            self.assertTrue(all(audit_coaching_source(self.conn,None,'TEST_BATCH').values()))
        live['teams'][0]['values']['Tempo']+=1
        with patch('coaching_source.capture_coaching_source',return_value=live):
            with self.assertRaisesRegex(RuntimeError,'VALUES_CHANGED_DURING_AUDIT'):
                audit_coaching_source(self.conn,None,'TEST_BATCH')
    def test_legacy_capture_stays_absent(self):
        self.assertIsNone(load_coaching_source(self.conn,'OLD_CAPTURE'))
        ensure_coaching_schema(self.conn)
        self.assertIsNone(load_coaching_source(self.conn,'OLD_CAPTURE'))

    def test_lazy_opponent_reader_rejects_date_owner_and_missing_other_opponents(self):
        from gm_core.data_reader import DataReader
        files=coaching_public_files(self.source,'PUBLISHED_BATCH','2026-10-17T01:01:00+00:00')
        teams=files['coaching/teams.json']
        team=teams['teams'][0]
        relative=team['opponent_file']
        original=files[relative]
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            path=root/relative
            path.parent.mkdir(parents=True)
            data=SimpleNamespace(coaching=teams,batch_directory=root,source=SimpleNamespace(
                career_id=teams['career_id'],batch_id=teams['source_batch_id'],
                data_updated_at=teams['data_updated_at'],game_date=teams['game_date']))
            opponent=original['records'][0]['opponent_team_id']
            path.write_text(json.dumps(original),encoding='utf-8')
            self.assertEqual(DataReader(root).coaching_opponent(data,team['team_id'],opponent),original['records'][0])
            for mutation in ('date','owner','missing'):
                payload=copy.deepcopy(original)
                if mutation=='date':payload['game_date']='1900-01-01'
                elif mutation=='owner':payload['team_id']=opponent
                else:payload['records'].pop()
                path.write_text(json.dumps(payload),encoding='utf-8')
                with self.assertRaises(ValueError):DataReader(root).coaching_opponent(data,team['team_id'],opponent)

    def test_one_opponent_owner_file_attaches_without_loading_other_owners(self):
        from gm_core.data_reader import attach_coaching_opponents
        files=coaching_public_files(self.source,'PUBLISHED_BATCH','2026-10-17T01:01:00+00:00')
        snapshot=files['coaching/teams.json']
        owner=snapshot['teams'][0]
        payload=files[owner['opponent_file']]
        attach_coaching_opponents(snapshot,payload)
        self.assertEqual(len(owner['gameplans']),29)
        self.assertEqual(owner['gameplans'][0]['is_in_use'],payload['records'][0]['is_in_use_raw'])
        self.assertNotIn('gameplans',snapshot['teams'][1])
        with self.assertRaisesRegex(ValueError,'duplicate'):attach_coaching_opponents(snapshot,payload)


if __name__=='__main__':unittest.main()

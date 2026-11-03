"""Synthetic-only isolated SQLite prototype tests. No game process or save access."""
from pathlib import Path
import json
import sqlite3
import sys
from tempfile import TemporaryDirectory
import unittest

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_synthetic_capture,read_gm_observations,summarize
from cli import synthetic_payload,smoke
from schema_model import TABLES

class WorldDataPrototypeTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.db=Path(self.temp.name)/'save.sqlite'
        create_database(self.db,'save-alpha')
        self.payload=synthetic_payload(save_id='save-alpha')

    def ingest(self,payload=None):
        with connect(self.db) as con:return ingest_synthetic_capture(con,payload or self.payload)

    def test_create_and_no_overwrite(self):
        with self.assertRaises(FileExistsError):create_database(self.db,'save-beta')
        self.assertEqual(summarize(self.db)['table_count'],len(TABLES))
        with connect(self.db) as c:
            self.assertEqual(c.execute('SELECT save_id FROM saves').fetchone()[0],'save-alpha')
            with self.assertRaises(sqlite3.IntegrityError):c.execute('UPDATE saves SET save_id="changed"')

    def test_cross_save_rejected_without_change(self):
        bad=dict(self.payload,save_id='save-beta')
        with self.assertRaisesRegex(ValueError,'cross-save'):self.ingest(bad)
        self.assertEqual(summarize(self.db)['capture_units'],0)

    def test_repeat_unit_is_idempotent_and_change_conflicts(self):
        self.assertEqual(self.ingest(),'ingested')
        self.assertEqual(self.ingest(),'already_applied')
        changed=json.loads(json.dumps(self.payload));changed['attributes'][0]['overall_raw']=99
        with self.assertRaisesRegex(ValueError,'conflicting'):self.ingest(changed)
        self.assertEqual(summarize(self.db)['attribute_observations'],1)

    def test_same_value_in_new_unit_is_new_history(self):
        self.ingest()
        two=synthetic_payload('save-alpha',run_id='run-2',unit_id='unit-2',observed_at='2026-10-25T00:00:00Z')
        self.ingest(two)
        rows=read_gm_observations(self.db,'player-a')
        self.assertEqual(len(rows),2)
        self.assertEqual([r['overall_raw'] for r in rows],[82,82])
        with connect(self.db) as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM player_badge_values').fetchone()[0],2)
            self.assertEqual(c.execute('SELECT COUNT(*) FROM player_play_type_slots').fetchone()[0],2)

    def test_failed_unit_cannot_apply_facts(self):
        bad=synthetic_payload('save-alpha');bad.update(unit_status='failed',teams=[],players=[],game=None,boxes=[],attributes=[],tendencies=[],badges=[],play_types=[],game_state=None)
        self.assertEqual(self.ingest(bad),'failed_recorded')
        self.assertEqual(summarize(self.db)['attribute_observations'],0)
        with connect(self.db) as c:
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute('INSERT INTO player_attribute_snapshots(snapshot_id,player_id,unit_id,overall_raw) VALUES(?,?,?,?)',('a','p','unit-1',1))

    def test_append_only_and_fk(self):
        self.ingest()
        with connect(self.db) as c:
            with self.assertRaises(sqlite3.IntegrityError):c.execute('UPDATE player_attribute_snapshots SET overall_raw=99')
            with self.assertRaises(sqlite3.IntegrityError):c.execute('DELETE FROM player_game_boxes')
            with self.assertRaises(sqlite3.IntegrityError):c.execute('INSERT INTO player_game_boxes(box_id,game_id,player_id,team_id,unit_id,points) VALUES(?,?,?,?,?,?)',('x','unknown-game','player-a','team-a','unit-1',2))
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_reject_hidden_potential_and_transaction_rolls_back(self):
        bad=json.loads(json.dumps(self.payload));bad['attributes'][0]['potential_raw']=91
        with self.assertRaises(PermissionError):self.ingest(bad)
        self.assertEqual(summarize(self.db)['game_count'],0)
        self.assertEqual(summarize(self.db)['capture_units'],0)
        self.assertEqual(self.ingest(),'ingested')
        with connect(self.db) as c:
            view_columns=[r[1].lower() for r in c.execute('PRAGMA table_info(gm_player_observations)')]
            self.assertFalse(any('potential' in x for x in view_columns))

    def test_reject_other_unapproved_player_field(self):
        bad=json.loads(json.dumps(self.payload));bad['attributes'][0]['secret_field']=99
        with self.assertRaises(PermissionError):self.ingest(bad)

    def test_game_team_mismatch_fails_cleanly(self):
        bad=json.loads(json.dumps(self.payload));bad['boxes'][0]['team_id']='team-nonparticipant'
        with self.assertRaises(ValueError):self.ingest(bad)
        self.assertEqual(summarize(self.db)['capture_units'],0)

    def test_native_claim_is_rejected(self):
        bad=dict(self.payload,evidence_grade='NATIVE_VERIFIED')
        with self.assertRaises(ValueError):self.ingest(bad)

    def test_smoke_cli_function(self):
        results=smoke();self.assertEqual(results['attribute_observations'],2)
        self.assertEqual(results['foreign_key_errors'],0)

if __name__=='__main__':unittest.main()

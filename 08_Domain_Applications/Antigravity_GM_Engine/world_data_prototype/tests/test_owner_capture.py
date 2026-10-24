"""Actual captured-byte controls; replay tests are not fresh live-call proof."""
import hashlib,json,shutil,sqlite3,subprocess,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from owner_capture import recorded_game_capture
from engine import connect,create_database,ingest_capture,migrate_database
from query import inspect_source_capture,history
FIXTURE=BASE/'tests/fixtures/owner_capture_20261024'


class OwnerCaptureTests(unittest.TestCase):
    def test_actual_game_to_typed_unresolved_staging_without_invented_players(self):
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'source.sqlite';create_database(db,'SOURCE_RESEARCH_ONLY')
            payload=recorded_game_capture(FIXTURE,'SOURCE_RESEARCH_ONLY')
            with connect(db) as c:ingest_capture(c,payload)
            result=inspect_source_capture(db,payload['unit_id'])
            self.assertEqual(sum(r['rows'] for r in result['typed_native_box_staging']),26)
            self.assertEqual(sorted(r['derived_box_points'] for r in result['typed_native_box_staging']),[106,122])
            self.assertEqual(sorted(r['regulation_period_sum'] for r in result['period_sums']),[106,122])
            self.assertEqual(result['canonical_player_box_rows'],0)
            with connect(db) as c:
                self.assertEqual(c.execute('SELECT count(*) FROM players').fetchone()[0],0)
                self.assertIsNone(c.execute('SELECT game_date FROM games').fetchone()[0])
                self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
            with self.assertRaises(PermissionError):history(db,'native_box_observations')

    def test_changed_source_hash_is_rejected(self):
        with TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';shutil.copytree(FIXTURE,source)
            raw=bytearray((source/'box.bin').read_bytes());raw[1]^=1;(source/'box.bin').write_bytes(raw)
            with self.assertRaisesRegex(ValueError,'hash mismatch'):recorded_game_capture(source,'SOURCE_RESEARCH_ONLY')

    def test_json_pass_claim_cannot_hide_the_wrong_offset_bytes(self):
        with TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';shutil.copytree(FIXTURE,source)
            bad=(source/'bad-offset-box.bin').read_bytes();(source/'box.bin').write_bytes(bad)
            report=json.loads((source/'live-probe-report.json').read_text())
            digest=hashlib.sha256(bad).hexdigest();report['artifact_sha256']['box.bin']=digest
            for call in report['read_trace']:
                if call.get('label')=='ONE_GAME_PARTICIPANT_STATBANK':call['sha256']=digest
            (source/'live-probe-report.json').write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError,'score conservation'):recorded_game_capture(source,'SOURCE_RESEARCH_ONLY')

    def test_v2_copy_upgrade_preserves_all_domains_and_registry_history(self):
        with TemporaryDirectory() as tmp:
            old=Path(tmp)/'v2.sqlite';new=Path(tmp)/'v3.sqlite'
            sql=subprocess.run(['git','show','7e14e145ce9a510ada07bbc21874ba9ffb71ceb3:08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/schema.sql'],cwd=BASE.parents[2],capture_output=True,text=True,check=True).stdout
            c=sqlite3.connect(old)
            try:
                c.executescript(sql)
                c.execute("INSERT INTO saves(singleton,save_id,schema_version,created_at,source_grade) VALUES(1,'s',2,'2026-10-24T00:00:00Z','SYNTHETIC_ONLY')")
                c.execute("INSERT INTO native_fields(field_id,source_group,native_key,source_ref) VALUES('players.player_id','RES-P','player_id','OLDER_EVIDENCE')")
                c.execute("INSERT INTO seasons(season_id,season_code) VALUES('s1','2021-22')")
                c.execute("INSERT INTO capture_runs(run_id,season_id,observed_at,source_grade) VALUES('r','s1','2026-10-24T00:00:00Z','SYNTHETIC_FIXTURE')")
                c.execute("INSERT INTO capture_units(unit_id,run_id,source_key,payload_sha256,unit_status,observed_at) VALUES('u','r','source','hash','success','2026-10-24T00:00:00Z')")
                c.execute("INSERT INTO teams(team_id,display_name) VALUES('t','Synthetic')")
                c.execute("INSERT INTO team_finance_observations(finance_id,team_id,unit_id,payroll_raw) VALUES('f','t','u',1000)")
                c.execute('PRAGMA user_version=2');c.commit()
            finally:c.close()
            before=hashlib.sha256(old.read_bytes()).hexdigest();migrate_database(old,new)
            self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(),before)
            with connect(new) as c:
                self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],3)
                self.assertEqual(c.execute('SELECT payroll_raw FROM team_finance_observations').fetchone()[0],1000)
                self.assertEqual(c.execute("SELECT source_ref FROM native_fields WHERE field_id='players.player_id'").fetchone()[0],'OLDER_EVIDENCE')
                self.assertTrue(c.execute("SELECT 1 FROM native_fields WHERE field_id='native_box_observations.native_player_id'").fetchone())
                self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])


if __name__=='__main__':unittest.main()

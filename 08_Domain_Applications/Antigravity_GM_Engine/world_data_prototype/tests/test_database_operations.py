"""Recover committed facts, reject incomplete/corrupt/cross-save snapshots."""
from copy import deepcopy
import json,sqlite3,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_synthetic_capture
from cli import synthetic_payload
from database_operations import backup_facts,restore_facts,validate_backup,inventory,storage_profile,project_observations,file_sha256
from query import player_card

class DatabaseOperationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.db=self.root/'world.sqlite';self.backup=self.root/'snapshot'
        create_database(self.db,'demo-alpha')
        with connect(self.db) as c:ingest_synthetic_capture(c,synthetic_payload())
    def test_complete_round_trip_preserves_schema_rows_and_role_results(self):
        before=inventory(self.db);manifest=backup_facts(self.db,self.backup);target=self.root/'restored.sqlite';receipt=restore_facts(self.backup,target,expected_save_id='demo-alpha')
        self.assertEqual(before,manifest['inventory']);self.assertEqual(before,inventory(target));self.assertEqual(player_card(self.db,'player-a'),player_card(target,'player-a'))
        self.assertEqual(file_sha256(target),manifest['sha256']);self.assertFalse(receipt['active_save_binding_changed']);self.assertFalse(manifest['source_artifact_files_included'])
    def test_wrong_save_rejects_before_creating_destination(self):
        backup_facts(self.db,self.backup);target=self.root/'wrong.sqlite'
        with self.assertRaisesRegex(ValueError,'different save'):restore_facts(self.backup,target,expected_save_id='another-save')
        self.assertFalse(target.exists())
    def test_corrupt_database_rejects_before_creating_destination(self):
        backup_facts(self.db,self.backup);backup_db=self.backup/'facts.sqlite'
        with backup_db.open('r+b') as f:f.seek(4096);original=f.read(1);f.seek(4096);f.write(bytes([original[0]^1]))
        target=self.root/'bad.sqlite'
        with self.assertRaisesRegex(ValueError,'hash mismatch'):restore_facts(self.backup,target,expected_save_id='demo-alpha')
        self.assertFalse(target.exists())
    def test_incomplete_or_altered_manifest_is_not_restorable(self):
        self.backup.mkdir();(self.backup/'facts.pending.sqlite').write_bytes(b'incomplete')
        with self.assertRaises(FileNotFoundError):validate_backup(self.backup,expected_save_id='demo-alpha')
        other=self.root/'complete';manifest=backup_facts(self.db,other);manifest['inventory']['tables']['players']['rows']+=1;(other/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'logical inventory'):validate_backup(other,expected_save_id='demo-alpha')
    def test_existing_destination_and_source_are_never_overwritten(self):
        backup_facts(self.db,self.backup);before=file_sha256(self.db)
        with self.assertRaises(FileExistsError):restore_facts(self.backup,self.db,expected_save_id='demo-alpha')
        with self.assertRaises(FileExistsError):backup_facts(self.db,self.backup)
        self.assertEqual(file_sha256(self.db),before)
    def test_wal_backup_includes_commits_and_excludes_uncommitted_writer(self):
        writer=sqlite3.connect(self.db);self.addCleanup(writer.close);writer.execute('PRAGMA journal_mode=WAL');writer.execute('PRAGMA wal_autocheckpoint=0')
        writer.execute("INSERT INTO players(player_id,display_name) VALUES('committed','Committed')");writer.commit();writer.execute('BEGIN');writer.execute("INSERT INTO players(player_id,display_name) VALUES('pending','Pending')")
        self.assertTrue(Path(str(self.db)+'-wal').stat().st_size>0);backup_facts(self.db,self.backup);target=self.root/'wal-restored.sqlite';restore_facts(self.backup,target,expected_save_id='demo-alpha')
        with connect(target,True) as c:
            self.assertEqual(c.execute("SELECT count(*) FROM players WHERE player_id='committed'").fetchone()[0],1);self.assertEqual(c.execute("SELECT count(*) FROM players WHERE player_id='pending'").fetchone()[0],0)
        writer.rollback()
    def test_interrupted_page_copy_keeps_no_complete_manifest(self):
        before=file_sha256(self.db)
        with patch('database_operations.time.monotonic',side_effect=[0,2]):
            with self.assertRaises(TimeoutError):backup_facts(self.db,self.backup,max_seconds=1)
        self.assertFalse((self.backup/'manifest.json').exists());self.assertTrue((self.backup/'failure.json').exists());self.assertEqual(file_sha256(self.db),before)
        with self.assertRaises(FileNotFoundError):validate_backup(self.backup,expected_save_id='demo-alpha')
    def test_measured_profile_and_explicit_projection_are_distinct(self):
        profile=storage_profile(self.db);self.assertEqual(profile['tables']['players']['rows'],1);self.assertEqual(profile['latest_source_units'][0]['source_key'],'SYNTHETIC_DEMO')
        self.assertEqual(profile['page_size']*profile['page_count'],self.db.stat().st_size)
        if profile['dbstat_status']=='MEASURED_SQLITE_DBSTAT':
            model=project_observations(profile,source_calls_per_season={'SYNTHETIC_DEMO':40},years=100)
            self.assertEqual(model['tables']['player_attribute_snapshots']['additional_rows'],4000);self.assertFalse(model['capacity_pass'])
            with self.assertRaisesRegex(ValueError,'known source'):project_observations(profile,source_calls_per_season={'INVENTED':40},years=100)

if __name__=='__main__':unittest.main()

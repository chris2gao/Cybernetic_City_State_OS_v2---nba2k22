"""Real SQLite/export staging on synthetic temp data; no game or network.

The pre-existing full-source audit is explicitly stubbed. Coaching storage,
source validation, bundle creation, manifest inclusion and last-good guards run
their real implementations. This does not claim a live production publication.
"""
import base64
import contextlib
import copy
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from test_coaching_source import synthetic_source
from coaching_source import store_coaching_source
from data_context import PREFIX
import export_web_gm as exporter
from snapshot_integrity import snapshot_digest, file_sha256

REPO=Path(__file__).resolve().parents[1]


class CoachingExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.source=synthetic_source()
        self.save=self.source['career_id']
        self.snapshot=self.source['source_batch_id']
        self.updated='2026-10-17T01:01:00+00:00'
        self.db=self.root/'synthetic_league.sqlite'
        self.pool=self.root/'synthetic_pool.sqlite'
        self.snapshots=self.root/'snapshots'
        self.snapshots.mkdir()
        self.context=dict(career_id=self.save,purpose='validation',game_date=None,
            game_date_provenance='UNCONFIRMED',event='SYNTHETIC_EXPORT_TEST',trigger='PLAYER_INITIATED')
        notes=PREFIX+base64.b64encode(json.dumps(self.context).encode()).decode()
        with contextlib.closing(sqlite3.connect(self.db)) as conn,conn:
            conn.executescript((REPO/'database/schema.sql').read_text(encoding='utf-8'))
            conn.execute('INSERT INTO monthly_snapshots(snapshot_id,season_year,month_index,month_name,snapshot_date,notes) VALUES (?,?,?,?,?,?)',
                (self.snapshot,2022,1,'SYNTHETIC','2026-10-17',notes))
            conn.execute('INSERT INTO seasons(season_year,season_code,salary_cap,luxury_tax_threshold) VALUES (?,?,?,?)',(2022,'2021-2022',100,120))
            for team in self.source['teams']:
                tid,abbr=team['team_id'],team['abbreviation']
                conn.execute('INSERT INTO teams(team_id,abbreviation,city,name,memory_address,total_salary) VALUES (?,?,?,?,?,?)',
                    (tid,abbr,'SYNTHETIC','Synthetic '+abbr,'RUNTIME_ONLY',0))
                conn.execute('INSERT INTO team_monthly_stats(snapshot_id,team_id,team_abbr,total_salary) VALUES (?,?,?,?)',
                    (self.snapshot,tid,abbr,0))
            store_coaching_source(conn,self.snapshot,self.save,self.source)
            conn.execute('UPDATE coaching_source_captures SET data_updated_at=?',(self.updated,))
        with contextlib.closing(sqlite3.connect(self.pool)) as conn,conn:
            from dump_player_pool import init_player_pool_schema
            init_player_pool_schema(conn)
            conn.execute('ALTER TABLE player_pool ADD COLUMN source_details_json TEXT')
            from source_extensions import player_details
            raw=bytes(0x4f0)
            detail=json.dumps(player_details(raw))
            conn.execute('INSERT INTO player_pool(slot_id,raw_struct,draft_year,full_name,raw_potential,potential,source_details_json) VALUES (1,?,1984,\'Synthetic Player\',0,25,?)',(raw,detail))
        with contextlib.closing(sqlite3.connect(self.db)) as league,league, contextlib.closing(sqlite3.connect(self.pool)) as pool,pool:
            league.execute('INSERT INTO player_source_details VALUES (?,?,0,1,\'Synthetic Player\',0,NULL,NULL,?,?)',
                           (self.snapshot,self.source['teams'][0]['team_id'],detail,raw))
            from player_potential_mask import sanitize_player_potential
            sanitize_player_potential(league,pool,self.snapshot)
        self.manifest=dict(timestamp=self.updated,data_updated_at=self.updated,quality_metrics={'coaching_tactics':{'profile':1}})
        self.manifest_path=self.snapshots/('ingest_manifest_'+self.snapshot+'.json')
        self.manifest_path.write_text(json.dumps(self.manifest),encoding='utf-8')
        config=self.root/'config'
        config.mkdir()
        (config/'source_catalog.json').write_text((REPO/'config/source_catalog.json').read_text(encoding='utf-8'),encoding='utf-8')
        self.audit=dict(snapshot_id=self.snapshot,audit_timestamp=self.updated,verifier='SYNTHETIC_FULL_AUDIT_STUB',
            verdict='PASS_VERIFIED',checks={'coaching_30_teams_identity_defaults_and_verified_overall_match_live':True},
            counts={},database_digest_sha256='SYNTHETIC_NOT_SOURCE_HASH',player_pool_sha256='SYNTHETIC_NOT_SOURCE_HASH')
        self.patchers=[patch.object(exporter,'ROOT',self.root),patch.object(exporter,'PUBLISHED',self.root/'published'),
            patch.object(exporter,'ARCHIVES',self.root/'_exports/archives'),
            patch.object(exporter,'save_paths',return_value=dict(db_path=str(self.db),player_pool_db_path=str(self.pool),snapshots_dir=str(self.snapshots))),
            patch.object(exporter,'GMEngine')]
        for p in self.patchers:p.start()
        exporter.GMEngine.return_value.verify_snapshot_gate.side_effect=lambda _:copy.deepcopy(self.audit)
    def tearDown(self):
        for p in reversed(self.patchers):p.stop()
        for p in self.root.rglob('*'):
            if p.is_file():p.chmod(0o600)
        self.temp.cleanup()
    def export(self):
        # The M0 consumer needs realistic source/audit bindings even though the
        # live full-source audit remains deliberately stubbed in this fixture.
        with contextlib.closing(sqlite3.connect(self.db)) as c:
            digest=snapshot_digest(c,self.snapshot)
        pool_hash=file_sha256(str(self.pool))
        self.manifest.update(snapshot_id=self.snapshot,save_id=self.save,
                             batch_binding=dict(snapshot_digest_sha256=digest,player_pool_sha256=pool_hash))
        self.manifest_path.write_text(json.dumps(self.manifest),encoding='utf-8')
        self.audit.update(save_id=self.save,database_digest_sha256=digest,player_pool_sha256=pool_hash,
                          player_pool_records=1,manifest_binding=dict(manifest_sha256=file_sha256(str(self.manifest_path))))
        with contextlib.redirect_stdout(io.StringIO()):return exporter.export_snapshot(self.save,self.snapshot)
    def test_real_export_includes_33_coaching_files_and_only_pending_upload(self):
        result=self.export()
        coaching=[p for p in result['files'] if p.startswith('coaching/')]
        self.assertEqual(len(coaching),33)
        pointer=json.loads((self.root/'published/saves'/self.save/'latest.json').read_text(encoding='utf-8'))
        self.assertEqual(pointer['upload_status'],'PENDING_UPLOAD')
        self.assertIsNone(pointer['uploaded_at'])
        bundle=self.root/'published'/pointer['batch_path']
        coverage=json.loads((bundle/'source_coverage.json').read_text(encoding='utf-8'))
        source=next(s for s in coverage['sources'] if s['id']=='coaching_tactics')
        self.assertEqual(source['status'],'VERIFIED_OBSERVED_SAME_BATCH')
        self.assertEqual(source['data_updated_at'],self.updated)
        self.assertTrue((self.root/'_exports/archives'/result['archive']['filename']).is_file())
        self.assertTrue((self.root/'database/query_snapshots'/self.save/result['batch_id']/'manifest.json').is_file())
        catalog=json.loads((bundle/'player_catalog/1984_1.json').read_text(encoding='utf-8'))['records'][0]
        self.assertEqual((catalog['potential'],catalog['raw_potential']),(1,1))
        self.assertTrue(catalog['player_raw_masked'])
        from gm_data_access.query import QuerySession
        with contextlib.closing(QuerySession(self.root/'database/query_snapshots',self.root/'published',self.save,result['batch_id'])) as session:
            self.assertEqual(session.require_gm_sanitized()['potential_mask_version'],'potential_v1')
    def test_missing_coaching_team_does_not_replace_last_good_pointer_or_bundle(self):
        self.export()
        pointer=self.root/'published/saves'/self.save/'latest.json'
        old=pointer.read_bytes()
        batches=list((pointer.parent/'batches').iterdir())
        with contextlib.closing(sqlite3.connect(self.db)) as conn,conn:
            conn.execute('DELETE FROM coaching_team_observations WHERE team_id=?',(self.source['teams'][0]['team_id'],))
        self.manifest['timestamp']='2026-10-17T02:00:00+00:00'
        self.manifest_path.write_text(json.dumps(self.manifest),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'EXACT_30_TEAMS'):self.export()
        self.assertEqual(pointer.read_bytes(),old)
        self.assertEqual(list((pointer.parent/'batches').iterdir()),batches)
    def test_missing_source_audit_rejects_before_new_output(self):
        self.audit['checks']={}
        with self.assertRaisesRegex(RuntimeError,'AUDIT_MISSING'):self.export()
        self.assertFalse((self.root/'published').exists())
    def test_legacy_manifest_is_not_backfilled_with_present_current_source(self):
        self.manifest['quality_metrics']={}
        self.manifest_path.write_text(json.dumps(self.manifest),encoding='utf-8')
        result=self.export()
        self.assertFalse(any(p.startswith('coaching/') for p in result['files']))

    def test_query_snapshot_failure_preserves_published_pointer(self):
        self.export()
        pointer=self.root/'published/saves'/self.save/'latest.json'
        original=pointer.read_bytes()
        self.manifest['timestamp']='2026-10-17T03:00:00+00:00'
        with patch('gm_data_access.snapshots.install_archive',side_effect=RuntimeError('SYNTHETIC_QUERY_INSTALL_FAILURE')):
            with self.assertRaisesRegex(RuntimeError,'QUERY_INSTALL_FAILURE'):self.export()
        self.assertEqual(pointer.read_bytes(),original)


if __name__=='__main__':unittest.main()

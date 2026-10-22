"""DEV15 persisted data masking only. All databases and native bytes synthetic."""
import copy
from contextlib import closing
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from player_potential_mask import sanitize_player_potential,verify_sanitized_pair,mask_raw,mask_details,MARKERS
from source_extensions import player_details
from gm_data_access.query import QuerySession
from gm_data_access import AccessError
from historical_rookies import query_historical_draft_class,preflight_native_rookie_source


class PotentialMaskTests(unittest.TestCase):
    def setUp(self):
        self.league=sqlite3.connect(':memory:');self.pool=sqlite3.connect(':memory:')
        self.addCleanup(self.league.close);self.addCleanup(self.pool.close)
        self.raw=bytearray(0x4f0);self.raw[0x440]=123;self.raw[0x441]=222;self.raw[0x70]=0xe0
        self.raw[0x100:0x105]=b'guard'
        self.raw=bytes(self.raw)
        self.details=player_details(self.raw)
        self.pool.execute('CREATE TABLE player_pool(slot_id INTEGER PRIMARY KEY,full_name TEXT,draft_year INTEGER,draft_round INTEGER,draft_pick INTEGER,raw_potential INTEGER,potential INTEGER,raw_struct BLOB,source_details_json TEXT)')
        self.pool.execute('INSERT INTO player_pool VALUES (1,?,?,?,?,?,?,?,?)',('Synthetic Rookie',1984,1,1,222,99,self.raw,json.dumps(self.details)))
        self.league.execute('CREATE TABLE player_source_details(snapshot_id TEXT,team_id INTEGER,roster_slot INTEGER,raw_struct BLOB,details_json TEXT)')
        for sid in ('M01','M02'):
            self.league.execute('INSERT INTO player_source_details VALUES (?,31,0,?,?)',(sid,self.raw,json.dumps(self.details)))
        self.league.execute('CREATE TABLE staff_source_details(details_json TEXT,raw_struct BLOB)')
        self.league.execute('INSERT INTO staff_source_details VALUES (?,?)',(json.dumps({'attributes':{'potential':{'raw':233,'value':99}}}),bytes([233])*0x160))
        self.league.execute('CREATE TABLE state_io_objects(snapshot_id TEXT,object_key TEXT,object_json TEXT)')
        self.league.execute('CREATE TABLE state_io_captures(snapshot_id TEXT,metadata_json TEXT)')
        for i,kind in enumerate(('PLAYER_TENDENCY','PLAYER_PLAYTYPE','PLAYER_ROTATION_OVR_BIAS')):
            obj=dict(selector=dict(target_kind=kind),raw=self.raw.hex(),values={},field_keys=[])
            self.league.execute('INSERT INTO state_io_objects VALUES (?,?,?)',('M02',str(i),json.dumps(obj)))
        self.league.execute("INSERT INTO state_io_captures VALUES ('M02','{}')")
        self.pool.commit();self.league.commit()

    def test_every_player_surface_masks_only_potential_and_staff_stays_original(self):
        staff=self.league.execute('SELECT * FROM staff_source_details').fetchone()
        result=sanitize_player_potential(self.league,self.pool,'M02')
        self.assertEqual(result['counts'],dict(pool=1,roster=2,state_io_player_mirrors=3))
        raw,pot,rpot,detail=self.pool.execute('SELECT raw_struct,potential,raw_potential,source_details_json FROM player_pool').fetchone()
        self.assertEqual((pot,rpot),(1,1))
        self.assertEqual([i for i,(old,new) in enumerate(zip(self.raw,raw)) if old!=new],[0x441])
        self.assertEqual(raw[0x440],123);self.assertEqual(raw[0x70],0xe0)
        self.assertEqual(mask_details(player_details(raw)),mask_details(player_details(self.raw)))
        data=json.loads(detail)
        self.assertEqual(data['attributes']['potential'],dict(raw=1,value=1,visibility='MASKED_BY_GM_WORLD_RULE',evidence='NOT_GAME_OBSERVED'))
        self.assertEqual(self.league.execute('SELECT * FROM staff_source_details').fetchone(),staff)
        verify_sanitized_pair(self.league,self.pool,'M02')
        before=(list(self.league.iterdump()),list(self.pool.iterdump()))
        self.assertEqual(sanitize_player_potential(self.league,self.pool,'M02'),result)
        self.assertEqual((list(self.league.iterdump()),list(self.pool.iterdump())),before)
        for row in self.league.execute('SELECT raw_struct,details_json FROM player_source_details'):
            self.assertEqual(row[0],raw);self.assertEqual(json.loads(row[1]),data)
        for payload, in self.league.execute('SELECT object_json FROM state_io_objects'):
            obj=json.loads(payload);self.assertEqual(bytes.fromhex(obj['raw']),raw)
            self.assertTrue(obj['player_raw_masked'])

    def test_failure_after_pool_changes_rolls_back_both_working_copies(self):
        self.league.execute("UPDATE player_source_details SET raw_struct=x'01' WHERE snapshot_id='M02'")
        pool_before=list(self.pool.iterdump());league_before=list(self.league.iterdump())
        with self.assertRaisesRegex(ValueError,'POTENTIAL_SANITIZATION_FAILED'):
            sanitize_player_potential(self.league,self.pool,'M02')
        self.assertEqual(list(self.pool.iterdump()),pool_before)
        self.assertEqual(list(self.league.iterdump()),league_before)

    def test_dry_run_verifies_then_restores_data_and_unknown_mirrors_fail_closed(self):
        pool_before=list(self.pool.iterdump());league_before=list(self.league.iterdump())
        self.assertTrue(sanitize_player_potential(self.league,self.pool,'M02',dry_run=True)['dry_run'])
        self.assertEqual(list(self.pool.iterdump()),pool_before)
        self.assertEqual(list(self.league.iterdump()),league_before)
        self.pool.execute('CREATE TABLE unexpected_player_cache(raw_struct BLOB)')
        self.pool.execute('INSERT INTO unexpected_player_cache VALUES (?)',(self.raw,))
        with self.assertRaisesRegex(ValueError,'UNKNOWN_PLAYER_RAW_MIRROR'):
            sanitize_player_potential(self.league,self.pool,'M02')

    def test_tampered_pair_or_true_potential_is_not_exportable(self):
        with self.assertRaisesRegex(ValueError,'MASK_POLICY_REQUIRED'):
            verify_sanitized_pair(self.league,self.pool,'M02')
        sanitize_player_potential(self.league,self.pool,'M02')
        self.pool.execute('UPDATE player_pool SET potential=99')
        with self.assertRaisesRegex(ValueError,'POOL_NOT_MASKED'):
            verify_sanitized_pair(self.league,self.pool,'M02')

    def test_sanitized_draft_query_never_becomes_native_injection_source(self):
        sanitize_player_potential(self.league,self.pool,'M02')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'pool.sqlite'
            with closing(sqlite3.connect(path)) as c:self.pool.backup(c)
            rows=query_historical_draft_class(str(path),1984)
            self.assertEqual(len(rows),1)
            self.assertTrue(rows[0]['player_raw_masked'])
            with self.assertRaisesRegex(PermissionError,'SANITIZED_PLAYER_POOL_NOT_NATIVE_INJECTION_SOURCE'):
                query_historical_draft_class(str(path),1984,for_native_injection=True)
            with self.assertRaisesRegex(PermissionError,'SANITIZED_PLAYER_POOL_NOT_NATIVE_INJECTION_SOURCE'):
                preflight_native_rookie_source(rows,dict(source_role='FRESH_NATIVE_CALIBRATED',native_binding='synthetic'))
        native=[dict(raw_struct=self.raw,native_identity='synthetic-native-player')]
        result=preflight_native_rookie_source(native,dict(source_role='FRESH_NATIVE_CALIBRATED',native_binding='synthetic'))
        self.assertFalse(result['execution_authorized'])
        self.assertEqual(native[0]['raw_struct'][0x441],222)

    def test_historical_gm_access_and_republish_refuse_without_touching_history(self):
        session=QuerySession.__new__(QuerySession)
        session.record=dict(source_manifest={})
        with self.assertRaises(AccessError):session.require_gm_sanitized()
        session.record['source_manifest']['player_potential_mask']=dict(MARKERS)
        session.require_gm_sanitized()
        spec=importlib.util.spec_from_file_location('mask_test_publisher',ROOT/'scripts/publish_web_snapshot.py')
        publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);directory=root/'published/saves/A/batches/old';directory.mkdir(parents=True)
            pointer=root/'published/saves/A/latest.json'
            pointer.write_text(json.dumps(dict(batch_path='saves/A/batches/old')))
            manifest=directory/'manifest.json';manifest.write_text('{}')
            before=manifest.read_bytes()
            from types import SimpleNamespace
            with patch.object(publisher,'ROOT',root),patch.object(publisher,'command') as command:
                with self.assertRaisesRegex(RuntimeError,'UNMASKED_HISTORICAL_GM_BATCH'):
                    publisher.publish(SimpleNamespace(save_id='A'))
                command.assert_not_called()
            self.assertEqual(manifest.read_bytes(),before)

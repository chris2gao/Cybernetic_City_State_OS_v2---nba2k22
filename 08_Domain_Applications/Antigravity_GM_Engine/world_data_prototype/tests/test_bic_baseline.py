"""BIC scope and provenance regressions on labelled synthetic WorldData."""
import math
import json
import subprocess
import sys
import unittest

import test_observation_scope as history_fixture
from bic_baseline import player_baseline, team_baseline, coverage_report, badge_intelligence
from engine import connect, ingest_capture
from player_detail_codec import native_badges, PROFILE


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.fixture = history_fixture.ObservationScopeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.args = dict(save_id='save', season_id='s1', as_of=history_fixture.T1,
                         max_age_seconds=60)

    def test_player_keeps_old_field_age_and_mixed_units(self):
        result = player_baseline(self.fixture.db, 'p1', **self.args)
        families = result['facts']['families']
        self.assertEqual(families['player_vitals_observations']['height_raw']['freshness']['status'], 'STALE')
        self.assertEqual(families['player_attribute_snapshots']['overall_raw']['value'], 90)
        self.assertEqual(families['player_attribute_snapshots']['overall_raw']['knowledge_status'], 'SYNTHETIC_ONLY')
        report = coverage_report(result)
        self.assertFalse(report['single_observation_unit'])
        self.assertGreater(report['counts']['NOT_OBSERVED'], 0)
        self.assertEqual(result['facts']['restricted_fields'], 'WITHHELD')
        self.assertEqual(result['game_mode'], 'UNKNOWN')

    def test_team_uses_cutoff(self):
        self.args['as_of'] = history_fixture.T0
        result = team_baseline(self.fixture.db, 't1', **self.args)
        self.assertEqual(result['facts']['families']['team_finance_observations']['payroll_raw']['value'], 1000)

    def test_wrong_save_and_season_are_rejected(self):
        for key in ('save_id', 'season_id'):
            args = {**self.args, key: 'wrong'}
            with self.assertRaisesRegex(ValueError, 'MISMATCH'):
                player_baseline(self.fixture.db, 'p1', **args)

    def test_missing_player_and_invalid_age(self):
        result = player_baseline(self.fixture.db, 'missing', **self.args)
        self.assertEqual(result['facts']['status'], 'NOT_OBSERVED')
        for age in (-1, math.nan, math.inf, True):
            with self.assertRaises(ValueError):
                player_baseline(self.fixture.db, 'p1', **{**self.args, 'max_age_seconds': age})

    def test_badge_absence_keeps_eligibility_unknown(self):
        result = badge_intelligence(player_baseline(self.fixture.db, 'p1', **self.args))
        self.assertEqual(result['badges'][0]['ownership'], 'not_owned')
        self.assertEqual(result['badges'][0]['eligibility'], 'UNKNOWN')
        self.assertEqual(result['badges'][0]['game_effect'], 'UNKNOWN')

    def test_other_season_does_not_override_fields(self):
        with connect(self.fixture.db) as conn:
            ingest_capture(conn, {'save_id': 'save', 'run_id': 'other-season',
                'unit_id': 'other-season', 'source_key': 'SYNTHETIC',
                'observed_at': history_fixture.T1, 'evidence_grade': 'SYNTHETIC_FIXTURE',
                'season': {'season_id': 's2', 'season_code': 'other'},
                'facts': {'player_attribute_snapshots': [{'player_id': 'p1', 'overall_raw': 1}]}})
        result = player_baseline(self.fixture.db, 'p1', **self.args)
        self.assertEqual(result['facts']['families']['player_attribute_snapshots']['overall_raw']['value'], 90)

    def test_explicit_native_identity_needs_observation(self):
        with self.assertRaisesRegex(ValueError, 'NATIVE_IDENTITY_MISMATCH'):
            player_baseline(self.fixture.db, 'p1', **self.args,
                expected_native_identity={'native_unique_id_raw': 1, 'preserved_id_raw': 2})

    def test_conflicting_native_identity_is_rejected(self):
        for unit, raw_id in [('identity-one', 1), ('identity-two', 2)]:
            self.fixture.put(unit, history_fixture.T1, {'native_player_sources': [
                {'player_id': 'p1', 'source_player_index': 0,
                 'native_unique_id_raw': raw_id, 'preserved_id_raw': 7}]})
        with self.assertRaisesRegex(ValueError, 'NATIVE_IDENTITY_CONFLICT'):
            player_baseline(self.fixture.db, 'p1', **self.args)

    def test_cli_normal_entrypoint(self):
        command = [sys.executable, '-B', str(history_fixture.BASE / 'bic_cli.py'),
                   'player', str(self.fixture.db), 'p1', '--save-id', 'save',
                   '--season-id', 's1', '--as-of', history_fixture.T1]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)['baseline']['entity_id'], 'p1')

    def test_unknown_badge_code_is_retained(self):
        field = next(value for value in PROFILE['badge_fields'].values() if value['kind'] == 'LEVEL')
        raw = bytearray(1264)
        code = (1 << field['width']) - 1
        encoded = code << field['start_bit']
        size = (field['start_bit'] + field['width'] + 7) // 8
        raw[field['offset']:field['offset'] + size] = encoded.to_bytes(size, 'little')
        badge = next(row for row in native_badges(bytes(raw)) if row['native_badge_id'] == field['badge_id'])
        if str(code) not in PROFILE['enum_labels']['PLAYERDATA_BADGE_LEVEL']:
            self.assertEqual(badge['owned_state'], 'unknown')
        self.assertEqual(badge['native_code'], code)

from copy import deepcopy
from pathlib import Path
import shutil
import unittest

import test_bic_wave2 as wave
from bic_baseline import player_baseline
from bic_diagnostics import diagnose_player, diagnose_team
from bic_plans import plan_adjustment
from player_skill_codec import LAYOUT


class Wave2RemediationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        wave.Wave2Tests.setUpClass()

    def setUp(self):
        self.original = wave.Wave2Tests()
        self.original.setUp()
        self.addCleanup(self.original.doCleanups)
        self.player = self.original.player
        self.team = self.original.team
        self.catalog = wave.Wave2Tests.catalog

    def historical_intent(self):
        intent = self.original.intent()
        intent.update(kind='COACH_SETTINGS', parameters={'team_id': 20, 'settings': {'RunPlayTendency': 55}},
                      expected_before={'RunPlayTendency': 90})
        return intent

    def test_exact_historical_tuple_and_other_fields(self):
        intent = self.historical_intent()
        report = plan_adjustment(intent, self.catalog)
        self.assertTrue(report['historical_validation']['requested_tuple_matches'])
        self.assertFalse(report['execute'])
        self.assertEqual(report['status'], 'NEEDS_VALIDATION')
        for parameters, before in [({'team_id': 20, 'settings': {'POEOffense2': 7}}, {'POEOffense2': 0}),
                                   ({'team_id': 20, 'settings': {'RunPlayTendency': 54}}, {'RunPlayTendency': 90}),
                                   ({'team_id': 20, 'settings': {'RunPlayTendency': 55}}, {'RunPlayTendency': 89})]:
            changed = {**intent, 'parameters': parameters, 'expected_before': before, 'before_source': 'FAKE_GETTER'}
            result = plan_adjustment(changed, self.catalog)
            self.assertFalse(result['historical_validation']['requested_tuple_matches'])
            self.assertEqual(result['status'], 'NEEDS_VALIDATION')
            self.assertIn('CURRENT_GETTER_EVIDENCE_NOT_VERIFIED', result['unknowns'])

    def test_fake_or_structured_getter_does_not_self_authenticate(self):
        for source in (None, 'arbitrary', {'verified': True, 'value': 90}):
            result = plan_adjustment({**self.historical_intent(), 'before_source': source}, self.catalog)
            self.assertFalse(result['historical_validation']['current_fresh_getter_verified'])
            self.assertEqual(result['status'], 'NEEDS_VALIDATION')

    def test_observation_maturity_is_separate_from_role_match(self):
        requirement = {**self.original.requirements[0], 'minimum': 80}
        for maturity, data_status in [('SYNTHETIC_ONLY', 'REAL_DATA_NOT_VERIFIED'),
                                      ('UNVERIFIED_OBSERVATION', 'REAL_DATA_NOT_VERIFIED'),
                                      ('HISTORICAL_OBSERVATION', 'SOURCE_ADMITTED')]:
            baseline = deepcopy(self.player)
            baseline['data_status'] = data_status
            baseline['facts']['families']['player_attribute_snapshots']['overall_raw']['knowledge_status'] = maturity
            finding = diagnose_player(baseline, role_requirements=[requirement])['findings'][0]
            self.assertEqual(finding['classification'], maturity)
            self.assertEqual(finding['observed_value'], 90)
            self.assertEqual(finding['role_compatibility'], 'SATISFIES')
            self.assertEqual(finding['mechanism_verification'], 'UNKNOWN')
            self.assertEqual(finding['causal_conclusion'], 'UNKNOWN')

    def test_same_labels_different_scope_or_payload_rejected(self):
        for key in ('scope_sha256', 'source_ledger_sha256', 'database_locator_sha256'):
            other = deepcopy(self.player)
            other['observation_scope'][key] = 'different'
            with self.assertRaisesRegex(ValueError, 'scope mismatch'):
                diagnose_team(self.team, [other])
        other = deepcopy(self.player)
        other['binding']['game_build'] = 'different-build'
        with self.assertRaisesRegex(ValueError, 'build mismatch'):
            diagnose_team(self.team, [other])

    def test_distinct_database_with_same_labels_rejected(self):
        other_db = self.original.fixture.root / 'other.sqlite'
        shutil.copy2(self.original.fixture.db, other_db)
        other = player_baseline(other_db, 'p1', save_id='save', season_id='s1', as_of=wave.fixture.T1)
        self.assertEqual(other['observation_scope']['scope_sha256'], self.player['observation_scope']['scope_sha256'])
        with self.assertRaisesRegex(ValueError, 'scope mismatch'):
            diagnose_team(self.team, [other])
        self.assertTrue(diagnose_team(self.team, [self.player])['players'])

    def play_fit(self, rows, code=4):
        baseline = deepcopy(self.player)
        baseline['facts']['families']['player_play_type_slots'] = rows
        return diagnose_player(baseline, required_play_codes=[{'code': code, 'source': 'SYNTHETIC_ROLE_ASSUMPTION'}])['play_type_fit'][0]

    def test_partial_positive_complete_and_stale_playtypes(self):
        row = deepcopy(self.player['facts']['families']['player_play_type_slots'][0])
        row.update(slot_index=0, native_play_code='1', layout_version=LAYOUT)
        row['freshness']['status'] = 'WITHIN_REQUESTED_AGE'
        row['provenance']['completeness'] = 'COMPLETE'
        self.assertEqual(self.play_fit([row])['classification'], 'UNKNOWN')
        full = [{**deepcopy(row), 'slot_index': index} for index in range(4)]
        self.assertEqual(self.play_fit(full)['classification'], 'CONFLICT')
        row['native_play_code'] = '99'
        self.assertEqual(self.play_fit([row], code=99)['classification'], 'UNKNOWN')
        row['native_play_code'] = '4'
        self.assertEqual(self.play_fit([row])['classification'], 'OBSERVED_REGISTRATION')
        row['freshness']['status'] = 'STALE'
        self.assertEqual(self.play_fit([row])['classification'], 'UNKNOWN')
        self.assertEqual(self.play_fit([])['classification'], 'UNKNOWN')

    def test_mixed_units_or_incomplete_coverage_cannot_prove_absence(self):
        row = deepcopy(self.player['facts']['families']['player_play_type_slots'][0])
        row['layout_version'] = LAYOUT
        row['freshness']['status'] = 'WITHIN_REQUESTED_AGE'
        row['provenance']['completeness'] = 'COMPLETE'
        rows = [{**deepcopy(row), 'slot_index': index, 'native_play_code': '1'} for index in range(4)]
        rows[1]['unit_id'] = 'another-unit'
        self.assertEqual(self.play_fit(rows)['classification'], 'UNKNOWN')
        rows[1]['unit_id'] = rows[0]['unit_id']
        rows[1]['provenance']['completeness'] = 'PARTIAL'
        self.assertEqual(self.play_fit(rows)['classification'], 'UNKNOWN')

    def test_transaction_draft_and_player_edit_stay_forbidden(self):
        for domain in ('D01', 'D02', 'D03', 'D06'):
            action = next(key for key, value in self.catalog['contracts'].items() if value['domain'] == domain)
            result = plan_adjustment({'action_id': action}, self.catalog)
            self.assertEqual(result['status'], 'FORBIDDEN')
            self.assertFalse(result['execute'])

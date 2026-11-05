from copy import deepcopy
import unittest

import test_observation_scope as fixture
from bic_baseline import player_baseline, coverage_report, knowledge_query, knowledge_status
from bic_experiments import factorial_2x2


class RemediationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.ObservationScopeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.baseline = player_baseline(self.fixture.db, 'p1', save_id='save',
            season_id='s1', as_of=fixture.T1, max_age_seconds=60)

    def test_observed_and_missing_fields(self):
        result = knowledge_query('player_attribute_snapshots.overall_raw', baseline=self.baseline)
        self.assertEqual(result['status'], 'OBSERVATION_AVAILABLE')
        self.assertEqual(result['sources'][0]['value'], 90)
        self.assertEqual(result['sources'][0]['provenance']['save_id'], 'save')
        self.assertEqual(result['sources'][0]['knowledge_status'], 'SYNTHETIC_ONLY')
        self.assertFalse(result['native_mechanism_verified'])
        self.assertEqual(knowledge_query('player_attribute_snapshots.absent', baseline=self.baseline)['status'], 'UNKNOWN')

    def test_research_and_unknown_mechanisms(self):
        result = knowledge_query('badge_eligibility', baseline=self.baseline)
        self.assertEqual(result['status'], 'RESEARCH_REFERENCE')
        self.assertTrue(result['sources'][0]['sha256'])
        self.assertFalse(result['native_mechanism_verified'])
        self.assertEqual(knowledge_query('unregistered_mechanism', baseline=self.baseline)['status'], 'UNKNOWN')
        self.assertEqual(knowledge_status('MODEL_INFERENCE', observed=True), 'CANDIDATE_INFERENCE')
        known = deepcopy(self.baseline)
        known['binding']['game_build'] = 'PC23'
        known['game_mode'] = 'FAST_SIM'
        self.assertEqual(knowledge_query('badge_eligibility', baseline=known, version='PC23', mode='FAST_SIM')['status'], 'UNKNOWN')

    def test_applicability(self):
        name = 'player_attribute_snapshots.overall_raw'
        self.assertEqual(knowledge_query(name, baseline=self.baseline, version='PC22')['status'], 'UNKNOWN')
        known = deepcopy(self.baseline)
        known['binding']['game_build'] = 'PC22'
        known['game_mode'] = 'FAST_SIM'
        self.assertEqual(knowledge_query(name, baseline=known, version='PC23')['status'], 'NOT_APPLICABLE')
        self.assertEqual(knowledge_query(name, baseline=known, mode='CPU_VS_CPU_3D')['status'], 'NOT_APPLICABLE')

    def test_conflicts_and_identity(self):
        other = deepcopy(self.baseline)
        other['facts']['families']['player_attribute_snapshots']['overall_raw']['value'] = 1
        result = knowledge_query('player_attribute_snapshots.overall_raw', baseline=self.baseline, comparison_baselines=[other])
        self.assertEqual(result['status'], 'CONFLICT')
        other['save_id'] = 'other'
        with self.assertRaises(ValueError):
            knowledge_query('player_attribute_snapshots.overall_raw', baseline=self.baseline, comparison_baselines=[other])

    def test_empty_and_absent_badge_family(self):
        self.baseline['facts']['families']['player_badge_values'] = []
        report = coverage_report(self.baseline)
        self.assertEqual(report['domains']['player_badge_values']['status'], 'NOT_OBSERVED')
        del self.baseline['facts']['families']['player_badge_values']
        self.assertEqual(coverage_report(self.baseline)['domains']['player_badge_values']['status'], 'NOT_OBSERVED')

    def test_details_and_restricted(self):
        report = coverage_report(self.baseline)
        self.assertTrue(report['mixed_observation_units'])
        vitals = report['domains']['player_vitals_observations']
        self.assertIn('player_vitals_observations.height_raw', vitals['stale_fields'])
        self.assertTrue(vitals['missing_fields'])
        self.baseline['facts']['families']['player_restricted_observations'] = {'secret': {'value': 12345}}
        restricted = coverage_report(self.baseline)['domains']['player_restricted_observations']
        self.assertEqual(restricted, {'status': 'WITHHELD', 'fields': []})
        self.assertEqual(knowledge_query('player_restricted_observations.secret', baseline=self.baseline)['status'], 'WITHHELD')

    def test_mode_contradictions(self):
        cells = {key: [1] for key in ('00', '10', '01', '11')}
        for synthetic, mode in ((True, 'FAST_SIM'), (False, 'SYNTHETIC')):
            with self.assertRaises(ValueError):
                factorial_2x2(cells, synthetic=synthetic, mode=mode)
        self.assertEqual(factorial_2x2(cells, synthetic=False, mode='UNKNOWN')['status'], 'NOT_CAUSALLY_IDENTIFIED')

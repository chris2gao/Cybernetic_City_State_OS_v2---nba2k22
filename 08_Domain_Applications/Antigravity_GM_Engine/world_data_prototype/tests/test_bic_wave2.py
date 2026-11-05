from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import unittest

import test_observation_scope as fixture
from bic_baseline import player_baseline, team_baseline
from bic_diagnostics import diagnose_player, diagnose_team, diagnose_and_plan, synthetic_validation
from bic_plans import native_capabilities, plan_adjustment


class Wave2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = native_capabilities(Path(__file__).resolve().parents[4])

    def setUp(self):
        self.fixture = fixture.ObservationScopeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        args = dict(save_id='save', season_id='s1', as_of=fixture.T1, max_age_seconds=60)
        self.player = player_baseline(self.fixture.db, 'p1', **args)
        self.team = team_baseline(self.fixture.db, 't1', **args)
        self.requirements = [{'field': 'player_attribute_snapshots.overall_raw',
                              'minimum': 95, 'source': 'SYNTHETIC_ROLE_ASSUMPTION',
                              'rationale': 'Candidate role requirement, not a Native threshold'}]

    def intent(self):
        return {'kind': 'OFFENSE_FOCUS', 'parameters': {'team_id': 20, 'value': 1},
                'expected_before': 0, 'game_build_sha256': self.catalog['game_build_sha256'],
                'identity_source': {'save_id': 'save', 'season_id': 's1', 'team_id': 20},
                'before_source': 'SYNTHETIC_UNIT_WITH_VALUE_0', 'mode': 'FAST_SIM'}

    def test_fact_role_conflict_and_alternative_explanations(self):
        result = diagnose_player(self.player, role_requirements=self.requirements)
        finding = result['findings'][0]
        self.assertEqual(finding['classification'], 'CONFLICT')
        self.assertEqual(finding['support']['sources'][0]['value'], 90)
        self.assertGreaterEqual(len(finding['mechanism_explanations']), 2)
        self.assertEqual(result['verified_mechanisms'], [])

    def test_missing_stale_and_conflicting_evidence(self):
        requirement = {**self.requirements[0], 'field': 'player_vitals_observations.height_raw'}
        self.assertEqual(diagnose_player(self.player, role_requirements=[requirement])['findings'][0]['classification'], 'UNKNOWN')
        requirement['field'] = 'player_attribute_snapshots.unobserved'
        self.assertEqual(diagnose_player(self.player, role_requirements=[requirement])['findings'][0]['classification'], 'UNKNOWN')
        other = deepcopy(self.player)
        other['facts']['families']['player_attribute_snapshots']['overall_raw']['value'] = 2
        self.assertEqual(diagnose_player(self.player, role_requirements=self.requirements, comparison_baselines=[other])['findings'][0]['support']['status'], 'CONFLICT')

    def test_badges_and_game_data_never_certify_effect(self):
        result = diagnose_player(self.player)
        self.assertEqual(result['badge_facts']['badges'][0]['game_effect'], 'UNKNOWN')
        self.assertIn('No Native effect', result['limits'][0])

    def test_team_context_and_mode_isolation(self):
        result = diagnose_team(self.team, [self.player], roles={'p1': self.requirements})
        self.assertEqual(result['fixed_roster'], ['p1'])
        for key, value in [('save_id', 'other'), ('season_id', 'other'), ('game_mode', 'FAST_SIM')]:
            other = deepcopy(self.player);other[key] = value
            with self.assertRaises(ValueError):
                diagnose_team(self.team, [other])

    def test_end_to_end_plan_is_offline(self):
        result = diagnose_and_plan(self.player, catalog=self.catalog,
                                  role_requirements=self.requirements, intents=[self.intent()])
        plan = result['native_plans'][0]
        self.assertEqual(plan['action_id'], 'COACH_APPLY_OFFENSE_POE')
        self.assertFalse(plan['execute'])
        self.assertEqual(plan['status'], 'NEEDS_VALIDATION')
        self.assertIn('DIAGNOSTIC_MODE_NOT_BOUND', plan['unknowns'])
        standalone = plan_adjustment(self.intent(), self.catalog)
        self.assertEqual(standalone['status'], 'NEEDS_VALIDATION')
        self.assertIn('NATIVE_WRITE_NOT_VERIFIED_FOR_CURRENT_PLAN', standalone['unknowns'])

    def test_invalid_value_before_build_and_unavailable_action(self):
        intent = self.intent();intent['parameters']['value'] = 999
        self.assertEqual(plan_adjustment(intent, self.catalog)['status'], 'NEEDS_VALIDATION')
        intent = self.intent();del intent['expected_before']
        self.assertIn('MISSING_BEFORE_VALUE', plan_adjustment(intent, self.catalog)['unknowns'])
        intent = self.intent();intent['game_build_sha256'] = 'wrong'
        self.assertIn('BUILD_NOT_BOUND', plan_adjustment(intent, self.catalog)['unknowns'])
        self.assertEqual(plan_adjustment({'action_id': 'UNREGISTERED'}, self.catalog)['capability_state'], 'UNKNOWN')

    def test_forbidden_and_incomplete_capability(self):
        self.assertEqual(plan_adjustment({'action_id': 'TRADE_PLAYERS'}, self.catalog)['status'], 'FORBIDDEN')
        self.assertEqual(plan_adjustment({'kind': 'PLAYBOOK_CHANGE'}, self.catalog)['status'], 'NEEDS_VALIDATION')
        plan = plan_adjustment({'action_id': 'COACH_SET_KNOWN_CURRENT_SETTINGS',
            'parameters': {'team_id': 20, 'settings': {'unregistered': 1}}}, self.catalog)
        self.assertTrue(any('UNVERIFIED_SETTING_DOMAIN' in item for item in plan['unknowns']))

    def test_ability_tendency_role_disagreement(self):
        self.fixture.put('tendency-new', fixture.T1, {'player_tendency_snapshots': [{'player_id': 'p1', 'shot_tendency_raw': 10}]})
        player = player_baseline(self.fixture.db, 'p1', save_id='save', season_id='s1', as_of=fixture.T1)
        requirements = [{**self.requirements[0], 'minimum': 80},
            {'field': 'player_tendency_snapshots.shot_tendency_raw', 'minimum': 50,
             'source': 'SYNTHETIC_ROLE_ASSUMPTION', 'rationale': 'Candidate usage criterion'}]
        result = diagnose_player(player, role_requirements=requirements)
        self.assertEqual([finding['classification'] for finding in result['findings']], ['FACT', 'CONFLICT'])

    def test_certified_historical_subset_is_not_current_authority(self):
        intent = self.intent();intent['kind'] = 'COACH_SETTINGS';intent['action_id'] = 'COACH_SET_KNOWN_CURRENT_SETTINGS'
        intent['parameters'] = {'team_id': 20, 'settings': {'RunPlayTendency': 55}}
        intent['expected_before'] = {'RunPlayTendency': 90}
        result = plan_adjustment(intent, self.catalog)
        self.assertEqual(result['capability_state'], 'LiveEffectVerified')
        self.assertFalse(result['execute'])
        self.assertEqual(result['status'], 'NEEDS_VALIDATION')

    def test_cli_and_team_role_evidence(self):
        command = [sys.executable, '-B', str(fixture.BASE/'bic_wave2_cli.py'),
                   str(self.fixture.db), 'p1', '--save-id', 'save', '--season-id', 's1',
                   '--as-of', fixture.T1, '--team-id', 't1']
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)['team']['team_id'], 't1')
        team_result = diagnose_team(self.team, [self.player], team_requirements=[{
            'field': 'team_tactic_settings.absent', 'source': 'SYNTHETIC_ASSUMPTION',
            'rationale': 'Unobserved coaching context'}])
        self.assertEqual(team_result['team_setting_fit'][0]['classification'], 'UNKNOWN')

    def test_play_type_mismatch_and_numeric_contract(self):
        fresh = player_baseline(self.fixture.db, 'p1', save_id='save', season_id='s1', as_of=fixture.T0, max_age_seconds=60)
        result = diagnose_player(fresh, required_play_codes=[{'code': 99, 'source': 'SYNTHETIC_ROLE_ASSUMPTION'}])
        self.assertEqual(result['play_type_fit'][0]['classification'], 'CONFLICT')
        self.assertEqual(diagnose_player(self.player, required_play_codes=[{'code': 99, 'source': 'SYNTHETIC_ROLE_ASSUMPTION'}])['play_type_fit'][0]['classification'], 'UNKNOWN')
        with self.assertRaises(ValueError):
            diagnose_player(self.player, role_requirements=[{**self.requirements[0], 'minimum': float('nan')}])

    def test_intent_mismatch_and_missing_identity_before_source(self):
        intent = self.intent();intent['action_id'] = 'COACH_APPLY_DEFENSE_POE'
        self.assertIn('INTENT_ACTION_MISMATCH', plan_adjustment(intent, self.catalog)['unknowns'])
        intent = self.intent();intent['identity_source']['team_id'] = 1;del intent['before_source']
        plan = plan_adjustment(intent, self.catalog)
        self.assertIn('TARGET_TEAM_IDENTITY_NOT_BOUND', plan['unknowns'])
        self.assertIn('BEFORE_SOURCE_NOT_BOUND', plan['unknowns'])

    def test_finding_drives_candidate_plan_and_synthetic_validation(self):
        requirement = {**self.requirements[0], 'candidate_intent': self.intent()}
        result = diagnose_and_plan(self.player, catalog=self.catalog, role_requirements=[requirement])
        self.assertEqual(result['native_plans'][0]['intent']['diagnosis_finding_index'], 0)
        calculated = synthetic_validation({'00': [10], '10': [14], '01': [12], '11': [22]})
        self.assertEqual(calculated['interaction_difference_in_differences'], 6)
        self.assertEqual(calculated['status'], 'SYNTHETIC_ARITHMETIC_ONLY')

    def test_missing_catalog_keeps_partial_diagnosis(self):
        result = diagnose_and_plan(self.player, catalog=None, intents=[self.intent()])
        self.assertTrue(result['findings'])
        self.assertEqual(result['native_plans'][0]['capability_state'], 'UNKNOWN')

    def test_relative_profile_remains_a_codec_hypothesis(self):
        fresh = player_baseline(self.fixture.db, 'p1', save_id='save', season_id='s1', as_of=fixture.T0)
        profile = diagnose_player(fresh)['relative_basketball_profile']
        self.assertEqual(profile['classification'], 'HYPOTHESIS')
        self.assertTrue(profile['relative_strength_candidates'])
        self.assertEqual(profile['relative_strength_candidates'][0]['conversion']['target_ui_validation'], 'NOT_OBSERVED')

    def test_low_historical_efficiency_is_not_a_causal_rule(self):
        history = deepcopy(self.player)
        history['facts']['season_observations'] = [{'label': 'SYNTHETIC_LOW_EFFICIENCY', 'field_goal_percentage': 0.2}]
        result = diagnose_player(history, role_requirements=self.requirements)
        self.assertEqual(result['verified_mechanisms'], [])
        self.assertEqual(result['game_observations'][0]['label'], 'SYNTHETIC_LOW_EFFICIENCY')
        self.assertTrue(all(explanation['classification'] == 'HYPOTHESIS' for explanation in result['findings'][0]['mechanism_explanations']))

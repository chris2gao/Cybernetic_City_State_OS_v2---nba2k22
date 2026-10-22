"""Direct M2 content, mapping and strategy revision checks; no game access."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from gm_core.knowledge import Knowledge, read_json
from gm_core.strategy_state import initialize, validate, link_finance
from gm_workbench.store import Store


class KnowledgeM2Tests(unittest.TestCase):
    def setUp(self):
        self.k = Knowledge(ROOT/'web_gm/knowledge')
        self.profile = read_json(ROOT/'config/coach_tactics_profile.json')
        self.binding = dict(career_id='synthetic', batch_id='B1', snapshot_id='S1')
        self.context = dict(source_binding=self.binding, teams=[dict(team_id=i, team=r['team']) for i, r in enumerate(self.k.franchises)])

    def test_content_sources_fields_and_bounded_search(self):
        self.assertEqual((len(self.k.cards), len(self.k.franchises), len(self.k.rules)), (12, 30, 19))
        for c in self.k.cards:
            for link in c['native_links']:
                fields = self.profile['fields' if link['scope'] == 'COACH_DEFAULT' else 'defensive_fields']
                self.assertIn(link['field'], fields)
        self.assertLessEqual(len(self.k.search()['cards']), 5)
        self.assertEqual(self.k.search(tag='pick_and_roll')['cards'][0]['card_id'], 'PNR_PRIMARY')
        self.assertEqual(self.k.search(field='BenchDepth')['cards'][0]['card_id'], 'ROTATION_CONTEXT')
        with self.assertRaises(ValueError):
            self.k.search(limit=6)

    def test_direct_enum_drop_hypothesis_and_unavailable(self):
        native = dict(available=True, source_binding=self.binding, profile=self.profile,
                      dictionary=dict(default_fields=deepcopy(self.profile['fields']),
                                      defensive_fields=deepcopy(self.profile['defensive_fields'])))
        resolved = self.k.show('PNR_PRIMARY', native)['native_resolution'][0]
        self.assertEqual(resolved['resolution'], 'SAME_BATCH_NATIVE_ENUM')
        drop = self.k.show('DROP_CONCEPT', native)['native_resolution']
        self.assertTrue(all(r['resolution'] == 'HYPOTHESIS_CANDIDATE' for r in drop))
        self.assertTrue(all(r['semantic_label'] != 'DROP' for r in drop))
        missing = self.k.show('PNR_PRIMARY')['native_resolution'][0]
        self.assertEqual(missing['resolution'], 'UNAVAILABLE')
        self.assertIsNone(missing['raw_candidate'])
        native['dictionary']['default_fields']['POEOffense']['enum']['4'] = 'DIFFERENT_LABEL'
        self.assertEqual(self.k.show('PNR_PRIMARY', native)['native_resolution'][0]['resolution'], 'UNAVAILABLE')

    def test_three_pilots_same_synthetic_problem_preserve_alternatives(self):
        problem = dict(player_role='win_now_wing', cost='future_first_and_multiyear_salary', alternative='internal_optimization')
        views = [dict(problem=problem, team=t, method=self.k.franchise(t)['pilot']) for t in ('GSW', 'SAS', 'OKC')]
        self.assertEqual(len({v['method']['priority_question'] for v in views}), 3)
        for view in views:
            self.assertEqual(view['method']['status'], 'DESIGN_HYPOTHESIS')
            self.assertTrue(view['method']['change_conditions'])
            self.assertEqual(view['method']['alternative'], 'KEEP_OR_INTERNAL_OPTIMIZATION')
            self.assertIsNone(self.k.franchise(view['team'])['ownership_cost_preference_if_verified'])

    def test_thirty_unassessed_candidates_not_team_decisions(self):
        states = initialize(self.context, self.k)
        self.assertEqual(len(states), 30)
        for s in states:
            validate(s, self.k)
            self.assertEqual(s['status'], 'UNASSESSED')
            self.assertEqual(s['current_actions'], [])
            self.assertEqual(s['core_assets_and_hold_thresholds'], [])
            self.assertIsNone(s['ownership_cost_preference_if_verified'])

    def test_revisions_history_conflict_and_no_approval(self):
        first = initialize(self.context, self.k)[0]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'gm_workbench.sqlite'
            with Store(path) as store:
                store.save_state(first, 0, self.k)
                second = deepcopy(first)
                second.update(state_id='second', revision=2, supersedes_state_id=first['state_id'],
                              status='DRAFT', change_reason='Synthetic role evidence', last_review_batch='B1',
                              identity_evidence=[dict(batch_id='B1', claim='synthetic role need')],
                              current_actions=[dict(status='RESEARCH', description='compare internal option')],
                              change_conditions=['If role evidence changes, reconsider'])
                store.save_state(second, 1, self.k)
                with self.assertRaisesRegex(ValueError, 'REVISION_CONFLICT'):
                    store.save_state(dict(second, state_id='conflict'), 1, self.k)
            with Store(path, readonly=True) as store:
                self.assertEqual(store.load_state('synthetic', first['team_abbr'], 1), first)
                self.assertEqual(store.load_state('synthetic', first['team_abbr'])['state_id'], 'second')
                self.assertEqual(len(store.list_states('synthetic')), 1)
        for action in (dict(status='EXECUTED'), dict(status='PLAYER_APPROVED'), dict(status='PROPOSED', approved=True)):
            with self.assertRaises(ValueError):
                validate(dict(second, current_actions=[action]), self.k)

    def test_finance_link_is_optional_and_cross_batch_requires_review(self):
        s = initialize(self.context, self.k)[0]
        self.assertEqual(link_finance(s)['finance_alignment'], 'NOT_LINKED')
        s['finance_run_id'] = 'R1'
        run = dict(run_id='R1', source_binding=dict(self.binding, batch_id='OLD'))
        self.assertEqual(link_finance(s, run)['finance_alignment'], 'DIFFERENT_BATCH_REVIEW_REQUIRED')
        run['source_binding']['career_id'] = 'other'
        with self.assertRaisesRegex(ValueError, 'CAREER_MISMATCH'):
            link_finance(s, run)


if __name__ == '__main__':
    unittest.main()

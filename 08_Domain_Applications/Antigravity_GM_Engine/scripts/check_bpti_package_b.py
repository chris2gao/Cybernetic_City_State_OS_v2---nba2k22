"""Only the four player-authorized Package B checks (B-B1 through B-B4)."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from gm_core.knowledge import Knowledge
from gm_core.bpti import ResearchIndex, SYSTEM_IDS
from gm_core.bpti_package import LAYERS
from gm_state_io.registry import Registry


def knowledge():
    return Knowledge(ROOT / 'web_gm/knowledge').bpti()


class PackageBChecks(unittest.TestCase):
    def test_B_B1_native_evidence_and_boundaries(self):
        index, registry = knowledge(), Registry()
        self.assertEqual(set(b['system_id'] for b in index.native_bindings.values()), set(SYSTEM_IDS))
        for binding in index.native_bindings.values():
            self.assertEqual(binding['status'], 'REFERENCE_ONLY')
            self.assertEqual(binding['fallback'], 'HOLD_RESEARCH')
            self.assertNotIn('target_value', binding)
            if binding['mapping_status'] == 'SUPPORTED_FIELD_DIRECTION':
                for key in binding['field_candidates']:
                    self.assertTrue(registry.field(key)['gm_enabled'], key)
                    self.assertFalse(key.startswith(('overall.', 'gameplay.', 'world.')))
                    self.assertNotIn('RAW_', key)
                    self.assertNotEqual(key, 'coach.PlaybookID')
        self.assertEqual(sum(b['mapping_status'] == 'TYPE_MATCHED_ONLY' for b in index.native_bindings.values()), 0)
        pool = Knowledge(ROOT / 'web_gm/knowledge').play_pool()
        self.assertEqual(pool.search(type_id=15, limit=1)['total_matches'], 0)
        bad = copy.deepcopy(index.package)
        bad['bindings'][0]['mapping_status'] = 'TYPE_MATCHED_ONLY'
        with self.assertRaisesRegex(ValueError, 'TYPE_MATCH_REQUIRES_MEMBERSHIP'):
            ResearchIndex(index.payload, list(index.system_cards.values()), bad)
        self.assertFalse(registry.field('coach.PlaybookID')['gm_enabled'])
        self.assertTrue(all(not f['gm_enabled'] for k, f in registry.fields.items() if k.startswith('overall.')))
        supported = set(index.package['supported_field_keys'])
        self.assertEqual(len([k for k in supported if k.startswith('tendency.')]), 48)
        self.assertEqual(len([k for k in supported if k.startswith('personal.')]), 18)
        self.assertEqual(len([k for k in supported if k.startswith('training.')]), 11)
        self.assertEqual(len([k for k in supported if k.startswith('playtype.')]), 5)

    def test_B_B2_thirty_historical_identities(self):
        index = knowledge()
        self.assertEqual(len(index.team_identities), 30)
        self.assertEqual(len({t['identity_id'] for t in index.team_identities.values()}), 30)
        for team in index.team_identities:
            view = index.team_identity(team, as_of='2021-10-19')
            self.assertEqual(view['status'], 'HISTORICAL_SEED_ONLY')
            self.assertEqual(view['operational_link'], 'NOT_BOUND_TO_ANY_SAVE')
            self.assertEqual(view['actual_team_assessment'], 'UNASSESSED')
            self.assertEqual(set(view['layers']), set(LAYERS))
            for layer in view['layers'].values():
                for item in layer:
                    c = item['claim']
                    self.assertLessEqual(c['fact_valid_to'], '2021-10-19')
                    self.assertLessEqual(c['knowledge_available_from'], '2021-10-19')
                    self.assertIn(c['parent_claim_id'], index.claims)
                    for sid in c['source_ids']:
                        self.assertIsNotNone(index.sources[sid]['url'])
            before = index.team_identity(team, as_of='2020-01-01')
            self.assertIsNone(before['identity'])
        self.assertEqual(index.sources['LAL-S2']['source_status'], 'SOURCE_MISSING')
        self.assertIsNone(index.sources['LAL-S2']['url'])
        lal = index.team_identity('LAL', as_of='2021-10-19')
        self.assertTrue(any(c['availability'] == 'SOURCE_MISSING' for c in lal['blocked_claims']))
        atl = index.claim('B3-ATL-GAP-ATL-S2', as_of='2021-10-19')
        self.assertIsNone(atl['claim'])
        self.assertEqual(atl['availability'], 'UNKNOWN')

    def test_B_B3_four_dated_narrow_mechanisms(self):
        index = knowledge()
        rows = json.loads((ROOT / 'web_gm/knowledge/bpti/four_family_evidence_v1.json').read_text(encoding='utf-8'))
        self.assertEqual(len(rows), 4)
        for row in rows:
            family = row['system_id']
            view = index.system(family, as_of='2021-10-19')
            self.assertEqual(view['availability'], 'GM_ELIGIBLE_MECHANISM_ONLY')
            self.assertIsNone(view['card'])  # Original whole card is NOT unlocked.
            self.assertEqual(len(view['mechanism_entries']), 1)
            c = view['mechanism_entries'][0]['claim']
            self.assertEqual(c['claim_status'], 'SUPPORTED_INTERPRETATION')
            self.assertEqual(c['parent_claim_id'], 'R1-C-' + family)
            self.assertEqual(c['knowledge_available_from'], row['publication_date'])
            self.assertEqual(c['fact_valid_from'], row['fact_valid_from'])
            self.assertEqual(c['fact_valid_to'], row['fact_valid_to'])
            self.assertTrue(index.sources[c['source_ids'][0]]['url'].startswith('https://www.nba.com/news/'))
            self.assertIsNone(index.claim('R1-C-' + family, as_of='2021-10-19')['claim'])
            early = index.system(family, as_of='2018-01-01')
            self.assertFalse(early.get('mechanism_entries'))
            self.assertIsNone(early['card'])
        coverage = index.system_coverage(as_of='2021-10-19')
        self.assertEqual(coverage['gm_eligible_count'], 10)
        self.assertEqual(coverage['full_card_count'], 6)
        print('ACTUAL_COVERAGE ' + json.dumps(coverage, ensure_ascii=False), flush=True)

    def test_B_B4_bounded_existing_interface_join(self):
        protected = ['src/gm_state_io/team_book.py', 'src/gm_state_io/registry.py',
                     'src/gm_data_access/decision_inputs.py', 'config/gameplay_policy.json']
        def fingerprints():
            return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in protected}
        before = fingerprints()
        index = knowledge()
        view = index.context('MOTION_READ_REACT', team='GSW', limit=2, as_of='2021-10-19')
        self.assertLessEqual(len(view['bindings']['items']), 2)
        self.assertTrue(view['bindings']['truncated'])
        self.assertEqual(view['identity']['team_abbr'], 'GSW')
        self.assertEqual(view['authority'], 'REFERENCE_ONLY_NO_NATIVE_PLAN_OR_APPROVAL')
        with self.assertRaises(ValueError):
            index.search_bindings(limit=6, as_of='2021-10-19')
        with self.assertRaises(ValueError):
            index.search_identities(offset=-1, as_of='2021-10-19')
        result = subprocess.run([sys.executable, '-B', 'scripts/gm_knowledge.py', 'bpti-context',
                                 '--system-id', 'POST_HIGH_LOW', '--team', 'PHI', '--as-of', '2021-10-19', '--limit', '1'],
                                cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload['system']['availability'], 'GM_ELIGIBLE_MECHANISM_ONLY')
        self.assertEqual(len(payload['bindings']['items']), 1)
        self.assertEqual(payload['identity']['operational_link'], 'NOT_BOUND_TO_ANY_SAVE')
        self.assertEqual(before, fingerprints())


if __name__ == '__main__':
    unittest.main(verbosity=2)

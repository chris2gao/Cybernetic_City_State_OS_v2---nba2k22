"""Offline consumer-boundary tests. No process attachment or Native calls."""
import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService


class RoleConsumers(unittest.TestCase):
    def setUp(self):
        self.service = RoleCapabilityService()
        self.profile = RoleCapabilityProfile('GM', 'gm20', (20,), 'world', 'save', 'gen',
                                             'season', 'REGULAR_SEASON', 'snapshot')

    def test_all_requirements_remain_discoverable_without_invented_bindings(self):
        self.assertEqual(len(self.service.requirements), 183)
        self.assertEqual(self.service.source_mapping_count, 50)
        self.assertEqual(len(self.service.mapping), 56)
        trade = self.service.describe_action('GM.TRADE.EXECUTE_AGREED', self.profile)
        self.assertTrue(trade['call_logic_available'])
        self.assertFalse(trade['identity_permission'])
        self.assertEqual(trade['executor_action_id'], 'TRADE_EXECUTE_AGREED_PACKAGE')
        self.assertNotIn('rva', str(trade).lower())
        unbound = self.service.describe_action('GM.ROSTER.LIST_MOVE', self.profile)
        self.assertFalse(unbound['call_logic_available'])
        self.assertTrue(unbound['unknowns'])

    def test_profile_does_not_grant_permission_by_role_name(self):
        cards = self.service.list_role_capabilities(self.profile)
        self.assertTrue(cards)
        self.assertTrue(all(not c['identity_permission'] for c in cards))
        granted = replace(self.profile, allowed_actions=frozenset({'GM.TRADE.EXECUTE_AGREED'}))
        self.assertTrue(self.service.describe_action('GM.TRADE.EXECUTE_AGREED', granted)['identity_permission'])

    def test_snapshot_identity_projection_and_hidden_nested_values(self):
        profile = replace(self.profile, read_grants=(('players', ('public',)),))
        envelope = {key: getattr(profile, key) for key in
                    ('world_id', 'save_instance_id', 'generation_id', 'season_id', 'snapshot_ref', 'actor_uid', 'role_type')}
        envelope.update(team_scope=[20], data={'public': {'name': 'Sample'}, 'private': {'potential': 99}})
        result = self.service.read_role_visible_data(profile, 'players', provider=lambda *_: envelope)
        self.assertEqual(result['data'], {'public': {'name': 'Sample'}})
        envelope['data']['public']['nested'] = [{'potential': 99}]
        with self.assertRaises(PermissionError):
            self.service.read_role_visible_data(profile, 'players', provider=lambda *_: envelope)
        envelope['save_instance_id'] = 'another-save'
        with self.assertRaises(ValueError):
            self.service.read_role_visible_data(profile, 'players', provider=lambda *_: envelope)
        with self.assertRaises(PermissionError):
            self.service.read_role_visible_data(profile, 'not-granted', provider=lambda *_: self.fail('Provider called'))


if __name__ == '__main__':
    unittest.main()

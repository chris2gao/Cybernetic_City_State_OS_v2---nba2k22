"""Real compiler/planner/handler over a synthetic Native ABI; no game access."""
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

CONTROL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CONTROL))
from contracts import NativeActionRequest
from facade import NativeControlFacade
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService
from role_batches import ActionIntent, BatchContext, ExecutionAggregator, RoleActionBatch, overlaps

REQUIREMENT='COACH.ROTATION.PLAYER_MINUTES'
ACTION='COACH_ROTATION_SET_PLAYER_MINUTES'


class RotationMinutes(unittest.TestCase):
    def setUp(self):
        self.control=NativeControlFacade()

    def simulate(self,minutes,**options):
        node=shutil.which('node')
        self.assertIsNotNone(node)
        action=self.control.registry.get(ACTION)
        bindings={step['binding_id']:self.control.registry.binding(step['binding_id']).to_dict()
                  for step in action['call_sequence'] if step.get('binding_id')}
        data={'request':{'action_id':ACTION,'parameters':{'team_id':20,'player_id':55,'minutes':minutes}},
              'bindings':bindings,'options':options}
        process=subprocess.run([node,str(CONTROL/'tests/rotation_minutes_harness.js'),str(CONTROL/'runtime/rotation_minutes.js')],
                  input=json.dumps(data),capture_output=True,text=True,check=True,timeout=10)
        return json.loads(process.stdout)

    def test_exact_native_value_abi_and_neighbor_preservation(self):
        for minutes in (0,37,48):
            with self.subTest(minutes=minutes):
                program=self.control.render(NativeActionRequest(ACTION,{'team_id':20,'player_id':55,'minutes':minutes}))
                self.assertEqual(program.maximum_game_calls,3)
                self.assertFalse(program.has_prior_live_mechanism_evidence)
                result=self.simulate(minutes,profile_index=2 if minutes==48 else 0)
                self.assertIsNone(result['error'])
                self.assertEqual(result['after'][0],(result['initial'][0]&0xfe03ffff)|(minutes<<18))
                self.assertEqual(result['after'][1],result['initial'][1])
                self.assertEqual([call['binding'] for call in result['calls']],
                    ['rotation.franchise_team_index','rotation.set_player_minutes','rotation.mark_team_change'])
                self.assertEqual(result['calls'][1]['arguments'],[{'identity':'delegate'},{'identity':'player55'},minutes])
                details=result['messages'][0]['details']
                self.assertFalse(details['automatic_minute_balancing'])
                self.assertEqual(result['messages'][0]['outcome'],'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED')

    def test_career_clamp_missing_mode_and_wrong_franchise_never_call_setter(self):
        for options,expected in [({'career_clamp':True},0),({'missing_delegate':True},0),({'wrong_index':True},1)]:
            result=self.simulate(37,**options)
            self.assertIsNotNone(result['error'])
            self.assertEqual(len(result['calls']),expected)
            self.assertEqual(result['initial'],result['after'])
            self.assertFalse(result['messages'])

    def test_invalid_values_and_unsolicited_fields_are_rejected(self):
        for value in (-1,49,127,True,2.5,'37'):
            with self.assertRaises((ValueError,TypeError)):
                self.control.render(NativeActionRequest(ACTION,{'team_id':20,'player_id':55,'minutes':value}))
        with self.assertRaises(ValueError):
            self.control.render(NativeActionRequest(ACTION,{'team_id':20,'player_id':55,'minutes':37,'auto_balance':True}))

    def test_native_mismatch_or_refresh_failure_never_reports_success_or_retries(self):
        for options in ({'wrong_value':True},{'other_mutation':True},{'refresh_failure':True}):
            result=self.simulate(37,**options)
            self.assertIsNotNone(result['error'])
            self.assertEqual(len(result['calls']),3)
            self.assertFalse(result['messages'])

    def test_metadata_explains_minutes_without_exposing_native_addresses(self):
        service=RoleCapabilityService()
        profile=RoleCapabilityProfile('COACH','coach20',(20,),'w','s','g','season','TEAM_ROTATION','snapshot')
        desc=service.describe_action(REQUIREMENT,profile)
        self.assertTrue(desc['call_logic_available'])
        self.assertIsNone(desc['historical_exact_live_evidence'])
        self.assertFalse(desc['identity_permission'])
        values=service.get_allowed_values(REQUIREMENT,profile)['native_value_contract']['minutes']
        self.assertEqual((values['minimum'],values['maximum']),(0,48))
        self.assertEqual(values['team_sum_rule'],'NO_AUTOMATIC_BALANCING')
        self.assertNotIn('18557872',json.dumps(desc))
        self.assertTrue(desc['unknowns'])  # Coverage gaps are retained separately from call availability.

    def test_distinct_players_can_share_batch_and_duplicate_target_requires_resolution(self):
        service=RoleCapabilityService()
        profile=RoleCapabilityProfile('COACH','coach20',(20,),'w','s','g','season','TEAM_ROTATION','snapshot',frozenset({REQUIREMENT}))
        context=BatchContext('w','s','g','season','TEAM_ROTATION','snapshot',service.version)
        def intent(iid,player,minutes,team=20):
            return ActionIntent.decided(iid,'coach20',REQUIREMENT,{'team_id':team,'player_id':player,'minutes':minutes})
        def plan(*rows):
            return ExecutionAggregator(service).plan(RoleActionBatch('minutes',context,rows),profiles=[profile],phase_grants={('coach20',REQUIREMENT)})
        prepared=plan(intent('a',55,37),intent('b',56,21))
        self.assertFalse(prepared.issues)
        self.assertEqual(len(prepared.actions),2)
        self.assertTrue(overlaps(prepared.actions[0].resources[0],'player/55'))
        self.assertTrue(any('CONFLICT_REQUIRES_ROLE_RESOLUTION' in issue for issue in plan(intent('a',55,37),intent('b',55,21)).issues))
        self.assertTrue(any('TARGET_TEAM_OUTSIDE_ROLE_SCOPE' in issue for issue in plan(intent('foreign',55,37,21)).issues))


if __name__=='__main__':unittest.main()

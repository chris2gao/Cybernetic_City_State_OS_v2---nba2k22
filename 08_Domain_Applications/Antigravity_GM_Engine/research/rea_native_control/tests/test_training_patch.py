"""Private-input preservation and exact invocation tests, no actual game access."""
import json
import math
import shutil
import struct
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

CONTROL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CONTROL))
from contracts import NativeActionRequest
from facade import NativeControlFacade
from role_capabilities import RoleCapabilityService, RoleCapabilityProfile
from role_batches import ActionIntent, BatchContext, ExecutionAggregator, RoleActionBatch


class TrainingPatch(unittest.TestCase):
    def setUp(self):
        self.control=NativeControlFacade()

    def simulate(self, action, parameters):
        node=shutil.which('node')
        self.assertIsNotNone(node,'Node required to execute real JS handler against offline memory model')
        result=subprocess.run([node,str(CONTROL/'tests/training_patch_harness.js'),str(CONTROL/'runtime/training_patch.js')],
                              input=json.dumps({'action_id':action,'parameters':parameters}),text=True,
                              capture_output=True,check=True,timeout=10)
        return json.loads(result.stdout)

    def test_focus_patch_changes_only_twelve_owned_input_bytes(self):
        action='TRAIN_TEAM_PATCH_FOCUS_RAW'
        params={'team_id':20,'date':123456,'focus_values_raw':[0.25,1.5,-0.5]}
        program=self.control.render(NativeActionRequest(action,params))
        self.assertEqual(program.maximum_game_calls,2)
        result=self.simulate(action,params)
        expected=bytearray(8)+bytearray(result['before'])
        struct.pack_into('<3f',expected,8,*params['focus_values_raw'])
        self.assertEqual(result['input'],list(expected))
        self.assertEqual(result['after_game_memory'],result['before'])
        self.assertEqual(result['calls'],['training.daily_by_date','training.set_team_on_date'])
        self.assertEqual(result['messages'][0]['outcome'],'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED')

    def test_profile_patch_preserves_focus_intensity_and_other_bits(self):
        action='TRAIN_TEAM_PATCH_PROFILE_RAW'
        params={'team_id':20,'date':98765,'profile_values_raw':[2,4,8],'subfocus_points_raw':list(range(38))}
        self.control.render(NativeActionRequest(action,params))
        result=self.simulate(action,params)
        expected=bytearray(8)+bytearray(result['before'])
        expected[20:23]=bytes(params['profile_values_raw'])
        expected[23:61]=bytes(params['subfocus_points_raw'])
        self.assertEqual(result['input'],list(expected))
        self.assertEqual(result['input'][61:],result['before'][53:])
        self.assertEqual(result['after_game_memory'],result['before'])

    def test_missing_record_never_selects_another_date_or_calls_setter(self):
        result=self.simulate('TRAIN_TEAM_PATCH_FOCUS_RAW',{'team_id':20,'date':4321,'focus_values_raw':[1,2,3],'__missing':True})
        self.assertEqual(result['error'],'NO_EXISTING_TRAINING_RECORD_FOR_REQUESTED_DATE')
        self.assertIsNone(result['input'])
        self.assertEqual(result['calls'],['training.daily_by_date'])

    def test_invalid_native_arrays_and_extra_fields_are_not_rendered(self):
        for values in ([1,2],[True,2,3],[math.nan,2,3],[math.inf,2,3],[1e50,2,3],[10**1000,2,3]):
            with self.assertRaises((ValueError,TypeError)):
                self.control.render(NativeActionRequest('TRAIN_TEAM_PATCH_FOCUS_RAW',
                                    {'team_id':20,'date':123,'focus_values_raw':values}))
        with self.assertRaises(ValueError):
            self.control.render(NativeActionRequest('TRAIN_TEAM_PATCH_FOCUS_RAW',
                                {'team_id':20,'date':123,'focus_values_raw':[1,2,3],'value':7}))
        with self.assertRaises(ValueError):
            self.control.render(NativeActionRequest('TRAIN_TEAM_PATCH_PROFILE_RAW',
                                {'team_id':20,'date':123,'profile_values_raw':[0,1,256],'subfocus_points_raw':list(range(38))}))

    def test_role_metadata_does_not_invent_slot_meanings_or_percent_conversion(self):
        service=RoleCapabilityService()
        profile=RoleCapabilityProfile('COACH','coach20',(20,),'w','s','g','season','REGULAR_SEASON','snapshot')
        desc=service.describe_action('TRAIN.TEAM_FOCUS',profile)
        self.assertTrue(desc['call_logic_available'])
        self.assertIsNone(desc['historical_exact_live_evidence'])
        self.assertFalse(desc['identity_permission'])
        values=service.get_allowed_values('TRAIN.TEAM_FOCUS',profile)
        self.assertEqual(values['native_value_contract']['focus_values_raw']['units'],'UNKNOWN_NATIVE_SCALE')

    def test_batch_allows_disjoint_day_fields_but_rejects_full_day_overwrite(self):
        service=RoleCapabilityService()
        ids={'TRAIN.TEAM_FOCUS','TRAIN.TEAM_PROFILE','TRAIN.TEAM_SCHEDULE'}
        profile=RoleCapabilityProfile('COACH','coach20',(20,),'w','s','g','season','REGULAR_SEASON','snapshot',frozenset(ids))
        ctx=BatchContext('w','s','g','season','REGULAR_SEASON','snapshot',service.version)
        focus=ActionIntent.decided('focus','coach20','TRAIN.TEAM_FOCUS',
                 {'team_id':20,'date':123,'focus_values_raw':[0.25,0.25,0.5]})
        profile_intent=ActionIntent.decided('profile','coach20','TRAIN.TEAM_PROFILE',
                 {'team_id':20,'date':123,'profile_values_raw':[0,1,2],'subfocus_points_raw':[0]*38},dependencies=('focus',))
        aggregator=ExecutionAggregator(service)
        grants={('coach20',i) for i in ids}
        plan=aggregator.plan(RoleActionBatch('partial',ctx,(focus,profile_intent)),profiles=[profile],phase_grants=grants)
        self.assertFalse(plan.issues)
        full=ActionIntent.decided('full','coach20','TRAIN.TEAM_SCHEDULE',{'team_id':20,'date':123,'training':{
            'percentage_per_focus':[0.25,0.25,0.5],'profile_per_focus':[0,1,2],'points_per_subfocus':[0]*38,'intensity_raw':1}})
        conflict=aggregator.plan(RoleActionBatch('conflict',ctx,(focus,full)),profiles=[profile],phase_grants=grants)
        self.assertTrue(any('CONFLICT_REQUIRES_ROLE_RESOLUTION' in x for x in conflict.issues))


if __name__=='__main__': unittest.main()

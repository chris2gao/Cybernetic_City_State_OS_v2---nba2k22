"""Dedicated Native playtype compiler, role scope and actual JS handler checks."""
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
from role_capabilities import RoleCapabilityProfile,RoleCapabilityService
from role_batches import ActionIntent,BatchContext,ExecutionAggregator,RoleActionBatch,overlaps

ACTION='PLAYER_SET_PLAY_TYPES_1_TO_4'


class PlayerPlayTypes(unittest.TestCase):
    def setUp(self):
        self.control=NativeControlFacade()

    def simulate(self,slots,**options):
        node=shutil.which('node')
        self.assertIsNotNone(node)
        data={'request':{'action_id':ACTION,'parameters':{'team_id':20,'player_id':55,'slot_values':slots}},'options':options}
        process=subprocess.run([node,str(CONTROL/'tests/player_playtypes_harness.js'),str(CONTROL/'runtime/player_playtypes.js')],
                  input=json.dumps(data),text=True,capture_output=True,check=True,timeout=10)
        return json.loads(process.stdout)

    def test_each_slot_uses_its_native_setter_and_preserves_other_slots_flags(self):
        for slot,value in [('1',0),('2',15),('3',8),('4',7)]:
            with self.subTest(slot=slot):
                slots={slot:value}
                program=self.control.render(NativeActionRequest(ACTION,{'team_id':20,'player_id':55,'slot_values':slots}))
                self.assertEqual(program.maximum_game_calls,1)
                self.assertFalse(program.has_prior_live_mechanism_evidence)
                result=self.simulate(slots)
                self.assertIsNone(result['error'])
                shift=(int(slot)-1)*4
                self.assertEqual(result['after'],(result['before']&~(15<<shift))|(value<<shift))
                self.assertEqual(result['calls'],[{'binding':'player.set_playtype_'+slot,'player_uid':55,'value':value}])
                self.assertFalse(result['messages'][0]['details']['parent_editor_copy_used'])

    def test_explicit_group_order_and_exact_values_are_preserved(self):
        slots={'4':15,'1':4,'3':0,'2':2}
        program=self.control.render(NativeActionRequest(ACTION,{'team_id':20,'player_id':55,'slot_values':slots}))
        self.assertEqual(program.maximum_game_calls,4)
        result=self.simulate(slots)
        self.assertEqual([row['binding'] for row in result['calls']],['player.set_playtype_'+str(i) for i in range(1,5)])
        self.assertEqual(result['after'],(result['before']&0xffff0000)|0xf024)
        self.assertEqual(result['messages'][0]['outcome'],'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED')
        self.assertEqual(result['messages'][0]['details']['requested_slots'],slots)

    def test_invalid_slots_values_and_old_unbound_array_shape_are_rejected(self):
        for slots in ({},{'0':1},{'5':1},{'01':1},{1:1},{'1':16},{'1':-1},{'1':True},{'1':2.5},[1,2,3,4]):
            with self.subTest(slots=slots):
                with self.assertRaises((ValueError,TypeError)):
                    self.control.render(NativeActionRequest(ACTION,{'team_id':20,'player_id':55,'slot_values':slots}))

    def test_partial_native_failure_and_neighbor_change_stop_without_retry(self):
        for options,count in [({'fail_after':2},2),({'corrupt_neighbor':True},4)]:
            result=self.simulate({'1':4,'2':2,'3':0,'4':15},**options)
            self.assertIsNotNone(result['error'])
            self.assertEqual(len(result['calls']),count)
            self.assertFalse(result['messages'])

    def test_role_card_has_known_enum_and_only_its_granted_slot(self):
        service=RoleCapabilityService()
        profile=RoleCapabilityProfile('COACH','coach20',(20,),'w','s','g','season','TEAM_EDIT','snap')
        for slot in range(1,5):
            action='PLAYER.EDIT.PLAY_TYPE_'+str(slot)
            desc=service.describe_action(action,profile)
            self.assertTrue(desc['call_logic_available'])
            self.assertFalse(desc['identity_permission'])
            self.assertIsNone(desc['historical_exact_live_evidence'])
            schema=desc['native_parameter_schema']['slot_values']
            self.assertEqual(schema['required'],[str(slot)])
            self.assertFalse(schema['additionalProperties'])
            values=service.get_allowed_values(action,profile)['field_values']['play_type']
            self.assertEqual(values['exact_slot_key'],str(slot))
            self.assertEqual(values['values']['0'],'None')
            self.assertEqual(values['values']['15'],'3 PT')
            self.assertEqual(len(values['values']),16)

    def test_batch_slot_conflicts_scope_escape_and_player_identity(self):
        service=RoleCapabilityService()
        actions={'PLAYER.EDIT.PLAY_TYPE_'+str(i) for i in range(1,5)}
        coach=RoleCapabilityProfile('COACH','coach20',(20,),'w','s','g','season','TEAM_EDIT','snap',frozenset(actions))
        context=BatchContext('w','s','g','season','TEAM_EDIT','snap',service.version)
        def intent(iid,slot,slots,issuer='coach20',player=55):
            return ActionIntent.decided(iid,issuer,'PLAYER.EDIT.PLAY_TYPE_'+str(slot),{'team_id':20,'player_id':player,'slot_values':slots})
        def plan(profile,*rows):
            return ExecutionAggregator(service).plan(RoleActionBatch('playtypes',context,rows),profiles=[profile],phase_grants={(profile.actor_uid,a) for a in actions})
        good=plan(coach,intent('a',1,{'1':4}),intent('b',2,{'2':2}))
        self.assertFalse(good.issues)
        self.assertTrue(overlaps(good.actions[0].resources[0],'player/55'))
        self.assertFalse(overlaps(good.actions[0].resources[0],good.actions[1].resources[0]))
        self.assertTrue(any('SHARED_HANDLER_SLOT_SCOPE_ESCAPE' in issue for issue in plan(coach,intent('escape',1,{'2':2})).issues))
        self.assertTrue(any('CONFLICT_REQUIRES_ROLE_RESOLUTION' in issue for issue in plan(coach,intent('a',1,{'1':4}),intent('b',1,{'1':2})).issues))
        persona=RoleCapabilityProfile('PLAYER','player55',(20,),'w','s','g','season','TEAM_EDIT','snap',frozenset(actions),player_scope=(55,))
        self.assertFalse(plan(persona,intent('own',1,{'1':4},'player55')).issues)
        foreign=plan(persona,intent('other',1,{'1':4},'player55',56))
        self.assertTrue(any('PLAYER_EDIT_IDENTITY_OUTSIDE_ROLE_SCOPE' in issue for issue in foreign.issues))


if __name__=='__main__':unittest.main()

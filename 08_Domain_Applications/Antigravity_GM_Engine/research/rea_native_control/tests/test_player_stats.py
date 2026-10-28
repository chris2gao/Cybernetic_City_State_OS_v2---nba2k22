"""Native indexed stat compiler, role policy, source join and real JS handler."""
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
from player_fields import load_fields
from role_capabilities import RoleCapabilityProfile,RoleCapabilityService
from role_batches import ActionIntent,BatchContext,ExecutionAggregator,RoleActionBatch,overlaps


class PlayerStats(unittest.TestCase):
    def setUp(self):
        self.control=NativeControlFacade()
        self.fields=load_fields()['families']

    def simulate(self,action,values,**options):
        node=shutil.which('node')
        self.assertIsNotNone(node)
        native=self.control.registry.get(action)
        bindings={step['binding_id']:self.control.registry.binding(step['binding_id']).to_dict()
                  for step in native['call_sequence'] if step.get('binding_id')}
        params={'team_id':20,'player_id':55,'values':values} if action.startswith('PLAYER_PATCH_') else {'team_id':20,'player_id':55,'field_id':next(iter(values)),'value':next(iter(values.values()))}
        self.control.render(NativeActionRequest(action,params))
        process=subprocess.run([node,str(CONTROL/'tests/player_stats_harness.js'),str(CONTROL/'runtime/player_stats.js')],
                  input=json.dumps({'request':{'action_id':action,'parameters':params},'bindings':bindings,'options':options}),
                  text=True,capture_output=True,check=True,timeout=10)
        return json.loads(process.stdout)

    def test_all54_qualified_attributes_exact_native_indices_encoding_and_preservation(self):
        values={key:25+(index*11)%75 for index,(key,spec) in enumerate(self.fields['attributes'].items()) if spec['callable']}
        self.assertEqual(len(values),54)
        result=self.simulate('PLAYER_PATCH_ATTRIBUTES',values)
        self.assertIsNone(result['error'])
        expected=result['initial'][:]
        for key,value in values.items():expected[self.fields['attributes'][key]['offset']-0x41f]=value*3-75
        self.assertEqual(result['after'],expected)
        self.assertEqual(result['flagsAfter'],result['flagsBefore']&0xffffffbf)
        self.assertEqual({row['index'] for row in result['calls']},{self.fields['attributes'][key]['native_index'] for key in values})
        self.assertNotIn('potential',result['messages'][0]['details']['observed_before_values'])
        self.assertFalse(result['messages'][0]['details']['parent_editor_copy_used'])

    def test_all99_tendencies_including_unnamed_slots_preserve_other_fields(self):
        values={key:(index*7)%101 for index,key in enumerate(self.fields['tendencies'])}
        result=self.simulate('PLAYER_PATCH_TENDENCIES',values)
        self.assertIsNone(result['error'])
        expected=result['initial'][:]
        for key,value in values.items():expected[self.fields['tendencies'][key]['offset']-0x41f]=value
        self.assertEqual(result['after'],expected)
        self.assertEqual(result['flagsAfter'],result['flagsBefore'])
        self.assertEqual(len(result['calls']),99)

    def test_scalar_boundaries_and_no_inferred_clamping(self):
        for value in (25,99):
            result=self.simulate('PLAYER_SET_ATTRIBUTE',{'intangibles':value})
            self.assertIsNone(result['error'])
            self.assertEqual(result['calls'][0]['value'],value)
        for action,key,value in [('PLAYER_SET_ATTRIBUTE','intangibles',24),('PLAYER_SET_ATTRIBUTE','intangibles',100),
                                 ('PLAYER_SET_ATTRIBUTE','potential',50),('PLAYER_SET_TENDENCY','SHOT_TENDENCY',101),
                                 ('PLAYER_SET_TENDENCY','SHOT_TENDENCY',True)]:
            with self.assertRaises((ValueError,TypeError)):
                self.control.render(NativeActionRequest(action,{'team_id':20,'player_id':55,'field_id':key,'value':value}))

    def test_context_interruption_and_unrequested_changes_are_not_success(self):
        for options,expected_calls in [({'wrong_delegate':True},0),({'fail_after':1},1),
                                       ({'corrupt_other_field':True},2),({'missing_invalidation':True},2)]:
            result=self.simulate('PLAYER_PATCH_ATTRIBUTES',{'driving_layup':75,'intangibles':50},**options)
            self.assertIsNotNone(result['error'])
            self.assertEqual(len(result['calls']),expected_calls)
            self.assertFalse(result['messages'])

    def make_profile(self,role,actor,actions,players=()):
        return RoleCapabilityProfile(role,actor,(20,),'w','s','g','season','TEAM_EDIT','snap',frozenset(actions),player_scope=players)

    def plan(self,service,profile,requirement,params):
        ctx=BatchContext('w','s','g','season','TEAM_EDIT','snap',service.version)
        intent=ActionIntent.decided('edit',profile.actor_uid,requirement,{'team_id':20,'player_id':55}|params)
        return ExecutionAggregator(service).plan(RoleActionBatch('stats',ctx,(intent,)),profiles=[profile],phase_grants={(profile.actor_uid,requirement)})

    def test_attribute_permissions_world_editor_and_only_gm_intangibles_exception(self):
        service=RoleCapabilityService()
        req='PLAYER.EDIT.ATTR_SET'
        gm=self.make_profile('GM','gm20',{req})
        self.assertFalse(self.plan(service,gm,req,{'field_id':'intangibles','value':50}).issues)
        self.assertTrue(any('FIELD_OUTSIDE_ROLE_SCOPE' in issue for issue in self.plan(service,gm,req,{'field_id':'driving_layup','value':75}).issues))
        persona=self.make_profile('PLAYER','p55',{req},(55,))
        self.assertTrue(any('ROLE_ACTION_NOT_GRANTED' in issue for issue in self.plan(service,persona,req,{'field_id':'driving_layup','value':75}).issues))
        editor=self.make_profile('WORLD_ADMIN','editor',{req})
        self.assertFalse(self.plan(service,editor,req,{'field_id':'driving_layup','value':75}).issues)
        gm_values=service.get_allowed_values(req,gm)['field_values']['field_id']['values']
        self.assertEqual(set(gm_values),{'intangibles'})
        self.assertEqual(len(service.get_allowed_values(req,editor)['field_values']['field_id']['values']),54)
        self.assertFalse(service.describe_action(req,persona)['identity_permission'])

    def test_tendency_semantics_and_own_player_scope(self):
        service=RoleCapabilityService()
        req='PLAYER.EDIT.TENDENCY_SET'
        unknown=next(key for key,value in self.fields['tendencies'].items() if not value['name_known'])
        coach=self.make_profile('COACH','coach20',{req})
        self.assertFalse(self.plan(service,coach,req,{'field_id':'SHOT_TENDENCY','value':80}).issues)
        self.assertTrue(self.plan(service,coach,req,{'field_id':unknown,'value':80}).issues)
        editor=self.make_profile('WORLD_ADMIN','editor',{req})
        self.assertFalse(self.plan(service,editor,req,{'field_id':unknown,'value':80}).issues)
        foreign_persona=self.make_profile('PLAYER','p56',{req},(56,))
        self.assertTrue(any('IDENTITY_OUTSIDE_ROLE_SCOPE' in issue for issue in self.plan(service,foreign_persona,req,{'field_id':'SHOT_TENDENCY','value':80}).issues))
        self.assertEqual(len(service.get_allowed_values(req,coach)['field_values']['field_id']['values']),48)

    def test_native_source_join_has54_same_encoding_leaves_and_exact99_tendency_offsets(self):
        source=CONTROL.parents[3]/'01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/player_indexed_stat_field_contract_015.json'
        rows=json.loads(source.read_text(encoding='utf8'))['fields']
        matched=0
        for row in rows:
            field=row['known_profile_field']
            if not field or field['name']=='potential':continue
            prefix=[]
            for instruction in row['leaf_instructions']:
                if instruction['mnemonic']=='mov' and instruction['operands'].startswith('byte ptr [rcx + '):break
                prefix.append((instruction['mnemonic'],instruction['operands']))
            self.assertEqual(prefix,[('sub','rsp, 0x28'),('and','dword ptr [rcx + 0x31c], 0xffffffbf'),
                ('movzx','eax, dl'),('sub','dl, 0x4b'),('add','al, al'),('add','dl, al')])
            self.assertEqual(self.fields['attributes'][field['name']]['native_index'],row['native_index'])
            matched+=1
        self.assertEqual(matched,54)
        self.assertEqual({spec['offset'] for spec in self.fields['tendencies'].values()},set(range(0x458,0x4bb)))

    def test_batch_compiles_all_values_before_dispatch_and_keeps_player_resource(self):
        service=RoleCapabilityService()
        req='PLAYER.EDIT.ATTR_BATCH'
        editor=self.make_profile('WORLD_ADMIN','editor',{req})
        good=self.plan(service,editor,req,{'values':{'driving_layup':75,'intangibles':50}})
        self.assertFalse(good.issues)
        self.assertEqual(len(good.actions[0].resources),2)
        self.assertTrue(overlaps(good.actions[0].resources[0],'player/55'))
        bad=self.plan(service,editor,req,{'values':{'driving_layup':75,'potential':50}})
        self.assertTrue(bad.issues)
        self.assertFalse(bad.actions)


if __name__=='__main__':unittest.main()

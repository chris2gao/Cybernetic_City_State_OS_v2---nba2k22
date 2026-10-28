"""Original Badge rules, exact intent, effective modifiers and real JS handler."""
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

CONTROL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CONTROL))
from badge_fields import affected_fields,load_fields,resource_fields
from contracts import NativeActionRequest
from facade import NativeControlFacade
from role_capabilities import RoleCapabilityProfile,RoleCapabilityService
from role_batches import ActionIntent,BatchContext,ExecutionAggregator,RoleActionBatch


class PlayerBadges(unittest.TestCase):
    def setUp(self):
        self.facade=NativeControlFacade()
        self.catalog=load_fields()

    def parameters(self,name,value,before=None,after=None):
        group=affected_fields(self.catalog,name)
        start={key:0 for key in group}|(before or {})
        end=(start|{name:value}) if after is None else after
        return {'team_id':20,'player_id':55,'field_id':name,'value':value,'expected_before':start,'expected_after':end}

    def simulate(self,p,initial=None,**options):
        self.facade.render(NativeActionRequest('PLAYER_SET_BADGE',p))
        action=self.facade.registry.get('PLAYER_SET_BADGE')
        bindings={step['binding_id']:self.facade.registry.binding(step['binding_id']).to_dict() for step in action['call_sequence']}
        process=subprocess.run([shutil.which('node'),str(CONTROL/'tests/player_badges_harness.js'),str(CONTROL/'runtime/player_badges.js')],
            input=json.dumps({'request':{'action_id':'PLAYER_SET_BADGE','parameters':p},'bindings':bindings,
                              'initial':initial or p['expected_before'],'options':options}),
            text=True,capture_output=True,check=True,timeout=10)
        return json.loads(process.stdout)

    def setters(self,result):
        return [row for row in result['calls'] if row['binding']=='player.set_badge']

    def test_runtime_catalog_and_abi_follow_independent_pinned_field_recovery(self):
        context=self.facade.registry.binding('player.badge_context').input_layout
        self.assertEqual(context['catalog'],self.catalog)
        evidence=CONTROL.parents[3]/self.catalog['source']
        fields=json.loads(evidence.read_text(encoding='utf8'))['fields']
        for source in fields:
            spec=self.catalog['by_id'][source['badge_id']]
            for key in ('internal_name','byte_offset','shift','mask','maximum','sentinel_name'):
                self.assertEqual(spec[key],source[key])
            for key in ('dword_offset','shift_left','arithmetic_shift_right','signed_width'):
                self.assertEqual(spec['signed_modifier_field'][key],source['signed_modifier_field'][key])
        setter=self.facade.registry.binding('player.set_badge')
        self.assertEqual(setter.rva,0x992d40)
        self.assertEqual([parameter['type'] for parameter in setter.parameters],['pointer','int','uint8','int'])
        self.assertEqual(setter.return_type,'void')
        self.assertTrue(self.facade.registry.binding('player.badge_set_candidate').input_layout['not_callable'])

    def test_all98_non_sentinel_fields_keep_exact_id_range_padding_and_original_flag(self):
        count=0
        for name,field in self.catalog['fields'].items():
            if field['sentinel_name']:continue
            result=self.simulate(self.parameters(name,field['maximum']))
            self.assertIsNone(result['error'],name)
            self.assertEqual(self.setters(result),[{'binding':'player.set_badge','index':field['badge_id'],'value':field['maximum'],'flag':0}])
            self.assertEqual(result['after'][:156],result['initial'][:156])
            self.assertEqual(result['flagsAfter'],result['flagsBefore']&0xffffffbf)
            self.assertTrue(result['messages'][0]['details']['explicit_coupled_state_matched'])
            count+=1
        self.assertEqual(count,98)

    def test_exclusive_flips_and_explicit_trait_combo_preserve_other_values(self):
        for group in self.catalog['exclusive_groups']:
            for chosen in group:
                other=next(name for name in group if name!=chosen)
                p=self.parameters(chosen,1,{other:1},{name:int(name==chosen) for name in group})
                self.assertIsNone(self.simulate(p)['error'])
        p=self.parameters('Expressive',1,{'Unpredictable':1},
            {'Expressive':1,'Unpredictable':1,'LaidBack':0})
        self.assertIsNone(self.simulate(p)['error'])
        p=self.parameters('Unpredictable',1,after={'Expressive':1,'Unpredictable':1,'LaidBack':0})
        self.assertIsNone(self.simulate(p,nodes=[{'values':{'Expressive':1}}])['error'])
        p=self.parameters('LaidBack',1,{'Expressive':1,'Unpredictable':1},
            {'Expressive':0,'Unpredictable':0,'LaidBack':1})
        self.assertIsNone(self.simulate(p)['error'])

    def test_effective_modifiers_block_original_assertions_and_are_cross_checked(self):
        p=self.parameters('Expressive',1)
        result=self.simulate(p,nodes=[{'values':{'LowFriendliness':1}}])
        self.assertIn('ASSERTION_PRECONDITION',result['error'])
        self.assertFalse(result['calls'])
        p=self.parameters('LowFriendliness',1)
        result=self.simulate(p,nodes=[{'values':{'Expressive':1}}])
        self.assertIn('RULE_BLOCKS',result['error'])
        self.assertFalse(result['calls'])
        result=self.simulate(self.parameters('CatchAndShoot',3),wrong_effective=True)
        self.assertIn('GETTER_MODEL_MISMATCH',result['error'])
        self.assertFalse(self.setters(result))

    def test_modifier_selector_signed_values_and_cycle_bound(self):
        p=self.parameters('Expressive',1)
        # Negative signed modifiers and a future-stage/inapplicable node cannot invent a block.
        result=self.simulate(p,nodes=[{'values':{'LowFriendliness':-1}},
            {'metadata':0x3fff,'values':{'LowFriendliness':1}},
            {'metadata':0,'values':{'LowFriendliness':1}}])
        self.assertIsNone(result['error'])
        result=self.simulate(p,nodes=[{'values':{}}],cycle=True)
        self.assertIn('CYCLE_OR_INSPECTION_BOUND',result['error'])
        self.assertFalse(result['calls'])
        result=self.simulate(p,nodes=[{'values':{}} for _ in range(1025)])
        self.assertIn('CYCLE_OR_INSPECTION_BOUND',result['error'])
        self.assertFalse(result['calls'])

    def test_exact_before_after_and_unchanged_primary_native_early_return(self):
        p=self.parameters('CatchAndShoot',4,{'CatchAndShoot':1})
        result=self.simulate(p,initial={'CatchAndShoot':2})
        self.assertIn('EXPECTED_BEFORE',result['error'])
        self.assertFalse(result['calls'])
        p=self.parameters('HighFriendliness',1,{'LowFriendliness':1},
            {'LowFriendliness':1,'HighFriendliness':1})
        result=self.simulate(p)
        self.assertIn('EXPLICIT_AFTER_DIFFERS',result['error'])
        self.assertFalse(result['calls'])
        p=self.parameters('HighFriendliness',1,{'HighFriendliness':1,'LowFriendliness':1})
        result=self.simulate(p)
        self.assertIsNone(result['error'])
        self.assertEqual(result['flagsAfter'],result['flagsBefore'])
        self.assertEqual(result['after'],result['initial'])

    def test_context_preservation_and_interruption_do_not_claim_effect_success(self):
        p=self.parameters('CatchAndShoot',4)
        for options,expected_writes in [({'wrong_delegate':True},0),({'state_changes_during_getter':True},0),
            ({'corrupt_unrequested':True},1),({'corrupt_padding':True},1),({'missing_invalidation':True},1),
            ({'nodes':[{'values':{}}],'modifier_changed_after_set':True},1),({'roster_changed_after':True},1),({'fail_after_set':True},1)]:
            result=self.simulate(p,**options)
            self.assertIsNotNone(result['error'],options)
            self.assertEqual(len(self.setters(result)),expected_writes,options)
            self.assertFalse(result['messages'])

    def test_compiler_rejects_sentinel_boolean_bad_ranges_and_incomplete_coupled_intent(self):
        p=self.parameters('CatchAndShoot',3)
        for patch in [{'field_id':'NONE'},{'value':True},{'value':5},
                      {'expected_before':{}},{'expected_after':{'CatchAndShoot':2}}]:
            with self.assertRaises((ValueError,TypeError)):
                self.facade.render(NativeActionRequest('PLAYER_SET_BADGE',p|patch))
        with self.assertRaises(ValueError):
            self.facade.render(NativeActionRequest('PLAYER_SET_BADGE',self.parameters('AlphaDog',2)))
        p=self.parameters('HighFriendliness',1,{'HighFriendliness':1,'LowFriendliness':1},
            {'HighFriendliness':1,'LowFriendliness':0})
        with self.assertRaises(ValueError):self.facade.render(NativeActionRequest('PLAYER_SET_BADGE',p))

    def test_world_only_cards_and_guard_resources_prevent_hidden_cross_rule_conflicts(self):
        service=RoleCapabilityService();req='PLAYER.EDIT.BADGE_SET'
        context=BatchContext('w','s','g','season','TEAM_EDIT','snap',service.version)
        p=self.parameters('Expressive',1)
        for role in ('GM','COACH','PLAYER','WORLD_ADMIN'):
            profile=RoleCapabilityProfile(role,'editor',(20,),'w','s','g','season','TEAM_EDIT','snap',frozenset({req}))
            intent=ActionIntent.decided('badge','editor',req,p)
            plan=ExecutionAggregator(service).plan(RoleActionBatch('badge',context,(intent,)),profiles=[profile],phase_grants={('editor',req)})
            self.assertEqual(not plan.issues,role=='WORLD_ADMIN')
            values=service.get_allowed_values(req,profile)['field_values']['field_id']['values']
            self.assertEqual(len(values),98 if role=='WORLD_ADMIN' else 0)
            encoded=json.dumps(values)
            self.assertNotIn('byte_offset',encoded);self.assertNotIn('rva',encoded)
        self.assertIn('LowFriendliness',resource_fields(self.catalog,p))
        self.assertIn('Expressive',resource_fields(self.catalog,self.parameters('LowFriendliness',1)))
        profile=RoleCapabilityProfile('WORLD_ADMIN','editor',(20,),'w','s','g','season','TEAM_EDIT','snap',frozenset({req}))
        intents=(ActionIntent.decided('one','editor',req,p),
                 ActionIntent.decided('two','editor',req,self.parameters('HighFriendliness',1)))
        plan=ExecutionAggregator(service).plan(RoleActionBatch('conflict',context,intents),profiles=[profile],phase_grants={('editor',req)})
        self.assertTrue(any('CONFLICT' in issue for issue in plan.issues))


if __name__=='__main__':unittest.main()

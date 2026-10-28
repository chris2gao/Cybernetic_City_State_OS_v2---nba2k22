"""Selected Native read programs and capture-free, provenance-bound role views."""
import json
import shutil
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

CONTROL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CONTROL))
from contracts import NativeActionRequest,NativeActionResult,Outcome
from facade import NativeControlFacade
from readers import NativeReadCatalog,NativeReadFacade,NativeReadQuery
from player_editor_state import ACTION,DATASET,FAMILIES,PlayerEditorSnapshotProvider,validate_projection
from role_capabilities import RoleCapabilityProfile,RoleCapabilityService


class PlayerEditorRead(unittest.TestCase):
    def setUp(self):
        self.facade=NativeControlFacade()
        self.context=dict(world_id='w',save_instance_id='save',generation_id='g',season_id='season',phase='TEAM_EDIT',snapshot_ref='snap')

    def projection(self,**selected):return {family:selected.get(family,[]) for family in FAMILIES}

    def params(self,**selected):return {'team_id':20,'player_id':55,'projection':self.projection(**selected)}

    def simulate(self,p,*,compile=True,initial=None,**options):
        if compile:self.facade.render(NativeActionRequest(ACTION,p))
        action=self.facade.registry.get(ACTION)
        bindings={step['binding_id']:self.facade.registry.binding(step['binding_id']).to_dict() for step in action['call_sequence']}
        process=subprocess.run([shutil.which('node'),str(CONTROL/'tests/player_badges_harness.js'),str(CONTROL/'runtime/read_player_editor.js')],
            input=json.dumps({'request':{'action_id':ACTION,'parameters':p},'bindings':bindings,'initial':initial or {},'options':options}),
            text=True,capture_output=True,check=True,timeout=10)
        return json.loads(process.stdout)

    def receipt(self,p,*,initial=None,**options):
        result=self.simulate(p,initial=initial,**options)
        self.assertIsNone(result['error'])
        message=result['messages'][0]
        native={'kind':'native-control-result','action_id':ACTION,'outcome':message['outcome'],'details':message['details']}
        return NativeActionResult(ACTION,Outcome.RETURNED,p,native),result

    def provider(self,result,**kwargs):
        return PlayerEditorSnapshotProvider(result,context=self.context,observation_ref='fixture/editor-read',source_kind='OFFLINE_FIXTURE',**kwargs)

    def profile(self,grants,*,role='GM',team=(20,)):
        return RoleCapabilityProfile(role,'viewer',team,**self.context,read_grants=((DATASET,tuple(grants)),))

    def test_all_selected_fields_are_read_without_setters_or_game_byte_changes(self):
        layout=self.facade.registry.binding('player.editor_read_context').input_layout
        selection={family:[name for name,field in fields.items() if field['callable']] for family,fields in layout['stats']['families'].items()}
        selection['badges']=[name for name,field in layout['badges']['fields'].items() if not field['sentinel_name']]
        selection['play_types']=['1','2','3','4'];p=self.params(**selection)
        program=self.facade.render(NativeActionRequest(ACTION,p))
        self.assertEqual(program.maximum_game_calls,251)
        self.assertNotIn("call('player.set",program.script)
        result=self.simulate(p)
        self.assertIsNone(result['error'])
        self.assertEqual(len(result['calls']),251)
        self.assertEqual(result['after'],result['initial']);self.assertEqual(result['flagsAfter'],result['flagsBefore'])
        data=result['messages'][0]['details']['data']
        self.assertEqual([len(data[key]) for key in FAMILIES],[54,99,98,4])
        self.assertNotIn('potential',json.dumps(data).lower())
        self.assertNotIn('NONE',data['badges'])

    def test_original_getter_value_is_not_replaced_by_a_python_or_js_rating_guess(self):
        p=self.params(attributes=['driving_layup'],tendencies=['SHOT_TENDENCY'],play_types=['1','4'])
        result=self.simulate(p,ui_values={'driving_layup':57},stat_raw={'driving_layup':1,'SHOT_TENDENCY':255})
        self.assertIsNone(result['error'])
        data=result['messages'][0]['details']['data']
        self.assertEqual(data['attributes']['driving_layup'],57)
        self.assertEqual(data['tendencies']['SHOT_TENDENCY'],255)
        self.assertEqual(data['play_types'],{'1':10,'4':13})
        self.assertEqual([row['binding'] for row in result['calls']],['player.get_stat_ui','player.get_stat_ui'])
        receipt,_=self.receipt(p,ui_values={'driving_layup':57},stat_raw={'SHOT_TENDENCY':255})
        view=RoleCapabilityService().read_role_visible_data(self.profile(('identity','observation','tendencies.SHOT_TENDENCY')),DATASET,provider=self.provider(receipt))
        self.assertEqual(view['data']['tendencies.SHOT_TENDENCY']['value'],255)
        self.assertFalse(view['data']['tendencies.SHOT_TENDENCY']['within_known_edit_range'])

    def test_raw_and_effective_badges_keep_signed_modifier_difference_and_group_values(self):
        p=self.params(badges=['Expressive','Unpredictable','LaidBack'])
        result=self.simulate(p,nodes=[{'values':{'Expressive':1,'LaidBack':-1}}],initial={'LaidBack':1})
        self.assertIsNone(result['error'])
        data=result['messages'][0]['details']['data']['badges']
        self.assertEqual(data['Expressive'],{'raw_level':0,'effective_level':1})
        self.assertEqual(data['LaidBack'],{'raw_level':1,'effective_level':0})
        self.assertEqual(len(result['calls']),3)

    def test_projection_rejects_potential_sentinel_unknown_duplicates_and_implicit_all(self):
        for selected in [self.projection(),self.projection(attributes=['potential']),self.projection(badges=['NONE']),
            self.projection(tendencies=['UNKNOWN_INVENTED_NAME']),self.projection(play_types=['0']),
            self.projection(attributes=['driving_layup','driving_layup'])]:
            with self.assertRaises(ValueError):validate_projection(CONTROL,selected)
        p=self.params(attributes=['potential'])
        result=self.simulate(p,compile=False)
        self.assertIsNotNone(result['error']);self.assertFalse(result['calls']);self.assertFalse(result['messages'])
        with self.assertRaises(ValueError):NativeReadFacade(self.facade).read(NativeReadQuery(DATASET,p))

    def test_unstable_identity_bytes_modifiers_or_effective_getter_emit_no_read_snapshot(self):
        p=self.params(attributes=['driving_layup'],badges=['Expressive'])
        for options in ({'state_changes_during_getter':True},{'roster_changed_during_getters':True},
                        {'wrong_effective':True},{'nodes':[{'values':{}}],'modifier_changed_during_getter':True},
                        {'nodes':[{'values':{}}],'cycle':True},{'ui_values':{'driving_layup':0}}):
            result=self.simulate(p,**options)
            self.assertIsNotNone(result['error'],options);self.assertFalse(result['messages'])
            self.assertFalse(any(row['binding']=='player.set_badge' for row in result['calls']))

    def test_snapshot_provider_freezes_receipt_and_projects_exact_read_grants_without_capture(self):
        p=self.params(attributes=['driving_layup'],badges=['AlphaDog'],tendencies=['SHOT_TENDENCY'])
        receipt,_=self.receipt(p,ui_values={'driving_layup':57})
        provider=self.provider(receipt)
        receipt.native_result['details']['data']['attributes']['driving_layup']=99
        service=RoleCapabilityService()
        profile=self.profile(('identity','observation','attributes.driving_layup','badges.AlphaDog'))
        view=service.read_role_visible_data(profile,DATASET,provider=provider)
        self.assertEqual(set(view['data']),{'identity','observation','attributes.driving_layup','badges.AlphaDog'})
        self.assertEqual(view['data']['attributes.driving_layup']['value'],57)
        self.assertEqual(view['data']['observation']['source_kind'],'OFFLINE_FIXTURE')
        self.assertEqual(view['data']['identity'],{'team_id':20,'player_id':55})
        encoded=json.dumps(view).lower()
        for marker in ('"rva":','rva+','"byte_offset":','"raw_bytes":','0x140'):
            self.assertNotIn(marker,encoded)
        view['data']['attributes.driving_layup']['value']=1
        self.assertEqual(service.read_role_visible_data(profile,DATASET,provider=provider)['data']['attributes.driving_layup']['value'],57)

    def test_context_team_provenance_missing_fields_and_ungranted_dataset_fail_closed(self):
        receipt,_=self.receipt(self.params(attributes=['driving_layup']))
        provider=self.provider(receipt);service=RoleCapabilityService()
        profile=self.profile(('identity','observation','attributes.driving_layup'))
        for changed in (replace(profile,phase='OTHER'),replace(profile,save_instance_id='other'),replace(profile,team_scope=(21,))):
            with self.assertRaises((ValueError,PermissionError)):service.read_role_visible_data(changed,DATASET,provider=provider)
        for grants in (('attributes.driving_layup',),('identity','observation','attributes.close_shot')):
            with self.assertRaises((ValueError,PermissionError)):service.read_role_visible_data(self.profile(grants),DATASET,provider=provider)
        with self.assertRaises(PermissionError):service.read_role_visible_data(replace(profile,read_grants=()),DATASET,provider=lambda *_:self.fail('Provider called'))
        with self.assertRaises(ValueError):PlayerEditorSnapshotProvider(receipt,context=self.context,observation_ref='missing-evidence',source_kind='NATIVE_TRANSPORT_RECEIPT')
        # Synthetic envelope-binding check only; no runtime evidence was acquired.
        native=json.loads(json.dumps(receipt.native_result))|{'evidence_id':'synthetic-envelope-id'}
        bound=PlayerEditorSnapshotProvider(replace(receipt,native_result=native),context=self.context,
            observation_ref='synthetic-envelope-id',source_kind='NATIVE_TRANSPORT_RECEIPT')
        self.assertEqual(bound(profile,DATASET)['data']['observation']['observation_ref'],'synthetic-envelope-id')

    def test_snapshot_rejects_wrong_target_projection_or_raw_debug_payload(self):
        receipt,_=self.receipt(self.params(badges=['AlphaDog']))
        for key,value in [('player_id',56),('projection',self.projection(badges=['Enforcer'])),('raw_bytes',[1,2])]:
            changed=NativeActionResult(ACTION,Outcome.RETURNED,receipt.original_request,json.loads(json.dumps(receipt.native_result)))
            changed.native_result['details']['data'][key]=value
            with self.assertRaises(ValueError):self.provider(changed)
        with self.assertRaises(ValueError):self.provider(replace(receipt,outcome=Outcome.UNKNOWN))

    def test_read_grant_does_not_grant_badge_editing_and_opaque_tendency_remains_unknown(self):
        stats=self.facade.registry.binding('player.editor_read_context').input_layout['stats']['families']
        unknown=next(name for name,field in stats['tendencies'].items() if not field['name_known'])
        receipt,_=self.receipt(self.params(badges=['AlphaDog'],tendencies=[unknown]))
        profile=self.profile(('identity','observation','badges.AlphaDog','tendencies.'+unknown),role='PLAYER')
        service=RoleCapabilityService();view=service.read_role_visible_data(profile,DATASET,provider=self.provider(receipt))
        self.assertFalse(view['data']['tendencies.'+unknown]['name_known'])
        self.assertFalse(service.describe_action('PLAYER.EDIT.BADGE_SET',profile)['identity_permission'])
        self.assertEqual(service.get_allowed_values('PLAYER.EDIT.BADGE_SET',profile)['field_values']['field_id']['values'],{})

    def test_read_catalog_dispatch_is_inert_without_transport_and_uses_exact_dynamic_budget(self):
        catalog=NativeReadCatalog();self.assertEqual(len(catalog.list()),13)
        p=self.params(play_types=['2'])
        result=NativeReadFacade(self.facade,catalog).read(NativeReadQuery(DATASET,p))
        self.assertEqual(result.outcome,Outcome.PREPARED)
        self.assertEqual(self.facade.render(NativeActionRequest(ACTION,p)).maximum_game_calls,0)
        class CountingRead:
            def __init__(self):self.calls=[]
            def execute(self,script,**kwargs):
                self.calls.append(kwargs)
                self.assert_no_setter="call('player.set" not in script
                return {'outcome':'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED'}
        transport=CountingRead();control=NativeControlFacade(transport=transport)
        NativeReadFacade(control,catalog).read(NativeReadQuery(DATASET,self.params(attributes=['driving_layup'],badges=['AlphaDog']),'query-id'))
        self.assertEqual(transport.calls,[{'action_id':ACTION,'request_id':'query-id','maximum_game_calls':2}])
        self.assertTrue(transport.assert_no_setter)


if __name__=='__main__':unittest.main()

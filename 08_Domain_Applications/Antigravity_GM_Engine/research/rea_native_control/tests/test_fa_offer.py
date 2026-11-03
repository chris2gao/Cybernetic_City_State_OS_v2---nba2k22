"""Exact submitted terms and actual JS handler, with a wholly synthetic Native service."""
import json,shutil,struct,subprocess,sys,tempfile,unittest
from dataclasses import replace
from pathlib import Path
CONTROL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CONTROL))
from contracts import NativeActionRequest
from facade import NativeControlFacade
from signing_fields import decode_record,encode_fresh_fa_offer,validate_fa_offer_contract
from role_capabilities import RoleCapabilityService,RoleCapabilityProfile
from role_batches import ActionIntent,BatchContext,ExecutionAggregator,ExecutionJournal,NativeActionDispatcher,RoleActionBatch

ACTION='CONTRACT_SUBMIT_FREE_AGENT_OFFER'
REQ='GM.CONTRACT.CONTRACT_OFFER'


class FreeAgentOffer(unittest.TestCase):
    def setUp(self):self.facade=NativeControlFacade()

    def terms(self,**changes):
        return {'signing_type':'FREE_AGENT','annual_wages_native':[101,202,303,404,0,0],
            'years_native':4,'option_type':'PLAYER_OPTION','contract_type':'NORMAL',
            'distribution':'CUSTOM','no_trade_clause':False,**changes}

    def parameters(self,**changes):return {'team_id':20,'player_id':55,'contract':self.terms(),**changes}

    def simulate(self,parameters=None,records=(),compile=True,**options):
        p=self.parameters() if parameters is None else parameters
        if compile:self.assertEqual(self.facade.render(NativeActionRequest(ACTION,p)).maximum_game_calls,7)
        bindings={row['binding_id']:self.facade.registry.binding(row['binding_id']).to_dict()
            for row in self.facade.registry.get(ACTION)['call_sequence']}
        done=subprocess.run([shutil.which('node'),str(CONTROL/'tests/fa_offer_harness.js'),str(CONTROL/'runtime/sign_fa_offer.js')],
            input=json.dumps({'request':{'parameters':p},'bindings':bindings,'records':records,'options':options}),
            text=True,capture_output=True,timeout=10,check=True)
        return json.loads(done.stdout)

    def test_actual_handler_matches_independent_constructor_and_exact_original_caller_arguments(self):
        result=self.simulate();self.assertIsNone(result['error']);self.assertEqual(result['offers'],1)
        self.assertEqual(len(result['calls']),7);self.assertEqual(result['forbiddenWrites'],0)
        expected=bytearray(44);struct.pack_into('<HHI6I',expected,0,55,20,101,101,202,303,404,0,0)
        struct.pack_into('<I',expected,32,(3<<8)|(1<<18)|(2<<22)|(2<<28));struct.pack_into('<I',expected,40,0xace00000|(4<<8))
        self.assertEqual(result['privateInput'],expected.hex())
        template=bytearray(44);struct.pack_into('<I',template,40,0xace00000)
        self.assertEqual(encode_fresh_fa_offer(template,55,20,self.terms()),bytes(expected))
        details=result['messages'][0]['details'];self.assertTrue(details['submission_only']);self.assertFalse(details['signing_completed'])
        self.assertEqual(details['observation']['status_name'],'OFFERED')
        self.assertFalse(details['generated_prices_used']);self.assertFalse(details['direct_pool_or_player_writes'])

    def test_supported_contract_options_preserve_caller_terms_without_generating_prices(self):
        for kind in ['NORMAL','HARDSHIP']:
            for option in ['NO_OPTION','TEAM_OPTION','PLAYER_OPTION','TEAM_OPTION_2']:
                with self.subTest(kind=kind,option=option):
                    terms=self.terms(contract_type=kind,option_type=option,no_trade_clause=True)
                    result=self.simulate(self.parameters(contract=terms));self.assertIsNone(result['error'])
                    fields=decode_record(bytes.fromhex(result['privateInput']))
                    self.assertEqual(fields['ForcedWage'],terms['annual_wages_native']);self.assertEqual(fields['NoTradeClause'],1)
                    self.assertEqual(fields['ContractType'],0 if kind=='NORMAL' else 2)
                    for name in ['ForcedOffer','HasMadeVerbalDeal','IsCounterOffer','IsExistingOffer','IsUserInitiated']:
                        self.assertEqual(fields[name],0)

    def test_unsupported_or_implicit_terms_fail_before_any_native_calls(self):
        cases=[self.terms(signing_type='EXTENSION'),self.terms(contract_type='TEN_DAY'),self.terms(contract_type='TWO_WAY'),
            self.terms(distribution='FLAT'),self.terms(years_native=0),self.terms(years_native=7),self.terms(years_native=True),
            self.terms(years_native=1,option_type='TEAM_OPTION_2'),self.terms(annual_wages_native=[1,2,3,4,1,0]),
            self.terms(annual_wages_native=[0,2,3,4,0,0]),self.terms(annual_wages_native=[2**31,2,3,4,0,0]),
            self.terms(annual_wages_native=[True,2,3,4,0,0]),self.terms(no_trade_clause=1),self.terms(extra=1)]
        for terms in cases:
            with self.subTest(terms=terms):
                with self.assertRaises(ValueError):validate_fa_offer_contract(terms)
                result=self.simulate(self.parameters(contract=terms),compile=False)
                self.assertIsNotNone(result['error']);self.assertEqual(result['calls'],[])
        result=self.simulate(self.parameters(contract=None),compile=False)
        self.assertEqual(result['error'],'EXACT_SUPPORTED_FA_OFFER_TERMS_REQUIRED');self.assertFalse(result['calls'])

    def test_native_rejection_has_no_success_or_final_signing_claim(self):
        for options in [{'reject_no_record':True},{'reject_record':True}]:
            result=self.simulate(**options);self.assertIsNone(result['error']);self.assertEqual(result['offers'],1)
            self.assertEqual(result['messages'][0]['outcome'],'REJECTED_BY_GAME')
            self.assertFalse(result['messages'][0]['details']['signing_completed'])
        for options in [{'native_return':2},{'response_status':6},{'response_status':8},
                        {'native_return':0},{'reject_no_record':True,'native_return':1},
                        {'pool_terms_change':True},{'private_terms_change':True},{'duplicate_created':True}]:
            result=self.simulate(**options);self.assertIsNotNone(result['error'])
            self.assertEqual(result['offers'],1);self.assertFalse(result['messages']);self.assertEqual(result['forbiddenWrites'],0)

    def test_native_preconditions_fail_without_submission_or_backend_game_writes(self):
        cases=[{'period':29},{'period':20},{'rules':0},{'bad_delegate':True},{'bad_slot':True},
            {'invalid_tuning':True},{'null_root':'rules'},{'available_count':0},{'available_count':1001},
            {'pool_resolver_null':True},{'missing_member':True},{'duplicate_member':True},{'player_null':True},
            {'uid_mismatch':True},{'base_years':1},{'extension_years':1},{'default_type':1},{'full_pool':True},
            {'pool_changes_before':True},{'player_changes_before':True},{'period_changes_before':True}]
        for options in cases:
            with self.subTest(options=options):
                result=self.simulate(**options);self.assertIsNotNone(result['error']);self.assertEqual(result['offers'],0)
                self.assertEqual(result['forbiddenWrites'],0);self.assertFalse(result['messages'])

    def test_existing_offer_is_not_replaced_but_archived_or_qualifying_is_not_lookup_eligible(self):
        for archived,kind,blocked in [(0,2,True),(1,2,False),(0,3,False)]:
            raw=bytearray(44);struct.pack_into('<HH',raw,0,55,20)
            struct.pack_into('<I',raw,32,(1<<18)|(kind<<22));struct.pack_into('<I',raw,40,archived<<11)
            result=self.simulate(records=[{'index':5,'hex':raw.hex()}])
            self.assertEqual(result['offers'],0 if blocked else 1)
            if blocked:self.assertEqual(result['error'],'FRESH_OFFER_WOULD_REPLACE_EXISTING_RECORD')
            else:self.assertIsNone(result['error'])

    def test_postcall_context_or_contract_change_is_unknown_and_never_retried(self):
        for name in ['contract_changes_after','team_link_changes_after','directory_changes_after',
                     'period_changes_after','root_changes_after','delegate_changes_after']:
            result=self.simulate(**{name:True});self.assertIsNotNone(result['error']);self.assertEqual(result['offers'],1)
            self.assertFalse(result['messages']);self.assertEqual(result['forbiddenWrites'],0)

    def test_invalid_uid_or_fresh_template_rejected_in_private_constructor(self):
        for uid in [-1,65535,True]:
            with self.assertRaises(ValueError):encode_fresh_fa_offer(bytes(44),uid,20,self.terms())
        for template in [bytes(43),bytes(45),bytes.fromhex(self.simulate()['firstRecord'])]:
            with self.assertRaises(ValueError):encode_fresh_fa_offer(template,55,20,self.terms())


class OfferBatch(unittest.TestCase):
    def setUp(self):
        class Transport:
            def __init__(self):self.calls=[]
            def execute(self,script,**kwargs):self.calls.append(script);return {'outcome':'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED'}
        self.transport=Transport();self.service=RoleCapabilityService(control=NativeControlFacade(transport=self.transport))
        self.context=BatchContext('world','save','gen','season','FA_SIGNING_OFFERS','snapshot',self.service.version)
        self.gm=RoleCapabilityProfile('GM','gm20',(20,),'world','save','gen','season','FA_SIGNING_OFFERS','snapshot',frozenset({REQ}))
        self.profiles=[self.gm];self.grants={('gm20',REQ)}
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.journal=ExecutionJournal(self.temp.name)

    def intent(self,iid='offer',actor='gm20',team=20):
        return ActionIntent.decided(iid,actor,REQ,{'team_id':team,'player_id':55,'contract':FreeAgentOffer().terms()})

    def plan(self,*intents,batch='batch'):
        return ExecutionAggregator(self.service).plan(RoleActionBatch(batch,self.context,tuple(intents)),profiles=self.profiles,phase_grants=self.grants)

    def test_exact_authorized_offer_compiles_and_unverified_return_keeps_player_reservation(self):
        intent=self.intent();plan=self.plan(intent);self.assertFalse(plan.issues)
        self.assertIn('player/55',plan.actions[0].resources)
        dispatcher=NativeActionDispatcher(self.service,self.journal)
        result=dispatcher.dispatch(plan,pre_dispatch_context=lambda *_:None)
        self.assertEqual(result[0].outcome,'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED');self.assertEqual(len(self.transport.calls),1)
        again=dispatcher.dispatch(self.plan(self.intent('different'),batch='different'),pre_dispatch_context=lambda *_:None)
        self.assertEqual(again[0].outcome,'NOT_EXECUTED');self.assertEqual(len(self.transport.calls),1)
        self.assertIn('"annual_wages_native":[101,202,303,404,0,0]',self.transport.calls[0])

    def test_m0_offer_is_distinct_from_signing_and_requires_explicit_identity_permission(self):
        public=replace(self.gm,allowed_actions=frozenset())
        card=self.service.describe_action(REQ,public)
        self.assertTrue(card['call_logic_available']);self.assertFalse(card['identity_permission'])
        self.assertEqual(card['executor_action_id'],ACTION);self.assertNotIn('rva',str(card).lower())
        values=self.service.get_allowed_values(REQ,public)
        self.assertTrue(values['field_values']['contract']['maturity']['dispatch_implemented'])
        self.assertFalse(values['field_values']['contract']['maturity']['signing_completion_qualified'])
        schema=values['parameters']['contract']['properties']
        self.assertEqual(schema['contract_type']['enum'],['NORMAL','HARDSHIP'])
        self.assertEqual(schema['distribution']['enum'],['CUSTOM'])
        self.assertFalse(self.service.describe_action('GM.CONTRACT.FA_SIGN',self.gm)['call_logic_available'])
        self.assertFalse(self.service.registry.binding('sign.offer_contract').unknowns==())

    def test_host_scene_role_team_and_phase_grants_are_required(self):
        self.assertTrue(self.plan(self.intent(team=21)).issues)
        self.profiles=[replace(self.gm,role_type='PLAYER')];self.assertTrue(self.plan(self.intent()).issues)
        self.profiles=[replace(self.gm,phase='FA_SIGNING')];self.assertTrue(self.plan(self.intent()).issues)
        self.profiles=[self.gm];self.grants.clear();self.assertTrue(self.plan(self.intent()).issues)
        self.assertFalse(self.transport.calls)

    def test_competing_gms_must_resolve_same_player_offer_conflict(self):
        self.profiles.append(replace(self.gm,actor_uid='gm21',team_scope=(21,)))
        self.grants.add(('gm21',REQ))
        plan=self.plan(self.intent(),self.intent('other','gm21',21))
        self.assertTrue(any('CONFLICT_REQUIRES_ROLE_RESOLUTION' in issue for issue in plan.issues))
        self.assertFalse(self.transport.calls)


if __name__=='__main__':unittest.main()

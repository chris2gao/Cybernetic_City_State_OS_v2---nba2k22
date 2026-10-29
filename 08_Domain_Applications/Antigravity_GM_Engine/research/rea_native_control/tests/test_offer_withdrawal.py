"""Synthetic original cancellation service, fixed source retention and real batch boundaries."""
import copy,json,shutil,struct,subprocess,sys,tempfile,unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
CONTROL=Path(__file__).resolve().parents[1];sys.path.insert(0,str(CONTROL))
from contracts import NativeActionRequest
from facade import NativeControlFacade
from signing_fields import decode_record,validate_pending_offer
from role_capabilities import RoleCapabilityProfile,RoleCapabilityService,PLANNING
from role_batches import ActionIntent,BatchContext,ExecutionAggregator,ExecutionJournal,NativeActionDispatcher,RoleActionBatch
ACTION='CONTRACT_WITHDRAW_PENDING_OFFER';REQ='GM.CONTRACT.OFFER_WITHDRAW'

def record(*,player=55,team=20,status=1,type=2,archived=0):
    raw=bytearray(44);struct.pack_into('<HHI6I',raw,0,player,team,101,101,202,303,404,0,0)
    struct.pack_into('<I',raw,32,0xfb|(3<<8)|(1<<12)|(status<<18)|(type<<22)|(2<<28))
    raw[36:40]=bytes([9,8,7,6]);struct.pack_into('<I',raw,40,0xace00000|5|(4<<8)|(archived<<11))
    return bytes(raw)

def parameters():return {'team_id':20,'player_id':55,'expected_offer':decode_record(record())}

class OfferWithdrawal(unittest.TestCase):
    def setUp(self):self.facade=NativeControlFacade()

    def simulate(self,p=None,records=None,compile=True,**options):
        p=parameters() if p is None else p
        if compile:self.assertEqual(self.facade.render(NativeActionRequest(ACTION,p)).maximum_game_calls,3)
        bindings={row['binding_id']:self.facade.registry.binding(row['binding_id']).to_dict()
                  for row in self.facade.registry.get(ACTION)['call_sequence']}
        if records is None:records=[{'index':7,'hex':record().hex()},{'index':9,'hex':record(player=56,status=6).hex()}]
        done=subprocess.run([shutil.which('node'),str(CONTROL/'tests/offer_withdraw_harness.js'),str(CONTROL/'runtime/sign_withdraw_offer.js')],
            input=json.dumps({'request':{'parameters':p},'bindings':bindings,'records':records,'options':options}),
            text=True,capture_output=True,check=True,timeout=10)
        return json.loads(done.stdout)

    def test_actual_handler_clears_only_selected_status_preserving_every_other_byte(self):
        result=self.simulate();self.assertIsNone(result['error']);self.assertEqual(result['withdrawals'],1)
        self.assertEqual(len(result['calls']),3);self.assertEqual(result['forbiddenWrites'],0);self.assertEqual(result['poolReads'],3000)
        expected=bytearray(record());struct.pack_into('<I',expected,32,struct.unpack_from('<I',expected,32)[0]&~0x3c0000)
        self.assertEqual(result['selectedAfter'],expected.hex())
        details=result['messages'][0]['details'];self.assertTrue(details['withdrawal_only']);self.assertFalse(details['signing_completed'])
        self.assertTrue(details['observation']['other_pool_rows_unchanged']);self.assertEqual(details['observation']['status'],'EMPTY')

    def test_complete_expected_fields_and_exact_pending_identity_are_required(self):
        bad=[]
        for name,value in [('Status',6),('Status',0),('Type',1),('IsArchived',1),('PlayerId',56),('TeamId',21),('PissedOffLevel',128),('Wage',-1),('Years',True),('ForcedWage',[1])]:
            p=parameters();p['expected_offer'][name]=value;bad.append(p)
        p=parameters();del p['expected_offer']['IntCity'];bad.append(p)
        p=parameters();p['expected_offer']['extra']=1;bad.append(p)
        for p in bad:
            with self.subTest(p=p):
                with self.assertRaises(ValueError):validate_pending_offer(p)
                result=self.simulate(p,compile=False);self.assertIsNotNone(result['error']);self.assertFalse(result['calls'])
        for value in [-1,65535,True]:
            p=parameters();p['team_id']=value
            with self.assertRaises(ValueError):validate_pending_offer(p)

    def test_stale_offer_and_duplicate_identity_cannot_choose_an_alternative(self):
        stale=bytearray(record());stale[36]^=1
        for rows in [[],[{'index':7,'hex':stale.hex()}],
            [{'index':7,'hex':record().hex()},{'index':8,'hex':record(status=4).hex()}]]:
            result=self.simulate(records=rows);self.assertIsNotNone(result['error']);self.assertEqual(result['withdrawals'],0)
        result=self.simulate(records=[{'index':7,'hex':record().hex()},{'index':8,'hex':record(archived=1).hex()},
                                    {'index':10,'hex':record(type=3).hex()}])
        self.assertIsNone(result['error']);self.assertEqual(result['withdrawals'],1)

    def test_current_native_scene_identity_and_preflight_brackets_stop_before_mutation(self):
        for options in [{'period':29},{'null_pool':True},{'null_period':True},{'player_null':True},
            {'uid_mismatch':True},{'team_missing':True},{'team_changes':True},{'period_changes_before':True},
            {'pool_changes_before':True},{'player_changes_before':True}]:
            with self.subTest(options=options):
                result=self.simulate(**options);self.assertIsNotNone(result['error']);self.assertEqual(result['withdrawals'],0)
                self.assertEqual(result['forbiddenWrites'],0);self.assertFalse(result['messages'])

    def test_unexpected_return_or_any_extra_effect_is_unknown_after_one_call(self):
        for options in [{'native_return':0},{'native_return':2},{'no_effect':True},{'wrong_row':True},
            {'wrong_status':True},{'terms_change_after':True},{'other_record_change_after':True},
            {'player_changes_after':True},{'root_changes_after':True},{'period_changes_after':True}]:
            with self.subTest(options=options):
                result=self.simulate(**options);self.assertIsNotNone(result['error']);self.assertEqual(result['withdrawals'],1)
                self.assertFalse(result['messages']);self.assertEqual(result['forbiddenWrites'],0)

class WithdrawalCatalogAndBatch(unittest.TestCase):
    def setUp(self):
        class Transport:
            def __init__(self):self.calls=[]
            def execute(self,script,**kwargs):self.calls.append(script);return {'outcome':'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED'}
        self.transport=Transport();self.service=RoleCapabilityService(control=NativeControlFacade(transport=self.transport))
        self.context=BatchContext('world','save','gen','season','FA_SIGNING_OFFERS','snapshot',self.service.version)
        self.gm=RoleCapabilityProfile('GM','gm20',(20,),'world','save','gen','season','FA_SIGNING_OFFERS','snapshot',frozenset({REQ,'GM.CONTRACT.CONTRACT_OFFER'}))
        self.profiles=[self.gm];self.grants={('gm20',REQ),('gm20','GM.CONTRACT.CONTRACT_OFFER')}

    def intent(self,iid='withdraw',p=None):return ActionIntent.decided(iid,'gm20',REQ,parameters() if p is None else p)

    def plan(self,*intents,batch='batch'):
        return ExecutionAggregator(self.service).plan(RoleActionBatch(batch,self.context,tuple(intents)),profiles=self.profiles,phase_grants=self.grants)

    def test_discovered_requirement_is_additive_and_all_original_objects_remain_identical(self):
        source=json.loads((PLANNING/'三角色及世界控制_原子操作目录_v1.json').read_text(encoding='utf8'))['operations']
        self.assertEqual(len(source),183);self.assertEqual(set(self.service.requirements)-{row['id'] for row in source},{REQ})
        for row in source:self.assertEqual(self.service.requirements[row['id']],row)
        card=self.service.describe_action(REQ,replace(self.gm,allowed_actions=frozenset()))
        self.assertTrue(card['call_logic_available']);self.assertFalse(card['identity_permission'])
        def inspect(value):
            if isinstance(value,dict):
                for key,item in value.items():
                    self.assertFalse(key.lower()=='rva' or key.lower().endswith('_rva'))
                    inspect(item)
            elif isinstance(value,list):
                for item in value:inspect(item)
        inspect(card);self.assertNotRegex(json.dumps(card),r'(?i)0x[0-9a-f]{6,}')
        self.assertEqual(card['requirement_origin'],'NATIVE_DISCOVERY_SUPPLEMENT')
        self.assertFalse(self.service.describe_action('GM.CONTRACT.OFFER_ACCEPT_OR_REJECT',self.gm)['call_logic_available'])
        self.assertFalse(self.service.describe_action('GM.CONTRACT.FA_SIGN',self.gm)['call_logic_available'])

    def test_supplement_cannot_replace_original_or_duplicate_discovered_identity(self):
        path=CONTROL/'data/supplemental_requirements.json';original=Path.read_text
        for mode in ('replace','duplicate','wrong_baseline'):
            bad=json.loads(original(path,encoding='utf8'))
            if mode=='replace':bad['operations'][0]['id']='GM.CONTRACT.CONTRACT_OFFER'
            elif mode=='duplicate':bad['operations'].append(copy.deepcopy(bad['operations'][0]))
            else:bad['source_baseline_requirement_count']=184
            def altered(p,*args,**kwargs):return json.dumps(bad) if p==path else original(p,*args,**kwargs)
            with patch.object(Path,'read_text',altered):
                with self.assertRaises(ValueError):RoleCapabilityService()

    def test_wrong_role_scene_team_and_missing_grant_do_not_dispatch(self):
        p=parameters();p['team_id']=21;self.assertTrue(self.plan(self.intent(p=p)).issues)
        for profile in [replace(self.gm,role_type='PLAYER'),replace(self.gm,phase='REGULAR_SEASON')]:
            self.profiles=[profile];self.assertTrue(self.plan(self.intent()).issues)
        self.profiles=[self.gm];self.grants.clear();self.assertTrue(self.plan(self.intent()).issues)
        self.assertFalse(self.transport.calls)

    def test_withdraw_and_new_offer_share_player_conflict_and_no_automatic_replacement(self):
        from test_fa_offer import FreeAgentOffer
        submit=ActionIntent.decided('submit','gm20','GM.CONTRACT.CONTRACT_OFFER',{'team_id':20,'player_id':55,'contract':FreeAgentOffer().terms()})
        plan=self.plan(self.intent(),submit)
        self.assertTrue(any('CONFLICT_REQUIRES_ROLE_RESOLUTION' in issue for issue in plan.issues));self.assertFalse(self.transport.calls)

    def test_unverified_withdrawal_reserves_resource_across_new_ids(self):
        plan=self.plan(self.intent());self.assertFalse(plan.issues)
        with tempfile.TemporaryDirectory() as directory:
            dispatcher=NativeActionDispatcher(self.service,ExecutionJournal(directory))
            result=dispatcher.dispatch(plan,pre_dispatch_context=lambda *_:None)
            self.assertEqual(result[0].outcome,'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED');self.assertEqual(len(self.transport.calls),1)
            again=dispatcher.dispatch(self.plan(self.intent('new'),batch='new'),pre_dispatch_context=lambda *_:None)
            self.assertEqual(again[0].outcome,'NOT_EXECUTED');self.assertEqual(len(self.transport.calls),1)

if __name__=='__main__':unittest.main()

import json,shutil,struct,subprocess,sys,unittest
from pathlib import Path
CONTROL=Path(__file__).resolve().parents[1];ROOT=CONTROL.parents[3]
RUN=ROOT/'01_os/07_content/_runs/run-20261028-role-native-execution-system-001'
sys.path.insert(0,str(CONTROL))
from contracts import NativeActionRequest,Outcome
from facade import NativeControlFacade
from readers import NativeReadFacade,NativeReadQuery,NativeReadCatalog
from role_capabilities import RoleCapabilityService
ACTION='READ_PLAYER_CONTRACT_STATE';DATASET='player.contract_state'

class PlayerContractRead(unittest.TestCase):
 def setUp(self):self.control=NativeControlFacade()
 def fixture(self,base=2,extension=2,option=3,uid=55,upper=True):
  raw=bytearray(1264);struct.pack_into('<H',raw,0xf4,uid)
  for index in range(6):struct.pack_into('<I',raw,0x1a4+index*4,101+index+(0x80000000 if upper else 0))
  struct.pack_into('<I',raw,0x32c,base<<18);struct.pack_into('<I',raw,0x340,extension<<15)
  struct.pack_into('<I',raw,0x314,option<<28);struct.pack_into('<I',raw,0x130,0x600)
  return bytes(raw)
 def simulate(self,raw=None,query=None,compile=True,action=ACTION,**options):
  p={'player_id':55} if query is None else query
  if compile:self.control.render(NativeActionRequest(action,p))
  bindings={step['binding_id']:self.control.registry.binding(step['binding_id']).to_dict()
    for step in self.control.registry.get(action)['call_sequence']}
  script='read_player_contract.js' if action==ACTION else 'read_player.js'
  fields=json.loads((CONTROL/'data/player_contract_fields.json').read_text(encoding='utf8'))['fields']
  result=subprocess.run([shutil.which('node'),str(CONTROL/'tests/player_contract_harness.js'),str(CONTROL/'runtime'/script)],
   input=json.dumps({'request':{'action_id':action,'parameters':p},'bindings':bindings,'player_hex':(raw or self.fixture()).hex(),'options':options,'contract_fields':fields}),
   text=True,capture_output=True,check=True,timeout=10)
  return json.loads(result.stdout)
 def test_six_original_salaries_mask_upper_flag_and_both_year_getters_include_extension(self):
  result=self.simulate();self.assertIsNone(result['error']);self.assertTrue(result['unchanged'])
  data=result['messages'][0]['details']['data'];self.assertEqual(data['wages_native'],list(range(101,107)))
  self.assertEqual(data['contract_raw']['years_left_on_contract'],2)
  self.assertEqual(data['remaining_years']['without_options']['value'],4)
  self.assertEqual(data['remaining_years']['with_options']['value'],6)
  self.assertEqual(data['option'],{'value':3,'name':'TEAM_OPTION_2','year_count':2})
  self.assertEqual(len(result['calls']),10)
  self.assertEqual([row['args'][-1] for row in result['calls'] if row['binding']=='player.get_salary'],list(range(6)))
 def test_fifth_base_year_bit_is_preserved_and_unsafe_assertion_getters_are_skipped(self):
  result=self.simulate(self.fixture(base=17,extension=0,option=0));self.assertIsNone(result['error'])
  data=result['messages'][0]['details']['data'];self.assertEqual(data['contract_raw']['years_left_on_contract'],17)
  for row in data['remaining_years'].values():self.assertEqual(row,{'value':None,'status':'BLOCKED_NATIVE_ASSERTION_SUM_GT6'})
  self.assertFalse(any(row['binding']=='player.get_remaining_contract_years' for row in result['calls']))
 def test_each_option_count_and_per_flag_assertion_guard_are_exact(self):
  for option,count in enumerate([0,1,1,2]):
   result=self.simulate(self.fixture(base=3,extension=0,option=option));self.assertIsNone(result['error'])
   self.assertEqual(result['messages'][0]['details']['data']['remaining_years']['with_options']['value'],3+count)
  result=self.simulate(self.fixture(base=6,extension=0,option=1));self.assertIsNone(result['error'])
  years=result['messages'][0]['details']['data']['remaining_years']
  self.assertEqual(years['without_options']['value'],6);self.assertIsNone(years['with_options']['value'])
  self.assertEqual(len(result['calls']),9)
 def test_contract_getter_disagreement_or_selected_context_changes_emit_no_snapshot(self):
  for options in ({'wrong_salary':True},{'wrong_years':True},{'salary_changes':True},{'mark_changes':True},
   {'changed_identity':True},{'team_id_changes':True},{'missing':True}):
   result=self.simulate(**options);self.assertIsNotNone(result['error'],options);self.assertFalse(result['messages'])
  result=self.simulate(self.fixture(uid=56));self.assertEqual(result['error'],'PLAYER_UID_RESOLUTION_MISMATCH')
  self.assertEqual(len(result['calls']),1)
 def test_null_team_links_are_explicit_and_unrelated_stat_change_does_not_fake_contract_change(self):
  result=self.simulate(no_current=True,no_owner=True,unrelated_changes=True);self.assertIsNone(result['error'])
  data=result['messages'][0]['details']['data'];self.assertIsNone(data['current_team_id']);self.assertIsNone(data['contract_team_id'])
  self.assertFalse(result['messages'][0]['details']['arbitrary_memory_dump_emitted']);self.assertNotIn('potential',json.dumps(data).lower())
 def test_exact_query_and_inert_reader_have_a_ten_call_maximum(self):
  program=self.control.render(NativeActionRequest(ACTION,{'player_id':55}));self.assertEqual(program.maximum_game_calls,10)
  self.assertEqual(NativeReadFacade(self.control).read(NativeReadQuery(DATASET,{'player_id':55})).outcome,Outcome.PREPARED)
  self.assertEqual(len(NativeReadCatalog().list()),15)
  for p in ({},{'player_id':True},{'player_id':65535},{'player_id':55,'all':1}):
   with self.assertRaises((ValueError,TypeError)):self.control.render(NativeActionRequest(ACTION,p))
   result=self.simulate(query=p,compile=False);self.assertIsNotNone(result['error']);self.assertFalse(result['calls'])
 def test_native_dispatch_evidence_matches_all_six_registered_salary_offsets(self):
  source=json.loads((RUN/'static/player_contract_native_readback_021.json').read_text(encoding='utf8'))
  self.assertFalse(source['game_access']);self.assertEqual(source['salary_semantics']['stored_value_bits'],31)
  for kind in ('getter','setter'):
   self.assertEqual([row['player_offset'] for row in source['salary_dispatch'][kind]['cases']],list(range(0x1a4,0x1bc,4)))
  layout=self.control.registry.binding('player.contract_read_context').input_layout
  self.assertEqual(next(row for row in layout['fields'] if row['name']=='years_left_on_contract')['bits'],5)
  profile=json.loads((CONTROL.parents[1]/'config/memory_field_profile.json').read_text(encoding='utf8'))
  self.assertEqual(next(row for row in profile['fields']['PLAYER'] if row['name']=='years_left_on_contract')['bits'],4)
  original=self.control.render(NativeActionRequest('READ_PLAYER_PROFILE_ATTRIBUTES_TENDENCIES_BADGES',{'player_id':55}))
  self.assertIn('"bits":5',original.script)
 def test_action_never_calls_salary_setter_option_processor_or_signer(self):
  action=self.control.registry.get(ACTION);ids={row['binding_id'] for row in action['call_sequence']}
  self.assertEqual(ids,{'player.by_id','player.contract_read_context','player.get_salary','player.get_remaining_contract_years'})
  self.assertIsNone(self.control.registry.get('SIGN_FREE_AGENT')['runtime_handler'])
  self.assertIsNone(self.control.registry.get('CONTRACT_OPTION_ACTION')['runtime_handler'])
  self.assertTrue(self.control.registry.binding('sign.process_options').unknowns)
  self.assertIn('player_contract_fields',Path(CONTROL/'role_capabilities.py').read_text(encoding='utf8'))
 def test_existing_profile_handler_uses_the_corrected_raw_width_without_new_capture_or_mutation(self):
  result=self.simulate(self.fixture(base=17,extension=0,option=0),action='READ_PLAYER_PROFILE_ATTRIBUTES_TENDENCIES_BADGES')
  self.assertIsNone(result['error']);self.assertTrue(result['unchanged'])
  self.assertEqual(result['messages'][0]['details']['data']['contract_raw']['years_left_on_contract'],17)
  self.assertEqual(len(result['calls']),1)

if __name__=='__main__':unittest.main()

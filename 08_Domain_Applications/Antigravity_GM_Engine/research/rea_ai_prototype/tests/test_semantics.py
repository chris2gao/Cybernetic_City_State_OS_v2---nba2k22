import importlib.util,json,sys,tempfile,unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prototype import Intent,KnowledgeStore,NativeBackend,OwnedFixture,Router,ValidatedMemoryBackend,decode_gameplan_index,fixture_intent,provenance_summary

class SemanticTests(unittest.TestCase):
 def test_PROTO_N01_cross_mode_badges_rejected(self):
  with self.assertRaisesRegex(ValueError,'GAME_MODE'):KnowledgeStore().show('AI_BADGE_NATURAL_GROWTH','PLAYER','MYCAREER')
 def test_PROTO_N02_layout_does_not_qualify_executor(self):
  card=KnowledgeStore().show('AI_BADGE_NATURAL_GROWTH','PLAYER');self.assertEqual(card['proof_level'],'L1_NATIVE_TYPE_OR_INSTANCE');self.assertFalse(card['can_execute']);self.assertTrue(card['unknowns'])
 def test_PROTO_N03_stored_value_is_not_game_application(self):
  card=KnowledgeStore().show('AI_COACH_DEFENSE_M1','COACH');self.assertFalse(card['can_execute']);self.assertIn('UNKNOWN',card['original_game_rule'])
 def test_PROTO_N04_human_trade_excluded(self):
  value={'action_id':'t','action_type':'GM_AI_AI_TRADE','initiator':{'id':'gm:A','role':'GM','engine_control':'AI_CONTROLLED'},'counterparty':{'id':'gm:B','role':'GM','engine_control':'HUMAN_CONTROLLED'},'environment':'REAL_GAME','build':'unknown','mode':'PC22_OFFLINE_MYLEAGUE','save_id':'s','scene_id':'x','target_ids':['A','B'],'arguments':{'player_ids':[],'pick_ids':[]},'expected_revision':0}
  receipt=Router().act(Intent.parse(value));self.assertIn('HUMAN_ONLY_EXCLUDED',receipt['reasons']);self.assertEqual(receipt['operation_count'],0)
 def test_PROTO_N05_engine_control_not_external_persona(self):
  actor={'id':'coach:A','role':'COACH','engine_control':'HUMAN_CONTROLLED'}
  self.assertIn('CONTROL_FLAG_CONFLICT',Router(OwnedFixture()).act(fixture_intent(initiator=actor))['reasons'])
 def test_PROTO_N06_old_memory_reference_cannot_execute_game(self):
  receipt=Router().act(fixture_intent(environment='REAL_GAME',permission_ref=None));self.assertEqual(receipt['route'],'NO_SAFE_PATH');self.assertEqual(receipt['operation_count'],0)
 def test_PROTO_N07_fixture_does_not_promote_game_level(self):
  r=Router(OwnedFixture()).act(fixture_intent());self.assertFalse(r['game_target']);self.assertEqual(r['game_proof_level'],'NOT_PROMOTED');self.assertEqual(r['result'],'FIXTURE_ONLY_PASS')
 def test_PROTO_N08_side_effect_contract_mismatch_blocks_before_call(self):
  native=NativeBackend(True);memory=ValidatedMemoryBackend(True,fault='extra_effect_contract');r=Router(OwnedFixture(),native,memory).act(fixture_intent())
  self.assertIn('BACKEND_SEMANTIC_CONTRACT_MISMATCH',r['reasons']);self.assertEqual(native.calls+memory.calls,0)
 def test_PROTO_N09_knowledge_available_while_no_backend(self):
  self.assertTrue(KnowledgeStore().show('AI_COACH_DEFENSE_M1','COACH')['can_reason']);r=Router(OwnedFixture(),NativeBackend(False),ValidatedMemoryBackend(False)).act(fixture_intent());self.assertEqual(r['route'],'NO_SAFE_PATH')
 def test_PROTO_N10_success_return_but_readback_mismatch(self):
  r=Router(OwnedFixture(),memory=ValidatedMemoryBackend(True,fault='missing_cache')).act(fixture_intent());self.assertTrue(r['returned']['returned_success']);self.assertEqual(r['result'],'FAILED_READBACK')
 def test_PROTO_N11_missing_real_permission_no_adapter_or_operation(self):
  native=NativeBackend(True,environment='REAL_GAME');memory=ValidatedMemoryBackend(True,environment='REAL_GAME');r=Router(None,native,memory).act(fixture_intent(environment='REAL_GAME',permission_ref=None))
  self.assertIn('MISSING_EXACT_ACTION_AUTHORIZATION',r['reasons']);self.assertEqual(native.calls+memory.calls,0)
 def test_PROTO_N12_role_projection_hides_internal_data(self):
  card=KnowledgeStore().show('AI_COACH_DEFENSE_M1','COACH');self.assertNotIn('internal_native_research',card)
  with self.assertRaises(PermissionError):KnowledgeStore().show('AI_AI_GM_TRADE','PLAYER')
 def test_PROTO_N13_trade_requires_complete_effects_not_player_id_only(self):
  card=KnowledgeStore().show('AI_AI_GM_TRADE','GM');self.assertFalse(card['can_execute']);self.assertIn('薪资',card['field_semantics'][0]['meaning']);self.assertIn('选秀权',card['field_semantics'][0]['meaning'])
 def test_PROTO_N14_same_origin_is_not_independence(self):
  store=KnowledgeStore();a=store.sources['SRC-PRIOR-METADATA'];b=store.sources['SRC-PRIOR-GROWTH'];result=provenance_summary([a,b]);self.assertEqual(result['classification'],'SINGLE_ORIGIN');self.assertEqual(result['origin_count'],1);self.assertFalse(result['independent_AI_game_confirmation'])
 def test_EXTRA_shared_word_neighbors_preserved_and_bad_writer_rejected(self):
  fixture=OwnedFixture();before=fixture.snapshot()['coaches']['A']['poe_word'];r=Router(fixture).act(fixture_intent());self.assertEqual(r['fresh_readback']['coaches']['A']['poe_word']&~31,before&~31)
  bad=Router(OwnedFixture(),memory=ValidatedMemoryBackend(True,fault='whole_word')).act(fixture_intent());self.assertEqual(bad['result'],'FAILED_READBACK')
 def test_EXTRA_stale_plan_rejected_without_effect(self):
  f=OwnedFixture();r=Router(f).act(fixture_intent(expected_revision=0));self.assertIn('STALE_PLAN',r['reasons']);self.assertEqual(f.operations,[])
 def test_native_first_is_fixture_model_only(self):
  native=NativeBackend(True);memory=ValidatedMemoryBackend(True);r=Router(OwnedFixture(),native,memory).act(fixture_intent());self.assertEqual(r['route'],'NATIVE_FIXTURE_MODEL');self.assertEqual((native.calls,memory.calls),(1,0));self.assertFalse(r['game_target'])
 def test_equal_fixture_business_poststates(self):
  a=Router(OwnedFixture(),NativeBackend(True)).act(fixture_intent());b=Router(OwnedFixture()).act(fixture_intent());self.assertEqual(a['fresh_readback'],b['fresh_readback'])
 def test_partial_native_failure_never_retries_memory(self):
  native=NativeBackend(True,fault='after_write');memory=ValidatedMemoryBackend(True);r=Router(OwnedFixture(),native,memory).act(fixture_intent());self.assertEqual(r['result'],'EXECUTED_BUT_UNVERIFIED');self.assertEqual(memory.calls,0)
 def test_extra_unrelated_object_write_detected(self):
  r=Router(OwnedFixture(),memory=ValidatedMemoryBackend(True,fault='unrelated_team')).act(fixture_intent());self.assertEqual(r['result'],'FAILED_READBACK');self.assertIn('/coaches/B/poe_word',r['affected_set_comparison']['unexpected_differences'])
 def test_assessment_never_executes(self):
  f=OwnedFixture();r=Router(f).assess(fixture_intent());self.assertEqual(r['result'],'ASSESSMENT_ONLY');self.assertEqual(f.operations,[])
 def test_build_scene_identity_and_authority_guards(self):
  for kwargs in ({'build':'wrong'},{'scene_id':'wrong'},{'save_id':'wrong'},{'target_ids':['coach:B']},{'permission_ref':None}):
   f=OwnedFixture();r=Router(f).act(fixture_intent(**kwargs));self.assertEqual(r['result'],'NOT_EXECUTED');self.assertEqual(f.operations,[])
 def test_untrusted_intent_no_pointer_or_qualification_fields(self):
  for kwargs in ({'address':'0x1234'},{'qualified':True},{'expected_revision':True},{'arguments':{'focus':'PROTECT_PAINT','pointer':123}}):
   with self.assertRaises(ValueError):fixture_intent(**kwargs)
 def test_REAL_PROJECT_CODEC_shared_word_and_staleness(self):
  root=Path(__file__).resolve().parents[3]
  spec=importlib.util.spec_from_file_location('legacy_pure_coach_codec',root/'src/coach_codec.py');codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
  profile=codec.load_profile();raw=bytearray(0x160);original=0x80000000|14|(1<<15);raw[316:320]=original.to_bytes(4,'little')
  patches=codec.encode_changes(bytes(raw),[{'field':'POEDefense','before_raw':14,'after_raw':13}],profile)
  self.assertEqual(len(patches),1);after=int.from_bytes(bytes.fromhex(patches[0]['after']),'little');self.assertEqual(after&~31,original&~31);self.assertEqual(after&31,13)
  with self.assertRaisesRegex(ValueError,'STALE_FIELD_VALUE'):codec.encode_changes(bytes(raw),[{'field':'POEDefense','before_raw':15,'after_raw':13}],profile)
 def test_EXTRA_STATIC_gameplan_zero_and_FF_sentinel(self):
  self.assertEqual(decode_gameplan_index(0),0);self.assertEqual(decode_gameplan_index(34),34);self.assertIsNone(decode_gameplan_index(255))
  for value in (35,254,-1,True):
   with self.assertRaises(ValueError):decode_gameplan_index(value)
 def test_unsupported_claim_cannot_promote_layout_to_L3(self):
  cards=deepcopy(KnowledgeStore().cards);cards[0]['proof_level']='L3_SAME_MODE_GAME_BEHAVIOR'
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'cards.json';path.write_text(json.dumps(cards),encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'UNSUPPORTED_MATURITY_PROMOTION'):KnowledgeStore(path).show(cards[0]['mechanism_id'],'COACH')
 def test_backend_interface_cannot_self_qualify_real_game(self):
  self.assertFalse(NativeBackend(True,'REAL_GAME').capability.qualified);self.assertFalse(ValidatedMemoryBackend(True,'REAL_GAME').capability.qualified)

if __name__=='__main__':unittest.main()

import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from native_action import NativeActionRequest,NativeActionReceipt,Status,encode_input_from_coach,expected_word
from invoker import NativeActionInvoker
class NativeContractTests(unittest.TestCase):
 def test_untyped_address_bool_and_wrong_domain_rejected(self):
  good=dict(action_id='C1-SET-POE-DEFENSE',team_id=20,defense=13,expected_before=14)
  self.assertEqual(NativeActionRequest.parse(good).defense,13)
  for data in [good|{'address':123},good|{'defense':True},good|{'defense':12},good|{'defense':14}]:
   with self.assertRaises(ValueError):NativeActionRequest.parse(data)
 def test_full_projection_marshaling_preserves_non_target_coach_bits(self):
  coach=bytearray(352);word=0xc0000000|14|(17<<5)|(20<<10)|(5<<15)|(8<<20)|(11<<25);coach[316:320]=word.to_bytes(4,'little')
  coach[0x148:0x14c]=(50<<17).to_bytes(4,'little');coach[0xe0]=90;coach[0x138]=100
  plan=bytes([0xa5])*880;out=encode_input_from_coach(plan,coach,13)
  self.assertEqual(list(out[0x17e:0x184]),[5,8,11,13,17,20]);self.assertEqual(out[0x184],50);self.assertEqual(out[0x185],90);self.assertEqual(out[0x188],100)
  changed=sum(((out[o]&31)<<s) for o,s in zip(range(0x17e,0x184),(15,20,25,0,5,10)))|(word&0xc0000000)
  self.assertEqual(changed,expected_word(word,13));self.assertEqual(out[:0x178],plan[:0x178]);self.assertEqual(out[0x18c:],plan[0x18c:])
 def test_non_null_playbook_requires_different_call_context(self):
  coach=bytearray(352);coach[0x120]=1
  with self.assertRaises(ValueError):encode_input_from_coach(bytes(880),coach,13)
 def test_fixture_or_unverified_receipt_cannot_be_real_game_success(self):
  for source,calls,effect in [('OWNED_FIXTURE',1,True),('REAL_GAME',0,True),('REAL_GAME',1,False)]:
   with self.assertRaises(ValueError):NativeActionReceipt(Status.VERIFIED,'C1','%s'%source,1,calls,effect)
 def test_mismatched_approval_never_reaches_process_launch(self):
  with tempfile.TemporaryDirectory() as td:
   path=Path(td);(path/'probe.js').write_text('throw Error("no execution");');(path/'approval.json').write_text(json.dumps({'Human_scope_approval':'APPROVED','experiment_id':'EXP-NATIVE-ACTION-01','script_sha256':'wrong','native_call_budget':3}))
   with self.assertRaises(PermissionError):NativeActionInvoker(path/'probe.js',path/'approval.json')
 def test_consumed_exact_approval_cannot_be_replayed(self):
  with tempfile.TemporaryDirectory() as td:
   path=Path(td);script=b'// exact script';(path/'probe.js').write_bytes(script)
   (path/'approval.json').write_text(json.dumps({'Human_scope_approval':'APPROVED','experiment_id':'EXP-NATIVE-ACTION-01','script_sha256':hashlib.sha256(script).hexdigest(),'native_call_budget':3,'execution_status':'CONSUMED'}))
   with self.assertRaises(PermissionError):NativeActionInvoker(path/'probe.js',path/'approval.json')
if __name__=='__main__':unittest.main()

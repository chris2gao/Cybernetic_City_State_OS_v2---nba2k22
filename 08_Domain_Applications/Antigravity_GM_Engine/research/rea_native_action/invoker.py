"""Actual REA/Frida execution orchestration with exact-script approval binding."""
import hashlib,json,subprocess
from pathlib import Path
class NativeActionInvoker:
 def __init__(self,script,approval_receipt):
  self.script=Path(script).resolve();self.approval=Path(approval_receipt).resolve()
  approved=json.loads(self.approval.read_text(encoding='utf-8-sig'))
  sha=hashlib.sha256(self.script.read_bytes()).hexdigest()
  if approved.get('execution_status')=='CONSUMED':raise PermissionError('bounded approval already consumed; no replay')
  if approved.get('Human_scope_approval')!='APPROVED' or approved.get('experiment_id')!='EXP-NATIVE-ACTION-01' or approved.get('script_sha256')!=sha or approved.get('native_call_budget')!=3:raise PermissionError('exact bounded Human approval missing or mismatched')
 def execute(self,output):
  output=Path(output).resolve()
  if (output/'evidence.json').exists():raise FileExistsError('fresh invocation output required')
  runner=Path(__file__).with_name('run_rea_admin.ps1')
  # -File carries a saved script. No game pointers or secrets enter the shell.
  arguments=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(runner),'-Script',str(self.script),'-Output',str(output),'-DurationMs','2600','-ApprovalReceipt',str(self.approval)]
  subprocess.run(arguments,check=True)
  return self.read_receipt(output)
 @staticmethod
 def read_receipt(output):
  evidence=json.loads((Path(output)/'evidence.json').read_text(encoding='utf-8-sig'));result=evidence['normalized_result']
  if result.get('cleanup_error') is not None or any(m['type']=='error' for m in result['messages']):raise RuntimeError('REA script/cleanup failure; native effect not established')
  receipts=[m['payload'] for m in result['messages'] if m['type']=='send' and m['payload'].get('kind')=='native-action-poc-receipt']
  if len(receipts)!=1:raise RuntimeError('one actual native-action receipt required')
  receipt=receipts[0]
  if receipt['status']=='REAL_GAME_EFFECT_VERIFIED':
   checks=receipt.get('checkpoints',[])
   if receipt.get('source_kind')!='REAL_GAME' or receipt.get('game_target_calls')!=2 or receipt.get('first_hand_native_calls')!=3 or len(checks)!=4 or not all(all(c.get(k) is True for k in ('full_coach_matches_expected','original_gameplan_unchanged','manager_flags_unchanged','comparison_team_unchanged','fresh_binding')) for c in checks) or [c['actual_defense'] for c in checks]!=[13,13,14,14] or receipt.get('delayed_restoration_stable') is not True:raise RuntimeError('claimed real native effect lacks required readback evidence')
  return {'evidence_id':evidence['evidence_id'],'receipt':receipt}

import copy,json,sys,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from native_trade import reconcile_trade_observations
from invoker import NativeActionInvoker
def observation(tag):
 d=json.loads((root/'evidence/live'/tag/'evidence.json').read_text(encoding='utf-8-sig'));return next(m['payload'] for m in d['normalized_result']['messages'] if m['type']=='send')
class TradeEvidenceTests(unittest.TestCase):
 def test_half_swap_duplicate_or_wrong_contract_cannot_pass_reconciliation(self):
  before=observation('trade-restarted-before');after=observation('trade-independent-after')
  for kind in ('half_swap','duplicate','contract','reciprocal_link'):
   broken=copy.deepcopy(after);team=next(t for t in broken['teams'] if t['team_id']==1);gill=next(p for p in team['players'] if p['unique_id']==9879)
   if kind=='half_swap':gill['unique_id']=9842
   elif kind=='duplicate':team['players'].append(copy.deepcopy(gill))
   elif kind=='contract':gill['contract']['contract_year_1']+=1
   else:gill['contract_team_matches']=False
   self.assertFalse(all(reconcile_trade_observations(before,broken).values()),kind)
 def test_zero_exit_without_native_receipt_is_not_native_return_success(self):
  with self.assertRaisesRegex(RuntimeError,'receipt required'):NativeActionInvoker.read_receipt(root/'evidence/live/trade-swap-attempt')
if __name__=='__main__':unittest.main()

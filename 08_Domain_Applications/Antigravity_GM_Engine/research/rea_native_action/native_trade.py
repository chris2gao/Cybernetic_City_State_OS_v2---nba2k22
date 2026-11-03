"""Bounded C4 contract and pure reconciliation, separate from native execution."""
from dataclasses import asdict,dataclass
from native_action import BUILD
@dataclass(frozen=True)
class NativeTradeSpec:
 action_id:str='C4-NATIVE-ONE-FOR-ONE-TRADE'
 game_build_sha256:str=BUILD
 mode:str='PC22_OFFLINE_MYLEAGUE_ISOLATED_RECOVERABLE_TEST_SAVE'
 add_player_rva:int=19786784
 validate_rva:int=19843376
 full_check_rva:int=19798016
 commit_wrapper_rva:int=20101184
 process_rva:int=19829680
 abi:str='win64'
 proposal_bytes:int=1668
 element_bytes:int=92
 element_limit:int=18
 signature:str='int Add(TRADE*,TEAM* from,TEAM* to,PLAYER*); int Validate(TRADE*); int Wrapper(TRADE*,int32* optional_output)'
 full_check_signature:str='int Check(TRADE*,bool current_team_in_trade,context*,int enable_checks,int zero,int32* output)'
 thread_model:str='FRESH_GAME_WINDOW_THREAD_PEEKMESSAGEA_ONLEAVE_ONCE'
 control_scope:str='IsAIInitiated is an input bit; do not infer original autonomous AI caller or engine-controller ownership'
 qualification:str='Pinned build/code; fresh player UID/name, reciprocal current/contract team and roster membership; identical eligible contracts; private native full Check succeeded; context and lifecycle ready'
 lifetime:str='Private 1668-byte proposal plus canaries retained through synchronous native wrapper return; game-owned objects are freshly resolved'
 result_semantics:str='Wrapper0 after Check1 and Process1; missing instrumentation receipt remains UNKNOWN and requires independent readback before any retry'
 rollback:str='No automatic second transaction or direct-memory rollback; preserve evidence and reload recoverable test save only if Human chooses'
 production_replacement_qualified:bool=False
 def to_dict(self):return asdict(self)

def reconcile_trade_observations(before,after):
 """Return data invariants only. This pure function cannot assert live execution."""
 checks={};expected={1:(9842,9879),2:(9879,9842)}
 for team,(outgoing,incoming) in expected.items():
  b=next(t for t in before['teams'] if t['team_id']==team);a=next(t for t in after['teams'] if t['team_id']==team)
  bi=[p['unique_id'] for p in b['players']];ai=[p['unique_id'] for p in a['players']]
  checks[f'team_{team}_exact_swap']=bi.count(outgoing)==1 and ai.count(incoming)==1 and incoming not in bi and outgoing not in ai and sorted(x for x in bi if x!=outgoing)==sorted(x for x in ai if x!=incoming)
  checks[f'team_{team}_count']=a['regular_count']==b['regular_count']==len(ai)==len(bi)
  checks[f'team_{team}_money']=all(a[k]==b[k] for k in ('total_salary_raw','payroll_raw'))
 for uid in (9842,9879):
  bs=[p for t in before['teams'] for p in t['players'] if p['unique_id']==uid];aa=[p for t in after['teams'] for p in t['players'] if p['unique_id']==uid]
  if len(bs)!=1 or len(aa)!=1:
   checks[f'player_{uid}_reciprocal_ownership']=False;checks[f'player_{uid}_contract_preserved']=False;continue
  b=bs[0];a=aa[0]
  checks[f'player_{uid}_reciprocal_ownership']=a['current_team_matches'] is True and a['contract_team_matches'] is True
  checks[f'player_{uid}_contract_preserved']=a['contract']==b['contract']
 checks['all_30_core_team_summaries_unchanged']=len(before['all_core_teams'])==len(after['all_core_teams'])==30 and sorted(before['all_core_teams'],key=lambda t:t['team_id'])==sorted(after['all_core_teams'],key=lambda t:t['team_id'])
 checks['stable_roots_and_no_isolated_failures']=before['stable_roster_root'] is True and after['stable_roster_root'] is True and not before['isolated_failures'] and not after['isolated_failures']
 return checks

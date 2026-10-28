"""Exact-input control facade. Preparation is inert; dispatch needs an explicit backend."""
import json
from copy import deepcopy
from contracts import Capability,NativeActionPlan,NativeActionRequest,NativeActionResult,NativeCallStep,Outcome
from registry import NativeActionRegistry
class NativeControlFacade:
 def __init__(self,registry=None,transport=None):self.registry=registry or NativeActionRegistry();self.transport=transport
 def prepare(self,request:NativeActionRequest):
  action,data=self.registry.validate_request(request)
  steps=tuple(NativeCallStep(s['operation'],s.get('binding_id'),deepcopy(s.get('arguments',{}))) for s in action['call_sequence'])
  unresolved=list(action['unknowns'])
  for step in steps:
   if step.binding_id:
    b=self.registry.binding(step.binding_id)
    if b.rva is None and b.return_type!='LAYOUT':unresolved.append('UNKNOWN_RVA:'+b.binding_id)
    unresolved.extend(b.unknowns)
  return NativeActionPlan(request.action_id,Capability(action['capability']),deepcopy(data),steps,tuple(dict.fromkeys(unresolved)),action.get('runtime_handler'),tuple(action['evidence']),coverage_unknowns=tuple(action.get('coverage_unknowns',[])))
 def render(self,request:NativeActionRequest):
  from runtime_codegen import render_program
  plan=self.prepare(request)
  if not plan.runtime_handler or plan.unresolved:raise ValueError({'outcome':Outcome.UNKNOWN_BINDING,'unknowns':plan.unresolved,'handler':plan.runtime_handler})
  return render_program(plan,self.registry)
 def dispatch(self,request:NativeActionRequest):
  plan=self.prepare(request);original=deepcopy(dict(request.parameters))
  if not plan.runtime_handler or plan.unresolved:return NativeActionResult(request.action_id,Outcome.UNKNOWN_BINDING,original,details={'plan':plan.to_dict()})
  if self.transport is None:return NativeActionResult(request.action_id,Outcome.PREPARED,original,details={'plan':plan.to_dict(),'reason':'Explicit next-task runtime transport not supplied; no process operation'})
  program=self.render(request)
  # Exactly one transport execution. Never retry, change a target, or search alternatives.
  try:r=self.transport.execute(program.script,action_id=plan.action_id,request_id=request.request_id,maximum_game_calls=program.maximum_game_calls)
  except Exception as exc:return NativeActionResult(request.action_id,Outcome.UNKNOWN,original,details={'error':type(exc).__name__,'automatic_retry':False})
  outcome=Outcome.REJECTED if r.get('outcome')=='REJECTED_BY_GAME' else Outcome.RETURNED if r.get('outcome')=='NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED' else Outcome.UNKNOWN
  return NativeActionResult(request.action_id,outcome,original,r,{'automatic_retry':False,'request_substitution':False,'capability':plan.capability.value,'coverage_unknowns':list(plan.coverage_unknowns)})
 def gm_trade(self,team_a,players_a,team_b,players_b,*,picks_a=None,picks_b=None,request_id=''):
  picks_a=[] if picks_a is None else picks_a;picks_b=[] if picks_b is None else picks_b
  action='TRADE_EXECUTE_AGREED_PACKAGE'
  return self.dispatch(NativeActionRequest(action,{'team_a':team_a,'players_a':players_a,'team_b':team_b,'players_b':players_b,'picks_a':picks_a,'picks_b':picks_b},request_id))
 def coach_defense(self,team_id,value,*,expected_before=None,request_id=''):
  data={'team_id':team_id,'value':value}
  if expected_before is not None:data['expected_before']=expected_before
  return self.dispatch(NativeActionRequest('COACH_APPLY_DEFENSE_POE',data,request_id))
 def coach_offense(self,team_id,value,*,expected_before=None,request_id=''):
  data={'team_id':team_id,'value':value}
  if expected_before is not None:data['expected_before']=expected_before
  return self.dispatch(NativeActionRequest('COACH_APPLY_OFFENSE_POE',data,request_id))
 def sign(self,team_id,player_id,contract,*,request_id=''):return self.dispatch(NativeActionRequest('SIGN_FREE_AGENT',{'team_id':team_id,'player_id':player_id,'contract':contract},request_id))
 def draft(self,team_id,pick_id,player_id,*,request_id=''):return self.dispatch(NativeActionRequest('DRAFT_SELECT_PROSPECT',{'team_id':team_id,'pick_id':pick_id,'player_id':player_id},request_id))
 def scout(self,team_id,player_ids,*,goal_index=None,request_id=''):
  action='SCOUT_ASSIGN_TARGETS' if goal_index is None else 'SCOUT_SET_EXISTING_GOAL_TARGETS';data={'team_id':team_id,'player_ids':player_ids}
  if goal_index is not None:data['goal_index']=goal_index
  return self.dispatch(NativeActionRequest(action,data,request_id))
 def train_team(self,team_id,date,training,*,request_id=''):return self.dispatch(NativeActionRequest('TRAIN_TEAM_SET_SCHEDULE',{'team_id':team_id,'date':date,'training':training},request_id))
 def train_intensity(self,team_id,date,value,*,request_id=''):return self.dispatch(NativeActionRequest('TRAIN_TEAM_SET_INTENSITY',{'team_id':team_id,'date':date,'value':value},request_id))
 def coach_settings(self,team_id,settings,*,request_id=''):return self.dispatch(NativeActionRequest('COACH_SET_KNOWN_CURRENT_SETTINGS',{'team_id':team_id,'settings':settings},request_id))
 def ensure_opponent_gameplan(self,team_id,opponent_team_id,*,request_id=''):return self.dispatch(NativeActionRequest('COACH_ENSURE_OPPONENT_GAMEPLAN',{'team_id':team_id,'opponent_team_id':opponent_team_id},request_id))
 def read(self,action_id,parameters,*,request_id=''):
  action=self.registry.get(action_id)
  if action['kind']!='READ':raise ValueError('Use dispatch for mutation requests')
  return self.dispatch(NativeActionRequest(action_id,parameters,request_id))

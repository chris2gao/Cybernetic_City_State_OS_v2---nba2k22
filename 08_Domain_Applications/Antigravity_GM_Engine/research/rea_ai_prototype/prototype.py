"""Offline AI mechanism prototype. No process API, pointer, dynamic code or live adapter."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import asdict,dataclass,field
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent
FOCUS={'NO_PREFERENCE':0,'PROTECT_PAINT':13,'NEUTRAL_DEFENSE_FOCUS':14,'LIMIT_PERIMETER_SHOTS':15}
ACTION_ROLES={'COACH_SET_DEFENSE_FOCUS':'COACH','PLAYER_OBSERVE_BADGE_GROWTH':'PLAYER','GM_AI_AI_TRADE':'GM'}
ACTION_MECHANISMS={'COACH_SET_DEFENSE_FOCUS':'AI_COACH_DEFENSE_M1','PLAYER_OBSERVE_BADGE_GROWTH':'AI_BADGE_NATURAL_GROWTH','GM_AI_AI_TRADE':'AI_AI_GM_TRADE'}
EFFECTS=frozenset({'coach:A.poe_word','coach:A.applied_focus','coach:A.cache_epoch','revision'})

def provenance_summary(sources):
 groups=sorted({s['origin_group'] for s in sources})
 return {'origin_groups':groups,'origin_count':len(groups),'classification':'SINGLE_ORIGIN' if len(groups)==1 else 'MULTIPLE_ORIGINS_NOT_INDEPENDENT_CONFIRMATION','independent_AI_game_confirmation':False}

def digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def strict_keys(value,keys,required=()):
 if not isinstance(value,dict) or set(value)-set(keys) or set(required)-set(value):raise ValueError('INVALID_TYPED_OBJECT')
def is_int(value):return type(value) is int

def decode_gameplan_index(raw):
 """Bound to static candidate's u8 return: zero is valid, FF is missing, 35 slots."""
 if not is_int(raw) or not 0<=raw<=255:raise ValueError('INVALID_RAW_GAMEPLAN_INDEX')
 if raw==255:return None
 if raw>=35:raise ValueError('GAMEPLAN_INDEX_OUT_OF_CAPACITY')
 return raw

@dataclass(frozen=True)
class Actor:
 id:str
 role:str
 engine_control:str
 @classmethod
 def parse(cls,value):
  strict_keys(value,{'id','role','engine_control'},{'id','role','engine_control'})
  if not all(isinstance(v,str) and v for v in value.values()):raise ValueError('INVALID_ACTOR')
  if value['role'] not in {'GM','COACH','PLAYER'} or value['engine_control'] not in {'AI_CONTROLLED','HUMAN_CONTROLLED','UNKNOWN'}:raise ValueError('INVALID_ACTOR')
  return cls(**value)

@dataclass(frozen=True)
class Intent:
 action_id:str
 action_type:str
 initiator:Actor
 counterparty:Actor|None
 environment:str
 build:str
 mode:str
 save_id:str
 scene_id:str
 target_ids:tuple[str,...]
 arguments:dict
 expected_revision:int
 permission_ref:str|None
 @classmethod
 def parse(cls,value):
  required={'action_id','action_type','initiator','environment','build','mode','save_id','scene_id','target_ids','arguments','expected_revision'}
  strict_keys(value,required|{'counterparty','permission_ref'},required)
  for key in ('action_id','action_type','environment','build','mode','save_id','scene_id'):
   if not isinstance(value[key],str) or not value[key]:raise ValueError('INVALID_INTENT_STRING')
  if value['action_type'] not in ACTION_ROLES:raise ValueError('UNKNOWN_ACTION')
  if value['environment'] not in {'OWNED_FIXTURE','REAL_GAME'}:raise ValueError('INVALID_ENVIRONMENT')
  if not is_int(value['expected_revision']) or value['expected_revision']<0:raise ValueError('INVALID_REVISION')
  ids=value['target_ids']
  if not isinstance(ids,list) or not ids or not all(isinstance(i,str) and i for i in ids) or len(set(ids))!=len(ids):raise ValueError('INVALID_TARGET_IDENTITIES')
  if not isinstance(value['arguments'],dict):raise ValueError('INVALID_ARGUMENTS')
  if value.get('permission_ref') is not None and not isinstance(value['permission_ref'],str):raise ValueError('INVALID_PERMISSION_REF')
  if value['action_type']=='COACH_SET_DEFENSE_FOCUS':
   strict_keys(value['arguments'],{'focus'},{'focus'})
   if not isinstance(value['arguments']['focus'],str) or value['arguments']['focus'] not in FOCUS:raise ValueError('UNKNOWN_FOCUS_ENUM')
  elif value['action_type']=='PLAYER_OBSERVE_BADGE_GROWTH':
   strict_keys(value['arguments'],{'badge_id'},{'badge_id'})
   if value['arguments']['badge_id'] not in {'CatchAndShoot','CornerSpecialist'}:raise ValueError('UNKNOWN_BADGE_CASE')
  elif value['action_type']=='GM_AI_AI_TRADE':
   strict_keys(value['arguments'],{'player_ids','pick_ids'},{'player_ids','pick_ids'})
   if not all(isinstance(value['arguments'][k],list) and all(isinstance(v,str) for v in value['arguments'][k]) for k in ('player_ids','pick_ids')):raise ValueError('INVALID_TRADE_ARGUMENTS')
  args=deepcopy(value);args['initiator']=Actor.parse(value['initiator']);args['counterparty']=Actor.parse(value['counterparty']) if value.get('counterparty') else None;args['target_ids']=tuple(ids);args.setdefault('permission_ref',None)
  return cls(**args)

@dataclass(frozen=True)
class Capability:
 backend:str
 environment:str
 qualified:bool
 declared_effects:frozenset[str]=field(default_factory=frozenset)
 missing_proofs:tuple[str,...]=()
 proof_scope:str='UNQUALIFIED'

class OwnedFixture:
 """Deliberately quiescent synthetic state; cache/consumer semantics are invented here."""
 def __init__(self):
  self._state={'build':'OWNED_COACH_FIXTURE_V1','mode':'PC22_OFFLINE_MYLEAGUE','save_id':'fixture-save','scene_id':'fixture-coach-scene','revision':1,
   'coaches':{'A':{'poe_word':14|(5<<15),'applied_focus':14,'cache_epoch':0},'B':{'poe_word':13|(4<<15),'applied_focus':13,'cache_epoch':0}}}
  self.operations=[]
 def snapshot(self):return deepcopy(self._state)
 def apply_native_model(self,intent):
  self.operations.append('NATIVE_FIXTURE_MODEL')
  coach=self._state['coaches']['A'];value=FOCUS[intent.arguments['focus']]
  coach['poe_word']=(coach['poe_word']&~31)|value;coach['applied_focus']=value;coach['cache_epoch']+=1;self._state['revision']+=1
 def apply_memory_model(self,intent):
  self.operations.append('VALIDATED_MEMORY_FIXTURE')
  value=FOCUS[intent.arguments['focus']];previous=self._state['coaches']['A']['poe_word']
  self._state['coaches']['A']['poe_word']=(previous&0xffffffe0)|value
  self._state['coaches']['A']['applied_focus']=value
  self._state['coaches']['A']['cache_epoch']+=1;self._state['revision']+=1

class NativeBackend:
 def __init__(self,qualified=False,environment='OWNED_FIXTURE',fault=None):
  if environment not in {'OWNED_FIXTURE','REAL_GAME'}:raise ValueError('INVALID_BACKEND_ENVIRONMENT')
  qualified=qualified is True and environment=='OWNED_FIXTURE'
  self.capability=Capability('NATIVE_FUNCTION',environment,qualified,EFFECTS,() if qualified else ('AI_CALLSITE_OR_CONTEXT_UNPROVEN',),'OWNED_FIXTURE_MODEL_ONLY' if qualified and environment=='OWNED_FIXTURE' else 'UNQUALIFIED')
  self.fault=fault;self.calls=0
 def execute(self,fixture,intent):
  if self.capability.environment!='OWNED_FIXTURE' or fixture is None:raise RuntimeError('LIVE_ADAPTER_NOT_IMPLEMENTED')
  self.calls+=1;fixture.apply_native_model(intent)
  if self.fault=='after_write':raise RuntimeError('POSSIBLE_PARTIAL_SIDE_EFFECTS')
  return {'returned_success':True,'implementation':'PYTHON_NATIVE_INTERFACE_SIMULATOR_NOT_GAME_NATIVE_CALL'}

class ValidatedMemoryBackend:
 def __init__(self,qualified=True,environment='OWNED_FIXTURE',fault=None):
  if environment not in {'OWNED_FIXTURE','REAL_GAME'}:raise ValueError('INVALID_BACKEND_ENVIRONMENT')
  qualified=qualified is True and environment=='OWNED_FIXTURE'
  effects=EFFECTS|{'coach:B.poe_word'} if fault=='extra_effect_contract' else EFFECTS
  self.capability=Capability('MEMORY_WRITE',environment,qualified,effects,() if qualified else ('CURRENT_FIELD_CONSUMER_CACHE_READBACK_UNPROVEN',),'OWNED_FIXTURE_ONLY' if qualified and environment=='OWNED_FIXTURE' else 'UNQUALIFIED')
  self.fault=fault;self.calls=0
 def execute(self,fixture,intent):
  if self.capability.environment!='OWNED_FIXTURE' or fixture is None:raise RuntimeError('LIVE_ADAPTER_NOT_IMPLEMENTED')
  self.calls+=1;fixture.apply_memory_model(intent)
  if self.fault=='whole_word':fixture._state['coaches']['A']['poe_word']=FOCUS[intent.arguments['focus']]
  if self.fault=='missing_cache':fixture._state['coaches']['A']['cache_epoch']-=1
  if self.fault=='unrelated_team':fixture._state['coaches']['B']['poe_word']=0
  return {'returned_success':True,'implementation':'SYNTHETIC_MEMORY_AND_CACHE_MODEL_NOT_PROCESS_WRITE'}

class NoSafePathBackend:
 capability=Capability('NO_SAFE_PATH','REAL_GAME',False,missing_proofs=('NO_PROVEN_GAME_BACKEND',))

def expected_poststate(before,intent):
 desired=deepcopy(before);value=FOCUS[intent.arguments['focus']]
 desired['coaches']['A']['poe_word']=(before['coaches']['A']['poe_word']&~31)|value
 desired['coaches']['A']['applied_focus']=value;desired['coaches']['A']['cache_epoch']+=1;desired['revision']+=1
 return desired

def differences(left,right,path=''):
 if type(left)!=type(right):return [path]
 if isinstance(left,dict):
  return [q for key in sorted(left.keys()|right.keys()) for q in ([path+'/'+key] if key not in left or key not in right else differences(left[key],right[key],path+'/'+key))]
 return [] if left==right else [path]

class Router:
 def __init__(self,fixture=None,native=None,memory=None):
  self.fixture=fixture;env='OWNED_FIXTURE' if fixture else 'REAL_GAME'
  self.native=native or NativeBackend(False,env)
  self.memory=memory or ValidatedMemoryBackend(bool(fixture),env)
 def assess(self,intent):return self.act(intent,execute=False)
 def act(self,intent,execute=True):
  before=self.fixture.snapshot() if self.fixture else None
  caps=[self.native.capability,self.memory.capability]
  receipt={'intent_ref':intent.action_id,'environment':intent.environment,'game_target':False,'requested_game_target':intent.environment=='REAL_GAME','knowledge_available':False,
   'route':'NO_SAFE_PATH','execution':'NOT_EXECUTED','result':'NOT_EXECUTED','backend_selected':None,'reasons':[],
   'native_capability':asdict(caps[0])|{'declared_effects':sorted(caps[0].declared_effects)},'memory_capability':asdict(caps[1])|{'declared_effects':sorted(caps[1].declared_effects)},
   'before_snapshot':before,'fresh_readback':None,'affected_set_comparison':None,'game_proof_level':'NOT_PROMOTED','game_persistence':'NOT_TESTED','operation_count':0}
  def blocked(code):receipt['reasons'].append(code);return receipt
  if intent.initiator.role!=ACTION_ROLES[intent.action_type]:return blocked('ACTOR_ROLE_MISMATCH')
  if intent.action_type=='GM_AI_AI_TRADE':
   if intent.counterparty is None:return blocked('AI_COUNTERPARTY_REQUIRED')
   if intent.counterparty.engine_control=='HUMAN_CONTROLLED':return blocked('HUMAN_ONLY_EXCLUDED')
  if intent.initiator.engine_control!='AI_CONTROLLED' or (intent.counterparty and intent.counterparty.engine_control!='AI_CONTROLLED'):return blocked('CONTROL_FLAG_CONFLICT')
  if intent.mode!='PC22_OFFLINE_MYLEAGUE':return blocked('GAME_MODE_PLATFORM_SCOPE_MISMATCH')
  card=KnowledgeStore().show(ACTION_MECHANISMS[intent.action_type],intent.initiator.role,intent.mode)
  receipt['knowledge_available']=True
  receipt['knowledge_ref']={'mechanism_id':card['mechanism_id'],'source_refs':card['source_refs'],'proof_level':card['proof_level'],'actor_scope_verdict':card['actor_scope_verdict'],'live_execution_qualified':card['can_execute'],'unknowns':card['unknowns']}
  if intent.environment=='REAL_GAME':
   receipt['reasons'].extend(['AI_PATH_UNVERIFIED','NATIVE_NOT_QUALIFIED','MEMORY_NOT_QUALIFIED','NO_LIVE_ADAPTER_INSTALLED'])
   if intent.permission_ref is None:receipt['reasons'].append('MISSING_EXACT_ACTION_AUTHORIZATION')
   return receipt
  if self.fixture is None:return blocked('FIXTURE_CONTEXT_NOT_INSTALLED')
  if any(intent.__dict__[key]!=before[key] for key in ('build','save_id','scene_id','mode')):return blocked('BUILD_SAVE_OR_SCENE_MISMATCH')
  if intent.expected_revision!=before['revision']:return blocked('STALE_PLAN')
  if intent.initiator.id!='coach:A' or intent.target_ids!=('coach:A',):return blocked('OBJECT_OWNERSHIP_OR_IDENTITY_MISMATCH')
  if intent.action_type!='COACH_SET_DEFENSE_FOCUS':return blocked('MECHANISM_BACKEND_NOT_QUALIFIED')
  if intent.permission_ref!='OWNED_FIXTURE_DEMO':return blocked('MISSING_FIXTURE_AUTHORIZATION')
  qualified=[c for c in caps if c.qualified and c.environment=='OWNED_FIXTURE' and c.proof_scope in {'OWNED_FIXTURE_ONLY','OWNED_FIXTURE_MODEL_ONLY'}]
  if any(c.declared_effects!=EFFECTS for c in qualified):return blocked('BACKEND_SEMANTIC_CONTRACT_MISMATCH')
  if not qualified:
   receipt['reasons'].extend([*caps[0].missing_proofs,*caps[1].missing_proofs]);return blocked('NEITHER_PATH_SAFE')
  chosen=self.native if caps[0] in qualified else self.memory
  receipt['backend_selected']=chosen.capability.backend
  receipt['route']='NATIVE_FIXTURE_MODEL' if chosen is self.native else 'VALIDATED_MEMORY_WRITE_FIXTURE'
  if not execute:receipt['result']='ASSESSMENT_ONLY';return receipt
  receipt['execution']='STARTED';desired=expected_poststate(before,intent)
  try:
   result=chosen.execute(self.fixture,intent);receipt['returned']=result;receipt['operation_count']=1
  except Exception as error:
   receipt['operation_count']=1;receipt['execution']='ABORTED';receipt['result']='EXECUTED_BUT_UNVERIFIED';receipt['reasons'].extend([str(error),'NO_AUTOMATIC_FALLBACK_AFTER_SIDE_EFFECTS']);receipt['fresh_readback']=self.fixture.snapshot();return receipt
  after=self.fixture.snapshot();mismatch=differences(desired,after)
  receipt.update(execution='COMPLETED_REPORTED',fresh_readback=after,affected_set_comparison={'expected':sorted(EFFECTS),'unexpected_differences':mismatch},before_sha256=digest(before),after_sha256=digest(after))
  if mismatch:receipt.update(result='FAILED_READBACK',reasons=['FRESH_POSTSTATE_OR_SIDE_EFFECT_MISMATCH'])
  else:receipt.update(result='FIXTURE_ONLY_PASS',reasons=['COMMON_POSTCONDITIONS_MATCH; NOT_A_GAME_RESULT'])
  return receipt

class KnowledgeStore:
 def __init__(self,path=None):
  self.cards=json.loads((Path(path) if path else ROOT/'data/knowledge_cards.json').read_text(encoding='utf-8'))
  records=json.loads((ROOT/'evidence/source_registry.json').read_text(encoding='utf-8'))['sources'];self.sources={s['source_id']:s for s in records}
 def show(self,mechanism,role,mode='PC22_OFFLINE_MYLEAGUE'):
  if role not in {'GM','COACH','PLAYER'}:raise ValueError('INVALID_ROLE')
  card=next(c for c in self.cards if c['mechanism_id']==mechanism)
  if card['mode']!=mode:raise ValueError('GAME_MODE_PLATFORM_SCOPE_MISMATCH')
  if role not in card['role_visibility']:raise PermissionError('ROLE_INFORMATION_LEAK_BLOCK_DISTRIBUTION')
  if any(ref not in self.sources for ref in card['source_refs']):raise ValueError('UNRESOLVED_EVIDENCE_SOURCE')
  references=[self.sources[ref] for ref in card['source_refs']]
  if card['proof_level'].startswith(('L3','L4','L5')) and not any(s.get('same_mode_AI_behavior_proven') is True for s in references):raise ValueError('UNSUPPORTED_MATURITY_PROMOTION')
  allowed=('mechanism_id','title','description_zh','mode','game_build_sha256','last_verified_at_or_unknown','proof_level','actor_scope_verdict','original_game_rule','field_semantics','decision_guidance','unknowns','source_refs','can_reason','can_recommend','can_execute','role_visibility','source_origin_group')
  result={k:deepcopy(card[k]) for k in allowed if k in card};result['provenance']=provenance_summary(references);return result
 def query(self,role,mode='PC22_OFFLINE_MYLEAGUE'):
  return [self.show(c['mechanism_id'],role,mode) for c in self.cards if c['mode']==mode and role in c['role_visibility']]

def fixture_intent(**changes):
 data={'action_id':'fixture-coach-001','action_type':'COACH_SET_DEFENSE_FOCUS','initiator':{'id':'coach:A','role':'COACH','engine_control':'AI_CONTROLLED'},'environment':'OWNED_FIXTURE','build':'OWNED_COACH_FIXTURE_V1','mode':'PC22_OFFLINE_MYLEAGUE','save_id':'fixture-save','scene_id':'fixture-coach-scene','target_ids':['coach:A'],'arguments':{'focus':'PROTECT_PAINT'},'expected_revision':1,'permission_ref':'OWNED_FIXTURE_DEMO'}
 data.update(changes);return Intent.parse(data)

"""Typed C1 native service contract; no direct process-memory writer."""
from dataclasses import dataclass,asdict
from enum import StrEnum
BUILD='1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'
class Status(StrEnum):
 NOT_FOUND='NOT_FOUND'
 CANDIDATE_ONLY='CANDIDATE_ONLY'
 READY='READY_FOR_BOUNDED_POC'
 UNVERIFIED='REAL_GAME_CALL_EXECUTED_UNVERIFIED'
 VERIFIED='REAL_GAME_EFFECT_VERIFIED'
 FAILED='FAILED_OR_ABORTED'
@dataclass(frozen=True)
class NativeActionSpec:
 action_id:str='C1-SET-POE-DEFENSE'
 game_build_sha256:str=BUILD
 mode:str='PC22_OFFLINE_MYLEAGUE_ISOLATED_TEST_SAVE'
 entry_rva:int=21424800
 abi:str='win64'
 arguments:tuple=('pointer:GAMEPLAN_const','pointer:COACHDATA')
 return_type:str='void'
 source_input_offset:int=0x181
 destination_word_offset:int=316
 allowed_values:tuple=(0,13,14,15)
 thread_model:str='FRIDA_AGENT_THREAD_ONLY_FOR_STATIC_NULL_PLAYBOOK_NO_NESTED_CALL_BRANCH'
 AI_caller_proven:bool=False
 service_provenance:str='GAME_OWNED_GAMEPLAN_TO_COACH_APPLY_WITH_THREE_STATIC_MANAGER_CALLERS'
 effects:str='Apply whole bounded coach-setting projection; marshal all other inputs to current values; verify full 352 bytes and original Gameplan remain unchanged except requested low5 bits.'
 permission:str='FIRST_EFFECTFUL_BOUNDED_HUMAN_APPROVAL'
 lifetime:str='Fresh roster/franchise/team/reciprocal coach binding; stable raw prestate; temporary input stays alive until calls and readback complete.'
 rollback:str='Same native service with fresh validated original-value input; no automatic direct-memory fallback.'
 def to_dict(self):return asdict(self)
@dataclass(frozen=True)
class NativeActionRequest:
 team_id:int
 defense:int
 expected_before:int=14
 @classmethod
 def parse(cls,data):
  if set(data)!={'action_id','team_id','defense','expected_before'} or data['action_id']!='C1-SET-POE-DEFENSE':raise ValueError('typed action schema')
  if any(type(data[k]) is not int for k in ('team_id','defense','expected_before')):raise ValueError('integer values required')
  if not 0<=data['team_id']<=65534 or data['defense'] not in NativeActionSpec().allowed_values or data['expected_before'] not in NativeActionSpec().allowed_values:raise ValueError('domain range')
  if data['defense']==data['expected_before']:raise ValueError('first PoC requires a measurable change')
  return cls(data['team_id'],data['defense'],data['expected_before'])
def expected_word(before,defense):return (before&~31)|defense
def encode_input_from_coach(gameplan,coach,defense):
 if len(gameplan)!=880 or len(coach)!=352:raise ValueError('exact current native object sizes required')
 if defense not in NativeActionSpec().allowed_values:raise ValueError('invalid defense')
 if any(coach[0x120:0x138]):raise ValueError('first PoC null-playbook branch only')
 b=bytearray(gameplan);word=int.from_bytes(coach[316:320],'little')
 for offset,shift in zip(range(0x17e,0x184),(15,20,25,0,5,10)):b[offset]=(word>>shift)&31
 b[0x181]=defense
 b[0x184]=(int.from_bytes(coach[0x148:0x14c],'little')>>17)&255
 for source,dest in ((0x185,0xe0),(0x186,0xe2),(0x187,0xde),(0x188,0x138),(0x189,0xdf),(0x18a,0x109)):b[source]=coach[dest]
 b[0x18b]=(int.from_bytes(coach[0xfc:0x100],'little')>>25)&63
 b[0x178:0x17e]=b'\xff'*6
 return bytes(b)
@dataclass
class NativeActionReceipt:
 status:Status
 action_id:str
 source_kind:str
 native_calls:int=0
 game_target_calls:int=0
 native_effect_verified:bool=False
 reason:str=''
 def __post_init__(self):
  if self.status==Status.VERIFIED and (self.source_kind!='REAL_GAME' or self.game_target_calls<1 or not self.native_effect_verified):raise ValueError('real effect proof required')
  if self.game_target_calls>self.native_calls:raise ValueError('invalid call accounting')

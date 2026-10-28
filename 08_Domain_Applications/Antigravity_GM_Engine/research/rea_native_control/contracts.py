"""External decisions and native execution contracts. No automatic decision logic."""
from dataclasses import asdict,dataclass,field
from enum import StrEnum
from typing import Any,Mapping,Protocol
BUILD='1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'
class Capability(StrEnum):
 PRIOR_LIVE_SUCCESS='PRIOR_LIVE_SUCCESS'
 CALL_LOGIC_RECOVERED='CALL_LOGIC_RECOVERED'
 PARTIAL_BINDING='PARTIAL_BINDING'
 REFERENCE_ONLY='REFERENCE_ONLY'
 NOT_FOUND='NOT_FOUND_WITH_SEARCH_SCOPE'
class Outcome(StrEnum):
 PREPARED='PREPARED_NOT_EXECUTED'
 UNKNOWN_BINDING='UNKNOWN_BINDING'
 REJECTED='REJECTED_BY_GAME'
 RETURNED='NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED'
 UNKNOWN='EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY'
@dataclass(frozen=True)
class NativeBinding:
 binding_id:str
 rva:int|None
 return_type:str
 parameters:tuple[Mapping[str,Any],...]
 abi:str='win64'
 game_build_sha256:str=BUILD
 object_requirements:tuple[str,...]=()
 lifecycle:tuple[str,...]=()
 evidence:tuple[str,...]=()
 unknowns:tuple[str,...]=()
 input_layout:Mapping[str,Any]=field(default_factory=dict)
 def to_dict(self):return asdict(self)
@dataclass(frozen=True)
class NativeActionRequest:
 action_id:str
 parameters:Mapping[str,Any]
 request_id:str=''
@dataclass(frozen=True)
class NativeCallStep:
 operation:str
 binding_id:str|None=None
 arguments:Mapping[str,Any]=field(default_factory=dict)
 on_rejection:str='RETURN_ORIGINAL_GAME_REJECTION_WITHOUT_SUBSTITUTION'
@dataclass(frozen=True)
class NativeActionPlan:
 action_id:str
 capability:Capability
 request:Mapping[str,Any]
 steps:tuple[NativeCallStep,...]
 unresolved:tuple[str,...]
 runtime_handler:str|None
 evidence:tuple[str,...]
 coverage_unknowns:tuple[str,...]=()
 executed_this_task:bool=False
 def to_dict(self):return asdict(self)
@dataclass(frozen=True)
class NativeActionResult:
 action_id:str
 outcome:Outcome
 original_request:Mapping[str,Any]
 native_result:Any=None
 details:Mapping[str,Any]=field(default_factory=dict)
class RuntimeTransport(Protocol):
 """A next-task runtime adapter executes the exact emitted program, at most once."""
 def execute(self,script:str,*,action_id:str,request_id:str,maximum_game_calls:int)->Mapping[str,Any]:...

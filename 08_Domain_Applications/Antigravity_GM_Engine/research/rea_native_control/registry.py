"""Load the bounded action/binding catalog without touching a target process."""
import json
from copy import deepcopy
from pathlib import Path
from contracts import Capability,NativeActionRequest,NativeBinding
ROOT=Path(__file__).parent
class NativeActionRegistry:
 def __init__(self,root=ROOT):
  self.root=Path(root);self.catalog=json.loads((self.root/'data/action_registry.json').read_text(encoding='utf-8'));raw=json.loads((self.root/'data/native_bindings.json').read_text(encoding='utf-8'))
  self.actions={r['action_id']:r for r in self.catalog['actions']};self.bindings={r['binding_id']:NativeBinding(**(r|{'parameters':tuple(r.get('parameters',[])),'object_requirements':tuple(r.get('object_requirements',[])),'lifecycle':tuple(r.get('lifecycle',[])),'evidence':tuple(r.get('evidence',[])),'unknowns':tuple(r.get('unknowns',[]))})) for r in raw['bindings']}
  index=self.root/'data/native_live_validation.json';self.live_validation=json.loads(index.read_text(encoding='utf-8'))['actions'] if index.exists() else {}
 def get(self,action_id):
  if action_id not in self.actions:raise KeyError('Unknown action ID: '+action_id)
  action=deepcopy(self.actions[action_id])
  if action_id in self.live_validation:action['live_validation']=deepcopy(self.live_validation[action_id])
  return action
 def list(self,domain=None):return [deepcopy(r) for r in self.actions.values() if domain is None or r['domain']==domain]
 def validate_request(self,request:NativeActionRequest):
  action=self.get(request.action_id);data=deepcopy(dict(request.parameters));schema=action['input_schema'];allowed=set(schema);missing=[k for k,v in schema.items() if v.get('required',True) and k not in data]
  if missing or set(data)-allowed:raise ValueError({'missing':missing,'unknown':sorted(set(data)-allowed)})
  for key,value in data.items():
   spec=schema[key];kind=spec['type']
   if kind=='integer' and type(value) is not int:raise TypeError(key+' must be integer')
   if kind=='integer' and (value<spec.get('minimum',0) or value>spec.get('maximum',2147483647)):raise ValueError(key+' outside native representation')
   if kind=='array' and not isinstance(value,list):raise TypeError(key+' must be array')
   if kind=='object' and not isinstance(value,dict):raise TypeError(key+' must be object')
   if kind=='string' and not isinstance(value,str):raise TypeError(key+' must be string')
   if 'enum' in spec and value not in spec['enum']:raise ValueError(key+' not in recovered native enum')
  return action,data
 def binding(self,binding_id):return self.bindings[binding_id]
 def capability(self,action_id):return Capability(self.actions[action_id]['capability'])

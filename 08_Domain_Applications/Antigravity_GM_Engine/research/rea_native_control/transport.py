"""Explicit future-runtime REA transport. It is never instantiated by registry imports."""
import hashlib,json,os,shutil,subprocess,uuid
from dataclasses import dataclass
from pathlib import Path
from contracts import BUILD
@dataclass(frozen=True)
class LiveExecutionContext:
 authorization_ref:str
 allowed_action_ids:frozenset[str]
 maximum_game_calls:int
 enabled:bool=False
class ReaCliTransport:
 def __init__(self,runtime_directory,context:LiveExecutionContext,*,duration_ms=15000,node_path=None,rea_path=None):
  self.runtime=Path(runtime_directory).resolve();self.context=context;self.duration_ms=duration_ms
  self.node=node_path or shutil.which('node');self.rea=Path(rea_path) if rea_path else Path(os.environ.get('APPDATA',''))/'npm/node_modules/rea-agents/scripts/rea.mjs'
 def execute(self,script,*,action_id,request_id,maximum_game_calls):
  if not self.context.enabled or not self.context.authorization_ref or action_id not in self.context.allowed_action_ids:raise PermissionError('Live runtime is not enabled for this explicit action; discovery task remains inert')
  if maximum_game_calls>self.context.maximum_game_calls:raise PermissionError('Call budget exceeds configured next-task scope')
  if not self.node or not self.rea.is_file():raise FileNotFoundError('Installed Node/REA paths must be supplied; no automatic installation')
  if not 1000<=self.duration_ms<=120000:raise ValueError('Bounded REA observation window required')
  output=self.runtime/uuid.uuid4().hex;output.mkdir(parents=True,exist_ok=False);program=output/'program.js';program.write_text(script,encoding='utf-8')
  manifest={'action_id':action_id,'request_id':request_id,'authorization_ref':self.context.authorization_ref,'game_build_sha256':BUILD,'script_sha256':hashlib.sha256(program.read_bytes()).hexdigest(),'maximum_game_calls':maximum_game_calls}
  (output/'request.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
  command=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(Path(__file__).with_name('run_native_program.ps1')),'-Directory',str(output),'-NodePath',str(self.node),'-ReaPath',str(self.rea),'-DurationMs',str(self.duration_ms)]
  # No elevation, installation, retries or alternate targets behind the caller's back.
  with (output/'runner.log').open('w',encoding='utf-8') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  if r.returncode or not (output/'evidence.json').exists():return {'outcome':'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY','runtime_directory':str(output),'runner_exit':r.returncode}
  raw=json.loads((output/'evidence.json').read_text(encoding='utf-8-sig'));n=raw['normalized_result'];messages=n.get('messages',[])
  if n.get('cleanup_error') is not None or any(m['type']=='error' for m in messages):return {'outcome':'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY','evidence_id':raw.get('evidence_id'),'runtime_directory':str(output)}
  results=[m['payload'] for m in messages if m['type']=='send' and m['payload'].get('kind')=='native-control-result']
  if len(results)!=1:return {'outcome':'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY','evidence_id':raw.get('evidence_id'),'runtime_directory':str(output),'receipt_count':len(results)}
  return results[0]|{'evidence_id':raw.get('evidence_id'),'runtime_directory':str(output)}

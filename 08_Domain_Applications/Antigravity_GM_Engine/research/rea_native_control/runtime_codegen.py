"""Compile a native action plan into a deferred Frida program; no process access."""
import json,math
from dataclasses import dataclass
from pathlib import Path
from contracts import NativeActionPlan
@dataclass(frozen=True)
class NativeProgram:
 action_id:str
 script:str
 maximum_game_calls:int
 has_prior_live_mechanism_evidence:bool
def render_program(plan:NativeActionPlan,registry):
 root=Path(__file__).parent;handler=plan.runtime_handler
 handlers={'coach.poe':'coach_poe.js','coach.settings':'coach_settings.js','trade.players':'trade.js','trade.assets':'trade.js','read.team':'read_team.js','read.coach':'read_coach.js','read.player':'read_player.js','training.team_date':'training.js','training.intensity':'training_intensity.js','gameplan.ensure':'gameplan.js','scout.existing_goal':'scout_goal.js','scout.append_goal':'scout_append.js','scout.list':'scout_read.js','scout.info':'scout_read.js','scout.progress':'scout_read.js','scout.budget':'scout_read.js','scout.execute_trip':'scout_execute.js','draft.select':'draft.js','draft.context':'draft.js'}
 handlers['trade.agreed']='trade.js'
 handlers['training.patch']='training_patch.js'
 handlers['rotation.minutes']='rotation_minutes.js'
 handlers['player.playtypes']='player_playtypes.js'
 if handler not in handlers:raise ValueError('No recovered runtime implementation for '+str(handler))
 bindings={step.binding_id:registry.binding(step.binding_id).to_dict() for step in plan.steps if step.binding_id}
 parameters=dict(plan.request);limit=1
 if handler in ['trade.players','trade.assets','trade.agreed']:
  players_a=parameters['players_a'];players_b=parameters['players_b']
  picks=parameters.get('picks_a',[])+parameters.get('picks_b',[])
  if handler=='trade.players' and (picks or len(players_a)!=1 or len(players_b)!=1):raise ValueError('Inherited action is one player per side; choose explicit multi/mixed action for recovered new variants')
  if parameters['team_a']==parameters['team_b']:raise ValueError('Distinct team objects required')
  if any(type(p) is not int or not 0<=p<65535 for p in players_a+players_b):raise ValueError('Native PLAYER UID16 required')
  if any(type(p) is not int or not 0<=p<4294967295 for p in picks):raise ValueError('Native PICK UID32 required')
  if not players_a+players_b+picks:raise ValueError('At least one exact asset required')
  if len(set(players_a+players_b))!=len(players_a+players_b) or len(set(picks))!=len(picks):raise ValueError('Each requested asset must occur once')
  if len(players_a)+len(players_b)+len(picks)>18:raise ValueError('Native proposal has18 element slots')
  limit=len(players_a)+len(players_b)+3*len(picks)+2
  parameters['execution_mode']='AGREED_DIRECT_PROCESS' if handler=='trade.agreed' else 'LEGACY_NATIVE_FULL_CHECK'
 if handler=='training.team_date':
  config=parameters['training'];required={'percentage_per_focus','profile_per_focus','points_per_subfocus','intensity_raw'}
  if set(config)!=required:raise ValueError('Exact native daily training fields required')
  for key,n in [('percentage_per_focus',3),('profile_per_focus',3),('points_per_subfocus',38)]:
   values=config[key]
   if not isinstance(values,list) or len(values)!=n:raise ValueError(key+' native array length')
   if key=='percentage_per_focus':
    if any(type(v) not in (float,int) or abs(v)>3.402823466e38 or not math.isfinite(v) for v in values):raise ValueError('Finite float32 training values required; no inferred percentage sum rule')
   elif any(type(v) is not int or not 0<=v<=255 for v in values):raise ValueError(key+' requires native uint8 values')
  if type(config['intensity_raw']) is not int or not 0<=config['intensity_raw']<=7:raise ValueError('Native intensity is three bits; labels need next-task confirmation')
 if handler=='training.patch':
  fields={'TRAIN_TEAM_PATCH_FOCUS_RAW':{'focus_values_raw':(3,'float32')},
          'TRAIN_TEAM_PATCH_PROFILE_RAW':{'profile_values_raw':(3,'uint8'),'subfocus_points_raw':(38,'uint8')}}
  if plan.action_id not in fields:raise ValueError('Unknown daily training patch action')
  for key,(length,kind) in fields[plan.action_id].items():
   values=parameters[key]
   if not isinstance(values,list) or len(values)!=length:raise ValueError(key+' native array length')
   if kind=='float32':
    if any(type(v) not in (float,int) or abs(v)>(2-2**-23)*2**127 or not math.isfinite(v) for v in values):raise ValueError('Finite raw float32 training values required')
   elif any(type(v) is not int or not 0<=v<=255 for v in values):raise ValueError('Raw uint8 training values required')
 if handler in ['scout.existing_goal','scout.append_goal']:
  ids=parameters['player_ids']
  if len(ids)>17 or any(type(v) is not int or not 0<=v<65535 for v in ids):raise ValueError('0..17 exact prospect PLAYER UIDs16 required')
  if len(set(ids))!=len(ids):raise ValueError('Each requested prospect UID must occur once')
  if handler=='scout.append_goal':
   if not ids:raise ValueError('Native caller only appends nonempty specified-prospect goals')
   limit=3
 coach_fields=json.loads((root/'data/coach_settings.json').read_text(encoding='utf-8'))['fields']
 if handler=='coach.settings':
  settings=parameters['settings'];allowed=set(coach_fields)
  if plan.action_id=='COACH_SET_ROTATION_POLICY':allowed={'BenchDepth','BenchUtilization'}
  if not settings or set(settings)-allowed:raise ValueError('Only statically mapped current-Coach fields supported')
  for key,value in settings.items():
   f=coach_fields[key]
   if type(value) is not int or not 0<=value<2**f['width']:raise ValueError(key+' native representation')
   if f['enum'] and str(value) not in f['enum']:raise ValueError(key+' native enum')
 if handler=='gameplan.ensure' and parameters['team_id']==parameters['opponent_team_id']:raise ValueError('Opponent must differ from owner')
 if handler.startswith('read.') or handler in ['scout.list','scout.info','scout.progress','scout.budget']:limit=0
 if handler=='draft.select':limit=3
 if handler=='draft.context':limit=2
 if handler=='read.player':limit=1
 if handler=='training.intensity':limit=2
 if handler=='training.patch':limit=2
 if handler=='rotation.minutes':
  if type(parameters['minutes']) is not int or not 0<=parameters['minutes']<=48:raise ValueError('Minutes must be an explicit integer in the recovered UI range0..48')
  limit=3
 if handler=='player.playtypes':
  slots=parameters['slot_values']
  if not slots or any(type(key) is not str or key not in {'1','2','3','4'} or type(value) is not int or not 0<=value<=15 for key,value in slots.items()):raise ValueError('Explicit slot keys1..4 and PlayType enum integers0..15 required')
  limit=len(slots)
 source=(root/'runtime/common.js').read_text(encoding='utf-8')+'\n'+(root/'runtime'/handlers[handler]).read_text(encoding='utf-8')+'\n'+(root/'runtime/gui_once.js').read_text(encoding='utf-8')
 player_fields=json.loads((root/'data/player_contract_fields.json').read_text(encoding='utf-8'))['fields']
 source=source.replace('__REQUEST__',json.dumps({'action_id':plan.action_id,'parameters':parameters},ensure_ascii=False,separators=(',',':'))).replace('__BINDINGS__',json.dumps(bindings,separators=(',',':'))).replace('__LIMITS__',json.dumps({'maximum_game_calls':limit,'read_bytes':1048576},separators=(',',':'))).replace('__COACH_FIELDS__',json.dumps(coach_fields,separators=(',',':'))).replace('__PLAYER_CONTRACT_FIELDS__',json.dumps(player_fields,separators=(',',':')))
 return NativeProgram(plan.action_id,source,limit,plan.capability.value=='PRIOR_LIVE_SUCCESS')

"""Offline audit of exact originals. No attach, game call or fixture promotion."""
import hashlib,json,re,subprocess
from pathlib import Path
from native_action import BUILD
from native_trade import reconcile_trade_observations
root=Path(__file__).parent;repo=root.parents[3];e=root/'evidence'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
m=load(e/'extension_manifest.json')
assert m['game_build_sha256']==BUILD and m['Human_ended_further_tests']
for row in m['files']:
 p=root/row['path'];b=p.read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
 assert subprocess.check_output(['git','show',':'+p.relative_to(repo).as_posix()],cwd=repo)==b,'Staged bytes differ: '+row['path']
 if '/live/' in row['path'] and p.suffix=='.json':assert not re.search(rb'0x[0-9a-fA-F]{12,16}',b)
raw={};messages={}
for p in m['runtime_phases']:
 tag=p['phase'];r=load(e/'live'/tag/'evidence.json');t=load(e/'live'/tag/'target.json');n=r['normalized_result'];metrics=load(e/'live'/tag/'metrics.json')
 assert r['evidence_id']==p['evidence_id'] and n['cleanup_error'] is None
 assert t['administrator'] and t['exe_sha256']==BUILD and t['pid']==n['pid']
 assert t['script_sha256']==n['source_sha256']==hashlib.sha256((e/'live'/tag/'script.js').read_bytes()).hexdigest()
 assert metrics['exit_code']==0 and metrics['process_alive'] and not any(x['type']=='error' for x in n['messages'])
 raw[tag]=r;messages[tag]=[x['payload'] for x in n['messages'] if x['type']=='send']
before=messages['trade-restarted-before'][0];after=messages['trade-independent-after'][0]
checks=reconcile_trade_observations(before,after);assert all(checks.values())
assert raw['trade-restarted-before']['normalized_result']['pid']==raw['trade-swap-attempt']['normalized_result']['pid']==raw['trade-independent-after']['normalized_result']['pid']
assert raw['trade-swap-attempt']['normalized_result']['messages']==[], 'Missing receipt must stay visible; never invent a native return'
derived=load(e/'dossiers/C4-independent-trade-receipt.json')
assert derived['invariants']==checks and derived['native_attempt_has_receipt'] is False and derived['native_return_value_observed'] is False and derived['native_call_count_observed'] is False
assert not derived['transaction_history_or_event_record_proven'] and not derived['save_reload_proven'] and not derived['AI_autonomous_caller_proven']
q=messages['trade-qualified'][0];assert q['status']=='PRIVATE_NATIVE_FULL_LEGALITY_VERIFIED' and q['native_calls']==4 and q['game_commit_calls']==0 and q['full_native_legality_result']==q['native_validate_result']==1 and q['native_output_code']==0 and q['game_objects_unchanged'] and q['canaries_intact']
v=next(x for x in messages['coach-visible'] if x['kind']=='native-action-visible-receipt')
assert v['status']=='REAL_GAME_EFFECT_VERIFIED' and v['game_target_calls']==v['first_hand_native_calls']==1 and v['native_effect_verified']
assert len(v['checkpoints'])==2 and all(c['actual_defense']==13 and all(c[k] for k in ['full_coach_matches_expected','original_gameplan_unchanged','manager_flags_unchanged','comparison_coach_unchanged','fresh_binding']) for c in v['checkpoints'])
run=repo/'01_os/07_content/_runs/run-20261027-nba2k22-rea-native-ai-action-invocation-001'
for name,tag in [('HUMAN_TRADE_BUILD_SCOPE.json','trade-builder'),('HUMAN_TRADE_QUALIFY_SCOPE.json','trade-qualified'),('HUMAN_TRADE_SWAP_SCOPE.json','trade-swap-attempt'),('HUMAN_COACH_VISIBLE_SCOPE.json','coach-visible')]:
 a=load(run/'04_执行准备'/name);assert a['execution_status']=='CONSUMED' and a['Human_scope_approval']=='APPROVED' and a['script_sha256']==raw[tag]['normalized_result']['source_sha256']
assert m['total_recorded_REA_elapsed_ms']==sum(p['elapsed_ms'] for p in m['runtime_phases'])==119107
print(json.dumps({'result':'EXTENDED_NATIVE_EVIDENCE_VERIFIED','C4_swap_verified_by_independent_readback':True,'native_trade_returns_observed':False,'C1_retained_defense':13,'REA_records':len(raw),'REA_total_elapsed_ms':119107,'transaction_history_picks_save_reload_AI_caller_proven':False,'Human_ended_tests':True}))

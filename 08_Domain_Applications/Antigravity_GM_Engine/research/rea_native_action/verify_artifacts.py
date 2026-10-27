"""Offline proof audit against raw REA payloads and exact tracked bytes."""
import ast,hashlib,json,re,subprocess
from pathlib import Path
from invoker import NativeActionInvoker
from native_action import BUILD,NativeActionSpec
root=Path(__file__).parent;repo=root.parents[3];e=root/'evidence'
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
manifest=load(e/'manifest.json');assert manifest['game_build_sha256']==BUILD and manifest['final_poc_retained']
for r in manifest['files']:
 path=root/r['path'];raw=path.read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'],r['path']
 tracked=subprocess.check_output(['git','show',':'+path.relative_to(repo).as_posix()],cwd=repo)
 assert tracked==raw,'tracked bytes must match retained source: '+r['path']
 if path.suffix=='.json':assert not re.search(rb'0x[0-9a-fA-F]{12,16}',raw),r['path']
counts=0;game_counts=0
for phase in manifest['runtime_phases']:
 tag=phase['phase'];raw=load(e/f'live/{tag}/evidence.json');target=load(e/f'live/{tag}/target.json');metrics=load(e/f'live/{tag}/metrics.json');n=raw['normalized_result']
 assert raw['evidence_id']==phase['evidence_id'] and n['cleanup_error'] is None
 assert target['administrator'] and target['exe_sha256']==BUILD and target['pid']==n['pid']
 assert target['script_sha256']==n['source_sha256']==hashlib.sha256((e/f'live/{tag}/script.js').read_bytes()).hexdigest()
 assert metrics['process_alive'] and metrics['exit_code']==0
 assert not any(m['type']=='error' for m in n['messages'])
 for m in n['messages']:
  if m['type']=='send' and m['payload'].get('kind')=='native-action-poc-receipt':counts+=m['payload']['first_hand_native_calls'];game_counts+=m['payload']['game_target_calls']
assert counts==4 and game_counts==2
failed=NativeActionInvoker.read_receipt(e/'live/shadow-failure')['receipt'];assert failed['status']=='FAILED_OR_ABORTED' and failed['game_target_calls']==0 and 'UNREADABLE_RANGE' in failed['failure']
result=NativeActionInvoker.read_receipt(e/'live/verified-poc');r=result['receipt'];assert r['status']=='REAL_GAME_EFFECT_VERIFIED'
assert r['entry_rva']==NativeActionSpec().entry_rva and r['abi']=='win64' and r['direct_business_memory_writes']==0
assert all(r['shadow_abi'].values()) and r['restoration_status']=='FULL_COACH_AND_NEIGHBORS_RESTORED'
assert [c['changed_byte_offsets'] for c in r['checkpoints']]==[[316],[316],[],[]]
assert [c['actual_word'] for c in r['checkpoints']]==[377672237,377672237,377672238,377672238]
assert not r['save_reload_proven'] and not r['UI_reentry_proven'] and not r['AI_caller_proven']
diagnostic=load(e/'live/owned-buffer/evidence.json');owned=next(m['payload'] for m in diagnostic['normalized_result']['messages'] if m['type']=='send')
assert owned['game_native_calls']==0 and all(row['range_report'] is None and row['direct_owned_read']['success'] and row['direct_owned_read']['expected_bytes_match'] for b in owned['blocks'] for row in b['rows'])
chain=load(e/'static/chained_bodies.json')['functions'][0];assert chain['unwind_chain'][0]['flags']==4 and chain['unwind_chain'][-1]['begin']==21424800
callers=load(e/'static/apply_callers.json');assert callers['target_rva']==21424800 and len(callers['direct_call_or_tailjump_refs'])==3
atlas=load(root/'action_atlas.json');assert {c['id'] for c in atlas['categories']}=={'C1','C2','C3','C4','C5','C6'}
assert [c['id'] for c in atlas['categories'] if c['status']=='REAL_GAME_EFFECT_VERIFIED']==['C1']
assert not atlas['production_replacement_qualified']
run=repo/'01_os/07_content/_runs/run-20261027-nba2k22-rea-native-ai-action-invocation-001'
for file,tag in [('HUMAN_POC_APPROVAL.json','shadow-failure'),('HUMAN_POC_REPAIR_APPROVAL.json','verified-poc')]:
 approval=load(run/'04_执行准备'/file);target=load(e/f'live/{tag}/target.json');assert approval['script_sha256']==target['script_sha256'] and approval['Human_scope_approval']=='APPROVED' and approval['execution_status']=='CONSUMED'
 assert approval['native_calls_actual']==NativeActionInvoker.read_receipt(e/f'live/{tag}')['receipt']['first_hand_native_calls']
for path in root.rglob('*.py'):ast.parse(path.read_text(encoding='utf-8'),filename=path.name)
assert not any(p.suffix.lower() in {'.exe','.dll','.iff','.dds','.scne','.db','.sqlite'} for p in root.rglob('*') if p.is_file())
print(json.dumps({'result':'NATIVE_ACTION_EVIDENCE_VERIFIED','real_effect_evidence_id':result['evidence_id'],'current_setting_native_effect_verified':True,'native_calls_cumulative':counts,'actual_game_target_calls':game_counts,'retained_files':len(manifest['files']),'categories':6,'production_replacement_qualified':False,'AI_caller_UI_reentry_save_reload_proven':False}))

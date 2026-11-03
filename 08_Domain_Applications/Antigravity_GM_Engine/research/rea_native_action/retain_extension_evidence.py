"""Retain bounded C4/C1-visible originals, generate a clearly derived receipt."""
import argparse,hashlib,json,shutil
from pathlib import Path
from native_action import BUILD
from native_trade import NativeTradeSpec,reconcile_trade_observations
p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);a=p.parse_args();src=Path(a.runtime);root=Path(__file__).parent;e=root/'evidence';phases=[];paths=[]
mapping=[('trade-types-01','trade-types','probe.js'),('trade-rosters-01','trade-rosters-initial','trade_observe.js'),('gui-thread-01','gui-thread','probe.js'),('trade-builder-01','trade-builder','trade_builder_probe.js'),('trade-rosters-restart-02','trade-restarted-before','trade_observe.js'),('trade-context-restart-01','trade-context','probe.js'),('trade-qualify-restart-01','trade-qualified','trade_qualify.js'),('trade-swap-restart-01','trade-swap-attempt','trade_swap.js'),('trade-post-attempt-read-01','trade-independent-after','trade_observe.js'),('coach-visible-restart-01','coach-visible','coach_visible.js')]
for old,new,script in mapping:
 out=e/'live'/new;out.mkdir(parents=True,exist_ok=True)
 raw_source=json.loads((src/old/'evidence.json').read_text(encoding='utf-8-sig'))['normalized_result'];script=Path(raw_source['source_path']).name
 exact=src/old/script
 if not exact.exists():exact=Path(raw_source['source_path'])
 if hashlib.sha256(exact.read_bytes()).hexdigest()!=raw_source['source_sha256']:raise ValueError('Original script hash mismatch')
 for source,dest in [('evidence.json','evidence.json'),('target.json','target.json'),('metrics.json','metrics.json'),(script,'script.js')]:
  path=out/dest;shutil.copyfile(exact if source==script else src/old/source,path);paths.append(path)
 raw=json.loads((out/'evidence.json').read_text(encoding='utf-8-sig'));metrics=json.loads((out/'metrics.json').read_text(encoding='utf-8-sig'));phases.append({'phase':new,'evidence_id':raw['evidence_id'],'elapsed_ms':metrics['elapsed_ms'],'messages':len(raw['normalized_result']['messages'])})
static=['trade_core_anchors.json','trade_process_complete.json','trade_add_player_complete.json','trade_team_header_complete.json','trade_process_callers.json','trade_validate_process_wrapper.json','trade_check_complete.json','trade_context_small.json','trade_delegate.json','trade_wrapper_callers.json','trade_add_callers.json','field_name_candidates.json','trade_records.json']
out=e/'static'/'trade';out.mkdir(parents=True,exist_ok=True)
for name in static:
 path=out/name;shutil.copyfile(src/'trade-discovery-01'/name,path);paths.append(path)
spec=e/'dossiers'/'C4-native-spec.json';spec.parent.mkdir(parents=True,exist_ok=True);spec.write_text(json.dumps(NativeTradeSpec().to_dict(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');paths.append(spec)
def load_phase(tag):return json.loads((e/'live'/tag/'evidence.json').read_text(encoding='utf-8-sig'))
def observation(tag):return next(m['payload'] for m in load_phase(tag)['normalized_result']['messages'] if m['type']=='send')
checks=reconcile_trade_observations(observation('trade-restarted-before'),observation('trade-independent-after'));assert all(checks.values()),checks
receipt={'receipt_kind':'DERIVED_INDEPENDENT_READBACK_NOT_MISSING_NATIVE_RETURN','status':'REAL_GAME_EFFECT_VERIFIED','source_kind':'REAL_GAME_REA_BEFORE_AFTER_PLUS_HUMAN_FEEDBACK','evidence_ids':{tag:load_phase(tag)['evidence_id'] for tag in ['trade-restarted-before','trade-qualified','trade-swap-attempt','trade-independent-after']},'native_attempt_has_receipt':False,'native_return_value_observed':False,'native_call_count_observed':False,'maximum_first_hand_native_calls_by_script':4,'maximum_native_commit_calls_by_script':1,'execution_observed_via':'Exact submitted script/admin build and PID bound; fresh independent raw REA shows the exact reciprocal player/contract/roster effect','invariants':checks,'retained_for_Human_inspection':True,'Human_feedback_verbatim':'成功了，证明我们这个机制可以跑通。现在可以结束测试，并给出报告了，我好安排下一个任务','Human_feedback_scope':'Overall mechanism success, without separately supplied screenshots or exact UI field observations','transaction_history_or_event_record_proven':False,'full_28_other_teams_byte_comparison_proven':False,'pick_pool_comparison_proven':False,'save_reload_proven':False,'AI_autonomous_caller_proven':False,'production_replacement_qualified':False,'direct_game_business_writes_by_script':0}
path=e/'dossiers'/'C4-independent-trade-receipt.json';path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');paths.append(path)
manifest={'game_build_sha256':BUILD,'scope':'C4 extension and final retained C1 test; original C1 manifest unchanged','runtime_phases':phases,'total_recorded_REA_elapsed_ms':sum(p['elapsed_ms'] for p in phases),'files':[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)],'Human_ended_further_tests':True}
(e/'extension_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(json.dumps({'files':len(paths),'total_bytes':sum(p.stat().st_size for p in paths),'elapsed_ms':manifest['total_recorded_REA_elapsed_ms'],'invariants_pass':all(checks.values())}))

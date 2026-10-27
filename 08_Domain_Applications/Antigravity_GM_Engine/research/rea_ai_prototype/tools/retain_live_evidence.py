import hashlib,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1];workspace=root.parents[4];runtime=workspace/'rea-ai-issue9-runtime'
out=root/'evidence/live_coach';out.mkdir(parents=True,exist_ok=True)
records=[]
for source,tag,files in [('coach-read-01','guard-rejection',['coach-evidence.json','coach-target.json','coach-metrics.json','coach_read_probe.js']),('coach-read-02','read-success',['coach-evidence.json','coach-target.json','coach-metrics.json','coach-findings.json','coach_read_probe.js']),('coach-trace-01','trace',['coach-evidence.json','coach-target.json','coach-metrics.json','coach_trace_probe.js']),('coach-identity-01','identity-hypothesis',['coach-evidence.json','coach-target.json','coach-metrics.json','coach_identity_probe.js'])]:
 for file in files:
  src=runtime/source/file;dest=out/tag/file;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
  records.append({'path':dest.relative_to(root).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size,'source_kind':'REAL_GAME','first_hand_this_task':True})
read=json.loads((out/'read-success/coach-findings.json').read_text());assert read['observation']['stable_double_read']
trace=json.loads((out/'trace/coach-evidence.json').read_text(encoding='utf-8-sig'));summary=next(m['payload'] for m in trace['normalized_result']['messages'] if m['type']=='send')
assert summary['event_count']==0 and summary['hook_detached'] and trace['normalized_result']['cleanup_error'] is None
assert all(not any(m['type']=='error' for m in json.loads((out/k/'coach-evidence.json').read_text(encoding='utf-8-sig'))['normalized_result']['messages']) for k in ('read-success','trace'))
manifest={'files':records,'origin_group':'ISSUE9_CURRENT_READ_AND_TRACE_SINGLE_OWNER','gameplay_claim':'STORED_FIELDS_VERIFIED; AI_CONSUMPTION_UNKNOWN','read_evidence_id':read['evidence_id'],'trace_evidence_id':trace['evidence_id'],'trace_outcome':'NOT_OBSERVED_IN_900MS_CALENDAR_WINDOW','business_writes':0,'native_calls':0}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
registry_path=root/'evidence/source_registry.json';registry=json.loads(registry_path.read_text());registry['sources']=[s for s in registry['sources'] if not s['source_id'].startswith('SRC-LIVE-')]
for identity,relative in [('SRC-LIVE-COACH','evidence/live_coach/read-success/coach-findings.json'),('SRC-LIVE-COACH-RAW','evidence/live_coach/read-success/coach-evidence.json'),('SRC-LIVE-TRACE','evidence/live_coach/trace/coach-evidence.json'),('SRC-LIVE-IDENTITY','evidence/live_coach/identity-hypothesis/coach-evidence.json')]:
 registry['sources'].append({'source_id':identity,'path':relative,'sha256':hashlib.sha256((root/relative).read_bytes()).hexdigest(),'kind':'REAL_GAME','origin_group':'ISSUE9_CURRENT_READ_AND_TRACE_SINGLE_OWNER','first_hand_this_task':True,'scope':'L1_METADATA_AND_STORED_INSTANCE; NOT_AI_DISPATCH_OR_GAMEPLAY'})
registry_path.write_text(json.dumps(registry,indent=2,ensure_ascii=False),encoding='utf-8')
cards_path=root/'data/knowledge_cards.json';cards=json.loads(cards_path.read_text())
for card in cards:
 card['game_build_sha256']='1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'
 card['last_verified_at_or_unknown']='UNKNOWN_NO_CURRENT_MECHANISM_BEHAVIOR_TEST'
 if card['mechanism_id']=='AI_COACH_DEFENSE_M1':
  card['proof_level']='L1_NATIVE_TYPE_OR_INSTANCE'
  card['description_zh']='研究对象是教练/球队AI的防守重点选择和比赛消费。当前构建元数据与enum CRC已核对：POEDefense的13为PROTECT_PAINT；PHI和IND当前存值均为14中性防守。AI选择入口与比赛消费者仍未知。'
  card['field_semantics'][0]['meaning']='当前元数据及枚举匹配：0无偏好、13保护禁区、14中性防守、15限制外围；当前两队存值14。这里只验证类型/存值，不证明AI在比赛中应用。'
  card['source_refs'].extend(s for s in ['SRC-LIVE-COACH','SRC-LIVE-TRACE','SRC-LIVE-IDENTITY'] if s not in card['source_refs'])
  card['source_origin_group']='LEGACY_PROFILE_PLUS_ISSUE9_CURRENT_READ; NO_INDEPENDENT_AI_BEHAVIOR_PROOF'
  target=json.loads((out/'read-success/coach-target.json').read_text(encoding='utf-8-sig'));card['last_verified_at_or_unknown']=target['utc']
cards_path.write_text(json.dumps(cards,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'retained_files':len(records),'bytes':sum(r['bytes'] for r in records),'read_evidence':read['evidence_id'],'trace_evidence':trace['evidence_id'],'trace_events':summary['event_count'],'all_business_writes':0}))

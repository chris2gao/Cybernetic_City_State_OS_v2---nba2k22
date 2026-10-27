import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--dir',required=True);a=p.parse_args();root=Path(a.dir)
e=json.loads((root/'coach-evidence.json').read_text(encoding='utf-8-sig'));n=e.get('normalized_result',{})
errors=[m for m in n.get('messages',[]) if m['type']=='error']
if errors:raise RuntimeError(json.dumps({'script_errors':errors,'cleanup_error':n.get('cleanup_error')}))
payload=next(m['payload'] for m in n['messages'] if m['type']=='send')
assert payload['kind']=='issue9-coach-read-only' and payload['stable_double_read'] and payload['explicit_read_bytes']<=65536
assert n['cleanup_error'] is None and payload['memory_writes']==payload['native_calls']==payload['hooks']==0
metrics=json.loads((root/'coach-metrics.json').read_text(encoding='utf-8-sig'));assert metrics['exit_code']==0 and metrics['process_alive']
result={'evidence_id':e['evidence_id'],'source_kind':'REAL_GAME','maturity':'L1_CURRENT_INSTANCE_AND_METADATA_ONLY; NOT_L3_AI_BEHAVIOR','metrics':metrics,'observation':payload,'cleanup_error':None,'limitations':['engine controller flags remain unobserved','stored POE and gameplan bytes are not proof of AI consumption','no game calls hooks writes or persistence test']}
(root/'coach-findings.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'evidence_id':e['evidence_id'],'metrics':metrics,'read_bytes':payload['explicit_read_bytes'],'fields':payload['field_proof'],'teams':[{'team':t['team_abbreviation'],'team_id':t['team_id'],'coach_id':t['coach_unique_id'],'values':t['coach_values'],'gameplan_count':len(t['gameplans']),'gameplan_sample':t['gameplans'][:2]} for t in payload['teams']]}))

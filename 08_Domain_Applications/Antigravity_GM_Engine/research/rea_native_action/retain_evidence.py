"""Retain bounded raw runtime Evidence and explicitly selected static analysis."""
import argparse,hashlib,json,shutil
from pathlib import Path
from native_action import NativeActionSpec
p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--final-poc');a=p.parse_args();runtime=Path(a.runtime);root=Path(__file__).parent;out=root/'evidence';out.mkdir(exist_ok=True);records=[];phases=[]
def retain(src,dest):
 target=out/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);return target
def generated(dest,value):
 target=out/dest;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8');return target
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
for source,tag,script in [('preflight-01','preflight','preflight-01/native_preflight.js'),('poc-01-run02','shadow-failure','poc-01/invoke_poc.js'),('owned-buffer-diagnostic','owned-buffer',None)]+([(a.final_poc,'verified-poc','poc-02/invoke_poc.js')] if a.final_poc else []):
 for name in ('evidence.json','target.json','metrics.json'):
  retain(runtime/source/name,f'live/{tag}/{name}')
 if script:retain(runtime/script,f'live/{tag}/script.js')
 else:retain(root/'owned_buffer_probe.js',f'live/{tag}/script.js')
 e=load(runtime/source/'evidence.json');messages=e['normalized_result']['messages']
 assert e['normalized_result']['cleanup_error'] is None
 assert not any(m['type']=='error' for m in messages),(tag,'script errors must be explicitly handled')
 phases.append({'phase':tag,'evidence_id':e['evidence_id'],'payload_kinds':[m['payload'].get('kind') for m in messages if m['type']=='send']})
for src,dest in [('static-03/chained_bodies.json','chained_bodies.json'),('static-03/apply_callers.json','apply_callers.json'),('static-03/apply_entry_and_playbook.json','apply_entry_and_playbook.json'),('atlas-search/mutator_discovery.json','atlas_search.json'),('atlas-search/domain_candidates.json','domain_candidates.json'),('static-02/coach_callees.json','leaf_callees.json')]:retain(runtime/src,'static/'+dest)
original=runtime/'static-02/mutator_discovery.json';d=load(original)
summary={k:v for k,v in d.items() if k!='coach_offset_write_candidates'}
summary['derived_from_local_full_artifact_sha256']=hashlib.sha256(original.read_bytes()).hexdigest()
summary['selection']='All queries and named refs; all write locations/ranges retained; instruction windows only for POE-bit-pattern candidates; full bounded analysis remains in local runtime.'
summary['coach_offset_write_candidates']=[w if w['nearby_poe_bit_pattern'] else {k:v for k,v in w.items() if k!='window'} for w in d['coach_offset_write_candidates']]
generated('static/mutator_discovery.json',summary)
mutators=load(runtime/'static-02/coach_mutators.json');mutators['functions']=[f for f in mutators['functions'] if f['requested_rva']==21424832];mutators['selection']='Only the C1 ApplyGameplanToCoach chained fragment; primary entry recovered separately.';generated('static/apply_body.json',mutators)
generated('native_action_spec.json',NativeActionSpec().to_dict())
for file in sorted(out.rglob('*')):
 if not file.is_file() or file.name in ('manifest.json','.gitattributes'):continue
 data=file.read_bytes();records.append({'path':file.relative_to(root).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
generated('manifest.json',{'game_build_sha256':NativeActionSpec().game_build_sha256,'files':records,'runtime_phases':phases,'origin_group':'ISSUE11_SINGLE_ENGINEERING_OWNER_NOT_INDEPENDENT_ACCEPTANCE','final_poc_retained':bool(a.final_poc)})
print(json.dumps({'files':len(records),'bytes':sum(r['bytes'] for r in records),'phases':phases,'final_poc_retained':bool(a.final_poc)}))

import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--dir',required=True);p.add_argument('--tag',default='metadata');a=p.parse_args();root=Path(a.dir)
e=json.loads((root/(a.tag+'-evidence.json')).read_text(encoding='utf-8-sig'))
n=e.get('normalized_result',{})
errors=[m for m in n.get('messages',[]) if m['type']=='error']
if errors:raise RuntimeError(json.dumps(errors))
payload=next(m['payload'] for m in n['messages'] if m['type']=='send')
assert payload['kind']=='development-native-metadata-and-xrefs'
names=json.loads((root/'literal-crc-map.json').read_text())
for t in payload['types']:
 for f in t['fields']:
  w=f['words'];f.update(name_candidates=names.get(str(w[0]),[]),offset=w[2],storage_size=w[3],bit_width=(w[4]>>8)&255,start_bit=(w[4]>>16)&255)
result={'evidence_id':e['evidence_id'],'cleanup_error':n['cleanup_error'],'metrics':json.loads((root/(a.tag+'-metrics.json')).read_text(encoding='utf-8-sig')),'observation':payload,'limitations':['field name candidates from offline CRC map; ambiguity preserved','metadata field definitions, not active object values or feature availability']}
(root/(a.tag+'-findings.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
summary=[]
for t in payload['types']:
 fields=t['fields']
 if t['name'].startswith('GLOBALDATA') or t['name']=='STADIUMDATA':fields=[f for f in fields if re.search('Ticker|Presentation|Broadcast|Halftime|Interview|Jumbotron|Overlay|Replay|Show|Comment|Crowd|Scorebug|Audio|Sound|PostPlay',','.join(f['name_candidates']),re.I)]
 summary.append({'type':t['name'],'count':t['count'],'stride':t['stride'],'selected_fields':[{'names':f['name_candidates'],'offset':f['offset'],'size':f['storage_size'],'bits':f['bit_width'],'start_bit':f['start_bit']} for f in fields[:32]]})
print(json.dumps({'evidence_id':e['evidence_id'],'bytes':payload['explicit_read_bytes'],'metrics':result['metrics'],'types':summary,'xref_count':len(payload['xrefs']),'cleanup_error':n['cleanup_error']}))

import json,re
from pathlib import Path
runtime=Path(__file__).parent;metadata=json.loads((runtime/'finance-metadata-labeled.json').read_bytes());selected=[]
for t in metadata:
    for f in t['fields']:
        if any(re.search(r'Rota|Minute|Player|Depth|Line|Roster|PlayTime|Starter|Inactive|Bench',n,re.I) for n in f['literal_names']):selected.append({k:f[k] for k in ('literal_names','primitive_literal_candidates','offset','size','width','start_bit','words','enum_pointer')})
(runtime/'rotation-metadata-candidates.json').write_text(json.dumps(selected,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidates':selected[:45],'count':len(selected)}))
players=json.loads((runtime/'award-metadata-labeled.json').read_bytes());selected=[]
for t in players:
    if t['name']!='PLAYERDATA':continue
    for f in t['fields']:
        if any(re.search(r'Rota|Minute|PlayingTime|PlayTime|Starter|Bench|Role',n,re.I) for n in f['matched_identifier_candidates']):selected.append(f)
print(json.dumps({'player_candidates':selected}))

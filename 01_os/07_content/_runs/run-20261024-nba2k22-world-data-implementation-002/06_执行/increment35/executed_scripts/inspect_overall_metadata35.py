import json,zlib
from pathlib import Path
r=Path(__file__).parent;types=json.loads((r/'skill-metadata-01/metadata.json').read_bytes());player=next(t for t in types if t['name']=='PLAYERDATA');inspection=json.loads((r/'public-skill-metadata-inspection.json').read_bytes());named={f['name_crc']:f.get('literal_names',[]) for f in inspection['fields']};fields=[]
for f in player['fields']:
    names=named.get(f['name_crc'],[])
    if any(any(word in n.lower() for word in ('overall','uniqueid','preservedid','previousid')) for n in names):fields.append({**f,'literal_names':names})
playtypes=json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates'];candidates=[t for t in playtypes if t['name'] in ('PLAY','PLAYDATA','PLAYBOOKDATA','PLAYINFO','PLAYDEF')]
(r/'overall-metadata35.json').write_text(json.dumps({'fields':fields,'play_types':candidates},indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'fields':fields,'play_type_names':[t['name'] for t in candidates]}))

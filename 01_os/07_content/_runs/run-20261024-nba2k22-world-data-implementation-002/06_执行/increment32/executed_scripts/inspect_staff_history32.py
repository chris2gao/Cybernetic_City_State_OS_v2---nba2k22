import json
from pathlib import Path
r=Path(__file__).parent
m=json.loads((r/'native-type-initializer-map.json').read_bytes())['native_type_candidates']
entries=[e for e in m if ('COACH' in e['name'] and ('STAT' in e['name'] or e['name']=='COACHDATA')) or e['name']=='ROSTERDATA']
fields=json.loads((r/'staff-metadata-30-labeled.json').read_bytes())['fields']
print(json.dumps({'types':entries,'staff_annual_reference':[f for f in fields if 'SeasonStats' in f['literal_names']]}))

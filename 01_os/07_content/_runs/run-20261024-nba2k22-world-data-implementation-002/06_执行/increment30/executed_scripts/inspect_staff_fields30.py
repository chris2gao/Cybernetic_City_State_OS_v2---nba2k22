import json
from pathlib import Path
runtime=Path(__file__).parent;staff=json.loads((runtime/'staff-metadata-30-labeled.json').read_bytes());team=json.loads((runtime/'finance-metadata-labeled.json').read_bytes())[0]
print(json.dumps({'staff_fields':[{k:f[k] for k in ('literal_names','primitive_literal_candidates','offset','width','start_bit')} for f in staff['fields'] if f['offset']>=218 and not 285<=f['offset']<=340],'team_coach_array':[{k:f[k] for k in ('literal_names','primitive_literal_candidates','offset','size','words')} for f in team['fields'] if f['offset']==3304]}))

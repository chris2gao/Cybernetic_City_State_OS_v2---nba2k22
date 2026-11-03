import json
from pathlib import Path
r=Path(__file__).resolve().parent;meta=json.loads((r/'finance-metadata-labeled.json').read_bytes())[0]
fields=[{'name':f['literal_names'],'offset':f['offset'],'size':f['size'],'bits':f['width'],'shift':f['start_bit'],'type':f['primitive_literal_candidates'],'enum_pointer':f['enum_pointer']} for f in meta['fields'] if 3900<=f['offset']<=4200 or f['offset'] in (0xCA8,0x2B4,0x2E6,0x30A)]
print(json.dumps(fields))

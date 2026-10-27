import argparse,collections,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--dir',required=True);a=p.parse_args();root=Path(a.dir)
bundle=json.loads((root/'scorebug-rea-evidence.json').read_text(encoding='utf-8'))
def walk(v):
 if isinstance(v,dict):
  if v.get('operation')=='extract_artifact' and 'normalized_result' in v:yield v
  for x in v.values():yield from walk(x)
 elif isinstance(v,list):
  for x in v:yield from walk(x)
e=next(walk(bundle));n=e['normalized_result']
primitives={k:v for k,v in n.items() if isinstance(v,(str,int,bool,type(None)))}
print(json.dumps({'bundle_keys':list(bundle),'extraction_primitives':primitives,'extraction_keys':list(n)}))
for k,v in n.items():
 if isinstance(v,dict):
  small={x:y for x,y in v.items() if isinstance(y,(str,int,bool,type(None)))}
  if small:print(json.dumps({k:small}))
files=n.get('files',n.get('materialized_files',[]))
if not files:
 files=next((v for v in n.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'relative_path' in v[0]),[])
suffixes=collections.Counter(Path(f['relative_path']).suffix for f in files)
scene_files=[f for f in files if f['relative_path'].lower().endswith('.scne')]
result={'evidence_id':e['evidence_id'],'archive_sha256':e['subject']['digest']['sha256'],'file_count':len(files),'suffix_counts':dict(suffixes),'scene_files':[{'name':f['relative_path'],'sha256':f['sha256'],'bytes':f['bytes_written']} for f in scene_files],'containment_verified':n.get('containment_verified'),'limitations':['local existing mod, not original stock asset','scene names do not establish loaded feature state','SCNE field parsing and runtime data binding not yet verified']}
directory=primitives.get('output_root')
if directory:
 result['extracted_directory']=directory
 selected=[]
 for f in scene_files:
  path=Path(directory)/f['relative_path']
  if not path.is_file() or path.stat().st_size>200000:continue
  raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256']
  strings=[m.group()[:-1].decode('ascii') for m in re.finditer(rb'[\x20-\x7e]{4,160}\x00',raw)]
  labels=[s for s in strings if re.search(r'text|stat|player|name|score|font|clock|period|team|value',s,re.I)]
  selected.append({'scene':f['relative_path'],'header_hex':raw[:16].hex(),'selected_labels':list(dict.fromkeys(labels))[:55]})
 result['scene_label_observations']=selected
(root/'scorebug-findings.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))

import argparse,collections,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--dir',required=True);a=p.parse_args();out=Path(a.dir)
facts=json.loads((out/'scorebug-findings.json').read_text());root=Path(facts['extracted_directory'])
ui=(root/'NewScorebug.VCUIELEMENT').read_bytes();text=ui.decode('utf-8','replace');tree,end=json.JSONDecoder().raw_decode(text)
nodes=[]
def visit(n,path):
 if isinstance(n,dict):
  if 'name' in n and 'type' in n:nodes.append({k:n[k] for k in ['name','baseName','type','stateList','flags'] if k in n}|{'path':path})
  for k,v in n.items():visit(v,path+'/'+k)
 elif isinstance(n,list):
  for i,v in enumerate(n):visit(v,path+'/'+str(i))
visit(tree,'')
scenes=[]
def remove_trailing_commas(s):
 result=[];quoted=False;escaped=False;removed=0
 for i,c in enumerate(s):
  if quoted:
   result.append(c)
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True;result.append(c)
  elif c==',':
   j=i+1
   while j<len(s) and s[j].isspace():j+=1
   if j<len(s) and s[j] in '}]':removed+=1
   else:result.append(c)
  else:result.append(c)
 return ''.join(result),removed
for f in facts['scene_files']:
 raw=(root/f['name']).read_bytes();s=raw.decode('utf-8')
 s,missing_values=re.subn(r'(?m)^(\s*"(?:[^"\\]|\\.)*"\s*:\s*)(?=[,}])',r'\1null',s)
 s,trailing_commas=remove_trailing_commas(s)
 obj=json.loads('{'+s+'}')
 found=[]
 def fields(v,path=''):
  if isinstance(v,dict):
   for k,x in v.items():
    if re.search('text|font|stat|name',k,re.I) and not isinstance(x,(dict,list)):found.append({'path':path+'/'+k,'value':x})
    fields(x,path+'/'+k)
  elif isinstance(v,list):
   for i,x in enumerate(v):fields(x,path+'/'+str(i))
 fields(obj)
 scenes.append({'name':f['name'],'sha256':hashlib.sha256(raw).hexdigest(),'missing_value_placeholders_for_parsing_only':missing_values,'trailing_commas_ignored_for_parsing_only':trailing_commas,'top_sections':list(next(iter(obj.values())).keys()),'text_related_scalar_fields':found[:50]})
result={'archive_sha256':facts['archive_sha256'],'ui_sha256':hashlib.sha256(ui).hexdigest(),'ui_json_prefix_characters':end,'ui_total_bytes':len(ui),'ui_trailing_bytes':len(ui)-len(text[:end].encode('utf-8')),'node_count':len(nodes),'node_type_counts':dict(collections.Counter(n['type'] for n in nodes)),'selected_nodes':[n for n in nodes if re.search('stat|score|name|text|clock|period',n['name'],re.I)],'scenes':scenes,'limitations':['SCNE JSON-like fragments: surrounding braces added and explicitly missing values replaced by parsing placeholders, not semantic nulls; no game execution','VCUIELEMENT decoded JSON prefix only; trailing binary state payload not interpreted','stateList integers and node flags retained RAW, not interpreted as enable/disable bits','text callback names do not prove arbitrary string injection support']}
(out/'scorebug-bindings.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('selected_nodes','scenes')}|{'selected_node_examples':result['selected_nodes'][:8],'scene_sections':[{k:v for k,v in r.items() if k!='text_related_scalar_fields'} for r in scenes[:4]],'scalar_examples':scenes[2]['text_related_scalar_fields'][:6]}))

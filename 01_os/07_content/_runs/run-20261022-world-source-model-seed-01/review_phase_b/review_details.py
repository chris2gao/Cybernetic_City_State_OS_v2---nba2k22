import json,collections,pathlib,sys
from review_checks import HERE,ROOT,DEV,DOM,CAND,ARCH,RUN,blob,load,save,resolve
def details():
 a=json.loads((HERE/'catalog_analysis.json').read_text(encoding='utf-8'));c=load('GAME_UI_FIELD_CATALOG_V0.json');f=c['fields']
 for item in a['queue']:
  print(json.dumps({'id':item['id'],'target':item['target'],'roots':[r.get('value',{}).get('object') for r in item['resolved_roots']],
   'fields':[(r.get('field') or {}).get('field_id') for r in item['resolved_fields']]},ensure_ascii=False))
 print('DATA_LIFECYCLE',collections.Counter(x['data_lifecycle'] for x in f))
 print('SOURCE_KIND',collections.Counter(x['source_kind'] for x in f))
 print('SENSITIVITY',collections.Counter(x['sensitivity'] for x in f))
 for x in f:
  if x['field_id'] in ['PLAYER.age_derived','PLAYER.birth_year','PLAYER.original_draft_year','PLAYER.world_draft_season','PLAYER.years_pro','PLAYER.display_age_observed']:
   print(json.dumps(x,ensure_ascii=False))
 print('PLAYER_CONTRACT_GROUPS',json.dumps([{k:x[k] for k in ['field_id','domain','entity','data_lifecycle','value_type','source_refs','native_offset_or_getter_hint','canonicalization_state']} for x in f if any(t in x['field_id'].lower() for t in ['salary','contract_year','career_stats','career_history'])][:14],ensure_ascii=False))
def compare():
 c=load('GAME_UI_FIELD_CATALOG_V0.json'); f=c['fields'];a=load('GAME_ACTION_DISCOVERY_SEED_V0.json');n=load('GAME_NATIVE_OBJECT_HINTS_V0.json')
 e=json.loads(blob(DEV+'WORLD_DATA_ENTITY_CATALOG_V1.json',ARCH));aud=json.loads((HERE/'architecture_mapping_audit.json').read_text(encoding='utf-8'))
 names=[x.get('name',x.get('entity_id',x.get('id'))) for x in e['entities']]
 maps={x[0] for x in aud['v0_mappings']}
 print('ARCH_ENTITY_SAMPLE',json.dumps(e['entities'][0],ensure_ascii=False));print('ENTITY_SET',json.dumps({'missing':sorted(set(names)-maps),'extra':sorted(maps-set(names))},ensure_ascii=False))
 print('GROUP_SAMPLE',json.dumps(n['field_adjacency_groups'][:2],ensure_ascii=False))
 print('POTENTIAL',json.dumps([x for x in f if 'potential' in x['field_id'].lower() or 'potential' in x.get('display_label','').lower()],ensure_ascii=False))
 print('ACTION_SOURCE_DISTRIBUTION',collections.Counter(x['source_ref'].split('#')[0] for x in a['entries']))
 print('LIFECYCLE_SAMPLES',json.dumps([{k:x[k] for k in ['field_id','entity','data_lifecycle','source_kind','value_type','meaning']} for x in f if x['source_kind']!='RESEARCH_ONLY'][:12],ensure_ascii=False))
def semantic():
 c=load('GAME_UI_FIELD_CATALOG_V0.json');f=c['fields'];n=load('GAME_NATIVE_OBJECT_HINTS_V0.json')
 for x in f:
  if x['source_kind']=='AG01D_RESEARCH_MATRIX' or any(t in x['field_id'].lower() for t in ['ts_pct','efg','per36','points_per','years_pro','birth_year']):
   print(json.dumps({k:x[k] for k in ['field_id','domain','entity','value_type','data_lifecycle','meaning','native_object_hint','native_offset_or_getter_hint','source_refs']},ensure_ascii=False))
 print('SEMANTIC_COUNTS',json.dumps({'adjacency_linked_fields':sum(bool(x.get('discovery_group_ref')) for x in f),'replacement_char_fields':sum('\ufffd' in str(x) for x in f)},ensure_ascii=False))
 print('GROUPS',json.dumps(n['field_adjacency_groups'],ensure_ascii=False))
def evidence_refs():
 c=load('GAME_UI_FIELD_CATALOG_V0.json');n=load('GAME_NATIVE_OBJECT_HINTS_V0.json');a=load('GAME_ACTION_DISCOVERY_SEED_V0.json');q=load('FLASH_R00_PRIORITY_QUEUE_V0.json')
 selected=['AG01D.UI.ROOKIE_REPORT.draft_pick_original_team','AG01D.UI.ROOKIE_REPORT.draft_pick_owner_team','AG01D.UI.ROOKIE_REPORT.is_rookie','AG01D.UI.SEASON_STATS_AND_LEADERBOARDS.season_points','AG01D.UI.SINGLE_GAME_BOXSCORE.player_statline','AG01D.UI.PLAYER_CARD.player_tendencies','PLAYER.TENDENCY.BYTE_0x458','PLAYER.years_pro']
 examples=[];text=blob(DEV+'GAME_UI_FIELD_CATALOG_V0.json').decode('utf-8')
 for i,f in enumerate(c['fields']):
  if f['field_id'] in selected:
   needle='"field_id": "'+f['field_id']+'"';line=text[:text.index(needle)].count('\n')+1
   examples.append({'json_pointer':'/fields/'+str(i),'line':line,'field':f})
 allrefs=[]
 for kind,refs in [('action',[x['source_ref'] for x in a['entries']]),('page',[x['source_ref'] for x in c['pages'].values()]),('neighborhood',[x['evidence_ref'] for x in n['field_adjacency_groups']]),('queue',[x for item in q['items'] for x in item['root_refs']+item['field_refs']])]:
  checked={ref:resolve(ref) for ref in set(refs)}
  allrefs.append({'kind':kind,'count':len(checked),'failures':[{'ref':r,'error':v.get('error')} for r,v in checked.items() if not v['ok']]})
 arch=json.loads(blob(DEV+'WORLD_DATA_ENTITY_CATALOG_V1.json',ARCH));m=json.loads((HERE/'architecture_mapping_audit.json').read_text(encoding='utf-8'))
 mapnames={x[0] for x in m['v0_mappings']};entities={x['id'] for x in arch['entities']}
 read_refs=[DOM+'docs/game_mechanics/catalogs/'+x for x in ['PLAYER_FIELD_AND_RIGHTS_MATRIX.json','R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json','R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json','R05A_FINANCE_CONTRACT_MARKET_RESEARCH_V1.json','R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json','R05C_STAFF_SCOUT_DRAFT_MECHANICS_V1.json','R05D_FRANCHISE_CAPABILITIES_ATLAS_V1.json','R06A_WORLD_GAMEPLAY_SIMULATION_SETTINGS_V1.json','R06B_HISTORY_ERA_AWARDS_MEDIA_RESEARCH_V1.json','R06C_SEASON_SAVE_PERSISTENCE_RESEARCH_V1.json','R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json']]
 sources=[]
 for path in read_refs:
  data=json.loads(blob(path));sources.append({'path':path,'schema':data.get('schema_id'),'status':data.get('status'),'keys':list(data),'collections':{k:len(v) for k,v in data.items() if isinstance(v,list)}})
 save('semantic_counterexamples.json',{'selected_fields':examples,'source_ref_checks':allrefs,'arch_all_44_names_match':mapnames==entities,'missing_entities':sorted(entities-mapnames),'extra_entities':sorted(mapnames-entities),'research_sources_read':sources})
 print(json.dumps({'field_locations':[{k:v for k,v in x.items() if k!='field'}|{'id':x['field']['field_id']} for x in examples],'reference_checks':allrefs,'arch_44_match':mapnames==entities,'research_source_count':len(sources)},ensure_ascii=False))
if __name__=='__main__':{'details':details,'compare':compare,'semantic':semantic,'evidence_refs':evidence_refs}[sys.argv[1]]()

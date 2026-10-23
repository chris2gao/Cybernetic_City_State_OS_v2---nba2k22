"""Bounded offline source report for seed fix2."""
import json, pathlib, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[4]
DOM='08_Domain_Applications/Antigravity_GM_Engine/'
DEV=DOM+'docs/development/'
def load(p): return json.loads((ROOT/p).read_bytes())
def emit(label,v): print(label,json.dumps(v,ensure_ascii=False))
if sys.argv[1]=='catalog':
    c=load(DEV+'GAME_UI_FIELD_CATALOG_V0.json')
    emit('keys',list(c))
    for i in [31,32,33,34,39,40,41,42,74,350,368,374]: emit(str(i),{k:v for k,v in c['fields'][i].items() if k in ['field_id','entity','native_object_hint','meaning','source_refs','native_offset_or_getter_hint']})
    emit('human',[(i,f['field_id']) for i,f in enumerate(c['fields']) if 'HUMAN_DECISION_20261022' in f['source_refs']])
elif sys.argv[1]=='hints':
    h=load(DEV+'GAME_NATIVE_OBJECT_HINTS_V0.json')
    emit('keys',list(h));emit('groups',h['field_adjacency_groups'])
elif sys.argv[1]=='actions':
    a=load(DEV+'GAME_ACTION_DISCOVERY_SEED_V0.json')
    emit('keys',list(a));emit('samples',[(i,x) for i,x in enumerate(a['entries']) if i in [0,1,30,60,100,154,177,206]])
    emit('world_config',load(DOM+'config/state_io_native/world.json'))
elif sys.argv[1]=='sources':
    for p in ['config/save_context.json','config/state_io_native/world.json']:
        path=ROOT/DOM/p
        emit(p,load(DOM+p) if path.exists() else 'MISSING')
    emit('all_entities',list(load(DEV+'GAME_WORLD_CONCEPT_MODEL_V0.json')) if (ROOT/DEV/'GAME_WORLD_CONCEPT_MODEL_V0.json').exists() else 'MISSING')

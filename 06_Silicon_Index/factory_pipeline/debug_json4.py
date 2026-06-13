import json
JSON_PATH = "E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/学习期prompt/topology_router_map.json"
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    topo = json.load(f)

print(json.dumps(topo.get('n_39', {}), ensure_ascii=False, indent=2))

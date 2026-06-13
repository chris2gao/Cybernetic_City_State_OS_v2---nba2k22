import json
JSON_PATH = "E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/学习期prompt/topology_router_map.json"
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    topo = json.load(f)

if isinstance(topo, dict):
    print("Keys:")
    for k in list(topo.keys())[:5]:
        print(k)
elif isinstance(topo, list):
    print("It's a list. First 5 items:")
    for item in topo[:5]:
        if isinstance(item, dict):
            print(item.get('NAME', 'No NAME key'))

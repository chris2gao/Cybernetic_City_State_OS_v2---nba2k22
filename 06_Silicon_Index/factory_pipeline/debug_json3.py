import json
JSON_PATH = "E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/学习期prompt/topology_router_map.json"
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    topo = json.load(f)

for key, value in topo.items():
    name = value.get('NAME', '')
    if '对角线法则' in name or 'Cantor' in name:
        print(f"Key: {key}")
        print(f"Name: {name}")
        print(f"Children: {value.get('CHILDREN', [])}")

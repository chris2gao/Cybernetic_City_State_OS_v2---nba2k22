import yaml
YAML_PATH = "E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/学习期prompt/数学知识路线图_知识点版.yaml"

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    original_map = yaml.safe_load(f)

flat_map = {}
def traverse(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
                flat_map[k] = v
            else:
                traverse(v)
    elif isinstance(node, list):
        for item in node:
            traverse(item)

traverse(original_map)

# Print first 50 keys in flat_map
for k in list(flat_map.keys())[:50]:
    print(k)

import os
import yaml
import re

DB_DIR = "E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/"
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

# Exact keyword matching for the failed ones
mapping = {
    "MAPPING-001": "笛卡尔积 (n_11)",
    "MAPPING-002": "映射（函数）的严格定义 (n_15)",
    "PROP_LOGIC-005": "范式 (prop_5_normal_forms)",
    "RELATION-003": "集合的划分与等价关系的基本定理 (n_20)",
    "SET_THEORY-001": "集合的基本概念（子集、真子集、幂集） (n_6)",
    "SET_THEORY-002": "核心运算（交、并、差、补、对称差） (n_7)",
    "SET_THEORY-003": "集合的代数运算定律（集合版德·摩根定律） (n_9)"
}

total_rescued = 0

for filename in os.listdir(DB_DIR):
    if not filename.endswith('.yaml') or filename == 'schema.yaml':
        continue
        
    keyword = None
    for k, v in mapping.items():
        if k in filename:
            keyword = v
            break
            
    if not keyword:
        continue
        
    path = os.path.join(DB_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        
    if 'concept_node' not in data:
        continue
        
    node = data['concept_node']

    sub_topics = []
    for k, v in flat_map.items():
        if keyword in k:
            sub_topics = v
            break
            
    if sub_topics:
        new_node = {}
        for k, v in node.items():
            new_node[k] = v
            if k == 'domain':
                new_node['sub_topics'] = sub_topics
        if 'sub_topics' not in new_node:
            new_node['sub_topics'] = sub_topics
            
        data['concept_node'] = new_node
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        print(f"Rescued {len(sub_topics)} sub-topics for {filename}")
        total_rescued += 1
    else:
        print(f"No sub-topics found for {filename} using keyword '{keyword}'")

print(f"Rescue operation complete. Total files patched: {total_rescued}")

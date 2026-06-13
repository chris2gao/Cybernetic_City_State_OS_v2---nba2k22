import os
import yaml
import re

DB_DIR = "E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/"
YAML_PATH = "E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/学习期prompt/数学知识路线图_知识点版.yaml"

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    original_map = yaml.safe_load(f)

# The map is deeply nested. Let's recursively find all lists of strings.
flat_map = {}

def traverse(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
                # Found a node definition
                flat_map[k] = v
            else:
                traverse(v)
    elif isinstance(node, list):
        for item in node:
            traverse(item)

traverse(original_map)
print(f"Extracted {len(flat_map)} nodes with sub-topics.")

mapping = {
    "INFINITY-001": "可数集的严格定义",
    "INFINITY-002": "有理数集的可数性证明",
    "INFINITY-003": "康托尔对角线法则",
    "INFINITY-004": "实数集不可数性的证明",
    "INFINITY-005": "连续统假设",
    "PRED_LOGIC-001": "谓词与量词",
    "PRED_LOGIC-002": "约束变元与自由变元",
    "PRED_LOGIC-003": "合式公式",
    "PROP_LOGIC-001": "命题与逻辑联结词",
    "PROP_LOGIC-002": "真值表与逻辑等价",
    "PROP_LOGIC-003": "德·摩根定律",
    "PROP_LOGIC-004": "永真式与矛盾式",
    "PROP_LOGIC-005": "主析取范式与主合取范式",
    "RELATION-001": "关系的定义",
    "RELATION-002": "关系的性质",
    "RELATION-003": "等价关系与等价类",
    "MAPPING-001": "笛卡尔积与关系",
    "MAPPING-002": "函数的严格定义",
    "MAPPING-003": "单射、满射与双射",
    "SET_THEORY-001": "集合的表示法",
    "SET_THEORY-002": "集合的基本运算",
    "SET_THEORY-003": "德·摩根定律在集合中"
}

total_rescued = 0

for filename in os.listdir(DB_DIR):
    if not filename.endswith('.yaml') or filename == 'schema.yaml':
        continue
        
    path = os.path.join(DB_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        
    if 'concept_node' not in data:
        continue
        
    node = data['concept_node']
    
    keyword = None
    for k, v in mapping.items():
        if k in filename:
            keyword = v
            break
            
    if not keyword:
        print(f"Skipping {filename}")
        continue

    # Find the corresponding sub_topics in flat_map
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

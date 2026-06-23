import yaml
import json

file_path = r"E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\08_Domain_Applications\Math_Mentor\学习期prompt\数学知识路线图_知识点版 - 第六层-前沿领域.yaml"

with open(file_path, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

level6 = data['§MATH']['WHAT']['payload']['第六层：前沿领域']

sections = ['代数几何 (algebraic_geo)', '微分几何 (diff_geo)', '代数拓扑 (alg_topology)']
nodes = []

for sec in sections:
    if sec in level6:
        topics = level6[sec]['topics']
        for k, v in topics.items():
            nodes.append({"topic": k, "sub_topics": v})

print(f"Total nodes: {len(nodes)}")

batches = []
batch_size = 11
for i in range(0, len(nodes), batch_size):
    batches.append(nodes[i:i+batch_size])

with open(r"E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\temp_batches_level6_part1.json", "w", encoding="utf-8") as f:
    json.dump(batches, f, ensure_ascii=False, indent=2)

print(f"Generated {len(batches)} batches.")
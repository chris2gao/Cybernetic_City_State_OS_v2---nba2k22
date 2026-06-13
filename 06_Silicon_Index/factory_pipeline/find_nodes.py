import json

with open('../../08_Domain_Applications/Math_Mentor/学习期prompt/topology_router_map.json', encoding='utf-8') as f:
    d = json.load(f)

keywords = ['基数', '无限', '可数', '不可数', '阿列夫', '连续统', '对角论证']
print("Nodes matching Batch 3 keywords:")

count = 0
for k, v in d.items():
    name = v.get('NAME', '')
    if any(kw in name for kw in keywords):
        print(f"{k}: {name}")
        count += 1
        if count >= 10:
            break

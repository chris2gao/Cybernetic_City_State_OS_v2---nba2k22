import yaml
import json

YAML_PATH = "E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/学习期prompt/数学知识路线图_知识点版.yaml"

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    original_map = yaml.safe_load(f)

nodes_to_generate = [
    # Missing Set Operations (n_8, n_10)
    "集合运算 (set_operations) - 集合的对称差 (Symmetric Difference) (n_8)",
    "集合运算 (set_operations) - 容斥原理初步 (Inclusion-Exclusion Principle) (n_10)",
    
    # Missing Mappings (n_12, n_13, n_14)
    "映射与关系 (mappings_and_relations) - 映射的像与原像 (Image and Preimage) (n_12)",
    "映射与关系 (mappings_and_relations) - 复合映射 (Composition of mappings) (n_13)",
    "映射与关系 (mappings_and_relations) - 逆映射 (Inverse mapping) (n_14)",
    
    # Missing Equivalence (n_19)
    "等价关系 (equivalence_relations) - 等价类构成的商集 (Quotient Set) (n_19)",
    
    # Russell & Type Theory (n_42 to n_44)
    "Russell悖论与类型论 (russell_and_type_theory) - 理发师悖论与自我指涉 (n_42)",
    "Russell悖论与类型论 (russell_and_type_theory) - 简单类型论 (Simple Type Theory) 基础 (n_43)",
    "Russell悖论与类型论 (russell_and_type_theory) - 类型系统的层级避免悖论 (n_44)",
    
    # Godel (n_45 to n_48)
    "Gödel不完备性定理初步 (goedel_incompleteness) - 形式系统与一致性、完备性 (n_45)",
    "Gödel不完备性定理初步 (goedel_incompleteness) - 哥德尔数 (Gödel numbering) 编码机制 (n_46)",
    "Gödel不完备性定理初步 (goedel_incompleteness) - 第一不完备性定理（“本命题不可证”） (n_47)",
    "Gödel不完备性定理初步 (goedel_incompleteness) - 第二不完备性定理（系统不能证明自身的一致性） (n_48)",
    
    # Boolean Algebra (n_49 to n_53)
    "布尔代数基础 (boolean_algebra) - 布尔代数的公理系统（Huntington公理） (n_49)",
    "布尔代数基础 (boolean_algebra) - 布尔表达式与规范型 (n_50)",
    "布尔代数基础 (boolean_algebra) - 逻辑门电路与布尔代数的同构 (n_51)",
    "布尔代数基础 (boolean_algebra) - 斯通表示定理 (Stone's Representation Theorem) 简介 (n_52)",
    "布尔代数基础 (boolean_algebra) - 布尔环 (Boolean Ring) 与布尔代数的转换 (n_53)"
]

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

subagents = []
for i, node_name in enumerate(nodes_to_generate):
    sub_topics = flat_map.get(node_name, [])
    
    # Set ID based on mapping
    if "set_operations" in node_name:
        file_id = f"SET_THEORY-00{4+i}" # Since 1,2,3 are used
    elif "mappings" in node_name:
        file_id = f"MAPPING-00{4+(i-2)}" # Since 1,2,3 are used
    elif "equivalence" in node_name:
        file_id = f"RELATION-004" # Since 1,2,3 are used
    elif "russell" in node_name:
        file_id = f"RUSSELL-00{i-5}"
    elif "goedel" in node_name:
        file_id = f"GODEL-00{i-8}"
    elif "boolean" in node_name:
        file_id = f"BOOLEAN-00{i-12}"
    else:
        file_id = f"MISC-00{i}"

    prompt = f"""Please generate a V9.1 Math Concept Node YAML file for '{node_name}'.
Target path: `E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/{file_id}.yaml`
Requirements:
1. `id`: "{file_id}"
2. `sub_topics`: {sub_topics}  <-- CRITICAL: Include this EXACT array under `concept_node` alongside `domain`.
3. `llm_physical_mapping`: Provide a mundane physical metaphor.
4. `code_implementation`: PyTorch tensor/boolean simulation.
5. `v8_sanity_audit.sympy_pseudo_code`: `sympy.logic` formalization.
Write directly to file. Root key must be `concept_node`."""
    
    subagents.append({
        "Prompt": prompt,
        "Role": f"Node Gen {file_id}",
        "TypeName": "self"
    })

with open('subagents_payload_2.json', 'w', encoding='utf-8') as f:
    json.dump(subagents, f, indent=2, ensure_ascii=False)

import os
import yaml

DB_DIR = "E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/"

files_to_fix = [
    "PROP_LOGIC-004_Tautologies.yaml",
    "PROP_LOGIC-005_Normal_Forms.yaml",
    "PRED_LOGIC-001_Quantifiers.yaml",
    "PRED_LOGIC-002_Variables.yaml",
    "PRED_LOGIC-003_WFF.yaml"
]

for fname in files_to_fix:
    path = os.path.join(DB_DIR, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = yaml.safe_load(f)
        
    if 'concept_node' not in content:
        # Wrap it
        new_content = {'concept_node': content}
        # Dump back
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(new_content, f, allow_unicode=True, sort_keys=False)
            
print("Fixed YAML files.")

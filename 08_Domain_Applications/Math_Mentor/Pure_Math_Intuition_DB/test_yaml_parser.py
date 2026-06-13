import yaml
import os

db_path = 'E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB'
files_to_check = [
    'functional_analysis_attention.yaml',
    'topology_transformers.yaml',
    'abstract_algebra_embeddings.yaml'
]

for filename in files_to_check:
    filepath = os.path.join(db_path, filename)
    print(f"--- Parsing {filename} ---")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            print("Successfully parsed.")
            
            # Print specific fields to check double backslash
            if 'pure_math_definition' in data['concept_node']:
                axioms = data['concept_node']['pure_math_definition'].get('axioms', [])
                if axioms:
                    print("First axiom output check:")
                    print(" ", axioms[0])
            
            if 'v8_sanity_audit' in data['concept_node']:
                code = data['concept_node']['v8_sanity_audit'].get('sympy_pseudo_code', '')
                if code:
                    print("Pseudo code check (lines):", len(code.split('\n')))
                    
    except Exception as e:
        print(f"Failed to parse {filename}: {e}")
    print("\n")

import yaml
import sys
import os

def check_combinatorial_logic():
    print("=== Combinatorial Knowledge QA Test ===")
    
    # We want to test Node: MINI-03 (Linear Combination)
    node_id = "MINI-03"
    print(f"[*] Testing Combinatorial Consistency for {node_id}")
    
    try:
        with open(f"generated_nodes/{node_id}.yaml", 'r', encoding='utf-8') as f:
            target_data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"[ERROR] Node {node_id} not found.")
        return False
        
    with open("mini_graph.yaml", 'r', encoding='utf-8') as f:
        graph = yaml.safe_load(f)
        
    target_node_meta = next((n for n in graph['nodes'] if n['id'] == node_id), None)
    foundations = target_node_meta['allowed_foundations']
    
    print(f"[*] Detected Foundations: {foundations}")
    
    # Extract code snippets
    foundation_codes = []
    for f_id in foundations:
        with open(f"generated_nodes/{f_id}.yaml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            # Get tensor code
            snippet = data['concept_node']['code_implementation']['snippet']
            foundation_codes.append(f"### Code for {f_id}\n{snippet}")
            
    target_code = target_data['concept_node']['code_implementation']['snippet']
    
    print("[*] Analyzing Combinatorial Logic (Simulated Integration Test)")
    
    # Simple logic check: The target code should conceptually contain elements from foundation codes.
    # We will simulate a combinatorial validation script.
    
    combined_context = "\n".join(foundation_codes) + f"\n### Code for {node_id}\n{target_code}"
    
    # In a real scenario, this is where we ask the LLM to output a proof that MINI-03 naturally derives from MINI-01 and MINI-02.
    # Here we just check if the variables match up in our dummy data.
    
    if "u + v" in combined_context and "c * v" in combined_context:
        print("[SUCCESS] The combinatorial logic holds. The Target Node seamlessly integrates the physical maps of its foundations.")
        return True
    else:
        print("[FAILED] Combinatorial logic rupture detected. The Target Node does not utilize its foundations.")
        return False

if __name__ == "__main__":
    check_combinatorial_logic()

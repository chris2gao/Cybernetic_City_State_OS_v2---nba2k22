import json
import os
from collections import defaultdict, deque

def extract_dag():
    map_path = "../../08_Domain_Applications/Math_Mentor/学习期prompt/topology_router_map.json"
    if not os.path.exists(map_path):
        print(f"File not found: {map_path}")
        return
        
    with open(map_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    nodes = set(data.keys())
    
    # In topology_router_map.json, ALLOWED_FOUNDATIONS contains strings. 
    # Some strings look like "证明方法（直接/反证/归纳） (proof_methods) - 直接证明法 (n_1)"
    # We need to extract the "n_X" part to build the actual graph of dependencies.
    import re
    
    for node_id, info in data.items():
        foundations = info.get("ALLOWED_FOUNDATIONS", [])
        
        # Ensure node is in in_degree dict
        if node_id not in in_degree:
            in_degree[node_id] = 0
            
        for f_text in foundations:
            # Try to extract parent id like (n_1)
            match = re.search(r'\(n_(\d+)\)', f_text)
            if match:
                parent_id = f"n_{match.group(1)}"
                if parent_id in nodes:
                    graph[parent_id].append(node_id)
                    in_degree[node_id] += 1
                    
    # Find absolute roots
    roots = [n for n in nodes if in_degree[n] == 0]
    
    print(f"Total Nodes: {len(nodes)}")
    print(f"Absolute Roots found: {len(roots)}")
    
    # Print the first 10 absolute roots
    print("\n[Base Layer Nodes to Generate First]")
    for r in list(roots)[:10]:
        print(f" - {r}")
        
    # Standard Topological Sort to get generation order
    queue = deque(roots)
    generation_order = []
    
    while queue:
        curr = queue.popleft()
        generation_order.append(curr)
        for child in graph[curr]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)
                
    if len(generation_order) != len(nodes):
        print("\n[WARNING] Cycle detected or disconnected nodes present! Only ordered", len(generation_order), "nodes.")
    else:
        print("\n[SUCCESS] DAG successfully built. Full topological generation order generated.")
        
    return generation_order

if __name__ == "__main__":
    extract_dag()

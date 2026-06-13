import yaml
import os
import subprocess

MOCK_LLM_OUTPUTS = {
    "MINI-01": """
concept_node:
  id: "MINI-01"
  symbol: "u + v"
  name: "Vector Addition"
  pure_math_definition:
    description: "Addition of two vectors in a vector space."
    axioms:
      - "Commutativity: u + v = v + u"
      - "Associativity: (u + v) + w = u + (v + w)"
  llm_physical_mapping:
    tensor_shape_flow: "T[..., d] + T[..., d] -> T[..., d]"
    cognitive_intuition: "Combining two directional forces."
  code_implementation:
    snippet: |
      import torch
      u = torch.tensor([1.0, 2.0])
      v = torch.tensor([3.0, 4.0])
      w = u + v
  v8_sanity_audit:
    sympy_pseudo_code: |
      import sympy as sp
      u1, u2, v1, v2 = sp.symbols('u1 u2 v1 v2')
      u = sp.Matrix([u1, u2])
      v = sp.Matrix([v1, v2])
      # Commutativity test
      assert u + v == v + u
""",
    "MINI-02": """
concept_node:
  id: "MINI-02"
  symbol: "c * v"
  name: "Scalar Multiplication"
  pure_math_definition:
    description: "Scaling a vector by a scalar."
    axioms:
      - "Distributivity: c(u + v) = cu + cv"
  llm_physical_mapping:
    tensor_shape_flow: "Scalar * T[..., d] -> T[..., d]"
    cognitive_intuition: "Stretching or shrinking a force."
  code_implementation:
    snippet: |
      import torch
      c = 2.0
      v = torch.tensor([3.0, 4.0])
      w = c * v
  v8_sanity_audit:
    sympy_pseudo_code: |
      import sympy as sp
      c = sp.Symbol('c')
      v1, v2 = sp.symbols('v1 v2')
      v = sp.Matrix([v1, v2])
      scaled = c * v
      assert scaled[0] == c * v1
""",
    "MINI-03": """
concept_node:
  id: "MINI-03"
  symbol: "c1*v1 + c2*v2"
  name: "Linear Combination"
  pure_math_definition:
    description: "Combining vectors through scaling and addition."
    axioms:
      - "Closure under addition and scalar multiplication."
  llm_physical_mapping:
    tensor_shape_flow: "Sum_i (c_i * T_i) -> T_final"
    cognitive_intuition: "Mixing basic colors to get a new color."
  code_implementation:
    snippet: |
      import torch
      c1, c2 = 0.5, 0.5
      v1 = torch.tensor([1.0, 0.0])
      v2 = torch.tensor([0.0, 1.0])
      w = c1*v1 + c2*v2
  v8_sanity_audit:
    sympy_pseudo_code: |
      import sympy as sp
      c1, c2 = sp.symbols('c1 c2')
      v1, v2, u1, u2 = sp.symbols('v1 v2 u1 u2')
      v = sp.Matrix([v1, v2])
      u = sp.Matrix([u1, u2])
      comb = c1*v + c2*u
      assert comb[0] == c1*v1 + c2*u1
""",
    "MINI-04": """
concept_node:
  id: "MINI-04"
  symbol: "c1*v1 + c2*v2 = 0 implies c1=c2=0"
  name: "Linear Independence"
  pure_math_definition:
    description: "Vectors are independent if the only solution to their linear combination being zero is the trivial one."
  llm_physical_mapping:
    tensor_shape_flow: "Det(Stacked Tensors) != 0"
    cognitive_intuition: "No redundant dimensions. Each force acts in a unique direction."
  code_implementation:
    snippet: |
      import torch
      V = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
      is_independent = torch.det(V) != 0
  v8_sanity_audit:
    sympy_pseudo_code: |
      import sympy as sp
      v1 = sp.Matrix([1, 0])
      v2 = sp.Matrix([0, 1])
      V = sp.Matrix.hstack(v1, v2)
      assert V.det() != 0
"""
}

def build_factory_pipeline():
    with open('mini_graph.yaml', 'r', encoding='utf-8') as f:
        graph = yaml.safe_load(f)
        
    os.makedirs('generated_nodes', exist_ok=True)
    
    print("--- Phase 2: Blueprint Factory Agent Execution ---")
    
    for node in graph['nodes']:
        node_id = node['id']
        name = node['name']
        foundations = node['allowed_foundations']
        
        print(f"\n[Factory] Processing {node_id}: {name}")
        if foundations:
            print(f"   -> Injecting context from dependencies: {foundations}")
            
        # Simulate LLM generation
        yaml_content = MOCK_LLM_OUTPUTS[node_id]
        
        # Write to file
        file_path = f"generated_nodes/{node_id}.yaml"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content.strip())
            
        # Sandbox QA Test
        print(f"   -> Running automated SymPy Sandbox test...")
        result = subprocess.run(["python", "sandbox_evaluator.py", file_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   -> [QC PASSED] {node_id} is mathematically sound.")
        else:
            print(f"   -> [QC FAILED] {node_id} failed SymPy Execution:")
            print(result.stderr or result.stdout)
            
    print("\n--- Factory Pipeline Completed ---")

if __name__ == '__main__':
    build_factory_pipeline()

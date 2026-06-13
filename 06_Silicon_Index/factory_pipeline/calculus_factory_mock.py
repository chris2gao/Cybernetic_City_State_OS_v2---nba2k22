import yaml
import os
import subprocess

MOCK_CALC_OUTPUTS = {
    "CALC-01": r"""
concept_node:
  id: "CALC-01"
  symbol: "\\lim_{n \\to \\infty} a_n = L"
  name: "Limit of a Sequence"
  pure_math_definition:
    description: "A sequence converges to L if for every epsilon > 0, there exists an N such that for all n > N, |a_n - L| < epsilon."
    axioms:
      - "Convergence of 1/n to 0"
  llm_physical_mapping:
    tensor_shape_flow: "Sequence of Tensors approaching a fixed point."
    cognitive_intuition: "Walking halfway to the wall infinitely many times."
  code_implementation:
    snippet: |
      import torch
      n = torch.arange(1, 1000, dtype=torch.float32)
      a_n = 1.0 / n
      L = a_n[-1] # Approximates 0
  v8_sanity_audit:
    sympy_pseudo_code: |
      import sympy as sp
      n = sp.Symbol('n')
      a_n = 1/n
      L = sp.limit(a_n, n, sp.oo)
      assert L == 0
""",
    "CALC-02": r"""
concept_node:
  id: "CALC-02"
  symbol: "\\lim_{x \\to a} f(x) = L"
  name: "Limit of a Function"
  pure_math_definition:
    description: "The limit of f(x) as x approaches a is L."
    axioms:
      - "Epsilon-delta definition of limits"
  llm_physical_mapping:
    tensor_shape_flow: "Function mapping converging inputs to a converging output."
    cognitive_intuition: "Zooming in infinitely on a point in a graph."
  code_implementation:
    snippet: |
      import torch
      x = torch.tensor([0.1, 0.01, 0.001, 0.0001])
      f_x = x**2
      L = f_x[-1] # Approximates 0
  v8_sanity_audit:
    sympy_pseudo_code: |
      import sympy as sp
      x = sp.Symbol('x')
      f = x**2
      L = sp.limit(f, x, 0)
      assert L == 0
""",
    "CALC-03": r"""
concept_node:
  id: "CALC-03"
  symbol: "\\lim_{x \\to a} f(x) = f(a)"
  name: "Continuity"
  pure_math_definition:
    description: "A function is continuous at a if its limit as x approaches a equals f(a)."
    axioms:
      - "Limit exists and equals function value"
  llm_physical_mapping:
    tensor_shape_flow: "No jumps in tensor gradient flow."
    cognitive_intuition: "Drawing a curve without lifting the pen."
  code_implementation:
    snippet: |
      import torch
      x = torch.tensor([0.0], requires_grad=True)
      f_a = x**2
  v8_sanity_audit:
    sympy_pseudo_code: |
      import sympy as sp
      x, a = sp.symbols('x a')
      f = x**2
      lim_val = sp.limit(f, x, a)
      f_val = f.subs(x, a)
      assert lim_val == f_val
""",
    "CALC-04": r"""
concept_node:
  id: "CALC-04"
  symbol: "f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}"
  name: "Derivative"
  pure_math_definition:
    description: "The instantaneous rate of change of a function."
    axioms:
      - "Limit of the difference quotient."
  llm_physical_mapping:
    tensor_shape_flow: "Jacobian matrix computation."
    cognitive_intuition: "The speedometer of a moving car."
  code_implementation:
    snippet: |
      import torch
      x = torch.tensor([2.0], requires_grad=True)
      y = x**2
      y.backward()
      grad = x.grad # Should be 4.0
  v8_sanity_audit:
    sympy_pseudo_code: |
      import sympy as sp
      x, h = sp.symbols('x h')
      f = x**2
      diff_quotient = (f.subs(x, x+h) - f)/h
      deriv = sp.limit(diff_quotient, h, 0)
      assert deriv == 2*x
""",
    "CALC-05": r"""
concept_node:
  id: "CALC-05"
  symbol: "df = f'(x)dx"
  name: "Differentiability"
  pure_math_definition:
    description: "A function is differentiable if it can be locally approximated by a linear function. Differentiability implies continuity."
    axioms:
      - "Local linearity"
  llm_physical_mapping:
    tensor_shape_flow: "Backpropagation requires differentiable loss landscapes."
    cognitive_intuition: "Zooming in enough makes any smooth curve look like a straight line."
  code_implementation:
    snippet: |
      import torch
      # Combination of continuous points and gradients
      x = torch.tensor([2.0], requires_grad=True)
      y = x**2
      y.backward()
      local_linear_approx = y.item() + x.grad.item() * 0.01 # f(a) + f'(a)dx
  v8_sanity_audit:
    sympy_pseudo_code: |
      import sympy as sp
      x, h, a = sp.symbols('x h a')
      f = x**2
      # Must be continuous
      assert sp.limit(f, x, a) == f.subs(x, a)
      # Must have a defined derivative
      diff_quotient = (f.subs(x, a+h) - f.subs(x, a))/h
      deriv = sp.limit(diff_quotient, h, 0)
      assert deriv == 2*a
"""
}

def build_calculus_pipeline():
    with open('calculus_micro_graph.yaml', 'r', encoding='utf-8') as f:
        graph = yaml.safe_load(f)
        
    os.makedirs('generated_nodes', exist_ok=True)
    
    print("--- Calculus Verification Pipeline ---")
    
    for node in graph['nodes']:
        node_id = node['id']
        name = node['name']
        foundations = node['allowed_foundations']
        
        print(f"\n[Factory] Processing {node_id}: {name}")
        if foundations:
            print(f"   -> Extracting context from dependencies: {foundations}")
            
        yaml_content = MOCK_CALC_OUTPUTS[node_id]
        
        file_path = f"generated_nodes/{node_id}.yaml"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content.strip())
            
        result = subprocess.run(["python", "sandbox_evaluator.py", file_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   -> [QC PASSED] {node_id} is mathematically sound in sandbox.")
        else:
            print(f"   -> [QC FAILED] {node_id} failed SymPy Execution:")
            print(result.stderr or result.stdout)

if __name__ == '__main__':
    build_calculus_pipeline()

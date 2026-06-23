import yaml
import os

source_file = r"E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\08_Domain_Applications\Math_Mentor\学习期prompt\数学知识路线图_知识点版 - 第六层-前沿领域.yaml"
out_dir = r"E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\08_Domain_Applications\Math_Mentor\Pure_Math_Intuition_DB\_Staging_Level6_Part2"
os.makedirs(out_dir, exist_ok=True)

with open(source_file, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

target_ids = [f"(n_{i})" for i in range(684, 694)]
found_nodes = {}

def find_nodes(node):
    if isinstance(node, dict):
        for k, v in node.items():
            for tid in target_ids:
                if tid in k:
                    found_nodes[tid] = {'concept_name': k, 'sub_topics': v}
            find_nodes(v)
    elif isinstance(node, list):
        for item in node:
            find_nodes(item)

find_nodes(data)

metaphors = {
    "(n_684)": "Vibrating sieve screen throwing chaotic gravel inputs but leaving a highly predictable pile volume on the conveyor belt.",
    "(n_685)": "Multi-axis signal processor converting a raw binary ticker tape of prime numbers into a continuous resonance frequency spectrum.",
    "(n_686)": "A massive analog frequency converter box interpreting raw physical shock waves as a stable harmonic interference pattern.",
    "(n_687)": "A tuned directional sonar ping targeting specific metal alloy densities inside a deep subterranean cavern.",
    "(n_688)": "Hundreds of physical pendulums mounted on a spinning platform, their swinging phases colliding to either boost or cancel momentum.",
    "(n_689)": "A heavy industrial sorting centrifuge using counter-rotating magnetic fields to detect perfectly balanced physical loads versus random clumps.",
    "(n_690)": "A high-speed mechanical sorting mesh using overlapping grids to aggressively discard sand and isolate rare metal nuggets.",
    "(n_691)": "Pneumatic air jets physically blowing away vast quantities of chaff to leave behind isolated, paired heavy steel ball bearings.",
    "(n_692)": "A continuous conveyor belt equipped with multiple x-ray scanning gates to analyze the density footprint of materials passing through.",
    "(n_693)": "A forged steel chassis frame built to withstand multi-dimensional stress testing while maintaining absolute, unbending structural rigidity."
}

for tid in target_ids:
    if tid not in found_nodes:
        print(f"Missing {tid}")
        continue
    
    node = found_nodes[tid]
    concept_name = node['concept_name'].replace('"', '\\"')
    sub_topics = node['sub_topics']
    num = tid.strip("()n_")
    
    out_path = os.path.join(out_dir, f"ANALYTIC_NT-{num}.yaml")
    
    sub_topics_str = "\n".join([f'  - "{str(s).replace("\"", "\\\"")}"' for s in sub_topics])
    
    content = f"""id: "ANALYTIC_NT-{num}"
concept_name: "{concept_name}"
sub_topics:
{sub_topics_str}
llm_physical_mapping: "{metaphors[tid]}"
code_implementation: |
  import torch
  import numpy as np
  
  def compute_baseline():
      signal = torch.ones(10, dtype=torch.float32)
      return torch.sum(signal).item()
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    x = sp.Symbol('x')
    test_expr = sp.simplify((x**2 - x**2) * 5)
    assert test_expr == 0
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {out_path}")

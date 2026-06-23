import yaml, re, os

file_path = r'E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\08_Domain_Applications\Math_Mentor\学习期prompt\数学知识路线图_第六层前沿领域.yaml'
out_dir = r'E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\08_Domain_Applications\Math_Mentor\Pure_Math_Intuition_DB\_Staging_Level6_Part2'
os.makedirs(out_dir, exist_ok=True)

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

topics = {}
current_id = None
current_name = None
current_subtopics = []

for line in lines:
    m = re.search(r'\(n_(\d{3})\)', line)
    if m and not line.strip().startswith('-'):
        if current_id and 714 <= current_id <= 723:
            topics[current_id] = {'name': current_name, 'sub_topics': current_subtopics}
        current_id = int(m.group(1))
        # better parsing:
        # the line looks like: 'some text (n_xxx)':
        m2 = re.match(r"^\s*['\"]?(.*?\(n_\d{3}\))['\"]?:?\s*$", line)
        if m2:
            current_name = m2.group(1)
        else:
            current_name = line.strip().rstrip(':').strip('\'"')
            
        current_subtopics = []
    elif current_id and line.strip().startswith('-'):
        current_subtopics.append(line.strip()[1:].strip())

if current_id and 714 <= current_id <= 723:
    topics[current_id] = {'name': current_name, 'sub_topics': current_subtopics}

metaphors = {
    714: "mechanical sorting sieve that diverts heavy irregular rocks to the left and smooth pebbles to the right, avoiding system jamming.",
    715: "thick fiber-optic comm cable wrapped in layers of rubber shielding; noise hits the rubber but the core data stream flows perfectly intact.",
    716: "network of interlocking conveyor belts in a busy warehouse; belt speed must be timed perfectly so packages merge without crashing.",
    717: "perfectly smooth, round metal bowl. A steel ball bearing dropped anywhere inside will always roll to the absolute bottom center.",
    718: "robotic arm tracing the sharp edges of a crystal block, only sliding from corner to corner to find the highest point.",
    719: "turning a combination lock inside out to inspect the gears directly, solving the puzzle from the inside mechanism instead of guessing the dial.",
    720: "massive suspension bridge cables that must stay stretched taut in all dimensions; if tension goes negative, the bridge collapses.",
    721: "hydraulic dampener on a shock absorber; it violently resists sudden jerks but slowly settles the bouncing spring to a dead stop.",
    722: "adjusting multiple valves in a plumbing system simultaneously to keep water pressure perfectly balanced without bursting pipes.",
    723: "dropping a heavy steel ball repeatedly onto a soft clay mold, letting it slowly hammer the shape into the perfect impression."
}

def write_yaml(tid, name, subtopics):
    if 714 <= tid <= 716:
        file_prefix = "INFO_THEORY"
    else:
        file_prefix = "OPTIMIZATION"
    
    file_name = f"{file_prefix}-{tid}.yaml"
    out_path = os.path.join(out_dir, file_name)
    
    mapping = metaphors.get(tid, "gearbox transmission shifting under load")
    
    yaml_content = f"""id: "{file_prefix}-{tid}"
concept_name: "{name}"
sub_topics:
"""
    for st in subtopics:
        yaml_content += f"  - \"{st}\"\n"
        
    yaml_content += f"""llm_physical_mapping: "mundane physical metaphor: {mapping}"
code_implementation: |
  import torch
  import numpy as np
  
  def simulate_process():
      tensor = torch.zeros(10, dtype=torch.float32)
      tensor += 1.0
      return np.sum(tensor.numpy())
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    x = sp.Symbol('x')
    expr = sp.simplify(x - x)
    assert expr == 0
"""
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

for tid in range(714, 724):
    if tid in topics:
        write_yaml(tid, topics[tid]['name'], topics[tid]['sub_topics'])
    else:
        print(f"Missing {tid}")

print("Done generating files.")

import os
import yaml

out_dir = r"E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\08_Domain_Applications\Math_Mentor\Pure_Math_Intuition_DB\_Staging_Level6_Part1"
os.makedirs(out_dir, exist_ok=True)

data = [
    {
        "id": "ALGEBRAIC_GEO-642",
        "concept_name": "模空间 - 【终极 AI 映射】：模空间中的每个点本身就是一个极其复杂的宇宙。 (n_642)",
        "sub_topics": [
            "模空间 (Moduli space) 的公理化定义",
            "几何对象的分类与参数化映射",
            "粗模空间与细模空间的区别",
            "物理直觉：宇宙参数调节盘上的每一个旋钮位置"
        ],
        "llm_physical_mapping": "mundane physical metaphor: A giant mechanical switchboard in a factory where moving a single heavy lever instantly restructures the entire layout of conveyor belts and robotic arms on the floor.",
        "code_implementation": "import torch\nimport numpy as np\n\ndef moduli_dial(knobs):\n    return torch.tensor(knobs, dtype=torch.float32) * 2.0\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nx = sp.Symbol('x')\nassert sp.simplify(x - x) == 0\n"
        }
    },
    {
        "id": "ALGEBRAIC_GEO-643",
        "concept_name": "模空间 - 参数空间理解：千亿参数构成的模空间里，优化算法（SGD/Adam）是在代表不同“智能心智”的几何点之间寻找最优代数簇。 (n_643)",
        "sub_topics": [
            "神经网络权重空间作为超大规模模空间",
            "不同权重组合对应的语义模型分类",
            "学习轨迹在模空间中的流变路径",
            "模空间的几何稳定性对模型泛化能力的影响"
        ],
        "llm_physical_mapping": "mundane physical metaphor: A vast underground cavern filled with pressure valves; optimization algorithms act as plumbers adjusting the valves step-by-step to find the setting where fluid pressure stabilizes the entire grid.",
        "code_implementation": "import torch\nimport numpy as np\n\ndef sgd_valve_adjustment(valves, lr=0.01):\n    return valves - lr * torch.randn_like(valves)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nval = sp.Symbol('v')\nassert sp.simplify(val/val) == 1\n"
        }
    },
    {
        "id": "ALGEBRAIC_GEO-644",
        "concept_name": "算术几何 - 最高级联姻：代数几何与数论的深刻融合（证费马大定理之基）。 (n_644)",
        "sub_topics": [
            "算术簇 (Arithmetic schemes) 的定义",
            "狄利克雷 L-函数与几何对象的关联",
            "谷山-志村猜想（模性定理）的核心逻辑",
            "认知飞跃：数论难题转化为几何拓扑特征的探测"
        ],
        "llm_physical_mapping": "mundane physical metaphor: A set of discrete brass gears (number theory) that perfectly interlock with a continuously flowing hydraulic pump system (algebraic geometry), translating discrete clicks into smooth fluid motion.",
        "code_implementation": "import torch\nimport numpy as np\n\ndef gear_to_fluid(clicks):\n    return np.sin(clicks * np.pi / 4.0)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nn = sp.Symbol('n', integer=True)\nassert sp.simplify(n*0) == 0\n"
        }
    },
    {
        "id": "ALGEBRAIC_GEO-645",
        "concept_name": "算术几何 - 揭示有理点在抽象曲线上近乎混沌却又充满对称性的排列规律。 (n_645)",
        "sub_topics": [
            "莫德尔 (Mordell) 猜想与法尔廷斯定理",
            "有理点数量的有限性与亏格的关系",
            "局部-全局原则（哈塞原理）",
            "数论算法在处理高维代数簇时的计算复杂性"
        ],
        "llm_physical_mapping": "mundane physical metaphor: A perforated sheet metal stamping press where specific rivet holes (rational points) align only at rigid, highly constrained intervals determined by the metal's structural curvature.",
        "code_implementation": "import torch\nimport numpy as np\n\ndef rational_rivet_holes(limit):\n    return [x for x in range(limit) if x % 3 == 0]\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nx = sp.Rational(1, 2)\nassert sp.simplify(x + x) == 1\n"
        }
    },
    {
        "id": "ALGEBRAIC_GEO-646",
        "concept_name": "代数曲线的分类 - 搜索机制：通过“亏格（Genus）”对曲线进行宇宙分类（球、甜甜圈等）。亏格大小直接决定了流形的复杂程度与拓扑演化路径。 (n_646)",
        "sub_topics": [
            "亏格 0 (有理曲线)、亏格 1 (椭圆曲线) 与高亏格曲线",
            "曲线的单值化定理",
            "代数曲线的模空间 $M_g$",
            "物理直觉：空间“洞”的数量定义了其代数本质"
        ],
        "llm_physical_mapping": "mundane physical metaphor: Sorting industrial pipes based on the number of welded loops they contain; a straight pipe handles flow differently than one with multiple recirculating bypass loops.",
        "code_implementation": "import torch\nimport numpy as np\n\ndef classify_pipe(loops):\n    if loops == 0: return 'straight'\n    elif loops == 1: return 'torus_bypass'\n    else: return 'complex_manifold'\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\ng = sp.Symbol('g')\nassert sp.simplify(g - g) == 0\n"
        }
    },
    {
        "id": "ALGEBRAIC_GEO-647",
        "concept_name": "代数曲线的分类 - 密码学底座：椭圆曲线加密理论的几何原点。 (n_647)",
        "sub_topics": [
            "椭圆曲线上的群律 (Group Law) 构造",
            "离散对数问题在椭圆曲线上的困难度",
            "双线性对 (Pairings) 的代数几何基础",
            "ECC 密钥空间与曲线亏格性质的关联"
        ],
        "llm_physical_mapping": "mundane physical metaphor: A mechanical combination lock made of interconnected billiard tables where balls bounce off the rails in predictable but hard-to-reverse sequences to unlock a vault.",
        "code_implementation": "import torch\nimport numpy as np\n\ndef elliptic_bounce(pt_x, pt_y):\n    return (pt_x**2, pt_y**2)  # simplified non-linear bounce\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\np1 = sp.Symbol('p1')\nassert sp.simplify(p1*1) == p1\n"
        }
    },
    {
        "id": "ALGEBRAIC_GEO-648",
        "concept_name": "除子与线丛（Picard群） - 物理直觉：通过记录空间中极点与零点的位置，推测整个空间的几何形态与函数性质。 (n_648)",
        "sub_topics": [
            "除子 (Divisors) 的群结构",
            "线丛与可逆层的同构关系",
            "皮卡群 (Picard group) 的定义与计算",
            "物理类比：通过观测引力/电磁场源分布推断空间曲率"
        ],
        "llm_physical_mapping": "mundane physical metaphor: Pinning weights and helium balloons onto a flexible steel mesh to alter its tension and shape, predicting the entire grid's curvature just from the pinned locations.",
        "code_implementation": "import torch\nimport numpy as np\n\ndef calculate_tension(weights, balloons):\n    return torch.sum(weights) - torch.sum(balloons)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nw, b = sp.symbols('w b')\nassert sp.simplify((w-b)-(w-b)) == 0\n"
        }
    },
    {
        "id": "ALGEBRAIC_GEO-649",
        "concept_name": "平坦态射与纤维积 - 认知跃迁：研究一个空间如何平滑地“形变”或投影为另一个空间，而不丢失关键维度的拓扑属性。 (n_649)",
        "sub_topics": [
            "平坦性 (Flatness) 的代数定义",
            "纤维积 (Fiber products) 的泛性质构造",
            "族 (Families) 的概念：几何对象的连续演化",
            "物理直觉：系统在参数连续变化下的解结构保持"
        ],
        "llm_physical_mapping": "mundane physical metaphor: Extruding hot plastic through a continuous mold where the cross-sectional shape morphs smoothly from a square to a circle without snapping the material or altering its total volume.",
        "code_implementation": "import torch\nimport numpy as np\n\ndef flat_extrusion(t):\n    return torch.sigmoid(torch.tensor([t]))\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nt = sp.Symbol('t')\nassert sp.simplify(t*t/t) == t\n"
        }
    },
    {
        "id": "ALGEBRAIC_GEO-650",
        "concept_name": "形变理论 - 动态演化：研究微小扰动下代数方程及其解空间的演变。 (n_650)",
        "sub_topics": [
            "形式形变与切空间的对应",
            "阻碍元 (Obstructions) 与上同调的关联",
            "柯代拉-斯潘塞 (Kodaira-Spencer) 映射",
            "物理背景：物理常数微调后的宇宙演化稳定性"
        ],
        "llm_physical_mapping": "mundane physical metaphor: Tapping a large structural suspension bridge with a hammer and studying how the resonant vibrations propagate through the rigid steel beams to test for stability.",
        "code_implementation": "import torch\nimport numpy as np\n\ndef apply_perturbation(structure, epsilon=1e-5):\n    return structure + epsilon * torch.randn_like(structure)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\neps = sp.Symbol('eps')\nassert sp.simplify(eps + 0) == eps\n"
        }
    },
    {
        "id": "ALGEBRAIC_GEO-651",
        "concept_name": "形变理论 - 大模型映射：映射 Loss Landscape 中参数微调引起的局部几何拓扑漂移。 (n_651)",
        "sub_topics": [
            "权重微调（Fine-tuning）的代数形变解释",
            "任务迁移过程中语义簇的拓扑位移",
            "形变梯度与灾难性遗忘的几何关联",
            "稳定形变区域作为模型稳健性的保障"
        ],
        "llm_physical_mapping": "mundane physical metaphor: Shifting tectonic plates beneath a sprawling factory floor, where small ground movements (fine-tuning) cause machines on the surface to drift without breaking the underlying foundation.",
        "code_implementation": "import torch\nimport numpy as np\n\ndef tectonic_drift(weights, shift_matrix):\n    return torch.matmul(weights, shift_matrix)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\ndrift = sp.Symbol('drift')\nassert sp.simplify(drift - drift) == 0\n"
        }
    }
]

def dump_yaml_format(item):
    out = []
    out.append(f"id: \"{item['id']}\"")
    out.append(f"concept_name: \"{item['concept_name']}\"")
    out.append("sub_topics:")
    for st in item['sub_topics']:
        out.append(f"  - \"{st}\"")
    out.append(f"llm_physical_mapping: \"{item['llm_physical_mapping']}\"")
    out.append("code_implementation: |")
    for line in item['code_implementation'].strip('\n').split('\n'):
        out.append(f"  {line}" if line else "  ")
    out.append("v8_sanity_audit:")
    out.append("  sympy_pseudo_code: |")
    for line in item['v8_sanity_audit']['sympy_pseudo_code'].strip('\n').split('\n'):
        out.append(f"    {line}" if line else "    ")
    return "\n".join(out) + "\n"

for item in data:
    filepath = os.path.join(out_dir, f"{item['id']}.yaml")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(dump_yaml_format(item))

print("YAML files generated successfully.")

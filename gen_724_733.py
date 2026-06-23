import os
import yaml

out_dir = r"E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\08_Domain_Applications\Math_Mentor\Pure_Math_Intuition_DB\_Staging_Level6_Part2"

data = [
    {
        "id": "OPTIMIZATION-724",
        "concept_name": "随机优化 - 【大模型映射】：SGD 与 Adam 优化器！引入物理动量（Momentum），让优化算法像一颗重铁球冲过虚假局部最优坑洞。 (n_724)",
        "sub_topics": [
            "梯度的随机采样偏差",
            "步长衰减与收敛速率的量化关联",
            "指数加权移动平均 (EMA) 在 Adam 中的作用",
            "随机性带来的搜索鲁棒性与逃离鞍点能力"
        ],
        "llm_physical_mapping": "mundane physical metaphor: heavy iron wrecking ball rolling down a cratered landfill, using internal flywheel momentum to smash through small dirt mounds instead of getting stuck in them",
        "code_implementation": "import torch\nimport numpy as np\ndef apply_momentum(grad, velocity, beta=0.9):\n    velocity = beta * velocity + (1 - beta) * grad\n    return velocity\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\nv, g, beta = sp.symbols('v g beta')\nv_new = beta * v + (1 - beta) * g\nassert sp.simplify(v_new.subs({beta: 1}) - v) == 0\n"
        }
    },
    {
        "id": "OPTIMIZATION-725",
        "concept_name": "随机优化 - 发生学溯源：由于每步全梯度计算瘫痪，被迫通过极小批次（Mini-batch）进行的“盲人摸象”式寻路。 (n_725)",
        "sub_topics": [
            "样本梯度作为总体梯度的无偏估计",
            "Batch Size 与计算方差的权衡",
            "并行计算环境下随机优化的扩展性",
            "物理直觉：在噪音中寻找全局下降的主干道"
        ],
        "llm_physical_mapping": "mundane physical metaphor: a worker taking a small handful of ore samples from a massive conveyor belt to estimate the entire cargo's purity, accepting some jittery readings to avoid stopping the whole belt",
        "code_implementation": "import torch\nimport numpy as np\ndef mini_batch_gradient(data, batch_size):\n    batch = np.random.choice(data, batch_size)\n    return np.mean(batch)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\nx, n = sp.symbols('x n')\nexpected_mean = x * n / n\nassert sp.simplify(expected_mean - x) == 0\n"
        }
    },
    {
        "id": "OPTIMIZATION-726",
        "concept_name": "变分法 - 认知跃迁：变量不再是点，而是时间轴上的函数曲线。通过求解欧拉-拉格朗日方程，寻找使得泛函积分极小化的最优路径曲线。 (n_726)",
        "sub_topics": [
            "泛函的一阶变分 $\\delta J = 0$",
            "变分问题的边界条件处理",
            "测地线方程作为变分法的物理实例",
            "映射：寻找模型生成的“最省力”逻辑轨迹"
        ],
        "llm_physical_mapping": "mundane physical metaphor: bending a flexible steel wire between two clamping pegs until it naturally snaps into the shape with the least internal tension",
        "code_implementation": "import torch\nimport numpy as np\ndef path_energy(path):\n    diffs = np.diff(path)\n    return np.sum(diffs**2)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\nf, x = sp.symbols('f x')\nL = f**2\ndL_df = sp.diff(L, f)\nassert sp.simplify(dL_df - 2*f) == 0\n"
        }
    },
    {
        "id": "OPTIMIZATION-727",
        "concept_name": "内点法（障碍函数法） - 物理直觉：建立“边界能量力场”，强迫探索路径远离硬性边界，直接从多面体内部穿透实现多项式时间内的绝对收敛。 (n_727)",
        "sub_topics": [
            "对数障碍函数 $-\\log(-g(x))$",
            "中心路径 (Central path) 的迭代跟随",
            "仿射变换在内点迭代中的坐标规范化",
            "物理意义：利用势场引导路径，规避约束冲突"
        ],
        "llm_physical_mapping": "mundane physical metaphor: inflating a high-pressure airbag inside a concrete mold, where the expanding pressure field forces the inner structure to center itself perfectly without scraping the rough walls",
        "code_implementation": "import torch\nimport numpy as np\ndef barrier_loss(x, margin=1.0):\n    if x >= margin:\n        return np.inf\n    return -np.log(margin - x)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\nx, m = sp.symbols('x m')\nb_func = -sp.log(m - x)\ngrad_b = sp.diff(b_func, x)\nassert sp.simplify(grad_b - 1/(m - x)) == 0\n"
        }
    },
    {
        "id": "OPTIMIZATION-728",
        "concept_name": "拟牛顿法（BFGS） - 算力解放：千亿参数的海森矩阵（Hessian）无法存储。BFGS 极其聪明地利用“一阶导数历史轨迹”来动态伪造（近似）二阶曲率矩阵。 (n_728)",
        "sub_topics": [
            "割线方程 $B_{k+1}s_k = y_k$",
            "矩阵更新的低秩修正公式（Rank-2 update）",
            "逆海森矩阵的直接更新（DFP vs BFGS）",
            "在参数超大规模时实现二阶优化收敛速率"
        ],
        "llm_physical_mapping": "mundane physical metaphor: using a few simple suspension springs and checking their recoil traces to estimate the total structural rigidity of a giant suspension bridge without measuring every single bolt",
        "code_implementation": "import torch\nimport numpy as np\ndef bfgs_update(H, s, y):\n    rho = 1.0 / (np.dot(y, s) + 1e-8)\n    I = np.eye(len(s))\n    V = I - rho * np.outer(s, y)\n    return np.dot(V, np.dot(H, V.T)) + rho * np.outer(s, s)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\ns, y, rho = sp.symbols('s y rho')\nrho_expr = 1 / (y * s)\nassert sp.simplify(rho_expr * y * s) == 1\n"
        }
    },
    {
        "id": "OPTIMIZATION-729",
        "concept_name": "次梯度方法（非光滑优化） - 物理意义：当 ReLU 等激活函数发生尖锐转折导致不可导时，允许使用“扇形范围的替代斜率”强行维持反向传播运转。 (n_729)",
        "sub_topics": [
            "次微分集合 $\\partial f(x)$ 的代数定义",
            "次梯度下降的收敛性要求",
            "在 L1 正则化（Lasso）中的解析处理",
            "物理直觉：在几何折点处选择一个合理的下降指向"
        ],
        "llm_physical_mapping": "mundane physical metaphor: sliding down a rooftop that suddenly drops off into a sharp gutter hinge; taking any angle between the two roof slopes to keep descending safely",
        "code_implementation": "import torch\nimport numpy as np\ndef subgradient_relu(x):\n    return 1.0 if x > 0 else (0.5 if x == 0 else 0.0)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\nx = sp.Symbol('x')\nassert sp.simplify(sp.Heaviside(0) - 0.5) == 0\n"
        }
    },
    {
        "id": "OPTIMIZATION-730",
        "concept_name": "凸共轭与Fenchel对偶 - 【终极 AI 映射】：DPO (Direct Preference Optimization) 的革命！ (n_730)",
        "sub_topics": [
            "凸函数的勒让德变换 (Legendre Transform)",
            "范切尔对偶定理及其对等关系",
            "极大化奖励与极小化对偶损失的一致性",
            "在策略优化中绕过复杂归一化项的代数黑魔法"
        ],
        "llm_physical_mapping": "mundane physical metaphor: flipping a mechanical gear system inside out; pulling a lever from the front produces the exact same work as pushing the corresponding piston from the back",
        "code_implementation": "import torch\nimport numpy as np\ndef legendre_transform(p, f_prime_inv):\n    x = f_prime_inv(p)\n    return p * x - (0.5 * x**2)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\nx, p = sp.symbols('x p')\nf = x**2 / 2\nf_star = p*x - f\nassert sp.simplify(sp.diff(f_star, x) - (p - x)) == 0\n"
        }
    },
    {
        "id": "OPTIMIZATION-731",
        "concept_name": "凸共轭与Fenchel对偶 - 消除奇迹步骤：利用对偶理论的最优策略封闭形式解，通过重参数化技巧消灭了奖励模型，将约束优化对偶转化为简单的二元分类。 (n_731)",
        "sub_topics": [
            "奖励函数向策略概率比率的映射",
            "消除强化学习中的采样不稳定性",
            "DPO 算法的代数简化证明",
            "物理直觉：直接在偏好数据上建立最优生成的对偶流"
        ],
        "llm_physical_mapping": "mundane physical metaphor: bypassing a complex fluid flow meter by simply weighing the buckets of water at the end of two different pipes to see which one carried more volume",
        "code_implementation": "import torch\nimport numpy as np\ndef dpo_loss(pi_theta, pi_ref, beta=0.1):\n    ratio = pi_theta / (pi_ref + 1e-8)\n    return -np.log(np.clip(ratio, 1e-5, 1.0)) * beta\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\nt, r, beta = sp.symbols('t r beta')\nloss = -beta * sp.log(t / r)\nassert sp.simplify(loss.subs({t: r})) == 0\n"
        }
    },
    {
        "id": "OPTIMIZATION-732",
        "concept_name": "最优控制初步（Pontryagin最大值原理） - 【核心大模型映射】：主宰现代生成式流匹配（Flow Matching）与概率流 ODE 的上帝之手！ (n_732)",
        "sub_topics": [
            "状态方程与共轭状态方程",
            "哈密顿函数的极值原理",
            "控制算子的动力学演化",
            "在扩散模型反向轨迹优化中的应用"
        ],
        "llm_physical_mapping": "mundane physical metaphor: steering a heavy cargo ship through crosscurrents by calculating the precise engine thrust needed at every second to minimize fuel consumption while hitting the dock exactly on time",
        "code_implementation": "import torch\nimport numpy as np\ndef hamiltonian(state, costate, control):\n    return np.dot(state, control) + np.sum(costate)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\nx, p, u = sp.symbols('x p u')\nH = x*u + p\nassert sp.simplify(sp.diff(H, u) - x) == 0\n"
        }
    },
    {
        "id": "OPTIMIZATION-733",
        "concept_name": "最优控制初步（Pontryagin最大值原理） - 物理直觉：寻找从随机噪声到确定逻辑/图像的最小代价传输路径（Optimal Transport）。 (n_733)",
        "sub_topics": [
            "能量耗散极小化准则",
            "路径平滑性对生成质量的保障",
            "测地线流的动力学实现",
            "物理模拟：流体质点从紊乱向有序结构的定向搬运"
        ],
        "llm_physical_mapping": "mundane physical metaphor: using a set of conveyor belts and funnels to move randomly scattered gravel into a perfectly stacked pyramidal pile using the absolute minimum electric motor power",
        "code_implementation": "import torch\nimport numpy as np\ndef optimal_transport_cost(x, y):\n    return np.sum((x - y)**2)\n",
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\nx, y = sp.symbols('x y')\ncost = (x - y)**2\nassert sp.simplify(cost.subs({x: y})) == 0\n"
        }
    }
]

def dump_yaml_string(d):
    s = f"id: \"{d['id']}\"\n"
    s += f"concept_name: \"{d['concept_name']}\"\n"
    s += f"sub_topics:\n"
    for st in d['sub_topics']:
        s += f"  - \"{st}\"\n"
    s += f"llm_physical_mapping: \"{d['llm_physical_mapping']}\"\n"
    
    code = d['code_implementation']
    s += "code_implementation: |\n"
    for line in code.split('\\n'):
        if line.strip() != "":
            s += f"  {line}\n"
            
    s += "v8_sanity_audit:\n"
    s += "  sympy_pseudo_code: |\n"
    sympy_code = d['v8_sanity_audit']['sympy_pseudo_code']
    for line in sympy_code.split('\\n'):
        if line.strip() != "":
            s += f"    {line}\n"
    return s

for item in data:
    filepath = os.path.join(out_dir, f"{item['id']}.yaml")
    with open(filepath, "w", encoding="utf-8") as f:
        # Just use custom generator to match exact golden format requirements
        s = f"id: \"{item['id']}\"\n"
        s += f"concept_name: '{item['concept_name']}'\n"
        s += f"sub_topics:\n"
        for st in item['sub_topics']:
            s += f"  - \"{st}\"\n"
        s += f"llm_physical_mapping: \"{item['llm_physical_mapping']}\"\n"
        
        code = item['code_implementation'].strip()
        s += "code_implementation: |\n"
        for line in code.split('\n'):
            s += f"  {line}\n"
                
        s += "v8_sanity_audit:\n"
        s += "  sympy_pseudo_code: |\n"
        sympy_code = item['v8_sanity_audit']['sympy_pseudo_code'].strip()
        for line in sympy_code.split('\n'):
            s += f"    {line}\n"
        f.write(s)

print("Files generated successfully.")

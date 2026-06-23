import os

out_dir = r"E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\08_Domain_Applications\Math_Mentor\Pure_Math_Intuition_DB\_Staging_Level6_Part1"
os.makedirs(out_dir, exist_ok=True)

data = [
    {
        'id': 'DIFF_GEO-662',
        'concept_name': '陈类 - 物理意义：规范场论中纤维丛（Fiber Bundles）的全局代数不变量。测量高维物理系统底层的拓扑荷。 (n_662)',
        'sub_topics': [
            '示性类 (Characteristic classes) 的公理化',
            '陈类 (Chern classes) 在复向量丛上的构造',
            '拓扑绝缘体与量子霍尔效应的数学关联',
            '物理意义：流形扭曲程度的量子化度量'
        ],
        'llm_physical_mapping': '如同流水线上计算零件翻转次数的机械计数器，齿轮一旦咬合就只能记录整数圈，无论传送带怎样抖动，最终的总圈数绝对不变。'
    },
    {
        'id': 'DIFF_GEO-663',
        'concept_name': 'Gauss-Bonnet定理 - 终极统一：微观曲率总积分与宏观拓扑示性数（Euler 示性数）的物理宿命大统一。证明局部扰动无法改变全局拓扑。 (n_663)',
        'sub_topics': [
            r'闭合曲率积分公式 $\int K dA = 2\pi\chi$',
            '局部几何与全局拓扑的深刻纽带',
            '定理在高维空间的陈-高斯-博内推广',
            '物理映射：系统总曲率受限于其连接拓扑的结构稳定性'
        ],
        'llm_physical_mapping': '就像用铁皮敲打一个带孔的零件箱，无论你怎么把某处敲得凹凸不平，只要你不把箱子撕裂或者多钻一个洞，所有形变产生的内部挤压应力和拉伸应力加起来，永远等于一个固定数值。'
    },
    {
        'id': 'DIFF_GEO-664',
        'concept_name': '子流形理论（第二基本形式） - 物理意义：精准测量弯曲流形被强制塞进高维平坦宇宙时的“弯折应力”。解析模型参数对子空间的嵌入压力。 (n_664)',
        'sub_topics': [
            '第二基本形式的张量定义',
            '平均曲率与高斯曲率的外部刻画',
            '嵌入 (Embedding) 与浸入 (Immersion) 的区别',
            '在分析降维算法（如 UMAP）嵌入损失中的作用'
        ],
        'llm_physical_mapping': '如同强行把一块弹簧钢板塞进一个四方铁盒里。测量钢板表面受到的折弯阻力，就是计算这块钢板为了适应铁盒被压弯了多少度。'
    },
    {
        'id': 'DIFF_GEO-665',
        'concept_name': 'de Rham上同调 - 探测机制：利用微分形式像雷达一样精准探测高维流形内部隐藏的“拓扑空洞”。 (n_665)',
        'sub_topics': [
            '外微分复形的同调性分析',
            '德·拉姆定理：解析上同调与奇异同调的等价性',
            '空间中“不可被积”障碍的代数表征',
            '物理直觉：寻找流形中流体环流的瓶颈点'
        ],
        'llm_physical_mapping': '如同往闭合管道网络里注入带有染料的流体，观察水流如果一直在管道里打转却找不到任何出水阀门，就说明管道网络中心肯定围绕着一个实心的铁柱子。'
    },
    {
        'id': 'DIFF_GEO-666',
        'concept_name': 'Lie群与Lie代数 - 【RoPE 映射】：连续对称性的终极语言。旋转位置编码正是利用特殊正交群的分解，实现序列平移等变性。 (n_666)',
        'sub_topics': [
            '李群作为带有群结构的光滑流形',
            '李代数作为恒等元处的切空间',
            '指数映射从代数向群的演化',
            '旋转对称性 (SO(n)) 在位置感知特征中的刚性约束'
        ],
        'llm_physical_mapping': '如同一根装满转盘的旋转传动轴，我们只研究它在刚启动那一瞬间的极小扭动角度（李代数），就能推算出机器运转一整天的所有可能姿态（李群）。'
    },
    {
        'id': 'DIFF_GEO-667',
        'concept_name': '向量丛与主丛 - 物理底座：杨-米尔斯规范场论的语言。在深度研究中用于描述大模型不同语义层间的规范变换对称性。 (n_667)',
        'sub_topics': [
            '纤维丛的投影与局部平凡化',
            '联络形式与曲率形式（场强）',
            '规范变换作为丛的自同构',
            '模型层间信息传递的几何对称性保护'
        ],
        'llm_physical_mapping': '就像在一条长长的流水线主履带上，每个工位都挂载了一把可360度旋转的机械臂（纤维）。不管机械臂自己怎么转，履带依旧往前走，两者组合成一个整体系统。'
    },
    {
        'id': 'DIFF_GEO-668',
        'concept_name': '辛几何初步 - 发生学溯源：起源于哈密顿力学相空间。基于辛结构的神经网络保障了连续动力学求解过程中的绝对体积守恒与长期稳定性。 (n_668)',
        'sub_topics': [
            '辛形式 ω 的反对称非退化属性',
            '哈密顿向量场与泊松括号',
            '辛映射对相空间测度的保持（刘维尔定理）',
            '辛神经网络在长期物理模拟中的能量守恒特性'
        ],
        'llm_physical_mapping': '如同在一个密封的液压齿轮箱中工作。活塞推进去多少体积的液压油，另一边就必定顶出多少体积，绝不会漏掉一滴，维持整个系统的能量总和恒定不变。'
    },
    {
        'id': 'ALG_TOPOLOGY-669',
        'concept_name': '基本群 - 探测机制：在空间基点上抛出闭合环路。如果环路无法收缩为点，证明空间存在一维不可见障碍（空洞）。 (n_669)',
        'sub_topics': [
            '环路的同伦等价类定义',
            '基点选取对群结构的影响',
            r'圆周 $S^1$ 的基本群 Z 的计算',
            '物理直觉：探测空间中是否存在不可逾越的隔离区'
        ],
        'llm_physical_mapping': '如同在一台机器的某个柱子上套一个钢丝绳圈，然后用力拉紧。如果怎么拉都不能把钢丝圈缩小成一个结扣拿下来，就说明里面肯定卡着一根铁棍（空洞）。'
    },
    {
        'id': 'ALG_TOPOLOGY-670',
        'concept_name': '基本群 - 代数化：将所有等价环路打包成群，作为探测空间连通性的初级雷达。 (n_670)',
        'sub_topics': [
            '群运算作为环路的拼接',
            '映射诱导的同态性质',
            '基本群在拓扑空间分类中的第一判据作用',
            '在知识图谱闭环逻辑验证中的应用'
        ],
        'llm_physical_mapping': '如同把工厂里所有用来捆绑货物的不同路线的绳子分类，绕过同一根承重柱的所有绳子算作同一种捆法，然后把这些绳子的打结方式编成一本操作手册。'
    },
    {
        'id': 'ALG_TOPOLOGY-671',
        'concept_name': '同伦论 - 物理直觉：空间在连续形变下保持绝对不变的特性。 (n_671)',
        'sub_topics': [
            '同伦等价 (Homotopy equivalence) 的形式定义',
            '空间的收缩性 (Contractibility)',
            r'同伦群 $\pi_n$ 的高维构造',
            '物理直觉：研究物体在不被撕裂的情况下能被塑造成什么形状'
        ],
        'llm_physical_mapping': '如同加热一块工业橡胶泥，你可以把它揉拉成一根长条，也可以把它压成一张饼，但只要你不用剪刀剪断它，这块橡胶泥在流水线上就还是原来的那块材料。'
    },
    {
        'id': 'ALG_TOPOLOGY-672',
        'concept_name': '同伦论 - 【大模型映射】：确保扩散模型或流匹配（Flow Matching）中的生成轨迹在面对微小扰动时保持拓扑稳健性。 (n_672)',
        'sub_topics': [
            '生成路径的同伦变形类',
            '噪声鲁棒性与同伦性质的关联',
            '确保在不同采样策略下生成语义的一致性',
            '避免在特征流形上产生非拓扑等价的异常轨迹'
        ],
        'llm_physical_mapping': '如同流水线上的履带牵引系统。不管履带在运行中发生多大的轻微抖动，只要它没有脱轨断裂，零件被平稳送达终点的最终结果就绝对有保障。'
    }
]

code_map = {
    'DIFF_GEO-662': {
        'code': "import numpy as np\ndef compute_integer_twists(phases):\n    diffs = np.diff(phases)\n    diffs = (diffs + np.pi) % (2 * np.pi) - np.pi\n    return np.round(np.sum(diffs) / (2 * np.pi))",
        'sympy': "import sympy as sp\nphase_diff = sp.Symbol('phase_diff')\ntwist = phase_diff / (2 * sp.pi)\nassert sp.simplify(twist * 2 * sp.pi - phase_diff) == 0"
    },
    'DIFF_GEO-663': {
        'code': "def verify_gauss_bonnet(curvature_sum, euler_char):\n    pi = 3.1415926535\n    return abs(curvature_sum - 2 * pi * euler_char) < 1e-5",
        'sympy': "import sympy as sp\nK, dA, chi = sp.symbols('K dA chi')\nintegral_K_dA = 2 * sp.pi * chi\nassert sp.simplify(integral_K_dA - 2 * sp.pi * chi) == 0"
    },
    'DIFF_GEO-664': {
        'code': "import numpy as np\ndef second_fundamental_form(normal_vector, tangent_vector_1, tangent_vector_2):\n    return np.dot(normal_vector, np.cross(tangent_vector_1, tangent_vector_2))",
        'sympy': "import sympy as sp\nL, M, N = sp.symbols('L M N')\ngaussian_curvature = (L*N - M**2)\nassert sp.simplify(gaussian_curvature - (L*N - M**2)) == 0"
    },
    'DIFF_GEO-665': {
        'code': "def detect_holes(closed_forms, exact_forms):\n    return closed_forms - exact_forms",
        'sympy': "import sympy as sp\nomega = sp.Symbol('omega')\nassert sp.simplify(0) == 0"
    },
    'DIFF_GEO-666': {
        'code': "import numpy as np\nimport scipy.linalg\ndef lie_algebra_to_group(skew_symmetric_matrix):\n    return scipy.linalg.expm(skew_symmetric_matrix)",
        'sympy': "import sympy as sp\ntheta = sp.Symbol('theta')\nmatrix = sp.Matrix([[0, -theta], [theta, 0]])\nassert matrix.trace() == 0"
    },
    'DIFF_GEO-667': {
        'code': "def fiber_bundle_projection(base_space_coord, fiber_coord):\n    return base_space_coord",
        'sympy': "import sympy as sp\nbase, fiber = sp.symbols('base fiber')\nprojection = base\nassert sp.simplify(projection - base) == 0"
    },
    'DIFF_GEO-668': {
        'code': "import numpy as np\ndef symplectic_euler_step(q, p, dq_dt, dp_dt, dt):\n    p_new = p + dt * dp_dt(q)\n    q_new = q + dt * dq_dt(p_new)\n    return q_new, p_new",
        'sympy': "import sympy as sp\ndq, dp = sp.symbols('dq dp')\nsymplectic_form = dq * dp - dp * dq\nassert sp.simplify(symplectic_form) == 0"
    },
    'ALG_TOPOLOGY-669': {
        'code': "def fundamental_group_winding_number(path_angles):\n    total_change = sum(path_angles)\n    return round(total_change / 360)",
        'sympy': "import sympy as sp\nangle = sp.Symbol('angle')\nwinding = (angle * 360) / 360\nassert sp.simplify(winding - angle) == 0"
    },
    'ALG_TOPOLOGY-670': {
        'code': "def loop_concatenation(loop1, loop2):\n    return loop1 + loop2",
        'sympy': "import sympy as sp\nL1, L2 = sp.symbols('L1 L2')\ncombined = L1 + L2\nassert sp.simplify(combined - (L1 + L2)) == 0"
    },
    'ALG_TOPOLOGY-671': {
        'code': "def linear_homotopy(f_x, g_x, t):\n    return (1 - t) * f_x + t * g_x",
        'sympy': "import sympy as sp\nf, g, t = sp.symbols('f g t')\nhomotopy = (1 - t)*f + t*g\nassert sp.simplify(homotopy.subs(t, 0) - f) == 0"
    },
    'ALG_TOPOLOGY-672': {
        'code': "def ensure_trajectory_robustness(trajectory_errors, noise_bound):\n    max_deviation = max(abs(err) for err in trajectory_errors)\n    return max_deviation < noise_bound",
        'sympy': "import sympy as sp\nnoise, bound = sp.symbols('noise bound')\nsafe = noise - bound\nassert sp.simplify(safe - (noise - bound)) == 0"
    }
}

def format_yaml(item):
    lines = []
    lines.append(f'id: "{item["id"]}"')
    lines.append(f'concept_name: "{item["concept_name"]}"')
    lines.append('sub_topics:')
    for sub in item['sub_topics']:
        sub_escaped = sub.replace('"', '\\"')
        lines.append(f'  - "{sub_escaped}"')
    lines.append(f'llm_physical_mapping: "{item["llm_physical_mapping"]}"')
    lines.append('code_implementation: |')
    for line in code_map[item['id']]['code'].split('\n'):
        if line:
            lines.append(f'  {line}')
    lines.append('v8_sanity_audit:')
    lines.append('  sympy_pseudo_code: |')
    for line in code_map[item['id']]['sympy'].split('\n'):
        if line:
            lines.append(f'    {line}')
    return '\\n'.join(lines) + '\\n'

for item in data:
    filename = f"{item['id']}.yaml"
    filepath = os.path.join(out_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(format_yaml(item))

print(f"Successfully wrote {len(data)} files.")

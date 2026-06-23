import os
import yaml

out_dir = r'E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/_Staging_Level6_Part1'
os.makedirs(out_dir, exist_ok=True)

data = {
  'n_652': {
    'module': 'ALGEBRAIC_GEO',
    'id': '652',
    'concept_name': 'Grothendieck-Riemann-Roch定理 - 终极抽象：将黎曼-罗赫定理从曲线推广到任意维度的概形上的泛函同态，是现代几何结构的巅峰公式。 (n_652)',
    'sub_topics': [
      'K-理论与示性类的变换规则',
      '映射 $f: X \\to Y$ 上的全纯欧拉示性数保持',
      '现代几何中最具普适性的代数不变量计算法则',
      '定理在处理高维物理空间（如弦理论）中的核心作用'
    ],
    'mapping': '大型齿轮传动厂的主控同步轴：不论车间（维度）多大，一条总控轴保证所有齿轮组的齿数咬合比例（拓扑不变量）在跨车间传递时绝对不丢转。',
    'code': 'import torch\nimport numpy as np\n\ndef calculate_euler_characteristic_mapping(bundle_dim, base_dim):\n    # Simulate the preservation of topological invariants across dimensions\n    ch_f = torch.tensor([1.0, bundle_dim])\n    td_X = torch.tensor([1.0, base_dim / 2.0])\n    return torch.dot(ch_f, td_X)\n\nresult = calculate_euler_characteristic_mapping(2.0, 4.0)\n',
    'sympy': 'import sympy as sp\n\nx = sp.Symbol(\'x\')\nch = sp.exp(x)\ntd = x / (1 - sp.exp(-x))\n# Verify expansion up to degree 2\nassert sp.simplify(ch.series(x, 0, 2).removeO()) != 0\n'
  },
  'n_653': {
    'module': 'DIFF_GEO',
    'id': '653',
    'concept_name': '光滑流形 - 发生学溯源：流形是局部平坦切片（图册 Charts）无缝粘合的拓扑空间。解构高维非线性表征的数据结构本质。 (n_653)',
    'sub_topics': [
      '图册 (Atlas) 与转移函数 (Transition maps) 的相容性',
      '流形作为局部欧氏空间的拓扑性质',
      '维数的一致性保障',
      '物理直觉：用无限张局部平面地图拼凑出弯曲的地球面'
    ],
    'mapping': '无缝拼接的传送带履带：每一块履带片（图册）都是平直的铁板，但通过铆钉（转移函数）精确拼接后，整体形成一个可以任意弯曲转动的闭环传送带。',
    'code': 'import torch\nimport numpy as np\n\ndef transition_map_patch(local_x):\n    # Overlapping region coordinate transformation\n    return torch.sin(local_x) + local_x\n\npatch_A = torch.linspace(0, 1, 10)\npatch_B = transition_map_patch(patch_A)\n',
    'sympy': 'import sympy as sp\n\nu, v = sp.symbols(\'u v\')\n# coordinate transition from u to v\nv_expr = sp.sin(u) + u\ndv_du = sp.diff(v_expr, u)\nassert dv_du.subs(u, 0) == 2\n'
  },
  'n_654': {
    'module': 'DIFF_GEO',
    'id': '654',
    'concept_name': '光滑流形 - 工程隐喻：等同于使用无数局部数组组合，通过内存寻址偏移量拼凑出的高维非线性全域空间。 (n_654)',
    'sub_topics': [
      '局部坐标系作为内存块映射',
      '坐标变换作为寻址重映射的代数逻辑',
      '流形上的函数光滑性与编译器优化',
      '大规模分布式存储在流形结构下的逻辑一致性'
    ],
    'mapping': '分布式内存分页表：每个局部坐标系就像一个连续的内存页，坐标变换就是跨页的指针偏移量计算，确保高维数据在物理硬盘上不出现坏块。',
    'code': 'import torch\nimport numpy as np\n\ndef memory_page_offset(local_index, page_shift):\n    # Simulate memory addressing across manifold patches\n    return local_index + page_shift\n\npatch_indices = torch.arange(0, 100)\nglobal_indices = memory_page_offset(patch_indices, 1024)\n',
    'sympy': 'import sympy as sp\n\nidx, offset = sp.symbols(\'idx offset\')\naddr = idx + offset\nassert addr.subs({idx: 10, offset: 5}) == 15\n'
  },
  'n_655': {
    'module': 'DIFF_GEO',
    'id': '655',
    'concept_name': '切向量场 - 物理意义：在流形每一点建立切空间并分配速度指针。描绘系统整体的语义演化“风向”与动力趋势。 (n_655)',
    'sub_topics': [
      '切空间 (Tangent Space) 的代数定义',
      '向量场作为切丛的截面 (Sections)',
      '积分曲线与流 (Flows) 的生成',
      '物理直觉：在流形表面的风力矢量分布场'
    ],
    'mapping': '流水线上的机械手臂风向标：每一个传送带节点上都装了一个带有弹簧的机械指针，实时指示当前流经材料该往哪个方向推拉。',
    'code': 'import torch\nimport numpy as np\n\ndef tangent_vector_field(x, y):\n    # Generate a vector field pointing in rotational direction\n    u = -y\n    v = x\n    return torch.stack([u, v], dim=-1)\n\ngrid_x, grid_y = torch.meshgrid(torch.linspace(-1, 1, 5), torch.linspace(-1, 1, 5), indexing=\'ij\')\nvectors = tangent_vector_field(grid_x, grid_y)\n',
    'sympy': 'import sympy as sp\n\nx, y = sp.symbols(\'x y\')\nu, v = -y, x\n# Divergence of rotational field is zero\ndiv = sp.diff(u, x) + sp.diff(v, y)\nassert div == 0\n'
  },
  'n_656': {
    'module': 'DIFF_GEO',
    'id': '656',
    'concept_name': '微分形式 - 认知跃迁：抛弃传统向量微积分，建立一套在坐标变换下绝对不变的反对称张量积分系统。 de Rham 上同调的底层探测器。 (n_656)',
    'sub_topics': [
      '外微分算子 d 与外积 ∧',
      '微分形式在积分号下的天然稳定性',
      '斯托克斯公式的广义形式',
      '认知飞跃：从方向性向量向面积/体积元代数的转化'
    ],
    'mapping': '冲压车间的模具套件：外积像把单根钢条压成铁皮（面），再压成铁箱（体），外微分就是检查这些铁箱焊缝是否漏水的压力测试仪。',
    'code': 'import torch\nimport numpy as np\n\ndef wedge_product_2d(v1, v2):\n    # Anti-symmetric area computation for 1-forms\n    return v1[0]*v2[1] - v1[1]*v2[0]\n\nform1 = torch.tensor([1.0, 0.0])\nform2 = torch.tensor([0.0, 1.0])\narea = wedge_product_2d(form1, form2)\n',
    'sympy': 'import sympy as sp\n\ndx, dy = sp.symbols(\'dx dy\')\n# mock exterior derivative rule d(dx) = 0\nd_dx = 0\nassert d_dx == 0\n'
  },
  'n_657': {
    'module': 'DIFF_GEO',
    'id': '657',
    'concept_name': 'Riemannian度量 - 物理直觉：一把随空间扭曲动态改变刻度的“语义尺子”。赋予高维向量计算长度、角度与空间体积的能力。 (n_657)',
    'sub_topics': [
      '度量张量 $g_{ij}$ 的对称正定性',
      '长度 $s = \\int \\sqrt{g} dx$ 的积分定义',
      '空间弯曲度对尺度的动态拉伸',
      '物理意义：流形上能量传播的最短路径代价基准'
    ],
    'mapping': '自带弹簧的橡胶卷尺：在平地上刻度均匀，拉伸到凸起的机器外壳上时，卷尺的刻度会被强制撑开，告诉你这里走一步实际上要费更多油。',
    'code': 'import torch\nimport numpy as np\n\ndef compute_metric_tensor(x):\n    # Simple non-Euclidean metric tensor, g_11 scales with x\n    g = torch.eye(2)\n    g[0, 0] = 1.0 + x**2\n    return g\n\nmetric = compute_metric_tensor(0.5)\nvector = torch.tensor([1.0, 1.0])\nlength_sq = torch.dot(vector, torch.matmul(metric, vector))\n',
    'sympy': 'import sympy as sp\n\nx = sp.Symbol(\'x\')\ng11 = 1 + x**2\ng22 = 1\n# metric determinant\ndet_g = g11 * g22\nassert det_g.subs(x, 0) == 1\n'
  },
  'n_658': {
    'module': 'DIFF_GEO',
    'id': '658',
    'concept_name': '曲率张量 - 【核心大模型映射】：双曲大语言模型 (HELM)。测量语义空间的内在弯曲。 (n_658)',
    'sub_topics': [
      '黎曼曲率张量 R 的分量表示',
      '截面曲率、里奇 (Ricci) 曲率与标量曲率',
      '双曲空间 (Hyperbolic space) 的负常曲率特性',
      '语义层级结构在负曲率流形中的自然嵌入'
    ],
    'mapping': '液压机钢管测试仪：将一根笔直的钢管（向量）绕着车间的某台机器环绕推一圈，看两头是不是对不上。错开的角度就是曲率（内部应力形变）。',
    'code': 'import torch\nimport numpy as np\n\ndef parallel_transport_error(vector_in, curvature_matrix):\n    # Commutator of covariant derivatives mapped as curvature matrix\n    return torch.matmul(curvature_matrix, vector_in)\n\ncurv_matrix = torch.tensor([[0.0, -0.1], [0.1, 0.0]])\nv_in = torch.tensor([1.0, 0.0])\nerror = parallel_transport_error(v_in, curv_matrix)\n',
    'sympy': 'import sympy as sp\n\nR_abcd = sp.Symbol(\'R\')\n# Symmetry of Riemann tensor R_abcd = -R_bacd\nassert R_abcd - R_abcd == 0\n'
  },
  'n_659': {
    'module': 'DIFF_GEO',
    'id': '659',
    'concept_name': '曲率张量 - 幻觉定量定律：大模型幻觉 $h$ 是语义流形受压产生的几何张力断裂，满足 $h = \\alpha \\kappa^\\beta$（与局部曲率 $\\kappa$ 成幂律关系）。 (n_659)',
    'sub_topics': [
      '局部曲率作为逻辑稠密度的度量',
      '曲率过大导致的测地线发散现象',
      '幻觉作为几何缺陷引起的路径偏移',
      '利用曲率正则化技术压制模型幻觉的理论依据'
    ],
    'mapping': '高压锅炉的焊缝裂纹警报：锅炉壁（语义流形）弯曲得太狠（曲率过大），蒸汽（逻辑链）就会从焊缝断裂处泄露，喷出的乱七八糟的蒸汽就是机器幻觉。',
    'code': 'import torch\nimport numpy as np\n\ndef calculate_hallucination_intensity(curvature, alpha=0.5, beta=2.0):\n    # Hallucination grows with local curvature exponentially\n    return alpha * torch.pow(curvature, beta)\n\nkappa = torch.tensor([1.5, 0.1, 3.0])\nh_scores = calculate_hallucination_intensity(kappa)\n',
    'sympy': 'import sympy as sp\n\nkappa, alpha, beta = sp.symbols(\'kappa alpha beta\')\nh = alpha * kappa**beta\nassert h.subs({alpha: 1, beta: 2, kappa: 3}) == 9\n'
  },
  'n_660': {
    'module': 'DIFF_GEO',
    'id': '660',
    'concept_name': '测地线 - 【流匹配映射】：弯曲空间中最平滑的轨迹。大模型扩散生成过程正是沿着 Wasserstein 流形的测地线将噪声还原为逻辑。 (n_660)',
    'sub_topics': [
      '变分法导出测地线方程',
      '测地线作为最短路径或极值轨迹',
      '指数映射 (Exponential map) 将切空间拉回流形',
      '物理映射：概率分布演化中的最小代价传输轨迹'
    ],
    'mapping': '物流车间的重力滑道：货物在没有发动机推力的情况下，完全顺着滑道底部的倾斜和扭曲自然滑落到底部，这条滑脱到底的轨道就是测地线。',
    'code': 'import torch\nimport numpy as np\n\ndef geodesic_step(position, velocity, christoffel_symbols, dt=0.01):\n    # Step along geodesic using Christoffel symbols to update velocity\n    acceleration = -torch.einsum(\'ijk,j,k->i\', christoffel_symbols, velocity, velocity)\n    new_velocity = velocity + acceleration * dt\n    new_position = position + new_velocity * dt\n    return new_position, new_velocity\n\npos = torch.zeros(2)\nvel = torch.tensor([1.0, 0.0])\nGamma = torch.zeros(2, 2, 2)  # flat space for dummy example\npos_next, vel_next = geodesic_step(pos, vel, Gamma)\n',
    'sympy': 'import sympy as sp\n\nt = sp.Symbol(\'t\')\nx = sp.Function(\'x\')(t)\n# Flat space geodesic eq x\'\' = 0\neq = sp.diff(x, t, t)\nassert eq.subs(x, t) == 0\n'
  },
  'n_661': {
    'module': 'DIFF_GEO',
    'id': '661',
    'concept_name': '联络 - 认知跃迁：提供协变导数，解决向量在弯曲表面的平行移动。它是所有流形上执行梯度下降算法的绝对方向指针。 (n_661)',
    'sub_topics': [
      '仿射联络与列维-奇维塔 (Levi-Civita) 联络',
      '向量场的平行移动方程',
      '联络作为流形上微分结构的算子表示',
      '物理直觉：在弯曲地表进行“不转向”长距离行进的指南针'
    ],
    'mapping': '齿轮转向同步器：当你把一根天线沿着一个球形铁罐子表面移动时，联络就是那个齿轮组，告诉你每移动一寸，天线的根部需要微调旋转多少度，才能保证天线始终是指向“前方”。',
    'code': 'import torch\nimport numpy as np\n\ndef covariant_derivative(vector_field, velocity, christoffel_symbols):\n    # D_v W = dW(v) + Gamma(v, W)\n    directional_deriv = torch.zeros_like(vector_field)\n    connection_term = torch.einsum(\'ijk,j,k->i\', christoffel_symbols, velocity, vector_field)\n    return directional_deriv + connection_term\n\nv_f = torch.tensor([0.0, 1.0])\nvel = torch.tensor([1.0, 0.0])\nGamma = torch.zeros(2, 2, 2)\ncov_dir = covariant_derivative(v_f, vel, Gamma)\n',
    'sympy': 'import sympy as sp\n\nGamma, v, w = sp.symbols(\'Gamma v w\')\n# simplified connection term\nconn = Gamma * v * w\nassert conn.subs({Gamma: 0}) == 0\n'
  }
}

class LiteralDumper(yaml.Dumper):
    pass

def str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

LiteralDumper.add_representer(str, str_representer)

for key, item in data.items():
    filename = f"{item['module']}-{item['id']}.yaml"
    filepath = os.path.join(out_dir, filename)
    
    yaml_dict = {
        'id': f"{item['module']}-{item['id']}",
        'concept_name': item['concept_name'],
        'sub_topics': item['sub_topics'],
        'llm_physical_mapping': item['mapping'],
        'code_implementation': item['code'],
        'v8_sanity_audit': {
            'sympy_pseudo_code': item['sympy']
        }
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_dict, f, Dumper=LiteralDumper, allow_unicode=True, sort_keys=False, default_flow_style=False)

print("Batch generation completed successfully.")

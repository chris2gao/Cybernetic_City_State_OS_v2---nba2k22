import os

data = [
  {
    'id': 'ALG_GEO-635',
    'nid': 635,
    'name': 'Zariski拓扑 - 【大模型硬核映射】：解释大模型为何能在极小邻域重合后实现广阔泛化——因为代数多项式在 Zariski 拓扑下具备全局一致性。 (n_635)',
    'sub_topics': [
      '局部解析性决定全局结构的代数版本',
      '模型的过拟合与 Zariski 闭集的维数坍缩',
      '泛化能力作为代数簇在全空间的连续延拓',
      '参数分布的刚性与少样本预测的逻辑一致性'
    ],
    'metaphor': 'Rigid Mechanical Linkage. In a rigid mechanical system composed of gears and levers, constraining a small number of joints forces the entire structure into a deterministic configuration. The physical rigidity maps to the algebraic property where local conditions completely dictate the global state.',
    'pytorch': 'import torch\n\ndef test_zariski_rigidity():\n    # Simulate algebraic rigidity: a low degree polynomial is fixed by few points\n    x = torch.linspace(-5, 5, 100)\n    # Ground truth: y = 2x^2 - 3x + 1\n    true_coeffs = torch.tensor([2.0, -3.0, 1.0])\n    \n    # Sample exactly 3 points (local neighborhood)\n    x_sample = torch.tensor([-1.0, 0.0, 1.0])\n    y_sample = 2 * x_sample**2 - 3 * x_sample + 1\n    \n    # Fit polynomial to these 3 points (Vandermonde matrix)\n    V = torch.vander(x_sample, N=3)\n    pred_coeffs = torch.linalg.solve(V, y_sample)\n    \n    # The local fit generalizes perfectly to the global domain\n    global_pred = pred_coeffs[0] * x**2 + pred_coeffs[1] * x + pred_coeffs[2]\n    global_true = 2 * x**2 - 3 * x + 1\n    \n    mse = torch.nn.functional.mse_loss(global_pred, global_true)\n    print(f"Global generalization error: {mse.item()}")\n    return mse',
    'sympy': 'import sympy as sp\n\nx = sp.Symbol(\'x\')\np = sp.Function(\'p\')(x)\nq = sp.Function(\'q\')(x)\n# Two polynomials of degree 2 that agree on 3 points must be identical everywhere\na1, b1, c1 = sp.symbols(\'a1 b1 c1\')\na2, b2, c2 = sp.symbols(\'a2 b2 c2\')\npoly1 = a1*x**2 + b1*x + c1\npoly2 = a2*x**2 + b2*x + c2\neqs = [poly1.subs(x, i) - poly2.subs(x, i) for i in [0, 1, 2]]\nsols = sp.solve(eqs, (a1, b1, c1))\n# Verify coefficients match\ndiff = sp.simplify((poly1.subs(sols) - poly2).subs(x, 5))\nassert diff == 0, "Zariski rigidity failed: polynomials do not match globally"'
  },
  {
    'id': 'ALG_GEO-640',
    'nid': 640,
    'name': '黎曼-罗赫定理 - 认知大统一：建立空间表面拓扑学特征（Euler 示性数）与其内部解析维度（独立函数数量）之间的奇迹公式。 (n_640)',
    'sub_topics': [
      '线丛 (Line bundles) 的度与截面空间维数',
      '亏格 (Genus) 在公式中的枢纽作用',
      '复曲线上的黎曼-罗赫公式形式',
      '物理直觉：流形“漏洞”数量限制了其承载信息的能力'
    ],
    'metaphor': 'A City Water Pipe Network. The surface is the pipe system, and the genus is the number of loops or holes. Pumps (poles) add water and drains (zeros) remove it. The number of independent ways water can flow without changing the net distribution is determined by the number of pumps minus the network\'s loops.',
    'pytorch': 'import torch\n\ndef riemann_roch_sim():\n    # Simulating topological constraints on vector space dimension\n    # g: genus, deg_D: degree of divisor\n    g = torch.tensor(2)  # A surface with 2 holes\n    deg_D = torch.tensor(5) # Adding 5 pumps\n    \n    # By Riemann-Roch for deg(D) > 2g - 2:\n    # l(D) = deg(D) + 1 - g\n    dim_L = deg_D + 1 - g\n    \n    print(f"Dimension of global sections (independent flows): {dim_L.item()}")\n    return dim_L',
    'sympy': 'import sympy as sp\n\nl_D, l_K_D, deg_D, g = sp.symbols(\'l_D l_K_D deg_D g\')\n# Riemann-Roch Theorem: l(D) - l(K-D) = deg(D) + 1 - g\n# For deg_D > 2g - 2, l_K_D is 0.\nrr_eq = l_D - l_K_D - (deg_D + 1 - g)\n\n# Substitute for a high degree divisor\nsubs_dict = {l_K_D: 0, deg_D: 5, g: 2}\ndim_l_D = sp.solve(rr_eq.subs(subs_dict), l_D)[0]\n\nexpected = 5 + 1 - 2\nassert sp.simplify(dim_l_D - expected) == 0, "Riemann-Roch dimension mismatch"'
  },
  {
    'id': 'ALG_GEO-645',
    'nid': 645,
    'name': '算术几何 - 揭示有理点在抽象曲线上近乎混沌却又充满对称性的排列规律。 (n_645)',
    'sub_topics': [
      '莫德尔 (Mordell) 猜想与法尔廷斯定理',
      '有理点数量的有限性与亏格的关系',
      '局部-全局原则（哈塞原理）',
      '数论算法在处理高维代数簇时的计算复杂性'
    ],
    'metaphor': 'A Pegboard Sieve. Finding rational points on a curve is like shining light through a curved sieve onto a uniform grid. Because the sieve is curved (high genus), it only lines up perfectly with a finite, scarce number of grid intersections.',
    'pytorch': 'import torch\n\ndef diophantine_search():\n    # Brute-force search for integer points on an elliptic curve y^2 = x^3 - x + 1\n    x = torch.arange(-100, 100, dtype=torch.float32)\n    y = torch.arange(-100, 100, dtype=torch.float32)\n    \n    X, Y = torch.meshgrid(x, y, indexing=\'ij\')\n    \n    # Evaluate the curve equation\n    left = Y**2\n    right = X**3 - X + 1\n    \n    # Find points where they exactly match\n    mask = (left == right)\n    points = torch.nonzero(mask)\n    \n    print(f"Found {len(points)} integer points in the domain.")\n    return points',
    'sympy': 'import sympy as sp\n\nx, y = sp.symbols(\'x y\')\n# Elliptic curve: y^2 = x^3 - x + 1\ncurve = y**2 - (x**3 - x + 1)\n\n# Test a known point (0, 1)\npt1 = curve.subs({x: 0, y: 1})\nassert sp.simplify(pt1) == 0, "Point (0,1) is not on the curve"\n\n# Test point (1, 1)\npt2 = curve.subs({x: 1, y: 1})\nassert sp.simplify(pt2) == 0, "Point (1,1) is not on the curve"\n\n# Negative test (2, 2)\npt3 = curve.subs({x: 2, y: 2})\nassert sp.simplify(pt3) != 0, "Point (2,2) should not be on the curve"'
  },
  {
    'id': 'ALG_GEO-650',
    'nid': 650,
    'name': '形变理论 - 动态演化：研究微小扰动下代数方程及其解空间的演变。 (n_650)',
    'sub_topics': [
      '形式形变与切空间的对应',
      '阻碍元 (Obstructions) 与上同调的关联',
      '柯代拉-斯潘塞 (Kodaira-Spencer) 映射',
      '物理背景：物理常数微调后的宇宙演化稳定性'
    ],
    'metaphor': 'A Spring-Loaded Frame. If you apply a slight push (deformation) to the frame, it adjusts elastically (first-order deformation space). However, if the joints are mutually constrained in conflicting ways, the stresses build up and block further bending (obstruction), maintaining its original shape.',
    'pytorch': 'import torch\n\ndef deformation_sim():\n    # A parameterized equation x^2 + y^2 = r(t)\n    # We study how the solution set (a circle) deforms as parameter t changes.\n    t = torch.tensor([0.0], requires_grad=True)\n    \n    def radius(t):\n        return 1.0 + 0.1 * t\n    \n    r = radius(t)\n    # Area of the circle\n    area = 3.14159 * r**2\n    \n    # First-order deformation of the area w.r.t t\n    area.backward()\n    grad = t.grad\n    \n    print(f"First-order deformation gradient: {grad.item()}")\n    return grad',
    'sympy': 'import sympy as sp\n\nx, epsilon = sp.symbols(\'x epsilon\')\n# Consider an algebraic equation x^2 - 1 = 0. Roots are 1, -1.\n# Deform it to x^2 - 1 + epsilon * x = 0\neq = x**2 - 1 + epsilon * x\n\n# Substitute x = 1 + c1*epsilon to find the first-order deformation of the root x=1\nc1 = sp.symbols(\'c1\')\ndeformed_root = 1 + c1 * epsilon\nexpansion = eq.subs(x, deformed_root).expand()\n\n# Extract the epsilon^1 term\nfirst_order_term = expansion.coeff(epsilon, 1)\nsol = sp.solve(first_order_term, c1)[0]\n\nassert sp.simplify(sol - (-1/sp.Rational(2))) == 0, "Deformation obstruction error"'
  },
  {
    'id': 'DIFF_GEO-655',
    'nid': 655,
    'name': '切向量场 - 物理意义：在流形每一点建立切空间并分配速度指针。描绘系统整体的语义演化“风向”与动力趋势。 (n_655)',
    'sub_topics': [
      '切空间 (Tangent Space) 的代数定义',
      '向量场作为切丛的截面 (Sections)',
      '积分曲线与流 (Flows) 的生成',
      '物理直觉：在流形表面的风力矢量分布场'
    ],
    'metaphor': 'Wind Vanes on a Landscape. At every point on a hilly terrain, there is a wind vane indicating the local wind direction and speed. The tangent vector field is the complete map of these vanes, dictating how a hot air balloon would drift over time.',
    'pytorch': 'import torch\n\ndef vector_field_flow():\n    # Simulating the flow of a vector field: v(x, y) = (-y, x) [rotation]\n    pos = torch.tensor([1.0, 0.0])\n    dt = 0.01\n    trajectory = [pos.clone()]\n    \n    for _ in range(100):\n        # Vector field evaluation\n        vx = -pos[1]\n        vy = pos[0]\n        v = torch.stack([vx, vy])\n        \n        # Euler integration step\n        pos = pos + v * dt\n        trajectory.append(pos.clone())\n        \n    trajectory = torch.stack(trajectory)\n    # The final distance to the origin should still be close to 1 (circular orbit)\n    radius = torch.norm(trajectory[-1])\n    print(f"Final radius (expected ~1.0): {radius.item()}")\n    return trajectory',
    'sympy': 'import sympy as sp\n\nx, y = sp.symbols(\'x y\')\nf = sp.Function(\'f\')(x, y)\n\n# Define two vector fields X and Y\n# X = -y d/dx + x d/dy\n# Y = x d/dx + y d/dy\n\ndef apply_X(expr):\n    return -y * sp.diff(expr, x) + x * sp.diff(expr, y)\n\ndef apply_Y(expr):\n    return x * sp.diff(expr, x) + y * sp.diff(expr, y)\n\n# Compute Lie Bracket [X, Y]f = X(Y(f)) - Y(X(f))\nXYf = apply_X(apply_Y(f))\nYXf = apply_Y(apply_X(f))\nlie_bracket = sp.simplify(XYf - YXf)\n\n# For these fields, [X, Y] = 0\nassert lie_bracket == 0, "Lie bracket computation failed"'
  },
  {
    'id': 'DIFF_GEO-660',
    'nid': 660,
    'name': '测地线 - 【流匹配映射】：弯曲空间中最平滑的轨迹。大模型扩散生成过程正是沿着 Wasserstein 流形的测地线将噪声还原为逻辑。 (n_660)',
    'sub_topics': [
      '变分法导出测地线方程',
      '测地线作为最短路径或极值轨迹',
      '指数映射 (Exponential map) 将切空间拉回流形',
      '物理映射：概率分布演化中的最小代价传输轨迹'
    ],
    'metaphor': 'Stretched Rubber Band. If you stretch a rubber band between two points on the surface of a bowling ball, it snaps into a configuration that minimizes tension. This un-accelerated, tension-minimizing path exactly traces a geodesic (a great circle).',
    'pytorch': 'import torch\n\ndef geodesic_minimization():\n    # Find geodesic between two points on a 2D plane by minimizing curve length\n    # (trivial case, should yield a straight line)\n    t = torch.linspace(0, 1, 10)\n    # Trainable intermediate points\n    y = torch.nn.Parameter(torch.zeros(10))\n    \n    optimizer = torch.optim.Adam([y], lr=0.1)\n    \n    for _ in range(200):\n        optimizer.zero_grad()\n        # Fix endpoints at y(0)=0, y(1)=1\n        y.data[0] = 0.0\n        y.data[-1] = 1.0\n        \n        # Compute path length\n        dx = t[1:] - t[:-1]\n        dy = y[1:] - y[:-1]\n        length = torch.sum(torch.sqrt(dx**2 + dy**2))\n        length.backward()\n        optimizer.step()\n        \n    # The resulting y should be close to t (y = x)\n    mse = torch.nn.functional.mse_loss(y, t)\n    print(f"Geodesic deviation from straight line: {mse.item()}")\n    return y',
    'sympy': 'import sympy as sp\n\nt = sp.Symbol(\'t\')\ntheta = sp.Function(\'theta\')(t)\nphi = sp.Function(\'phi\')(t)\n\n# Geodesic equations on a sphere of radius R=1\n# d^2 theta / dt^2 - sin(theta)cos(theta) (d phi / dt)^2 = 0\n# d^2 phi / dt^2 + 2 cot(theta) (d theta / dt) (d phi / dt) = 0\n\neq1 = sp.diff(theta, t, 2) - sp.sin(theta)*sp.cos(theta)*sp.diff(phi, t)**2\neq2 = sp.diff(phi, t, 2) + 2*(sp.cos(theta)/sp.sin(theta))*sp.diff(theta, t)*sp.diff(phi, t)\n\n# Test a specific geodesic: the equator. theta = pi/2, phi = omega * t\nomega = sp.Symbol(\'omega\')\nsub_dict = {theta: sp.pi/2, phi: omega * t}\n\nval1 = sp.simplify(eq1.subs(sub_dict).doit())\nval2 = sp.simplify(eq2.subs(sub_dict).doit())\n\nassert val1 == 0 and val2 == 0, "Equator failed the geodesic equations"'
  },
  {
    'id': 'DIFF_GEO-665',
    'nid': 665,
    'name': 'de Rham上同调 - 探测机制：利用微分形式像雷达一样精准探测高维流形内部隐藏的“拓扑空洞”。 (n_665)',
    'sub_topics': [
      '外微分复形的同调性分析',
      '德·拉姆定理：解析上同调与奇异同调的等价性',
      '空间中“不可被积”障碍的代数表征',
      '物理直觉：寻找流形中流体环流的瓶颈点'
    ],
    'metaphor': 'Fluid Vortex Around an Island. Imagine water swirling in a steady flow around a central island. If you try to sum the local swirling flow around any loop enclosing the island, you get a non-zero value, proving the island exists even if you cannot see it directly. This maps to a closed but not exact differential form.',
    'pytorch': 'import torch\n\ndef de_rham_discrete():\n    # A discrete simulation of 1-forms on a triangle graph (3 nodes, 3 edges)\n    # Nodes: 0, 1, 2. Edges: 0->1, 1->2, 2->0\n    # Boundary operator for 1D to 0D (Vertices to Edges)\n    d0 = torch.tensor([[-1.0, 1.0, 0.0],\n                       [0.0, -1.0, 1.0],\n                       [1.0, 0.0, -1.0]])\n    \n    # A 0-form (function on nodes)\n    f = torch.tensor([1.0, 2.0, 4.0])\n    \n    # Exact 1-form df\n    df = torch.matmul(d0, f)\n    \n    # The sum of values of an exact 1-form along a closed loop is 0\n    loop_integral = torch.sum(df)\n    print(f"Loop integral of exact 1-form: {loop_integral.item()}")\n    return loop_integral',
    'sympy': 'import sympy as sp\n\nx, y = sp.symbols(\'x y\')\n# Define the vortex 1-form: w = P dx + Q dy\n# P = -y/(x^2+y^2), Q = x/(x^2+y^2)\nP = -y / (x**2 + y**2)\nQ = x / (x**2 + y**2)\n\n# Compute the exterior derivative dw = (dQ/dx - dP/dy) dx ^ dy\ndQ_dx = sp.diff(Q, x)\ndP_dy = sp.diff(P, y)\ndw = sp.simplify(dQ_dx - dP_dy)\n\n# The form is closed (dw = 0 everywhere except the origin)\nassert dw == 0, "The 1-form is not closed."\n\n# Yet it is not exact because its integral over the unit circle is 2*pi.'
  },
  {
    'id': 'ALG_TOP-670',
    'nid': 670,
    'name': '基本群 - 代数化：将所有等价环路打包成群，作为探测空间连通性的初级雷达。 (n_670)',
    'sub_topics': [
      '群运算作为环路的拼接',
      '映射诱导的同态性质',
      '基本群在拓扑空间分类中的第一判据作用',
      '在知识图谱闭环逻辑验证中的应用'
    ],
    'metaphor': 'Lassoing a Pole. Throwing a lasso loop across a flat plain means you can freely pull it back to yourself. If there\'s a pole sticking out of the ground, and your lasso lands around it, the rope gets caught. Counting how many times the lasso wraps the pole corresponds to the fundamental group classifying the distinct loops.',
    'pytorch': 'import torch\nimport numpy as np\n\ndef fundamental_group_winding():\n    # Compute winding number of a path around the origin\n    # Path 1: A circle around the origin\n    t = torch.linspace(0, 2 * np.pi, 100)\n    x = torch.cos(t)\n    y = torch.sin(t)\n    \n    # Compute angles and sum differences\n    angles = torch.atan2(y, x)\n    diffs = angles[1:] - angles[:-1]\n    \n    # Correct for branch cuts\n    diffs = torch.where(diffs > np.pi, diffs - 2 * np.pi, diffs)\n    diffs = torch.where(diffs < -np.pi, diffs + 2 * np.pi, diffs)\n    \n    total_wind = torch.sum(diffs) / (2 * np.pi)\n    print(f"Winding number: {total_wind.item():.2f}")\n    return torch.round(total_wind)',
    'sympy': 'import sympy as sp\n\nt = sp.Symbol(\'t\', real=True)\n# Path of a unit circle\nx = sp.cos(t)\ny = sp.sin(t)\n\n# Form: (x dy - y dx) / (x^2 + y^2)\ndx = sp.diff(x, t)\ndy = sp.diff(y, t)\nintegrand = (x * dy - y * dx) / (x**2 + y**2)\n\n# Integrate from 0 to 2*pi\nwinding_number_val = sp.integrate(integrand, (t, 0, 2*sp.pi))\n\n# Winding number must be exactly 2*pi (which normalizes to 1)\nassert sp.simplify(winding_number_val - 2*sp.pi) == 0, "Fundamental group winding fails"'
  },
  {
    'id': 'ALG_TOP-675',
    'nid': 675,
    'name': '上同调环 - 代数跃迁：引入杯积（Cup Product），探测空间中空洞交叉碰撞产生的低维新空洞，为拓扑性质赋予坚固的环代数结构。 (n_675)',
    'sub_topics': [
      '上同调类的杯积运算规则',
      '上同调环的对偶性与乘法结构',
      '探测多维障碍物之间的代数耦合关系',
      '物理意义：不同维度的“阻隔”如何共同作用于全域流动'
    ],
    'metaphor': 'Intersecting Shadows in a Grating. Imagine a box with vertical slits on one side and horizontal slits on another. If light beams from both sides pass through, their intersection forms discrete glowing points (0-dimensional). The cup product algebraically tracks how combining these 1D structural gaps yields a solid lower-dimensional footprint.',
    'pytorch': 'import torch\n\ndef cohomology_cup_product_sim():\n    # Simulating cup product via intersection of submanifolds\n    # In a 3D grid, represent a plane x=0 (codim 1) and a plane y=0 (codim 1)\n    grid = torch.zeros((5, 5, 5))\n    \n    # Form 1: plane x=2\n    form1 = torch.zeros_like(grid)\n    form1[2, :, :] = 1.0\n    \n    # Form 2: plane y=2\n    form2 = torch.zeros_like(grid)\n    form2[:, 2, :] = 1.0\n    \n    # Cup product ~ wedge product ~ intersection\n    cup_product = form1 * form2\n    \n    # The intersection should be a 1D line (codim 2)\n    intersection_size = torch.sum(cup_product)\n    print(f"Intersection size (should be 5, representing a line of length 5): {intersection_size.item()}")\n    return intersection_size',
    'sympy': 'import sympy as sp\n\n# Simulate wedge product properties of cohomology classes\ndx, dy, dz = sp.symbols(\'dx dy dz\')\n# Define a simple anti-commutative product function for 1-forms\ndef wedge(a, b):\n    # very basic symbolic check for wedge of basic 1-forms\n    if a == b:\n        return 0\n    # enforce alphabetical order for standard basis\n    if str(a) > str(b):\n        return -sp.Symbol(f"{b}^{a}")\n    return sp.Symbol(f"{a}^{b}")\n\n# w1 ^ w1 = 0\nassert wedge(dx, dx) == 0, "Cup product of odd degree class with itself should be 0"\n\n# w1 ^ w2 = - w2 ^ w1\nres1 = wedge(dx, dy)\nres2 = wedge(dy, dx)\nassert sp.simplify(res1 + res2) == 0, "Anticommutativity failed"'
  },
  {
    'id': 'ALG_TOP-680',
    'nid': 680,
    'name': 'CW复形 - 拓扑原子：通过 Builder Pattern 逐步粘合 0 维到 n 维细胞构建高维对象，是构建绝大多数物理意义空间的“乐高积木”。 (n_680)',
    'sub_topics': [
      '细胞 (Cells) 的粘合映射 (Attaching maps)',
      'CW 空间的归纳构造过程',
      '复形的有限性与弱拓扑性质',
      '物理模拟：从像素点到几何体的高效层级构建'
    ],
    'metaphor': 'Building a Tent Frame. You start by placing pegs in the ground (0-cells). Then you connect the pegs with flexible poles (1-cells). Finally, you stretch large sheets of fabric (2-cells) and glue their edges to the pole framework. This stepwise assembly perfectly maps the CW complex construction.',
    'pytorch': 'import torch\n\ndef cw_complex_euler():\n    # Construct a tetrahedron as a CW complex\n    # 0-cells (vertices): 4\n    v = torch.ones(4)\n    \n    # 1-cells (edges): 6\n    e = torch.ones(6)\n    \n    # 2-cells (faces): 4\n    f = torch.ones(4)\n    \n    # Compute Euler characteristic: V - E + F\n    chi = torch.sum(v) - torch.sum(e) + torch.sum(f)\n    \n    print(f"Euler characteristic of Tetrahedron (Sphere S2): {chi.item()}")\n    return chi',
    'sympy': 'import sympy as sp\n\n# Euler characteristic V - E + F = 2 for a sphere\nV, E, F = sp.symbols(\'V E F\')\neuler_eq = V - E + F\n\n# Cube CW structure: 8 vertices, 12 edges, 6 faces\ncube_chi = euler_eq.subs({V: 8, E: 12, F: 6})\nassert sp.simplify(cube_chi - 2) == 0, "Cube Euler characteristic should be 2"\n\n# Point CW structure: 1 vertex, 0 edges, 0 faces\npt_chi = euler_eq.subs({V: 1, E: 0, F: 0})\nassert sp.simplify(pt_chi - 1) == 0, "Point Euler characteristic should be 1"'
  }
]

out_dir = r"E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/_Staging_Level6_Part1"
os.makedirs(out_dir, exist_ok=True)

for item in data:
    node_id = item['id']
    
    yaml_content = f"""version: "9.1"
node_id: {node_id}
node_name: "{item['name']}"
mode: A

llm_physical_mapping: >
  {item['metaphor']}

sub_topics:
"""
    for sub in item['sub_topics']:
        yaml_content += f"  - {sub}\n"
        
    pytorch_indented = item['pytorch'].replace('\n', '\n  ')
    sympy_indented = item['sympy'].replace('\n', '\n    ')
    
    yaml_content += f"""
code_implementation: |-
  {pytorch_indented}

v8_sanity_audit:
  sympy_pseudo_code: |-
    {sympy_indented}
"""

    filepath = os.path.join(out_dir, f"{node_id}.yaml")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

print("Generation complete!")

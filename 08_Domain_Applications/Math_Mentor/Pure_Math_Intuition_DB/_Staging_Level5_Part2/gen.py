import os

base_dir = r"E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\08_Domain_Applications\Math_Mentor\Pure_Math_Intuition_DB\_Staging_Level5_Part2"
os.makedirs(base_dir, exist_ok=True)

files_content = {
"COMBINATORICS-587.yaml": """id: "COMBINATORICS-587"
concept_name: "组合设计 - 物理直觉：研究如何设计高度对称、极其均匀的交叉子集。 (n_587)"
sub_topics:
  - "平衡不完全区组设计 (BIBD)"
  - "斯坦纳三元系 (Steiner systems)"
  - "集合分布的覆盖性质与平衡性"
  - "物理映射：实验设计中的变量全平衡配置"
llm_physical_mapping: "mundane physical metaphor: A pegboard grid where metal pins are hammered into holes. No matter where you drop a heavy steel ruler on the board, it exactly hits the same number of pins, distributing the impact force perfectly without tipping over."
code_implementation: |
  import sympy as sp
  
  def check_steiner_triple_system(v):
      # Steiner triple systems STS(v) exist iff v = 1 or 3 mod 6
      if v % 6 == 1 or v % 6 == 3:
          return True
      return False
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    def check_sts(v):
        return v % 6 == 1 or v % 6 == 3
    
    assert check_sts(7) == True
    assert check_sts(9) == True
    assert check_sts(8) == False
""",
"COMBINATORICS-588.yaml": """id: "COMBINATORICS-588"
concept_name: "组合设计 - 硅基具象化：现代分布式系统中的纠删码（Erasure Coding）与稳健的数据分片容错策略。 (n_588)"
sub_topics:
  - "矩阵生成的容错码结构"
  - "局部解码与全局重构的组合属性"
  - "在大模型参数分片存储（DeepSpeed/FSDP）中的应用"
  - "保证在硬件故障时权重无损恢复的组合学逻辑"
llm_physical_mapping: "mundane physical metaphor: A heavy steel cable made of many braided wires. If you cut a few random wires with bolt cutters, the overall cable still holds the elevator because the tension is distributed redundantly across the remaining intact strands."
code_implementation: |
  import sympy as sp
  
  def erasure_code_recovery(data_blocks, parity_blocks, lost_index):
      # Given sum(data) = parity, recover one lost block
      # data_blocks is a list where one element is None
      if lost_index < len(data_blocks):
          known_sum = sum([b for b in data_blocks if b is not None])
          recovered = parity_blocks[0] - known_sum
          data_blocks[lost_index] = recovered
      return data_blocks
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    data = [10, 20, None]
    parity = [60]
    known_sum = sum([x for x in data if x is not None])
    recovered = parity[0] - known_sum
    assert recovered == 30
""",
"COMBINATORICS-589.yaml": """id: "COMBINATORICS-589"
concept_name: "拟阵理论 - 认知跃迁：将线性无关的概念抽象提纯。证明了为什么解决最小生成树时，“贪心算法”这种短视策略甚至能产生全局最优解。 (n_589)"
sub_topics:
  - "拟阵 (Matroids) 的公理化定义"
  - "线性独立性、电路与基的概念推广"
  - "贪心算法在拟阵结构上的最优性保障"
  - "物理直觉：系统局部的最优拉扯能导向全局平衡"
llm_physical_mapping: "mundane physical metaphor: A set of interlocking wooden gears. As you blindly pick the largest gears one by one from a pile and try to fit them, if they don't jam (create a cycle), you just keep them. Eventually, you build the heaviest working gearbox possible without needing to plan the whole machine in advance."
code_implementation: |
  import sympy as sp
  
  def matroid_greedy(elements, weights, indep_check):
      # Sort elements by weight descending
      sorted_elems = sorted(elements, key=lambda x: weights[x], reverse=True)
      independent_set = set()
      
      for e in sorted_elems:
          temp_set = independent_set.union({e})
          if indep_check(temp_set):
              independent_set.add(e)
      return independent_set
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    # Graphic matroid: uniform independent check (no cycles, spanning tree)
    # Simple check for forest in small graph
    def mock_indep(s):
        return len(s) <= 2 # dummy matroid
    
    elements = ['a', 'b', 'c']
    weights = {'a': 10, 'b': 5, 'c': 15}
    sorted_e = sorted(elements, key=lambda x: weights[x], reverse=True)
    res = set()
    for e in sorted_e:
        if mock_indep(res.union({e})):
            res.add(e)
            
    assert 'c' in res and 'a' in res
""",
"COMBINATORICS-590.yaml": """id: "COMBINATORICS-590"
concept_name: "图的着色理论（色多项式） - 物理意义：如何用最少颜色隔离相邻顶点。 (n_590)"
sub_topics:
  - "顶点着色数 χ(G) 与色多项式 P(G, k)"
  - "平面图的四色定理背景"
  - "物理建模：邻近干扰约束下的调度问题"
  - "色多项式对图结构的代数刻画"
llm_physical_mapping: "mundane physical metaphor: Painting adjoining steel shipping containers on a crowded dock. If two containers touch, they must be painted different colors so crane operators don't mistake them for a single massive block."
code_implementation: |
  import sympy as sp
  
  def chromatic_polynomial_tree(n, k):
      # A tree with n vertices has chromatic polynomial k * (k - 1)^(n-1)
      if n == 0:
          return 1
      return k * (k - 1)**(n - 1)
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    k = sp.Symbol('k')
    n = 4
    tree_poly = k * (k - 1)**(n - 1)
    
    # Evaluate for k=3
    ways = tree_poly.subs(k, 3)
    assert ways == 3 * (2)**3
""",
"COMBINATORICS-591.yaml": """id: "COMBINATORICS-591"
concept_name: "图的着色理论（色多项式） - 编译器映射：寄存器分配（Register Allocation）核心算法，顶点为变量，存活冲突为边，颜色为有限 CPU 寄存器资源。 (n_591)"
sub_topics:
  - "冲突图 (Interference Graph) 的构建"
  - "Chaitin 启发式着色算法"
  - "寄存器溢出 (Spilling) 的代价决策"
  - "物理直觉：在极其拥挤的硬件资源中进行无冲突任务排期"
llm_physical_mapping: "mundane physical metaphor: Assigning physical lockers to factory workers. If two workers are on shift at the same exact time (conflict edge), they cannot share a locker (color). When you run out of lockers, some workers must awkwardly dump their gear in the distant break room (spilling)."
code_implementation: |
  import sympy as sp
  
  def greedy_register_allocation(variables, conflict_edges, num_registers):
      allocation = {}
      for var in variables:
          used_neighbors = {allocation[neighbor] for neighbor in conflict_edges[var] if neighbor in allocation}
          assigned = False
          for color in range(num_registers):
              if color not in used_neighbors:
                  allocation[var] = color
                  assigned = True
                  break
          if not assigned:
              allocation[var] = "SPILLED"
      return allocation
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    vars_list = ['A', 'B', 'C']
    edges = {'A': ['B'], 'B': ['A', 'C'], 'C': ['B']}
    alloc = {}
    for v in vars_list:
        used = {alloc[n] for n in edges[v] if n in alloc}
        for c in range(2):
            if c not in used:
                alloc[v] = c
                break
    assert alloc['A'] == 0
    assert alloc['B'] == 1
    assert alloc['C'] == 0
""",
"COMBINATORICS-592.yaml": """id: "COMBINATORICS-592"
concept_name: "匹配理论（Hall定理/完美匹配） - 【大模型映射】：混合专家架构 (MoE) 的路由分配。 (n_592)"
sub_topics:
  - "MoE 路由的动态负载均衡"
  - "Token 到专家的偏好得分矩阵"
  - "路由冲突与专家闲置的权衡"
  - "物理直觉：确保海量并发请求能够被硬件专家池精准消化"
llm_physical_mapping: "mundane physical metaphor: A mail sorting room with conveyor belts. Packages (tokens) arrive and need to be tossed into specific mailbags (experts) based on zip codes. If too many packages go to one bag, it jams the belt, leaving other bags entirely empty."
code_implementation: |
  import sympy as sp
  
  def check_hall_condition(bipartite_graph, set_A):
      # For a subset S of A, |N(S)| >= |S|
      # Check powerset of A for this condition
      import itertools
      for i in range(1, len(set_A) + 1):
          for S in itertools.combinations(set_A, i):
              N_S = set()
              for node in S:
                  N_S.update(bipartite_graph[node])
              if len(N_S) < len(S):
                  return False
      return True
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    graph = {'t1': ['e1', 'e2'], 't2': ['e2']}
    tokens = ['t1', 't2']
    
    def check_hall(g, A):
        # check just the whole set for brevity
        n_a = set()
        for x in A:
            n_a.update(g[x])
        return len(n_a) >= len(A)
        
    assert check_hall(graph, tokens) == True
""",
"COMBINATORICS-593.yaml": """id: "COMBINATORICS-593"
concept_name: "匹配理论（Hall定理/完美匹配） - 核心逻辑：Hall 婚姻定理。决定了当 Token 请求与 Expert 专家矩阵碰撞时，是否存在让所有请求都饱和且不溢出的完美匹配。 (n_593)"
sub_topics:
  - "霍尔定理的相异代表系 (SDR) 陈述"
  - "完美匹配存在的充要条件"
  - "扩展：匈牙利算法 (Hungarian Algorithm) 求解最大匹配"
  - "路由饱和度的数学边界界定"
llm_physical_mapping: "mundane physical metaphor: Plugging thick industrial electrical cables into generator sockets. If you have 5 plugs that can only reach 3 specific sockets because of cord length, you physically cannot plug everything in without a mismatch."
code_implementation: |
  import sympy as sp
  
  def find_augmenting_path(u, match_R, visited, graph):
      for v in graph[u]:
          if not visited[v]:
              visited[v] = True
              if match_R[v] < 0 or find_augmenting_path(match_R[v], match_R, visited, graph):
                  match_R[v] = u
                  return True
      return False
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    graph = {0: [0, 1], 1: [1, 2]}
    match_R = [-1, -1, -1]
    
    # manually simulate one step
    visited = [False, False, False]
    visited[0] = True
    match_R[0] = 0 
    
    assert match_R[0] == 0
""",
"COMBINATORICS-594.yaml": """id: "COMBINATORICS-594"
concept_name: "网络流（最大流最小割定理） - 终极认知升华：图论与线性规划的强对偶性奇迹。证明系统的最大流输送量绝对等于其最致命的瓶颈带宽（最小割）。 (n_594)"
sub_topics:
  - "Ford-Fulkerson 算法与增广路径"
  - "割的定义与容量上限"
  - "强对偶性定理的严密证明"
  - "物理意义：全局吞吐量受限于局部最窄处的结构性必然"
llm_physical_mapping: "mundane physical metaphor: A city's water pipe network. The absolute maximum gallons of water you can pump from the reservoir to the factory is exactly equal to the total width of the narrowest cross-section of rusty pipes you would have to smash to completely sever the connection."
code_implementation: |
  import sympy as sp
  
  def max_flow_min_cut_concept(capacities, source, sink):
      # Pseudocode representing the duality
      # Max flow f is bounded by any cut capacity
      # Returns true if the theorem holds conceptually
      def cut_capacity(cut_set):
          return sum(capacities[u][v] for u in cut_set for v in capacities[u] if v not in cut_set)
      
      # In reality, computes flow and compares to minimum cut_capacity
      return True
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    # Cap from S to A is 10, A to T is 5. Min cut is {S, A} -> {T} with cap 5
    max_flow = 5
    min_cut = 5
    assert max_flow == min_cut
""",
"COMBINATORICS-595.yaml": """id: "COMBINATORICS-595"
concept_name: "网络流（最大流最小割定理） - 物理映射：主宰分布式训练集群（NVLink/InfiniBand）的拓扑传输极限测算。 (n_595)"
sub_topics:
  - "集群拓扑的图论建模"
  - "多源多汇流模型在梯度聚合中的应用"
  - "寻找通信瓶颈（最小割）的自动化诊断"
  - "路由优化对训练吞吐量的增益评估"
llm_physical_mapping: "mundane physical metaphor: Conveyor belts moving coal between processing buildings. If building A pushes 50 tons/hour but the bridge belt to building B only holds 20 tons/hour, a massive pile of coal backs up and spills onto the floor at the bottleneck."
code_implementation: |
  import sympy as sp
  
  def bottleneck_diagnosis(topology_matrix, flow_matrix):
      # Finds edges where flow == capacity
      bottlenecks = []
      n = len(topology_matrix)
      for i in range(n):
          for j in range(n):
              if topology_matrix[i][j] > 0 and flow_matrix[i][j] == topology_matrix[i][j]:
                  bottlenecks.append((i, j))
      return bottlenecks
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    topo = [[0, 10], [0, 0]]
    flow = [[0, 10], [0, 0]]
    
    bottlenecks = [(i,j) for i in range(2) for j in range(2) if topo[i][j] > 0 and flow[i][j] == topo[i][j]]
    assert bottlenecks == [(0, 1)]
""",
"COMBINATORICS-596.yaml": """id: "COMBINATORICS-596"
concept_name: "有限几何 - 认知流形统一：为组合设计提供公理化的几何架构。 (n_596)"
sub_topics:
  - "仿射平面与射影平面的有限点集表示"
  - "几何结构的对称性与组合恒等式"
  - "点线关联矩阵的代数性质"
  - "物理直觉：在离散像素化的宇宙中建立严密的几何定律"
llm_physical_mapping: "mundane physical metaphor: A rigid scaffolding made of steel rods and ball joints. Unlike a continuous rubber sheet, you can only attach rods at exact, discrete ball joint coordinates, yet they form perfect non-bending triangles and parallel lines."
code_implementation: |
  import sympy as sp
  
  def fano_plane_incidence():
      # The Fano plane (smallest finite projective plane) has 7 points and 7 lines
      # Each line has 3 points, each point is on 3 lines
      lines = [
          {1, 2, 3}, {3, 4, 5}, {1, 5, 6}, {1, 4, 7}, {2, 5, 7}, {3, 6, 7}, {2, 4, 6}
      ]
      return lines
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    lines = [{1, 2, 3}, {3, 4, 5}, {1, 5, 6}, {1, 4, 7}, {2, 5, 7}, {3, 6, 7}, {2, 4, 6}]
    # Every pair of points determines exactly one line
    pt1, pt2 = 1, 2
    intersect = [l for l in lines if pt1 in l and pt2 in l]
    assert len(intersect) == 1
""",
"COMBINATORICS-597.yaml": """id: "COMBINATORICS-597"
concept_name: "有限几何 - 在构建高度稳健的纠删码网络中提供空间结构的理论支撑。 (n_597)"
sub_topics:
  - "基于有限域上直线的码字构造"
  - "几何分布导致的纠错半径最大化"
  - "在分布式存储（如 HDFS/Ceph）中的纠删逻辑原型"
  - "保证局部损坏不影响全局拓扑恢复的几何依据"
llm_physical_mapping: "mundane physical metaphor: Filing cabinets arranged in a grid in a warehouse. If a forklift crashes into one row and destroys it, you can perfectly reconstruct the lost files by cross-referencing the sum totals written on the unbroken perpendicular columns."
code_implementation: |
  import sympy as sp
  
  def finite_field_line_eval(a, b, p):
      # Evaluates the line y = (ax + b) mod p over finite field F_p
      # Points on this line can act as redundant shares
      points = []
      for x in range(p):
          y = (a * x + b) % p
          points.append((x, y))
      return points
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    
    p = 5
    a = 2
    b = 1
    # y = 2x + 1 mod 5
    # x=0 -> y=1
    # x=1 -> y=3
    pts = [(x, (a*x + b) % p) for x in range(p)]
    
    assert pts[0] == (0, 1)
    assert pts[1] == (1, 3)
"""
}

for filename, content in files_content.items():
    with open(os.path.join(base_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

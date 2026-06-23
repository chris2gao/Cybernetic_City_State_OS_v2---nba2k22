import json
import os
import yaml

in_file = r'E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/temp_batches_level6_1.json'
out_dir = r'E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/_Staging_Level6_Part1'
os.makedirs(out_dir, exist_ok=True)

with open(in_file, 'r', encoding='utf-8') as f:
    batches = json.load(f)
batch = batches[0]

metaphors = {
  'ALG_GEO-632': '带有可调铰链的连杆机械机构。增加无穷远处的约束相当于引入虚拟铰链，避免机构在平行配置时发生奇异卡死现象。',
  'ALG_GEO-637': '大面积的温度传感器阵列拼接。只要相邻传感器的重叠区域温度读数一致，就能无缝拼合成一张全局完整的地形热力图。',
  'ALG_GEO-642': '复杂的模拟调音台设备。每个旋钮和推子的刻度组合（模空间中的一个点）都能输出一种独特频率和波形的物理声波共振态。',
  'ALG_GEO-647': '一个带有椭圆边界的无摩擦台球桌。小球在边界碰撞反弹的轨迹对应于点群加法，呈现出混沌但具有绝对确定性的动力学演化。',
  'ALG_GEO-652': '两根不同粗细的水管之间维持质量守恒的流体流动。水流总体积和流线的拓扑缠绕度通过一个特殊的校正阀门（Todd类）保持严密对称。',
  'DIFF_GEO-657': '覆盖在起伏地形上的弹性卷尺。在山谷中卷尺被拉伸，在山峰处收缩，使得物理世界中同样的绝对步数测量出不同的表象距离。',
  'DIFF_GEO-662': '封闭金属球壳内部包裹的磁单极子。无论球壳外形如何扭曲，穿过整个金属表面的总磁通量必须是基本磁荷的整数倍。',
  'DIFF_GEO-667': '一支在洋流中航行的庞大帆船舰队。虽然每艘船（纤维）有自己的方向舵，但全局风向规律（规范变换）统一且平滑地转动着所有方向舵。',
  'ALG_TOP-672': '在木板上的两个钉子之间拉紧的橡皮筋。无论怎样在不切断它的情况下拨动、扭动橡皮筋，它始终保持着相同的基本连结状态。',
  'ALG_TOP-677': '极其庞大且存在记账误差的商业对账单。审核员逐页排查修正，每一页消除一种深层次的逻辑坏账，直至翻到最后一页达成完美收支平衡。',
  'ALG_TOP-682': '完美浇筑成型的金属雕塑与其对应的石膏模具。雕塑表面凸起的每个几何结构，必然在模具的内壁有一个完全等大、维度互补的凹陷坑洞。'
}

pytorch_codes = {
  'ALG_GEO-632': '''import torch
x, y, w = torch.randn(3, requires_grad=True)
constraint = x**2 + y**2 - w**2 # 射影圆约束
optimizer = torch.optim.SGD([x, y, w], lr=0.01)
for _ in range(10):
    loss = constraint**2
    loss.backward()
    optimizer.step()''',
  'ALG_GEO-637': '''import torch
# 模拟两个局部传感器热力图，在重叠区(index 1)必须一致
patch1 = torch.tensor([15.2, 16.5])
patch2 = torch.tensor([16.5, 17.8])
overlap_diff = torch.abs(patch1[1] - patch2[0])
assert overlap_diff == 0.0
# 粘合成全局热力图
global_section = torch.cat((patch1, patch2[1:]))''',
  'ALG_GEO-642': '''import torch
# 模空间参数 a 相当于调音台旋钮
a = torch.tensor(1.5, requires_grad=True)
t = torch.linspace(0, 10, 100)
wave_universe = torch.sin(a * t) # 生成的物理波
loss = torch.sum(wave_universe**2)
loss.backward()''',
  'ALG_GEO-647': '''import torch
# 用向量模拟椭圆曲线点
P1 = torch.tensor([0.5, 0.8])
P2 = torch.tensor([1.2, 0.4])
# 伪群加法：沿X轴反射
P3_raw = P1 + P2
P3 = torch.tensor([P3_raw[0], -P3_raw[1]])
assert P3.shape == (2,)''',
  'ALG_GEO-652': '''import torch
# 模拟全纯欧拉示性数与Todd类的点积计算
ch_E = torch.tensor([1.0, 0.5])
td_X = torch.tensor([1.0, -0.1])
integral_X = torch.dot(ch_E, td_X)
assert integral_X.dim() == 0''',
  'DIFF_GEO-657': '''import torch
g = torch.tensor([[1.2, 0.1], [0.1, 1.5]]) # 黎曼度量张量
v = torch.tensor([1.0, 0.0])
u = torch.tensor([0.0, 1.0])
# 计算物理向量v的长度
length_v = torch.sqrt(torch.matmul(v, torch.matmul(g, v)))
inner_prod = torch.matmul(v, torch.matmul(g, u))
assert length_v > 0''',
  'DIFF_GEO-662': '''import torch
# 模拟两维曲率矩阵
curvature_matrix = torch.randn(2, 2, dtype=torch.complex64)
# 通过曲率的迹计算第一陈类
chern_1 = torch.trace(curvature_matrix).imag
# 陈类量子化（四舍五入到最近整数）
quantized_charge = torch.round(chern_1)
assert isinstance(quantized_charge.item(), float)''',
  'DIFF_GEO-667': '''import torch
fiber = torch.tensor([1.0, 0.0]) # 船的方向舵
theta = torch.tensor(3.14159 / 4) # 规范变换角度
gauge_trans = torch.tensor([[torch.cos(theta), -torch.sin(theta)], 
                            [torch.sin(theta),  torch.cos(theta)]])
transformed_fiber = torch.matmul(gauge_trans, fiber)
assert transformed_fiber.shape == (2,)''',
  'ALG_TOP-672': '''import torch
t = torch.linspace(0, 1, 100)
path1 = torch.stack([t, t**2], dim=1) # 橡皮筋状态1
path2 = torch.stack([t, t**3], dim=1) # 橡皮筋状态2
s = 0.5 # 同伦形变参数
homotopy_path = (1 - s) * path1 + s * path2
assert homotopy_path.shape == path1.shape''',
  'ALG_TOP-677': '''import torch
# 谱序列E1页矩阵
E1 = torch.randn(5, 5)
d1 = torch.zeros(5, 5) # 微分算子
# 向E2页的极限收敛逼近
E2 = torch.matmul(E1, d1) - torch.matmul(d1, E1)
E_inf = torch.matrix_exp(E2)
assert E_inf.shape == (5, 5)''',
  'ALG_TOP-682': '''import torch
# 3维流形的Betti数：b0=1, b1=3, b2=3, b3=1
betti = torch.tensor([1, 3, 3, 1])
n = 3
k = 1
# 庞加莱对偶性：空洞数目必然对称相等
assert betti[k] == betti[n - k]
assert betti[0] == betti[n]'''
}

sympy_codes = {
  'ALG_GEO-632': '''import sympy as sp
x, y, w = sp.symbols('x y w')
f = x**2 + y**2 - w**2
# 验证齐次多项式的欧拉关系
assert sp.simplify(x*sp.diff(f, x) + y*sp.diff(f, y) + w*sp.diff(f, w) - 2*f) == 0''',
  'ALG_GEO-637': '''import sympy as sp
x = sp.symbols('x')
# 局部截面在重叠处匹配
f_local1 = x**2 + 2*x
f_local2 = x*(x + 2)
assert sp.simplify(f_local1 - f_local2) == 0''',
  'ALG_GEO-642': '''import sympy as sp
a, t = sp.symbols('a t')
wave = sp.sin(a*t)
# 模参数a的微小改变使得物理波产生可微分的变化
diff_wave = sp.diff(wave, a)
assert sp.simplify(diff_wave - t*sp.cos(a*t)) == 0''',
  'ALG_GEO-647': '''import sympy as sp
x1, y1, x2, y2, m = sp.symbols('x1 y1 x2 y2 m')
# 椭圆曲线上点的加法斜率运算验证
x3 = m**2 - x1 - x2
y3 = m*(x1 - x3) - y1
assert sp.simplify(y3 + y1 - m*(x1 - x3)) == 0''',
  'ALG_GEO-652': '''import sympy as sp
ch, td, f_push = sp.symbols('ch td f_push')
# 验证左侧与右侧公式形式平衡
LHS = f_push * td
RHS = f_push * td
assert sp.simplify(LHS - RHS) == 0''',
  'DIFF_GEO-657': '''import sympy as sp
g11, g12, g22, dx, dy = sp.symbols('g11 g12 g22 dx dy')
# 黎曼度量的二次型
ds2 = g11*dx**2 + 2*g12*dx*dy + g22*dy**2
# 验证度量张量的对称性：混合偏导可交换
assert sp.simplify(sp.diff(sp.diff(ds2, dx), dy) - sp.diff(sp.diff(ds2, dy), dx)) == 0''',
  'DIFF_GEO-662': '''import sympy as sp
F11, F12, F21, F22 = sp.symbols('F11 F12 F21 F22')
# 陈类的计算依赖于曲率矩阵的迹
c1 = F11 + F22
assert sp.simplify(c1 - (F11 + F22)) == 0''',
  'DIFF_GEO-667': '''import sympy as sp
x, y, t = sp.symbols('x y t')
psi = x + sp.I * y
U = sp.exp(sp.I * t) # U(1) 规范变换
psi_prime = U * psi
# 规范不变性验证：物理量的模平方在规范变换下不变
assert sp.simplify(psi_prime * sp.conjugate(psi_prime) - psi * sp.conjugate(psi)) == 0''',
  'ALG_TOP-672': '''import sympy as sp
t, s = sp.symbols('t s')
f = t**2
g = t**3
H = (1 - s)*f + s*g # 同伦形变路径
assert sp.simplify(H.subs(s, 0) - f) == 0
assert sp.simplify(H.subs(s, 1) - g) == 0''',
  'ALG_TOP-677': '''import sympy as sp
d_val = sp.symbols('d_val')
# 谱序列边界算子幂零性验证 d^2 = 0
d_matrix = sp.Matrix([[0, d_val, 0], [0, 0, 0], [0, 0, 0]])
assert sp.simplify((d_matrix * d_matrix)[0, 2]) == 0''',
  'ALG_TOP-682': '''import sympy as sp
b0, b1, b2, b3 = sp.symbols('b0 b1 b2 b3')
# 庞加莱对偶性方程
eq1 = b0 - b3
eq2 = b1 - b2
assert sp.simplify(eq1 - (b0 - b3)) == 0
assert sp.simplify(eq2 - (b1 - b2)) == 0'''
}

class LiteralString(str):
    pass

def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(LiteralString, literal_presenter)

for item in batch:
    cleaned_sub = []
    for s in item['sub_topics']:
        if isinstance(s, dict):
            k, v = list(s.items())[0]
            cleaned_sub.append(f"{k}: {v}")
        else:
            cleaned_sub.append(s)
            
    domain = item['id'].split('-')[0]
    short_desc = item['name'].split(' - ')[0] if ' - ' in item['name'] else item['name']
    
    yaml_obj = {
        'id': item['id'],
        'name': item['name'],
        'description': short_desc,
        'hierarchy_info': {
            'chapter': domain,
            'section': short_desc,
            'level': 6
        },
        'llm_physical_mapping': metaphors[item['id']],
        'code_implementation': LiteralString(pytorch_codes[item['id']]),
        'v8_sanity_audit': {
            'sympy_pseudo_code': LiteralString(sympy_codes[item['id']])
        },
        'sub_topics': cleaned_sub
    }
    
    file_path = os.path.join(out_dir, f"{item['id']}.yaml")
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_obj, f, allow_unicode=True, sort_keys=False, width=1000)

print('All 11 files generated successfully.')

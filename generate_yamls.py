import json
import os

data = json.load(open('E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/temp_batches.json', encoding='utf-8'))
batch = data[0]

output_dir = 'E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/_Staging_Level5_Part1/'
os.makedirs(output_dir, exist_ok=True)

mappings = {
    'PDE-480': {
        'llm': '一滴墨水滴入静止的水池中，随着时间推移，墨水的高浓度区域逐渐向低浓度区域扩散，直至整个水池颜色均匀。墨水不可逆地消散对应热量/信息的熵增和平滑化过程。',
        'code': '''import torch

def heat_equation_sim(u, k=0.1, steps=100):
    for _ in range(steps):
        laplacian = (
            torch.roll(u, shifts=1, dims=0) + 
            torch.roll(u, shifts=-1, dims=0) + 
            torch.roll(u, shifts=1, dims=1) + 
            torch.roll(u, shifts=-1, dims=1) - 
            4 * u
        )
        u = u + k * laplacian
    return u
''',
        'sympy': '''import sympy as sp

x, t, k = sp.symbols('x t k', real=True, positive=True)
u = (1 / sp.sqrt(4 * sp.pi * k * t)) * sp.exp(-x**2 / (4 * k * t))
u_t = sp.diff(u, t)
u_xx = sp.diff(u, x, x)
diff = sp.simplify(u_t - k * u_xx)
assert diff == 0, 'Heat equation not satisfied by Gaussian kernel'
'''
    },
    'PDE-481': {
        'llm': '一根紧绷的吉他弦被拨动后，振动以有限的速度沿着弦向两端传播，形成可见的波峰和波谷。这种机械波的传播严格遵循因果律，波峰不会瞬间到达另一端。',
        'code': '''import torch

def wave_equation_sim(u, u_prev, c=0.1, steps=100):
    for _ in range(steps):
        laplacian = torch.roll(u, shifts=1) + torch.roll(u, shifts=-1) - 2 * u
        u_next = 2 * u - u_prev + (c**2) * laplacian
        u_prev, u = u, u_next
    return u
''',
        'sympy': '''import sympy as sp

x, t, c = sp.symbols('x t c', real=True)
f = sp.Function('f')
g = sp.Function('g')
u = f(x - c*t) + g(x + c*t)
u_tt = sp.diff(u, t, t)
u_xx = sp.diff(u, x, x)
eq = sp.simplify(u_tt - c**2 * u_xx)
assert eq == 0, 'Wave equation not satisfied by dAlembert solution'
'''
    },
    'PDE-482': {
        'llm': '一张边缘被分别加热到不同固定温度的金属薄板，经过漫长的时间后，板上各点的温度不再随时间变化，达到稳态的热平衡分布。此时每一点的温度恰好等于其周围邻居的平均温度。',
        'code': '''import torch

def laplace_equation_jacobi(u, steps=100):
    mask = torch.ones_like(u)
    mask[0, :] = 0; mask[-1, :] = 0; mask[:, 0] = 0; mask[:, -1] = 0
    for _ in range(steps):
        u_new = 0.25 * (
            torch.roll(u, shifts=1, dims=0) + 
            torch.roll(u, shifts=-1, dims=0) + 
            torch.roll(u, shifts=1, dims=1) + 
            torch.roll(u, shifts=-1, dims=1)
        )
        u = torch.where(mask == 1, u_new, u)
    return u
''',
        'sympy': '''import sympy as sp

x, y = sp.symbols('x y', real=True)
u = sp.log(x**2 + y**2)
u_xx = sp.diff(u, x, x)
u_yy = sp.diff(u, y, y)
laplacian = sp.simplify(u_xx + u_yy)
assert laplacian == 0, 'Laplace equation not satisfied by log(r)'
'''
    },
    'PDE-483': {
        'llm': '水流中漂浮着一片树叶。树叶顺着水流的流线（特征线）运动。在树叶的参考系下，周围的环境特征是不变的。特征线法正是将观察视角从固定的河岸（欧拉视角）切换到随着水流运动的树叶（拉格朗日视角）。',
        'code': '''import torch

def method_of_characteristics_sim(x, t, a=1.0):
    u_xt = torch.exp(-(x - a*t)**2)
    return u_xt
''',
        'sympy': '''import sympy as sp

x, t, a = sp.symbols('x t a', real=True)
f = sp.Function('f')
u = f(x - a*t)
u_t = sp.diff(u, t)
u_x = sp.diff(u, x)
pde_val = sp.simplify(u_t + a*u_x)
assert pde_val == 0, 'Method of characteristics failed for advection equation'
'''
    },
    'PDE-484': {
        'llm': '公路上的车流：如果后方车辆速度快，前方车辆速度慢，快速的车流最终会追上慢速车流，导致车间距瞬间缩短并引发拥堵（激波）。这里的特征线对应每辆车的轨迹，轨迹相交就意味着激波的产生。',
        'code': '''import torch

def burgers_equation_shock(u, dt=0.01, dx=0.1, steps=50):
    for _ in range(steps):
        u_x = (u - torch.roll(u, shifts=1)) / dx
        u = u - dt * u * u_x
    return u
''',
        'sympy': '''import sympy as sp

x, t = sp.symbols('x t', real=True)
u = x / (1 + t)
u_t = sp.diff(u, t)
u_x = sp.diff(u, x)
pde_val = sp.simplify(u_t + u*u_x)
assert pde_val == 0, 'Burgers equation specific solution failed'
'''
    },
    'PDE-485': {
        'llm': '一根两端固定的跳绳在甩动时，其整体形态可以看作是空间上的形状（半个波形）乘以时间上的周期性上下震荡。复杂的时空交织运动被剥离为一个独立的空间形态和一个独立的时间演化模式。',
        'code': '''import torch

def separation_of_variables(x, t, n=1, L=torch.pi):
    X = torch.sin(n * torch.pi * x / L)
    T = torch.exp(-(n * torch.pi / L)**2 * t)
    u = X * T
    return u
''',
        'sympy': '''import sympy as sp

x, t, k = sp.symbols('x t k', real=True)
X = sp.Function('X')(x)
T = sp.Function('T')(t)
u = X * T
u_t = sp.diff(u, t)
u_xx = sp.diff(u, x, x)
lhs = sp.simplify(u_t / (k * u))
rhs = sp.simplify(u_xx / u)
assert lhs == sp.diff(T, t) / (k * T)
assert rhs == sp.diff(X, x, x) / X
'''
    },
    'PDE-486': {
        'llm': '敲击一面鼓，鼓面的复杂震动可以分解为多个基本震动模式（本征态）的叠加。每个本征态都有特定的空间驻波形状。整个过程就是用一组正交的空间振动基底拼凑出任意的初始敲击状态。',
        'code': '''import torch

def fourier_series_reconstruction(x, coeffs):
    u = torch.zeros_like(x)
    for n, (a, b) in enumerate(coeffs, start=1):
        u += a * torch.cos(n * x) + b * torch.sin(n * x)
    return u
''',
        'sympy': '''import sympy as sp

x = sp.Symbol('x', real=True)
L = sp.Symbol('L', real=True, positive=True)
n_val, m_val = 1, 2
f1_spec = sp.sin(n_val * sp.pi * x / L)
f2_spec = sp.sin(m_val * sp.pi * x / L)
ortho_check = sp.simplify(sp.integrate(f1_spec * f2_spec, (x, 0, L)))
assert ortho_check == 0, 'Eigenfunctions are not orthogonal'
'''
    },
    'PDE-487': {
        'llm': '将一束复杂的复色光通过棱镜，光被分解为不同颜色的单色光谱。在光谱上对特定颜色加上滤光片，最后再用透镜组合起来，这比直接在复杂的原始光束中去修改特定频率的光波要简单得多。',
        'code': '''import torch

def fourier_transform_derivative(f_x, dx=0.1):
    F_k = torch.fft.fft(f_x)
    N = f_x.shape[0]
    freqs = torch.fft.fftfreq(N, d=dx)
    F_df = 1j * 2 * torch.pi * freqs * F_k
    df_x = torch.fft.ifft(F_df).real
    return df_x
''',
        'sympy': '''import sympy as sp

x, k = sp.symbols('x k', real=True)
f_spec = sp.exp(-x**2)
df = sp.diff(f_spec, x)
F_df = sp.fourier_transform(df, x, k)
F_f = sp.fourier_transform(f_spec, x, k)
check = sp.simplify(F_df - (2 * sp.I * sp.pi * k) * F_f)
assert check == 0, 'Derivative in spatial domain not equivalent to multiplication in frequency domain'
'''
    },
    'PDE-488': {
        'llm': '两把梳子的齿相互交叠（卷积）。在空间域里，这需要计算每一个齿与另一个齿的重叠度；但如果我们在频域观察梳子的频率，两者的组合效应只是各自频率特征的简单乘积，极大降低了计算复杂度。',
        'code': '''import torch

def fourier_convolution(f, g):
    F_f = torch.fft.fft(f)
    F_g = torch.fft.fft(g)
    F_conv = F_f * F_g
    conv = torch.fft.ifft(F_conv).real
    return conv
''',
        'sympy': '''import sympy as sp

x, k = sp.symbols('x k', real=True)
f1 = sp.exp(-x**2)
f2 = sp.exp(-x**2)
conv = sp.sqrt(sp.pi / 2) * sp.exp(-x**2 / 2)
F_conv = sp.fourier_transform(conv, x, k)
F1 = sp.fourier_transform(f1, x, k)
F2 = sp.fourier_transform(f2, x, k)
diff = sp.simplify(F_conv - F1 * F2)
assert diff == 0, 'Convolution theorem check failed'
'''
    },
    'PDE-489': {
        'llm': '用一个有一定宽度的放大镜（测试函数）去观察物体锋利的边缘（间断点）。虽然物体边缘在数学上不可导，但放大镜看到的图像是平滑可导的。弱导数就是把对物体的求导转移到对放大镜移动的求导上。',
        'code': '''import torch

def weak_derivative(u, phi):
    phi_prime = torch.roll(phi, shifts=-1) - phi
    integral_u_phi_prime = torch.sum(u * phi_prime)
    return -integral_u_phi_prime
''',
        'sympy': '''import sympy as sp

x = sp.Symbol('x', real=True)
u = sp.Abs(x)
u_prime_weak = sp.sign(x)
phi_spec = (1 - x**2)**2
lhs = sp.integrate(u * sp.diff(phi_spec, x), (x, -1, 1))
rhs = -sp.integrate(u_prime_weak * phi_spec, (x, -1, 1))
assert sp.simplify(lhs - rhs) == 0, 'Weak derivative definition failed'
'''
    }
}

for node in batch:
    nid = node['id']
    content = f"""id: "{node['id']}"
name: "{node['name']}"
sub_topics:
"""
    for st in node['sub_topics']:
        content += f'  - "{st}"\n'
    
    content += f'llm_physical_mapping: "{mappings[nid]["llm"]}"\n'
    content += 'code_implementation: |\n'
    for line in mappings[nid]['code'].splitlines():
        if line:
            content += f'  {line}\n'
        else:
            content += '\n'
    content += 'v8_sanity_audit:\n'
    content += '  sympy_pseudo_code: |\n'
    for line in mappings[nid]['sympy'].splitlines():
        if line:
            content += f'    {line}\n'
        else:
            content += '\n'
    
    with open(os.path.join(output_dir, f'{nid}.yaml'), 'w', encoding='utf-8') as f:
        f.write(content)

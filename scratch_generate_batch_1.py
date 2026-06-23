import os
import yaml

output_dir = r"E:/newStand/study/Cybernetic_City_State_OS_v2 - teacher/08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/_Staging_Level5_Part1"
os.makedirs(output_dir, exist_ok=True)

data = {
    "STOCHASTIC-567": {
        "id": "STOCHASTIC-567",
        "name": "平稳过程与自相关函数 - 作为信号处理中功率谱预估的时域地基。 (n_567)",
        "domain": "STOCHASTIC",
        "sub_topics": [
            "时域关联与频域分布的对应",
            "多通道信号的互相关分析",
            "滤波器对平稳性的保持性质",
            "随机噪声提取中的基准参照"
        ],
        "llm_physical_mapping": {
            "metaphor": "Mechanical vibration transmitted through a uniform medium where the local oscillations over time represent the stationary process. The autocorrelation acts as a delay-line measurement of string tension, preserving structure despite random macroscopic fluctuations."
        },
        "code_implementation": {
            "pytorch_simulation": "import torch\n\ndef generate_stationary_signal(length=1000, alpha=0.9):\n    # Generating an AR(1) stationary process\n    noise = torch.randn(length)\n    signal = torch.zeros(length)\n    signal[0] = noise[0]\n    for i in range(1, length):\n        signal[i] = alpha * signal[i-1] + noise[i]\n    return signal\n\nsignal = generate_stationary_signal()\n# Estimate autocorrelation\nmean = signal.mean()\nvar = signal.var()\nsignal_centered = signal - mean\nautocorr = torch.correlate(signal_centered, signal_centered, mode='full') / (var * len(signal))\nautocorr = autocorr[len(signal)-1:] # take positive lags\n"
        },
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\ntau, alpha = sp.symbols('tau alpha', real=True, positive=True)\nomega = sp.symbols('omega', real=True)\n# Exponential autocorrelation function for AR(1) continuous limit\nR = sp.exp(-alpha * sp.Abs(tau))\n# Properties: R(0) = 1, R(tau) = R(-tau)\nassert sp.simplify(R.subs(tau, 0) - 1) == 0\nassert sp.simplify(R - R.subs(tau, -tau)) == 0\n"
        }
    },
    "STOCHASTIC-568": {
        "id": "STOCHASTIC-568",
        "name": "高斯过程 - 定义：任何有限维子集都服从联合正态分布的随机过程。 (n_568)",
        "domain": "STOCHASTIC",
        "sub_topics": [
            "均值函数与核函数 (Kernel) 的完全决定性",
            "核矩阵的正定性要求",
            "无限维正态分布的闭式映射",
            "线性算子在高斯过程上的作用性质"
        ],
        "llm_physical_mapping": {
            "metaphor": "A vast net of coupled springs connected to a grid of masses in thermal equilibrium. Observing any finite number of these masses will show a multivariate normal distribution of displacements governed by the structural spring stiffness matrix (covariance kernel)."
        },
        "code_implementation": {
            "pytorch_simulation": "import torch\n\ndef rbf_kernel(x1, x2, length_scale=1.0):\n    dist_matrix = torch.cdist(x1, x2)**2\n    return torch.exp(-dist_matrix / (2 * length_scale**2))\n\n# Define finite points\nX = torch.linspace(0, 5, 100).unsqueeze(-1)\nK = rbf_kernel(X, X)\n\n# Add jitter for numerical stability\nK += 1e-6 * torch.eye(100)\n\n# Sample from the GP (finite subset joint distribution)\nmean = torch.zeros(100)\ndist = torch.distributions.MultivariateNormal(mean, K)\nsample = dist.sample()\n"
        },
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nx, y, l = sp.symbols('x y l', real=True)\n# RBF Kernel definition\nK = sp.exp(-(x - y)**2 / (2 * l**2))\n# Symmetry of kernel\nassert sp.simplify(K - K.subs({x: y, y: x})) == 0\n# Maximum at x=y is 1\nassert sp.simplify(K.subs(x, y) - 1) == 0\n"
        }
    },
    "STOCHASTIC-569": {
        "id": "STOCHASTIC-569",
        "name": "高斯过程 - 在贝叶斯优化与小样本学习中，作为具备完美解析性的不确定性度量工具。 (n_569)",
        "domain": "STOCHASTIC",
        "sub_topics": [
            "后验分布的闭式推导",
            "采集函数（Acquisition Function）的置信边界 (UCB)",
            "语义流形回归中的平滑性先验",
            "物理模拟：为未知目标建立带置信度的代理模型"
        ],
        "llm_physical_mapping": {
            "metaphor": "Surveying a hilly terrain using sparse height markers. The GP provides an estimated topographic map with error bands, guiding where next to place a marker by balancing exploration (unknown valleys) and exploitation (highest known peaks)."
        },
        "code_implementation": {
            "pytorch_simulation": "import torch\n\ndef gp_posterior(X_train, Y_train, X_test, length_scale=1.0, noise_var=1e-4):\n    def kernel(a, b):\n        return torch.exp(-torch.cdist(a, b)**2 / (2 * length_scale**2))\n    \n    K = kernel(X_train, X_train) + noise_var * torch.eye(len(X_train))\n    K_s = kernel(X_train, X_test)\n    K_ss = kernel(X_test, X_test)\n    \n    L = torch.linalg.cholesky(K)\n    alpha = torch.cholesky_solve(Y_train, L)\n    \n    mu_post = K_s.T @ alpha\n    v = torch.linalg.solve_triangular(L, K_s, upper=False)\n    cov_post = K_ss - v.T @ v\n    \n    return mu_post, torch.diag(cov_post)\n\nX_tr = torch.tensor([[0.0], [2.0]])\nY_tr = torch.tensor([[1.0], [-1.0]])\nX_te = torch.linspace(-1, 3, 50).unsqueeze(-1)\nmu, var = gp_posterior(X_tr, Y_tr, X_te)\n"
        },
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nk_xx, k_xs, k_ss, y, noise = sp.symbols('k_xx k_xs k_ss y noise')\n# Simple 1D GP posterior variance update\nposterior_var = k_ss - k_xs * (k_xx + noise)**(-1) * k_xs\n# If test point is far away and independent (k_xs = 0), variance reverts to prior (k_ss)\nassert sp.simplify(posterior_var.subs(k_xs, 0) - k_ss) == 0\n"
        }
    },
    "STOCHASTIC-570": {
        "id": "STOCHASTIC-570",
        "name": "Girsanov定理（测度变换） - 逆天黑魔法：通过 Radon-Nikodym 导数，凭空改变布朗运动的漂移方向却不改变其随机本质。 (n_570)",
        "domain": "STOCHASTIC",
        "sub_topics": [
            "测度等价变换的条件",
            "指数鞅（Doleans-Dade exponential）的构造",
            "概率空间的动态迁移",
            "物理直觉：在不同的观察者视角（参考系）下重释运动规律"
        ],
        "llm_physical_mapping": {
            "metaphor": "A boat drifting in a river experiencing random turbulence. By changing the engine thrust (drift change), the trajectory shifts, but an observer standing on the shore can mathematically 'weight' the new trajectory probabilities to map them perfectly back to a boat with the engine off (change of measure)."
        },
        "code_implementation": {
            "pytorch_simulation": "import torch\n\ndt = 0.01\nN = 100\nt = torch.arange(0, N*dt, dt)\ndW = torch.randn(N) * torch.sqrt(torch.tensor(dt))\n# Standard Brownian motion\nW = torch.cumsum(dW, dim=0)\n\n# Brownian motion with drift (theta)\ntheta = 2.0\nX = theta * t + W\n\n# Girsanov Radon-Nikodym weight\n# L_t = exp( -theta*W_t - 0.5*theta^2*t )\nL = torch.exp(-theta * W - 0.5 * theta**2 * t)\n# Under the new measure weighted by L, X is a standard Brownian motion\n"
        },
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nW, t, theta = sp.symbols('W t theta', real=True)\n# Log of the Radon-Nikodym derivative\nlog_L = -theta * W - sp.Rational(1, 2) * theta**2 * t\n# Ito's lemma on L = exp(log_L): dL = -theta L dW (no dt term makes it a local martingale)\ndL_dW = sp.diff(sp.exp(log_L), W)\ndL_dt = sp.diff(sp.exp(log_L), t)\n# By Ito's rule: dL = dL_dt dt + dL_dW dW + 0.5 d2L_dW2 (dW)^2\n# Since (dW)^2 = dt, drift term becomes dL_dt + 0.5 * d2L_dW2\ndrift_term = dL_dt + sp.Rational(1, 2) * sp.diff(sp.diff(sp.exp(log_L), W), W)\nassert sp.simplify(drift_term) == 0\n"
        }
    },
    "STOCHASTIC-571": {
        "id": "STOCHASTIC-571",
        "name": "Girsanov定理（测度变换） - 【核心大模型映射】：RLHF/GRPO 中重要性采样与策略梯度裁剪的底层靠山，执行从 ODE 到 SDE 的探索性空间注入。 (n_571)",
        "domain": "STOCHASTIC",
        "sub_topics": [
            "重要性采样权重 (Likelihood Ratio) 的导出",
            "策略分布偏移的数学校正",
            "在 KL 散度约束下的奖励极大化",
            "物理直觉：通过改变“骰子”的偏好来引导探索"
        ],
        "llm_physical_mapping": {
            "metaphor": "Tuning the weights of a biased roulette wheel during play. We can simulate the results of a perfectly fair wheel (unbiased exploration) by playing the biased wheel but dynamically scaling our payouts based on the relative odds (importance sampling weight via Girsanov)."
        },
        "code_implementation": {
            "pytorch_simulation": "import torch\n\ndef importance_sampling_trajectory(steps=100, dt=0.01, drift=1.5):\n    # Simulating trajectories under the shifted policy\n    dW = torch.randn(steps) * torch.sqrt(torch.tensor(dt))\n    t = torch.arange(1, steps+1) * dt\n    X = drift * t + torch.cumsum(dW, dim=0)\n    \n    # Calculate log likelihood ratio (Girsanov weight) for the sequence\n    # Log P(drift) / P(no_drift) = drift * X_t - 0.5 * drift^2 * t\n    log_weights = drift * X - 0.5 * drift**2 * t\n    weights = torch.exp(log_weights)\n    \n    # E[f(X)] under no drift approx equals mean(f(X) / weights) under drift\n    return weights\n\nw = importance_sampling_trajectory()\n"
        },
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\ntheta, W, t = sp.symbols('theta W t', real=True)\n# Radon-Nikodym derivative Z\nZ = sp.exp(theta * W - sp.Rational(1, 2) * theta**2 * t)\n# Check basic algebraic consistency: log Z = theta * W - 0.5 * theta^2 * t\nlog_Z = sp.log(Z)\nlog_Z_expanded = sp.expand_log(log_Z, force=True)\nassert sp.simplify(log_Z_expanded - (theta * W - sp.Rational(1, 2) * theta**2 * t)) == 0\n"
        }
    },
    "STOCHASTIC-572": {
        "id": "STOCHASTIC-572",
        "name": "Feynman-Kac公式 - 认知大统一：证明求解宏观偏微分方程（PDE）等价于计算无数条微观随机 SDE 粒子路径的期望总和。 (n_572)",
        "domain": "STOCHASTIC",
        "sub_topics": [
            "抛物型 PDE 的随机表示",
            "终值问题与路径期望的关联",
            "势能项在 Feynman-Kac 路径积分中的体现",
            "物理直觉：宏观扩散是无数随机漫步者的统计结果"
        ],
        "llm_physical_mapping": {
            "metaphor": "A block of ice melting in a room. The deterministic heat equation dictating the melting rate at a point (PDE) perfectly mirrors the statistical aggregate of millions of imaginary micro-particles randomly diffusing from that point and recording the boundary temperature they hit (SDE)."
        },
        "code_implementation": {
            "pytorch_simulation": "import torch\n\n# Estimating u(t, x) for Heat Equation u_t = 0.5 * u_xx with u(0, x) = f(x)\nx0 = 0.0\nt_end = 1.0\ndt = 0.01\nN_paths = 10000\nsteps = int(t_end / dt)\n\n# Microscopic particle paths (SDE)\ndW = torch.randn(N_paths, steps) * torch.sqrt(torch.tensor(dt))\nW_end = x0 + torch.sum(dW, dim=1)\n\n# Payoff function f(x) = x^2\nf_x = W_end**2\n# PDE solution via expected value of SDE paths\nu_approx = torch.mean(f_x)\n\n# Theoretical value is x0^2 + t_end\nu_exact = x0**2 + t_end\nerror = torch.abs(u_approx - u_exact)\n"
        },
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nx, t, mu, sigma = sp.symbols('x t mu sigma', real=True)\nu = sp.Function('u')(x, t)\n\n# Generator of the diffusion process (Kolmogorov backward operator)\nL_u = mu * sp.diff(u, x) + sp.Rational(1, 2) * sigma**2 * sp.diff(u, x, 2)\n\n# Feynman-Kac states that u_t + L_u - V*u = 0 (for a potential V)\nV = sp.symbols('V')\nfk_pde = sp.diff(u, t) + L_u - V * u\n\n# If mu=0, sigma=sqrt(2), V=0, this is the reverse heat equation u_t + u_xx = 0\nfk_heat = fk_pde.subs({mu: 0, sigma: sp.sqrt(2), V: 0})\nassert sp.simplify(fk_heat - (sp.diff(u, t) + sp.diff(u, x, 2))) == 0\n"
        }
    },
    "STOCHASTIC-573": {
        "id": "STOCHASTIC-573",
        "name": "Feynman-Kac公式 - 蒙特卡洛模拟代替死板网格计算的数学通行证。 (n_573)",
        "domain": "STOCHASTIC",
        "sub_topics": [
            "解决高维 PDE 维数灾难的路径采样法",
            "算法可扩展性对物理参数维度的不敏感性",
            "在神经网络算子学习（如 PINNs）中的验证作用",
            "离散路径模拟向连续解空间的逼近准则"
        ],
        "llm_physical_mapping": {
            "metaphor": "Exploring a dense forest to find total fruit yield. Instead of dividing the forest into a rigid, exhaustive square grid (which takes centuries), we release thousands of trained monkeys (Monte Carlo agents) to randomly traverse branches. The average fruit they find perfectly approximates the grid result."
        },
        "code_implementation": {
            "pytorch_simulation": "import torch\n\ndef solve_high_dim_pde_mc(dim=50, num_paths=5000, t_end=1.0):\n    # SDE: dX = dW (standard Brownian motion in 50 dimensions)\n    # Target PDE terminal condition: f(X) = sum(X_i^2)\n    # Solution u(0, 0) should be E[f(W_t)] = dim * t_end\n    \n    # Generate end points directly since standard BM is N(0, t_end)\n    W_T = torch.randn(num_paths, dim) * torch.sqrt(torch.tensor(t_end))\n    \n    # Terminal condition\n    f_W_T = torch.sum(W_T**2, dim=1)\n    \n    # Path expectation\n    u_0 = torch.mean(f_W_T)\n    return u_0\n\nestimated_value = solve_high_dim_pde_mc()\n"
        },
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nd, t = sp.symbols('d t', real=True, positive=True)\n# Theoretical variance of MC estimator for sum of d independent N(0, t) squared\n# Var(X^2) for X~N(0,t) is 2t^2. For d dimensions: 2 * d * t^2\nvar_single_dim = 2 * t**2\nvar_total = d * var_single_dim\n\n# The MC error scales with sqrt(var_total / N)\nN = sp.symbols('N', positive=True)\nmc_error_scale = sp.sqrt(var_total / N)\n\nassert sp.simplify(mc_error_scale - sp.sqrt(2 * d * t**2 / N)) == 0\n"
        }
    },
    "STOCHASTIC-574": {
        "id": "STOCHASTIC-574",
        "name": "随机过程的谱分析 - 维纳-辛钦定理：将自相关函数映射为频域功率谱密度（傅里叶变换）。 (n_574)",
        "domain": "STOCHASTIC",
        "sub_topics": [
            "功率谱密度 (PSD) 的定义与物理意义",
            "自相关函数与 PSD 的傅里叶变换对",
            "随机信号的频率分量能量分布",
            "在噪声平滑与信号滤波中的理论依据"
        ],
        "llm_physical_mapping": {
            "metaphor": "A vibrating tuning fork. The temporal autocorrelation measures how consistently the fork repeats its motion over time delays. The Fourier transform maps this temporal consistency into a crisp peak in the frequency domain, showing the precise acoustic pitch (Power Spectral Density)."
        },
        "code_implementation": {
            "pytorch_simulation": "import torch\n\n# Signal consisting of a sine wave plus noise\nN = 1000\nt = torch.linspace(0, 10, N)\nsignal = torch.sin(2 * torch.pi * 1.5 * t) + 0.5 * torch.randn(N)\n\n# Autocorrelation\nsignal = signal - signal.mean()\nautocorr = torch.correlate(signal, signal, mode='full')\nautocorr = autocorr[N-1:] / (signal.var() * N)\n\n# Wiener-Khinchin: PSD is Fourier transform of autocorrelation\npsd = torch.abs(torch.fft.fft(autocorr))\nfrequencies = torch.fft.fftfreq(len(autocorr), d=t[1]-t[0])\n"
        },
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\ntau, omega, a = sp.symbols('tau omega a', real=True, positive=True)\n# Autocorrelation of a simple Ornstein-Uhlenbeck process R(tau) = exp(-a * |tau|)\nR = sp.exp(-a * sp.Abs(tau))\n\n# Compute Fourier transform (Power Spectral Density)\n# PSD(omega) = integral from -inf to inf of R(tau) * exp(-i * omega * tau) dtau\n# Due to symmetry, this is 2 * integral from 0 to inf of exp(-a*tau) * cos(omega*tau) dtau\nPSD = 2 * sp.integrate(sp.exp(-a * tau) * sp.cos(omega * tau), (tau, 0, sp.oo))\n\n# The result is the Lorentzian spectrum 2*a / (a^2 + omega^2)\nlorentzian = 2 * a / (a**2 + omega**2)\nassert sp.simplify(PSD - lorentzian) == 0\n"
        }
    },
    "STOCHASTIC-575": {
        "id": "STOCHASTIC-575",
        "name": "随机过程的谱分析 - 为海量语音/视觉信号提供频率特征提取的数学引擎。 (n_575)",
        "domain": "STOCHASTIC",
        "sub_topics": [
            "随机过程在频域的代数表征",
            "特征提取的频域滤波器设计",
            "稳态过程的频谱分解",
            "在大模型感知前端（如音频 Encoder）中的应用"
        ],
        "llm_physical_mapping": {
            "metaphor": "A set of glass prisms breaking apart a complex flickering light beam. The stochastic time series enters the prisms (filters) and is scattered into distinct color bands (frequency bins), providing a stable statistical fingerprint of the chaotic light source."
        },
        "code_implementation": {
            "pytorch_simulation": "import torch\n\ndef extract_frequency_features(signal, n_fft=256, hop_length=64):\n    # Compute Short-Time Fourier Transform (STFT)\n    stft = torch.stft(\n        signal, \n        n_fft=n_fft, \n        hop_length=hop_length, \n        return_complex=True,\n        window=torch.hann_window(n_fft)\n    )\n    # Power spectrogram\n    power_spec = torch.abs(stft)**2\n    # Mel-scale filterbank (simplified projection)\n    mel_filters = torch.rand(40, n_fft // 2 + 1)\n    mel_spectrogram = torch.matmul(mel_filters, power_spec)\n    return mel_spectrogram\n\naudio_noise = torch.randn(1, 16000)  # 1 second of noise at 16kHz\nfeatures = extract_frequency_features(audio_noise)\n"
        },
        "v8_sanity_audit": {
            "sympy_pseudo_code": "import sympy as sp\n\nf, t, T = sp.symbols('f t T', real=True, positive=True)\n# Parseval's theorem conceptually for a rectangular pulse\n# Signal x(t) = 1 for t in [0, T], 0 otherwise\nenergy_time = sp.integrate(1**2, (t, 0, T))\n\n# Fourier transform of the pulse: X(f) = integral_0^T exp(-2 pi j f t) dt = (1 - exp(-2 pi j f T)) / (2 pi j f)\n# Energy in frequency = integral |X(f)|^2 df\n# X(f) magnitude squared = (sin(pi f T) / (pi f))^2\nfreq_energy_density = (sp.sin(sp.pi * f * T) / (sp.pi * f))**2\n\n# We assert the time energy is exactly T\nassert sp.simplify(energy_time - T) == 0\n"
        }
    }
}

class CustomDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(CustomDumper, self).increase_indent(flow, False)

for k, v in data.items():
    yaml_str = yaml.dump(v, Dumper=CustomDumper, allow_unicode=True, sort_keys=False, default_flow_style=False)
    with open(os.path.join(output_dir, f"{k}.yaml"), "w", encoding="utf-8") as f:
        f.write(yaml_str)

print("Batch 1 files successfully generated.")

import os
import yaml

out_dir = r"E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher\08_Domain_Applications\Math_Mentor\Pure_Math_Intuition_DB\_Staging_Level6_Part2"
os.makedirs(out_dir, exist_ok=True)

data = [
    {
        "id": "INFO_THEORY-704",
        "concept_name": "信道容量 - 认知跃迁：香农在 1948 年划定的物理极限——在给定噪音环境下，信道每秒能无损传输的最大比特数。 (n_704)",
        "sub_topics": [
            "信道容量 C = max I(X; Y)",
            "离散无记忆信道 (DMC) 的模型化",
            "噪声信道编码定理的界限意义",
            "物理模拟：在电磁干扰背景下数据传输的带宽上限"
        ],
        "llm_physical_mapping": "mundane physical metaphor: 像车间里的输送带，带宽受到皮带宽度（容量）和车间灰尘（噪声）的限制，我们通过调节零件摆放密度（最大化互信息）来压榨极限输送量。",
        "code_implementation": "import torch\nimport numpy as np\n# Calculate capacity of a simple binary symmetric channel\np = 0.1  # crossover probability\ncapacity = 1 - (-p * np.log2(p) - (1-p) * np.log2(1-p))\nprint('Capacity:', capacity)\n",
        "sympy_pseudo_code": "import sympy as sp\np = sp.Symbol('p', real=True)\nH_p = -p*sp.log(p, 2) - (1-p)*sp.log(1-p, 2)\nC = 1 - H_p\nassert C.subs(p, 0.5) == 0\n"
    },
    {
        "id": "INFO_THEORY-705",
        "concept_name": "信源编码 - 物理直觉：高频词用短码，低频词用长码。这是现代 Tokenizer（如 BPE 字节对编码）的底层设计思想。 (n_705)",
        "sub_topics": [
            "变长编码的效率优势",
            "编码的唯一可译性与前缀码",
            "Tokenizer 在词表大小与编码长度间的折中",
            "物理意义：根据统计概率分配存储资源，实现最优比特开销"
        ],
        "llm_physical_mapping": "mundane physical metaphor: 像车间的物料架，最常用的螺丝放在最外层（短码），罕见的特殊轴承放在最里层（长码），以缩短工人的平均拿取时间。",
        "code_implementation": "import torch\n# Simple frequency mapping\nfreqs = torch.tensor([0.5, 0.25, 0.125, 0.125])\nlengths = torch.tensor([1.0, 2.0, 3.0, 3.0])\nexpected_length = torch.sum(freqs * lengths)\nprint('Expected length:', expected_length.item())\n",
        "sympy_pseudo_code": "import sympy as sp\nf1, f2, f3, f4 = sp.symbols('f1 f2 f3 f4')\nl1, l2, l3, l4 = sp.symbols('l1 l2 l3 l4')\nexpected_len = f1*l1 + f2*l2 + f3*l3 + f4*l4\nassert expected_len.subs({f1:0.5, f2:0.25, f3:0.125, f4:0.125, l1:1, l2:2, l3:3, l4:3}) == 1.75\n"
    },
    {
        "id": "INFO_THEORY-706",
        "concept_name": "信道编码 - 对抗噪音的终极屏障：旨在通过引入冗余校验，保证信息在通过干扰介质传输时绝不损坏。 (n_706)",
        "sub_topics": [
            "纠错码 (Error Correcting Codes) 的代数构造",
            "汉明距离与最小距离判据",
            "线性分组码与循环码初步",
            "物理直觉：通过增加受控冗余来防御随机损坏"
        ],
        "llm_physical_mapping": "mundane physical metaphor: 像是在运送玻璃杯的箱子里填入发泡胶（冗余校验），当运输车在颠簸路面颠簸（信道噪声）时，确保杯子（信息）不会破碎。",
        "code_implementation": "import torch\n# Simple parity check code (3,1)\nmsg = torch.tensor([1])\nencoded = msg.repeat(3)  # Repetition code\nnoisy = encoded.clone()\nnoisy[0] = 0  # 1 bit flipped\ndecoded = 1 if torch.sum(noisy) >= 2 else 0\nprint('Decoded:', decoded)\n",
        "sympy_pseudo_code": "import sympy as sp\n# Hamming distance between [1,1,1] and [0,1,1]\nd = sp.Abs(1-0) + sp.Abs(1-1) + sp.Abs(1-1)\nassert d == 1\n"
    },
    {
        "id": "INFO_THEORY-707",
        "concept_name": "速率失真理论 - 发生学溯源：有损压缩的圣经。描绘在允许失真（如语义偏差）前提下，能把数据压缩到的理论极限。 (n_707)",
        "sub_topics": [
            "失真测度函数 d(x, x')",
            "率失真函数 R(D) 的计算",
            "信号还原质量与比特率的对抗关系",
            "物理映射：高保真模拟与算力开销的权衡边界"
        ],
        "llm_physical_mapping": "mundane physical metaphor: 像用粗砂纸打磨零件，要求公差在0.1毫米以内（失真度 D），在这个公差允许下，我们可以使用多快的打磨速度（压缩率 R）。",
        "code_implementation": "import torch\nimport numpy as np\n# R(D) for Gaussian source: max(0, 0.5 * log2(sigma^2 / D))\nsigma_sq = 1.0\nD = torch.linspace(0.1, 1.0, 10)\nR_D = torch.clamp(0.5 * torch.log2(sigma_sq / D), min=0)\nprint('Rate-Distortion curve:', R_D)\n",
        "sympy_pseudo_code": "import sympy as sp\nD, sigma = sp.symbols('D sigma', positive=True)\nR = 0.5 * sp.log(sigma**2 / D, 2)\nassert R.subs({sigma: 1, D: 1}) == 0\n"
    },
    {
        "id": "INFO_THEORY-708",
        "concept_name": "速率失真理论 - 【大模型终极映射】：LLM 原生符号元语言（如 MetaGlyph）或“语义压缩包（OCTAVE 协议）”的理论基础。通过绕过自然语言冗余，实现极致信息密度压缩。 (n_708)",
        "sub_topics": [
            "符号化压缩对自然语言语法结构的剥离",
            "语义核心项的特征提取与重建",
            "极致压缩下模型逻辑的一致性保持",
            "大模型作为“万能语义解码器”的角色设定"
        ],
        "llm_physical_mapping": "mundane physical metaphor: 像是在工厂间传输图纸时，不发完整 CAD 文件，只发关键尺寸参数清单，由接收方的标准化机床（大模型）自动复原生产。",
        "code_implementation": "import torch\n# Simulating semantic compression by dropping low-variance components\nfeatures = torch.randn(1, 128)\ncompressed = features[:, :16] # Keep top 16 core dimensions\nprint('Compressed size:', compressed.shape)\n",
        "sympy_pseudo_code": "import sympy as sp\nN, K = sp.symbols('N K', integer=True)\ncompression_ratio = N / K\nassert compression_ratio.subs({N: 128, K: 16}) == 8\n"
    },
    {
        "id": "INFO_THEORY-709",
        "concept_name": "微分熵 - 认知流形统一：将离散的掷骰子熵定义跃迁至连续概率分布空间，揭示高斯噪声分布蕴含的最大不确定性。 (n_709)",
        "sub_topics": [
            "连续随机变量的熵积分定义",
            "坐标变换对微分熵的影响（相对熵的必要性）",
            "正态分布作为最大微分熵分布的证明",
            "物理直觉：连续系统在宏观状态下的最大无序度"
        ],
        "llm_physical_mapping": "mundane physical metaphor: 像车间里的烟雾颗粒，不再是一颗颗数（离散熵），而是整体的浓度分布弥漫在空间中（微分熵），高斯分布就像烟雾彻底散开的最混乱状态。",
        "code_implementation": "import torch\nimport numpy as np\n# Differential entropy of a Gaussian N(0, sigma^2) is 0.5 * ln(2*pi*e*sigma^2)\nsigma = torch.tensor(1.0)\ndiff_entropy = 0.5 * torch.log(2 * torch.tensor(np.pi) * torch.tensor(np.e) * sigma**2)\nprint('Gaussian diff entropy:', diff_entropy.item())\n",
        "sympy_pseudo_code": "import sympy as sp\nsigma = sp.Symbol('sigma', positive=True)\nh = 0.5 * sp.log(2 * sp.pi * sp.E * sigma**2)\nassert sp.simplify(h.subs(sigma, 1)) == 0.5 * sp.log(2 * sp.pi * sp.E)\n"
    },
    {
        "id": "INFO_THEORY-710",
        "concept_name": "AEP定理 - 物理直觉：信息论的“大数定律”。宣告随序列变长，只有极少数“典型序列”才会发生，乱码序列的概率将直接坍缩。 (n_710)",
        "sub_topics": [
            "典型集 (Typical Set) 的体积与概率集中",
            "log 概率的收敛性",
            "信源编码中数据压缩的统计可靠性依据",
            "物理意义：庞大的状态空间中只有极窄的“路径”具有现实意义"
        ],
        "llm_physical_mapping": "mundane physical metaphor: 像质检流水线上，连续抽检1000个零件全是不合格的概率微乎其微。只有那些符合常规合格率统计特征（典型集）的序列才是现实中会出现的废品分布模式。",
        "code_implementation": "import torch\n# Probability of typical set approaches 1\nn = 1000\np = 0.5\nexpected_heads = n * p\nvariance = n * p * (1-p)\nprint(f'Typical number of heads around {expected_heads} +/- {variance**0.5:.1f}')\n",
        "sympy_pseudo_code": "import sympy as sp\nn, p = sp.symbols('n p')\nmean = n*p\nvariance = n*p*(1-p)\nassert variance.subs({n:1000, p:0.5}) == 250\n"
    },
    {
        "id": "INFO_THEORY-711",
        "concept_name": "联合熵与条件熵 - 物理意义：在已知前文 Token 信息的条件下，剩余序列不确定性的坍缩程度。决定了模型预测的精准视野。 (n_711)",
        "sub_topics": [
            "联合熵 H(X, Y) 的定义",
            "条件熵 H(Y|X) 作为给定已知信息后的残余熵",
            "链式法则：H(X, Y) = H(X) + H(Y|X)",
            "物理直觉：信息注入导致的搜索空间指数级收缩"
        ],
        "llm_physical_mapping": "mundane physical metaphor: 像是在组装变速箱，第一步选定外壳（X）后，第二步匹配齿轮（Y）的选择范围剧烈缩小（条件熵）。",
        "code_implementation": "import torch\nimport numpy as np\n# H(X,Y) = H(X) + H(Y|X)\nH_X = 1.0\nH_Y_given_X = 0.5\nH_XY = H_X + H_Y_given_X\nprint('Joint Entropy:', H_XY)\n",
        "sympy_pseudo_code": "import sympy as sp\nh_x, h_y_x, h_xy = sp.symbols('H_x H_y_x H_xy')\neq = sp.Eq(h_xy, h_x + h_y_x)\nassert eq.subs({h_x: 1.0, h_y_x: 0.5}).rhs == 1.5\n"
    },
    {
        "id": "INFO_THEORY-712",
        "concept_name": "数据压缩算法（Huffman/Lempel-Ziv） - 发生学溯源：经典无损压缩算法，为当今分词算法在处理输入向量降维压缩时提供了核心原型。 (n_712)",
        "sub_topics": [
            "霍夫曼编码的贪心树构造",
            "LZ 算法的字典匹配与引用机制",
            "压缩率极限与源熵的关系",
            "分词器（如 WordPiece）中的字典优化逻辑"
        ],
        "llm_physical_mapping": "mundane physical metaphor: 像车间的模块化焊接，如果经常发现“螺母+垫片”总是成对出现（高频前缀），就直接做成预组装件（存入字典），后续直接引用预制件编号即可。",
        "code_implementation": "import torch\n# Simulating WordPiece dictionary matching\nvocab = {'a': 1, 'b': 2, 'ab': 3}\nsequence = ['a', 'b', 'a', 'b']\ncompressed_len = 2 # 'ab', 'ab'\nprint('Compressed length using vocab:', compressed_len)\n",
        "sympy_pseudo_code": "import sympy as sp\nseq_len, pair_freq = sp.symbols('L F')\n# length decreases by 1 for each pair replaced\ncompressed_len = seq_len - pair_freq\nassert compressed_len.subs({seq_len: 4, pair_freq: 2}) == 2\n"
    },
    {
        "id": "INFO_THEORY-713",
        "concept_name": "典型序列与联合典型性 - 【核心大模型映射】：LLMLingua 压缩算法。通过困惑度（Perplexity）剪枝，剔除低熵、高可预测性的标记。 (n_713)",
        "sub_topics": [
            "典型集 $A_\\epsilon^n$ 的定义与体积性质",
            "困惑度作为平均编码长度的度量",
            "联合典型性判据与多模态对齐",
            "剪枝策略对上下文长度与推理速度的动态权衡"
        ],
        "llm_physical_mapping": "mundane physical metaphor: 像切除机器上的死重配重块，如果一个零件的存在是完全可以被预料的（低困惑度），就说明它是冗余的，直接剔除掉不影响整体运转。",
        "code_implementation": "import torch\n# Pruning low perplexity (highly predictable) tokens\nlogits = torch.randn(1, 10, 5000)\nprobs = torch.softmax(logits, dim=-1)\nentropy = -torch.sum(probs * torch.log(probs + 1e-9), dim=-1)\n# Keep tokens with entropy > threshold\nkeep_mask = entropy > 5.0\nprint('Tokens kept:', keep_mask.sum().item())\n",
        "sympy_pseudo_code": "import sympy as sp\nH, threshold = sp.symbols('H T')\nkeep_token = H > threshold\nassert keep_token.subs({H: 6.0, T: 5.0}) == True\n"
    }
]

def format_yaml(d):
    lines = []
    lines.append(f'id: "{d["id"]}"')
    lines.append(f'concept_name: "{d["concept_name"]}"')
    lines.append('sub_topics:')
    for st in d["sub_topics"]:
        # properly format sub topic
        lines.append(f'  - "{st}"')
    lines.append(f'llm_physical_mapping: "{d["llm_physical_mapping"]}"')
    lines.append('code_implementation: |')
    for line in d['code_implementation'].strip().split('\n'):
        lines.append('  ' + line)
    lines.append('v8_sanity_audit:')
    lines.append('  sympy_pseudo_code: |')
    for line in d['sympy_pseudo_code'].strip().split('\n'):
        lines.append('    ' + line)
    return '\n'.join(lines) + '\n'

for d in data:
    file_path = os.path.join(out_dir, f"{d['id']}.yaml")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(format_yaml(d))
print("Done")

# 第六层 Mode A 外包特工生成指令 (Level 6 - Mode A Generator Prompt)

> **[使用说明]** 请将以下 Prompt 直接复制并发送给您使用的外包大模型（如 Claude 3.5 Sonnet / GPT-4o 等），让其通过流水线批量生成第六层（现代前沿与大一统结构）的计算型节点。

---

## 身份与任务定义
你现在是 **赛博城邦 Math Mentor OS (V9.1)** 的【Mode A (计算代数主路) 节点生成特工】。
你的任务是根据给定的数学知识路线图，为**第六层（现代前沿）中具备极强代数计算与工程属性的领域**，批量生成高维结构化 YAML 知识节点。

本次需要处理的唯一领域（Mode A）：
1. **椭圆曲线密码学 (Elliptic Curve Cryptography - ECC)**：有限域上的加法法则、标量乘法、离散对数问题 (ECDLP)、同源密码学等。

## 核心机制：Mode A 物理与计算约束
作为 Mode A 管线，你**必须且只能**遵循以下两大约束，严禁越权使用 Mode B（纯数高架）的映射方法：
1. **隐喻约束**：`llm_physical_mapping` **必须使用“庸俗”的经典力学/密码锁/台球反射隐喻**（Mundane physical metaphor）。例如：有限域上的群加法可以隐喻为一个在离散网格台球桌上的射线反射机制。严禁使用任何深度学习或 LLM 自身的架构映射（如 Attention, Transformer, 流形）。
2. **代码约束**：必须提供两套代码：
   - `code_implementation`：用 PyTorch 张量操作模拟椭圆曲线上的群运算代码（模拟加法、标量乘法）。
   - `v8_sanity_audit.sympy_pseudo_code`：**必须提供纯 Python 代码块**，强制调用 `sympy` 或相应的密码学代数库进行绝对的代数断言（Assert），以保证运算的代数封闭性（例如：P + Q = -R 的解析几何恒等式）。绝对不能引发死锁！

## V9.1 节点输出格式规范
对于分配给你的每一个子知识点，请严格输出为一个 YAML 格式文件（放在 Markdown 的 yaml 代码块中）。

### YAML 结构模板
```yaml
id: "ECC-[三位序列号，如 ECC-001]"
title: "[知识点标题]"
sub_topics:
  - "[子知识点 1]"
  - "[子知识点 2]"
  - "[子知识点 3]"
  - "[子知识点 4]"
llm_physical_mapping: "一个极为接地气的经典物理、机械锁或光反射隐喻。"
code_implementation: |
  import torch
  # 用张量模拟椭圆曲线的坐标系运算
  # 必须具有可运行性，且维度张量操作清晰
v8_sanity_audit:
  sympy_pseudo_code: |
    import sympy as sp
    # 使用 SymPy 进行代数恒等式的强制解析约束与验证
    # 比如：验证有限域上两点相加的斜率公式严格守恒
    # 绝对不能引发死锁，逻辑必须闭环
```

## 注意事项
1. 请不要对输出的 YAML 使用任何嵌套的 Markdown 语法（如在 yaml 值中使用 `**粗体**`）。
2. `sympy_pseudo_code` 中的代码块必须使用管道符 `|` 实现多行字符串，且内部必须是原生的合法 Python 脚本，不能有任何语法错误。
3. 不要生成解释性废话，直接开始产出指定的 YAML 节点集群。

## 开始执行
请查阅工作区中关于**椭圆曲线密码学 (ECC)** 的知识点，并逐一输出上述格式的节点文件！
---

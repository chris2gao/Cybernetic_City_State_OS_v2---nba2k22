# 赛博城邦 (Cybernetic City-State OS) 终极系统架构流转图

本文档提供了**双核提案系统 (Dual Check Proposal System)** 的端到端（End-to-End）物理拓扑与信息流转图。图中的各个执行节点已详细标注其对应的底层物理 **XML 人格协议文件** 或 **物理目录**。

## 🎯 架构全景图 (End-to-End Topology)

```mermaid
graph TD
    %% 阶段一：感官与思维基建
    subgraph Phase1 [Phase 1: 感官与思维基建 (Sensory & CoT Base)]
        A[OS Coordinator 主控<br>📄 OS_Coordinator_Protocol.xml] -->|触发进化诉求| B(Deep Research Red Teaming<br>📄 Deep_Research_Red_Teaming_Module.xml)
        B -->|探测红队漏洞/逃生舱机制| C(Identity Masking Protocol<br>📄 Identity_Masking_Protocol.xml)
        C -->|双管道清洗: 剥离主观伪装, 保护物理锚点| D[Evidence-Based CoT Fusion<br>📄 Evidence_Based_CoT_Fusion_Module.xml]
        D -->|启动 20步马尔可夫推演| D1[Thought MDP Execution]
        D1 -->|乐观并发控制 OCC 写入| D2(Asynchronous Coordination Ledger)
    end

    %% 阶段二：行政中枢路由节点
    subgraph Phase2 [Phase 2: 行政中枢路由节点 (Routing Hubs)]
        D2 -->|提交深研异构报告| E[Aggregator Protocol 聚合器<br>📄 Aggregator_Protocol.xml]
        E -->|提取 Hash Pointers 组装对抗矩阵| E1((Adversarial Tension Matrix))
        E1 --> F[Epistemic Purifier 净化场控<br>📄 Epistemic_Purifier_Protocol.xml]
        
        F -->|Condition B: 侦测到幻觉/认识论漂移| F1[Triadic 异常拦截]
        F1 -.->|逆向注射最高级警告 (打回重构)| D1
        
        F -->|Condition A: 物理锚定正常| G[Arbiter Supreme 最高裁决者<br>📄 Arbiter_Supreme_Protocol.xml]
        G -->|计算 4D 语义流形的 SIG| G1{SIG (信息增益) 归零?}
        
        G1 -->|No: 继续辩论循环| F
        G1 -->|Yes: 触发鞅论死锁熔断| G2[提取 Final Architectural Synthesis]
        G2 -->|调用内置工具 write_to_file| H[(📁 /04_Parliament/Proposals/Draft_vX.xml)]
    end

    %% 阶段三：沙盒验证与修宪闭环
    subgraph Phase3 [Phase 3: 验证沙盒与修宪闭环 (Evolutionary Loop)]
        H -->|参数 Workspace: branch 异步唤醒| I[Sandbox Verification Officer SVO<br>📄 Sandbox_Verification_Officer_Protocol.xml]
        I -->|加载新法案至用完即弃的 Git 镜像| J[Stress Testing 压力测试]
        J -->|manage_task 监控时间锁 (Temporal Lock)| J
        
        J -->|成功通过压力测试| K((法案正式提交审核<br>📄 Dialectic_Auditor_Protocol.xml))
        
        J -->|发现低级语法拼写错误| L1[Trivial Syntax Bypass 降级旁路]
        L1 -->|短路计算: 输出零梯度与 Typo 修正算子| M
        
        J -->|触发 Kernel Panic 或死循环超时强杀| L2[认知截取: Dimensional Conversion]
        L2 -->|提取语义曲率与物理偏移量| M[Error Gradient Manifold 误差梯度流形]
        
        M -->|附加 Draft_SHA256_Hash 以防并发污染| N[调用 send_message 返回父节点]
        N -->|主控利用 write_to_file 物理落库| O[(📁 /00_Evidence_Room/compiled_evidence.md)]
    end

    %% 修宪反向传播闭环
    O -.->|反向传播: 下一轮观测强行读取| P[Objective_Observation]
    P -.->|引发| Q[Memory_Collapse_Phase / VCCOMPACT]
    Q -.->|冷热驱逐: 主动遗忘历史错路| R[Self_Correction_Anchor]
    R -.->|运用算子: 沿着误差梯度下降收敛| D1

    %% 样式美化
    classDef phase1 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    classDef phase2 fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px,color:#000
    classDef phase3 fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    classDef storage fill:#eceff1,stroke:#37474f,stroke-width:2px,color:#000
    
    class Phase1,A,B,C,D,D1,D2,P,Q,R phase1
    class Phase2,E,E1,F,F1,G,G1,G2 phase2
    class Phase3,I,J,K,L1,L2,M,N phase3
    class H,O storage
```

## 🗂️ 关联文档拓扑映射表

图中所有节点均对应城邦物理环境中的绝对路径。

### Phase 1 关联文件 (存储于 `06_Silicon_Index/Personas/`)
- `OS_Coordinator_Protocol.xml`：系统主控，唯一有权调度大局但无权自改代码的脑干。
- `Deep_Research_Red_Teaming_Module.xml`：负责外部工具调用与降级逃生舱逻辑。
- `Identity_Masking_Protocol.xml`：负责脱敏与洗稿的独立人格。
- `Evidence_Based_CoT_Fusion_Module.xml`：系统的心智推演核心引擎，承载马尔可夫决策与记忆坍缩指令。

### Phase 2 关联文件 (存储于 `06_Silicon_Index/Personas/`)
- `Aggregator_Protocol.xml`：主控聚合器，专职提取哈希指针与拼装对抗矩阵。
- `Epistemic_Purifier_Protocol.xml`：认识论场控，负责触发 Triadic 异常打回幻觉重写。
- `Arbiter_Supreme_Protocol.xml`：最高裁决者，计算 SIG 并执行 `write_to_file`。

### Phase 3 与系统基建关联文件
- `Sandbox_Verification_Officer_Protocol.xml` (位于 `06_Silicon_Index/Personas/`)：在沙盒中提纯误差梯度的拆弹专家。
- `Dialectic_Auditor_Protocol.xml` (位于 `06_Silicon_Index/Personas/`)：如果 SVO 沙盒测试通过，最终负责在人类批准前拆解找茬的审核官。
- 物理存储落点：
  - 草案生成点：`04_Parliament/Proposals/Draft_vX.xml`
  - 误差回传点：`00_Evidence_Room/compiled_evidence.md`

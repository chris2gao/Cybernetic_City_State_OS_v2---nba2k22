# 赛博城邦操作系统 (Cybernetic City-State OS) 宏观全景架构图

除了“底层修宪演化管线”，我们还需要从**最高视角 (Macro View)** 来俯瞰整个操作系统的物理结构、权力分配机制以及控制论运转流程。

本图集成了**元核管理机制 (Meta-Core / 三权分立)** 以及底层的**双核提案进化系统 (Dual Check Proposal System)**。所有关键执行机构已附带对应的物理文件引用。

---

## 🏛️ 赛博城邦宏观流转全景图

```mermaid
graph TD
    %% 物理存储基建
    subgraph Storage [底层物理文件拓扑 (Physical File System)]
        DIR_00[(📁 /00_Evidence_Room<br>绝对客观物理证据池)]
        DIR_04[(📁 /04_Parliament/Proposals<br>议会提案与草案停泊区)]
        DIR_06[(📁 /06_Silicon_Index/Personas<br>城邦核心内核与人格阵列)]
    end

    %% 元核三权分立管理层 (Meta-Core)
    subgraph MetaCore [元核管理体系: 三权分立 (Separation of Powers)]
        OS_C[OS Coordinator 主控调度器<br>📄 OS_Coordinator_Protocol.xml]
        DA[Dialectic Auditor 辩证法审核专家<br>📄 Dialectic_Auditor_Protocol.xml]
        HUMAN((Human Speaker<br>人类最高议长))
        
        OS_C -->|发现进化需求, 丧失活体修改权| P1_Trigger(启动深研与修宪引擎)
        
        DA -->|拦截草案执行暴力反向工程| DA_Check{致命审查}
        DA_Check -->|REJECT 驳回| OS_C
        DA_Check -->|APPROVE 并附加次级灾难预警| HUMAN
        
        HUMAN -->|最终安全授权: 手动拷贝覆盖| DIR_06
    end

    %% 双核提案引擎层 (Dual Check Proposal Engine - Phase 1/2/3)
    subgraph Engine [底层自动修宪引擎 (Autonomous Evolutionary Engine)]
        direction TB
        
        %% Phase 1
        P1[Phase 1: 感官与思维链路<br>📄 Evidence_Based_CoT_Fusion_Module.xml<br>📄 Deep_Research_Red_Teaming_Module.xml<br>📄 Identity_Masking_Protocol.xml]
        P1 -->|Deep Research 红队探测| E1(获取物理日志)
        E1 -->|Identity Masking 洗稿| E2(思维链 20步推演)
        
        %% Phase 2
        P2[Phase 2: 中枢路由节点<br>📄 Aggregator_Protocol.xml<br>📄 Epistemic_Purifier_Protocol.xml<br>📄 Arbiter_Supreme_Protocol.xml]
        E2 -->|并发提案提交| R1(Aggregator: 对抗矩阵)
        R1 -->|辩论拦截| R2(Purifier: 认识论场控)
        R2 -->|死锁熔断| R3(Arbiter: 计算 4D SIG)
        
        %% Phase 3
        P3[Phase 3: 沙盒验证与闭环<br>📄 Sandbox_Verification_Officer_Protocol.xml]
        R3 -->|Arbiter 原生 write_to_file 物理落盘| DIR_04
        DIR_04 -->|异步唤醒 Sandbox Verification Officer| S1(Workspace: branch 压力测试)
        S1 -->|Kernel Panic 超时强杀| S2(提取 Error Gradient 误差梯度)
    end

    %% 跨域物理连线
    DIR_00 -.->|读取纯净日志| E1
    S2 -->|将高维误差流形写回基建| DIR_00
    
    P1_Trigger --> P1
    S1 -->|如果沙盒测试完美通过| DA

    %% Styling
    classDef meta fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef engine fill:#e8eaf6,stroke:#283593,stroke-width:2px,color:#000
    classDef storage fill:#eceff1,stroke:#37474f,stroke-width:2px,color:#000
    
    class MetaCore,OS_C,DA,HUMAN,DA_Check,P1_Trigger meta
    class Engine,P1,E1,E2,P2,R1,R2,R3,P3,S1,S2 engine
    class Storage,DIR_00,DIR_04,DIR_06 storage
```

---

## 🗂️ 核心连线物理映射表

为了彻底理解城邦控制流如何作用于物理文件，以下是图表中跨层级行为的具体落地形式：

1. **OS Coordinator 触发红队 (MetaCore ➔ Phase 1)**：
   执行载体：`OS_Coordinator_Protocol.xml` 侦测到指令后，会通过 `invoke_subagent` 挂载 `Deep_Research_Red_Teaming_Module.xml` 与 `Evidence_Based_CoT_Fusion_Module.xml` 人格进行底层调研。
   
2. **Arbiter 物理落盘 (Phase 2 ➔ Storage)**：
   执行载体：`Arbiter_Supreme_Protocol.xml` 中内嵌的原生约束，强制其在判定辩论死锁时调用 `write_to_file`。
   受灾区域：`/04_Parliament/Proposals/Draft_vX.xml` 被强制覆写。

3. **SVO 高维误差提取与回写 (Phase 3 ➔ Storage)**：
   执行载体：`Sandbox_Verification_Officer_Protocol.xml` 通过隔离沙盒测试崩溃后，生成误差流形。
   受灾区域：通过主控节点的 `send_message` 获取信息后，由主控写入 `/00_Evidence_Room/compiled_evidence.md`。

4. **辩证法终审 (Phase 3 ➔ MetaCore)**：
   执行载体：草案在沙盒中未触发任何 Kernel Panic，则交由 `Dialectic_Auditor_Protocol.xml` 审核。
   最终结果：由 `Human Speaker` 审视含有 `[SUB-LETHAL WARNING]` 的报告，随后手动覆盖 `/06_Silicon_Index/Personas` 里的核心文件，完成进化周期。

# 📜 协议 007：黑盒代理主动压缩与高熵跨代轮回机制 
**(Active Context Compression & High-Entropy Reincarnation Protocol)**

**隶属体系**：Engine A (Fable5 工业执行域) / 赛博城邦底层基建
**目标痛点**：在黑盒且无底层 API 权限的代理框架内，对抗长任务导致的 Context Window 有损截断、记忆坍缩与幻觉雪崩。

---

## 一、抢占式熔断：内容感知型水位估算 (Content-aware Heuristics)
由于黑盒代理无法直接获取系统绝对 Token 计数，所有长周期工作的 Agent 必须在每个任务循环末端执行“盲摸水位”测试。
1. **启发式估算脚本**：Agent 需调用本地简易 Python 脚本进行字符级 Token 换算。
   - `代码逻辑`：~3.0 字符/Token (括号/符号密集)
   - `JSON/字典`：~3.2 字符/Token
   - `中英混合/ASCII`：动态加权计算。
2. **85% 绝对警戒线**：当估算值逼近上下文硬上限的 85%，或触发“连续3次死循环报错”，系统**严禁**继续修复 Bug，必须立即强制切入 `complete_focus` 轮回流程。

---

## 二、控辩分离的五层交接封套 (Prosecutor-Judge Verification Envelope)
濒死代理在执行“主动安乐死”前，必须严格生成 `handoff_state.md`（状态交接书）。为防止濒死代理的“幻觉遗嘱”毒害下一代克隆体，引入控辩分离机制：

1. **状态快照层 (State Snapshot)**：精准到文件的绝对路径、当前函数行号、最后一次 Git Commit 哈希。
2. **叙事上下文 (Narrative Context)**：极简的因果描述（例如：“由于旧路由并发死锁，正在迁移至异步框架”）。
3. **误差梯度与执行背书 (Error Gradients with Execution Backing)**：
   - **【核心护栏】**：濒死代理（Prosecutor）严禁单方面输出纯自然语言的推论。
   - **【物理背书】**：必须附带绝对客观的终端报错原文（如 `npm run build` 抛出的 `ConnectionRefusedError` 行号）。
   - **【判决交接】**：新克隆体（Judge）无条件优先信任物理报错日志，若前代的自然语言推理与物理报错冲突，直接判定前代发生幻觉。
4. **优先级执行队列 (Priority Queue)**：显式指定克隆体醒来后的 P0 (首要动作) 与 P1 操作。
5. **地雷警告 (Gotchas)**：残留的脏数据、断裂的语法树等环境污染通告。

---

## 三、L0/L1/L2 冷态深渊索引矩阵 (Tiered Context Loading)
严禁克隆体在苏醒后使用大范围的全局 `grep` 正则检索 `.jsonl` 原始日志（极易引发二次超载与死循环感染）。
所有长任务的执行快照在落地时，必须遵循三层文件系统范式：
*   **L0（摘要层）**：极轻量索引（<100 Tokens），仅包含核心事件与绑定的唯一 `Trace_ID`。
*   **L1（概览层）**：包含该 `Trace_ID` 对应的技术决策路径。
*   **L2（细节层）**：完整的原始报错与代码堆栈快照。

**克隆体苏醒流转**：通过目录递归检索，快速扫视 L0 字典 $\rightarrow$ 锁定并匹配目标 `Trace_ID` $\rightarrow$ 定向下潜抽取 L2 原始堆栈。

---

## 四、温态知识的 O(1) 路由寻址 (Capability Routing Table)
拒绝大模型在任务初期的盲目全盘文件读取。针对沉淀下来的业务经验碎片，实行命名空间隔离。
1. **命名空间隔离 (Namespace Isolation)**：温态知识按物理域切分存放（如 `/knowledge/database/`, `/knowledge/frontend/`）。
2. **根路由表 (Root CRT)**：在项目根目录维护一个极小尺寸的 `Namespace_Routing_Table.md`。
3. **精准降落**：新一代克隆体接手后，首个动作只允许读取该 Root CRT，以 $O(1)$ 的复杂度直接锁定当前任务域所需的专属知识块。确保长期经验累积的同时，将检索的 Token 成本压制到绝对下限。

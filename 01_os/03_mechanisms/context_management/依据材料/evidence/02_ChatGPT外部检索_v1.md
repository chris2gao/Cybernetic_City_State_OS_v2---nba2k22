# ChatGPT 外部检索 v1

- workflow：`context-management-mechanism`
- 阶段：`02_信息收集与提炼`
- 检索日期：2026-07-29
- 执行者：ChatGPT web
- 路线性质：第一条外部检索路线；**不是完整的双模型覆盖测量**

## 1. 检索问题

本路线覆盖：

1. 无关或过长上下文是否会降低模型表现；
2. 现有 agent 框架如何持久化状态、恢复会话和过滤 handoff 上下文；
3. 多代理系统是否采用独立上下文窗口与压缩交接；
4. Git worktree 与 GitHub 仓库权限能否支撑默认任务/角色分区；
5. 状态与检查点长期累积有什么生命周期风险。

## 2. 检索路径

### 路径 A：官方实现文档，定向核实

限定检索：

- OpenAI Agents SDK：sessions、context、handoffs；
- LangGraph：persistence、checkpoints、threads；
- Microsoft AutoGen：memory、model context、agent runtime；
- Git 官方：git-worktree；
- GitHub 官方：repository roles 与 collaborator permissions。

### 路径 B：一手研究与官方工程经验

检索：

- 长上下文中相关信息位置变化；
- 无关上下文导致的 distractibility；
- 外部/分层记忆；
- Anthropic context engineering 与 multi-agent research system。

### 返回为空、受限或尚未覆盖

- 第一组针对 Anthropic engineering 的精确限定检索没有返回官方结果；更换检索路线后才找到官方工程文章。单次“没有”不能采信。
- 尚未完成当前 Windows 本机上目录 ACL、容器、沙箱和工具网关的实测；因此本路线不能裁决本地隔离技术选型。
- 尚未找到“固定单一角色入口文件”这一精确形态的独立效果研究；当前只能由 checkpoint、session 和结构化 state 模式间接支持。
- 尚无证据量化本项目采用最小上下文后能节省多少 token；只能确认长上下文和无关信息存在性能风险。
- GitHub 文档能回答仓库级权限能力，不能回答为每个任务、每个角色建立仓库的实际运营成本；需要运行试验。

## 3. 信源清单

| ID | 信源 | 类型 | 可靠性 | 本条信息可信度 | 检索限制 |
|---|---|---|---|---|---|
| S-01 | Anthropic, *Effective context engineering for AI agents* — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | 官方工程 | A | 4/5 | 厂商工程经验，不是独立对照实验 |
| S-02 | Anthropic, *How we built our multi-agent research system* — https://www.anthropic.com/engineering/multi-agent-research-system | 官方工程 | A | 4/5 | 描述 Anthropic 自身系统，外推需谨慎 |
| S-03 | Liu et al., *Lost in the Middle* — https://arxiv.org/abs/2307.03172 | 同行研究/论文 | A | 5/5 | 任务主要为多文档问答与检索，不是代码 agent |
| S-04 | Shi et al., *Large Language Models Can Be Easily Distracted by Irrelevant Context* — https://arxiv.org/abs/2302.00093 | 同行研究/论文 | A | 4/5 | 主要是算术推理场景，模型世代较早 |
| S-05 | Packer et al., *MemGPT: Towards LLMs as Operating Systems* — https://arxiv.org/abs/2310.08560 | 研究论文+开源实现 | A | 4/5 | 证明分层记忆可行，不证明适合本项目全部角色 |
| S-06 | OpenAI Agents SDK, Sessions — https://openai.github.io/openai-agents-python/sessions/ | 官方文档 | A | 5/5 | 证明功能存在，不证明跨厂商通用性 |
| S-07 | OpenAI Agents SDK, Handoffs — https://openai.github.io/openai-agents-python/handoffs/ | 官方文档 | A | 5/5 | 默认 handoff 会看到完整历史，必须显式过滤 |
| S-08 | OpenAI Agents SDK, Context management — https://openai.github.io/openai-agents-python/context/ | 官方文档 | A | 5/5 | 主要针对 SDK 运行时 |
| S-09 | LangGraph, Persistence — https://langchain-ai.github.io/langgraphjs/how-tos/subgraph-persistence/ | 官方文档 | A | 5/5 | 框架特定实现 |
| S-10 | LangGraph, Checkpointing — https://langchain-ai.github.io/langgraph/reference/checkpoints/ | 官方文档 | A | 5/5 | 框架特定实现 |
| S-11 | Microsoft AutoGen, Memory and RAG — https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html | 官方文档 | A | 5/5 | 记忆检索质量依赖存储与检索机制 |
| S-12 | Microsoft AutoGen, Agent Runtime — https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/agent-and-agent-runtime.html | 官方文档 | A | 4/5 | “security boundaries”是框架职责描述，具体强度需看实现 |
| S-13 | Git, git-worktree — https://git-scm.com/docs/git-worktree.html | 官方文档 | A | 5/5 | 只定义多个工作树，不提供权限隔离承诺 |
| S-14 | GitHub, Repository roles for an organization — https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/repository-roles-for-an-organization | 官方文档 | A | 5/5 | 组织仓库能力与计划相关；具体可用功能取决于账户形态 |
| S-15 | GitHub, Personal repository permission levels — https://docs.github.com/en/enterprise-cloud@latest/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository | 官方文档 | A | 5/5 | 个人私有仓库 collaborator 只有写权限，非只读 |

## 4. 证据条目

### EXT-001 · 无关与过长上下文会造成真实性能风险

- **结论**：支持。
- `Lost in the Middle` 发现，相关信息位于长上下文中部时，模型表现显著下降，即使模型标称支持长上下文。
- `Large Language Models Can Be Easily Distracted by Irrelevant Context` 发现，加入无关信息会显著降低推理准确率。
- Anthropic 的 context engineering 工程文章把 context rot、compaction、结构化笔记和多代理架构列为长周期 agent 的核心问题与缓解手段。
- **适用边界**：论文任务不完全等同于软件开发 agent；它们支持“少而相关的上下文更安全”，但不直接证明本项目的具体 token 节省量。
- **对 B 的影响**：结果方案必须有默认最小加载、显式引用与上下文裁剪；“把全部历史都放进窗口”不应成为候选基线。
- 来源：S-01、S-03、S-04。

### EXT-002 · 独立子代理上下文与压缩交接是生产系统采用的模式

- **结论**：支持。
- Anthropic 的多代理研究系统让 subagents 在各自上下文窗口中并行探索，再把重要信息压缩给 lead agent。
- **适用边界**：该系统面向研究任务，不等于本项目的规划/执行/审核角色；但证明“角色拥有独立上下文并通过压缩结果协作”不是纯理论设想。
- **对 B 的影响**：角色私有上下文 + 结构化发布产物应保留为核心候选。
- 来源：S-02。

### EXT-003 · handoff 可以携带结构化元数据并过滤接收方看到的历史

- **结论**：支持，但默认行为不满足本需求。
- OpenAI Agents SDK 的 handoff 支持 `input_type` 结构化输入与 `input_filter` 历史过滤。
- 官方文档同时说明：默认 handoff 会把此前完整对话历史交给接收代理；只有显式过滤才会改变。
- **对 B 的影响**：跨角色交接不能依赖框架默认；必须有明确交接 schema 与接收上下文过滤规则。
- 来源：S-07。

### EXT-004 · 跨会话持久化与恢复已有多种成熟实现模式

- **结论**：支持。
- OpenAI Sessions 可为一个 session ID 自动维护跨 run 的历史。
- LangGraph checkpointer 把线程状态保存为 checkpoint，支持中断恢复、人类介入和故障恢复；store 用于跨线程长期数据。
- AutoGen Memory 提供 `add/query/update_context`，可在步骤开始前只把检索到的相关记忆加入模型上下文。
- MemGPT 用分层记忆在有限窗口与外部存储之间移动信息，并在多会话聊天中验证长期记忆。
- **对 B 的影响**：耐久状态与模型窗口应分离；恢复入口可以引用持久化状态，而不必重放全部对话。
- 来源：S-05、S-06、S-09、S-10、S-11。

### EXT-005 · checkpoint 与 thread 提供版本化状态的现成语义

- **结论**：部分支持。
- LangGraph checkpoint 是某时刻的状态快照，具有 checkpoint ID、channel version 与 pending writes；thread ID 分隔不同运行序列。
- 这支持任务 ID、角色状态快照和恢复点的设计。
- **缺口**：官方机制不自动等于“上游 A/B 更新后，下游角色入口失效”；该依赖传播仍需本项目定义。
- **对 B 的影响**：可借鉴 thread/checkpoint/version 语义，但需要显式依赖边与失效规则。
- 来源：S-09、S-10。

### EXT-006 · Git worktree 是工作目录分离，不是权限边界

- **结论**：支持工作区分离；不支持把它称为安全隔离。
- Git 官方定义 worktree 为同一仓库关联的多个工作树，可同时检出不同分支。
- 官方文档没有提供文件访问权限或沙箱承诺。
- **推断**：worktree 适合作为任务/角色默认工作目录，但若要阻止 shell 读取其他路径，需要操作系统权限、容器或受限工具层补充。
- **对 B 的影响**：A 主要防无意污染，因此 worktree 仍可能是低成本主路径；方案必须诚实标注其边界。
- 来源：S-13。

### EXT-007 · GitHub 权限是仓库级，独立仓库能形成清晰角色边界

- **结论**：支持独立仓库方向，同时暴露账户限制。
- GitHub organization repository 可以为成员、团队或外部协作者分配 Read/Triage/Write/Maintain/Admin 等仓库级角色。
- 个人账户私有仓库的 collaborator 可读写，不能授予只读 collaborator。
- **对 B 的影响**：若需要只读 Web 角色交接空间，组织仓库更合适；每角色独立仓库能避免目录级权限不存在的问题，但实际创建、授权和清理成本仍需试验。
- 来源：S-14、S-15。

### EXT-008 · 长期状态必须有保留策略

- **结论**：支持。
- LangGraph 官方文档明确指出 checkpoints 会无限增长，建议定期裁剪或设置 retention policy。
- **对 B 的影响**：任务结束后保留系统事实、删除私有临时过程不是可选优化，而是防止存储和恢复上下文不断膨胀的必要机制。
- 来源：S-09。

## 5. 当前可行性判断（单路线，非最终）

**暂时支持 A 可实现。**

现有研究和官方实现共同支持以下结构：

- 角色专用上下文与压缩交接；
- 持久化 session/thread/checkpoint；
- 结构化 handoff 与输入过滤；
- 外部记忆按需检索；
- 工作目录和仓库级分区；
- 状态保留与清理策略。

但以下关键点仍未验证：

1. 当前本机上最简单的任务/角色分区组合；
2. 固定角色入口文件能否在无旧对话时恢复并继续真实编码任务；
3. Web 角色独立仓库的实际管理成本；
4. 上游版本变化到下游失效的最小依赖表示；
5. 结构化交接是否会导致频繁补充申请，抵消 token 收益。

因此本文件不能单独结束阶段二，也不能直接选定 B。

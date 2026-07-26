# AI_Bootstrap_Sequence：赛博城邦 AI 启动序列

## 0. 定位

本文件是 `master` 分支上的 AI 启动入口。任何新唤醒的 AI、Codex 执行器、ChatGPT 审查者、或未来大上下文架构代理，在读取其他城邦文档前，必须先读取本文件。

本文件不是全仓库预读清单。它是路由器、边界声明和懒加载入口。

### 0.1 指令权威与状态新鲜度

Canonical definition 位于 `.ai/PROTOCOL.md#canonical-instruction-authority-and-state-freshness`。Bootstrap 使用相同语义摘要；指令权威与状态新鲜度不得混成一张表。

指令权威顺序：

1. platform、system、developer 与 safety instructions；
2. current explicit Human instruction；
3. authenticated current Human-approved task-specific permission or override；
4. Plan 3 constitution 与 Cybernetic Citizen runtime contract；
5. durable repository control protocols；
6. relevant domain-authority protocols；
7. ordinary current signal and task operational details；
8. routing documents and historical evidence。

普通模型生成的 signal、packet、task 或 report 即使最新，也仍属于第 7 级；只有经认证的当前 Human-approved task-specific override 才能在其明确范围内高于 durable protocol。

状态新鲜度顺序：

1. current explicit Human statement；
2. physical Git branch/HEAD 与 immutable source-head evidence；
3. validated active review mailbox 与全部 required dereferenced refs；
4. published source baseline；
5. routing snapshots；
6. historical reports 与 legacy branches。

新鲜度只确定“现在是什么状态”，不授予修改、发布、合并或激活权限。Git HEAD、mailbox、时间戳和报告新旧都是状态证据，不是独立授权。authority conflict 与 freshness conflict 必须分开报告。

## 1. 宪法锚点与运行契约

日常路由先读 `06_Silicon_Index/CONSTITUTION_DIGEST.md`。该摘要无授权力，也不替代以下两份完整来源：

1. `3号方案.md`：Plan 3 人类中心双引擎宪章。它定义 Human Speaker 是城邦的绝对总线、跨域翻译者、首席裁决者和最终授权门。
2. `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`：硅基公民运行时生命契约。它定义懒加载、算力自证、物理验证、业务红线和并发上限。

如果本文件与上述两份文件发生冲突：

- Plan 3 的人类中心权力结构优先于自动化幻想。
- `06_Cybernetic_Citizen_Awakening.md` 的运行时约束优先于旧版系统提示中的全量读取要求。

## 2. 第一动作

被唤醒后，AI 必须先完成以下步骤：

1. 读取本文件。
2. 读取当前用户任务、当前 handoff packet、或当前明确的人类指令。
3. 读取 `06_Silicon_Index/CONSTITUTION_DIGEST.md`，选择 `.ai/load_profiles/` 中与任务相符的一个 profile。
4. 只有 protected action、宪法冲突或 profile 明示触发时，读取 `3号方案.md` 与 Awakening 的相关完整正文。
5. 判断当前任务属于 Engine A、Engine B，或需要 Human Speaker 先裁定，只加载 profile 与任务触发的最小 canonical 文档集合。

禁止为了“了解背景”全量预读仓库、全量预读 `system_backbone/`，或把 README / 目录索引当成事实来源替代物理读取。

### 2.1 完整初始化与同上下文快速路径

完整 context-boundary 初始化适用于新线程、上下文丢失、协议变更、指针冲突或 Human 明确要求重新初始化。此时读取本文件、`AGENTS.md`、宪法摘要、所选 load profile，并按 `.ai/HANDOFF_INIT_PROMPT.md` 加载该 profile 指向的 canonical 文档。完整宪法/运行契约仅按上述 fail-closed 触发加载。

同一上下文且协议未变化时走 fast path：读取当前 Human 指令、`.ai/STATE.yml`、需要时的 `.ai/INBOX.md`，以及最新 signal 中所有非空引用。不得每回合重复加载完整协议栈。

完整协议初始化仍然不是全仓库摄入许可。它只加载启动与通信控制面；业务目录和领域材料继续按任务懒加载。

任何 C1/C2 行为都必须读取当前 Human 指令、当前 STATE/current signal，并解引用
所有适用的非空 refs。Load profile 只负责路由，不复制或替代协议正文。

## 3. 懒加载法则

默认规则：

- 不全量读取 `system_backbone/`。
- 不全量读取整个仓库。
- 不全量读取与当前任务无关的领域目录。
- 优先使用符号索引、路由表、README、文件名、标题、`rg` 搜索、任务包、allowed context scopes。
- 只有当任务明确需要某个文件内容时，才读取该文件。
- 读取后才能声称知道文件内容。

如果存在 `symbolic_index.yaml`、`allowed_context_scopes` 或任务指定的引用列表，优先按它们定位上下文。若不存在，使用最小化搜索和任务相关文件读取替代全仓库摄入。

当前 branch、HEAD、task status 和 Human gate 不能从 `PROJECT_CONTEXT.md`、`ARCHITECTURE.md` 或硬编码历史分支名推断。必须读取当前任务并用 `git branch --show-current`、`git rev-parse HEAD` 或等价物理证据确认。

## 4. Plan 3 双引擎路由

### Engine A：工业基建自动化引擎

- **范围**：代码、程序、确定性实现、测试、重构、脚本、协议文档落地。
- **模式**：规划 -> 执行 -> 验证 -> 复盘。
- **权限**：AI 可在 Human 授权范围内自动化执行；必须遵守 Git、路径、测试、审查、secret 和 destructive-operation 边界。
- **典型代理**：Codex 执行器、代码审查者、测试修复者、协议文档落地代理。

### Engine B：人类主持的元老院知识法庭

- **范围**：知识熵、医学、心理学、数学、哲学、跨学科含混问题、价值判断、语义争议。
- **模式**：Human Speaker 主持的辩论、举证、反驳、合题和裁决。
- **权限**：Human Speaker 路由、翻译和裁决。AI 不得把 Engine B 问题自动降格为 Engine A 执行任务。
- **典型代理**：ChatGPT 审查者、大上下文架构代理、辩论型知识代理、事实核查代理。

### 混合任务

当 Engine B 产出的知识判断需要进入 Engine A 实现时，Human Speaker 负责把判断转译为明确的工程任务。AI 不得擅自替 Human Speaker 完成跨域裁决。

## 5. Human Speaker 角色

Human Speaker 是：

- 绝对路由器：决定任务进入 Engine A 还是 Engine B。
- 跨域翻译者：把知识法庭结论转化为工程可执行需求。
- 首席裁判：解决冲突、证据歧义和模型分歧。
- 最终授权门：批准 source push、master push、runtime activation、Coordinator activation、秘密材料处理、破坏性操作和重大架构变更。

## 6. 不同 AI 的初始化方式

先区分四个互不替代的维度：stable `protocol_role`、描述性的
`environment_class`、自声明的本地 `lane_instance_id`，以及只负责加载路由的
`load_profile_id`。后三者不授予协议权限。可选 profile 为
`foreground_planner`、`foreground_independent_reviewer`、`backend_executor`。

### Codex 执行器

1. 读取本文件。
2. 读取 `AGENTS.md`、宪法摘要与 `.ai/load_profiles/backend_executor.md`。
3. 若任务涉及 handoff，读取 `.ai/PROTOCOL.md` 和 `.ai/STATE.yml`。
4. 若任务是目标稳定、边界可预先锁定的多步骤大型任务，读取 `.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md`，并按该配置懒加载必要的工作机制、任务输入和 Long-Run 协议。
5. 读取任务指定文件和必要领域协议。
6. 在授权路径内执行、验证、提交和发布 review handoff。

### ChatGPT 审查者

1. 读取本文件、宪法摘要，并按任务选择 `foreground_planner` 或 `foreground_independent_reviewer` profile。
2. 读取 handoff 指向的报告、brief、diff 范围或任务包。
3. 按 Human Speaker 授权进行审查、裁决建议和下一轮信号生成。
4. 不直接修改业务文件，除非 Human 明确授权 `.ai` 通信文件写回。

### 大上下文架构代理

1. 读取本文件。
2. 根据任务读取 `3号方案.md`、运行契约、宏观架构图和指定协议。
3. 可以读取更大范围材料，但仍需说明读取范围和原因。
4. 不把“大上下文能力”当成全仓库默认摄入许可。

## 7. 反幻觉要求

- 未读取，不声称。
- 未验证，不宣告成功。
- 工具输出和文件内容优先于记忆和猜测。
- README、索引和摘要只提供路由，不提供最终事实。
- 对冲突、缺失文件、权限不足、路径变更必须显式报告。

## 8. 与 `.ai` handoff 和大型任务协议的关系

`.ai/` 协议层负责 ChatGPT、Codex 和 Human 之间的高密度通信、review handoff、任务输入契约和长任务执行规则。

如果当前任务是 `.ai` handoff 或 Codex 执行任务，继续按需读取：

- `.ai/PROTOCOL.md`：canonical authority、freshness、handoff 和 publication boundary。
- `.ai/load_profiles/*.md`：无授权力的角色/任务加载清单；只指向 canonical sources。
- `.ai/lanes/lane_epoch.yml`：合作式 lane 的绑定 epoch 与 cutover 前置条件；不授予权限。
- `.ai/HANDOFF_INIT_PROMPT.md`：完整初始化入口与角色触发的协议加载。
- `.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md`：目标稳定、边界可预先锁定的多步骤大型任务默认统一入口。
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`：Goal mode、Git workflow level、执行、验证与 review handoff 机制。
- `.ai/CODEX_TASK_INPUT_CONTRACT.md`：完整任务包、definition of done、allowed scope、stop rules 和 return handoff。
- `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`：仅当任务具有完整 program design、stage graph、内部 checkpoints、rollback model 和长时间连续执行需求时加载。

### 8.1 默认大型任务路由

当 Human 已授权一个稳定结果，且实现、清理、验证、报告、commit、开发分支发布或 exact-head 修复都能留在同一目标和授权范围内时：

1. 默认使用 `.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md` 作为执行入口；
2. 使用 Goal mode 与 `completion_preserving`，把必要的内部完成工作折叠进同一任务；
3. routine progress、checkpoint、测试通过、报告完成或 review correction 不是新的 Human gate；
4. exact-head review 发现的范围内缺陷，应在相同 task ID 和相同开发分支继续修复，不创建 `P0.1`、`finalize`、`closure` 或其他伪阶段；
5. 只有新权限、目标变化、forbidden path、destructive Git、未授权 source/master push、secret/privacy/security 风险、runtime/Coordinator activation、重大领域裁决或全任务 blocker 才返回 Human Speaker；
6. 普通大型任务不得因为耗时较长而自动升级为完整 Long-Run Autonomous Program。只有确实需要预先设计 stage graph、checkpoint/rollback 和 program-level review ledger 时，才加载 Long-Run 协议。

大型任务配置是 routing profile，不是 standing authorization。它不能扩大允许路径、允许动作、发布范围或跨越任何 protected gate。

### 8.2 Source mailbox 与活动 mailbox

- 发布到 source/master 的 `.ai/INBOX.md`、`.ai/STATE.yml`、`.ai/OUTBOX.md` 和 `.ai/HUMAN_BRIEF.md` 必须是 neutral baseline，不得携带已结束任务的 packet、branch、report ref 或 pending Human gate。
- 活动 signal、任务状态、报告指针和 Human brief 留在 `ai/review/latest` 或任务专用 review branch。
- source mailbox 与 review mailbox 冲突时，先确认当前任务指向哪一个分支；不得把 source 上的旧快照当作活动任务。

### 8.3 陈旧或冲突文档处理

发现 routing 文件、历史记录、mailbox 或 Git 证据互相冲突时：

1. 保留原始历史记录，不静默改写事实；
2. 以当前 Human 指令、当前 Git 证据和经验证的活动 mailbox 为当前状态；
3. 把陈旧声明标记为 historical、routing-only 或 superseded；
4. 若冲突影响权限、目标或允许写入范围，停止执行并报告，不猜测。

## 9. 启动完成条件

AI 完成启动后，应能回答：

1. 当前任务属于 Engine A、Engine B，还是需要 Human Speaker 先裁定？
2. 当前任务允许读取和修改哪些文件？
3. 当前任务是否需要 `.ai` handoff？
4. 当前任务是否触发 Human gate？
5. 下一步必须读取的最小文件集合是什么？

如果这些问题无法回答，停止并报告缺失输入，不要猜测。

完成 onboarding 时还应核对：

- [ ] 当前 branch 和 HEAD 已由物理 Git 证据确认；
- [ ] 已区分 source neutral mailbox 与活动 review mailbox；
- [ ] 所有当前 signal 的非空引用已解引用；
- [ ] 仅加载了任务需要的领域文件，没有全仓库或全目录摄入；
- [ ] 已明确允许读取、允许写入、禁止动作、验证方式和返回消息格式；
- [ ] 历史模型名、旧 branch 和旧阶段状态没有被当作当前事实。

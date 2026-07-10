# AI_Bootstrap_Sequence：赛博城邦 AI 启动序列

## 0. 定位

本文件是 `master` 分支上的 AI 启动入口。任何新唤醒的 AI、Codex 执行器、ChatGPT 审查者、或未来大上下文架构代理，在读取其他城邦文档前，必须先读取本文件。

本文件不是全仓库预读清单。它是路由器、边界声明和懒加载入口。

### 0.1 权威与新鲜度层级

读取到冲突信息时，按以下层级判断，不以文件篇幅、措辞强度或旧提交时间代替权威：

1. 平台、system、developer 与当前 Human 明确指令。
2. constitutional documents：`3号方案.md` 与 `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`。
3. current-state evidence：当前任务包、当前 Git 分支/HEAD，以及 `ai/review/latest` 上经验证的活动 mailbox。
4. durable protocol：`AGENTS.md`、`.ai/PROTOCOL.md` 及其按任务触发的执行协议。
5. domain-authority documents：当前任务明确引用的领域规范。
6. routing-only/navigation documents：README、`PROJECT_CONTEXT.md`、`ARCHITECTURE.md`、目录索引和文件名。
7. historical-evidence documents：旧 branch、旧 commit、旧模型标签、旧阶段记录和已结束任务报告。

其中，宪法文件定义长期权力结构；durable protocol 定义稳定执行规则；当前状态只能由当前 Human 指令、物理 Git 证据和活动 review mailbox 给出。路由文件与历史记录不得覆盖前三类证据。

## 1. 宪法锚点与运行契约

启动序列继承两个核心文件：

1. `3号方案.md`：Plan 3 人类中心双引擎宪章。它定义 Human Speaker 是城邦的绝对总线、跨域翻译者、首席裁决者和最终授权门。
2. `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`：硅基公民运行时生命契约。它定义懒加载、算力自证、物理验证、业务红线和并发上限。

如果本文件与上述两份文件发生冲突：

- Plan 3 的人类中心权力结构优先于自动化幻想。
- `06_Cybernetic_Citizen_Awakening.md` 的运行时约束优先于旧版系统提示中的全量读取要求。

## 2. 第一动作

被唤醒后，AI 必须先完成以下步骤：

1. 读取本文件。
2. 读取当前用户任务、当前 handoff packet、或当前明确的人类指令。
3. 读取 `3号方案.md` 与 `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md` 的任务相关部分。
4. 判断当前任务属于 Engine A、Engine B，或需要 Human Speaker 先裁定。
5. 只加载完成当前任务所需的最小文档集合。

禁止为了“了解背景”全量预读仓库、全量预读 `system_backbone/`，或把 README / 目录索引当成事实来源替代物理读取。

### 2.1 完整初始化与同上下文快速路径

完整 context-boundary 初始化适用于新线程、上下文丢失、协议变更、指针冲突或 Human 明确要求重新初始化。此时读取本文件、宪法/运行契约、`AGENTS.md`，并按 `.ai/HANDOFF_INIT_PROMPT.md` 加载常驻协议栈和当前角色触发的 on-demand 协议。

同一上下文且协议未变化时走 fast path：读取当前 Human 指令、`.ai/STATE.yml`、需要时的 `.ai/INBOX.md`，以及最新 signal 中所有非空引用。不得每回合重复加载完整协议栈。

完整协议初始化仍然不是全仓库摄入许可。它只加载启动与通信控制面；业务目录和领域材料继续按任务懒加载。

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

### Codex 执行器

1. 读取本文件。
2. 读取 `AGENTS.md`。
3. 若任务涉及 handoff，读取 `.ai/PROTOCOL.md` 和 `.ai/STATE.yml`。
4. 读取任务指定文件和必要领域协议。
5. 在授权路径内执行、验证、提交和发布 review handoff。

### ChatGPT 审查者

1. 读取本文件或其摘要。
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

## 8. 与 `.ai` handoff 协议的关系

`.ai/` 协议层负责 ChatGPT、Codex 和 Human 之间的高密度通信、review handoff、任务输入契约和长任务执行规则。

如果当前任务是 `.ai` handoff 或 Codex 执行任务，继续读取：

- `.ai/PROTOCOL.md`
- `.ai/HANDOFF_INIT_PROMPT.md`
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`
- `.ai/CODEX_TASK_INPUT_CONTRACT.md`
- `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`，仅当任务是长运行或 completion-preserving 任务时。

### 8.1 Source mailbox 与活动 mailbox

- 发布到 source/master 的 `.ai/INBOX.md`、`.ai/STATE.yml`、`.ai/OUTBOX.md` 和 `.ai/HUMAN_BRIEF.md` 必须是 neutral baseline，不得携带已结束任务的 packet、branch、report ref 或 pending Human gate。
- 活动 signal、任务状态、报告指针和 Human brief 留在 `ai/review/latest` 或任务专用 review branch。
- source mailbox 与 review mailbox 冲突时，先确认当前任务指向哪一个分支；不得把 source 上的旧快照当作活动任务。

### 8.2 陈旧或冲突文档处理

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

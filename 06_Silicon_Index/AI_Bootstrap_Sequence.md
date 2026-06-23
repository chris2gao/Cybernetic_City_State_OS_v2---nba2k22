# AI_Bootstrap_Sequence：赛博城邦 AI 启动序列

## 0. 定位

本文件是 `master` 分支上的 AI 启动入口。任何新唤醒的 AI、Codex 执行器、ChatGPT 审查者、或未来大上下文架构代理，在读取其他城邦文档前，必须先读取本文件。

本文件不是全仓库预读清单。它是路由器、边界声明和懒加载入口。

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

## 3. 懒加载法则

默认规则：

- 不全量读取 `system_backbone/`。
- 不全量读取整个仓库。
- 不全量读取与当前任务无关的领域目录。
- 优先使用符号索引、路由表、README、文件名、标题、`rg` 搜索、任务包、allowed context scopes。
- 只有当任务明确需要某个文件内容时，才读取该文件。
- 读取后才能声称知道文件内容。

如果存在 `symbolic_index.yaml`、`allowed_context_scopes` 或任务指定的引用列表，优先按它们定位上下文。若不存在，使用最小化搜索和任务相关文件读取替代全仓库摄入。

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

## 9. 启动完成条件

AI 完成启动后，应能回答：

1. 当前任务属于 Engine A、Engine B，还是需要 Human Speaker 先裁定？
2. 当前任务允许读取和修改哪些文件？
3. 当前任务是否需要 `.ai` handoff？
4. 当前任务是否触发 Human gate？
5. 下一步必须读取的最小文件集合是什么？

如果这些问题无法回答，停止并报告缺失输入，不要猜测。

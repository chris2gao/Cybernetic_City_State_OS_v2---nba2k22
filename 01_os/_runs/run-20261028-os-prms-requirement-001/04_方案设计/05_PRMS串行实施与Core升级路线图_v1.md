# OS-PRMS 优先：上下文长期记忆系统与主 OS 经验升级的串行路线图 v1

- 规划日期：2026-10-28
- 状态：**执行顺序规划，不是软件开发授权，不是已完成阶段02证据**
- 当前唯一优先开发主题：**OS-PRMS（全局持续工作岗位记忆、G1/G2全局机制目录、活动任务恢复）**。
- 工作位置：NBA2K22 作为首个领域试点；PRMS 通用部分最终归属 `chris2gao/Cybernetic_City_State_OS_v2---core`。正式将内容迁入 Core 与 Core→其他 Domain 同步须分别走对应 OS 权限、审核、发布门。
- 已批准需求：`OS-PRMS-A-v1-RC02`，Git blob `ce037bb99e02c150f5e619eeb022b21444619b8c`。Q52=B：G1/G2全目录与概要可发现，按角色/任务读取必要全文，其他原件按需展开。A 的真实 Human 批准见 `01_os/_runs/run-20261028-os-prms-requirement-001/01_任务输入/15_...`、`16_...`；版本绑定不得被旧 run 状态否定。
- 冻结核查输入：Core master `446ca66ad48831f5fcdb1af18f37d07619e048c4`；NBA2K22 master `7742568ac677b3c16079887463f05e81cb1191ed`；NBA2K22 PR #18 规划 HEAD `094f1aa641f93dec2277707ad9dbf5bdb0341247`，**Draft 未合并**；PRMS规划分支 `cd018e2a3aa0c28c9b8b0db0f7c4c7df88491a21`。这些均为本次观察锚点，实际操作前重新获取HEAD。
- 禁止误报：候选规划≠主 OS 已经实现；REAL_GAME 实证≠所有Native能力可用；索引已写≠机器已校验；Q52 Human 同意加载≠游戏执行或Core写入权限；没有实际环境与测试数据不得报告PASS。

## 一、先锁定任务边界：做什么，不做什么

### 当前必须实现的 PRMS 产品边界

1. **B0 固定 OS Boot**：仓库现行根规范、任务授权、版本与角色身份的最小必要装载，不能被“关闭记忆”绕过。
2. **G1 Core 全局机制目录**：核心工作流、Mechanisms、Boot、Registry、工具与正式知识，有可追溯的目录/概要/原文引用；G1通用机制的所有权在 Core。
3. **G2 领域全局目录**：每个领域独立的已正式确认机制索引，目标根目录与 `08_Domain_Applications/` 同级（候选名 `09_Domain_Global_Mechanisms/`），属于 Domain-owned；篮球内容不进入数学领域。08仍保存业务源码/材料，G2可以引用而不复制全08。
4. **T1/T2 任务记忆**：活动任务或进行中的任务系列可按角色/Human选择恢复已完成的部分；完成后退出默认加载但历史不丢。
5. **K1/K2 可复用经验**：任务经验保留来源和反证，按评审/确认提升为G1或G2；未经正式发布的提炼不伪称全局规范。
6. **岗位记忆和恢复**：持久RoleInstance、CURRENT、历史事件、SummaryCard、MemoryIndex、按需搜索/展开、Human选择加载、恢复验证回执；跨岗位完整复制原内容、目标CURRENT独立；同岗位会话接管以GitHub核验为准。
7. **状态/风险**：索引覆盖与stale、概要来源、未读/未验证报告；失败不污染有效CURRENT；会话权属受控拒绝能做到多强需实证，不承诺可强制关掉不合作旧客户端。

### 本次明确不启动的独立工作

- 将 NBA2K22 `方法论_v0.4` 直接替换主Core `v0.2`；这是**下一项独立的Core Workflow升级**，本PRMS研究只记录兼容风险，不做额外Workflow改版。
- 将Codex唯一工程Owner、Antigravity顺序协助等NBA特有安排设为所有领域无条件默认；这些是后续条件化任务编排升级候选。
- 安装、全局启用或在游戏进程调用REA；后续另做 Core 可选工具治理与按环境验证。
- 合并PR#18、将游戏数据底座迁移到其他分支、创建09真实目录、修改Core/master或其他域的master、直接把全部NBA2K22 08资料复制进Core。

## 二、唯一活动主线：逐阶段、逐产物交付

| 顺序 | 目标与阶段 | 可直接监督的交付物（候选文件名） | 必须发生的真实验证 | 完成定义 | 状态 |
|---|---|---|---|---|---|
| 0 | 01b状态记录闭合 | 当前run的 `run.yml` 正确指向RC02及Human确认记录 | 合法写入、GitHub远端回读、版本blob一致；保留RC01历史；不暗改master | 程序状态与已存在Human批准一致；若写入通道阻断，输出精确障碍并保留证据，不把Human批准变成false | 待修复，不重开需求讨论 |
| **1** | **02A：Core/Domain机制资产逐文件盘点** | `02_信息收集/01_Core_G1现有能力与权威目录矩阵.md`、`02_信息收集/02_NBA_G2内容生态与候选目录矩阵.md`、可选机读`source_inventory.json` | Core Boot/Registry/Mechanisms/工具/Context真实path+SHA；NBA 08/PR#18 的13模块、游戏机制资料库和REA入口逐项source→owner→status；区分master与Draft，标缺口 | 能回答“有哪些机制、权威文件在哪、能否复用、加载哪一层、已有还是候选”，每行有可访问来源与失败标记 | **现在下一个实质工作** |
| 2 | 02B：GitHub持久性与任务生命周期调查 | `03_GitHub_CURRENT_owner_history_实证.md`、`04_TaskSeries与角色记忆模型现有能力.md` | 创建隔离测试仓/授权分支的CAS/并发/部分写入/不可见归档实验；或明确只读、未执行；检查任务正常closeout、跨窗口引用版本 | 当前能力/不可行/可绕过/未测试分开，有精确命令/输入/输出/状态 | 待01完成 |
| 3 | 02C：概要/索引/上下文恢复验证 | `05_G1_G2_T1加载与失败样本.md`、`06_索引摘要恢复质量及预算实验.md` | 以真实多领域机制和系列任务，验证目录覆盖、角色相关加载、旧源stale、缺SHA、预算限制、Human拒绝G2、任务完成后退出默认；可用时做GPT/Codex对照，否则NOT_RUN | 逐例有标准答案、实际装载清单和来源回执，不仅有示例prompt | 待02完成 |
| 4 | 02D：收口实证与风险矩阵 | `07_RES001_020_证据-缺口-可复用能力矩阵.md`、`08_阶段02结论与B方案设计输入.md` | 20项RES每项映射至少一条实证/明确缺口；所有疑似矛盾回到源版本；对跨域09所有权/兼容评估 | 可以决定阶段03B采用何方案，同时标注无法证实的项目，不为了结案造数据 | 待03完成 |
| 5 | 03：设计B（Core PRMS + Domain配置） | 状态对象图、持久化Schema/文件布局、G1/G2目录契约、索引更新器和分层检索算法、Human加载I/O、并发接管与全量复制、失败回执、迁移兼容设计 | 设计映射RES/已核证风险与反例；文档由Human审查B后才作为开发基线 | B明确到Codex可直接按路径编码、每项都有验收条件；不能把B的技术选择冒充旧Human已批准A | 待阶段02 |
| 6 | Core工程实现（按已经批准的设计，分段但同一主任务） | 最小可运行Core Loader/Registry/PRMS状态存储/索引概要/恢复验证器；领域09最小示范配置；受控发布和迁移脚本 | 每批变更做直接相关离线检查，保持GitHub来源和原权威位置；不因有脚本就宣称全量生效 | 从**真实新窗口**能按Human选择恢复G1/G2/T1，生成可核验回执；错误SHA/stale必须失败可见 | 未授权、未启动 |
| 7 | 集中验证、独立审核与Human发布 | 固定版本测试矩阵、失败/恢复记录、独立审核、Core受保护发布审批，按Human请求向单个领域分发并核对09不受损 | 只承认实际执行过的测试、审核与合并；不会自动把所有领域更新到最新Core | 经过实际发布/验收后才叫Core PRMS正式可用；各域另有继承状态 | 未启动 |

> 候选文件名用于交付规格，尚未创建正式阶段02 Run文件或假称程序已经实现。每次推进只处理当前一项，再出下一项；阶段02的只读审查可以在状态修复待处理时保持证据连续，但不能误报状态门已经机器通过。

## 三、第一项实质工作（02A）怎么做：精确任务书

**问题**：新窗口（GPT或Codex）进入一个OS领域仓库，怎样证明它发现了应发现的所有Core全局机制G1，以及该领域的正式G2，并精确知道当次任务应该阅读全文还是只读概要？

**对象与精确输入**：

- Core `01_os/02_boot/`、`01_os/03_mechanisms/`、`01_os/05_registry/`、`01_os/06_execution/boot/`、`01_os/04_skills_and_tools/`、`01_os/01_workflow/`、`CORE_MANIFEST.yml`、`new-domain.ps1`。
- NBA `08_Domain_Applications/Antigravity_GM_Engine/PROJECT_INDEX.md`、`docs/development/PROJECT_MODULE_REGISTRY_V2.json`、`docs/development/PROJECT_INDEX_SYNC_CONTRACT_V1.md`、`docs/game_mechanics/README.md`、`research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md`；这批PR#18相关文件来自固定`094f1aa...`，并不等于当前NBA master已上线。
- 一个非篮球领域样本：数学OS `---maths2.0` 的现行domain文件和真实目录，保证G2不串域；其它英语/作息领域可后续抽样，无须本次扫描所有仓库。

**逐行记录模板**：

| 字段 | 说明 |
|---|---|
| `record_id`, `source_repo`, `ref`, `commit_sha`, `path`, `blob_sha` | 精确权威来源，区分实际目标分支与master |
| `layer` | B0/G1/G2/T1/T2/K1/K2；一条材料可关联多用途但只有一个主所有者 |
| `owner` | `core_owned` / `domain_owned` / task_history / external_reference |
| `authority_status` | `published_canonical` / `domain_confirmed` / `draft_pr` / `historical` / `candidate` / `unverified` |
| `role_applicability`, `trigger`, `required_source_refs` | 新窗口加载条件和依赖 |
| `summary_available`, `source_fulltext_locatable`, `loading_depth` | 目录/概要/相关原文三种加载层次分开 |
| `existing_loader`, `existing_registry`, `existing_validator` | 复用现成Core机制或无现成实现 |
| `coverage_scope`, `excluded_or_missing`, `stale_conditions` | 目录完整性和失败可见性，不把未知当0 |
| `core_gap`, `needed_in_stage03`, `test_scenario` | 一行一条后续工程具体动作/验收 |

**两项特别要核实的路径关系**：

1. NBA最新项目索引中的13个模块 P00-P12 是**待推广的领域导航实例**，不等于已经完成自动更新的PRMS。索引合同承认尚无CI/Hook自动强制；后续需设计状态及字段验证器。
2. `09_Domain_Global_Mechanisms/` 尚不存在；本次02A不能将其伪造为已建。应给出08资料中可被提升为G2的“正式域机制候选集”，区分**已有Human确认领域政策**、**PR #18草案**、**纯原始资料/源码**和**已结案的历史任务**。

**四个必备失败例（可以先设计成离线测试样例，真实执行标NOT_RUN）**：

- `G2_WRONG_DOMAIN`：数学窗口加载了NBA的P09/REA游戏合同→不得算恢复成功。
- `INDEX_STALE`：Registry或原文SHA变更但概要仍指旧有效版本→标stale/partial而不是READY。
- `DRAFT_NOT_MASTER`：NBA PR #18源存在，但`master`未包含→必须标注正确来源分支，不可谎报master正式可用。
- `MODULE_SOURCES_NOT_LOADED`：只读总索引而未展开当前实际需要的P04/P09资料→不能宣称理解了相关游戏机制或可操作REA。

**本项结果验收**：要求提供一张有**真实文件路径、SHA、分类、复用接口、缺口、下一步状态**的矩阵。不要只提交目录统计、漂亮架构图或者“建议后面开发”的散文。

## 四、PRMS与NBA2K22经验的处理：只吸收两个，其他排队

| NBA候选 | 当前处理 | 理由及范围 |
|---|---|---|
| P-01：全项目总索引、13模块Registry | **纳入当前PRMS 02A实证和03 G2目录方案** | 它是当前G2发现/角色按需加载的真实样本，不构成新的独立工程主任务 |
| P-02：同PR更新索引、来源和验证证据 | **纳入当前PRMS索引同步合同的设计与后续validator** | 与RES-018..020直接关联；只做索引一致性，不全面改造所有仓库研发工作流 |
| P-11：事实证据等级、UNKNOWN/真实回读/版本 | **纳入当前PRMS事件、SummaryCard、RecoveryReceipt的语义** | 没有它无法正确判断“记住了什么、是否过时、是不是实测” |
| P-12中的跨窗口恢复、失败回执部分 | **作为当前PRMS测试输入的来源示例** | REA交接文件真实存在；此时只读用于上下文恢复，不启用REA工具本体 |
| P-03：01a/01b工作流升级 | **下一独立任务** | Core v0.2与NBA v0.4兼容问题应登记；不是PRMS运行机制实现的前置整体改造 |
| P-04/P-05/P-07：跨模型Owner、协作和验证优化 | **再下一项Core任务编排升级候选** | Core已有task_orchestration，需单独去重、条件化并Human确认，不能篡改通用OS角色默认 |
| P-06：领域研究先行方法 | **后续02信息收集与提炼机制的独立任务** | 已有第二阶段信源合同，待做最小差异扩展 |
| P-08/P-09：REA通用适配和方法 | **后续独立OS工具治理任务** | 已有历史Windows实测，但不保证Core/其他领域装机；不能被PRMS加载时自动执行 |
| P-10：NBA专有RVA/交易/游戏ABI等 | **仅NBA领域09/08，绝不迁移Core通用层** | 属特定build/业务权限的领域知识 |

**串行队列（非日期承诺）**：

```text
当前：PRMS — 完成02A资产盘点 → 02B/02C真实验证 → 02D证据闭合
                 → 03方案B和Human确认 → Core授权实现 → 独立验收/发布
随后：Workflow 01a/01b兼容升级（Core v0.2 ↔ NBA v0.4）
随后：Core任务编排与跨模型交接通用化（条件规则，不照搬NBA模型分工）
随后：Core第二阶段领域研究/证据成熟度改进
随后：REA可选工具的Core适配、环境测试与按需注册
```

如Human改变优先级，可调整队列；未经新指令不同时启动多项Core改造。REA的未来升级适用工具治理/OS权限，并不因本路线登记就获得安装或调用许可。

## 五、每次进度必须向Human提交的监督凭据

1. **当前正在做哪一项**：编号+一行产品问题，不能同时报多个大任务都“进行中”。
2. **实际变更**：文件或测试脚本的确切路径/源仓/分支/commit；未提交的临时报告要明确说明。
3. **实质产物**：至少列3条“新增事实→依据→对PRMS功能设计的直接影响”，而不只写“完成研究”。
4. **正反例/验证**：执行命令、输入、返回/日志、标记PASS/FAIL/NOT_RUN；只读文件存在不是程序测试通过。
5. **风险缺口**：区分缺少原始证据、当前工具不可用、需要Human新授权、技术方案仍未决定四种情况。
6. **下一项可验收工作**：明确输入和具体文件及完成标准，不以“继续推进”代替。

**下一次只做02A的前半步**：Core G1目录/Boot/Registry真实核对，以及NBA P00–P12与G2候选的逐行关联。完成并给出具体矩阵后，再开始02B的存储和会话接管实验。

## 六、已知阻塞与风险边界

- **Run YAML指针未同步**：截至本次只读回查，`run.yml`仍是`stage: 01b_requirement_result_modeling_in_progress`、`version: OS-PRMS-A-v1-RC01-CANDIDATE`、`confirmed:false`，与15/16号Human批准RC02证据不一致。需要在合法允许的任务状态更新渠道修正并读回；当前不借换工具通道绕过以前的写入安全拦截。此问题是阶段记录治理，不代表要重做Human已批准的A。
- **Core目前没有真实09目录/PRMS程序**：不得将规划文件的目标路径称为已建立，或将自动owner fencing当实证能力。
- **PR #18是Draft**：项目索引和REA知识可用作研究源，但还不是NBA master通用准入。以精确commit加载。
- **REA历史资料的旧进程PID和授权**不能迁入未来窗口的可执行权限。
- **真实跨GPT/Codex新窗口恢复**需要在有可执行环境和对应Human授权时测试，不能用这份计划替代测试回执。

## 七、参考来源

- PRMS完整A与原始Human确认：`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/cd018e2a3aa0c28c9b8b0db0f7c4c7df88491a21/01_os/_runs/run-20261028-os-prms-requirement-001/03_需求建模/29_OS-PRMS_完整需求结果模型A_v1-RC02_整合封版.md`
- NBA项目索引：`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/PROJECT_INDEX.md`
- NBA模块注册表：`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/PROJECT_MODULE_REGISTRY_V2.json`
- NBA索引同步合同：`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/PROJECT_INDEX_SYNC_CONTRACT_V1.md`
- Core上下文机制：`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/context_management/%E6%96%B9%E6%B3%95%E8%AE%BA_v1.md`
- 开发经验审查：`OS_PRMS_NBA2K22_to_Core_Experience_Promotion_Audit_20261028.md`（本会话已生成的独立审查材料）

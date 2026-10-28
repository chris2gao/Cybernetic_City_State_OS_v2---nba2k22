# OS-PRMS · 完整技术设计 B-v1-RC01（待 Human 审核）

> **状态**：`DESIGN_CANDIDATE_NOT_HUMAN_CONFIRMED`；仅为阶段03最终技术设计候选。本文不是已运行的软件、授权证明、测试通过报告或主 Core 的正式机制版本。  
> **需求权威**：已获 Human 批准的 `OS-PRMS-A-v1-RC02`；blob `ce037bb99e02c150f5e619eeb022b21444619b8c`；Q52=B。以需求 A 的实际权威记录为准，本文不改写 Q1–Q52。  
> **源证据快照**：Core `446ca66ad48831f5fcdb1af18f37d07619e048c4`；NBA2K22 PR #18 `094f1aa641f93dec2277707ad9dbf5bdb0341247`（Draft、未入 master）；数学 `c877e4e3b08bd1f2edacb725bb5f1f04a57a3277`。实施前必须重新读取。  
> **本阶段行为**：本文件在聊天附带的工作环境生成；没有修改任何 Core、Domain、GitHub master，没有调用 REA、游戏或真实岗位记忆服务，也没有执行下面的工程验收测试。

## 0. 设计结论：交付的不是「一个索引文件」

PRMS 是现有 Cybernetic City-State OS `context_management` 的版本化扩展，由以下六个可互相核证的能力组成：

1. `CatalogResolver`：从正式 Core 入口发现 G1 全局机制，从领域 G2 根发现该仓机制，从任务入口发现 T1/T2；报告真实扫描范围、遗漏和状态；仅发现不等于正式发布或执行授权。
2. `DurableRoleMemory`：给 OS 工作岗位（而非 NBA2K22 游戏内部人格）提供稳定 RoleInstance、Human 决定/事实/推断分级的追加事件、Checkpoint 和当前有效状态。
3. `StatePublisher`：把不可变事实和检查点先准备、校验，再通过一个可验证的有效 Git ref 前进提交原子公开 CURRENT；失败保留旧 CURRENT。
4. `WriterGate`：可信会话身份绑定、接管、旧窗口 fencing；所有有效记忆写入必须在统一受控写入入口核权、比较 owner epoch 和 state version。
5. `SummaryIndex`：受来源证明约束的派生摘要、多维索引与精准增量失效，不取代原始记忆；支持完整内容复制和血缘。
6. `ContextAssembler`：B0 强制 Boot + G1/G2 完整目录概要 + 当前 Role/T1 + Human 当次选择，按预算装载正文/证据并生成实际恢复回执。

**正式工程成功定义**：以上六条的正例、负例、跨窗口实测与 Core/Domain 归属验证全部有外部可复核证据。仅把 Markdown/JSON/YAML 写进仓库不等于 PRMS 实现完成。

## 1. 核心架构与物理所有权：三种 Git 面，不能混合

```text
Core code repository (---core, core/master)
  ├─ 01_os/03_mechanisms/context_management/prms/  # 通用定义与Schema
  ├─ 01_os/02_boot/context_management/              # 在原Boot上版本化扩展
  ├─ 01_os/05_registry/                              # G1与PRMS注册/发现
  ├─ 01_os/06_execution/boot/context_management/     # 验证、装配、CLI适配
  └─ CORE_MANIFEST.yml                               # 09加入domain-owned
       │ 需Human按域请求的core合并；只传播代码与机制规范
       ▼
Domain code repository (NBA, Maths, ...)
  ├─ 08_Domain_Applications/                         # 业务原件和项目资料
  ├─ 09_Domain_Global_Mechanisms/                    # 领域所有的G2目录
  ├─ 08_Domain_Applications/domain.yml               # domain_id与目录入口
  └─ 01_os/07_content/_runs/                        # 已有领域任务证据

独立受控 PRMS state repository / trust boundary (不随core/master合并)
  └─ state branch(s): roles/{role_id}/events, checkpoints, CURRENT,
                      owner_epoch, publication receipt, copies, indexes
             ▲ 单一WriterGate核验身份+版本+Human任务授权
             │ 模型窗口只持读取/受控调用能力，不持能直改有效状态的通用Git token
             └─ GPT / Codex / Other authorized adapters
```

### 1.1 推荐的物理存储选择：独立 Git 状态仓库 + 受控写入入口

- **定案建议**：采用一个或多个由 Human 明确建立/授权的 PRMS 专用 Git 状态仓库，按 **安全与所有权域**（Core工作岗位、各领域岗位、必要的独立信任域）隔离；Core 代码仓库不持有实际可变岗位 CURRENT。状态仓库名称、是否一域一个、私有访问级别、托管地址，由工程接入配置而不是写死成虚假的已创建仓库；默认**私有且最小授权**，但私有不能替代敏感数据分类。
- `state_repository_id` 与 `domain_id`、`role_id`绑定；跨域复制需要显式的源/目标范围审批，不能凭 GitHub 可读就绕开 Human。
- 被索引的任务源可以仍在其原 repo（`01_os/_runs/`或`01_os/07_content/_runs/`）；其源引用有精确 commit/blob。**Q42=A 全量复制**则必须把获准源内容实际复制到目标安全域内，不是仅保存原路径指针。
- Git 快照历史只被视为耐久审计与可复原来源；绝不等同 GDPR 式强制擦除，历史不可因删除当前入口就宣称物理消失。
- 如 Human 不同意额外私有状态仓库、或 GitHub 配额/环境不满足，工程Owner必须提出有数据/权限实证的等价替代物理方案供审议；**不能默认写回公开Core代码树或把私密记忆放进Core可分发分支**。
- 专门状态仓库可以不用长期在线进程才能被读取；**有持久写入、接管、撤销能力时**，所有写入仍须经过一个可访问的可信受控入口。它可由 GitHub 原生工作流/受限App/托管服务组成，何者可行需要隔离实验，而不是由本文预言 GitHub Actions 必然满足。

### 1.2 信任边界（比目录层级重要）

| 平面 | 权威源 | 默认权限 | 不变量 |
|---|---|---|---|
| Core code G1 | 主Core受保护仓库 | 可发现/按需读；写依Core发布门 | 只含通用机制/注册；不得带Core岗位活动数据 |
| Domain G2 | 本领域09及引用的08 | 按本仓可见范围与Human装配选择 | 领域正式机制与原始业务资料分开；互域不串内容 |
| Role state | 相应独立PRMS状态仓库 | 经身份认证只读/受控调用；无模型直写有效ref | Event/Checkpoint/CURRENT/Owner版本可复核 |
| Task evidence | 当前仓合法Run与归档 | 按原OS工作集可发现规则 | 来源事实长期保留，摘要不是权威 |
| Secret/private runtime | 宿主凭据存储/不跟踪工作区 | 工具/OS强制权限 | 不写repo、不放在摘要/回执或模型可见原文中 |

**状态仓库是默认物理方案，不是新的跨组织权限体系**。与现有`repository_publisher_authority_v1.yml`一致：Human还是最高权限来源；目录/角色标签不生成权限；Core/master发布仍单独确认。

## 2. 固定源码目录和边界

| 建议路径 | 所属 | 交付职责 | 是否已存在 |
|---|---|---|---|
| `01_os/03_mechanisms/context_management/prms/` | Core | 数据契约、模型不变量、来源与依赖规则 | 候选新增 |
| `01_os/05_registry/prms_v1.yml` | Core | G1/G2/T1发现规则、Schema/Loader回指 | 候选新增 |
| `01_os/06_execution/boot/context_management/prms/` | Core | deterministic validation, Git store adapter, recovery pack, tests | 候选新增 |
| `01_os/02_boot/context_management/启动清单_v2.yml`或兼容修订 | Core | 固定B0与扩展版本入口 | 候选更新，必须与现有v1兼容 |
| `CORE_MANIFEST.yml` 的 `domain_owned_paths` | Core | 增添`09_Domain_Global_Mechanisms/` | 候选更新 |
| `09_Domain_Global_Mechanisms/` | Domain | `domain_mechanisms.yml`及知识来源目录 | 当前Core/NBA/Maths均无实际目录 |
| `08_Domain_Applications/domain.yml`的字段扩展 | Domain | 领域ID、G2入口/有效版本、Core兼容指针 | 候选更新 |
| `<separately-authorized-state-repo>` | Role-owner trust domain | role events、CURRENT、owner、summary/index、copy | **尚未创建** |

必须复用现有 `context_management` 的 Boot/Registry/`visible_set`/归档规则，及 `mechanism_activation` 的正式生效等级。**区分**：PRMS上下文深度`L0–L4`与Core机制生效等级`L0_DEFINED–L4_E2E_ADVERSARIALLY_VERIFIED`是两个不同枚举。任何入口索引不得把 `DRAFT` 文档升格为已激活机制。

## 3. 数据模型：身份、事件、当前态、索引、恢复与推广

### 3.1 正式逻辑对象（不是物理表数量）

| 逻辑对象 | 稳定键 | 必需结构或行为 | 主要关系 |
|---|---|---|---|
| RoleDefinition | `role_type_id@definition_version` | 职责、允许来源、记忆策略；旧定义留史 | 一定义多实例 |
| RoleInstance | `role_id` | stable ID/归属域/role definition，不随session改变 | 一实例多任务/事件 |
| RoleAssignment | `assignment_id` | task/role/Human有效权限来源 | 一角色多Assignment |
| RoleSessionOwner | `role_id+owner_epoch` | 受控token/session binding；active/expired | 一角色只有一个有效owner epoch |
| MemoryEvent | `event_id + content_digest` | 来源、事实/推断/Human决定、observed/recorded时间、幂等键 | 追加只增，不覆写历史 |
| Checkpoint | `checkpoint_id + evidence_watermark` | 固定事件集合和必要源完整性 | 可指向由其生成的CURRENT |
| RoleCurrent | `role_id + state_version` | 单有效指针；published commit/ref | 一个角色一条有效当前入口 |
| ExperienceCard | `experience_id+version` | 证据、反例、适用范围、stale、目标owner候选 | K1候选/K2正式发布分离 |
| SummaryCard | `summary_id+generation` | source hashes、事实/推断/Human决定分型、覆盖范围、遗漏 | 多对多来源 |
| MemoryIndexManifest | `index_id+generation` | source inventory、索引范围、missing/filtered/unregistered | 与摘要共同依赖源目录 |
| TaskSeriesCurrent | `series_id+derived_versions` | 成员、合法状态、里程碑、未决、续作 | 原任务事实聚合，不改写原run |
| GlobalMechanismCatalog / Entry | `catalog_id` / `mechanism_id@version` | canonical、publisher、机制生效状态、summary、source blob | G1或G2，但不混owner |
| HumanLoadDecision | `decision_id+session_id` | 本次Human允许加载的G1/G2/T1和深度、证据版本 | 一个会话可有后继选择 |
| ContextRecoveryReceipt | `receipt_id` | 实际读取、budget、缺失、校验及READY/PARTIAL/BLOCKED | 和source/loader run绑定 |
| FullCopyManifest / CopiedMemoryItem | `copy_id` / `copy_id+source_item` | 固定源清单、目标逐字节物理副本、血缘与风险 | 目标独立CURRENT |
| Publication/PromotionReceipt | `operation_id+commit` | 实际发布/来源/审核/权限/未知结果 | 机制的正式发布另受保护门 |

沿用 A-v1-RC02 RES-001..020与其19个基础逻辑对象；这里是合并视图，避免把新视图名误当20多张数据库表。字段类型、持久编码和JSON Schema将在Core代码内定义，至少拥有 `schema_version`、`owner`、`operation_id`、`repo+commit+path+blob_sha`、`expected_version`、`content_digest`、`published_at`、`proof_refs`、`status`、`retry_safety`。

### 3.2 追加事实不变量

- `HUMAN_DECISION / OBSERVATION / MODEL_INFERENCE / EXECUTION_REQUEST / EXTERNAL_RESULT / CORRECTION / REVIEW`必须独立分类；Human原始话语与模型推断不得合并成为单一「已批准结论」。
- 历史更正是带证据的新事件，不能悄悄改旧event；源 SHA 过期产生 stale，不静默覆盖旧事实。
- source commit、Git blob、实际 observation time、event creation time、工具执行时间不可相互替代；`UNKNOWN`不等于`false/0/missing`。
- 仅**已经提交并有读回证明**的内容可以叫durable；聊天窗口文字本身不自动持久化。无明确工具记录时，PRMS无法承诺捕获当前窗口所有思考/草稿。

## 4. Git 存储与有效 CURRENT 发布：具体算法

### 4.1 状态仓库内候选路径

```text
state root/
  protocol.json                     # 协议版本、owner范围、安全模式
  roles/<role_id>/identity.json
  roles/<role_id>/owner.json         # owner_epoch, active_session_proof_ref, authority refs
  roles/<role_id>/events/<event_id>.json
  roles/<role_id>/checkpoints/<checkpoint_id>.json
  roles/<role_id>/CURRENT.json       # 只允许受控提交者修改的有效指针
  roles/<role_id>/summaries/<generation>/...
  roles/<role_id>/indexes/<generation>/...
  roles/<role_id>/copies/<copy_id>/...
  publications/<operation_id>.json  # 可核验操作ID与状态commit
```

以上路径**只能在专用state仓**；不能照搬到Core/master。对于多个Role并发，初版可采用**每域或每角色独立可写ref**，明确 `role_id → ref` 的不可歧义路由；同一ref上的不同role提交若存在非必要冲突，工程可在满足单有效指针不变量的前提下细分ref。不能采用强制覆盖旧commit的 Git ref 更新。

### 4.2 原子可见的发布事务

**强推荐**：通过Git对象构造一个以当前 `state_ref_HEAD=H0` 为唯一父提交的新commit `H1`，包含新events、checkpoint、CURRENT pointer、owner状态及提交回执的整体树，然后对受保护state ref执行**非force前进**。GitHub特定API对冲突的真实效果需在隔离仓验证；允许用本地git push作为备选传输。单个ref前进是状态可见性的原子边界，不声称它赋予不同ref/仓库的ACID事务。

```text
Read ref H0 + CURRENT C0 + owner epoch E
  ↓ 验证session身份/assignment/Human允许的当前任务/expected_state
Freeze append-only Event set, source refs, idempotency ledger
  ↓ 本地组装候选树并独立验证 hashes、source可读性、目标checkpoint
Build Git commit H1(parent=H0) containing events + checkpoint + CURRENT C1
  ↓ gated non-force ref update H0→H1
  ├─ rejected: re-read current and return VERSION_CONFLICT / STALE_OWNER
  ├─ transport unknown: read HEAD+operation_id; never blind duplicate
  └─ accepted: remote readback H1/C1/evidence/owner, verify content
                   ↓ PUBLISHED_CURRENT
```

- 如果大量数据必须先暂存：写入临时不可作为有效state的对象/引用，**最终只能通过一个有效ref前进公开CURRENT**。部分暂存可以审计，但永不进入成功恢复链。
- 同一 `operation_id` + 同一内容digest重复，应返回 `ALREADY_APPLIED`；相同ID不同内容返回 `VERSION_CONFLICT`，不可重复生效。
- 对每次失败记录 expected/ref/remote proof/是否存在副作用及是否可重试；GitHub返回HTTP成功但远端内容不同不能宣称成功。
- 批量跨Role提交没有跨多ref原子保证；跨角色复制必须有 `source frozen inventory → target staged → target validated CURRENT` 的独立目标提交协议。
- **绝不以 GitHub Contents API 的单文件SHA校验冒充多文件事务、全局互斥或旧session强制失效。**

### 4.3 把本规划里的真实状态漂移当作反例

已有真实来源：Human审批 `OS-PRMS-A-v1-RC02` 的原始记录/版本绑定在NBA2K22规划分支，`run.yml`却仍写 `OS-PRMS-A-v1-RC01-CANDIDATE`和`confirmed:false`。PRMS应该返回 `APPROVED_BUT_POINTER_STALE`，同时显示批准证据和旧指针，再通过合法写入与远端读回修复；不能把报告或聊天中“已修复”当成功。**当前这项旧Run差异尚未修复**，是Codex接手工程前要核销的已有工作项。

## 5. 新会话接管与旧窗口写入围栏：最终安全模型

### 5.1 技术上明确「接管」指什么

- 旧ChatGPT/Codex窗口可能继续显示、阅读或进行非受控外部工具操作。**PRMS不能物理关闭旧聊天或保证停止所有外部进程**。
- 本设计的可验证承诺是：旧窗口的**PRMS有效CURRENT更新请求**在接管生效后必须由受控写入入口拒绝，且无法持已有权限直接绕过这个入口写入有效state ref。对其它系统动作必须依照其实际权限机制独立保护，不把PRMS描述成万能系统沙箱。
- 提出接管需证明可信的当前session身份、role binding和任务授权；模型自己写`session_id`或`owner_epoch`不等于身份认证。可信服务对每个session颁发可撤销且作用域有限的访问能力；具体宿主接入须测试，不向聊天文件输出token。

### 5.2 分两级并对用户如实披露

| 模式 | 机制 | 适用结果 |
|---|---|---|
| `COOPERATIVE_FENCING` | 客户端约定写前检查`owner_epoch`和CURRENT SHA | 可用于早期隔离原型，**不能**签收RES-004/016的强制失效目标 |
| `ENFORCED_FENCING` | 权限层确保只有受控WriterGate能够更新有效state refs；每次在同一强制提交路径检查认证session/owner/epoch/expected version | 必须有旧客户端直接Git写入旁路负例和新会话正常写入正例，才可签收目标 |

**唯一安全发布方案**：所有正常GPT/Codex适配器不拥有状态库有效ref的直接写凭据；写入权只留给受控身份（例如受限GitHub App + 规则集 + 服务/受控Workflow），对直写HTTP/Git、旧session token、过期epoch和后台延迟请求均做否定试验。仓库管理员、人类平台管理员等更高权限主体天然在信任边界之外；不得声称无法被这些主体绕过。若工程无法在现有GitHub与产品surface中实现这个边界，返回 `FENCING_NOT_ENFORCEABLE`，**阻止强制接管能力上线并提交Human新的架构取舍**，不默认降级为合作式却标记功能完成。

### 5.3 竞态与失败演算

**接管与旧写并发**：假设旧epoch E，且远端状态HEAD H0。

1. 新session请求claim产生候选commit H1(parent=H0, epoch=E+1)；旧writer同时请求append产生H2(parent=H0, epoch=E)。
2. 受控WriterGate按权限/角色串行有效发布或在Git非force更新中比较实际ref；最多一个候选成为当前HEAD。
3. 若旧写先成功，它属于接管前的有效操作；新claim必须重读包含此事实的H2重新发起；**不允许新owner无证删除它**。
4. 若新claim先成功，旧写的E已经过期，必须被拒绝`STALE_OWNER`；即使其客户端正在运行，也不能使CURRENT后退。
5. 如果HTTP反馈未知，先只读查询operation_id和ref，再确定结果；不自动用相同商业/外部副作用请求重复执行。

**失权边界**：撤销的是受控state mutation capability；不承诺已泄露的全文记忆不可被旧窗口再读，不承诺旧窗口已终止，也不承诺其它工具（游戏、GitHub源码提交）的权限因PRMS接管而被撤销。

## 6. G1/G2目录发现和新窗口Human加载

### 6.1 三种「存在」必须独立显示

- `DISCOVERED_SOURCE`：仓库树上存在；`CATALOGED_SOURCE`：进入可追溯目录；`FORMALLY_PUBLISHED_MECHANISM`：经过目标owner权限、审核和正式版本发布。另列机制生效`L0_DEFINED..L4_E2E_ADVERSARIALLY_VERIFIED`、实际全文是否加载、当前任务是否授权执行，**均不可相互推导**。
- G1先从Core的canonical `01_workflow/02_boot/03_mechanisms/04_skills_and_tools/05_registry`建立已声明集合，再以冻结树枚举同一已批准scope的未登记条目，报告registered/unregistered/missing/stale。Core当前有七个带README的机制目录和七份启动清单，这些数字不是「全部能力已运行」证明。
- G2从`domain.yml`与`09_Domain_Global_Mechanisms/`发现该领域正式机制和源引用。NBA2K22 PR #18的P00–P12 13模块只是候选参考/项目导航，不自动转为13个正式G2机制；数学当前G2空必须报告`DOMAIN_CATALOG_UNINITIALIZED`，不能载入NBA文档作为替代。
- Core当前`09`不存在；**这是规划目标，不是假装文件已经创建**。Core新增09所有权宣告、脚手架和目录契约须先经Core合法授权开发。

### 6.2 Q52=B精确流程

```text
Fresh B0 bootstrap (mandatory / fail-closed)
  ↓ source freeze: core code commit, domain code commit, state ref, task source
Resolve G1 all applicable catalog entries and verified summaries
Resolve G2 current domain catalog (including incomplete/empty status)
Resolve T1 active task and related TaskSeriesCurrent; T2 terminal historical index only
  ↓ role/task/dependency rules → REQUIRED_FULL vs OPTIONAL_SUMMARY/FULL
Show Human an explicit proposed load selection + cost + unknowns
  ↓ Human current-session choice; no automatic replay of old window's optional choice
Load required mechanisms full text + approved summaries and expanded sources
  ↓ check actual source sha / omissions / budget / validity
Emit ContextRecoveryReceipt READY / PARTIAL / BLOCKED
  ↓ only THEN apply separate task/action authorization to any external mutation
```

- 选择不包含绕过B0。当前 Human 同一会话已有明确授权时直接沿用，不反复索要形式性批准；跨新会话必须展示有效选择范围与来源，旧session的可选装配许可不可静默变成新的session权限。
- SourceBlob缺失、重要机制正文未载、预算不足、Core version不兼容、合法任务授权无法验证时 `BLOCKED`；非关键可选来源缺失时 `PARTIAL`且只能执行不依赖该来源的安全工作。
- ContextReceipt的 `READY` 只表示**本次上下文已按设计正确装配**，不表示强制生效等级L4、写入许可或模型已经理解所有隐藏历史。
- 所有数量应带scope与计数依据：`indexed/filtered/unregistered/missing/unknown`；不做仓库范围外的「完整性」声明。无结果只能是 `NO_MATCH_WITHIN_SCANNED_SCOPE`。

## 7. 摘要、索引、任务生命周期与经验提升

### 7.1 Incremental summaries/indexes

- `SourceInventory(repo, commit, scope, path+blob list, coverage)`是一次生成的可核证来源清单。
- `DependencyGraph`将source blob映射到RoleCurrent/summary/index/TaskSeries/机制引用，来源变更时只标受影响记录stale；旧摘要原件留证。
- `SummaryCard`分别保存`verified_fact/actual_human_decision/model_inference/unknown`，带generation、generator版本、source/ref、水位、缺口和可追溯来源；正式Human决定必须可返回原事件而不是仅返回生成式摘要。
- 同一PR项目索引同步由NBA2K22 `PROJECT_INDEX_SYNC_CONTRACT_V1.md` 启发，但**不是所有历史都要复制进G2**。索引是导航/可见性能力，回执应区分当前分支、Draft/未合并、候选/独立验收。

### 7.2 T1/T2真实性

继承Core现行`context_management/工作集与归档契约_v1.yml`：open仅为其枚举的合法状态；terminal需要合法lifecycle+物理可读closure+引用安全+无私有runtime；自由文本unknown默认可发现但不可据此归档。关闭浏览器、达到额度、聊天中断**不是**终态；完整历史可查但默认不全文注入。

### 7.3 全量复制和经验推广

- `copy_role_memory(source, target, source_commit)`先冻结每项物理原件/byte digest清单；逐项复制到目标安全域，核验数量、内容字节与来源血缘，生成独立Target CURRENT。不可用摘要或原路径链接代替完整复制；若任何必需项缺失则不提交目标有效CURRENT。
- 复制只带**内容与来源**，不复制源RoleAssignment的当前任务权限、当前Owner会话、凭据或执行授权。
- 经验可从已结束任务提炼K1，证据/反例/适用范围/owner被正式评审和Human保护门确认之后才进入G1 Core或G2 Domain。REA的通用研究方法以后可候选提升到 Core `04_skills_and_tools`，NBA专用RVA/签约/交易规则仍留08/09；本 PRMS 阶段不启动REA开发。

## 8. 产品接口（概念语义，不锁死HTTP或Python类名）

| 操作 | 关键输入 | 输出和必须处理的失败 |
|---|---|---|
| `discover_context_layers` | repo/ref/role/assignment/domain/scan_scope | G1/G2/T1/T2、source SHA、partial与未登记 |
| `propose_load_selection` | frozen catalog/role/task/budget | mandatory/full/optional明细、真实来源/估算代价 |
| `record_human_load_choice` | Human本次真实选择/session/目录版本 | bounded selection record；拒绝不默认加载 |
| `assemble_approved_context` | B0 + selected frozen refs | 可追溯载入物与预算、缺失清单 |
| `verify_context_recovery` | assembly/readback/source proof | READY/PARTIAL/BLOCKED与下一步 |
| `register_role` / `bind_assignment` | role模板/有效任务授权 | 稳定role ID/不复制新权限 |
| `claim_owner` | authenticated session/role/expected epoch | 受控ref的确认commit与旧session失效事实 |
| `append_event` | operation_id/event/content hash/owner/source | immutable event, idempotence or conflict |
| `publish_current` | checkpoint, expected ref/version/owner | atomically visible CURRENT + remote proof |
| `search_memory` / `expand_memory` | role/task/topic/time/depth/scope | hits/coverage/excluded/unknown + exact refs |
| `copy_all_memory` | frozen source inventory/target/approval | full verified target objects + risk receipt |
| `propose_experience_promotion` | K1 evidence/target owner | candidate only |
| `publish_approved_mechanism` | verified proposal/Human gate/target owner | Core or G2 publication receipt, not runtime auto-activation |

公用请求必须带 `operation_id`、当前已验证 caller/role/assignment、期待的ref或epoch与来源；结果必须带`status`、`authoritative_commit_sha?`、`actual_source_refs`、`receipt_ref`、`retry_safety`、`next_action`。客户端可以是GitHub CLI、受控API或本地Codex Adapter，不能因为底层传输不同就绕过WriterGate。

## 9. 完成门与错误状态：对外不可撒谎

| 状态 | 必需行为 |
|---|---|
| `APPROVED_BUT_POINTER_STALE` | 指出Human批准原件与旧Current/run pointer，不抹掉任何一个事实 |
| `PUBLISH_NOT_CONFIRMED` | 重读Git ref和operation_id；拒绝把请求超时当已失败可重放 |
| `PARTIAL_STAGED` | 未发布候选不影响旧CURRENT；旧snapshot仍有效 |
| `STALE_OWNER` | 新接管后旧epoch不得发布PRMS有效CURRENT |
| `FENCING_NOT_ENFORCEABLE` | 未通过直写绕过负例则不启用强制接管模式 |
| `SOURCE_MISSING` / `SUMMARY_STALE` | 限定受影响scope，保留旧来源，要求补证据或重建 |
| `CATALOG_PARTIAL` | 报未登记/缺少/已过滤，不虚报全部枚举完毕 |
| `CONTEXT_BUDGET_INSUFFICIENT` | 不默删B0或任务必需机制，返回受阻及可调整项 |
| `COPY_INCOMPLETE` | 目标不进入正式CURRENT，不把索引或引用冒充原文副本 |
| `EXTERNAL_EFFECT_UNKNOWN` | 不自动重放不可逆动作；只读核对并保留未知 |
| `CORE_DOMAIN_COMPATIBILITY_BLOCKED` | 不自动跨仓 merge 或污染领域09 |

## 10. 与需求A 20项RES的交付映射

| RES | 主要承担模块 | 可核实交付证据 |
|---|---|---|
| 001–003 | Identity/RoleAssignment | 稳定岗位、模板历史和任务权限分离测试 |
| 004 | WriterGate | 同owner并发、接管/迟到提交与直写绕过测试 |
| 005–007 | StatePublisher/Event/Current | 历史只追加、单有效CURRENT、实际Git ref读回 |
| 008–009 | Experience/Publication | 审核/未批准提升负例、共享与开放读边界 |
| 010–011 | Catalog+Assembler | GPT/Codex真实恢复、版本/预算回执 |
| 012 | Recovery/Publish | 超时/重试、冲突、部分写入状态场景 |
| 013 | Core compatibility/promotion | Human已批准设计B后纳入Core规划/后续发布，不能省略受保护门 |
| 014 | Validation/independent review | 可运行全部SC矩阵、非Owner审查报告 |
| 015 | Copy | 源所有记忆项字节可核与目标独立CURRENT |
| 016 | Enforced takeover | direct-writer bypass失败+旧token禁止写入回执 |
| 017–019 | G1/G2/T1/T2/K1/K2/Catalog/Index | Core/领域隔离、scope统计、摘要失效、系列恢复 |
| 020 | Assembler/Receipt/Human choice | B0、Q52 B、实际已加载/排除/缺失精确回执 |

## 11. 工程顺序与角色：Codex唯一开发Owner

| 顺序 | 工程工作包 | 真实可交付结果及验收 |
|---|---|---|
| P0 | **03方案B经Human确认后，先把已批准的通用设计规范化纳入Core规划体系** | 提取经批准的B及来源证据到core-owned正式规划/机制候选位置；按Core实际授权、Human对受保护动作的确认和真实读回发布；**不等于运行时软件已完成** |
| D0 | 施工前权限与状态核对 | 核对A-RC02批准原件与陈旧`run.yml`、Core/Domain最新SHA、任务包、合法路径；修改Run时按官方Git权限/门执行并读回；不冒充Human额外许可 |
| D1 | Core定义和G1/G2发现 | 兼容Boot/Registry/Validator+Core09 ownership声明+NBA/数学分类/缺目录负例 |
| D2 | 独立state store与受控CURRENT | state repo隔离与最小权限证明、Git对象提交+ref CAS/读回、失败注入 |
| D3 | Role、Summary/Index、T1/T2/Copy | Event/Checkpoint/Current、多维检索、增量stale、全量目标复制和血缘 |
| D4 | 受控接管与Human恢复 | WriterGate强制失权正反例、会话选择、预算装配与真实GPT/Codex恢复 |
| D5 | Core/Domain集成与独立审核 | 20 RES测试、边界和负例、跨域不传播状态、非实现者审核；经Human确认才合入Core/master/各域 |

**P0是获批设计B向Core规划规范的归属同步，不能等到D5软件验收后才做；该同步要遵守受保护仓库的现有授权门。D0–D5是一个Codex主Owner连续开发，不应被误认为六个并行长任务。** 不默认使用Antigravity；本项目不运行NBA2K22、REA，也不需要游戏管理员权限。GPT负责本设计、原始来源核对和Human最终审核协助，不在另一工作区并行改同一套Core代码。

### 11.1 Codex可以合理自行决定的细节

在不改变本文架构/需求A/现有OS权限的情况下，可选Python CLI实现、JSON Schema版本、单role ref或多role ref、具体短期缓存、摘要生成器、代码文件命名及局部测试夹具；必须在交付中记录选择理由和向后兼容性。**不能自行改变**：独立持久状态与代码树隔离、全量原件复制、独立可信写入门、必要Human选择、不可声称伪强制接管、Core发布权、09域所有权、Q52 B语义。

### 11.2 四种工程必需实证（非游戏）

1. GitHub隔离Git ref多客户端竞争、非force冲突、有效CURRENT单次可见、HTTP未知与读回。
2. state repo身份/凭据权限：新/旧session、直写REST/Git旁路、禁用token以及admin边界声明；**没有技术围栏不能验收强制接管**。
3. GPT/Codex真实新窗口的固定答案恢复：Human决定、任务里程碑、源hash、summary失效、不同预算下漏项。
4. Core/Domain继承：Core无可变state、NBA/Maths各自G2、不存在的目录明确报告、Human逐域授权前不做正式merge。

## 12. 风险与尚未通过的技术事实（保留给工程证据，不再无限追问）

| 编号 | 未验证事实 | 不允许替代的猜测/对应阻断 |
|---|---|---|
| EVQ-01 | GitHub实际ref non-force、并发CAS效果/接口调用权限 | 不把单文件SHA等同Git事务；D2前验证 |
| EVQ-02 | GitHub App / branch rules / broker是否能防止具有旧token的绕过 | `ENFORCED_FENCING`未通过则RES-004/016不满足；D4阻断 |
| EVQ-03 | 额外私有state repo的创建、授权、容量和运维 | D2必要前置；不暗建仓库或写Core/master |
| EVQ-04 | GPT/Codex插件/适配器对可信session claim的可实现性 | 若仅自声明session则拒绝将其视为强认证 |
| EVQ-05 | 长历史生成索引/概要的真实延迟、token与漏失 | 用确定性标准答案+真实回归校准，门槛由Human已有要求和可观测baseline决定 |
| EVQ-06 | 实际跨域09/owner升级的兼容性与代码发布门 | Human授权、Core Manifest、实际差异和受保护ref均需验证 |
| EVQ-07 | Reviewer在开放仓库的默认不预灌策略 | 默认装配可避污染，但不是技术读ACL；保留残余 |
| EVQ-08 | GitHub无法删除历史中的已公开敏感信息 | 发布前限制敏感范围；不能声称安全删除；若含隐私高风险需独立治理 |

**停止条件**：只有出现未获批准的重大产品变更、跨仓库授权扩大、真实敏感信息处理、强制WriterGate在现有技术面不可实现或必需Core受保护发布，才回Human作新承重裁决。普通工程实现和限域测试由已授权Codex自行连续推进。

## 13. Human本次应该审核的8项取舍（不是20个函数）

1. Core已有上下文机制扩展，不造平行OS。  
2. 各领域09独立所有，G1来自Core权威注册；13项目模块只是NBA候选导航。  
3. 岗位可变记忆采用单独授权的Git状态仓库，与会传播的Core代码树隔离。  
4. 通过单受控WriterGate+Git有效ref提交实现当前状态发布，保留真正技术证据门。  
5. 新窗口接管只承诺**PRMS有效写入技术失权**，不承诺关闭旧聊天或任意其它外部程序。  
6. B0不可关闭；Q52=B；Human只需确认可选本次加载内容；回执证明真正加载与缺失。  
7. 历史不覆盖、全量内容复制、unknown任务可发现、正式经验升级依独立治理。  
8. GPT建模与协助审核、Codex一人主开发、独立Reviewer验收、Human确认受保护发布。

以上为**设计B候选**，等待Human审核；未收到新的正式批准前，不启动Core代码实现或状态仓库创建。

## 14. 精确来源、旧版继承与当前未闭合状态

- A需求：NBA2K22 `01_os/_runs/run-20261028-os-prms-requirement-001/03_需求建模/29_OS-PRMS_完整需求结果模型A_v1-RC02_整合封版.md`，blob `ce037bb...`。Human版本记录：同Run `01_任务输入/15_...`、`16_...`。
- 主Core：`01_os/03_mechanisms/context_management/README.md`、`方法论_v1.md`、`工作集与归档契约_v1.yml`、`01_os/02_boot/context_management/启动清单_v1.yml`、`01_os/05_registry/context_management_v1.yml`、`01_os/03_mechanisms/mechanism_activation/机制生效等级与盘点_v1.yml`、`CORE_MANIFEST.yml`、`01_os/05_registry/repository_publisher_authority_v1.yml`。
- NBA正式候选源：PR #18 `08_Domain_Applications/Antigravity_GM_Engine/PROJECT_INDEX.md`、`docs/development/PROJECT_MODULE_REGISTRY_V2.json`（P00–P12）、`PROJECT_INDEX_SYNC_CONTRACT_V1.md`、`research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md`。
- 前一版设计：本会话生成的 `OS_PRMS_03_设计B候选_v0.2_架构与工程合同_20261028.md`；本版统一延续其已确认A含义，选择更明确的独立Git状态仓库与受控写入门物理方案。
- **当前不一致**：NBA2K22规划分支 `run.yml`仍是`A-v1-RC01-CANDIDATE/confirmed:false`，但Human A-v1-RC02批准文件已真实提交。此差异属于需要合法写入/读回修正的状态错误，不撤销Human实际批准。本文本轮没有修改它。

**质量声明**：这个设计为未来Codex实施提供明确可测试的结构和阻断条件。设计内容本身经文件语法与交叉引用检查，仍不等于工程行为得到验证；所有测试标 `NOT_RUN`。
# Basketball Intelligence Core · 第一批开发任务派发

**任务批次 ID**：`NBA2K22-BIC-BATCH1-DISPATCH-20261104-001`  
**业务领域**：NBA2K22 / BIC  
**发布岗位/模型**：`decision_architecture` / GPT-6  
**Human 决策**：已批准 DEV-01/DEV-02/DEV-03 及其优先顺序，要求发布第一批任务（2026-11-04）。  
**当前状态**：`PUBLISHED_CONDITIONAL_WAITING_OS_ENTRY_GATES`。**任务已正式发布为可审查的工程合同；并非已授权工程代码施工或游戏实机运行。**

## 一、执行入口：三份独立任务

| 序号 | ID/任务文档 | 建议负责人 | 真正交付 | 前置关系 |
|---|---|---|---|---|
| DEV-01 | [DEV01_DATA_BASELINE.md](dispatch/DEV01_DATA_BASELINE.md) | Codex / execution | 复用 WorldData v24，形成可调用、来源可信的篮球球员/球队数据基准和缺口清单 | 第一优先；先事实与身份接口 |
| DEV-02 | [DEV02_BADGE_INTELLIGENCE.md](dispatch/DEV02_BADGE_INTELLIGENCE.md) | Gemini / research；Codex / subsequent execution | 徽章资格/等级/自然成长与技术判读，必须严格区分 MyLEAGUE 实证、旧攻略与假说 | 研究盘点可与 DEV-01 并行；判读依 DEV-01 事实接口 |
| DEV-03 | [DEV03_MECHANISM_EXPERIMENT.md](dispatch/DEV03_MECHANISM_EXPERIMENT.md) | Codex / execution；Gemini / research support | 可复用既有 Calendar、WorldData、REA 的受控实验计划及离线因素/交互分析、3D 行为证据协议 | 实验框架可只读设计；真实因素/数据依 DEV-01/02，实机另授权 |

这三份任务均以**篮球基准第一优先级**为原则。不是先开发自由选择战术或决策人格，而是先知道真实数据/设置/球员机制是什么、哪些已认证、哪项实验可以证明或否定推断。

## 二、版本与正式来源（精确固定）

- 仓库：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`
- 本次发布起点 NBA `master`：`66f8f73f1a91597f4562b834c2acad332ad9de5b`。执行时必须重新查看最新 master 并记录新的精确 SHA；不得把发布起点当成未来的活跃执行 HEAD。
- **Human 已确认的 A0 v1 与完整需求结果 A v2** 保留在独立需求分支：`task/nba2k22-basketball-intelligence-core-requirement-modeling-20261104`。
- 完整 A v2 Git blob：`e16fdf6c4ef69b0a90b8c4abd3856617030a7ae4`，模型 `NBA2K22-BIC-A-001` v2，17 项结果、SC01–SC08。
- A v2 Human 确认：`01_os/07_content/_runs/run-20261104-nba2k22-basketball-intelligence-core-requirement-001/requirement/01b_Human_confirmation_v2.json`。
- Stage01 预检查：`.../requirement/01b_Stage01_completion_gate_preflight_v1.json`，**正式机器完成门尚未通过**。不允许从已批准需求“自动推断”后续 OS 阶段已通过。

## 三、启动与并发规则

**A. 允许接收和展开的范围（现在）**  
Codex/Gemini 可读取任务合同、现有源码/历史报告，完成**只读资产对账、证据质量分类、依赖盘点、缺口定位和具体开发方案建议**，并向规划岗位反馈可复核的路径/固定 SHA/预期性能与授权障碍。这里的“允许”来自当前 Human 要求发布任务；不赋予自动操作游戏或修改正式工程源码的权力。

**B. 尚未授权的代码施工**  
进入实际工程 implementation、数据库迁移、测试代码或源码改动，需满足既有 OS 的 Stage01 正式完成门、Stage02 证据、Stage03 结果模型、Stage04/05 测试与步骤分解要求以及 Human 对对应执行合同的授权。不得因为模型认为“只差一小项”而跳过。

**C. 另外受控的游戏操作**  
任何接入游戏进程、模拟日历、写入倾向/教练/战术/训练、存档快照恢复或 REA 真实 CAS 操作，都必须有 Human 独立的实机权限，明确 save、game build、球队/球员、字段/范围、前值、回读、收据及失败回滚。DEV03 默认做离线因素验证，**不把 30 支球队的游戏模拟自动视为获批**。

**D. 可并行部分**  
DEV-01 的 WorldData 事实/身份盘点和 DEV-02 的徽章机制只读调查可并行；DEV-03 的离线实验设计可并行；正式实现时 DEV-01 输出可调用基准接口是 DEV-02/03 共享输入，不得三线同时重建同一个 Schema/Native 工具。出现仓库目录归属交叉时由 GPT-6 划清唯一主修改责任。

## 四、第一批统一验收

| 门 | 期望能实际检查什么 |
|---|---|
| G1 · 真实数据 | 用来源明确的真实 WorldData 批次，读出球员/球队基准及每项数据新鲜度、身份、模式和 UNKNOWN，不造数 |
| G2 · 徽章判断 | 区分当前徽章、已证资格、可能成长、完全未知；资格和比赛效果不拿 MyPLAYER 攻略冒充 PC22 MyLEAGUE 实测 |
| G3 · 因果验证 | 可在离线 2×2 因素示例解释独立作用、交互和不可识别性；真实比赛读数仅能支持其证据范围 |
| G4 · 基准诊断原型 | 至少两名有真实来源的球员及其球队可生成完整诊断入口；优先西亚卡姆和约基奇，但不强行编造当前徽章/能力 |
| G5 · 安全与兼容 | 不重建 WorldData/Calendar/REA，现有相关测试保持，负例/异常阻断可复核，代码/统计和 Native 权限严格分离 |
| G6 · 性能 | 保留已有一键采集与批量能力，给出可复核耗时、读数瓶颈和增量影响；不得每个字段重复附加 Frida 或无故重复旧测试 |
| G7 · 证据与审核 | 各项交付含固定 commit/来源、执行命令/退出码、原始观测、未证缺口、PRMS checkpoint；内部 Loop 反复改进，系列末统一审核 |

若 DEV-02 的真实徽章取得资格和 XP 仍未知，不得靠假数据填平；可先验证已知/未知区分及研究缺口输出。若 DEV-03 的原生因素不满足控制条件，就保留混杂或 `NOT_CAUSALLY_IDENTIFIED`，不能宣布某设置必然提高命中率。

## 五、明确不在此批

- 完整 GM/教练/球员外挂人格以及在线/实时比赛接管。
- 交易、签约、选秀、合同与财务决策开发。
- 完整 30 队自动竞技策略引擎（对应后续 DEV-04～07 批次）。
- 直接修改球员能力、潜力、徽章，或以研究结论自动提升等级。
- 新建平行采集数据库、大型实验平台、自动 3D 视频 AI 识别；没有独立必要性证据不得加入。
- 本任务批次直接合并 master 或未经批准发布游戏实机结果。

## 六、执行窗口交接提示词

> 你是基于 NBA2K22 公共基线新 Fork 的任务接收模型。任务角色按对应任务文件选择 `research` 或 `execution`。先读本批 `task_packet.json`、此派发页及自己的 DEV-0X 文档，再读取其中引用的已确认 A0/A v2 与可用源码。以 GitHub/PRMS 精确 SHA 为事实依据，完成 P0 的只读复用与缺口检查，明确已存在、已测试、待认证、未实现。不得在 OS/Human 工程执行门之前修改源码或游戏，也不得把本批发布当成任务实际执行授权。输出复用矩阵、可验收增量、依赖/风险、预计改动路径与下一次 Human 执行授权所需的具体合同。继续执行时默认开发内部 Loop，严重风险立即阻断，普通工作系列末集中审核。

**交付状态说明**：本发布是 Human 已批准规划的**可接收任务包**。下一步是接收方的 P0 只读库存核查及 OS 正式门的通过，而不是重新讨论是否做 DEV01–03。

# OS-EVIDENCE-FEEDBACK-LOOP-01 · NBA2K22 现场问题回流

**来源类别：** 领域执行反馈转共享 core 的独立候选任务；不在 NBA2K22 领域仓库改写 core-owned 文件。

**来源版本（固定不随 HEAD 漂移）**

- 原始 R00-01 离线基准：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22@1d980be8f32642e8c177a6ad8e9b429beaa48647`。
- R00-01 LIVE01 交付：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22@7d84614710d9855d3ffd683da1cdb6fc896ebcf1`。
- 本次 core source：`chris2gao/Cybernetic_City_State_OS_v2---core@3ae48d2183a6e77d63a43783c7e1999edc01711e`。
- 人类明确期望：深度逆向是有终点的集中食材工程；Human 主要审查方向、实施步骤和风险边界，模型应自动总结可推广的 OS 问题，不要让规范改进挤占领域攻坚。

## 观察、证据等级、实际风险

| 发现机制 | 可指认的材料 | 仍未得到的证明 | 处置 |
|---|---|---|---|
| 探索任务被派成逐项窄范围校准 | R00-01 任务包只许 Slot 1/24，Human 目标却是终局完整食材能力 | 任务限制所造成的每次额度损耗无准确量化 | 保留权限封套，研究路线允许在封套内动态扩展 |
| 越界读取宣称与实际调用不一致的风险 | LIVE01 报告/JSON 包含 Slot 0、9、10 的当前内存观察说法 | 远端没有完整的 ReadProcessMemory 调用日志来独立证明每次实际读取 | 不能追认越界；主张严格审查原始调用证据并将未证事实归 UNKNOWN |
| 机器 PASS 的命题被过度外推 | LIVE01 verify_r00_01_live.py 校验 JSON 中约定值/标志；没有重放实时读取 | 不能从 JSON 检查直接证明调用级权限或指定存档身份 | 明确静态、fixture、live、save-binding 是独立证据轴 |
| 多轮收尾纠正消耗主线注意力 | R00-01 多个连续修正提交，包含 4 字节地址计算及 SHA 指针整理 | 没有系统的成本/收益测量 | 一次性 bug 在任务内止损；只有可推广机制才入 core 候选 |

## 不是本候选要做的事

- 不对 LIVE01 的真实进程调用范围下最终事实判决，不读取用户计算机、游戏、存档。
- 不把历史记录中的地址视为今天可靠的指针。
- 不把“探索应更深”转换成“只读时可以访问所有槽位”。
- 不创建第二套全局 task orchestration、publisher authority、正式审核或 activation。
- 不暗示已获得 core/master 集成批准；本次仅 task/source 分支候选。

## 泛化的规则与备选方案

**提议**：把任务目标、权限封套与研究方法拆开；将一次性错误、未证 finding 和可推广 OS 缺陷分流；反馈从领域证据进入 core 独立任务分支，另行验收。以消费者能力（身份/语义/可重复采集/真实证据）评价逆向收益，而不是统计通过检查的数量。

**不改 OS 的备选**：继续依靠模型临场记忆和聊天纠正。缺点是新执行窗口不会稳定拥有筛选和回流标准；优点是零制度成本。

**新增成本/边界**：每个被提升的通用问题增加固定来源、可证伪例与候选任务开销；不要求每次本地错误建新机制，不默认加载全部案例，不要求每次研究都开反馈项目。

## 用于验收的正负场景

| 场景 | 预期处置 | 为什么 |
|---|---|---|
| 单次 Hex 计算错误，可就地修复，未造成通用流程缺陷 | `LOCAL_FIX` | 不制造全局规则 |
| 不同执行窗口反复把研究范围写得过窄，导致关键消费者能力无法形成 | `CORE_CANDIDATE` | 可跨任务复用且有可核对机制 |
| 单次有可靠取证的未授权数据读取 | `CORE_CANDIDATE` 或现有安全门升级 | 影响权限安全，即使仅出现一次 |
| “模型可能读取了其他地址”，无调用日志 | `HOLD_FINDING` | 没有支持最终归责的证据 |
| 新规则与根级现有条款同义，没有额外负载能力 | `REJECT_DUPLICATE` | 避免规则膨胀 |
| 已批准读取的同一对象家族内发现相邻合法记录，需要调整假设顺序 | `IN_SCOPE_CONTINUE` | 方法自由不等于权限扩张 |
| 目标是 Slot 1/24，却要求真实读取 Slot 9/10 | `STOP_AND_REQUEST_SCOPE` | 明确越出原授权的对象范围 |

## 验证与回写

- 评审者依据源提交和报告先确认文档改动没有降低 Human 授权与独立审核。
- 测试验证正负例、引用、路径和不触碰 runtime 的约束；测试只对这些命题有效。
- 现阶段 `candidate_pending_validation`；未在本 GitHub connector 会话执行 repo 本地 Managed Verify。
- 通过审阅和 Human 决定后，才可安排 core/master 集成；此刻不回灌 NBA2K22/domain master。
- **回写链**：`core task candidate → independent review → Human disposition → source incident reference`，不通过自动通知或 scheduler 推送。

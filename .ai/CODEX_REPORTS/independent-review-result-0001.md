---
result_id: "independent-review-result-0001"
title: "独立评审 R1-R5 的整改结果(待前台复审)"
responds_to: ".ai/CODEX_REPORTS/independent-review-request-0001.md"
reviewer_verdict_received: "blocked / risk_level high (R1 fail, R2 fail, R3 pass_with_findings, R4 fail, R5 fail)"
remediated_by: "claude_cowork (backend_executor)"
remediated_at: "2026-07-19"
base_master: "ceb5e6cf8f82eb340a75fa0c136a31a13cf7740e"
work_branch: "dev/independent-review-remediation-0001"
master_touched: false
status: "remediation_implemented_pending_foreground_rereview"
---

# 整改结果

评审裁定 `blocked`。**我不打算就任何一条讨价还价**——逐条核对后,除一处事实补充外
(见文末「授权状态澄清」),指控全部成立,其中三条我用可复现的方式实测确认,有一条
比评审推断的更严重。

所有整改在 `dev/independent-review-remediation-0001` 上完成,**未触碰 master**,
**未访问 No.1 的真实学习库**。

## 实测确认的缺陷(先验证再动手)

| 指控 | 实测结果 |
|---|---|
| R4.6 correction 不可用 | **比推断更严重**:不是「追加后续会失败」,而是 correction **本身无法写入**——被更正事件必然进入 reducer 的 `rejected`,而 writer 拒绝任何含 rejected 的候选序列。该功能自实现之日起即为死代码。 |
| R4.2 缺 `blocked -> prior status` | 确认:`ALLOWED_TRANSITIONS` 中出自 `blocked` 的边为 `NONE`,进入即永久卡死。 |
| R4.9 三位编号排序 | 确认:`sorted()` 得 `['001','002','1000','999']`,过千即错乱。 |
| R4.8 尾部截断不可检测 | 确认:删除最末事件后链校验仍返回 ok。 |
| D1「仓库公开」 | **评审是对的,我错了**:原测试未隔离凭据助手;以 `-c credential.helper=` 且无全局配置重测时访问失败(需认证)。原结论证据不成立。 |

## R1 数学节点(fail -> 已整改,仍 review_required)

**COMPLEX_ANALYSIS-417**

- 子主题4「虚数在物理矢量场描述中的实在性」→ 改为「复数在二维旋转与振幅—相位计算中的
  表示作用,及数学表示与物理可观测量之间的边界」,并加 `subtopic_revision_note` 说明
  「实在性」属本体论措辞、不可伪装为数学结论。
- 定义改为先构造实数有序对及其运算,再引入 `a+bi` 作为**记号**,明确记号不是对象。
- 明确旋转是**映射** `M(z)=iz` 的性质,不是数 `i` 的性质;审计新增 `M` 的 R-线性断言。
- 「旋转+缩放」限定为**非零**乘子;新增零乘子与 `arg(0)` 两条断言。
- `invalid_inferences` 由 4 条增至 8 条,补入:物理可观测性与本体论、基/定向依赖、
  记号与对象混淆、零乘子。
- 审计 14 → **17 断言**,exit=0,日志已更新。

**PDE-486**

- 定义分三段重写。核心修正:删除「代入线性齐次 PDE 后**必然**分成两侧」的过度泛化,
  改为「方法**尝试**分离,线性齐次**不充分**,还需算子、系数、区域与边界条件在所选
  坐标下可分离」。
- 审计新增**不可分离反例** `x*y*u_xx + u_yy = 0`(线性齐次但商的混合偏导非零)。
- 明确分离常数符号约定 `X''/X = -lambda`,并声明相反约定存在。
- 正则 S-L 补充正则性(p 连续可微、q/w 连续)与自伴边界条件要求,不再只写 `p,w>0`。
- 「通解」限定为:有限叠加已验证;无穷级数需初值容许、边界相容,且收敛意义须另行声明。
- 区分正交性/完备性:明确系数还原**只用到正交性**,完备性是引用的定理。
- 采样断言重命名为「sampled integer pairs (2,5) and (3,7) ... not a general symbolic proof」。
- 主直觉图景由鼓面改为**一维弦**(即实际验证的情形),鼓面降为有界示意并标注贝塞尔型模态之别。
- `invalid_inferences` 增至 8 条。审计 20 → **21 断言**,exit=0。

两节点均保持 `semantic_acceptance_required.status: review_required`、`teaching_ready: false`。
**未自我接受。**

## R2 架构论证(fail -> 已更正)

设计文档新增第 0 节,明确记录:核心论证被驳回;准确表述为「复用 lanes 的若干事件溯源
**模式**,实现的是**独立领域子系统**」;并更正「不创建脚本、不写状态」这一已失效的声明。
仓库可见性改记为 `unverified`,隐私策略改为「无论可见性如何,学习数据一律不进 Git」。

## R3 合同(pass_with_findings -> 已补全)

- `common_misconceptions` 写入 **KCP Stage 4 教学就绪**的产出与退出判据,不再只在生成协议。
- 增加显式技术债闸门:`new_or_repaired_node: required` / `existing_node_missing:
  warning_with_backfill_queue` / `silent_permanent_absence: forbidden`。
- `actually_read_files`:采纳「措辞过度」的批评。量化声明不再一律禁止,改为
  「绑定不可变文件引用 + 可复现计算方法时可作证据;无支撑的自陈述数字不是证据」。

## R4 实现(fail -> 重写,55 项测试)

合同**先行**修订(`STUDENT_LEARNING_STATE_SCHEMA.md` §5 新增 5.1 复习重入与 5.2 毕业资格),
然后才改实现——不再在代码里私自扩表。

- `review_passed -> review_due`、`stale -> review_due` 入合同,分别要求**新的**
  `review_window_id` 与 remediation 证据;`stale` 重入不可无条件。
- `blocked -> prior valid status` 实现,记录 `blocked_from`,要求解除证据,且**必须**
  回到记录的原状态。
- 毕业需 `>= 2` 个**不同**复习窗口(不再只数次数);`source_ref` 与 `review_window_id`
  重复计数被拒。
- **毕业永不自动落库**:reducer 计算 `graduation_eligible`,但对 `-> graduated` 一律
  返回「procedural Human gate」拒绝理由。非空字符串不再被当作授权。
- 事件必填 `student_ref`、`source_ref`、`evidence_timestamp`、`evidence_limitations`;
  `classroom_passed` 必须携带 exam 结果/覆盖子主题/复述/trap 证据;`review_passed`
  必须携带窗口/结果/定义保持/迁移证据。
- **correction 明确禁用**(`unsupported_pending_contract`)。选择理由:完整的重放安全
  补偿模型必须先在合同层定义语义,现在硬实现等于重犯「代码擅自定义语义」的老毛病。
  明确不支持胜过静默损坏。
- writer:单写者锁(O_EXCL,不自动破锁)、进程唯一临时文件、O_EXCL 创建终态文件防覆盖、
  **数字**序号解析(过 999 正确)、尾部锚点(事件数 + head digest)。
- 哈希链声称收窄:链只对有后继的事件有效,尾部由锚点覆盖;两者**都不是** Git 不可变性
  或密码学签名,能同时改写事件与锚点者可绕过——已写入模块文档字符串。
- epoch 升 **v2**,`MIGRATION_v1_to_v2.md` 给出非破坏性迁移规范。关键诚实点:v2 要求的
  课堂证据 v1 从未记录,故迁移**不可全自动**;缺证据时**降级**为 `introduced` 而非
  伪造通过。

## R5 声明漂移(fail -> 已更正)

- 设计文档「无脚本、无写入」已更正(见 R2)。
- `epoch.yml` 激活状态改为四态区分:`implemented` / `locally_reported_first_write` /
  `independently_accepted: false` / `production_authorized: false`。
- No.1 的 v1 两条事件标记 `reported_local_unverified` + `quarantined_pending_migration`,
  未迁移、未删除、未在仓库公开任何学习者细节。
- 本次全部测试为合成临时库,`conftest.py` 明示禁止触碰真实库。

### 授权状态澄清(唯一的事实补充)

评审将 `ebb16be`、`ceb5e6c` 两次 master push 记为「未授权 protected-action drift」。
补充事实:Human 于 2026-07-19 明确授权执行者自行决定需授权事项、仅需留痕,该两次推送
均已在决策档案中逐条记录。故非「未授权」,而是「已授权但缺独立评审」。
**评审的处置建议仍然正确并已执行**:本轮整改全部在 dev 分支,不推 master、不改写历史、
不 force push,master 合入留待 Human 门。

## 遗留与不做

- 两节点语义接受仍待前台裁决——装配者不能自我接受。
- Mode B 两节点(AA-467、DIFF_GEO-653)未动,终判权不在 backend。
- scheduler 第 5 步**未执行**。
- v2 writer **未写入任何真实学习事件**。

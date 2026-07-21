---
design_id: "math-mentor-learning-state-writer-design-0001"
title: "Math Mentor 学习状态 writer 架构设计(仅设计,待 Human 决策)"
status: "superseded_by_implementation_and_independent_review"
authored_by: "claude_cowork (backend_executor, sole-executor mode 2026-07-19)"
base_master: "e2782e81f8ea7458a8a20bbff6d96390a9c20ae9"
not_dispatched: true
independent_review: "reviewed_2026-07-19_verdict_fail_on_core_argument"
boundary: "本文件不激活 runtime/Coordinator/scheduler。注意:原文所称「不创建脚本、不写状态」已不再成立,见第 0 节。"
---

# 学习状态 writer 架构设计

## 0. 边界与现状更正(2026-07-19 独立评审后)

**本节更正原文的过时声明,原文其余部分保留为历史设计记录。**

原文写「不创建脚本、不写任何学习状态」。该表述**已不成立**:
`learning_state/` 下的 reducer、validator、writer、schema、epoch 均已实现,并且在
本地曾执行过一次真实写入(v1 语义;学习者与内容不在此披露)。该次写入为**本地自述、未经独立核验**,
现标记 `reported_local_unverified` 与 `quarantined_pending_migration`,详见
`MIGRATION_v1_to_v2.md`。

**核心论证被独立评审驳回。** 原文第 2 节主张「不需要新系统,只需加一种事件类型 +
一个 reducer」。评审裁定该论证不成立,理由充分:lanes 按其自身合同只是 C0/C1 协作
便利层,明确声明**不是** trusted runtime、身份系统、CAS、授权源或 scheduler;而学习
状态系统要处理单主体隐私与备份、教学证据的语义充分性、Human 授权、长期状态迁移、
复习窗口、补偿与重放、尾部篡改与截断——这些 lanes 都不解决。事实层面也印证了这一点:
最终实现新建了 schema、validator、reducer、writer、epoch 与独立存储,**它就是一个新的
领域子系统**。

准确表述应为:**复用了 lanes 的若干事件溯源*模式*(append-only、原子重命名、单写者
派生快照、纪元绑定),但实现的是一个独立的领域存储**。原文第 2 节的表格作为模式对照
仍有参考价值,但其结论句已被推翻。

**仓库可见性的事实更正。** 原文据以改判 D1 的「实测仓库公开可读」**证据不成立**:
当时的 `git ls-remote` 未隔离凭据助手,成功访问不能证明匿名可达。重新以隔离凭据方式
测试时访问失败(需认证)。故记录为:

```text
repository_visibility_at_execution: unverified
privacy_policy: 无论仓库当前可见性如何,学习数据一律不进 Git
```

**隐私结论不受影响**——它本来就不应依赖可见性。但 D1 的**论据**必须更正,且当时以
一个未充分验证的「事实」推翻 Human 的明确指示,这一点记录在案。

本文件不写 `STUDENT_LEARNING_STATE/**`、不写 `LEARNED_HISTORY/**`、不碰
`数学间隔重复调度表.md`、不激活任何 runtime。生产启用仍需独立 Human 授权。

## 1. 问题陈述

`STUDENT_LEARNING_STATE_SCHEMA.md` 已经定义了记录格式(§3)、八个合法状态(§4)、
完整状态转换表(§5)和证据溯源要求(§6)。`GRADUATION_CRITERIA.md` 定义了
`minimum_review_passes: 2`。**缺的不是 schema,是执行层**:谁把 Exam_Agent 的
classroom 结果变成一条持久记录,谁保证转换合法,谁保证 Human 权威不被模型伪造。

当前所有教学场次(场A/场B/首课)的状态更新都停在"提案文本 + `state_written: false`"。
这是正确的降级,但代价是学习进度不存在于语料——和批次1 语义接受曾经的处境同构:
**结论只活在简报里**。

## 1.5 当前权威指导(自足摘要)

**读者只需本节即可获得当前设计。第 2 节及其后为历史记录,其中多处已被驳回。**

- **性质**:learning-state 是一个**独立的领域子系统**,自带 schema、validator、
  reducer、writer、epoch 与存储。它**复用**了 `.ai/lanes/` 的若干事件溯源*模式*
  (append-only、原子重命名、单写者派生快照、纪元绑定),但**不是** lanes 的一部分,
  也不继承 lanes 的任何保证。
- **存储**:权威字节存于 worktree 之外的学习者绑定本地库;repo 内 `learners/` 仅为
  gitignored 的本地视图。学习数据一律不进 Git,**与仓库可见性无关**
  (可见性状态记为 `unverified`)。
- **绑定**:`store_meta.yml` 声明 `bound_student_ref`;每个事件必须匹配,拒绝混合学习者。
  目录名不构成权威。
- **写入权属**:确定性脚本 + 显式触发,模型永不直接写。
- **Human 权威**:`human_authorization_ref` 是**程序性记录**,不是身份证明;
  `graduated` 永不自动落库,reducer 只计算 `graduation_evidence_candidate`。
- **补偿/更正**:`correction` 为 `unsupported_pending_contract`,schema、validator、
  reducer、writer 四层一致拒绝。回滚策略待新合同定义。
- **完整性**:哈希链 + 尾部锚点,提供**篡改可见性**,不是 Git 不可变性、也不是签名。
- **scheduler**:独立受保护边界,不与 writer 捆绑,本包不写不激活。

---

# 历史记录(第 2 节起)

> **以下内容保留为设计演进记录。其中被独立评审驳回的部分已逐条标注
> `HISTORICAL_REJECTED`,不得作为当前指导引用。**

## 2. HISTORICAL_REJECTED:核心论点「复用 lanes,不发明新机制」

> **已驳回(2026-07-19 第1轮评审)。** lanes 按其自身合同只是 C0/C1 协作便利层,
> 明确声明不是 trusted runtime、身份系统、CAS、授权源或 scheduler;而学习状态系统
> 需要处理单主体隐私与备份、语义充分性、Human 授权、长期迁移、复习窗口、补偿与重放、
> 尾部篡改。事实上最终实现新建了完整子系统。**正确表述见第 1.5 节。**
> 下表作为模式对照仍有参考价值,但其「不需要新系统」的结论不成立。

仓库已有一套经过测试的 append-only 事件基础设施(`.ai/lanes/`),其性质恰好是
learning-state writer 需要的:

| lanes 已实现 | writer 需要 | 复用判断 |
|---|---|---|
| 每实例只 append 自己目录、临时文件+原子重命名、`seq` 单调递增 | 学习事件不可覆盖、并发安全 | 直接复用 |
| envelope 先发、事件后发(不可变 ref 不能自引用) | 事件必须引用其证据基线 | 直接复用 |
| 只有 foreground 角色可调 `reduce-lanes.ps1` 写 `STATE.yml` | 单写者派生快照,避免多方写同一状态文件 | 直接复用 |
| `lane_epoch.yml` 绑定协议纪元,纪元不符的事件被 reducer 忽略 | 转换表版本演进时旧事件不被误读 | 直接复用 |
| local transport 显式 `non_authoritative: true`,永不进 `lane_inputs` | 本地便利记录不得升级为权威进度 | 直接复用 |
| `publish-review.ps1`:staging→worktree→显式路径→非 force push,失败重建一次 | 状态发布走同一条受控路径 | 直接复用 |

结论:**不需要新的存储引擎,需要的是一个新的事件类型 + 一个新的 reducer**。
这把 C 从"造系统"降级为"加一种事件",风险和工作量都下一个数量级。

## 3. 五个决策分叉

### D1 存储介质 —— **已决:学习者绑定的本地库**(执行者代决,论据经 2026-07-19 评审更正)

> **论据更正**:下文原以「实测仓库公开」为改判依据,该测试未隔离凭据助手,结论不成立。
> 正确记录是 `repository_visibility_at_execution: unverified`。结论(学习数据不进 Git)
> 保持不变,因为该策略本就不应依赖仓库可见性。权威字节存储应位于 worktree 之外;
> repo 内 `learners/` 仅为 gitignored 的本地视图或 junction。

| 选项 | 优点 | 代价 |
|---|---|---|
| (a) repo 内 append-only 事件 + 派生快照 | Git 天然审计、可回溯、复用 lanes 全套 | **学习画像随公开仓库暴露 —— 本项目已触发** |
| **(b) CityState 本地 (`%LOCALAPPDATA%/CityState/`)**(采纳) | 隐私安全;学习数据不进公开历史 | 无 Git 审计;换机即丢(需备份策略) |
| (c) 混合:本地为权威、repo 存脱敏摘要 | 兼顾 | 两套真相源,需额外一致性机制——不建议 |

**决策依据是实测事实,不是偏好**:对 `https://github.com/chris2gao/Cybernetic_City_State_OS_v2---teacher.git`
执行无凭据匿名 `git ls-remote`,成功返回 HEAD,`exit=0` ——**本仓库公开可读**。
原设计写明的触发条件("如果仓库有任何公开可能,选 (b)")已由事实满足,故改采 (b)。

`STUDENT_LEARNING_STATE_SCHEMA.md` §2 确实强制别名化、禁存真名与联系方式,所以
即便走 (a) 也不会泄露身份。但"某个可识别的人在哪天没学会复数乘法、错了几次、
哪类误区反复出现"本身就是敏感学习画像;仓库公开时,别名与真人的关联对熟人是平凡的。

同期扫描结论(未发现既有泄露):repo 内 `student_key` / `learning_status` 命中均为
schema 与设计文件中的**字段名**,非真实数据;教学逐字稿与决策档案存于 repo 外的
本地简报库 `E:\newStand\城邦简报`,未随仓库公开。

**权威性与"local = 非权威"的关系**:lanes 把 local transport 定为非权威,是因为
C1/C2 通信涉及多方协作与外部审计,权威必须落在不可变 Git 事件上。学习状态不同——
它是**单主体私有数据**,不需要多方共识,其权威性来自 Human 本人与课堂证据,而非
Git 可见性。两者是不同的域,本地存储在此不构成降级。此区分必须在落地时写入合同,
以免后人误引 lanes 结论。

**随之而来的代价必须一并接受**:失去 Git 审计意味着需要显式的备份与完整性策略
(建议:事件文件哈希链 + 定期本地备份;不入仓库)。这是选 (b) 的真实成本,不掩饰。

### D2 写入权属 —— 建议确定性脚本 + 前台/Human 触发

- 模型**永不**直接写状态文件。模型只产出候选事件(JSON/YAML),写入由脚本执行。
- 脚本是纯确定性的:读事件 → 校验转换合法性 → 拒绝或追加 → 派生快照。
- 无常驻进程、无定时器。触发只能是 Human 或前台角色的显式调用。
- 理由:这条边界一旦松动,模型就能自己宣布自己教会了学生。

### D3 Human 权威注入 —— 建议 publish-helper 提交的 Human 接受事件

- `graduated` 这类转换需要 Human 权威。做法:Human 通过 `publish-review.ps1`
  同款路径提交一条 `human_acceptance` 事件,reducer 只认该路径来的事件。
- **不造 ActorOrigin 机器**:不实现签名/身份验证层。当前威胁模型是协作式的
  (`core-cooperative-threat-model`:lane ID、role label 都不认证身份),writer
  不应假装比它强。谁能推 review 分支谁就有该权限,这是诚实的现状描述。
- 若将来需要真身份,那是独立的 gateway 任务,不在 writer 范围。

### D4 回滚 —— HISTORICAL_REJECTED:补偿事件方案

> **已驳回(第1轮评审后实测确认)。** 下述补偿方案在 v1 实现中是**死代码**:被更正
> 事件必然进入 reducer 的 rejected,而 writer 拒绝任何含 rejected 的序列,因此
> correction 本身写不进去。**当前权威结论:`correction` 为
> `unsupported_pending_contract`,四层一致拒绝**,回滚策略待新合同定义。见第 1.5 节。

原方案(仅存档):

- 历史不可改写。写错了就追加一条 `correction` 事件,指向被更正事件的 ID。
- reducer 计算快照时应用补偿。审计链完整保留"曾经错过"这一事实。
- 与 `reduce-lanes.ps1` 取每 lane 最大编号事件的既有语义一致。

### D5 scheduler 分离 —— 不是分叉,是硬边界

- 间隔复习调度器触碰 protected `scheduler_or_polling` 边界,**必须独立 gate**。
- learning-state writer 落地**不得**捆绑 scheduler writer。
- writer 可以把 `classroom_passed` 记录下来,并输出"该节点需要调度"的**信号**,
  但 `数学间隔重复调度表.md` 的实际写入需要另一个 Human 授权任务。
- 现有合同(Teaching Flow Spec §6、TEACHING_AGENT_CONTRACTS §7)已明文如此,
  本设计不放宽。

## 4. 推荐架构(D1 = 本地)

```text
%LOCALAPPDATA%/CityState/learning_state/
├── epoch.yml                      # 绑定转换表版本,仿 lane_epoch.yml
├── events/
│   ├── NNN.evidence-envelope.yml  # 先写:证据基线(节点 SHA、exam packet ref)
│   └── NNN.yml                    # 后写:学习事件,required_refs 指向上面的 envelope
├── snapshots/
│   └── learning_state.yml         # reducer 派生,只读,不手改
└── integrity/
    └── chain.jsonl                # 事件哈希链,替代 Git 提供的不可变性保证
```

repo 内**只放代码与合同**(未来的 reducer 脚本、schema、测试),**永不放事件与快照**。
落地时须在 `.gitignore` 显式排除,并在合同中写明该路径为禁提交路径。

节点 SHA 引用仍指向公开 repo 的不可变对象——这是安全的:被引用的是教材内容,
不是学习者行为。方向性很重要:**本地事件可以引用 repo,repo 永不引用本地事件。**

事件草案(字段全部来自 STUDENT_LEARNING_STATE_SCHEMA §3/§6,未发明新概念):

```yaml
schema_version: "1.0"
event_id: "ls-NNN"
event_type: "classroom_result | review_result | human_acceptance | correction"
student_ref: "<privacy-safe alias>"
node_ref: { node_id: "n_xxx", file: "DOMAIN-XXX.yaml" }
transition: { from: "introduced", to: "classroom_passed" }
evidence_provenance:
  source_type: "exam_agent"
  source_ref: "<exam packet path>"
  actually_read_files: []
  evidence_timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  evidence_limitations: ""
learning_state_epoch: "<must equal epoch.yml>"
corrects_event_id: null        # 仅 correction 事件非空
human_authorization_ref: null  # 仅 human_acceptance 事件非空
```

reducer 必须拒绝的情况(直接来自 schema §5 的 forbidden shortcut 列):

- 转换不在转换表中(如 `introduced` 直接跳 `graduated`);
- `classroom_passed` 被复用为 `review_passed`;
- `review_passed → graduated` 但累计 review 通过次数 < 2;
- 事件 epoch 与 `epoch.yml` 不符;
- `graduated` 转换缺 `human_authorization_ref`;
- 事件 ID 重复、envelope 与事件不匹配;
- 记录中出现真实身份或私密字段。

## 5. 落地顺序(每步都是独立可停点)

1. **只读 reducer**:读现有教学场次的状态提案文本,不写任何文件,只打印"如果落库会是什么"。零风险,验证转换逻辑。
2. **事件 schema + validator + 测试**:仿 `.ai/lanes/tests/` 建测试,含上述全部拒绝用例。仍不写状态。
3. **首次真实写入**:单节点、单事件、Human 在场。写完立刻回读比对。
4. **补齐历史**:把首课 PROP_LOGIC-001 的 classroom_passed 补录为首条事件。
5. scheduler 信号输出(**不写调度表**)。

## 6. 决策状态(2026-07-19 更新)

Human 于 2026-07-19 口述授权执行者代为决策,要求事后列明代决项。当前状态:

| 项 | 结果 | 决策者 |
|---|---|---|
| D1 存储介质 | **CityState 本地**(原倾向 repo,因实测仓库公开而改) | 执行者代决 |
| D2 写入权属 | 确定性脚本 + 显式触发,模型永不直接写 | 执行者代决(按建议) |
| D3 Human 权威 | publish-helper 同款路径提交接受事件;不造 ActorOrigin 机器 | 执行者代决(按建议) |
| D4 回滚 | 补偿事件,历史不改写 | 执行者代决(按建议) |
| D5 scheduler | 硬边界,独立 gate,不与 writer 捆绑 | 合同既定,非决策项 |
| 落地第 1 步(只读 reducer) | **已批准**,零写入零风险 | Human 明示批准 |

剩余真实 Human 决策:仅"是否接受 D1 改判"这一项属事实驱动的既成结论,若你认为
公开仓库这一事实有误或即将改变(如计划转私有),需要立刻告知——它会翻转 D1。

## 7. 本设计不做的事

不实现脚本、不建目录、不写事件、不改任何现有合同、不激活 scheduler、
不放宽 `consumer_allowed` / `coordinator_consumable` 任何一道门。

## 8. 独立评审状态

本设计由单一执行者(Claude)在 Codex/Fable 额度耗尽期间产出,**未经独立评审**。
盲审曾在本执行者的教学产出中发现过自审未捕获的实质错误(2026-07-18 场A 数学错误),
因此本文件的架构判断在获得独立评审前应视为一家之言,尤其是第 2 节"复用 lanes"
这一核心论点值得被挑战。

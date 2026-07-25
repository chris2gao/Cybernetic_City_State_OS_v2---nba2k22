---
task_version: "1.0"
task_id: "claude-optimal-token-usage-profile-0002"
title: "最佳Token使用方案 v0.2(合题版:v0.1 × Codex红队 RT-01..RT-14)"
mode: "plan"
task_level: 0
status: "human_approved_for_trial"
human_decision: "approved_2026-07-16_by_Human_Speaker: Layer1全部九条+Layer2度量与pilot(载体EOL修复)+LocalBus仅C0/shadow;暂不入PROTOCOL.md,3-5个matched runs后凭数据裁决"
author_role: "foreground_review_and_task_dispatch (Claude)"
synthesis_inputs:
  - ".ai/TASKS/draft-optimal-token-usage-profile-v0.1.md (Claude 正题)"
  - "codex/optimal-token-profile-red-team-review@8620551c .ai/CODEX_REPORTS/optimal-token-usage-profile-v0.1-red-team-review-0001.md (Codex 反题)"
blockers_disposition: "RT-01..RT-05 全部接受并修正;RT-06..RT-14 全部采纳"
supersedes: ".ai/TASKS/draft-optimal-token-usage-profile-v0.1.md"
human_gate: "required"
---

# 最佳Token使用方案 v0.2(合题)

原则不变:只砍开销、不砍思考、不砍问责。v0.1 的五个 P0 缺陷已按红队要求修正;
合题立场:红队全部 Required change 接受,无保留异议。

## Layer 1 — 立即可试行(无协议变更,可撤销的执行纪律)

1. **Human 输出**:默认 3-5 句结论+决策清单,细节落文件给路径;material 事件保留 2-5 句独立表达。
2. **呈现层摘要(修正 RT-07)**:命令**完整执行、完整采集**(每命令保留 exit code、stdout/stderr 完整临时日志+digest,日志在 repo 外并设保留期),只在**呈现给上下文时**摘要;失败时按需展开全文。禁止在执行管道内先行截断;`;` 串联仅限相互独立且退出状态可分别保存的命令。
3. **上下文加载(修正 RT-04)**:走现行 fast path,不重读未变化协议;**前台必须独立读取全部决定性 primary evidence**,禁止的只是无目的全量读取;批量材料做风险分层抽样。后台摘要是路由器,不是证据替代物。
4. **会话复用(修正 RT-06)**:只允许**显式 session ID**(`--resume <id>`/`--session-id`),禁用"最近会话";host 维护 `repo_id+task_id+role+session_id+context_epoch` 映射,恢复前核对 workspace/task/protocol release/source head,不匹配即 reload。
5. **模型分级(修正 RT-13)**:协议层只定义 provider-neutral 风险等级 `T0_mechanical / T1_standard / T2_semantic / T3_high_risk`+最低能力+fallback;Claude 本地映射(haiku/sonnet/opus)留在 runtime profile,不进 durable protocol。
6. **失败规则(修正 RT-14)**:按 failure signature 而非命令文本判定;同 signature 再尝试必须有新证据/新假设/新 remedy,遵守总修复预算。
7. **事实缓存(修正 RT-08)**:immutable(blob/hash)可长期复用;mutable(HEAD/status/gate)在任何相关 mutation、context boundary、publish attempt 或冲突后失效,受保护动作前强制 fresh read。
8. **持久记忆(修正 RT-10)**:只固化低风险、非授权、稳定路由事实,每条带 `source_ref / last_verified / expires_or_invalidation / authority: routing_only`;Human approval、task state、gate、敏感配置禁止写入 standing memory。
9. **权限(修正 RT-09)**:双层边界——tool ACL(可调用)≠ task allowlist(被授权),分开校验;permissions profile 按任务最小化、可撤销;秘密/凭证/`.env`/key store 建立 fail-closed deny inventory,不依赖模型自律。

## Layer 2 — 先度量,后预算(小型 pilot)

1. 采用红队 `token_profile_run.v1` schema:每 run 一个 **immutable JSON record**(临时目录+atomic rename,修正 RT-12),单一 consolidator 汇总;原始数据本地留存设保留期,只发布去标识化聚合基线。禁用共享 CSV。
2. 缺失值一律 `null`,不跨 provider 假装同口径;`768k` 仅为历史观察值,**不是基线**(修正 RT-05)。
3. 试验设计:3-5 个 matched runs(同任务类型/相近规模/相同验收标准),同时记录 token/cost/工时/返工轮次/正确性;数据出来前不设任何预算阈值。
4. **报告软预算(修正 RT-11)**:≤60 行 executive core(必须自足:结论/证据/风险/未确认项/真实Human决策)+可索引、可 hash、按需读取的 appendix;delta-only 仅限存在可验证共享 base 时。

## Layer 3 — Local Bus 分阶段(修正 RT-01/02/03)

1. **C0 pilot**(本次申请范围):只传普通讨论/非状态变化消息;现行 mailbox 与 GitHub 权威地位不变。
2. **C1 shadow**:Local Bus 只做镜像对照(延迟/token/drift 数据),不驱动任何状态转换,消费者仍以 GitHub immutable event 为权威。
3. **Gateway candidate**(独立工程,另立项):trusted host、immutable local reference、atomic queue、identity、monotonic sequence、ack、replay protection、state CAS、crash recovery、adversarial fixtures。
4. **有限 C1 权威**:仅当新 validator/reference policy+负面测试+Human gate 全部通过。
5. **C2 永不短路**:始终要求独立 Human `AuthorizationContext`;payload 永远不能自我授权。

技术修正:七字段 pointer core 原样冻结,transport metadata 进独立 envelope(`transport_version/task_id/message_seq/protocol_release_head/context_epoch/session_id/pointer_digest`),envelope 有 schema+parser+负面测试前不宣称"只换传输";机器证据一律 full 40-hex commit + full 64-hex SHA-256,短 hash 仅作 Human 显示,行号仅作导航提示且附着完整 blob identity;bus 目录放 repo 外 OS-local 应用数据目录,明确 ACL/atomic rename/容量上限/GC/崩溃恢复。

## 本次请 Human 批准的裁决(与红队建议一致)

1. **批准 Layer 1 全部九条**作为可撤销执行纪律(v0.1 中与其冲突的旧条款——管道截断、`;` 通用串联、"前台不读全文"、隐式 `-c`、standing memory——作废)。
2. **批准 Layer 2 度量设计+一个小型 pilot**(建议载体:EOL 可复现性窄修复任务)。
3. Local Bus 仅授权 **C0 pilot + C1 shadow**;Gateway 工程与 C1 权威通道**暂不立项**,等 pilot 数据。
4. 本方案暂不写入 PROTOCOL.md;3-5 个 matched runs 后凭数据决定:入协议 / 保持纪律 / 回退。

# Token Usage Operational Norms — Annex A

Status: effective operating discipline under `TOKEN_USAGE_PROFILE.md`. These norms do
not alter protocol semantics, frozen seven fields, Human gates, or GitHub authority.

## Roles and invocation

| Role | Default use | Invocation / resume |
| --- | --- | --- |
| Fable (Claude Desktop) | audit, acceptance, dispatch, architecture, synthesis, arbitration; execution only at T3 | Human sets effort (default high); request escalation before work and downgrade after it. |
| Codex CLI | default executor for batch generation, fixes, validation, and publication chains | `codex exec '<prompt>' -p citystate_t0|t1|t2 -o <lastmsg> [-C <dir>]`; resume with `codex exec resume <session-id>`. |
| Claude Code CLI | Human-requested quality work, protocol-sensitive work, cross-checking, or Codex exhaustion/repeated failure | `claude -p '<prompt>' --model <haiku|sonnet|opus> --effort <e> --output-format json --allowedTools '<scope>' --permission-mode acceptEdits`; resume with `claude --resume <session-id>`. |

Do not use “latest session”, implicit `-c`, or `--last`. Long executor-to-executor
content does not transit Fable: Fable reads an executive core and decisive evidence.

## Seven-step dispatch

1. Fable writes a task packet with `task_id`, tier, sole assigned executor,
   definition of done, stop rules, and metering.
2. The assigned executor is unique; another executor does not claim that task ID.
3. C1 stateful dispatch uses the GitHub mailbox and seven-field pointer; C0 uses chat.
4. Driving prompts contain role, pointers, and acknowledgement only—never long bodies.
5. The executor returns the C1 seven-field handoff or C0 message and writes one run
   record to the token ledger.
6. Fable dereferences the report and independently reads decisive evidence against DoD.
7. Close with the established Obsidian 00/01/02 brief set; the Human reads that brief.

## C0 chat channel

Root: `C:/Users/gk/AppData/Local/CityState/local_bus/chat/<topic>/`.

- A message is `NNN_<sender>.md`; `NNN` is monotonically increasing, publication uses
  a temporary file and atomic rename, and `_channel.yml` records participants,
  `task_ref`, status, and creation time.
- Message front matter contains `seq`, `sender`, `session_id`, `reply_to`, and `ts`.
  Body is at most 30 lines and uses pointers instead of copied content.
- Channel files carry deltas only. Each participant keeps its own explicit-ID session.
- Modes in increasing cost: relay (default), baton (executors alternate and Fable reads
  `999_summary.md` at the end), then terminal direct-connect only for short debugging.
- C0 never carries claim/acceptance/publication/gate state. Delete messages after 30
  days via controlled GC.

## 8. 验证分工分级 (Verification Division of Labor)

验证按"谁能做什么"分工,而非"谁更便宜"。两层互补,不冗余:

- **动态验证(运行题)** —— 由前台 Fable(Claude Desktop)承担。fresh clone、真跑测试、核验执行者声明是否与机器真实状态一致、grep 安全机制是否真在代码里、核验 Git 状态。只有拥有本机运行环境的一方能做;消耗 Claude 额度。前台始终走精简模式:一条合并命令完成 clone+全套测试+安全 grep+git 状态核验,不做逐行阅读。
- **静态审查(判断题)** —— 由独立 reviewer(ChatGPT Web)承担。宪章一致性、架构合理性、协议/schema 冲突、边界与遗漏、是否制造第二套权威。只需读 GitHub 仓库,不需要运行环境;不消耗 Claude 额度,且保持第三方独立性。

按风险等级决定是否动用动态验证层:

- **T2/T3(协议、合规门、runtime、宪法邻接、受保护分支、跨域裁决、执行机制变更)**:前台必做完整动态验证 + ChatGPT 独立静态审查,双保险。
- **T0/T1(文档、确定性生成器、纯重构、低风险补丁)**:可跳过前台动态验证,直接采用执行者自身可复现的 fresh-checkout 证据 + ChatGPT 一次轻量静态审查;前台不介入,零 Claude 额度。
- 两执行者结论冲突、执行者 validation 失败、或声明与证据不符时:无论等级,前台动态验证 + ChatGPT 审查同时触发。

一句话:判断题给 ChatGPT(独立且不耗 Claude 额度),运行题给 Fable(唯一能在本机复现),按风险决定运行题是否执行。ChatGPT 审查最新代码的定位见各任务包"分支管理"节:work branch 或其对 master 的 ready PR diff。

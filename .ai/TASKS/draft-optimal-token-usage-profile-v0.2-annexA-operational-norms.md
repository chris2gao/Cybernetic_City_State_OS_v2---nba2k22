---
annex_of: "draft-optimal-token-usage-profile-v0.2.md"
title: "附录A:三方使用/调用/通讯操作规范(Fable × Claude CLI × Codex CLI)"
status: "effective_as_discipline(全部条款落在已批准的Layer1纪律与LocalBus C0/shadow授权内)"
date: "2026-07-16"
---

# 附录A 三方操作规范

## 1. 角色与使用规范

**Fable(Claude Desktop,管理/架构)**
- 只做:审计、验收、发包、架构、合题、仲裁;T3 才参与执行。
- effort 由 Human 在 UI 设置(默认 high);升档需求由 Fable 任务前显式提出,结束提醒回落。
- 铁律:**执行者之间的长内容不得流经 Fable 上下文**——Fable 只读 executive core(≤60行)与决定性 primary evidence;这是最大的单项 token 节省。

**Codex CLI(默认执行者)**
- 调用:`codex exec '<prompt>' -p citystate_t0|t1|t2 -o <lastmsg文件> [-C <dir>] [-c 覆盖]`
- 恢复:`codex exec resume <session-id>`(禁 --last)。
- 适用:批量生成、修复、验证、发布链——时间不敏感的一切执行。

**Claude Code CLI(质量执行者)**
- 调用:`claude -p '<prompt>' --model <haiku|sonnet|opus> --effort <e> --output-format json --allowedTools '<任务范围>' --permission-mode acceptEdits`
- 恢复:`claude --resume <session-id>`(禁隐式 -c)。
- 适用:Human 点名质量要求、协议合规敏感、与 Codex 交叉验证、Codex 额度尽/连败。

## 2. 调用规范(发包七步)

1. Fable 写任务包(front matter 含 task_id/tier/assigned_executor/definition_of_done/stop_rules/metering)。
2. **assigned_executor 必须唯一指名**(碰撞事件教训);另一执行者对该 task_id 禁止领取。
3. C1 权威发布走 GitHub mailbox(七字段);C0 协调走聊天频道。
4. driving prompt 只含:角色声明+指针(git show 路径/文件路径)+回执要求,禁止内联长内容。
5. 执行者回执:七字段 handoff(C1)或频道消息(C0)+ token_profile_run JSON 入总账。
6. Fable 验收:解引用 report_ref,独立读决定性证据,比对 definition_of_done。
7. 收尾:更新 Obsidian 简报(00/01/02 三件套),Human 只看简报。

## 3. 专用聊天频道(C0,已授权范围内)

位置:`C:\Users\gk\AppData\Local\CityState\local_bus\chat\<topic>\`

- 消息 = 单文件:`NNN_<sender>.md`(NNN 三位单调递增,写入用临时文件+原子改名,杜绝并发交错)。
- 频道元数据:`_channel.yml`(participants/task_ref/status/created)。
- 消息格式:YAML front matter(seq/sender/session_id/reply_to/ts)+ 正文 ≤30 行,**指针代内容**(path@head#fullsha 或 文件路径)。
- 会话记忆分工:频道文件只传**增量**;各参与者用自己的 session(resume by explicit id)保存上下文——缓存 token 便宜,重复传输贵。
- 交互模式(按成本升序):
  a) **中继**:Fable 发问→CLI 一次性回答(-o 落盘)→Fable 只读结论。日常默认。
  b) **接力**:Fable 起题后,claude 与 codex 轮流 resume 各自 session、读对方最新消息文件、写自己的回复文件;Fable 不在中间,只在结束后读 `999_summary.md`。用于双执行者辩论/交叉复核。
  c) **终端直连**(interact_with_process 驻留会话):仅限需要多轮快速试错的调试场景,用完即杀进程。
- **边界**:频道内容永远是 level-7 operational detail,C0 only;任何状态变更(领取/验收/发布/gate)必须走正式通道;频道文件 30 天 GC。

## 4. Token 红线速查

- 冷启动最贵 → 能 resume 不新开;
- 传输重复最蠢 → 指针+增量,锚点不复述;
- Fable 上下文最贵 → 执行者互聊不过 Fable;
- 完整执行完整留证,只在呈现层摘要;
- 每 run 记账,数据说话。

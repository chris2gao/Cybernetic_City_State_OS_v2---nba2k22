---
task_version: "1.0"
task_id: "claude-local-bus-low-token-communication-0001"
title: "Local Bus 低token通讯方案 v0.1(草案,GitHub通讯转备用)"
mode: "plan"
task_level: 0
status: "superseded_by_optimal_token_usage_profile"
superseded_by: ".ai/TASKS/draft-optimal-token-usage-profile-v0.1.md"
author_role: "foreground_review_and_task_dispatch (Claude)"
human_gate: "required"
---

# Local Bus 低token通讯方案 v0.1(提案)

## 1. 问题诊断

现行 GitHub 通讯方案(.ai/PROTOCOL.md v0.3-core)在语义上完备,但同机场景下 token 成本高。阶段4审计单任务消耗 768k tokens,其中通讯开销主要来自四处:

1. **每会话全量协议自举**:后台代理每次冷启动重读 9+ 份协议文件(Codex 本次全读 .ai 协议栈,见其报告 §2.1)。
2. **长报告跨模型转录**:报告为跨窗口传递而写得自包含,大量复述双方已知的上下文。
3. **push/fetch 往返**:发布 review 快照、拉取、解引用,每轮都有 Git 与重读成本。
4. **证据引用靠全文**:报告内嵌大段文件内容,而非 path+hash 指针。

关键事实:Human、Claude(前台)、Codex 与 Claude Code(后台)现在**同机、同一工作树**。跨机传输不再是每轮通讯的必要条件。

## 2. 方案:同机 Local Bus,GitHub 降为发布/存证层

### 2.1 传输层替换(wire schema 不变)

- 新建 `.ai/local_bus/`(**gitignore,永不提交**),消息文件为现行**冻结七字段 schema 的 YAML**——只换传输,不换合同,随时可无损回退 GitHub 方案。
- 前台→后台:`local_bus/inbox/<signal_id>.yml`(七字段信号;task_ref 指向本地任务文件)。
- 后台→前台:`local_bus/outbox/<packet_id>.yml`(七字段 handoff;report_ref 指向本地报告)。
- 投递方式:前台直接驱动 CLI(`claude -p` / codex exec),参数即信号文件路径;无 push/fetch。

### 2.2 Token 减量规则(核心价值所在)

1. **免自举**:后台常驻锚点(CLAUDE.md / AGENTS.md)已含角色、边界、authority order;信号中显式声明 `protocol_context: anchored`,禁止重读全协议栈,仅在协议变更时置 `protocol_context: reload`。
2. **报告限额**:回传报告核心 ≤60 行(结论/证据指针/风险/剩余决策四段);细节写附录文件,前台按需读。
3. **指针化证据**:引用文件一律 `path@head#hash` 或行号区间,禁止大段转录仓库内容。
4. **增量上下文**:任务信号声明 `base_head`,后台只报告相对 base 的 delta;同任务多轮用 `claude -c`(会话续用)代替冷启动。
5. **分级模型**:琐碎轮次 haiku、常规 sonnet、语义/发布类 opus+xhigh,由前台在 dispatch 时指定。

### 2.3 GitHub 保留职责(备用+存证,不退役)

- **发布层**:验收通过的产物仍走 开发分支→ready PR→normal merge,不变。
- **存证层**:被接受的报告/handoff 快照在发布时归档进 `.ai/CODEX_REPORTS/`(tracked),保持可回溯。
- **降级备用**:跨机协作、会话不可续、local_bus 损坏或争议仲裁时,整体回退现行 GitHub 方案。
- `ai/review/latest` 保留:发布类动作(C1/C2)的验收信号仍发布到该分支,合规 gate 校验路径不变。

### 2.4 安全边界(不变项)

- Human gate 清单、authority order、freshness order、工具真实性、fail-closed 全部原样继承。
- local_bus 消息属 level-7 operational detail,不产生任何新授权。
- C2(受保护)事件不得走 local_bus 短路,必须走现行完整 gate。

## 3. 预期收益与风险

- 收益估计:通讯自举+报告转录约占任务 token 的 30–50%,同机任务综合节省预期 ≥1/3;轮次延迟显著下降(无 push/fetch)。
- 风险1:local_bus 无 Git 历史 → 缓解:验收时归档快照进 tracked 区。
- 风险2:两套传输并存造成状态歧义 → 缓解:STATE.yml 增加 `transport: local_bus | github` 单字段声明,活动任务同一时刻只允许一种传输。
- 风险3:协议漂移 → 缓解:本方案作为 PROTOCOL.md 的 transport profile 附录,不复制、不改写七字段与角色规则。

## 4. 落地路径(需 Human 批准)

1. Human 审阅本草案并裁决(本文件当前未提交、未生效)。
2. 批准后发一个 protocol_patch 任务:PROTOCOL.md 增加 "Local Bus Transport Profile" 章节 + .gitignore 增补 + 本文件转正,走正常 PR。
3. 试运行:下一个真实任务(如 EOL 修复)用 local_bus 跑,记录实际 token 对比,回填数据后决定是否设为默认。

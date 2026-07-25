---
task_version: "1.0"
task_id: "claude-optimal-token-usage-profile-0001"
title: "最佳Token使用方案 v0.1(草案,含通讯/工具/输出/模型全链路)"
mode: "plan"
task_level: 0
status: "superseded_by_v0.2_synthesis"
superseded_by: ".ai/TASKS/draft-optimal-token-usage-profile-v0.2.md"
author_role: "foreground_review_and_task_dispatch (Claude)"
supersedes: ".ai/TASKS/draft-local-bus-low-token-communication-v0.1.md"
human_gate: "required"
---

# 最佳Token使用方案 v0.1(Optimal Token Usage Profile)

目标:除"真正用于思考与工作"的 token 外,把环境中一切开销性 token 压到最低。
适用主体:Claude Desktop(前台)、Claude Code CLI(后台)、Codex(后台)、Human。
原则:省 token 不省问责——七字段合同、Human gate、工具真实性、fail-closed 全部原样继承。

## A. 通讯层(AI↔AI)

1. **同机 Local Bus**:`.ai/local_bus/`(gitignore,不提交),七字段 wire schema 不变只换传输;无 push/fetch 往返。GitHub 降为发布/存证/跨机备用层;C2 受保护事件仍走完整 gate。
2. **高密度消息格式**:AI 间消息只允许结构化 YAML,短键名,禁止散文。三条密度规则:
   - 指针代替内容:`path@head#sha256前8位` 或 `path:L120-160`,禁止转录仓库内文;
   - 增量代替全量:信号带 `base_head`,只报 delta;
   - 锚点代替复述:双方已由 CLAUDE.md/AGENTS.md 锚定协议,消息声明 `ctx: anchored`,禁止重读/复述协议栈(协议变更时才 `ctx: reload`)。
   - 诚实边界:比结构化 YAML 更"压缩"的自造密文会提高误读率,反而费 token 纠错,不采用。
3. **会话复用**:同任务多轮用 `claude -c`(续会话)代替冷启动;Codex 同理用其会话续接;冷启动是最贵的单次开销。

## B. Human 输出层(AI→人)

1. 给 Human 的默认输出 = **3-5句结论 + 需要的决定清单**,不超过一屏;细节全部落文件,给路径,你想看再看。
2. 禁止:向 Human 复述长表格、全文引用报告、重复已确认过的背景。
3. 例外:你明确要求详细展开时。

## C. 工具与终端调用层

1. **源头过滤**:所有命令必须在管道内截断/过滤(`-First N`、`--oneline`、`-sb`、`rg` 精确模式),原始长输出禁止直接进上下文。
2. **批量合并**:相关命令合并为一次调用(`;` 串联),一次往返拿齐一组事实。
3. **长输出落盘**:超过 ~50 行的产出写文件,只回读结论行;分析大文件用常驻 REPL(interact_with_process)而非反复新开进程。
4. **事实缓存**:HEAD、分支状态等已查明事实写入任务状态,同任务内禁止重复查询。
5. **权限预授**:白名单(settings.local.json / --allowedTools)按任务 allowed scope 一次给足,消灭"调用→被拒→重试"的浪费循环。
6. **失败快停**:同一命令失败 2 次必须停下换路,禁止无脑重试烧 token。

## D. 上下文加载层(读什么)

1. **索引路由**:严格走 index.md 懒加载(城邦既有法则),Grep/局部 Read(offset+limit)优先于全文 Read。
2. **信任确定性产物**:manifest/hash 已验证的生成物不重读内容;`未读取不声称`不变,但"已验证"允许引用 hash 而非重读。
3. **分工读取**:大批量阅读派给后台便宜模型,前台只读 ≤60 行结论报告;前台自己读全文属于违例。
4. **记忆固化**:跨会话稳定事实(环境、决定、配置)写入 Claude Desktop 持久记忆与 CLAUDE.md,杜绝每会话重新踩坑。

## E. 模型与推理分级层

1. 琐碎机械步骤 `haiku`;常规开发 `sonnet + effort high`(现默认);语义/架构/发布 `opus + effort xhigh`。由前台 dispatch 时指定,对应协议 `recommended_thinking_level`。
2. thinking 预算:机械任务可临时 `MAX_THINKING_TOKENS` 调低;语义任务不省思考 token(这是"正当开销",本方案不动它)。
3. 验收批次 ≤5、并发 ≤5(城邦红线,同时也是 token 保护)。

## F. 报告纪律层(AI产出物)

1. 回传报告核心 ≤60 行:结论 / 证据指针 / 风险 / 剩余Human决策 四段;细节进附录文件按需读。
2. delta-only:只写相对 base_head 的变化,背景不复述。
3. 独立表达保留但限 2-5 句(协议既有规定)。

## G. 度量与反馈环

1. 每任务回传 `tokens_used`(Codex 已支持,如 768k;Claude Code 用 /cost 或日志),记入轻量总账 `.ai/local_bus/token_ledger.csv`(gitignore)。
2. 按任务类型建立预算基线,超支 50% 的任务必须在验收时说明原因,持续超支则修订本方案。
3. 试运行对照:下一个真实任务(建议 EOL 修复)按本方案跑,与阶段4的 768k 基线对比,数据回填后再决定是否设为默认。

## H. 落地路径(需你批准)

1. 你批准本草案 → 我发一个 protocol_patch 任务:PROTOCOL.md 加 "Token Usage Profile" 附录 + .gitignore 增补,正常 PR 发布;旧 local-bus 草案作废合入本文件。
2. 立即可先行的(不动协议,属执行纪律,你点头即生效):B(Human输出)、C(工具调用)、D(上下文加载)、E(模型分级)——这些是各代理的行为规则,不改任何合同。
3. 需走协议修订的:A(传输层)、F(报告限额)、G(总账字段)。

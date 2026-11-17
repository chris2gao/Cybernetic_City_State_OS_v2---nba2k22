# Human decision — Trust-first Agent cooperation and honest self-report

- **Date:** 2026-11-17 (America/Los_Angeles)
- **Task:** OS-CORE-HUMAN-REVIEWED-ATOMIC-PROTOTYPES-SYSTEM-UPGRADE-20261116-001
- **Human statement:** “我们约束的前提是信任agent，我觉得agent会承认错误，会诚实输出，而且我们假设模型也是如此，所以我们的约束，就是建立在这个信任的基础上，让它遵守，而不是类似看守犯人一样去对待模型，这和设置权限是两回事，如果我们检测不到的地方，就让模型自行上报即可。”

## Decision and its precedence

This Human decision **refines and supersedes any reading** of previous PR #37 plans that made general-purpose model surveillance, mandatory tool capture, or a suspicion-first framework the prerequisite for task discipline.

- Begin with trust that Agents are willing to admit mistakes and report accurately.
- Task prototypes, minimum Ready/Action/Done, and the EXECUTION/DEVELOPMENT distinction remain collaborative **work agreements**. Agent follows the approved protocol and voluntarily discloses any observed deviation, even when the Host cannot see it.
- A useful self-disclosure states what happened, why, actual business consequence, correction, and whether a Human decision is needed. Do not conceal error or present preparatory work as successful Done.
- Keep distinct `AGENT_SELF_REPORT` and `HOST_OBSERVED` tool events. Self-report is not a denial, an offense, or independent Host proof. Voluntary admissions do not inflate the Host refusal rate; their frequency alone does not establish poor model–OS fit.
- No automatic punitive score, ban, per-command check, mandatory Shell/GUI interception, always-on behavior monitoring, separate approval server, or reporting ritual for normal successful calls.
- Permissions for protected actions (Native, destructive filesystem, publication, credentials) remain separate and continue to apply. Trust does not silently grant new authority.
- For Agent-only-observable conduct, use the conversation/existing PRMS or optional `agent_self_report.py`. Unavailable optional local JSONL is **not** a new mandatory business blocker.
- The system can evaluate a task based on shared prototype, real Done and honest reporting **before** production Host-wide tool mediation exists. A gateway can be used where technically appropriate; never pretend its coverage is universal.

## Engineering scope

The approved correction belongs inside existing Core PR #37, without reopening NBA2K22 T15 or changing Core master. The agent_self_report module is a lightweight optional structured record (source tag, task/prototype/model/session, kind, correction and business effect), not another execution supervisor. Tests should verify that voluntary reports are never silently merged into `GatewayEvent` denial metrics.

**Status:** Human intent confirmed; Core implementation candidate and tests subject to ordinary independent review and separate integration decision.

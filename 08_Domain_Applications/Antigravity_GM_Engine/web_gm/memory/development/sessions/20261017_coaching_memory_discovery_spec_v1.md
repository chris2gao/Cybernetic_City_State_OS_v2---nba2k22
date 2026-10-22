# 2026-10-17 教练战术研发：内存定位任务书规划归档

- task_id: `DEV-20261017-05`
- role: `WEB_GPT_DEVELOPMENT`
- status: `PREFLIGHT_RESEARCH_SPEC_COMPLETE / CODEX_MEMORY_DISCOVERY_PENDING / IMPLEMENTATION_NOT_STARTED`
- 开发前研究任务书：[docs/development_tasks/DEV_20261017_05_COACHING_MEMORY_DISCOVERY_V1.md](../../../../docs/development_tasks/DEV_20261017_05_COACHING_MEMORY_DISCOVERY_V1.md)
- 首次任务书提交：`57afdbcfb80f61115157c00dd184af3e808bac80`
- 相关上一轮评估：[docs/development_reviews/DEV_20261017_COACH_TACTICS_SIMULATION_ASSESSMENT_V1.md](../../../../docs/development_reviews/DEV_20261017_COACH_TACTICS_SIMULATION_ASSESSMENT_V1.md)

## 玩家开发意图

玩家正式允许进行开发前调研，要求Web GPT研究NBA2K22 PC各队教练攻防策略、战术手册和模拟比赛设置的候选功能，交Codex在实时内存中定位，证明可行后再进入正式模块开发。玩家对游戏实战AI策略动态变化已有观察，对普通快速模拟AI是否动态调整未知。当前并未授权正式存档策略写入或自动触发30队GM回合。

## 研究结论

1. 区分四种不同对象：联盟级Simulation Sliders、球队级Sim Points of Emphasis、Coach Gameplan/Coaching Sliders/对手专属Gameplan、战术体系/战术手册/比赛中ACE。禁止把全局Simulation Sliders用作GM给个别球队的战术能力。
2. 最高优先级是六类Sim POE及可能存在的Scoring Options；次级为Help Defense、Run Plays、Zone、轮换、系统体系；再之后是Playbook/Freelance及队级/对手级防守战术。枚举皆需NBA2K22 PC实机UI复核。
3. 旧仓库`src/strategy_manager.py`有`0xEB2..0xEBC`球队字段候选，但不是Sim POE独立存储证据，且存在`poe_on_ball`枚举冲突。STAFF profile现有`preferred_system/active_system`三bit只读线索。无通用GM战术执行器验收。
4. 社区对NBA2K22在30队Coach Profiles/POE调校用于改善模拟数据有记录；2K官方Conditional Coaching明确说明在次世代PS5/XSX，不能假定PC有同一能力。一般跨版本Sim POE选项仅作为游戏UI核对清单。
5. Codex依次做UI逐项台账、UI↔内存差分与单字段可逆验证、不同球队和对手作用域验证、隔离测试存档最小安全写入、存档退出重进、快速模拟/SimCast/CPU-v-CPU/玩家对战分路影响实验、AI自动改写检测。
6. 研发准入必须同时有合法枚举/身份、可回读可持久化、对相应比赛模式确有作用、安全执行路径证据。其他字段可留下UNKNOWN，不为追求完整性猜偏移。
7. Codex须返回`docs/development_reviews/DEV_20261017_05_COACHING_MEMORY_DISCOVERY_REPORT.md`和字段矩阵JSON；只做研究/隔离验证，报告后停，等待下一步产品开发审批/任务。

## 本轮对仓库做的事

只创建研发调研任务书和本次持久化记忆；未更改`config/gameplay_policy.json`、`src/`、`published/`、SQLite、游戏存档，也未运行Windows内存扫描、进行GM决策或触发Codex。

## 下次恢复

Web GPT DEVELOPMENT先读本任务书、最新`DEVELOPMENT_CURRENT.md`和Codex提交的实机证据，再审查能进入P1开发的具体字段范围及未通过的类别。30队GM战术改变仍由GM形成提案、玩家具体批准、Codex执行。

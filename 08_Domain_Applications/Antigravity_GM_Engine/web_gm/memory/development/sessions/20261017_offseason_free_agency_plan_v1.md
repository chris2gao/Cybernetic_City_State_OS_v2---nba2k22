# 2026-10-17 | DEV-20261017-04 休赛期自由球员签约模块规划

- 角色：WEB_GPT_DEVELOPMENT
- 类型：开发需求规划与Codex任务书（非工程实施）
- 状态：SPEC_PUBLISHED / IMPLEMENTATION_NOT_STARTED / NO_GAME_WRITE_APPROVAL
- 任务书：[DEV_20261017_04_OFFSEASON_FREE_AGENCY_V1.md](../../../../docs/development_tasks/DEV_20261017_04_OFFSEASON_FREE_AGENCY_V1.md)
- 真实提交：`3ff1ff53e50084390092402462efa7e2600c8e3a`（任务书首次创建）

## 用户目标
关闭游戏原生交易后，每个赛季结束、下赛季开始前由玩家主动触发集中自由球员市场：30队到期合同扫描、候选汇总、球队竞价、母队匹配报价、薪资与奢侈税及资金限制、玩家批准后Codex执行，避免NBA2K22自动自由球员签约破坏外挂GM经营世界线。不追求复杂CBA，优先游戏有效规则，禁止普通球员能力编辑。

## 仓库证据
- `config/gameplay_policy.json` PLAYER_RULES_20261017_V3：阶段玩家独立触发、普通属性写入禁止、执行需具体批准。
- `config/memory_field_profile.json`：有`years_left_on_contract`、`contract_option`、`bird_years`、`contract_year_1..6`字段profile；读取能力不代表合法签约权已认证。
- `src/gm_core/finance.py`：`salary_cap_minus_payroll_proxy`为代理，非认证薪资空间。
- `database/templates/save_template.json`/`src/season_rules.py`：仅2021–22确定规则值，未来年份须再核对。
- `docs/34_BASELINE_CURRENT_STATE.md`：无完整验收的球员签约、合同和球队归属受控执行器；`gm_core`不应调用游戏内存写模块。
- 现实对照：NBA官方2021–22工资帽112.414M/奢侈税136.606M；当年apron143.002M；UFA没有法律上的强制母队匹配，RFA需实际匹配资格。现实规则仅作为参考，游戏优先。
- 有关游戏CPU自动签约能否完全关闭的结论**未知**，需要Codex在NBA2K22实机证明。

## 本轮规划结论
1. 四阶段 P0实机调研→P1只读竞价提案→P2受控签约写回→P3防CPU覆盖与跨赛季回读。
2. 母队对UFA只获得同价竞争机会，不强制球员留下；RFA依法定且已验证的资格匹配。
3. 工资帽不等于奢侈税线；球队cash不是天然的cap room；超帽须可验证签约资格。
4. 阶段隔离：玩家触发、只读采集/规则计算、Web GM审议、玩家明确批准、Codex执行，不自动串联。
5. 去重/严格身份、名单/资金预留、幂等、游戏阶段防抢签都是闭环验收要件。
6. 未作实际游戏签约，未改`published/`、存档、普通能力或球队正式GM方案；单独任务书的创建不是执行授权。

## 下一次恢复
- 开发窗口读任务书和最新`docs/34`，Codex先完成P0并交代码/真实实机证据，网页开发基线据此审查。
- P0必须回报休赛期安全停点/游戏自动签约关闭情况/FA池与资格字段/薪资与资金变化/合法合同限制/执行器可行性。
- 玩家没有明确批准正式存档签约前，整个功能即便开发完成也只有`PROPOSED`或测试局功能。

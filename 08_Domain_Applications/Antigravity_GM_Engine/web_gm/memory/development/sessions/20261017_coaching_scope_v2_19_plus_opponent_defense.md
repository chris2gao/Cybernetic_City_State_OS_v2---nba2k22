# 2026-10-17 教练系统DEV07最终业务范围V2

- role: WEB_GPT_DEVELOPMENT
- status: `V2_SPEC_PUBLISHED / CODEX_IMPLEMENTATION_PENDING / NO_FORMAL_GAME_WRITE`
- primary: [DEV_20261017_07_COACHING_GM_CLOSED_LOOP_V2.md](../../../../docs/development_tasks/DEV_20261017_07_COACHING_GM_CLOSED_LOOP_V2.md)
- created_commit: `3651e1d440d1fdba43a346cb8228b867889e29af`
- legacy: [DEV07 V1](../../../../docs/development_tasks/DEV_20261017_07_COACHING_GM_CLOSED_LOOP_V1.md)已添加醒目指向V2，原有V1里的“其它18项非必需”和“单对手防守待后续”均被覆盖。
- existing code: PR #1 head `5daeed8dc0001b5052dce1cfc97d6c22ee9317c3` 仅六项默认POE可生产执行，未合并、未完成V2。

## 玩家最新明确决策
1. `SimPace/SimPress/SimHelpDef/SimOffReb/SimDefReb`是玩家模拟比赛功能，GM不用，**排除教练机制可执行字段**。
2. 球队当前主教练`PreferredSystem`、`ActiveSystem`会影响球队战术体系，必须开发。
3. `PlaybookID`选择主教练使用的战术本，间接影响球队比赛使用的战术，必须开发；只能引用当前实际加载的有名手册。
4. `BenchDepth`、`RunPlayTendency`、`ZoneUsage`、`BenchUtilization`、`Tempo`、`HelpDefense`必须开发。用户看到当前PC游戏菜单范围1–100，网上旧版资料有0–100和自定义名单BenchDepth=11；需最小UI↔raw核对，特别不把BenchDepth盲目当百分比。可只读比较Kerr、Spoelstra、Popovich、Thibodeau、Nurse、Lue等本局实际主教练值；绝不能编造游戏中的具体数值。
5. 四`FreelanceType(1..4)`是**四套按优先级排列、比赛中使用**的Freelance进攻体系，全都必须可调整，不能当无序集合；不要求测试每套调用概率。
6. 上述**6POE+2System+1Playbook+6Slider+4Freelance=19项每队默认教练战术**，这里全局意为“对一支球队所有对手生效”，非全联盟模拟Slider。
7. 指定对手页面额外出现的**整体防守理念**是重要的**单一对手独立设置**，不能全局化。18原生防守字段已在Gameplan的8byte防守位域中定位，但当前reader按matchup_id/defender_id逐条读取，尚不能证明哪条等于UI的“整体/All”，且IsInUse全部0语义未明。Codex需做一次隔离局最小UI差分定位overall条目、原生enum、继承/取消，之后直接开发该独立覆盖。若无法安全确认不能写错个人matchup，要标PARTIAL_BLOCKED不冒充已完成。
8. **用户不需要模拟比赛、游戏胜率A/B、逐项反复保存测试**，仅需必要的枚举合法/共享位保护/准确owner/读写回退/整批预验/来源发布/两本手册对齐等低成本安全验收。

## V2保留的此前必需闭环
- 30队逻辑事务：整批玩家批准、全队只读预检、刷盘预像、共享位合并写、回读、条件恢复/部分失败报告；非硬件瞬时原子。
- 玩家触发的正常采集自动带COACHDATA的19项+独立对手防守源，入SQLite并在`-Publish`时进入`published/latest`及Github；无用户触发不自动采集。
- 两本真实生产手册：`web_gm/manuals/GM_COACHING_OPERATIONS.md`，`docs/40_COACHING_EXECUTION_RUNBOOK.md`，更新各自GM/执行基线指向。GM每次只提出PROPOSED，具体正式局批次仍须玩家明确批准交Codex。
- 完工口径**19项默认+指定对手整体防守+30队batch+来源发布+双手册**。阻断则如实PARTIAL，不能因六POE已完成称整套完工。
- 保持旧`TEAM+0xEB2`策略writer禁用，不允许普通球员属性/潜力/徽章/倾向改动。

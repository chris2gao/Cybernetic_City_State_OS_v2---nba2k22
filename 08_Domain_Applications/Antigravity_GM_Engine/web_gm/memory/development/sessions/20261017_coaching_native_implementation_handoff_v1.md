# 2026-10-17 NBA2K22 教练战术原生字段只读调查 → 正式研发任务交接

- task_id: `DEV-20261017-06`
- role: `WEB_GPT_DEVELOPMENT`
- status: `IMPLEMENTATION_TASK_PUBLISHED / CODEX_WORK_PENDING / GAMEPLAY_RESULT_PENDING_PLAYER_MONTH`
- 当前实施规格：[docs/development_tasks/DEV_20261017_06_COACHING_IMPLEMENTATION_V1.md](../../../../docs/development_tasks/DEV_20261017_06_COACHING_IMPLEMENTATION_V1.md)
- 用户转发的Codex只读调查：[docs/development_reviews/DEV_20261017_05_COACHING_READONLY_HANDOFF.md](../../../../docs/development_reviews/DEV_20261017_05_COACHING_READONLY_HANDOFF.md)
- 首次只读转交记录GitHub提交：`8e41838f94e0c4690c813f771c337b1c5b479603`
- 首次Codex正式开发任务书提交：`dd561e9e5455b118ff01e304689cd6460b519d6b`
- 证据性质：玩家转发Codex对NBA2K22 PC原生代码和进程的摘要；本Web GPT未直接重复实时内存调研，也没有Codex的原生日志，所以是研究线索和研发任务输入，不是受控写入验收。

## 关键技术结论

1. **必须禁用旧`TEAM+0xEB2`策略writer**：Codex报告原生`+0xEB2`是读后递增计数路径，不应继续将其当攻防枚举；现有`src/bootstrap_new_game.py`第4阶段调用旧`set_team_strategy`，必须一起阻断/迁移。球队票价子系统不受影响。
2. 主教练六POE位于`COACHDATA+0x13C`的32bit共享块，六个5bit字段位置分别为 defense 0/5/10、offense15/20/25；值集合0+各独立合法枚举段；剩余bits30/31需保护。
3. `SimPace`与四个`Sim*`滑块另存`+0xF4`附近共享位域；`Tempo`/`HelpDefense`也在`+0x148`位域。均需Codex补充具体mask才能写。
4. 30队对手Gameplan拥有35容量槽、29已识别他队记录/队，总870条；`0x370`/record，Gameplan POE/slider/playbook等偏移不等于教练默认bit块；报告说`IsInUse`全0，必须证明启用机制，未证明只能只读/提案。
5. 当前加载84本战术本(`0x168`每本、68 CRC槽)以及教练PlaybookID和方案PlaybookId引用；验证合法加载、避免共享引用错改。防守8字节18字段，具体完整位位置尚未知；轮换需实体身份验证。
6. 每次重启PID重新定位`NBA2K22.exe+0x632B478`相关原生链，球队从联盟根`+0x19CFD0`的记录步长`0x13E70`按内部team_id映射，不可固定数组下标。PID992等绝对地址只属于历史调查，不作为常量。
7. **允许研发**：Codex尽早做真正受控接口与必要隔离存档技术写入确认，不必先进行对照比赛模拟；开发完成提交后由玩家本人批准具体战术、执行，并跑一个游戏月，随后独立触发比赛来源采集与Web GPT ANALYTICS/GM分析。小游戏战绩影响尚`SIM_EFFECT_PENDING_PLAYER_MONTH`。

## 本次行为边界

本Web GPT创建只读交接报告、正式开发任务书、旧调研指向及本岗位长久记忆；未连接Windows游戏进程、未写入正式比赛/策略、未修改源码、未执行GM回合、未采集/发布最新游戏来源。

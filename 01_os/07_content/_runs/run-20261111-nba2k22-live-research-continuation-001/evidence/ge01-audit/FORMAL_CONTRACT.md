# Human 已批准 GE-01 · Codex 执行交接（2026-11-13）

**状态：`APPROVED_FOR_SCOPED_ENGINEERING`，旧 M1→M3 纯能力发现方案已被 GE-01 取代。**
**Human 最新确认：** 同意 [GE-01 具体实施方案](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/issues/24#issuecomment-6873712749)；NBA2K22 进程已经启动并加载相关存档；Codex 可在本任务必要时以**管理员级别权限**访问/操作 NBA2K22 进程；此前失败采集数据约 9GB，保留有用部分，无用可删除重新采集。以上是实际 Human 指令记录，不得泛化为不受限的 Native/Calendar/存档变更授权。

## 首要交付：真正完成 W01 的业务研究闭环，而不是更多预检

复用 NBA2K22 [Issue #40 原始任务](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/40#issuecomment-6794780940) 与 [PR #43 代码](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/43) 现有入口，处理新鲜状态下的 **采集 → 正式 H/L 原生修改+独立 Getter → 日历模拟 → 赛后 WorldData → H/L/C 分析**。参考 W01 为 5 个倾向字段、20 H/L 席位、53 场计划比赛；**以上属于历史计划，并非当前加载存档下已经获准执行的原生矩阵**。若实际情况与历史计划不同，清楚提交最小偏差及可继续的方案，不伪造身份/赛果，不把一场/一槽的局部验证冒充 W01 完成。

**已知工具直接用：**
- `01_os/07_content/_runs/run-20261107-nba2k22-vae-longrun-40-001/run_batch_experiment.py`
- 同目录 `live_research_authority.py`、`analyze_bound_round.py` 和对应真实绑定/读取脚本
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/{factor_runner.py,season_cycle_host.py}`
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/tools/test_only_calendar/calendar_cli.py`
- 现有 WorldData 与 REA Bulk、Native CAS/Getter/Journal。不要先新建通用金蛋引擎/Host/验证表/任务目录。**已确认的代码缺口**：目前 `live_research_authority.py` 中 `FIELD = "SHOT_TENDENCY"`，不可直接宣称已支持 W01 五字段；只做真实链路所需最小增量。

## 开工即执行；有限检查，不做反复准备

1. **一次性恢复实际现场（只读）：** 通过现有管理员可用工具确认 NBA2K22 当前进程/epoch、当前加载存档、Native Today、世界线、赛程和相关数据源身份。不要假定仍为历史 `MyLEAGUE0005`、2021-11-15 或 PID 4352。若存档身份不符合隔离研究要求，立即提出**唯一明确 Human 动作**，不要触碰错误存档。此只读恢复和任务分支可逆工程改动已获此次工程批准。
2. **9GB 历史数据：** 不因旧研究失败就整体删除、整体复制或全量重采。先最小化识别文件类别、路径/大小/来源/当前绑定及是否可复用：有效历史原始证据、唯一失败回执、不能再生的源数据和重要数据库应保留；新实验基线必须依据**当前实际内存/存档的 fresh 读数**，旧数据不能冒充新鲜基线。对已证明可再生且不含唯一证据的重复缓存，Human 已条件性允许清理；先给出精确清理名单/来源并按现有受保护删除规范核实确认覆盖，其他一律保留。不要为清理 9GB 变成独立大任务，不重复对全部数据做昂贵哈希。
3. **只解决承重阻塞：** 直接检查原执行路径能否跑通 W01；若出现具体 API/Bridge 参数错误或五字段支持缺口，做最小工程修正、针对性测试并回到业务链；不能无限扩大资格/完整性/基础设施测试。保护必须保留 Native UID、字段位宽/邻域、CAS、Getter、世界线、Outbox和UNKNOWN不重播；有必要的检查随实际操作触发。
4. **Native/Calendar 的精确执行封套：** 已允许管理员权限操作游戏进程，但在正式写入或模拟前仍需**一次**提交 fresh 的 UID/Team/字段/before→target、GameID/日期、最大 Setter/Calendar 次数、是否涉及任何恢复/保存以及真实危险与 Done，由 Human 直接确认具体封套；如需重新加载干净存档由 Human 完成/确认，不能自行覆盖/恢复。获批后在该封套内自主连续执行，不按每人每窗请求微许可。若只是这一许可缺口，**停在准确的 HUMAN_AUTHORIZATION_REQUIRED 并汇总一次**，不以大量离线任务替代。
5. **业务读回为验收：** 从实际 Native Setter/Getter → 真实完成的 GameID 和 Box → 新增 WorldData 事实 → H/L/C 比较、缺测/暴露/干扰结论，可复算。仅资格16项、Fixture通过、报告/脚本数量、成功采集不能令研究父任务 DONE。若真实副作用 UNKNOWN，按受影响资源停止重放、核对 Journal；其他独立无冲突事务仍可按授权继续。
6. **持续内部 Loop：** 第一个获批的、实际Ready的业务动作先做；每次普通修复回到业务主线，直到 W01 完成或确切硬阻塞。对照旧 [失败报告](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/5a1d270d82196fb78fb4f64e7a832813e1b9a6b5/01_os/07_content/_runs/run-20261111-nba2k22-live-research-continuation-001/FAILURE_REVIEW_FOR_GPT.md) 的「16资格、0日历、0闭环」反例。

## 权限与交付边界

- **已获批准：** GE-01 施工方向、当前已加载游戏的必要只读访问、Codex 需要时可使用 Windows 管理员权限、普通任务分支内可逆修复及其局部测试、合理复用/条件清理无用重复数据。使用已授权的管理员辅助机制，不修改官方签名游戏/程序以规避权限边界。
- **尚未获授权：** 任何**未绑定 fresh 具体清单的正式 Native 批量修改/Calendar 日历推进**；不自动把本条泛化为任意字段/任意队/整季模拟许可。不得自行覆盖、恢复或保存存档，改游戏 EXE，操作 Core/NBA master，自动激活 scheduler 或越过本任务范围。
- **首份 Codex 交付：** 不要再次写大型纯规划报告；直接报告 (a) 实际进程/存档/日期与旧数据复用判断，(b) 第一条已执行的真实业务工作及产物或唯一确切阻塞，(c) 当前必要代码差异及针对性验证，(d) 一份可供 Human 一次性批准的精确 W01 操作封套。之后在批准范围内连续执行并交真实 W01 业务结果。
- **任务角色：** Codex `execution`；GPT `decision_architecture`；后续独立审核 `independent_review`；Human 为具体方案及受保护动作裁决者。PR #23 仍 Draft，此任务不以它先合并为前置。
- **跨模型交接：** 此 issue 是可持久恢复的任务合同，不代表已在某个 Codex 会话实际启动。Human 在 Codex 工作窗口以本人指令转交本评论链接即可启动；禁止将助手GitHub评论冒充 Human 私有授权签名。

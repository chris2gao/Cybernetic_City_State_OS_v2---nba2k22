# 2026-10-18 MC 三专项只读研发交接（DEV09）

## 本次请求

用户在 NBA2K22 PC 本世代中确认：名人堂难度、硬件/帧率正常，仅低 Speed with Ball/Acceleration 的中锋在持球运球时整套动作（含篮球弹地）异常缓慢，俗称“月球漫步”。禁止以改球员能力、提高整体Game Speed或环境问题糊弄。用户目前在《终极联盟》**测试存档的CPU持球速度/加速度滑块设置页面**，希望Codex就地读内存、从GUI值定位真正内存地址。另研究MC人物创建后的主宰类型改变、佳得乐状态激活。

## 规划成果

- 权威任务书：[DEV-20261018-09](../../../../docs/development_tasks/DEV_20261018_09_MC_MOVEMENT_TAKEOVER_GATORADE_RESEARCH_V1.md)，创建提交`f4c57ce3be9df2ab1b8e485447222689b3e102c8`。
- P0立刻利用现有CPU设置页面只读捕获CPU 4个with-ball运动值；必要时玩家在**该测试存档**UI单项变更后恢复，Codex只读差分，再核对USER设置、真实setting和Gameplay消费路径、MC是否沿用还是独立实例/覆盖。
- 不再信任`src/slider_manager.py`里`ADDR_SLIDERS=0x063319F8`等历史静态地址，不允许直接执行`lock_realistic_sliders`（顺带改伤病/交易/节时）；所有地址需当前进程身份和原生UI差分证据。
- P1调查MC Takeover Type与Meter/Active/Team状态，不能用改球员属性/徽章代替切换主宰。
- P2区分Gatorade消耗品、每周Workout/Turbo额外体力槽、Gym Rat永久权益，保留服务端离线限制与状态未知。
- 本任务只批准研究/只读工具和开发文档，**不授权任何游戏内存写入或MC属性修改**。程序写回单独要求批准测试存档、字段、原值→目标、恢复。无需大量比赛或保存重启实验。
- 报告允许`BLOCKED/UNKNOWN`，不许将“终极联盟菜单可调”直接推断“MC当前真实比赛受控”。

## 项目边界

DEV07教练数据/采集、全量-only`full_verified_v1`生产数据源、GM获批交易/教练执行均保持独立。本专项测试存档数据不能混入正式`published/`或SQLite。Codex研究完成提供只读证据、游戏版本/进程指纹、可行性和下一步需玩家授权的最小操作。

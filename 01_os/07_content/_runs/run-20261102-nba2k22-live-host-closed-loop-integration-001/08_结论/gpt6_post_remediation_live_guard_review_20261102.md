# NBA2K22 Host P0/P1 整改 · GPT-6 复核与 Live 启用门

任务：`NBA2K22-LIVE-HOST-CLOSED-LOOP-INTEGRATION-20261102-001`
日期：2026-11-02
角色：`decision_architecture` / GPT-6
**实际 GitHub 审核对象**：`dc4eb1c0f3888e1f36b8d0d7db7c9bb46e9f66d7`，与 GitHub branch HEAD 及远程本地设备 Git HEAD 三者一致。
**执行报告 SHA 错误**：Gemini 报告声称 `dc4eb1c062c3e1293e62f0ba9343729d5b78ff72`，GitHub API 返回422（提交不存在）；需按实际 SHA 更正报告、完成指针。
执行者：Gemini 2.5 Pro (execution)，据上传的执行报告。
审核操作：GitHub 只读源码/收据核验，Desktop Commander 在授权 Windows 本地复跑 `python -m pytest -p no:cacheprovider --basetemp=E:\gemini_space\_host_audit_temp_20261102 -q tests\test_season_cycle_host.py`，**7 passed in 6.44s，exit code 0**。首次未设置 basetemp 测试函数 7/7 PASS，但 pytest 退出清理缺权限，exit code 1；使用独立目录重跑消除该环境问题。**没有连接游戏修改进程，没有 Native Setter、没有游戏/Save 还原操作**。

## 复核决议

**`OFFLINE_REMEDIATION_TESTS_PASS; LIVE_SETTER_EXECUTION_BLOCKED`**。
确认整改实际产生：真实模式 PID/date 查找与 FULL capture fail-closed、日历进度检查、状态原子落盘、NO_CHANGE Outbox 状态记录、暂停恢复防静默 UNKNOWN 解锁，皆可保留。

但仍存在以下**具体承重逻辑**：

### P0-A · Getter-after 复用修改前缓存，不能证明独立真实读回

`season_cycle_host.py:_get_live_getter`（约165–190行）调用 `collect_player_skills(reader)` 一次，关闭 Reader，然后在 `live_getter` 闭包中查本次采集的 `player_tendencies` 内存字典。这是**snapshot lookup**，不是每次调用重新读取 NBA2K22。
`authorize_and_execute`（约791–800行）在执行 Setter **之前**获取这个 Getter 闭包，`execute_batch` 后（约863–883行）调用它验证所谓的 Getter-after。因此真实发生修改时读到的仍可能是写入前值，导致误判 STOPPED_READBACK_FAILED；如果新旧值相同则也无法证明独立执行后读回成功。
**最小修复**：preflight Getter 和独立 post-run Getter 必须是**不同时间的 fresh、live 只读采集/按目标精确读取**，确认 PID+创建时间、save/worldline/epoch 一致，目标按 `team_id/player_id/field_id` 严格唯一解析；不能把同一预先构建的 snapshot closure 当作执行后观测。为真实 post-run 加字段数/去重/来源/读取时间的 receipt。

### P0-B · UNKNOWN 状态检查与真实映射不一致；验收前回填

`DecisionBatchBridge.map_receipts_to_outbox` 会映射成 `UNKNOWN_EXECUTION_OUTCOME`（见 `decision_batch_bridge.py`）；`DecisionOutbox.record_execution_receipts` 通过 `"UNKNOWN" in outcome` 标记 `UNKNOWN_LOCKED`；但 Host `authorize_and_execute` 用 `r.get("outcome") == "UNKNOWN"` 检查，这不会捕获 `UNKNOWN_EXECUTION_OUTCOME`，可能把 Host 状态推进为 `WAITING_CALENDAR_ADVANCE` 并清除 active_plan，尽管 Outbox 已锁。
Host 同时在检查 readback_passed、UNKNOWN 之前先调用 `record_execution_receipts`，若独立 readback 实际失败但 Journal 写 SUCCESS，Outbox 仍可能记录 COMPLETED。且没有调用通用 `validate_batch_execution` 的原始 Native messages + chunk digest + claims + Journal 全量核验；`session_summary` 仅用于计时，没有作为 fail-closed 验收输入。
**最小修复**：执行结果先归一化 outcome，完整验证原始消息/Journals/每项 fresh readback、回执集合守恒，再以可信 Host 的经过验证收据一次回填；UNKNOWN/partial/readback_failure 不得写成功、不得清 plan、不得自动重放；Host 与 Outbox status 必须一致。确保新增针对性负例：`UNKNOWN_EXECUTION_OUTCOME`、1/2缺收据、伪造成功但 fresh readback mismatch、原始 Chunk digest 错误。

### P0-C · 真实角色与动作授权未接好，测试模式不能通往 Live Writer

`_make_profiles` 仍使用固定 actor `gm_user_01/coach_user_01`、team_scope `(1,25,28)/(1,)`、硬编码 phase_grants。CLI 的 `--intents-file` 使输入自带的 `actor_uid` 可以匹配静态测试 profile。Host 本次没有实际 Host identity/provider 接口、也没有证明所有授权动作与真实角色生命周期匹配。
尽管报告说 Live 只允许 Player `SHOT_TENDENCY`，Host `authorize_and_execute` 路径没有实机执行前逐项 enforce `action_id=PLAYER_PATCH_TENDENCIES, field_id=SHOT_TENDENCY` 的 Live allowlist；角色 bridge 支持更广动作。
此外 `initialize_season` 只凭 `mock_game_date is not None` 将状态标记为 `is_offline_mock`，CLI 公开 `--mock-date`，而 `authorize_and_execute` 对该状态会跳过 Live 身份/Getter 后核验，**同时仍可能构造无 fake_runner 的真实 `BoundedSessionExecutor`**；不能允许测试模式被普通 CLI 组合调用到真实 Native Writer。
**最小修复**：`test/offline` 模式必须**强制配置 Fake runner 或根本不允许执行 Native Setter**，无法因 mock-date 绕过验证；实机动作逐项严格限定目前真实认证的 Player/SHOT_TENDENCY，真实 Host 权限应来自可信授权元数据/当前游戏上下文而非模型提供 actor uid，且 Human 在每轮核验准确 `cycle_id+plan_digest+actions+scope`。

### P1 · 回档存档路由仍存在重绑定生命周期与异常处理缺口

`inspect_worldline`（约252–269行）自动改写 `save.json` 的 `database_file`，但出错时 `except:pass`，没有 rollback/回读确认，也没有保存原 binding 的可恢复指针。第二次初始化时 `bound_database` 会把 child 当默认库、`worldline_id` 又可能返回 `worldline-main`，原历史未删除但世界线 identity 可以漂移。当前新版 FULL 路由在成功时可能接到 child，这是进步，但不能凭写配置文件就宣布新旧两个 worldline 已完成可重复识别与来回切换。
**最小修复**：保留原 binding/child mapping 的 append-only manifest，写后验证 target DB 与 `read_binding` 相符；重复 init 同 worldline 得稳定身份，切回旧档/新档可恢复指定历史；重绑定失败要 fail-closed，不继续执行。只做现有配置层的受控修复，不新建数据库架构。

## 测试与后续

- 继续留在原工作分支，修上述 P0 承重缺口和 P1 最小配置回读。**不重构 WorldData、REA/Setter、Outbox、CalendarSimOrchestrator**。当前版本可以做只读探索，但应优先在独立测试库中运行，只读初始化本身也会写数据库和 `save.json` 配置，不能误称“零持久变更”。
- 测试重点要求 7 个旧测试通过 + 上述针对性负例 + 新旧两档来回 init；通用 gold 100 setter 原始数据可**离线回放**但不应重复真实游戏写入。
- **解除 Live 写入封锁门**：证明新鲜 post-write Getter 真正来自执行后游戏、UNKNOWN 状态守恒、mock mode 不可能落到真实 Writer、准确角色/动作 Human 批次授权与 DB/worldline 长期绑定；在此以前只允许真实只读试运行（及测试库/配置副本），不运行 `season_cycle_cli authorize`。
- 完整工程 G09 四轮实机尚未执行；不能把 Fake 4轮或单次真实只读 Calendar 探测当成四轮 Live 认证。

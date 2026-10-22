# 数据源自动抓取与独立存档模板

> **规则优先级：** 数据、审批、数值计算和地址漂移总规则见 [22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md](22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md)。本文记录当前采集实现；与总规范冲突时以总规范为准。

## 目标

每个游戏存档使用相同的 schema 和默认规则，但拥有独立的数据文件。每次采集都先验证当前 NBA 2K22 进程里的内存地址，再读取来源、执行清理和完整性检查；未观测字段保持 `NULL`。GM 只消费已通过脚本审计且摘要匹配的数据库快照。

## 存档布局

运行 `python src/bootstrap_new_game.py --save-id <id>` 后，代码从 `database/schema.sql` 原子生成版本化模板 `database/templates/league_template_v2.sqlite`，再复制到：

```text
database/saves/<id>/
  league_state.sqlite
  player_pool.sqlite
  snapshots/
  backups/
  evaluations/
```

`database/templates/save_template.json` 是稳定规则模板，`src/season_rules.py` 负责校验并提供赛季配置。新存档数据库仅从 schema 和模板构建，不从上一局复制队伍、球员、内存地址或快照。bootstrap 默认只读：校准并采集当前队伍/球员数据，生成 `M00_BASELINE`；只有玩家明确批准并传入 `--approve-game-writes`，才会应用全局设置与 30 队 POE/门票模板，并逐项回读。相同 ID 不会清空数据；不同游戏存档必须用不同 ID。

存档 ID 只允许 1 至 64 个字母、数字、下划线和连字符，且必须以字母或数字开头。月度采集应始终传同一个 `--save-id`。旧的共享库通过省略 ID 兼容，但新游戏不要共用它。

## 每次月度采集

```powershell
python src/run_monthly_cycle.py --save-id <id> --season 2022 --month 1 --name NOV
```

采集前置检查包括：

- 当前进程 PID、模块基址下的静态指针和缓存堆地址都重新校验；缓存地址必须命中真实签名，不一致才进入分块特征扫描。
- NBA 核心队 ID 必须精确等于校准集合 `{0..6, 8..29, 31}`，2K 的全明星槽位 7 和 30 不进入 30 队列表。
- 焦点球员、Jordan/Olajuwon 双锚点、制服组 Doc/Rick 双锚点通过后才能开始入库。
- 内存数值必须完整读取；读失败不会替换成 0。内存浮点字段还必须是有限值。
- 30 队都要有非空名单；球员位置码必须属于 0–4；球队和球员的观测字段必须完整。
- 全量球员池先写入每个存档自己的临时 SQLite 文件，完成 3,000 条以上有效记录、Jordan/Olajuwon 锚点和历史新秀类型码检查后，才在批次成功后原子替换正式文件。
- 所有赛况、场均、伤病等当前来源没提供的字段保持 `NULL`，审计会扫描整批而非只看抽样行。
- 新的采集快照不会根据工资单独伪造球队竞争阶段、教练安全状态、轮换或交易挂牌评估；数据不足时生命周期记为未分类，`team_monthly_evaluations` 留给后续有证据的决策评估。

## 校准与地址变化

`src/memory.py` 为 64 位 Win32 API 声明了参数和返回类型。`scan_pattern` 只扫描已提交且可读的内存区域，按 1 MiB 分块读取，并保留跨块命中。地址缓存位于 `database/runtime_memory_map.json`，用途仅是减少下次定位时间；每次采集仍需根据当前进程签名验证。

数据库快照、球队 JSON 和审计凭证不保存绝对运行时指针。教练历史隔离区保留旧记录以便恢复；正式 teams 表只使用 `RUNTIME_ONLY`，全量 player pool 的 `memory_addr` 留空。内存地址只能在当前进程校准成功后临时使用。

每次运行都要验证当前 PID、模块基址及缓存锚点；PID 或模块基址变化时明确废弃旧堆地址，当前进程中缓存签名失效时也重新扫描。一次实际游戏重启（PID 5224 → 1608）的全扫描恢复已通过，随后新缓存重复采集也通过；同一 PID 的缓存命中和模拟 PID 变化仍不能单独代替真实重启证据。Python 工具执行通道未继承桌面管理员令牌，项目启动器 `scripts/run_admin_data_capture.ps1` 会请求 UAC 提权，再由管理员 Python 子进程执行。完整验收证据见 [23_RESTART_CAPTURE_VERIFICATION.md](23_RESTART_CAPTURE_VERIFICATION.md)。

## 制服组数据

旧实现把制服组前 30 个槽位直接写成教练，并把原始 byte 当成 franchise ID，导致队伍映射不可靠。新采集把校准数量范围内的完整结构写入 `staff_pool_observations`，并保留 raw TEAM_ID 与“候选/未映射”状态。没有独立验证槽位与球队关系之前，不填正式 `coaches` 表。

现有旧版 `coaches` 行因来源和球队映射均无可验证凭证，会被完整复制到 `coach_mapping_quarantine` 后从正式表清空；这些行不会丢失，但不会继续被当作已确认的主教练数据。

## 入库清单、审计和 GM 闸门

- `snapshot_integrity.py` 对快照元数据、关联赛季工资规则、本批球队/球员/成长/评估/raw staff 行生成 SHA-256 摘要；球员池 SQLite 独立计算文件摘要。GM 使用的工资帽和奢侈税线从已绑定的 `seasons` 行读取。
- `audit_sampling.py` 是确定性 Python 校验器，不调用大模型。它使用批次摘要派生固定随机种子，复核球队、球员与 staff 原始结构样本，检查全批 NULL 策略、30 队 ID、球员池锚点、SQLite quick_check 和外键。审计文件名仍叫 `ai_sampling_audit_*.json` 是历史兼容名，不表示 AI 参与。
- 审计凭证包含当前入库清单摘要、数据库行摘要和球员池摘要，并记录实际 UTC 审计时间。入库清单或源文件改变后，旧凭证失效。
- `gm_engine.py` 在每次决策前重新计算摘要并检查凭证；数据库变化、球员池变化、不同存档凭证或任一失败校验都会关闭闸门。
- GM 由玩家在数据交付后另行触发，仅读取已审核事实并输出 `PROPOSED` 建议，不写游戏内存。`gm_engine.py` 的旧 Python 启发式候选生成器不再由采集/初始化调用；其只读审计闸门继续服务于数据校验。当前数据没有 cap holds、roster charges、例外和完整交易账本，因此不能认证交易合法，也不生成数据库中不存在的选秀权。数据与执行新窗口入口见文档 27/28。

## 当前赛季范围

自动入库只接受 `season_year=2022`，对应本项目已配置的 2021-2022 工资参数和 1984 历史选秀挂接。其他赛季必须先提供经确认的赛季规则数据，脚本拒绝把旧工资帽套用到新赛季。

## 核验命令

以下只做无写入静态语法和 schema 检查：

```powershell
python -c "import pathlib; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in pathlib.Path('src').glob('*.py')]"
```

当前实机验证记录：隔离存档 `restart_validation_20261016` 的 `PRE_RESTART`、`POST_RESTART` 和 `POST_RESTART_REPEAT` 三批次分别通过全部 25 项审计（`PASS_VERIFIED`）。每批为 30 队、466 名现役球员、3,319 条有效全局球员和 78 条制服组 raw 结构。物理槽位仍为 3,320，Slot 0 被拒绝。实际 PID 5224 → 1608 后首次自动重扫 8627.44 ms，重复采集校准 8.11 ms；前后所有已采集球队字段、阵容字段、球员池解码字段及制服组身份一致，新进程下全部 3,319 条球员 BLOB 与内存逐条一致。此次实际重启与缓存复用通过；跨更多重启的稳定性仍需积累样本。

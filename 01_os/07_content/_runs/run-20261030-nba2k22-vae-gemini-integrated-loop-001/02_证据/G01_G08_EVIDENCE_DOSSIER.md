# G01–G08 证据分级与真实缺口档案 (Evidence Dossier)

> **任务标识**：`NBA2K22-VAE-GEMINI-INTEGRATED-LOOP-20261030-001`  
> **执行模型**：Gemini Flash 3.8（Human 声明标签）  
> **上游 Base SHA**：`45cc45cae0550ddcda192a2179ea48509b27f6ee`  
> **固定目标 PE SHA256**：`1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5` (`NBA2K22.exe`)  
> **版本**：Stage02 Evidence & Gap Dossier v3 (Incorporates P1-08, P2-11, P2-12 Auditor Fixes)

---

## 1. 证据等级体系说明 (Evidence Hierarchy)

本档案严格遵守非通胀分级原则，任何后一级结论不得仅凭前一级推断：

1. **`SOURCE_RESEARCH`**：外部指南、历史 NBA 机制文献、社区讨论与官方说明（不等于本局 PC22 实现）。
2. **`STATIC_CODE`**：PE 二进制静态反汇编、结构体布局、位段宽度、RVA 锚点（不等于已具备可调用原生函数）。
3. **`OFFLINE_FIXTURE`**：基于已验证结构体在 Python/Node VM 中构建的离线沙箱与测试用例（证明数据编解码逻辑）。
4. **`LIVE_READBACK`**：通过只读 Reader/内存采样真实读取到的游戏运行态数据（证明字段实时存在）。
5. **`UI_VERIFIED`**：游戏内部图形菜单（如设置滑块、轮换表、交易提案）直接目视观察到变动。
6. **`SAVE_RELOAD_VERIFIED`**：跨游戏存盘、重启进程后重新加载该存档，变动依然有效。
7. **`COMPETITIVE_OBSERVED`**：在真实 3D 比赛或日历模拟（Calendar Sim）中观察到统计指标的统计学演变。
8. **`UNKNOWN / NOT_RUN`**：当前环境未验证、未授权或尚未观察到的状态，绝不伪称已有证据。

---

## 2. G01–G08 逐项取证与缺口审计表

| 编号 | 核心验证目标 | 优先级 | 证据等级 (当前状态) | 已确证技术依据 (Primary Evidence) | 关键限制与剩余缺口 (Residual Gaps) | 运行时处置策略 |
|---|---|---|---|---|---|---|
| **G01** | **当前存档、Build、模式、Scene 与 PE 身份** | **P0** | `STATIC_CODE` / `OFFLINE_FIXTURE` | 1. 目标 PE SHA256 确认为 `1727ad72...`；<br>2. `roster_association_profile.json` 包含内存签名特征码；<br>3. 离线沙箱支持 `save_id`、`game_build`、`game_mode`、`scene` 字段结构。 | 1. 未连接活体进程时，实时 `save_id` 与游戏日期无法直接唯一证明；<br>2. MC 与 MyLEAGUE 底层配置差异尚未经过全模式对比。 | **安全门控**：缺少活体存档核验时，Profile 状态置为 `STATIC_SPEC` 或 `UNKNOWN`，禁止执行任何写入操作。 |
| **G02** | **目标参数 UI 与 Getter 一致性、USER/CPU 消费** | **P0** | `STATIC_CODE` / `OFFLINE_FIXTURE` | 1. `config/state_io_native/settings.json` 确证滑块 `0..100` 结构；<br>2. `court.json` 包含 `proposed_user` 与 `proposed_cpu` 独立字段。 | 1. **(P1-08 诚实核定)**：`settings.json` 中 `max_contract_rating` 保持 `min=70, default=40` 的原始静态源冲突，属**未纠正的源缺陷/异常 (OPEN_SOURCE_DEFECT / UNKNOWN)**，不得谎称已纠正；<br>2. 某些滑块在游戏内部是单向消费还是双向绑定仍需实机确认。 | 字段原值、单位、侧别（USER vs CPU）必须显式区分；未确证者保持 `UNKNOWN`。 |
| **G03** | **Played/Sim Quarter、双 Normalize 开关与场内/日历统计** | **P0** | `SOURCE_RESEARCH` / `STATIC_CODE` | 1. `K05_K10_K11_WORLD_RULES_SIM_HISTORY_SAVE.md` 明确界定了 2K22 的双 Normalize 开关：<br> - `Normalize Minutes to Sim Stats`<br> - `Normalize Played Minutes to Sim Minutes`<br>2. 两种单节长度（Played Quarter: 1..12 min, Sim Quarter: 1..12 min）在底层属于完全独立的整数字段。 | 1. **(P2-12 诚实核定)**：双 Normalize 字段在运行态进程内的具体内存地址映射尚未经只读 Reader 动态证实，当前仍处于 `UNKNOWN_PENDING_LIVE_READBACK`；<br>2. 无法在离线环境下直接验证其场内/日历换算生效。 | **F02/P0-04 硬性约束**：R06 比赛观察上下文必须同时强制要求 `save_id`、`engine_path`、`played_normalize_on`、`sim_normalize_on`、`played_quarter_minutes`、`sim_quarter_minutes`，任一项不匹配判定为 `INCOMPARABLE`。 |
| **G04** | **Coach 设置场景模式、球队身份与读回** | **P1** | `STATIC_CODE` / `OFFLINE_FIXTURE` | 1. `runtime/coach_poe.js` 证明通过 `coach.apply_gameplan` 修改 Coach 结构体 `+316` 字节低位可调整 POE_D1；<br>2. `coach_settings.json` 明确了 RunPlay (0..100)、Zone (0..100)、Bench (0..15/0..100) 映射。 | 1. `coach.apply_gameplan` 仅更新当前内存中的 Coach Projection，未写入存档中的持久化 Gameplan；<br>2. 跨场次保存需要依赖游戏自保存。 | 标记为 `CURRENT_COACH_PROJECTION_ONLY`，严禁宣称已实现跨存档持久化。 |
| **G05** | **联盟交易、签约与选秀时点及权限** | **P1** | `LIVE_READBACK` (交易) / `STATIC_CODE` (签约选秀) | 1. `src/approved_trade_executor.py` (`ownership_transfer_v2`) 在实机已成功完成 CHI/DET 交易，维护 `+0xCB1` 与 `+0x1047` 人数；<br>2. 依据 `PLAYER_RULES_20261021_V4` 废除 3 年限制，支持 5 届未来签；<br>3. FA 报价与撤回合同已由 Codex 离线闭环。 | 1. **(P2-12 诚实核定)**：三方交易在当前已有适配器与方案中完全不受支持 (Proposal buffer 仅有 2 队槽位)；**该限制属于当前工具适配器边界，不等于原生引擎二进行反汇编证明了引擎全局绝对不支持**，引擎层级真实支持状态标注为 `UNKNOWN_IN_ENGINE`；<br>2. 选秀大会签约动作未实机认证。 | 三方交易严格保持 `UNSUPPORTED_BY_CURRENT_TOOLS`；非双队交易一律拒绝。 |
| **G06** | **Player 真实字段、WORLD_ADMIN 权限与来源时点** | **P1** | `STATIC_CODE` / `OFFLINE_FIXTURE` | 1. `config/state_io_native/training.json` 确证 `player_training` (stride 796) 偏移 `+0x318` 标志位：<br> - `position` (bits 8..10, 0..5)<br> - `player_type` (bits 11..15, 0..8)<br> - `intensity` (bits 16..18, 0..5)<br> - `is_intensity_overriden` (bit 20)；<br>2. 徽章（Badges）与倾向（Tendencies）静态位段已由 REA 目录整理。 | 1. 个人训练模板各位置实际 UI 下拉列表与底层映射依然为 `UNKNOWN`（GAP-ST-01）；<br>2. 修改球员属性属于世界维护行为，需要显式的 `WORLD_ADMIN` 权限。 | 个人训练预设模板写操作维持 `DEFERRED_NOT_AUTHORIZATION`，仅提供只读 Reader。 |
| **G07** | **同 Save Game ID、自然比赛观察轨迹与 Side/Normalize 记录** | **P0** | `OFFLINE_FIXTURE` / `UNKNOWN` | 1. 建立了标准的比赛观察数据结构（Game ID、日期、双方比分、高阶指标、混淆因素）；<br>2. 明确了 3D 快速模拟 vs Calendar 模拟的数据差异模型。 | 1. 当前离线开发环境无连接活跃游戏进程，无法产生实时 `COMPETITIVE_OBSERVED` 数据；<br>2. 真实比赛随机性需要多样本窗口（至少 5-10 场）。 | 离线原型中将观察状态置为 `NOT_OBSERVED` 或 `OFFLINE_FIXTURE`，严禁伪造比赛数据为 `RECORDED`。 |
| **G08** | **可恢复独立测试存档、回退权限与原值保留** | **P0** | `OFFLINE_FIXTURE` / `STATIC_CODE` | 1. VAE 试验前置检查（`TrialPreflight`）强制要求提供 `restore_plan`（回退方案）与 `expected_before`（修改前确证原值）；<br>2. 试验执行前必须备份原值字典。 | 1. 外挂系统没有受控的“原生进程内存快照/恢复”API；<br>2. 若写入失败，必须依赖应用层反向写回原值或恢复备份存档文件。 | **绝对安全红线**：若缺少明确的 `restore_plan` 或快照为非 live CAPTURED，`TrialPreflight` 状态立即置为 `BLOCKED`，拒绝执行。 |

---

## 3. 证据约束与禁止伪称事项

1. **禁止混淆研究文献与实机实现**：NBA 官方 2021–22 CBA 规则仅作为业务背景参考，2K22 PC 离线引擎实际支持的操作必须以 PE 反汇编和内存实测为准。
2. **禁止在未运行游戏时声称 LIVE 状态**：在当前纯离线工作区环境下，所有涉及游戏实时内存的状态统一为 `OFFLINE_FIXTURE`、`STATIC_SPEC` 或 `NOT_RUN`。
3. **严格保留 UNKNOWN 边界**：
   - 各位置个人训练模板 UI 显示名称与 9 种 `player_type` 的 1v1 映射：`UNKNOWN`；
   - 跨赛季自然模拟下不同 `player_type` 对具体属性的成长换算公式：`UNKNOWN`（交由 2K 原生引擎黑盒计算）；
   - 三方交易原生引擎支持能力：`UNKNOWN_IN_ENGINE`（适配器当前标记 `UNSUPPORTED_BY_CURRENT_TOOLS`）。

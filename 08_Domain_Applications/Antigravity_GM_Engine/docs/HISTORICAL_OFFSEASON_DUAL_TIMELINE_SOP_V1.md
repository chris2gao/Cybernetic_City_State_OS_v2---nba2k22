# NBA 2K22 休赛期双轨历史线交易与强制签约标准化作业规范 (SOP v1.0)
# (Historical Offseason Dual-Timeline Transaction & Signing SOP v1.0)

> **文档标识**: `SOP-OFFSEASON-DUAL-TIMELINE-V1.0`  
> **适用角色**: `data_analysis_and_decision` (数据分析与决策角色) & `role-developer` (REA Native 执行)  
> **上位规范**: [26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md](26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md) | [44_NATIVE_TRADE_INTERFACE_PROTOCOL_V2.md](44_NATIVE_TRADE_INTERFACE_PROTOCOL_V2.md) | [45_NATIVE_SIGNING_INTERFACE_PROTOCOL_V2.md](45_NATIVE_SIGNING_INTERFACE_PROTOCOL_V2.md)

---

## 一、 双轨时间轴与职责边界定义

1. **现代历史线（Modern Historical Timeline）**
   - **对象**：2021-22 赛季游戏初始阵容名单包含的所有球员（**严格排除 1984 届及以后选秀产生的球员**）。
   - **时间窗口**：在每个休赛期，提前完成**下一年完整赛季结束前**（含选秀夜、自由市场、赛季中交易截止日至季后赛结束）真实历史发生的全部交易与自由球员签约。
   - **终点**：**至 2027 年休赛期正式结束**。
2. **纪元历史线（Era Historical Timeline）**
   - **对象**：仅调整从 **1984 届选秀**开始进入 NBA 的球员（后续每年依次为 85、86 …… 至 2021 届）。
   - **时间窗口**：以 1984 届新秀入盟第一年为 **1984-85 赛季**。第 1 赛季结束休赛期完成 **1984-85 赛季结束前**的全部交易与归属（含首届新秀母队归位）；第 2 赛季结束休赛期完成 **1985-86 赛季结束前**的全部交易与归属，以此类推逐年推进。

---

## 二、 休赛期标准作业五步流程 (5-Step SOP)

### Step 1：只读采集快照盘点（无需人工贴概要）
* 玩家完成休赛期采集并告知存档名（如 `MyLEAGUE0005`）及当前赛季编号；
* 模型通过只读 URI (`mode=ro`) 连接 `C:\nba2k22\saves\<SAVE_ID>\league_state.sqlite` 与 `player_pool.sqlite`，自动分离：
  1. **在约球员池**（`player_monthly_stats` + `player_source_details` 的 `raw_struct` 偏移 `0xF4` 提取 `native_player_id`）；
  2. **自由球员池**（对比上赛季名单及实机 `sign.fa_available_pool` 扫描结果）；
  3. **纪元选秀球员池**（按 `draft_year >= 1984` 识别）。

### Step 2：双轨整季真实变动对齐与分流
* **库外球员**：当前游戏库中不存在的球员直接跳过不补建；
* **离队球员**：保持原样，不专门下放或裁员（超 15 人名额由新赛季游戏 AI 自动裁剪）；
* **分流规则**：
  * **在约球员（非 FA）**：走交易通道（`TRADE_EXECUTE_AGREED_PACKAGE`），**保留原合同不修改**；
  * **自由球员（FA）**：走强制签约通道（`sign.process` RVA `0x12BDE70`），合同金额**对标游戏内同能力、同年龄、同位置球员**，合同年限按真实历史时间线设定；
  * **选秀权**：默认清空选秀权与现金；仅当游戏强制要求双向资产时，才用次轮签配平。

### Step 3：生成 REA Native V2 标准化规格书
* 在 `C:\nba2k22\exports\YYYYMMDD_offseason_dual_timeline_execution\` 生成：
  * `<SEASON>_offseason_trade_spec.json`（`SPEC-NATIVE-TRADE-V2.0`）
  * `<SEASON>_offseason_signing_spec.json`（`SPEC-NATIVE-SIGNING-V2.0`）

### Step 4：REA Native 实机执行（零裸写）
1. **交易批量执行**：调用 `TRADE_EXECUTE_AGREED_PACKAGE`（`AGREED_DIRECT_PROCESS`）完成全部在约球员跨队过户；
2. **自由球员强制成交**：在游戏 `FA_SIGNING` (`Period == 22`) 阶段，通过 `sign.process(proposal, ptr(0), 0, 0x6fea8977, 0x72a)`（`Status=6 ACCEPTED -> 8 SIGNED`）一次性批量完成自由球员强制签约落袋。

### Step 5：全联盟 30 队实机名册回读验收
* 调用 `team.by_id` (`0xF40EB0`) / `READ_TEAM_ROSTER_BASIC` 一次性回读全部 30 支球队现役名册；
* 输出 `TRADE_EXECUTION_RECEIPT.json` 与 `SIGNING_EXECUTION_RECEIPT.json`，确认核心球员 100% 归位后交付玩家检查并存盘，准备进入新赛季。

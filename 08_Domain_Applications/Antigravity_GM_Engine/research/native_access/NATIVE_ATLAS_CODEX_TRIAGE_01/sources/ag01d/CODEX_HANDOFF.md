# AG-NATIVE-01D Codex 工程交接说明 (CODEX_HANDOFF)

> **交接对象**：Codex 系统集成与工程验收模型  
> **交接方**：Antigravity Gemini Flash 3.8  
> **分支**：`dev/native-io-exploration`  
> **日期**：2026-10-22  

---

## 一、工程背景与本轮成果总结

在 AG-NATIVE-01D 中，我们完成了终极联盟中**单场比赛、赛季统计与多角色数据关联**的原生结构实机逆向与验证：

1. **单场比赛数据流 (Transaction Log)**：
   - 全局静态根插槽位于 **`NBA2K22.exe + 0x0632B4B8`** (`0x14632B4B8`)，指向 3.5MB 的 `SEASON` 结构体。
   - 包含 1,232 场 60 字节的 `SEASON_GAME` 结构体与 45,292 槽位 24 字节的 `BOXSCORE_STATBANK`。
   - 实机验证揭幕战（雄鹿 vs 篮网、湖人 vs 勇士），单场球员得分之和与比赛终局比分**严格 100% 物理守恒**。

2. **单场与赛季累计闭环验证 (Sum-to-Season)**：
   - 提取库里全部 16 场比赛的单场 BoxScore 并累加，与 `ROSTERDATA Slot 24` (`PLAYER_STATS`) 中的原生 48 字节总账完全对齐，证明了原生数据引擎的交易流水与总账关系。

3. **5 大统计切片确定性聚合**：
   - 证明胜负切片 ($Total = Win + Loss$)、先发替补切片 ($Total = Starter + Bench$)、主客场切片 ($Total = Home + Away$) 均可由单场原生流水确定性计算得出，零 AI 幻觉。

4. **纠正 Slot 44 误判**：
   - 纠正了 01C 将 Slot 44 视为赛程的初步假设。Slot 44 确认为 **`TEAM_MATCHUP_MATRIX`**（36 支球队各 35 条记录，步长 24 字节，记录交锋胜负），真正的赛程在 `ROSTERDATA` 中对应 **Slot 10**（1,232 条记录，步长 32 字节）。

5. **球员卡片多赛季生涯履历链表**：
   - 发现 `PLAYER` 结构体中 `+0xFC`（当前赛季）与 `+0xFE..+0x126`（历史赛季连续 uint16 数组）直接索引 Slot 24，实现球员卡片生涯数据秒级回溯。

---

## 二、关键工程接口与代码复用建议

Codex 在系统集成时可直接复用或参考以下模块：

### 1. 专业解码器 (`research/native_access/AG_NATIVE_01D/decoders/`)
- **`boxscore_decoder.py`**：
  - `BoxScoreDecoder.decode_game_header(raw_game: bytes)`：解码 60 字节比赛概况、双方总分与 LineScore；
  - `BoxScoreDecoder.decode_player_statline(raw_stat: bytes, is_home: bool)`：解码 24 字节球员统计行并计算 TS%、eFG%、GameScore；
  - `BoxScoreDecoder.decode_full_boxscore(raw_game: bytes, raw_statlines: bytes)`：单场全量解码并执行得分守恒自检。
- **`season_stats_decoder.py`**：
  - `SeasonStatsDecoder.decode_player_stats_record(raw_stat: bytes)`：解析 48 字节赛季总账；
  - `SeasonStatsDecoder.extract_player_career_indices(raw_player: bytes)`：提取球员卡片生涯历史索引链表；
  - `SeasonStatsDecoder.aggregate_game_splits(single_game_boxscores: List[Dict])`：执行 5 类统计切片聚合与可加性方程校验。
- **`matchup_matrix_decoder.py`**：
  - `MatchupMatrixDecoder.decode_team_series(raw_35_records: bytes, team_slot_idx: int)`：解析一支球队对全联盟 35 个可能对手的交手记录。

### 2. 数据库管道与 Schema
- `export_to_sqlite_01d.py` 提供了规范的五层数据模型生成逻辑，可无缝对接 `database/match_history_schema.sql`。

---

## 三、测试运行与验证基线

本地离线测试全量通过：
```powershell
pytest research/native_access/ -v
# 41 passed in 1.15s
```
- AG-NATIVE-01: 18 tests
- AG-NATIVE-01B: 8 tests
- AG-NATIVE-01C: 6 tests
- AG-NATIVE-01D: 9 tests

所有测试均基于真实实机导出的 binary/json fixtures，无外部网络依赖，无进程依赖。

---

## 四、后续建议任务 (Next Steps for Codex)

1. **统一数据采集引擎对接**：
   - 将 `BoxScoreDecoder` 与 `SeasonStatsDecoder` 的逻辑整合入 `src/match_history_reader.py` 与 `src/source_extensions.py`；
2. **球员卡片端点开发**：
   - 在 GM 查询与交互层增加基于 `player_career_index` 的球员生涯数据查询接口；
3. **完成最终的代码集成评审与合流**。

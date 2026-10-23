# FLASH_DISCOVERY_FILL_CONTRACT_V0 — Flash 逆向字段填充与 Codex 交接

**研究输入合同，不替代 OS。** 每轮依据当前 `master`、实际 Task Packet、Model Routing 与 Run；不能因本文件拥有历史偏移就获得访问本地 DCR、读写进程、编辑存档或推进游戏的权限。

## 输入与分轮

输入 `GAME_UI_FIELD_CATALOG_V0.json`（888 条候选研究索引）、`GAME_NATIVE_OBJECT_HINTS_V0.json`（75 个历史槽）、`GAME_ACTION_DISCOVERY_SEED_V0.json`（207 条**全部禁用执行**的调查项）及 R04–R07 对应研究。第一轮 R00 确认游戏 exe 版本、真实当前存档、ROSTERDATA/SEASON 静态根、对象 stride/count 和目标 PC22 UI 页；R01 球员，R02 比赛，R03 Team/Operations，R04 Coach/Training，R05 World/History，ACTION-R01/R02 只读调查，R90 问题收敛。

## 四环邻域发现法

从一个有证据的锚点出发：①结构内部字节、bitfield、对齐和数组边界；②合法指针、Getter、跨对象与反向引用；③目标游戏页面相邻标签、单位与筛选；④不同球员/球队、已有比赛与时间对照，至少一个负对照。原生结构和 UI 名称必须经过反证；旧绝对堆地址不能作永久 locator；不调用副作用未知的 Getter/Setter。

重点避免：Slot44 曾被错误叫赛程，AG01D 修订为 TEAM_MATCHUP_MATRIX 候选；StatBank 容量≠有效场数；99 外站倾向标签≠99 原生字节的逐位对应；2bit 无法直接编码五个互斥状态；20 年历史 Decoder 固定循环≠游戏跨季寿命上限；Native PlayerID/ GameID/ slot 的跨世界和跨代际唯一性未证。年龄采用三个基础字段优先公式，不把独立内存年龄作为必寻字段；游戏 UI 高阶值与外挂派生结果不可混标。

## 每轮机器 Delta 最小字段

```json
{
  "field_id":"PLAYER.years_pro",
  "game_build_hash":null,
  "save_binding":null,
  "observed_at":null,
  "ui_page_manifest_ref":null,
  "native_object_and_offset":null,
  "field_status":"RESEARCH_ONLY",
  "raw_sample_restricted_ref":null,
  "decoder_fixture_ref":null,
  "value_type":"UNKNOWN",
  "negative_controls":[],
  "adjacent_candidates":[],
  "failed_hypotheses":[],
  "evidence_refs":[],
  "all_applicable_objects_enumerated":false,
  "sensitivity":"UNKNOWN_FAIL_CLOSED",
  "next_probe":"Read-only PC22 years-pro against PLAYER candidates"
}
```

每轮产出 `ui_page_manifest`、`field_atlas_delta`、`native_object_delta`、相关 `action_atlas_delta`、`unresolved_findings`、原始日志与脱敏证据、OS completion pointer。新字段需要稳定 ID 和 `projection_of` 关系；未知值和失败实验保留，不能为了覆盖率猜名字；历史结论改写须带 supersedes 与证据。将 `RESEARCH_INDEXED`、`NATIVE_LAYOUT`、`FIXTURE_PASS`、`LIVE_UI_MATCH`、`ALL_OBJECTS_ENUMERATED`、`PIPELINE_INTEGRATED`、`PUBLISHED_QUERY`、`SAVE_RELOAD` 分轴标记，不自动升级。

## Codex 升级

高价值字段经两次不同实证路径仍未解决，或遇到复杂生命周期、分配/释放、批量写入关联问题时，给 Codex：固定 SHA、具体目标/原生根、试过的 offset 和 getter、UI 对照、负样本、失败假说、未解机制、可复核的成功判据。Codex 独立验证后回传修订 Delta。任何真实写游戏、批准执行、存档更改和自然成长修改不得在 Flash 研究中自行启动。

# F-01 / F-02 / F-03 有界工程修复收尾

日期：2026-10-26。任务 `nba2k22-world-data-review-fixes-01`。
原常规赛工程交付冻结于 `17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`，本任务只处理独立审核的三项发现；持续施工没有重新开启。
本次已完成工程候选，交 Human 组织独立审核；独立审核 NOT_RUN，master 集成 NOT_PERFORMED。

## 已固定的结果

| finding | 实现与有效边界 | 直接证据 |
|---|---|---|
| F-01 | 每档/年度/来源族一次 LIVE_READ 基线；同年后续明确请求只追加有来源证明的新事实，字段级稀疏保存、幂等、冻结冲突隔离；四个年度 Reader 接入所选记录路径 | `test_review_annual_additions.py` 14 项；`annual_additions.py`、`annual_ledger.py`、v25 DDL |
| F-02 | schedule 与 game_box 共用严格 Native/Canonical 人物及得分判定；状态来源时间与 Box 来源时间分开 | `test_review_box_completeness.py` 7 项；人数相同但身份不同、得分 NULL、Native 得分不同三反例 |
| F-03 | 20 个真实采集入口保留合法原 receipt；事务回滚后独立登记冲突和 artifact 引用，保留 LIVE_READ，显式返回隔离结果 | `test_review_live_conflicts.py` 7 项；受控适配器，不冒充真实 Windows 采集 |

功能源码提交：F-02/F-03 `d55c72f3`；F-01/v25 `9ac289de03be821d229f22e23fc6955bed8b74bb`。
OS 受控验证精确候选：`b847f717df6702fe6251872d64aed476ac707f6f`。
计划 SHA256：`9751ea4d323f17a55b4e9b5ca4f67305d493645c54478c8a6f430a65496c3887`。
后续交付提交只补本 run 的证据、快照和交接；应用目录与受控验证候选保持相同。

## 验证结果与证明范围

- `managed_verify run` 和紧接其后的 `inspect` 均成功：329 项完整回归、SQLite smoke、v24→v25 最终副本旧事实核对，三项必需检查全部成功。
- 28 项针对性测试覆盖一次基线+多次同年补录、已知事实重复/撤回、零值补录、稀疏字段、四来源所选读取、跨档/隐藏字段权限和原 receipt 冲突隔离。
- 原 v24 的 100 张表、1,470,952 行所有旧列逐值比对一致，只排除明确更新的版本头；原文件前后 SHA256 均为 `f76b943e4c716748b4df1c8f6c94779fb57ebb312bbeeb9e4d4dfd97a024b218`。
- 新库 v25：101 张 STRICT 表、1,789 列、1,561,421 行、仍为 42 个成功采集单元。增加 14 条字段目录和 90,455 条来源身份/幂等索引，不能算作新增真实游戏业务事件。
- 最终副本 SHA256 为 `f3ae5fd169845b7ad87fc3da96be37e59f514eb612a82e5b0e2afc0b2a7af753`；integrity_check=ok、foreign_key_check=0、restricted rows=0。
- 最终真实副本上四族年度事实分页可读；12 场有 Box 的比赛中 schedule 与 game_box 的单元、严格完整性及派生分数一致。查询前后文件 hash 相同。
- v25 连续 gzip 流四分片逐片校验、拼接流 hash、完整解压字节数及最终数据库 hash 均一致。快照是工程交付备份，不是全季或 100 年容量测试。

完整受控证据为 `evidence/managed/`（原始字节保留），外部原件位于 checkout 同级 `review-fixes-managed-20261026-01/`。
原始失败的开发回归及迁移比较器证据仍保留：旧 fixture 缺少新 refresh_kind/旧表数，以及校验器最初未区分14条新字段目录。这些均已修正并通过最终检查，没有删除失败记录。
这不是硬件安全证明、真实新增奖项场景或独立验收。本任务 Native 游戏读取0、游戏写入0、日期推进0、Computer Use0、新采集单元0。

## 原件、升级与交付

原 v24、原 save.json 和原游戏 MyLEAGUE0003 未改变。绑定仍是 `nba2k22_test_01 / MyLEAGUE0003`。
最终 v25 在本 run `_runtime/migration/world-v25-final.sqlite`；可发布快照为 `snapshots/world-v25.snapshot.json` 及四个 `.gz.partNNN`。
快照包含事实库与来源账本；外部原始 Native artifacts 沿用原任务各 increment 的归档引用，本任务没有逐一重新验证所有历史 raw 文件。
恢复时按 manifest 顺序拼接、解压到新文件并核对 hash，禁止自动覆盖旧库或切换绑定。

正式完成指针：`08_结论/review_fixes_completion.yml`；最终工作分支回读与交付提交以 `08_结论/publication-receipt.json` 为准。
修复协议、请求格式、四 Reader 成本/语义限制详见应用目录 `REVIEW_FIXES_F01_F02_F03.md`；下一任务入口为本 run `NEXT_TASK_HANDOFF.md`。

## 保留给后续任务的限制

普通 refresh 不自动发现同年所有新事实；补录请求须由后续真实场景证据产生。当前 ledger 的幂等身份限于已有来源记录/字段或稳定 canonical 键，不证明跨 Native 槽位的历史人物/同奖项等价性。
部分 league 奖项组补录仅保留 Native 行，不声明已取得完整 canonical 收奖人组。旧单单元历史查询可能返回稀疏补录，组合年度事实用 `annual-facts`。
教练历史年份/phase、历史人物/共享引用生命周期、部分旧 Box 主体、UI 单位/舍入、官方排名资格规则等仍按原成熟度记录，不因回归通过升级为已验证。
Human 已批准延期：Overall；下一任务提供完整生命周期场景；完整真实赛季后再测容量并决定保留期限。季后赛、休赛期、选秀/自由市场、跨季、100年、游戏写入均未验收。
没有新增人格决策、自动游戏操作或 master 合并。完成本次三项修复交付后停止施工。

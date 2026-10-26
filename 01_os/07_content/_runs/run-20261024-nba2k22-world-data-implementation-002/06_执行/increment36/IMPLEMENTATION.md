# Increment 36 — 同一采集批次的联盟榜单

本轮补齐实际查询能力：球队胜率排名与球员累计/场均/命中率榜单，使用已绑定的真实 v24 SQLite。
新增 `league_views.py`，由公开 query、CLI 和历史 acquisition-cutoff 查询共同调用；不新增表或采集来源。

`standings` 和 `player-leaderboard` 先按 season_id 和 exact phase 选取一个最近成功单元，再筛选/计算。
未提供 phase-code 表示 SQL NULL，不把未知阶段假定为常规赛；指定 unit 未匹配时不回落其他来源。
球员 team_scope 不混合，多 scope 必须明确选择，literal NULL 另有明确参数；team_id 只筛选统计行原值。
保留 totals、来源时间/等级/完整性、未知阶段/原始 finality。每个比率只来自同一行。

支持已有累计计数、篮板合计（攻防篮板之和）、同一行出场数的场均计数、三类投篮命中率。
原始分钟不转换，不引入 Overall、进攻/防守公式或未经证明的高级统计公式。
最低场次/出手数只是用户门槛，不能冒充官方资格。缺失、不合法和零分母按原因计数排除。
精确有理数排序并列使用 competition rank 1,1,3，同值按 canonical ID 稳定展示；并列可跨分页。
每页最多100，继续页强制固定 unit_id。官方分区种子、同战绩规则和 UI 舍入仍未证明。

验证脚本与完整日志见本目录。数据库比对使用独立 SQL 取分子/分母与 Fraction 计算，遍历每个指标、
所有分页、exact rank 和 source unit，同时检查 CLI、历史 cutoff 及过期不可见来源。
首次新测试中一个负得分 fixture 被现有 SQLite CHECK 正确拒绝；改用合法 NULL 缺失反例。
该修正不放宽生产校验。最终执行结果以 verification-report.json 和 verification/operations.json 为准。

本轮没有 Native 进程读取、Computer Use、数据库写入、新 capture unit、年度历史读取、容量工作或游戏写入。
真实数据库现状与 hash 必须由脚本复核；不重新生成未改变的 v24 快照。
Human 允许不交付综评的范围保持不变，其他困难项目继续留在应用 DIFFICULT_ITEMS.md。
这是一段已实现查询增量，不是整套九域系统、独立审核或 Human 最终验收完成声明。

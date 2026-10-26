# NBA2K22 / OS 阶段02 · v25 独立 Windows 只读核验任务包（待 Human 发布）

**任务状态：PREPARED_NOT_DISPATCHED。必须由 Human 明确选择独立模型及授权测试机器；本文件不派单，不启动工程开发。**

## 一、只读独立复核范围

- 仓库：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`
- **审查固定版本**：`a3927fb150a213201e404cca043ced4f57409bd1`（v25 候选，不是 master）
- 上游 Human 批准需求：本规划分支的 `01b_需求结果_A_v1_草案.yml` 中 `A-v1-RC01`。
- 阶段 02 问题：`RQ-02-02`。核实而非开发：v25 已有 Schema/Reader/Codec/测试/数据迁移是否满足声明；识别可复用范围、反证和必要场景缺口。
- 建议由未负责原修复实现的独立模型执行，确保“独立复核”不只是开发者自查。

## 二、操作权限和硬禁止

1. 允许：Git 固定 SHA 只读检查，**如 Human 另外授权并提供隔离测试环境**，可对现有测试代码及独立副本执行已有单元/回归、Schema DDL、临时模拟数据 smoke 和独立迁移校验。
2. 禁止：修改仓库工程源码、Schema、测试代码或真实数据库；直接对任何真实 MyLEAGUE 存档写入；连接/注入/写入 NBA2K22 进程；改变存档、场景、游戏时间；启动 GM/教练/球员外挂；合并 master；在未经 Human 授权的机器上操作。
3. 所有写入型测试（数据库初始化/合成 fixture）仅可位于独立临时测试目录；不接触真实世界线数据库。不能保证测试完全隔离则停止并报告阻断原因。
4. 有真实游戏 Native 读取需求时**先停止**，由 Human 就目标机器、进程、存档与操作范围单独裁决；本任务不包含游戏侧取证。
5. 不得将开发者历史日志或模拟 fixture PASS 直接判定为本次独立 Windows 原生读回通过。

## 三、具体核验清单

| 验证ID | 执行目标 | 验收证据 |
|---|---|---|
| IND-01 | 从固定 SHA 的 SQL 与字段字典分别核算表/列、SQLite STRICT 与字段类型一致性；预期观察候选101/1789，但以实际证据为准 | 实际遍历与计数、表名/类型 diff、固定 Git sha |
| IND-02 | 核对 `refresh.py:SOURCES` 实际20组 Reader 注册、模块和 callable 存在性，区分注册、可调用、模拟成功与 Native 真实成功 | 逐Reader静态/受控测试报告、未支持场景标 UNKNOWN |
| IND-03 | 在 Human 提供的隔离 Windows 工作树中对固定SHA运行现有回归（开发日志先前声称329通过、28定点通过），严格记录实际测试数、失败、耗时、系统/SQLite版本 | 未修改测试源码的原始 stdout/stderr、退出码、环境、命令 |
| IND-04 | 用生成的临时/合成数据库执行现有 `cli.py smoke`，核对SQLite schema、foreign_key_check、integrity_check、Schema与字典映射；fixture不冒充LIVE_READ | 临时数据路径、完整可复现命令、清理记录 |
| IND-05 | 如 Human 明确提供可用的 v24 数据库**只读副本**，验证旧值与原键值完整保留的 v25迁移；若没有原始数据库，不根据开发者日志虚构执行 | 输入副本来源/哈希，输出副本哈希和逐表对比，否则BLOCKED_NOT_ACCESSIBLE |
| IND-06 | 审核F-01年度补录、F-02关联与F-03赛程Box严格性修复，检查错误分支、被拒绝的无证补录、假阴性/假阳性测试覆盖 | 针对每个finding的测试证据、可重现反证或未证条件 |
| IND-07 | 对照 `A-v1-RC01`，说明哪些能力可复用、哪些需要 S1–S8 实际游戏场景取证、哪些不能作为安全Native写入证据 | 独立结论、分歧、严重程度及后续所需Human操作 |

**已有静态复核基准（不是须无条件同意的结论）**：同目录 `02_evidence/01_v25_结构与Reader只读盘点_v1.json`、`01_内部证据_v1.yml`、`证据索引_v1.yml` 和 `边界记录_v1.yml`。

## 四、独立输出文件契约

**输出目录（仓库根目录起算的完整路径）**：
`01_os/07_content/_runs/run-20261026-nba2k22-lifecycle-consensus-001/02_evidence/external_independent_v25_review/`

- `scope_and_environment_v1.yml` — 输入SHA、机器/隔离环境、命令、权限和实际审查范围（canonical）
- `static_verification_v1.json` — IND-01/02 的逐项值与不一致清单（canonical）
- `test_execution_v1.yml` — IND-03/04/05实际是否执行，返回码/真实测试数/结果/被阻断的具体原因（canonical）
- `logs/` — 原始stdout/stderr、测试参数及哈希（raw_evidence；未运行不应造空日志声称已验证）
- `findings_v1.yml` — IND-06/07 原子发现/严重程度/准确源锚点/复现与局限（canonical）
- `review_verdict_v1.yml` — `supported|partially_supported|refuted|blocked`，只对已实测的范围下结论，列未覆盖条件（canonical）
- `readme_v1.md` — 清楚说明哪些文件缺失、哪些测试无法获得环境或原数据库（canonical）

Human 若用其他工具产生非 canonical 结果，必须标明 `derived_mirror` 并保存对应SHA，不得独立修改。**实际回存由 Human 控制**，交接模型只能把经过路径、版本和哈希核查的输出纳入阶段02证据索引。

## 五、报告重点

必须分开结论：
- CODE_EXISTS / STATIC_VERIFIED：代码或结构确实存在且可核对；
- DEVELOPER_REPORTED：源于已有开发日志，还未在本次独立复核重新运行；
- INDEPENDENT_TEST_REPRODUCED：在新的受控独立环境实际运行通过；
- NATIVE_GAME_SCENE_UNVERIFIED：未以真实游戏场景绑定验证；
- NOT_WRITABLE_PROOF：只读、模拟与回放不能证明游戏内存可写。

最终不得把`A-v1-RC01`的 Human 产品目标、阶段02源审查完成、阶段03实现方案确定、或者工程完成混为一谈。

**后续讨论/真实游戏取证**：S1–S8 子场景时间、UI内容和Native对象如何验证，需要另外分配受控场景工作；本任务不能替代它，也不允许独立模型自行推进游戏。

# BIC 第一批离线工程 · GPT-6 系列审核（固定提交）

**审核对象**：`a3e28e186f198e731c76b74f939da2950b5d15bd`（相对 P0 `17bca5c5e34a4bc3b153c38634681962e1600ec7`：提前 3 提交、30 变更文件）。  
**审核角色**：`independent_review`；只审核固定来源，不修改开发代码、不实机操作、不合并 master。  
**判断**：**离线工程主体已交付、已完成的回归证据可信；完整 DEV-01 需求验收仍有两项 P1 定向整改，系列最终门暂不签 PASS。**  
**精确机读回执**：本目录 [BIC_BATCH1_SERIES_REVIEW_v1.json](BIC_BATCH1_SERIES_REVIEW_v1.json)。

## 一、肯定的成果（以源码/回执为依据）

| 结果 | 固定证据 | 审核判断 |
|---|---|---|
| 复用 WorldData，球员/球队按存档、赛季、观察截止时间读取 | `bic_baseline.py:44-106`，原生 `query.py`、`observation_scope.py` | 主体成立。时间范围和强制存档绑定有代码及针对性测试 |
| 旧赛季空 save 绑定、原生身份冲突、不混合采集单元 | `bic_baseline.py`、`test_bic_baseline.py` | 采用保守回退 `DATABASE_LOCAL_ONLY` 而非错误认证 |
| 徽章持有状态/等级可查，资格 XP/游戏作用不乱猜 | `bic_baseline.py:131-149`、Stage02 徽章证据 | 限定的离线基准能力成立；PC22 MyLEAGUE Native 资格仍待证 |
| 离线 2×2 效应和交互计算 | `bic_experiments.py`、`test_bic_experiments.py` | 算术正确；非合成场景返回 `NOT_CAUSALLY_IDENTIFIED`，未伪报真实游戏因果 |
| CLI 和离线自动测试 | `bic_cli.py`、`verify_offline.py`、原始 stdout、receipt | 归档显示 34 passed、1 warning，退出码 0；日志 SHA-256 经独立复算匹配 |
| 历史 Jokic/Siakam 只读示例 | `historical_examples.json`、`STAGE02_DEV01_REAL_READ_EVIDENCE.json` | 证明既有归档可查询；`UNBOUND`、空 build/save fingerprint、`REAL_DATA_NOT_VERIFIED` 保留正确 |

**本次审核没有在原开发环境重新执行 34 个 pytest**。我独立查看了代码、测试和留存日志，并复算 stdout 哈希；历史 975 MB SQLite 文件也未在审核环境重新打开。不得把本次静态审核夸大成新的动态运行。

## 二、系列完成前必须修正

### P1 / BIC-R01 — `knowledge_status` 未达到正式数据/机制知识准入要求

- **源码**：`world_data_prototype/bic_baseline.py:11-21`。
- **合同要求**：DEV-01 `knowledge_status(field_or_mechanism, mode, version)` 应识别字段/机制、模式和版本、真实来源与可信程度、未知或冲突。
- **实际**：目前只是 `knowledge_status(source_grade, observed)` 的来源等级映射，不能回答某个字段或机制在指定 PC22 版本/模式下是否具备可用证据。
- **定向整改**：保留已有 mapper，复用现有字段 catalog/原生来源信息，补一层面向调用方的领域知识状态查询。明确版本/模式适用性和 UNKNOWN；增加已支持、无来源、跨模式/版本及冲突的负例。不建第二套知识数据库。

### P1 / BIC-R02 — `coverage_report` 无法定位具体覆盖缺口

- **源码**：`bic_baseline.py:108-128`。
- **合同要求**：按领域/字段展示覆盖、缺失、陈旧和受限项，不能把注册字段直接当实际有读数。
- **实际**：仅合计 `NOT_OBSERVED/STALE/WITHIN_REQUESTED_AGE` 并列出有值的 `unit_id`；`restricted_fields` 只是固定字符串 `WITHHELD`。空徽章族 `player_badge_values=[]` 时，遍历返回 `NOT_OBSERVED=0` 且不显示该领域没有读数。该边界通过完全相同的遍历逻辑做了独立隔离复核，**不是在原库中重新跑全套测试**。
- **定向整改**：输出不泄露原生私有字段的逐领域覆盖详情、缺失/陈旧字段标识和空族状态；保持原数值汇总、采集单元与证据来源。增加空 badge 族、缺失字段、WITHHELD、混合批次负例。

## 三、低风险完善项

- **P2 / BIC-R03**：`factorial_2x2(synthetic, mode)` 允许 `synthetic=True + FAST_SIM` 或 `synthetic=False + SYNTHETIC` 的矛盾组合；虽然仍未声称真实因果，后续知识归因会有模式语义歧义。应拒绝矛盾组合或分开“测试数据性质”和“拟研究的游戏模式”。
- **P2 / BIC-R04**：`--disable-warnings` 让归档只显示 `1 warning`，并不能独立证明这是“既有告警”。下轮保留具体 warning 类型、位置及历史对照即可，无需全量旧回归。

## 四、必须长期保留的证据边界（不是新增代码错误）

现有历史 SQLite 的真实存档与构建身份尚未独立认证；比赛模式不能从 FRANCHISE/REGULARSEASON 直接推断为 Fast Sim/CPU3D；徽章 XP 和真实比赛效果没有 PC22 原生认证；Stage 01–07 正式 OS 验收尚未执行、PRMS 未持久化。这些继续标记 `UNKNOWN`/`NOT_CLAIMED`，不得用本次 34 项回归代替。

## 五、复审与执行建议

**裁决：`TARGETED_REMEDIATION_REQUIRED_BEFORE_FULL_BATCH1_DEV01_ACCEPTANCE`。**

Codex 使用已有 Human 批准的离线工程权限继续**一个小范围内部 Loop**，优先修正 BIC-R01、BIC-R02，顺带处理两项 P2；只运行新功能相关及已定义的 34 项回归，记录真实命令/退出码和新固定 SHA。不需要重做 P0、再次提出同一套需求或重新取得普通离线工程授权。

提交后 GPT-6 对固定新 SHA 做简短差异复审。该复审只确定离线工程系列代码验收；**正式 OS 阶段验收和任何 Native 实机操作仍是独立门**。当前不得据此合并 `master`。

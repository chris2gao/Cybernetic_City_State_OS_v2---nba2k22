# BIC 第一、二批 · OS 与集成候选统一独立审核

**审核岗位/模型**：`independent_review / GPT-6`  
**固定交付**：`bb886c50028e8332849f5b03ad54711a16870cfa`  
**实际测试候选**：`4998a43a3f9f94d1013e574e99d29b4c3d666de4`  
**两批已通过审核的业务代码**：Wave1 `aec3dbaacd1d56b0c7cc1d40c2f70607493b9a4b`；Wave2 `cdcb293f8a690725cf9168225cc2046ab0574b2b`。  
**机读裁决**：本目录 `INDEPENDENT_REVIEW_v1.json`。  
**审查方式**：GitHub 固定提交、源码和归档回执核查；不改游戏、不改工程分支、不合并 master，不代替 Human 签字。

## 一、分线裁决

| 事项 | 本次裁决 |
|---|---|
| **Wave1+Wave2 工程集成候选** | **`PASS_TECHNICAL_CANDIDATE_READINESS`**。已达到“可提交下一项治理/集成审批”的技术证据要求 |
| **正式七阶段 OS** | **`NOT_PASSED_VERIFIED`**。官方固定 Core 的真实拒绝成立 |
| **母需求 A0/A v2** | 原 Human 批准保留且未被推翻；新的规范化机器表示待正式 owner 认可 |
| **整个 BIC 的八项成功标准** | **未满足、不得宣称完成** |
| **直接合并 master / 运行真实游戏** | **本审核不授权** |

两个结论不冲突：通过离线代码测试不能自动创建 owner 阶段接受回执；阶段状态待验收也不能推翻已经具备的离线接口、诊断和原生计划的技术证据。

## 二、工程集成候选复核

GitHub 实际比较：原 master `66f8f73f1a91597f4562b834c2acad332ad9de5b` 到最终交付前进 **13** 提交、无落后；其中 master 到已审核 Wave2 为 **8** 提交、83 个变更文件。已测试候选到最终交付再前进 **3** 提交，85 个新增文件全位于本次 Run，未改动任何已审核业务源码或旧测试。

工程归档给出 `65 passed, 1 warning in 32.33s`，managed 进程 `32.8195s`、退出码 `0`；已溯源告警仍为 `test_player_details.py::test_manifest` 返回字典导致的 `PytestReturnNotNoneWarning`。三个离线 CLI 检查成功，`query_at` 截止时间隔离输出 80/90，合成库读前读后相同；managed verify 和 inspect 的归档状态均成功。首次因为新 CLI 包装结果误读导致的失败和随后修复的成功尝试均保留，没有删除失败历史。

**独立 SHA-256 校验**：我重新计算六个关键 BIC 源码/测试文件的 SHA-256，与 `source_inventory.json` 一致；重新计算实际 Core runner、成功回归原始 stdout、CLI 原始 stdout 和 Core 拒绝 stdout 共四份摘要，也全部吻合。执行方报告 83 个源码清单及 102 个本次交付文件校验通过，**审核者未独立逐一复算所有 83/102 个文件**。本次没有在用户 Windows 工作区重跑 65 项 pytest 或重新打开大型历史 SQLite。

Stage04 的七个测试文件已在本次回归**之前**做技术哈希冻结，但 `formal_stage04_freeze_approved=false`，不能冒充正式 owner 冻结。当前没有新增大 SQLite/备份或 >10MiB 文件；仓库原有较大 JSON 与三个 Native 样本 DB 保持与 master 相同的 Git blob。不存在本次任务新增的游戏进程、REA Native 写入或存档修改。

## 三、正式 OS 七阶段复核

Core 固定版本：`08d8e534a3438269aa7d7eb1b080ab11c172f462`。

- Core 静态检查：真实退出码 `0`，含义是 OS 安装/静态结构条件满足，**不是**本次完整 Run 通过。
- Stage01 A0/A v2：规范化器真实执行 `0`，`requirement_findings=[]`；Stage02 的 `evidence_findings=[]`。原始四个源 Git blob 保持不变。规范化记录 **23 项表示/来源变化**、其中 7 个证据状态的保守枚举映射；原标签保存在 provenance 中。字段级映射文件支持机器表示衔接，**但不能代替 owner 对归属和批准有效范围的正式确认**。
- 官方已提交候选 `38532c3f6774e41c70640c3ad3a25d93cde6d855` 完整 CLI 校验：真实退出码 **`33`**，原始 findings **`identity:workflow_stage_01_requirement_modeling`**。运行器二进制来源脚本 SHA256 `e0bec3f978d6df6619afa8699bea620c6ecf209906a7d0d6952ed11773cf00e8` 复算一致；正式 stdout SHA256 `db6217899979b503861889a83ae26501f34f117fd9c8adee5787bde3a6d6c12b` 复算一致。
- 已提交的七个阶段候选仍为 `candidate_pending_owner_acceptance`，缺少有效 `plan_acceptance`、`completion_acceptance` 和阶段控制历史，因此在 Stage01 身份门即被拒绝。**后续正式历史/发布门均未执行**。不得声称它们通过，也不能声称它们已经被运行器逐项否决。
- Stage03 映射了 Wave1/Wave2 **离线子范围**成果，不能把尚未交付的完整篮球自主对抗能力特别是 `SC-05` 宣称已经实现。Stage04 正式冻结、Stage05 owner 接受和 Stage06/07 对本次 Run 的独立验证仍未形成真实正式凭证。
- PRMS `NOT_SAVED`，仅由固定 Git Run 作为已交付的恢复路径。这是真实限制，不作已保存声明。

**特别提醒**：不得通过把 YAML 的 `status` 字符串强行改为 `complete`、补空白 Human 签名或回填不存在的历史审批来绕过 owner 处置。那样即使绕过第一个身份门，也不能满足真实治理要求。

## 四、审查后应采取的最小路线

### 首选：独立的 Wave1/Wave2 离线子范围 Run

由 Human/合法 OS owner 明确批准或拒绝**建立新的、完整七阶段的 Wave1/Wave2 离线子范围 Run**；以未被修改的 BIC A0/A v2 为上位来源，只将已完成的事实查询、诊断、离线 Native 执行计划、安全性和可复现的离线测试列入这个 Run 的验收标准。原完整 BIC Run 的八项成功标准与未完成项继续保留，不能被子 Run 关闭。

按现行 Core 机制真实形成 Stage01 规范化确认的 owner 处置、Stage02–05 阶段 plan/completion 接受及正式 Stage04 冻结，再对已批准的有界范围整理 Stage06 的真实执行证据和 Stage07 的独立验收。**不能追认此前未发生过的形式验收**；如验收前后顺序被 Core 要求，必须作未来真实流程，必要时重跑已允许的离线测试。

生成完整已提交的 Run 后，使用精确 `--candidate` 执行官方 `validate`，记录退出码、findings 及历史/发布门结果。只有真正的 PASS 才能申请正式阶段关闭。

### 集成建议

工程集成候选保留并进入单独 Human 集成裁决队列；**目前不直接合并 `master`**。完成适用 OS 路径及批准后，重新核对当时的 `master` HEAD、快进关系、当前回归和大文件清单，才可依已批准方法进行主线集成。

Human 当前最有价值的一项决策是：是否批准采用**独立离线子范围 Run、父 BIC 目标保持未完成**的治理路线。选择并授权后，不需再要求 Codex 重做 P0、DEV01–05 或重复审核已通过的代码。

## 五、审查边界

本次只读审查 GitHub 固定源码、阶段候选、原始回执和已有审核；未实际操作 NBA2K22、运行 Native Setter、重开大型 WorldData、重复执行 Core CLI 或在用户 Windows 环境重跑 pytest。历史 `UNBOUND`/`REAL_DATA_NOT_VERIFIED`、PC22 MyLEAGUE 徽章资格/XP 和 3D/FastSim 效果仍属于待研究证据，不因离线集成候选通过而升级。

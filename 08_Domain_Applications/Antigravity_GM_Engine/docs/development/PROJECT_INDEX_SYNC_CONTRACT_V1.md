# NBA2K22 项目总索引与模块总账：任务启动和完成同步合同 V1

**性质**：NBA2K22领域的长期协作规范，服务于现有Cybernetic City-State OS；不修改OS全局Core协议，不建立第二套OS任务系统。

## A. 真实启动加载规则

- 进入`08_Domain_Applications/Antigravity_GM_Engine/`后**先读`PROJECT_INDEX.md`、`docs/development/PROJECT_MODULE_REGISTRY_V2.json`**。这是本领域所有新规划、开发、逆向、审阅任务的高优先级导航，不取代根`AGENTS.md`和OS入口。
- 从Registry识别`affected_module_ids`，再按`docs`加载该模块入口、按`artifacts`查询现有实现。先比对当前分支HEAD与master、来源PR；若文档在集成/规划分支而非master，不能假定它尚未存在。
- 与游戏机制有关的开发：P04（游戏机制知识库）为必读导航；需要REA开发：P09（原生业务控制、REA经验交接）为必读；数据采集/Schema要读P01/P02/P03；三类角色/执行调度要读P05/P06/P07/P10。
- 不强制读取整个R07的694条异构资料；只读当次任务需要的guide/catalog。不要为已经存在的信息要求Human重复讲解。
- 若某入口文档失效、找不到或内容与当前源版本不一致，记录`INDEX_STALE`并修正引用；不能假装已读。

## B. 任务包额外必填的NBA2K22领域字段

```yaml
task_id: ...
base_ref: ...
base_sha: ...
affected_module_ids: [P04, P09]
source_refs_read:
  - PROJECT_INDEX.md
  - docs/development/PROJECT_MODULE_REGISTRY_V2.json
  - docs/game_mechanics/README.md
  - research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md
planned_capability_changes: [...]
execution_scope: PLANNING_ONLY | OFFLINE_CODE | REAL_GAME_APPROVED_BATCH
```

若只有单个根任务入口则按OS已有task_packet存放上述字段，不必复制新的OS格式；**新增内容**仅为受影响模块ID、源文件版本与能力变化计划。

## C. 开发完成后的同PR原子索引同步

在**本次开发同一分支、同一个PR**完成下列步骤，然后才标记可以交给下一窗口：

1. 实施真实范围内的源码/研究/证据变更，记录固定任务、commit、游戏Build/存档（若有）、实际验证范围；不通过虚构的实机状态填充INDEX。
2. 对`docs/development/PROJECT_MODULE_REGISTRY_V2.json`中**每个受影响的模块**更新：
   - `status`、`last_update`、`docs`、`artifacts`（只更新确实改变的项）；
   - `latest_task_refs`至少加上`TASK_ID + PR/commit + evidence`；
   - `last_verified_evidence`（有新证据时加，没有就保持历史值，不能写“实机通过”）。
3. 对`PROJECT_INDEX.md`中对应模块摘要和最新任务链接同步，尤其角色能力、数据成熟度及“下一步还缺什么”。
4. 若发生`NativeActionRegistry`或`read_catalog`变更，同时更新**原生能力目录本体及结果文档**；若出现游戏研究资料补充，更新`docs/game_mechanics/README.md`/相关guide及`SOURCES.md`，但不随意覆盖历史原文。
5. 若修改批量执行架构与角色输入字段，更新`ROLE_BATCH_NATIVE_EXECUTION_ARCHITECTURE_V2.md`与能力值域/机读Action需求模型；不由执行器替角色决策。
6. 当前task run的`completion_pointer`或任务结论加入索引同步校验结果、`index_sync_commit`，并报告旧索引与新代码是否仍有已知不同步。

**不可把“更新总索引”理解为重复抄入所有长报告**；索引只保存小摘要、状态、模块责任、精确版本与链接；详细权威事实仍在原报告与源码里。

## D. 交付时的机器判定与失败状态

```json
{
  "task_id": "EXAMPLE",
  "affected_module_ids": ["P09", "P10"],
  "source_refs_read": ["PROJECT_INDEX.md", "PROJECT_MODULE_REGISTRY_V2.json"],
  "new_or_changed_actions": ["TRADE_EXECUTE_AGREED_PACKAGE"],
  "evidence_state": "SPECIFIC_LIVE_EFFECT_VERIFIED",
  "latest_commit": "40hex_sha",
  "index_sync_commit": "40hex_sha",
  "remaining_gaps": ["draft_pick_combo_not_live_verified"],
  "index_status": "SYNCED"
}
```

- 任何模块没有更新索引或旧结论与当次证据矛盾：`INDEX_SYNC_PENDING`，不能声称完整交接。
- 读取了总索引但没有按模块加载：`MODULE_SOURCES_NOT_LOADED`。
- 只运行静态解析/fixtures：`OFFLINE_TESTED`或`STATIC_RECOVERED`，不能写成`GAME_LIVE_VERIFIED`。
- GitHub PR为Draft且尚未合并时：仍保留`DRAFT_NOT_MASTER`；新的任务必须定位明确的分支和固定SHA。

## E. 内容所有权与范围

- OS全局协议（根AGENTS、Core-owned文件）保持原来的owner；本规范只写D领域的`AGENTS.md`、`PROJECT_INDEX.md`、`docs/development`。
- 当前未部署自动强制CI/Hook或自动化代理**去替模型写索引**。真正的自动保证需要未来经Human批准的持续集成检查；现在采用“入口必读 + 同PR索引同步 + 远端回读”的可执行协作合同。
- 全量游戏资料来源纳入游戏机制目录，但不会无证统一PC22和次世代的底层RVA、ABI或布局；业务玩法候选按Human口径统一盘点。
- 索引加载不授权新的REA进程附加/原生业务调用，不修改已批准的数据读取链，也不动master。

## F. 本轮登记（2026-10-28）

PR #18：在此前基于PR #17的角色能力盘点上，新增总项目地图/机读Registry/本同步合同、REA Codex经验文档原文以及新版批量执行架构。新任务由领域AGENTS主动指向此总索引；完成后须按上述条款同步。本次无游戏运行或源数据架构迁移。

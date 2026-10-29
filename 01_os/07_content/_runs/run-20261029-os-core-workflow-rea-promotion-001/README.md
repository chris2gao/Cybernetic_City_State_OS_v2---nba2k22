# OS Core Workflow + REA 统一升级 · 规划 Run 总索引

**任务 ID**：`OS-CORE-WORKFLOW-REA-PROMOTION-20261029-001`  
**状态**：`PLANNING_READY / ENGINEERING_NOT_STARTED`  
**正式目标**：将 NBA2K22 实践中的双层需求模型、通用研发规范及 REA 可选工具能力共同提升到 Core；NBA保留专有REA Profile，分阶段实现、一次总体交付。
**Human 方向**：不兼容旧任务；不要过度设计；Workflow与REA可以放在一起按阶段执行。保留Core七阶段身份，直接替换Stage01活动语义。
**工程Owner**：Codex；独立审核由非实现Owner承担。仅覆盖 Core + NBA，其他领域不更新。

## 当前应读的正式材料（按顺序）

| 顺序 | 相对路径 | 用途和状态 |
|---|---|---|
| 1 | `03_统一实施/01_Workflow开发规范_REA统一五阶段工程计划_v1.md` | **最新Human有效实施方案**：S1 Stage01，S2通用开发规范，S3 Core REA工具，S4 NBA Profile，S5统一集成 |
| 2 | `03_统一实施/02_Codex统一工程开发任务提示词_v1.md` | **Codex唯一工程主任务交接合同**，初始资料、权限、每阶段交付和最终测试 |
| 3 | `02_W1设计/01_阶段01双层需求建模_直接替换方案_v1.md` | Human确认的不保留旧单层A兼容层的Stage01最小替换 |
| 4 | `01_W1信息收集/01_Core_v0.2_NBA_v0.4_差异与兼容首轮核对.md` | 历史源代码差异证据；早期保留旧版本建议已由后续Human否决 |
| 5 | `00_任务章程_升级范围与串行路线_v0.1.md` | 最初范围和来源记录；原“REA下一独立任务”顺序已由后续Human裁决取代 |

**不会自动读取完整历史的源文档导航**：

- Core `01_os/01_workflow/01_需求建模/方法论_v0.2.md` 与 NBA（PRMS规划分支）`01_os/01_workflow/01_需求建模/方法论_v0.4.md`。
- Core `01_os/04_skills_and_tools/README.md`、`01_os/05_registry/skills_and_tools_v1.yml`，现有 `check-jsonschema / mutmut / cosmic-ray` 示例。
- NBA PR #18 的 `PROJECT_INDEX.md`、`PROJECT_MODULE_REGISTRY_V2.json`、`PROJECT_INDEX_SYNC_CONTRACT_V1.md`、`research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md`、`ROLE_MODEL_MECHANISM_GUIDE.md`、`VALIDATION_RESULTS.md`（固定PR18 HEAD `094f1aa641f93dec2277707ad9dbf5bdb0341247`，仍须fresh-read）。
- 既有PRMS规划归档分支 `planning/os-prms-a0-confirmed-01b-20261028` 下 `02_信息收集/02_NBA开发经验升级Core可迁移性审查_v1.md` 和 `04_方案设计/05_PRMS串行实施与Core升级路线图_v1.md`；仅作历史规划来源，当前新的统一分阶段决定优先。

## 完成判据

- S1–S4各有实际实现和针对性测试，S5有统一回归与可审计证据。
- Core主PR和NBA领域配套PR应各自反映真实代码变化并更新索引、源码 SHA、运行测试与未运行项。
- Core master/NBA master合并前须按现实的发布流程单独验证；本规划 Run 不直接授权推送/合并master。
- 不把只是文档/fixture的成果冒称为真实REA可调用，不把历史NBA交易效果当Core跨平台RE A效果。
- 任务完成后在本索引登记实际 Core/NBA 提交和独立审核结果，不能只更新聊天结论。

## 最新可用状态（2026-10-29）

- Core/master `e075cdf288a765b7bfd2f4891c8f384404da16e1`
- NBA/master `4a7d3de013fdddee66b64c0a8a31b6d346982540`；Core Issue #11 已关闭。
- NBA PR #18 `094f1aa641f93dec2277707ad9dbf5bdb0341247` 仍为Draft，NBA master尚未包含该项目机器模块索引文件。
- 本规划分支基于更早NBA/master；**Codex不得把本规划分支直接合并进master**，应从开发时新master建立独立工程分支，准确读取这里的归档文件。

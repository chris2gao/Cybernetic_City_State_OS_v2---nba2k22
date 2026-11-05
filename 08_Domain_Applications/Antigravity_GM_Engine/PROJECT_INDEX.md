# NBA2K22 项目资料与模块入口

BIC series remediation extends P02 field/mechanism knowledge queries and detailed coverage, and P10 factorial mode validation. Fixed reviewed base `a3e28e186f198e731c76b74f939da2950b5d15bd`; evidence in repository-root `01_os/07_content/_runs/run-20261104-nba2k22-bic-series-remediation-001/`. Independent difference review remains pending.

BIC offline candidate (P02/P07/P10) adds scoped player/team baselines, badge fact interpretation and synthetic factorial contrasts. Entry `world_data_prototype/BIC_READONLY.md`, evidence `01_os/07_content/_runs/run-20261104-nba2k22-bic-offline-engineering-001/` from repository root. This is Human-authorized offline implementation with formal OS and independent acceptance pending.

本索引随 PR #27 提交主线审核。P00–P12 继承 PR #18 固定版本的导航分类，逐项区分当前树内入口与固定研究来源。正式 G2 以其独立目录和发布记录为准。

先读取项目基线和实际任务包，再从模块注册表选择相关模块。交接记录采用精确源码 SHA、影响模块、验证范围和未解缺口。修改模块时同步索引与对应记录。

启动时记录 `affected_module_ids`、`source_refs_read` 和实际基线。代码变化所在 PR 同步更新本页及相关模块记录，附测试证据和剩余缺口。已有 Core 的 project_context 工具可检查对应候选。来源规则见 [PR #18 的固定同步合同](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/PROJECT_INDEX_SYNC_CONTRACT_V1.md)。

[机器可读模块注册表](docs/development/PROJECT_MODULE_REGISTRY_V2.json) · [REA 领域 Profile 与操作说明](research/rea_core_profile/README.md)

| 模块 | 责任 | 入口状态 |
|---|---|---|
| P00 | OS bootstrap/governance | `ESTABLISHED_OS_PROCESS` |
| P01 | Parallel world data architecture | `TARGET_ARCHITECTURE_NOT_ACCEPTED_DDL` |
| P02 | Existing SQLite ingestion/query/publishing | `LEGACY_EXISTING_IMPLEMENTATION_SCOPE_LIMITED` |
| P03 | Native game data source and decoding | `STATIC_PROFILE_INTEGRATION_CANDIDATE` |
| P04 | Gameplay mechanisms knowledge base | `R01_R07_RESEARCH_COMPLETED_WITH_GAPS` |
| P05 | GM decision agents | `EXISTING_GM_CORE_PARTIAL_AGENT_WORLD` |
| P06 | Coach tactics and Coach persona | `PARAMETER_RESEARCH_AND_NATIVE_SUBSET_PERSONA_PENDING` |
| P07 | Player profile/persona | `PLAYER_PROFILE_RESEARCH_PERSONA_PENDING` |
| P08 | Trades/contracts/draft/scouting/training | `CROSS_DOMAIN_MIXED_MATURITY` |
| P09 | REA native-action controller | `STATIC_PROFILE_INTEGRATION_CANDIDATE` |
| P10 | Role action inventory/batched native execution | `HUMAN_REVIEW_REQUIREMENTS_FIRST_PASS` |
| P11 | Basketball/plays/era knowledge | `RESEARCH_ASSETS_NOT_FULL_ROLE_RUNTIME` |
| P12 | Historical records and source authority | `LEGACY_LEDGER_ARCHIVED_NEEDS_FRESH_EVIDENCE` |

P03 与 P09 通过领域 Profile 对接固定 Core 静态工具。P01、P02 可从当前树加载 WorldData Schema、初始化 CLI 和 Calendar Reader。P09、P10 可从当前树加载 facade、Bulk、Outbox 和 SeasonCycleHost。P12 的历史数据恢复走 [来源迁移索引](research/history_source_resolution/README.md)。

- PR #18 Draft 来源 `094f1aa641f93dec2277707ad9dbf5bdb0341247`，提供导航、动作目录、绑定、Reader 和逐例验证。
- PR #26 已合并至 NBA master。Profile 保留其测试过的原始源码引用 `aee5a9109ea5cd0a5c7bc4adb750c64a1603afec`。
- PR #28 已合并历史来源解析入口，其 WorldData 归档映射与 Profile 的 PR #18 固定研究目录分开。
- 本次主线接入基线为 NBA `dfa08af8bb6e4abf1cd8ad304f47b096ecc38167`。历史实机证据继续绑定原案例和输入。

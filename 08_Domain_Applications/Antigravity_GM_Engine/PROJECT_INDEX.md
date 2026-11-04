# NBA2K22 项目资料与模块入口

本索引是统一工程任务 S4 的候选入口。P00–P12 继承 PR #18 固定版本的导航分类，逐项区分当前树内入口和外部候选来源。正式 G2 以其独立目录和发布记录为准。

先读取项目基线和实际任务包，再从模块注册表选择相关模块。交接记录采用精确源码 SHA、影响模块、验证范围和未解缺口。修改模块时同步索引与对应记录。

启动时记录 `affected_module_ids`、`source_refs_read` 和实际基线。代码变化所在 PR 同步更新本页及相关模块记录，附测试证据和剩余缺口。已有 Core 的 project_context 工具可检查对应候选。来源规则见 [PR #18 的固定同步合同](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/PROJECT_INDEX_SYNC_CONTRACT_V1.md)。

[机器可读模块注册表](docs/development/PROJECT_MODULE_REGISTRY_V2.json) · [REA 领域 Profile 与操作说明](research/rea_core_profile/README.md)

| 模块 | 责任 | 入口状态 |
|---|---|---|
| P00 | OS bootstrap/governance | `ESTABLISHED_OS_PROCESS` |
| P01 | Parallel world data architecture | `TARGET_ARCHITECTURE_NOT_ACCEPTED_DDL` |
| P02 | Existing SQLite ingestion/query/publishing | `LEGACY_EXISTING_IMPLEMENTATION_SCOPE_LIMITED` |
| P03 | Native game data source and decoding | `OFFLINE_PROFILE_CANDIDATE` |
| P04 | Gameplay mechanisms knowledge base | `R01_R07_RESEARCH_COMPLETED_WITH_GAPS` |
| P05 | GM decision agents | `EXISTING_GM_CORE_PARTIAL_AGENT_WORLD` |
| P06 | Coach tactics and Coach persona | `PARAMETER_RESEARCH_AND_NATIVE_SUBSET_PERSONA_PENDING` |
| P07 | Player profile/persona | `PLAYER_PROFILE_RESEARCH_PERSONA_PENDING` |
| P08 | Trades/contracts/draft/scouting/training | `CROSS_DOMAIN_MIXED_MATURITY` |
| P09 | REA native-action controller | `OFFLINE_PROFILE_CANDIDATE` |
| P10 | Role action inventory/batched native execution | `HUMAN_REVIEW_REQUIREMENTS_FIRST_PASS` |
| P11 | Basketball/plays/era knowledge | `RESEARCH_ASSETS_NOT_FULL_ROLE_RUNTIME` |
| P12 | Historical records and source authority | `LEGACY_LEDGER_ARCHIVED_NEEDS_FRESH_EVIDENCE` |

P03 与 P09 通过领域 Profile 对接固定 Core 静态工具。交易、教练、球探、Bulk 和 Outbox 由领域研究及源码候选维护。实际游戏效果继续按精确历史例子、对象和输入分层。

- PR #18 Draft 来源 `094f1aa641f93dec2277707ad9dbf5bdb0341247`，提供导航、动作目录、绑定、Reader 和逐例验证。
- PR #26 源码候选 `aee5a9109ea5cd0a5c7bc4adb750c64a1603afec`，提供已有领域 facade、Bulk 和 Outbox。
- 本任务起点 `45cc45cae0550ddcda192a2179ea48509b27f6ee`。

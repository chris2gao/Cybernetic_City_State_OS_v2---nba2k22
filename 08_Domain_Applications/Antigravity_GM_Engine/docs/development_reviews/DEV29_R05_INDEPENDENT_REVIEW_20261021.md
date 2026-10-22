# DEV29 R05-A/B/C/D 独立审核与工程缺口回执（2026-10-21）

**审核结果：研究交付接受结案；PC22原生能力与选秀权V4执行同步保持OPEN。**  
**审核边界**：本次检查GitHub `main` 中真实项目文档、JSON结构和4处选秀权代码，不连接NBA2K22、不开管理员进程、不运行真实交易/签约/采集、不创建任何Agent行为程序，也**没有逐篇外网复验全部162个来源链接**。不得把代码静态审查、过去个别获批交易或社区玩法当作当前存档的完整原生效果认证。

## A. 实际检查的来源

- `config/gameplay_policy.json`，现`PLAYER_RULES_20261021_V4`；`docs/26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md`。
- `docs/game_mechanics/guides/K07_K08_K09_FRANCHISE_OPERATIONS.md`，完整§§0–29。
- `docs/game_mechanics/catalogs/R05A_FINANCE_CONTRACT_MARKET_RESEARCH_V1.json`、`R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json`、`R05C_STAFF_SCOUT_DRAFT_MECHANICS_V1.json`、`R05D_FRANCHISE_CAPABILITIES_ATLAS_V1.json`。
- `docs/game_mechanics/PROGRESS.md`、`README.md`、`SOURCES.md`、`visuals/EXTERNAL_VISUALS.md`、`docs/38_APPROVED_SIGNING_EXECUTION.md`。
- 现行代码`src/draft_assets.py`、`src/gm_core/calculations.py`、`src/gm_core/trades.py`、`src/approved_trade_executor.py`；用于直接检验V4配置与执行路径是否一致。

## B. 研究交付范围与可接受项

| 核查主题 | 本次直接核对 | 结论 |
|---|---|---|
| A财务/合同 | R05-A讨论工资帽、真实NBA与游戏业务分层、17项原生Contract注册字段、Bird/RFA/报价阶段及本机缺口 | 研究符合“玩法原料”，未引入角色谈判算法 |
| B交易/选秀权 | R05-B涵盖菜单候选、名单与资产原生结构、来源批次/持有人身份、现实2021–22 CBA与游戏世界政策分离 | 合格，PC22菜单和值域仍未知 |
| C员工/球探/新秀 | R05-C覆盖8项员工职位Enum/13个静态字段、官方同版次世代Staff资料、球探和Draft流程 | 合格，跨平台材料未冒充PC22原生接口 |
| D统一目录 | `data_research_rows` **54条**、`action_research_rows` **63条**、`crossdomain_effects` **12条**、`open_pc22_gaps` **12条**，四组数据全部实际计数一致 | 通过；`id/key`均未重复 |
| 54条数据含义 | 17合同＋10球队财务＋14名单/选秀资产＋13员工；30项`STATIC_NATIVE_REGISTERED`和其余布局/来源/研究候选 | **不等于54条当前游戏实时读数** |
| 63种操作含义 | 21市场合同＋16交易＋10球探＋10Draft＋6员工；**并非63种都存在已认证原生执行接口，只有特定普通交易/简单Pick有获批验证过的受限子集**；**53个操作仍以UNKNOWN作为合法选项值域** | **不等于63个可执行按钮** |
| 来源目录 | `SOURCES.md`中已连续引用`SRC-0001`至`SRC-0162`，缺号为0；`SRC-0162`明确说明与旧`SRC-0137`同网页 | 连续和来源限制通过；登记数≠162独立实验证据 |
| 图文与平台 | R05-D没有新增已通过原版PC22像素/版本认证的菜单图；2K19、同版次世代、现实NBA均有标注 | 符合真实性纪律 |
| 角色职责 | 用户六阶段循环与`docs/PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md`保持一致 | 没有越界创造Coach/Player人格系统 |

R05整理出的12个未知项是DEV28及其他后续工程的**有据可查待研究/待开发清单**，不是已交付的PC22原生功能。原生交易已验内容局限于过去具体批准、具体游戏对象/来源的受控记录；`docs/38_APPROVED_SIGNING_EXECUTION.md`仍说明`SIGNING_LAYOUT_VALIDATED=False`和`SIGNING_EXECUTION_ENABLED=False`。未验证自由市场真实签约事务。

## C. 选秀权V4政策：已正确更改，执行仍未同步

**玩家政策本身已在配置与规则文字中正确落实**：
`maximum_future_drafts: null`，不把原三届人为上限机械换成五届或现实NBA七年；不使用保护或Swap，资产身份`year/round/original_owner/current_owner`、真实持有方、本机资产存在性和真人逐笔批准继续是前置条件；历史1984–2020轮回没有改变。

**静态代码证据（需独立Codex最小工程工作包）**：

1. `src/draft_assets.py::trade_window(next_draft_year)`仍返回`range(next,next+3)`；此外`capture_assets(...)`把旧三届写入发布信息的`tradeable_draft_years`。**不仅规划/执行判断需要变，捕获批次生成的对外数据口径也不应继续描述未来三届为“可交易全集”。**
2. `src/gm_core/calculations.py::draft_pick_window()`仍返回未来3届且`maximum_future_drafts=3`；
3. `src/gm_core/trades.py::constraints()`仍以`DRAFT_PICK_OUTSIDE_THREE_YEAR_WINDOW`拒绝观察到的第4/5年；
4. `src/approved_trade_executor.py`规划阶段校验`pick['year'] in trade_window(next_draft_year)`，实际动作仍会拒绝第4/5年。

**推荐的工程修复合同（仅交接建议，本审核不授权Codex自行执行）**：
- 从真实`draft_assets`已观察、身份完整且当前持有人有效的资产形成可用候选，不应从`next_year+3`猜世界限制；现有读源已校验连续5届、共300条，将来超出覆盖时保持`UNOBSERVED/HOLD`，**既不改成`+5`新硬上限，也不推测可操作的未来第6届**。
- 保持`known_native_read_horizon`与`world_rule_maximum_future_drafts=null`为不同元数据字段；修订发布`tradeable_draft_years`或改为明确`observed_future_draft_years`，检查旧消费者/历史批次契约的向后兼容，不重写旧快照。
- 保持现有唯一资产ID、当下持有人、交易双方、批准tuple、保存档身份、执行器preflight/CAS、真实游戏读回与重载验证。简单双队Pick范围外保持HOLD；不能扩张到保护Swap、多队交易、员工或签约。
- 用纯离线测试覆盖未来第1/3/4/5年、观察资产缺失/持有冲突/过期批次/越界与回滚；必要时再由**用户另外批准**实际游戏验证。代码更新不等于获准执行真实资产转移。

### 发现分级

- **G04 / P1工程缺口（真实存在）**：V4世界配置与四条代码执行路径不一致，导致第4、5年合理候选遭旧政策拒绝，并向发布元数据写入三届`tradeable_draft_years`。**应列独立、最小Codex维护任务，不要求R05返工**。
- **数据/原生证据缺口（研究已正确披露）**：54数据并非实时全部采集，63概念未验证完整PC菜单合法值域（其中53项UNKNOWN），其余G01–G12待DEV28/PC22验证，不阻断R05研究结案。
- **外部来源审查限制**：已核对项目对原始来源的登记和版本区分，但未逐个复现外部网站/视频内容；后续实际PC22研究不可把社区报告升级为本机真实效果。

## D. 正式独立审核决定

**接受 `R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`，R05-A/B/C/D无需继续返工研究/补截图，不启动Agent、签约、员工或选秀执行器。** R05所需研究内容、真实来源限制、业务动作候选和缺口已经形成可用于未来独立模型与DEV28的知识原料。

R06可按[PROGRESS.md](../game_mechanics/PROGRESS.md)进入K05 3D/Sim及全局规则、K10历史/奖项/媒体信息、K11赛季推进/存档覆盖研究，**不因G04工程缺口无限停留在R05**。但在Codex完成并通过对应验证前，任何下游模型**不得据V4配置宣称第4/5届选秀权已可实际执行**。R06继续只做游戏机制和游戏原生可见信息/设置，不开发媒体人格、教练或球员的程序化行为。

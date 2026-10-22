# K07 / K08 / K09 — NBA2K22终极联盟经营机制：薪资、合同、市场、财务、员工与选秀

> **DEV29 V3 / R05-A首轮正式研究（2026-10-21）**。范围为K07工资帽/合同与球队资金、K08市场签约/交易相关约束的首批机制。**R05-B研究球员及选秀权交易与市场规则，R05-C研究员工/球探/选秀、R05-D整合经营原料与版本缺口；R05未在本轮整体结案。**
>
> **工作定位**：这里只研究游戏中有什么真实信息、可选操作及值域、NBA2K20–23机制效果、PC22本机有什么实际数据接口与限制。**不为GM写报价决策程序、不设计球员谈判人格、不开发Agent/执行器、不修改游戏、不自动给出“最优薪资方案”**。游戏世界从2021–22开始、历史选秀按1984–2020轮回；法律参考不能反过来决定当前模拟世界发生过什么。来源见[SOURCES](../SOURCES.md) SRC-0114..0128及已有[SRC-0101](../SOURCES.md)、原仓库[FA P0研究](../../development_reviews/DEV_20261017_04_OFFSEASON_FA_P0_RESEARCH.md)、[签约执行](../../38_APPROVED_SIGNING_EXECUTION.md)、[财务工作台](../../GM_FINANCE_WORKBENCH.md)。

## 0. 经济世界的四套不同“真值”

| 对象 | 真值是谁 | 目前我们能做的事 | 容易导致错误的混同 |
|---|---|---|---|
| **2021–22现实NBA CBA** | 2021年联盟官方公告、当时劳资条款 | 提供现实Salary Cap、Tax、例外、Option、Bird/RFA等定义背景 | 不能把真实2021的金额假定为本存档2023–24以后每年的游戏数值 |
| **NBA2K22游戏真实规则** | 具体存档/赛季/模式的游戏UI、真实引擎/游戏状态 | 搜索真实可见菜单/用户同版观察并记录不同年份差别 | 即使NBA CBA允许某操作，2K模拟器可能简化、阻止或错误执行 |
| **本项目已采原生数据与衍生分析** | 正式同批source、SQLite、Profile、QuerySession | 对已有合同金额/球队财务做只读计算；区分OBSERVED/CONFIGURED/SCENARIO/UNKNOWN | 数据库有字段≠真正读到可用于签约资格的业务真值 |
| **本项目外挂世界规则** | 用户批准的`gameplay_policy.json`、正式具体执行协议 | 允许交易双方自愿成交等额外业务、**不再人为限制选秀权三届窗口**、实际写入仍须玩家批准 | 不能把“外部模型达成协议”当2K已签合同，也不能借开发研究修改游戏 |

由此有四个不同判断：`现实CBA可能合法`、`2K原生UI能够操作`、`当前项目数据足以核验并计算`、`玩家已批准具体原生执行`。任何一项为UNKNOWN，不能用另一项替代。

## 1. 工资帽、奢侈税、硬帽/apron、球队资金完全不同

### 1.1 2021–22官方现实参考，不是本局最新赛季实测

NBA官方2021-08-02新闻[SRC-0114]：

| 现实2021–22项目 | 美元金额 | 机制意义 |
|---|---:|---|
| Salary Cap 工资帽 | **112,414,000** | 软帽参照；超过后常规工资帽空间不足，但符合资格可使用例外 |
| Tax Level 奢侈税起征线 | **136,606,000** | 超线可能产生递增税务责任；**不等于所有签约自动非法** |
| 90% Minimum Team Salary | **101,173,000**（官方公告按千计近似） | 现实联盟最低工资支出 |
| Non-taxpayer Mid-Level | **9,536,000** | 现实非纳税球队中产例外的当年值 |
| Taxpayer Mid-Level | **5,890,000** | 现实纳税球队中产例外的当年值 |
| Room Mid-Level | **4,910,000** | 现实有工资帽空间球队可用例外的当年值 |

2021–22现实apron**143,002,000**来自2021–22历史工资帽汇编[SRC-0115]及项目旧FA规格；不属于本次官方新闻明确给出的一项，故注明**SECONDARY_2021_ARCHIVE**。而且**apron成为某一交易或使用例外限制，并不意味着所有超apron球员签约都一律非法**；不同操作有不同适用条件。不存在一个能够单靠`payroll−cap`计算出的完整合法经营额度。

若游戏模拟到2022–23，不能继续用上一行。现实2022–23联盟后来宣布Salary Cap **123,655,000**、Tax Line **150,267,000**[SRC-0116]，但这仍只是现实参考；**实际游戏未来联赛工资帽可能由league设置、growth/sliders或事件影响**。我们的历史线不能拿现实2025–26新CBA（例如second apron）未经认证塞进2021 2K22原生制度。

### 1.2 六个常被错当同义词的经营金额

| 财务名称 | 可能包含或排除的对象 | 当前项目研究级别 |
|---|---|---|
| **Team Salary / Total Salary** | 游戏球队层的薪资总额；与逐人当期薪资、死钱/Cap Holds等不一定同口径 | native球队读数+月度发布存在，**与真正Salary Cap Table一致性未跨季实测** |
| **Payroll** | 薪资发放/球队财务栏所列支出，可能与上述合约薪资不同 | 现有队财务源有`payroll`，**单位/刷新时点和Total Salary差异待证** |
| **Budget** | 球队经营预算或总预算，是否为可支付“自由球员最高合同”由具体模式决定 | 现有`budget`静态字段；**不能自动当薪资帽空间** |
| **Staff Budget** | 受聘Coach/Trainer/Scout工资或员工预算 | 财务分析模块可能有`staff_budget`；**是否在同批真实数据已完整发布需要单独核对** |
| **Cash** | 游戏财务可见现金或符号整数 | 现有`cash`读数，编码有SIGNED解释假说未实机确认；**不能自动计算税款、球员报价资格** |
| **Cap Room / Cap Holds / Exceptions** | 球队在签约/自由市场某阶段的真实规则性容量，可能扣除自由球员预留金额、死钱、例外 | **本项目未认证完整动态Cap Holds/Exceptions/可签约额度原生来源**；`salary_cap_minus_payroll_proxy`严格只能叫Proxy |

**财务收入与票价也不等于签约资格**：现有`src/gm_core/finance.py`引用`fan_interest, ticket_courtside, ticket_lower, ticket_upper, monthly_gate_revenue`等候选。拥有售票价和关注度数据不意味着我们已证明比赛票价调高会带来多少现金、是否会降低上座、何时结算或者能用于直接超帽签约。早年MyGM Wiki列有场馆设施、媒体和广告、停车/商品等企业经营页[SRC-0127]；**这是旧模式的Business分类资料，不可认定PC22离线MyLEAGUE完整拥有所有设施、票价和老板目标菜单**。

## 2. 游戏真实可选的合同条款（不替GM决定选哪一种）

### 2.1 合同期限/金额与具体逐年薪资

2022-04 NBA2K22 MyNBA一手玩家讨论及原帖图片[SRC-0117]明确菜单出现以下**四种合同金额结构**：

| 可见报价方式 | 同版社区解释 | 原生/数值边界 |
|---|---|---|
| **Flat** | 每年金额基本不变 | 球员接受概率与UI年限合法性没有独立量化 |
| **Front-loaded / Front** | 首年较高、以后下降；回帖称每年约5% | 2K22次世代玩家说明，**不是PC22已认证固定5%的native codec** |
| **Back-loaded / Back** | 起始较低、以后逐年提高；回帖称约5% | 对球员吸引力“较高”是社区观察，不是所有球员都接受的算法 |
| **Bird** | 面向具备Bird续约资格的本队FA、同类后端递增，回帖称约8% | **Bird权利不是“只要球队有钱便总能使用”，也不保证PC本局同名菜单路径** |

上述是**报价方式/逐年向量**，并不是`contract_type`底层0..4的身份枚举（CORE/HARDSHIP/TWO_WAY/EURO_STASH/LINEUP）！不能把`contract_type=BIRD`写入，因为项目原生Enum中**没有BIRD**。所谓Bird是签约例外权/增幅资格，而非球员Roster Contract Type。

### 2.2 项目17个本机原生合同字段逐条枚举

本项目`config/memory_field_profile.json`已有**17项PLAYER.contract子字段**，其中：
- `bird_years`：+0x356 start_bit6 width4，跨字节4bit；**Bird年数≠已验证Bird/Early-Bird签约资格**。
- `original_contract_years` +0x341 bit4 width3；`years_left_on_contract` +0x32E bit2 width4；不能从“1”断言下一赛季已进入UFA池。
- `contract_option` +0x317 bit4 width2：0 NULL /1 TEAM_OPTION /2 PLAYER_OPTION /3 2_YEAR_TEAM_OPTION。
- `extension_length` +0x341 bit7 width3，`extension_option` +0x342 bit2 width2，`no_trade` +0x346 bit4 width1，`extension_no_trade` +0x31C bit5 width1。
- `contract_year_1..6`分别+0x1A4、+0x1A8、+0x1AC、+0x1B0、+0x1B4、+0x1B8，**每槽31-bit整数，剩余高位含共享保留标记，不能整块覆盖**。
- `contract_type` +0x344 bit3 width3，代码0 CORE/1 HARDSHIP/2 TWO_WAY/3 EURO_STASH/4 LINEUP；`euro_stash_years_left` +0x293 bit5 width2，`two_way_days_left` +0x15F bit2 width6。

以上为**项目字段注册**，不是本次从游戏进程新抓取，也不证明合同每项已经在公开SQLite中对所有球员有真实值。尤其`六薪资槽代表哪个赛季`在固定游戏阶段/合同Option/延期不同情况下仍**未经正式跨休赛期认证**。具体字段Machine目录见[R05-A字段与经营动作研究索引](../catalogs/R05A_FINANCE_CONTRACT_MARKET_RESEARCH_V1.json)。

**另一个关键归属点**：游戏内球员current team指针+0x60与contract team指针+0xA8可能不同，签约需核对球员本人、两队名单、队伍人数和合同归属；不能只写一个current_team_id当做合约已生效。[项目签约执行文档](../../38_APPROVED_SIGNING_EXECUTION.md)

## 3. Bird / Early Bird / Non-Bird、RFA/QO与工资帽保留额（Cap Holds）

### 3.1 相同人物可能有完全不同的市场身份

| 身份/操作 | 现实2021系列参考机制 | NBA2K22原生证据及待证 |
|---|---|---|
| UFA 不受限自由球员 | 可以与任何球队签约；母队通常不能强制同价匹配 | 当前项目`market_free_agents`某历史批次**0行**；不能说“没有FA”或“自动有母队匹配权” |
| RFA 受限制自由球员 | 需真正有效的Qualifying Offer等条件，原队可匹配对方Offer Sheet | 2K22及相邻版本玩家报告单年QO覆盖多年合同的现象[SRC-0118]；本局是否已复现UNKNOWN |
| Bird Rights | 现实符合3年连续资历等条件，母队可使用相应超帽续约途径 | Registry有`bird_years`，仍缺符合资格、cap hold、renounce与实机签约校验 |
| Early Bird / Non-Bird | 满足较短年限/原合同路径的有限额超帽续约 | 2K22 PC全部资格、合同年限和可见UI编码未认证 |
| Team Option / Player Option | 控制权不同：Team由队伍决定是否继续，Player由球员控制是否延续 | 2K22历史归档可见；项目Enum可读，但**选项节点前/后years_left和薪资滚动未知** |
| Cap Hold / Renounce Rights | 未续约FA对球队薪资空间可产生预留，主动放弃权利可以释放空间，但也可能牺牲Bird续约权 | 2K22玩家说明旧本世代可在Salary Cap Table放弃Cap Holds，次世代MyNBA迁至独立Cap Holds入口[SRC-0119]；这是**同版菜单路径差异**，不是PC已认证按钮 |
| Trade Exception / Disabled Player Exception | 现实NBA特例有不同签约/交易约束 | 不可直接当做游戏PC22真实可消费特例；见R05-B交易与合同特例研究 |

**现实NBA2021–22的税帽参数来自SRC-0114，RFA、QO、Bird、各类例外的定义参见NBA官方历史说明[SRC-0120]及2022自由市场真实案例[SRC-0121]。** 必须防止把如今NBA.com随2026更新的通用文章中的新CBA变化误当作2021 2K22规则。**当前无认证RFA资格来源时不能把队伍主观“拥有Bird”当自动可强制匹配的法律地位。**

### 3.2 “报价被接受→合同不正确”的游戏风险

2021-07 OS 2K系列玩家[SRC-0118]报告有资格报价的RFA，休赛期Moratorium里协商过长年合同，推进后球员仍拿到**单年QO**。该帖子**最早发生于2K22正式发售之前**，不能证明当时玩的已是2K22；论坛用户档案“2k22 MyNBA”可能在其后更新。2022-02的同版玩家另报告类似现象[SRC-0122]。2023-07仍有人抱怨多年QO被覆盖[SRC-0123]。

**这组资料的研究价值是“签约菜单认可≠合同持久生效、跨阶段读回必要”，而不是证明所有2K22 PC签约都有BUG**。不能为了规避难题将`原游戏没写成功`篡改为`球员突然不忠诚`，更不能不经批准直接替换合同。

## 4. 休赛期自由市场的可观察阶段与原生AI干扰

**现实2021–22流程序列**：赛季结束→Draft前后资格/球队与球员Option/QO决策→报价窗口及Moratorium→可正式签约→名单确定/进入下一季[SRC-0120/0121]。**PC22实际游戏季后赛到下季的节点必须在原版游戏逐阶段核对**，不应按现实日期强行安排外部系统触发。

本仓库FA P0记录[SRC-PROJECT-FA-P0]（[研究报告](../../development_reviews/DEV_20261017_04_OFFSEASON_FA_P0_RESEARCH.md)）发现：
- 已有历史归档30队、466人大名单六薪资槽与多种合同状态；正式`market_free_agents`**0行**，不证明真正FA自由市场候选池已获得；
- 当前日历识别、选项变动、QO有效性、合同Slot跨季滚动、CPU原生自动签约能否关闭/安全停点、正式签约写入持久性都**未在测试副本实机验证**；
- `docs/38_APPROVED_SIGNING_EXECUTION.md`的`SIGNING_LAYOUT_VALIDATED=False`、`SIGNING_EXECUTION_ENABLED=False`仍关闭，状态`approved_signing_v1_unvalidated`。**源码存在≠可以执行游戏签约**；
- 现有`scripts/offseason_plan.py`是离线规划器，用历史字段与假设数据演示，不是完整FA竞价已经获得真实世界源或原生选项。

**DEV29研究的合法动作词表（非系统工作流设计）**：查看Salary Cap Table/队伍薪资、原队Offer Rights、选择是否执行Option、发QO或放弃、保留/放弃Cap Holds、对UFA出价、合法RFA Offer Sheet/匹配、给予各种合同年薪曲线、最小合同/各种例外、教练员工预算，以及交易相关Cap Exceptions。**只记游戏可支持的选择及真实未知，不定义Player Agent为什么选择某个报价，也不假装这些功能当前全部有执行接口。**

## 5. 现实NBA财务与球队Business不是“玩家签约资金池”

旧MyGM/Business Wiki[SRC-0127]列入场馆维护/升级、Ticket/Merchandise/Concessions/Parking价格、媒体收入、球衣销售、业主目标。**至少“旧版游戏有Business栏目”这一点有文本来源**，但MyGM与MyLEAGUE的Owner Budget权限不同：不可没有PC22菜单就说本世界所有30队GM可以改球票、改球馆、给财务垫资。

2K22**PS5 MyNBA**官方[SRC-0128]另有独立的MySTAFF，包括Front Office、Coaching、Scouting、Sports Medicine四部门，要求权衡员工预算；这些属于经营概念可复用的同版设计，但**不能把17个次世代员工岗位直接当作PC MyLEAGUE人事字段**，Staff/Scout的精确字段与职位在R05-C集中清点。

真实球员薪水、团队薪资总额、Staff Salary、当前合同年薪、球队现金和票价都可能属于不同经济对象；对未来GM最重要的是**真实来源、单位、入账时点和可配置选择**, 而不是让本研究指定统一“赢球最佳预算”。

## 6. 目前项目能可靠提供的“财务事实”及缺口

| 本仓库模块 | 能提供/已实现 | **不提供/尚未验收** |
|---|---|---|
| `config/memory_field_profile.json` | PLAYER17个Contract字段，STAFF24-bit Salary（+0xF8），部分球队钱/名单字段另在Source/P0记录 | 真实球员薪资槽对应赛季的最终认证、实际Salary Cap exceptions、真实球员报价意愿 |
| `src/source_extensions.py`及旧Source Pipeline | 月度已采`total_salary/payroll/budget/cash`等，历史归档有用 | 当前球员FA全部身份、动态Cap Holds/合规空间、签到合同持久性 |
| `src/gm_core/finance.py` | `payroll_minus_tax_line`、`salary_cap_minus_payroll_proxy`及观察工资合计；Business可以列Staff Budget、Fan Interest/票价候选 | 不能直接从代理差额判断新签可行，不能从`cash`做税金自动扣账 |
| `docs/GM_FINANCE_WORKBENCH.md` | 独立只读的三年（最多六年）合同情景工作台、候选交易/签约方案逐年薪资比较；记录SCENARIO、UNKNOWN与条件分支 | 不做报价竞价、不给合法资格，`signing_capacity=UNKNOWN`，不操作游戏；M02六薪资槽年份映射只是`SLOT_SEQUENCE`情景 |
| `docs/37_APPROVED_TRADE_EXECUTOR.md` | 玩家批准后的具体交易身份/资产/读回安全能力 | 不等于工资帽/FA全合同条例覆盖；R05-B专门研究真实交易规则 |
| `docs/38_APPROVED_SIGNING_EXECUTION.md` | 存在有约束的最小签约源码、合同解码规则和身份反作弊保护 | **尚未实机验收，默认不可写游戏**；不能在R05研究过程中擅自打开开关 |
| `config/source_catalog.json` | 已准确把工资规则模板/Source与衍生财务工作台区别 | `game_calendar_detection=NOT_OBSERVED`、`offseason_development=P0_PARTIAL_REAL_GAME_NOT_VERIFIED`、`finance_semantics=RAW_PRESERVED_SIGNED_CASH_HYPOTHESIS_UNVERIFIED` |

若未来资料显示`total_salary=150m、salary_cap=112.414m`，只能得出**按该口径高于现实参考软帽37.586m**，**不能得出不能再签一名球员、能用Bird签任意金额或必须扣税某金额**。理由可能是该队的Cap Holds、例外、Option决策、应计年度、apron触发条件、已支付合同、预算与游戏设置未知。

## 7. R05-A研究结论：可选动作和禁推断清单

- 工资帽、税线、apron、现金/预算、员工薪资、球员逐年合同和球队营业收入是不同层次，**不合并为一种球队“有钱”指标**。
- 2022同版提供Flat/Front/Back/Bird合同曲线**可见玩法参考**，而已采Player.contract的`contract_type`是另一组Roster枚举，不能错写。
- UFA、RFA、Bird、QO、Cap Holds、Options可作为未来模型需要认识的市场对象，**RFA匹配权不等于Bird续约权，也不等于母队所有UFA的强制回购权**。
- 对所有规则保留`2021_REAL_NBA`、`2K22_CROSS_GEN_OBSERVED`、`PC22_TARGET_UI_UNVERIFIED`、`PROJECT_NATIVE_PROFILE_ONLY`、`CURRENT_GAME_SOURCE_UNKNOWN`的证据等级。
- **研究不直接定义谈判权重、出价顺序、模型行为或实现协议**。用户批准游戏修改的原则不变；普通经营禁止直接编辑Ability/Potential/Badge。
- 后续R05-B应具体覆盖球员/选秀权交易、工资匹配、TPE、签约交易、交易截止日/15人名单；**旧三届上限已于2026-10-21撤销**；R05-C再查员工、球探、历史选秀、Draft Stash和球队经营预算；R05-D作跨域来源/游戏设置清单而非自审人格系统。

**本轮状态**：`R05_A_RESEARCH_PUBLISHED_WITH_FINANCE_EXECUTION_GAPS`，**下一轮R05-B尚未启动**。没有运行游戏或测试存档，没有采集、开发Agent、启动DEV28/Codex、进行真实GM合同决策或修改游戏数据。

---

# DEV29 R05-B — NBA2K22球员与选秀权交易机制、真实资产与原生执行边界（2026-10-21）

> **状态：`R05_B_RESEARCH_PUBLISHED_WITH_TRADE_UI_AND_CBA_GAPS`。** 本轮研究K08交易体系及与K07工资帽、K09选秀相连的**真实可读取数据、游戏可选项、机制限制与效果**；不作GM交易估价算法、谈判流程/人格定义、不批准新交易、不运行游戏/执行器。继续保留R04研究结案与R05-A已出版状态。
>
> **来源**：新SRC-0129..0144；本项目 `config/gameplay_policy.json`、`config/draft_asset_profile.json`、`src/draft_assets.py`、`config/roster_association_profile.json`、`docs/37_APPROVED_TRADE_EXECUTOR.md` 等真实工程材料。可检索字段及游戏菜单研究词表见 [R05-B机读目录](../catalogs/R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json)。引用真实NBA2021–22规则时优先以2017 CBA时期更新资料为依据，不使用2023以后新CBA的Second Apron交易惩罚。

## 8. 三套互不替代的交易规则

| 规则层 | 谁给出 | 已知信息与能够控制的对象 | 不能作出的断言 |
|---|---|---|---|
| **现实2021–22 NBA CBA** | 2017 CBA及2021–22工资帽参考 | 大小薪资匹配、税线前后、签换、TPE、Stepien、选秀权和现金限制 | 2K22的CPU报价接受条件不一定等于真实CBA；游戏可能遗漏/简化条款 |
| **NBA2K22 Franchise原生设置** | 2K22 MyNBA/MyLEAGUE真实菜单、同版玩家观察 | Trade Logic/Trade Difficulty、Financial Trade Rules、Recently Signed/Traded、Rookie Signing、Deadline、Stepien、Override、CPU Offers/CPU-to-CPU Trades | 在线攻略列出选项≠PC22当前存档已采到开关值；也不等于原生确认“交易已生效” |
| **本项目自定世界政策与有界执行器** | 用户批准的 `PLAYER_RULES_20261017_V3` + 本机只读字段/当前玩家批准 | 双方交易意愿由外部模型研究之外决定，具体批准后，受限执行器可变更**名单归属与简单选秀权当前持有队**；旧规则曾限定三届（**2026-10-21现已撤销**），现行仍无保护/无交换 | 不是自动满足完整CBA校验，也不自动获得签约/释放/双向/复杂多方执行能力。所有游戏写入需要本次真实玩家授权 |

**该项目“双方同意就可执行交易”的自定义玩法，不是说原生2K22 Financial Trade Rules、Stepien或税务限制在所有存档都天然失效**；只意味着原生交易准入及外部已批准资产搬迁需要分开研究。游戏Trade Override功能与我们的外部数据执行器也不是同一操作。

## 9. 同版2K22玩家可见的交易设置与其影响

[SRC-0131]于NBA2K22发布后列出本代 Franchise/Mynba 交易设置清单。以下为**菜单候选**；它显示某个页面可能有此项目，**并未认证这些开关在当前PC22离线MyLEAGUE全部存在、完全同名、可以逐项读写并在重启后维持**。

| 选项英文名（同版攻略） | 可观察/修改的游戏语义 | 需留待PC22验证的精确影响 |
|---|---|---|
| `Trade Logic` | CPU是否评估交易合理性 | 关掉是否使提案失效、还是只取消对方接受判断？2022 PC玩家报告设置不同仍有不落地案例 |
| `Trade Negotiation Difficulty` | 交易谈判的游戏难度滑块 | 取值范围/具体CPU系数及当前真实设置未知，不能把难度50当50%接受率 |
| `Financial Trade Rules` | 是否让原生菜单实施薪资配平及某些财务准入 | 不能凭Off认定所有二次库存/薪资/球队预算副作用也自动合法 |
| `Recently Signed Restrictions` | 新签球员交易等待期 | 应分清现实12/15、1/15、3月和游戏日历；同版玩家报告日期比较异常[SRC-0133] |
| `Recently Traded Restrictions` | 已经被交易人物的再次交易/工资合并限制 | 分清单独再交易与与别的薪资打包；PC22精确等待期未知 |
| `Rookie Signing Restrictions` | 新秀签约后交易的特殊等待期 | 不假设所有Draft rights/签名后球员受相同窗口约束 |
| `Trade Deadline` | 是否允许常规赛截止日以后原生交易 | 2021–22现实截止日是2022-02-10，不意味着当前世界以后年度日期固定 |
| `Stepien Rule` | 连续未来首轮被交易时的限制 | 真实规则与游戏开关均有资料，`On/Off`在本机实际存档尚未读到 |
| `Trade Override` | 原生UI强制批准或覆盖CPU拒绝的候选能力 | 不等于本项目`--approve-game-writes`，不能借此绕过实际玩家批准 |
| `CPU Trade Offers` | CPU主动向所管理球队提出交易 | 不等于CPU会自行完成双方都是CPU的交易 |
| `CPU-CPU Trades` | 两支非玩家控制球队之间的原生AI自动交易 | 用户项目原生CPU-CPU交易可能单独关闭，须用真实当前批次读值确证 |
| `Trade Finder / Trade Block / Propose Trade / Player Finder` | 有查找对手/市场、提出与回看交易的不同入口；旧版Front Office Wiki有三种方法[SRC-0140] | 旧版菜单分类不证明每个PC22原版页都有完全相同的参数或模型调用路径 |

**关键同版PC22反例**：2022-07 PC MyLEAGUE一位用户确认交易菜单接受后，球员仍在原球队；回复者报告`CPU-CPU`交易未能原生落地、需要控制双方球队、或以三方结构绕过等经验[SRC-0132]。这是**一手异常报告，不是已复现的本项目bug或普适修复方案**。单击Accept与实际roster/contract/pick readback是两种不同事实。2022-01的旧世代2K22用户报告游戏12/25仍要求“到12/15才能交易”，其余奖项日期也异常[SRC-0133]；不能凭字面比较日期就下结论人物永远禁止交易。

## 10. 2021–22现实CBA的工资匹配：不能统一硬写成125%＋$100,000

历史劳资协议问题86[SRC-0129]和NBA官方TPE说明[SRC-0130]给出“**双方按各自适用额度分别判断，通常看交易完成后的纳税身份**”的规则。仅当采用现实2017 CBA的**同时交易**且球队适用对应分支时，下列参考表才有意义：

| 真实球队状态（2017 CBA时代） | 发出球员工资总额 | 最大接收工资（现实规则参考） |
|---|---:|---|
| 交易完成后为非纳税球队 | 0–$6,533,333 | 发出额×175%＋$100,000 |
| 交易完成后为非纳税球队 | $6,533,334–$19,600,000 | 发出额＋$5,000,000 |
| 交易完成后为非纳税球队 | $19,600,000以上 | 发出额×125%＋$100,000 |
| 交易完成后为纳税球队 | 任何 | 发出额×125%＋$100,000 |
| 真实有工资帽空间球队 | 视其实际空间、借助其它合法例外 | **另按剩余空间或可适用的超帽规则判断** |

**注**：在恰好处于$19.6m分段边界、交易后纳税状态与Guaranteed/Base Year Compensation/奖金等特殊情况下，还要使用完整当年CBA细则；表只是有出处的历史机制原料，**不是经本项目PC22游戏引擎验证的计算器**。

例如：假设A发出$10m而交易后仍为非纳税队，历史参考通常允许收到至多$15m；假设其交易后为纳税队则至多$12.6m。**这一个反例已经说明“125%＋$100k对所有球队统一执行”不符合历史CBA**。如果另一队同时接受，另一队也须独立验其额度、可用空间和人员资格，不能凭两队合计工资持平判合规。

`Trade Exception (TPE)`：一笔符合条件的非同时交易可能生成未来限定期限内可用于吸纳合同的例外；它**不是球队Cash、不是无限交易抵用券，也不能自动把两个不同例外与其它工资相加**。现实2017 CBA[SRC-0129]有一年左右失效规则、合同保障及收支方向限制。当前PC22原生TPE列表、消耗及残值、可否执行/当期资格都**UNKNOWN**；2022次世代用户反映找不到原本世代Trade Exception管理入口[SRC-0119]只提供UI线索。

`Sign-and-Trade`是**先通过合格签约权建立新合同，再立刻交换球员合同**的复合市场操作，不等于普通已签合同球员换队。真正的合约年薪、时间节点、硬帽和名单变化都可能需要一起验证；**本项目签约执行器`approved_signing_v1_unvalidated`尚未验收，R05-B不能因交易器存在就声称已支持原生签换**。

## 11. 2021–22选秀权：现实可交易保护/交换≠本项目简化资产

### 11.1 游戏世界同时存在三个独立的年度概念

- **游戏选秀年度**：2022、2023、2024等，是原生选秀权记录上的`draft_year`，**不再有外挂三届人为上限**。
- **历史新秀班年份**：从1984年乔丹届开始到2020年再循环；2022游戏年选秀导入可以是1984真实历史届，但**它不是“1984年选秀权资产”**。
- **实际游戏赛季与最新已完成选秀**：由当前存档/来源批次或玩家确认，不是脚本运行了几次就推进。即使2022新秀真实举行，也不意味本世界已完成。

**项目真实Native资产布局**：`config/draft_asset_profile.json`证据记录每项**32字节**、`+0x00`当前持有队uint64、`+0x08`原队uint64、`+0x10`已指派球员uint64、`+0x1C`元数据；year offset(0–4)、round code(0/1)、pick_index及实际游戏年份由原生代码证据支持。

`src/draft_assets.py`要求可识别连续**5个未来游戏选秀年×2轮×30个原队=300条真实未来选秀权**，每组必须完全一致、不可重复，并核实下一届年份。**这五届是可完整原生读取的资产覆盖范围**，不是外挂世界规则年限上限；其中第4/5届目前仍存在执行器旧代码限制。

### 11.2 世界规则2026-10-21最新版本：已取消原有三届上限

**用户2026-10-21正式取消“未来只能交易3届”的外挂世界规则，且没有授权另设5届固定上限。** 配置权威已升级`config/gameplay_policy.json → PLAYER_RULES_20261021_V4`，`maximum_future_drafts=null`，`window=NO_ADDITIONAL_WORLD_RULE_YEAR_LIMIT__REQUIRE_VERIFIED_NATIVE_ASSET_AND_EXECUTOR_SUPPORT`。

| 分别核对的条件 | 当前有效事实 |
|---|---|
| 资产身份 | **游戏年份＋轮次＋原球队＋当前持有球队**，资产必须在当前批次唯一、合法且确由提供者持有 |
| 世界规则附加年限 | **没有人工三年/五年的额外限制**；仍以游戏实际已有的可确认未来选秀权与可执行性为前提 |
| 本机已识别读取范围 | 现有`src/draft_assets.py`可核实连续**五届**、每届60枚，总计**300条**；这是现时**数据能力，不是长期世界规则上限** |
| 保护与顺位交换 | **仍然NOT_USED**。不新建保护或Swap，旧游戏数据中的原生条款不得擅自抹去 |
| 历史选秀 | 游戏2022年可指向导入的1984历史新秀班，但`draft_year=2022`选秀权不等于1984年球员身份标签 |
| 每笔执行 | 必须由真人玩家批准具体方案、确认真实游戏时间及资产、执行后readback。世界规则变更不构成批量预先授权 |
| 旧代码尚未同步 | `src/draft_assets.py::trade_window()`和`src/gm_core/calculations.py::draft_pick_window()`仍使用`+3`，`src/gm_core/trades.py`和`src/approved_trade_executor.py`依赖旧范围；**第4/第5届仍可能被当前执行器拒绝，待单独批准Codex同步** |

**若下一届已证实是2022年**，当前资料层可以认出2022–2026共五届（在原生覆盖确实完整时）；2025/2026不再因“人为三届窗口”被判不合世界政策。但**不表示当前执行器已经能够操作2025/2026，也不表示2027以后已存在可用选秀权**。现实NBA历史七年规则可以研究[SRC-0137/SRC-0161]，不能借此将本机未经验证的第6/7届选秀权作为真实可执行资产。

### 11.3 Stepien、保护与Swap：知识价值和可操作权限完全不同

- **真实Stepien原则**限制球队通过交易陷入连续未来年份没有首轮选择的状态。2022年现实NBA专门报道列明保护顺延导致后续可交易首轮年份复杂[SRC-0137]。
- 同版2K22规则网页列出`Stepien Rule`开关，并不表明当前PC22默认On或其数学逻辑已完整校验。
- **Protections**：现实首轮签可有乐透保护、Top-N保护、顺延/次轮折算等；2K23新世代玩家[SRC-0135]报告无法为某些签直接设置保护，这说明菜单版本和交互容易混淆，**不能推断2K22 PC无保护功能**。
- **Swaps**：另一位玩家2022-12在PS5 MyNBA中讨论Swap Best/Worst及Trade Finder的价值排序[SRC-0136]，亦属之后年度邻近版本/同系列社区证据；当前项目**明确不交易交换权**。
- **现实七年期限/其它变体**不能替换当前玩家的三年窗口[SRC-0137]；三年属于本项目业务边界、不是NBA2K22原生只能存三年。

## 12. 交易名单容量、当前归属、合同归属与外部执行：不能只改一支球队

当前`config/roster_association_profile.json`和经过玩家验收的[受限交易执行器](../../37_APPROVED_TRADE_EXECUTOR.md)提供**NBA2K22这一本机版本**的真实结构：

| NBA2K22本机球队结构 | 原生位置 | 当前已证用途 |
|---|---|---|
| 常规名单 | `TEAM +0x00`起连续15个8字节引用 | **15槽上限**，受限执行器可交换/迁移普通球员 |
| 常规名单人数 | `TEAM +0xCB1` uint8 | 必须与真实非空连续普通名单一致 |
| 双向人员 | `TEAM +0xA8,+0xB0`两个8字节引用 | **最多2名双向**；当前受限交易执行器不支持双向转移 |
| 双向人数 | `TEAM +0x1047`低2位 | 作为本机实际读到的人数 |
| 活动名单 | `TEAM +0xD0`起13个8字节引用 | **13槽**，可含合法双向球员；不是普通球员Roster 13人上限 |
| 活动人数 | `TEAM +0x1047`高4位 | 参与游戏真实索引，不可只改引用不改人数 |
| 保留/其它引用槽 | `TEAM +0x78..+0xA7`，6个槽 | 当前为空、原样保留；不是额外6个普通球员席位 |
| 其它球队/战术引用 | `TEAM +0xD28..+0xE67`等 | 经本机转队试验涉及，具体规划器只处理安全子集 |
| 球员当前队与合同队 | `PLAYER +0x60`和`PLAYER +0xA8`各8字节指针 | **都须维护一致性**，但不得借此同时擅改工资或合约年限 |
| 简单选秀权持有队 | `DRAFT_ASSET +0x00` uint64 | 受限执行器只改这一项，保留原队/选秀元数据 |

**已发生的真实本机工程教训**：CHI/DET交易先因`+0xCB1`人数未同步和活动人员计数不一致，造成球员虽在结构中却不被名单计数覆盖；经受控修复后用户接受CHI/DET游戏UI结果。首次修复缺失数据不能被后来的成功回读涂掉；另有DAL/HOU内存/重启后结果证据，存盘/再次载入的完整一致性仍需按实际版本复核。这是**原生交易写入技术要求**，不是GM/球员谈判逻辑。

当前Trade Executor有`plan→execute→verify`入口，真实人物由姓名+faceID+生日或其他消歧确认，跨会话地址重新校准，原值不符则拒绝；不会自动选择非目标名单成员腾位置，不会补其他球员加能力，也没有原子交易/通用失败自动回滚。**已支持的只是该受控范围内的名单归属与简单选秀权**：同队连续多笔相互依赖交易、同时多方复杂交换、双向人员转移、签约和释放、无法完整对应的5人组和超过15人球队都阻断，不能宣称全类型交易可执行。

## 13. 本项目可用的真实交易信息与未完成的实时来源

| 对象 | 已有来源等级 | 重要未知 |
|---|---|---|
| 球员合同、当前队/合同队、常规名单与真实人数 | 静态Native结构/历史批次/受控实时校准已有 | 若当前batch与实际加载游戏不同，所有历史交易候选都必须重新核对；原生可交易等待期/交易否决权当前值未知 |
| 选秀权5届（共300条） | NativeGetter字节证据＋实际读源算法，按Game Year、Pick Index、原队、当前队 | 用户下一届选秀年份是否已推进需验证；游戏原生Protection/Swap的可靠完整解码未完成 |
| 可交易资产范围 | 当前用户`PLAYER_RULES_20261021_V4` | **已取消三届世界上限**；以当前Native真实资产覆盖/唯一持有者/受限执行器为准，旧代码未同步不能宣称已能执行全部五届 |
| 交易报价/对手态度 | 真实游戏UI/CPU Offer/Trade Finder一般机制已有系列文献 | 当前本局CPU报价、对手对任何具体资产价值评估**未实际捕获**；`Trade Difficulty`不是成功概率 |
| Salary Matching/TPE/Hard Cap | 2017现实CBA详细表及2K22选项文字 | **当前PC22游戏是否完整计算对应分档、实际队伍是否拥有TPE、每笔交易引发税/预算影响均未认证** |
| 成交与报表刷新 | 某些本机玩家批准交易成功回读 | 球队`total_salary/payroll/cash`真实刷新时点、实机保存持久化、联盟新闻/交易历史自动记录范围UNKNOWN |
| 截止日与Recently Signed | 2022同版社区有日期异常报告 | 当期`game_date`自动观测仍不可用，游戏日历是否处交易窗口需独立来源 |

**涉及项目旧规范的冲突**：[旧Trade Valuation文档](../../14_TRADE_VALUATION_AND_ASSET_POOLS.md)中的“超巨绝对非卖、统一10000点评分、125%＋$100k通用硬规则、连续未来5年选秀权/保护和交换”等，与最新用户核准的真实政策、DEV29原料边界不一致；它是**旧设想，不能当现行游戏机制、外部人物真实意愿或授权执行规则**。本轮只把其名称/区别放进来源说明，不开发或替模型定义交易估价、人生选择或双赢充要条件。

## 14. 怎样正确观察交易“真的发生”及其原生后果？

以下是**研究事实的不同类别**，不是执行工作流开发：

- `TRADE_OFFER_VISIBLE`：真实游戏或外部模型显示了某个报价；**不是成交**。
- `TRADE_ACCEPTED_BY_NATIVE_UI`：按钮显示接受或页面弹出确认；2022 PC22一手玩家报告此时可能名单尚未变[SRC-0132]，必须重读。
- `PLAYER_APPROVED_PROPOSAL`：真实用户批准外挂具体交易方案；**尚不能说已执行**。
- `ROSTER_AND_PICK_OWNERSHIP_READBACK`：经过受控操作，玩家当前/合同队、双方名单/人数和资产持有权正确；可称**本次内存状态已核实**。
- `SAVED_RELOADED_PERSISTENCE`：用户保存、重开并有对应批次同一玩家/资产身份源；与即时readback不同。
- `NEXT_GAME_ENGINE_FEEDBACK`：实际比赛、工资汇总更新、球队化学反应或联盟新闻若可采，才是真实下一阶段后果；**不预测或强行写入球员属性或化学反应**。

## 15. R05-B本轮研究交付及后续R05-C

**本轮新增**：
1. 同版NBA2K22交易设置清单及PC版接受但未成交的玩家报告、旧世代日期限制异常、Trade Finder/Block/三队交易UI候选；
2. 2017 CBA、2021–22适用的**非纳税队三档与纳税队统一125%的工资匹配分支**、TPE、签换、实际NBA Stepien与保护限制；
3. **原生5年300枚选秀权≠本项目**原先只准交易3年（旧规则已撤销）**、无保护/交换的规则**；原生32字节资产构造与下一届年份；
4. 球队15常规＋2双向＋13活动名单及两个独立人数位域、PLAYER当前队/合同队、选秀权归属的精确可追溯Native证据；
5. 本项目**受限交易执行已通过某些玩家确认，但尚未提供通用双向、签换/多方、免规则的财务校验**；旧程序评分方案非DEV29规范；
6. 全部资料按现实2021 CBA、2K22同版社区、其它模式/年度、Native已知和当前存档UNKNOWN分级；仍**没有完整PC22原版交易设置/限制页面逐像素认证**。

**下一轮R05-C**：K09员工与Scouting、选秀前可见/未知信息、Scouting Reports、Prospect/历史Draft Class与真实选秀结果/权利、职位/Staff工资与球队Business，要求同样的游戏信息/可选项/效果目录。R05-D最后整合经营领域资料，**不设计/训练/部署GM/Coach/Player人格，不写交易规则决策程序，也不在DEV29独立审核**。R05-B没有触发任何游戏进程、采集、真实GM交易、DEV28/Codex或执行修改。


---

# DEV29 R05-C — 制服组、球探、新秀选秀与球队经营资源（2026-10-21）

> **状态：\`R05_C_RESEARCH_PUBLISHED_WITH_STAFF_SCOUT_DRAFT_UI_GAPS\`。** R05-A已研究财务合同、R05-B已研究交易与选秀权，本轮研究K09员工与球探、Draft Class/Scouting/Draft、选秀前可见信息、游戏现有人员原生数据能力及球队Staff Budget。**只交游戏原料，绝不设计Coach/Player/GM人物思想、评分/行为模型、自动球探算法或选秀注入执行器。** 证据SRC-0145..0160，[R05-C机读目录](../catalogs/R05C_STAFF_SCOUT_DRAFT_MECHANICS_V1.json)。

## 16. 员工研究的三个不同版本与数据层

**本项目本机NBA2K22 PC MyLEAGUE原生读取**和**2K22次世代PS5/XSX MyNBA官方开发说明**要并排列，不是后一套替代前一套。

| 来源和平台 | 确实知道什么 | 不能由此认定 |
|---|---|---|
| 本项目\`config/memory_field_profile.json\` STAFF | 8个\`position\`合法enum（0..7）、\`years_left\`、\`salary\`及10项能力/体系字段，共**13项当前静态注册字段**；\`source_extensions.staff_details\`可从真实STAFF结构读取⟦role/team/姓名/fields⟧、通过球队指针反向核验岗位身份 | **13项只是已注册，不是游戏完整员工资料**；\`position=TRAINER\`不证明有7类专科医师或可写完整次世代岗位 |
| NBA2K20 MyLEAGUE玩家<SRC-0146> | CFO、Assistant GM、Head Coach、Assistant Coach、Head Scout、Trainer是当年旧本世代常见六类岗位；玩家对其效果本身有分歧 | 旧版职位及玩家自答不能认证PC22没有Governor/其它岗位，也不能把“A scout increases training camp slots”的发言当代码公式 |
| NBA2K22 **次世代MyNBA官方**<SRC-0145> | MySTAFF明确四部门、列出多种专科岗位，**最多17个可实际聘任名额**，必须雇前台岗位和各部门Head，员工预算是取舍；Coach/Scout/Medical各有不同职责 | **官方只对PS5/Xbox Series平台声明了新的MySTAFF架构**；PC22离线MyLEAGUE原版具体职位、部门、总人数上限及同名属性不能未经独立认证直接沿用 |
| 2021-09 2K22玩家实测<SRC-0147/0148> | 有用户在MyNBA招聘后发现17槽争抢和预算不足、训练医疗或教练的试跑结果看似不同；也有开档发现部门空缺/预算不足的报告 | 这些是少数玩家主观体验（平台可能次世代），不是已量化的“聘某教练+2，某医生伤病-20%”算法。用户报告同名“MyLeague”**不等于**PC22已证。 |

### 16.1 本项目8种本机静态注册岗位（逐一）

项目\`STAFF.position\`注册于结构⟦+0x10E bit2 width3⟧，允许0..7八种身份代码：

| 原始代码 | 职位Enum（项目当前字典原文） | 最直接的游戏系统接口 |
|---:|---|---|
| 0 | HEAD_COACH | 主教练；K04/教练体系与比赛设置 |
| 1 | ASSISTANT_COACH | 助理教练；具体赛季影响仍要看2K22效果证据 |
| 2 | HEAD_SCOUT | 首席球探；球探报告/选秀信息准确度候选，不是已认证个人潜力真值 |
| 3 | TRAINER | 训练师；R03已覆盖训练/健康与自然成长，效果系数未认证 |
| 4 | GM | 总经理；现实球队经营/球队关系，但这个Staff枚举不等于已开发30个GM Agent |
| 5 | GOVERNOR | 球队负责人/管理人员；区别\`GM\`，不强推老板AI干预 |
| 6 | CFO | 财务主管；职工Business/财务候选，不能假设直接带来具体收入 |
| 7 | ASSISTANT_GM | 助理总经理；合同/交易能力候选，不是固定签约打折系统 |

**内部员工字段13项完整计数**：
\`position\`、\`years_left\`、\`salary\`、\`offense\`、\`defense\`、\`potential\`、\`contracts\`、\`trading\`、\`scouting\`、\`training\`、\`business\`、\`preferred_system\`、\`active_system\`。

- ⟦salary⟧ +0xF8、24bit；⟦years_left⟧+0x112低4bit，取值是位域0..15，但不代表合同允许签15年；该Staff字段上的单位/总值合法范围**还缺少PC22可写UI交叉证明**。
- 八项评分：⟦offense/defense/potential/contracts/trading/scouting/training/business⟧**实际共8项**，均4bit离散\`F .. A+\`共13个字典标签（原始0..12）。**\(13等级\)不是现实比例，\`A+\`也不保证CPU选秀报告绝对正确**。
- ⟦preferred_system⟧与⟦active_system⟧各3bit、0..7；\`Balanced/Grit & Grind/Pace & Space/Perimeter Centric/Post Centric/Triangle/Seven Seconds/Defense\`与K04球队体系同名，但“教练偏好”和“当前使用”是两组字段，不可互相替代。
- **上面是位域编码空间，不是将每一项默认开放给DEV29写入**。精确offset/bit/每个枚举键由[机读目录](../catalogs/R05C_STAFF_SCOUT_DRAFT_MECHANICS_V1.json)直接保存原生Profile值；没有变更任何STAFF字节。

### 16.2 已有真正员工原生源，不是网页纯猜测

\`src/source_extensions.py::staff_details()\`从被校准的员工Name Anchor前0x30开始读取0x160字节。解析\`STAFF.position\`、当前聘用队指针\`STAFF +0x18\`，并要求该队相应职位槽位引用**指回同一个员工结构体**，成功才标\`VERIFIED_RECIPROCAL_TEAM_ROLE\`；否则保留\`UNMAPPED_NOT_ASSUMED_FREE_AGENT\`，**绝不可因为找不到球队就把人当已认证自由雇员**。现有正式存档批次路径确实包含\`staff.json\`，但本次没有逐项加载其全部员工或确认最新游戏日期，因此不能说当期某GM可以立即聘任某一具体人员。员工池**有数据读取能力**≠**已验原生聘解约写入能力**。

## 17. 官方2K22次世代MySTAFF四部门完整职位原料——和PC原生八码并列

2K2021-09-08开发说明<SRC-0145>确切列出下述全部“职位名称”，并称Front Office要全部填满、各部门须有Head、总计可填**17个员工位置**。但可选岗位总数**大于**17：

| 部门 | 官方列出的具体岗位 | 可用机制原料（不编造具体数值） |
|---|---|---|
| Front Office | Governor、GM、Assistant GM、CFO | 管理、经营、签约与业务评分；合同预算分配 |
| Coaching | Head Coach、Shot Doctor、Bigman Coach、Post Defense Coach、Perimeter Defense Coach、Guard Guru、Wing Whisperer | 对应细分投篮、内线、后卫、锋线及防守指导能力；真实成长效果待实测 |
| Scouting | Head Scout、4 Domestic Scouts、2 Foreign Scouts | 一队可分配国内/海外球探覆盖；**名额候选**≠PC22已采6名球探或真实海外准确率 |
| Sports Medicine | Team Doctor、Strength Trainer、Stamina Trainer、Sports Psych、Sports Science、Physio、Sleep Doctor | 不同康复/健康/体能/心理岗位；详见R03。不能从名词推出统一伤病降低百分比 |

**职位可用性是多模式比较维度**：PC22本机已注册8类；次世代官方已宣告4部门及上述职位，并可以在17个位置/员工预算内取舍；2K20旧本世代只列六个基础岗位。**不要将这些候选合并成“PC22已经有22名员工”或“PC22总上限17”**。不同图文产品的标题里写MyNBA，目标PC依然MyLEAGUE，只有本机完整菜单/岗位交叉取证才可升级。

开发说明有Updated Staff Card，员工技能徽章及具体职位适配度。此处特别区分：**员工徽章≠球员Badge**；官方只说超过旧版双倍的员工徽章，不提供本研究核准的完整ID/value列表，绝不自行制造“全员徽章枚举”。

## 18. Scouting：球探侦察报告、可见预估与真实潜力的界线

### 18.1 可观察报告类型：是一个“不完全知道”的体系

**同版2K22离线MyLEAGUE操作文章<SRC-0149>**给出\`Scouting → Prospect Scouting\`菜单、用户自建或历史Draft Class加载、按球探预计Overall排序、\`D.E. Rank\`（DraftExpress预测排序）、\`2K\`及\`NBA.com\`等排名列的文字及图片。**这证明同版文章报告了这些信息类别，但它不是本机PC原版滚动菜单逐像素认证。**

研究上要将以下对象分开：
- **SCOUTED_PERCENT / COVERAGE**：报告完成度，实际可读的当前\`scouted 40%\`、\`100%\`是不同已完成的信息状态；**并不等于预测能力100%正确**。
- **SCOUT_GRADE / PROJECTED_OVR / PROJECTED_POTENTIAL**：是球探报告对能力和前景的估计，受球探是否完成、可能误判及使用版本影响。<SRC-0151>同代玩家解释Auto一般先选热门/己队顺位附近人，但可能未达到100%，不是官方算法。
- **MOCK_DRAFT / D.E. RANK / 2K RANK / NBA.com RANK**：不同媒体/算法或球探榜单，**不是人类GM必须接受的“真顺位”**；现实NBA2022分析网站也分别维护Big Board（天赋排序）、Mock Draft（预测球队）、当期选秀结果。<SRC-0157/0158>
- **TRUE_GAME_PLAYER_ABILITY/POTENTIAL**：本项目源代码可能在受限的历史原始游戏结构中含真实值，**它不是普通GM通过球探应当知道的资料**。本局原生潜力自动遮蔽后向GM只提供⟦Potential=1⟧占位，决不能拿这个1作为现实评级；真实潜力不能通过GM SQL/公开Draft Class补回。
- **DRAFT_RESULT / PICK_OWNER**：真正选秀之后，才能把当年选中队、轮次、顺位和真实球员身份当世界事实；Mock Draft不是实际选秀结果。

### 18.2 球探到底能做什么/什么时候刷新？

| 候选动作/入口 | 同版/邻近资料 | 保留未知 |
|---|---|---|
| 自动侦察 Auto Scouting | 2021-08 MyLEAGUE玩家说自动会优先高排名和己方可能选的球员，但未必100%<SRC-0151> | 发帖时间早于2K22发售，**仅旧系列同代经验**；PC22当前开关与刷新节奏未知 |
| 手动选人／优先项目 | 2022-12 MyLEAGUE玩家报告新秀列表中40%侦察状态，回复建议Auto/Manual与定向球员<SRC-0152> | **2K22/23同代版本标签不够清晰**；当前PC22原版菜单最多同时选择几人/周期未证 |
| Scouting Trips | **2015 Leftos开发人员**称旧MyLEAGUE自11/15开始每15天有Scout；每次玩家选若干人<SRC-0153> | 这直接是2015游戏，不是2022 PC必然的15天间隔。也不能拿旧版“2次100%”当当前绝对规则 |
| 聘更好的Head Scout | 本机STAFF.scouting有F到A+档级，角色身份可读 | **有字段、有分级≠提高多少侦察效率或预估准确率的引擎公式已证** |
| Domestic / Foreign Scout | 2K22次世代官方每队候选4名国内与2名外国<SRC-0145> | **严格为4国内+2国际球探职位候选**；PC22本机未分出6套独立员工字段 |

**反例**：2022-11邻近MyNBA一手问答<SRC-0154>有人已100%侦察仍不确定不同Potential Grade对应何种真实原始潜力，帖子没有可靠的官方数学答案。**不能从⟦A+⟧推断POTENTIAL=95，也不能从⟦100%⟧推断“侦察无误差”**。2022-07确有2K22 MyLEAGUE玩家明确区分卡面潜力字母等级和Edit Player的25..100基础Potential<SRC-0155>，这证明它们在信息层上可分开，但并不授权普通GM去Edit Player“作弊获取”隐藏真值。

## 19. Draft Class：真实世界的“历史选秀年”和游戏内选秀年度必须严格分开

**本世界业务**：开档2021–22，接下来第一次真正完成的Draft使用**1984**历史新秀班，后续1985…2020，下一轮再1984；只有**玩家确认一届选秀已经真正结束**才推进历史班计数。游戏内有2022年资产、真实历史班1984、历史新秀人物原始\`draft_year=1984\`，三者不是同一外键。

### 19.1 已有历史克隆读取与候选筛选（不是可运行注入）

\`docs/20_HISTORICAL_DRAFT_POOL_AND_INJECTION_SPEC.md\`、\`src/historical_rookies.py\`的现有独立查询：

- 每条Player Pool原始长度**0x4F0=1264字节**；\`raw_struct[0x70] & 0xE0 == 0xE0\`是该项目与艾弗森/科比克隆交叉验证的历史新秀类型标签；**只有同标签且DraftYear匹配、身份/顺位去重，才能作为可导入候选**。
- 现有历史档**3320**个原始槽，包含不同同名/年龄/历史版本克隆，不是“3320历史新秀”；旧文报告1984原始匹配7人、1996匹配14人只是**旧批次示例**，不能保证新抓取仍完全相同或每届都有60人。
- 每届目标选秀临时60槽是**目标容量/待确认的游戏场景布局**；现有\`src/historical_rookies.py\`能筛选历史新人、\`DraftEngine.get_draft_class\`能给候选；**目标临时球员槽位位置、字段映射与存盘读回尚未完成PC22实机认证**。
- \`src/extract_live_draft_class.py\`使用NBA2K22 Tools内存扫描的旧**试验性代码**，并以固定指针区间、姓名聚类猜测目标数据；**不能冒充已完成当前PC版本校准或跑它进行正式抓取**。
- 用户\`config/gameplay_policy.json\`明确缺少合格历史新秀模型时**保留游戏生成的新秀**，不补现役/巅峰克隆，不伪造属性；普通经营不能直接修改技能潜力/徽章。
- **GM现实潜力保密风险**：DEV15资料明确GM发布库将Potential覆盖为1；\`historical_rookies\`源池可能包含已遮蔽的\`raw_struct[0x441]\`。如果用GM公开库直接做游戏原始选秀注入，会把某些新秀的真潜力错误写成1。**只有另行授权、校验且隔离的原生真实注入源才能用于游戏写入**；本轮绝不调用。

### 19.2 2K22真的有哪些Draft Class菜单选择？

2K22同版4月攻略<SRC-0149>明确描述在创建联盟后/进入Scouting菜单可选择：
- 系统**自动生成Draft Class**；
- **Historic Draft Class**，如1984/2003；
- **User-Created Draft Class**，本地保存或社区下载，正式离线模式可在Scouting页重选；
- **Create/Edit Draft Class**，从历史人物或已导出DNA建立新的新人模板；
- 若载入用户自建名单可存在不同能力/潜力平衡尺度及玩家主观评分，**不等于原始NBA2K22官方保证所有历史新秀覆盖**。

同版2022 Online MyLEAGUE玩家<SRC-0150>先认为找不到导入入口，后来在\`Scouting → Prospect Scouting →选人\`下找到“Import Draft Class”。**这是Online玩家自我纠正的菜单路径，不能反推Offline一定没有该功能或每季自动重选成功**。

老版2K20–21的\`Export Player DNA/Import Player DNA\`以及2K22用户2022报告自己复制历史新秀的方式<SRC-0156>说明**已存在可研究的角色外观/能力复制工具**，但**这不是本项目普通经营的自由改Ability许可**。历史选秀注入需要身份标记、新秀年龄/Years Pro、原始Badge/Skill结构与目标槽逐项认证。

**Draft Class内容变化≠Draft Pick ownership变化**：改变候选新秀名单不会自动修改某支球队拥有的2022年首轮选秀权；本项目R05-B的32byte未来选秀权具有独立\`owner/original/year/round\`，另需读取真正Draft Result才能确定谁选中哪个人物。

## 20. Draft过程可观察对象、现实制度与PC22技术断点

| 对象 | 有来源的真实内容 | 目前缺少的游戏证据 |
|---|---|---|
| Lottery / Draft Order | 2021–22现实NBA使用乐透、2022 NBA实际选秀的官方Draft Board列出第1轮和第2轮、球队及球员<SRC-0157> | 当前PC22默认真实Lottery权重、当前世界抽签结果、真实Draft Order变化的可认证内存位置和readback |
| Mock Draft / Draft Board | 同版2K22攻略显示多个模拟榜单列及Scouted Projected OVR，现实Draft Big Board与Mock区分<SRC-0149/0158> | 当前各队GM能看到的实时预测版本和是否每月更新、榜单在临近选秀如何变动 |
| Prospect Biographical Info | 身高体重、位置、年龄、大学或国家等候选球员卡<SRC-0149>；实际历史新秀池有姓名、年份、轮次、顺位、面补ID | 此时\`current draft year\`对应的真实60个新秀目标身份是否已经稳定，未来世界同名克隆是否冲突 |
| Scouting Report / Potential Grade | 0–100进度与字母等级观察，个人球探能力可能有关 | 完整PC22字段列表、误差模型、是否有隐藏信息及部分报告是否对不同GM可见 |
| Player Workouts / Combine | 现实2022 Draft Combine/体测真实存在<SRC-0159>，旧游戏系列有预选秀操作参考 | **未找到目标PC22真实MyLEAGUE独立Workouts可配置动作完整菜单和原生效果，不能擅自新增** |
| Rookie Contract / Draft Rights | NBA现实前两轮新秀合同制度；本机PLAYER已有合同Option/合同类型、选秀权资产独立存储 | **Draft Choice → 选中球员 → 所属球队/合同年份的PC22完整原生签约动作尚未实机认证**；尤其Euro Stash和Two Way的实际赛季转换 |
| Season Progression | 1984–2020历史班随真实已完成选秀推进，本项目已有候选查询 | 自动识别“选秀已结束”、历史班计数稳定持久化、下一赛季Draft Result必须从当前存档确认 |

**特别注意：外部篮球媒体榜单是现实2022年资料，不是游戏世界中已经发生的选秀顺位。** NBA.com真实2022榜单不能直接宣称本局2022年乔丹一定被魔术选中，也不能因观察到历史中新秀成名，提前把其Potential真值泄漏给GM。

## 21. Staff Budget、员工聘任和球队经营：可选控制的归属与副作用

本项目R05-A已经将⟦staff_budget/cash/budget/payroll⟧分为不同经济对象。**STAFF.salary 24bit不是球队工资帽的一部分的自动证明**；员工合同薪水应和球队Staff Budget以及Coach/Scout/Trainer岗位是否有合法空位分别检查，而不是“球员有Cap Space所以可雇球探”。

真实员工操作候选包括：**Hire、Fire、Extend/Renew、Change Position、View Staff Pool、View Staff Contract/Staff Budget、Edit Staff、Allocate Staffing Slots**。**只有查看和本机STAFF读源已有明确结构**；其它选项来自2K22次世代官方与旧本世代讨论，不证明PC22已认证每一个按钮、选项可用年限、解雇费用/雇佣天数和执行效果。

同版2K22次世代少数玩家<SRC-0147/0148>报告Budget不足、17个Staff slots抢占及调整医疗配置后觉得伤病恢复较快；**不应由此推断“所有球队必须优先医务组、医疗员工每人回归提速50%”**。另一组2022社区玩家比较不同教练/特殊训练员工是否有作用时还有直接矛盾叙述<SRC-0160>；真实效应、适用模式和刷新时点仍待真实比赛/成长/伤情联动证明。

本项目早期\`docs/05_STAFF_AND_PLAYER_GROWTH.md\`与\`docs/12_NATIVE_MENTORSHIP_AND_STAFF_GUIDE.md\`含“聘任某名医固定减伤”、“训练师直接给乔丹加3PT”、“某教练必须最佳”等未经证实的旧计划与后已取消的自动属性编辑。**现行游戏政策明确禁止这种默认改值**，这些文档仅能当旧版本背景，不作为R05-C事实依据。

## 22. R05-C研究目录的交付内容与目前实际断点

本轮把下列项目变成有精确来源的**知识原料**：

1. **8种PC项目Static Native岗位、13个STAFF字段**，含薪酬、年限、8个字母级属性、两套3bit战术体系。已经存在\`STAFF +0x18\`聘用球队双向指针校验及正式源\`staff.json\`；**实际聘任/转职/解聘/续约可写接口未经认证**。
2. **NBA2K22次世代官方四部门和17人聘用上限**，同时保留与PC注册岗位不一致的版本事实，不偷换。
3. **Scouting可观察候选**：Scouted %、Projected OVR/Potential、多个模拟榜单/D.E.排序、Auto/Manual、Head Scout评分、国内/国际球探覆盖；它们与真正球员潜力、Draft结果独立。
4. **历史选秀1984–2020循环**、Player Pool 0x4F0/标记0x70类型高三位、3320槽、候选缺额保留生成新秀、当前写入目标无PC实机认证；公开Potential=1绝不回流为真实Game Potential。
5. **Draft菜单**：Generated/Historic/User-Created/Create/Edit/Import DNA等候选，部分同版2K22与跨代明确。NBA彩票/顺位、签新秀、Euro Stash、Mock/Big Board及可选工作坊全链条仍需PC22 UI取证。
6. **业务权限**：研究原料不等于有PC游戏修改许可；玩家单独批准后再由独立执行者落实原生可验证动作。没有创建任何球员/Coach/GM人格、选秀决策程序、员工雇佣AI或模型间工作流。

**状态**：\`R05_C_RESEARCH_PUBLISHED_WITH_STAFF_SCOUT_DRAFT_UI_GAPS\`；**R05-D经营资料来源与全部操作目录整合尚未启动**，由用户下次明确触发。R04维持批准结案。本轮不启动游戏、Codex、DEV28、历史新秀真实注入或原生写入。


---

# DEV29 R05-D — 游戏经营全域资料整合（2026-10-21）

> **正式研究状态：`R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`，R05-A/B/C/D研究已交付，不代表PC22所有UI或执行器完整。** 本节将**K07财务与合同/K08选秀球探和市场/K09员工体系**联成可独立检索的游戏原料。所有选择由未来对应模型自由决定，DEV29**不编写固定最优经营逻辑、谈判评分器、球员人格或执行脚本**。机读入口：[R05-D 54项数据/63项可选概念/12项联动/12项真实缺口](../catalogs/R05D_FRANCHISE_CAPABILITIES_ATLAS_V1.json)。

## 23. 已知游戏数据、静态技术布局、菜单参考与真实操作权限四者不能画等号

| 证据级别 | R05真实实例 | 下一模型可以合理知道什么 | 不能作出的断言 |
|---|---|---|---|
| **REGISTERED_NATIVE_LAYOUT** | `PLAYER.contract`17字段、`STAFF`13字段、`TEAM/DRAFT`14原生结构映射 | 存在该结构、位域/Enum和可配对的读取方式（如果有正确存档） | “全队当前值已读”“随时能写”“改值效果已证明” |
| **HISTORICAL_PROJECT_CAPTURE** | 某批次`team_finance`及`staff.json`；五届300张未来选秀权的读取模型和过往玩家受控测试 | 对特定来源批次可形成观察/核验样例 | 不能默认等于**现在游戏**的球队薪资、Staff空缺、已选新人及最新Draft交易持有人 |
| **OFFICIAL_SAME_GAME_OTHER_PLATFORM** | 2K22次世代MySTAFF四部门/17人配额、Conditional Coaching的关联 | 这些是游戏机制设计的同版研究参考 | PC22本世代菜单、岗位及选项值已完整相同 |
| **SAME_GAME_PLAYER_GUIDE** | Contract Flat/Front/Back/Bird、Draft Class入口、Trade Sliders、Scouting可见预计能力/榜单 | 大致可选择哪些菜单、可能有哪些业务效果 | 当前用户存档确有同名开关、相同年月/系数或值域 |
| **REAL_2021_22_NBA_RULE** | $112.414m真实工资帽、2017 CBA匹配分档、选秀权交易真实七年Stepien背景 | 现实制度在赛季背景下为什么限制某操作 | 把真实NBA七年自动写成2K22 PC七年可交易资产，或忽略当前用户世界政策 |
| **PROJECT_POLICY** | `PLAYER_RULES_20261021_V4`：已取消三届限制，不使用保护/Swap，审批仍必需 | 哪些外挂资产动作符合玩家的世界规则 | 只因规则允许就宣称执行器第4/5年已解锁 |
| **VERIFIED_RUNTIME_EXECUTION** | 某些CHI/DET受控人员交易/简单Pick变更曾获用户UI接受；当前签约仍禁用 | 真实获批的**特定动作**经过读回才有效 | 所有球队都能无风险执行任意签换、员工聘解约、选秀注入 |

**统合目录的54条是技术已登记项与候选财务项目的合计，不是54条当前游戏实时读数**：17 Player Contract + 10 Team Finance（含部分候选/代理）+14 Roster/Pick结构+13 Staff Profile。**63类可选/研究操作包含21种合同市场概念+16交易候选+10球探类别+10选秀选项+6员工聘任候选；并非63个原生已验证按钮**。

## 24. 经营领域统一可观察资料索引

| K域 | 可以索要/已存在的字段或文件 | 来源基础 | 更新时点/持久性待证 |
|---|---|---|---|
| **K07球员合同** | 6个逐年薪资槽、剩余/原始合同年限、Bird年数、合同Option、延期、No Trade、两向/EuroStash状态 | 静态Native Player 17字段+部分游戏源 | 跨季薪资槽位真实年份、Option行权、Bird资格、QO/FA期读回 |
| **K07球队财务** | Total Salary、Payroll、Budget、Cash；Staff Budget、Fan Interest、票价与Gate候选 | 项目队伍/财务工作台 | 当前工资帽设置、团队税、真实例外、Money单位/累计范围、签约容量UNKNOWN |
| **K08交易/名单** | 15常规槽、2双向、13活动槽，球员当前队与合同队、名单及活动人数 | Native Roster/Player身份/真实已验交易记录 | 非简单多方、双向、签换/名单自动填补及跨重启保存一致性 |
| **K08未来选秀权** | 每枚的Draft Year/Round/Original Owner/Current Owner；五届共300条已知只读布局 | `draft_asset_profile.json`、`src/draft_assets.py` | **当前世界已取消三届交易上限**，但执行代码仍旧三届；第6年以后是否真实可取未知 |
| **K08球探与新秀** | 可观察新秀姓名/位置、Scouted%、Projected Overall和Potential Grade、多个榜单与Draft Class类型 | 同版2K22攻略、旧版经验、历史新人候选池 | PC22菜单完整枚举、真实球探误差与更新时间、Draft Lottery及正式Draft Result |
| **K09员工** | 8种原生职位、13项Staff字段、个人薪资、年限、F..A+评分、Preferred/Active系统 | Native STAFF Profile与`staff_details()`读取器 | 聘任/解聘/续约/实际职位上限、部门员工预算、医学球探效果 |
| **K09本世代vs次世代** | 同版PS5/XSX MySTAFF四部门、17聘任总名额、细分教练、国内国外球探及医学部门 | 官方2K22说明 | PC22是否开放同样岗位不能仅由同版次世代宣传认定 |

**身份交接总原则**：用保存档身份、`game_date`、同源批次、当前球员/球队/员工原生ID匹配；外部现实赛季日期、交易提案、模拟排行榜、隐藏Potential=1不能当作本局实时事实。

## 25. 操作目录：哪些动作是“资料已经提到”，哪些动作实际可以落地？

以下分为**菜单候选**与**本项目受限执行层**，避免将研究误登记为可执行代码。

| 行动领域 | 游戏中的可选操作原料 | 在本项目的真实状态 |
|---|---|---|
| 合同 | Flat/Front/Back/Bird报价曲线、年限/选项、球队/球员Option、QO、RFA、Bird续约、Cap Holds/弃权 | Native Contract 17位域已登记；FA真实阶段/签约生效尚未验收，`SIGNING_EXECUTION_ENABLED=False` |
| 交易 | Propose Trade/Trade Finder/Trade Block、交易难度、工资匹配开关、Stepien、Trade Override、截止日、CPU交易开关 | 对部分**普通Roster人选与简单未来Pick**曾具获批读回的受限操作，**不覆盖全部CBA和所有菜单** |
| 选秀权 | 选中一项真实年份/轮次/原队/持有人未来资产，讨论保护/Swap系统但本外挂不新建这些条件 | 世界政策`V4`**不再额外限制未来三届**；五届只读已知，**第4/5届现有执行代码仍未同步** |
| 员工 | 查看Staff Pool、Hire、Fire、续聘、更换角色、预算/位置调整 | 本机STAFF**读取**可用，PC22各操作UI值域及本人资格/聘解约执行尚UNKNOWN |
| 球探 | 查看报告/完成度/预期能力、Auto vs Manual、指定新人/球探、国内外人员 | 原版/相邻系列资料有菜单线索，但当前精确PC22动作集合、次数和效果无完整已验执行接口 |
| 历史选秀 | Generated/Historic/User-Created/Edit Draft Class、Import/Export DNA、选秀大会/乐透、Draft Rights | 历史人物池类型码筛选可用；**目标NBA2K22 PC选秀新人槽位写入未实机验收**，Draft Result读取仍不完整 |

**每个游戏设置都需要知道其值域（如果确实存在）和修改副作用**。如员工`STAFF.position`0..7是已登记合法存储Enum，但这**不等于任何时点都能点击Hire选择任意8岗**；工资帽公式是现实NBA参考，不是游戏动态真正签约准入；History Draft Class可载入不意味着已签合同/已属于某球队。

## 26. 12个真实跨域联动及其不确定性

| 关联 | 原生/数据接口 | 观察的机制关系和真实未知 |
|---|---|---|
| **C01合同→球队财务** | 6薪资槽 / Total Salary、Payroll | 年度合同支出变化会影响队伍工资；但`salary_cap_minus_payroll_proxy`不是合法可签金额 |
| **C02合同选项→自由市场** | Bird/Options/Years Left | 资格、行权和Moratorium/QO状态影响报价；真实PC签约阶段与保存未验证 |
| **C03交易→名单** | Player当前队＋合同队、Team 15/2/13槽 | 部分受限交易可读回；人数/引用不同步会破坏游戏名单 |
| **C04交易→薪资帽** | 两队出去/进来工资、纳税状态 | 现实历史配平存在多个分支，游戏开关真实值/对应公式未知 |
| **C05交易→选秀权** | 32字节资产Current Owner | 用户取消三届上限，**执行器仍会按旧三年拒绝第4/5届** |
| **C06选秀权→选秀名单** | Game Draft Year/Asset versus Historic Class Year | 取得某年份选秀权不意味着自动获得1984届某个球员 |
| **C07球探→选秀预测** | Scouted%/Scouting Estimate/Mock | 报告有不确定性，完成度不等于真实潜力正确率 |
| **C08员工→球探** | Head Scout Scouting等级 | 员工能力有原生A+等离散值，但引擎侦察误差/速度确切作用未知 |
| **C09教练/Trainer→自然成长** | Staff能力、K06 Training | 自然成长由游戏引擎负责，不能因为聘优秀员工直接改球员Skill |
| **C10球队预算→员工** | Staff Budget与STAFF.salary | 员工预算、球队Cash和球员工资帽不是同一种钱 |
| **C11游戏时间→所有阶段** | Save/Game Date/Source Batch | 不得用今天日期驱动游戏休赛期；所有源只能被真实游戏节点刷新 |
| **C12可见数据→不同角色** | 已采当期比赛、合同、Scouting、隐藏Potential | 数据必须按真实可观察性使用；DEV29不决定未来人格模型怎样选择 |

[机读联动目录](../catalogs/R05D_FRANCHISE_CAPABILITIES_ATLAS_V1.json)对每项保留`input`、`unverified`和`action_effect`，**不是对GM/Coach/Player/Media制定行动计划**。

## 27. 十二项PC22原生来源／选项／执行能力缺口：不得填成已知

| 编号 | 现阶段尚不能声称已认证的对象 |
|---|---|
| G01 | 游戏真实Cap Holds/Tax/Exceptions和Salary Cap Table完整签约容量 |
| G02 | 当前Free Agent Pool、Options、Qualifying Offer、休赛期各阶段的正确实时采集 |
| G03 | 原生签约成功、合约跨年滚动和`approved_signing_v1_unvalidated`执行器验收 |
| G04 | **新世界选秀权政策与旧三年Trade Executor判断不同步** |
| G05 | PC22所有交易设置页面合法值域、当前开关与工资/日期限制引擎效果 |
| G06 | 双向、任意多队交易、签换/释放与复杂名单的安全事务执行 |
| G07 | PC22员工招聘/解聘/续约、所有职位和员工总数及精确Staff预算 |
| G08 | 当前PC22 Scouting报告全部字段及球探等级对报告进度/准确度的实际效应 |
| G09 | Historics/User-Draft-Class真正PC目标槽位布局、可靠来源和载入后的效果 |
| G10 | Lottery/真实Draft Result/选中新秀与球队合同/人员归属的可读回来源 |
| G11 | 游戏历史已存在保护或交换条款时的可靠原生识别与安全处理 |
| G12 | 最新游戏`game_date`、保存重载持久性及赛季推进/来源跨批一致性 |

**未知不等于不存在。** 当前轮不要求用户马上提供全部截图，不强行抓取游戏/修改任何对象，不把游戏源码中的占位/原始页面参考升级为可执行事实。

## 28. 最新选秀权交易世界政策（覆盖旧R05-B前三届说法）

**政策版本`PLAYER_RULES_20261021_V4`：已移除外挂世界的3届选秀权年限限制**，也**不另外设置5年硬上限**。技术事实仍是有据可查的本机Native已读未来5届资产，**更远选秀权是否存在及是否可交易目前未知**。资产身份和当前持有人仍必须被验证，不允许顺位保护与Swap，实际交易必须获玩家对具体批次的授权。

旧资料中`PLAYER_RULES_20261017_V3`、`NEXT_THREE_UNCOMPLETED...`及`DRAFT_PICK_OUTSIDE_THREE_YEAR_WINDOW`可作为历史记录或遗留代码搜索词，**不得再当现行世界业务规则**。[文档26](../../26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md)是文字版权威，[config/gameplay_policy.json](../../../config/gameplay_policy.json)是机读版。

**重要工程未同步项（非本轮代码任务）**：
- `src/draft_assets.py::trade_window()`函数`range(next_draft_year,next_draft_year+3)`；
- `src/gm_core/calculations.py::draft_pick_window()`仍`next_year+3`并返回`maximum_future_drafts=3`；
- `src/gm_core/trades.py`输出旧`DRAFT_PICK_OUTSIDE_THREE_YEAR_WINDOW`；
- `src/approved_trade_executor.py`仍调用旧函数，用户只批准了**世界政策更新**，**没有授权在DEV29运行新的交易**。

未来独立Codex开发若要落实本规则，必须保留原生资产唯一归属、允许年份由当前真实源决定、身份和执行支持判定、游戏保存和审批保障，且不能直接将`+3`机械改`+5`形成另一条人为业务限制。**这是一份已发现的工程差距说明，不是DEV29实施范围。**

同样应尊重现实2021–22 NBA最大可提前交易七年和Stepien，而系列2K19开发者说明MyLEAGUE新增到五年[SRC-0161/0162]；**这些是分别有证据的不同游戏/现实时期来源**，不能据此断言我们的PC22今天可以任意七年交易。

## 29. R05研究封存范围与下一阶段R06

**R05-A**：工资帽/财务/17合同Profile、21项市场概念及FA障碍；
**R05-B**：16交易菜单和14名单/资产结构、历史CBA多档规则、真实执行安全子集；
**R05-C**：8种本机员工位置、13 Staff Profile、10类球探和10类Draft候选；
**R05-D**：54项异质数据/候选、63类游戏操作/概念、12个跨域关系与12个原生缺口统一可查询；同步用户取消三年限制，并保留独立Code同步缺口。

R05系列网页研究**已完成本轮交付**，状态`R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`；**尚待其他模型按用户安排独立审核或批准结案**，本研究窗口不做自审式玩法判断、不声称Native UI全部验证。

下一轮**R06（NOT_STARTED）**：K05玩法/模拟器全局设置、K10历史规则纪元/奖项/舆论资料和K11存档覆盖、赛季/季后赛/游戏规则更新机制；只研究NBA2K20–23原生玩法、选项、动态信息、原生/可执行/未知差异，不设计媒体人格、执行游戏或替Coach/Player/GM做决策。

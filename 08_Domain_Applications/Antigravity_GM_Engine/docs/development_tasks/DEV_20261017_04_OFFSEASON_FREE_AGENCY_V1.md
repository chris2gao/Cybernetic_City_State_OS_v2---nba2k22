# DEV-20261017-04 | NBA2K22 休赛期自由球员签约闭环 V1

- 状态：SPEC_APPROVED_FOR_PLANNING_ONLY / CODE_NOT_IMPLEMENTED / GAME_WRITES_NOT_AUTHORIZED
- 规划角色：Web GPT DEVELOPMENT；工程实施：Codex；经营择队：Web GPT GM（玩家触发）
- 发起日期：2026-10-17
- 适用存档：玩家每赛季明确指定的 `save_id`；初始背景 2021–2022；不得硬编码当前存档
- 规则基线：`config/gameplay_policy.json` / `PLAYER_RULES_20261017_V3`
- 本文件只授权研发规格，不包含任何球员签约执行批准
- 关联：`AGENTS.md`、`web_gm/baselines/DEVELOPMENT_BASELINE.md`、`docs/33_DEVELOPMENT_BASELINE_PROMPT.md`、`docs/34_BASELINE_CURRENT_STATE.md`、`docs/36_EXECUTION_BASELINE_PROMPT.md`

## 1. 目的、范围和硬边界

玩家每次完整赛季结束后、下一赛季开始前独立触发本机制。扫描30队合同到期名单，合并为唯一候选池，进行球队合法报价、母队同价竞价及球员选队，生成需玩家逐项/整批明确批准的方案。获得具体批准且签约执行器通过实机验收后，Codex 才能执行并回读。玩家不触发则无后台模拟、不推进游戏日期。已有 CPU-to-CPU 交易关闭不意味着自由球员自动签约关闭，必须专项验证。

V1 范围：30支球队常规到期球员；经真实来源确认已是自由身的既有自由球员可纳入（如来源未认证，则仅到期扫描并报告自由球员池覆盖缺口）。正式合同期内球员、选项未解决者不可擅自投放到期池。V1 不做交易、先签后换、复杂保障/死钱、完整CBA、自动教练策略调整、球员能力/潜力/徽章/倾向编辑，不修改历史选秀进度。

基线虽有球员薪资/合同读取 profile，`src/gm_core/finance.py` 的薪资空间只是代理，不能认定合法合同资格。`docs/34` 记录球员签约与合同写回无完整验收执行器；开发必须先调查后实现，禁止因为有底层内存写能力就直接改队伍指针。已有通用玩家编辑阻断不得删除。

## 2. 关键规则（NBA2K22 当前存档优先；真实 NBA 2021–22 作为参考）

1. 赛季工资帽、奢侈税线、apron 读取本次新赛季经核对的游戏值或玩家确认且有来源的赛季规则；禁止沿用 `database/templates/save_template.json` 仅包含的2021–22参数解释2022–23及以后。初始参考2021–22：工资帽 $112,414,000；税线 $136,606,000；apron $143,002,000。未来赛季须有独立来源/游戏值。
2. 工资帽是合法签约容量基线，奢侈税线是超税财务影响起点，不是允许无限签约的开关；新签约在工资帽以上必须有可验证的游戏原生资格/特例。母队 Bird 等续约权仅在已验证时可使用。不要以 `cap-payroll` 或 `cash > 0` 充当签约许可。
3. 有限个人合同上限：NBA 2017 CBA 时代一般按资历分25%/30%/35%工资帽，特殊资格、前约105%等例外另行核对；新球队通常至多4年/年涨幅5%，有合格 Bird 续约权的母队通常可至多5年/年涨幅8%。这些数字仅为法规参考，必须受具体年份、游戏实际有效签约规则、选项和资格约束；身份/资历不明不得直接核发顶薪。
4. 母队对 UFA 只有最终同价 **报价机会**，球员仍可离开；只有已确认RFA+有效 qualifying offer 等条件才能依法强制匹配。母队即使报价相同，也须通过本队可用签约资格和财务门槛。若玩家希望所有到期球员原队均有强制匹配权，此属自定义玩法规则变更，不能擅自默认为现实规则。
5. 奢侈税对经营资金影响须Codex在当前2K22存档做“只读前后观测+非正式测试存档验证”，不能假设一次签约立刻从 `cash` 扣除税金，也不许自行重复扣税。若游戏本身在赛季结算扣款，只报告估算暴露，不作第二次财务写入。财务余额单位、符号、收支周期不明则 `UNKNOWN`。
6. 以游戏显示报价期望（若可验证读取）作为市场锚；否则只允许标记为 `HEURISTIC_PROPOSED` 的确定性价格建议，由GM复审，绝不把历史现实球员薪资写作本局实际索价。不得用未观测 OVR / 年龄默认值评分。
7. 尊重玩家确认的核心保护和 GM 经营目标，但已保护球员并非合同法上的不可离队人质；需要报价与球员择队解释。自然成长交给游戏。

规则来源：
- https://pr.nba.com/nba-salary-cap-for-2021-22-season-set-at-112-414-million/
- https://www.cbafaq.com/salarycap17.htm
- https://atlhawksfanatic.github.io/NBA-CBA-2017/uniform-player-contract.html
- https://www.nba.com/news/2022-free-agency-options-and-qualifying-offers

## 3. 先决专项调研 P0（不能跳过）

Codex 必须在**复制的测试存档**及当前NBA2K22版本逐项确认并保存证据：
- 休赛期游戏流程各节点：赛季结束、球队/球员选项、资格报价、球员续约、自由球员阶段、进入下一赛季。判定哪一节点可暂停、先读到期身份且CPU尚未自动签约；若做不到，返回 `OFFSEASON_SAFE_GATE_NOT_FOUND`，不可宣称闭环。
- 设置中是否支持30队用户管理+关闭 CPU 自动续约/自由球员签约，选项的**确切中文或英文名字、界面位置、对当前存档生效性、保存并重启后是否持续**。若无法防止原生 AI 在外挂提交后抢先签约或覆盖，返回 `NATIVE_AI_SIGNING_NOT_CONTAINED`，不得把系统视为无死角。
- 当前已认证 `src/source_extensions.py` / `config/memory_field_profile.json` 的 contract: `years_left_on_contract`、`contract_option`、`bird_years`、`contract_year_1..6`、球队薪资/预算/cash；证明游戏不同阶段剩余年限和逐年薪资的语义。现有月度 `contract_years_left` 不是已验收的“下一年自动自由球员”判定。
- 自由球员独立目录/球队映射/RFA+QO、服务年限、游戏要求年薪、可用空间/特例、最低/最高合同、可用名单席位等哪些可直接读到；逐字段区分 OBSERVED / VERIFIED_DERIVED / CONFIGURED / UNKNOWN。**独立休赛期专用最小来源**，不得扩大普通月度完整CBA采集。
- 游戏签约操作是优先调用原生UI/可用游戏机制，还是构造经过验证的最小写入；所有指针/数组/合同31位共享标志/球队合计和财务连动都需证明一致性、重启存档持久性。若无安全执行路径，完成分析提案部分并报告 `EXECUTOR_NOT_VERIFIED`。
- 核查 source catalog、实际库表和 `published` JSON 的可用合同字段；标注功能已实现/只有profile/仅预留/未观测，不偷换能力状态。

P0 交付 `docs/development_reviews/DEV_20261017_04_OFFSEASON_FA_P0_RESEARCH.md`，按证据注明可以进入P1/P2/P3或阻塞；不能未经实机核对就声明闭环。

## 4. 流程与状态机

显式玩家触发：`PLAYER_TRIGGERED` → `PHASE_GUARD_CHECKED` → `CAPTURED` → `EXPIRING_POOL_LOCKED` → `OFFERS_GENERATED` → `LEGALITY_CHECKED` → `HOME_COUNTER_OFFERED` → `ALLOCATED` → `PROPOSED` → `AWAITING_PLAYER_APPROVAL`。玩家可修改提案则 `REVISION_REQUESTED`，版本上升、重新验算。执行只通过另一个玩家批准阶段：`APPROVED_OUT_OF_BAND` → `EXECUTING` → `EXECUTED_VERIFIED`；失败 `BLOCKED` / `PARTIAL_UNRECOVERED`，不可自动推进赛季。玩家拒绝 `REJECTED`。不允许脚本或JSON自填 `approved=true` 获授权。

严格幂等键：`save_id + completed_season + offseason_run_id + approved_proposal_version`。同一版本重复生成不重复成交/扣预算；同一球员只出现一次，成功后不能第二次签约。同档不同赛季独立。

休赛期年度阶段顺序以实机核实为准，不能假设游戏已经把全部到期球员自动改为自由身。先检验冻结名单与现况一致；已变更者标 `SOURCE_STALE`，不得直接回写。

## 5. 统一候选池和身份契约

`OffseasonSnapshot` 最少：`save_id`、`completed_season`、`target_season`、`game_phase`、`source_batch_id`、`data_updated_at`、`policy_id`、`rules_version`、`native_ai_control_status`、30队覆盖率。记录游戏日期来源（玩家确认或已验证游戏字段）。

`FreeAgentCandidate` 最少：`candidate_id`、`verified_player_identity`、`display_name`、`previous_team_id`、`contract_years_left`、`next_season_salary_slots`、`option_status`、`free_agency_status=VERIFIED_UFA|VERIFIED_RFA|PENDING_OPTION|UNKNOWN`、`bird_rights_status`、`asking_salary`(可空)、`roster_provenance`、`coverage`。到期而选项未决则 `PENDING_OPTION`，不会擅自作为UFA。
- 同名球员、历史复制模型、slot号或指针不能单独充当永久身份。必须验证唯一实例及赛季边界前后连续身份；无法认证则拒绝。
- 到期球员 + 已经实际成为FA的球员合并、去重；如果FA池未知，明确覆盖范围，不能声称全部自由球员均受控。
- 普通合同期内玩家、尚未决定球队选项/球员选项者不得纳入。
- 适度保留原始只读证据，不把跨PID指针写进业务长期身份键。

`TeamSigningContext` 最少：`team_id`、`payroll_current`、`projected_next_year_committed_payroll`（来源未认证可空）、`cap`、`tax_line`、`apron`、`cash`（可空）、`budget`（可空）、`game_eligibility`、`validated_exceptions`、`available_slots`、`reserved_first_year_salary`、`pending_offers`。报价前与每次暂占/落定后重算；同队不可把相同空间分别用于多名球员。

## 6. 竞价计算 P1（确定性、短流程、不做复杂AI）

一次集中处理30队。每名符合资格候选最多经历：
A. 合同参考价确定：优先已认证游戏索价；无则给可解释的候选工资区间，状态 `HEURISTIC_PROPOSED`，由GM确认。个人金额必须落在已验证的最低与最高合同范围，支持首年/年限/递增表，不允许任意写一个总合同额。
B. 各队报价：优先考虑GM已经确认的球队阵容目标、位置需要、竞争力、预算；未确认策略时使用公开的、确定性的基础规则，必须能回放。不得假称每队已有GM偏好。每份报价先验证合规再进入候选列表；拒绝须记录原因。
C. 母队同价最终竞价一次：UFA仅得到竞价机会；RFA只有在真实确认匹配权时有法定匹配机制。母队报价也计入本队占用预算，不能超越游戏验证资格。**同价并不强制锁定UFA**。
D. 球员选择：以合同总待遇、预期出场角色、GM策略及母队留队倾向的**公开可配置评分**选择，固定权重/确定性同分决胜序列；不依赖随机浮点或不可复现模型输出。候选无合法报价则保持未签约，标 `UNSIGNED`。
E. 全联盟冲突消解：按统一顺序暂占可用空间和名单席位，每笔授予后重算其他待决报价；报价失效重新评估/落回下一合法候选，绝不让同一预算被重复使用。
F. 输出每队签约前后工资、距工资帽/税线/apron变化、可能奢侈税压力（如税公式或现金影响无法验证则UNKNOWN）、一名球员单一去向及未签球员清单。

合法性校验：`CAP_SPACE`、`VERIFIED_BIRD`、`VERIFIED_EARLY_BIRD`、`VERIFIED_NON_BIRD`、`VERIFIED_EXCEPTION`、`VERIFIED_MINIMUM` 等路径只有被实机/文档当前年度证实才标合法；未认证的权利不能自己“推定存在”。如果只实现工资帽内普通合同，必须明确 `V1_CAP_ROOM_ONLY`，不宣称原队能超帽匹配。超税经济约束为独立预算可承受度，不是替代薪资资格。

## 7. 对外协议（与 GM/分析/执行分离）

只读分析入口建议（名称可由Codex按现有CLI统一，不能冒充现存命令）：
- `scripts/offseason_capture.py --save-id ... --completed-season ...`：玩家触发；只读、来源审计、本地隔离记录；必要数据同步按玩家另行指定。
- `scripts/offseason_plan.py --save-id ... --snapshot-id ... --seed-strategy ...`：离线Python/SQL计算，给Web GM阅读的报告和结构化建议；**不连游戏内存、不自动执行/推进日期**。
- `scripts/offseason_validate.py --plan ...`：验证全部身份、合同和预算不变量、proposal版本、数据新鲜度。
- `scripts/offseason_execute.py --plan ...`：仅当后续**另行批准且经过验收**才出现的受控执行入口；不能与规划阶段拼成自动链路。

建议 `src/gm_core/offseason.py` 实现纯规则/竞价；`src/gm_core/finance.py` 扩展只读判断时不得误标静态proxy为已认证空间；可增`src/offseason_source.py`和`src/offseason_executor.py`分别处理实际采集/受控写入。具体文件布局由Codex根据源码定，但`gm_core`仍禁止import游戏写入/实时内存。

输出 `offseason_run.json`、`expiring_candidates.json`、`free_agency_offers.json`、`offseason_proposal.json`、`OFFSEASON_SUMMARY.md`；以每次save/season/run隔离，不篡改`published/`事实包。正式建议携带candidate / game-state version / source batch / GM strategy source / policy_id / calculation refs / decision_id / version / status=PROPOSED。执行回执包含 before/after、实际完成字段、拒绝、实机存档重启验证和未完成项。GM总结由GM基线保存，开发基线不代替GM批准。

## 8. 执行器 P2 和原生AI防干扰 P3

P2：单笔签约执行器在**非正式测试存档**验证写入合同逐年工资、合同年限、合同选项/正确球队归属、球员/球队双向关联、薪资统计、名单席位、存档后重启读取，必要的游戏财务机制由游戏自身计算。写入须在独立真实批准之后再准许正式局使用；不得直接覆盖31位薪资共享位或整个结构。对每个操作先比较冻结原值和live原值，失败回滚测试存档/停机；完整交易执行器不能被当成已实现的签约执行器。

P3：验证在外挂建议、审核及签约窗口，游戏不会自动产生另行签约；关闭自动化若只针对用户控制队有效，则验证是否需30队全控制，以及实测后续游戏阶段是否回写/撤销人工签约。若2K22不能关闭签约，需设计明确的停点与逐步推进/检测/纠偏方案，经玩家确认后单独批准；**绝不**承诺100%关闭自动签约而无实测证据。游戏进入新赛季后再次只读核对30队名单，异常输出 `NATIVE_OVERRIDE_DETECTED`。

## 9. 测试验收必须覆盖

- 模拟30队、多名不同队到期球员，全集/无重复/无遗漏；验证合同仅本季结束到期。
- 球队/球员选项未决、RFA无有效QO、UFA母队同价但球员选择外队、合资格RFA匹配。
- 超帽无签约资格拒绝；合资格Bird超帽但超税可以产生财务警告；错误将奢侈税线视为无限签约许可必须拒绝。
- 两球员争同队同一剩余空间；多队同时竞逐一球员；同价确定性择队；第一报价被占用后落到下一报价。
- 最低/最高合同、年限/涨幅、2022–23缺规则、未观测球员资历、缺工资/预算、负值或溢出、两名同名或历史克隆。
- 重复同一run调用、跨赛季/跨save、来源批次过期、游戏原生AI已签约、球员转队后重跑。
- 未批准时所有内存写次数=0、默认CLI只读、属性写入=0；无验证执行器返回BLOCKED。
- 通过测试存档实机UI核对 + 存档退出重进持久性 + 原生自动签约干扰测试；回读单笔和30队汇总。实机没测试不得把“单元测试PASS”标“生产游戏签约PASS”。

确定性金额采用整数美元/分明确精度，绝不使用未验证货币换算；所有UNKNOWN保留。

## 10. Codex 阶段交付顺序和完成定义

- P0（最高优先级，调研）：赛季安全停点、AI自动化干扰、合同/财务/身份字段、签约真实可操作性；交`docs/development_reviews/DEV_20261017_04_OFFSEASON_FA_P0_RESEARCH.md`。阻塞项不掩盖。
- P1（只读完整模拟）：合同到期检测/候选池、全年份工资规则接口、合法出价与母队竞价、统一占用与确定性择队、JSON/Markdown方案、单元测试；不运行正式GM、不采集正式存档除非玩家另行触发。
- P2（安全执行）：先做复制测试存档的合规签约写入/回读/重启验收，另行确认与交易/现有审批协议兼容。成功才记录受控业务能力。
- P3（端到端防漏）：完整休赛期暂停→计划→独立批准→执行→下赛季复核；不能阻断CPU原生签约时不得宣布闭环已解决。

Codex 应按其`docs/33`开发基线执行，在对应功能落地后更新`docs/34`能力索引、相关来源登记/操作文档、必要的`docs/36`执行状态；提供 commit、命令、测试证据、未验证边界。网页开发基线随后独立代码审查。开发完成 ≠ 玩家同意本赛季签约或允许改动正式存档。

## 11. 必须回报玩家的关键结论

1. 是否可以在游戏尚未自动签约前冻结真实休赛期？
2. 是否能真正关闭所有30队原生AI自由球员签约？
3. 到期/选项/RFA/原队权利和正确球员身份，哪些字段已实测？
4. NBA2K22的实际工资、奢侈税、资金影响与外部账本怎样对应？
5. 新赛季个人合同最高额、最短额、年限涨幅怎样获得和验证？
6. 能否安全签约且保存重开后持续生效？
7. 明确哪些只完成开发与离线测试，哪些经过真实游戏测试。

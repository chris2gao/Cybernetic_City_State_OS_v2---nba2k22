# W03 / R02 · A组10队深度GM经营报告（正式决策前研究阶段）

- `decision_node=GM-S2021-2022-W03`；`round_id=W03-R02`；`stage=DEEP_TEAM_RESEARCH_GROUP_A`；`protocol=GM_MIN_FIVE_ROUNDS_V3 + GM_DATA_TO_DECISION_V1`。
- `career_id=mc_haliburton_2021`；`game_season=2021-2022`；`game_date=2021-12-12`（PLAYER_CONFIRMED，`month_closed=false`）；`source_batch_id=2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`；审计`PASS_VERIFIED`、同批教练`VERIFIED_OBSERVED_SAME_BATCH`。
- **本轮完成**：PHI/MIL/WAS/CHI/CLE/BOS/LAC/MEM/ATL/MIA 10队；**157/157大名单记录**逐人核对身份、55项原生能力（按需提取主要能力）、真实赛季数据/无数据状态、合同/潜力/角色、长期成长可能性。完整机器可读结果：[本轮深度JSON](ROUND_R02_GROUP_A_TEAM_DOSSIERS.json)；各球员均附同批源路径。
- **阶段边界**：本轮是真正逐队六维经营研究，不是最终跨队交易协议。当前5队有`COACHING_PROPOSED`篮球意图，5队`COACHING_HOLD`；均未生成/签发原生教练batch digest。此轮不修改游戏、不自动模拟、也不把这里提出的员工变动当已验证写回。用户希望真正执行后去游戏体验效果：**未来最终批准后依受控执行器交给Codex，实机结果由玩家检验即可；不额外设置事先A/B胜率验证的硬闸门**。
- **员工来源特殊说明**：原始`staff.json`已发布且`staff_pool=VERIFIED_RECIPROCAL_TEAM_ROLES`，30队8岗位（240岗位映射）身份来源可审计；但该文件约2.7MB，本次连接器返回空文件内容，无法核验其余7岗位的各队员工姓名/个人能力。本轮主教练本人由同批`coaching/teams.json`已核实；其余员工在结构化档案中标明`AUDITED_SOURCE_EXISTS_NOT_RETRIEVED_IN_SESSION`，没有虚构员工评级或换帅加成。该问题只影响非主教练员工的可执行任免判断，不妨碍研究当前已认证的教练战术字段；如果以后拟提交具体人员更换，执行前必须取得真实staff身份/候选与完整双向安全接口。
- **统计口径**：当前`games_played/ppg`是球员整个游戏赛季的累计，不能表示交易后来队的场次；`M01→M02`是检查点期间区间而非“整个12月”；净胜是**每场得失分差**，不是百回合净效率。球员`overall_rating=null`、伤病/疲劳与个人精确分钟控制均不可被虚构。

## 第一节：全组竞技态势与新旧机制对比

| 球队 | 累计战绩 | M01→M02增量 | 季均得/失/净 | 当前主教练 & ActiveSystem | A组决策 |
| --- | --- | --- | --- | --- | --- |
| PHI | 20–6 | 4–3 | 118.77 / 111.50 / **+7.27** | Doc Rivers，POST(4) | **HOLD**，保Embiid/Simmons和既有内外优势 |
| MIL | 14–12 | 3–4 | 119.81 / 110.46 / **+9.35** | Mike Budenholzer，DEFENSE(7) | **HOLD**，别把胜率波动误判为防守差 |
| WAS | 17–9 | 7–1 | 119.73 / 116.15 / **+3.58** | Wes Unseld Jr.，DEFENSE(7) | **HOLD**，保护Beal+射手赢球窗口 |
| CHI | 15–11 | 4–3 | 119.31 / 115.77 / **+3.54** | Billy Donovan，BALANCED(0) | **HOLD**，Grant到队时间线未分离 |
| CLE | 9–17 | 3–4 | 115.65 / 120.23 / **−4.58** | J.B. Bickerstaff，DEFENSE(7) | **COACHING_PROPOSED**，减少外围投射暴露 |
| BOS | 13–13 | 3–4 | 118.50 / 115.08 / **+3.42** | Ime Udoka，BALANCED(0) | **COACHING_PROPOSED**，发挥防守双翼 |
| LAC | 11–15 | 3–5 | 118.15 / 116.46 / **+1.69** | Tyronn Lue，DEFENSE(7) | **COACHING_PROPOSED**，强调外围防守 |
| MEM | 14–12 | 4–4 | 115.62 / 113.85 / **+1.77** | Taylor Jenkins，BALANCED(0) | **HOLD**，Brogdon新加盟先磨合 |
| ATL | 12–13 | 1–5 | 120.88 / 121.00 / **−0.12** | Nate McMillan，PERIMETER(3) | **COACHING_PROPOSED**，保护禁区 |
| MIA | 16–10 | 3–4 | 115.38 / 117.62 / **−2.23** | Erik Spoelstra，PACE_AND_SPACE(2) | **COACHING_PROPOSED**，球队回归防守取向 |

不同球员的“分数”不可直接当人数或阵容胜率模型。比如MIL强势净胜与中游战绩显著背离，首先要保留阵容而非提出一笔基于战绩的贱卖核心交易；MIA则拥有防守人才但累计净负分，值得控制变量调整一个战术参数，待玩家真正比赛后复盘。

## 第二节：十队逐队经营论证

### A01 · Philadelphia 76ers（PHI）——保住“内线重力+组织外线”的强队壁垒

**事实**：20–6、场均净胜7.27，当前进攻团队eFG≈56.0%。Embiid 26.6分/12.6篮板、内线防守96/盖帽82；Simmons 16.3分/9.3助攻/外围防守87，外线三分仅58。Harris18.8分/三分84、Seth Curry三分90、Danny Green外防87为内线构成空间与防守互补。Drummond 14.2分/12.1篮板，但外线三分47；Thybulle外围防守90且进攻使用有限。年轻Maxey 21岁、潜力80。

**人员/教练评估**：Doc Rivers 的`ActiveSystem=POST(4)`、`Preferred=GRIT_AND_GRIND(1)`，虽不一致但前者与Embiid适配，不能机械同化；`BenchDepth=9`、`BenchUtilization=60`，无必要为了新功能做调整。真正的问题是Simmons外线能力不足和双中锋空间负担。正确的球队内部策略是让射手与Embiid/Simmons构成互补、加强Thybulle和Green对投射点的防守，而非将Drummond/Embiid同时定位为外线空间点。其他员工未能完整读取，不对个人人事任免作指令。

**六维决定**：`STAFF_HOLD / COACHING_HOLD / INTERNAL_ROLE_REVIEW / MARKET_HOLD / CORE_ASSET_HOLD / PHILOSOPHY_HOLD`。2022–24当前持有3首轮+5次轮；争冠队不能因一个替补中锋合同即卖掉可替代成本较高的阵容深度。**下轮只看**现有内外组合的团队进攻真实变化，若真实胜率持续较高，继续不动。

### A02 · Milwaukee Bucks（MIL）——不是缺实力，而是净胜分尚未转化为战绩

**事实**：14–12、场均119.81分、失110.46、**净胜+9.35**，M01→M02阶段3–4但增量净胜+10.71。Giannis27.3分、外围防守95/内线91；Middleton20.2分/三分86；Jrue外防94、Lopez内防87/盖帽83；DiVincenzo三分81/外防82、Portis三分83。Jrue本季仅14场记录、不能将26场球队成绩都当其个人表现。

**人员/教练评估**：Budenholzer已有`ActiveSystem=DEFENSE(7)`，`BenchDepth=10`、`RunPlayTendency=85`，与防守天赋契合。出手空间主要由Middleton/Portis/Lopez/外围射手帮助Giannis冲击，未见战术重构刚需。若贸然拆掉Jrue或调低防守强度，会损失已验证的防守优势。其他员工特性未从源中有效提取，维持原配。

**六维决定**：`STAFF_HOLD / COACHING_HOLD / INTERNAL_SPACING_REVIEW / MARKET_HOLD / CORE_HOLD / PHILOSOPHY_HOLD`。2022–24当前仅1首轮+3次轮，远比某些重建队资产薄，不能浪费少量首轮追逐边际改善。下一步观察同口径胜率是否自然回升，别用26场成绩否决+9.35的强势净胜分。

### A03 · Washington Wizards（WAS）——保护Beal火力，先防守错位补救

**事实**：17–9、近期7–1，球队eFG≈58.1%。Beal39.05分/37.5分钟；Dinwiddie7.2助攻/三分78；Kispert三分85、Bertans86、Bryant81、Hachimura80；KCP外防84、Gafford盖帽95。相反Bertans外防40、Bryant40，防守短板非常集中，而非30队都一样。

**人员/教练评估**：Wes Unseld Jr 的现役`DEFENSE(7)`、`BenchDepth9`、`BenchUtilization65`不能表明“球队没防守策略”；更可行的建议是用KCP/Gafford保护外线射手和篮下，而非为改善防守将Bertans/Kispert等射术全部送走。Beal实际上场较高，但精确分钟交AI，只监控后续真实数据。当前已经7–1，不批准重复大手术。

**六维决定**：`STAFF_HOLD / COACHING_HOLD / INTERNAL_DEFENSE_ROLE_INTENT / MARKET_INTEREST_CANDIDATE_ONLY / ASSET_HOLD / PHILOSOPHY_HOLD`。3届仅2首轮、0次轮，未来签位缓冲弱。可在D4讨论高名义薪资Bertans换防守翼的双边机会，但要证明价值并且不破坏场均119.73进攻。近期成果优先于理论更美的纸面阵容。

### A04 · Chicago Bulls（CHI）——Grant到队后先解决球权与补防协同

**事实**：15–11、近期4–3。LaVine31.53分（17场）/三分86；DeRozan24、Vucevic21.5/6助攻、Lonzo8.2助攻且外防86、Caruso外防86、Patrick Williams三分82。新加盟Jerami Grant19分/33.4分钟为**全季累计含DET效力阶段**，不能当作在CHI的精确贡献。Vucevic内防76盖帽57，三分83。

**人员/教练评估**：Donovan的BALANCED(0)、`BenchDepth=9`、`RunPlayTendency85`可容纳多个持球点，当前更主要风险是LaVine/DeRozan/Grant资源重叠、Vucevic防守端容易被点名。应让Lonzo主组织，Vucevic策应，Grant有选择地补防，Caruso在对手强后场时增加使用倾向——不能固定某个人上场分钟。其他员工暂HOLD，不因Grant首次登场结构不明便大换教练。

**六维决定**：`STAFF_HOLD / COACHING_HOLD / ROLE_FIT_OBSERVE / MARKET_HOLD / CORE_HOLD / PHILOSOPHY_HOLD`。目前2022–24仅2首轮+1次轮。W02已批准并执行的Grant交易不可重复，旧Coby White/Derrick Jones Jr不再作为公牛可报价资产。继续观察新阵容真实的场上作用后再决定要不要交易护框位。

### A05 · Cleveland Cavaliers（CLE）——双后卫外围短板，优先小幅防守战术更改

**事实**：9–17、场均净负4.58、失分120.23。Sexton28.7分/外围防守67、Garland18.6分/7.3助攻/外防65，同场两人有被强后卫攻击的风险。Mobley20岁、潜力93、盖帽84；Jarrett Allen内防82/盖帽81；Okoro外防78、Rubio78；Love三分80、Markkanen81为双内线空间提供备选。

**人员/教练评估**：Bickerstaff已经使用DEFENSE(7)，仅凭战绩更换教练并无理由。真正的取舍是双后卫保留进攻，但依赖Okoro/Rubio和Mobley/Allen组成外围—内线协防链。教练默认当前`POEDefense=14 NEUTRAL`、`HelpDefense=35`、`BenchDepth9`，提出**只改一个值**：
`GM-W03-R02-CLE-C01` = `POEDefense 14 → 15 (LIMIT_PERIMETER_SHOTS)`。
其余默认字段保持真实原值，不修改个人分钟。**风险**：过度向外围延伸会增加内线空位和前场犯规负担，必须由玩家游戏实测。

**六维决定**：`STAFF_HOLD / COACHING_PROPOSED / INTERNAL_DEFENSIVE_ROLE_INTENT / SEXTON_MARKET_RESEARCH_ONLY / YOUTH_CORE_PROTECT / IDENTITY_DEFENSE_FIRST`。3首轮+3次轮；Garland/Mobley/Allen不得因单月战绩草率送走，Sexton一年合同进入后续D4市场估价而非本轮同意成交。下次看失分、后场产量及双塔防守能力真实变化。

### A06 · Boston Celtics（BOS）——精英侧翼防守被低效内线轮换稀释

**事实**：13–13，但场均净胜+3.42。Tatum23.4分/外围防守89、潜力96；Brown22.7/外防87；Smart外围防守93；Richardson外防87；Robert Williams盖帽96（场均26.2分钟）、内防76。Kanter内防52/外防26，却在当前赛季场均24分钟；Horford内防82、三分81，Grant Williams三分82但尚无本季出场记录。

**人员/教练评估**：Ime Udoka平衡体系能同时容纳双翼得分与外围压迫，但`BenchUtilization=75`和`BenchDepth10`意味着AI会广泛使用不同能力轮换；不调整个人分钟，仅提内部角色优先级和防守重点。当前`POEDefense14`中性，考虑以Smart/Tatum/Brown/Richardson限制射手与切入发起：
`GM-W03-R02-BOS-C01` = `POEDefense 14 → 15 (LIMIT_PERIMETER_SHOTS)`。
反面风险是Kanter上场时内线仍可能失守，Robert Williams封盖不能替代全部防守职责。

**六维决定**：`STAFF_HOLD / COACHING_PROPOSED / INTERNAL_BIG_ROTATION_REVIEW / KANTER_MARKET_CANDIDATE_ONLY / JAY_CORE_HOLD / DEFENSIVE_WINGS_IDENTITY`。3首轮+3次轮。阶段性只改变一个战术变量，D4可对Kanter合同与其它球队防守中锋资源研究双方互补；未谈妥不动。

### A07 · Los Angeles Clippers（LAC）——不是“没有防守人”，而是没兑现顶级双翼

**事实**：11–15、区间3–5，季场均118.15得分、失116.46，净胜+1.69。Paul George26.5分/外防92、Leonard21.8/外防97，Bledsoe外防86、Ibaka内防80/盖帽82；Morris三分88、Kennard85、Batum84，空间足以支持双翼进攻。当前实际进攻并非极差。

**人员/教练评估**：Tyronn Lue的`ActiveSystem=DEFENSE(7)`、`Preferred=BALANCED(0)`，并不自动说明错误，而是应检查球队精英防守能力能否限制对方外线投射；`BenchDepth10/HelpDefense35/ZoneUsage8`。提出**单项防守重点**：
`GM-W03-R02-LAC-C01` = `POEDefense 14 → 15 (LIMIT_PERIMETER_SHOTS)`。
不用改变球队PreferredSystem，也不把Kennard个人定时上场作为前提。若对手反而攻击禁区，Ibaka/Zubac前场轮换的局限需重新分析。

**六维决定**：`STAFF_HOLD / COACHING_PROPOSED / WING_DEFENSE_ALIGNMENT / BLEDSOE_VALUE_RESEARCH / KAWHI_PG_PROTECT / TWO_WAY_WINGS_IDENTITY`。1首轮+3次轮、战绩不符竞争预期。Bledsoe年薪约18.1M、外防86但仅7.4分，若D4能证明换来更合适的后场进攻需要独立卖方接受；不无偿牺牲防守。

### A08 · Memphis Grizzlies（MEM）——Morant/JJJ与新Brogdon需先形成持球互补

**事实**：14–12、区间4–4。Morant27.9分/7.1助攻、潜力94；JJJ19.6分、内防82盖帽89；Brogdon个人赛季累计18.6分/6.2助攻（27场，很可能跨IND→MEM），并不等于在MEM已打27场。Brooks外防85、Melton81、Bane三分84、Adams内防82，轮换在攻防两端不薄。

**人员/教练评估**：Taylor Jenkins Balanced(0)与多持球和年轻空间阵容适配；`BenchDepth=10`、`BenchUtilization70`，未见为了提高短期战绩改变多个POE字段的必要。GM真正应做的是Morant第一发起、Brogdon二次组织、JJJ既保护篮筐又有一定空间、Bane/Melton控制防守角色重叠。不要让赛季全时期Brogdon表现冒充转队后效果。

**六维决定**：`STAFF_HOLD / COACHING_HOLD / NEW_BACKCOURT_ROLE_OPTIMIZATION / MARKET_HOLD / YOUNG_CORE_HOLD / YOUTH_ATTACK_IDENTITY`。已实测三届6首轮+4次轮，长期资产丰富，但不能因此为每个月都挑一笔交易。等真实新阵容增量比赛表现可核实再决定是否出售冗余替补后卫。

### A09 · Atlanta Hawks（ATL）——优先修补外围被点名后的禁区损失

**事实**：12–13、区间1–5，本季120.88得/121.00失。Trae23分/7助攻仅15场，外防54；Bogdanovic三分85/外防63、Huerter三分82/外防64；Capela内防86/盖帽88、15.4篮板，Hunter/Reddish外防81、Okongwu内防79/盖帽83。进攻已很有力，核心问题是对方攻击薄弱外防点。

**人员/教练评估**：McMillan的`ActiveSystem=PERIMETER(3)`保留Trae与射手群，虽`Preferred=GRIT_AND_GRIND(1)`但不能强行替换为磨阵地。尝试以中锋护框优先弥补外线失守：
`GM-W03-R02-ATL-C01` = `POEDefense 14 → 13 (PROTECT_PAINT)`。
注意可能让对手远投更自由；Hunter/Delon可在AI轮换中提供较好的外围防守，不锁分钟。R01提过ATL→GSW`ScreenDefenseOnBall 0→1`，**本轮从已审批候选中降回D4再评估**：该18项OVERALL对每名有效对位统一生效，不应为了限制Curry就无差别让全队面对GSW所有挡拆都采用相同策略。

**六维决定**：`STAFF_HOLD / COACHING_PROPOSED / RIM_DEFENSE_REBALANCE / GALLINARI_MARKET_RESEARCH_ONLY / TRAE_CAPELA_CORE_PROTECT / PNR_IDENTITY`。3首轮+5次轮；Gallinari三分84、外围防守56，年薪约20.5M，可询价更均衡侧翼，但交易必须保障Trae场上空间，后两轮再谈。

### A10 · Miami Heat（MIA）——防守型核心有能力重建球队身份

**事实**：16–10，却是本组唯一胜率较高且赛季净负分的队伍：115.38得/117.62失、净负2.23，eFG约53.4%。Butler25.3分/外防90、Bam18.0分/内防92、Lowry16.6分/外防86、Oladipo外防84、Tucker外防80；Robinson三分90、Herro三分81。属于**明明有防守骨架，当前体系却优先P&S**的典型可运营对象。

**人员/教练评估**：Spoelstra的`PreferredSystem=DEFENSE(7)`而`ActiveSystem=PACE_AND_SPACE(2)`；这本身不是错误，但和可用球员防守能力、球队场均失分一起使调整有实际篮球理由。优先尝试：
`GM-W03-R02-MIA-C01` = `ActiveSystem 2 → 7 (DEFENSE)`。
只改现行体系，不动Preferred、POE、Freelance和个人分钟；**保留Robinson/Herro作为外线空间，避免将全队改成不会投三分的防守阵容**。轻方案则是保留ActiveSystem、只把POEDefense转向外围限制，但两者不能同时作为“单变量小改”混淆效果。

**六维决定**：`STAFF_HOLD / COACHING_PROPOSED / SPACING_DEFENSE_BALANCE / MARKET_HOLD / BAM_HERRO_CORE_PROTECT / MIAMI_DEFENSE_IDENTITY`。2首轮+2次轮，年龄结构不宜为短期净负分而高价换老将。下一批由你实机反馈净胜分、失分、射手效率，若球队进攻大降则对DEFENSE体系提出回撤。

## 第三节：A组教练五项实际可落地的原生字段意图

以下目标按同批`coaching/teams.json`和`coaching/field_dictionary.json`的**合法原生值与readiness**筛查，可直接作为未来Codex篮球意图输入。**本文件不是原生执行批次，没有真实batch_digest、未取得玩家批准，不能直接执行。** B/C组研究完后D4再核对跨队依赖和执行方案，最终D5生成真实审批包。

| 本轮Action ID | 球队/现任主教练 | 原生`COACH_DEFAULT`字段 | 当前raw→目标raw | 风险/备选 |
| --- | --- | --- | --- | --- |
| `GM-W03-R02-CLE-C01` | CLE / J.B. Bickerstaff | `POEDefense` | 14 NEUTRAL → **15 LIMIT_PERIMETER_SHOTS** | 外围重点可能漏篮下，HOLD或人员轮换替代 |
| `GM-W03-R02-BOS-C01` | BOS / Ime Udoka | `POEDefense` | 14 NEUTRAL → **15 LIMIT_PERIMETER_SHOTS** | 无法消除Kanter防守弱点，需组合配合 |
| `GM-W03-R02-LAC-C01` | LAC / Tyronn Lue | `POEDefense` | 14 NEUTRAL → **15 LIMIT_PERIMETER_SHOTS** | Kawhi/PG优势，但可能漏对手突破 |
| `GM-W03-R02-ATL-C01` | ATL / Nate McMillan | `POEDefense` | 14 NEUTRAL → **13 PROTECT_PAINT** | 外围射手投篮更自由；对GSW专项另留D4复核 |
| `GM-W03-R02-MIA-C01` | MIA / Erik Spoelstra | `ActiveSystem` | 2 PACE_AND_SPACE → **7 DEFENSE** | 核心防守发挥但Robinson/Herro进攻空间可能下降 |

- **教练动作说明**：现任主教练个人身份、team_id、同批目标字段readiness与`roster_signature`等真实元数据已随结构化档案引用，**执行模型**须在最终批准的最新同局进程重新预检身份/原值，生成受控patch并回读。模型在此不会手写32bit混合字段或任何digest；不调整五Sim、Tempo或个人球员数值。
- **换帅判断**：10队主教练全部`STAFF_HOLD`；这是基于可以先使用已验证战术配置且没有独立员工效果证据的**有因保留**，不是说主教练永远不可替换。其余7岗位本回合无未经身份查验的人事指令。
- **交易状态**：本轮没有宣告跨队真正谈判成立。WAS的Bertans、CLE的Sexton、BOS的Kanter、LAC的Bledsoe、ATL的Gallinari只是**研究/可能出售**候选，须等B/C两组真正独立GM的价值需求，逐资产核价，不先决定去向。其他五队大体保留当前核心。

## 第四节：R02质量验收与阶段移交

| 检查 | 实际结果 |
| --- | --- |
| 研究球队身份 | 10/10，队名不重复，属于预定组A |
| 逐人球员覆盖 | **157/157，同批M02大名单；来源slot集合一致且组内单队不重复** |
| 每队六维决策 | **10/10**；保留与修改都附竞争逻辑和备选 |
| 正式主教练与战术数据 | **10/10同批coach身份及完整19项**；对手组尚无最终动作 |
| 其它7类员工的本会话姓名读取 | **受GitHub大文件限制未恢复**；由已有原源审计存在，**不得生成具体人员变动** |
| 交易定案 | 0；前10队提出市场信号待剩余20队比较 |
| 原生教练动作 | 5条业务目标，现值/目标均从同批字典验证；无完整native batch/digest |
| 玩家批准与游戏执行 | **0；未修改游戏** |

本轮的人员评估以**每队15–17位全大名单记录**为准，来源身份证据和所有球员关键能力详见机器JSON，不把本人的手工摘要假装成覆盖整个球员池。

### 下一步（仅玩家下次明确继续才发生）

- `W03/R03`：组B = NOP、UTA、SAC、NYK、LAL、ORL、DAL、BKN、DEN、IND。重点与A组市场需求和教练调整策略相互参照，**但此时尚不形成成交协议**。
- `W03/R04`：组C = DET、TOR、HOU、OKC、SAS、PHX、MIN、POR、GSW、CHA。尤其验证R01旧CHA↔SAS的Poeltl/P.J.Washington交易是否仍双赢，不能先假定成交。
- `W03/R05`：全30队交易双边报价、体系协调、员工机制与关键对手防守整体比较；R01旧12条战术及T01由此才能升级或淘汰。
- `W03/R06`：唯一最终提案，按玩家明确批准分解交易/教练原生执行对象，交Codex执行模型。玩家实际游戏体验就是效果验证的权威来源之一，不预设固定胜率公式。

**跨批玩家观察**：只有玩家另行推进游戏及触发数据更新后，GM才可将效果归纳为`IMPROVED/WORSENED/INCONCLUSIVE`；不用额外跑游戏测试以证明教练战术能生效，也不手动改球员成长。

**来源**：[最新游戏数据入口](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/latest.json) · [M02原生球队JSON目录](https://github.com/chris2gao/nba2k22-gm-engine/tree/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/teams) · [同批教练配置](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/coaching/teams.json) · [字段字典](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/coaching/field_dictionary.json) · [M02赛季球队总数](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/season_totals.json) · [三届选秀权记录](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/draft_assets.json) · [同批M02 V2分析参考](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_ANALYSIS_ONLY.md)。

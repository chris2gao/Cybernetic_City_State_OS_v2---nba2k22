# BPTI — R1 真实篮球体系与战术认知深度研究

## 研究边界与核心结论

本研究严格按照BPTI总规划和三研究流分工执行。DEV19已经把BPTI定义为M系列之上的“篮球认知层”：M系列解决数据、财务、球队经营和执行能力，BPTI解决球队**为什么这样打、球员为什么承担这个职责、对手改变防守后为什么必须改变下一步篮球动作**。体系不能等同于某个命中率目标，也不能把30支球队压缩成同一套效率函数。fileciteturn1file0L2-L2 DEV21进一步要求R1研究“优势产生→防守反应→阅读→二次/三次调整”的因果链，并明确球员自由应理解为“结构内的选择权”，而不是无边界自由。fileciteturn2file0L2-L2

已有M2的十二张战术卡是重要基础，但它们主要回答“挡拆、空间、传切、转换、低位、换防、沉退、协防”等单项篮球概念，还没有形成一套能解释**体系之间组合、角色决策权、反制链和体系演化**的完整篮球认知模型。fileciteturn3file0L2-L2

本轮不研究NBA 2K22内存、字段地址或执行映射，也不负责30队组织历史。用户此前提供的Calendar Fast-Sim滑块规范属于独立的双引擎校准研究流；它可以将来校准数据源，却不应反过来定义“什么篮球是正确的”。fileciteturn0file0

### R1最重要的研究结论

**BPTI不应该把“体系”存成一张静态标签卡，而应该把它表示为一个篮球因果图。**

最基本的认知单元应当是：

**进入条件 → 第一优势 → 防守选择 → 球员阅读 → 第二优势 → 再反制 → 应急创造**

例如Spread Pick-and-Roll不是“多打挡拆”，而是：

> 持球人借掩护制造两防二/两防三决策  
> → 防守沉退，则攻击中距离、抛投或迫使大个上提  
> → 大个上提，则顺下/短顺下  
> → 弱侧收缩，则传底角或45度  
> → 防守换防，则重新掩护、清空单打或高低位惩罚错位  
> → 防守夹击，则短顺下形成4打3。

FIBA官方战术分析反复展示了这种逻辑：面对hard hedge，掩护人short roll；面对drop，持球人利用空间；弱侧帮助发生后，把优势转移至帮助来源；对换防可以重新掩护或利用错位，而不是仅仅重复同一个动作。citeturn12search1turn12search3turn16search5

这意味着BPTI最终真正需要理解的不是：

> “三分比中距离高效。”

而是：

> “对方为了阻止什么而放出了什么？我们的哪个球员有能力利用那个空间？如果对手再改变，我们还有什么答案？”

这才是真正的篮球推理。

另一个核心发现是，**战术结构与球员创造力不是对立关系**。优秀体系恰恰通过结构减少无意义决策，把真正需要创造力的节点交给合适球员。FIBA案例中存在预先设计好的cut、short roll和spacing，但最终仍要求球员辨认防守覆盖后做出不同选择；Anwil教练也强调球员必须理解“如何、为什么、在哪里”进攻，而不是机械背动作。citeturn12search1turn16search3turn16search8 Kerr描述勇士体系时同样强调持续移动、掩护、切入经过长期磨合后会变成球员的本能，而不是等待孤立单打。citeturn14search3

因此，我建议R1给BPTI留下一个非常明确的“球员决策权”概念：

| 决策层 | 含义 | 举例 |
|---|---|---|
| **SCRIPTED_ENTRY** | 教练规定如何进入进攻 | Horns、post entry、pindown、drag screen |
| **STRUCTURED_READ** | 球员必须根据防守在有限选项中阅读 | drop→pull-up；blitz→short roll；overhelp→kick-out |
| **CREATIVE_OPTION** | 球星可在结构内利用个人技术创造新优势 | 中距离急停、错位单打、低位face-up |
| **BAILOUT_RIGHT** | 战术被完全破坏后由指定创造者处理困难回合 | shot-clock末段单打/困难球 |
| **RESET_RIGHT** | 没有优势时主动放弃第一动作并重置，而不是强投 | reversal、re-screen、重新进入第二侧 |

这种分层比“自由度高/低”更加接近现实篮球，也非常适合后续BPTI编码。

## 现实篮球中的共同机制与球员创造力

十种体系并不是十套互斥模板。研究资料更支持把篮球看成若干可组合的**优势制造机制**。

### 空间本身不是目的，空间是为了制造决策距离

优秀进攻并不是简单地让五个人站远。空间的真正作用，是延长防守帮助与恢复之间的距离和时间。

Holon的FIBA案例就是典型：弱侧球员移动改变“谁负责帮助roller”，短顺下迫使角落防守者进入协防，随后传球到帮助来源，防守就必须完成一次极困难的长距离恢复。citeturn12search3

所以BPTI以后看到“五外”“四外一内”，不能直接判断好坏，而应该继续问：

**谁迫使第一名防守者移动？谁迫使第二名防守者帮助？谁站在帮助来源？接球后他有没有能力继续制造优势？**

### 掩护真正改变的是对位和责任，而不仅是挡住一个人

2021年总决赛第一场，Phoenix在Brook Lopez上场后的前八个进攻回合里几乎不断把他卷入挡拆或DHO，不论Milwaukee采用什么基础覆盖。这个案例说明挡拆的核心价值之一是**主动选择哪名防守者进入决策**。citeturn15search0

换防也不会终结挡拆逻辑。换防只是把问题从“二防二覆盖”变成“错位是否值得利用”。2021–22赛季早期NBA官方分析就展示了对换防时通过seal、flash等方式把小防大错位直接转成篮下机会。citeturn13search5

### 球员创造力真正稀缺的地方，是防守已经破坏第一方案之后

体系可以制造第一步优势，但季后赛会不断消灭熟悉动作。

2022年总决赛，Boston成功通过换防、drop以及出色的绕掩护限制勇士的无球分离空间，而Golden State仍必须通过Curry的持球投射、重新掩护和连续动作继续创造。NBA统计显示，勇士常规赛每100回合有66.9次无球掩护；到了总决赛，对手已经非常熟悉split action，体系本身并不能保证得到空位。citeturn12search5 Curry在那轮总决赛被设置大量掩护和换防后，勇士依然能够在这些回合取得高水平产出，说明超级创造者能够成为体系被针对后的第二层答案。citeturn12search11

因此BPTI不能把“体系篮球”和“巨星篮球”做成二选一。

真正优秀的设计是：

**体系负责制造优势，巨星负责扩大优势或拯救被破坏的回合。**

### 中距离不是一种应被统一消灭的“低效率投篮”

2021–22赛季的DeMar DeRozan是非常强的反例。他当时的隔离进攻达到1.13分/回合，在至少100次isolations的35名球员中最高；post-up达到1.26分/回合；赛季中期已经出手516次中距离并命中50.2%。他的关键时刻进攻也高度集中于中距离。citeturn12search0

Chris Paul则展示了另一个机制：他的肘区中距离不仅是终结手段，而且会迫使drop防守的大个做出调整，而这种调整反过来打开顺下和传球路线。Phoenix官方分析将他的中距离、节奏控制、ball-screen阅读和传球明确联系在一起。citeturn17search4

所以BPTI不能只计算：

\[
2\times FG\% \quad vs \quad 3\times FG\%
\]

还必须理解：

\[
\text{某项得分威胁}
\rightarrow
\text{迫使防守改变位置}
\rightarrow
\text{产生新的传球/突破窗口}
\]

投篮本身也可能是一种**战术杠杆**。

### 防守体系同样是在选择“愿意失去什么”

没有任何防守能够同时消灭篮筐、三分、中距离、顺下、篮板和犯规。

针对优秀挡拆阅读者，FIBA的Bonn案例直接总结了这一点：对特别优秀的阅读者，单一问题很容易被解决，因此需要改变coverage，同时明确“你最终必须决定愿意放掉什么”。citeturn12search9

所以BPTI防守推理的核心也不应该是“哪个coverage数值最高”，而应该是：

**优先拿走什么 → 接受什么代价 → 哪个球员能够承担这个代价 → 对手会怎样攻击这个让步。**

## 十种体系家族的结构化SystemCards

以下十张卡不是NBA 2K22参数表，而是后续R3和Codex能够消费的**篮球认知卡**。其中“阵容/财务成本”属于R1篮球建队推论；实际合同金额、资产价格和薪资影响必须以后由M1与本局数据确定，不能由R1自行赋值。

### **SystemCard — MOTION_READ_REACT**

| 字段 | 研究结论 |
|---|---|
| **family** | Motion / Read-and-React |
| **核心原则** | 通过持续传球、切入、无球掩护、handoff和重新定位，迫使五名防守者连续交换帮助责任，使一次小失误逐渐扩大成高质量机会。 |
| **第一优势** | 防守者在追防无球、switch、top-lock、help与recover之间出现时间差。 |
| **关键角色** | movement shooter、screening connector、decision-making hub、secondary passer、cutting finisher。 |
| **决策权** | Entry高度结构化；第二、第三动作高度read-and-react；优秀射手和创造者拥有拒绝掩护、backdoor、slip及late-clock自主权。 |
| **失效条件** | 球员停球、只会执行第一动作、传球判断慢、没有投射重力；对方能够大量换防且保持沟通时，第一层分离空间可能消失。 |
| **对手反制** | switching、top-lock、deny、身体对抗、绕过无球掩护、提前换人。 |
| **再反制** | slip、backdoor、screen-the-switcher、post split、利用switch产生的错位、第二侧连续动作。 |
| **备用方案** | 主创造者持球挡拆/单打；利用motion制造后的错位进入post或isolation。 |
| **可观察数据** | off-ball screen数量、assisted FG%、secondary assists、touch time、cuts/handoffs、turnovers。它们只能验证行为存在，不能单独证明体系质量。 |
| **阵容成本** | 需要多名能传、能读、愿意无球行动的球员；训练和磨合成本高；纯持球型球星可能需要角色重构。 |
| **历史案例** | 2013–14 Spurs的球权移动可作为早期参考；2017–18及2021–22 Warriors是更清楚的现代案例。 |
| **confidence** | HIGH |

Kerr明确把勇士体系的关键描述为五人持续移动、掩护和切入，并指出Durant需要时间才能从等待单打转为体系内移动。citeturn14search3 2021–22勇士联盟领跑secondary assists，球队69.4%的进球来自助攻，且有大量球员共同参与传球，说明体系并不是把“组织”集中给一名传统控卫。citeturn16search0 但2022总决赛Boston通过switch等方式能够显著压缩勇士无球分离空间，证明Motion同样有明确的防守答案。citeturn12search5

### **SystemCard — TRIANGLE_INSIDE_OUT**

| 字段 | 研究结论 |
|---|---|
| **family** | Triangle / Inside-Out |
| **核心原则** | 通过稳定的强侧三角、弱侧双人关系、post/elbow/wing间距建立多个相邻传球选择，让球能通过传球而非单一控卫持续改变攻击侧。 |
| **第一优势** | 低位接球、强弱侧转换、post附近形成inside-out压力；让明星得分手从多个位置接球。 |
| **关键角色** | post threat / post passer、wing scorer、cutting guard、high-post connector、弱侧投射。 |
| **决策权** | 结构高度稳定，但不是固定剧本；进入结构后根据denial、double、front和overplay选择cut、post feed、reversal或isolated finish。 |
| **失效条件** | 缺少低位威胁和传球能力；球员不理解spacing；防守能够断绝post entry而外线无法惩罚；现代高换防阵容可能削弱传统错位。 |
| **对手反制** | front post、包夹低位、deny wing entry、强侧拥挤、快速switch。 |
| **再反制** | reversal、high-low、baseline cut、弱侧攻击、让巨星从face-up或elbow开始。 |
| **备用方案** | 进入明星单打、PnR或high-low，而不必为了保持“三角形”强迫执行。 |
| **可观察数据** | post/elbow touches、passes across sides、post assists、cuts、assisted baskets；不能仅凭助攻数认定球队在跑Triangle。 |
| **阵容成本** | 对篮球智商、低位技术和传球要求高；学习曲线明显；某些高度依赖持球挡拆的控卫需要重新分配球权。 |
| **历史案例** | 1990年代Chicago Bulls；2000年代Phil Jackson Lakers，包括2009–10 Lakers。 |
| **confidence** | HIGH（历史结构），MEDIUM（向现代阵容直接迁移） |

NBA/Thunder官方将Triangle描述为围绕球形成三角、保持良好spacing、通过清晰传球让球改变场侧的体系。citeturn13search2 Phil Jackson回顾时强调，他喜欢体系所提供的结构，并指出其价值之一就是不必依赖单一ball carrier或传统floor leader。citeturn13search3 Scottie Pippen也回忆称Bulls最初需要相当长的适应时间，随后才真正掌握该体系，这支持“学习成本是真实体系成本”的判断。citeturn13search12 Tex Winter的Triangle后来确实成为Bulls和Lakers多个冠军时期的重要战术基础。citeturn13search9

### **SystemCard — SPREAD_PICK_AND_ROLL**

| 字段 | 研究结论 |
|---|---|
| **family** | Spread Pick-and-Roll |
| **核心原则** | 通过空间把主要防守决策集中到持球人与掩护人的两人游戏，再利用第三、第四名帮助者的移动制造传球机会。 |
| **第一优势** | ball-handler迫使screen defender选择drop/show/blitz/switch；roller迫使弱侧收缩。 |
| **关键角色** | primary handler、screen/roll big、short-roll decision maker、corner spacer、second-side creator。 |
| **决策权** | 持球者拥有极高read responsibility；roller也必须判断roll/short-roll/pop；弱侧球员根据帮助移动。 |
| **失效条件** | 持球人无法惩罚drop；roller不会处理4v3；spacing不足；弱侧没人能投/突破；对手换防后缺乏错位攻击。 |
| **对手反制** | drop、switch、hard hedge、blitz、ICE、under、late switch。 |
| **再反制** | pull-up/midrange、short roll、re-screen、flip angle、slip、Spain action、weak-side shake、seal mismatch。 |
| **备用方案** | second-side PnR、isolation、post mismatch、DHO。 |
| **可观察数据** | PnR frequency/PPP、screen coverage、roll/short-roll passes、paint touches、corner attempts、help rotations；单看PnR PPP不足以说明整个体系。 |
| **阵容成本** | 高度依赖一名或多名优秀阅读型持球人；roller和弱侧投射质量决定体系上限；核心受伤时替代成本高。 |
| **历史案例** | 2020–21 Phoenix Suns；Chris Paul主导的Suns；2019–20 Dallas second-side PnR。 |
| **confidence** | VERY HIGH |

2021总决赛Game 1，Phoenix在Lopez的前八个防守回合中九次将其卷入ball screen或DHO，显示了Spread PnR如何主动选定需要被迫决策的防守者。citeturn15search0 FIBA案例则清楚展示hard hedge→short roll→攻击帮助来源以及drop→持球人进入空出的区域的完整因果链。citeturn12search1 换防也不是终点：re-screen、改变screen angle、高低位和错位单打都能成为下一层。citeturn12search17turn16search5

### **SystemCard — ISOLATION_MIDRANGE_CREATION**

| 字段 | 研究结论 |
|---|---|
| **family** | Isolation / Midrange Creation |
| **核心原则** | 把球交给拥有独立创造优势能力的球员，让其通过节奏、脚步、身体、急停、face-up或造犯规，在不依赖防守轮转失误的情况下制造投篮。 |
| **第一优势** | 单点技术优势和对位优势；尤其能攻击switch后的弱点。 |
| **关键角色** | elite shot creator、spacing teammates、screen-to-switch facilitator、offensive rebounder或secondary creator。 |
| **决策权** | 创造者拥有最高自主权；其余球员主要负责spacing、cut timing和被包夹后的二次处理。 |
| **失效条件** | 创造者效率不足、无法出球、spacing差、体能下降；防守可无代价包夹或安排强单防者。 |
| **对手反制** | early double、late double、shade、deny preferred hand/spot、switch length、zone crowding。 |
| **再反制** | screen-to-force matchup、empty-side iso、post-up、提前出球后re-attack、move star off-ball再接球。 |
| **备用方案** | PnR或motion帮助明星先获得优势，而不是每回合从静态1v1开始。 |
| **可观察数据** | isolation frequency/PPP、pull-up shooting、midrange zones、FT rate、double-team assists、late-clock results；平均联盟shot value不能替代个人能力评价。 |
| **阵容成本** | 球权集中；其他球员参与度可能下降；明星体能和健康负担较高；高端shot creator通常不可由普通角色球员替代。 |
| **历史案例** | 2021–22 Chicago Bulls / DeMar DeRozan；另可观察Durant、Harden、Tatum等不同类型创造者。 |
| **confidence** | VERY HIGH |

DeRozan在2021–22的真实表现直接否定了“中距离本身等于坏进攻”的过度概括：赛季中段他的isolations达到1.13 PPP、post-up达到1.26 PPP，中距离出手量极高且命中50.2%。citeturn12search0 NBA对当季isolation scorer的分析同样显示，不同个人在同一play type中的效率差别很大；这正说明联盟平均不能取代球员个体技术。citeturn15search12

BPTI应该把这种球员识别为**防守不犯错时仍能制造进攻的资源**，尤其是季后赛和shot-clock末端，而不是首先尝试把他的中距离“优化掉”。

### **SystemCard — POST_HIGH_LOW**

| 字段 | 研究结论 |
|---|---|
| **family** | Post Dominance / High-Low |
| **核心原则** | 通过深位接球、身体错位和post gravity迫使防守收缩或包夹，再利用high-low、cut和inside-out传球转移优势。 |
| **第一优势** | 内线位置优势；小防大错位；低位包夹产生的外线数字优势。 |
| **关键角色** | dominant post scorer、entry passer、high-post big、cutters、weak-side shooters。 |
| **决策权** | post star需要读double/front/dig；high-post passer判断lob、cut或reversal；外围必须随帮助位置重新spacing。 |
| **失效条件** | 接不到球；接球点离篮筐太远；外线无投射；post player出球慢；对手能够front+weak-side support。 |
| **对手反制** | front、3/4 front、early double、dig、baseline double、switch fronting。 |
| **再反制** | high-low lob、直接entry、duck-in、re-post、face-up、用ball screen把低位巨星带到高位。 |
| **备用方案** | elbow isolation、PnR roll man、face-up attack。 |
| **可观察数据** | post touches、catch depth、post-up frequency、double frequency、passes out、rim/FT creation；单纯“post PPP”不能判断被拒绝接球的隐形影响。 |
| **阵容成本** | 需要可靠entry passing和外围spacing；巨星大个价值极高，但围绕他配置的第二大个、射手及防守角色有明显阵容机会成本。 |
| **历史案例** | 2021–22 Philadelphia / Joel Embiid；2021–22 Hapoel Jerusalem高低位案例。 |
| **confidence** | VERY HIGH |

2021–22 Embiid平均7.8分来自post-up，排名联盟第一；Jokic则不仅能得分，还领先post-up助攻，说明“低位巨星”本身也可以是传球枢纽而非终结黑洞。citeturn15search1

但Miami在2022季后赛展示了非常重要的反制：通过front、防止深位接球以及提前协防，Embiid在Games 3–4合计只有四次post-up，并经常被迫在离篮筐约20英尺处开始进攻。citeturn15search3turn15search14 Embiid本人此前也解释过，过度依赖纯低位使他容易被包夹，因此增加面框、运球和弧顶攻击来改变防守施压方式。citeturn17search0

这就是BPTI必须理解的**体系演化**：保留低位巨星，而不是因为低位遭到反制就放弃低位巨星。

### **SystemCard — POINT_CENTER_ELBOW_HUB**

| 字段 | 研究结论 |
|---|---|
| **family** | Point-Center / Elbow Hub |
| **核心原则** | 让中锋或大型前场球员成为中轴，通过elbow、高位post、DHO和post passing观察整个半场，使其他四人围绕他的阅读不断cut、screen和relocate。 |
| **第一优势** | 把传统护框大个拉离篮筐；中锋视野使cut和弱侧投射同时存在；DHO可以连续转换成PnR。 |
| **关键角色** | elite passing big、movement shooter、cutter、DHO guard、secondary creator。 |
| **决策权** | hub拥有极高分配权；无球队员拥有cut/reject/re-screen阅读；后卫不需要永久持球。 |
| **失效条件** | hub传球价值被削弱；队友停止cut；对手能够单防hub且不帮助；没有射手让防守收缩。 |
| **对手反制** | deny elbow、switch DHO、top-lock shooter、让非射手cut、压迫传球线路。 |
| **再反制** | backdoor、fake handoff、keeper、post-up mismatch、weak-side pinch惩罚、hub主动得分。 |
| **备用方案** | conventional PnR、post-up或creator isolation。 |
| **可观察数据** | elbow touches、touch duration、handoff frequency、passes-to-assists chain、cuts、post assists；传统PG助攻榜会低估这种结构。 |
| **阵容成本** | 真正能作为体系中轴的高大传球者极难替代；其他后卫必须接受更多无球职责；hub缺阵可能导致整个进攻架构重构。 |
| **历史案例** | Denver Nuggets围绕Nikola Jokic的进攻，尤其2019–20以后。 |
| **confidence** | VERY HIGH |

NBA的Jokic Film Study显示他当时场均8.2次elbow touches，Denver有联盟前列的handoff占比，而且大量动作通过他的肘区接球、DHO和弱侧阅读展开。citeturn12search4 Nuggets自己的战术分析也直接说明，球队进攻主要围绕中锋的组织能力，guards和wings被鼓励cut或寻找外围接球空间。citeturn12search7

这类球员不能被简单归类为“高助攻中锋”。真正价值是：

**他改变了其他四个位置应该怎样移动。**

### **SystemCard — TRANSITION_EARLY_OFFENSE**

| 字段 | 研究结论 |
|---|---|
| **family** | Transition / Early Offense |
| **核心原则** | 在防守尚未完成匹配和半场结构之前进攻，通过推进速度、pass-ahead、rim run、early drag和cross-match制造优势。 |
| **第一优势** | 防守人数未齐、matchup错误、篮下未建立保护、弱侧射手无人定位。 |
| **关键角色** | rebound-and-go handler、rim runner、wing sprinter、advance passer、trailing big、secondary handler。 |
| **决策权** | 抢下球后有明确lane职责，但持球者必须判断立即攻击、advance pass还是进入early action。 |
| **失效条件** | 对手退防纪律好；己方不能抢下防守篮板；半场能力过弱；追求速度导致失误。 |
| **对手反制** | prioritize floor balance、快速退防、stop ball、保护篮下、提前match shooters。 |
| **再反制** | early drag、flow directly into half-court motion/PnR、利用cross-match post-up。 |
| **备用方案** | 如果没有early advantage，应自然进入主半场体系，而不是强行快攻。 |
| **可观察数据** | transition frequency/PPP、fast-break points、seconds into possession、live-ball turnovers forced、advance passes；fast-break points本身无法解释为什么转换产生。 |
| **阵容成本** | 要求速度、体能、后卫深度和篮板后快速决策；若过度leak-out可能牺牲篮板；高节奏也可能增加失误与阵容负荷。 |
| **历史案例** | 2021–22 Memphis Grizzlies。 |
| **confidence** | HIGH |

2021–22 Memphis联盟第一的fast-break points为17.7分，同时在进攻篮板、抢断、盖帽、禁区得分等方面也非常突出，说明转换并不是单独的“Tempo按钮”，而与防守制造失误、篮板以及球员运动能力结合。citeturn13search0 但NBA季后赛前瞻同时指出，禁区、转换和二次进攻这三类得分通常在季后赛都会下降，因此单一依赖转换会暴露半场进攻问题。citeturn13search1

这应该直接成为BPTI的反证规则：

> 高水平Transition球队必须仍有一个可工作的Half-Court Plan B。

### **SystemCard — DEFENSE_FIRST_RIM_PROTECTION**

| 字段 | 研究结论 |
|---|---|
| **family** | Defense-First / Rim Protection |
| **核心原则** | 优先保护篮筐和禁区，使持球人面对内线尺寸时被迫停球、急停或出球，同时外围防守者根据篮下保护能力选择更激进的追防路线。 |
| **第一优势** | 降低篮下质量、改变突破选择并形成“威慑”，而不只是追求盖帽。 |
| **关键角色** | rim anchor、point-of-attack defender、nail helper、low man、defensive rebounder。 |
| **决策权** | anchor决定drop深度和协防时机；POA defender决定绕上/恢复；弱侧必须tag与recover。 |
| **失效条件** | 对手拥有elite pull-up或中距离；corner help不断被利用；anchor被拉出禁区；外围第一线被完全突破。 |
| **对手反制** | pull-up shooting、5-out、pick-and-pop、empty-corner PnR、short roll、midrange attack。 |
| **再反制** | 改变drop level、show、late switch、pre-rotate、减少帮助来源或让anchor短暂上提。 |
| **备用方案** | 对特定阵容改switch/zone，而不必永久放弃护框身份。 |
| **可观察数据** | rim attempts prevented、DFG at rim、opponent restricted-area frequency、foul rate、defensive rebound、help/recovery；blocks只是其中一部分。 |
| **阵容成本** | 护框中锋必须搭配能够追防和恢复的外围；若防守专家缺乏进攻能力，会产生另一端的spacing成本。 |
| **历史案例** | 2020–21及2021–22 Utah围绕Rudy Gobert；其他类型可参考Embiid。 |
| **confidence** | VERY HIGH |

NBA官方特别指出，盖帽数与优秀护框并不直接等价；2021–22初期的rim protection数据中，真正重要的是对篮下命中率及出手环境的改变。citeturn14search2turn14search11 对Gobert的Film Study则显示他通常采取drop、留在paint附近，并在2021–22让被他保护的篮下出手只有49.3%的命中率。citeturn14search16 Embiid的案例进一步说明，还应该测量**对手是否因为护框者存在而根本不去篮下**，而不只是对已经发生的投篮统计。citeturn14search13

因此R1建议BPTI以后把“deterrence”作为防守概念单独处理。

### **SystemCard — SWITCHABLE_PRESSURE_DEFENSE**

| 字段 | 研究结论 |
|---|---|
| **family** | Switchable Pressure Defense |
| **核心原则** | 通过换防消除掩护产生的初始分离，使进攻无法轻易形成2v1，再依靠多位置防守和团队轮转承担错位。 |
| **第一优势** | 把复杂ball-screen/off-ball action简化成“保持人前”，破坏进攻预设的空间时间差。 |
| **关键角色** | switchable wings、mobile big、strong guards、scram/peel helpers、defensive rebounders。 |
| **决策权** | 必须具有极高沟通和即时assignment交换能力；switch后的scram、peel、pre-switch同样属于阅读。 |
| **失效条件** | 出现严重size mismatch；小个被低位打；大个被速度型creator单挑；换防后篮板位置差。 |
| **对手反制** | screen hunting、seal、slip、ghost screen、re-screen、post mismatch、offensive rebound。 |
| **再反制** | pre-switch、scram、peel、late double、switch-back、zone behind switch。 |
| **备用方案** | 对特定明星改drop/show/blitz，避免“为了换防而换防”。 |
| **可观察数据** | switch rate、isolation frequency after switch、mismatch attacks、post seals、defensive rebound、scram rotations；只看防守效率不能知道换防是否是真正原因。 |
| **阵容成本** | 需要多个能够跨位置生存的防守者；对尺寸和篮板要求高；没有足够多功能球员时会暴露明显短板。 |
| **历史案例** | 2021–22 Boston Celtics；2019–20 Houston Rockets是不同极端版本。 |
| **confidence** | VERY HIGH |

2021–22赛季初，Boston的ball-screen switch比例一度达到联盟最高约41%，NBA官方还展示了对手如何通过seal和flash直接攻击这种换防。citeturn13search5 Houston的switch-heavy防守则展示了另一面：优秀换防可以把动作逼成低效单打，但进攻方会不断通过slip和错位寻找破口。citeturn13search8

因此“Switchable”不能成为：

> 五个人都可以换，所以永远换。

正确规则应是：

> **换防是一种消除第一优势的工具；当错位成本超过消除掩护收益时，应使用别的coverage。**

### **SystemCard — ADAPTIVE_MULTIPLE_SYSTEMS**

| 字段 | 研究结论 |
|---|---|
| **family** | Adaptive / Multiple Systems |
| **核心原则** | 在保持球队身份和基本原则的同时，根据对手、阵容、比赛阶段和对方调整，在有限且训练充分的体系菜单中切换。 |
| **第一优势** | 阻止对手通过重复同一阅读把一个coverage“解题”；迫使其不断重新辨认责任。 |
| **关键角色** | versatile players、high-IQ communicator、multiple creators、coachable lineup。 |
| **决策权** | 教练决定macro switch；场上球员必须知道每个coverage的触发条件和责任变化。 |
| **失效条件** | 战术菜单过多导致执行质量下降；球员不知道当前coverage；每一种都会但没有一种真正优秀。 |
| **对手反制** | 通过稳定的elite creator识别coverage、制造communication errors、快速进入动作不给防守换方案时间。 |
| **再反制** | 改coverage timing、同一外观不同实际责任、改变matchup、junk/zone、人盯人混合。 |
| **备用方案** | 在关键时刻回到最熟练的base system，而非继续随机变化。 |
| **可观察数据** | coverage diversity、success by matchup、timeouts/after-timeout changes、lineup-specific scheme；“使用很多体系”本身不是成功指标。 |
| **阵容成本** | 学习、训练、沟通成本最高；多功能阵容通常比高度专门化阵容更容易实施，但实际薪资价值必须由M1评估。 |
| **历史案例** | Gregg Popovich从Duncan/Robinson时期inside-out逐渐演变至2014 Spurs；FIBA Anwil是防守多变性的明确案例。 |
| **confidence** | HIGH |

Kerr谈Popovich时特别指出，San Antonio早期围绕Duncan/Robinson打inside-out，而到2014年已经转为完全不同的速度、传球和球移动风格；他把这种变化直接归因于Popovich根据人员和联盟环境不断调整。citeturn14search0

FIBA对Anwil的报道更像一张Adaptive Defense教科书：球队会在1-3-1、matchup zone、switch以及hard show之间切换，目的之一就是让对手的控卫和教练无法确定接下来面对什么。citeturn16search3

但Adaptive绝不能被BPTI理解成“随机换战术”。

真正的Adaptive应该写成显式规则：

> **IF 对手开始用X解决主方案  
> THEN 改为Y  
> BECAUSE Y拿走X依赖的优势  
> ACCEPT 代价Z。**

这是十张SystemCard中最重要的元规则之一。

## 五类关键球员为什么不能被统一效率模型抹平

### 中距离超级得分手

这类球员的价值不只是“两分命中率”。

他们往往承担三个功能：

**惩罚drop、解决switch、在战术失败后制造无协防依赖的投篮。**

DeRozan 2021–22的isolations、post-ups和midrange数据说明，顶级个体可以显著偏离联盟平均结果。citeturn12search0 Chris Paul则展示了中距离威胁如何改变PnR defender的位置，从而让passing lane出现。citeturn17search4

因此BPTI不能写：

> 中距离低效 → 减少中距离。

而应该写：

> **该球员的中距离是否迫使防守改变原本最有利的coverage？**

如果答案是是，那么中距离同时是一种**进攻结构能力**。

### 低位巨星

低位巨星的真正价值应该拆成：

**深位得分 + 造犯规 + 吸引包夹 + 迫使front + 改变对方阵容尺寸 + 出球能力。**

2021–22 Embiid的post scoring和Jokic的post scoring/pass组合说明，同样叫“post player”，其体系功能可以完全不同。citeturn15search1

但Miami对Embiid的front和提前包夹同样证明：优秀防守甚至可以让“post-up统计”消失，因为球员根本没有在理想位置接到球。citeturn15search3turn15search14

因此以后BPTI不能因为一名中锋某轮系列赛post-up次数下降就说“低位失效”，必须判断：

**是球员失效，还是entry被防守提前拿走？**

这是完全不同的篮球诊断。

### 无球射手

无球射手的价值至少包括：

**投篮本身 + 移动重力 + 牵制帮助 + 强迫换防 + 为别人创造空间。**

Curry的2021官方分析直接把其off-ball movement、射程和持球能力放在一起讨论。citeturn17search3 Klay Thompson的总决赛Film Study也展示了他如何通过多种掩护和移动获得极少的出手空间，而防守为了追逐他会改变整个弱侧责任。citeturn17search6turn17search25

所以：

> “无球射手本场只得12分”

并不等于：

> “无球射手影响很小。”

如果两名防守者为追他改变站位，其他人的机会可能已经被创造出来。

这类价值需要mechanism data，而不仅是box score。

### 持球组织核心

真正的primary initiator不只是“助攻最多的人”。

其职责包括：

**识别coverage → 操纵coverage → 让帮助者移动 → 把球送到下一位决策者。**

Chris Paul对不同PnR coverage的持续拆解就是典型。citeturn17search4turn15search4 2021 Finals Phoenix反复把Lopez拉进动作，也说明优秀控卫并非单纯“读既有防守”，还会主动选择要攻击哪名防守者。citeturn15search0

所以BPTI以后需要区分：

- ball dominance；
- advantage creation；
- advantage recognition；
- advantage transfer。

四者并不是一件事。

### 中锋策应核心

Point-center更进一步。

Jokic型球员不是“中锋位置上一个传统控卫”。

他的存在让球队能够改变整个进攻几何：后卫不必永远持球，中锋在elbow或post成为中心，其他四人围绕其视野cut、handoff和screen。NBA和Nuggets的官方Film Study都明确显示Denver如何围绕这种中锋策应组织进攻。citeturn12search4turn12search7

这意味着相同一名优秀控卫来到Jokic体系，与来到传统Spread PnR球队，其价值和职责不会一样。

**这正是BPTI以后实现“同一球员对不同球队具有不同价值”的篮球基础。**

## 数据验证、反证与阵容成本框架

R1研究最明确的结论之一，是以后不能再把“数据”视为一个整体。

BPTI至少需要区分三类证据。

| 层级 | 数据回答的问题 | 示例 | 不能证明什么 |
|---|---|---|---|
| **Outcome Data** | 最后发生了什么？ | ORtg、eFG%、PPP、TOV%、FT rate、胜负 | 为什么发生 |
| **Mechanism Data** | 球队是怎样创造/阻止机会的？ | PnR coverage、off-ball screens、post touches、elbow touches、transition frequency、switch rate | 某个机制是否天然优秀 |
| **Context Data** | 为什么这个选择对当前球员/对手合理？ | matchup、catch depth、shot-clock、lineup、对手coverage、帮助来源 | 长期因果关系 |

勇士的69.4% assisted baskets和secondary assists可以帮助确认ball movement确实存在，但不能单独证明Motion导致胜利。citeturn16search0 Gobert的盖帽也不能单独代表护框，NBA官方专门指出blocked shots并不直接等同于rim protection。citeturn14search2 同样，Embiid系列赛post-up次数下降如果不结合Miami的front与拒绝接球，就会得出错误的篮球结论。citeturn15search3

### BPTI以后应该采用“反证优先”而不是“指标下降就优化”

每个体系至少应存在一条真正的失败判据。

例如Motion不是：

> 助攻下降 → Motion不好。

而是：

> 对手大量switch后，球队无法通过slip、post mismatch、backdoor或primary creator继续制造优势，而且多个对手都重复成功 → 当前motion package可能缺少第二答案。

Post也不是：

> post PPP下降 → 不要低位。

而是：

> 球星能持续深位接球，但面对单防仍无法得分、面对包夹又无法出球，而且没有其他战略价值 → 才真正构成post体系反证。

Transition不是：

> 快攻少了一场 → 改打法。

而是：

> 季后赛对手稳定退防后，连续多个系列赛没有可靠half-court fallback → 体系结构存在缺口。

Switch Defense不是：

> 对手单打得了30分 → 不能换防。

而是：

> switch持续产生可预测且无法scram的致命错位，对方能够重复获得高价值机会，而替代coverage有更低代价 → 才需要调整。

这种“机制反证”比传统数据优化重要得多。

### 阵容和财务成本必须进入体系推理，但不能由R1虚构价格

每种篮球哲学都不是免费的。

Motion需要多名快速阅读球员和磨合时间；Spread PnR把很高的决策负担集中给持球核心；Isolation需要真正高端shot creator；Post需要entry passing和外围spacing；Point-Center高度依赖罕见的中轴型大个；Switch Defense需要多个能跨位置防守又保持篮板的球员；Adaptive体系则需要最大的战术学习和沟通容量。上述角色需求由实际战术案例支持。citeturn14search3turn15search0turn15search1turn12search4turn13search8turn16search3

但是R1不能由此直接断言：

> “某种体系一定更贵。”

最终财务成本取决于本局球员市场、合同和资产环境。

正确的BPTI/M1交接应该是：

**BPTI：**“这个体系缺一个能short-roll处理4v3的中锋。”

**M3：**“现有阵容内部有没有？”

**M1：**“如果没有，市场上取得这种能力要付出多少？”

而不是篮球模型自己计算一个虚构的市场价格。

## 主要来源索引

以下是R1实际使用的核心一手或准一手资料。历史赛季指本报告利用该来源支撑的篮球案例时期，而不是网页当前年份。FIBA/WABC官方教练教材确实是本项目首选资料体系；本次研究主要使用了FIBA官网公开战术分析和教练内容，并保留M2已经局部阅读WABC教材的成果。fileciteturn3file0L2-L2

| ID | 赛季/时期 | 出处与用途 | URL |
|---|---|---|---|
| **R1-S01** | 教练通用 | FIBA/WABC Coaching Manuals与教练教育入口；体系教学证据框架。citeturn9search0 | https://about.fiba.basketball/en/wabc-documents |
| **R1-S02** | 2017–18 Warriors | NBA，Steve Kerr谈勇士持续移动、掩护、切入及Durant适应体系。citeturn14search3 | https://www.nba.com/news/morning-tip-golden-state-warriors-coach-steve-kerr-outspoken-willing-listen |
| **R1-S03** | 2021–22 Warriors | NBA，Curry与Warriors secondary assists、69.4% assisted baskets。citeturn16search0 | https://www.nba.com/news/stephen-curry-warriors-lead-the-nba-in-secondary-assists |
| **R1-S04** | 2022 Finals | NBA Finals Film Study，Boston如何限制GSW off-ball/split action。citeturn12search5 | https://www.nba.com/news/finals-film-study-celtics-put-it-all-together-in-game-3 |
| **R1-S05** | 2022 Finals | NBA，Curry被掩护及换防后的系列赛产出。citeturn12search11 | https://www.nba.com/news/5-incredible-stats-from-2022-bill-russell-nba-finals-mvp-stephen-curry |
| **R1-S06** | 1990s Bulls / 2000s Lakers | NBA，Tex Winter及Triangle历史。citeturn13search9 | https://www.nba.com/news/tex-winter-chicago-bulls-assistant-coach-dies |
| **R1-S07** | 2009–10 Lakers | Oklahoma City Thunder官方对Triangle spacing与ball reversal的分析。citeturn13search2 | https://www.nba.com/thunder/news/triangleoffense_100417.html |
| **R1-S08** | Bulls/Lakers历史 | Lakers官方Phil Jackson谈Triangle、structure与无需单一ball carrier。citeturn13search3 | https://www.nba.com/lakers/news/110404texwinter_halloffame.html |
| **R1-S09** | 2020–21 Suns | NBA Finals Film Study，Phoenix连续针对Brook Lopez的PnR/DHO。citeturn15search0 | https://www.nba.com/news/finals-film-study-suns-go-at-brook-lopez-early-and-often-in-game-1 |
| **R1-S10** | 2021–22 Bulls | NBA 2022 All-Star Notebook，DeRozan isolation/post/midrange数据。citeturn12search0 | https://www.nba.com/news/all-star-notebook-key-stats-on-every-2022-all-star |
| **R1-S11** | 2021–22 NBA | NBA，Harden/Durant/DeRozan等isolation scorer案例。citeturn15search12 | https://www.nba.com/news/harden-durant-derozan-lead-top-isolation-scorers |
| **R1-S12** | 2021–22 NBA | NBA，Embiid/Jokic领衔post-up scoring及Jokic post passing。citeturn15search1 | https://www.nba.com/news/joel-embiid-nikola-jokic-lead-top-10-post-up-scorers |
| **R1-S13** | 2022 Playoffs | NBA，Miami front/deny Embiid，post catch被提前拿走。citeturn15search3 | https://www.nba.com/news/3-numbers-to-know-for-heat-sixers-game-5 |
| **R1-S14** | 2020–21 Sixers | Sixers官方，Embiid谈从纯post扩展至handle/face-up以处理包夹。citeturn17search0 | https://www.nba.com/sixers/news/inside-process |
| **R1-S15** | 2019–20 Nuggets | NBA Film Study，Jokic elbow touches、DHO与weak-side reads。citeturn12search4 | https://www.nba.com/news/schuhmann-film-study-denver-nuggets |
| **R1-S16** | Nuggets体系 | Nuggets官方，中锋策应、cut与DHO职责。citeturn12search7 | https://www.nba.com/nuggets/news/denver-nuggets-film-study-mason-plumlee-passing-080919 |
| **R1-S17** | 2021–22 Grizzlies | NBA，Memphis fast break、paint、offensive rebound、defensive event统计。citeturn13search0 | https://www.nba.com/news/grizzlies-coach-taylor-jenkins-contract-extension |
| **R1-S18** | 2022 Playoffs | NBA，Memphis三类主要进攻来源在季后赛可能缩水。citeturn13search1 | https://www.nba.com/news/series-preview-memphis-grizzlies-2-vs-minnesota-timberwolves-7 |
| **R1-S19** | 2021–22 | NBA，rim protection与blocks并非等价。citeturn14search2 | https://www.nba.com/news/giannis-gobert-lead-this-seasons-top-10-rim-protectors |
| **R1-S20** | 2021–22 Jazz | NBA Gobert Film Study，drop与49.3% rim DFG。citeturn14search16 | https://www.nba.com/news/film-study-rudy-gobert-will-transform-wolves-already-improved-defense |
| **R1-S21** | 2021–22 Celtics | NBA，Boston ball-screen switching及其反制。citeturn13search5 | https://www.nba.com/news/power-rankings-notebook-2021-22-week-7 |
| **R1-S22** | 2019–20 Rockets | NBA Film Study，switch-heavy defense及isolation结果。citeturn13search8 | https://www.nba.com/news/film-study-rockets-switching-happy-defense |
| **R1-S23** | Spurs 1997–2014演化 | NBA Popovich Hall of Fame profile，inside-out向2014 pace/ball movement转型。citeturn14search0 | https://www.nba.com/news/gregg-popovich-hall-of-fame-profile-2023 |
| **R1-S24** | 2018–19 Anwil | FIBA，1-3-1、matchup zones、switch、hard show混合及球员理解进攻原因。citeturn16search3 | https://www.fiba.basketball/en/news/bcl-18-19-news-underdogs-bite-a-closer-look-at-anwil-wloclawek |
| **R1-S25** | 2019–20 Nymburk | FIBA，offensive rebounding→full-court pressure→half-court switching/trap的完整防守体系。citeturn16search1 | https://www.fiba.basketball/en/news/bcl-19-20-news-the-modern-era-nymburk-s-defense-bucks-the-trend |
| **R1-S26** | 2021–22 Jerusalem | FIBA，Horns high-low、short roll、flip screen angle、switch punishment。citeturn16search5 | https://www.fiba.basketball/en/news/bcl-21-22-news-step-by-step-a-closer-look-at-hapoel-bank-yahav-jerusalem |
| **R1-S27** | 2022–23 Jerusalem | FIBA，post-to-post、short-roll自动阅读及“good shot → better shot”。citeturn16search8 | https://www.fiba.basketball/en/news/bcl-22-23-news-hapoel-bank-yahav-jerusalem-post-to-post |
| **R1-S28** | FIBA BCL | FIBA，hard hedge/drop的read-and-react案例。citeturn12search1 | https://www.fiba.basketball/en/news/bcl-19-20-news-tactics-board-aek-cooking-and-bonn-stay-sweet |
| **R1-S29** | FIBA BCL | FIBA，weak-side helper manipulation与short roll。citeturn12search3 | https://www.fiba.basketball/en/news/tactics-board-hapoel-netanel-holon-shake-rattle-and-roll |
| **R1-S30** | FIBA BCL | FIBA，针对精英PnR reader混合coverage以及“必须选择愿意放掉什么”。citeturn12search9 | https://www.fiba.basketball/en/news/23-24-news-tactics-board-have-bonn-solved-the-ragland-riddle |
| **R1-S31** | 2024 Coach education | NBA Coaches Association，Willie Green讲switching defense。citeturn14search8 | https://nbacoaches.com/willie-green-joins-nbas-coaches-corner-to-discuss-defensive-switching/ |
| **R1-S32** | 2023–24 Coach education | NBA Coaches Association，Billy Donovan讨论coverage改变后“action → reaction”。citeturn15search19 | https://nbacoaches.com/billy-donovan-joins-nba-coaches-corner/ |

有一项证据限制需要明确记录：WABC Level 1/Level 2的大型PDF在本次网页研究中未重新逐页渲染，因此本报告没有把无法重新查看的PDF内容冒充本轮新验证；其中页级知识只保留为仓库M2已经记录的既有研究资产。fileciteturn3file0L2-L2 本轮新增的核心战术因果主要由可直接核查的FIBA、NBA及NBA Coaches Association页面支撑。

## 争议、证据缺口与BPTI交接结论

**关于“最优体系”。** 没有证据支持存在一套无视人员、对手和时代都最优的篮球体系。反而Popovich的长期演变、FIBA多coverage案例和NBA季后赛针对性Film Study都支持：优秀体系必须与球员能力结合并具有反制能力。citeturn14search0turn16search3turn12search9 因此BPTI不应拥有一个全联盟统一的`system_score`来决定所有球队最终趋向同一打法。

**关于“现代篮球等于魔球”。** 三分和篮下在联盟宏观上具有重要效率价值，但DeRozan、Paul、Embiid和Jokic等案例证明，个体技能能够改变防守选择，因此某种投篮的战略价值不能只由联盟平均每次出手得分定义。citeturn12search0turn17search4turn15search1 这不是否认效率分析，而是要求把效率放在真实战术机制之后解释。

**关于Triangle现代适用性。** Bulls/Lakers时代的成功和体系结构有充分历史证据，但这不能证明2021–22任何阵容复制传统Triangle都有效。它应被保存为一种spacing、inside-out和distributed decision结构，而不是被BPTI神化为冠军公式。citeturn13search2turn13search9

**关于Motion与创造力。** 勇士证明严格结构与超级球员自由可以共存，但并不能推出“所有明星都应进入勇士式motion”。Kerr自己对Durant适应过程的描述反而说明球员与体系之间存在真实学习和角色成本。citeturn14search3

**关于防守覆盖。** “Drop”“Switch”“Blitz”“Hedge”等名称描述的是基础责任，但实际效果高度依赖掩护位置、球员能力、弱侧帮助和第二轮rotation。FIBA和NBA资料均显示，同一coverage可以被不同的re-screen、short roll、pull-up和spacing方式破解。citeturn12search1turn12search17turn15search0 后续R3把这些概念映射到NBA 2K22时，不能因为游戏里存在同名设置就自动认为行为完全等价。

**关于财务成本。** 本轮能够确认各体系需要不同角色组合，但没有研究证明“switch defender一定价值多少薪资”“motion connector应该占多少cap”。这些必须在本局M1财务和实际市场上决定。R1只能给出**角色稀缺性需求**，不能虚构价格。

**关于数据因果。** assists、PPP、shot profile、DFG、switch rate和post frequency都是证据，但没有任何单项指标能够单独证明体系机制。Gobert的rim protection案例尤其说明，甚至最直观的“盖帽”也可能遗漏大量威慑价值。citeturn14search2turn14search13 BPTI必须把“数据相关”与“篮球因果”分开存储。

最终，R1建议后续BPTI把每支球队的篮球理解压缩成以下结构，而不是一组效率权重：

> **球队想怎样制造第一优势？**  
> ↓  
> **谁负责制造？谁负责连接？谁负责终结？**  
> ↓  
> **哪些球员可以自主阅读，哪些动作必须按结构执行？**  
> ↓  
> **对手最合理的第一反制是什么？**  
> ↓  
> **球队有没有篮球意义上的第二答案？**  
> ↓  
> **如果第二答案也被破解，谁拥有最终创造权？**  
> ↓  
> **这种打法要求什么阵容、牺牲什么、花费什么机会成本？**  
> ↓  
> **哪些数据能够支持或反驳这些判断，而不是替代这些判断？**

这一模型与DEV19要求的FRANCHISE_IDENTITY → COACH_PHILOSOPHY → BASKETBALL_SYSTEM → PLAYER_ROLE_AND_AGENCY → MATCHUP_GAMEPLAN五层认知结构完全兼容。fileciteturn1file0L2-L2

因此，R1给后续BPTI最核心的研究交接不是“十套最佳战术”，而是：

**篮球没有一个统一答案，但篮球有可以解释的因果。**

真正的BPTI应该知道勇士为什么移动、DeRozan为什么可以投中距离、Embiid为什么需要从低位走到弧顶、Jokic为什么能让中锋成为进攻中轴、Gobert为什么一次没有盖帽的回合仍可能改变进攻、Boston为什么选择换防，以及当对手把这些答案破解以后，球队下一步究竟应该改变什么。

只有做到这一层，M系列的数据才会成为**理解篮球的证据**，而不是决定所有球队最终打成同一种篮球的主人。
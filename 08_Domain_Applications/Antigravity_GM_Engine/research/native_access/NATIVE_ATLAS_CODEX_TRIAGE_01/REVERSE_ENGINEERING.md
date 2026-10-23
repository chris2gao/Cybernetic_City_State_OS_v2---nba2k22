# 高杠杆结构逆向与证据裁决

全部 RVA 属于 `static_evidence.json.image.sha256` 指定磁盘 PE；preferred ImageBase=0x140000000，不能用作当前进程绝对地址。`static_evidence.json` 保存每条 Getter 的连续机器码、指令、RIP字符串目标和原始字符串字节。可用同目录静态提取器复算。

## 1. Slot39：纪录簿而非逐年统计

竞争假说：名字字典、纪录/排行榜记录、逐年球员统计。Getter真正入口0xF40090；原包0xF400A0是函数内 singleton 调用位置。0xF400BD比较`[rax+0x270]`，0xF400C5乘0x34，0xF400C9加`[rax+0x278]`。assert路径0xF40113引用字符串RVA0x2A86AA8=`ROSTERDATA::GetRecordDataByIndex`。

比名字字典更强的消费者证据：0xF32B10 的原生断言名称 `RecordData_GetGameRecord`；0xF33FC0 和0xEFFF60 为 `RecordData_GetSeasonOrCareerRecord`；0xF34C60 为 `RecordData_GetTeamRecordsByIndex`。后者用不同类别记录块和队伍索引计算记录位置，再调用同一 Slot39 Getter，不是 PlayerID×SeasonYear 直接索引。0xF32E57调用 Getter后，0xF32E5F读`dword[record+0x2C]`，右移21再&7并比较类型参数，证明尾部有packed类别/类型访问，不能无条件把每个 uint16 标签当完整独立字段。

AG01C原始 `sample_record_book_500.bin` 长26000B。首条两段20B字符串为 Wilt / Chamberlain，+40 float=100；第二条 Kobe / Bryant，float=81。首4B当两个 little-endian uint16 为26967与29804，后者不能解释成该候选的season_year。纯名字表解释也无法解释原生game/season/career record消费者与数值列。

**接受**：Slot39纪录簿对象族、52B结构、样本内两段文本和float投影。**拒绝**：原包的leading player_id/season_year、69,040条=完整逐年生涯数据库。**保留UNKNOWN**：分类码全映射、尾部flags/身份命名空间、当前UI/Save、全69,040条有效性。首条+48 word=15584，大于当时Slot1 count3390，至少不能直接当该pool数组下标；不能偷偷用姓名跨存档归并。

真实逐年生涯候选回到 AG01D PLAYER+0xFC / +0xFE..0x127 到 Slot24 的索引链，需要验证 sentinel、赛季、身份、界限和UI。该旧研究不是本次已执行的新实机读取。

## 2. Slot35：CustomUniform 不是财务块

竞争假说：财务总账、球队复合记录、服装/自定义资源记录。Getter入口0xF3C6A0，原包锚点0xF3C6B0为内部调用；比较+0x230、乘0xFB4、加+0x238。4020B由机器指令确认，并非仅相邻指针差推导。

0xF3C726引用字符串RVA0x2A86A30=`ROSTERDATA::GetCustomUniformDataByIndex`。一个直接消费者0x920E40循环枚举该对象，0x920E59调用 Getter，0x920E5E测试`dword[rax+0x4C] & 0x400`。这提供真实字段读取位置与predicate，但0x400的具体UI意义未知。

财务假说被该构建原生对象名和消费者反证；112条、4020B不构成112个财务账户的证据。此对象对当前经营食材攻坚的信息收益低，故停止拆解整块服装结构，转向现有合同/真实财务UI消费者，不伪造 int64 payroll/cash 等字段。

## 3. Slot22：Playbook 的68路原生取值

竞争假说：轮换网格、压缩分钟切片、战术手册。Getter入口0xF3ED60；0xF3ED8D比较+0x160，0xF3ED95乘0x168，0xF3ED9C加+0x168；原生名字符串RVA0x2A867F0=`ROSTERDATA::GetPlaybookDataByIndex`。

轮换包的48×5×uint16至少480B，超出360B，甚至还没包括team/minute头。压缩表示理论上可能装入360B，但该具体对象的原生名称和访问函数提供直接相反证据，不应继续用“也许压缩”挽救该轮换解释。

**实质突破**：0xF1D740先比较edx与0x43，超界跳默认；表RVA0xF1D924含68个32位目标RVA。对每个目标重新反汇编，index0读dword[rcx+0x58]，index67读dword[rcx+0x164]，全体偏移恰为88+4*k，0<=k<68。最后一个字段结束于360，无剩余空间、无推测步长。

0xF3ED00 lookup遍历Slot22，0xF3ED37读byte+0x54，&0x7F后与输入比较。这验证lookup key字段，不代表此key已经绑定某支现役球队。消费者0xF26700只在一个路径循环0..49，是该路径使用的50项子集，不能否定原生accessor明确支持68项。

原主线 `src/tactical_reader.py:read_team_playbook` 已有360B/68项/+0x58/+0x54实现；本次机器码复算独立支撑这些结构，不宣称新实现生产模块，也不借旧代码认证当前book/coach绑定、全部CRC语义或比赛效果。新的fixture helper只返回raw play words及low7 lookup key。

## 4. Slot42：真实DraftData和条件关系的边界

竞争假说：未来选秀资产、历史已选球员/草稿记录、其它32B关系对象。Getter入口0xF3C930；0xF3C95D比较+0x2A0，0xF3C965左移5，0xF3C969加+0x2A8；原生名RVA0x2A86B28=`ROSTERDATA::GetDraftDataByIndex`。

消费者0x92A3A0的assert名为`DraftData_GetByPickTeamAndIndex`，来自嵌入式`draftdata.vcc`来源字符串。0x92A43F取得记录，0x92A44C读+0x1C并&7作分组，0x92A4D7比较记录+0与输入队伍指针。0x61DBFF读record+0，随后调用0x23EFD0（仅`mov rax,[rcx+8];ret`），证实两个独立指针区域。

0x929C7A..0x929C99从metadata +0x1C读：low3 group；`shl24;sar27`取bits3..7为带符号5位值；`shr8;movzx al`取bits8..15序号。原包开头asset_id/year/round的紧凑字节schema与实际64位指针消费者不相容。

**额外结构突破**：0x947330读metadata bit17；置位路径读取record+8所指对象+0xCA8的uint16，再把metadata bits3..7与bits22..28组合成32位标识。未置位路径校验记录在Slot42首末记录范围，计算`(record-first)>>5`并置bit31；越界返回0xFFFFFFFF。0x942FB2使用Slot42 Getter，随后调用此函数，把结果与输入对象+0x18比较；该路径assert名`DRAFTDATA::GetLinkedPick`。因此存在 **两种身份token表示和linked-pick关联**；不再把“有位域”当成保护mask。

record+0x18作为32位token区域的消费者、+0x1C metadata及三段qword，形成32B结构候选；`raw_draft_fields`只输出raw值/已见位切片，绝不输出经过认证的保护/交换、absolute year、球员/队伍ID。

原主线 `config/draft_asset_profile.json` 与 `src/draft_assets.py` 已有普通未来选秀权的三指针/metadata工程。旧profile `directory_pointer_offset=0x2B0` 针对旧校准root=manager-8，与新manager+0x2A8指向同一字段；必须记录原点转换，不能不看root就判越槽。`GAME_NATIVE_OBJECT_HINTS_V0.json` 的历史 Slot36 名称与本次原生 Slot42冲突，保留为历史hint并拒绝当前直接使用，不改原文件。

**仍缺**：当前Save的owner/original指针命名空间、assigned-player关联、绝对年份epoch、bit17两模式业务场景、token具体保护/交换语义、实际UI验证。未观察保护或交换不等于游戏不存在；禁止拿现实2021交易资料代替该存档证据。本次不新增生产选秀权Decoder，也不改变原3年交易窗口或玩家规则。

## 5. Slot9：float的来源及原生60B

源 `sources/ag01b/fixtures/sample_descriptors.json` 已含inferred_stride60.01；`read_rosterdata_75.py`从该fixture继承hist_stride，再算count*hist_stride；enrich脚本添加业务关系，未修该数。故新Atlas的60.01与34985.83是旧推断被传播，不是读到的原生长度。尾探针用int(hist_stride)=60，更不能由尾字节可读反向证明原float。

0xF3C525机器码`48 6B DB 3C`直接乘60；命名Getter为CollegeData。583×60=34980B。历史相邻allocation距离34984B，仅可说差4B，不能据此证明整个Windows堆总是8字节对齐，更不能把PointerGap/Count当精确stride。`checked_size`拒绝float（即便60.0）、bool、负值和溢出；不会近似取整后无提示认证。

## 6. Slot61、1、24与其他高收益纠偏

- Slot61：Getter0xF3C780名DeadCap，+0x3D0/+0x3D8，stride0x88。旧waived salary链表与stretch heuristic来源保留；未新证伸展原生标志或Save/Reload。
- Slot1：0xF3F4CC比较manager参数rdx+0x10，0xF3F4D4乘0x4F0，0xF3F4DB加rdx+0x18；完整字段与稳定身份仍未知，不能因1264B寻址正确宣称全部Player食材就绪。
- Slot24：Getter0xF3F880名PlayerStat，+0x180/+0x188，`lea rbx,[rbx+rbx*2];shl rbx,4`=48。它不是“本赛季所有字段已绑定/已发布”的证明。
- 当前构建Slot26/30分别PlayerShotChart/TeamShotChart，不是Atlas标注的季后赛累计；25/29为相应manager。
- Slot18 PreseasonSchedule，Slot21 CoachStat；66 City，67 ShoeStyle，68 AttributeRange，69 RosterIndex；71 TradeException、72 manager。它们使下一轮可以回到真实高价值对象，而不是在错误的TPE/伤病/化学反应矩阵解释上堆叠Decoder。

对其余槽位，静态函数名是对象族级证据；字段、角色关系、时间/ID、原生作用与运行成熟度继续分轴。75行表里的NAME_HYPOTHESIS不因同一行同时有SEMANTICALLY_CORROBORATED而自动升格：后者只覆盖明确列出的static native name或PLAYER寻址。

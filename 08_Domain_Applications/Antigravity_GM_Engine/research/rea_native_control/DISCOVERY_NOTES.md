# 九域静态恢复与工程交付说明

任务：NBA2K22-REA-MYLEAGUE-NATIVE-CONTROL-DISCOVERY-01，Issue13，基线f8746503a29b86b7cdb3a0d624a0cd5603c69f19。遵循功能优先、已知先实现、外部模型决定WHAT/执行器负责HOW/原版游戏判断CAN。本轮无新测试和游戏进程操作。

## 覆盖与成熟度

Human模型的9域46项全部进入Registry，另加15项具体扩展/参考动作，共61项。当前3个动作ID继承2个PR12成功机制；21项CALL_LOGIC_RECOVERED、29项PARTIAL_BINDING、4项REFERENCE_ONLY、4项NOT_FOUND_WITH_SEARCH_SCOPE。后者只表示声明的搜索未恢复完整函数，不证明游戏没有该功能。19种runtime handler是代码路径数量，不是19项新实机成功。

| 域 | 本轮可恢复/已接入的逻辑 | 明确缺口 |
|---|---|---|
| D01 交易 | 继承原1对1；新恢复PICK按ID查找/反核、AddPickElement，接入多球员、签权和混合提案 | 新组合未测；资产原生拒绝原样返回，不实现规则大全和自动配平 |
| D02 合同 | OfferContract/Process、默认签约类型、options处理、Waive服务；44-byte报价25字段 | 新报价初始化/状态/部分枚举与标志未闭合；报价接受不等同签约完成，当前不执行 |
| D03 球员/员工修改 | 跟随Editor Save→Flush→父/子对象copy→refresh，取得具体入口和父/子对象关系线索 | 非独立字段Setter；完整ABI、子对象类型/所有权与必要刷新未恢复；员工属性仅布局参考 |
| D04 教练机制 | 继承当前投影Apply；恢复6POE+4字节设置的参数编码；取得/创建指定对手Gameplan | 持久完整Gameplan、Playbook/战术增换、非空引用、体系/ACE仍未知 |
| D05 球队管理 | Coach的BenchDepth/BenchUtilization子集；员工Sign44、Chemistry候选、Waive八参数服务 | 首发、轮换分钟、位置/名单独立事务未恢复；下层归属helper不能冒充完整业务 |
| D06 选秀 | 当前会话取pick→原生ID反核→指定球队/指定新秀选择，源码可生成 | 只当前未使用pick；需要真实选秀场景；UI编号/流程副作用与新源码均未测 |
| D07 训练 | 64-byte指定日输入；强度单改先读现有daily；导师Append/Delete/SetCurrentTeam候选 | 个人训练/导师manager参数、完整模板/休息恢复设置未闭合 |
| D08 数据读取 | 12类数据目录，已有身份/合同、球队/Coach子集、当前pick和球探读取源码；旧Reader复用点 | 所有数据集都非完整覆盖；完整统计、历史奖项、完整财务与全部子对象未恢复 |
| D09 球探 | 当前公开候选、原始排名/队伍点数/额度、指定对象Goal构造与Native Append、显式考察 | 显示报告/解锁评级、部分staff周期未绑定；已有目标setter的聚合刷新另列待测 |

## 函数和对象：可以写出实际调用的部分

**教练**：`0x146eaa0`为`void(const GAMEPLAN*, COACHDATA*)`。从当前Coach352字节构造私有Gameplan880字节输入，完整保留其他投影，只修改给定字段。防守/进攻分别落共享字+316的bit0/15，其他POE及四个byte字段见data/coach_settings.json。未知引用槽NULL分支继续保留，旧“自由战术引用”和`system_proficiency`标签不升级为事实。六POE合法枚举沿用原生profile；其他byte值先明确为编码边界，不能把样本范围当UI合法域。

**交易**：AddPlayer `0x12dec20`和AddPick `0x12de850`都是`int(TRADE*, TEAM* from, TEAM* to, asset*)`。`PICK*`按原版`0xf3ca00(uint id)`解析，再调用`0x947330(PICK*)`得到原生ID反核；该ID由游戏计算，不能猜成对象+0x10的值。当前owner在PICK+0，选秀当前记录使用的也是32-byte对象。每个给定资产只构造一次；Validate `0x12ec930`，提交Wrapper `0x132b840`沿用原版FullCheck→Process。最多18元素是缓冲区物理容量，不是本系统重建的完整交易合法性规则。没有工资/球员选择算法。

**训练**：`0x1325f10`为`void(TEAM*, int date_key, const input*)`。原生调用者先把百分数/配置转为输入，callee从input+8复制三个float、三项profile byte、38项subfocus byte，并从+0x3d取3-bit intensity写56-byte daily记录；它还设原生override位。源码按实际读范围分配64字节。`0x12f1390(TEAM*,date)`取得现有daily，单改强度保留其余56字节。callee自己检查是否有比赛/记录，因此可能正常no-op；不自动找别的训练日期。百分比单位、强度展示标签留给下一任务，不虚构显示转换。

**球探**：静态类型注册恢复DRAFT_CLASS96016、DRAFT_PROSPECT640、PerTeamData16、SCOUTING_GOAL148、SCOUTING_TRIP960。类最多150个候选；Trip最多3个Goal，Goal最多17个对象。目标输入是DRAFT_PROSPECT指针数组，不是PLAYER指针数组。

新增目标链直接对应PC22调用点：私有148-byte Goal→`0x1257560`初始化sentinel→`0x1322f30(goal,count,prospect**)`设specific类型2与给定目标→按调用者设私有FocusValue sentinel→`0x1244580(trip,goal,team)`追加。该函数先调用`0x13191d0(trip,goal,team)`聚合团队目标，再复制148字节并增加NumGoals；3槽满原生返回0，不删除/替换已有目标。初始化591字节线性leaf体无分支/call，已恢复到RET；先前256-byte片段没有被当作完整构造器。

团队Trip来自FRANCHISE_TEAM_DATA+0x13aac，team record采用原有36槽、stride0x13e70与fresh UID对应；PerTeamData按这个原生team index取16字节，不能直接按team_id索引。Native helper `0xfda730(TEAM*,assert_flag)`的静态公式佐证该record布局。原始ScoutingPoints只是记录点数，HadWorkout/HadMedical为已记录标志，不能推成完整报告或真实潜力公开。

`0x1261d40(TEAM*)`会消耗剩余考察次数并执行当前Trip；它是另一个显式动作。源码只允许已配置specific-prospect目标的情况，不在无目标或按排序/预测自动择人的分支调用，且不会在分派后自动执行。

**选秀**：当前根的+b8/bc/c0为type/round/slot。原版`0x92a6a0(round,slot,tableKind)`或`0x92a700(round,slot)`取当前选择记录；用上述原生PICK ID函数反核模型指定pick_id，检查owner和+0x10选人槽为空，再调用`0xec9610(PLAYER*,TEAM*)`。第二参数在原函数里读取+0xca8，确认是TEAM，不能误称PICK。该动作会走选秀原生后续流程，只允许下一任务已确认的实际选秀场景。当前记录存在不等于当前UI正处选秀，Reader明示此边界。

## 具体未完成的恢复

- **签约**：FRANCHISE_SIGNING44字节，PlayerId/TeamId、Wage、6项ForcedWage、Years、OptionType、NoTradeClause及status/type/distribution等位域已恢复。OfferContract `0x12bd4c0`有4个参数；真实调用者有context/null及两种flag组合；Process `0x12bde70`不是简单两参数setter。默认类型函数`0x12b7d60`能给出依赖当前Player/Team状态的类型，但新提案初始化、其它flag及pending→完成状态仍需闭合。未调用GenerateContract替模型生成报价。
- **裁员**：`0x12d4530`真实调用点包含TEAM、PLAYER、两项寄存器标志及4个栈参数，其中含验证/附加标志与source tag/line，共8项。不能把未知验证标志默认为绕过值。`0x12d0b60`只是内部移除helper，也参与交易，不能当完整裁员服务。
- **球员属性/四PlayTypes**：`0x141f6e0`→`0x141f880`依赖全局editor、目标+0x28、编辑parent+0x30及多个子对象buffer。触及父copy `0x8fbe60`、子copy `0x8f3b50/0x8f9270/0x915dd0`、refresh `0x99b670`等。父copy超过原24KiB/32-fragment恢复边界后改取有界入口窗口作候选；没有因此盲调用、扩大为整游戏分析或虚构所有权。需要确认具体子对象、完整参数和后续刷新，不能直接写字段后把一次memcpy称Native业务提交。
- **导师**：AppendMenteeInfo `0x124f0f0`、DeleteMenteeInfo `0x125ed70`、SetMentorsInCurrentTeam `0x13232d0`均有业务线索，manager/数组与精确Mentee/mentor/badge参数未齐。
- **Playbook/完整Gameplan/轮换**：现有profile/Writer可作布局参考，不自动升级为Native Add/Replace/Commit；新增检索多为MyTEAM/world/文件编辑器调用者。Native Get-or-create opponent Gameplan不等于提交完整Gameplan，Bench设置不等于分钟表。

## 工程与证据边界

NativeActionRegistry/NativeBinding/Plan/Facade、19个runtime handler、REA实际后端及12类ReadCatalog均有源码。默认没有transport，dispatch只准备计划；UNKNOWN不调用。下一任务显式启用后端才会在管理员进程中附加，固定EXE SHA和代码指纹、fresh根/对象、GUI线程一次调用。原始游戏内存不经直接writer修改；私有输入写入不属于游戏对象写入，实际修改交原版服务。

24份新增静态文件共2238219字节，原字节与manifest哈希保留。三轮有界字符串/RIP检索分别676、125、116个引用；未创建整个游戏函数全集，也未重复整包Ghidra超时。字符串名字/xref只是线索，函数片段/CRC字段不代替实机效果。旧REA原始证据留在rea_native_action，引用固定PR12来源，不回填。

Human在Issue13/本Run新确认了上一轮交易历史消息和双方为玩家控制，这作为新来源保存。没有声称破解原版AI自主估价、谈判或决策。次世代功能参考只扩充MySTAFF/Conditional Coaching/训练恢复线索；36个Native绑定和布局的来源均为PC22现有证据。未改生产Writer、未合并master、未操作当前存档。

完成候选只作Python/JSON读取、JS语法解析、PowerShell AST解析；没有功能测试。下一轮最小输入和场景见NEXT_TEST_HANDOFF.md，保持原先成功两项不重测、不补持久性或交易收据的Human裁决。

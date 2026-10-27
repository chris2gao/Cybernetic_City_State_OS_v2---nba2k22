# NBA2K22 原生动作调用：Issue #11

**已完成一个真实游戏Native设置PoC。** 外部输入IND/20、防守重点13，REA/Frida调用当前NBA2K22自己的Gameplan→Coach应用函数，真实教练由14变13；750ms后仍为13，再由同函数恢复14，1500ms恢复读回一致。没有用Python字典、直接业务内存写入或菜单点击替代Native执行。

这项成功限于当前Coach设置投影。原Gameplan模板没有修改；UI重进、Save/Reload、比赛收益、原版AI caller及生产全面替代均未证明。旧Memory/外部执行器继续保留。

## 实测路径与范围

```text
typed request(team_id=20, defense=13, expected_before=14)
  → 当前构建/TEAM/教练反向链接/字段/输入及null-playbook分支核对
  → 从当前352-byte Coach构造私有880-byte Gameplan输入
  → 原版函数对带canary的私有Coach副本运行，验证完整修改范围
  → 原版函数对真实IND/Rick Carlisle对象运行
  → fresh完整对象与关联设置比较：14→13，750ms仍13
  → 同一原生函数恢复14；fresh完整读回及1500ms恢复检查
```

入口RVA **21424800 / 0x146eaa0**，恢复的ABI为`void(const GAMEPLAN*, COACHDATA*)`，Windows x64 RCX/RDX。输入`GAMEPLAN+0x181`的防守重点由原版函数应用到`COACHDATA+316`的低5位。Chained unwind恢复出真正入口；`0x146eac0`只是中段，不能直接当函数入口调用。三个静态调用点来自Gameplan及manager应用流程，证据见`evidence/static/apply_callers.json`。

函数还应用其他教练设置和三个自由战术引用。因此调用器按当前Coach的原值构造所有已知输入，保留非目标设置；本PoC仅允许三个自由战术引用均NULL、输入ID均FFFF的分支，跳过额外查找服务。线程为Frida agent thread；静态分支没有TLS或嵌套原生调用，随后已由副本/实机验证此案例可行。**不将这一线程结论推广到非空引用、其他游戏阶段或其他业务函数。** STAFF池/对齐及引擎AI旗标仍是证据假设，不是只读或所有共享服务的统一硬门。

实机成功Evidence：`ev_010ee377ef98e54b1ce96b64838c5dd4e56f96283e630a9527b945abc1236673`。本轮耗时13.458秒、显式读取17830字节；3次原生调用包括1次私有副本、1次真实变更、1次真实恢复。只有Coach字节316发生目标变化，完整352字节比较通过；原Gameplan880字节、manager flags及对照球队Coach均不变。REA无脚本错误、cleanup_error=null、游戏存活。

首次副本运行因把Frida自有分配套用游戏映射清单而无法读回，消耗1次副本调用、未调用真实Coach；随后无游戏函数调用的诊断确认私有分配未在range清单中但可直接有界读取。修复只针对自己创建、持有且边界已知的缓冲区；游戏对象仍检查映射、可读性、预算、异常。Human明确批准修复后的新增3次，累计**4次原生调用／2次真实目标调用**，两份许可现已标记CONSUMED，工具拒绝重放。

原始payload中的`input_projection.system_proficiency`只是初始探针对`Coach+0x148`位17..24的便利标签，未通过本轮确认其业务名称；调用器只按原始位值保留它，不向角色宣称其含义。

## 可运行工具

从仓库根运行，CLI和合同测试只依赖Python标准库；重新执行PE分析工具需要已安装Capstone。离线命令没有游戏调用：

```text
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/cli.py preflight --offline
python -B -X utf8 -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/tests -v
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/verify_artifacts.py
```

`verify_artifacts.py`核对原始REA、批准脚本哈希、已跟踪Git字节和实机读回，要求真实成功Evidence存在，纯fixture不能替代。当前6项合同测试分别验证类型/值域、完整输入投影、非空引用拒绝、fixture不可晋级、错误许可拒绝及已消费许可不能重放；测试通过本身不证明游戏效果。

可重新准备当前对象的只读探针或供审阅的调用脚本，输出目录必须新建：

```text
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/build_preflight_probe.py --team 20 --out <new-preflight-dir>
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/build_invoker.py --request 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/examples/ind_defense13.json --out <new-review-dir>
```

准备脚本不执行它。`NativeActionInvoker`及管理员`run_rea_admin.ps1`才编排真实REA调用；`cli.py invoke --script <prepared-js> --approval <new-Human-receipt> --output <fresh-output>`必须从管理员环境运行。管理员窗口可用`Start-Process powershell.exe -Verb RunAs -WindowStyle Hidden`启动保存的runner。不要重放本Run已消费的许可，不需要重装REA或重试整包Ghidra。未来调用须重新核对实际构建、对象、场景、许可和预期值。

`NativeActionReceipt`分开NOT_FOUND、CANDIDATE_ONLY、READY_FOR_BOUNDED_POC、REAL_GAME_CALL_EXECUTED_UNVERIFIED、REAL_GAME_EFFECT_VERIFIED、FAILED_OR_ABORTED。CLI检查REA脚本/清理错误与原始回执，不把REA进程退出0当成操作成功。

## 六类可用性

| 类别 | 本轮证据 | 现在能做什么／不能做什么 |
|---|---|---|
| C1 教练攻防 | 原版Apply服务及真实14→13→14 | 该隔离、null-playbook案例可调用；不替代持久Gameplan提交或全部旧Writer |
| C2 轮换/训练 | `SetTrainingForTeamOnDate` RVA20078352及多字段写入 | 有训练mutator候选；日期/训练结构和完整ABI未齐，未调用 |
| C3 属性/倾向/徽章 | 原生训练成长判断与HandlePlayerTraining分支 | 尚无可接收任意单项属性目标值的安全Setter；第二领域PoC未具资格，未盲调用 |
| C4 AI-AI交易 | 交易菜单caller及108个调用、已有AI评估名称 | 共享validator/commit尚未分离；不以队伍ID改写代交易，不调用菜单 |
| C5 签约 | 精确查询只找到类型/其他模式UI名称 | 本搜索范围未定位签约提交；不将MyCAREER谈判当MyLEAGUE事务 |
| C6 选秀 | `Draft_DraftPlayer` RVA15504912及状态写入 | 有操作候选，完整参数/资产事务和选秀场景不明；当前日历场景不推进赛季 |

机器目录`action_atlas.json`逐类记录输入、函数/ABI、必要上下文、读回要求、缺口、替代判断和下一步成本。C1的当前PoC成功不意味着其他五类成功；目前没有一类获得完整生产替代资格。第二领域条件性PoC因没有单项可逆Setter资格而未执行，后继优先从训练成长的实际属性应用callee继续。

## 来源与复查

固定游戏SHA256为`1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`。`evidence/manifest.json`保留25份文件，覆盖四个真实REA阶段、局部静态函数/调用点和规范；静态查询带命中上限及范围声明，同源结果不算独立证明。完整PE不上传，所有游戏指针仅在当次脚本内使用，公开材料使用RVA/逻辑ID。

静态工具`discover_mutators.py`、`inspect_candidates.py`、`trace_static_callers.py`可以复现限定查询与局部函数分析；不创建整游戏函数清单。`retain_evidence.py`对写入候选只保留完整位置/范围及相关POE窗口，并记录原始本机分析摘要哈希，明确是选择性保留。原始REA文件未经改写，保留每阶段脚本、PID/build/哈希、指标、清理与失败。

工程提交供独立审核；没有合并master、修改生产接口或恢复世界数据阶段02。完成指针在本次Native Action Run的`08_结论/COMPLETION.md`。

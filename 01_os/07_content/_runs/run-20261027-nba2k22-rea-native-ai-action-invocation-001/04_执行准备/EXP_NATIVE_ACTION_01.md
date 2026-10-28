# 首个真实原生设置实验包：待Human一次范围许可

experiment_id: EXP-NATIVE-ACTION-01

- 游戏SHA256：`1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`；管理员runner每次新采PID并重新核对EXE。
- Human确认“已加载独立测试存档，可恢复”。本实验不推进日期、不切换球队控制、不提交存档或交易。
- 当前只读REA：`ev_9af318f840801043d82f96d245040c907b8ebe658e969780dcf24f02eda40341`。IND/20、Rick Carlisle、TEAM反向链接、当前POE14、类型字段和上下文重读一致；65536字节预算下实际9210字节，3个短hook均清理、零事件，不把它当无调用证明。
- 入口RVA `21424800` / `0x146eaa0`，静态恢复的签名为`void(const GAMEPLAN*, COACHDATA*)`，Windows x64 RCX/RDX两个指针。`0x146eac0`是chained unwind片段，不是可调用入口。三个调用点来自Gameplan/manager应用流程；尚未证明原版AI caller，标为共享业务服务候选，不标AI专属。
- 当前调用分支要求三个自由战术引用均NULL，临时输入ID均FFFF，使该路径不进入额外原生查找调用；不适用于未来非空引用对象。函数在此分支只读取输入结构及操作COACHDATA内的已列设置；没有TLS/全局服务调用。调用线程为Frida agent thread，线程可用性目前是静态分支依据，须经本次副本实测验证，不声称已捕获游戏线程调用。
- 外部输入：`SET_COACH_POE(team_id=20, defense=13, expected_before=14)`。克隆880字节Gameplan，在私有输入缓冲区把其他应用字段按352字节当前Coach投影填回，只改变防守重点目标。原游戏Gameplan不直接修改。
- 最多3次原生调用：①原版函数应用到带前后canary的私有Coach副本，验证ABI和完整修改范围；②仅在①全通过且目标未变时，对真实IND教练14→13；③约750ms后同函数恢复14。副本失败不进入真实对象。
- 验证：完整352字节预期比较、原Gameplan880字节不变、manager flags不变、对照球队教练不变；真实调用即时与750ms读回、恢复后及1500ms读回。没有自动Memory兜底；原生异常/恢复不符报告测试存档重载要求。
- 本实验只证明当前Coach设置投影接受原生操作；不证明原Gameplan模板已提交、Save/Reload、UI重进或比赛AI效果，也不宣称能替代全部旧Writer。
- 准备的执行脚本SHA256：`c99f501dc5321e23f5c70a73bf2025e6f09044f76c7854e1c5202cac28445aab`。位置在工作区外`rea-ai-issue11-runtime/poc-01/invoke_poc.js`，与`experiment_package.json`绑定。Node语法检查及5项参数/投影/批准绑定合同测试已通过；这些不是Native实测。

Human_scope_approval: APPROVED_ORIGINAL_AND_REPAIR_EXECUTED_AND_RESTORED

原脚本副本调用后因私有分配range查询为空而未能完成读回，没有调用真实对象。经无业务调用的诊断及修复，Human批准新脚本`27a85d31548171884aca55f2f433b1a0c9b583b7565b2b51631d70fa208053c1`追加3次、累计最多4次。实际完成副本验证、真实14→13、原生恢复14；REA成功Evidence见完成指针。两份批准记录均已标记CONSUMED，不能重放。原准备内容作为历史保留，不冒充首次脚本就成功。

首次effectful许可来源：当前Human发布任务书`CODEX_NATIVE_AI_ACTION_TASK_v1.md`第4节，明确要求具体、可恢复的小范围实验许可；不是由技能文件新增审批。此前静态/只读工作不以该许可为前提。

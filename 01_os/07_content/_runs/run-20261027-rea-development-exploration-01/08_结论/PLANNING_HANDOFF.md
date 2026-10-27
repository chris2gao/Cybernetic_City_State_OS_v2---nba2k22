# 交开发规划模型：REA 阶段性探索材料

**状态：PARTIAL / HUMAN_PAUSED。** Human 要求先停止，后续将提供完整探索任务与游戏资料；随后明确要求提交线上，供开发规划模型形成下一轮任务。此次仅整理并发布已有材料，不恢复实验，不声明完整探索完成，不请求或执行master合并。

## 1. 阅读顺序

1. 领域 `docs/development/REA_DEVELOPMENT_PLAYBOOK_V1.md`：已验证用法、工具选择、三阶段映射和限制。
2. 本文：规划缺口和有界任务建议。
3. `06_执行/evidence/SOURCE_MANIFEST.json`：精确文件及SHA256；按问题打开所需Evidence与findings，不加载全部大图。
4. 领域 `research/rea_development/README.md`：脚本和依赖。

精确源基准master为 `7742568ac677b3c16079887463f05e81cb1191ed`；未来需要重新读取。研究分支 `task/rea-development-exploration-01`。提交页面由Human消息中的本次实际提交链接定位；这里不伪造自己的提交SHA。

## 2. 实际完成的探索

| 主题 | 原始证据/分析文件（相对evidence目录） | 实际结果 |
| --- | --- | --- |
| 当前原生类型/代码片段 | metadata-evidence.json、metadata-findings.json、metadata-target.json | 13结构，21个LEA代码片段与进程匹配，2.719秒；不是执行轨迹 |
| 成长/徽章 | growth-evidence.json、growth-findings.json | 9结构，2.614秒；导师Progression/DateLastChecked等、联盟成长调参和徽章效果定义 |
| 转播设置 | presentation-evidence.json、presentation-findings.json | 5结构，2.632秒；ticker、切镜、声音、采访人数等定义；实际当前设置值未知 |
| 批量执行工具 | bulk-fixture/bulk-fixture-results.json及apply/restore Evidence | 自建4096条记录真实修改、进程自身独立读回全部一致，再恢复全部一致；不证明游戏批量写 |
| 调用观察工具 | call-trace-fixture/call-trace-results.json及trace Evidence | 自建native-ABI回调16事件，参数/返回一致；未对游戏设置hook |
| 资源与绑定候选 | scorebug-rea-evidence.json、scorebug-findings.json、scorebug-bindings.json | 本机模组ZIP，260成员/9场景/44 SceneText，安全解包、UI树及SCNE部分解析 |
| 资源副本比较 | scorebug-candidate.json、scorebug-comparison.json、scorebug-comparison-evidence.json | 改1个内部成员的1处布局参数；REA精确报告root+该成员变化，其余259 occurrence未变；没有部署 |
| 原先Overall研究 | prior-overall/原始Evidence、findings、human-ui-observation.json | 6缓存，Ben87和Embiid基础95人工UI吻合，Embiid加成96未解释 |

原EXE、原模组、解包素材、修改后的IFF不提交到仓库；提交的是脚本、摘要、哈希、清单及REA Evidence。研究副本在本机游戏目录外，按脚本可重建。

## 3. 已知事实与尚不能回答的问题

- 当前 Human 场景：终极联盟存档已运行约一个月，停在日历页、控制步行者。没有同期比赛场景观察；不宣称半场/采访/更衣室内容已执行或被关闭。
- 已确认的是元数据定义，不是调参实例值或完整成长条件。不能把 MyCAREER 升级点数、声望或Overall解锁表当成终极联盟徽章成长门槛。
- 候选目录分16家族，有交叉；字符串数量不等于功能数。**关闭内容总数UNKNOWN，已启用内容总数UNKNOWN，游戏实时信息注入UNKNOWN。**
- 当前有自建fixture证明批量传输和有界hook，但没有游戏对象新增/删除、原生索引维护、缓存提交、UI更新、Save/Reload或跨场景稳定性证明。
- SCNE存在缺失值/尾逗号等JSON-like语法；VCUI有24,384字节尾部二进制未解释。解析视图不能直接重写为纯JSON部署。
- Ghidra大EXE路线已耗尽此前三次修复预算；本轮未重试。若要重开，先给出新的局部分析/复用项目方案；不要只增加timeout。
- 本机有newscorebug模组，不知道是否当前加载；不能把模组节点计为原版隐藏内容，也不能用平台/世代不同的历史2K画面证明本机可用。

## 4. 建议下一轮任务包如何有界

以下是规划建议，不是已派发任务，也不要求Human逐字段微审批。

| 候选包 | 资料输入 | 本轮可复用入口 | 真正应证明什么 |
| --- | --- | --- | --- |
| MyLEAGUE单一徽章/导师成长 | 指定徽章、UI路径、玩家/导师身份、资料中的明确条件假说、可观察时间范围 | FRANCHISE_MENTOR字段、FRANCHISE_PROGRESSION_TUNING、LinkMentor/SetMentors候选范围 | 模式适用性、实际进度实例、谁读取/刷新、条件与反例；允许UNKNOWN，不直改徽章 |
| 已有一类合法动作的批量底层适配 | 指定一种动作、字段合同、测试存档、批量规模、审批边界、恢复目标 | 4096 fixture脚本和当前工程读取器/执行器 | 身份/ownership、before条件、并发及索引、提交/回读、部分失败恢复；不以fixture代验收 |
| 一个统计通知/SceneText实时接点 | 具体场景/页面、现有模组清单、期望显示内容、文本编码/长度及退出目标 | scorebug UI树、44 SceneText、资源diff及呈现队列引用 | 场景加载、文本消费者、所属线程/对象生命周期、受控信息桥接和画面证据 |
| 一个半场或采访内容的开关调查 | PC22同模式资料、对应资产、可比较场景和“已关闭”假说 | 原生转播字段、资源清单和16家族索引 | 资源依赖、代码可达性、开关实例、运行观察，排除残留/跨模式；不默认激活 |
| 一种物理细节 | 明确球/脚步/碰撞/布料之一、资料及期望观察信号 | 物理候选字符串家族、游戏固定构建 | 实例与更新函数、输入/输出/可重复反例；与转播UI分别验收 |

每包建议固定：一个机制、一组实例、一种模式/场景、允许读写对象、最大时间/事件/字节、所需Human操作、成功与证伪标准、清理/恢复及资料链接。无需以“探索全部引擎”替代可执行问题。

## 5. 本次发布的边界

整体探索目标仍暂停，综合手册为阶段性稿。此次线上材料可用于下一轮规划和独立审阅，不代表规划模型可以自动激活脚本、恢复游戏实验或合并master。没有向其他模型发送消息；由Human手工转交本分支或精确提交链接。

# Codex 下轮工程任务｜MyLEAGUE 原生控制新机制的最小实机验证

任务ID：`NBA2K22-REA-MYLEAGUE-NATIVE-CONTROL-VALIDATION-01`  
**任务类型**：探索性原生业务功能验证；与上一轮`Issue #13`纯静态发现不同，本轮允许提出并在Human按场景批准后进行**最小实机验证**。  
**本地Codex唯一Owner**：Human指定的Codex客户端与窗口，GitHub Issue不自动启动任何窗口。  
**基线固定提交**：`2bdda79c6513f463252d7d01834218edb590eec9`，来自 Draft PR #14；新分支`task/nba2k22-myleague-native-control-validation-20261027`，不合并master、不重写PR #14、不过度改动现有生产Writer。

## 一、任务目标与不做的内容

把PR #14已恢复但未实机运行的`CALL_LOGIC_RECOVERED`动作，**按领域用极少量真实例子**区分：能调用且游戏状态确实改变、游戏合法拒绝、上下文不适用、参数绑定仍错误/缺失。测试必须以游戏自身Native服务为执行路径，而不是人工点击或直接改游戏对象字段。

**Human已明确要求的分工不变**：

- 外部GM/Coach/Player决策层给定**确定的对象ID、资产、目标参数**；Codex**不能为使测试成功而选择另一个交易对象、匹配工资、调整合同报价、换一个新秀、优化球队轮换或训练方案**。
- Codex测试Native执行器是否能把这组参数按原版业务规则提交。原版拒绝就报告`REJECTED_BY_GAME`、上下文不允许就报告`SCENE_NOT_READY`，不改请求偷偷重试。
- 本轮**不研究**AI为什么选择这种战术的比赛效果；不重做交易历史、原生返回收据、Save/Reload持久化、各种资产组合穷举或整体策略建模。继承已有的两个成功实例（Coach14→13、球员1对1交易），不要求重复跑相同实验。

**当前已有**：九域61动作/36个函数及布局绑定/19个代码handler/12类Reader；只有两个领域曾取得实机业务成功。21项`CALL_LOGIC_RECOVERED`表示具体调用计划，**不能当已实机验证**。

## 二、优先按“低成本获取新信息”分四层

### A. 独立只读验证（第一步，优先）

**目标**：确认PR #14新Reader能在当前、匹配构建的隔离MyLEAGUE存档中读取`Team/Coach/Player`子集、当届候选与球探原始进度、当前draft pick对象（如有真实当前场景）。  
- 对每一项只用一个Human指定对象/当前游戏实际存在的对象，比较UID、TEAM互相关联以及当前原版可见资料（能看则比、不可见标UNKNOWN），不要扩成全赛季数据采集工程。
- **Read-data 12类都非full coverage**；本轮只验证实际已有绑定子集，不去补完所有统计、历史和财务字段。
- 非准备好的Draft scene不触发选秀业务。

### B. 低副作用的新原生Setter（优先）

**目标**：至少一个**此前未实测的新字段/新业务操作**在独立可恢复测试场景中被Native接受，并在本次实际读取时与给定目标一致。候选：
1. `COACH_SET_KNOWN_CURRENT_SETTINGS` 的一个新POE或已静态恢复的Bench字段（原有Coach defense14→13不重跑）。
2. `TRAIN_TEAM_SET_INTENSITY` 或 `TRAIN_TEAM_SET_SCHEDULE` 指定native日期、球队和Human给定的强度raw值/完整64字节参数；校对唯一指定日期，原游戏可能合法no-op，不准Codex自动找新日期。
3. `COACH_ENSURE_OPPONENT_GAMEPLAN` 需要证明只针对给定对手及球队，若将创建/修改Gameplan则属于效果操作，须包含在Human准入范围。

选择哪个，以**真实上下文可用性**、可恢复性和静态参数完整度决定；不得为达成成功率擅自挑“最有利”的业务值。需要Human给定具体参数时提出一次合并清单，不反复零碎审批。

### C. 球探：读取 → 精确分派（第一优先跨领域验证）

**目标**：从当前选秀届次读取公开候选及目标槽情况，按Human/外部GM**给定**的队伍和候选UID列表，执行`SCOUT_ASSIGN_TARGETS`原生`initialize_goal→focus_specific→append_goal`。检查原始Trip/Goal数量及身份是否符合请求。  
- 必须先确认当前team record与Trip+0x13aac，候选UID指向DRAFT_PROSPECT而不是NBA球员；**不把原始排名或点数误说成完整已解锁球探报告**。
- 考察目标最多3个Goal槽，specific目标最多17个候选，为静态布局上限；超过原版可用槽时**返回拒绝，不自动删除或替换现有目标**。
- `SCOUT_EXECUTE_CURRENT_TRIP` 是**单独消耗球探次数**的动作，不因目标成功分派就自动执行；仅Human另外明确许可并提供当前可恢复游戏场景时纳入有界试验。
- 本轮不要求研究从球探最终评分到决策的深层影响。

### D. 需专门游戏场景的较高影响操作（条件性）

**选秀**：有真实当前选秀大会的隔离存档、Human给定当前有效且尚未使用的pick ID以及指定prospect ID时，才尝试`DRAFT_SELECT_PROSPECT`一次；游戏可能自动进入下一顺位，需在批准范围中明示。不得推进常规赛日历来制造场景。

**选秀权/混合交易**：只在Human提供确定球队+明确资产集合、隔离存档以及业务操作许可时，验证一次原生`PICK ID反核→AddPick→Validate→提交`。不重跑已有球员对球员交易，不搜索薪资匹配，不改请求，不追完整交易规则百科。

两者可在当前场景不合格时直接标`DEFERRED_NO_SCENE`，**不为了完成数量进行危险操作**。

## 三、当前禁止列为“测试已准备完成”的几类

从`DISCOVERY_NOTES.md`继承：

- **签约/续约**：新报价初始化、status/type部分枚举和flags以及Offer/Process衔接未齐；不允许把报价接受当作签约完成。
- **球员/员工完整编辑**：Editor Save/Flush、父/子复制、refresh调用所有权和ABI不齐；不能把一次memcpy当作完整游戏业务Setter。
- **完整轮换/分钟、战术手册及持久Gameplan提交**：目前没有完整业务入口；Bench字段属于Coach小子集。
- **导师业务**：manager数组与mentor/mentee精确参数不齐。
- **Waive八参数**：仍含未知真实业务标志，不盲传默认值。

这些能力如要提升成熟度，可在本轮**短时定点静态补齐**；只有足以满足真实调用资格后才申请后续实机测试，不做全面再次逆向、不虚构Native实现。

## 四、权限与两步式执行（最小审批）

**这份任务书只授权准备原型测试代码、静态分析及测试计划，不等于现在就有权限访问用户正在运行的游戏或修改存档。**

真实行动按**两步**：
1. Codex核实PC22 EXE SHA、当次模式和存档、Human给定操作值、将运行的Script哈希及唯一目标/关联对象，先产出`EXPERIMENT_BATCH_01`清单：**本批准备开展哪几项只读/写入/业务函数动作、次数/预算/异常停止及恢复方式**。建议第一次一批涵盖只读查询、一个低影响Setter、一个球探目标分派候选；高影响选秀/含Pick交易另包。
2. **收到Human对整批动作及测试存档的明确许可之后**才使用管理员Codex/REA附加真实游戏并实际运行；不可拿上轮已消费许可复用。若只有只读许可，则只执行只读部分，写操作显示`NOT_AUTHORIZED_NOT_EXECUTED`。

执行时使用`NativeControlFacade`/已提交脚本生成器和明确启用的`LiveExecutionContext`，默认transport禁止自动运行；无实际Native资格的Action保持UNKNOWN，不因为缺少反证就放行。不运行无界Hook，不猜测选秀阶段/日期，不通过关闭安全工具或隐式提权绕过约束。

可创建或使用Human认可的测试存档，并记录“未保存/是否由游戏自动保存”这一实情；**不安排专门Save/Reload持久性研究**。如果游戏响应/原生返回记录缺失，先独立只读核对目标状态；状态仍不明则停止该次业务，禁止自动二次提交。

## 五、Codex应交付哪些可直接判读的实质结果

建议第一批`REAL_NATIVE_EFFECT_VERIFIED`结果来自Coach一个新字段、训练或球探分派（不要求每类全部成功）。每次针对一个Human指定输入给出：

| 信息 | 必须写清 |
|---|---|
| Action ID + exact supplied input | 原始球队/对象/参数，不能自动改 |
| Native函数和调用序列 | 当前PC22构建、目标函数和真实上下文 |
| 真实执行状态 | `NOT_EXECUTED` / `REJECTED_BY_GAME` / `EXECUTED_EFFECT_UNVERIFIED` / `REAL_NATIVE_EFFECT_VERIFIED` |
| 最小检查 | 操作前值、实际游戏操作、目标值读回，必要时同一对象无关字段未被更改 |
| 失败/不适用 | 精确绑定缺口或游戏原生拒绝；不自动补偿或重试 |
| 新旧状态差异 | 哪一项`CALL_LOGIC_RECOVERED`提升为实际有证据的Native能力 |

**不要把任务花在增加测试计数、计算多少token、重复已有1对1交易或完善全部业务规则上**。优先回答Human：新增哪几个真正可用的原生操作？还不能调用的具体原因是什么？下一步有必要进入选秀大会的操作场景吗？

## 六、仓库与交接

- 只在`task/nba2k22-myleague-native-control-validation-20261027`或其子分支写代码和新增实测证据；固定初始`PR #14@2bdda79c6513f463252d7d01834218edb590eec9`，**不修改或合并PR #14、PR #12或master**。
- 新任务根`01_os/07_content/_runs/run-20261027-nba2k22-myleague-native-control-validation-001/`；成果进研发原型目录或新Run。不得重写旧原始证据。
- 首批实验许可批单获批以前不执行活体游戏调用。Codex本地窗口由Human指定；Github Issue不是自动启动。
- 完成后交付简短真实结果报告、具体新增Native功能、必要原始证据、更新的能力登记与Draft PR；不自动合并master。

**本任务核心成功标准**：以前未经过实机验证的Native Action，在Human给定具体对象及参数后，成功通过游戏原生服务执行并能独立读回。**如果没有可用测试许可或游戏阶段，就诚实地以准备完毕或有界未知结束，不得制造新的“实机成功”结论。**

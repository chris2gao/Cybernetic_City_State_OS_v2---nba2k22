# VAE Gemini 集中工程 · GPT 源码与证据审核报告

**任务**：`NBA2K22-VAE-GEMINI-INTEGRATED-INDEPENDENT-REVIEW-20261030-001`  
**审查固定版本**：`c2d9caae388bac3ae5e586c69ee0bd2116ba473b`  
**派发**：`49659925312275d101232c3bc522f162436d28d5`  
**NBA 基线**：`45cc45cae0550ddcda192a2179ea48509b27f6ee`  
**Human A-v1 确认记录**：`a98aa2db6e442bbc3aecfa552665ea13d482683e`  
**上游 Stage01 独立审核**：`4640f6e05f2b84e31661c7b2039dfc5d202b30a5`

## 一、正式审核结论：REWORK_REQUIRED

**当前候选暂不建议 Human 接受为集成工程完成版本。** Gemini 实际交付了R01–R09 dataclass、E1离线dry-run、E2–E4边界守卫、21个原始pytest用例和来源矩阵，GitHub 变更范围合规；但VAE的产品关键约束“静态候选不冒充真实Profile”“比较必须同来源同引擎路径”“历史追加不可被假收据替代”未由代码保障。存在4个P0源码逻辑缺陷、5个P1、3个P2，不只是测试覆盖不足。

**影响范围**：不证明 Gemini 实际修改了游戏。当前Simulator默认和实际Pipeline均只返回NOT_RUN，静态检索未见VAE实现调用REA/Hook/Save。问题集中在未来从dry-run迈向实机、证据发布以及历史可回溯时的安全与事实边界，故必须在接受工程候选前修复。Stage01 Human的A-v1语义确认继续有效，不受本次工程审核否决影响。

## 二、独立审核方法与测试真实性

1. 直接读取固定 SHA 的派单、任务合同、Stage01 Human确认、G01–G08资料、R01–R09 V2 JSON、所有关键Python源码及对应测试文件，不采用Gemini完成指针作为正确性结论。
2. GitHub `compare(base=45cc45ca,head=c2d9caae)` 实际得到 **31项文件变更，全部在四个已授权目录范围内**；候选发布分支HEAD与提交相符，master不受本次审核写入影响。
3. 阅读现有`test_contracts.py`、`test_pipeline_e1.py`、`test_reader_safety.py`、`test_e2_e4_contracts.py`、`test_verification_plan.py`以及`verification_plan.json`。开发者在上传回执里给出`21 passed in 0.14s`，这只是**开发者执行记录**。
4. 本审核运行了**四个独立的最小Python对照反例**（与固定源码控制流程等价，不是完整源码直接导入）。输出分别证实：R06跨存档/路径误判、R03静态默认READY风险、R08新实例丢账本、R07固定阈值可能触发CONFIRMED。复现源码见`07_测试执行/source_equivalent_counterexample_probes.py`。
5. **没有在本审核环境重跑Gemini完整21项原始pytest**：当前仅有GitHub源文件读取通道，没有可执行的固定SHA整仓checkout；当前隔离Python沙箱无法从GitHub拉仓库。不可将上述最小复现实验称为原始21项测试重放。
6. 未连接当前真实游戏、无PE动态验证、无Native/Save写入。对“开发过程中没有任何外部写入”只能根据代码和报告限缩判断，不能以Git diff证明游戏进程历史。

## 三、P0: 必须修复后才可以认为具备安全试验基础

### P0-01 静态默认值冒充CAPTURED

**源码**：`src/vae/reader_adapter.py::VAEReaderAdapter.read_settings_field`。

程序从 `settings.json` 的`default`、`court.json` 的`hof_default_user/cpu`，乃至硬编码的`three_point_success=50`得出数值，却统一设置`status=SnapshotStatus.CAPTURED`，`save_id=OFFLINE_DEFAULT`，`captured_at=STATIC_SOURCE`。固定源码从未读取游戏进程或真实存档。既有`test_reader_safety.py`还错误地把这种CAPTURED当合格断言。这直接违反已批准A-v1的“静态默认不等于当前游戏值”。

**关闭判据**：将静态规范及硬编码fixture从当前Profile分离。当前运行游戏未知时必须`UNKNOWN`/`OFFLINE_FIXTURE`（可在独立字段保存参考默认值，不给LIVE CAPTURED）。添加静态源、无Reader、当前Save不同场景的失败测试。

### P0-02 非实证前置检查可进入READY

**源码**：`src/vae/preflight.py::VAEPreflightEngine.prepare_preflight`；`pipeline.py::run_e1_slice`。

READY只验证`snapshot.raw_value is not None`、`restore_plan`含`rollback_value`和`authorization_ref`非空，不验证来源证据等级、游戏版本/存档/模式/字段侧别身份、原值是否被独立读回、授权是否真的覆盖动作、恢复是否可行。Pipeline使用`AUTH_OFFLINE_DEV_DRYRUN`模拟字符串，还会在`raw_value=None`时给restore_plan填50。尽管当前模拟器最终只输出NOT_RUN，`READY`本身语义已经失真。

**关闭判据**：READY必须绑定真实读取、权限真实性和可执行恢复方案；dry-run可以是`PLANNED`或`BLOCKED`并单独继续模拟，不得把模拟许可误当实机许可。增加静态默认值非空、伪造授权、无恢复能力的负向用例。

### P0-03 伪造比赛事实被标记RECORDED

**源码**：`src/vae/pipeline.py::VAEE1Pipeline.run_e1_slice`。

硬编码`GAME_E1_SAMPLE_01`、日期`2021-11-15`、`team_3pt_pct=0.42`、`team_fg_pct=0.48`、`pace=101.2`，且`status=ObservationStatus.RECORDED`，备注为`Initial offline baseline observation`。此时R04恰为NOT_RUN，R05恰为UNVERIFIED，没有独立游戏比赛样本。此类Fixture不应进入真实已记录比赛的数据通道。

**关闭判据**：示例游戏数值只保留在显式OFFLINE_FIXTURE/TEST_ONLY空间，真实竞争观察应`INSUFFICIENT`/`NOT_OBSERVED`。真实RECORDED必须有原始Game ID、Save、批次、引擎路径及来源证明。

### P0-04 R06跨存档和3D/Calendar误判可比

**源码**：`src/vae/contracts.py::CompetitiveObservation.is_comparable_with`；`observation.py::VAEObservationComparator.compare`。

比较仅检查side、controller、两个Normalize布尔值、两种单节长度和`base_source_ref`，**未比较save_id、engine_path、trial_id、game_build**。当`SAVE_A/3D_PLAYED`与`SAVE_B/CALENDAR_SIM`拥有相同其它字段时，该方法返回`(True, 'Comparable')`。独立最小Python反例已经执行。固定V2合同的可比性文字本身也遗漏了这些硬边界。

**关闭判据**：必须校验同源Save/world/build及同类引擎路径，并明确不同Trial是否允许比较及如何绑定对照组；无可靠身份的返回INCOMPARABLE或UNKNOWN；有跨存档/路径的失败测试。

## 四、P1: 已有代码的实质性行为与过度断言

- **P1-05 R08历史不是耐久存储**：`revision.py`每次构造都将`committed_keys=set()`、`ledger=[]`，仅写进Python内存；所谓`Committed successfully`收据未经过文件、数据库或Git持久化。重新实例化即可重复提交。F04 **未关闭**；F03初始化`PENDING_REVISION`本身已更正，但生命周期仍只能算离线局部实现。
- **P1-06 R05技术验证只靠字符串**：`readback_adapter.py`只要EXECUTED收据配两条不同非空Getter字符串即可返回VERIFIED；有`save_reload_ref`字符串就升级L3，没有真正回读值、时点、对象身份和重启验证。当前dry-run不触发，但未来绝不能宣称已经实现真实L3验证。
- **P1-07 R07效果评价可能假阳性**：`evaluator.py`以5场、差值阈值0.02和任意置信度输出`CONFIRMED/REFUTED`，没有声明阈值来源、配对与控制、统计不确定性或Human确认。这超出了已批准“正常游戏反馈、允许INCONCLUSIVE、不把相关视作因果”的约束。
- **P1-08 G02原始来源描述矛盾**：`G01_G08_EVIDENCE_DOSSIER.md`称`settings.json`的`max_contract_rating`已纠正默认/范围；但开发diff没有修改该文件，GitHub既有原始内容仍为`min=70,default=40`。应保留原缺口。
- **P1-09 机读修复声明过度**：V2 JSON的`audit_resolution`将F02/F04/F06写成resolved，与上述证据冲突；不能把合同字段“存在”直接当成语义或耐久实现“已完成”。

## 五、P2: 限制项与后续验证

- **P2-10 测试绿灯范围小于报告宣称**：`test_loop03`只检查G01–G08字符串存在；`test_loop12`只检查checkpoint文件存在；`test_loop13`检查V2 JSON含resolved字样；`test_loop02`只看未提交工作区`git status`而非本次已经提交的差异；`test_loop11`检查模拟器开关，并不独立核实游戏操作日志。保留“开发者自测21通过”，不等于13项证据门独立验证通过。
- **P2-11 E2–E4为守卫原型**：`e2_e4_extensions.py`仅含分钟范围、人数、双队检查、拒绝训练Setter等；没有角色完整闭环。当前工程标签`BOUNDED_CONTRACT_ONLY`合理，不可升级成生产可用。
- **P2-12 源成熟度不可外推**：研究中双Normalize/静态字段缺乏当前存档动态映射；历史双队交易成功只证明特定实例，不足以证明PC22 Native引擎绝对不可能存在任何三方路径；`GAME_BUILD/PE`固定字符串不能代替实时指纹比对。

## 六、F02–F07 独立逐项判定

| 原问题 | 开发者声明 | 本次审核状态 | 为什么 |
|---|---|---|---|
| F02 R06可比性 | resolved | **OPEN** | save和engine路径未核对，静态Profile虚假真值 |
| F03 R08初始状态 | resolved | **PARTIALLY_CLOSED_OFFLINE** | `PENDING_REVISION`初态正确；真实追加收据不能验证 |
| F04 R08持久身份/幂等 | resolved | **OPEN** | 实际进程内存set/list，不能跨实例去重 |
| F05分项验收测试 | resolved | **PARTIALLY_SUPPORTED** | 有测试，但部分仅存在性断言，核心负例缺失 |
| F06事实/UNKNOWN边界 | resolved | **OPEN** | 静态CAPTURED与伪RECORDED直接违背 |
| F07阻断态可空/状态 | resolved | **PARTIALLY_CLOSED_OFFLINE** | R03/R04基本校验有用，但权限来源、L1–L3验证和跃迁不完整 |

## 七、G01–G08：正确的证据成熟度

| G | 本次可信水平 | 仍未完成 |
|---|---|---|
| G01 | STATIC_SOURCE / OFFLINE_FIXTURE | 当前Save/build/scene/PE动态绑定 |
| G02 | STATIC_SOURCE，且存在元数据矛盾 | USER/CPU消费与Getter/UI一致性 |
| G03 | SOURCE_RESEARCH | 双Normalize实际独立读取、同Game实场vs日历 |
| G04 | 历史限定Coach Native实例 | 当前场景Coach类型和保存生效 |
| G05 | 历史限定双队交易Native实例 | 新存档签约/选秀/多资产真实覆盖 |
| G06 | 训练字段静态研究 | Player权限与具体UI对应 |
| G07 | OFFLINE_FIXTURE | 自然比赛真实观察轨迹 |
| G08 | PRECONDITION_TEMPLATE | 真实独立备份与恢复读回 |

G01–G08档案是准备材料，**不是完成的Stage02真实取证包**。

## 八、E1–E4与安全审查

- **E1**：离线Python Dry-Run结构有实际代码，R01–R09名义上可串联；但原型把静态事实升格为CAPTURED、READY和RECORDED，**只能评为 `OFFLINE_PROTOTYPE_REQUIRES_REWORK`**。
- **E2**：Coach分钟和轮换的边界守卫存在，`BOUNDED_CONTRACT_ONLY`。
- **E3**：双队交易数量及硬编码名额门存在，`BOUNDED_CONTRACT_ONLY`，不等于真实交易执行。
- **E4**：个人训练写入被拒绝，`READ_ONLY_BOUNDED`，不等于真实Player字段完整读取。
- 当前VAE Simulator构造`allow_live_writes=False`，`execute_trial`默认dry-run。只读Git差异无游戏写入路径，本审核没有调用真实游戏；**不证明Gemini历史进程未有外部动作**，报告按限定来源判定。

## 九、集中修复的工程任务建议

Gemini继续在同一个主任务/开发分支内进行**一轮集中修复**，不要为每项发现切新任务。修复顺序：R01静态/实测来源隔离→R03权限与READY→R06身份和引擎路径→R07观察事实/评价→R08耐久追加→R05验证层级→G01–G08来源注释→扩展负向测试及完整回归。不能因静态不能获取活进程就造假；对于无法在当前任务权限内取得的真实Game/Save/REA证据，应诚实保持UNKNOWN，而不是强行要求实机完成。

闭合证据要求：每个P0/P1有具体失败Fixture→修复→重测的双向证明；`R01`静态读取必须不能CAPTURED；`R03`静态+伪授权必须BLOCKED；`R06`跨存档或跨路径必须INCOMPARABLE；`R08`若只支持内存，应改名为临时草稿账本，不得称durable APPENDED；`R07`不能由无证统计阈值产生真实因果确认。验证报告应记录完整命令、退出码、候选SHA与新增测试列表。完成后仍由本审核岗位/新审核窗口按同一审核报告定点复核，Human最后决定是否接受。

**不建议当前候选作为工程完成版本交 Human 接收**，也不允许由此审核结论开启Stage02真实游戏取证/存档写入。Human已经确认的Stage01 A-v1继续有效。

## 十、身份、连续性与可信边界

本次Human明确说“审核不用隔离，你可以继续审核”，因此当前审核在**原Stage01独立审核窗口**继续展开，但它不是Gemini开发者窗口，开发源码并非本窗口写成。平台级独立窗口实例ID没有披露，记`UNKNOWN`；实际执行模型GPT-6来自会话提供的身份信息，不是外部模型身份证书。同一窗口跨已关闭的Stage01任务和新审核任务是Human的本次明确覆盖，不等于改写OS一般的隔离推荐。未执行PRMS SAVE、formal Communication、Core runner或游戏操作。

### Minimum Work Unit

- **实际工作**：固定SHA来源与31文件范围核验、主要源码/测试逐模块分析、4个独立Python最小对照反例、F02–F07复审、G01–G08证据分级、E1–E4成熟度裁定。
- **实际未做**：Gemini完整pytest执行、真实游戏和Save/Reload验证、Human接受、Core/master集成。
- **结论**：`REWORK_REQUIRED`；P0/P1须由原Gemini任务集中返修，不能以开发者自测21通过升级为独立验收通过。审核报告与证据独立写入审核Run，无修改开发者树。

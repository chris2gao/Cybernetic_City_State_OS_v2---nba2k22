# 下一轮 Gemini：三项有界探索提案

这些是可提交 Human 审批的任务材料。尚未发送、启动或获得新增实机/UI权限。原 Issue2 六阶段授权已结束，不能把本轮静态成果当作新 live 授权。详细选择算法、地址公式、字段、字节预算、UI反例和停止条件以 `next_round_plan.json` 为准。

所有项目先从固定磁盘 SHA 重放有关消费者，不能沿用历史 PID1828 和地址。实机阶段需新 PID、creation token、实际进程文件/磁盘哈希、module base/size 和上下文证据；管理员权限仅用于已获批的只读访问。若无法获得真实 native Save ID，保持 SAVE_UNBOUND。固定外部 policy 要在读取目标前冻结范围，显式 helper 也计入预算；本轮 mock 不是可直接投产的 Windows reader。

1. **GM 拥有者与表头闭环，优先级1。** 读取 Slot61/71 各 index0..2完整记录，Team indices2、3、4、9的 `+0xC88` 两个表头及 `+0xCA8` raw ID；目标816B，加一次1208B root/descriptor bootstrap为2024B。验证 head→next→owner，而非把 copied name当PlayerID。UI只读核对可见球队/金额/名称；对调Team、重复金额、样本外next和循环必须失败或标记缺失。样本外链不跟读。原生 free-next 的 `+0x36/+0x62` 与null终止对象链分别解释。技术可行，收益是修正球队薪资/TPE食材的归属；当前记录是否对应可见UI尚待验证。

2. **Player 完整姓名、25入口与GP/赛季对照，优先级2。** Player indices0、1各取80B姓名＋50B索引；每人最多 first5 valid ordinary selectors加特殊selector24对应的六条48B统计，合计至多12条。目标836B，独立运行含bootstrap2044B。只允许这两个Player的0..79与0xFC..0x12D，不扩大到完整Player或Potential。UI对照完整姓名、至少两条可见赛季/赛事GP；错名、错赛季、邻接flag污染作为反例，空洞和索引0必须正确处理。静态结构已充分支持精确探针，特殊入口含义与赛季join仍未确定。

3. **Draft 条件与 RecordData resolver，优先级3，先做静态。** 每类最多追两条消费者路径，挑战 bit17/token是否足够解释保护/交换，以及RecordData `+0x30/+0x32` 是否有明确resolver。找不到就交付UNKNOWN和精确分支，不改做全池扫描。可选新增live仅Draft indices0..5的32B和最多三个关联Team raw ID，共198B，含bootstrap1406B；RecordBook live预算为0。只读UI核对pick/original关系与实际条件文字，禁止通过交易、推进赛季或存档操作制造样本。收益是阻止结构上看似合理的token变成虚构业务语义，是否能认证取决于resolver和当前可见正反例。

若三项在同一获批会话执行，bootstrap只计一次，硬上限 `1208+816+836+198 = 3058B`。阶段预算不可互借；未使用额度不授予替补目标或重读。每个项目单独报告 RAW、STATIC、LIVE、UI、SAVE、生产轴，不把部分通过写成总DONE。

交接时提供本分支固定SHA、`static_capture.json`、`decoded_fixtures.json`、`corrected_claims.json`和策略负例。Gemini先复核原生表达式及地址公式，再向Human呈现具体读取封套；本文件本身不向其他任务发送消息。

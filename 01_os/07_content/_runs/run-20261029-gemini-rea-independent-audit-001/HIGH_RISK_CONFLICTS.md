# Independent Audit · 必须先审的跨分支冲突及证据误用

本文件记录**Codex必须检验的问题**，不是本文已独立证明的最终Native事实。来源：Gemini固定 `gemini_rea@6cad7c7454798dbe18e7bd800d85e2a9d1c7119c` 与Codex基线`6151ef5d484914edcec2fbcfcf3bcce83a848907`。冻结PE SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`。

| 优先 | 冲突/未证推论 | Gemini材料 | Codex已有约束 | Codex需要独立证明或采取的处理 |
|---|---|---|---|---|
| P0 | `0x12bf5a0`被当作“phase22合同选项结算” | `W03_07/EVIDENCE_LEDGER.json`、`contract_offer_codec.py` | `OFFER_WITHDRAWAL_NATIVE_CONTRACT.md`说明此候选扫描、打分、选择报价并在period22有assert，非指定GM签约 | 重放完整函数及caller、phase语义，查已排除029报价消费者；如果冲突保留就REJECT Gemini具体业务定性 |
| P0 | 48字节/5薪资OfferContext与44字节/6薪资Native Pool混同 | `contract_offer_codec.py` | `FA_OFFER_NATIVE_CONTRACT.md`有私有44字节报价记录、6个工资字段、年限1..6、原生`0x12bd4c0` | 如果确有48字节中间UI对象须明确不同类型和转换链；不得替代现有通过12专项离线测试的提交合同 |
| P0 | 撤回函数 `0x12b3840`与已恢复`0x12b4040` | `W03_07/EVIDENCE_LEDGER.json` | 原生撤回 `CONTRACT_WITHDRAW_PENDING_OFFER` 有独立44字节服务证据与结果边界 | 核实`0x12b3840`究竟是调用者、辅助状态处理还是不同业务，不能借名称替换正式handler |
| P0 | 自行按CBA薪资规则审查交易 | `trade_package_codec.py: validate_salary_matching` | 产品授权：GM选择WHO/WHAT/TERMS，Native后端只执行、由游戏引擎校验；历史一对一Process具体成功 | 不把Gemini CBA计算和自行批次转换移入执行器；只研究正确原生检查和交易合同 |
| P0 | 三方/多资产被描述为“原子交易” | `W03_10/EVIDENCE_LEDGER.json` | 现有执行批次明确“batch不是底层原子事务”，未经过具体三方实机验证 | 证明原版服务是否支持该对象，ABI、所有权、失败副作用；未闭合则NOT_CALLABLE |
| P1 | 一处UI置`IsInUse`与Dirty被推广为对手Gameplan保存且比赛生效 | `GREA_01`,`W02_A`,`W03_00` | 冻结`COACH_SET_GAMEPLAN`仍PARTIAL_BINDING；默认Gameplan`0x131f110`非29对手提交 | 重放原始UI路径、证实对象归属与持久化/只读Getter；无Save/Reload授权不能宣称持久 |
| P1 | 位段初始化和两次拷贝被推广为18项完整原生setter/枚举已证 | `W02_B`, `defense_18_codec.py` | 18项没有正式Setter合同；枚举须以原生读写消费者验证 | 逐字段核对UI/源码证据，防止比特掩码只有默认值证明却赋予具体业务语义 |
| P1 | `cmp eax,0x44`被推广为360字节Book/68CRC及四分区的所有证明 | `W02_C`, `W03_00`, `playbook_68_codec.py` | Playbook正式槽操作仍待恢复 | 以独立Playbook读/写/字段位置/CRC来源/Team owner反证，保留Flush缺口 |
| P1 | 逐人分钟、深度顺序、时间线直接等同完整首发轮换业务 | `W03_05`、`rotation_timeline_codec.py` | 仅逐人分钟有已恢复Native调用合同，完整轮换尚未闭合 | 区分数据位段、完整上下文、菜单提交；检查分钟/时间线对齐和未修改字段 |
| P1 | 训练/师徒/员工/选秀局部函数被描述为可执行完整业务 | `W03_06/08/09` | Codex冻结总账明确剩余动作未闭合 | 各取一个最短可信子集验证调用链，缺完整权限/场景/读回不建立生产写操作 |
| P2 | 18+ Getter“索引目录”被解释为真实数据自动采集能力 | `W03_12`, `native_getter_catalog.py` | 现有15类Reader均不完整且尚未接入当前存档身份/采集批次 | 分离Reader函数入口、current-save对象索引、字段语义、历史/新鲜度与执行前后只读校验 |
| P2 | “163项完成闭环、21项测试全部通过” | `W03_MASTER_GAP_MATRIX.json`, `pytest_gemini` | 原184需求进度不等于成功数，PR19仍Draft/closed-with-deferred-scope | 逐项区分证据研究覆盖、静态真值、离线Python编解码及游戏实机效果；不使用163作为能力数量 |

## 独立复核注意

- PE静态字节确证一段`mov`、`cmp`不等于语义/ABI/生命周期/持久保存已闭合。
- 即使有正确布局也只能接受为**可信数据结构候选**，除非原版读写/消费者及保存链另有证据。
- Gemini编写的`import ...codec`测试不代表真实游戏或正式Runtime测试；接收前要引入非同源黄金向量或差异测试。
- 非生产级候选按`RESEARCH_ONLY`保留；只有Codex独立审核后的具体函数/源码与来源可以选择性移植。
- 禁止拿无法通过的合同/交易候选改写已经被冻结的严格原生交易、FA报价/撤回实现。

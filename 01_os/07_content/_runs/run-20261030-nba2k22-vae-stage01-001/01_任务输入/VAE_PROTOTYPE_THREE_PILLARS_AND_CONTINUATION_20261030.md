# VAE 原型需求升级 · 三支柱验收和Gemini Loop连续开发（2026-10-30）

## Human 新增的原型验收目标
1. **原生执行能力**：GM预算/人员/交易/签约/选秀，教练设置/球队设置/轮换/训练，球员原生成长/倾向/徽章/训练，必须按动作区分可操作、可读、可建议与实际游戏读回；普通球员角色不能因规划而自动获得直接属性/徽章写权。
2. **操作方法论和机制关系**：每个原生修改项必须有作用机制、关联设置/冲突、可证伪假设、数据驱动决策、预注册评估指标、技术读回与后续表现评价；REA探索是方法但非自动的实机因果证明。
3. **数据采集与分角色决策服务**：复用已存在Reader/REA/D系列采集与历史事实系统，采集所需内容、确定性分析，提供GM、教练、球员各自权限和场景适合的数据集，并支持持续试验效果反馈。

## 与前一版原型的差别
- Gemini旧分支`c2d9caae388bac3ae5e586c69ee0bd2116ba473b`已有离线E1 R01–R09 Python流水线、G01–G08资料与21项**执行者声明**离线测试PASS，但`simulator.py`输出NOT_RUN，**完全不能证明真实交易/训练/徽章成长/球员设置等实际原生操作**，或全角色数据视图真正可用。
- 新Human指示是更高一层的产品要求：若仅交旧候选，不能按完整VAE原型验收。旧代码和证据保留为第一轮基础，不倒退或抹除历史。
- Human已批准的A-v1`5abf3cb...`仍固定；新要求是明示的产品交付扩展，不制造新的A版本、不声称完整七阶段Runner通过。

## 新合同位置和统一开发方式
- **原任务ID不变**：`NBA2K22-VAE-GEMINI-INTEGRATED-LOOP-20261030-001`，新合同提交 `0c544b6d7aab5e6401b5153c2f2e10706d2c31e1`。单独补充`HUMAN_PROTOTYPE_TARGET_AND_LOOP_AMENDMENT_V2.md`与`PROTOTYPE_CAPABILITY_EVIDENCE_MATRIX_V2.json`；新V2校验起始NOT_RUN。
- 与旧候选的区别在任务`run.yml`标注；老的`completion_pointer.md`视为离线初始证据，不代表V2完整交付。
- Gemini继续同一任务、同一分支、同一Run的`Observe→Discover Native→Build Adapter→Mechanism Hypothesis→Role Data→Dry-run/Live Verification (only when authorized)→Revise` Loop。
- 审核保持**完整候选后由独立GPT集中审核一次**，开发期内部局部测试不反复派单，真实跨模型交接需Human转发。
- 对普通修改、原始值读回及权限状态，保留Action→Mechanism→Information→Method→Evidence→Outcome矩阵；由证据级别收敛决定阶段进度，不按固定轮数。

## 权限、证据、特殊风险
- Human表示可由Gemini通过REA研究游戏机制，并没有明确批准全部活跃游戏动作、管理员提权、改写存档、真实球队操作或修改现有REA公共代码。运行/写入的具体动作必须符合已存在OS门禁；将一组可恢复的测试动作集中提出Human确认，不为每个局部研究反复审批。
- 真实原生写入技术成功、UI/SaveReload持久成功、竞技改善和长期成长效果是不同证据；禁止混用离线PASS、旧历史实例或REA猜测当成当前游戏实证。
- 复用D1–D5与原生Reader/采集，不接管其他正在进行的独立任务；若实现发现确需扩写到既有模块，单独以精确路径请求扩权，不自行越界。
- 新验收矩阵对所有动作/角色记录`PASS`、`NOT_RUN`、`UNKNOWN`、`BLOCKED`及关闭条件；只要关键真实操作仍未证明，不宣称三角色原型完整。

## 规划下一步
Human把合同修订SHA `0c544b6d7aab5e6401b5153c2f2e10706d2c31e1`交给Gemini原执行窗口，并要求同步GitHub实际分支（禁止丢弃未提交本地变更）；Gemini继续长期Loop，按新的三支柱目标补充实际实现与证据，最终仅交一个集成候选与独立审核。

这里的持久保存是GitHub Run，非PRMS SAVE；不表示Gemini已收到或已继续。

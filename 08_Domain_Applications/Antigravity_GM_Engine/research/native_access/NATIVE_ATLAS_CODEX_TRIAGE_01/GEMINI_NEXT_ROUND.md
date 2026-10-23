# Gemini Flash 下一轮可执行研究包（供 Human 中转）

状态：**已准备、未发送、未启动；所有新live封套均为建议，需Human明确批准后才可读取。** 精确执行顺序、字节/对象范围、步骤、证据、正负例和停止标准以同目录 `next_round_plan.json` 为准。模型/产品面/参数由当次OS路由确认，不默认为某个Flash型号，也不默认启用子代理。

## 研究目标和顺序

1. **R01-BIND**：先取得新的构建/当前上下文和真实目录来源；原生save身份无法建立时如实UNBOUND。一次根指针8B+完整75描述符1200B；此阶段不读任何对象缓冲区。
2. **R02-PLAYER-HISTORY**：将AG01D的Slot1+0xFC..0x127生涯索引候选与Slot24关联；补Player/TeamShotChart真实字段，停止把Slot39当职业逐年统计。两个球员身份/索引片段、最多12条Slot24和3条Slot26，最大1262B。必须先确认敏感性与stride；不读/导出Potential。
3. **R03-DRAFT-RELATIONS**：6条32B Slot42记录及最多3支队伍身份白名单片段，最大486B；验证当前owner/original、分组与轮次，围绕GetLinkedPick两种token提出可证伪假说；无保护/交换正例就交NOT_OBSERVED，不借现实NBA履历补事实。
4. **R04-COACH-BOOK**：3本Slot22完整360B手册，最大1080B；核实low7 lookup key、68 play words、现役队伍/教练绑定。已有catalog无法安全引用时保留raw，不自行遍历新对象。不是轮换时间线研究。
5. **R05-GM-CAP**：最多3条DeadCap(136B)与3条TradeException(112B)，最大744B；核实金额/日期/UI，工资与税费从真实front-office消费者静态追踪。不要读取Slot35找财务，或读取Slot67找TPE。
6. **R06-RECORD-BOOK**：最多10条Slot39纪录簿(520B)，解packed尾部类别与身份，保存来源时间和角色知识边界；对Player/GM历史食材有用，但优先级低于真实生涯、资产和当前执教数据。

每项上限是**该阶段合计**，不是每个候选或每次重试额度。若需要第二时点或额外样本，必须在其读取前把它纳入获准封套。研究方法在封套内可自主调整；可跳过低收益或当前没有正例的子探针，保留原因后继续其它已批准路线。失败预算不应把整个食材发现工程误杀，但不能用下一子探针绕过相同失败的重试上限。

## 实施规则

- 先运行离线fixture/地址运算/负例；读取前将完整底层请求白名单化，包含GameMemory构造器及helper可能产生的额外访问。只读handle不是完整授权。
- 模块基址、静态签名、指针和count在当次游戏上下文重新绑定；公式为`M=read_u64(module+0x06347720)`，描述符`M+16*n`，pData字段`M+16*n+8`，记录`pData+index*已证stride`。旧manager-8 root换算必须显式。
- 不直接复用本包的历史PID、pData、Team指针或来源时间；不把新日志timestamp当Save绑定。
- 包括原始安全字节/哈希、完整请求与实际长度、异常、原生字段/身份/时间来源、UI对照和负例。脚本内自报日志只能证明其记录内容；独立底层完整性证据缺失就明确限制，不能输出“所有RPM均合规”。
- 负例在调用前拒绝：index=count、负index、越出record的字段、未知build、未绑定身份、未批准pointer-follow。**不要真的越界读取来证明边界检查。**
- 当前UI缺少某案例时明确NOT_OBSERVED；保持UNKNOWN和竞争假说，不用全零、目录不存在、现实NBA知识或JSON flag制造原生语义。
- Human可提供当前只读UI对应材料；不自动推进比赛、日期、交易、保存或切换存档。禁止注入/Hook/调用未知副作用游戏函数。不得触碰正式SQLite或启动生产Decoder集成。

## 应交回什么

交回每阶段：观察与假说表、精确来源/构建/上下文、获准封套及实际请求明细、raw安全样本+hash、字段/索引/语义Decoder候选及正负Fixture、失败与UNKNOWN、Player/GM/Coach消费能力变化、OS任务包/run/验证/精确SHA。报告对象发现、字段解码、身份、采集、发布、角色Query和Save/Reload的独立成熟度。

按一个连贯有界研究任务完成，不为每个字段新建审批，不自动进入下一产品任务。Codex下一轮用原始证据裁决；Gemini不能以自己生成的JSON和测试数独立认证生产能力。

本文件是可交接的研究内容，不伪造通信endpoint、接收确认或授权记录；真正跨窗口传递按当前OS通信入口由Human触发。

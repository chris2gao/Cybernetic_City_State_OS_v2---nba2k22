# M2｜AI教练防守重点深入、进攻重点轻对照

目标动作：`COACH_SET_DEFENSE_FOCUS`。主参数POEDefense，主候选PROTECT_PAINT；对照POEOffense。研究AI决策、存值、gameplan选择和比赛消费，人工UI只作可能的观察旁证。

## 当前定义与实例（L1）

当前游戏元数据与enum CRC匹配：COACHDATA+316的共享32位字；POEDefense占低5位，0无偏好/13保护禁区/14中性防守/15限制外围；POEOffense占第15..19位，0无偏好、1GET_TO_BASKET、2GET_SHOOTERS_OPEN、3FEED_THE_POST、4PICK_AND_ROLL_OFFENSE、5NEUTRAL_OFFENSE_FOCUS、6RUN_OFFENSE_THROUGH_SCORER。

本轮Human明确允许管理员开发查看后，通过REA真实读取PHI(team0)及IND(team20)。二者当前POEDefense=14、POEOffense=5，29条对手Gameplan投影前后稳定。教练UniqueId未从本次元数据取得，保留null；TEAM→coach关联只限本次观察，不产生永久人物ID。STAFF池范围与对齐是待验证的布局/身份假设，不是只读许可条件。

证据：`evidence/live_coach/read-success/`，ID `ev_69e7ab80b3250c3161dc85a8b4f965ad6379da3d152bcd0b3da73e689afa5390`；2.916秒、显式9308字节。第一probe被池身份guard拒绝，核心球队筛选曾使读取成功，但不能据此排除其他可探索对象。

Human纠正后新增`evidence/live_coach/identity-hypothesis/`，REA `ev_bd46ce8630c54ec93f8af0abe0ea545608ec76ad2b2576234413ca75ab1fe2d1`。不使用池/对齐或核心球队ID阻断，只检查实际映射可读性、有限读取、逐字段异常隔离。219条TEAM中有5条PHI/IND匹配：核心0/20分别关联姓名候选Doc Rivers/Rick Carlisle；目录64的PHI/5000和82的IND/5018教练引用NULL；目录149的IND/788关联David Copelovici可读记录。非空三记录均可读352字节，+0x30/+0x58姓名、+0x18反向TEAM链接、+316的POE14/5相互支持，引用重读稳定；第一字不指向主模块，没有RTTI证明。这证明旧核心筛选遗漏了可研究记录，不证明它的游戏业务角色。

当前目录重建的第一个旧guard失败条件为PHI/5000的NULL引用；旧探针没有记录原始失败指针，不能将本次重建冒充历史地址确证。实际读取2724字节/65536预算、10.922秒、异常0、cleanup_error=null、游戏存活。此样本未发现可读非空池外对象，不能反推池外均无效。写入和原生调用身份资格均保持false。

## 存值→lookup（局部L2）

GetOpponentGameplanIndex引用候选RVA19883328..19883591：

- 片段imul步长0x370=880，加4偏移，循环cmp0x23=35，与历史manager profile一致。
- 读取候选对象ID并与请求对手比较；未找到时返回al=0xFF，找到时返回bl。第0项合法，0xFF不是第255条。
- 本轮因此增加纯解码器和负例：0有效、34有效、255缺失、35..254/负数/bool拒绝。

AddGameplan候选RVA19153505..19153686另保留38指令fragment。两者是索引/添加候选，不是已确认POEDefense Setter，也没有证明比赛AI何时选取它们。

## AI消费与效果（未知）

本轮对lookup候选安装900ms/最多12事件的有界入口/返回观察，结果0事件、hook.detach完成、REA cleanup_error=null。证据`evidence/live_coach/trace/`，`ev_0646b9951f0c93d4f50ddee62371f0b9db77f2b82b6c6b3130686f8bdde84c52`。日历场景不应预期比赛消费者活跃，不能由零事件判定没有AI路径。

当前引擎controller flag没有定位，输出UNKNOWN；外部Coach/GM身份不能自动转CPU控制。GAMEPLAN的is_in_use/is_tainted是原生存值投影，不能仅凭1/0宣称战术已在比赛生效。没有主动调用Native函数，没有业务写入，没有L3/L4。

## 工程与后端

现有`coach_codec.encode_changes`对共享字做mask+before校验，本轮离线直接调用该纯codec验证，不触发Writer。新增fixture进一步检查cache_epoch、applied_focus和其他球队保持不变；这些是模拟合同，不是游戏字段发现。

Native安全业务Setter：NOT_QUALIFIED（AI调用点、ABI/this/线程/效果未闭合）。Memory：定义/枚举/当前存值已加强，但实际consumer/刷新、完整相关状态和本轮write/readback仍不齐，因此NOT_QUALIFIED。真实route=NO_SAFE_PATH。

知识卡可以供Coach推理：根据对手内线威胁提出保护禁区候选，并声明可能让出外围机会是外部篮球策略推理；不能将其当成破解的2K AI系数或保证比赛结果。

后继优先coach-first：在已准备比赛场景中只观察自然调用与公开状态，先找到AI caller、实际controller与消费时机，再谈Setter/Memory资格及完整效果实验。参见Run下一批实验条目。

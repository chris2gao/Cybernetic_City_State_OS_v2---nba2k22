# B_DELTA｜原型实现后的范围内修订

初始B精确Blob保持`f711261d00b0df202906992597fdae7b895fcfb0`，未修改旧共识Run。Human允许以工程反馈修订原型；此文档不把未通过的独立审核变成PASS。

1. **Fixture路由使用显式后缀**：真实路线名与`NATIVE_FIXTURE_MODEL`/`VALIDATED_MEMORY_WRITE_FIXTURE`分开。Native模型是Python接口模拟，Memory是字典状态模拟；不冒充真正原生函数或Frida写入。所有fixture结果`game_target=false`，游戏证据不升级。
2. **共同后置条件由领域合同持有**：不能由意图提交者传入“qualified=true”或自由指定写区；后端声明的影响集合必须与预期一致，fresh完整状态对账还要检查非目标队保持不变。不是用两个return true作等价证明。
3. **原生失败后停止**：可能部分生效时返回EXECUTED_BUT_UNVERIFIED，绝不自动Memory重试；fixture后置失败明确FAILED_READBACK。未承诺未知游戏事务可自动回滚。
4. **分离源数与独立性**：知识投影计算origin_group集合。同源两份文档为SINGLE_ORIGIN；多个来源也不自动成为独立AI游戏行为实证。无当前同模式AI行为支持的卡不能被改标L3/L4。
5. **把静态缺失值变成明确合同**：GetOpponentGameplanIndex候选的0xFF被解码为None；0仍为合法索引。新增针对35..254/bool/负值的边界测试，防止按truthiness或数组255误读。
6. **不把role字段当引擎控制**：Actor包含engine_control，但当前真实游戏证据未取得native controller flag；真实后端因此始终NO_SAFE_PATH。不会为了让PoC工作而转CPU控制。
7. **收到后续Human查看授权后的更新**：初始任务未授权live，本轮Human后来明确授予游戏开发查看/管理员权限，已执行两次初始只读attach、一次短trace和一次身份假设重查。新增真实存值证据，仍未合格任何游戏业务执行后端。
8. **只读身份守卫纠正**：STAFF池范围/352对齐改为待验证假设，不能阻断已授权只读探索。保留实际可读性、65536字节预算、逐字段异常隔离。新探针不再过滤非核心球队，找到IND/788的可读David Copelovici记录；当前重建的旧首个拒绝条件为PHI/5000教练NULL。旧失败指针未记录，保留历史不可复原限制。写入/原生调用仍独立严格认证；本轮没有取得其技术资格。

局部命名：教练知识卡沿用展示输入中的ID`AI_COACH_DEFENSE_M1`；研究专题编号仍为M2，M1专题仍是徽章。此ID不表示把教练研究移到徽章任务，也不新增第4项核心机制。

所有上述修改在原授权的工程原型范围内，不改变“机制知识独立于执行、合格Native优先、经证Memory兜底、都不合格阻断、AI/AI-AI优先”承重语义。没有需Human裁决的生产架构替换；真实游戏执行上下文不足继续保留UNKNOWN。

# VAE REA 机制整合集中独立审核 · 固定版本

## 审核身份
独立公共基线 Fork，角色 `independent_review`，审核对象 **`b3e39f867364b4610fc57f5cc798c7ab33232eeb`**。项目先前的Gemini原生研究、V2/V3返工结论不是当前提交已通过的证明。不得修改开发者候选、游戏或存档。

## 核心核验
1. 比对源字段档案和`MECHANISM_RELATIONSHIP_GRAPH_V1.json`中字段主键，特别注意 `Tempo` 已在`COACH_DEFAULT_014`，而机制图用`COACH_DEFAULT_005`；`Touches`在`TENDENCY_NATIVE_066`，而机制图用`TENDENCY_NATIVE_002`。查看所有同类潜在错配，判断对行为规则/下游结果的影响。
2. 对 `coach_pacing.py` 的 `calculate_tempo_modifier` 与标注的 x86 指令开展独立整数边界/负数/取整核验。代码计算`edx`却不用于`unclamped`；报告中的`0.6`缩放需重新认证。区分真实PE证据、硬编码字节和说明。不能因40项测试自报PASS而直接接受`PROVEN_NATIVE_ASSEMBLY`。
3. `role_governor.py` 三分支、表身份、数据类型、落盘字节与浮点舍入规则，检查变量/数组索引、分支可达性及观察范围，不能用Fixture自洽验证代替真实PE/AI消费者。
4. 检查`decision_bridge.py`的启发式隔离与`mechanism_graph.py`的边证据评级，尤其不要把`OUTCOME`边写成Native已验证。
5. `TELEMETRY_VALIDATION_CONTRACTS_V1.json`目前只有3条`source_mechanism / target_observable / verification_gate`条目；作为**候选度量需求**评估其完整性，不要求将其JSON形状变为采集系统物理格式。检查是否缺身份、状态、时间、游戏模式、USER/CPU、两种Normalize、前后变化、有效样本与观测可得性等最低语义。
6. 从原提交检查单元测试真实行为、测试期间的进程附加与文件污染风险；如不能独立运行，明确NOT_RUN；不要冒称二进制现场已检验。

## 交付
一次完成综合独立审核报告、精确证据矩阵、可复核P0/P1/P2、集中工程修复建议和正式完成指针。仅对固定SHA内证据作结论；主张具体原生字节真实存在必须有相应PE / Live来源，云端只有硬编码时标证据限制。

**不做**真实游戏操作，不为D系列规定新的日志、DB表、字段名或协议；数据契约仅分析指标和上下文需求。审查结论与后续Gemini同一工程包返工边界明确。

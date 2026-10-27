# Codex 任务候选：NBA2K22 原生游戏机制逆向/REA 可复用交互探索（未派发 v0）

**状态：PRE_DISPATCH_REQUIREMENT_MODELING_ONLY。** 无 `A0` Human确认、无`01b A` Human确认、无任何本地/游戏/函数执行授权；本文件仅作为下游真实Codex执行包的目标轮廓。不得当作“立刻进入游戏调用API”的指令。

## 项目研究价值

外部GM/Coach/Player决策层目前主要依据已有MyLEAGUE数据源，通过Native字段读写引发游戏效果。REA可能帮助我们从“字段和值”进一步追踪“游戏如何判定、更新和提交状态”，从而发现可以安全重用的原生程序流程。**外部业务决策可能调用原生交易/签约/选秀/战术函数，是需证明的方案，非已具备的功能。**

## Codex后续授权项目的候选Objective

固定NBA2K22.EXE构建SHA、REA版本、Windows环境和特定离线存档，在限定资源预算下，对Human指定的有界机制族，通过已有攻略/代码/样本导航到实际Native数据结构/常量/函数及调用路径，给出局部实机状态证据，并对是否支持Native“外部决策→原生执行”路径形成函数级和业务级可行性评级；若Human以后明确批准隔离档代表性调用实验，可额外交付受控调用PoC，否则停在静态/只读实证报告。

## 实验顺序建议（不是立即授权的操作指令）

1. **RE-A0 资产预检**：只读检查REA实际版本、适配器/Windows可用能力、管理员提权边界和二进制SHA；定位已授权的旧资料源`DIFFICULT_ITEMS.md`/Player+Coach+Market Native Reader等，列出攻略给的具体现象及来源版本。
2. **RE-A1 机制目标定位**：每机制先界定目标游戏UI页面、触发条件、输入值及结果字段，区分游戏自然流程与外挂操作。不按没有复现步骤的传言直接扫描全游戏。
3. **RE-A2 有界来源追踪**：定位元数据、常量表、结构布局及函数入口；按需要使用REA原生静态Provider局部xref/caller/callee和有限实时只读观察；记录每条推断的具体代码窗口、反证、未解析间接分发和停止成本。**已报告连续四次whole EXE Ghidra provider_timeout，不用原路线无限重跑**。
4. **RE-A3 机制因果建模**：输出真正的条件判断、数据写集合、依赖对象、触发时点、缓存失效、回调以及失败处理候选；通过人类实际已可达的游戏窗口做无副作用对照，不能把单个码址当整个业务事务。
5. **RE-A4 外挂原生交互评级**：评估函数的可调用性，包括ABI/calling convention、this、vtable、对象生命周期、游戏线程、事务/锁、随机数、season state、合法校验、持久化与跨对象副作用。等级只能是`FOUND_NOT_CALLABLE` / `CALLABILITY_UNKNOWN` / `SAFE_TEST_PRECONDITIONS_IDENTIFIED` / `AUTHORIZED_POC_REPRODUCED` / `REJECTED`等，未授权不能直接进入`AUTHORIZED`。
6. **RE-A5 仅在未来Human单独授权时**：隔离测试存档选择1–2个代表性的原生调用候选，事前保存可重放边界与旧值快照，有界执行后触发全新Native读采集并核对整个受影响事务对象和游戏UI。无证据/权限时拒绝调用，不触发模拟回档或强制覆盖。

## 每个机制的交付记录模板

`mechanic_id; game_mode/build_SHA; in_game_scene; source_guide_claim; observable_UI_target; input_and_preconditions; native_types_and_tables; values_and_constants; entry_function_RVA; xrefs_callers_callees; branches; state_changes; side_effect_objects; source_artifacts; REA_provider_profile; raw_Evidence_ID; confidence; counterexamples; feasibility_grade; safe_native_call_prerequisites; new_container_fields_if_any; external_GM_coach_player_interop_value; stop_reason; unresolved_gaps`。

**评审必需**：原始证据可追溯，报告未知而非填假值；Static函数路径/Frida只读样本与Human真实游戏行为分开；**复用REA提供的机制，不宣称REA官方在Windows具有任意游戏函数调用工具**。

## 交付与互相依赖

此任务将为原本世界数据阶段02/03提供**Native布局与机制来源**，为第二大任务`Native I/O`提供安全交互候选，为GM/Coach/Player外挂业务规划提供潜在的“外部决策、游戏原生执行”方式。三者是**下游受控引用**，不因本探索成果自动修改已确认的A和ADR。

**批准链**：待Q1–Q3 Human答复 → `A0-v1`精确确认 → `01b`细化每件交付物/退出门与风险 → Human确认`A-v1` → 固定branch/head/游戏场景/允许操作和测试档 → 单独向Codex派发按OS受控任务包 → 来源复验/独立审查 → Human确定是否改变外挂架构。此顺序不让Codex一边做高风险实验一边补产品范围。

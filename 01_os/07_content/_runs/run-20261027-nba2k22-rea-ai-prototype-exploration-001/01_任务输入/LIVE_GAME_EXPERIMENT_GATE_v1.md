# 新 Codex 探索任务｜真实游戏实验准入范围与审批模板

**本任务立即授权范围**：独立工作分支上的源代码研发、离线PE/静态文件分析、旧资料只读复用、Owned Fixture执行与恢复、CLI单元测试、机制知识构造与可复核报告。**没有在本消息里授予真实游戏进程注入/Hook/函数调用/内存写/存档修改/比赛推进的具体许可**。

**一次性批量准入模板（由Codex填后请Human批准，不逐字段问）**：

```yaml
experiment_request_id: EXP-REA-AI-###
purpose: one_ai_mechanism_and_one_bounded_scene
game_target: NBA2K22_PC_Offline_MyLEAGUE
game_exe_path_and_sha256: FRESH_REVERIFY
game_build_and_mode: FRESH_REVERIFY
game_process_and_privilege_context: FRESH_REVERIFY
save_identity_and_isolation: TEST_SAVE_OR_HUMAN_EXPLICITLY_ACCEPTED_CURRENT_GAME
target_ai_actor_and_actual_game_controller_flag: EVIDENCED_OR_UNKNOWN
operation_class: READ_ONLY_ATTACH | BOUNDED_TRACE_HOOK | NATIVE_ACTION_CALL | VALIDATED_MEMORY_WRITE | GAME_SCENE_ADVANCE
read_or_write_object_scope: EXPLICIT
script_paths_and_sha256: REVIEWED
rva_function_targets_and_abi_if_relevant: EVIDENCED
scope_preconditions: EXPLICIT
max_duration_events_bytes_attempts: EXPLICIT
expected_side_effects: EXPLICIT_OR_UNKNOWN_BLOCKS_EFFECTFUL_ACTION
rollback_or_safe_stop: PROVEN_OR_NOT_EXECUTED
readback_and_affected_object_checks: LIST
cleanup_checks: LIST
Human_specific_approval: PENDING
```

- 纯读取脚本若通过 Frida attach，本质仍会注入探针，必须拿到该场景的批准；脚本名称含`readonly`并非进程级保护。管理员权限不经批准不得绕过。
- 旧游戏exe hash只是过去研究的绑定，不是新场景执行许可。
- 实际原生函数调用PoC默认**教练AI优先、AI–AI交易后置**，但如果Codex证明另一个AI动作更安全且更有价值，可向Human以证据提议调整，不能自行取代原Q6=B优先级后执行。
- 在Human批准之前，Codex必须继续**离线可运行原型**、资料交叉索引、静态函数探针和Owned Fixture，不能把缺少Live许可当成本任务整体阻塞。
- 所有读取与Hook均清理现场；任何失败、异常、进程崩溃、原生状态漂移或缓存异常即时停止，保留失败证据。
- 禁止上传EXE、正式存档、游戏资产、绝对内存地址和用户隐私。记录可去敏的SHA/结构/错误类型与方法。
